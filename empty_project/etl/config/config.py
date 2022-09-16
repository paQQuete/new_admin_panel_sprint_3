import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

dsn = {
        "dbname": os.environ.get('DB_NAME'),
        "user": os.environ.get("DB_USER"),
        "password": os.environ.get("DB_PASSWORD"),
        "host": os.environ.get("DB_HOST"),
        "port": os.environ.get("DB_PORT"),
    }
ELASTIC_URL = os.environ.get('ELASTIC_URL')
LOOP_TIMEOUT = int(os.environ.get('LOOP_TIMEOUT'))

INDEX_NAME = "movies"
STATE_STORAGE = "state_storage.json"
INDEX_SCHEMA = "es_schema.json"
BATCH_SIZE = 200