from functools import singledispatch
from abc import ABC, abstractmethod
from dataclasses import dataclass


class Query(ABC):
    ...


@dataclass
class QueryResult:
    result: any


class QueryHandler(ABC):
    @abstractmethod
    def handle(self, query: Query) -> QueryResult:
        raise NotImplementedError()


@singledispatch
def execute_query(query):
    raise NotImplementedError(f'No implementation exists for the query type {type(query).__name__}')
