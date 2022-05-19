import sqlite3
from typing import Generator


class SQLiteLoader:
    def __init__(
        self,
        db_name: str,
    ):
        self.db_name = db_name
        self.connect = sqlite3.connect(db_name)
        self.connect.row_factory = sqlite3.Row

    def get_data(self, table_name: str, limit=50) -> Generator:
        """Возвращает генератор с результатами запроса по всей таблице

        Args:
             limit: количество выдуваемых элементов за одно общение,
             table_name: имя таблицы в БД.

        Returns:
         Генератор
        """
        with self.connect as cursor:
            count = cursor.execute(
                "select count() from {table_name}".format(
                    table_name=table_name,
                ),
            ).fetchone()[0]
            for offset in range(0, count, limit):
                quare = (
                    "select * from {table_name} limit {limit} offset {offset}".format(
                        table_name=table_name,
                        limit=limit,
                        offset=offset,
                    )
                )
                yield cursor.execute(quare).fetchall()

    def close(self):
        """Закрывает соединение с БД."""
        self.connect.close()
