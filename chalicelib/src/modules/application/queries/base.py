from chalicelib.src.modules.infrastructure.factory import IncidenceFactory
from chalicelib.src.seedwork.application.commands import CommandHandler
from chalicelib.src.seedwork.application.queries import QueryHandler


class QueryBaseHandler(QueryHandler):
    def __init__(self):
        self._incidence_factory: IncidenceFactory = IncidenceFactory()

    @property
    def incidence_factory(self):
        return self._incidence_factory
