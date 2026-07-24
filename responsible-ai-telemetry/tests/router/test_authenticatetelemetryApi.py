import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from router.authenticatetelemetryApi import authenticateRouter


class TestAuthenticateTelemetryRouter(unittest.TestCase):

    def setUp(self):
        app = FastAPI()
        app.include_router(authenticateRouter)
        self.client = TestClient(app)

    @patch('router.authenticatetelemetryApi.userManagementElasticDataPush')
    def test_user_management_telemetry_success(self, mock_push):

        payload = {
            "tenantName": "tenant",
            "apiName": "api",
            "request": {
                "userName": "user",
                "email": "a@b.com",
                "loginTime": "10",
                "logOutTime": "20",
                "duration": "10"
            },
            "response": {
                "responseMessage": "OK"
            }
        }

        response = self.client.post("/usermanagementtelemetryapi", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json())
        mock_push.assert_called_once()
