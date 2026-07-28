"""
Unit tests for app.dao.Html module.
Tests cover all methods and edge cases for 100% code coverage.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add src directory to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))


class TestAttributeDict:
    """Tests for AttributeDict class."""
    
    def test_attribute_dict_operations(self):
        """Test all AttributeDict operations."""
        from app.dao.Html import AttributeDict
        
        attr_dict = AttributeDict({'key': 'value'})
        assert attr_dict['key'] == 'value'
        assert attr_dict.key == 'value'


@patch('app.dao.Html.mydb')
class TestHtml:
    """Tests for Html class methods."""
    
    def test_find_one_success(self, mock_mydb):
        """Test find_one returns HtmlFileId."""
        from app.dao.Html import Html
        
        mock_collection = Mock()
        mock_result = {'HtmlFileId': 'html_file_123'}
        mock_collection.find_one.return_value = mock_result
        mock_mydb.__getitem__.return_value = mock_collection
        Html.mycol = mock_collection
        
        result = Html.find_one(123.456, 789.012)
        
        assert result == 'html_file_123'
        mock_collection.find_one.assert_called_once_with(
            {"BatchId": 123.456, "TenetId": 789.012},
            {"_id": 0, "HtmlFileId": 1}
        )
    
    def test_find_one_batch_id_none(self, mock_mydb):
        """Test find_one raises ValueError when batch_id is None."""
        from app.dao.Html import Html
        
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find_one(None, 789.012)
    
    def test_find_one_tenet_id_none(self, mock_mydb):
        """Test find_one raises ValueError when tenet_id is None."""
        from app.dao.Html import Html
        
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find_one(123.456, None)
    
    def test_find_one_batch_id_not_float(self, mock_mydb):
        """Test find_one raises ValueError when batch_id is not float."""
        from app.dao.Html import Html
        
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find_one("123.456", 789.012)
    
    def test_find_one_tenet_id_not_float(self, mock_mydb):
        """Test find_one raises ValueError when tenet_id is not float."""
        from app.dao.Html import Html
        
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find_one(123.456, "789.012")
    
    def test_find_one_both_invalid(self, mock_mydb):
        """Test find_one raises ValueError when both IDs are invalid."""
        from app.dao.Html import Html
        
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find_one(None, None)
    
    def test_find_one_database_error(self, mock_mydb):
        """Test find_one raises ValueError on database error."""
        from app.dao.Html import Html
        
        mock_collection = Mock()
        mock_collection.find_one.side_effect = Exception("Database connection failed")
        Html.mycol = mock_collection
        
        with pytest.raises(ValueError, match="Invalid BatchID/TenetID"):
            Html.find_one(123.456, 789.012)
    
    def test_find_one_key_error(self, mock_mydb):
        """Test find_one raises ValueError on KeyError."""
        from app.dao.Html import Html
        
        mock_collection = Mock()
        mock_collection.find_one.return_value = {'wrong_key': 'value'}
        Html.mycol = mock_collection
        
        with pytest.raises(ValueError, match="Invalid BatchID/TenetID"):
            Html.find_one(123.456, 789.012)
    
    def test_find_success(self, mock_mydb):
        """Test find returns full html document."""
        from app.dao.Html import Html
        
        mock_collection = Mock()
        mock_result = {
            'HtmlFileId': 'html_file_456',
            'BatchId': 123.456,
            'TenetId': 789.012,
            'Content': '<html>...</html>'
        }
        mock_collection.find_one.return_value = mock_result
        Html.mycol = mock_collection
        
        result = Html.find(123.456, 789.012)
        
        assert result == mock_result
        assert result['HtmlFileId'] == 'html_file_456'
        mock_collection.find_one.assert_called_once_with(
            {"BatchId": 123.456, "TenetId": 789.012}
        )
    
    def test_find_batch_id_none(self, mock_mydb):
        """Test find raises ValueError when batch_id is None."""
        from app.dao.Html import Html
        
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find(None, 789.012)
    
    def test_find_tenet_id_none(self, mock_mydb):
        """Test find raises ValueError when tenet_id is None."""
        from app.dao.Html import Html
        
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find(123.456, None)
    
    def test_find_batch_id_not_float(self, mock_mydb):
        """Test find raises ValueError when batch_id is not float."""
        from app.dao.Html import Html
        
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find(123, 789.012)
    
    def test_find_tenet_id_not_float(self, mock_mydb):
        """Test find raises ValueError when tenet_id is not float."""
        from app.dao.Html import Html
        
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find(123.456, 789)
    
    def test_find_database_error(self, mock_mydb):
        """Test find raises ValueError on database error."""
        from app.dao.Html import Html
        
        mock_collection = Mock()
        mock_collection.find_one.side_effect = Exception("Connection lost")
        Html.mycol = mock_collection
        
        with pytest.raises(ValueError, match="Invalid BatchID/TenetID"):
            Html.find(123.456, 789.012)
    
    def test_findall_multiple_results(self, mock_mydb):
        """Test findall returns multiple html documents."""
        from app.dao.Html import Html
        
        mock_collection = Mock()
        mock_results = [
            {'BatchId': 123.456, 'TenetId': 789.012, 'HtmlFileId': 'file1'},
            {'BatchId': 456.789, 'TenetId': 789.012, 'HtmlFileId': 'file2'}
        ]
        mock_collection.find.return_value = mock_results
        Html.mycol = mock_collection
        
        query = {"TenetId": 789.012}
        result = Html.findall(query)
        
        assert len(result) == 2
        assert result[0].HtmlFileId == 'file1'
        assert result[1].BatchId == 456.789
        mock_collection.find.assert_called_once_with(query, {})
    
    def test_findall_single_result(self, mock_mydb):
        """Test findall returns single html document."""
        from app.dao.Html import Html
        
        mock_collection = Mock()
        mock_results = [{'BatchId': 123.456, 'HtmlFileId': 'single_file'}]
        mock_collection.find.return_value = mock_results
        Html.mycol = mock_collection
        
        result = Html.findall({"BatchId": 123.456})
        
        assert len(result) == 1
        assert result[0].HtmlFileId == 'single_file'
    
    def test_findall_empty(self, mock_mydb):
        """Test findall returns empty list."""
        from app.dao.Html import Html
        
        mock_collection = Mock()
        mock_collection.find.return_value = []
        Html.mycol = mock_collection
        
        result = Html.findall({"BatchId": 999.999})
        
        assert result == []
    
    def test_delete_success(self, mock_mydb):
        """Test delete removes html documents."""
        from app.dao.Html import Html
        
        mock_collection = Mock()
        mock_delete_result = Mock()
        mock_delete_result.deleted_count = 2
        mock_collection.delete_many.return_value = mock_delete_result
        Html.mycol = mock_collection
        
        query = {"TenetId": 789.012}
        Html.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
    
    def test_delete_single_record(self, mock_mydb):
        """Test delete with single record."""
        from app.dao.Html import Html
        
        mock_collection = Mock()
        Html.mycol = mock_collection
        
        query = {"BatchId": 123.456}
        Html.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
    
    def test_delete_no_matching_records(self, mock_mydb):
        """Test delete when no records match."""
        from app.dao.Html import Html
        
        mock_collection = Mock()
        mock_delete_result = Mock()
        mock_delete_result.deleted_count = 0
        mock_collection.delete_many.return_value = mock_delete_result
        Html.mycol = mock_collection
        
        query = {"BatchId": 999.999}
        Html.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
