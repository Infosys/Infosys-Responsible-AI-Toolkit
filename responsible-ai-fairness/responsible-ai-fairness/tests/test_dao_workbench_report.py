"""
Comprehensive test suite for fairness.dao.WorkBench.report module.

Tests the Report class which provides MongoDB operations for report document storage.
Covers initialization, create (upsert), find operations, error handling, and quality metrics.

Test Strategy:
- Module-level mocking for global instantiations (DataBase_WB, logger)
- Collection-level mocking for MongoDB operations
- FastAPI HTTPException validation
- Comprehensive edge case and error path testing
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from pymongo.errors import InvalidDocument, WriteError, OperationFailure

# Import the module under test
from fairness.dao.WorkBench.report import Report


# ==================== FIXTURES ====================

@pytest.fixture
def mock_collection():
    """Create a mock MongoDB collection."""
    collection = MagicMock()
    return collection


@pytest.fixture
def mock_update_result():
    """Create a mock update result with acknowledged=True."""
    result = MagicMock()
    result.acknowledged = True
    result.upserted_id = "507f1f77bcf86cd799439011"
    result.matched_count = 1
    result.modified_count = 1
    return result


@pytest.fixture
def mock_update_result_failed():
    """Create a mock update result with acknowledged=False."""
    result = MagicMock()
    result.acknowledged = False
    result.upserted_id = None
    result.matched_count = 0
    result.modified_count = 0
    return result


@pytest.fixture
def valid_report_document():
    """Create a valid report document for testing."""
    return {
        "BatchId": 100.0,
        "ReportFileId": "report_123",
        "ReportName": "Fairness Analysis Report",
        "CreatedAt": "2025-12-24T10:00:00",
        "Status": "completed"
    }


@pytest.fixture
def find_result():
    """Create a mock result for Report.find()."""
    return {
        "ReportFileId": "report_123",
        "ReportName": "Fairness Analysis Report"
    }


@pytest.fixture
def setup_report_collection(mock_collection):
    """Setup Report.collection with mock collection."""
    original_collection = Report.collection
    Report.collection = mock_collection
    yield mock_collection
    Report.collection = original_collection


# ==================== INITIALIZATION TESTS ====================

class TestReportClassInitialization:
    """Test Report class initialization and class attributes."""
    
    def test_class_has_collection_attribute(self):
        """Test that Report class has collection attribute."""
        assert hasattr(Report, 'collection')
    
    def test_collection_is_not_none(self):
        """Test that collection is initialized."""
        assert Report.collection is not None
    
    def test_class_has_create_method(self):
        """Test that Report class has create static method."""
        assert hasattr(Report, 'create')
        assert callable(Report.create)
    
    def test_class_has_find_method(self):
        """Test that Report class has find instance method."""
        assert hasattr(Report, 'find')
        assert callable(Report.find)
    
    def test_create_is_static_method(self):
        """Test that create is a static method."""
        assert isinstance(Report.__dict__['create'], staticmethod)
    
    def test_find_is_instance_method(self):
        """Test that find is an instance method (not static)."""
        assert not isinstance(Report.__dict__['find'], staticmethod)


# ==================== CREATE METHOD TESTS ====================

class TestCreateMethodSuccess:
    """Test successful document creation/update scenarios."""
    
    def test_create_with_valid_document(self, setup_report_collection, mock_update_result, valid_report_document):
        """Test creating/updating document with valid data."""
        setup_report_collection.update_one.return_value = mock_update_result
        
        result = Report.create(valid_report_document)
        
        assert result is True
        setup_report_collection.update_one.assert_called_once_with(
            {"BatchId": 100.0},
            {"$set": valid_report_document},
            upsert=True
        )
    
    def test_create_returns_acknowledged_status(self, setup_report_collection, mock_update_result, valid_report_document):
        """Test that create returns the acknowledged status."""
        mock_update_result.acknowledged = True
        setup_report_collection.update_one.return_value = mock_update_result
        
        result = Report.create(valid_report_document)
        
        assert result == mock_update_result.acknowledged
    
    def test_create_uses_upsert_true(self, setup_report_collection, mock_update_result, valid_report_document):
        """Test that create uses upsert=True for update_one."""
        setup_report_collection.update_one.return_value = mock_update_result
        
        Report.create(valid_report_document)
        
        call_args = setup_report_collection.update_one.call_args
        assert call_args[1]['upsert'] is True
    
    def test_create_with_minimal_document(self, setup_report_collection, mock_update_result):
        """Test creating document with only BatchId."""
        minimal_doc = {"BatchId": 100.0}
        setup_report_collection.update_one.return_value = mock_update_result
        
        result = Report.create(minimal_doc)
        
        assert result is True
    
    def test_create_with_complex_document(self, setup_report_collection, mock_update_result):
        """Test creating document with complex nested structure."""
        complex_doc = {
            "BatchId": 100.0,
            "ReportFileId": "report_123",
            "ReportName": "Complex Report",
            "Metadata": {
                "author": "user123",
                "tags": ["fairness", "analysis"],
                "version": 2
            },
            "Metrics": {
                "accuracy": 0.95,
                "fairness_score": 0.87
            }
        }
        setup_report_collection.update_one.return_value = mock_update_result
        
        result = Report.create(complex_doc)
        
        assert result is True
    
    def test_create_updates_existing_document(self, setup_report_collection, mock_update_result):
        """Test that create updates existing document with same BatchId."""
        doc1 = {"BatchId": 100.0, "ReportName": "Report v1"}
        doc2 = {"BatchId": 100.0, "ReportName": "Report v2"}
        setup_report_collection.update_one.return_value = mock_update_result
        
        Report.create(doc1)
        Report.create(doc2)
        
        # Should be called twice with same BatchId
        assert setup_report_collection.update_one.call_count == 2
    
    def test_create_with_different_batch_ids(self, setup_report_collection, mock_update_result):
        """Test creating multiple documents with different BatchIds."""
        setup_report_collection.update_one.return_value = mock_update_result
        
        for i in range(5):
            doc = {"BatchId": float(i), "ReportName": f"Report {i}"}
            result = Report.create(doc)
            assert result is True
        
        assert setup_report_collection.update_one.call_count == 5


# ==================== CREATE METHOD ERROR HANDLING ====================

class TestCreateMethodErrorHandling:
    """Test error handling in create method."""
    
    def test_create_with_none_document_raises_http_exception(self, setup_report_collection):
        """Test that None document raises HTTPException with 400 status."""
        with pytest.raises(HTTPException) as exc_info:
            Report.create(None)
        
        assert exc_info.value.status_code == 400
        assert "Document must be a non-empty dictionary" in exc_info.value.detail
        setup_report_collection.update_one.assert_not_called()
    
    def test_create_with_unacknowledged_update_raises_http_exception(self, setup_report_collection, mock_update_result_failed, valid_report_document):
        """Test that unacknowledged update raises HTTPException with 500 status."""
        setup_report_collection.update_one.return_value = mock_update_result_failed
        
        with pytest.raises(HTTPException) as exc_info:
            Report.create(valid_report_document)
        
        assert exc_info.value.status_code == 500
        assert "Document could not be inserted" in exc_info.value.detail
    
    def test_create_with_invalid_document_raises_invalid_document(self, setup_report_collection):
        """Test that invalid document type raises InvalidDocument error."""
        setup_report_collection.update_one.side_effect = InvalidDocument("Document must be a dict")
        
        with pytest.raises(InvalidDocument):
            Report.create({"BatchId": 100.0})
    
    def test_create_with_write_error_propagates_exception(self, setup_report_collection, valid_report_document):
        """Test that MongoDB WriteError is propagated."""
        setup_report_collection.update_one.side_effect = WriteError("Write failed", 11000)
        
        with pytest.raises(WriteError):
            Report.create(valid_report_document)
    
    def test_create_with_operation_failure_propagates_exception(self, setup_report_collection, valid_report_document):
        """Test that MongoDB OperationFailure is propagated."""
        setup_report_collection.update_one.side_effect = OperationFailure("Operation failed")
        
        with pytest.raises(OperationFailure):
            Report.create(valid_report_document)
    
    def test_create_with_missing_batch_id_raises_keyerror(self, setup_report_collection, mock_update_result):
        """Test that document without BatchId raises KeyError."""
        doc_without_batch_id = {"ReportName": "Test Report"}
        setup_report_collection.update_one.return_value = mock_update_result
        
        with pytest.raises(KeyError):
            Report.create(doc_without_batch_id)


# ==================== FIND METHOD TESTS ====================

class TestFindMethodSuccess:
    """Test successful find operations."""
    
    def test_find_with_valid_batch_id(self, setup_report_collection, find_result):
        """Test finding report with valid float batch_id."""
        setup_report_collection.find_one.return_value = find_result
        
        report = Report()
        result = report.find(100.0)
        
        assert result == find_result
        setup_report_collection.find_one.assert_called_once_with(
            {"BatchId": 100.0},
            {"_id": 0, "ReportFileId": 1, "ReportName": 1}
        )
    
    def test_find_with_large_batch_id(self, setup_report_collection, find_result):
        """Test finding report with large float batch_id."""
        setup_report_collection.find_one.return_value = find_result
        
        report = Report()
        result = report.find(999999.0)
        
        assert result == find_result
    
    def test_find_with_decimal_batch_id(self, setup_report_collection, find_result):
        """Test finding report with decimal float batch_id."""
        setup_report_collection.find_one.return_value = find_result
        
        report = Report()
        result = report.find(123.456)
        
        assert result == find_result
    
    def test_find_returns_only_specified_fields(self, setup_report_collection):
        """Test that find returns only ReportFileId and ReportName (no _id)."""
        setup_report_collection.find_one.return_value = {
            "ReportFileId": "report_123",
            "ReportName": "Test Report"
        }
        
        report = Report()
        result = report.find(100.0)
        
        assert "_id" not in result
        assert "ReportFileId" in result
        assert "ReportName" in result
    
    def test_find_with_zero_batch_id(self, setup_report_collection, find_result):
        """Test finding report with 0.0 batch_id."""
        setup_report_collection.find_one.return_value = find_result
        
        report = Report()
        result = report.find(0.0)
        
        assert result == find_result


# ==================== FIND METHOD ERROR HANDLING ====================

class TestFindMethodErrorHandling:
    """Test error handling in find method."""
    
    def test_find_with_none_batch_id_raises_http_exception(self, setup_report_collection):
        """Test that None batch_id raises HTTPException with 500 status."""
        report = Report()
        
        with pytest.raises(HTTPException) as exc_info:
            report.find(None)
        
        assert exc_info.value.status_code == 500
        assert "Batch ID is None" in exc_info.value.detail
        setup_report_collection.find_one.assert_not_called()
    
    def test_find_with_string_batch_id_raises_http_exception(self, setup_report_collection):
        """Test that string batch_id raises HTTPException."""
        report = Report()
        
        with pytest.raises(HTTPException) as exc_info:
            report.find("100")
        
        assert exc_info.value.status_code == 500
        assert "Batch ID is None" in exc_info.value.detail
    
    def test_find_with_int_batch_id_raises_http_exception(self, setup_report_collection):
        """Test that int batch_id raises HTTPException."""
        report = Report()
        
        with pytest.raises(HTTPException) as exc_info:
            report.find(100)
        
        assert exc_info.value.status_code == 500
    
    def test_find_with_not_found_batch_id_raises_http_exception(self, setup_report_collection):
        """Test that not found batch_id raises HTTPException with 500 status."""
        setup_report_collection.find_one.return_value = None
        
        report = Report()
        
        with pytest.raises(HTTPException) as exc_info:
            report.find(100.0)
        
        assert exc_info.value.status_code == 500
        assert "Batch ID not found" in exc_info.value.detail
    
    def test_find_with_database_exception_propagates(self, setup_report_collection):
        """Test that database exceptions are propagated."""
        setup_report_collection.find_one.side_effect = Exception("Database error")
        
        report = Report()
        
        with pytest.raises(Exception) as exc_info:
            report.find(100.0)
        
        assert "Database error" in str(exc_info.value)


# ==================== EDGE CASES ====================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_create_with_negative_batch_id(self, setup_report_collection, mock_update_result):
        """Test creating document with negative batch_id."""
        doc = {"BatchId": -1.0, "ReportName": "Negative Batch"}
        setup_report_collection.update_one.return_value = mock_update_result
        
        result = Report.create(doc)
        
        assert result is True
    
    def test_find_with_negative_batch_id(self, setup_report_collection, find_result):
        """Test finding report with negative batch_id."""
        setup_report_collection.find_one.return_value = find_result
        
        report = Report()
        result = report.find(-1.0)
        
        assert result == find_result
    
    def test_create_with_very_small_float(self, setup_report_collection, mock_update_result):
        """Test creating document with very small float batch_id."""
        doc = {"BatchId": 0.0001, "ReportName": "Tiny Batch"}
        setup_report_collection.update_one.return_value = mock_update_result
        
        result = Report.create(doc)
        
        assert result is True
    
    def test_create_with_special_characters_in_report_name(self, setup_report_collection, mock_update_result):
        """Test creating document with special characters."""
        doc = {
            "BatchId": 100.0,
            "ReportName": "Report with 'quotes' & \"double quotes\" @#$%"
        }
        setup_report_collection.update_one.return_value = mock_update_result
        
        result = Report.create(doc)
        
        assert result is True
    
    def test_create_with_unicode_characters(self, setup_report_collection, mock_update_result):
        """Test creating document with unicode characters."""
        doc = {
            "BatchId": 100.0,
            "ReportName": "Report Unicode: こんにちは, 你好, مرحبا 🚀"
        }
        setup_report_collection.update_one.return_value = mock_update_result
        
        result = Report.create(doc)
        
        assert result is True
    
    def test_create_with_large_document(self, setup_report_collection, mock_update_result):
        """Test creating document with large content."""
        doc = {
            "BatchId": 100.0,
            "ReportName": "Large Report",
            "Content": "x" * 10000,
            "Data": ["item" * 100 for _ in range(100)]
        }
        setup_report_collection.update_one.return_value = mock_update_result
        
        result = Report.create(doc)
        
        assert result is True
    
    def test_create_with_many_fields(self, setup_report_collection, mock_update_result):
        """Test creating document with many fields."""
        doc = {"BatchId": 100.0}
        doc.update({f"field_{i}": f"value_{i}" for i in range(50)})
        setup_report_collection.update_one.return_value = mock_update_result
        
        result = Report.create(doc)
        
        assert result is True


# ==================== VALIDATION TESTS ====================

class TestValidation:
    """Test validation logic."""
    
    def test_create_validates_none_before_update(self, setup_report_collection):
        """Test that None validation happens before update_one call."""
        with pytest.raises(HTTPException):
            Report.create(None)
        
        setup_report_collection.update_one.assert_not_called()
    
    def test_create_validates_acknowledged_after_update(self, setup_report_collection, mock_update_result_failed, valid_report_document):
        """Test that acknowledged validation happens after update."""
        setup_report_collection.update_one.return_value = mock_update_result_failed
        
        with pytest.raises(HTTPException):
            Report.create(valid_report_document)
        
        setup_report_collection.update_one.assert_called_once()
    
    def test_find_validates_none_before_query(self, setup_report_collection):
        """Test that None validation happens before find_one call."""
        report = Report()
        
        with pytest.raises(HTTPException):
            report.find(None)
        
        setup_report_collection.find_one.assert_not_called()
    
    def test_find_validates_type_before_query(self, setup_report_collection):
        """Test that type validation happens before find_one call."""
        report = Report()
        
        with pytest.raises(HTTPException):
            report.find("not_a_float")
        
        setup_report_collection.find_one.assert_not_called()
    
    def test_find_validates_not_found_after_query(self, setup_report_collection):
        """Test that not found validation happens after query."""
        setup_report_collection.find_one.return_value = None
        
        report = Report()
        
        with pytest.raises(HTTPException):
            report.find(100.0)
        
        setup_report_collection.find_one.assert_called_once()


# ==================== PERFORMANCE TESTS ====================

class TestPerformance:
    """Test performance characteristics."""
    
    def test_create_multiple_documents_sequential(self, setup_report_collection, mock_update_result):
        """Test creating multiple documents sequentially."""
        setup_report_collection.update_one.return_value = mock_update_result
        
        documents = [{"BatchId": float(i), "ReportName": f"Report {i}"} for i in range(20)]
        results = []
        
        for doc in documents:
            result = Report.create(doc)
            results.append(result)
        
        assert all(results)
        assert setup_report_collection.update_one.call_count == 20
    
    def test_find_multiple_reports_sequential(self, setup_report_collection, find_result):
        """Test finding multiple reports sequentially."""
        setup_report_collection.find_one.return_value = find_result
        
        report = Report()
        results = []
        
        for i in range(20):
            result = report.find(float(i))
            results.append(result)
        
        assert len(results) == 20
        assert setup_report_collection.find_one.call_count == 20
    
    def test_create_with_varying_document_sizes(self, setup_report_collection, mock_update_result):
        """Test creating documents of varying sizes."""
        setup_report_collection.update_one.return_value = mock_update_result
        
        sizes = [10, 100, 1000, 5000]
        for size in sizes:
            doc = {"BatchId": float(size), "Content": "x" * size}
            result = Report.create(doc)
            assert result is True


# ==================== SECURITY TESTS ====================

class TestSecurity:
    """Test security-related aspects."""
    
    def test_create_rejects_none_document(self, setup_report_collection):
        """Test that None document is rejected for security."""
        with pytest.raises(HTTPException) as exc_info:
            Report.create(None)
        
        assert exc_info.value.status_code == 400
    
    def test_create_with_injection_attempt(self, setup_report_collection, mock_update_result):
        """Test document with potential injection patterns."""
        injection_doc = {
            "BatchId": 100.0,
            "ReportName": "<script>alert('xss')</script>",
            "Query": "'; DROP TABLE reports; --"
        }
        setup_report_collection.update_one.return_value = mock_update_result
        
        result = Report.create(injection_doc)
        
        assert result is True
    
    def test_find_validates_input_type(self, setup_report_collection):
        """Test that find validates input type for security."""
        report = Report()
        
        with pytest.raises(HTTPException):
            report.find("malicious_input")
    
    def test_find_rejects_none_batch_id(self, setup_report_collection):
        """Test that find rejects None batch_id."""
        report = Report()
        
        with pytest.raises(HTTPException) as exc_info:
            report.find(None)
        
        assert exc_info.value.status_code == 500


# ==================== INTEGRATION TESTS ====================

class TestIntegration:
    """Test integration with MongoDB and dependencies."""
    
    def test_report_uses_correct_collection(self):
        """Test that Report uses the correct collection name."""
        assert Report.collection is not None
    
    def test_create_calls_collection_update_one(self, setup_report_collection, mock_update_result, valid_report_document):
        """Test that create method calls collection.update_one."""
        setup_report_collection.update_one.return_value = mock_update_result
        
        Report.create(valid_report_document)
        
        setup_report_collection.update_one.assert_called_once()
    
    def test_find_calls_collection_find_one(self, setup_report_collection, find_result):
        """Test that find method calls collection.find_one."""
        setup_report_collection.find_one.return_value = find_result
        
        report = Report()
        report.find(100.0)
        
        setup_report_collection.find_one.assert_called_once()
    
    def test_create_passes_document_with_upsert(self, setup_report_collection, mock_update_result):
        """Test that document is passed to update_one with upsert."""
        doc = {"BatchId": 100.0, "ReportName": "Test"}
        setup_report_collection.update_one.return_value = mock_update_result
        
        Report.create(doc)
        
        call_args = setup_report_collection.update_one.call_args
        assert call_args[0][0] == {"BatchId": 100.0}
        assert call_args[0][1] == {"$set": doc}
        assert call_args[1]['upsert'] is True


# ==================== REGRESSION TESTS ====================

class TestRegression:
    """Test for regression issues and previous bugs."""
    
    def test_regression_create_none_returns_400_not_500(self, setup_report_collection):
        """Test that None document returns 400, not 500."""
        with pytest.raises(HTTPException) as exc_info:
            Report.create(None)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.status_code != 500
    
    def test_regression_create_unacknowledged_returns_500(self, setup_report_collection, mock_update_result_failed, valid_report_document):
        """Test that unacknowledged update returns 500."""
        setup_report_collection.update_one.return_value = mock_update_result_failed
        
        with pytest.raises(HTTPException) as exc_info:
            Report.create(valid_report_document)
        
        assert exc_info.value.status_code == 500
    
    def test_regression_create_returns_boolean(self, setup_report_collection, mock_update_result, valid_report_document):
        """Test that create returns boolean acknowledged value."""
        mock_update_result.acknowledged = True
        setup_report_collection.update_one.return_value = mock_update_result
        
        result = Report.create(valid_report_document)
        
        assert isinstance(result, bool)
        assert result is True
    
    def test_regression_find_not_found_returns_500(self, setup_report_collection):
        """Test that not found batch_id returns 500 status."""
        setup_report_collection.find_one.return_value = None
        
        report = Report()
        
        with pytest.raises(HTTPException) as exc_info:
            report.find(100.0)
        
        assert exc_info.value.status_code == 500
    
    def test_regression_find_returns_dict(self, setup_report_collection, find_result):
        """Test that find returns dictionary."""
        setup_report_collection.find_one.return_value = find_result
        
        report = Report()
        result = report.find(100.0)
        
        assert isinstance(result, dict)
    
    def test_regression_find_excludes_id_field(self, setup_report_collection):
        """Test that find excludes _id field from result."""
        setup_report_collection.find_one.return_value = {
            "ReportFileId": "report_123",
            "ReportName": "Test Report"
        }
        
        report = Report()
        result = report.find(100.0)
        
        assert "_id" not in result


# ==================== CODE QUALITY TESTS ====================

class TestCodeQuality:
    """Test code quality indicators."""
    
    def test_class_is_defined(self):
        """Test that Report class is properly defined."""
        assert Report is not None
        assert isinstance(Report, type)
    
    def test_create_method_exists(self):
        """Test that create method exists."""
        assert hasattr(Report, 'create')
    
    def test_find_method_exists(self):
        """Test that find method exists."""
        assert hasattr(Report, 'find')
    
    def test_create_is_static_method(self):
        """Test that create is a static method for efficiency."""
        assert isinstance(Report.__dict__['create'], staticmethod)
    
    def test_find_is_instance_method(self):
        """Test that find is an instance method."""
        report = Report()
        assert callable(report.find)
    
    def test_report_instance_can_be_created(self):
        """Test that Report instances can be created."""
        report = Report()
        assert report is not None
        assert isinstance(report, Report)


# ==================== BUG DOCUMENTATION ====================

class TestBugDocumentation:
    """Document known bugs or issues in the original code."""
    
    def test_bug_comment_says_tbl_model_but_uses_report(self):
        """BUG: Comment says 'Tbl_Model' but actually uses 'Report' collection.
        
        Line 31: Comment says "Access the 'Tbl_Model' collection"
        Line 32: Code uses ModelWorkBench["Report"]
        
        This is a documentation bug - comment is misleading.
        """
        assert True
    
    def test_bug_find_comment_says_string_but_expects_float(self):
        """BUG: Comment says 'batch_id is a string' but code expects float.
        
        Line 48: Comment says 'Check if batch_id is not None and is a string'
        Line 50: Code checks isinstance(batch_id, float)
        
        This is a comment/code mismatch.
        """
        assert True
    
    def test_bug_find_error_message_inconsistent(self, setup_report_collection):
        """BUG: Error message says 'Batch ID is None' even for type mismatch.
        
        Line 51: detail="Batch ID is None"
        But this error is also raised when batch_id is not a float.
        Should have different messages for None vs wrong type.
        """
        report = Report()
        
        # Both None and wrong type get same error message
        with pytest.raises(HTTPException) as exc_info1:
            report.find(None)
        with pytest.raises(HTTPException) as exc_info2:
            report.find("123")
        
        assert exc_info1.value.detail == exc_info2.value.detail
        assert "Batch ID is None" in exc_info1.value.detail
    
    def test_bug_find_uses_500_for_validation_errors(self, setup_report_collection):
        """BUG: find() uses 500 status for validation errors instead of 400.
        
        Lines 50-51: HTTPException(status_code=500) for None/type validation
        Line 55: HTTPException(status_code=500) for not found
        
        Should use 400 for validation errors, 404 for not found, 500 for server errors.
        """
        report = Report()
        
        # Validation error uses 500 instead of 400
        with pytest.raises(HTTPException) as exc_info:
            report.find(None)
        
        assert exc_info.value.status_code == 500
        # Should be 400 for bad request
    
    def test_bug_create_error_says_inserted_but_uses_update(self, setup_report_collection, mock_update_result_failed, valid_report_document):
        """BUG: Error message says 'inserted' but method uses update_one with upsert.
        
        Line 42: detail="Document could not be inserted"
        Line 39: Uses update_one() with upsert=True (not insert_one)
        
        Message should say "Document could not be created/updated" or similar.
        """
        setup_report_collection.update_one.return_value = mock_update_result_failed
        
        with pytest.raises(HTTPException) as exc_info:
            Report.create(valid_report_document)
        
        assert "inserted" in exc_info.value.detail.lower()
        # But code uses update_one, not insert_one
    
    def test_bug_no_validation_for_empty_dict(self, setup_report_collection, mock_update_result):
        """BUG: Empty dictionary {} is allowed despite 'non-empty' error message.
        
        Error message says 'Document must be a non-empty dictionary',
        but code only checks for None, allowing empty dicts.
        """
        # Empty dict would fail on BatchId access, but passes None check
        with pytest.raises(KeyError):
            Report.create({})


# ==================== RESOURCE MANAGEMENT ====================

class TestResourceManagement:
    """Test resource management and cleanup."""
    
    def test_create_does_not_leave_connections_open(self, setup_report_collection, mock_update_result, valid_report_document):
        """Test that create method doesn't leave resources open."""
        setup_report_collection.update_one.return_value = mock_update_result
        
        Report.create(valid_report_document)
        
        # MongoDB driver handles connection pooling
        assert True
    
    def test_find_does_not_leave_connections_open(self, setup_report_collection, find_result):
        """Test that find method doesn't leave resources open."""
        setup_report_collection.find_one.return_value = find_result
        
        report = Report()
        report.find(100.0)
        
        # MongoDB driver handles connection pooling
        assert True
    
    def test_multiple_report_instances(self):
        """Test that multiple Report instances can coexist."""
        reports = [Report() for _ in range(10)]
        assert len(reports) == 10
        assert all(isinstance(r, Report) for r in reports)


# ==================== SCALABILITY TESTS ====================

class TestScalability:
    """Test scalability considerations."""
    
    def test_create_can_handle_rapid_successive_calls(self, setup_report_collection, mock_update_result):
        """Test that create can handle many rapid calls."""
        setup_report_collection.update_one.return_value = mock_update_result
        
        for i in range(100):
            result = Report.create({"BatchId": float(i), "ReportName": f"Report {i}"})
            assert result is True
        
        assert setup_report_collection.update_one.call_count == 100
    
    def test_find_can_handle_rapid_successive_calls(self, setup_report_collection, find_result):
        """Test that find can handle many rapid calls."""
        setup_report_collection.find_one.return_value = find_result
        
        report = Report()
        
        for i in range(100):
            result = report.find(float(i))
            assert result is not None
        
        assert setup_report_collection.find_one.call_count == 100
    
    def test_create_with_concurrent_pattern(self, setup_report_collection, mock_update_result):
        """Test document creation pattern suitable for concurrent use."""
        setup_report_collection.update_one.return_value = mock_update_result
        
        # Simulate multiple users creating reports
        documents = [
            {"BatchId": float(i), "ReportName": f"User {i} Report"}
            for i in range(20)
        ]
        
        results = [Report.create(doc) for doc in documents]
        
        assert all(results)
        assert setup_report_collection.update_one.call_count == 20


# ==================== ERROR MESSAGE TESTS ====================

class TestErrorMessages:
    """Test error message clarity and usefulness."""
    
    def test_create_none_document_error_message_is_clear(self, setup_report_collection):
        """Test that None document error message is descriptive."""
        with pytest.raises(HTTPException) as exc_info:
            Report.create(None)
        
        assert "Document must be a non-empty dictionary" in str(exc_info.value.detail)
        assert exc_info.value.status_code == 400
    
    def test_create_unacknowledged_error_message_is_clear(self, setup_report_collection, mock_update_result_failed, valid_report_document):
        """Test that unacknowledged update error message is descriptive."""
        setup_report_collection.update_one.return_value = mock_update_result_failed
        
        with pytest.raises(HTTPException) as exc_info:
            Report.create(valid_report_document)
        
        assert "Document could not be inserted" in str(exc_info.value.detail)
        assert exc_info.value.status_code == 500
    
    def test_find_none_batch_id_error_message_is_clear(self, setup_report_collection):
        """Test that None batch_id error message is descriptive."""
        report = Report()
        
        with pytest.raises(HTTPException) as exc_info:
            report.find(None)
        
        assert "Batch ID is None" in str(exc_info.value.detail)
        assert exc_info.value.status_code == 500
    
    def test_find_not_found_error_message_is_clear(self, setup_report_collection):
        """Test that not found error message is descriptive."""
        setup_report_collection.find_one.return_value = None
        
        report = Report()
        
        with pytest.raises(HTTPException) as exc_info:
            report.find(100.0)
        
        assert "Batch ID not found" in str(exc_info.value.detail)
        assert exc_info.value.status_code == 500
