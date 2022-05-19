import logging
from datetime import datetime

from icecream import ic
from marshmallow_dataclass import dataclass

from elasticsearch.elasticsearch import BaseElasticsearch
from helpers.backoff import backoff
from helpers.state import State
from postgres.postgresextractor import PostgresExtractor
from postgres.schema import SqlRequestSchema, StateSchema

ic.includeContext = True


def create_objects(chang: list[dict], schema: dataclass) -> list[dataclass]:
    field_names = [name for name in chang[0].keys()]
    data = [{key: item[key] for key in field_names} for item in chang]
    return schema().load(data, many=True)


@backoff(start_sleep_time=10, logging_level=logging.CRITICAL)
def load_from_postgres_to_elastic(state: State,
                                  es: BaseElasticsearch,
                                  pg: PostgresExtractor,
                                  sql_requests: list[SqlRequestSchema],
                                  schema: list[dataclass]):
    for sql_request, schema in zip(sql_requests, schema, ):
        state_data: StateSchema = StateSchema.Schema().load({"index": state.get_state("index")})
        index = state_data.index.get(sql_request.index)
        sql_request.modified = index.modified if index else None
        sql_request.offset = index.offset if index else 0
        flag = False
        for chang in pg.execute(sql_request):

            if chang:
                flag = True
                objs = create_objects(chang, schema)

                match sql_request.prescription:
                    case "select":
                        es.insert_many(sql_request.index, schema().dump(objs, many=True))
                        logging.info(
                            f" load_from_postgres_to_elastic: Создано {len(objs)} записей в {sql_request.index.upper()}")
                    case "delete":
                        obj = None
                        count = 0
                        for count, obj in enumerate(objs):
                            ic(es.delete_document_by_id(obj.table_name, obj.field_id))
                            logging.info(f" Удалена запись из {obj.table_name.upper()}, id = {obj.field_id}")
                        logging.info(f" Всего удалено записей из {obj.table_name.upper()}, {count + 1}")
                    case _:
                        logging.info(f"load_from_postgres_to_elastic {index=}")

                state_data.update(
                    {sql_request.index: sql_request.Schema(only={"modified", "offset"}).dump(sql_request)})
                state.set_state("index", state_data.Schema().dump(state_data).get("index"))

        if flag:
            sql_request.offset = 0
            sql_request.modified = datetime.now()
            state_data.update({sql_request.index: sql_request.Schema(only={"modified", "offset"}).dump(sql_request)})
            state.set_state("index", state_data.Schema().dump(state_data).get("index"))
