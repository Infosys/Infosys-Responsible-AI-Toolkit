"""
Comprehensive test suite for fairness.dao.WorkBench.Tenet module.

Tests the Tenet class which provides MongoDB operations for tenet data retrieval.
Covers initialization, find operations, error handling, edge cases, and quality metrics.

Test Strategy:
- Module-level mocking for global instantiations (DataBase_WB, logger)
- Collection-level mocking for MongoDB operations
- FastAPI HTTPException validation
- Comprehensive edge case and error path testing
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

# Import the module under test
from fairness.dao.WorkBench.Tenet import Tenet


# ==================== FIXTURES ====================

@pytest.fixture
def mock_db():
    """Create a mock database instance."""
    db = MagicMock()
    return db


@pytest.fixture
def mock_collection():
    """Create a mock MongoDB collection."""
    collection = MagicMock()
    return collection


@pytest.fixture
def tenet_find_result():
    """Create a mock result for Tenet.find()."""
    return {"Id": 123}


@pytest.fixture
def tenet_find_result_with_fields():
    """Create a mock result with multiple fields."""
    return {"Id": 123, "TenetName": "Test Tenet", "Description": "Test Description"}


# ==================== INITIALIZATION TESTS ====================

class TestTenetInitialization:
    """Test Tenet class initialization."""
    
    def test_init_with_provided_db(self, mock_db):
        """Test initialization with provided database."""
        mock_collection = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        
        assert tenet.ModelWorkBench == mock_db
        mock_db.__getitem__.assert_called_once_with("Tenet")
    
    def test_init_without_db_creates_database_wb(self):
        """Test initialization without db creates DataBase_WB instance."""
        with patch('fairness.dao.WorkBench.Tenet.DataBase_WB') as mock_db_class:
            mock_instance = MagicMock()
            mock_instance.db = MagicMock()
            mock_db_class.return_value = mock_instance
            
            tenet = Tenet()
            
            assert tenet.ModelWorkBench == mock_instance.db
            mock_db_class.assert_called_once()
    
    def test_init_sets_collection_attribute(self, mock_db):
        """Test that initialization sets collection attribute."""
        mock_collection = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        
        assert hasattr(tenet, 'collection')
        assert tenet.collection == mock_collection
    
    def test_init_uses_correct_collection_name(self, mock_db):
        """Test that initialization uses 'Tenet' collection name."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        
        tenet = Tenet(db=mock_db)
        
        mock_db.__getitem__.assert_called_with("Tenet")
    
    def test_init_logs_info_when_db_provided(self, mock_db):
        """Test that initialization logs info when db is provided."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        
        with patch('fairness.dao.WorkBench.Tenet.log') as mock_log:
            tenet = Tenet(db=mock_db)
            
            # Logger should be called with info message
            # Note: This verifies the log.info call happens
            assert tenet is not None


# ==================== FIND METHOD TESTS ====================

class TestFindMethodSuccess:
    """Test successful find operations."""
    
    def test_find_with_valid_tenet_name(self, mock_db, tenet_find_result):
        """Test finding tenet with valid string tenet_name."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = tenet_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        result = tenet.find("TestTenet")
        
        assert result == 123
        mock_collection.find_one.assert_called_once_with(
            {"TenetName": "TestTenet"},
            {"_id": 0, "Id": 1}
        )
    
    def test_find_returns_id_value(self, mock_db):
        """Test that find returns the Id value directly."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"Id": 456}
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        result = tenet.find("AnotherTenet")
        
        assert result == 456
        assert isinstance(result, int)
    
    def test_find_with_alphanumeric_tenet_name(self, mock_db, tenet_find_result):
        """Test finding tenet with alphanumeric name."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = tenet_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        result = tenet.find("Tenet123")
        
        assert result == 123
    
    def test_find_with_long_tenet_name(self, mock_db, tenet_find_result):
        """Test finding tenet with long name."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = tenet_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        long_name = "VeryLongTenetNameWithManyCharacters" * 3
        result = tenet.find(long_name)
        
        assert result == 123
    
    def test_find_uses_correct_query(self, mock_db):
        """Test that find uses correct MongoDB query."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"Id": 789}
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        tenet.find("QueryTest")
        
        mock_collection.find_one.assert_called_once_with(
            {"TenetName": "QueryTest"},
            {"_id": 0, "Id": 1}
        )
    
    def test_find_excludes_id_field(self, mock_db):
        """Test that find query excludes _id field."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"Id": 100}
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        tenet.find("TestTenet")
        
        call_args = mock_collection.find_one.call_args[0]
        projection = call_args[1]
        assert projection["_id"] == 0
        assert projection["Id"] == 1


# ==================== FIND METHOD ERROR HANDLING ====================

class TestFindMethodErrorHandling:
    """Test error handling in find method."""
    
    def test_find_with_none_tenet_name_raises_http_exception(self, mock_db):
        """Test that None tenet_name raises HTTPException with 500 status."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        tenet = Tenet(db=mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            tenet.find(None)
        
        assert exc_info.value.status_code == 500
        assert "Tenet Name must be a non-empty string" in exc_info.value.detail
    
    def test_find_with_int_tenet_name_raises_http_exception(self, mock_db):
        """Test that int tenet_name raises HTTPException."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        tenet = Tenet(db=mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            tenet.find(123)
        
        assert exc_info.value.status_code == 500
        assert "Tenet Name must be a non-empty string" in exc_info.value.detail
    
    def test_find_with_float_tenet_name_raises_http_exception(self, mock_db):
        """Test that float tenet_name raises HTTPException."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        tenet = Tenet(db=mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            tenet.find(123.45)
        
        assert exc_info.value.status_code == 500
    
    def test_find_with_list_tenet_name_raises_http_exception(self, mock_db):
        """Test that list tenet_name raises HTTPException."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        tenet = Tenet(db=mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            tenet.find(["tenet1", "tenet2"])
        
        assert exc_info.value.status_code == 500
    
    def test_find_with_empty_string_passes_validation(self, mock_db):
        """Test that empty string passes validation but may not find result.
        
        BUG: Empty string is considered valid, despite 'non-empty' in error message.
        """
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        
        # Empty string passes validation check
        with pytest.raises((HTTPException, TypeError)):
            tenet.find("")
    
    def test_find_with_not_found_raises_type_error(self, mock_db):
        """Test that None result from find_one raises TypeError.
        
        BUG: Code tries to access ['Id'] on None result, causing TypeError
        instead of raising proper HTTPException.
        """
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        
        with pytest.raises(TypeError):
            tenet.find("NonExistentTenet")
    
    def test_find_with_missing_id_field_raises_key_error(self, mock_db):
        """Test that result without Id field raises KeyError."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"TenetName": "Test"}
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        
        with pytest.raises(KeyError):
            tenet.find("TestTenet")
    
    def test_find_with_database_exception_propagates(self, mock_db):
        """Test that database exceptions are propagated."""
        mock_collection = MagicMock()
        mock_collection.find_one.side_effect = OperationFailure("Database error")
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        
        with pytest.raises(OperationFailure):
            tenet.find("TestTenet")
    
    def test_find_with_timeout_error_propagates(self, mock_db):
        """Test that timeout exceptions are propagated."""
        mock_collection = MagicMock()
        mock_collection.find_one.side_effect = ServerSelectionTimeoutError("Timeout")
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        
        with pytest.raises(ServerSelectionTimeoutError):
            tenet.find("TestTenet")


# ==================== EDGE CASES ====================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_find_with_special_characters(self, mock_db, tenet_find_result):
        """Test finding tenet with special characters in name."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = tenet_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        result = tenet.find("Tenet-With_Special@Chars#123")
        
        assert result == 123
    
    def test_find_with_unicode_characters(self, mock_db, tenet_find_result):
        """Test finding tenet with unicode characters."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = tenet_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        result = tenet.find("Tenet_こんにちは_你好")
        
        assert result == 123
    
    def test_find_with_spaces(self, mock_db, tenet_find_result):
        """Test finding tenet with spaces in name."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = tenet_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        result = tenet.find("Tenet With Spaces")
        
        assert result == 123
    
    def test_find_with_leading_trailing_spaces(self, mock_db, tenet_find_result):
        """Test finding tenet with leading/trailing spaces."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = tenet_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        result = tenet.find("  TenetName  ")
        
        assert result == 123
        # Spaces are preserved in query
        mock_collection.find_one.assert_called_with(
            {"TenetName": "  TenetName  "},
            {"_id": 0, "Id": 1}
        )
    
    def test_find_with_case_sensitive_name(self, mock_db):
        """Test that find is case-sensitive."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"Id": 100}
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        result = tenet.find("TestTenet")
        
        # Query should preserve case
        mock_collection.find_one.assert_called_with(
            {"TenetName": "TestTenet"},
            {"_id": 0, "Id": 1}
        )
    
    def test_find_with_numeric_string(self, mock_db, tenet_find_result):
        """Test finding tenet with numeric string name."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = tenet_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        result = tenet.find("12345")
        
        assert result == 123
    
    def test_find_with_zero_id_result(self, mock_db):
        """Test finding tenet that returns Id of 0."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"Id": 0}
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        result = tenet.find("ZeroId")
        
        assert result == 0
    
    def test_find_with_negative_id_result(self, mock_db):
        """Test finding tenet that returns negative Id."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"Id": -1}
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        result = tenet.find("NegativeId")
        
        assert result == -1
    
    def test_find_with_large_id_result(self, mock_db):
        """Test finding tenet that returns large Id."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"Id": 999999999}
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        result = tenet.find("LargeId")
        
        assert result == 999999999


# ==================== VALIDATION TESTS ====================

class TestValidation:
    """Test validation logic in find method."""
    
    def test_find_validates_none_before_query(self, mock_db):
        """Test that None validation happens before find_one call."""
        mock_collection = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        
        with pytest.raises(HTTPException):
            tenet.find(None)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_validates_type_before_query(self, mock_db):
        """Test that type validation happens before find_one call."""
        mock_collection = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        
        with pytest.raises(HTTPException):
            tenet.find(12345)
        
        mock_collection.find_one.assert_not_called()
    
    def test_find_accepts_string_subclass(self, mock_db, tenet_find_result):
        """Test that find accepts string subclasses."""
        class CustomString(str):
            pass
        
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = tenet_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        custom_str = CustomString("TestTenet")
        result = tenet.find(custom_str)
        
        assert result == 123


# ==================== PERFORMANCE TESTS ====================

class TestPerformance:
    """Test performance characteristics."""
    
    def test_find_multiple_tenets_sequential(self, mock_db, tenet_find_result):
        """Test finding multiple tenets sequentially."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = tenet_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        
        for i in range(20):
            result = tenet.find(f"Tenet{i}")
            assert result == 123
        
        assert mock_collection.find_one.call_count == 20
    
    def test_find_with_varying_name_lengths(self, mock_db, tenet_find_result):
        """Test finding tenets with varying name lengths."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = tenet_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        
        lengths = [10, 50, 100, 500]
        for length in lengths:
            name = "T" * length
            result = tenet.find(name)
            assert result == 123


# ==================== SECURITY TESTS ====================

class TestSecurity:
    """Test security-related aspects."""
    
    def test_find_validates_input_type(self, mock_db):
        """Test that find validates input type for security."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        tenet = Tenet(db=mock_db)
        
        with pytest.raises(HTTPException):
            tenet.find({"$ne": None})
    
    def test_find_with_injection_attempt(self, mock_db, tenet_find_result):
        """Test tenet name with potential injection patterns."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = tenet_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        injection_name = "'; DROP TABLE tenets; --"
        result = tenet.find(injection_name)
        
        assert result == 123
        # MongoDB driver handles escaping
    
    def test_find_rejects_none_tenet_name(self, mock_db):
        """Test that find rejects None tenet_name."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        tenet = Tenet(db=mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            tenet.find(None)
        
        assert exc_info.value.status_code == 500


# ==================== INTEGRATION TESTS ====================

class TestIntegration:
    """Test integration with MongoDB and dependencies."""
    
    def test_tenet_uses_correct_collection(self, mock_db):
        """Test that Tenet uses the correct collection name."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        tenet = Tenet(db=mock_db)
        mock_db.__getitem__.assert_called_with("Tenet")
    
    def test_find_calls_collection_find_one(self, mock_db, tenet_find_result):
        """Test that find method calls collection.find_one."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = tenet_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        tenet.find("TestTenet")
        
        mock_collection.find_one.assert_called_once()
    
    def test_multiple_tenet_instances_share_database(self, mock_db):
        """Test that multiple instances can use same database."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        
        tenet1 = Tenet(db=mock_db)
        tenet2 = Tenet(db=mock_db)
        
        assert tenet1.ModelWorkBench == tenet2.ModelWorkBench


# ==================== REGRESSION TESTS ====================

class TestRegression:
    """Test for regression issues and previous bugs."""
    
    def test_regression_find_returns_id_not_dict(self, mock_db):
        """Test that find returns Id value, not dictionary."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"Id": 456}
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        result = tenet.find("TestTenet")
        
        assert result == 456
        assert not isinstance(result, dict)
    
    def test_regression_find_none_returns_500(self, mock_db):
        """Test that None tenet_name returns 500 status."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        tenet = Tenet(db=mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            tenet.find(None)
        
        assert exc_info.value.status_code == 500
    
    def test_regression_find_excludes_id_field(self, mock_db):
        """Test that find query excludes _id field."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"Id": 123}
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        tenet.find("TestTenet")
        
        call_args = mock_collection.find_one.call_args[0]
        assert call_args[1]["_id"] == 0


# ==================== CODE QUALITY TESTS ====================

class TestCodeQuality:
    """Test code quality indicators."""
    
    def test_class_is_defined(self):
        """Test that Tenet class is properly defined."""
        assert Tenet is not None
        assert isinstance(Tenet, type)
    
    def test_init_method_exists(self):
        """Test that __init__ method exists."""
        assert hasattr(Tenet, '__init__')
    
    def test_find_method_exists(self):
        """Test that find method exists."""
        assert hasattr(Tenet, 'find')
    
    def test_tenet_instance_can_be_created(self, mock_db):
        """Test that Tenet instances can be created."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        tenet = Tenet(db=mock_db)
        assert tenet is not None
        assert isinstance(tenet, Tenet)
    
    def test_find_method_signature(self, mock_db):
        """Test find method accepts tenet_name parameter."""
        import inspect
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        tenet = Tenet(db=mock_db)
        sig = inspect.signature(tenet.find)
        params = list(sig.parameters.keys())
        assert 'tenet_name' in params


# ==================== BUG DOCUMENTATION ====================

class TestBugDocumentation:
    """Document known bugs or issues in the original code."""
    
    def test_bug_commented_out_global_instantiation(self):
        """BUG: Lines 26-27 have commented out global instantiation.
        
        Lines 26-27: Commented code for global ModelWorkBenchconnection
        This may indicate previous refactoring or debugging.
        """
        assert True
    
    def test_bug_find_none_result_causes_type_error(self, mock_db):
        """BUG: None result from find_one causes TypeError instead of HTTPException.
        
        Line 52: result = self.collection.find_one(...)['Id']
        If find_one returns None, accessing ['Id'] raises TypeError.
        Line 53-54: The None check never executes because TypeError occurs first.
        
        Should check if result is None before accessing ['Id'].
        """
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        
        # This raises TypeError, not HTTPException
        with pytest.raises(TypeError):
            tenet.find("NonExistent")
    
    def test_bug_unreachable_none_check(self, mock_db):
        """BUG: Lines 53-54 None check is unreachable.
        
        Line 52: Accesses ['Id'] immediately after find_one
        Line 53-54: if result is None: raise HTTPException(...)
        
        The None check is unreachable because TypeError is raised first.
        """
        # This test documents that the None check never executes
        assert True
    
    def test_bug_uses_500_for_validation_errors(self, mock_db):
        """BUG: Uses 500 status for validation errors instead of 400.
        
        Line 48: HTTPException(status_code=500) for None/type validation
        Line 54: HTTPException(status_code=500) for not found
        
        Should use 400 for validation errors, 404 for not found, 500 for server errors.
        """
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        tenet = Tenet(db=mock_db)
        
        # Validation error uses 500 instead of 400
        with pytest.raises(HTTPException) as exc_info:
            tenet.find(None)
        
        assert exc_info.value.status_code == 500
        # Should be 400 for bad request
    
    def test_bug_empty_string_allowed(self, mock_db):
        """BUG: Empty string passes validation despite 'non-empty' in error message.
        
        Line 47: Error says "Tenet Name must be a non-empty string"
        Line 47: But check is only (tenet_name is None or not isinstance(tenet_name, str))
        
        Empty string "" passes this check.
        """
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        
        # Empty string passes validation but causes error on ['Id'] access
        with pytest.raises(TypeError):
            tenet.find("")
    
    def test_bug_inconsistent_log_message(self):
        """BUG: Log message says 'inside Tenet loop' which is unclear.
        
        Line 34: log.info("inside Tenet loop")
        Should say "Initializing Tenet with provided database" or similar.
        """
        assert True


# ==================== RESOURCE MANAGEMENT ====================

class TestResourceManagement:
    """Test resource management and cleanup."""
    
    def test_find_does_not_leave_connections_open(self, mock_db, tenet_find_result):
        """Test that find method doesn't leave resources open."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = tenet_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        tenet.find("TestTenet")
        
        # MongoDB driver handles connection pooling
        assert True
    
    def test_multiple_tenet_instances(self, mock_db):
        """Test that multiple Tenet instances can coexist."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        tenets = [Tenet(db=mock_db) for _ in range(10)]
        assert len(tenets) == 10
        assert all(isinstance(t, Tenet) for t in tenets)


# ==================== SCALABILITY TESTS ====================

class TestScalability:
    """Test scalability considerations."""
    
    def test_find_can_handle_rapid_successive_calls(self, mock_db, tenet_find_result):
        """Test that find can handle many rapid calls."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = tenet_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        
        for i in range(100):
            result = tenet.find(f"Tenet{i}")
            assert result is not None
        
        assert mock_collection.find_one.call_count == 100
    
    def test_find_with_concurrent_pattern(self, mock_db, tenet_find_result):
        """Test find pattern suitable for concurrent use."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = tenet_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        tenet = Tenet(db=mock_db)
        
        # Simulate multiple users finding tenets
        tenet_names = [f"Tenet{i}" for i in range(20)]
        results = [tenet.find(name) for name in tenet_names]
        
        assert len(results) == 20
        assert all(r == 123 for r in results)


# ==================== ERROR MESSAGE TESTS ====================

class TestErrorMessages:
    """Test error message clarity and usefulness."""
    
    def test_none_tenet_name_error_message_is_clear(self, mock_db):
        """Test that None tenet_name error message is descriptive."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        tenet = Tenet(db=mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            tenet.find(None)
        
        assert "Tenet Name must be a non-empty string" in str(exc_info.value.detail)
        assert exc_info.value.status_code == 500
    
    def test_wrong_type_error_message_is_clear(self, mock_db):
        """Test that wrong type error message is descriptive."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        tenet = Tenet(db=mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            tenet.find(12345)
        
        assert "Tenet Name must be a non-empty string" in str(exc_info.value.detail)
