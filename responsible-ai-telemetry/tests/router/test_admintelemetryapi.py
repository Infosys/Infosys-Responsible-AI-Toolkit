import unittest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch
from mapper.admintelemetrydata import AdminTelemetryData
from datetime import datetime
from router.admintelemetryapi import adminRouter

class TestAdminTelemetryRouter(unittest.TestCase):

    def setUp(self):
        app = FastAPI()
        app.include_router(adminRouter)
        self.client = TestClient(app)

    @patch('router.admintelemetryapi.adminElasticDataPush')
    def test_admin_telemetry_success(self, mock_push):
        mock_push.return_value = None

        payload = AdminTelemetryData(
            tenant="tenant",
            apiname="api",
            date=datetime.now(),
            admin_requests={
                "recognizer_name": "name",
                "recognizer_type": "type",
                "recognizer_value_pattern": "pattern",
                "entity": "entity",
                "context": "context",
                "score_range": "high"
            }
        )

        payload_dict = payload.model_dump()
        if isinstance(payload_dict.get('date'), datetime):
            payload_dict['date'] = payload_dict['date'].isoformat()

        response = self.client.post(
            "/admintelemetryapi",
            json=payload_dict
        )

        self.assertEqual(response.status_code, 200)
        mock_push.assert_called_once()
