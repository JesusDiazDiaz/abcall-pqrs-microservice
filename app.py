import json
import logging
from collections import defaultdict, Counter
from datetime import datetime
from io import BytesIO
from statistics import mean

from chalice import Chalice, BadRequestError, CognitoUserPoolAuthorizer, NotFoundError, Response
from openpyxl.workbook import Workbook
from sqlalchemy import and_

from chalicelib.src.modules.application.commands.create_incident import CreateIncidentCommand
from chalicelib.src.modules.application.commands.update_incident import UpdateIncidenceCommand
from chalicelib.src.modules.infrastructure.dto import Base, IncidentType, Status, Incidence
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

    status_counts = Counter(incidence["status"] for incidence in query_result)
    total_incidences = len(query_result)

    percentage_distribution = {
        key: (value / total_incidences) * 100 if total_incidences > 0 else 0
        for key, value in status_counts.items()
    }

    closed_data = [
        incidence for incidence in query_result if incidence["status"] == "CERRADO"
    ]

    closed_per_month = defaultdict(int)
    resolution_times = defaultdict(list)

    for incidence in closed_data:
        close_date = datetime.strptime(incidence["estimated_close_date"], "%Y-%m-%d")
        start_date = datetime.strptime(incidence["date"], "%Y-%m-%d")

        month_key = close_date.strftime("%Y-%m")
        closed_per_month[month_key] += 1
        resolution_times[month_key].append((close_date - start_date).days)

    average_resolution_times = {
        month: mean(times) for month, times in resolution_times.items() if times
    }

    channel_counts = Counter(incidence["channel"] for incidence in query_result if incidence["channel"])

    stats = {
        "total_resolved": status_counts["CERRADO"],
        "total_pending": status_counts["ABIERTO"],
        "total_escalated": status_counts["ESCALADO"],
        "average_resolution_time_per_month": average_resolution_times,
        "closed_incidences_per_month": closed_per_month,
        "distribution": percentage_distribution,
        "incidences_per_channel": channel_counts,
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
    required_fields = ["title", "type", "description", "channel"]
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
        ticket_number=ticket_number,
        channel=incidence_as_json["channel"],
    )

    execute_command(command)

    return {'status': "ok", "ticket_number": ticket_number}


@app.route('/pqrs/stats/report', cors=True, methods=['POST'], authorizer=authorizer)
def download_incidences_report():
    request_data = app.current_request.json_body

    start_date = request_data.get("start_date")
    end_date = request_data.get("end_date")
    incidence_type = request_data.get("incidence_type")

    if not start_date or not end_date or not incidence_type:
        raise BadRequestError("Missing required filters: start_date, end_date, or incidence_type")

    start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")

    incidences_result = execute_query(GetIncidentsQuery(filters={
        "type": incidence_type
    })).result

    filtered_incidences = [
        incidence for incidence in incidences_result
        if start_date_dt <= datetime.strptime(incidence["estimated_close_date"], "%Y-%m-%d") <= end_date_dt
    ]

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Incidences Report"

    headers = [
        "ID", "Status", "Channel", "Type", "Date",
        "Estimated Close Date", "Resolution Time (Days)"
    ]
    sheet.append(headers)

    for incidence in filtered_incidences:
        close_date = datetime.strptime(incidence["estimated_close_date"], "%Y-%m-%d")
        start_date = datetime.strptime(incidence["date"], "%Y-%m-%d")
        resolution_time = (close_date - start_date).days

        sheet.append([
            incidence["id"],
            incidence["status"],
            incidence.get("channel", "N/A"),
            incidence["type"],
            incidence["date"],
            incidence["estimated_close_date"],
            resolution_time
        ])

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return Response(
        body=output.read(),
        status_code=200,
        headers={
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Content-Disposition': 'attachment; filename="incidences_report.xlsx"'
        }
    )


@app.route('/migrate', methods=['POST'])
def migrate():
    try:
        init_db(migrate=True)
        return {"message": "Tablas creadas con éxito"}
    except Exception as e:
        return {"error": str(e)}
