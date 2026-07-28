import unittest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch
from mapper.registertelemetrtdata import RegisterTelemetryData
from router.registertelemetryApi import registerRouter

class TestRegisterTelemetryRouter(unittest.TestCase):

    def setUp(self):
        app = FastAPI()
        app.include_router(registerRouter)
        self.client = TestClient(app)

    @patch('router.registertelemetryApi.registerElasticDataPush')
    def test_register_telemetry(self, mock_push):
        mock_push.return_value = None

        from datetime import datetime
        payload = RegisterTelemetryData(
            tenant="t",
            apiname="api",
            date=datetime.now(),
            register_requests={
                "email": "a@b.com",
                "login": "user",
                "password": "pass"
            }
        )

        payload_dict = payload.model_dump()
        payload_dict['date'] = payload_dict['date'].isoformat()

        response = self.client.post(
            "/registertelemetryapi",
            json=payload_dict
        )

        self.assertEqual(response.status_code, 200)
        mock_push.assert_called_once()
