from dataclasses import field
from datetime import datetime
from typing import Any
from typing import ClassVar, Type
from typing import Literal
from typing import Optional

from marshmallow import Schema
from marshmallow.base import FieldABC
from marshmallow_dataclass import dataclass

PRESCRIPTION = Literal["select", "delete"]


@dataclass
class SqlRequestSchema:
    select: str = ""
    where: str = ""
    group_field: str = ""
    order_field: str = ""
    modified: datetime = None  # fields.DateTime(missing=True, default=datetime(year=2000, month=1, day=1))
    offset: int = 0
    limit: int = 100
    index: str = ""
    prescription: PRESCRIPTION = ""

    Schema: ClassVar[Type[Schema]] = Schema

    @property
    def query(self):
        query = self.select
        if self.modified:
            query += "WHERE " + self.where.format(date=self.modified)
        if self.group_field:
            query += """GROUP BY {field_group} """.format(field_group=self.group_field)
        if self.order_field:
            query += """ORDER BY {field_order} """.format(field_order=self.order_field)
        query += """
        OFFSET {offset}
        LIMIT {limit}
        """.format(
            limit=self.limit, offset=self.offset
        )
        return query


@dataclass
class ModifiedSchema(FieldABC):
    offset: int = 0
    modified: datetime = None
    Schema: ClassVar[Type[Schema]] = Schema


@dataclass
class StateSchema:
    index: Optional[dict[str, ModifiedSchema]] = field(default_factory=dict)
    Schema: ClassVar[Type[Schema]] = Schema

    def update(self, data: dict[str, Any]):
        for index, modified in data.items():
            self.index.update({index: ModifiedSchema.Schema().load(modified)})


if __name__ == "__main__":
    from icecream import ic

    schema_data = {
        "select": """
        SELECT
        fw.id,
        fw.rating as imdb_rating,
        array_agg(DISTINCT g.name) as genre,
        fw.title,
        coalesce(fw.description, '') as description,
        coalesce(array_agg(distinct p.full_name) filter (where pfw."role" = 'director'), '{}') as director,
        coalesce(array_agg(distinct p.full_name) filter (where pfw."role" = 'actor'), '{}') as actors_names, 
        coalesce(array_agg(distinct p.full_name) filter (where pfw."role" = 'writer'), '{}') as writers_names,
        coalesce(json_agg(distinct jsonb_build_object('id', p.id, 'name', p.full_name)) filter (where pfw."role" = 'actor'), '[]') as actors,
        coalesce(json_agg(distinct jsonb_build_object('id', p.id, 'name', p.full_name)) filter (where pfw."role" = 'writer'), '[]') as writers
        FROM content.film_work fw
        LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
        LEFT JOIN content.person p ON p.id = pfw.person_id
        LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
        LEFT JOIN content.genre g ON g.id = gfw.genre_id
        """,
        "where": "fw.modified > '{date}' or g.modified > '{date}' or p.modified > '{date}'",
        "group_field": "fw.id",
        "order_field": "fw.modified",
        "modified": datetime(year=2000, month=1, day=1).isoformat(),
        "offset": 0,
        "limit": 100,
    }

    # ic(datetime(year=2000, month=1, day=1).isoformat())
    # schema_model: SqlRequestSchema = SqlRequestSchema.Schema().load(data=schema_data)
    # print(schema_model.query)

    last_data = [
        {
            # "index": "10",
            # "offset": 0,
            # "modified": None
        },
        {
            "index": "12",
            "offset": 110,
            "modified": datetime(datetime.now().year, datetime.now().month, datetime.now().day).isoformat(),
        }, ]
    last_data = {
        "index": {
            "person":
                {
                    'modified': datetime(datetime.now().year, datetime.now().month, datetime.now().day).isoformat(),
                    # 'offset': 10
                },
            "genre":
                {'modified': datetime(datetime.now().year, datetime.now().month, datetime.now().day).isoformat(),
                 'offset': 10}
        },
    }
    # last_data = {}
    # ic(datetime(2000, 1, 1).isoformat())
    # last_data = {}
    obj: StateSchema = StateSchema.Schema().load(last_data)
    # ic(type(obj.index.get("person").modified))
    ic(obj.index.get("person"))
    obj.update({"genre": {
        "index": "112",
        "offset": 111111111111,
        "modified": datetime(datetime.now().year, datetime.now().month, datetime.now().day),
    }})

    # ic(StateSchema.Schema().load(obj))
    ic(obj)
    a = obj.index.get("genre")
    a.modified = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
    ic(obj.Schema().dump(obj), a)

a = {
    "index": {
        "index": {
            "genre": {
                "modified": "null",
                "offset": 100
            },
            "person": {
                "modified": "null",
                "offset": 1500
            }
        }
    }
}
