"""
Unit tests for app.dao.PreprocessorDb module.
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
        from app.dao.PreprocessorDb import AttributeDict
        
        attr_dict = AttributeDict({'key': 'value'})
        assert attr_dict['key'] == 'value'
        assert attr_dict.key == 'value'


@patch('app.dao.PreprocessorDb.mydb')
@patch('app.dao.PreprocessorDb.GridFS')
class TestPreprocessor:
    """Tests for Preprocessor class methods."""
    
    def test_get_all_success(self, mock_gridfs, mock_mydb):
        """Test get_all returns distinct values."""
        from app.dao.PreprocessorDb import Preprocessor
        
        mock_collection = Mock()
        mock_collection.distinct.return_value = ['prep1', 'prep2', 'prep3']
        mock_mydb.__getitem__.return_value = mock_collection
        Preprocessor.mycol = mock_collection
        
        result = Preprocessor.get_all('PreprocessorName')
        
        assert result == ['prep1', 'prep2', 'prep3']
        mock_collection.distinct.assert_called_once_with('PreprocessorName')
    
    def test_get_all_empty(self, mock_gridfs, mock_mydb):
        """Test get_all returns empty list."""
        from app.dao.PreprocessorDb import Preprocessor
        
        mock_collection = Mock()
        mock_collection.distinct.return_value = []
        Preprocessor.mycol = mock_collection
        
        result = Preprocessor.get_all('PreprocessorName')
        
        assert result == []
    
    def test_findone_success(self, mock_gridfs, mock_mydb):
        """Test findOne returns preprocessor by ID."""
        from app.dao.PreprocessorDb import Preprocessor
        
        mock_collection = Mock()
        mock_result = [{'_id': '123', 'PreprocessorName': 'TestPrep', 'IsActive': 'Y'}]
        mock_collection.find.return_value = mock_result
        Preprocessor.mycol = mock_collection
        
        result = Preprocessor.findOne('123')
        
        assert result._id == '123'
        assert result.PreprocessorName == 'TestPrep'
        mock_collection.find.assert_called_once_with({"_id": '123'}, {})
    
    def test_findall_multiple_results(self, mock_gridfs, mock_mydb):
        """Test findall returns multiple preprocessors."""
        from app.dao.PreprocessorDb import Preprocessor
        
        mock_collection = Mock()
        mock_results = [
            {'_id': 1, 'PreprocessorName': 'Prep1', 'IsActive': 'Y'},
            {'_id': 2, 'PreprocessorName': 'Prep2', 'IsActive': 'Y'}
        ]
        mock_collection.find.return_value = mock_results
        Preprocessor.mycol = mock_collection
        
        query = {"IsActive": "Y"}
        result = Preprocessor.findall(query)
        
        assert len(result) == 2
        assert result[0].PreprocessorName == 'Prep1'
        assert result[1].PreprocessorName == 'Prep2'
        mock_collection.find.assert_called_once_with(query, {})
    
    def test_findall_empty(self, mock_gridfs, mock_mydb):
        """Test findall returns empty list."""
        from app.dao.PreprocessorDb import Preprocessor
        
        mock_collection = Mock()
        mock_collection.find.return_value = []
        Preprocessor.mycol = mock_collection
        
        result = Preprocessor.findall({"UserId": "nonexistent"})
        
        assert result == []
    
    @patch('app.dao.PreprocessorDb.time')
    @patch('app.dao.PreprocessorDb.datetime')
    def test_create_success(self, mock_datetime, mock_time, mock_gridfs, mock_mydb):
        """Test create inserts new preprocessor."""
        from app.dao.PreprocessorDb import Preprocessor
        
        mock_time.time.return_value = 1234567890.123
        mock_time.sleep = Mock()
        mock_now = datetime.datetime(2026, 1, 5, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_collection = Mock()
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 1234567890.123
        mock_collection.insert_one.return_value = mock_insert_result
        Preprocessor.mycol = mock_collection
        
        values = {
            'userId': 'user123',
            'preprocessorName': 'TestPreprocessor',
            'preprocessorFileId': 'file_123'
        }
        
        result = Preprocessor.create(values)
        
        assert result == 1234567890.123
        mock_time.time.assert_called_once()
        mock_time.sleep.assert_called_once_with(1/1000)
        
        expected_doc = {
            "_id": 1234567890.123,
            "UserId": 'user123',
            "PreprocessorId": 1234567890.123,
            "PreprocessorName": 'TestPreprocessor',
            "PreprocessorFileId": 'file_123',
            "IsActive": "Y",
            "CreatedDateTime": mock_now,
            "LastUpdatedDateTime": mock_now,
        }
        mock_collection.insert_one.assert_called_once_with(expected_doc)
    
    @patch('app.dao.PreprocessorDb.time')
    @patch('app.dao.PreprocessorDb.datetime')
    def test_create_different_values(self, mock_datetime, mock_time, mock_gridfs, mock_mydb):
        """Test create with different preprocessor values."""
        from app.dao.PreprocessorDb import Preprocessor
        
        mock_time.time.return_value = 9876543210.456
        mock_time.sleep = Mock()
        mock_now = datetime.datetime(2026, 1, 5, 15, 30, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_collection = Mock()
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 9876543210.456
        mock_collection.insert_one.return_value = mock_insert_result
        Preprocessor.mycol = mock_collection
        
        values = {
            'userId': 'user456',
            'preprocessorName': 'AnotherPreprocessor',
            'preprocessorFileId': 'file_456'
        }
        
        result = Preprocessor.create(values)
        
        assert result == 9876543210.456
    
    @patch('app.dao.PreprocessorDb.log')
    def test_update_success(self, mock_log, mock_gridfs, mock_mydb):
        """Test update modifies preprocessor."""
        from app.dao.PreprocessorDb import Preprocessor
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_collection.update_one.return_value = mock_update_result
        Preprocessor.mycol = mock_collection
        
        prep_id = 123
        update_values = {'PreprocessorName': 'UpdatedPrep', 'IsActive': 'N'}
        
        result = Preprocessor.update(prep_id, update_values)
        
        assert result is True
        expected_newvalues = {"$set": update_values}
        mock_collection.update_one.assert_called_once_with(
            {"_id": prep_id},
            expected_newvalues
        )
        mock_log.debug.assert_called_once_with(str(expected_newvalues))
    
    @patch('app.dao.PreprocessorDb.log')
    def test_update_not_acknowledged(self, mock_log, mock_gridfs, mock_mydb):
        """Test update returns False when not acknowledged."""
        from app.dao.PreprocessorDb import Preprocessor
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = False
        mock_collection.update_one.return_value = mock_update_result
        Preprocessor.mycol = mock_collection
        
        result = Preprocessor.update(123, {'IsActive': 'N'})
        
        assert result is False
    
    def test_delete_success(self, mock_gridfs, mock_mydb):
        """Test delete removes preprocessors."""
        from app.dao.PreprocessorDb import Preprocessor
        
        mock_collection = Mock()
        Preprocessor.mycol = mock_collection
        
        query = {"UserId": "user123"}
        Preprocessor.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
    
    def test_delete_single_record(self, mock_gridfs, mock_mydb):
        """Test delete with single record."""
        from app.dao.PreprocessorDb import Preprocessor
        
        mock_collection = Mock()
        Preprocessor.mycol = mock_collection
        
        query = {"_id": 123}
        Preprocessor.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
