import json
import logging
import os

from redis import Redis

from elasticsearch.elasticsearch import BaseElasticsearch
from helpers.backoff import before_execution
from helpers.state import State, RedisStorage
from postgres.create_table import create_table
from postgres.postgresextractor import PostgresExtractor
from postgres.schema import SqlRequestSchema
from postgres_to_es import load_from_postgres_to_elastic
from schema.schema import GenreSchema, PersonSchema, FilmSchema, DeleteSchema
from sql import SQL_GENRE, SQL_MOVIES, SQL_PERSON, SQL_DELETE

if __name__ == "__main__":
    # load_dotenv()
    logging.basicConfig(level=logging.INFO)
    filename = "elasticsearch/movies_es_schema.json"
    index = "movies"

    # создаем индекс movies
    with open(filename, "r", encoding="utf-8") as file:
        schema_movies: dict = json.loads(file.read())
    es = BaseElasticsearch(host=os.getenv("ELASTIC_HOST", "127.0.0.1"))
    before_execution()(es.create_index)(index, schema_movies)

    # создаем индекс person
    with open("elasticsearch/person_es_schema.json", "r", encoding="utf-8") as file:
        schema_movies: dict = json.loads(file.read())
    es = BaseElasticsearch(host=os.getenv("ELASTIC_HOST", "127.0.0.1"))
    before_execution()(es.create_index)("person", schema_movies)

    # Postgres, добавляем необходимые функции, и триггеры, и так на всякий случай таблицы.
    create_table(os.getenv("POSTGRES_DSN"))

    pg = PostgresExtractor(os.getenv("POSTGRES_DSN", "postgres://app:123qwe@127.0.0.1:5432/movies_database"))
    state = State(RedisStorage(Redis(os.getenv("REDIS_HOST", "127.0.0.1"))))

    sql_requests = SqlRequestSchema.Schema().load(data=[SQL_GENRE, SQL_MOVIES, SQL_PERSON, SQL_DELETE], many=True)
    load_from_postgres_to_elastic(state, es, pg, sql_requests, [GenreSchema, FilmSchema, PersonSchema, DeleteSchema])
