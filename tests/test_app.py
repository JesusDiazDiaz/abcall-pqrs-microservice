import json
from datetime import datetime
from unittest import mock
from unittest.mock import patch, MagicMock

from chalice.test import Client
from chalice import NotFoundError
from app import app


def test_get_incidences():
    mock_context = {
        'authorizer': {
            'claims': {
                'sub': 'user123',
                'email': 'user@example.com',
                'custom:custom:userRole': 'admin'
            }
        }
    }

    mock_incidents = [
        {
            "id": 1,
            "client_id": 2,
            "subject": "Incident 1",
            "description": "test",
            "status": "ABIERTO",
            "date": "2024-10-20",
            "estimated_close_date": "2024-10-28",
            "user_sub": "72c16f9f-5f13-439b-bf09-7440edd16086",
            "type": "PETICION",
            "communication_type": "SMS"
        }
    ]

    mock_request = MagicMock()
    mock_request.context = mock_context
    mock_request.headers = {
        'Content-Type': 'application/json'
    }

    with patch('chalice.app.Request', return_value=mock_request):
        with patch('chalicelib.src.modules.infrastructure.repository.IncidenceRepositoryPostgres.get_all', return_value=mock_incidents):
            with Client(app) as client:
                response = client.http.get('/pqrs')

                assert response.status_code == 200

                response_data = json.loads(response.body)
                assert response_data == mock_incidents


def test_incidence_post():
    with Client(app) as client:
        request_body = {
            "title": "Network issue",
            "type": "Peticion",
            "description": "The network is down",
        }

        mock_context = {
            'authorizer': {
                'claims': {
                    'sub': 'user123',
                    'email': 'user@example.com'
                }
            }
        }

        mock_request = MagicMock()
        mock_request.json_body = request_body
        mock_request.context = mock_context
        mock_request.headers = {
            'Content-Type': 'application/json'
        }

        with patch('chalice.app.Request', return_value=mock_request):
            with patch('chalicelib.src.modules.infrastructure.dispatchers.Dispatcher.publish_command') as mock_publish_command:
                response = client.http.post(
                    '/pqrs',
                    headers={'Content-Type': 'application/json'},
                    body=json.dumps(request_body)
                )

                assert response.status_code == 200
                response_data = json.loads(response.body)
                assert response_data['status'] == 'ok'

                assert mock_publish_command.call_count == 1

                expected_message = {
                    "title": request_body["title"],
                    "type": request_body["type"],
                    "description": request_body["description"],
                    "date": mock.ANY,
                    "user_sub": "user123",
                    "ticket_number": mock.ANY
                }

                mock_publish_command.assert_called_with(expected_message)

def test_get_incidence_by_id_found():
    # Mock the context and data for the endpoint
    mock_incidence_id = "1"
    mock_incidence = [
        {
            "id": 1,
            "client_id": 2,
            "subject": "Incident 1",
            "description": "test",
            "status": "ABIERTO",
            "date": "2024-10-20",
            "estimated_close_date": "2024-10-28",
            "user_sub": "72c16f9f-5f13-439b-bf09-7440edd16086",
            "type": "PETICION",
            "communication_type": "SMS"
        }
    ]

    # Mock request object
    mock_request = MagicMock()
    mock_request.headers = {
        'Content-Type': 'application/json'
    }

    # Patch the Request object and the execute_query function
    with patch('chalice.app.Request', return_value=mock_request):
        with patch('chalicelib.src.modules.infrastructure.repository.IncidenceRepositoryPostgres.get_all', return_value=mock_incidence):
            # Create a test client for the app
            with Client(app) as client:
                response = client.http.get(f'/pqrs/{mock_incidence_id}')

                # Check that the response status code is 200
                assert response.status_code == 200

                # Parse the response data
                response_data = json.loads(response.body)
                assert response_data == mock_incidence


def test_get_incidence_by_id_not_found():
    # Mock the context and data for the endpoint
    mock_incidence_id = "999"  # Use an ID that will simulate a not found case

    # Mock request object
    mock_request = MagicMock()
    mock_request.headers = {
        'Content-Type': 'application/json'
    }

    # Patch the Request object and the execute_query function
    with patch('chalice.app.Request', return_value=mock_request):
        with patch('chalicelib.src.modules.infrastructure.repository.IncidenceRepositoryPostgres.get_all', return_value=[]):

            # Create a test client for the app
            with Client(app) as client:
                try:
                    client.http.get(f'/pqrs/{mock_incidence_id}')
                except NotFoundError as e:
                    assert str(e) == f"Incidence with incidence_id {mock_incidence_id} not found"