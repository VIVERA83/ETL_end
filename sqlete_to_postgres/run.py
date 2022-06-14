import os
from app.load_data import load_from_sqlite, TABLE
from app.create_table import create_table
import logging
import psycopg2
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    logging.info(" Getting started creating tables in POSTGRES")
    pg_con = psycopg2.connect(dsn=os.getenv("POSTGRES_DSN"))

    try:
        create_table(pg_con)
    except Exception as er:
        print(er)

    logging.info(f" Current folder {os.getcwd() + ' app/db.sqlite'}")
    logging.info(" Start uploading data to POSTGRES")
    load_from_sqlite(os.getenv("POSTGRES_DSN"), "app/db.sqlite", TABLE)
    logging.info(" Uploading data to POSTGRES completed")
