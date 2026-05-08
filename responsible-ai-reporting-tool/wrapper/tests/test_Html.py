import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from bson import ObjectId

# Add src to path for imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.dao.Html import Html


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_collection():
    """Fixture to mock MongoDB collection"""
    with patch.object(Html, 'collection') as mock_coll:
        yield mock_coll


@pytest.fixture
def sample_html_data():
    """Fixture providing sample HTML data"""
    return {
        "_id": ObjectId("507f1f77bcf86cd799439011"),
        "BatchId": 1.1,
        "TenetId": 2.2,
        "HtmlFileId": "html_file_123",
        "ReportName": "test_report.html",
        "CreatedDateTime": "2024-01-01 10:00:00"
    }


@pytest.fixture
def sample_html_data_zip():
    """Fixture providing sample HTML data for zip file"""
    return {
        "_id": ObjectId("507f1f77bcf86cd799439012"),
        "BatchId": 3.3,
        "TenetId": 1.1,
        "HtmlFileId": "html_file_456",
        "ReportName": "combined_report.zip",
        "CreatedDateTime": "2024-01-02 15:30:00"
    }


# ============================================================================
# Test Html.find_one Method
# ============================================================================

class TestHtmlFindOne:
    """Test Html.find_one method"""
    
    def test_find_one_success(self, mock_collection, sample_html_data):
        """Test successful find_one with valid BatchId and TenetId"""
        # Setup mock
        mock_collection.find_one.return_value = {
            "HtmlFileId": "html_file_123",
            "ReportName": "test_report.html"
        }
        
        # Execute
        html_file_id, report_name = Html.find_one(batch_id=1.1, tenet_id=2.2)
        
        # Assert
        assert html_file_id == "html_file_123"
        assert report_name == "test_report.html"
        mock_collection.find_one.assert_called_once_with(
            {"BatchId": 1.1, "TenetId": 2.2},
            {"_id": 0, "HtmlFileId": 1, "ReportName": 1}
        )
    
    def test_find_one_with_zip_file(self, mock_collection):
        """Test find_one with zip file report"""
        mock_collection.find_one.return_value = {
            "HtmlFileId": "html_file_456",
            "ReportName": "combined_report.zip"
        }
        
        html_file_id, report_name = Html.find_one(batch_id=3.3, tenet_id=1.1)
        
        assert html_file_id == "html_file_456"
        assert report_name == "combined_report.zip"
        assert report_name.endswith('.zip')
    
    def test_find_one_batch_id_none(self, mock_collection):
        """Test find_one with None batch_id"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find_one(batch_id=None, tenet_id=2.2)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_one_tenet_id_none(self, mock_collection):
        """Test find_one with None tenet_id"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find_one(batch_id=1.1, tenet_id=None)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_one_both_none(self, mock_collection):
        """Test find_one with both None"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find_one(batch_id=None, tenet_id=None)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_one_batch_id_not_float(self, mock_collection):
        """Test find_one with non-float batch_id"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find_one(batch_id="1.1", tenet_id=2.2)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_one_tenet_id_not_float(self, mock_collection):
        """Test find_one with non-float tenet_id"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find_one(batch_id=1.1, tenet_id="2.2")
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_one_batch_id_integer(self, mock_collection):
        """Test find_one with integer batch_id (should fail as not float)"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find_one(batch_id=1, tenet_id=2.2)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_one_tenet_id_integer(self, mock_collection):
        """Test find_one with integer tenet_id (should fail as not float)"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find_one(batch_id=1.1, tenet_id=2)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_one_no_record_found(self, mock_collection):
        """Test find_one when no record found"""
        mock_collection.find_one.return_value = None
        
        with pytest.raises(ValueError, match="No record found for BatchID/TenetID: 1.1, 2.2"):
            Html.find_one(batch_id=1.1, tenet_id=2.2)
        
        mock_collection.find_one.assert_called_once()
    
    def test_find_one_database_exception(self, mock_collection):
        """Test find_one with database exception"""
        mock_collection.find_one.side_effect = Exception("Database connection error")
        
        with pytest.raises(Exception, match="Database connection error"):
            Html.find_one(batch_id=1.1, tenet_id=2.2)
        
        mock_collection.find_one.assert_called_once()
    
    def test_find_one_missing_html_file_id(self, mock_collection):
        """Test find_one when HtmlFileId is missing in result"""
        mock_collection.find_one.return_value = {
            "ReportName": "test_report.html"
        }
        
        html_file_id, report_name = Html.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert html_file_id is None
        assert report_name == "test_report.html"
    
    def test_find_one_missing_report_name(self, mock_collection):
        """Test find_one when ReportName is missing in result"""
        mock_collection.find_one.return_value = {
            "HtmlFileId": "html_file_123"
        }
        
        html_file_id, report_name = Html.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert html_file_id == "html_file_123"
        assert report_name is None
    
    def test_find_one_empty_result_fields(self, mock_collection):
        """Test find_one with empty result fields"""
        mock_collection.find_one.return_value = {
            "HtmlFileId": "",
            "ReportName": ""
        }
        
        html_file_id, report_name = Html.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert html_file_id == ""
        assert report_name == ""
    
    def test_find_one_with_negative_batch_id(self, mock_collection):
        """Test find_one with negative batch_id"""
        mock_collection.find_one.return_value = {
            "HtmlFileId": "html_file_789",
            "ReportName": "negative_test.html"
        }
        
        html_file_id, report_name = Html.find_one(batch_id=-1.1, tenet_id=2.2)
        
        assert html_file_id == "html_file_789"
        assert report_name == "negative_test.html"
    
    def test_find_one_with_zero_values(self, mock_collection):
        """Test find_one with zero values"""
        mock_collection.find_one.return_value = {
            "HtmlFileId": "html_file_000",
            "ReportName": "zero_test.html"
        }
        
        html_file_id, report_name = Html.find_one(batch_id=0.0, tenet_id=0.0)
        
        assert html_file_id == "html_file_000"
        assert report_name == "zero_test.html"
    
    def test_find_one_with_large_float_values(self, mock_collection):
        """Test find_one with large float values"""
        mock_collection.find_one.return_value = {
            "HtmlFileId": "html_file_999",
            "ReportName": "large_test.html"
        }
        
        html_file_id, report_name = Html.find_one(batch_id=999999.99, tenet_id=888888.88)
        
        assert html_file_id == "html_file_999"
        assert report_name == "large_test.html"
    
    def test_find_one_with_very_small_float_values(self, mock_collection):
        """Test find_one with very small float values"""
        mock_collection.find_one.return_value = {
            "HtmlFileId": "html_file_small",
            "ReportName": "small_test.html"
        }
        
        html_file_id, report_name = Html.find_one(batch_id=0.00001, tenet_id=0.00002)
        
        assert html_file_id == "html_file_small"
        assert report_name == "small_test.html"
    
    def test_find_one_projection_fields(self, mock_collection):
        """Test that find_one uses correct projection fields"""
        mock_collection.find_one.return_value = {
            "HtmlFileId": "html_file_123",
            "ReportName": "test_report.html"
        }
        
        Html.find_one(batch_id=1.1, tenet_id=2.2)
        
        # Verify projection excludes _id and includes only HtmlFileId and ReportName
        call_args = mock_collection.find_one.call_args
        assert call_args[0][1] == {"_id": 0, "HtmlFileId": 1, "ReportName": 1}
    
    def test_find_one_query_structure(self, mock_collection):
        """Test that find_one builds correct query structure"""
        mock_collection.find_one.return_value = {
            "HtmlFileId": "html_file_123",
            "ReportName": "test_report.html"
        }
        
        Html.find_one(batch_id=1.1, tenet_id=2.2)
        
        # Verify query structure
        call_args = mock_collection.find_one.call_args
        assert call_args[0][0] == {"BatchId": 1.1, "TenetId": 2.2}
    
    def test_find_one_with_special_characters_in_report_name(self, mock_collection):
        """Test find_one with special characters in ReportName"""
        mock_collection.find_one.return_value = {
            "HtmlFileId": "html_file_special",
            "ReportName": "test_report-v1.2_final (2024).html"
        }
        
        html_file_id, report_name = Html.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert html_file_id == "html_file_special"
        assert report_name == "test_report-v1.2_final (2024).html"
    
    def test_find_one_with_unicode_in_report_name(self, mock_collection):
        """Test find_one with Unicode characters in ReportName"""
        mock_collection.find_one.return_value = {
            "HtmlFileId": "html_file_unicode",
            "ReportName": "报告_test_テスト.html"
        }
        
        html_file_id, report_name = Html.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert html_file_id == "html_file_unicode"
        assert report_name == "报告_test_テスト.html"


# ============================================================================
# Test Html.find Method
# ============================================================================

class TestHtmlFind:
    """Test Html.find method"""
    
    def test_find_success(self, mock_collection, sample_html_data):
        """Test successful find with valid BatchId and TenetId"""
        mock_collection.find_one.return_value = sample_html_data
        
        result = Html.find(batch_id=1.1, tenet_id=2.2)
        
        assert result == sample_html_data
        assert result["HtmlFileId"] == "html_file_123"
        assert result["ReportName"] == "test_report.html"
        mock_collection.find_one.assert_called_once_with(
            {"BatchId": 1.1, "TenetId": 2.2}
        )
    
    def test_find_with_all_fields(self, mock_collection, sample_html_data):
        """Test find returns all fields from document"""
        mock_collection.find_one.return_value = sample_html_data
        
        result = Html.find(batch_id=1.1, tenet_id=2.2)
        
        assert "_id" in result
        assert "BatchId" in result
        assert "TenetId" in result
        assert "HtmlFileId" in result
        assert "ReportName" in result
        assert "CreatedDateTime" in result
    
    def test_find_batch_id_none(self, mock_collection):
        """Test find with None batch_id"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find(batch_id=None, tenet_id=2.2)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_tenet_id_none(self, mock_collection):
        """Test find with None tenet_id"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find(batch_id=1.1, tenet_id=None)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_both_none(self, mock_collection):
        """Test find with both None"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find(batch_id=None, tenet_id=None)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_batch_id_not_float(self, mock_collection):
        """Test find with non-float batch_id"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find(batch_id="1.1", tenet_id=2.2)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_tenet_id_not_float(self, mock_collection):
        """Test find with non-float tenet_id"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find(batch_id=1.1, tenet_id="2.2")
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_batch_id_integer(self, mock_collection):
        """Test find with integer batch_id (should fail)"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find(batch_id=1, tenet_id=2.2)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_tenet_id_integer(self, mock_collection):
        """Test find with integer tenet_id (should fail)"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find(batch_id=1.1, tenet_id=2)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_no_record_found(self, mock_collection):
        """Test find when no record found (returns None)"""
        mock_collection.find_one.return_value = None
        
        result = Html.find(batch_id=1.1, tenet_id=2.2)
        
        assert result is None
        mock_collection.find_one.assert_called_once()
    
    def test_find_database_exception(self, mock_collection):
        """Test find with database exception"""
        mock_collection.find_one.side_effect = Exception("Connection timeout")
        
        with pytest.raises(ValueError, match="Invalid BatchID/TenetID: 1.1, 2.2: Connection timeout"):
            Html.find(batch_id=1.1, tenet_id=2.2)
        
        mock_collection.find_one.assert_called_once()
    
    def test_find_with_negative_values(self, mock_collection, sample_html_data):
        """Test find with negative float values"""
        sample_html_data["BatchId"] = -1.1
        sample_html_data["TenetId"] = -2.2
        mock_collection.find_one.return_value = sample_html_data
        
        result = Html.find(batch_id=-1.1, tenet_id=-2.2)
        
        assert result["BatchId"] == -1.1
        assert result["TenetId"] == -2.2
    
    def test_find_with_zero_values(self, mock_collection, sample_html_data):
        """Test find with zero float values"""
        sample_html_data["BatchId"] = 0.0
        sample_html_data["TenetId"] = 0.0
        mock_collection.find_one.return_value = sample_html_data
        
        result = Html.find(batch_id=0.0, tenet_id=0.0)
        
        assert result["BatchId"] == 0.0
        assert result["TenetId"] == 0.0
    
    def test_find_with_large_float_values(self, mock_collection, sample_html_data):
        """Test find with large float values"""
        sample_html_data["BatchId"] = 999999.99
        sample_html_data["TenetId"] = 888888.88
        mock_collection.find_one.return_value = sample_html_data
        
        result = Html.find(batch_id=999999.99, tenet_id=888888.88)
        
        assert result["BatchId"] == 999999.99
        assert result["TenetId"] == 888888.88
    
    def test_find_with_precision_float_values(self, mock_collection, sample_html_data):
        """Test find with high precision float values"""
        sample_html_data["BatchId"] = 1.123456789
        sample_html_data["TenetId"] = 2.987654321
        mock_collection.find_one.return_value = sample_html_data
        
        result = Html.find(batch_id=1.123456789, tenet_id=2.987654321)
        
        assert result["BatchId"] == 1.123456789
        assert result["TenetId"] == 2.987654321
    
    def test_find_query_structure(self, mock_collection, sample_html_data):
        """Test that find builds correct query structure"""
        mock_collection.find_one.return_value = sample_html_data
        
        Html.find(batch_id=1.1, tenet_id=2.2)
        
        # Verify query structure (no projection in find)
        call_args = mock_collection.find_one.call_args
        assert call_args[0][0] == {"BatchId": 1.1, "TenetId": 2.2}
        assert len(call_args[0]) == 1  # Only query, no projection
    
    def test_find_returns_complete_document(self, mock_collection):
        """Test that find returns complete document with all fields"""
        complete_doc = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "BatchId": 1.1,
            "TenetId": 2.2,
            "HtmlFileId": "html_file_123",
            "ReportName": "test_report.html",
            "CreatedDateTime": "2024-01-01 10:00:00",
            "UpdatedDateTime": "2024-01-01 12:00:00",
            "Status": "SUCCESS",
            "FileSize": 1024
        }
        mock_collection.find_one.return_value = complete_doc
        
        result = Html.find(batch_id=1.1, tenet_id=2.2)
        
        assert len(result) == len(complete_doc)
        assert all(key in result for key in complete_doc.keys())
    
    def test_find_with_list_type(self, mock_collection):
        """Test find with list type (should fail)"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find(batch_id=[1.1], tenet_id=2.2)
    
    def test_find_with_dict_type(self, mock_collection):
        """Test find with dict type (should fail)"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find(batch_id={"value": 1.1}, tenet_id=2.2)
    
    def test_find_with_boolean_type(self, mock_collection):
        """Test find with boolean type (should fail)"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Html.find(batch_id=True, tenet_id=2.2)
    
    def test_find_exception_message_includes_ids(self, mock_collection):
        """Test that exception message includes BatchID and TenetID"""
        mock_collection.find_one.side_effect = Exception("Test error")
        
        with pytest.raises(ValueError) as exc_info:
            Html.find(batch_id=1.1, tenet_id=2.2)
        
        assert "1.1" in str(exc_info.value)
        assert "2.2" in str(exc_info.value)
        assert "Test error" in str(exc_info.value)


# ============================================================================
# Comparison Tests between find and find_one
# ============================================================================

class TestHtmlFindVsFindOne:
    """Test differences between find and find_one methods"""
    
    def test_find_vs_find_one_return_structure(self, mock_collection, sample_html_data):
        """Test that find returns full document while find_one returns specific fields"""
        mock_collection.find_one.return_value = sample_html_data
        
        # Call find
        find_result = Html.find(batch_id=1.1, tenet_id=2.2)
        
        # Reset mock
        mock_collection.reset_mock()
        mock_collection.find_one.return_value = {
            "HtmlFileId": "html_file_123",
            "ReportName": "test_report.html"
        }
        
        # Call find_one
        html_file_id, report_name = Html.find_one(batch_id=1.1, tenet_id=2.2)
        
        # find returns dict with all fields
        assert isinstance(find_result, dict)
        assert "_id" in find_result
        
        # find_one returns tuple with specific fields
        assert isinstance(html_file_id, str)
        assert isinstance(report_name, str)
    
    def test_find_vs_find_one_no_record_behavior(self, mock_collection):
        """Test different behavior when no record found"""
        # find returns None
        mock_collection.find_one.return_value = None
        find_result = Html.find(batch_id=1.1, tenet_id=2.2)
        assert find_result is None
        
        # find_one raises exception
        mock_collection.reset_mock()
        mock_collection.find_one.return_value = None
        with pytest.raises(ValueError, match="No record found"):
            Html.find_one(batch_id=1.1, tenet_id=2.2)
    
    def test_find_vs_find_one_projection_usage(self, mock_collection, sample_html_data):
        """Test that find_one uses projection but find doesn't"""
        mock_collection.find_one.return_value = sample_html_data
        
        # Call find
        Html.find(batch_id=1.1, tenet_id=2.2)
        find_call_args = mock_collection.find_one.call_args
        
        # Reset mock
        mock_collection.reset_mock()
        mock_collection.find_one.return_value = {
            "HtmlFileId": "html_file_123",
            "ReportName": "test_report.html"
        }
        
        # Call find_one
        Html.find_one(batch_id=1.1, tenet_id=2.2)
        find_one_call_args = mock_collection.find_one.call_args
        
        # find has no projection (only 1 argument)
        assert len(find_call_args[0]) == 1
        
        # find_one has projection (2 arguments)
        assert len(find_one_call_args[0]) == 2


# ============================================================================
# Integration and Edge Case Tests
# ============================================================================

class TestHtmlIntegration:
    """Integration and edge case tests"""
    
    def test_sequential_find_operations(self, mock_collection, sample_html_data):
        """Test multiple sequential find operations"""
        mock_collection.find_one.return_value = sample_html_data
        
        # Multiple calls should work independently
        result1 = Html.find(batch_id=1.1, tenet_id=2.2)
        result2 = Html.find(batch_id=1.1, tenet_id=2.2)
        result3 = Html.find(batch_id=1.1, tenet_id=2.2)
        
        assert result1 == result2 == result3
        assert mock_collection.find_one.call_count == 3
    
    def test_sequential_find_one_operations(self, mock_collection):
        """Test multiple sequential find_one operations"""
        mock_collection.find_one.return_value = {
            "HtmlFileId": "html_file_123",
            "ReportName": "test_report.html"
        }
        
        # Multiple calls should work independently
        result1 = Html.find_one(batch_id=1.1, tenet_id=2.2)
        result2 = Html.find_one(batch_id=1.1, tenet_id=2.2)
        result3 = Html.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert result1 == result2 == result3
        assert mock_collection.find_one.call_count == 3
    
    def test_mixed_find_and_find_one_operations(self, mock_collection, sample_html_data):
        """Test mixed find and find_one operations"""
        mock_collection.find_one.side_effect = [
            sample_html_data,
            {"HtmlFileId": "html_file_123", "ReportName": "test_report.html"},
            sample_html_data,
            {"HtmlFileId": "html_file_123", "ReportName": "test_report.html"}
        ]
        
        # Alternate between find and find_one
        find_result = Html.find(batch_id=1.1, tenet_id=2.2)
        find_one_result = Html.find_one(batch_id=1.1, tenet_id=2.2)
        find_result2 = Html.find(batch_id=1.1, tenet_id=2.2)
        find_one_result2 = Html.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert isinstance(find_result, dict)
        assert isinstance(find_one_result, tuple)
        assert mock_collection.find_one.call_count == 4
    
    def test_different_batch_tenet_combinations(self, mock_collection):
        """Test with various BatchId and TenetId combinations"""
        test_cases = [
            (1.1, 2.2),
            (3.3, 1.1),
            (0.1, 0.2),
            (99.99, 88.88),
            (-1.1, -2.2)
        ]
        
        for batch_id, tenet_id in test_cases:
            mock_collection.find_one.return_value = {
                "HtmlFileId": f"html_{batch_id}_{tenet_id}",
                "ReportName": f"report_{batch_id}_{tenet_id}.html"
            }
            
            html_file_id, report_name = Html.find_one(batch_id=batch_id, tenet_id=tenet_id)
            
            assert html_file_id == f"html_{batch_id}_{tenet_id}"
            assert report_name == f"report_{batch_id}_{tenet_id}.html"
    
    def test_concurrent_validation_checks(self, mock_collection):
        """Test that validation happens before database call"""
        # Invalid input should not reach database
        invalid_inputs = [
            (None, 2.2),
            (1.1, None),
            ("1.1", 2.2),
            (1.1, "2.2"),
            (1, 2.2),
            (1.1, 2)
        ]
        
        for batch_id, tenet_id in invalid_inputs:
            with pytest.raises(ValueError):
                Html.find_one(batch_id=batch_id, tenet_id=tenet_id)
            
            with pytest.raises(ValueError):
                Html.find(batch_id=batch_id, tenet_id=tenet_id)
        
        # Database should never be called for invalid inputs
        mock_collection.find_one.assert_not_called()


# ============================================================================
# Static Method Tests
# ============================================================================

class TestHtmlStaticMethods:
    """Test that methods are properly defined as static"""
    
    def test_find_one_is_static_method(self):
        """Test that find_one is a static method"""
        assert isinstance(Html.__dict__['find_one'], staticmethod)
    
    def test_find_is_static_method(self):
        """Test that find is a static method"""
        assert isinstance(Html.__dict__['find'], staticmethod)
    
    def test_can_call_without_instance(self, mock_collection):
        """Test that methods can be called without creating an instance"""
        mock_collection.find_one.return_value = {
            "HtmlFileId": "html_file_123",
            "ReportName": "test_report.html"
        }
        
        # Should work without creating Html instance
        result = Html.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert result is not None
        
        mock_collection.find_one.return_value = {"HtmlFileId": "test"}
        result2 = Html.find(batch_id=1.1, tenet_id=2.2)
        
        assert result2 is not None