import unittest
from unittest.mock import patch, MagicMock
import sys

# ---- Block heavy dependencies before router import ----
sys.modules['middleware.text_anonymize'] = MagicMock()
sys.modules['privacy'] = MagicMock()
sys.modules['privacy.service'] = MagicMock()
sys.modules['privacy.service.textPrivacy'] = MagicMock()
sys.modules['presidio_image_redactor'] = MagicMock()
sys.modules['matplotlib'] = MagicMock()

from fastapi.testclient import TestClient
from fastapi import FastAPI
from mapper.privacytelemetrydata import TelemetryData
from router.privacytelemetryapi import router

class TestPrivacyTelemetryRouter(unittest.TestCase):

    def setUp(self):
        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)

    @patch('router.privacytelemetryapi.privacyElasticDataPush')
    def test_privacy_telemetry(self, mock_push):
        mock_push.return_value = {}

        from datetime import datetime
        payload = TelemetryData(
            uniqueid="1",
            tenant="t",
            apiname="api",
            user="u",
            lotNumber="lot",
            date=datetime.now(),
            request={
                "portfolio_name": "pf",
                "account_name": "acc",
                "exclusion_list": ["none"],
                "inputText": "hello"
            },
            response=[]
        )

        payload_dict = payload.model_dump()
        payload_dict['date'] = payload_dict['date'].isoformat()
        response = self.client.post(
            "/privacytelemetryapi",
            json=payload_dict
        )

        self.assertEqual(response.status_code, 200)
        mock_push.assert_called_once()
