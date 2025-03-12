from abc import ABC, abstractmethod
from functools import singledispatchmethod

from pydantic import BaseModel, Field

from pysota.core import Publication, ResultPage
from pysota.core.query import IQuery


class Provider(ABC, BaseModel):
    name: str = Field(...)

    @abstractmethod
    def extract_items(self, payload, query: IQuery) -> list[Publication]:
        raise NotImplementedError

    @singledispatchmethod
    @abstractmethod
    def search(self) -> ResultPage:
        raise NotImplementedError

    @abstractmethod
    def search_next(self, result_page: ResultPage) -> ResultPage:
        raise NotImplementedError

    def log(self, msg) -> None:
        print(f'- {msg}')
