from dataclasses import asdict, astuple
from typing import Any
from uuid import UUID

import psycopg2
import logging
from psycopg2.extensions import connection as _connection
from psycopg2.extensions import cursor as _cursor
from psycopg2.extras import DictCursor

psycopg2.extras.register_uuid()


class PostgresSaver:
    def __init__(self, dns: str):
        self.db_name = dns[dns.rfind("/") + 1 :]
        self.conn: _connection = psycopg2.connect(dns, cursor_factory=DictCursor)

    def close(self):
        self.conn.close()
        logging.info(f" PostgresSaver.close: Connecting to the database {self.db_name} closed")

    def find_by_id(self, table_name: str, id_: UUID) -> bool:
        """Поиск записи по id"""
        query = "select * from {} where id = %s;".format(table_name)
        with self.conn.cursor() as cursor:
            try:
                cursor.execute(query=query, vars=[id_])
            except psycopg2.ProgrammingError as ex:
                logging.error(
                    f"Maybe tables: {table_name} not in the database: {self.db_name}, check its availability\n"
                    f"{ex}"
                )
            return bool(cursor.fetchone())

    @staticmethod
    def _get_query(table_name: str, data: Any) -> str:
        """Создает текст sql запроса"""
        fields = ", ".join(asdict(data).keys())
        values = "%s," * len(asdict(data).keys())
        values = values[:-1]
        query = "insert into {table_name} ({fields}) values ({values})".format(
            table_name=table_name, fields=fields, values=values
        )
        return query

    def insert(self, table_name: str, data: list[Any]):
        """Вставка данных в таблицу, пачками"""
        query = self._get_query(table_name, data[0])
        with self.conn as conn, conn.cursor() as cursor:
            cursor: _cursor
            vars_list = [
                astuple(obj) for obj in data if not self.find_by_id(table_name, obj.id)
            ]
            try:
                cursor.executemany(query, vars_list)
            except psycopg2.DatabaseError as ex:
                logging.error(
                    f"Maybe tables: {table_name} not in the database: {self.db_name}, check its availability\n"
                    f"{ex}"
                )
