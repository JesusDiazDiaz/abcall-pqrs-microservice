from uuid import UUID
import logging
from chalicelib.src.modules.domain.repository import IncidenceRepository
from chalicelib.src.modules.infrastructure.dto import Incidence, IncidenceSchema
from chalicelib.src.config.db import db_session, init_db

LOGGER = logging.getLogger('abcall-pqrs-microservice')


class IncidenceRepositoryPostgres(IncidenceRepository):
    def __init__(self):
        self.db_session = init_db()

    def _close_session(self):
        self.db_session.close()

    def add(self, incidence):
        raise NotImplementedError

    def get(self, id):
        try:
            incidence = self.db_session.query(Incidence).filter_by(id=id).first()
        finally:
            self._close_session()

        if not incidence:
            raise ValueError("Incidence not found")

        return incidence

    def remove(self, entity):
        raise NotImplementedError

    def get_all(self):
        incident_schema = IncidenceSchema(many=True)

        try:
            result = self.db_session.query(Incidence).all()
        finally:
            self._close_session()

        return incident_schema.dump(result)

    def update(self, id, data) -> None:
        raise NotImplementedError
