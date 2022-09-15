from contextlib import contextmanager
from datetime import datetime
from typing import *

import psycopg2
from psycopg2.extras import DictCursor

from utils import sql
from utils.backoff import backoff


@contextmanager
def pg_conn_context(dsl: dict):

    @backoff()
    def connect(dsl):
        conn = psycopg2.connect(**dsl, cursor_factory=DictCursor)
        conn.cursor()
        return conn

    conn = connect(dsl)
    yield conn
    conn.close()


class PgExtract:
    def __init__(self, connection) -> None:
        self.conn = connection
        self.cursor = self.conn.cursor()

    @backoff()
    def get_last_modified(self) -> Dict:
        """
        Метод для получения наибольшей даты обновления всех объектов
        Возвращает максимальное значение поля modified из таблиц:
        - person
        - genre
        - film_work
        """
        self.cursor.execute(sql.PG_LAST_MODIFIED)
        return dict(self.cursor.fetchone()).get("updated_at")

    @backoff()
    def get_movies_to_update(self, last_modified: datetime) -> List[Dict]:
        """Запрос и получение списка идентификаторов кинопроизведений для обновления.
        Возвращает кинопроизведения, в которых дата одновления (updated_at) одноой или нескольких
        записей person, genre, film_work - больше параметра last_modified
        При наличии обновлений в нескольких объектах кинопроизведения (например, в связанных genre и person)
        для каждого кинопроизведения возвращается максимальная дата обновления.
        :param last_modified: дата, используется для фильтрации выборки.
        """
        if last_modified != None:
            self.cursor.execute(sql.PG_MOVIES_TO_UPDATE, {"date": last_modified})
        else:
            self.cursor.execute(sql.PG_MOVIES_TO_UPDATE)
        return [dict(row) for row in self.cursor.fetchall()]

    @backoff()
    def select_all_movies(self) -> None:
        """ "
        Запрос всех кинопроизведений (данные в курсоре)
        """
        self.cursor.execute(sql.PG_SELECT_ALL)

    @backoff()
    def select_movies(self, ids: tuple) -> None:
        """
        Запрос кинопроизведений по id(данные в курсоре)
        :param ids: кортеж идентификаторов кинопроизведений
        """
        self.cursor.execute(sql.PG_SELECT_BY_ID, (ids))

    @backoff()
    def extract_batch(self, batch_size=100) -> List[Dict]:
        """
        Возвращение пачки данных из курсора
        :param batch_size: размер пачки данных
        Возвращает список кинопроизведений в формате,
        пригодном для загрузки в индекс Elasticsearch
        """
        return [dict(row) for row in self.cursor.fetchmany(batch_size)]