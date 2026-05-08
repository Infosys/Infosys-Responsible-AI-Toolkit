"""
Unit tests for privacy.dao.AccPtrnMappingDb module.
Tests AccPtrnDb class database operations.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
sys.path.insert(0, 'src')
from privacy.dao.AccPtrnMappingDb import AccPtrnDb, AttributeDict


class TestAccPtrnDb:
    """Test AccPtrnDb database operations"""
    
    @patch('privacy.dao.AccPtrnMappingDb.AccPtrnDb.mycol')
    def test_findOne_returns_attribute_dict(self, mock_mycol):
        """Test findOne returns AttributeDict"""
        test_id = 555
        mock_data = {"_id": test_id, "accMasterId": 123, "ptrnRecId": 456}
        mock_mycol.find.return_value = [mock_data]
        
        result = AccPtrnDb.findOne(test_id)
        
        assert isinstance(result, AttributeDict)
        assert result._id == test_id
        assert result.accMasterId == 123
        assert result.ptrnRecId == 456
        mock_mycol.find.assert_called_once_with({"_id": test_id}, {})
    
    @patch('privacy.dao.AccPtrnMappingDb.AccPtrnDb.mycol')
    def test_findall_returns_list(self, mock_mycol):
        """Test findall returns list of AttributeDict"""
        query = {"isActive": "Y"}
        mock_data = [
            {"_id": 1, "accMasterId": 100, "ptrnRecId": 200},
            {"_id": 2, "accMasterId": 101, "ptrnRecId": 201}
        ]
        mock_mycol.find.return_value = mock_data
        
        result = AccPtrnDb.findall(query)
        
        assert len(result) == 2
        assert all(isinstance(item, AttributeDict) for item in result)
        assert result[0].accMasterId == 100
        assert result[1].ptrnRecId == 201
        mock_mycol.find.assert_called_once_with(query, {})
    
    @patch('privacy.dao.AccPtrnMappingDb.AccPtrnDb.mycol')
    @patch('privacy.dao.AccPtrnMappingDb.time.time')
    @patch('privacy.dao.AccPtrnMappingDb.datetime')
    def test_create_inserts_document(self, mock_datetime, mock_time, mock_mycol):
        """Test create inserts new document"""
        mock_time.return_value = 6666666666.0
        mock_now = Mock()
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 6666666666.0
        mock_mycol.insert_one.return_value = mock_insert_result
        
        value = {"Aid": 123, "Pid": 456}
        result = AccPtrnDb.create(value)
        
        assert result == 6666666666.0
        mock_mycol.insert_one.assert_called_once()
        call_args = mock_mycol.insert_one.call_args[0][0]
        assert call_args["_id"] == 6666666666.0
        assert call_args["accMasterId"] == 123
        assert call_args["ptrnRecId"] == 456
        assert call_args["isActive"] == "Y"
        assert call_args["isCreated"] == "Not Started"
    
    @patch('privacy.dao.AccPtrnMappingDb.AccPtrnDb.mycol')
    def test_update_modifies_document(self, mock_mycol):
        """Test update modifies existing document"""
        test_id = 555
        update_value = {"isActive": "N"}
        
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_mycol.update_one.return_value = mock_update_result
        
        result = AccPtrnDb.update(test_id, update_value)
        
        assert result is True
        mock_mycol.update_one.assert_called_once_with(
            {"_id": test_id},
            {"$set": update_value}
        )
    
    @patch('privacy.dao.AccPtrnMappingDb.AccPtrnDb.mycol')
    def test_delete_removes_document(self, mock_mycol):
        """Test delete removes document"""
        test_id = 555
        
        mock_delete_result = Mock()
        mock_delete_result.acknowledged = True
        mock_mycol.delete_many.return_value = mock_delete_result
        
        result = AccPtrnDb.delete(test_id)
        
        assert result is None  # delete doesn't return anything
        mock_mycol.delete_many.assert_called_once_with({"_id": test_id})
    
    @patch('privacy.dao.AccPtrnMappingDb.AccPtrnDb.mycol')
    def test_findall_empty_result(self, mock_mycol):
        """Test findall with no results"""
        query = {"isActive": "X"}
        mock_mycol.find.return_value = []
        
        result = AccPtrnDb.findall(query)
        
        assert result == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
