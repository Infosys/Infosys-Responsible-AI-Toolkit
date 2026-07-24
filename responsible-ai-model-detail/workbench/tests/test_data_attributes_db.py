"""
Unit tests for app.dao.DataAttributesDb module.
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
        from app.dao.DataAttributesDb import AttributeDict
        
        attr_dict = AttributeDict({'key': 'value'})
        assert attr_dict['key'] == 'value'
        assert attr_dict.key == 'value'
        
        attr_dict['new_key'] = 'new_value'
        assert attr_dict.new_key == 'new_value'
        
        attr_dict.another_key = 'another_value'
        assert attr_dict['another_key'] == 'another_value'
        
        del attr_dict['key']
        assert 'key' not in attr_dict
        
        attr_dict.test = 'test_value'
        del attr_dict.test
        assert 'test' not in attr_dict


@patch('app.dao.DataAttributesDb.mydb')
class TestDataAttributes:
    """Tests for DataAttributes class methods."""
    
    def test_get_all_success(self, mock_mydb):
        """Test get_all returns distinct values successfully."""
        from app.dao.DataAttributesDb import DataAttributes
        
        mock_collection = Mock()
        mock_collection.distinct.return_value = ['DatasetName', 'Description', 'Source']
        mock_mydb.__getitem__.return_value = mock_collection
        DataAttributes.mycol = mock_collection
        
        result = DataAttributes.get_all('DataAttributeName')
        
        assert result == ['DatasetName', 'Description', 'Source']
        mock_collection.distinct.assert_called_once_with('DataAttributeName')
    
    def test_get_all_empty(self, mock_mydb):
        """Test get_all returns empty list when no results."""
        from app.dao.DataAttributesDb import DataAttributes
        
        mock_collection = Mock()
        mock_collection.distinct.return_value = []
        DataAttributes.mycol = mock_collection
        
        result = DataAttributes.get_all('DataAttributeName')
        
        assert result == []
    
    def test_findone_success(self, mock_mydb):
        """Test findOne returns attribute by ID."""
        from app.dao.DataAttributesDb import DataAttributes
        
        mock_collection = Mock()
        mock_result = [{'_id': '123', 'DataAttributeName': 'TestAttr', 'IsActive': 'Y'}]
        mock_collection.find.return_value = mock_result
        DataAttributes.mycol = mock_collection
        
        result = DataAttributes.findOne('123')
        
        assert result._id == '123'
        assert result.DataAttributeName == 'TestAttr'
        mock_collection.find.assert_called_once_with({"_id": '123'}, {})
    
    def test_findall_multiple_results(self, mock_mydb):
        """Test findall returns multiple records."""
        from app.dao.DataAttributesDb import DataAttributes
        
        mock_collection = Mock()
        mock_results = [
            {'_id': 1, 'DataAttributeName': 'Attr1', 'IsActive': 'Y'},
            {'_id': 2, 'DataAttributeName': 'Attr2', 'IsActive': 'Y'}
        ]
        mock_collection.find.return_value = mock_results
        DataAttributes.mycol = mock_collection
        
        query = {"IsActive": "Y"}
        result = DataAttributes.findall(query)
        
        assert len(result) == 2
        assert result[0].DataAttributeName == 'Attr1'
        assert result[1].DataAttributeName == 'Attr2'
        mock_collection.find.assert_called_once_with(query, {})
    
    def test_findall_single_result(self, mock_mydb):
        """Test findall returns single record."""
        from app.dao.DataAttributesDb import DataAttributes
        
        mock_collection = Mock()
        mock_results = [{'_id': 1, 'DataAttributeName': 'Attr1'}]
        mock_collection.find.return_value = mock_results
        DataAttributes.mycol = mock_collection
        
        query = {"DataAttributeName": "Attr1"}
        result = DataAttributes.findall(query)
        
        assert len(result) == 1
        assert result[0].DataAttributeName == 'Attr1'
    
    def test_findall_empty(self, mock_mydb):
        """Test findall returns empty list."""
        from app.dao.DataAttributesDb import DataAttributes
        
        mock_collection = Mock()
        mock_collection.find.return_value = []
        DataAttributes.mycol = mock_collection
        
        result = DataAttributes.findall({"IsActive": "N"})
        
        assert result == []
    
    @patch('app.dao.DataAttributesDb.time')
    @patch('app.dao.DataAttributesDb.datetime')
    def test_create_success(self, mock_datetime, mock_time, mock_mydb):
        """Test create inserts new data attribute."""
        from app.dao.DataAttributesDb import DataAttributes
        
        mock_time.time.return_value = 1234567890.123
        mock_time.sleep = Mock()
        mock_now = datetime.datetime(2026, 1, 5, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_collection = Mock()
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 1234567890.123
        mock_collection.insert_one.return_value = mock_insert_result
        DataAttributes.mycol = mock_collection
        
        values = {
            'dataAttributeName': 'TestAttribute',
            'tenetId': 'T001'
        }
        
        result = DataAttributes.create(values)
        
        assert result == 1234567890.123
        mock_time.time.assert_called_once()
        mock_time.sleep.assert_called_once_with(1/1000)
        
        expected_doc = {
            "_id": 1234567890.123,
            "DataAttributeId": 1234567890.123,
            "DataAttributeName": 'TestAttribute',
            "IsActive": "Y",
            "TenetId": 'T001',
            "CreatedDateTime": mock_now,
            "LastUpdatedDateTime": mock_now,
        }
        mock_collection.insert_one.assert_called_once_with(expected_doc)
    
    @patch('app.dao.DataAttributesDb.time')
    @patch('app.dao.DataAttributesDb.datetime')
    def test_create_different_values(self, mock_datetime, mock_time, mock_mydb):
        """Test create with different attribute values."""
        from app.dao.DataAttributesDb import DataAttributes
        
        mock_time.time.return_value = 9876543210.456
        mock_time.sleep = Mock()
        mock_now = datetime.datetime(2026, 1, 5, 15, 30, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_collection = Mock()
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 9876543210.456
        mock_collection.insert_one.return_value = mock_insert_result
        DataAttributes.mycol = mock_collection
        
        values = {
            'dataAttributeName': 'Description',
            'tenetId': 'T002'
        }
        
        result = DataAttributes.create(values)
        
        assert result == 9876543210.456
    
    def test_finddavid_found(self, mock_mydb):
        """Test findDAVId returns ID when found."""
        from app.dao.DataAttributesDb import DataAttributes
        
        mock_collection = Mock()
        mock_collection.find_one.return_value = {'_id': 123, 'DataAttributeName': 'TestAttr'}
        DataAttributes.mycol = mock_collection
        
        name = {'DataAttributeName': 'TestAttr'}
        id_dict = {'tenetId': 'T001'}
        
        result = DataAttributes.findDAVId(name, id_dict)
        
        assert result == 123
        expected_query = {
            "DataAttributeName": 'TestAttr',
            "TenetId": 'T001'
        }
        mock_collection.find_one.assert_called_once_with(expected_query)
    
    def test_finddavid_not_found(self, mock_mydb):
        """Test findDAVId returns None when not found."""
        from app.dao.DataAttributesDb import DataAttributes
        
        mock_collection = Mock()
        mock_collection.find_one.return_value = None
        DataAttributes.mycol = mock_collection
        
        name = {'DataAttributeName': 'NonExistent'}
        id_dict = {'tenetId': 'T999'}
        
        result = DataAttributes.findDAVId(name, id_dict)
        
        assert result is None
    
    @patch('app.dao.DataAttributesDb.log')
    def test_update_success(self, mock_log, mock_mydb):
        """Test update modifies data attribute."""
        from app.dao.DataAttributesDb import DataAttributes
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_collection.update_one.return_value = mock_update_result
        DataAttributes.mycol = mock_collection
        
        attr_id = 1234567890.123
        update_values = {'DataAttributeName': 'UpdatedAttr', 'IsActive': 'N'}
        
        result = DataAttributes.update(attr_id, update_values)
        
        assert result is True
        expected_newvalues = {"$set": update_values}
        mock_collection.update_one.assert_called_once_with(
            {"_id": attr_id},
            expected_newvalues
        )
        mock_log.debug.assert_called_once_with(str(expected_newvalues))
    
    @patch('app.dao.DataAttributesDb.log')
    def test_update_not_acknowledged(self, mock_log, mock_mydb):
        """Test update returns False when not acknowledged."""
        from app.dao.DataAttributesDb import DataAttributes
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = False
        mock_collection.update_one.return_value = mock_update_result
        DataAttributes.mycol = mock_collection
        
        result = DataAttributes.update(123, {'IsActive': 'N'})
        
        assert result is False
    
    @patch('app.dao.DataAttributesDb.log')
    def test_update_multiple_fields(self, mock_log, mock_mydb):
        """Test update with multiple fields."""
        from app.dao.DataAttributesDb import DataAttributes
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_collection.update_one.return_value = mock_update_result
        DataAttributes.mycol = mock_collection
        
        update_values = {
            'DataAttributeName': 'NewName',
            'IsActive': 'Y',
            'TenetId': 'T003'
        }
        
        result = DataAttributes.update(456, update_values)
        
        assert result is True
    
    def test_delete_success(self, mock_mydb):
        """Test delete removes data attributes."""
        from app.dao.DataAttributesDb import DataAttributes
        
        mock_collection = Mock()
        mock_delete_result = Mock()
        mock_delete_result.deleted_count = 2
        mock_collection.delete_many.return_value = mock_delete_result
        DataAttributes.mycol = mock_collection
        
        query = {"IsActive": "N"}
        DataAttributes.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
    
    def test_delete_single_record(self, mock_mydb):
        """Test delete with single record."""
        from app.dao.DataAttributesDb import DataAttributes
        
        mock_collection = Mock()
        DataAttributes.mycol = mock_collection
        
        query = {"_id": 123}
        DataAttributes.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
    
    def test_delete_no_matching_records(self, mock_mydb):
        """Test delete when no records match."""
        from app.dao.DataAttributesDb import DataAttributes
        
        mock_collection = Mock()
        DataAttributes.mycol = mock_collection
        
        query = {"DataAttributeName": "NonExistent"}
        DataAttributes.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
