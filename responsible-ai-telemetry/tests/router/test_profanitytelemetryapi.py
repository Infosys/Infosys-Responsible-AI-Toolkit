import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from router.profanitytelemetryapi import profanityRouter


class TestProfanityTelemetryRouter(unittest.TestCase):

    def setUp(self):
        app = FastAPI()
        app.include_router(profanityRouter)
        self.client = TestClient(app)

    @patch('router.profanitytelemetryapi.profanityElasticDataPush')
    def test_profanity_telemetry(self, mock_push):

        payload = {
            "uniqueid": "1",
            "tenant": "t",
            "apiname": "api",
            "user": "u",
            "lotNumber": "lot",
            "request": {"inputText": "hello"},
            "response": {
                "profanity": [],
                "profanityScoreList": [],
                "outputText": "clean"
            }
        }

        mock_push.return_value = {"ok": True}

        response = self.client.post("/profanitytelemetryapi", json=payload)

        self.assertEqual(response.status_code, 200)
        mock_push.assert_called_once()
