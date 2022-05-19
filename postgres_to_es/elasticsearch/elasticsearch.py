import json
import logging
import uuid
from typing import Any

import requests


class BaseElasticsearch:
    __HEADERS = {"Content-Type": "application/json"}
    __SEARCH = "_search/"
    __DOC = "_doc/"
    __REFRESH = "_refresh"
    __BULK = "_bulk"
    __CAT = "_cat"
    __COUNT = "_count"

    def __init__(
            self,
            host: str = "localhost",
            port: int = 9200,
    ):
        self.base_url = "http://{host}:{port}".format(host=host, port=port)
        self.logging = logging.getLogger()

    def create_index(self, index: str, schema: dict = None):
        url = self._create_url(index)
        return requests.put(
            url=url, data=json.dumps(schema), headers=self.__HEADERS
        ).json()

    def delete_index(self, index: str, query: str = ""):
        url = self._create_url(index, query=query)
        return requests.delete(url=url, headers=self.__HEADERS).json()

    def delete_document_by_id(self, index: str, id: str):
        url = self._create_url(index=index, uri=self.__DOC, query=id)
        return requests.delete(url=url, headers=self.__HEADERS).json()

    def show_all_index(self, query: str = "") -> str:
        url = f"{self.base_url}/{self.__CAT}/indices/{query}"
        return requests.get(url=url, headers=self.__HEADERS).content.decode(
            encoding="utf-8"
        )

    def select_by_id(self, index: str, id: str) -> dict:  # noqa
        """
        Выборка по id
        :param id:
        :return: словарь с результатом поиска
        """
        uri = self.__DOC + id
        url = self._create_url(
            index,
            uri=uri,
        )
        return requests.get(url=url, headers=self.__HEADERS).json()

    def select(self, index: str, schema: dict = None):
        url = self._create_url(index, self.__SEARCH)
        if not schema:
            schema = {}
        return requests.get(
            url=url, data=json.dumps(schema), headers=self.__HEADERS
        ).json()

    def insert_one(
            self, index: str, data: dict[str, Any] = None, query: str = ""
    ) -> dict:
        # if not data:
        #     data = {}
        url = self._create_url(index, self.__DOC, query=query)
        result = requests.post(
            url=url, data=json.dumps(data), headers=self.__HEADERS
        ).json()
        self._refresh(index)
        return result

    def insert_many(self, index, data: list[dict], query: str = ""):
        # "?filter_path=items.*.error" - в ответ вернет только те записи которы ене попали в бд
        url = self._create_url(index, self.__BULK, query=query)
        st = ""
        for record in data:
            meta_data = {
                "index": {"_index": index, "_id": record.get("id", uuid.uuid4().hex)}
            }
            st += json.dumps(meta_data) + "\n" + json.dumps(record) + "\n"

        return requests.post(url, data=st, headers=self.__HEADERS).json()

    def _create_url(self, index: str, uri: str = "", query: str = "") -> str:
        """
        служебный метод который формирует url для запроса в elastic
        :param uri:
        :return:
        """
        url = f"{self.base_url}/{index}/{uri}{query}"
        self.logging.info(url)
        return url

    def _refresh(self, index: str) -> dict:
        url = self._create_url(index, self.__REFRESH)
        return requests.get(url).json()

    def get_count_documents(self, index) -> int or None:
        url = self._create_url(index, uri=self.__COUNT)
        result: dict = requests.get(url, headers=self.__HEADERS).json()
        return result.get("count")

