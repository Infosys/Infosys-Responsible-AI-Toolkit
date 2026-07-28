import unittest
from unittest.mock import MagicMock, patch
import sys

# ---- Mock heavy / external dependencies before import ----
sys.modules['elasticsearch'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['service.elasticconnectionservice'] = MagicMock()

from service.authenticateservice import userManagementElasticDataPush


class TestAuthenticateService(unittest.TestCase):

    @patch('service.authenticateservice.es')
    @patch('service.authenticateservice.os.getenv')
    def test_user_management_push_creates_index_and_inserts(self, mock_getenv, mock_es):
        # Arrange
        mock_getenv.return_value = "DEV"
        mock_es.indices.exists.return_value = False

        # Search returns no results
        mock_es.search.return_value = {
            "hits": {"total": {"value": 0}}
        }

        data = MagicMock()
        data.tenantName = "tenant1"
        data.apiName = "api1"

        data.request = MagicMock()
        data.request.userName = "user1"
        data.request.email = "user@test.com"
        data.request.loginTime = "10:00"
        data.request.logOutTime = "11:00"
        data.request.duration = "1 hour"

        data.response = MagicMock()
        data.response.responseMessage = "Success"

        # Act
        userManagementElasticDataPush(data, id="123")

        # Assert
        mock_es.indices.create.assert_called_once()
        mock_es.index.assert_called_once()
        mock_es.update.assert_not_called()
        mock_es.indices.refresh.assert_called_once()

    @patch('service.authenticateservice.es')
    @patch('service.authenticateservice.os.getenv')
    def test_user_management_push_updates_existing_record(self, mock_getenv, mock_es):
        # Arrange
        mock_getenv.return_value = "PROD"
        mock_es.indices.exists.return_value = True

        # Search returns one hit
        mock_es.search.return_value = {
            "hits": {
                "total": {"value": 1},
                "hits": [
                    {"_id": "existing123"}
                ]
            }
        }

        data = MagicMock()
        data.tenantName = "tenant2"
        data.apiName = "api2"

        data.request = MagicMock()
        data.request.userName = "user2"
        data.request.email = "user2@test.com"
        data.request.loginTime = "09:00"
        data.request.logOutTime = "10:00"
        data.request.duration = "0 Seconds"

        data.response = MagicMock()
        data.response.responseMessage = "Updated"

        # Act
        userManagementElasticDataPush(data)

        # Assert
        mock_es.update.assert_called_once()
        mock_es.index.assert_not_called()
        mock_es.indices.refresh.assert_called_once()
