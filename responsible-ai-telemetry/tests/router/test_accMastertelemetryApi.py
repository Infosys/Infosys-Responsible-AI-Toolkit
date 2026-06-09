import unittest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch
from mapper.accounttelemetrydata import AccountMasterTelemetryData
from datetime import datetime
from router.accMastertelemetryApi import accMasterRouter

class TestAccMasterTelemetryRouter(unittest.TestCase):

    def setUp(self):
        app = FastAPI()
        app.include_router(accMasterRouter)
        self.client = TestClient(app)

    @patch('router.accMastertelemetryApi.accMasterElasticDataPush')
    def test_acc_master_telemetry_success(self, mock_push):
        mock_push.return_value = None

        payload = AccountMasterTelemetryData(
            tenant="tenant1",
            apiname="api1",
            date=datetime.now(),
            accMaster_requests={
                "portfolio_name": "pf",
                "account_name": "acc",
                "dataGrp_list": ["grp"]
            }
        )

        payload_dict = payload.model_dump()
        # ensure datetime is JSON serializable
        if isinstance(payload_dict.get('date'), datetime):
            payload_dict['date'] = payload_dict['date'].isoformat()

        response = self.client.post(
            "/accMastertelemetryapi",
            json=payload_dict
        )

        self.assertEqual(response.status_code, 200)
        mock_push.assert_called_once()
