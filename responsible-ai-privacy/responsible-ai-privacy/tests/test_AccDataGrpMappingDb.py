"""
Unit tests for privacy.dao.AccDataGrpMappingDb module.
Tests AccDataGrpDb class database operations.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
sys.path.insert(0, 'src')
from privacy.dao.AccDataGrpMappingDb import AccDataGrpDb, AttributeDict


class TestAccDataGrpDb:
    """Test AccDataGrpDb database operations"""
    
    @patch('privacy.dao.AccDataGrpMappingDb.AccDataGrpDb.mycol')
    def test_findOne_returns_attribute_dict(self, mock_mycol):
        """Test findOne returns AttributeDict"""
        test_id = 456
        mock_data = {"_id": test_id, "accMasterId": 123, "dataRecogGrpId": 789}
        mock_mycol.find.return_value = [mock_data]
        
        result = AccDataGrpDb.findOne(test_id)
        
        assert isinstance(result, AttributeDict)
        assert result._id == test_id
        assert result.accMasterId == 123
        assert result.dataRecogGrpId == 789
        mock_mycol.find.assert_called_once_with({"_id": test_id}, {})
    
    @patch('privacy.dao.AccDataGrpMappingDb.AccDataGrpDb.mycol')
    def test_findall_returns_list(self, mock_mycol):
        """Test findall returns list of AttributeDict"""
        query = {"isActive": "Y"}
        mock_data = [
            {"_id": 1, "accMasterId": 10},
            {"_id": 2, "accMasterId": 20}
        ]
        mock_mycol.find.return_value = mock_data
        
        result = AccDataGrpDb.findall(query)
        
        assert len(result) == 2
        assert all(isinstance(item, AttributeDict) for item in result)
        assert result[0].accMasterId == 10
        assert result[1].accMasterId == 20
        mock_mycol.find.assert_called_once_with(query, {})
    
    @patch('privacy.dao.AccDataGrpMappingDb.AccDataGrpDb.mycol')
    @patch('privacy.dao.AccDataGrpMappingDb.time.time')
    @patch('privacy.dao.AccDataGrpMappingDb.datetime')
    def test_create_inserts_document(self, mock_datetime, mock_time, mock_mycol):
        """Test create inserts new document"""
        mock_time.return_value = 9876543210.0
        mock_now = Mock()
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_insert_result = Mock()
        mock_insert_result.acknowledged = True
        mock_mycol.insert_one.return_value = mock_insert_result
        
        value = {"Aid": 123, "Did": 789}
        result = AccDataGrpDb.create(value)
        
        assert result is True
        mock_mycol.insert_one.assert_called_once()
        call_args = mock_mycol.insert_one.call_args[0][0]
        assert call_args["_id"] == 9876543210.0
        assert call_args["accMasterId"] == 123
        assert call_args["dataRecogGrpId"] == 789
        assert call_args["isActive"] == "Y"
        assert call_args["isHashify"] is False
    
    @patch('privacy.dao.AccDataGrpMappingDb.AccDataGrpDb.mycol')
    def test_update_modifies_document(self, mock_mycol):
        """Test update modifies existing document"""
        query = {"_id": 123}
        update_value = {"isActive": "N", "isHashify": True}
        
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_mycol.update_one.return_value = mock_update_result
        
        result = AccDataGrpDb.update(query, update_value)
        
        assert result is True
        mock_mycol.update_one.assert_called_once_with(
            query,
            {"$set": update_value}
        )
    
    @patch('privacy.dao.AccDataGrpMappingDb.AccDataGrpDb.mycol')
    def test_delete_removes_by_dataRecogGrpId(self, mock_mycol):
        """Test delete removes documents by dataRecogGrpId"""
        test_id = 789
        
        mock_delete_result = Mock()
        mock_delete_result.acknowledged = True
        mock_mycol.delete_many.return_value = mock_delete_result
        
        result = AccDataGrpDb.delete(test_id)
        
        assert result is True
        mock_mycol.delete_many.assert_called_once_with({"dataRecogGrpId": test_id})
    
    @patch('privacy.dao.AccDataGrpMappingDb.AccDataGrpDb.mycol')
    def test_deleteMany_with_custom_query(self, mock_mycol):
        """Test deleteMany with custom query"""
        query = {"isActive": "N", "accMasterId": 123}
        
        mock_delete_result = Mock()
        mock_delete_result.acknowledged = True
        mock_mycol.delete_many.return_value = mock_delete_result
        
        result = AccDataGrpDb.deleteMany(query)
        
        assert result is True
        mock_mycol.delete_many.assert_called_once_with(query)
    
    @patch('privacy.dao.AccDataGrpMappingDb.AccDataGrpDb.mycol')
    def test_findall_empty_result(self, mock_mycol):
        """Test findall with no results"""
        query = {"isActive": "X"}
        mock_mycol.find.return_value = []
        
        result = AccDataGrpDb.findall(query)
        
        assert result == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
