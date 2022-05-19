import json
import logging
import os

from dotenv import load_dotenv
from redis import Redis

from elasticsearch.elasticsearch import BaseElasticsearch
from helpers.backoff import before_execution
from helpers.state import State, RedisStorage
from postgres.postgresextractor import PostgresExtractor
from postgres.schema import SqlRequestSchema
from postgres_to_es import load_from_postgres_to_elastic
from schema.schema import GenreSchema, PersonSchema, FilmSchema, DeleteSchema
from sql import SQL_GENRE, SQL_MOVIES, SQL_PERSON, SQL_DELETE

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    filename = "elasticsearch/movies_es_schema.json"
    index = "movies"

    with open(filename, "r", encoding="utf-8") as file:
        schema_movies: dict = json.loads(file.read())
    es = BaseElasticsearch(host=os.getenv("ELASTIC_HOST"))

    before_execution()(es.create_index)(index, schema_movies)

    pg = PostgresExtractor(os.getenv("POSTGRES_DSN"))
    state = State(RedisStorage(Redis(os.getenv("REDIS_HOST"))))

    sql_requests = SqlRequestSchema.Schema().load(data=[SQL_GENRE, SQL_MOVIES, SQL_PERSON, SQL_DELETE], many=True)
    load_from_postgres_to_elastic(state, es, pg, sql_requests, [GenreSchema, FilmSchema, PersonSchema, DeleteSchema])
