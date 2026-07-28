import unittest
from unittest.mock import MagicMock, patch, Mock
import sys
from datetime import datetime

# ---- Mock heavy dependencies ----
sys.modules['elasticsearch'] = MagicMock()
sys.modules['mapper.evalllmtelemetrydata'] = MagicMock()
sys.modules['service.elasticconnectionservice'] = MagicMock()
sys.modules['pydantic'] = MagicMock()
sys.modules['dateutil'] = MagicMock()

from service.evalllmtelemetryservice import evalllmElasticPush


class TestEvalLLMTelemetryService(unittest.TestCase):

    @patch('service.evalllmtelemetryservice.es')
    def test_evalllm_push_with_object_input_and_index_create(self, mock_es):
        """Test push when index doesn't exist"""

        mock_es.indices.exists.return_value = False
        mock_es.index = MagicMock()
        mock_es.indices.refresh = MagicMock()

        moderation = Mock()
        moderation.analysis = "good"
        moderation.score = "0.9"
        moderation.threshold = "0.5"
        moderation.result = "pass"

        data = Mock()
        data.uniqueid = "123"
        data.userid = "user"
        data.accountName = "acc"
        data.portfolioName = "pf"
        data.lotNumber = "lot"
        data.created = datetime.now()
        data.model = "gpt"
        data.moderationResults = moderation
        data.evaluation_check = "ok"
        data.timeTaken = "10ms"
        data.description = "test"

        evalllmElasticPush(data)

        mock_es.indices.create.assert_called_once()
        mock_es.index.assert_called_once()
        mock_es.indices.refresh.assert_called_once()

    @patch('service.evalllmtelemetryservice.es')
    @patch('service.evalllmtelemetryservice.parse_obj_as')
    def test_evalllm_push_with_string_input(self, mock_parse, mock_es):
        """Test push when input is JSON string"""

        mock_es.indices.exists.return_value = True
        mock_es.index = MagicMock()
        mock_es.indices.refresh = MagicMock()

        moderation = Mock()
        moderation.analysis = "analysis"
        moderation.score = "1.0"
        moderation.threshold = "0.8"
        moderation.result = "pass"

        parsed = Mock()
        parsed.uniqueid = "321"
        parsed.userid = "user2"
        parsed.accountName = "acc2"
        parsed.portfolioName = "pf2"
        parsed.lotNumber = "lot2"
        parsed.created = datetime.now()
        parsed.model = "model2"
        parsed.moderationResults = moderation
        parsed.evaluation_check = "ok"
        parsed.timeTaken = "5ms"
        parsed.description = "desc"

        mock_parse.return_value = parsed

        evalllmElasticPush('{"dummy": "json"}')

        mock_parse.assert_called_once()
        mock_es.index.assert_called_once()
        mock_es.indices.refresh.assert_called_once()

    @patch('service.evalllmtelemetryservice.es')
    def test_evalllm_push_handles_elastic_exception(self, mock_es):
        """Test that Elastic exception is handled"""

        mock_es.indices.exists.return_value = True
        mock_es.index.side_effect = Exception("ES down")
        mock_es.indices.refresh = MagicMock()

        moderation = Mock()
        moderation.analysis = "bad"
        moderation.score = "0.1"
        moderation.threshold = "0.5"
        moderation.result = "fail"

        data = Mock()
        data.uniqueid = "999"
        data.userid = "user"
        data.accountName = "acc"
        data.portfolioName = "pf"
        data.lotNumber = "lot"
        data.created = datetime.now()
        data.model = "gpt"
        data.moderationResults = moderation
        data.evaluation_check = "fail"
        data.timeTaken = "50ms"
        data.description = "error"

        evalllmElasticPush(data)

        mock_es.indices.refresh.assert_called_once()
