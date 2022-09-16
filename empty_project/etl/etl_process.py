import json
import time

from elasticsearch import Elasticsearch

from utils.logger import logger
from etl_core import load, extract
import utils
from config import config


def create_es_index(
        es_client: Elasticsearch,
        index_name: str,
        index_schema: str,
) -> None:
    """Функция для создания индекса, если его еще не существует"""
    with open(index_schema) as f:
        schema = json.loads(f.read())
        result = es_client.indices.create(index=index_name, body=schema)
        logger.debug(result)
        logger.info(f"Created index with name: {index_name}")


if __name__ == "__main__":
    appenv = config.initvar()

    while True:
        with load.es_conn_context(appenv['ELASTIC_URL']) as es, extract.pg_conn_context(appenv['dsn']) as pg:
            if not es.indices.exists(appenv['INDEX_NAME']):
                create_es_index(es, appenv['INDEX_NAME'], appenv['INDEX_SCHEMA'])
            load.load_to_es(es, pg, STATE_STORAGE=appenv['STATE_STORAGE'], BATCH_SIZE=appenv['BATCH_SIZE'],
                            INDEX_NAME=appenv['INDEX_NAME'])
            logger.info(f"Next sync attempt in {appenv['LOOP_TIMEOUT']} seconds.")
            time.sleep(appenv['LOOP_TIMEOUT'])
