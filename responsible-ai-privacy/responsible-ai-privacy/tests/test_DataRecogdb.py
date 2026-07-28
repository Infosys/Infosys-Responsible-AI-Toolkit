"""
Unit tests for privacy.dao.DataRecogdb module.
Tests RecogDb class database operations.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
sys.path.insert(0, 'src')
from privacy.dao.DataRecogdb import RecogDb, AttributeDict


class TestRecogDb:
    """Test RecogDb database operations"""
    
    @patch('privacy.dao.DataRecogdb.RecogDb.mycol')
    def test_findOne_returns_attribute_dict(self, mock_mycol):
        """Test findOne returns AttributeDict"""
        test_id = 777
        mock_data = {"_id": test_id, "RecogName": "EmailRecognizer", "RecogType": "pattern"}
        mock_mycol.find.return_value = [mock_data]
        
        result = RecogDb.findOne(test_id)
        
        assert isinstance(result, AttributeDict)
        assert result._id == test_id
        assert result.RecogName == "EmailRecognizer"
        assert result.RecogType == "pattern"
        mock_mycol.find.assert_called_once_with({"_id": test_id}, {})
    
    @patch('privacy.dao.DataRecogdb.RecogDb.mycol')
    def test_findall_returns_list(self, mock_mycol):
        """Test findall returns list of AttributeDict"""
        query = {"isActive": "Y"}
        mock_data = [
            {"_id": 1, "RecogName": "EmailRecognizer"},
            {"_id": 2, "RecogName": "PhoneRecognizer"}
        ]
        mock_mycol.find.return_value = mock_data
        
        result = RecogDb.findall(query)
        
        assert len(result) == 2
        assert all(isinstance(item, AttributeDict) for item in result)
        assert result[0].RecogName == "EmailRecognizer"
        assert result[1].RecogName == "PhoneRecognizer"
        mock_mycol.find.assert_called_once_with(query, {})
    
    @patch('privacy.dao.DataRecogdb.RecogDb.mycol')
    @patch('privacy.dao.DataRecogdb.time.time')
    @patch('privacy.dao.DataRecogdb.datetime')
    def test_create_inserts_document(self, mock_datetime, mock_time, mock_mycol):
        """Test create inserts new document"""
        mock_time.return_value = 7777777777.0
        mock_now = Mock()
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 7777777777.0
        mock_mycol.insert_one.return_value = mock_insert_result
        
        value = {
            "Name": "CustomRecognizer",
            "entity": "CUSTOM_ENTITY",
            "type": "pattern",
            "score": 0.9,
            "context": ["context1"],
            "edit": True,
            "define": False
        }
        result = RecogDb.create(value)
        
        assert result == 7777777777.0
        mock_mycol.insert_one.assert_called_once()
        call_args = mock_mycol.insert_one.call_args[0][0]
        assert call_args["_id"] == 7777777777.0
        assert call_args["RecogId"] == 7777777777.0
        assert call_args["RecogName"] == "CustomRecognizer"
        assert call_args["supported_entity"] == "CUSTOM_ENTITY"
        assert call_args["RecogType"] == "pattern"
        assert call_args["Score"] == 0.9
        assert call_args["isActive"] == "Y"
        assert call_args["isCreated"] == "Not Started"
    
    @patch('privacy.dao.DataRecogdb.RecogDb.mycol')
    def test_update_modifies_document(self, mock_mycol):
        """Test update modifies existing document"""
        test_id = 777
        update_value = {"Score": 0.95, "isActive": "N"}
        
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_mycol.update_one.return_value = mock_update_result
        
        result = RecogDb.update(test_id, update_value)
        
        assert result is True
        mock_mycol.update_one.assert_called_once_with(
            {"_id": test_id},
            {"$set": update_value}
        )
    
    @patch('privacy.dao.DataRecogdb.RecogDb.mycol')
    def test_delete_removes_document(self, mock_mycol):
        """Test delete removes document"""
        test_id = 777
        
        mock_delete_result = Mock()
        mock_delete_result.acknowledged = True
        mock_mycol.delete_many.return_value = mock_delete_result
        
        result = RecogDb.delete(test_id)
        
        assert result is None  # delete doesn't return anything
        mock_mycol.delete_many.assert_called_once_with({"_id": test_id})
    
    @patch('privacy.dao.DataRecogdb.RecogDb.mycol')
    def test_findall_empty_result(self, mock_mycol):
        """Test findall with no results"""
        query = {"RecogName": "NonExistent"}
        mock_mycol.find.return_value = []
        
        result = RecogDb.findall(query)
        
        assert result == []
        mock_mycol.find.assert_called_once_with(query, {})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
