from pydantic import BaseSettings, BaseModel


class EnvSettings(BaseModel):
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    ELASTIC_URL: str
    LOOP_TIMEOUT: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ConstSettings(BaseModel):
    INDEX_NAME = "movies"
    STATE_STORAGE = "state_storage.json"
    INDEX_SCHEMA = "es_schema.json"
    BATCH_SIZE = 200


def initvar() -> dict:
    '''
    :return: dict with all app config variables
    '''
    etl_env_settings = EnvSettings().dict()
    etl_const_settings = ConstSettings().dict()

    dsn = {
        "dbname": etl_env_settings.get('DB_NAME'),
        "user": etl_env_settings.get("DB_USER"),
        "password": etl_env_settings.get("DB_PASSWORD"),
        "host": etl_env_settings.get("DB_HOST"),
        "port": etl_env_settings.get("DB_PORT"),
    }
    ELASTIC_URL = etl_env_settings.get('ELASTIC_URL')
    LOOP_TIMEOUT = etl_env_settings.get('LOOP_TIMEOUT')

    INDEX_NAME = etl_const_settings.get('INDEX_NAME')
    INDEX_SCHEMA = etl_const_settings.get('INDEX_SCHEMA')
    STATE_STORAGE = etl_const_settings.get('STATE_STORAGE')
    BATCH_SIZE = etl_const_settings.get('BATCH_SIZE')

    return {
        'dsn': dsn,
        'ELASTIC_URL': ELASTIC_URL,
        'LOOP_TIMEOUT': LOOP_TIMEOUT,
        'INDEX_NAME': INDEX_NAME,
        'INDEX_SCHEMA': INDEX_SCHEMA,
        'STATE_STORAGE': STATE_STORAGE,
        'BATCH_SIZE': BATCH_SIZE
    }

