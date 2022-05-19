import datetime
import uuid
from dataclasses import dataclass, field


@dataclass
class Actor:
    id: uuid
    name: str


@dataclass
class Writer:
    id: uuid
    name: str


@dataclass
class Film:
    id: uuid
    imdb_rating: float
    genre: list[str]
    title: str
    description: str
    director: list[str]
    actors_names: list[str]
    actors_names: str
    writers_names: str
    actors: list[Actor]
    writers: list[Writer]


# ________________

@dataclass
class Genre:
    id: uuid
    name: str
    description: str


@dataclass
class Person:
    id: uuid
    full_name: str


@dataclass
class Delete:
    id: uuid
    field_id: uuid
    table_name: str
    created: datetime.datetime
