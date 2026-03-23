import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from router.evalLLMtelemetryapi import evalLLM


class TestEvalLLMTelemetryRouter(unittest.TestCase):

    def setUp(self):
        app = FastAPI()
        app.include_router(evalLLM)
        self.client = TestClient(app)

    @patch('router.evalLLMtelemetryapi.evalllmElasticPush')
    def test_evalllm_telemetry(self, mock_push):

        payload = {
            "uniqueid": "1",
            "userid": "user",
            "accountName": "acc",
            "portfolioName": "pf",
            "lotNumber": "lot",
            "created": "2024-01-01T10:00:00",
            "model": "gpt",
            "moderationResults": {
                "analysis": "ok",
                "score": "1",
                "threshold": "1",
                "result": "pass"
            },
            "evaluation_check": "pass",
            "timeTaken": "1s",
            "description": "desc"
        }

        response = self.client.post("/evalllmtelemetryapi", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json())
        mock_push.assert_called_once()
