import logging
from chalicelib.src.modules.infrastructure.dispatchers import Dispatcher
from chalicelib.src.seedwork.application.handlers import Handler

LOGGER = logging.getLogger('abcall-pqrs-events-microservice')


class CreateIncidentHandler(Handler):

    @staticmethod
    def handle_create_incident(event):
        LOGGER.info("handle create incident and send event to dispatcher")

        dispatcher = Dispatcher()
        dispatcher.publish_command(event)