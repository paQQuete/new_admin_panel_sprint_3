import os
import json
import time
import sys
from pathlib import Path

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from utils.logger import logger
from etl_core import load, extract
import utils

load_dotenv()
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

dsl = {
    "dbname": os.environ.get("DB_NAME"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST"),
    "port": os.environ.get("DB_PORT"),
}

ELASTIC_URL = os.environ.get('ELASTIC_URL')
LOOP_TIMEOUT = os.environ.get('LOOP_TIMEOUT')
INDEX_NAME = "movies"
STATE_STORAGE = "state_storage.json"
INDEX_SCHEMA = "es_schema.json"
BATCH_SIZE = 200


def create_es_index(
        es_client: Elasticsearch,
        index_name: str,
        index_schema: str,
) -> None:
    """Функция для создания индекса, если его еще не существует"""
    if not es_client.indices.exists(index=index_name):
        with open(index_schema) as f:
            schema = json.loads(f.read())
            result = es_client.indices.create(index=index_name, body=schema)
            logger.debug(result)
            logger.info(f"Created index with name: {index_name}")


if __name__ == "__main__":
    while True:
        with load.es_conn_context(ELASTIC_URL) as es, extract.pg_conn_context(dsl) as pg:
            create_es_index(es, INDEX_NAME, INDEX_SCHEMA)
            load.load_to_es(es, pg)
            logger.info(f"Next sync attempt in {LOOP_TIMEOUT} seconds.")
            time.sleep(int(LOOP_TIMEOUT))