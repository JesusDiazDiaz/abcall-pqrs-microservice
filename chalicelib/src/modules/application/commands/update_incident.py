import logging
from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict

from chalicelib.src.modules.application.commands.base import CommandBaseHandler
from chalicelib.src.seedwork.application.commands import execute_command
from chalicelib.src.seedwork.application.commands import Command
from chalicelib.src.modules.domain.repository import IncidenceRepository

LOGGER = logging.getLogger('abcall-pqrs-events-microservice')


@dataclass
class UpdateIncidenceCommand(Command):
    incidence_id: int
    data: dict


class UpdateIncidenceHandler(CommandBaseHandler):
    def handle(self, command: UpdateIncidenceCommand):
        LOGGER.info(f"Handling UpdateIncidenceCommand for ID {command.incidence_id}")

        repository = self.incidence_factory.create_object(IncidenceRepository.__class__)

        try:
            repository.update(command.incidence_id, command.data)
            LOGGER.info(f"Incidence with ID {command.incidence_id} updated successfully.")
        except ValueError as ve:
            LOGGER.error(f"Update failed: {str(ve)}")
            raise ve
        except Exception as e:
            LOGGER.error(f"Unexpected error during update: {str(e)}")
            raise e


@execute_command.register(UpdateIncidenceCommand)
def execute_update_incidence_command(command: UpdateIncidenceCommand):
    handler = UpdateIncidenceHandler()
    handler.handle(command)
