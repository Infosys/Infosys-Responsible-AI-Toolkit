import unittest
from unittest.mock import MagicMock, patch, Mock
import sys
from datetime import datetime

# ---- Mock heavy dependencies ----
sys.modules['elasticsearch'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['mapper.moderationtelemetrydata'] = MagicMock()
sys.modules['service.elasticconnectionservice'] = MagicMock()
sys.modules['middleware.text_anonymize'] = MagicMock()

from service.testmoderationservice import moderationElasticDataPushTest


def full_moderation_block():
    return {
        "text": "hello",
        "promptInjectionCheck": {"injectionConfidenceScore": 0.1, "injectionThreshold": 0.5, "result": "ok"},
        "jailbreakCheck": {"jailbreakSimilarityScore": 0.1, "jailbreakThreshold": 0.5, "result": "ok"},
        "privacyCheck": {"entitiesRecognised": "x", "entitiesConfiguredToBlock": "y", "result": "ok"},
        "profanityCheck": {"profaneWordsIdentified": "x", "profaneWordsthreshold": 1, "result": "ok"},
        "toxicityCheck": {"toxicityScore": {}, "toxicitythreshold": 0.2, "result": "ok"},
        "restrictedtopic": {"topicScores": {}, "topicThreshold": 0.1, "result": "ok"},
        "textQuality": {"readabilityScore": 0.9, "textGrade": "A"},
        "refusalCheck": {"refusalSimilarityScore": 0.1, "RefusalThreshold": 0.5, "result": "ok"},
        "summary": {"status": "pass", "reason": "none"}
    }


class TestTestModerationService(unittest.TestCase):

    @patch('service.testmoderationservice.textAnonymize')
    @patch('service.testmoderationservice.es')
    def test_moderation_test_push_success(self, mock_es, mock_anon):
        mock_es.indices.exists.return_value = False
        mock_es.index = MagicMock()
        mock_anon.return_value = "ANON"

        moderation = Mock()
        moderation.text = "hello"
        moderation.dict.return_value = full_moderation_block()

        data = Mock()
        data.uniqueid = "1"
        data.portfolioName = "pf"
        data.accountName = "acc"
        data.created = datetime.now()
        data.moderationResults = moderation
        data.anonymize = True

        result = moderationElasticDataPushTest(data)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["uniqueid"], "1")
        mock_es.indices.create.assert_called_once()
        mock_es.index.assert_called_once()
