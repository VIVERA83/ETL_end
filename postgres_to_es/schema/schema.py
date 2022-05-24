import datetime
import uuid
from datetime import datetime
from typing import Any, ClassVar, Type

from marshmallow import EXCLUDE, Schema, fields, post_load, pre_load

from .model import Actor, Writer, Film, Genre, Person, Delete


class BaseSchema(Schema):
    id = fields.UUID(allow_none=True, default=uuid.uuid4().hex)
    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        ordered = True
        unknown = EXCLUDE

    @post_load
    def make_object(self, data: dict[str, Any], **kwargs):  # noqa
        return self.__model__(**data)  # noqa


class ActorSchema(BaseSchema):
    __model__ = Actor
    name = fields.Str(allow_none=True)


class WriterSchema(BaseSchema):
    __model__ = Writer
    name = fields.Str(allow_none=True)


class FilmSchema(BaseSchema):
    __model__ = Film
    imdb_rating = fields.Float(allow_none=True)
    genre = fields.List(fields.Str(allow_none=True))
    title = fields.Str()
    description = fields.Str()
    director = fields.List(fields.Str(allow_none=True))
    actors_names = fields.List(fields.Str(allow_none=True))
    writers_names = fields.List(fields.Str(allow_none=True))
    actors = fields.List(fields.Nested(ActorSchema))
    writers = fields.List(fields.Nested(WriterSchema))


class GenreSchema(BaseSchema):
    __model__ = Genre

    name = fields.Str()
    description = fields.Str(allow_none=True)


class PersonSchema(BaseSchema):
    __model__ = Person

    full_name = fields.Str(required=True)
    birth_date = fields.Date(allow_none=True)
    role = fields.Str(allow_none=True)
    film_ids = fields.List(fields.Str(allow_none=True), allow_none=True)

    @pre_load
    def make(self, data: dict[str, Any], **kwargs):  # noqa
        if role := data.get("role"):
            data["role"] = ", ".join(role)
        else:
            data["role"] = None

        if films_ids := data.get("film_ids"):
            data["film_ids"] = films_ids.split(",")
        else:
            data["film_ids"] = None

        if not data.get("birth_date"):
            data["birth_date"] = None

        return data


class DeleteSchema(BaseSchema):
    __model__ = Delete
    field_id = fields.UUID()
    table_name = fields.Str()
    created = fields.DateTime()

    @pre_load
    def make(self, data: dict[str, Any], **kwargs):  # noqa

        if isinstance(data.get("created"), datetime):
            data["created"] = data.get("created").isoformat()
            if data.get("table_name") == "film_work":
                data["table_name"] = "movies"

        return data
