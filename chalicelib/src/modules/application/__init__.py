import logging

from pydispatch import dispatcher

from chalicelib.src.modules.application.handlers import CreateIncidentHandler

LOGGER = logging.getLogger('abcall-pqrs-events-microservice')

LOGGER.info("dispatcher connected")

dispatcher.connect(
    CreateIncidentHandler.handle_create_incident,
    signal='CreateIncidentIntegration'
)