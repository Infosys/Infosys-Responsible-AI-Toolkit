import unittest
from unittest.mock import MagicMock, patch
import sys

# ---- Mock heavy / external dependencies before import ----
sys.modules['elasticsearch'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['service.elasticconnectionservice'] = MagicMock()

from service.accountMasterService import accMasterElasticDataPush


class TestAccMasterService(unittest.TestCase):

    @patch('service.accountMasterService.es')
    def test_acc_master_elastic_data_push_creates_index_and_pushes_data(self, mock_es):
        # Arrange
        mock_es.indices.exists.return_value = False

        data = MagicMock()
        data.tenant = "tenant1"
        data.apiname = "api1"
        data.date = "2025-01-01"

        data.accMaster_requests = MagicMock()
        data.accMaster_requests.portfolio_name = "portfolioA"
        data.accMaster_requests.account_name = "accountA"
        data.accMaster_requests.dataGrp_list = ["group1", "group2"]

        # Act
        accMasterElasticDataPush(data)

        # Assert
        mock_es.indices.exists.assert_called_once_with(index='accmasterindex')
        mock_es.indices.create.assert_called_once()
        mock_es.index.assert_called_once()
        mock_es.indices.refresh.assert_called_once_with(index='accmasterindex')

    @patch('service.accountMasterService.es')
    def test_acc_master_elastic_data_push_when_index_already_exists(self, mock_es):
        # Arrange
        mock_es.indices.exists.return_value = True

        data = MagicMock()
        data.tenant = "tenant2"
        data.apiname = "api2"
        data.date = "2025-01-02"

        data.accMaster_requests = MagicMock()
        data.accMaster_requests.portfolio_name = "portfolioB"
        data.accMaster_requests.account_name = "accountB"
        data.accMaster_requests.dataGrp_list = ["groupX"]

        # Act
        accMasterElasticDataPush(data)

        # Assert
        mock_es.indices.exists.assert_called_once_with(index='accmasterindex')
        mock_es.indices.create.assert_not_called()
        mock_es.index.assert_called_once()
        mock_es.indices.refresh.assert_called_once_with(index='accmasterindex')
