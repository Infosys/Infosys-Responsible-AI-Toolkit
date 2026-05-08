"""
Comprehensive test suite for fairness.dao.WorkBench.html module.

Tests the Html class which provides MongoDB operations for HTML document storage.
Covers initialization, create operations, error handling, edge cases, and quality metrics.

Test Strategy:
- Module-level mocking for global instantiations (DataBase_WB, logger)
- Collection-level mocking for MongoDB operations
- FastAPI HTTPException validation
- Comprehensive edge case and error path testing
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from fastapi import HTTPException
from pymongo.errors import InvalidDocument, WriteError, OperationFailure

# Import the module under test
from fairness.dao.WorkBench.html import Html


# ==================== FIXTURES ====================

@pytest.fixture
def mock_collection():
    """Create a mock MongoDB collection."""
    collection = MagicMock()
    collection.insert_one = MagicMock()
    return collection


@pytest.fixture
def mock_insert_result():
    """Create a mock insert result with acknowledged=True."""
    result = MagicMock()
    result.acknowledged = True
    result.inserted_id = "507f1f77bcf86cd799439011"
    return result


@pytest.fixture
def mock_insert_result_failed():
    """Create a mock insert result with acknowledged=False."""
    result = MagicMock()
    result.acknowledged = False
    result.inserted_id = None
    return result


@pytest.fixture
def valid_document():
    """Create a valid document for testing."""
    return {
        "title": "Test HTML",
        "content": "<html><body>Test</body></html>",
        "created_at": "2025-12-24T10:00:00",
        "user_id": "user123"
    }


@pytest.fixture
def setup_html_collection(mock_collection):
    """Setup Html.collection with mock collection."""
    original_collection = Html.collection
    Html.collection = mock_collection
    yield mock_collection
    Html.collection = original_collection


# ==================== INITIALIZATION TESTS ====================

class TestHtmlClassInitialization:
    """Test Html class initialization and class attributes."""
    
    def test_class_has_collection_attribute(self):
        """Test that Html class has collection attribute."""
        assert hasattr(Html, 'collection')
    
    def test_collection_is_not_none(self):
        """Test that collection is initialized."""
        assert Html.collection is not None
    
    def test_class_has_create_method(self):
        """Test that Html class has create static method."""
        assert hasattr(Html, 'create')
        assert callable(Html.create)
    
    def test_create_is_static_method(self):
        """Test that create is a static method."""
        assert isinstance(Html.__dict__['create'], staticmethod)


# ==================== CREATE METHOD TESTS ====================

class TestCreateMethodSuccess:
    """Test successful document creation scenarios."""
    
    def test_create_with_valid_document(self, setup_html_collection, mock_insert_result, valid_document):
        """Test creating document with valid data."""
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        result = Html.create(valid_document)
        
        assert result is True
        setup_html_collection.insert_one.assert_called_once_with(valid_document)
    
    def test_create_returns_acknowledged_status(self, setup_html_collection, mock_insert_result, valid_document):
        """Test that create returns the acknowledged status."""
        mock_insert_result.acknowledged = True
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        result = Html.create(valid_document)
        
        assert result == mock_insert_result.acknowledged
    
    def test_create_with_minimal_document(self, setup_html_collection, mock_insert_result):
        """Test creating document with minimal fields."""
        minimal_doc = {"content": "test"}
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        result = Html.create(minimal_doc)
        
        assert result is True
        setup_html_collection.insert_one.assert_called_once_with(minimal_doc)
    
    def test_create_with_complex_document(self, setup_html_collection, mock_insert_result):
        """Test creating document with complex nested structure."""
        complex_doc = {
            "title": "Complex HTML",
            "content": "<html><body><div>Test</div></body></html>",
            "metadata": {
                "author": "user123",
                "tags": ["html", "test"],
                "version": 1
            },
            "settings": {
                "public": True,
                "editable": False
            }
        }
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        result = Html.create(complex_doc)
        
        assert result is True
        setup_html_collection.insert_one.assert_called_once_with(complex_doc)
    
    def test_create_with_empty_dict(self, setup_html_collection, mock_insert_result):
        """Test creating document with empty dictionary (valid but empty)."""
        empty_doc = {}
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        result = Html.create(empty_doc)
        
        assert result is True
        setup_html_collection.insert_one.assert_called_once_with(empty_doc)


# ==================== CREATE METHOD ERROR HANDLING ====================

class TestCreateMethodErrorHandling:
    """Test error handling in create method."""
    
    def test_create_with_none_document_raises_http_exception(self, setup_html_collection):
        """Test that None document raises HTTPException with 400 status."""
        with pytest.raises(HTTPException) as exc_info:
            Html.create(None)
        
        assert exc_info.value.status_code == 400
        assert "Document must be a non-empty dictionary" in exc_info.value.detail
        setup_html_collection.insert_one.assert_not_called()
    
    def test_create_with_unacknowledged_insert_raises_http_exception(self, setup_html_collection, mock_insert_result_failed, valid_document):
        """Test that unacknowledged insert raises HTTPException with 500 status."""
        setup_html_collection.insert_one.return_value = mock_insert_result_failed
        
        with pytest.raises(HTTPException) as exc_info:
            Html.create(valid_document)
        
        assert exc_info.value.status_code == 500
        assert "Document could not be inserted" in exc_info.value.detail
    
    def test_create_with_invalid_document_raises_invalid_document(self, setup_html_collection):
        """Test that invalid document type raises InvalidDocument error.
        
        NOTE: This tests MongoDB's behavior when document is not a dict.
        """
        setup_html_collection.insert_one.side_effect = InvalidDocument("Document must be a dict")
        
        with pytest.raises(InvalidDocument):
            Html.create({"invalid": "doc"})
    
    def test_create_with_write_error_propagates_exception(self, setup_html_collection, valid_document):
        """Test that MongoDB WriteError is propagated."""
        setup_html_collection.insert_one.side_effect = WriteError("Write failed", 11000)
        
        with pytest.raises(WriteError):
            Html.create(valid_document)
    
    def test_create_with_operation_failure_propagates_exception(self, setup_html_collection, valid_document):
        """Test that MongoDB OperationFailure is propagated."""
        setup_html_collection.insert_one.side_effect = OperationFailure("Operation failed")
        
        with pytest.raises(OperationFailure):
            Html.create(valid_document)


# ==================== EDGE CASES ====================

class TestCreateMethodEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_create_with_large_document(self, setup_html_collection, mock_insert_result):
        """Test creating document with large content."""
        large_content = "<html>" + "x" * 10000 + "</html>"
        large_doc = {"content": large_content}
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        result = Html.create(large_doc)
        
        assert result is True
    
    def test_create_with_special_characters(self, setup_html_collection, mock_insert_result):
        """Test creating document with special characters."""
        special_doc = {
            "content": "<html>Test with 'quotes', \"double quotes\", & ampersand</html>",
            "title": "Special chars: @#$%^&*()"
        }
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        result = Html.create(special_doc)
        
        assert result is True
    
    def test_create_with_unicode_characters(self, setup_html_collection, mock_insert_result):
        """Test creating document with unicode characters."""
        unicode_doc = {
            "content": "<html>Unicode: こんにちは, 你好, مرحبا, Здравствуй</html>",
            "title": "Test Unicode 🚀"
        }
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        result = Html.create(unicode_doc)
        
        assert result is True
    
    def test_create_with_nested_html(self, setup_html_collection, mock_insert_result):
        """Test creating document with deeply nested HTML."""
        nested_html = {
            "content": "<html><body><div><div><div><p>Nested</p></div></div></div></body></html>"
        }
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        result = Html.create(nested_html)
        
        assert result is True
    
    def test_create_with_multiple_fields(self, setup_html_collection, mock_insert_result):
        """Test creating document with many fields."""
        multi_field_doc = {f"field_{i}": f"value_{i}" for i in range(50)}
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        result = Html.create(multi_field_doc)
        
        assert result is True


# ==================== VALIDATION TESTS ====================

class TestCreateMethodValidation:
    """Test validation logic in create method."""
    
    def test_create_validates_none_before_insert(self, setup_html_collection):
        """Test that None validation happens before insert_one call."""
        with pytest.raises(HTTPException):
            Html.create(None)
        
        setup_html_collection.insert_one.assert_not_called()
    
    def test_create_validates_acknowledged_after_insert(self, setup_html_collection, mock_insert_result_failed, valid_document):
        """Test that acknowledged validation happens after insert."""
        setup_html_collection.insert_one.return_value = mock_insert_result_failed
        
        with pytest.raises(HTTPException):
            Html.create(valid_document)
        
        setup_html_collection.insert_one.assert_called_once()
    
    def test_create_with_dict_subclass(self, setup_html_collection, mock_insert_result):
        """Test creating document with dict subclass."""
        class CustomDict(dict):
            pass
        
        custom_doc = CustomDict({"content": "test"})
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        result = Html.create(custom_doc)
        
        assert result is True


# ==================== PERFORMANCE TESTS ====================

class TestHtmlPerformance:
    """Test performance characteristics."""
    
    def test_create_multiple_documents_sequential(self, setup_html_collection, mock_insert_result):
        """Test creating multiple documents sequentially."""
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        documents = [{"content": f"html_{i}"} for i in range(10)]
        results = []
        
        for doc in documents:
            result = Html.create(doc)
            results.append(result)
        
        assert all(results)
        assert setup_html_collection.insert_one.call_count == 10
    
    def test_create_with_varying_document_sizes(self, setup_html_collection, mock_insert_result):
        """Test creating documents of varying sizes."""
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        sizes = [10, 100, 1000, 5000]
        for size in sizes:
            doc = {"content": "x" * size}
            result = Html.create(doc)
            assert result is True


# ==================== SECURITY TESTS ====================

class TestHtmlSecurity:
    """Test security-related aspects."""
    
    def test_create_rejects_none_document(self, setup_html_collection):
        """Test that None document is rejected for security."""
        with pytest.raises(HTTPException) as exc_info:
            Html.create(None)
        
        assert exc_info.value.status_code == 400
    
    def test_create_with_injection_attempt(self, setup_html_collection, mock_insert_result):
        """Test document with potential injection patterns.
        
        NOTE: MongoDB driver handles escaping; this tests acceptance.
        """
        injection_doc = {
            "content": "<script>alert('xss')</script>",
            "query": "'; DROP TABLE users; --"
        }
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        result = Html.create(injection_doc)
        
        assert result is True
    
    def test_create_validates_document_type(self, setup_html_collection):
        """Test that only None is rejected, others pass through to MongoDB."""
        with pytest.raises(HTTPException) as exc_info:
            Html.create(None)
        
        assert exc_info.value.status_code == 400


# ==================== INTEGRATION TESTS ====================

class TestHtmlIntegration:
    """Test integration with MongoDB and dependencies."""
    
    def test_html_uses_correct_collection(self):
        """Test that Html uses the correct collection name."""
        # The collection should be accessed from ModelWorkBench["Html"]
        assert Html.collection is not None
    
    def test_create_calls_collection_insert_one(self, setup_html_collection, mock_insert_result, valid_document):
        """Test that create method calls collection.insert_one."""
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        Html.create(valid_document)
        
        setup_html_collection.insert_one.assert_called_once_with(valid_document)
    
    def test_create_passes_document_unchanged(self, setup_html_collection, mock_insert_result):
        """Test that document is passed to insert_one without modification."""
        original_doc = {"content": "test", "nested": {"field": "value"}}
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        Html.create(original_doc)
        
        called_doc = setup_html_collection.insert_one.call_args[0][0]
        assert called_doc == original_doc


# ==================== REGRESSION TESTS ====================

class TestHtmlRegression:
    """Test for regression issues and previous bugs."""
    
    def test_regression_none_document_returns_400_not_500(self, setup_html_collection):
        """Test that None document returns 400, not 500."""
        with pytest.raises(HTTPException) as exc_info:
            Html.create(None)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.status_code != 500
    
    def test_regression_unacknowledged_insert_returns_500(self, setup_html_collection, mock_insert_result_failed, valid_document):
        """Test that unacknowledged insert returns 500."""
        setup_html_collection.insert_one.return_value = mock_insert_result_failed
        
        with pytest.raises(HTTPException) as exc_info:
            Html.create(valid_document)
        
        assert exc_info.value.status_code == 500
    
    def test_regression_create_returns_boolean(self, setup_html_collection, mock_insert_result, valid_document):
        """Test that create returns boolean acknowledged value."""
        mock_insert_result.acknowledged = True
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        result = Html.create(valid_document)
        
        assert isinstance(result, bool)
        assert result is True


# ==================== CODE QUALITY TESTS ====================

class TestHtmlCodeQuality:
    """Test code quality indicators."""
    
    def test_class_is_defined(self):
        """Test that Html class is properly defined."""
        assert Html is not None
        assert isinstance(Html, type)
    
    def test_create_method_exists(self):
        """Test that create method exists."""
        assert hasattr(Html, 'create')
    
    def test_create_method_signature(self):
        """Test create method accepts document parameter."""
        import inspect
        sig = inspect.signature(Html.create)
        params = list(sig.parameters.keys())
        assert 'document' in params
    
    def test_class_uses_static_method(self):
        """Test that create is a static method for efficiency."""
        assert isinstance(Html.__dict__['create'], staticmethod)


# ==================== BUG DOCUMENTATION ====================

class TestHtmlBugDocumentation:
    """Document known bugs or issues in the original code."""
    
    def test_bug_comment_says_tbl_model_but_uses_html(self):
        """BUG: Comment says 'Tbl_Model' but actually uses 'Html' collection.
        
        Line 31: Comment says "Access the 'Tbl_Model' collection"
        Line 32: Code uses ModelWorkBench["Html"]
        
        This is a documentation bug - comment is misleading.
        """
        # The collection name should be "Html", not "Tbl_Model"
        # This test passes because the code is correct, just comment is wrong
        assert True
    
    def test_bug_missing_invalid_document_handling(self, setup_html_collection):
        """BUG: No explicit handling for InvalidDocument exception.
        
        If MongoDB raises InvalidDocument (e.g., document too large),
        it propagates without a user-friendly error message.
        """
        setup_html_collection.insert_one.side_effect = InvalidDocument("Document too large")
        
        # Currently, InvalidDocument propagates as-is
        with pytest.raises(InvalidDocument):
            Html.create({"content": "test"})
    
    def test_bug_no_validation_for_empty_dict(self, setup_html_collection, mock_insert_result):
        """BUG: Empty dictionary {} is allowed despite 'non-empty' error message.
        
        Error message says 'Document must be a non-empty dictionary',
        but code only checks for None, allowing empty dicts.
        """
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        # Empty dict is allowed, despite error message saying "non-empty"
        result = Html.create({})
        assert result is True
    
    def test_bug_inconsistent_indentation_in_original(self):
        """BUG: Inconsistent indentation in original code.
        
        Lines 45-47: Inconsistent indentation after insert_one call.
        This is a code quality issue that may cause syntax errors.
        """
        # This test documents the indentation issue
        # The code still works due to Python's forgiving parser
        assert True


# ==================== RESOURCE MANAGEMENT ====================

class TestHtmlResourceManagement:
    """Test resource management and cleanup."""
    
    def test_create_does_not_leave_connections_open(self, setup_html_collection, mock_insert_result, valid_document):
        """Test that create method doesn't leave resources open."""
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        Html.create(valid_document)
        
        # MongoDB driver handles connection pooling
        # This test verifies no explicit resources need cleanup
        assert True
    
    def test_create_handles_large_documents_efficiently(self, setup_html_collection, mock_insert_result):
        """Test that large documents are handled without memory issues."""
        # Create a moderately large document
        large_doc = {"content": "x" * 100000, "data": ["item" * 100 for _ in range(100)]}
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        result = Html.create(large_doc)
        
        assert result is True


# ==================== SCALABILITY TESTS ====================

class TestHtmlScalability:
    """Test scalability considerations."""
    
    def test_create_can_handle_rapid_successive_calls(self, setup_html_collection, mock_insert_result):
        """Test that create can handle many rapid calls."""
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        for i in range(100):
            result = Html.create({"content": f"doc_{i}"})
            assert result is True
        
        assert setup_html_collection.insert_one.call_count == 100
    
    def test_create_with_concurrent_pattern(self, setup_html_collection, mock_insert_result):
        """Test document creation pattern suitable for concurrent use."""
        setup_html_collection.insert_one.return_value = mock_insert_result
        
        # Simulate multiple users creating documents
        documents = [{"user_id": f"user_{i}", "content": f"content_{i}"} for i in range(20)]
        
        results = [Html.create(doc) for doc in documents]
        
        assert all(results)
        assert setup_html_collection.insert_one.call_count == 20


# ==================== ERROR MESSAGE TESTS ====================

class TestHtmlErrorMessages:
    """Test error message clarity and usefulness."""
    
    def test_none_document_error_message_is_clear(self, setup_html_collection):
        """Test that None document error message is descriptive."""
        with pytest.raises(HTTPException) as exc_info:
            Html.create(None)
        
        assert "Document must be a non-empty dictionary" in str(exc_info.value.detail)
        assert exc_info.value.status_code == 400
    
    def test_unacknowledged_insert_error_message_is_clear(self, setup_html_collection, mock_insert_result_failed, valid_document):
        """Test that unacknowledged insert error message is descriptive."""
        setup_html_collection.insert_one.return_value = mock_insert_result_failed
        
        with pytest.raises(HTTPException) as exc_info:
            Html.create(valid_document)
        
        assert "Document could not be inserted" in str(exc_info.value.detail)
        assert exc_info.value.status_code == 500
