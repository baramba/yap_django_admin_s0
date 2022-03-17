import logging
import os
import sqlite3
from typing import final

import dateutil.parser
import psycopg2
import pytest
from dotenv import load_dotenv
from psycopg2 import OperationalError

sql_count_query = (
    "select count(1) from film_work",
    "select count(1) from genre",
    "select count(1) from genre_film_work",
    "select count(1) from person",
    "select count(1) from person_film_work",
)
sql_data_query = (
    ("select * from film_work", "film_work"),
    ("select * from genre", "genre"),
    ("select * from genre_film_work", "genre_film_work"),
    ("select * from person", "person"),
    ("select * from person_film_work", "person_film_work"),
)


class TestConsMigration(object):
    def setup_class(self):
        load_dotenv()
        self.dsl = {
            "dbname": os.environ.get("DB_NAME"),
            "user": os.environ.get("DB_USER"),
            "password": os.environ.get("DB_PASSWORD"),
            "host": os.environ.get("DB_HOST", "127.0.0.1"),
            "port": os.environ.get("DB_PORT", 5432),
            "options": "-c search_path=content,public",
        }
        self.fetch_size = 100
        path_to_db_file = os.environ.get("PATH_TO_SQLITE")

        try:
            with sqlite3.connect(path_to_db_file) as sq_conn:
                with psycopg2.connect(**self.dsl) as pg_conn:
                    self.pg_cur = pg_conn.cursor()
                    self.sq_cur = sq_conn.cursor()
        except (OperationalError, sqlite3.Error) as err:
            logging.error("Ошибка работы с БД:\n {e}".format(e=err))
            pytest.exit("Ошибка работы с БД: ", returncode=2)

    @pytest.mark.parametrize("sql_query", sql_count_query)
    def test_row_count(self, sql_query):
        pg_count, sq_count = (), ()
        self.pg_cur.execute(sql_query)
        self.sq_cur.execute(sql_query)
        sq_count = self.sq_cur.fetchall()
        pg_count = self.pg_cur.fetchall()
        assert pg_count == sq_count

    def get_next_rows(self):
        while True:
            records = self.pg_cur.fetchmany(size=self.fetch_size)
            if not records:
                break
            yield from records

    def str_to_datetime(self, data_row: dict):
        # приводим строку к datetime
        if "created" in data_row:
            data_row["created"] = dateutil.parser.isoparse(data_row["created"])
        if "modified" in data_row:
            data_row["modified"] = dateutil.parser.isoparse(data_row["modified"])
        if "description" in data_row and data_row["description"] is None:
            data_row["description"] = ""
        return data_row

    @pytest.mark.parametrize("sql_query, table_name", sql_data_query)
    def test_data_cons(self, sql_query, table_name):
        self.pg_cur.execute(sql_query)
        columns_names = ",".join(
            columns_name[0] for columns_name in self.pg_cur.description
        )
        columns = columns_names.split(",")
        # приводим названия колонок к SQLite
        columns_names = columns_names.replace("created", "created_at")
        columns_names = columns_names.replace("modified", "updated_at")
        for pg_result in self.get_next_rows():
            pg_res_dict = dict(zip(columns, pg_result))
            sql_q = "select {cn} from '{tn}' where id='{id}'".format(
                cn=columns_names,
                tn=table_name,
                id=pg_res_dict["id"],
            )
            self.sq_cur.execute(sql_q)
            sq_result = self.sq_cur.fetchone()
            sq_res_dict = dict(zip(columns, sq_result))
            sq_res_dict = self.str_to_datetime(sq_res_dict)
            assert pg_res_dict == sq_res_dict, "id: {id}, table: {t}".format(
                id=pg_res_dict["id"],
                t=table_name,
            )
