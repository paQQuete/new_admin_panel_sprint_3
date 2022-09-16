import json
import time

from elasticsearch import Elasticsearch

from utils.logger import logger
from etl_core import load, extract
import utils
from config.config import *


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

    while True:
        with load.es_conn_context(ELASTIC_URL) as es, extract.pg_conn_context(dsn) as pg:
            if not es.indices.exists(INDEX_NAME):
                create_es_index(es, INDEX_NAME, INDEX_SCHEMA)
            load.load_to_es(es, pg, STATE_STORAGE=STATE_STORAGE, BATCH_SIZE=BATCH_SIZE,
                            INDEX_NAME=INDEX_NAME)
            logger.info(f"Next sync attempt in {LOOP_TIMEOUT} seconds.")
            time.sleep(LOOP_TIMEOUT)
