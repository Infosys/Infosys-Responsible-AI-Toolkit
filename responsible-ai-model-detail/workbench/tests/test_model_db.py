"""
Unit tests for app.dao.ModelDb module.
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
        from app.dao.ModelDb import AttributeDict
        
        attr_dict = AttributeDict({'key': 'value'})
        assert attr_dict['key'] == 'value'
        assert attr_dict.key == 'value'


@patch('app.dao.ModelDb.mydb')
@patch('app.dao.ModelDb.GridFS')
class TestModel:
    """Tests for Model class methods."""
    
    def test_get_all_success(self, mock_gridfs, mock_mydb):
        """Test get_all returns distinct values."""
        from app.dao.ModelDb import Model
        
        mock_collection = Mock()
        mock_collection.distinct.return_value = ['model1', 'model2', 'model3']
        mock_mydb.__getitem__.return_value = mock_collection
        Model.mycol = mock_collection
        
        result = Model.get_all('ModelName')
        
        assert result == ['model1', 'model2', 'model3']
        mock_collection.distinct.assert_called_once_with('ModelName')
    
    def test_get_all_empty(self, mock_gridfs, mock_mydb):
        """Test get_all returns empty list."""
        from app.dao.ModelDb import Model
        
        mock_collection = Mock()
        mock_collection.distinct.return_value = []
        Model.mycol = mock_collection
        
        result = Model.get_all('ModelName')
        
        assert result == []
    
    def test_findone_success(self, mock_gridfs, mock_mydb):
        """Test findOne returns model by ID."""
        from app.dao.ModelDb import Model
        
        mock_collection = Mock()
        mock_result = [{'_id': '123', 'ModelName': 'TestModel', 'IsActive': 'Y'}]
        mock_collection.find.return_value = mock_result
        Model.mycol = mock_collection
        
        result = Model.findOne('123')
        
        assert result._id == '123'
        assert result.ModelName == 'TestModel'
        mock_collection.find.assert_called_once_with({"_id": '123'}, {})
    
    def test_findall_multiple_results(self, mock_gridfs, mock_mydb):
        """Test findall returns multiple models."""
        from app.dao.ModelDb import Model
        
        mock_collection = Mock()
        mock_results = [
            {'_id': 1, 'ModelName': 'Model1', 'IsActive': 'Y'},
            {'_id': 2, 'ModelName': 'Model2', 'IsActive': 'Y'}
        ]
        mock_collection.find.return_value = mock_results
        Model.mycol = mock_collection
        
        query = {"IsActive": "Y"}
        result = Model.findall(query)
        
        assert len(result) == 2
        assert result[0].ModelName == 'Model1'
        assert result[1].ModelName == 'Model2'
        mock_collection.find.assert_called_once_with(query, {})
    
    def test_findall_empty(self, mock_gridfs, mock_mydb):
        """Test findall returns empty list."""
        from app.dao.ModelDb import Model
        
        mock_collection = Mock()
        mock_collection.find.return_value = []
        Model.mycol = mock_collection
        
        result = Model.findall({"UserId": "nonexistent"})
        
        assert result == []
    
    @patch('app.dao.ModelDb.time')
    @patch('app.dao.ModelDb.datetime')
    def test_create_success(self, mock_datetime, mock_time, mock_gridfs, mock_mydb):
        """Test create inserts new model."""
        from app.dao.ModelDb import Model
        
        mock_time.time.return_value = 1234567890.123
        mock_time.sleep = Mock()
        mock_now = datetime.datetime(2026, 1, 5, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_collection = Mock()
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 1234567890.123
        mock_collection.insert_one.return_value = mock_insert_result
        Model.mycol = mock_collection
        
        values = {
            'userId': 'user123',
            'modelName': 'TestModel',
            'modelVersion': '1.0',
            'modelData': 'model_data_123',
            'modelEndPoint': 'http://api.example.com/model'
        }
        
        result = Model.create(values)
        
        assert result == 1234567890.123
        mock_time.time.assert_called_once()
        mock_time.sleep.assert_called_once_with(1/1000)
        
        expected_doc = {
            "_id": 1234567890.123,
            "UserId": 'user123',
            "ModelId": 1234567890.123,
            "ModelName": 'TestModel',
            "ModelVersion": '1.0',
            "IsActive": "Y",
            "ModelData": 'model_data_123',
            "ModelEndPoint": 'http://api.example.com/model',
            "CreatedDateTime": mock_now,
            "LastUpdatedDateTime": mock_now,
        }
        mock_collection.insert_one.assert_called_once_with(expected_doc)
    
    @patch('app.dao.ModelDb.time')
    @patch('app.dao.ModelDb.datetime')
    def test_create_different_values(self, mock_datetime, mock_time, mock_gridfs, mock_mydb):
        """Test create with different model values."""
        from app.dao.ModelDb import Model
        
        mock_time.time.return_value = 9876543210.456
        mock_time.sleep = Mock()
        mock_now = datetime.datetime(2026, 1, 5, 15, 30, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_collection = Mock()
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 9876543210.456
        mock_collection.insert_one.return_value = mock_insert_result
        Model.mycol = mock_collection
        
        values = {
            'userId': 'user456',
            'modelName': 'AnotherModel',
            'modelVersion': '2.0',
            'modelData': 'model_data_456',
            'modelEndPoint': 'http://api.example.com/model2'
        }
        
        result = Model.create(values)
        
        assert result == 9876543210.456
    
    @patch('app.dao.ModelDb.log')
    def test_update_success(self, mock_log, mock_gridfs, mock_mydb):
        """Test update modifies model."""
        from app.dao.ModelDb import Model
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_collection.update_one.return_value = mock_update_result
        Model.mycol = mock_collection
        
        model_id = 123
        update_values = {'ModelName': 'UpdatedModel', 'IsActive': 'N'}
        
        result = Model.update(model_id, update_values)
        
        assert result is True
        expected_newvalues = {"$set": update_values}
        mock_collection.update_one.assert_called_once_with(
            {"_id": model_id},
            expected_newvalues
        )
        mock_log.debug.assert_called_once_with(str(expected_newvalues))
    
    @patch('app.dao.ModelDb.log')
    def test_update_not_acknowledged(self, mock_log, mock_gridfs, mock_mydb):
        """Test update returns False when not acknowledged."""
        from app.dao.ModelDb import Model
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = False
        mock_collection.update_one.return_value = mock_update_result
        Model.mycol = mock_collection
        
        result = Model.update(123, {'IsActive': 'N'})
        
        assert result is False
    
    @patch('app.dao.ModelDb.log')
    def test_update_multiple_fields(self, mock_log, mock_gridfs, mock_mydb):
        """Test update with multiple fields."""
        from app.dao.ModelDb import Model
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_collection.update_one.return_value = mock_update_result
        Model.mycol = mock_collection
        
        update_values = {
            'ModelName': 'NewModel',
            'ModelVersion': '3.0',
            'IsActive': 'Y',
            'ModelEndPoint': 'http://new.api.com'
        }
        
        result = Model.update(456, update_values)
        
        assert result is True
    
    def test_delete_success(self, mock_gridfs, mock_mydb):
        """Test delete removes models."""
        from app.dao.ModelDb import Model
        
        mock_collection = Mock()
        Model.mycol = mock_collection
        
        query = {"UserId": "user123"}
        Model.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
    
    def test_delete_single_record(self, mock_gridfs, mock_mydb):
        """Test delete with single record."""
        from app.dao.ModelDb import Model
        
        mock_collection = Mock()
        Model.mycol = mock_collection
        
        query = {"_id": 123}
        Model.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
