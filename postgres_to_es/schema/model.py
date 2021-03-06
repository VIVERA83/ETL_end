import datetime
import uuid
from dataclasses import dataclass
from typing import Optional

@dataclass
class Actor:
    id: uuid
    name: str


@dataclass
class Writer:
    id: uuid
    name: str


@dataclass
class Genre:
    id: uuid
    name: str
    description: Optional[str] = None


@dataclass
class Film:
    id: uuid
    imdb_rating: float
    genre: list[Genre]
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
class Person:
    id: uuid
    full_name: str
    birth_date: datetime.datetime
    role: str
    film_ids: list[uuid]


@dataclass
class Delete:
    id: uuid
    field_id: uuid
    table_name: str
    created: datetime.datetime
