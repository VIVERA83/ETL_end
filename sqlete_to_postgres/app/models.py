import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Base:
    id: uuid.UUID
    created: datetime.timestamp


@dataclass
class MixinModified:
    modified: datetime.timestamp


@dataclass
class FilmWork(MixinModified, Base):
    title: str
    description: str
    creation_date: str
    rating: float
    type: str


@dataclass
class Person(MixinModified, Base):
    full_name: str


@dataclass
class PersonFilmWork(Base):
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str


@dataclass
class Genre(MixinModified, Base):
    name: str
    description: str


@dataclass
class GenreFilmWork(Base):
    genre_id: uuid.UUID
    film_work_id: uuid.UUID
