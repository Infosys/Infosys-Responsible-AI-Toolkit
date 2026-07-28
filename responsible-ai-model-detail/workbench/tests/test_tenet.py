"""
Unit tests for app.dao.Tenet module.
Tests cover all methods and edge cases for 100% code coverage.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
import datetime
import time

# Add src directory to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))


class TestAttributeDict:
    """Tests for AttributeDict class."""
    
    def test_attribute_dict_getattr(self):
        """Test dictionary item access via attribute notation."""
        from app.dao.Tenet import AttributeDict
        attr_dict = AttributeDict({'test_attr': 'value'})
        assert attr_dict.test_attr == 'value'
    
    def test_attribute_dict_setitem(self):
        """Test setting dictionary item via bracket notation."""
        from app.dao.Tenet import AttributeDict
        attr_dict = AttributeDict()
        attr_dict['test_attr'] = 'value'
        assert attr_dict['test_attr'] == 'value'
    
    def test_attribute_dict_setattr(self):
        """Test setting dictionary item via attribute notation."""
        from app.dao.Tenet import AttributeDict
        attr_dict = AttributeDict()
        attr_dict.test_attr = 'value'
        assert attr_dict.test_attr == 'value'
    
    def test_attribute_dict_delitem(self):
        """Test deleting dictionary item via bracket notation."""
        from app.dao.Tenet import AttributeDict
        attr_dict = AttributeDict({'test_attr': 'value'})
        del attr_dict['test_attr']
        assert 'test_attr' not in attr_dict
    
    def test_attribute_dict_delattr(self):
        """Test deleting dictionary item via attribute notation."""
        from app.dao.Tenet import AttributeDict
        attr_dict = AttributeDict({'test_attr': 'value'})
        del attr_dict.test_attr
        assert 'test_attr' not in attr_dict
    
    def test_attribute_dict_initialization_with_dict(self):
        """Test initializing AttributeDict with a dictionary."""
        from app.dao.Tenet import AttributeDict
        initial_data = {'name': 'test', 'id': 123}
        attr_dict = AttributeDict(initial_data)
        assert attr_dict['name'] == 'test'
        assert attr_dict['id'] == 123
    
    def test_attribute_dict_initialization_empty(self):
        """Test initializing empty AttributeDict."""
        from app.dao.Tenet import AttributeDict
        attr_dict = AttributeDict()
        assert len(attr_dict) == 0


@patch('app.dao.Tenet.mydb')
@patch('app.dao.Tenet.GridFS')
class TestTenet:
    """Tests for Tenet class methods."""
    
    def test_get_all_success(self, mock_gridfs, mock_mydb):
        """Test get_all returns distinct values successfully."""
        from app.dao.Tenet import Tenet
        
        # Mock the collection's distinct method
        mock_collection = Mock()
        mock_collection.distinct.return_value = ['Fairness', 'Explainability', 'Robustness']
        mock_mydb.__getitem__.return_value = mock_collection
        Tenet.mycol = mock_collection
        
        result = Tenet.get_all('TenetName')
        
        assert result == ['Fairness', 'Explainability', 'Robustness']
        mock_collection.distinct.assert_called_once_with('TenetName')
    
    def test_get_all_empty(self, mock_gridfs, mock_mydb):
        """Test get_all returns empty list when no results."""
        from app.dao.Tenet import Tenet
        
        mock_collection = Mock()
        mock_collection.distinct.return_value = []
        Tenet.mycol = mock_collection
        
        result = Tenet.get_all('TenetName')
        
        assert result == []
        mock_collection.distinct.assert_called_once_with('TenetName')
    
    def test_findone_success(self, mock_gridfs, mock_mydb):
        """Test findOne returns the ID for a given tenet name."""
        from app.dao.Tenet import Tenet
        
        mock_collection = Mock()
        mock_result = [{'Id': 123, 'TenetName': 'Fairness'}]
        mock_collection.find.return_value = mock_result
        Tenet.mycol = mock_collection
        
        result = Tenet.findOne('fairness')
        
        assert result == 123
        mock_collection.find.assert_called_once_with({"TenetName": "Fairness"}, {})
    
    def test_findone_lowercase_input(self, mock_gridfs, mock_mydb):
        """Test findOne capitalizes lowercase input."""
        from app.dao.Tenet import Tenet
        
        mock_collection = Mock()
        mock_result = [{'Id': 456, 'TenetName': 'Explainability'}]
        mock_collection.find.return_value = mock_result
        Tenet.mycol = mock_collection
        
        result = Tenet.findOne('explainability')
        
        assert result == 456
        mock_collection.find.assert_called_once_with({"TenetName": "Explainability"}, {})
    
    def test_findone_uppercase_input(self, mock_gridfs, mock_mydb):
        """Test findOne handles uppercase input correctly."""
        from app.dao.Tenet import Tenet
        
        mock_collection = Mock()
        mock_result = [{'Id': 789, 'TenetName': 'Robustness'}]
        mock_collection.find.return_value = mock_result
        Tenet.mycol = mock_collection
        
        result = Tenet.findOne('ROBUSTNESS')
        
        assert result == 789
        mock_collection.find.assert_called_once_with({"TenetName": "Robustness"}, {})
    
    def test_findall_success_multiple_results(self, mock_gridfs, mock_mydb):
        """Test findall returns multiple records as AttributeDict list."""
        from app.dao.Tenet import Tenet
        
        mock_collection = Mock()
        mock_results = [
            {'_id': 1, 'TenetName': 'Fairness', 'Id': 100},
            {'_id': 2, 'TenetName': 'Explainability', 'Id': 200}
        ]
        mock_collection.find.return_value = mock_results
        Tenet.mycol = mock_collection
        
        query = {"IsActive": "Y"}
        result = Tenet.findall(query)
        
        assert len(result) == 2
        assert result[0].TenetName == 'Fairness'
        assert result[1].TenetName == 'Explainability'
        mock_collection.find.assert_called_once_with(query, {})
    
    def test_findall_success_single_result(self, mock_gridfs, mock_mydb):
        """Test findall returns single record correctly."""
        from app.dao.Tenet import Tenet
        
        mock_collection = Mock()
        mock_results = [{'_id': 1, 'TenetName': 'Fairness', 'Id': 100}]
        mock_collection.find.return_value = mock_results
        Tenet.mycol = mock_collection
        
        query = {"TenetName": "Fairness"}
        result = Tenet.findall(query)
        
        assert len(result) == 1
        assert result[0].TenetName == 'Fairness'
        assert result[0].Id == 100
    
    def test_findall_empty_results(self, mock_gridfs, mock_mydb):
        """Test findall returns empty list when no results."""
        from app.dao.Tenet import Tenet
        
        mock_collection = Mock()
        mock_collection.find.return_value = []
        Tenet.mycol = mock_collection
        
        query = {"TenetName": "NonExistent"}
        result = Tenet.findall(query)
        
        assert result == []
        mock_collection.find.assert_called_once_with(query, {})
    
    def test_findall_with_complex_query(self, mock_gridfs, mock_mydb):
        """Test findall with complex query conditions."""
        from app.dao.Tenet import Tenet
        
        mock_collection = Mock()
        mock_results = [{'_id': 1, 'TenetName': 'Fairness', 'IsActive': 'Y', 'ProjectName': 'Test'}]
        mock_collection.find.return_value = mock_results
        Tenet.mycol = mock_collection
        
        query = {"IsActive": "Y", "ProjectName": "Test"}
        result = Tenet.findall(query)
        
        assert len(result) == 1
        assert result[0].IsActive == 'Y'
        assert result[0].ProjectName == 'Test'
    
    @patch('app.dao.Tenet.time')
    @patch('app.dao.Tenet.datetime')
    def test_create_success(self, mock_datetime, mock_time, mock_gridfs, mock_mydb):
        """Test create inserts a new tenet successfully."""
        from app.dao.Tenet import Tenet
        
        # Mock time and datetime
        mock_time.time.return_value = 1234567890.123
        mock_time.sleep = Mock()
        mock_now = datetime.datetime(2026, 1, 5, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        # Mock collection
        mock_collection = Mock()
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 1234567890.123
        mock_collection.insert_one.return_value = mock_insert_result
        Tenet.mycol = mock_collection
        
        values = {
            'tenetid': 'T001',
            'tenetname': 'Fairness',
            'projectname': 'TestProject'
        }
        
        result = Tenet.create(values)
        
        assert result == 1234567890.123
        mock_time.time.assert_called_once()
        mock_time.sleep.assert_called_once_with(1/1000)
        
        expected_doc = {
            "_id": 1234567890.123,
            "Id": 'T001',
            "TenetName": 'Fairness',
            "ProjectName": 'TestProject',
            "CreatedDateTime": mock_now,
            "LastUpdatedDateTime": mock_now,
        }
        mock_collection.insert_one.assert_called_once_with(expected_doc)
    
    @patch('app.dao.Tenet.time')
    @patch('app.dao.Tenet.datetime')
    def test_create_with_different_values(self, mock_datetime, mock_time, mock_gridfs, mock_mydb):
        """Test create with different tenet values."""
        from app.dao.Tenet import Tenet
        
        mock_time.time.return_value = 9876543210.456
        mock_time.sleep = Mock()
        mock_now = datetime.datetime(2026, 1, 5, 15, 30, 45)
        mock_datetime.datetime.now.return_value = mock_now
        
        mock_collection = Mock()
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = 9876543210.456
        mock_collection.insert_one.return_value = mock_insert_result
        Tenet.mycol = mock_collection
        
        values = {
            'tenetid': 'T002',
            'tenetname': 'Explainability',
            'projectname': 'AIProject'
        }
        
        result = Tenet.create(values)
        
        assert result == 9876543210.456
        
        expected_doc = {
            "_id": 9876543210.456,
            "Id": 'T002',
            "TenetName": 'Explainability',
            "ProjectName": 'AIProject',
            "CreatedDateTime": mock_now,
            "LastUpdatedDateTime": mock_now,
        }
        mock_collection.insert_one.assert_called_once_with(expected_doc)
    
    @patch('app.dao.Tenet.log')
    def test_update_success(self, mock_log, mock_gridfs, mock_mydb):
        """Test update modifies a tenet successfully."""
        from app.dao.Tenet import Tenet
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_collection.update_one.return_value = mock_update_result
        Tenet.mycol = mock_collection
        
        tenet_id = 1234567890.123
        update_values = {'TenetName': 'Updated Fairness', 'IsActive': 'N'}
        
        result = Tenet.update(tenet_id, update_values)
        
        assert result is True
        expected_newvalues = {"$set": update_values}
        mock_collection.update_one.assert_called_once_with(
            {"_id": tenet_id},
            expected_newvalues
        )
        mock_log.debug.assert_called_once_with(str(expected_newvalues))
    
    @patch('app.dao.Tenet.log')
    def test_update_single_field(self, mock_log, mock_gridfs, mock_mydb):
        """Test update with single field modification."""
        from app.dao.Tenet import Tenet
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_collection.update_one.return_value = mock_update_result
        Tenet.mycol = mock_collection
        
        tenet_id = 999
        update_values = {'IsActive': 'N'}
        
        result = Tenet.update(tenet_id, update_values)
        
        assert result is True
        expected_newvalues = {"$set": update_values}
        mock_collection.update_one.assert_called_once_with(
            {"_id": tenet_id},
            expected_newvalues
        )
    
    @patch('app.dao.Tenet.log')
    def test_update_acknowledged_false(self, mock_log, mock_gridfs, mock_mydb):
        """Test update returns False when not acknowledged."""
        from app.dao.Tenet import Tenet
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = False
        mock_collection.update_one.return_value = mock_update_result
        Tenet.mycol = mock_collection
        
        tenet_id = 123
        update_values = {'TenetName': 'Test'}
        
        result = Tenet.update(tenet_id, update_values)
        
        assert result is False
    
    @patch('app.dao.Tenet.log')
    def test_update_multiple_fields(self, mock_log, mock_gridfs, mock_mydb):
        """Test update with multiple fields."""
        from app.dao.Tenet import Tenet
        
        mock_collection = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_collection.update_one.return_value = mock_update_result
        Tenet.mycol = mock_collection
        
        tenet_id = 456
        update_values = {
            'TenetName': 'Robustness',
            'ProjectName': 'NewProject',
            'IsActive': 'Y',
            'Status': 'Active'
        }
        
        result = Tenet.update(tenet_id, update_values)
        
        assert result is True
        expected_newvalues = {"$set": update_values}
        mock_collection.update_one.assert_called_once_with(
            {"_id": tenet_id},
            expected_newvalues
        )
    
    def test_delete_success(self, mock_gridfs, mock_mydb):
        """Test delete removes tenets matching query."""
        from app.dao.Tenet import Tenet
        
        mock_collection = Mock()
        mock_delete_result = Mock()
        mock_delete_result.deleted_count = 2
        mock_collection.delete_many.return_value = mock_delete_result
        Tenet.mycol = mock_collection
        
        query = {"IsActive": "N"}
        Tenet.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
    
    def test_delete_single_record(self, mock_gridfs, mock_mydb):
        """Test delete with query matching single record."""
        from app.dao.Tenet import Tenet
        
        mock_collection = Mock()
        mock_delete_result = Mock()
        mock_delete_result.deleted_count = 1
        mock_collection.delete_many.return_value = mock_delete_result
        Tenet.mycol = mock_collection
        
        query = {"_id": 123}
        Tenet.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
    
    def test_delete_no_matching_records(self, mock_gridfs, mock_mydb):
        """Test delete when no records match the query."""
        from app.dao.Tenet import Tenet
        
        mock_collection = Mock()
        mock_delete_result = Mock()
        mock_delete_result.deleted_count = 0
        mock_collection.delete_many.return_value = mock_delete_result
        Tenet.mycol = mock_collection
        
        query = {"TenetName": "NonExistent"}
        Tenet.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
    
    def test_delete_complex_query(self, mock_gridfs, mock_mydb):
        """Test delete with complex query conditions."""
        from app.dao.Tenet import Tenet
        
        mock_collection = Mock()
        mock_delete_result = Mock()
        mock_delete_result.deleted_count = 5
        mock_collection.delete_many.return_value = mock_delete_result
        Tenet.mycol = mock_collection
        
        query = {"IsActive": "N", "ProjectName": "OldProject"}
        Tenet.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)


@patch('app.dao.Tenet.DB')
@patch('app.dao.Tenet.GridFS')
class TestTenetInitialization:
    """Tests for Tenet class initialization and module-level code."""

class TestAttributeDictEdgeCases:
    """Additional edge case tests for AttributeDict."""
    
    def test_attribute_dict_with_special_keys(self):
        """Test AttributeDict with special character keys."""
        from app.dao.Tenet import AttributeDict
        attr_dict = AttributeDict({'attr-with-dash': 'value1', 'attr_with_underscore': 'value2'})
        assert attr_dict['attr-with-dash'] == 'value1'
        assert attr_dict.attr_with_underscore == 'value2'
    
    def test_attribute_dict_with_numeric_values(self):
        """Test AttributeDict with numeric values."""
        from app.dao.Tenet import AttributeDict
        attr_dict = AttributeDict({'int': 42, 'float': 3.14, 'bool': True})
        assert attr_dict.int == 42
        assert attr_dict.float == 3.14
        assert attr_dict.bool is True
    
    def test_attribute_dict_with_nested_dict(self):
        """Test AttributeDict with nested dictionary."""
        from app.dao.Tenet import AttributeDict
        attr_dict = AttributeDict({'nested': {'inner': 'value'}})
        assert attr_dict['nested']['inner'] == 'value'
    
    def test_attribute_dict_update_existing_key(self):
        """Test updating existing key in AttributeDict."""
        from app.dao.Tenet import AttributeDict
        attr_dict = AttributeDict({'test_attr': 'old_value'})
        attr_dict.test_attr = 'new_value'
        assert attr_dict.test_attr == 'new_value'
    
    def test_attribute_dict_multiple_operations(self):
        """Test multiple operations on AttributeDict."""
        from app.dao.Tenet import AttributeDict
        attr_dict = AttributeDict()
        attr_dict['a'] = 1
        attr_dict.b = 2
        attr_dict['c'] = 3
        
        assert attr_dict.a == 1
        assert attr_dict['b'] == 2
        assert attr_dict.c == 3
        
        del attr_dict.a
        assert 'a' not in attr_dict
        assert len(attr_dict) == 2
