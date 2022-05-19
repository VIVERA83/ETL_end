import logging
from typing import Generator, TYPE_CHECKING

if TYPE_CHECKING:
    from schema import SqlRequestSchema

import psycopg2
from psycopg2.extras import DictCursor


class PostgresExtractor:
    def __init__(self, dns: str):
        self.dns = dns
        self.db_name = dns[dns.rfind("/") + 1:]

    def execute(self, sql: "SqlRequestSchema") -> Generator:
        with psycopg2.connect(self.dns).cursor(cursor_factory=DictCursor) as cursor:
            while True:
                cursor.execute(query=sql.query)
                sql.offset += sql.limit
                if data := cursor.fetchall():
                    yield data
                else:
                    logging.info("Выгрузка таблицы окончена")
                    return []
