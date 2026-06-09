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
from mapper.explainabilitytelemetrydata import TelemetryData, ExplainBulkProcessTelemetryData
from router.explainabilitytelemetryapi import explainabilityRouter

class TestExplainabilityTelemetryRouter(unittest.TestCase):

    def setUp(self):
        app = FastAPI()
        app.include_router(explainabilityRouter)
        self.client = TestClient(app)

    @patch('router.explainabilitytelemetryapi.explainabilityElasticDataPush')
    def test_explainability_single(self, mock_push):
        mock_push.return_value = {}

        from datetime import datetime
        payload = TelemetryData(
            uniqueid="1",
            tenant="t",
            apiname="api",
            user="u",
            lotNumber="lot",
            date=datetime.now(),
            request={"portfolio_name": "pf", "account_name": "acc", "inputText": "hello", "explainerID": 1},
            response={"explainerID": 1, "explanation": [{"predictedTarget": "label", "anchor": ["a"]}]}
        )

        payload_dict = payload.model_dump()
        payload_dict['date'] = payload_dict['date'].isoformat()
        response = self.client.post(
            "/explainabilitytelemetryapi",
            json=payload_dict
        )

        self.assertEqual(response.status_code, 200)
        mock_push.assert_called_once()

    @patch('router.explainabilitytelemetryapi.explainabilityBulkElasticDataPush')
    def test_explainability_bulk(self, mock_push):
        mock_push.return_value = {}

        from datetime import datetime
        payload = ExplainBulkProcessTelemetryData(
            uniqueId="1",
            tenetName="t",
            apiName="api",
            userId="u",
            date=datetime.now(),
            response=[]
        )

        payload_dict = payload.model_dump()
        payload_dict['date'] = payload_dict['date'].isoformat()
        response = self.client.post(
            "/explainabilitybulktelemetryapi",
            json=payload_dict
        )

        self.assertEqual(response.status_code, 200)
        mock_push.assert_called_once()
