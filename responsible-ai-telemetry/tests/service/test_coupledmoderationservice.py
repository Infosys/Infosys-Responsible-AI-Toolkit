import unittest
from unittest.mock import MagicMock, patch, Mock
import sys

# ---- Mock heavy dependencies ----
sys.modules['pymongo'] = MagicMock()
sys.modules['elasticsearch'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['mapper.coupledmoderationtelemetrydata'] = MagicMock()
sys.modules['middleware.text_anonymize'] = MagicMock()

from service.coupledmoderationservice import coupledModerationElasticDataPush


def full_moderation_block():
    return {
        "text": "input",
        "promptInjectionCheck": {"injectionConfidenceScore": "1", "injectionThreshold": "1", "result": "ok"},
        "jailbreakCheck": {"jailbreakSimilarityScore": "1", "jailbreakThreshold": "1", "result": "ok"},
        "privacyCheck": {"entitiesRecognised": "x", "entitiesConfiguredToBlock": "y", "result": "ok"},
        "profanityCheck": {"profaneWordsIdentified": "x", "profaneWordsthreshold": "y", "result": "ok"},
        "toxicityCheck": {"toxicityScore": [{"toxicScore": [{"metricScore": 0.5}]}]},
        "restrictedtopic": {
            "topicScores": [{}], "topicThreshold": "1", "result": "ok",
            "topicTypesConfiguredToBlock": "x", "topicTypesRecognised": "y"
        },
        "textQuality": {"readabilityScore": "1", "textGrade": "A"},
        "refusalCheck": {"refusalSimilarityScore": "1", "RefusalThreshold": "1", "result": "ok"},
        "customThemeCheck": {"customSimilarityScore": "1", "themeThreshold": "1", "result": "ok"},
        "randomNoiseCheck": {"smoothLlmScore": "1", "smoothLlmThreshold": "1", "result": "ok"},
        "advancedJailbreakCheck": {"text": "x", "result": "ok"},
        "summary": {"status": "ok", "reason": "none"},

        # ⭐ REQUIRED BY SERVICE — THIS FIXES YOUR ERROR
        "textRelevanceCheck": {
            "PromptResponseSimilarityScore": 0.88
        }
    }


class TestCoupledModerationService(unittest.TestCase):

    @patch('service.coupledmoderationservice.es')
    @patch('service.coupledmoderationservice.textAnonymize')
    def test_successful_data_push_with_anonymization(self, mock_anon, mock_es):

        mock_es.ping.return_value = True
        mock_es.indices.exists.return_value = False
        mock_es.index = MagicMock()
        mock_es.indices.refresh = MagicMock()
        mock_anon.return_value = "ANON"

        mock_choice = Mock()
        mock_choice.text = "choice"
        mock_choice.dict.return_value = {"text": "choice", "index": 0, "finishReason": "stop"}

        moderation = Mock()
        moderation.dict.return_value = {
            "requestModeration": full_moderation_block(),
            "responseModeration": full_moderation_block()
        }
        moderation.requestModeration = Mock(text="input")
        moderation.responseModeration = Mock(generatedText="output")

        data = Mock()
        data.uniqueid = "123"
        data.object = "chat"
        data.userid = "user"
        data.lotNumber = "lot"
        data.model = "model"
        data.created = "now"
        data.choices = [mock_choice]
        data.moderationResults = moderation
        data.Moderation_layer_time = None
        data.portfolioName = "pf"
        data.accountName = "acc"
        data.anonymize = True

        result = coupledModerationElasticDataPush(data)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["uniqueid"], "123")
        self.assertTrue(mock_anon.call_count >= 3)
        mock_es.index.assert_called_once()


    @patch('service.coupledmoderationservice.es')
    def test_index_creation_when_missing(self, mock_es):

        mock_es.ping.return_value = True
        mock_es.indices.exists.return_value = False
        mock_es.indices.create = MagicMock()
        mock_es.index = MagicMock()
        mock_es.indices.refresh = MagicMock()

        mock_choice = Mock()
        mock_choice.text = "x"
        mock_choice.dict.return_value = {"text": "x", "index": 0, "finishReason": "stop"}

        moderation = Mock()
        moderation.dict.return_value = {
            "requestModeration": full_moderation_block(),
            "responseModeration": full_moderation_block()
        }
        moderation.requestModeration = Mock(text="x")
        moderation.responseModeration = Mock(generatedText="y")

        data = Mock()
        data.uniqueid = "456"
        data.object = "chat"
        data.userid = "user"
        data.lotNumber = "lot"
        data.model = "model"
        data.created = "now"
        data.choices = [mock_choice]
        data.moderationResults = moderation
        data.Moderation_layer_time = None
        data.portfolioName = "pf"
        data.accountName = "acc"
        data.anonymize = False

        coupledModerationElasticDataPush(data)

        mock_es.indices.create.assert_called_once()
        mock_es.index.assert_called_once()
