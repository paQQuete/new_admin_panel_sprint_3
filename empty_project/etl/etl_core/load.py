from datetime import datetime

from elasticsearch import ConnectionError, Elasticsearch, helpers
from contextlib import contextmanager
from psycopg2.extensions import connection as _connection

from utils.logger import logger
from utils import state
from utils.backoff import backoff
from . import extract


@contextmanager
def es_conn_context(url: str):
    """Контекстный менеджер для подключения к Elasticsearch"""

    @backoff(ConnectionError, message="Elasticsearch connection error")
    def connect(url):
        es = Elasticsearch(url)
        logger.info(es.info())
        return es

    es = connect(url)
    yield es


def load_to_es(
        es_client: Elasticsearch,
        pg_connection: _connection,
) -> None:
    """Основной метод для инкрементальной миграции данных из БД Postgres в индекс movies в Elasticsearch"""
    INDEX_NAME = "movies"
    STATE_STORAGE = "state_storage.json"
    BATCH_SIZE = 100

    pg_extractor = extract.PgExtract(pg_connection)

    # Получаем последнее состояние из файла
    file_storage = state.JsonFileStorage(STATE_STORAGE)
    curr_state = state.State(file_storage)
    last_modified = curr_state.get_state("modified")

    # Если текущее состояние в файле не найдено, считаем загрузку первоначальной и выгружаем все кинопроизведения.
    if not last_modified:
        logger.info("Initial load started.")
        last_modified = str(pg_extractor.get_last_modified())
        pg_extractor.select_all_movies()
        load_batch(es_client, pg_extractor, BATCH_SIZE, INDEX_NAME)
        logger.info(f"last_modified = {last_modified}")
    # Если в файле есть состояние, загружаем фильмы, обновленные позже даты из файла
    # Состояние, которое будет установленно в качестве текущего для следующей итерации,
    # изменится на максимальную дату modified из выбранных для обновления кинопроизведений.
    # Если с момента предыдущей итерации данные не изменились, состояние останется прежним
    else:
        logger.info("Last modified = {}".format(last_modified))
        movies = pg_extractor.get_movies_to_update(
            datetime.fromisoformat(last_modified)
        )
        if movies:
            ids = tuple(row["id"] for row in movies)
            pg_extractor.select_movies(ids)
            load_batch(es_client, pg_extractor, BATCH_SIZE, INDEX_NAME)
            last_modified = str(max(row["modified"] for row in movies))
            logger.info("last_modified = {}".format(last_modified))

    # Сохраняем новое значения состояния в файл, бросаем исключение если значение None или False, чтобы не писать неправильное состояние в файл
    if last_modified and last_modified != str(None):
        curr_state.set_state("modified", last_modified)
    else:
        raise Exception(f''''modified' state is not True, we don't save the state to {file_storage.file_path}''')


def load_batch(
        es_client: Elasticsearch,
        pg_extractor: extract.PgExtract,
        batch_size: int,
        index_name: str,
) -> None:
    """
    Функция для получения пакета данных из Postgres и пакетной загрузки в Elasticsearch
    """
    while True:
        logger.info(f"Extracting batch of {batch_size}")
        data = pg_extractor.extract_batch(batch_size)
        if not data:
            logger.info("PG cursor is empty")
            break

        def gendata():
            """
            Получение генератора json для использования в пакетной загрузке в Elasticsearch
            """
            for row in data:
                yield {"_index": index_name, "_id": row["id"], "_source": row}

        result = helpers.bulk(es_client, gendata(), stats_only=True)
        logger.debug(result)
        logger.info("Batch loaded")
