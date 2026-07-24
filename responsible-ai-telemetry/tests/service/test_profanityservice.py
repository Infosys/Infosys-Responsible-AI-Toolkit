import unittest
from unittest.mock import MagicMock, patch, Mock
import sys

# ---- Mock heavy dependencies ----
sys.modules['elasticsearch'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['service.elasticconnectionservice'] = MagicMock()
sys.modules['middleware.text_anonymize'] = MagicMock()

from service.profanityservice import profanityElasticDataPush


class TestProfanityService(unittest.TestCase):

    @patch('service.profanityservice.textAnonymize')
    @patch('service.profanityservice.es')
    def test_profanity_push_with_anonymization_and_index_create(self, mock_es, mock_anon):
        mock_es.indices.exists.return_value = False
        mock_es.index = MagicMock()
        mock_es.indices.refresh = MagicMock()
        mock_anon.return_value = "ANON_TEXT"

        request = Mock()
        request.inputText = "raw text"

        response = Mock()
        response.dict.return_value = {
            "profanity": [{
                "profaneWord": "bad",
                "beginOffset": 0,
                "endOffset": 3
            }],
            "profanityScoreList": [{
                "metricName": "toxicity",
                "metricScore": 0.9
            }],
            "outputText": "clean"
        }
        response.outputText = "clean"

        data = Mock()
        data.uniqueid = "123"
        data.tenant = "tenant"
        data.apiname = "api"
        data.user = "user"
        data.lotNumber = "lot"
        data.date = "2024-01-01T10:00:00.000000"
        data.request = request
        data.response = response
        data.anonymize = True

        result = profanityElasticDataPush(data)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["uniqueid"], "123")
        mock_anon.assert_called_once()
        mock_es.indices.create.assert_called_once()
        mock_es.index.assert_called_once()
        mock_es.indices.refresh.assert_called_once()

    @patch('service.profanityservice.es')
    def test_profanity_push_without_anonymization(self, mock_es):
        mock_es.indices.exists.return_value = True
        mock_es.index = MagicMock()
        mock_es.indices.refresh = MagicMock()

        request = Mock()
        request.inputText = "plain"

        response = Mock()
        response.dict.return_value = {
            "profanity": [],
            "profanityScoreList": [{
                "metricName": "clean",
                "metricScore": 0.0
            }],
            "outputText": "plain"
        }
        response.outputText = "plain"

        data = Mock()
        data.uniqueid = "456"
        data.tenant = "tenant"
        data.apiname = "api"
        data.user = "user"
        data.lotNumber = "lot"
        data.date = "2024-01-01T10:00:00.000000"
        data.request = request
        data.response = response
        data.anonymize = False

        result = profanityElasticDataPush(data)

        self.assertEqual(result["anonymize"], False)
        mock_es.index.assert_called_once()
        mock_es.indices.refresh.assert_called_once()
