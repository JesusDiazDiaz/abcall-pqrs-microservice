import json
from chalice.test import Client
from app import app


 def test_incidence_post():
     with Client(app) as client:
         request_body = {
             "incidence_type": "technical",
             "status": "open",
             "risk_level": "high"
         }

         response = client.http.post(
             '/pqrs',
             headers={'Content-Type': 'application/json'},
             body=json.dumps(request_body)
         )

         assert response.status_code == 200

         response_data = json.loads(response.body)
         assert response_data['status'] == 'ok'