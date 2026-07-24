"""
Unit tests for privacy.dao.TelemetryFlagDb module.
Tests TelemetryFlag class database operations.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
sys.path.insert(0, 'src')
from privacy.dao.TelemetryFlagDb import TelemetryFlag, AttributeDict


class TestTelemetryFlag:
    """Test TelemetryFlag database operations"""
    
    @patch('privacy.dao.TelemetryFlagDb.TelemetryFlag.mycol')
    def test_findOne_returns_attribute_dict(self, mock_mycol):
        """Test findOne returns AttributeDict"""
        test_id = 888
        mock_data = {"_id": test_id, "Module": "TestModule", "TelemetryFlag": True}
        mock_mycol.find.return_value = [mock_data]
        
        result = TelemetryFlag.findOne(test_id)
        
        assert isinstance(result, AttributeDict)
        assert result._id == test_id
        assert result.Module == "TestModule"
        assert result.TelemetryFlag is True
        mock_mycol.find.assert_called_once_with({"_id": test_id}, {})
    
    @patch('privacy.dao.TelemetryFlagDb.TelemetryFlag.mycol')
    def test_findall_returns_list(self, mock_mycol):
        """Test findall returns list of AttributeDict"""
        query = {"TelemetryFlag": True}
        mock_data = [
            {"_id": 1, "Module": "Module1", "TelemetryFlag": True},
            {"_id": 2, "Module": "Module2", "TelemetryFlag": True}
        ]
        mock_mycol.find.return_value = mock_data
        
        result = TelemetryFlag.findall(query)
        
        assert len(result) == 2
        assert all(isinstance(item, AttributeDict) for item in result)
        assert result[0].Module == "Module1"
        assert result[1].Module == "Module2"
        mock_mycol.find.assert_called_once_with(query, {})
    
    @patch('privacy.dao.TelemetryFlagDb.TelemetryFlag.mycol')
    @patch('privacy.dao.TelemetryFlagDb.time.time')
    @patch('privacy.dao.TelemetryFlagDb.datetime')
    def test_create_inserts_document(self, mock_datetime, mock_time, mock_mycol):
        """Test create inserts new document"""
        mock_time.return_value = 8888888888.0
        mock_now = Mock()
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 8888888888.0
        mock_mycol.insert_one.return_value = mock_insert_result
        
        value = {"module": "NewModule"}
        result = TelemetryFlag.create(value)
        
        assert result == 8888888888.0
        mock_mycol.insert_one.assert_called_once()
        call_args = mock_mycol.insert_one.call_args[0][0]
        assert call_args["_id"] == 8888888888.0
        assert call_args["Module"] == "NewModule"
        assert call_args["TelemetryFlag"] is False  # Default value
    
    @patch('privacy.dao.TelemetryFlagDb.TelemetryFlag.mycol')
    def test_update_modifies_document(self, mock_mycol):
        """Test update modifies existing document"""
        test_id = 888
        update_value = {"TelemetryFlag": True}
        
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_mycol.update_one.return_value = mock_update_result
        
        result = TelemetryFlag.update(test_id, update_value)
        
        assert result is True
        mock_mycol.update_one.assert_called_once_with(
            {"_id": test_id},
            {"$set": update_value}
        )
    
    @patch('privacy.dao.TelemetryFlagDb.TelemetryFlag.mycol')
    def test_delete_removes_document(self, mock_mycol):
        """Test delete removes document"""
        test_id = 888
        
        mock_delete_result = Mock()
        mock_delete_result.acknowledged = True
        mock_mycol.delete_many.return_value = mock_delete_result
        
        result = TelemetryFlag.delete(test_id)
        
        assert result is None  # delete doesn't return anything
        mock_mycol.delete_many.assert_called_once_with({"_id": test_id})
    
    @patch('privacy.dao.TelemetryFlagDb.TelemetryFlag.mycol')
    def test_findall_empty_result(self, mock_mycol):
        """Test findall with no results"""
        query = {"Module": "NonExistent"}
        mock_mycol.find.return_value = []
        
        result = TelemetryFlag.findall(query)
        
        assert result == []
        mock_mycol.find.assert_called_once_with(query, {})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
