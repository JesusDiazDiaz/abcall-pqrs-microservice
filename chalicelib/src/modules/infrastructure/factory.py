from dataclasses import dataclass
from chalicelib.src.seedwork.domain.factory import Factory
from chalicelib.src.seedwork.domain.repository import Repository
from chalicelib.src.modules.domain.repository import IncidenceRepository
from .exceptions import ImplementationNotExistsForFactoryException
from .repository import IncidenceRepositoryPostgres


@dataclass
class IncidenceFactory(Factory):
    def create_object(self, obj: type, mapper: any = None) -> Repository:
        if obj == IncidenceRepository.__class__:
            return IncidenceRepositoryPostgres()

        raise ImplementationNotExistsForFactoryException()