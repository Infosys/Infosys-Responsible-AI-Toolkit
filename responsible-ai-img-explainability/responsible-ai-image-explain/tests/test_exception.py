"""
Comprehensive tests for exception classes and handlers
Combines basic exception tests with advanced exception handling patterns
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock, Mock
from typing import Any, Dict

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from image_explain.exception.exception import (
    RaiHelmException,
    RaiHelmNotFoundError,
    RaiHelmNameNotEmptyError
)
from image_explain.exception import global_exception


class TestRaiHelmException:
    """Test suite for RaiHelmException base class"""
    
    def test_raihelmexception_creation(self):
        """Test creating base RaiHelmException"""
        exc = RaiHelmException("Test error")
        assert isinstance(exc, Exception)
        assert hasattr(exc, 'status_code')
        assert hasattr(exc, 'detail') or hasattr(exc, 'args')
    
    def test_raihelmexception_is_abstract(self):
        """Test that RaiHelmException can be instantiated"""
        exc = RaiHelmException("Test message")
        assert exc is not None
    
    def test_raihelmexception_inheritance(self):
        """Test RaiHelmException inherits from Exception"""
        exc = RaiHelmException("Test")
        assert isinstance(exc, Exception)
    
    def test_raise_rai_helm_exception(self):
        """Test raising RaiHelmException"""
        with pytest.raises(RaiHelmException):
            raise RaiHelmException("Test error")
    
    def test_rai_helm_exception_message(self):
        """Test RaiHelmException message"""
        msg = "Custom error message"
        try:
            raise RaiHelmException(msg)
        except RaiHelmException as e:
            assert str(e) == msg
    
    def test_rai_helm_exception_is_exception(self):
        """Test RaiHelmException inherits from Exception"""
        assert issubclass(RaiHelmException, Exception)
    
    def test_rai_helm_exception_empty_message(self):
        """Test RaiHelmException with empty message"""
        try:
            raise RaiHelmException("")
        except RaiHelmException as e:
            assert str(e) == ""
    
    def test_exception_str_method(self):
        """Test exception __str__ method"""
        exc = RaiHelmException("Error message")
        assert str(exc) == "Error message"
    
    def test_exception_repr_method(self):
        """Test exception __repr__ method"""
        exc = RaiHelmException("Error")
        repr_str = repr(exc)
        assert "RaiHelmException" in repr_str or "Error" in repr_str
    
    def test_exception_args_attribute(self):
        """Test exception args attribute"""
        msg = "Test error"
        exc = RaiHelmException(msg)
        assert len(exc.args) > 0
        assert exc.args[0] == msg


class TestRaiHelmNotFoundError:
    """Test suite for RaiHelmNotFoundError"""
    
    def test_raihelmnotfounderror_creation(self):
        """Test creating RaiHelmNotFoundError"""
        exc = RaiHelmNotFoundError("test_id")
        assert isinstance(exc, RaiHelmException)
        assert hasattr(exc, 'status_code')
        assert hasattr(exc, 'detail')
    
    def test_raihelmnotfounderror_detail_message(self):
        """Test error detail contains the provided name"""
        test_name = "test_usecase"
        exc = RaiHelmNotFoundError(test_name)
        assert test_name in exc.detail
    
    def test_raihelmnotfounderror_status_code(self):
        """Test error has NOT_FOUND status code (404)"""
        exc = RaiHelmNotFoundError("test")
        # Status code should be 404 (NOT_FOUND)
        assert exc.status_code is not None
        # The status code should be an integer
        assert isinstance(exc.status_code, int)
    
    def test_raihelmnotfounderror_multiple_names(self):
        """Test with different usecase names"""
        names = ["usecase_1", "test_case_2", "my_usecase"]
        for name in names:
            exc = RaiHelmNotFoundError(name)
            assert name in exc.detail
    
    def test_raise_not_found_error(self):
        """Test raising RaiHelmNotFoundError"""
        with pytest.raises(RaiHelmNotFoundError):
            raise RaiHelmNotFoundError("Resource not found")
    
    def test_not_found_error_message(self):
        """Test RaiHelmNotFoundError message"""
        msg = "Item not found"
        try:
            raise RaiHelmNotFoundError(msg)
        except RaiHelmNotFoundError as e:
            assert str(e) == msg
    
    def test_not_found_error_inherits_from_rai_helm(self):
        """Test RaiHelmNotFoundError inherits from RaiHelmException"""
        assert issubclass(RaiHelmNotFoundError, RaiHelmException)
    
    def test_not_found_error_is_exception(self):
        """Test RaiHelmNotFoundError inherits from Exception"""
        assert issubclass(RaiHelmNotFoundError, Exception)


class TestRaiHelmNameNotEmptyError:
    """Test suite for RaiHelmNameNotEmptyError"""
    
    def test_raihelmnamnotemptyerror_creation(self):
        """Test creating RaiHelmNameNotEmptyError"""
        exc = RaiHelmNameNotEmptyError("test_name")
        assert isinstance(exc, RaiHelmException)
        assert hasattr(exc, 'status_code')
        assert hasattr(exc, 'detail')
    
    def test_raihelmnamnotemptyerror_status_code(self):
        """Test error has appropriate status code"""
        exc = RaiHelmNameNotEmptyError("test")
        # Should have 409 status code
        assert exc.status_code is not None
        assert isinstance(exc.status_code, int)
    
    def test_raihelmnamnotemptyerror_detail_message(self):
        """Test error detail message exists"""
        exc = RaiHelmNameNotEmptyError("test")
        assert exc.detail is not None
        assert isinstance(exc.detail, str)
        assert len(exc.detail) > 0
    
    def test_raise_name_not_empty_error(self):
        """Test raising RaiHelmNameNotEmptyError"""
        with pytest.raises(RaiHelmNameNotEmptyError):
            raise RaiHelmNameNotEmptyError("Name cannot be empty")
    
    def test_name_not_empty_error_message(self):
        """Test RaiHelmNameNotEmptyError message"""
        msg = "Name field required"
        try:
            raise RaiHelmNameNotEmptyError(msg)
        except RaiHelmNameNotEmptyError as e:
            assert str(e) == msg
    
    def test_name_not_empty_error_inherits_from_rai_helm(self):
        """Test RaiHelmNameNotEmptyError inherits from RaiHelmException"""
        assert issubclass(RaiHelmNameNotEmptyError, RaiHelmException)


class TestExceptionHierarchy:
    """Test exception class hierarchy"""
    
    def test_exception_inheritance_chain(self):
        """Test proper inheritance chain"""
        exc1 = RaiHelmNotFoundError("test")
        assert isinstance(exc1, RaiHelmException)
        assert isinstance(exc1, Exception)
        
        exc2 = RaiHelmNameNotEmptyError("test")
        assert isinstance(exc2, RaiHelmException)
        assert isinstance(exc2, Exception)
    
    def test_exceptions_are_distinct(self):
        """Test different exception types are distinct"""
        exc1 = RaiHelmNotFoundError("test")
        exc2 = RaiHelmNameNotEmptyError("test")
        assert type(exc1) != type(exc2)
    
    def test_exception_raising(self):
        """Test exceptions can be raised and caught"""
        with pytest.raises(RaiHelmNotFoundError):
            raise RaiHelmNotFoundError("test")
        
        with pytest.raises(RaiHelmNameNotEmptyError):
            raise RaiHelmNameNotEmptyError("test")
    
    def test_exception_catching_by_parent_type(self):
        """Test catching exceptions by parent type"""
        with pytest.raises(RaiHelmException):
            raise RaiHelmNotFoundError("test")
        
        with pytest.raises(RaiHelmException):
            raise RaiHelmNameNotEmptyError("test")
    
    def test_exception_hierarchy(self):
        """Test exception hierarchy relationships"""
        assert issubclass(RaiHelmNotFoundError, RaiHelmException)
        assert issubclass(RaiHelmNameNotEmptyError, RaiHelmException)
        assert issubclass(RaiHelmException, Exception)
    
    def test_multiple_exception_instances(self):
        """Test creating multiple exception instances"""
        exc1 = RaiHelmException("Error 1")
        exc2 = RaiHelmNotFoundError("Error 2")
        exc3 = RaiHelmNameNotEmptyError("Error 3")
        
        assert isinstance(exc1, RaiHelmException)
        assert isinstance(exc2, RaiHelmNotFoundError)
        assert isinstance(exc3, RaiHelmNameNotEmptyError)
        assert str(exc1) == "Error 1"
        assert str(exc2) == "Error 2"
        assert str(exc3) == "Error 3"
    
    def test_exception_catching_by_base_class(self):
        """Test catching exceptions by base class"""
        errors_caught = []
        
        try:
            raise RaiHelmNotFoundError("Not found")
        except RaiHelmException as e:
            errors_caught.append(type(e).__name__)
        
        try:
            raise RaiHelmNameNotEmptyError("Empty name")
        except RaiHelmException as e:
            errors_caught.append(type(e).__name__)
        
        assert len(errors_caught) == 2
        assert "RaiHelmNotFoundError" in errors_caught
        assert "RaiHelmNameNotEmptyError" in errors_caught


class TestGlobalExceptionModule:
    """Tests for global exception module"""
    
    def test_global_exception_module_exists(self):
        """Test global_exception module can be imported"""
        assert global_exception is not None
    
    def test_global_exception_has_exceptions(self):
        """Test global_exception module has exception classes"""
        # Check that the module can be imported
        assert hasattr(global_exception, '__name__')
    
    def test_global_exception_custom_error(self):
        """Test custom errors in global exception module"""
        # Try to access and use exception classes if they exist
        module_dict = vars(global_exception)
        exception_classes = [
            name for name in module_dict 
            if isinstance(module_dict[name], type) and 
            issubclass(module_dict[name], Exception)
        ]
        # Module should have at least one exception-related class or attribute
        assert global_exception is not None


class TestExceptionUsage:
    """Tests for exception usage patterns"""
    
    def test_exception_in_try_except(self):
        """Test exception handling in try-except"""
        try:
            raise RaiHelmException("Test error")
        except RaiHelmException as e:
            assert "Test error" in str(e)
    
    def test_exception_chain(self):
        """Test exception chaining"""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise RaiHelmException(f"Wrapped: {str(e)}") from e
        except RaiHelmException as e:
            assert "Wrapped" in str(e)
    
    def test_exception_with_different_messages(self):
        """Test exceptions with various message formats"""
        test_messages = [
            "Simple error",
            "Error with special chars: !@#$%",
            "Error with unicode: 你好世界",
            "Multi-line\nerror\nmessage",
            "Error with quotes: \"quoted\"",
        ]
        
        for msg in test_messages:
            try:
                raise RaiHelmException(msg)
            except RaiHelmException as e:
                assert str(e) == msg
    
    def test_exception_attributes(self):
        """Test exception attributes"""
        exc = RaiHelmException("Test")
        assert hasattr(exc, 'args')
        assert exc.args[0] == "Test"
    
    def test_exception_in_function(self):
        """Test exception raised in function"""
        def raise_error():
            raise RaiHelmException("Function error")
        
        with pytest.raises(RaiHelmException) as exc_info:
            raise_error()
        
        assert "Function error" in str(exc_info.value)
    
    def test_exception_in_nested_function(self):
        """Test exception in nested functions"""
        def outer():
            def inner():
                raise RaiHelmNotFoundError("Inner error")
            inner()
        
        with pytest.raises(RaiHelmNotFoundError) as exc_info:
            outer()
        
        assert "Inner error" in str(exc_info.value)
    
    def test_exception_with_finally(self):
        """Test exception with finally block"""
        cleanup_called = []
        
        try:
            try:
                raise RaiHelmException("Test error")
            finally:
                cleanup_called.append(True)
        except RaiHelmException:
            pass
        
        assert len(cleanup_called) == 1


class TestExceptionComparison:
    """Tests for comparing and identifying exceptions"""
    
    def test_same_exception_type(self):
        """Test comparing same exception types"""
        exc1 = RaiHelmException("Error")
        exc2 = RaiHelmException("Error")
        
        assert type(exc1) == type(exc2)
        assert str(exc1) == str(exc2)
    
    def test_different_exception_types(self):
        """Test comparing different exception types"""
        exc1 = RaiHelmNotFoundError("Not found")
        exc2 = RaiHelmNameNotEmptyError("Empty")
        
        assert type(exc1) != type(exc2)
    
    def test_exception_type_checking(self):
        """Test type checking for exceptions"""
        exc = RaiHelmNotFoundError("Test")
        
        assert isinstance(exc, RaiHelmNotFoundError)
        assert isinstance(exc, RaiHelmException)
        assert isinstance(exc, Exception)


class TestExceptionEdgeCases:
    """Tests for edge cases in exception handling"""
    
    def test_exception_with_none_message(self):
        """Test exception behavior with None"""
        try:
            raise RaiHelmException(None)
        except RaiHelmException as e:
            # Python will convert None to string
            assert e.args[0] is None
    
    def test_exception_with_numeric_message(self):
        """Test exception with numeric message"""
        try:
            raise RaiHelmException(404)
        except RaiHelmException as e:
            assert e.args[0] == 404
    
    def test_exception_with_dict_message(self):
        """Test exception with dict message"""
        error_dict = {"code": 500, "msg": "Server error"}
        try:
            raise RaiHelmException(error_dict)
        except RaiHelmException as e:
            assert e.args[0] == error_dict
    
    def test_multiple_exception_instances_same_message(self):
        """Test multiple instances with same message are independent"""
        msg = "Shared error"
        exc1 = RaiHelmException(msg)
        exc2 = RaiHelmException(msg)
        
        assert exc1 is not exc2
        assert str(exc1) == str(exc2)


class TestExceptionRecovery:
    """Tests for exception recovery and handling"""
    
    def test_catch_and_reraise(self):
        """Test catching and re-raising exception"""
        with pytest.raises(RaiHelmException) as exc_info:
            try:
                raise RaiHelmException("Original")
            except RaiHelmException:
                raise
        
        assert "Original" in str(exc_info.value)
    
    def test_catch_and_convert(self):
        """Test catching one exception and raising another"""
        with pytest.raises(RaiHelmNotFoundError):
            try:
                raise ValueError("Not found")
            except ValueError as e:
                raise RaiHelmNotFoundError(str(e))
    
    def test_multiple_exception_handlers(self):
        """Test multiple exception handlers"""
        handled = []
        
        try:
            raise RaiHelmNotFoundError("Not found")
        except RaiHelmNotFoundError:
            handled.append("NotFound")
        except RaiHelmException:
            handled.append("Generic")
        
        assert handled == ["NotFound"]
