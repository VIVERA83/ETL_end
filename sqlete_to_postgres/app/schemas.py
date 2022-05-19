from datetime import datetime
from typing import Any, ClassVar, Type

from marshmallow import EXCLUDE, Schema, fields, post_load, pre_load

from .models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork


class BaseSchema(Schema):
    id = fields.UUID(required=True)
    created = fields.DateTime(data_key="created_at")
    Schema: ClassVar[Type[Schema]] = Schema

    @pre_load
    def make(self, data: dict[str, Any], **kwargs):  # noqa

        if isinstance(data.get("created_at"), datetime):
            data["created_at"] = data.get("created_at").isoformat()

        if data.get("updated_at"):
            if isinstance(data.get("updated_at"), datetime):
                data["updated_at"] = data.get("updated_at").isoformat()
        return data

    @post_load
    def make_object(self, data: dict[str, Any], **kwargs):  # noqa
        return self.__model__(**data)  # noqa

    class Meta:
        ordered = True
        unknown = EXCLUDE


class MixinModified:
    modified = fields.DateTime(
        data_key="updated_at",
    )


class FilmWorkSchema(MixinModified, BaseSchema):
    __model__ = FilmWork

    title = fields.Str(required=True)
    description = fields.Str(missing=None)
    creation_date = fields.Date(missing=None)
    rating = fields.Float(allow_none=True)
    type = fields.Str(required=True)


class PersonSchema(MixinModified, BaseSchema):
    __model__ = Person

    full_name = fields.Str(required=True)


class PersonFilmWorkSchema(MixinModified, BaseSchema):
    __model__ = PersonFilmWork

    film_work_id = fields.UUID(required=True)
    person_id = fields.UUID(required=True)
    role = fields.Str(required=True)


class GenreSchema(MixinModified, BaseSchema):
    __model__ = Genre

    name = fields.Str()
    description = fields.Str(allow_none=True)


class GenreFilmWorkSchema(BaseSchema):
    __model__ = GenreFilmWork

    genre_id = fields.UUID(required=True)
    film_work_id = fields.UUID(required=True)
