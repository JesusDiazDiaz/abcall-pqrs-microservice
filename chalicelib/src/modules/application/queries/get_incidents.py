from dataclasses import dataclass
from chalicelib.src.seedwork.application.queries import Query, QueryResult, execute_query
from chalicelib.src.modules.application.queries.base import QueryBaseHandler
from chalicelib.src.modules.domain.repository import IncidenceRepository


@dataclass
class GetIncidentsQuery(Query):
    ...


class GetIncidentsHandler(QueryBaseHandler):
    def handle(self, query: GetIncidentsQuery):
        repository = self.incidence_factory.create_object(IncidenceRepository.__class__)
        result = repository.get_all()
        return QueryResult(result=result)


@execute_query.register(GetIncidentsQuery)
def execute_get_incidents(query: GetIncidentsQuery):
    handler = GetIncidentsHandler()
    return handler.handle(query)