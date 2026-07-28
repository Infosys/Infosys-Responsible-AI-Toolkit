import unittest
from unittest.mock import MagicMock, patch
import sys

# ---- Mock heavy dependencies ----
sys.modules['elasticsearch'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['service.elasticconnectionservice'] = MagicMock()

from service.registerService import registerElasticDataPush


class TestRegisterService(unittest.TestCase):

    @patch('service.registerService.es')
    def test_register_push_creates_index_and_inserts(self, mock_es):
        mock_es.indices.exists.return_value = False
        mock_es.index = MagicMock()
        mock_es.indices.refresh = MagicMock()

        data = MagicMock()
        data.tenant = "tenant1"
        data.apiname = "api1"
        data.date = "2024-01-01"

        data.register_requests = MagicMock()
        data.register_requests.email = "test@example.com"
        data.register_requests.login = "user"
        data.register_requests.password = "pass"

        registerElasticDataPush(data)

        mock_es.indices.create.assert_called_once()
        mock_es.index.assert_called_once()
        mock_es.indices.refresh.assert_called_once()

    @patch('service.registerService.es')
    def test_register_push_when_index_exists(self, mock_es):
        mock_es.indices.exists.return_value = True
        mock_es.index = MagicMock()
        mock_es.indices.refresh = MagicMock()

        data = MagicMock()
        data.tenant = "tenant2"
        data.apiname = "api2"
        data.date = "2024-01-02"

        data.register_requests = MagicMock()
        data.register_requests.email = "user@test.com"
        data.register_requests.login = "login"
        data.register_requests.password = "secret"

        registerElasticDataPush(data)

        mock_es.indices.create.assert_not_called()
        mock_es.index.assert_called_once()
        mock_es.indices.refresh.assert_called_once()
