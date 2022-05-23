import logging

import psycopg2


def create_table(dns: str):
    """Создание новых таблиц"""
    with open("postgres/movies_database.ddl") as file:
        sql = file.read()

    pg_connect = psycopg2.connect(dns)
    with pg_connect as conn, conn.cursor() as pg_cursor:
        try:
            pg_cursor.execute(sql)
        except psycopg2.ProgrammingError as e:
            logging.error(f" create_table: {e.pgerror}")
            return
        logging.info(" create_table: Таблицы созданы, созданы НЕОБХОДИМЫЕ ФЦНКЦИИ И ТРИГЕРЫ")
