"""Миграция данных из SQLite в Postgres."""

import logging
import os
import sqlite3
from contextlib import contextmanager

import psycopg2
from dotenv import load_dotenv
from psycopg2 import OperationalError
from psycopg2.extensions import cursor as _cursor
from psycopg2.extras import DictCursor, execute_values

from structures import TABLES


class PostgresSaver(object):
    """Класс для загрузки данных о фильмах в Postgres."""

    def __init__(self, pg_cur: _cursor):
        self.cursor = pg_cur
        self._rows_data = []

    def save_all_data(self, movies_data: list):
        """save_all_data сохраняет данные в Postgres.

        Arguments:
            movies_data -- список обьектов для сохранения в Posgres.
        """
        self._rows_data = []
        columns_name = ",".join(movies_data[0].get_fields())
        table_name = movies_data[0].table_name()
        for record in movies_data:
            self._rows_data.append(record.get_as_tuple())

        sql_query = "INSERT INTO content.{tb} ({cols}) VALUES %s ON CONFLICT (id) DO NOTHING;".format(
            tb=table_name,
            cols=columns_name,
        )
        execute_values(self.cursor, sql_query, self._rows_data)


class SQLiteLoader(object):
    """класс для загрузки данных из SQLite."""

    def __init__(self, sq_conn: sqlite3.Cursor, fetch_size: int):
        self.fetch_size = fetch_size
        self.cursor = sq_cur

    def get_rows_gen(self):
        """get_row_gen генератор для чтения данных из БД по self.fetch_size записей.

        Yields:
            генератор для получения данных из SQLite
        """

        for table_class in TABLES:
            table = table_class()
            fields = table.get_fields()
            columns = ",".join(fields)
            # Приведение названий полей к названиям в SQLite
            columns = columns.replace("created", "created_at")
            columns = columns.replace("modified", "updated_at")

            sql_query = "select {} from {}".format(columns, table.table_name())
            self.cursor.execute(sql_query)

            while True:
                rows_data = []
                kwargs = {}
                records = self.cursor.fetchmany(size=self.fetch_size)
                if not records:
                    break
                for record in records:
                    for key in fields:
                        kwargs[key] = record[fields.index(key)]
                    rows_data.append(table_class(**kwargs))
                yield rows_data

    def load_movies(self):
        """load_movies Загружает данные из SQLite в классы соответсвуюшие классы.

        Yields:
            генератор на порцию записей из таблицы
        """
        yield from self.get_rows_gen()


def load_from_sqlite(sq_cur: sqlite3.Cursor, pg_cur: _cursor):
    """Основной метод загрузки данных из SQLite."""

    fetch_size = 1000
    postgres_saver = PostgresSaver(pg_cur)
    sqlite_loader = SQLiteLoader(sq_cur, fetch_size)
    for movies_data in sqlite_loader.load_movies():
        postgres_saver.save_all_data(movies_data)


@contextmanager
def open_sqlite(file_name: str):
    conn = sqlite3.connect(file_name)
    try:
        logging.info("Creating connection to SQLite")
        yield conn.cursor()
    finally:
        logging.info("Closing connection to SQLite")
        conn.commit()
        conn.close()


@contextmanager
def open_postgres(dsl: dict):
    conn = psycopg2.connect(**dsl, cursor_factory=DictCursor)
    try:
        logging.info("Creating connection to Postgres")
        yield conn.cursor()
    finally:
        logging.info("Closing connection to Postgres")
        conn.commit()
        conn.close()


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    dsl = {
        "dbname": os.environ.get("DB_NAME"),
        "user": os.environ.get("DB_USER"),
        "password": os.environ.get("DB_PASSWORD"),
        "host": os.environ.get("DB_HOST", "127.0.0.1"),
        "port": os.environ.get("DB_PORT", 5432),
    }
    workdir = os.path.dirname(__file__)
    path_to_db_file = workdir + "/db.sqlite"
    try:
        with open_sqlite(path_to_db_file) as sq_cur:
            with open_postgres(dsl) as pg_cur:
                load_from_sqlite(sq_cur, pg_cur)
    except (OperationalError, sqlite3.Error) as err:
        logging.error("Ошибка работы с БД:\n {e}".format(e=err))
