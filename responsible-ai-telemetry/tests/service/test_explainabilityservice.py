import unittest
from unittest.mock import MagicMock, patch, Mock
import sys
from datetime import datetime

# ---- Mock heavy dependencies ----
sys.modules['elasticsearch'] = MagicMock()
sys.modules['pydantic'] = MagicMock()
sys.modules['mapper.explainabilitytelemetrydata'] = MagicMock()
sys.modules['service.elasticconnectionservice'] = MagicMock()
sys.modules['middleware.text_anonymize'] = MagicMock()
sys.modules['dateutil'] = MagicMock()

from service.explainabilityservice import (
    explainabilityElasticDataPush,
    explainabilityBulkElasticDataPush
)


class TestExplainabilityService(unittest.TestCase):

    @patch('service.explainabilityservice.es')
    @patch('service.explainabilityservice.textAnonymize')
    @patch('service.explainabilityservice.parse')
    def test_explainability_single_push_with_anonymization(
        self, mock_parse, mock_anon, mock_es
    ):
        mock_es.indices.exists.return_value = False
        mock_es.index = MagicMock()
        mock_es.indices.refresh = MagicMock()
        mock_anon.return_value = "ANON_TEXT"

        mock_parse.return_value = datetime.now()

        # Build response explanation object
        explanation = Mock()
        explanation.dict.return_value = {"predictedTarget": "x", "anchor": "y"}

        response = Mock()
        response.explanation = [explanation]

        request = Mock()
        request.inputText = "raw text"
        request.dict.return_value = {
            "portfolio_name": "pf",
            "account_name": "acc",
            "inputText": "raw text",
            "explainerID": 1
        }

        data = Mock()
        data.uniqueid = "123"
        data.tenant = "tenant"
        data.apiname = "api"
        data.user = "user"
        data.lotNumber = "lot"
        data.date = "2024-01-01"
        data.request = request
        data.response = response
        data.anonymize = True

        result = explainabilityElasticDataPush(data)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["uniqueid"], "123")
        mock_anon.assert_called_once()
        mock_es.indices.create.assert_called_once()
        mock_es.index.assert_called_once()
        mock_es.indices.refresh.assert_called_once()

    @patch('service.explainabilityservice.es')
    @patch('service.explainabilityservice.textAnonymize')
    def test_explainability_bulk_push(self, mock_anon, mock_es):
        mock_es.indices.exists.return_value = True
        mock_es.index = MagicMock()
        mock_es.indices.refresh = MagicMock()
        mock_anon.side_effect = lambda x: f"ANON_{x}"

        bulk_response_item = Mock()
        bulk_response_item.InputPrompt = "prompt"
        bulk_response_item.Response = "response"
        bulk_response_item.Chain_of_Thought = "chain"
        bulk_response_item.dict.return_value = {
            "InputPrompt": "prompt",
            "Response": "response",
            "Chain_of_Thought": "chain",
            "Token_Cost": 5
        }

        data = Mock()
        data.uniqueId = "bulk123"
        data.tenetName = "tenant"
        data.apiName = "api"
        data.userId = "user"
        data.date = None
        data.anonymize = True
        data.response = [bulk_response_item]

        result = explainabilityBulkElasticDataPush(data)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["uniqueId"], "bulk123")
        mock_es.index.assert_called_once()
        mock_es.indices.refresh.assert_called_once()
