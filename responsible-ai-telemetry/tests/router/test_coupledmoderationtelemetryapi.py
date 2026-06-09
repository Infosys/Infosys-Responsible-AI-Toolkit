import sys
import unittest
from unittest.mock import MagicMock, patch

# ---- Block heavy dependencies before router import ----
sys.modules['middleware.text_anonymize'] = MagicMock()
sys.modules['privacy'] = MagicMock()
sys.modules['privacy.service'] = MagicMock()
sys.modules['privacy.service.textPrivacy'] = MagicMock()
sys.modules['presidio_image_redactor'] = MagicMock()
sys.modules['matplotlib'] = MagicMock()

from fastapi import FastAPI
from fastapi.testclient import TestClient


import router.coupledmoderationtelemetryapi as api


class TestCoupledModerationTelemetryAPI(unittest.TestCase):

    def setUp(self):
        app = FastAPI()
        app.include_router(api.coupledModerationRouter)
        self.client = TestClient(app)

    @patch('router.coupledmoderationtelemetryapi.coupledModerationElasticDataPush')
    def test_coupled_moderation_telemetry_success(self, mock_push):

        mock_push.return_value = {"status": "ok"}

        # Build a minimal valid completionResponse using model_construct defaults
        from mapper.coupledmoderationtelemetrydata import completionResponse, Choice, ModerationResults, Result, RequestModeration, ResponseModeration
        from datetime import datetime

        choice = Choice(text="hello", index=0, finishReason="stop")
        # minimal nested moderation objects (use examples where possible)
        req_mod = {}  # many nested optional fields; empty dict is acceptable for minimal construct
        resp_mod = {}

        # Call the router handler directly with a lightweight object to avoid
        # HTTP-level validation; the router only prints and forwards the data.
        from types import SimpleNamespace
        payload_obj = SimpleNamespace(
            uniqueid="123",
            object="chat.completion",
            userid="user1",
            lotNumber="LOT-1",
            model="gpt",
            created="1646932609",
            choices=[choice],
            moderationResults=SimpleNamespace(),
            portfolioName="pf",
            accountName="acc",
        )

        import asyncio
        res = asyncio.run(api.moderationTelemetryProcessing(payload_obj))
        assert res == {"status": "ok"}
        mock_push.assert_called_once()

