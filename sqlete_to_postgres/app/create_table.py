from psycopg2.extensions import connection as _connection
from psycopg2.extensions import cursor as _cursor
import logging


def create_table(pg_connect: _connection):
    """Создание новых таблиц"""
    with open("app/movies_database.ddl") as file:
        sql = file.read()

    with pg_connect as conn, conn.cursor() as pg_cursor:
        pg_cursor: _cursor
        pg_cursor.execute(sql)
    logging.info(" create_table: Tables created")
