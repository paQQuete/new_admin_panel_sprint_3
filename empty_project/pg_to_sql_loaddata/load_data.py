import sqlite3
import psycopg2
from dotenv import load_dotenv
from typing import List, Tuple, Dict, Any, Union
import os

from pathlib import Path
from psycopg2.extras import DictCursor, execute_values
from contextlib import contextmanager
from dclasses import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork, TABLE_MAPPING


@contextmanager
def conn_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


class Worker():
    def __init__(self, sqlcur: sqlite3.Connection.cursor, pg__cur: psycopg2.extras.DictCursor, table_name: str,
                 dclass: Union[Genre, GenreFilmwork, Filmwork, PersonFilmwork, Person], batch_size: int, target_schema: str):
        self.__table_name = table_name
        self.__sqlquery = 'SELECT * FROM {}'.format(self.__table_name)
        self.__cur = sqlcur.execute(self.__sqlquery)
        self.__colnames = self.__get__colnames()
        self.__batch_size = batch_size
        self.__dclass = dclass
        self.__pg__cur = pg__cur
        self.__target_schema = target_schema

    def __get__colnames(self) -> Tuple[str]:
        column_names = tuple(map(lambda x: x[0], self.__cur.description))
        return column_names

    def __fetch_data(self) -> List[sqlite3.Row]:
        return self.__cur.fetchmany(size=self.__batch_size)

    def __parse_zip_sqlrow(self, sqlrow: sqlite3.Row) -> Dict[str, Any]:
        row_dict = dict()
        rowdata = tuple(map(lambda x: x, sqlrow))
        for eachtuple in tuple(zip(self.__colnames, rowdata)):
            row_dict.update({eachtuple[0]: eachtuple[1]})
        return row_dict


    def worker(self):
        fetched_data = [1]
        while len(fetched_data) != 0:
            fetched_data = self.__fetch_data()
            for rawrow in fetched_data:
                d = self.__parse_zip_sqlrow(rawrow)
                filled_dclass = self.__dclass(**d)
            columns = str(tuple(map(lambda x: x, self.__colnames))).replace("'", "")
            rows = list(map(lambda x: tuple(x), fetched_data))
            query = f'INSERT INTO {self.__target_schema}.{self.__table_name} {columns} VALUES %s ON CONFLICT (id) DO NOTHING'
            execute_values(self.__pg__cur, query, rows)


def main(sqlcur: sqlite3.Connection.cursor, pg__cur: psycopg2.extras.DictCursor, batch_size: int, target_schema: str):
    for table, dclass in TABLE_MAPPING.items():
        sql_worker_instance = Worker(sqlcur, pg__cur, table, dclass, batch_size, target_schema)
        sql_worker_instance.worker()


if __name__ == '__main__':
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    DSL: dict = {'dbname': os.getenv('dbname'), 'user': os.getenv('user'), 'password': os.getenv('password'),
                 'host': os.getenv('host'),
                 'port': os.getenv('port')}
    PG_TARGET_SCHEMA: str = 'content'
    BATCH_SIZE: int = 100

    with conn_context('db.sqlite') as sqlite_conn, psycopg2.connect(**DSL,
                                                                    cursor_factory=DictCursor) as pg_conn:
        sqlcursor = sqlite_conn.cursor()
        pg_cursor = pg_conn.cursor()
        main(sqlcursor, pg_cursor, BATCH_SIZE, PG_TARGET_SCHEMA)
