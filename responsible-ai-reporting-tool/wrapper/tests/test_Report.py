import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from bson import ObjectId
from pymongo.errors import InvalidDocument

# Add src to path for imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.dao.Report import Report


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_collection():
    """Fixture to mock MongoDB collection"""
    with patch.object(Report, 'collection') as mock_coll:
        yield mock_coll


@pytest.fixture
def sample_report_document():
    """Fixture providing sample report document"""
    return {
        "BatchId": 1.1,
        "TenetId": 2.2,
        "ReportFileId": "report_file_123",
        "ContentType": "application/pdf",
        "ReportName": "test_report.pdf",
        "CreatedDateTime": "2024-01-01 10:00:00",
        "Status": "SUCCESS"
    }


@pytest.fixture
def sample_report_document_zip():
    """Fixture providing sample report document for zip file"""
    return {
        "BatchId": 3.3,
        "TenetId": 1.1,
        "ReportFileId": "report_file_456",
        "ContentType": "application/zip",
        "ReportName": "combined_report.zip",
        "CreatedDateTime": "2024-01-02 15:30:00",
        "Status": "SUCCESS"
    }


@pytest.fixture
def sample_insert_result():
    """Fixture providing mock insert result"""
    mock_result = Mock()
    mock_result.acknowledged = True
    mock_result.inserted_id = ObjectId("507f1f77bcf86cd799439011")
    return mock_result


# ============================================================================
# Test Report.create Method
# ============================================================================

class TestReportCreate:
    """Test Report.create method"""
    
    def test_create_success(self, mock_collection, sample_report_document, sample_insert_result):
        """Test successful document creation"""
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create(sample_report_document)
        
        assert result is True
        mock_collection.insert_one.assert_called_once_with(sample_report_document)
    
    def test_create_with_pdf_content_type(self, mock_collection, sample_insert_result):
        """Test create with PDF content type"""
        document = {
            "BatchId": 1.1,
            "TenetId": 2.2,
            "ReportFileId": "pdf_file_123",
            "ContentType": "application/pdf",
            "ReportName": "report.pdf"
        }
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create(document)
        
        assert result is True
        mock_collection.insert_one.assert_called_once_with(document)
    
    def test_create_with_zip_content_type(self, mock_collection, sample_insert_result):
        """Test create with ZIP content type"""
        document = {
            "BatchId": 3.3,
            "TenetId": 1.1,
            "ReportFileId": "zip_file_456",
            "ContentType": "application/zip",
            "ReportName": "combined.zip"
        }
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create(document)
        
        assert result is True
        mock_collection.insert_one.assert_called_once_with(document)
    
    def test_create_with_all_fields(self, mock_collection, sample_insert_result):
        """Test create with all possible fields"""
        document = {
            "BatchId": 1.1,
            "TenetId": 2.2,
            "ReportFileId": "report_full_123",
            "ContentType": "application/pdf",
            "ReportName": "full_report.pdf",
            "CreatedDateTime": "2024-01-01 10:00:00",
            "UpdatedDateTime": "2024-01-01 12:00:00",
            "Status": "SUCCESS",
            "FileSize": 2048,
            "Description": "Test report"
        }
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create(document)
        
        assert result is True
        mock_collection.insert_one.assert_called_once_with(document)
    
    def test_create_with_minimal_fields(self, mock_collection, sample_insert_result):
        """Test create with minimal required fields"""
        document = {
            "BatchId": 1.1,
            "ReportFileId": "minimal_123"
        }
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create(document)
        
        assert result is True
        mock_collection.insert_one.assert_called_once_with(document)
    
    def test_create_document_none(self, mock_collection):
        """Test create with None document"""
        with pytest.raises(ValueError, match="Document must be a non-empty value"):
            Report.create(None)
        
        mock_collection.insert_one.assert_not_called()
    
    def test_create_invalid_document(self, mock_collection):
        """Test create with invalid document type"""
        mock_collection.insert_one.side_effect = InvalidDocument("Invalid document structure")
        
        document = {"test": "data"}
        
        with pytest.raises(ValueError, match="Document is not a valid document"):
            Report.create(document)
        
        mock_collection.insert_one.assert_called_once_with(document)
    
    def test_create_insert_not_acknowledged(self, mock_collection):
        """Test create when insert is not acknowledged"""
        mock_result = Mock()
        mock_result.acknowledged = False
        mock_collection.insert_one.return_value = mock_result
        
        document = {"BatchId": 1.1, "ReportFileId": "test_123"}
        
        with pytest.raises(RuntimeError, match="Failed to insert document into the collection"):
            Report.create(document)
        
        mock_collection.insert_one.assert_called_once_with(document)
    
    def test_create_with_empty_dict(self, mock_collection, sample_insert_result):
        """Test create with empty dictionary"""
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create({})
        
        assert result is True
        mock_collection.insert_one.assert_called_once_with({})
    
    def test_create_with_special_characters(self, mock_collection, sample_insert_result):
        """Test create with special characters in fields"""
        document = {
            "BatchId": 1.1,
            "ReportName": "report-v1.2_final (2024).pdf",
            "Description": "Test <>&\"' special chars"
        }
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create(document)
        
        assert result is True
    
    def test_create_with_unicode_characters(self, mock_collection, sample_insert_result):
        """Test create with Unicode characters"""
        document = {
            "BatchId": 1.1,
            "ReportName": "报告_test_テスト.pdf",
            "Description": "测试 Тест 🚀"
        }
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create(document)
        
        assert result is True
    
    def test_create_with_nested_document(self, mock_collection, sample_insert_result):
        """Test create with nested document structure"""
        document = {
            "BatchId": 1.1,
            "ReportFileId": "nested_123",
            "Metadata": {
                "Author": "Test User",
                "Version": "1.0",
                "Tags": ["ai", "report", "analysis"]
            }
        }
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create(document)
        
        assert result is True
    
    def test_create_with_list_values(self, mock_collection, sample_insert_result):
        """Test create with list values"""
        document = {
            "BatchId": 1.1,
            "ReportFileId": "list_123",
            "Tags": ["tag1", "tag2", "tag3"],
            "Attachments": [
                {"name": "file1.pdf", "size": 1024},
                {"name": "file2.pdf", "size": 2048}
            ]
        }
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create(document)
        
        assert result is True
    
    def test_create_with_numeric_values(self, mock_collection, sample_insert_result):
        """Test create with various numeric values"""
        document = {
            "BatchId": 1.1,
            "TenetId": 2.2,
            "FileSize": 1024,
            "PageCount": 10,
            "Version": 1.5,
            "Rating": 4.8
        }
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create(document)
        
        assert result is True
    
    def test_create_with_boolean_values(self, mock_collection, sample_insert_result):
        """Test create with boolean values"""
        document = {
            "BatchId": 1.1,
            "ReportFileId": "bool_123",
            "IsPublic": True,
            "IsArchived": False,
            "HasAttachments": True
        }
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create(document)
        
        assert result is True
    
    def test_create_with_null_values(self, mock_collection, sample_insert_result):
        """Test create with null/None values in fields"""
        document = {
            "BatchId": 1.1,
            "ReportFileId": "null_123",
            "Description": None,
            "UpdatedDateTime": None
        }
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create(document)
        
        assert result is True
    
    def test_create_database_connection_error(self, mock_collection):
        """Test create with database connection error"""
        mock_collection.insert_one.side_effect = Exception("Connection timeout")
        
        document = {"BatchId": 1.1, "ReportFileId": "error_123"}
        
        with pytest.raises(Exception, match="Connection timeout"):
            Report.create(document)
    
    def test_create_with_large_document(self, mock_collection, sample_insert_result):
        """Test create with large document"""
        document = {
            "BatchId": 1.1,
            "ReportFileId": "large_123",
            "Data": "x" * 10000,  # Large string
            "Items": [{"id": i, "value": f"item_{i}"} for i in range(100)]
        }
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create(document)
        
        assert result is True
    
    def test_create_with_datetime_objects(self, mock_collection, sample_insert_result):
        """Test create with datetime objects"""
        from datetime import datetime
        
        document = {
            "BatchId": 1.1,
            "ReportFileId": "datetime_123",
            "CreatedDateTime": datetime(2024, 1, 1, 10, 0, 0),
            "UpdatedDateTime": datetime(2024, 1, 1, 12, 0, 0)
        }
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create(document)
        
        assert result is True
    
    def test_create_returns_acknowledged_value(self, mock_collection):
        """Test that create returns the acknowledged value"""
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_collection.insert_one.return_value = mock_result
        
        document = {"BatchId": 1.1}
        result = Report.create(document)
        
        assert result is True
        assert result == mock_result.acknowledged
    
    def test_create_with_object_id(self, mock_collection, sample_insert_result):
        """Test create with ObjectId field"""
        document = {
            "BatchId": 1.1,
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "ReportFileId": "objectid_123"
        }
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create(document)
        
        assert result is True
    
    def test_create_multiple_documents_sequentially(self, mock_collection, sample_insert_result):
        """Test creating multiple documents sequentially"""
        mock_collection.insert_one.return_value = sample_insert_result
        
        documents = [
            {"BatchId": 1.1, "ReportFileId": "seq_1"},
            {"BatchId": 2.2, "ReportFileId": "seq_2"},
            {"BatchId": 3.3, "ReportFileId": "seq_3"}
        ]
        
        results = []
        for doc in documents:
            result = Report.create(doc)
            results.append(result)
        
        assert all(results)
        assert mock_collection.insert_one.call_count == 3


# ============================================================================
# Test Report.find_one Method
# ============================================================================

class TestReportFindOne:
    """Test Report.find_one method"""
    
    def test_find_one_success(self, mock_collection):
        """Test successful find_one with valid BatchId and TenetId"""
        mock_collection.find_one.return_value = {
            "ReportFileId": "report_file_123",
            "ContentType": "application/pdf",
            "ReportName": "test_report.pdf"
        }
        
        result = Report.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert result is not None
        assert result["ReportFileId"] == "report_file_123"
        assert result["ContentType"] == "application/pdf"
        assert result["ReportName"] == "test_report.pdf"
        mock_collection.find_one.assert_called_once_with(
            {"BatchId": 1.1, "TenetId": 2.2},
            {"_id": 0, "ReportFileId": 1, "ContentType": 1, "ReportName": 1}
        )
    
    def test_find_one_with_pdf_content_type(self, mock_collection):
        """Test find_one with PDF content type"""
        mock_collection.find_one.return_value = {
            "ReportFileId": "pdf_123",
            "ContentType": "application/pdf",
            "ReportName": "document.pdf"
        }
        
        result = Report.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert result["ContentType"] == "application/pdf"
        assert result["ReportName"].endswith('.pdf')
    
    def test_find_one_with_zip_content_type(self, mock_collection):
        """Test find_one with ZIP content type"""
        mock_collection.find_one.return_value = {
            "ReportFileId": "zip_456",
            "ContentType": "application/zip",
            "ReportName": "combined.zip"
        }
        
        result = Report.find_one(batch_id=3.3, tenet_id=1.1)
        
        assert result["ContentType"] == "application/zip"
        assert result["ReportName"].endswith('.zip')
    
    def test_find_one_batch_id_none(self, mock_collection):
        """Test find_one with None batch_id"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Report.find_one(batch_id=None, tenet_id=2.2)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_one_tenet_id_none(self, mock_collection):
        """Test find_one with None tenet_id"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Report.find_one(batch_id=1.1, tenet_id=None)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_one_both_none(self, mock_collection):
        """Test find_one with both None"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Report.find_one(batch_id=None, tenet_id=None)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_one_batch_id_not_float(self, mock_collection):
        """Test find_one with non-float batch_id"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Report.find_one(batch_id="1.1", tenet_id=2.2)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_one_tenet_id_not_float(self, mock_collection):
        """Test find_one with non-float tenet_id"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Report.find_one(batch_id=1.1, tenet_id="2.2")
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_one_batch_id_integer(self, mock_collection):
        """Test find_one with integer batch_id (should fail)"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Report.find_one(batch_id=1, tenet_id=2.2)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_one_tenet_id_integer(self, mock_collection):
        """Test find_one with integer tenet_id (should fail)"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Report.find_one(batch_id=1.1, tenet_id=2)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_one_batch_id_list(self, mock_collection):
        """Test find_one with list type batch_id"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Report.find_one(batch_id=[1.1], tenet_id=2.2)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_one_tenet_id_dict(self, mock_collection):
        """Test find_one with dict type tenet_id"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Report.find_one(batch_id=1.1, tenet_id={"value": 2.2})
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_one_batch_id_boolean(self, mock_collection):
        """Test find_one with boolean batch_id"""
        with pytest.raises(ValueError, match="BatchID/TenetID must be a non-empty float"):
            Report.find_one(batch_id=True, tenet_id=2.2)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_one_no_record_found(self, mock_collection):
        """Test find_one when no record found (returns None)"""
        mock_collection.find_one.return_value = None
        
        result = Report.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert result is None
        mock_collection.find_one.assert_called_once()
    
    def test_find_one_database_exception(self, mock_collection):
        """Test find_one with database exception"""
        mock_collection.find_one.side_effect = Exception("Connection timeout")
        
        with pytest.raises(ValueError, match="Invalid BatchID/TenetID: 1.1, 2.2: Connection timeout"):
            Report.find_one(batch_id=1.1, tenet_id=2.2)
        
        mock_collection.find_one.assert_called_once()
    
    def test_find_one_with_negative_batch_id(self, mock_collection):
        """Test find_one with negative batch_id"""
        mock_collection.find_one.return_value = {
            "ReportFileId": "negative_123",
            "ContentType": "application/pdf",
            "ReportName": "negative_test.pdf"
        }
        
        result = Report.find_one(batch_id=-1.1, tenet_id=2.2)
        
        assert result is not None
        assert result["ReportFileId"] == "negative_123"
    
    def test_find_one_with_zero_values(self, mock_collection):
        """Test find_one with zero values"""
        mock_collection.find_one.return_value = {
            "ReportFileId": "zero_123",
            "ContentType": "application/pdf",
            "ReportName": "zero_test.pdf"
        }
        
        result = Report.find_one(batch_id=0.0, tenet_id=0.0)
        
        assert result is not None
        assert result["ReportFileId"] == "zero_123"
    
    def test_find_one_with_large_float_values(self, mock_collection):
        """Test find_one with large float values"""
        mock_collection.find_one.return_value = {
            "ReportFileId": "large_123",
            "ContentType": "application/pdf",
            "ReportName": "large_test.pdf"
        }
        
        result = Report.find_one(batch_id=999999.99, tenet_id=888888.88)
        
        assert result is not None
    
    def test_find_one_with_small_float_values(self, mock_collection):
        """Test find_one with very small float values"""
        mock_collection.find_one.return_value = {
            "ReportFileId": "small_123",
            "ContentType": "application/pdf",
            "ReportName": "small_test.pdf"
        }
        
        result = Report.find_one(batch_id=0.00001, tenet_id=0.00002)
        
        assert result is not None
    
    def test_find_one_with_high_precision_floats(self, mock_collection):
        """Test find_one with high precision float values"""
        mock_collection.find_one.return_value = {
            "ReportFileId": "precision_123",
            "ContentType": "application/pdf",
            "ReportName": "precision_test.pdf"
        }
        
        result = Report.find_one(batch_id=1.123456789, tenet_id=2.987654321)
        
        assert result is not None
    
    def test_find_one_projection_fields(self, mock_collection):
        """Test that find_one uses correct projection fields"""
        mock_collection.find_one.return_value = {
            "ReportFileId": "proj_123",
            "ContentType": "application/pdf",
            "ReportName": "projection_test.pdf"
        }
        
        Report.find_one(batch_id=1.1, tenet_id=2.2)
        
        # Verify projection excludes _id and includes specific fields
        call_args = mock_collection.find_one.call_args
        assert call_args[0][1] == {
            "_id": 0,
            "ReportFileId": 1,
            "ContentType": 1,
            "ReportName": 1
        }
    
    def test_find_one_query_structure(self, mock_collection):
        """Test that find_one builds correct query structure"""
        mock_collection.find_one.return_value = {
            "ReportFileId": "query_123",
            "ContentType": "application/pdf",
            "ReportName": "query_test.pdf"
        }
        
        Report.find_one(batch_id=1.1, tenet_id=2.2)
        
        # Verify query structure
        call_args = mock_collection.find_one.call_args
        assert call_args[0][0] == {"BatchId": 1.1, "TenetId": 2.2}
    
    def test_find_one_with_special_characters_in_report_name(self, mock_collection):
        """Test find_one with special characters in ReportName"""
        mock_collection.find_one.return_value = {
            "ReportFileId": "special_123",
            "ContentType": "application/pdf",
            "ReportName": "report-v1.2_final (2024).pdf"
        }
        
        result = Report.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert result["ReportName"] == "report-v1.2_final (2024).pdf"
    
    def test_find_one_with_unicode_in_report_name(self, mock_collection):
        """Test find_one with Unicode characters in ReportName"""
        mock_collection.find_one.return_value = {
            "ReportFileId": "unicode_123",
            "ContentType": "application/pdf",
            "ReportName": "报告_test_テスト.pdf"
        }
        
        result = Report.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert result["ReportName"] == "报告_test_テスト.pdf"
    
    def test_find_one_with_missing_report_file_id(self, mock_collection):
        """Test find_one when ReportFileId is missing"""
        mock_collection.find_one.return_value = {
            "ContentType": "application/pdf",
            "ReportName": "test.pdf"
        }
        
        result = Report.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert "ReportFileId" not in result
        assert result["ContentType"] == "application/pdf"
    
    def test_find_one_with_missing_content_type(self, mock_collection):
        """Test find_one when ContentType is missing"""
        mock_collection.find_one.return_value = {
            "ReportFileId": "missing_ct_123",
            "ReportName": "test.pdf"
        }
        
        result = Report.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert "ContentType" not in result
        assert result["ReportFileId"] == "missing_ct_123"
    
    def test_find_one_with_missing_report_name(self, mock_collection):
        """Test find_one when ReportName is missing"""
        mock_collection.find_one.return_value = {
            "ReportFileId": "missing_rn_123",
            "ContentType": "application/pdf"
        }
        
        result = Report.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert "ReportName" not in result
        assert result["ReportFileId"] == "missing_rn_123"
    
    def test_find_one_with_empty_result_fields(self, mock_collection):
        """Test find_one with empty result fields"""
        mock_collection.find_one.return_value = {
            "ReportFileId": "",
            "ContentType": "",
            "ReportName": ""
        }
        
        result = Report.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert result["ReportFileId"] == ""
        assert result["ContentType"] == ""
        assert result["ReportName"] == ""
    
    def test_find_one_exception_message_includes_ids(self, mock_collection):
        """Test that exception message includes BatchID and TenetID"""
        mock_collection.find_one.side_effect = Exception("Test error")
        
        with pytest.raises(ValueError) as exc_info:
            Report.find_one(batch_id=1.1, tenet_id=2.2)
        
        error_message = str(exc_info.value)
        assert "1.1" in error_message
        assert "2.2" in error_message
        assert "Test error" in error_message
    
    def test_find_one_multiple_sequential_calls(self, mock_collection):
        """Test multiple sequential find_one calls"""
        mock_collection.find_one.return_value = {
            "ReportFileId": "seq_123",
            "ContentType": "application/pdf",
            "ReportName": "test.pdf"
        }
        
        result1 = Report.find_one(batch_id=1.1, tenet_id=2.2)
        result2 = Report.find_one(batch_id=1.1, tenet_id=2.2)
        result3 = Report.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert result1 == result2 == result3
        assert mock_collection.find_one.call_count == 3
    
    def test_find_one_different_batch_tenet_combinations(self, mock_collection):
        """Test with various BatchId and TenetId combinations"""
        test_cases = [
            (1.1, 2.2, "combo1"),
            (3.3, 1.1, "combo2"),
            (0.1, 0.2, "combo3"),
            (99.99, 88.88, "combo4"),
            (-1.1, -2.2, "combo5")
        ]
        
        for batch_id, tenet_id, report_id in test_cases:
            mock_collection.find_one.return_value = {
                "ReportFileId": report_id,
                "ContentType": "application/pdf",
                "ReportName": f"report_{report_id}.pdf"
            }
            
            result = Report.find_one(batch_id=batch_id, tenet_id=tenet_id)
            
            assert result["ReportFileId"] == report_id
            assert result["ReportName"] == f"report_{report_id}.pdf"
        
        assert mock_collection.find_one.call_count == len(test_cases)


# ============================================================================
# Static Method Tests
# ============================================================================

class TestReportStaticMethods:
    """Test that methods are properly defined as static"""
    
    def test_create_is_static_method(self):
        """Test that create is a static method"""
        assert isinstance(Report.__dict__['create'], staticmethod)
    
    def test_find_one_is_static_method(self):
        """Test that find_one is a static method"""
        assert isinstance(Report.__dict__['find_one'], staticmethod)
    
    def test_can_call_create_without_instance(self, mock_collection, sample_insert_result):
        """Test that create can be called without creating an instance"""
        mock_collection.insert_one.return_value = sample_insert_result
        
        # Should work without creating Report instance
        result = Report.create({"BatchId": 1.1, "ReportFileId": "test_123"})
        
        assert result is True
    
    def test_can_call_find_one_without_instance(self, mock_collection):
        """Test that find_one can be called without creating an instance"""
        mock_collection.find_one.return_value = {
            "ReportFileId": "test_123",
            "ContentType": "application/pdf",
            "ReportName": "test.pdf"
        }
        
        # Should work without creating Report instance
        result = Report.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert result is not None


# ============================================================================
# Integration Tests
# ============================================================================

class TestReportIntegration:
    """Integration tests for Report class"""
    
    def test_create_and_find_one_workflow(self, mock_collection, sample_insert_result):
        """Test complete workflow: create then find_one"""
        # Create document
        document = {
            "BatchId": 1.1,
            "TenetId": 2.2,
            "ReportFileId": "workflow_123",
            "ContentType": "application/pdf",
            "ReportName": "workflow_test.pdf"
        }
        mock_collection.insert_one.return_value = sample_insert_result
        
        create_result = Report.create(document)
        assert create_result is True
        
        # Find document
        mock_collection.find_one.return_value = {
            "ReportFileId": "workflow_123",
            "ContentType": "application/pdf",
            "ReportName": "workflow_test.pdf"
        }
        
        find_result = Report.find_one(batch_id=1.1, tenet_id=2.2)
        
        assert find_result["ReportFileId"] == document["ReportFileId"]
        assert find_result["ContentType"] == document["ContentType"]
        assert find_result["ReportName"] == document["ReportName"]
    
    def test_multiple_create_operations(self, mock_collection, sample_insert_result):
        """Test multiple create operations in sequence"""
        mock_collection.insert_one.return_value = sample_insert_result
        
        documents = [
            {"BatchId": 1.1, "TenetId": 2.2, "ReportFileId": "multi_1"},
            {"BatchId": 3.3, "TenetId": 1.1, "ReportFileId": "multi_2"},
            {"BatchId": 5.5, "TenetId": 4.4, "ReportFileId": "multi_3"}
        ]
        
        results = [Report.create(doc) for doc in documents]
        
        assert all(results)
        assert mock_collection.insert_one.call_count == 3
    
    def test_multiple_find_one_operations(self, mock_collection):
        """Test multiple find_one operations with different IDs"""
        test_data = [
            (1.1, 2.2, "report_1"),
            (3.3, 1.1, "report_2"),
            (5.5, 4.4, "report_3")
        ]
        
        for batch_id, tenet_id, report_id in test_data:
            mock_collection.find_one.return_value = {
                "ReportFileId": report_id,
                "ContentType": "application/pdf",
                "ReportName": f"{report_id}.pdf"
            }
            
            result = Report.find_one(batch_id=batch_id, tenet_id=tenet_id)
            assert result["ReportFileId"] == report_id
        
        assert mock_collection.find_one.call_count == len(test_data)
    
    def test_error_recovery_after_failed_create(self, mock_collection, sample_insert_result):
        """Test that subsequent operations work after a failed create"""
        # First create fails
        mock_collection.insert_one.side_effect = InvalidDocument("Invalid doc")
        
        with pytest.raises(ValueError, match="Document is not a valid document"):
            Report.create({"test": "data"})
        
        # Reset mock for successful create
        mock_collection.insert_one.side_effect = None
        mock_collection.insert_one.return_value = sample_insert_result
        
        # Second create succeeds
        result = Report.create({"BatchId": 1.1, "ReportFileId": "recovery_123"})
        assert result is True
    
    def test_error_recovery_after_failed_find_one(self, mock_collection):
        """Test that subsequent operations work after a failed find_one"""
        # First find_one fails
        mock_collection.find_one.side_effect = Exception("DB Error")
        
        with pytest.raises(ValueError, match="Invalid BatchID/TenetID"):
            Report.find_one(batch_id=1.1, tenet_id=2.2)
        
        # Reset mock for successful find_one
        mock_collection.find_one.side_effect = None
        mock_collection.find_one.return_value = {
            "ReportFileId": "recovery_123",
            "ContentType": "application/pdf",
            "ReportName": "recovery.pdf"
        }
        
        # Second find_one succeeds
        result = Report.find_one(batch_id=1.1, tenet_id=2.2)
        assert result is not None


# ============================================================================
# Edge Cases and Boundary Tests
# ============================================================================

class TestReportEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_create_with_max_float_values(self, mock_collection, sample_insert_result):
        """Test create with maximum float values"""
        import sys
        document = {
            "BatchId": sys.float_info.max,
            "TenetId": sys.float_info.max
        }
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create(document)
        assert result is True
    
    def test_create_with_min_float_values(self, mock_collection, sample_insert_result):
        """Test create with minimum positive float values"""
        import sys
        document = {
            "BatchId": sys.float_info.min,
            "TenetId": sys.float_info.min
        }
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create(document)
        assert result is True
    
    def test_find_one_with_inf_values(self, mock_collection):
        """Test find_one with infinity values"""
        # float('inf') is still a float, so it should pass type check
        mock_collection.find_one.return_value = {
            "ReportFileId": "inf_123",
            "ContentType": "application/pdf",
            "ReportName": "inf_test.pdf"
        }
        
        result = Report.find_one(batch_id=float('inf'), tenet_id=2.2)
        assert result is not None
    
    def test_create_with_very_long_string_values(self, mock_collection, sample_insert_result):
        """Test create with very long string values"""
        long_string = "x" * 100000
        document = {
            "BatchId": 1.1,
            "ReportFileId": long_string,
            "ReportName": long_string,
            "Description": long_string
        }
        mock_collection.insert_one.return_value = sample_insert_result
        
        result = Report.create(document)
        assert result is True
    
    def test_find_one_network_timeout(self, mock_collection):
        """Test find_one with network timeout exception"""
        from pymongo.errors import NetworkTimeout
        mock_collection.find_one.side_effect = NetworkTimeout("Network timeout")
        
        with pytest.raises(ValueError, match="Invalid BatchID/TenetID.*Network timeout"):
            Report.find_one(batch_id=1.1, tenet_id=2.2)
    
    def test_create_with_duplicate_key_error(self, mock_collection):
        """Test create with duplicate key error"""
        from pymongo.errors import DuplicateKeyError
        mock_collection.insert_one.side_effect = DuplicateKeyError("Duplicate key")
        
        with pytest.raises(DuplicateKeyError, match="Duplicate key"):
            Report.create({"BatchId": 1.1, "_id": ObjectId()})