import unittest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch
from mapper.errorloggingtelemetrydata import ErrorLog
from router.errorloggingtelemetryapi import errorloggingRouter

class TestErrorLoggingTelemetryRouter(unittest.TestCase):

    def setUp(self):
        app = FastAPI()
        app.include_router(errorloggingRouter)
        self.client = TestClient(app)

    @patch('router.errorloggingtelemetryapi.errorLoggingElasticDataPush')
    def test_error_logging_telemetry_success(self, mock_push):
        mock_push.return_value = None

        # Use model_construct to ensure minimal valid payload for ErrorLog
        # Call handler directly with a small simple object matching expected fields
        from types import SimpleNamespace
        from datetime import datetime
        payload_obj = SimpleNamespace(
            uniqueid="1",
            tenant="t",
            apiname="api",
            error="boom",
            stacktrace="trace",
            date=datetime.now()
        )

        import asyncio
        res = asyncio.run(errorloggingRouter.routes[0].endpoint(payload_obj))
        # Router wraps the payload in {'data': ...} and returns it
        assert isinstance(res, dict)
        assert 'data' in res
        assert getattr(res['data'], 'uniqueid', None) == "1"

        mock_push.assert_called_once()
