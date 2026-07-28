import unittest
from unittest.mock import MagicMock, patch, Mock
import sys
from datetime import datetime

# ---- Mock heavy dependencies ----
sys.modules['elasticsearch'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['service.elasticconnectionservice'] = MagicMock()
sys.modules['middleware.text_anonymize'] = MagicMock()

from service.privacyservice import privacyElasticDataPush


class TestPrivacyService(unittest.TestCase):

    @patch('service.privacyservice.textAnonymize')
    @patch('service.privacyservice.es')
    def test_privacy_push_with_anonymization_and_index_create(self, mock_es, mock_anon):
        mock_es.indices.exists.return_value = False
        mock_es.index = MagicMock()
        mock_es.indices.refresh = MagicMock()
        mock_anon.return_value = "ANON_TEXT"

        request = Mock()
        request.inputText = "raw text"
        request.dict.return_value = {
            "portfolio_name": "pf",
            "account_name": "acc",
            "exclusion_list": [],
            "inputText": "raw text"
        }

        response_item = Mock()
        response_item.dict.return_value = {
            "type": "PII",
            "beginOffset": 0,
            "endOffset": 4,
            "score": 0.9,
            "responseText": "text"
        }

        data = Mock()
        data.uniqueid = "123"
        data.tenant = "tenant"
        data.apiname = "api"
        data.user = "user"
        data.lotNumber = "lot"
        data.date = "2024-01-01T10:00:00.000000"
        data.request = request
        data.response = [response_item]
        data.anonymize = True

        result = privacyElasticDataPush(data)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["uniqueid"], "123")
        mock_anon.assert_called_once()
        mock_es.indices.create.assert_called_once()
        mock_es.index.assert_called_once()
        mock_es.indices.refresh.assert_called_once()

    @patch('service.privacyservice.es')
    def test_privacy_push_without_anonymization(self, mock_es):
        mock_es.indices.exists.return_value = True
        mock_es.index = MagicMock()
        mock_es.indices.refresh = MagicMock()

        request = Mock()
        request.inputText = "plain"
        request.dict.return_value = {
            "portfolio_name": "pf",
            "account_name": "acc",
            "exclusion_list": [],
            "inputText": "plain"
        }

        response_item = Mock()
        response_item.dict.return_value = {
            "type": "NONE",
            "beginOffset": 0,
            "endOffset": 0,
            "score": 0.0,
            "responseText": ""
        }

        data = Mock()
        data.uniqueid = "456"
        data.tenant = "tenant"
        data.apiname = "api"
        data.user = "user"
        data.lotNumber = "lot"
        data.date = "2024-01-01T10:00:00.000000"
        data.request = request
        data.response = [response_item]
        data.anonymize = False

        result = privacyElasticDataPush(data)

        self.assertEqual(result["anonymize"], False)
        mock_es.index.assert_called_once()
        mock_es.indices.refresh.assert_called_once()
