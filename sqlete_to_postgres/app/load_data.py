import logging
from marshmallow.schema import SchemaMeta
from .postgres_saver import PostgresSaver
from .sqlite_loader import SQLiteLoader
from .schemas import (
    FilmWorkSchema,
    GenreFilmWorkSchema,
    GenreSchema,
    PersonFilmWorkSchema,
    PersonSchema,
)

TABLE = {
    "film_work": FilmWorkSchema,
    "person": PersonSchema,
    "person_film_work": PersonFilmWorkSchema,
    "genre": GenreSchema,
    "genre_film_work": GenreFilmWorkSchema,
}


def load_from_sqlite(
        dsn_postgres: str, sql_db_path: str, tables: dict[str, SchemaMeta]
):
    sqlite_loader = SQLiteLoader(sql_db_path)
    postgres_saver = PostgresSaver(dsn_postgres)

    for table_name, schema in tables.items():
        count_records = 0
        for records in sqlite_loader.get_data(table_name):
            obj = [schema().load(data=dict(record)) for record in records]
            postgres_saver.insert(table_name, obj)
            count_records += len(records)
        logging.info(f" load_from_sqlite: в {table_name.upper()} загружено {count_records} записей")
    sqlite_loader.close()
    postgres_saver.close()
