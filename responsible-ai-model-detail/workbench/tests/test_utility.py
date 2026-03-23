"""
Unit tests for app.service.utility module.
Tests cover all utility functions for 100% code coverage.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open
import json

# Add src directory to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from app.service.utility import Utility, AttributeDict


class TestAttributeDict:
    """Tests for AttributeDict class."""
    
    def test_attribute_dict_getitem(self):
        """Test dictionary item access via bracket notation."""
        attr_dict = AttributeDict({'test_attr': 'value'})
        assert attr_dict['test_attr'] == 'value'
    
    def test_attribute_dict_getattr(self):
        """Test dictionary item access via attribute notation."""
        attr_dict = AttributeDict({'test_attr': 'value'})
        assert attr_dict.test_attr == 'value'
    
    def test_attribute_dict_setitem(self):
        """Test setting dictionary item via bracket notation."""
        attr_dict = AttributeDict()
        attr_dict['test_attr'] = 'value'
        assert attr_dict['test_attr'] == 'value'
    
    def test_attribute_dict_setattr(self):
        """Test setting dictionary item via attribute notation."""
        attr_dict = AttributeDict()
        attr_dict.test_attr = 'value'
        assert attr_dict.test_attr == 'value'
    
    def test_attribute_dict_delitem(self):
        """Test deleting dictionary item via bracket notation."""
        attr_dict = AttributeDict({'test_attr': 'value'})
        del attr_dict['test_attr']
        assert 'test_attr' not in attr_dict
    
    def test_attribute_dict_delattr(self):
        """Test deleting dictionary item via attribute notation."""
        attr_dict = AttributeDict({'test_attr': 'value'})
        del attr_dict.test_attr
        assert 'test_attr' not in attr_dict


class TestLoadTenets:
    """Tests for loadtenets function."""
    
    @patch('app.service.utility.InfosysRAI')
    @patch('builtins.open', new_callable=mock_open, read_data='[{"tenetid": "1", "tenetname": "Fairness", "projectname": "RAI"}]')
    @patch('app.service.utility.Utility.mydb')
    @patch('builtins.print')
    def test_loadtenets_collection_not_exists(self, mock_print, mock_mydb, mock_file, mock_infosys_rai):
        """Test loadtenets when Tenet collection doesn't exist."""
        mock_mydb.list_collection_names.return_value = []
        mock_infosys_rai.addTenet.return_value = "Successfully added Fairness Tenet."
        
        result = Utility.loadtenets()
        
        assert result == "Success"
        mock_infosys_rai.addTenet.assert_called_once()
        mock_print.assert_called()
    
    @patch('builtins.open', new_callable=mock_open, read_data='[{"tenetid": "1", "tenetname": "Fairness", "projectname": "RAI"}]')
    @patch('app.service.utility.Utility.mydb')
    def test_loadtenets_collection_exists(self, mock_mydb, mock_file):
        """Test loadtenets when Tenet collection already exists."""
        mock_mydb.list_collection_names.return_value = ['Tenet']
        
        result = Utility.loadtenets()
        
        assert result == "Success"
    
    @patch('builtins.open', new_callable=mock_open, read_data='[{"tenetid": "1", "tenetname": "Explainability", "projectname": "RAI"}, {"tenetid": "2", "tenetname": "Security", "projectname": "RAI"}]')
    @patch('app.service.utility.InfosysRAI')
    @patch('app.service.utility.Utility.mydb')
    @patch('builtins.print')
    def test_loadtenets_multiple_tenets(self, mock_print, mock_mydb, mock_infosys_rai, mock_file):
        """Test loadtenets with multiple tenets."""
        mock_mydb.list_collection_names.return_value = []
        mock_infosys_rai.addTenet.return_value = "Successfully added tenet."
        
        result = Utility.loadtenets()
        
        assert result == "Success"
        assert mock_infosys_rai.addTenet.call_count == 2
    
    @patch('app.service.utility.Utility.mydb')
    def test_loadtenets_exception(self, mock_mydb):
        """Test loadtenets when an exception occurs."""
        mock_mydb.list_collection_names.side_effect = Exception("Database error")
        
        result = Utility.loadtenets()
        
        assert result == "Something Went Wrong"
    
    @patch('builtins.open', side_effect=FileNotFoundError())
    @patch('app.service.utility.Utility.mydb')
    def test_loadtenets_file_not_found(self, mock_mydb, mock_file):
        """Test loadtenets when tenet.json file is not found."""
        mock_mydb.list_collection_names.return_value = []
        
        result = Utility.loadtenets()
        
        assert result == "Something Went Wrong"


class TestLoadModelAttributes:
    """Tests for loadmodelattributes function."""
    
    @patch('app.service.utility.ModelAttributes')
    @patch('builtins.open', new_callable=mock_open, read_data='[{"ModelAttributeName": "algorithm", "TenetId": "T001"}]')
    @patch('app.service.utility.Utility.mydb')
    @patch('builtins.print')
    def test_loadmodelattributes_collection_not_exists(self, mock_print, mock_mydb, mock_file, mock_model_attrs):
        """Test loadmodelattributes when ModelAttributes collection doesn't exist."""
        mock_mydb.list_collection_names.return_value = []
        mock_model_attrs.create.return_value = 'attr_id_123'
        
        result = Utility.loadmodelattributes()
        
        assert result == "Success"
        mock_model_attrs.create.assert_called_once()
        mock_print.assert_called()
    
    @patch('builtins.open', new_callable=mock_open, read_data='[{"ModelAttributeName": "algorithm", "TenetId": "T001"}]')
    @patch('app.service.utility.Utility.mydb')
    def test_loadmodelattributes_collection_exists(self, mock_mydb, mock_file):
        """Test loadmodelattributes when ModelAttributes collection already exists."""
        mock_mydb.list_collection_names.return_value = ['ModelAttributes']
        
        result = Utility.loadmodelattributes()
        
        assert result == "Success"
    
    @patch('app.service.utility.ModelAttributes')
    @patch('builtins.open', new_callable=mock_open, read_data='[{"ModelAttributeName": "algorithm", "TenetId": "T001"}, {"ModelAttributeName": "framework", "TenetId": "T002"}]')
    @patch('app.service.utility.Utility.mydb')
    @patch('builtins.print')
    def test_loadmodelattributes_multiple_attributes(self, mock_print, mock_mydb, mock_file, mock_model_attrs):
        """Test loadmodelattributes with multiple attributes."""
        mock_mydb.list_collection_names.return_value = []
        mock_model_attrs.create.return_value = 'attr_id'
        
        result = Utility.loadmodelattributes()
        
        assert result == "Success"
        assert mock_model_attrs.create.call_count == 2
    
    @patch('app.service.utility.Utility.mydb')
    def test_loadmodelattributes_exception(self, mock_mydb):
        """Test loadmodelattributes when an exception occurs."""
        mock_mydb.list_collection_names.side_effect = Exception("Database error")
        
        result = Utility.loadmodelattributes()
        
        assert result == "Something Went Wrong"
    
    @patch('builtins.open', side_effect=FileNotFoundError())
    @patch('app.service.utility.Utility.mydb')
    def test_loadmodelattributes_file_not_found(self, mock_mydb, mock_file):
        """Test loadmodelattributes when modelattributes.json file is not found."""
        mock_mydb.list_collection_names.return_value = []
        
        result = Utility.loadmodelattributes()
        
        assert result == "Something Went Wrong"
    
    @patch('app.service.utility.ModelAttributes')
    @patch('builtins.open', new_callable=mock_open, read_data='[{"ModelAttributeName": "algorithm", "TenetId": "T001"}]')
    @patch('app.service.utility.Utility.mydb')
    @patch('builtins.print')
    def test_loadmodelattributes_create_returns_none(self, mock_print, mock_mydb, mock_file, mock_model_attrs):
        """Test loadmodelattributes when create returns None."""
        mock_mydb.list_collection_names.return_value = []
        mock_model_attrs.create.return_value = None
        
        result = Utility.loadmodelattributes()
        
        assert result == "Success"
        # Verify that the success message is not printed when id is None
        assert not any('got initalised Successfully' in str(call) for call in mock_print.call_args_list if call[0])


class TestLoadDataAttributes:
    """Tests for loaddataattributes function."""
    
    @patch('app.service.utility.DataAttributes')
    @patch('builtins.open', new_callable=mock_open, read_data='[{"DataAttributeName": "dataType", "TenetId": "T001"}]')
    @patch('app.service.utility.Utility.mydb')
    @patch('builtins.print')
    def test_loaddataattributes_collection_not_exists(self, mock_print, mock_mydb, mock_file, mock_data_attrs):
        """Test loaddataattributes when DataAttributes collection doesn't exist."""
        mock_mydb.list_collection_names.return_value = []
        mock_data_attrs.create.return_value = 'attr_id_123'
        
        result = Utility.loaddataattributes()
        
        assert result == "Success"
        mock_data_attrs.create.assert_called_once()
        mock_print.assert_called()
    
    @patch('builtins.open', new_callable=mock_open, read_data='[{"DataAttributeName": "dataType", "TenetId": "T001"}]')
    @patch('app.service.utility.Utility.mydb')
    def test_loaddataattributes_collection_exists(self, mock_mydb, mock_file):
        """Test loaddataattributes when DataAttributes collection already exists."""
        mock_mydb.list_collection_names.return_value = ['DataAttributes']
        
        result = Utility.loaddataattributes()
        
        assert result == "Success"
    
    @patch('app.service.utility.DataAttributes')
    @patch('builtins.open', new_callable=mock_open, read_data='[{"DataAttributeName": "dataType", "TenetId": "T001"}, {"DataAttributeName": "format", "TenetId": "T002"}]')
    @patch('app.service.utility.Utility.mydb')
    @patch('builtins.print')
    def test_loaddataattributes_multiple_attributes(self, mock_print, mock_mydb, mock_file, mock_data_attrs):
        """Test loaddataattributes with multiple attributes."""
        mock_mydb.list_collection_names.return_value = []
        mock_data_attrs.create.return_value = 'attr_id'
        
        result = Utility.loaddataattributes()
        
        assert result == "Success"
        assert mock_data_attrs.create.call_count == 2
    
    @patch('app.service.utility.Utility.mydb')
    def test_loaddataattributes_exception(self, mock_mydb):
        """Test loaddataattributes when an exception occurs."""
        mock_mydb.list_collection_names.side_effect = Exception("Database error")
        
        result = Utility.loaddataattributes()
        
        assert result == "Something Went Wrong"
    
    @patch('builtins.open', side_effect=FileNotFoundError())
    @patch('app.service.utility.Utility.mydb')
    def test_loaddataattributes_file_not_found(self, mock_mydb, mock_file):
        """Test loaddataattributes when datasetattributes.json file is not found."""
        mock_mydb.list_collection_names.return_value = []
        
        result = Utility.loaddataattributes()
        
        assert result == "Something Went Wrong"
    
    @patch('app.service.utility.DataAttributes')
    @patch('builtins.open', new_callable=mock_open, read_data='[{"DataAttributeName": "dataType", "TenetId": "T001"}]')
    @patch('app.service.utility.Utility.mydb')
    @patch('builtins.print')
    def test_loaddataattributes_create_returns_none(self, mock_print, mock_mydb, mock_file, mock_data_attrs):
        """Test loaddataattributes when create returns None."""
        mock_mydb.list_collection_names.return_value = []
        mock_data_attrs.create.return_value = None
        
        result = Utility.loaddataattributes()
        
        assert result == "Success"
        # Verify that the success message is not printed when id is None
        assert not any('got initalised Successfully' in str(call) for call in mock_print.call_args_list if 'got initalised Successfully' in str(call))
    
    @patch('app.service.utility.DataAttributes')
    @patch('builtins.open', new_callable=mock_open, read_data='[{"DataAttributeName": "dataType", "TenetId": "T001"}]')
    @patch('app.service.utility.Utility.mydb')
    @patch('builtins.print')
    def test_loaddataattributes_prints_id(self, mock_print, mock_mydb, mock_file, mock_data_attrs):
        """Test loaddataattributes prints attribute id."""
        mock_mydb.list_collection_names.return_value = []
        mock_data_attrs.create.return_value = 'attr_id_456'
        
        result = Utility.loaddataattributes()
        
        assert result == "Success"
        # Verify that id is printed
        printed_calls = [str(call) for call in mock_print.call_args_list]
        assert any('attr_id_456' in call for call in printed_calls)
