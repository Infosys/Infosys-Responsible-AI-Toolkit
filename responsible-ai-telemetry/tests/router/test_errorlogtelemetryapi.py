import unittest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch
from mapper.errorlogtelemetrydata import TelemetryData
from router.errorlogtelemetryapi import errorlogRouter

class TestErrorLogTelemetryRouter(unittest.TestCase):

    def setUp(self):
        app = FastAPI()
        app.include_router(errorlogRouter)
        self.client = TestClient(app)

    @patch('router.errorlogtelemetryapi.errorLogElasticDataPush')
    def test_error_log_telemetry(self, mock_push):
        mock_push.return_value = None

        from types import SimpleNamespace
        from datetime import datetime
        payload_obj = SimpleNamespace(
            uniqueid="1",
            tenant="t",
            apiname="api",
            error="boom",
            date=datetime.now()
        )

        import asyncio
        res = asyncio.run(errorlogRouter.routes[0].endpoint(payload_obj))
        assert isinstance(res, dict)
        assert 'data' in res
        assert getattr(res['data'], 'uniqueid', None) == "1"

        mock_push.assert_called_once()
