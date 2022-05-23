import logging

import psycopg2


def create_table(dns: str):
    """Создание новых таблиц"""
    with open("postgres/movies_database.ddl") as file:
        sql = file.read()

    with psycopg2.connect(dns).cursor() as cursor:
        print(sql)
        try:
            cursor.execute(query=sql)
        except psycopg2.ProgrammingError as e:
            logging.error(f" create_table: {e.pgerror}")
        logging.info(" create_table: Таблицы созданы, созданы НЕОБХОДИМЫЕ ФЦНКЦИИ И ТРИГЕРЫ")
