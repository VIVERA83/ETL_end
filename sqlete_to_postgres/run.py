import os
from app.load_data import load_from_sqlite, TABLE
from app.create_table import create_table
import logging
import psycopg2
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    logging.info(" Начало создаем таблицы в POSTGRES")
    pg_con = psycopg2.connect(dsn=os.getenv("POSTGRES_DSN"))
    # create_table(pg_con)

    logging.info(f" текущая папка {os.getcwd()+' app/db.sqlite'}")
    logging.info(" Начало загрузки данных в POSTGRES")
    load_from_sqlite(os.getenv("POSTGRES_DSN"), "app/db.sqlite", TABLE)
    logging.info(" Загрузка данных в POSTGRES завершена")
