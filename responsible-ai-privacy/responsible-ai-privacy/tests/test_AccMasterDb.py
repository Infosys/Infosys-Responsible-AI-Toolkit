"""
Unit tests for privacy.dao.AccMasterDb module.
Tests AccMasterDb class database operations.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
sys.path.insert(0, 'src')
from privacy.dao.AccMasterDb import AccMasterDb, AttributeDict


class TestAttributeDict:
    """Test AttributeDict functionality"""
    
    def test_attribute_dict_getitem(self):
        """Test getting items as attributes"""
        attr_dict = AttributeDict({"key": "value"})
        assert attr_dict.key == "value"
        assert attr_dict["key"] == "value"
    
    def test_attribute_dict_setitem(self):
        """Test setting items as attributes"""
        attr_dict = AttributeDict()
        attr_dict.key = "value"
        assert attr_dict["key"] == "value"
    
    def test_attribute_dict_delitem(self):
        """Test deleting items as attributes"""
        attr_dict = AttributeDict({"key": "value"})
        del attr_dict.key
        assert "key" not in attr_dict


class TestAccMasterDb:
    """Test AccMasterDb database operations"""
    
    @patch('privacy.dao.AccMasterDb.AccMasterDb.mycol')
    def test_findOne_returns_attribute_dict(self, mock_mycol):
        """Test findOne returns AttributeDict"""
        test_id = 123
        mock_data = {"_id": test_id, "portfolio": "TestPortfolio", "account": "TestAccount"}
        mock_mycol.find.return_value = [mock_data]
        
        result = AccMasterDb.findOne(test_id)
        
        assert isinstance(result, AttributeDict)
        assert result._id == test_id
        assert result.portfolio == "TestPortfolio"
        mock_mycol.find.assert_called_once_with({"_id": test_id}, {})
    
    @patch('privacy.dao.AccMasterDb.AccMasterDb.mycol')
    def test_findall_returns_list(self, mock_mycol):
        """Test findall returns list of AttributeDict"""
        query = {"isActive": "Y"}
        mock_data = [
            {"_id": 1, "portfolio": "Port1"},
            {"_id": 2, "portfolio": "Port2"}
        ]
        mock_mycol.find.return_value = mock_data
        
        result = AccMasterDb.findall(query)
        
        assert len(result) == 2
        assert all(isinstance(item, AttributeDict) for item in result)
        assert result[0].portfolio == "Port1"
        assert result[1].portfolio == "Port2"
        mock_mycol.find.assert_called_once_with(query, {})
    
    @patch('privacy.dao.AccMasterDb.AccMasterDb.mycol')
    @patch('privacy.dao.AccMasterDb.time.time')
    @patch('privacy.dao.AccMasterDb.datetime')
    def test_create_inserts_document(self, mock_datetime, mock_time, mock_mycol):
        """Test create inserts new document"""
        mock_time.return_value = 1234567890.0
        mock_now = Mock()
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 1234567890.0
        mock_mycol.insert_one.return_value = mock_insert_result
        
        value = {"AName": "TestPortfolio", "SName": "TestAccount"}
        result = AccMasterDb.create(value)
        
        assert result == 1234567890.0
        mock_mycol.insert_one.assert_called_once()
        call_args = mock_mycol.insert_one.call_args[0][0]
        assert call_args["_id"] == 1234567890.0
        assert call_args["portfolio"] == "TestPortfolio"
        assert call_args["account"] == "TestAccount"
        assert call_args["ThresholdScore"] == 0.85
        assert call_args["isActive"] == "Y"
    
    @patch('privacy.dao.AccMasterDb.AccMasterDb.mycol')
    def test_update_modifies_document(self, mock_mycol):
        """Test update modifies existing document"""
        test_id = 123
        update_value = {"ThresholdScore": 0.9, "isActive": "N"}
        
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_mycol.update_one.return_value = mock_update_result
        
        result = AccMasterDb.update(test_id, update_value)
        
        assert result is True
        mock_mycol.update_one.assert_called_once_with(
            {"_id": test_id},
            {"$set": update_value}
        )
    
    @patch('privacy.dao.AccMasterDb.AccMasterDb.mycol')
    def test_delete_removes_document(self, mock_mycol):
        """Test delete removes document"""
        test_id = 123
        
        mock_delete_result = Mock()
        mock_delete_result.acknowledged = True
        mock_mycol.delete_many.return_value = mock_delete_result
        
        result = AccMasterDb.delete(test_id)
        
        assert result is True
        mock_mycol.delete_many.assert_called_once_with({"_id": test_id})
    
    @patch('privacy.dao.AccMasterDb.AccMasterDb.mycol')
    def test_findall_empty_result(self, mock_mycol):
        """Test findall with no results"""
        query = {"isActive": "X"}
        mock_mycol.find.return_value = []
        
        result = AccMasterDb.findall(query)
        
        assert result == []
        mock_mycol.find.assert_called_once_with(query, {})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
