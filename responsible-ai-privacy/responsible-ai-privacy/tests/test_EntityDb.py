"""
Unit tests for privacy.dao.EntityDb module.
Tests EntityDb class database operations.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
sys.path.insert(0, 'src')
from privacy.dao.EntityDb import EntityDb, AttributeDict


class TestEntityDb:
    """Test EntityDb database operations"""
    
    @patch('privacy.dao.EntityDb.EntityDb.mycol')
    def test_findOne_returns_attribute_dict(self, mock_mycol):
        """Test findOne returns AttributeDict"""
        test_id = 111
        mock_data = {"_id": test_id, "EntityName": "PERSON", "RecogId": 222}
        mock_mycol.find.return_value = [mock_data]
        
        result = EntityDb.findOne(test_id)
        
        assert isinstance(result, AttributeDict)
        assert result._id == test_id
        assert result.EntityName == "PERSON"
        assert result.RecogId == 222
        mock_mycol.find.assert_called_once_with({"_id": test_id}, {})
    
    @patch('privacy.dao.EntityDb.EntityDb.mycol')
    def test_findall_returns_list(self, mock_mycol):
        """Test findall returns list of AttributeDict"""
        query = {"RecogId": 222}
        mock_data = [
            {"_id": 1, "EntityName": "PERSON"},
            {"_id": 2, "EntityName": "EMAIL"}
        ]
        mock_mycol.find.return_value = mock_data
        
        result = EntityDb.findall(query)
        
        assert len(result) == 2
        assert all(isinstance(item, AttributeDict) for item in result)
        assert result[0].EntityName == "PERSON"
        assert result[1].EntityName == "EMAIL"
        mock_mycol.find.assert_called_once_with(query, {})
    
    @patch('privacy.dao.EntityDb.EntityDb.mycol')
    @patch('privacy.dao.EntityDb.time.time')
    def test_create_inserts_document(self, mock_time, mock_mycol):
        """Test create inserts new document"""
        mock_time.return_value = 5555555555.0
        
        mock_insert_result = Mock()
        mock_insert_result.acknowledged = True
        mock_mycol.insert_one.return_value = mock_insert_result
        
        value = {"Name": "CREDIT_CARD", "dgid": 333}
        result = EntityDb.create(value)
        
        assert result is True
        mock_mycol.insert_one.assert_called_once()
        call_args = mock_mycol.insert_one.call_args[0][0]
        assert call_args["_id"] == 5555555555.0
        assert call_args["EntityId"] == 5555555555.0
        assert call_args["EntityName"] == "CREDIT_CARD"
        assert call_args["RecogId"] == 333
    
    @patch('privacy.dao.EntityDb.EntityDb.mycol')
    def test_update_modifies_document(self, mock_mycol):
        """Test update modifies existing document"""
        test_id = 111
        update_value = {"EntityName": "UPDATED_ENTITY"}
        
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_mycol.update_one.return_value = mock_update_result
        
        result = EntityDb.update(test_id, update_value)
        
        assert result is True
        mock_mycol.update_one.assert_called_once_with(
            {"_id": test_id},
            {"$set": update_value}
        )
    
    @patch('privacy.dao.EntityDb.EntityDb.mycol')
    def test_delete_removes_document(self, mock_mycol):
        """Test delete removes document"""
        test_id = 111
        
        mock_delete_result = Mock()
        mock_delete_result.acknowledged = True
        mock_mycol.delete_many.return_value = mock_delete_result
        
        result = EntityDb.delete(test_id)
        
        assert result is True
        mock_mycol.delete_many.assert_called_once_with({"_id": test_id})
    
    @patch('privacy.dao.EntityDb.EntityDb.mycol')
    def test_deleteMany_with_custom_query(self, mock_mycol):
        """Test deleteMany with custom query"""
        query = {"RecogId": 333}
        
        mock_delete_result = Mock()
        mock_delete_result.acknowledged = True
        mock_mycol.delete_many.return_value = mock_delete_result
        
        result = EntityDb.deleteMany(query)
        
        assert result is True
        mock_mycol.delete_many.assert_called_once_with(query)
    
    @patch('privacy.dao.EntityDb.EntityDb.mycol')
    def test_findall_empty_result(self, mock_mycol):
        """Test findall with no results"""
        query = {"EntityName": "NONEXISTENT"}
        mock_mycol.find.return_value = []
        
        result = EntityDb.findall(query)
        
        assert result == []
        mock_mycol.find.assert_called_once_with(query, {})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
