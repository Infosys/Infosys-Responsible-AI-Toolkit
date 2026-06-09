import unittest
from unittest.mock import MagicMock, patch
import sys

# ---- Mock heavy / external dependencies before import ----
sys.modules['elasticsearch'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['service.elasticconnectionservice'] = MagicMock()
sys.modules['pydantic'] = MagicMock()

from service.adminservice import adminElasticDataPush


class TestAdminService(unittest.TestCase):

    @patch('service.adminservice.es')
    def test_admin_elastic_data_push_creates_index_and_pushes_data(self, mock_es):
        # Arrange
        mock_es.indices.exists.return_value = False

        data = MagicMock()
        data.tenant = "tenant1"
        data.apiname = "api1"
        data.date = "2025-01-01"

        data.admin_requests = MagicMock()
        data.admin_requests.recognizer_name = "rec1"
        data.admin_requests.recognizer_type = "type1"
        data.admin_requests.recognizer_value_pattern = "pattern1"
        data.admin_requests.entity = "entity1"
        data.admin_requests.context = "context1"
        data.admin_requests.score_range = "0.9"

        # Act
        adminElasticDataPush(data)

        # Assert
        mock_es.indices.exists.assert_called_once_with(index='adminindex')
        mock_es.indices.create.assert_called_once()
        mock_es.index.assert_called_once()
        mock_es.indices.refresh.assert_called_once_with(index='adminindex')

    @patch('service.adminservice.es')
    def test_admin_elastic_data_push_when_index_already_exists(self, mock_es):
        # Arrange
        mock_es.indices.exists.return_value = True

        data = MagicMock()
        data.tenant = "tenant2"
        data.apiname = "api2"
        data.date = "2025-01-02"

        data.admin_requests = MagicMock()
        data.admin_requests.recognizer_name = "rec2"
        data.admin_requests.recognizer_type = "type2"
        data.admin_requests.recognizer_value_pattern = "pattern2"
        data.admin_requests.entity = "entity2"
        data.admin_requests.context = "context2"
        data.admin_requests.score_range = "0.8"

        # Act
        adminElasticDataPush(data)

        # Assert
        mock_es.indices.exists.assert_called_once_with(index='adminindex')
        mock_es.indices.create.assert_not_called()
        mock_es.index.assert_called_once()
        mock_es.indices.refresh.assert_called_once_with(index='adminindex')
