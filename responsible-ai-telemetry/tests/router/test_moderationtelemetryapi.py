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
from mapper.moderationtelemetrydata import ModerationResults
from mapper.moderationrequestdata import ModerationRequestData
from mapper.coupledmoderationrequestdata import CoupledModerationRequestData
from router.moderationtelemetryapi import moderationRouter

class TestModerationTelemetryRouter(unittest.TestCase):

    def setUp(self):
        app = FastAPI()
        app.include_router(moderationRouter)
        self.client = TestClient(app)

    @patch('router.moderationtelemetryapi.moderationElasticDataPush')
    def test_moderation_telemetry(self, mock_push):
        mock_push.return_value = {}

        # Call router handler directly with constructed model to avoid
        # HTTP validation issues for the highly nested model
        payload_model = ModerationResults.model_construct()
        import asyncio
        res = asyncio.run(moderationRouter.routes[0].endpoint(payload_model))
        assert res == {}

    @patch('router.moderationtelemetryapi.moderationRequestElasticDataPush')
    def test_moderation_request(self, mock_push):
        mock_push.return_value = {}

        payload_model = ModerationRequestData.model_construct()
        import asyncio
        res = asyncio.run(moderationRouter.routes[1].endpoint(payload_model))
        assert res == {}

    @patch('router.moderationtelemetryapi.coupledRequestModerationElasticDataPush')
    def test_coupled_moderation_request(self, mock_push):
        mock_push.return_value = {}

        payload_model = CoupledModerationRequestData.model_construct()
        import asyncio
        res = asyncio.run(moderationRouter.routes[2].endpoint(payload_model))
        assert res == {}
