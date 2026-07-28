"""
Unit tests for app.dao.Batch module.
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
        from app.dao.Batch import AttributeDict
        
        attr_dict = AttributeDict({'key': 'value'})
        assert attr_dict['key'] == 'value'
        assert attr_dict.key == 'value'


@patch('app.dao.Batch.mydb')
@patch('app.dao.Batch.GridFS')
class TestBatch:
    """Tests for Batch class methods."""
    
    def test_get_all_success(self, mock_gridfs, mock_mydb):
        """Test get_all returns distinct values."""
        from app.dao.Batch import Batch
        
        mock_collection = Mock()
        mock_collection.distinct.return_value = ['batch1', 'batch2', 'batch3']
        mock_mydb.__getitem__.return_value = mock_collection
        Batch.mycol = mock_collection
        
        result = Batch.get_all('BatchId')
        
        assert result == ['batch1', 'batch2', 'batch3']
        mock_collection.distinct.assert_called_once_with('BatchId')
    
    def test_get_all_empty(self, mock_gridfs, mock_mydb):
        """Test get_all returns empty list."""
        from app.dao.Batch import Batch
        
        mock_collection = Mock()
        mock_collection.distinct.return_value = []
        Batch.mycol = mock_collection
        
        result = Batch.get_all('BatchId')
        
        assert result == []
    
    @patch('builtins.print')
    def test_findone_success(self, mock_print, mock_gridfs, mock_mydb):
        """Test findOne returns batch ID."""
        from app.dao.Batch import Batch
        
        mock_collection = Mock()
        mock_result = [{'Id': 100, 'BatchId': 'B001', 'Status': 'completed'}]
        mock_collection.find.return_value = mock_result
        Batch.mycol = mock_collection
        
        result = Batch.findOne('B001')
        
        assert result == 100
        mock_collection.find.assert_called_once_with({"BatchId": 'B001'}, {})
        mock_print.assert_called()
    
    def test_findall_multiple_results(self, mock_gridfs, mock_mydb):
        """Test findall returns multiple batches."""
        from app.dao.Batch import Batch
        
        mock_collection = Mock()
        mock_results = [
            {'_id': 1, 'BatchId': 'B001', 'Status': 'completed'},
            {'_id': 2, 'BatchId': 'B002', 'Status': 'running'}
        ]
        mock_collection.find.return_value = mock_results
        Batch.mycol = mock_collection
        
        query = {"UserId": "user123"}
        result = Batch.findall(query)
        
        assert len(result) == 2
        assert result[0].BatchId == 'B001'
        assert result[1].Status == 'running'
        mock_collection.find.assert_called_once_with(query, {})
    
    def test_findall_empty(self, mock_gridfs, mock_mydb):
        """Test findall returns empty list."""
        from app.dao.Batch import Batch
        
        mock_collection = Mock()
        mock_collection.find.return_value = []
        Batch.mycol = mock_collection
        
        result = Batch.findall({"UserId": "nonexistent"})
        
        assert result == []
    
    @patch('app.dao.Batch.time')
    @patch('app.dao.Batch.datetime')
    def test_create_success(self, mock_datetime, mock_time, mock_gridfs, mock_mydb):
        """Test create inserts new batch."""
        from app.dao.Batch import Batch
        
        mock_time.time.return_value = 1234567890.123
        mock_now = datetime.datetime(2026, 1, 5, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_collection = Mock()
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 'inserted_id'
        mock_collection.insert_one.return_value = mock_insert_result
        Batch.mycol = mock_collection
        
        payload = {
            'userId': 'user123',
            'title': 'Test Batch',
            'modelId': 'M001',
            'dataId': 'D001',
            'preProcessorId': 'P001'
        }
        tenant_id = 'T001'
        
        result = Batch.create(payload, tenant_id)
        
        assert result['BatchId'] == 1234567890.123
        assert result['TenetId'] == 'T001'
        
        expected_data = {
            "BatchId": 1234567890.123,
            "UserId": 'user123',
            "Title": 'Test Batch',
            "Status": 'Not Started',
            "TenetId": 'T001',
            "ModelId": 'M001',
            "DataId": 'D001',
            "PreprocessorId": 'P001',
            "CreatedDateTime": mock_now,
            "LastUpdatedDateTime": mock_now,
        }
        mock_collection.insert_one.assert_called_once_with(expected_data)
    
    @patch('app.dao.Batch.time')
    @patch('app.dao.Batch.datetime')
    def test_create_different_values(self, mock_datetime, mock_time, mock_gridfs, mock_mydb):
        """Test create with different batch values."""
        from app.dao.Batch import Batch
        
        mock_time.time.return_value = 9876543210.456
        mock_now = datetime.datetime(2026, 1, 5, 15, 30, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_collection = Mock()
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 'id2'
        mock_collection.insert_one.return_value = mock_insert_result
        Batch.mycol = mock_collection
        
        payload = {
            'userId': 'user456',
            'title': 'Another Batch',
            'modelId': 'M002',
            'dataId': 'D002',
            'preProcessorId': 'P002'
        }
        
        result = Batch.create(payload, 'T002')
        
        assert result['BatchId'] == 9876543210.456
        assert result['TenetId'] == 'T002'
    
    @patch('app.dao.Batch.log')
    def test_update_success(self, mock_log, mock_gridfs, mock_mydb):
        """Test update modifies batch."""
        from app.dao.Batch import Batch
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_collection.update_one.return_value = mock_update_result
        Batch.mycol = mock_collection
        
        batch_id = 123
        update_values = {'Status': 'completed'}
        
        result = Batch.update(batch_id, update_values)
        
        assert result is True
        expected_newvalues = {"$set": update_values}
        mock_collection.update_one.assert_called_once_with(
            {"_id": batch_id},
            expected_newvalues
        )
        mock_log.debug.assert_called_once_with(str(expected_newvalues))
    
    @patch('app.dao.Batch.log')
    def test_update_not_acknowledged(self, mock_log, mock_gridfs, mock_mydb):
        """Test update returns False when not acknowledged."""
        from app.dao.Batch import Batch
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = False
        mock_collection.update_one.return_value = mock_update_result
        Batch.mycol = mock_collection
        
        result = Batch.update(123, {'Status': 'failed'})
        
        assert result is False
    
    def test_delete_success(self, mock_gridfs, mock_mydb):
        """Test delete removes batches."""
        from app.dao.Batch import Batch
        
        mock_collection = Mock()
        Batch.mycol = mock_collection
        
        query = {"UserId": "user123"}
        Batch.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
    
    @patch('builtins.print')
    def test_findstatus_success(self, mock_print, mock_gridfs, mock_mydb):
        """Test findStatus returns batch status."""
        from app.dao.Batch import Batch
        
        mock_collection = Mock()
        mock_result = [{'BatchId': 'B001', 'Status': 'completed'}]
        mock_collection.find.return_value = mock_result
        Batch.mycol = mock_collection
        
        result = Batch.findStatus('B001')
        
        assert result == 'completed'
        mock_collection.find.assert_called_once_with({"BatchId": 'B001'}, {})
        mock_print.assert_called_with('completed')
    
    @patch('builtins.print')
    def test_findstatus_different_status(self, mock_print, mock_gridfs, mock_mydb):
        """Test findStatus with different status values."""
        from app.dao.Batch import Batch
        
        mock_collection = Mock()
        mock_result = [{'BatchId': 'B002', 'Status': 'running'}]
        mock_collection.find.return_value = mock_result
        Batch.mycol = mock_collection
        
        result = Batch.findStatus('B002')
        
        assert result == 'running'
    
    @patch('builtins.print')
    def test_findbatchtable_success(self, mock_print, mock_gridfs, mock_mydb):
        """Test findBatchTable returns batch list for user."""
        from app.dao.Batch import Batch
        
        mock_collection = Mock()
        mock_results = [
            {'BatchId': 'B001', 'Status': 'completed', 'Title': 'Batch 1'},
            {'BatchId': 'B002', 'Status': 'running', 'Title': 'Batch 2'}
        ]
        mock_collection.find.return_value = mock_results
        Batch.mycol = mock_collection
        
        result = Batch.findBatchTable('user123')
        
        assert len(result) == 2
        assert result[0]['BatchId'] == 'B001'
        assert result[1]['Status'] == 'running'
        mock_collection.find.assert_called_once_with({"UserId": 'user123'}, {"_id": 0})
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_findbatchtable_empty(self, mock_print, mock_gridfs, mock_mydb):
        """Test findBatchTable returns empty list."""
        from app.dao.Batch import Batch
        
        mock_collection = Mock()
        mock_collection.find.return_value = []
        Batch.mycol = mock_collection
        
        result = Batch.findBatchTable('nonexistent')
        
        assert result == []
        mock_print.assert_called_with([], "result")
