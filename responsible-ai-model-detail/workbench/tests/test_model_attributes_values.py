"""
Unit tests for app.dao.ModelAttributesValuesDb module.
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
    """Tests for AttributeDict class in ModelAttributesValuesDb."""
    
    def test_attribute_dict_basic_operations(self):
        """Test basic AttributeDict operations."""
        from app.dao.ModelAttributesValuesDb import AttributeDict
        attr_dict = AttributeDict({'key': 'value'})
        assert attr_dict['key'] == 'value'
        assert attr_dict.key == 'value'
        
        attr_dict.new_key = 'new_value'
        assert attr_dict['new_key'] == 'new_value'


@patch('app.dao.ModelAttributesValuesDb.mydb')
@patch('app.dao.ModelAttributesValuesDb.log')
class TestModelAttributesValues:
    """Tests for ModelAttributesValues class methods."""
    
    def test_findone_success(self, mock_log, mock_mydb):
        """Test findOne returns AttributeDict for given id."""
        from app.dao.ModelAttributesValuesDb import ModelAttributesValues
        
        mock_collection = Mock()
        mock_result = [{'_id': 123, 'ModelAttributeValuesId': 456, 'ModelAttributeValues': 'test_value'}]
        mock_collection.find.return_value = mock_result
        ModelAttributesValues.mycol = mock_collection
        
        result = ModelAttributesValues.findOne(123)
        
        assert result._id == 123
        assert result.ModelAttributeValuesId == 456
        mock_collection.find.assert_called_once_with({"_id": 123}, {})
    
    def test_findall_multiple_results(self, mock_log, mock_mydb):
        """Test findall returns list of AttributeDict objects."""
        from app.dao.ModelAttributesValuesDb import ModelAttributesValues
        
        mock_collection = Mock()
        mock_results = [
            {'_id': 1, 'ModelAttributeId': 'attr1', 'ModelId': 'model1'},
            {'_id': 2, 'ModelAttributeId': 'attr2', 'ModelId': 'model2'}
        ]
        mock_collection.find.return_value = mock_results
        ModelAttributesValues.mycol = mock_collection
        
        query = {"IsActive": "Y"}
        result = ModelAttributesValues.findall(query)
        
        assert len(result) == 2
        assert result[0].ModelAttributeId == 'attr1'
        assert result[1].ModelAttributeId == 'attr2'
        mock_collection.find.assert_called_once_with(query, {})
    
    def test_findall_empty_results(self, mock_log, mock_mydb):
        """Test findall returns empty list when no results."""
        from app.dao.ModelAttributesValuesDb import ModelAttributesValues
        
        mock_collection = Mock()
        mock_collection.find.return_value = []
        ModelAttributesValues.mycol = mock_collection
        
        query = {"ModelId": "nonexistent"}
        result = ModelAttributesValues.findall(query)
        
        assert result == []
    
    @patch('app.dao.ModelAttributesValuesDb.time')
    @patch('app.dao.ModelAttributesValuesDb.datetime')
    def test_create_success(self, mock_datetime, mock_time, mock_log, mock_mydb):
        """Test create inserts new model attribute value successfully."""
        from app.dao.ModelAttributesValuesDb import ModelAttributesValues
        
        mock_time.time.return_value = 1234567890.123
        mock_time.sleep = Mock()
        mock_now = datetime.datetime(2026, 1, 5, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_collection = Mock()
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 1234567890.123
        mock_collection.insert_one.return_value = mock_insert_result
        ModelAttributesValues.mycol = mock_collection
        
        values = {
            'modelAttributeId': 'attr123',
            'modelId': 'model456',
            'modelAttributeValues': 'test_value'
        }
        
        result = ModelAttributesValues.create(values)
        
        assert result == 1234567890.123
        mock_time.time.assert_called_once()
        mock_time.sleep.assert_called_once_with(1/1000)
        
        expected_doc = {
            "_id": 1234567890.123,
            "ModelAttributeValuesId": 1234567890.123,
            "ModelAttributeId": 'attr123',
            "ModelId": 'model456',
            "ModelAttributeValues": 'test_value',
            "IsActive": "Y",
            "CreatedDateTime": mock_now,
            "LastUpdatedDateTime": mock_now,
        }
        mock_collection.insert_one.assert_called_once_with(expected_doc)
    
    def test_update_success(self, mock_log, mock_mydb):
        """Test update modifies model attribute value successfully."""
        from app.dao.ModelAttributesValuesDb import ModelAttributesValues
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_collection.update_one.return_value = mock_update_result
        ModelAttributesValues.mycol = mock_collection
        
        attr_id = 123
        update_values = {'ModelAttributeValues': 'updated_value', 'IsActive': 'N'}
        
        result = ModelAttributesValues.update(attr_id, update_values)
        
        assert result is True
        expected_newvalues = {"$set": update_values}
        mock_collection.update_one.assert_called_once_with(
            {"_id": attr_id},
            expected_newvalues
        )
        mock_log.debug.assert_called_once_with(str(expected_newvalues))
    
    def test_update_not_acknowledged(self, mock_log, mock_mydb):
        """Test update returns False when not acknowledged."""
        from app.dao.ModelAttributesValuesDb import ModelAttributesValues
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = False
        mock_collection.update_one.return_value = mock_update_result
        ModelAttributesValues.mycol = mock_collection
        
        result = ModelAttributesValues.update(123, {'IsActive': 'N'})
        
        assert result is False
    
    @patch('app.dao.ModelAttributesValuesDb.time')
    @patch('app.dao.ModelAttributesValuesDb.datetime')
    def test_create_for_batch_data_success(self, mock_datetime, mock_time, mock_log, mock_mydb):
        """Test createForBatchData inserts batch-specific model attribute value."""
        from app.dao.ModelAttributesValuesDb import ModelAttributesValues
        
        mock_time.time.return_value = 9876543210.456
        mock_time.sleep = Mock()
        mock_now = datetime.datetime(2026, 1, 5, 15, 30, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_collection = Mock()
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 9876543210.456
        mock_collection.insert_one.return_value = mock_insert_result
        ModelAttributesValues.mycol = mock_collection
        
        values = {
            'ModelAttributeId': 'attr789',
            'modelId': 'model101',
            'ModelAttributevalues': 'batch_value',
            'BatchId': 'batch202'
        }
        
        ModelAttributesValues.createForBatchData(values)
        
        expected_doc = {
            "_id": 9876543210.456,
            "ModelAttributeValuesId": 9876543210.456,
            "ModelAttributeId": 'attr789',
            "ModelId": 'model101',
            "ModelAttributeValues": 'batch_value',
            "IsActive": "Y",
            "BatchId": 'batch202',
            "CreatedDateTime": mock_now,
            "LastUpdatedDateTime": mock_now,
        }
        mock_collection.insert_one.assert_called_once_with(expected_doc)
        mock_time.time.assert_called_once()
        mock_time.sleep.assert_called_once_with(1/1000)
    
    @patch('app.dao.ModelAttributesValuesDb.time')
    @patch('app.dao.ModelAttributesValuesDb.datetime')
    def test_create_for_batch_data_with_different_values(self, mock_datetime, mock_time, mock_log, mock_mydb):
        """Test createForBatchData with different batch data."""
        from app.dao.ModelAttributesValuesDb import ModelAttributesValues
        
        mock_time.time.return_value = 1111111111.111
        mock_time.sleep = Mock()
        mock_now = datetime.datetime(2026, 1, 5, 10, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_collection = Mock()
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 1111111111.111
        mock_collection.insert_one.return_value = mock_insert_result
        ModelAttributesValues.mycol = mock_collection
        
        values = {
            'ModelAttributeId': 'attr_new',
            'modelId': 'model_new',
            'ModelAttributevalues': 'new_batch_value',
            'BatchId': 'batch_new'
        }
        
        ModelAttributesValues.createForBatchData(values)
        
        assert mock_collection.insert_one.called
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args['ModelAttributeId'] == 'attr_new'
        assert call_args['ModelId'] == 'model_new'
        assert call_args['ModelAttributeValues'] == 'new_batch_value'
        assert call_args['BatchId'] == 'batch_new'
    
    def test_delete_success(self, mock_log, mock_mydb):
        """Test delete removes model attribute values matching query."""
        from app.dao.ModelAttributesValuesDb import ModelAttributesValues
        
        mock_collection = Mock()
        mock_delete_result = Mock()
        mock_delete_result.deleted_count = 3
        mock_collection.delete_many.return_value = mock_delete_result
        ModelAttributesValues.mycol = mock_collection
        
        query = {"IsActive": "N"}
        ModelAttributesValues.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
    
    def test_delete_with_model_id(self, mock_log, mock_mydb):
        """Test delete with specific model id."""
        from app.dao.ModelAttributesValuesDb import ModelAttributesValues
        
        mock_collection = Mock()
        mock_delete_result = Mock()
        mock_delete_result.deleted_count = 1
        mock_collection.delete_many.return_value = mock_delete_result
        ModelAttributesValues.mycol = mock_collection
        
        query = {"ModelId": "model123", "IsActive": "N"}
        ModelAttributesValues.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
    
    def test_delete_no_matching_records(self, mock_log, mock_mydb):
        """Test delete when no records match the query."""
        from app.dao.ModelAttributesValuesDb import ModelAttributesValues
        
        mock_collection = Mock()
        mock_delete_result = Mock()
        mock_delete_result.deleted_count = 0
        mock_collection.delete_many.return_value = mock_delete_result
        ModelAttributesValues.mycol = mock_collection
        
        query = {"ModelId": "nonexistent"}
        ModelAttributesValues.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
    
    def test_findall_with_complex_query(self, mock_log, mock_mydb):
        """Test findall with complex query conditions."""
        from app.dao.ModelAttributesValuesDb import ModelAttributesValues
        
        mock_collection = Mock()
        mock_results = [
            {
                '_id': 1,
                'ModelAttributeId': 'attr1',
                'ModelId': 'model1',
                'IsActive': 'Y',
                'ModelAttributeValues': 'value1'
            }
        ]
        mock_collection.find.return_value = mock_results
        ModelAttributesValues.mycol = mock_collection
        
        query = {"ModelId": "model1", "IsActive": "Y"}
        result = ModelAttributesValues.findall(query)
        
        assert len(result) == 1
        assert result[0].ModelAttributeId == 'attr1'
        assert result[0].ModelAttributeValues == 'value1'
    
    @patch('app.dao.ModelAttributesValuesDb.time')
    @patch('app.dao.ModelAttributesValuesDb.datetime')
    def test_create_with_numeric_values(self, mock_datetime, mock_time, mock_log, mock_mydb):
        """Test create with numeric model attribute values."""
        from app.dao.ModelAttributesValuesDb import ModelAttributesValues
        
        mock_time.time.return_value = 2222222222.222
        mock_time.sleep = Mock()
        mock_now = datetime.datetime(2026, 1, 5, 14, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_collection = Mock()
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 2222222222.222
        mock_collection.insert_one.return_value = mock_insert_result
        ModelAttributesValues.mycol = mock_collection
        
        values = {
            'modelAttributeId': 'attr999',
            'modelId': 999,
            'modelAttributeValues': 42.5
        }
        
        result = ModelAttributesValues.create(values)
        
        assert result == 2222222222.222
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args['ModelAttributeValues'] == 42.5
    
    def test_update_multiple_fields(self, mock_log, mock_mydb):
        """Test update with multiple fields."""
        from app.dao.ModelAttributesValuesDb import ModelAttributesValues
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_collection.update_one.return_value = mock_update_result
        ModelAttributesValues.mycol = mock_collection
        
        update_values = {
            'ModelAttributeValues': 'new_value',
            'IsActive': 'N',
            'LastUpdatedDateTime': datetime.datetime(2026, 1, 5)
        }
        
        result = ModelAttributesValues.update(456, update_values)
        
        assert result is True
        expected_newvalues = {"$set": update_values}
        mock_collection.update_one.assert_called_once_with(
            {"_id": 456},
            expected_newvalues
        )
