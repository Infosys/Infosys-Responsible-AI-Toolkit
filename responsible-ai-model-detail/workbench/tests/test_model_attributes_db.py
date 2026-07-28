"""
Unit tests for app.dao.ModelAttributesDb module.
Tests cover all methods and edge cases for 100% code coverage.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import datetime
import time

# Add src directory to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))


class TestAttributeDict:
    """Tests for AttributeDict class."""
    
    def test_attribute_dict_operations(self):
        """Test all AttributeDict operations."""
        from app.dao.ModelAttributesDb import AttributeDict
        
        attr_dict = AttributeDict({'key': 'value'})
        assert attr_dict['key'] == 'value'
        assert attr_dict.key == 'value'


@patch('app.dao.ModelAttributesDb.mydb')
class TestModelAttributes:
    """Tests for ModelAttributes class methods."""
    
    def test_get_all_success(self, mock_mydb):
        """Test get_all returns distinct values successfully."""
        from app.dao.ModelAttributesDb import ModelAttributes
        
        mock_collection = Mock()
        mock_collection.distinct.return_value = ['Accuracy', 'Precision', 'Recall']
        mock_mydb.__getitem__.return_value = mock_collection
        ModelAttributes.mycol = mock_collection
        
        result = ModelAttributes.get_all('ModelAttributeName')
        
        assert result == ['Accuracy', 'Precision', 'Recall']
        mock_collection.distinct.assert_called_once_with('ModelAttributeName')
    
    def test_get_all_empty(self, mock_mydb):
        """Test get_all returns empty list when no results."""
        from app.dao.ModelAttributesDb import ModelAttributes
        
        mock_collection = Mock()
        mock_collection.distinct.return_value = []
        ModelAttributes.mycol = mock_collection
        
        result = ModelAttributes.get_all('ModelAttributeName')
        
        assert result == []
    
    def test_findone_success(self, mock_mydb):
        """Test findOne returns attribute by ID."""
        from app.dao.ModelAttributesDb import ModelAttributes
        
        mock_collection = Mock()
        mock_result = [{'_id': '123', 'ModelAttributeName': 'TestAttr', 'IsActive': 'Y'}]
        mock_collection.find.return_value = mock_result
        ModelAttributes.mycol = mock_collection
        
        result = ModelAttributes.findOne('123')
        
        assert result._id == '123'
        assert result.ModelAttributeName == 'TestAttr'
        mock_collection.find.assert_called_once_with({"_id": '123'}, {})
    
    def test_findall_multiple_results(self, mock_mydb):
        """Test findall returns multiple records."""
        from app.dao.ModelAttributesDb import ModelAttributes
        
        mock_collection = Mock()
        mock_results = [
            {'_id': 1, 'ModelAttributeName': 'Attr1', 'IsActive': 'Y'},
            {'_id': 2, 'ModelAttributeName': 'Attr2', 'IsActive': 'Y'}
        ]
        mock_collection.find.return_value = mock_results
        ModelAttributes.mycol = mock_collection
        
        query = {"IsActive": "Y"}
        result = ModelAttributes.findall(query)
        
        assert len(result) == 2
        assert result[0].ModelAttributeName == 'Attr1'
        assert result[1].ModelAttributeName == 'Attr2'
        mock_collection.find.assert_called_once_with(query, {})
    
    def test_findall_empty(self, mock_mydb):
        """Test findall returns empty list."""
        from app.dao.ModelAttributesDb import ModelAttributes
        
        mock_collection = Mock()
        mock_collection.find.return_value = []
        ModelAttributes.mycol = mock_collection
        
        result = ModelAttributes.findall({"IsActive": "N"})
        
        assert result == []
    
    @patch('app.dao.ModelAttributesDb.time')
    @patch('app.dao.ModelAttributesDb.datetime')
    def test_create_success(self, mock_datetime, mock_time, mock_mydb):
        """Test create inserts new model attribute."""
        from app.dao.ModelAttributesDb import ModelAttributes
        
        mock_time.time.return_value = 1234567890.123
        mock_time.sleep = Mock()
        mock_now = datetime.datetime(2026, 1, 5, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_collection = Mock()
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 1234567890.123
        mock_collection.insert_one.return_value = mock_insert_result
        ModelAttributes.mycol = mock_collection
        
        values = {
            'modelAttributeName': 'TestAttribute',
            'tenetId': 'T001'
        }
        
        result = ModelAttributes.create(values)
        
        assert result == 1234567890.123
        mock_time.time.assert_called_once()
        mock_time.sleep.assert_called_once_with(1/1000)
        
        expected_doc = {
            "_id": 1234567890.123,
            "ModelAttributeId": 1234567890.123,
            "ModelAttributeName": 'TestAttribute',
            "IsActive": "Y",
            "TenetId": 'T001',
            "CreatedDateTime": mock_now,
            "LastUpdatedDateTime": mock_now,
        }
        mock_collection.insert_one.assert_called_once_with(expected_doc)
    
    @patch('app.dao.ModelAttributesDb.time')
    @patch('app.dao.ModelAttributesDb.datetime')
    def test_create_different_values(self, mock_datetime, mock_time, mock_mydb):
        """Test create with different attribute values."""
        from app.dao.ModelAttributesDb import ModelAttributes
        
        mock_time.time.return_value = 9876543210.456
        mock_time.sleep = Mock()
        mock_now = datetime.datetime(2026, 1, 5, 15, 30, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_collection = Mock()
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 9876543210.456
        mock_collection.insert_one.return_value = mock_insert_result
        ModelAttributes.mycol = mock_collection
        
        values = {
            'modelAttributeName': 'Accuracy',
            'tenetId': 'T002'
        }
        
        result = ModelAttributes.create(values)
        
        assert result == 9876543210.456
    
    @patch('app.dao.ModelAttributesDb.log')
    def test_update_success(self, mock_log, mock_mydb):
        """Test update modifies model attribute."""
        from app.dao.ModelAttributesDb import ModelAttributes
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_collection.update_one.return_value = mock_update_result
        ModelAttributes.mycol = mock_collection
        
        attr_id = 1234567890.123
        update_values = {'ModelAttributeName': 'UpdatedAttr', 'IsActive': 'N'}
        
        result = ModelAttributes.update(attr_id, update_values)
        
        assert result is True
        expected_newvalues = {"$set": update_values}
        mock_collection.update_one.assert_called_once_with(
            {"_id": attr_id},
            expected_newvalues
        )
        mock_log.debug.assert_called_once_with(str(expected_newvalues))
    
    @patch('app.dao.ModelAttributesDb.log')
    def test_update_not_acknowledged(self, mock_log, mock_mydb):
        """Test update returns False when not acknowledged."""
        from app.dao.ModelAttributesDb import ModelAttributes
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = False
        mock_collection.update_one.return_value = mock_update_result
        ModelAttributes.mycol = mock_collection
        
        result = ModelAttributes.update(123, {'IsActive': 'N'})
        
        assert result is False
    
    def test_findmavid_found(self, mock_mydb):
        """Test findMAVId returns ID when found."""
        from app.dao.ModelAttributesDb import ModelAttributes
        
        mock_collection = Mock()
        mock_collection.find_one.return_value = {'_id': 123, 'ModelAttributeName': 'TestAttr'}
        ModelAttributes.mycol = mock_collection
        
        name = {'ModelAttributeName': 'TestAttr'}
        id_dict = {'tenetId': 'T001'}
        
        result = ModelAttributes.findMAVId(name, id_dict)
        
        assert result == 123
        expected_query = {
            "ModelAttributeName": 'TestAttr',
            "TenetId": 'T001'
        }
        mock_collection.find_one.assert_called_once_with(expected_query)
    
    def test_findmavid_not_found(self, mock_mydb):
        """Test findMAVId returns None when not found."""
        from app.dao.ModelAttributesDb import ModelAttributes
        
        mock_collection = Mock()
        mock_collection.find_one.return_value = None
        ModelAttributes.mycol = mock_collection
        
        name = {'ModelAttributeName': 'NonExistent'}
        id_dict = {'tenetId': 'T999'}
        
        result = ModelAttributes.findMAVId(name, id_dict)
        
        assert result is None
    
    def test_delete_success(self, mock_mydb):
        """Test delete removes model attributes."""
        from app.dao.ModelAttributesDb import ModelAttributes
        
        mock_collection = Mock()
        mock_delete_result = Mock()
        mock_delete_result.deleted_count = 2
        mock_collection.delete_many.return_value = mock_delete_result
        ModelAttributes.mycol = mock_collection
        
        query = {"IsActive": "N"}
        ModelAttributes.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
    
    def test_delete_single_record(self, mock_mydb):
        """Test delete with single record."""
        from app.dao.ModelAttributesDb import ModelAttributes
        
        mock_collection = Mock()
        ModelAttributes.mycol = mock_collection
        
        query = {"_id": 123}
        ModelAttributes.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
