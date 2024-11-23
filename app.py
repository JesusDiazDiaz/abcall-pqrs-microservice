import json
import logging
from collections import defaultdict
from datetime import datetime
from statistics import mean

from chalice import Chalice, BadRequestError, CognitoUserPoolAuthorizer, NotFoundError
from chalicelib.src.modules.application.commands.create_incident import CreateIncidentCommand
from chalicelib.src.modules.application.commands.update_incident import UpdateIncidenceCommand
from chalicelib.src.modules.infrastructure.dto import Base, IncidentType, Status
from chalicelib.src.modules.infrastructure.facades import MicroservicesFacade
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


@app.route('/pqrs/stats', cors=True, authorizer=authorizer)
def incidences_stats():
    query_result = execute_query(GetIncidentsQuery()).result

    status_counts = defaultdict(int)
    closed_per_month = defaultdict(int)
    resolution_times = defaultdict(list)

    for incidence in query_result:
        status_counts[incidence["status"]] += 1

        if incidence["status"] == "CERRADO":
            close_date = datetime.strptime(incidence["estimated_close_date"], "%Y-%m-%d")
            closed_per_month[close_date.strftime("%Y-%m")] += 1

            start_date = datetime.strptime(incidence["date"], "%Y-%m-%d")
            resolution_times[close_date.strftime("%Y-%m")].append((close_date - start_date).days)

    total_incidences = len(query_result)
    percentage_distribution = {
        "ABIERTO": (status_counts["ABIERTO"] / total_incidences) * 100 if total_incidences > 0 else 0,
        "CERRADO": (status_counts["CERRADO"] / total_incidences) * 100 if total_incidences > 0 else 0,
        "ESCALADO": (status_counts["ESCALADO"] / total_incidences) * 100 if total_incidences > 0 else 0,
    }

    average_resolution_times = {
        month: mean(days) for month, days in resolution_times.items() if days
    }

    stats = {
        "total_resolved": status_counts["CERRADO"],
        "total_pending": status_counts["ABIERTO"],
        "total_escalated": status_counts["ESCALADO"],
        "average_resolution_time_per_month": average_resolution_times,
        "closed_incidences_per_month": closed_per_month,
        "distribution": percentage_distribution,
    }

    return stats

@app.route('/pqrs/{incidence_id}/assign', methods=['POST'], cors=True, authorizer=authorizer)
def incidences_assigned(incidence_id):
    user_claims = app.current_request.context['authorizer']['claims']
    user_sub = user_claims.get('sub')

    facade = MicroservicesFacade()
    current_user = facade.get_user(user_sub)

    LOGGER.info("User with role %s assign pqr", current_user["user_role"] )

    if current_user["user_role"] != "Agent":
        raise BadRequestError("User authenticated it's not a agent")

    command = UpdateIncidenceCommand(
        incidence_id=incidence_id,
        data={
            "agent_assigned": current_user["id"],
        }
    )

    execute_command(command)

    return {'status': "ok"}


@app.route('/pqrs/{incidence_id}', methods=['PUT'], cors=True, authorizer=authorizer)
def update_incidence(incidence_id):
    request = app.current_request
    body = request.json_body

    allowed_fields = {"status", "communication_type", "agent_assigned", "channel"}
    invalid_fields = set(body.keys()) - allowed_fields
    if invalid_fields:
        raise BadRequestError(f"Invalid fields provided: {', '.join(invalid_fields)}")

    status_types = [incidenceStatus.name for incidenceStatus in Status]
    if body["status"] not in status_types:
        raise BadRequestError(f"Invalid 'type' value. Must be one of {status_types}")

    if body.get("status") == Status.CERRADO.name:
        body["estimated_close_date"] = datetime.now()

    command = UpdateIncidenceCommand(
        incidence_id=int(incidence_id),
        data=body
    )

    try:
        execute_command(command)
        return {"message": f"Incidence {incidence_id} updated successfully"}
    except ValueError as ve:
        raise BadRequestError(str(ve))
    except Exception as e:
        raise BadRequestError(f"Unexpected error: {str(e)}")


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

    if app.current_request.query_params is not None:
        query_result = execute_query(GetIncidentsQuery(filters={**app.current_request.query_params}))
    else:
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
    user_sub = incidence_as_json.get('user_sub', user_claims.get('sub'))
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
