"""
Unit tests for DataDb DAO layer.
"""

import pytest
import os
import sys
import time
import datetime
from unittest.mock import Mock, MagicMock, patch

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app.dao.DataDb import Data, AttributeDict


class TestAttributeDictDataDb:
    """Tests for AttributeDict class in DataDb."""
    
    def test_attribute_dict_getattr(self):
        ad = AttributeDict({'test_key': 'test_value'})
        assert ad.test_key == 'test_value'
    
    def test_attribute_dict_setattr(self):
        ad = AttributeDict()
        ad.new_key = 'new_value'
        assert ad.new_key == 'new_value'
    
    def test_attribute_dict_delattr(self):
        ad = AttributeDict({'key_to_delete': 'value'})
        del ad.key_to_delete
        assert 'key_to_delete' not in ad


class TestDataGetAll:
    """Tests for Data.get_all method."""
    
    @patch('app.dao.DataDb.Data.mycol')
    def test_get_all_success(self, mock_mycol):
        mock_mycol.distinct.return_value = ['data1', 'data2', 'data3']
        
        result = Data.get_all('DataSetName')
        
        assert result == ['data1', 'data2', 'data3']
        mock_mycol.distinct.assert_called_once_with('DataSetName')
    
    @patch('app.dao.DataDb.Data.mycol')
    def test_get_all_empty(self, mock_mycol):
        mock_mycol.distinct.return_value = []
        
        result = Data.get_all('DataSetName')
        
        assert result == []


class TestDataFindOne:
    """Tests for Data.findOne method."""
    
    @patch('app.dao.DataDb.Data.mycol')
    def test_find_one_success(self, mock_mycol):
        mock_mycol.find.return_value = [{
            '_id': '12345',
            'DataId': '12345',
            'DataSetName': 'TestData',
            'SampleData': 'sample_file_id',
            'UserId': 'user123',
            'IsActive': 'Y'
        }]
        
        result = Data.findOne('12345')
        
        assert result['DataSetName'] == 'TestData'
        assert result._id == '12345'
        mock_mycol.find.assert_called_once_with({"_id": '12345'}, {})
    
    @patch('app.dao.DataDb.Data.mycol')
    def test_find_one_with_multiple_fields(self, mock_mycol):
        mock_mycol.find.return_value = [{
            '_id': '67890',
            'DataId': '67890',
            'DataSetName': 'AnotherData',
            'SampleData': 'another_file_id',
            'UserId': 'user456',
            'GroundTruthImageFileId': 'ground_truth_id',
            'IsActive': 'Y',
            'CreatedDateTime': datetime.datetime.now(),
            'LastUpdatedDateTime': datetime.datetime.now()
        }]
        
        result = Data.findOne('67890')
        
        assert result.DataSetName == 'AnotherData'
        assert result.UserId == 'user456'


class TestDataFindAll:
    """Tests for Data.findall method."""
    
    @patch('app.dao.DataDb.Data.mycol')
    def test_findall_success(self, mock_mycol):
        mock_mycol.find.return_value = [
            {'_id': '1', 'DataId': '1', 'DataSetName': 'Data1', 'UserId': 'user1', 'IsActive': 'Y'},
            {'_id': '2', 'DataId': '2', 'DataSetName': 'Data2', 'UserId': 'user1', 'IsActive': 'Y'}
        ]
        
        result = Data.findall({'UserId': 'user1', 'IsActive': 'Y'})
        
        assert len(result) == 2
        assert result[0].DataSetName == 'Data1'
        assert result[1].DataSetName == 'Data2'
        mock_mycol.find.assert_called_once_with({'UserId': 'user1', 'IsActive': 'Y'}, {})
    
    @patch('app.dao.DataDb.Data.mycol')
    def test_findall_empty(self, mock_mycol):
        mock_mycol.find.return_value = []
        
        result = Data.findall({'UserId': 'nonexistent'})
        
        assert result == []
    
    @patch('app.dao.DataDb.Data.mycol')
    def test_findall_single_result(self, mock_mycol):
        mock_mycol.find.return_value = [
            {'_id': '1', 'DataId': '1', 'DataSetName': 'SingleData', 'UserId': 'user1', 'IsActive': 'Y'}
        ]
        
        result = Data.findall({'DataId': '1'})
        
        assert len(result) == 1
        assert result[0].DataSetName == 'SingleData'


class TestDataCreate:
    """Tests for Data.create method."""
    
    @patch('app.dao.DataDb.Data.mycol')
    @patch('app.dao.DataDb.time')
    def test_create_success(self, mock_time, mock_mycol):
        mock_time.time.return_value = 1234567890.123
        mock_time.sleep = Mock()
        
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 1234567890.123
        mock_mycol.insert_one.return_value = mock_insert_result
        
        values = {
            'sampleData': 'file_id_123',
            'dataSetName': 'NewDataSet',
            'userId': 'user123',
            'groundTruthImageFileId': 'gt_file_id'
        }
        
        result = Data.create(values)
        
        assert result == 1234567890.123
        mock_mycol.insert_one.assert_called_once()
        call_args = mock_mycol.insert_one.call_args[0][0]
        assert call_args['DataSetName'] == 'NewDataSet'
        assert call_args['UserId'] == 'user123'
        assert call_args['IsActive'] == 'Y'
        assert call_args['_id'] == 1234567890.123
        assert call_args['DataId'] == 1234567890.123
    
    @patch('app.dao.DataDb.Data.mycol')
    @patch('app.dao.DataDb.time')
    def test_create_with_na_ground_truth(self, mock_time, mock_mycol):
        mock_time.time.return_value = 9876543210.456
        mock_time.sleep = Mock()
        
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 9876543210.456
        mock_mycol.insert_one.return_value = mock_insert_result
        
        values = {
            'sampleData': 'sample_file',
            'dataSetName': 'TestData',
            'userId': 'user456',
            'groundTruthImageFileId': 'NA'
        }
        
        result = Data.create(values)
        
        assert result == 9876543210.456
        call_args = mock_mycol.insert_one.call_args[0][0]
        assert call_args['GroundTruthImageFileId'] == 'NA'


class TestDataUpdate:
    """Tests for Data.update method."""
    
    @patch('app.dao.DataDb.Data.mycol')
    def test_update_success(self, mock_mycol):
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_mycol.update_one.return_value = mock_update_result
        
        result = Data.update('12345', {'IsActive': 'N'})
        
        assert result is True
        mock_mycol.update_one.assert_called_once_with(
            {"_id": '12345'}, 
            {"$set": {'IsActive': 'N'}}
        )
    
    @patch('app.dao.DataDb.Data.mycol')
    def test_update_multiple_fields(self, mock_mycol):
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_mycol.update_one.return_value = mock_update_result
        
        update_values = {
            'DataSetName': 'UpdatedName',
            'SampleData': 'new_file_id',
            'LastUpdatedDateTime': datetime.datetime.now()
        }
        
        result = Data.update('67890', update_values)
        
        assert result is True
        mock_mycol.update_one.assert_called_once()
    
    @patch('app.dao.DataDb.Data.mycol')
    def test_update_not_acknowledged(self, mock_mycol):
        mock_update_result = Mock()
        mock_update_result.acknowledged = False
        mock_mycol.update_one.return_value = mock_update_result
        
        result = Data.update('12345', {'IsActive': 'N'})
        
        assert result is False


class TestDataDelete:
    """Tests for Data.delete method."""
    
    @patch('app.dao.DataDb.Data.mycol')
    def test_delete_success(self, mock_mycol):
        mock_mycol.delete_many.return_value = Mock()
        
        Data.delete({'UserId': 'user123', 'DataId': '12345'})
        
        mock_mycol.delete_many.assert_called_once_with({'UserId': 'user123', 'DataId': '12345'})
    
    @patch('app.dao.DataDb.Data.mycol')
    def test_delete_by_userid(self, mock_mycol):
        mock_mycol.delete_many.return_value = Mock()
        
        Data.delete({'UserId': 'user456'})
        
        mock_mycol.delete_many.assert_called_once_with({'UserId': 'user456'})
    
    @patch('app.dao.DataDb.Data.mycol')
    def test_delete_by_dataid(self, mock_mycol):
        mock_mycol.delete_many.return_value = Mock()
        
        Data.delete({'DataId': '67890'})
        
        mock_mycol.delete_many.assert_called_once_with({'DataId': '67890'})
