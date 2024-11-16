import json
import logging
from datetime import datetime

from chalice import Chalice, BadRequestError, CognitoUserPoolAuthorizer, NotFoundError
from chalicelib.src.modules.application.commands.create_incident import CreateIncidentCommand
from chalicelib.src.modules.infrastructure.dto import Base, IncidentType
from chalicelib.src.seedwork.application.commands import execute_command
from chalicelib.src.config.db import init_db, engine
from chalicelib.src.seedwork.application.queries import execute_query
from chalicelib.src.modules.application.queries.get_incidents import GetIncidentsQuery

app = Chalice(app_name='abcall-pqrs-microservice')
app.debug = True

LOGGER = logging.getLogger('abcall-pqrs-events-microservice')


authorizer = CognitoUserPoolAuthorizer(
    'AbcPool',
    provider_arns=['arn:aws:cognito-idp:us-east-1:044162189377:userpool/us-east-1_YDIpg1HiU']
)

@app.route('/pqrs/assigned', cors=True, authorizer=authorizer)
def incidences_assigned():
    user_claims = app.current_request.context['authorizer']['claims']
    user_sub = user_claims.get('sub')

    query_result = execute_query(GetIncidentsQuery(filters={"user_sub": user_sub}))
    return query_result.result


@app.route('/pqrs/assigned/{ticket_number}', cors=True, authorizer=authorizer)
def get_incidence_by_ticket_number(ticket_number):
    user_claims = app.current_request.context['authorizer']['claims']
    user_sub = user_claims.get('sub')

    query_result = execute_query(GetIncidentsQuery(filters={"ticket_number": ticket_number, "user_sub": user_sub}))

    if not query_result.result:
        raise NotFoundError(f"Incidence with ticket_number {ticket_number} not found")

    return query_result.result


@app.route('/pqrs/{incidence_id}', cors=True)
def get_incidence_by_id(incidence_id):
    query_result = execute_query(GetIncidentsQuery(filters={"id": incidence_id}))

    if not query_result.result:
        raise NotFoundError(f"Incidence with incidence_id {incidence_id} not found")

    return query_result.result


@app.route('/pqrs', cors=True, authorizer=authorizer)
def incidences():
    user_claims = app.current_request.context['authorizer']['claims']
    user_id = user_claims.get('sub')
    email = user_claims.get('email')

    LOGGER.info(f"test cd")

    user_role = user_claims.get('custom:custom:userRole', None)
    LOGGER.info(f"User {email} get incidences, userId: {user_id} with role `{user_role}`")

    query_result = execute_query(GetIncidentsQuery())
    return query_result.result


@app.route('/pqrs', methods=['POST'], cors=True, authorizer=authorizer)
def incidence_post():
    incidence_as_json = app.current_request.json_body

    LOGGER.info("Receive create incident request")
    required_fields = ["title", "type", "description"]
    for field in required_fields:
        if field not in incidence_as_json:
            raise BadRequestError(f"Missing required field: {field}")

    valid_types = [incident.value for incident in IncidentType]
    if incidence_as_json["type"] not in valid_types:
        raise BadRequestError(f"Invalid 'type' value. Must be one of {valid_types}")

    user_claims = app.current_request.context['authorizer']['claims']
    user_sub = user_claims.get('sub')
    email = user_claims.get('email')

    LOGGER.info(f"User {email} create incidence, userId: {user_sub}")

    ticket_number = CreateIncidentCommand.generate_ticket_number()

    command = CreateIncidentCommand(
        title=incidence_as_json["title"],
        type=incidence_as_json["type"],
        description=incidence_as_json["description"],
        date=datetime.now(),
        user_sub=user_sub,
        ticket_number=ticket_number
    )

    execute_command(command)

    return {'status': "ok", "ticket_number": ticket_number}


@app.route('/migrate', methods=['POST'])
def migrate():
    try:
        init_db(migrate=True)
        return {"message": "Tablas creadas con éxito"}
    except Exception as e:
        return {"error": str(e)}
