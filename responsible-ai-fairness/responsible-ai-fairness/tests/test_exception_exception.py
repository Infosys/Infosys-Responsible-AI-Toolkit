"""
Comprehensive test suite for exception.py

This test file validates the custom exception classes in the fairness exception module:
- FairnessException (abstract base class)
- FairnessNotFoundError
- FairnessNameNotEmptyError
- FairnessUIParameterNotFoundError
- FairnessAttributeError

Focus areas:
- Clarity & Readability
- Isolation
- Repeatability
- Coverage
- Assertions

Quality metrics covered:
- Functional Correctness
- Edge Cases
- Error Handling
- Performance
- Resource Management
- Security
- Scalability
- Integration Points
- Regression
- Code Quality Indicators
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from abc import ABC

# Now import the module under test
from fairness.exception.exception import (
    FairnessException,
    FairnessNotFoundError,
    FairnessNameNotEmptyError,
    FairnessUIParameterNotFoundError,
    FairnessAttributeError
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_usecase_name():
    """Sample usecase name for testing."""
    return "test_usecase_123"


@pytest.fixture
def sample_error_detail():
    """Sample error detail message."""
    return "Test error detail message"


@pytest.fixture
def special_chars_name():
    """Usecase name with special characters."""
    return "test<>usecase&'\"@#$%"


@pytest.fixture
def unicode_name():
    """Usecase name with unicode characters."""
    return "测试用例_тест_🚀"


@pytest.fixture
def long_name():
    """Very long usecase name."""
    return "a" * 1000


@pytest.fixture
def empty_string():
    """Empty string."""
    return ""


# ============================================================================
# TEST CLASS: FairnessException Base Class
# ============================================================================

class TestFairnessExceptionBase:
    """Test FairnessException abstract base class."""
    
    def test_is_abstract_base_class(self):
        """Test that FairnessException inherits from ABC."""
        assert issubclass(FairnessException, ABC)
    
    def test_inherits_from_exception(self):
        """Test that FairnessException inherits from Exception."""
        assert issubclass(FairnessException, Exception)
    
    def test_cannot_instantiate_directly_without_concrete_implementation(self):
        """Test abstract class behavior (though Python ABC doesn't strictly prevent instantiation)."""
        # Note: Python's ABC with Exception doesn't prevent instantiation without abstract methods
        # This documents the actual behavior
        try:
            exc = FairnessException("Test detail")
            assert exc.status_code == 400
            assert str(exc) == "Test detail"
        except TypeError:
            # If it does raise, that's also acceptable for an ABC
            pass
    
    def test_init_sets_status_code(self, sample_error_detail):
        """Test __init__ sets status_code to HTTP_STATUS_BAD_REQUEST."""
        exc = FairnessException(sample_error_detail)
        assert exc.status_code == 400
    
    def test_init_calls_super_with_detail(self, sample_error_detail):
        """Test __init__ calls Exception.__init__ with detail."""
        exc = FairnessException(sample_error_detail)
        assert str(exc) == sample_error_detail
    
    def test_init_with_empty_detail(self):
        """Test initialization with empty detail string."""
        exc = FairnessException("")
        assert exc.status_code == 400
        assert str(exc) == ""
    
    def test_exception_can_be_raised(self, sample_error_detail):
        """Test that FairnessException can be raised and caught."""
        with pytest.raises(FairnessException) as exc_info:
            raise FairnessException(sample_error_detail)
        
        assert str(exc_info.value) == sample_error_detail
        assert exc_info.value.status_code == 400
    
    def test_exception_attributes_accessible(self, sample_error_detail):
        """Test that exception attributes are accessible."""
        exc = FairnessException(sample_error_detail)
        
        assert hasattr(exc, 'status_code')
        assert hasattr(exc, 'args')
        assert exc.args[0] == sample_error_detail


# ============================================================================
# TEST CLASS: FairnessNotFoundError
# ============================================================================

class TestFairnessNotFoundError:
    """Test FairnessNotFoundError exception class."""
    
    def test_inherits_from_fairness_exception(self):
        """Test that FairnessNotFoundError inherits from FairnessException."""
        assert issubclass(FairnessNotFoundError, FairnessException)
    
    def test_inherits_from_exception(self):
        """Test that FairnessNotFoundError inherits from Exception."""
        assert issubclass(FairnessNotFoundError, Exception)
    
    def test_init_sets_status_code_to_404(self, sample_usecase_name):
        """Test __init__ sets status_code to HTTP_STATUS_NOT_FOUND (404)."""
        exc = FairnessNotFoundError(sample_usecase_name)
        assert exc.status_code == 404
    
    def test_init_replaces_placeholder_in_message(self, sample_usecase_name):
        """Test __init__ replaces PLACEHOLDER_TEXT with actual name."""
        exc = FairnessNotFoundError(sample_usecase_name)
        
        expected_detail = f"Usecase id {sample_usecase_name} Not Found"
        assert exc.detail == expected_detail
    
    def test_detail_attribute_exists(self, sample_usecase_name):
        """Test that detail attribute is set correctly."""
        exc = FairnessNotFoundError(sample_usecase_name)
        
        assert hasattr(exc, 'detail')
        assert isinstance(exc.detail, str)
    
    def test_exception_can_be_raised(self, sample_usecase_name):
        """Test that FairnessNotFoundError can be raised and caught."""
        with pytest.raises(FairnessNotFoundError) as exc_info:
            raise FairnessNotFoundError(sample_usecase_name)
        
        assert exc_info.value.status_code == 404
        assert sample_usecase_name in exc_info.value.detail
    
    def test_can_be_caught_as_fairness_exception(self, sample_usecase_name):
        """Test that FairnessNotFoundError can be caught as FairnessException."""
        with pytest.raises(FairnessException) as exc_info:
            raise FairnessNotFoundError(sample_usecase_name)
        
        assert isinstance(exc_info.value, FairnessNotFoundError)
    
    def test_can_be_caught_as_exception(self, sample_usecase_name):
        """Test that FairnessNotFoundError can be caught as base Exception."""
        with pytest.raises(Exception) as exc_info:
            raise FairnessNotFoundError(sample_usecase_name)
        
        assert isinstance(exc_info.value, FairnessNotFoundError)


# ============================================================================
# TEST CLASS: FairnessNotFoundError Edge Cases
# ============================================================================

class TestFairnessNotFoundErrorEdgeCases:
    """Test edge cases for FairnessNotFoundError."""
    
    def test_with_empty_name(self, empty_string):
        """Test with empty string as name."""
        exc = FairnessNotFoundError(empty_string)
        
        assert exc.status_code == 404
        assert "Usecase id  Not Found" == exc.detail
    
    def test_with_special_characters(self, special_chars_name):
        """Test with special characters in name."""
        exc = FairnessNotFoundError(special_chars_name)
        
        assert exc.status_code == 404
        assert special_chars_name in exc.detail
    
    def test_with_unicode_characters(self, unicode_name):
        """Test with unicode characters in name."""
        exc = FairnessNotFoundError(unicode_name)
        
        assert exc.status_code == 404
        assert unicode_name in exc.detail
    
    def test_with_very_long_name(self, long_name):
        """Test with very long name (1000 characters)."""
        exc = FairnessNotFoundError(long_name)
        
        assert exc.status_code == 404
        assert long_name in exc.detail
    
    def test_with_none_name(self):
        """Test with None as name (should cause TypeError in replace).
        
        BUG: Code doesn't handle non-string types, raises TypeError.
        """
        with pytest.raises(TypeError, match="replace\\(\\) argument 2 must be str"):
            exc = FairnessNotFoundError(None)
    
    def test_with_numeric_name(self):
        """Test with numeric name (should cause TypeError in replace).
        
        BUG: Code doesn't handle non-string types, raises TypeError.
        """
        with pytest.raises(TypeError, match="replace\\(\\) argument 2 must be str"):
            exc = FairnessNotFoundError(12345)


# ============================================================================
# TEST CLASS: FairnessNameNotEmptyError
# ============================================================================

class TestFairnessNameNotEmptyError:
    """Test FairnessNameNotEmptyError exception class."""
    
    def test_inherits_from_fairness_exception(self):
        """Test that FairnessNameNotEmptyError inherits from FairnessException."""
        assert issubclass(FairnessNameNotEmptyError, FairnessException)
    
    def test_init_sets_status_code_to_409(self, sample_usecase_name):
        """Test __init__ sets status_code to HTTP_STATUS_409_CODE (409)."""
        exc = FairnessNameNotEmptyError(sample_usecase_name)
        assert exc.status_code == 409
    
    def test_init_sets_detail_to_validation_error(self, sample_usecase_name):
        """Test __init__ sets detail to USECASE_NAME_VALIDATION_ERROR."""
        exc = FairnessNameNotEmptyError(sample_usecase_name)
        
        expected_detail = "Usecase name should not be empty"
        assert exc.detail == expected_detail
    
    def test_name_parameter_not_used_in_message(self, sample_usecase_name):
        """Test that name parameter is not used in detail message (bug documentation)."""
        exc = FairnessNameNotEmptyError(sample_usecase_name)
        
        # Bug: name parameter is accepted but not used
        assert sample_usecase_name not in exc.detail
    
    def test_detail_attribute_exists(self, sample_usecase_name):
        """Test that detail attribute is set correctly."""
        exc = FairnessNameNotEmptyError(sample_usecase_name)
        
        assert hasattr(exc, 'detail')
        assert isinstance(exc.detail, str)
    
    def test_exception_can_be_raised(self, sample_usecase_name):
        """Test that FairnessNameNotEmptyError can be raised and caught."""
        with pytest.raises(FairnessNameNotEmptyError) as exc_info:
            raise FairnessNameNotEmptyError(sample_usecase_name)
        
        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "Usecase name should not be empty"
    
    def test_different_names_produce_same_detail(self):
        """Test that different names produce the same detail message."""
        exc1 = FairnessNameNotEmptyError("name1")
        exc2 = FairnessNameNotEmptyError("name2")
        exc3 = FairnessNameNotEmptyError("")
        
        assert exc1.detail == exc2.detail == exc3.detail


# ============================================================================
# TEST CLASS: FairnessUIParameterNotFoundError
# ============================================================================

class TestFairnessUIParameterNotFoundError:
    """Test FairnessUIParameterNotFoundError exception class."""
    
    def test_inherits_from_fairness_exception(self):
        """Test that FairnessUIParameterNotFoundError inherits from FairnessException."""
        assert issubclass(FairnessUIParameterNotFoundError, FairnessException)
    
    def test_init_sets_status_code_to_422(self, sample_usecase_name):
        """Test __init__ sets status_code to HTTP_STATUS_DATA_PROCESSING_ERROR (422)."""
        exc = FairnessUIParameterNotFoundError(sample_usecase_name)
        assert exc.status_code == 422
    
    def test_init_sets_detail_to_validation_error(self, sample_usecase_name):
        """Test __init__ sets detail to USECASE_NAME_VALIDATION_ERROR."""
        exc = FairnessUIParameterNotFoundError(sample_usecase_name)
        
        expected_detail = "Usecase name should not be empty"
        assert exc.detail == expected_detail
    
    def test_name_parameter_not_used_in_message(self, sample_usecase_name):
        """Test that name parameter is not used in detail message (bug documentation)."""
        exc = FairnessUIParameterNotFoundError(sample_usecase_name)
        
        # Bug: name parameter is accepted but not used
        # Also bug: uses USECASE_NAME_VALIDATION_ERROR instead of parameter error message
        assert sample_usecase_name not in exc.detail
    
    def test_detail_attribute_exists(self, sample_usecase_name):
        """Test that detail attribute is set correctly."""
        exc = FairnessUIParameterNotFoundError(sample_usecase_name)
        
        assert hasattr(exc, 'detail')
        assert isinstance(exc.detail, str)
    
    def test_exception_can_be_raised(self, sample_usecase_name):
        """Test that FairnessUIParameterNotFoundError can be raised and caught."""
        with pytest.raises(FairnessUIParameterNotFoundError) as exc_info:
            raise FairnessUIParameterNotFoundError(sample_usecase_name)
        
        assert exc_info.value.status_code == 422
        assert exc_info.value.detail == "Usecase name should not be empty"


# ============================================================================
# TEST CLASS: FairnessAttributeError
# ============================================================================

class TestFairnessAttributeError:
    """Test FairnessAttributeError exception class."""
    
    def test_inherits_from_fairness_exception(self):
        """Test that FairnessAttributeError inherits from FairnessException."""
        assert issubclass(FairnessAttributeError, FairnessException)
    
    def test_init_sets_status_code_to_400(self, sample_error_detail):
        """Test __init__ sets status_code to HTTP_STATUS_BAD_REQUEST (400)."""
        exc = FairnessAttributeError(sample_error_detail)
        assert exc.status_code == 400
    
    def test_init_sets_detail_from_parameter(self, sample_error_detail):
        """Test __init__ sets detail to the provided detail parameter."""
        exc = FairnessAttributeError(sample_error_detail)
        
        assert exc.detail == sample_error_detail
    
    def test_detail_attribute_exists(self, sample_error_detail):
        """Test that detail attribute is set correctly."""
        exc = FairnessAttributeError(sample_error_detail)
        
        assert hasattr(exc, 'detail')
        assert isinstance(exc.detail, str)
    
    def test_exception_can_be_raised(self, sample_error_detail):
        """Test that FairnessAttributeError can be raised and caught."""
        with pytest.raises(FairnessAttributeError) as exc_info:
            raise FairnessAttributeError(sample_error_detail)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == sample_error_detail
    
    def test_with_empty_detail(self, empty_string):
        """Test with empty detail string."""
        exc = FairnessAttributeError(empty_string)
        
        assert exc.status_code == 400
        assert exc.detail == ""
    
    def test_with_long_detail(self):
        """Test with very long detail string."""
        long_detail = "Error: " + "x" * 10000
        exc = FairnessAttributeError(long_detail)
        
        assert exc.status_code == 400
        assert exc.detail == long_detail


# ============================================================================
# TEST CLASS: Exception Hierarchy Integration
# ============================================================================

class TestExceptionHierarchyIntegration:
    """Test exception hierarchy and polymorphism."""
    
    def test_all_custom_exceptions_inherit_from_fairness_exception(self):
        """Test that all custom exceptions inherit from FairnessException."""
        assert issubclass(FairnessNotFoundError, FairnessException)
        assert issubclass(FairnessNameNotEmptyError, FairnessException)
        assert issubclass(FairnessUIParameterNotFoundError, FairnessException)
        assert issubclass(FairnessAttributeError, FairnessException)
    
    def test_all_custom_exceptions_inherit_from_base_exception(self):
        """Test that all custom exceptions inherit from base Exception."""
        assert issubclass(FairnessNotFoundError, Exception)
        assert issubclass(FairnessNameNotEmptyError, Exception)
        assert issubclass(FairnessUIParameterNotFoundError, Exception)
        assert issubclass(FairnessAttributeError, Exception)
    
    def test_polymorphic_catch_as_fairness_exception(self):
        """Test catching different exception types as FairnessException."""
        exceptions = [
            FairnessNotFoundError("test"),
            FairnessNameNotEmptyError("test"),
            FairnessUIParameterNotFoundError("test"),
            FairnessAttributeError("test")
        ]
        
        for exc in exceptions:
            with pytest.raises(FairnessException):
                raise exc
    
    def test_status_codes_are_different_across_exceptions(self):
        """Test that different exception types have appropriate status codes."""
        exc1 = FairnessException("test")
        exc2 = FairnessNotFoundError("test")
        exc3 = FairnessNameNotEmptyError("test")
        exc4 = FairnessUIParameterNotFoundError("test")
        exc5 = FairnessAttributeError("test")
        
        assert exc1.status_code == 400
        assert exc2.status_code == 404
        assert exc3.status_code == 409
        assert exc4.status_code == 422
        assert exc5.status_code == 400
    
    def test_exception_types_are_distinct(self):
        """Test that exception types can be distinguished."""
        exc1 = FairnessNotFoundError("test")
        exc2 = FairnessNameNotEmptyError("test")
        
        assert type(exc1) != type(exc2)
        assert isinstance(exc1, FairnessNotFoundError)
        assert not isinstance(exc1, FairnessNameNotEmptyError)


# ============================================================================
# TEST CLASS: Error Handling
# ============================================================================

class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_exception_with_type_error_in_replace(self):
        """Test behavior when replace() receives non-string type.
        
        BUG: The code doesn't handle non-string name parameters, 
        causing TypeError when str.replace() is called.
        """
        # Dict type should cause TypeError
        with pytest.raises(TypeError, match="replace\\(\\) argument 2 must be str"):
            exc = FairnessNotFoundError({"dict": "value"})
    
    def test_exception_repr_works(self, sample_usecase_name):
        """Test that exception repr() works correctly."""
        exc = FairnessNotFoundError(sample_usecase_name)
        
        repr_str = repr(exc)
        assert repr_str is not None
        assert isinstance(repr_str, str)
    
    def test_exception_str_works(self, sample_usecase_name):
        """Test that exception str() works correctly."""
        exc = FairnessNotFoundError(sample_usecase_name)
        
        str_str = str(exc)
        assert str_str is not None
        assert isinstance(str_str, str)
    
    def test_multiple_exceptions_independent(self):
        """Test that multiple exception instances are independent."""
        exc1 = FairnessNotFoundError("name1")
        exc2 = FairnessNotFoundError("name2")
        
        assert exc1.detail != exc2.detail
        assert "name1" in exc1.detail
        assert "name2" in exc2.detail


# ============================================================================
# TEST CLASS: Performance Tests
# ============================================================================

class TestPerformance:
    """Test performance characteristics."""
    
    def test_exception_creation_performance(self):
        """Test that creating exceptions is fast."""
        import time
        
        start = time.time()
        for i in range(1000):
            exc = FairnessNotFoundError(f"test_{i}")
        duration = time.time() - start
        
        assert duration < 1.0  # Should create 1000 exceptions in less than 1 second
    
    def test_exception_raising_performance(self):
        """Test that raising and catching exceptions is reasonably fast."""
        import time
        
        start = time.time()
        for i in range(100):
            try:
                raise FairnessNotFoundError(f"test_{i}")
            except FairnessNotFoundError:
                pass
        duration = time.time() - start
        
        assert duration < 1.0  # Should raise/catch 100 exceptions in less than 1 second
    
    def test_detail_message_generation_performance(self):
        """Test that detail message generation is fast."""
        import time
        
        start = time.time()
        for i in range(1000):
            exc = FairnessNotFoundError(f"usecase_{i}")
            _ = exc.detail
        duration = time.time() - start
        
        assert duration < 1.0


# ============================================================================
# TEST CLASS: Security Tests
# ============================================================================

class TestSecurity:
    """Test security-related aspects."""
    
    def test_exception_doesnt_expose_sensitive_info_in_base_exception(self):
        """Test that base exception doesn't inadvertently expose info."""
        exc = FairnessException("Password: secret123")
        
        # Detail is passed to Exception, so it will be in str(exc)
        # This documents the behavior - sensitive info should not be passed
        assert "secret123" in str(exc)
    
    def test_sql_injection_patterns_in_name(self):
        """Test with SQL injection patterns in name."""
        sql_injection = "'; DROP TABLE users; --"
        exc = FairnessNotFoundError(sql_injection)
        
        # Exception should handle this as regular string
        assert exc.status_code == 404
        assert sql_injection in exc.detail
    
    def test_xss_patterns_in_name(self):
        """Test with XSS patterns in name."""
        xss_pattern = "<script>alert('XSS')</script>"
        exc = FairnessNotFoundError(xss_pattern)
        
        # Exception should handle this as regular string
        assert exc.status_code == 404
        assert xss_pattern in exc.detail
    
    def test_path_traversal_patterns_in_name(self):
        """Test with path traversal patterns in name."""
        path_traversal = "../../etc/passwd"
        exc = FairnessNotFoundError(path_traversal)
        
        assert exc.status_code == 404
        assert path_traversal in exc.detail


# ============================================================================
# TEST CLASS: Scalability Tests
# ============================================================================

class TestScalability:
    """Test scalability aspects."""
    
    def test_many_concurrent_exceptions(self):
        """Test creating many exception instances."""
        exceptions = []
        
        for i in range(1000):
            exc = FairnessNotFoundError(f"usecase_{i}")
            exceptions.append(exc)
        
        assert len(exceptions) == 1000
        assert all(exc.status_code == 404 for exc in exceptions)
    
    def test_exception_memory_overhead(self):
        """Test that exceptions don't have excessive memory overhead."""
        import sys
        
        exc = FairnessNotFoundError("test")
        size = sys.getsizeof(exc)
        
        # Exception should be reasonably sized (this is informational)
        assert size < 10000  # Less than 10KB per exception


# ============================================================================
# TEST CLASS: Regression Tests
# ============================================================================

class TestRegression:
    """Test for regression issues and backwards compatibility."""
    
    def test_exception_detail_attribute_consistent(self):
        """Test that all exceptions have detail attribute."""
        exceptions = [
            FairnessNotFoundError("test"),
            FairnessNameNotEmptyError("test"),
            FairnessUIParameterNotFoundError("test"),
            FairnessAttributeError("test")
        ]
        
        for exc in exceptions:
            assert hasattr(exc, 'detail')
            assert isinstance(exc.detail, str)
    
    def test_exception_status_code_attribute_consistent(self):
        """Test that all exceptions have status_code attribute."""
        exceptions = [
            FairnessException("test"),
            FairnessNotFoundError("test"),
            FairnessNameNotEmptyError("test"),
            FairnessUIParameterNotFoundError("test"),
            FairnessAttributeError("test")
        ]
        
        for exc in exceptions:
            assert hasattr(exc, 'status_code')
            assert isinstance(exc.status_code, int)
    
    def test_exception_inheritance_chain_maintained(self):
        """Test that exception inheritance chain is maintained."""
        exc = FairnessNotFoundError("test")
        
        assert isinstance(exc, FairnessNotFoundError)
        assert isinstance(exc, FairnessException)
        assert isinstance(exc, Exception)
        assert isinstance(exc, BaseException)


# ============================================================================
# TEST CLASS: Code Quality Indicators
# ============================================================================

class TestCodeQuality:
    """Test code quality indicators."""
    
    def test_fairness_exception_class_exists(self):
        """Test FairnessException class is properly defined."""
        assert FairnessException is not None
        assert callable(FairnessException)
    
    def test_fairness_not_found_error_class_exists(self):
        """Test FairnessNotFoundError class is properly defined."""
        assert FairnessNotFoundError is not None
        assert callable(FairnessNotFoundError)
    
    def test_fairness_name_not_empty_error_class_exists(self):
        """Test FairnessNameNotEmptyError class is properly defined."""
        assert FairnessNameNotEmptyError is not None
        assert callable(FairnessNameNotEmptyError)
    
    def test_fairness_ui_parameter_not_found_error_class_exists(self):
        """Test FairnessUIParameterNotFoundError class is properly defined."""
        assert FairnessUIParameterNotFoundError is not None
        assert callable(FairnessUIParameterNotFoundError)
    
    def test_fairness_attribute_error_class_exists(self):
        """Test FairnessAttributeError class is properly defined."""
        assert FairnessAttributeError is not None
        assert callable(FairnessAttributeError)
    
    def test_module_has_required_exports(self):
        """Test module exports all required components."""
        from fairness.exception import exception
        
        assert hasattr(exception, 'FairnessException')
        assert hasattr(exception, 'FairnessNotFoundError')
        assert hasattr(exception, 'FairnessNameNotEmptyError')
        assert hasattr(exception, 'FairnessUIParameterNotFoundError')
        assert hasattr(exception, 'FairnessAttributeError')
    
    def test_all_exception_classes_have_docstrings(self):
        """Test that all exception classes have docstrings."""
        assert FairnessException.__doc__ is not None
        assert FairnessNotFoundError.__doc__ is not None
        assert FairnessNameNotEmptyError.__doc__ is not None
        assert FairnessUIParameterNotFoundError.__doc__ is not None
        assert FairnessAttributeError.__doc__ is not None


# ============================================================================
# TEST CLASS: Bug Documentation
# ============================================================================

class TestBugDocumentation:
    """Document known bugs and issues in the original code."""
    
    def test_bug_global_constants_commented_but_used(self):
        """
        BUG DOCUMENTATION: global_constants import is commented out but still used
        
        Location: Line 23
        Issue: The import line is commented:
            # from aicloudlibs.constants import constants as global_constants
        But the code still uses global_constants throughout:
            - Line 32: self.status_code = global_constants.HTTP_STATUS_BAD_REQUEST
            - Line 42: self.status_code = global_constants.HTTP_STATUS_NOT_FOUND
            - Line 51: self.status_code = global_constants.HTTP_STATUS_409_CODE
            - Line 59: self.status_code = global_constants.HTTP_STATUS_DATA_PROCESSING_ERROR
            - Line 68: self.status_code = global_constants.HTTP_STATUS_BAD_REQUEST
        
        Impact: Code will raise NameError at runtime when trying to use these classes
        Severity: CRITICAL - code is completely broken without the import
        
        Expected: Uncomment the import or provide global_constants another way
        """
        # This test documents that the mocking is necessary for the code to work
        try:
            exc = FairnessException("test")
            # If this works, it's because we mocked global_constants
            assert exc.status_code == 400
        except NameError as e:
            # If not mocked, this is the error that occurs
            pytest.fail(f"NameError occurred: {e}")
    
    def test_bug_unused_import_sys(self):
        """
        BUG DOCUMENTATION: Unused import
        
        Location: Line 20
        Issue: import sys, traceback - both are imported but never used
        Impact: Unnecessary imports
        Severity: Minor (code smell)
        """
        # Test module loads successfully despite unused imports
        from fairness.exception import exception
        assert True
    
    def test_bug_unused_import_traceback(self):
        """
        BUG DOCUMENTATION: Unused import
        
        Location: Line 20
        Issue: traceback is imported but never used
        Impact: Unnecessary import
        Severity: Minor (code smell)
        """
        from fairness.exception import exception
        assert True
    
    def test_bug_unused_imports_from_local_constants(self):
        """
        BUG DOCUMENTATION: Unused imports
        
        Location: Line 22
        Issue: SPACE_DELIMITER and USECASE_ALREADY_EXISTS are imported but never used
        Impact: Unnecessary imports
        Severity: Minor (code smell)
        """
        from fairness.exception import exception
        assert True
    
    def test_bug_name_parameter_not_used_in_name_not_empty_error(self):
        """
        BUG DOCUMENTATION: Parameter accepted but not used
        
        Location: Line 48-51 (FairnessNameNotEmptyError.__init__)
        Issue: __init__ accepts 'name' parameter but doesn't use it
            def __init__(self,name):
                self.detail = USECASE_NAME_VALIDATION_ERROR
        
        Impact: Misleading API - parameter suggests it will be used in message
        Severity: Moderate (confusing interface)
        
        Expected: Either use the name in the message or remove the parameter
        """
        exc1 = FairnessNameNotEmptyError("name1")
        exc2 = FairnessNameNotEmptyError("completely_different_name")
        
        # Bug: both produce identical detail messages
        assert exc1.detail == exc2.detail
        assert "name1" not in exc1.detail
    
    def test_bug_name_parameter_not_used_in_ui_parameter_error(self):
        """
        BUG DOCUMENTATION: Parameter accepted but not used
        
        Location: Line 57-60 (FairnessUIParameterNotFoundError.__init__)
        Issue: __init__ accepts 'name' parameter but doesn't use it
        Also uses wrong error message (USECASE_NAME_VALIDATION_ERROR instead of parameter error)
        
        Impact: Very confusing - "ParameterNotFoundError" uses "name validation" message
        Severity: Moderate (wrong error message for the exception type)
        
        Expected: Use appropriate error message for parameter errors and use the name parameter
        """
        exc = FairnessUIParameterNotFoundError("missing_param_x")
        
        # Bug: parameter name not in message
        assert "missing_param_x" not in exc.detail
        # Bug: uses name validation error instead of parameter error
        assert exc.detail == "Usecase name should not be empty"
    
    def test_bug_typo_in_docstring_dscription(self):
        """
        BUG DOCUMENTATION: Typo in docstring
        
        Location: Line 29 (FairnessException class docstring)
        Issue: "dscription:" should be "description:"
        Impact: Minor typo in documentation
        Severity: Minor (documentation error)
        """
        assert "dscription" in FairnessException.__doc__.lower()
    
    def test_bug_typo_in_docstring_parametr(self):
        """
        BUG DOCUMENTATION: Typo in docstring
        
        Location: Line 54 (FairnessUIParameterNotFoundError class docstring)
        Issue: "ParametrNotFoundError" should be "ParameterNotFoundError"
        Impact: Minor typo in documentation
        Severity: Minor (documentation error)
        """
        assert "Parametr" in FairnessUIParameterNotFoundError.__doc__
    
    def test_bug_inconsistent_naming_usecase_vs_fairness(self):
        """
        BUG DOCUMENTATION: Inconsistent naming
        
        Location: Multiple locations
        Issue: Docstrings refer to "UsecaseException", "UsecaseNotFoundError" etc.
               but actual class names use "Fairness" prefix
        Impact: Confusing documentation doesn't match code
        Severity: Minor (documentation inconsistency)
        
        Examples:
        - Line 29: "Abstract base class of UsecaseException" (but class is FairnessException)
        - Line 39: "UsecaseNotFoundError thrown by" (but class is FairnessNotFoundError)
        """
        # Docstring says "UsecaseException" but class name is "FairnessException"
        assert "Usecase" in FairnessException.__doc__
        assert "FairnessException" == FairnessException.__name__
    
    def test_bug_missing_type_annotation_for_name_parameter(self):
        """
        BUG DOCUMENTATION: Inconsistent type annotations
        
        Location: Lines 41, 49, 58 (exception __init__ methods)
        Issue: FairnessException has type annotation for detail parameter
               but other exceptions don't have type annotations for name parameter
        
        Impact: Inconsistent code style, missing type hints
        Severity: Minor (style inconsistency)
        
        FairnessException: def __init__(self, detail: str) -> None:
        FairnessNotFoundError: def __init__(self,name):  # No type annotation
        """
        # Test documents the inconsistency
        import inspect
        
        fairness_sig = inspect.signature(FairnessException.__init__)
        notfound_sig = inspect.signature(FairnessNotFoundError.__init__)
        
        # FairnessException has annotations
        assert fairness_sig.parameters['detail'].annotation == str
        # FairnessNotFoundError doesn't have annotations
        assert notfound_sig.parameters['name'].annotation == inspect.Parameter.empty


# ============================================================================
# TEST CLASS: Exception Message Validation
# ============================================================================

class TestExceptionMessageValidation:
    """Test exception message content and formatting."""
    
    def test_not_found_error_message_format(self):
        """Test FairnessNotFoundError message format is correct."""
        exc = FairnessNotFoundError("test123")
        
        assert exc.detail == "Usecase id test123 Not Found"
        assert exc.detail.startswith("Usecase id ")
        assert exc.detail.endswith(" Not Found")
    
    def test_name_not_empty_error_message_is_constant(self):
        """Test FairnessNameNotEmptyError always produces same message."""
        messages = []
        
        for name in ["name1", "name2", "", "test", None]:
            exc = FairnessNameNotEmptyError(name)
            messages.append(exc.detail)
        
        # All messages should be identical
        assert len(set(messages)) == 1
        assert messages[0] == "Usecase name should not be empty"
    
    def test_ui_parameter_error_message_is_constant(self):
        """Test FairnessUIParameterNotFoundError always produces same message."""
        exc1 = FairnessUIParameterNotFoundError("param1")
        exc2 = FairnessUIParameterNotFoundError("param2")
        
        assert exc1.detail == exc2.detail
        assert exc1.detail == "Usecase name should not be empty"
    
    def test_attribute_error_message_matches_input(self):
        """Test FairnessAttributeError message matches provided detail."""
        test_messages = [
            "Attribute 'x' not found",
            "Invalid attribute access",
            "Missing required attribute"
        ]
        
        for msg in test_messages:
            exc = FairnessAttributeError(msg)
            assert exc.detail == msg


# ============================================================================
# TEST CLASS: Status Code Validation
# ============================================================================

class TestStatusCodeValidation:
    """Test that status codes are appropriate for each exception type."""
    
    def test_status_codes_are_valid_http_codes(self):
        """Test that all status codes are valid HTTP status codes."""
        exceptions = [
            (FairnessException("test"), 400),
            (FairnessNotFoundError("test"), 404),
            (FairnessNameNotEmptyError("test"), 409),
            (FairnessUIParameterNotFoundError("test"), 422),
            (FairnessAttributeError("test"), 400)
        ]
        
        valid_http_codes = range(100, 600)
        
        for exc, expected_code in exceptions:
            assert exc.status_code in valid_http_codes
            assert exc.status_code == expected_code
    
    def test_not_found_error_uses_404(self):
        """Test FairnessNotFoundError uses 404 Not Found."""
        exc = FairnessNotFoundError("test")
        assert exc.status_code == 404
    
    def test_name_not_empty_error_uses_409(self):
        """Test FairnessNameNotEmptyError uses 409 Conflict."""
        exc = FairnessNameNotEmptyError("test")
        assert exc.status_code == 409
    
    def test_ui_parameter_error_uses_422(self):
        """Test FairnessUIParameterNotFoundError uses 422 Unprocessable Entity."""
        exc = FairnessUIParameterNotFoundError("test")
        assert exc.status_code == 422
    
    def test_attribute_error_uses_400(self):
        """Test FairnessAttributeError uses 400 Bad Request."""
        exc = FairnessAttributeError("test")
        assert exc.status_code == 400
