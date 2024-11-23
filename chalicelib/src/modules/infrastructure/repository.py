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

    def get_all(self, filters=None):
        incident_schema = IncidenceSchema(many=True)

        try:
            query = self.db_session.query(Incidence)

            if filters:
                query = query.filter_by(**filters)

            result = query.all()
        finally:
            self._close_session()

        return incident_schema.dump(result)

    def update(self, id, data) -> None:
        raise NotImplementedError

    def update(self, id, data) -> None:
        try:
            incidence = self.db_session.query(Incidence).filter_by(id=id).first()

            if not incidence:
                raise ValueError(f"Incidence with ID {id} not found.")

            for key, value in data.items():
                if hasattr(incidence, key):
                    setattr(incidence, key, value)
                else:
                    LOGGER.warning(f"Field {key} does not exist in Incidence model and was ignored.")

            self.db_session.commit()
            LOGGER.info(f"Incidence with ID {id} updated successfully.")
        except Exception as e:
            self.db_session.rollback()
            LOGGER.error(f"Error updating incidence with ID {id}: {str(e)}")
            raise e
        finally:
            self._close_session()
