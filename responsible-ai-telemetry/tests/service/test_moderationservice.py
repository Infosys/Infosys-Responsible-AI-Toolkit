import unittest
from unittest.mock import MagicMock, patch, Mock
import sys
from datetime import datetime

# ---- Mock heavy dependencies ----
sys.modules['elasticsearch'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['mapper.moderationtelemetrydata'] = MagicMock()
sys.modules['mapper.coupledmoderationrequestdata'] = MagicMock()
sys.modules['service.elasticconnectionservice'] = MagicMock()
sys.modules['middleware.text_anonymize'] = MagicMock()

from service.moderationservice import (
    moderationElasticDataPush,
    moderationRequestElasticDataPush,
    coupledRequestModerationElasticDataPush
)


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


class TestModerationService(unittest.TestCase):

    @patch('service.moderationservice.helpers.bulk')
    @patch('service.moderationservice.textAnonymize')
    @patch('service.moderationservice.es')
    def test_moderation_elastic_push_success(self, mock_es, mock_anon, mock_bulk):
        mock_es.indices.exists.return_value = False
        mock_es.index = MagicMock()
        mock_es.indices.refresh = MagicMock()
        mock_anon.return_value = "ANON"

        moderation = Mock()
        moderation.dict.return_value = full_moderation_block()

        data = Mock()
        data.uniqueid = "1"
        data.lotNumber = "lot"
        data.userid = "user"
        data.Source = "api"
        data.portfolioName = "pf"
        data.accountName = "acc"
        data.created = datetime.now()
        data.moderationResults = moderation
        data.Moderation_layer_time = None
        data.anonymize = True

        result = moderationElasticDataPush(data)

        self.assertIsInstance(result, dict)
        mock_es.indices.create.assert_called_once()
        mock_es.indices.refresh.assert_called_once()

    @patch('service.moderationservice.es')
    def test_moderation_request_push(self, mock_es):
        mock_es.indices.exists.return_value = False
        mock_es.index = MagicMock()

        thresholds = Mock()
        thresholds.dict.return_value = {"PromptinjectionThreshold": 0.1}

        data = Mock()
        data.lotNumber = "lot"
        data.userid = "user"
        data.AccountName = "acc"
        data.PortfolioName = "pf"
        data.ModerationChecks = "checks"
        data.ModerationCheckThresholds = thresholds

        result = moderationRequestElasticDataPush(data)

        self.assertEqual(result["userid"], "user")
        mock_es.indices.create.assert_called_once()
        mock_es.index.assert_called_once()

    @patch('service.moderationservice.textAnonymize')
    @patch('service.moderationservice.es')
    def test_coupled_request_moderation_push(self, mock_es, mock_anon):
        mock_es.indices.exists.return_value = False
        mock_es.index = MagicMock()
        mock_anon.return_value = "ANON_PROMPT"

        thresholds = Mock()
        thresholds.dict.return_value = {"PromptinjectionThreshold": 0.1}

        data = Mock()
        data.lotNumber = "lot"
        data.userid = "user"
        data.AccountName = "acc"
        data.PortfolioName = "pf"
        data.model_name = "gpt"
        data.translate = "no"
        data.temperature = 0.5
        data.LLMinteraction = "chat"
        data.PromptTemplate = "template"
        data.EmojiModeration = "yes"
        data.Prompt = "hello"
        data.InputModerationChecks = "input"
        data.OutputModerationChecks = "output"
        data.llm_BasedChecks = "llm"
        data.ModerationCheckThresholds = thresholds
        data.anonymize = True

        result = coupledRequestModerationElasticDataPush(data)

        self.assertEqual(result["userid"], "user")
        mock_es.indices.create.assert_called_once()
        mock_es.index.assert_called_once()
