import logging
import json
from dataclasses import dataclass

from datetime import datetime
from pydispatch import dispatcher
from chalicelib.src.modules.application.commands.base import CommandBaseHandler
from chalicelib.src.seedwork.application.commands import execute_command
from chalicelib.src.seedwork.application.commands import Command

LOGGER = logging.getLogger('abcall-pqrs-events-microservice')


@dataclass
class CreateIncidentCommand(Command):
    type: str
    title: str
    description: str
    date: datetime
    user_sub: str


class UpdateInformationHandler(CommandBaseHandler):
    def handle(self, command: CreateIncidentCommand):
        LOGGER.info("Handle createIncidentCommand")

        event = {
            "type": command.type,
            "title": command.title,
            "description": command.description,
            "date": command.date.timestamp(),
            "user_sub": command.user_sub
        }
        dispatcher.send(signal='CreateIncidentIntegration', event=json.dumps(event))


@execute_command.register(CreateIncidentCommand)
def execute_update_information_command(command:  CreateIncidentCommand):
    handler = UpdateInformationHandler()
    handler.handle(command)
