"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Unit tests for recognizer_service.py
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from io import BytesIO
import pandas as pd


@pytest.mark.unit
class TestDataRecogGrp:
    """Test cases for DataRecogGrp class"""

    @patch('rai_admin.config.logger.request_id_var')
    @patch('rai_admin.service.recognizer_service.RecogDb')
    @patch('rai_admin.service.recognizer_service.EntityDb')
    def test_dataEntry_success(self, mock_entity_db, mock_recog_db, mock_request_id):
        """Test successful data entry creation"""
        from rai_admin.service.recognizer_service import DataRecogGrp
        
        mock_recog_db.find_all.return_value = []
        mock_recog_db.create.return_value = "recog_123"
        mock_entity_db.create.return_value = "success"
        
        payload = {
            "name": "Test Recognizer",
            "entity": "EMAIL",
            "type": "pattern",
            "score": 0.9,
            "context": "test context",
            "file": None,
            "ptrn": "test@example.com"
        }
        
        result = DataRecogGrp.dataEntry(payload)
        
        assert result.status == "success"
        mock_recog_db.create.assert_called_once()
        mock_entity_db.create.assert_called_once()

    @patch('rai_admin.config.logger.request_id_var')
    @patch('rai_admin.service.recognizer_service.RecogDb')
    def test_dataEntry_duplicate_name(self, mock_recog_db, mock_request_id):
        """Test data entry with duplicate name"""
        from rai_admin.service.recognizer_service import DataRecogGrp
        
        mock_recog_db.find_all.return_value = [{"RecogName": "Test Recognizer"}]
        
        payload = {
            "name": "Test Recognizer",
            "entity": "EMAIL",
            "type": "pattern",
            "score": None,
            "context": None,
            "file": None,
            "ptrn": "test@example.com"
        }
        
        result = DataRecogGrp.dataEntry(payload)
        
        assert result.status == "False"

    @patch('rai_admin.config.logger.request_id_var')
    @patch('rai_admin.service.recognizer_service.RecogDb')
    def test_getDataEntry(self, mock_recog_db, mock_request_id):
        """Test getting all data entries"""
        from rai_admin.service.recognizer_service import DataRecogGrp
        
        mock_data = [
            {"RecogName": "Recognizer1", "entity": "EMAIL"},
            {"RecogName": "Recognizer2", "entity": "PHONE"}
        ]
        mock_recog_db.find_all.return_value = mock_data
        
        result = DataRecogGrp.getDataEntry()
        
        assert result.RecogList == mock_data
        mock_recog_db.find_all.assert_called_once_with({})

    @patch('rai_admin.config.logger.request_id_var')
    @patch('rai_admin.service.recognizer_service.EntityDb')
    def test_getEntityDetails(self, mock_entity_db, mock_request_id):
        """Test getting entity details"""
        from rai_admin.service.recognizer_service import DataRecogGrp
        
        mock_entities = [
            {"EntityName": "entity1", "RecogId": "recog_123"},
            {"EntityName": "entity2", "RecogId": "recog_123"}
        ]
        mock_entity_db.find_all.return_value = mock_entities
        
        payload = MagicMock()
        payload.RecogId = "recog_123"
        
        result = DataRecogGrp.getEntityDetails(payload)
        
        assert result.DataEntities == mock_entities

    @patch('rai_admin.config.logger.request_id_var')
    @patch('rai_admin.service.recognizer_service.RecogDb')
    def test_DataGrpUpdate_success(self, mock_recog_db, mock_request_id):
        """Test successful data group update"""
        from rai_admin.service.recognizer_service import DataRecogGrp
        
        mock_recog_db.update.return_value = "success"
        
        payload = MagicMock()
        payload.RecogId = "recog_123"
        payload.RecogName = "Updated Recognizer"
        payload.supported_entity = "EMAIL"
        
        result = DataRecogGrp.DataGrpUpdate(payload)
        
        assert result.status == "success"
        mock_recog_db.update.assert_called_once()

    @patch('rai_admin.config.logger.request_id_var')
    @patch('rai_admin.service.recognizer_service.EntityDb')
    def test_EntityUpdate_success(self, mock_entity_db, mock_request_id):
        """Test successful entity update"""
        from rai_admin.service.recognizer_service import DataRecogGrp
        
        mock_entity_db.update.return_value = "success"
        
        payload = MagicMock()
        payload.EntityId = "entity_123"
        payload.EntityName = "Updated Entity"
        
        result = DataRecogGrp.EntityUpdate(payload)
        
        assert result.status == "success"

    @patch('rai_admin.config.logger.request_id_var')
    @patch('rai_admin.service.recognizer_service.EntityDb')
    def test_EntityAdd_success(self, mock_entity_db, mock_request_id):
        """Test successful entity addition"""
        from rai_admin.service.recognizer_service import DataRecogGrp
        
        mock_entity_db.find_all.return_value = []
        mock_entity_db.create.return_value = "success"
        
        payload = MagicMock()
        payload.RecogId = "recog_123"
        payload.EntityNames = ["entity1", "entity2"]
        
        result = DataRecogGrp.EntityAdd(payload)
        
        assert result.status == "success"

    @patch('rai_admin.config.logger.request_id_var')
    @patch('rai_admin.service.recognizer_service.AccDataGrpDb')
    @patch('rai_admin.service.recognizer_service.EntityDb')
    @patch('rai_admin.service.recognizer_service.RecogDb')
    def test_DataGrpDelete(self, mock_recog_db, mock_entity_db, mock_acc_data_grp_db, mock_request_id):
        """Test data group deletion"""
        from rai_admin.service.recognizer_service import DataRecogGrp
        
        mock_recog_db.delete.return_value = "success"
        mock_acc_data_grp_db.delete_many.return_value = "success"
        mock_entity_db.delete_many.return_value = "success"
        
        payload = MagicMock()
        payload.RecogId = "recog_123"
        
        result = DataRecogGrp.DataGrpDelete(payload)
        
        mock_recog_db.delete.assert_called_once_with("recog_123")
        mock_acc_data_grp_db.delete_many.assert_called_once()
        mock_entity_db.delete_many.assert_called_once()


@pytest.mark.unit
class TestAttributeDict:
    """Test cases for AttributeDict class"""

    def test_attribute_dict_getitem(self):
        """Test AttributeDict get item"""
        from rai_admin.service.recognizer_service import AttributeDict
        
        attr_dict = AttributeDict({"key": "value"})
        assert attr_dict["key"] == "value"

    def test_attribute_dict_setitem(self):
        """Test AttributeDict set item"""
        from rai_admin.service.recognizer_service import AttributeDict
        
        attr_dict = AttributeDict()
        attr_dict["key"] = "value"
        assert attr_dict["key"] == "value"

    def test_attribute_dict_delitem(self):
        """Test AttributeDict delete item"""
        from rai_admin.service.recognizer_service import AttributeDict
        
        attr_dict = AttributeDict({"key": "value"})
        del attr_dict["key"]
        assert "key" not in attr_dict
