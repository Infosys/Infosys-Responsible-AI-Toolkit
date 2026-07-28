"""
Unit tests for DataAttributesValuesDb DAO layer.
"""

import pytest
import os
import sys
import time
import datetime
from unittest.mock import Mock, MagicMock, patch

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app.dao.DataAttributesValuesDb import DataAttributesValues, AttributeDict


class TestAttributeDictDataAttributesValues:
    """Tests for AttributeDict class in DataAttributesValuesDb."""
    
    def test_attribute_dict_getattr(self):
        ad = AttributeDict({'attr_key': 'attr_value'})
        assert ad.attr_key == 'attr_value'
    
    def test_attribute_dict_setattr(self):
        ad = AttributeDict()
        ad.new_attr = 'new_val'
        assert ad.new_attr == 'new_val'
    
    def test_attribute_dict_delattr(self):
        ad = AttributeDict({'key_del': 'value_del'})
        del ad.key_del
        assert 'key_del' not in ad


class TestDataAttributesValuesFindOne:
    """Tests for DataAttributesValues.findOne method."""
    
    @patch('app.dao.DataAttributesValuesDb.DataAttributesValues.mycol')
    def test_find_one_success(self, mock_mycol):
        mock_mycol.find.return_value = [{
            '_id': '12345',
            'DataAttributeValuesId': '12345',
            'DataAttributeId': 'attr_101',
            'DataId': 'data_201',
            'DataAttributeValues': 'test_value',
            'IsActive': 'Y'
        }]
        
        result = DataAttributesValues.findOne('12345')
        
        assert result['DataAttributeValues'] == 'test_value'
        assert result._id == '12345'
        mock_mycol.find.assert_called_once_with({"_id": '12345'}, {})
    
    @patch('app.dao.DataAttributesValuesDb.DataAttributesValues.mycol')
    def test_find_one_with_all_fields(self, mock_mycol):
        now = datetime.datetime.now()
        mock_mycol.find.return_value = [{
            '_id': '67890',
            'DataAttributeValuesId': '67890',
            'DataAttributeId': 'attr_102',
            'DataId': 'data_202',
            'DataAttributeValues': 'another_value',
            'IsActive': 'Y',
            'CreatedDateTime': now,
            'LastUpdatedDateTime': now
        }]
        
        result = DataAttributesValues.findOne('67890')
        
        assert result.DataAttributeId == 'attr_102'
        assert result.DataId == 'data_202'
        assert result.IsActive == 'Y'


class TestDataAttributesValuesFindAll:
    """Tests for DataAttributesValues.findall method."""
    
    @patch('app.dao.DataAttributesValuesDb.DataAttributesValues.mycol')
    def test_findall_success(self, mock_mycol):
        mock_mycol.find.return_value = [
            {'_id': '1', 'DataAttributeValuesId': '1', 'DataAttributeId': 'attr1', 
             'DataId': 'data1', 'DataAttributeValues': 'value1', 'IsActive': 'Y'},
            {'_id': '2', 'DataAttributeValuesId': '2', 'DataAttributeId': 'attr2', 
             'DataId': 'data1', 'DataAttributeValues': 'value2', 'IsActive': 'Y'}
        ]
        
        result = DataAttributesValues.findall({'DataId': 'data1', 'IsActive': 'Y'})
        
        assert len(result) == 2
        assert result[0].DataAttributeValues == 'value1'
        assert result[1].DataAttributeValues == 'value2'
        mock_mycol.find.assert_called_once_with({'DataId': 'data1', 'IsActive': 'Y'}, {})
    
    @patch('app.dao.DataAttributesValuesDb.DataAttributesValues.mycol')
    def test_findall_empty(self, mock_mycol):
        mock_mycol.find.return_value = []
        
        result = DataAttributesValues.findall({'DataId': 'nonexistent'})
        
        assert result == []
    
    @patch('app.dao.DataAttributesValuesDb.DataAttributesValues.mycol')
    def test_findall_single_result(self, mock_mycol):
        mock_mycol.find.return_value = [
            {'_id': '1', 'DataAttributeValuesId': '1', 'DataAttributeId': 'attr1', 
             'DataId': 'data_single', 'DataAttributeValues': 'single_value', 'IsActive': 'Y'}
        ]
        
        result = DataAttributesValues.findall({'DataId': 'data_single'})
        
        assert len(result) == 1
        assert result[0].DataAttributeValues == 'single_value'


class TestDataAttributesValuesCreate:
    """Tests for DataAttributesValues.create method."""
    
    @patch('app.dao.DataAttributesValuesDb.DataAttributesValues.mycol')
    @patch('app.dao.DataAttributesValuesDb.time')
    def test_create_success(self, mock_time, mock_mycol):
        mock_time.time.return_value = 1234567890.123
        mock_time.sleep = Mock()
        
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 1234567890.123
        mock_mycol.insert_one.return_value = mock_insert_result
        
        values = {
            'dataAttributeId': 'attr_123',
            'dataId': 'data_456',
            'dataAttributeValues': 'test_attribute_value'
        }
        
        result = DataAttributesValues.create(values)
        
        assert result == 1234567890.123
        mock_mycol.insert_one.assert_called_once()
        call_args = mock_mycol.insert_one.call_args[0][0]
        assert call_args['DataAttributeId'] == 'attr_123'
        assert call_args['DataId'] == 'data_456'
        assert call_args['DataAttributeValues'] == 'test_attribute_value'
        assert call_args['IsActive'] == 'Y'
        assert call_args['_id'] == 1234567890.123
        assert call_args['DataAttributeValuesId'] == 1234567890.123
    
    @patch('app.dao.DataAttributesValuesDb.DataAttributesValues.mycol')
    @patch('app.dao.DataAttributesValuesDb.time')
    def test_create_with_different_values(self, mock_time, mock_mycol):
        mock_time.time.return_value = 9876543210.456
        mock_time.sleep = Mock()
        
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 9876543210.456
        mock_mycol.insert_one.return_value = mock_insert_result
        
        values = {
            'dataAttributeId': 'attr_789',
            'dataId': 'data_012',
            'dataAttributeValues': 'another_test_value'
        }
        
        result = DataAttributesValues.create(values)
        
        assert result == 9876543210.456


class TestDataAttributesValuesCreateForBatchData:
    """Tests for DataAttributesValues.createForBatchData method."""
    
    @patch('app.dao.DataAttributesValuesDb.DataAttributesValues.mycol')
    @patch('app.dao.DataAttributesValuesDb.time')
    def test_create_for_batch_data_success(self, mock_time, mock_mycol):
        mock_time.time.return_value = 1111111111.111
        mock_time.sleep = Mock()
        
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 1111111111.111
        mock_mycol.insert_one.return_value = mock_insert_result
        
        values = {
            'DataAttributeId': 'attr_batch_1',
            'dataId': 'data_batch_1',
            'DataAttributevalues': 'batch_attribute_value',
            'BatchId': 'batch_123'
        }
        
        result = DataAttributesValues.createForBatchData(values)
        
        assert result == 1111111111.111
        mock_mycol.insert_one.assert_called_once()
        call_args = mock_mycol.insert_one.call_args[0][0]
        assert call_args['DataAttributeId'] == 'attr_batch_1'
        assert call_args['DataId'] == 'data_batch_1'
        assert call_args['DataAttributeValues'] == 'batch_attribute_value'
        assert call_args['BatchId'] == 'batch_123'
        assert call_args['IsActive'] == 'Y'
        assert call_args['_id'] == 1111111111.111
        assert call_args['DataAttributeValuesId'] == 1111111111.111
    
    @patch('app.dao.DataAttributesValuesDb.DataAttributesValues.mycol')
    @patch('app.dao.DataAttributesValuesDb.time')
    def test_create_for_batch_data_different_batch(self, mock_time, mock_mycol):
        mock_time.time.return_value = 2222222222.222
        mock_time.sleep = Mock()
        
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 2222222222.222
        mock_mycol.insert_one.return_value = mock_insert_result
        
        values = {
            'DataAttributeId': 'attr_batch_2',
            'dataId': 'data_batch_2',
            'DataAttributevalues': 'another_batch_value',
            'BatchId': 'batch_456'
        }
        
        result = DataAttributesValues.createForBatchData(values)
        
        assert result == 2222222222.222
        call_args = mock_mycol.insert_one.call_args[0][0]
        assert call_args['BatchId'] == 'batch_456'


class TestDataAttributesValuesUpdate:
    """Tests for DataAttributesValues.update method."""
    
    @patch('app.dao.DataAttributesValuesDb.DataAttributesValues.mycol')
    def test_update_success(self, mock_mycol):
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_mycol.update_one.return_value = mock_update_result
        
        result = DataAttributesValues.update('12345', {'DataAttributeValues': 'updated_value'})
        
        assert result is True
        mock_mycol.update_one.assert_called_once_with(
            {"_id": '12345'}, 
            {"$set": {'DataAttributeValues': 'updated_value'}}
        )
    
    @patch('app.dao.DataAttributesValuesDb.DataAttributesValues.mycol')
    def test_update_multiple_fields(self, mock_mycol):
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_mycol.update_one.return_value = mock_update_result
        
        update_values = {
            'DataAttributeValues': 'new_value',
            'IsActive': 'N',
            'LastUpdatedDateTime': datetime.datetime.now()
        }
        
        result = DataAttributesValues.update('67890', update_values)
        
        assert result is True
        mock_mycol.update_one.assert_called_once()
    
    @patch('app.dao.DataAttributesValuesDb.DataAttributesValues.mycol')
    def test_update_not_acknowledged(self, mock_mycol):
        mock_update_result = Mock()
        mock_update_result.acknowledged = False
        mock_mycol.update_one.return_value = mock_update_result
        
        result = DataAttributesValues.update('12345', {'IsActive': 'N'})
        
        assert result is False
    
    @patch('app.dao.DataAttributesValuesDb.DataAttributesValues.mycol')
    def test_update_is_active_flag(self, mock_mycol):
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_mycol.update_one.return_value = mock_update_result
        
        result = DataAttributesValues.update('abc123', {'IsActive': 'N'})
        
        assert result is True
        mock_mycol.update_one.assert_called_once_with(
            {"_id": 'abc123'}, 
            {"$set": {'IsActive': 'N'}}
        )


class TestDataAttributesValuesDelete:
    """Tests for DataAttributesValues.delete method."""
    
    @patch('app.dao.DataAttributesValuesDb.DataAttributesValues.mycol')
    def test_delete_success(self, mock_mycol):
        mock_mycol.delete_many.return_value = Mock()
        
        DataAttributesValues.delete({'DataId': 'data123'})
        
        mock_mycol.delete_many.assert_called_once_with({'DataId': 'data123'})
    
    @patch('app.dao.DataAttributesValuesDb.DataAttributesValues.mycol')
    def test_delete_by_attribute_id(self, mock_mycol):
        mock_mycol.delete_many.return_value = Mock()
        
        DataAttributesValues.delete({'DataAttributeId': 'attr456'})
        
        mock_mycol.delete_many.assert_called_once_with({'DataAttributeId': 'attr456'})
    
    @patch('app.dao.DataAttributesValuesDb.DataAttributesValues.mycol')
    def test_delete_by_batch_id(self, mock_mycol):
        mock_mycol.delete_many.return_value = Mock()
        
        DataAttributesValues.delete({'BatchId': 'batch789'})
        
        mock_mycol.delete_many.assert_called_once_with({'BatchId': 'batch789'})
    
    @patch('app.dao.DataAttributesValuesDb.DataAttributesValues.mycol')
    def test_delete_multiple_criteria(self, mock_mycol):
        mock_mycol.delete_many.return_value = Mock()
        
        DataAttributesValues.delete({'DataId': 'data123', 'IsActive': 'N'})
        
        mock_mycol.delete_many.assert_called_once_with({'DataId': 'data123', 'IsActive': 'N'})
