"""
Unit tests for app.dao.Report module.
Tests cover all methods and edge cases for 100% code coverage.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from pymongo.errors import InvalidDocument

# Add src directory to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))


class TestAttributeDict:
    """Tests for AttributeDict class."""
    
    def test_attribute_dict_operations(self):
        """Test all AttributeDict operations."""
        from app.dao.Report import AttributeDict
        
        attr_dict = AttributeDict({'key': 'value'})
        assert attr_dict['key'] == 'value'
        assert attr_dict.key == 'value'


@patch('app.dao.Report.mydb')
class TestReport:
    """Tests for Report class methods."""
    
    def test_create_success(self, mock_mydb):
        """Test create inserts document successfully."""
        from app.dao.Report import Report
        
        mock_collection = Mock()
        mock_insert_result = Mock()
        mock_insert_result.acknowledged = True
        mock_collection.insert_one.return_value = mock_insert_result
        mock_mydb.__getitem__.return_value = mock_collection
        Report.mycol = mock_collection
        
        document = {'BatchId': 123.456, 'TenetId': 789.012, 'ReportData': 'test'}
        
        result = Report.create(document)
        
        assert result is True
        mock_collection.insert_one.assert_called_once_with(document)
    
    def test_create_none_document(self, mock_mydb):
        """Test create raises ValueError for None document."""
        from app.dao.Report import Report
        
        with pytest.raises(ValueError, match="Document must be a non-empty value"):
            Report.create(None)
    
    def test_create_not_acknowledged(self, mock_mydb):
        """Test create raises RuntimeError when insert not acknowledged."""
        from app.dao.Report import Report
        
        mock_collection = Mock()
        mock_insert_result = Mock()
        mock_insert_result.acknowledged = False
        mock_collection.insert_one.return_value = mock_insert_result
        Report.mycol = mock_collection
        
        document = {'BatchId': 123.456}
        
        with pytest.raises(RuntimeError, match="Failed to insert document into the collection"):
            Report.create(document)
    
    def test_create_invalid_document(self, mock_mydb):
        """Test create raises ValueError for invalid document."""
        from app.dao.Report import Report
        
        mock_collection = Mock()
        mock_collection.insert_one.side_effect = InvalidDocument("Invalid document")
        Report.mycol = mock_collection
        
        document = {'invalid': 'document'}
        
        with pytest.raises(ValueError, match="Document is not a valid document"):
            Report.create(document)
    
    def test_find_one_success(self, mock_mydb):
        """Test find_one returns report details."""
        from app.dao.Report import Report
        
        mock_collection = Mock()
        mock_result = {
            'ReportFileId': 'file_123',
            'ContentType': 'application/pdf',
            'ReportName': 'Test Report'
        }
        mock_collection.find_one.return_value = mock_result
        Report.mycol = mock_collection
        
        result = Report.find_one(123.456, 789.012)
        
        assert result == mock_result
        mock_collection.find_one.assert_called_once_with(
            {"BatchId": 123.456, "TenetId": 789.012},
            {"_id": 0, "ReportFileId": 1, "ContentType": 1, "ReportName": 1}
        )
    
    def test_find_one_batch_id_none(self, mock_mydb):
        """Test find_one raises ValueError when batch_id is None."""
        from app.dao.Report import Report
        
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Report.find_one(None, 789.012)
    
    def test_find_one_tenet_id_none(self, mock_mydb):
        """Test find_one raises ValueError when tenet_id is None."""
        from app.dao.Report import Report
        
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Report.find_one(123.456, None)
    
    def test_find_one_batch_id_not_float(self, mock_mydb):
        """Test find_one raises ValueError when batch_id is not float."""
        from app.dao.Report import Report
        
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Report.find_one("123.456", 789.012)
    
    def test_find_one_tenet_id_not_float(self, mock_mydb):
        """Test find_one raises ValueError when tenet_id is not float."""
        from app.dao.Report import Report
        
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Report.find_one(123.456, "789.012")
    
    def test_find_one_both_invalid(self, mock_mydb):
        """Test find_one raises ValueError when both IDs are invalid."""
        from app.dao.Report import Report
        
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Report.find_one("invalid", None)
    
    def test_find_one_database_error(self, mock_mydb):
        """Test find_one raises ValueError on database error."""
        from app.dao.Report import Report
        
        mock_collection = Mock()
        mock_collection.find_one.side_effect = Exception("Database connection failed")
        Report.mycol = mock_collection
        
        with pytest.raises(ValueError, match="Invalid BatchID/TenetID"):
            Report.find_one(123.456, 789.012)
    
    def test_findall_multiple_results(self, mock_mydb):
        """Test findall returns multiple reports."""
        from app.dao.Report import Report
        
        mock_collection = Mock()
        mock_results = [
            {'BatchId': 123.456, 'TenetId': 789.012, 'ReportName': 'Report1'},
            {'BatchId': 456.789, 'TenetId': 789.012, 'ReportName': 'Report2'}
        ]
        mock_collection.find.return_value = mock_results
        Report.mycol = mock_collection
        
        query = {"TenetId": 789.012}
        result = Report.findall(query)
        
        assert len(result) == 2
        assert result[0].ReportName == 'Report1'
        assert result[1].BatchId == 456.789
        mock_collection.find.assert_called_once_with(query, {})
    
    def test_findall_single_result(self, mock_mydb):
        """Test findall returns single report."""
        from app.dao.Report import Report
        
        mock_collection = Mock()
        mock_results = [{'BatchId': 123.456, 'ReportName': 'Single Report'}]
        mock_collection.find.return_value = mock_results
        Report.mycol = mock_collection
        
        result = Report.findall({"BatchId": 123.456})
        
        assert len(result) == 1
        assert result[0].ReportName == 'Single Report'
    
    def test_findall_empty(self, mock_mydb):
        """Test findall returns empty list."""
        from app.dao.Report import Report
        
        mock_collection = Mock()
        mock_collection.find.return_value = []
        Report.mycol = mock_collection
        
        result = Report.findall({"BatchId": 999.999})
        
        assert result == []
    
    def test_delete_success(self, mock_mydb):
        """Test delete removes reports."""
        from app.dao.Report import Report
        
        mock_collection = Mock()
        mock_delete_result = Mock()
        mock_delete_result.deleted_count = 2
        mock_collection.delete_many.return_value = mock_delete_result
        Report.mycol = mock_collection
        
        query = {"TenetId": 789.012}
        Report.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
    
    def test_delete_single_record(self, mock_mydb):
        """Test delete with single record."""
        from app.dao.Report import Report
        
        mock_collection = Mock()
        Report.mycol = mock_collection
        
        query = {"BatchId": 123.456}
        Report.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
    
    def test_delete_no_matching_records(self, mock_mydb):
        """Test delete when no records match."""
        from app.dao.Report import Report
        
        mock_collection = Mock()
        mock_delete_result = Mock()
        mock_delete_result.deleted_count = 0
        mock_collection.delete_many.return_value = mock_delete_result
        Report.mycol = mock_collection
        
        query = {"BatchId": 999.999}
        Report.delete(query)
        
        mock_collection.delete_many.assert_called_once_with(query)
