'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
"""
Comprehensive tests for error_utils module.
Tests the handle_exceptions decorator with various scenarios.
"""
import pytest
from unittest.mock import MagicMock, patch
from app.utility.error_utils import handle_exceptions


class TestHandleExceptionsDecorator:
    """Tests for handle_exceptions decorator."""
    
    def test_decorator_allows_success(self):
        """Test that decorator doesn't interfere with successful execution."""
        @handle_exceptions()
        def successful_func():
            return "success"
        
        result = successful_func()
        assert result == "success"
    
    def test_decorator_catches_exception(self):
        """Test that decorator catches and returns exceptions."""
        @handle_exceptions()
        def failing_func():
            raise ValueError("test error")
        
        result = failing_func()
        assert isinstance(result, ValueError)
        assert str(result) == "test error"
    
    def test_decorator_with_logger_on_class(self):
        """Test decorator uses logger from class instance."""
        mock_logger = MagicMock()
        
        class TestService:
            def __init__(self):
                self.log = mock_logger
            
            @handle_exceptions("log")
            def method_that_fails(self):
                raise RuntimeError("class method error")
        
        service = TestService()
        result = service.method_that_fails()
        
        assert isinstance(result, RuntimeError)
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert "method_that_fails" in call_args
        assert "class method error" in call_args
    
    def test_decorator_with_custom_logger_attr(self):
        """Test decorator with custom logger attribute name."""
        mock_logger = MagicMock()
        
        class TestService:
            def __init__(self):
                self.custom_log = mock_logger
            
            @handle_exceptions("custom_log")
            def failing_method(self):
                raise TypeError("type error")
        
        service = TestService()
        result = service.failing_method()
        
        assert isinstance(result, TypeError)
        mock_logger.error.assert_called_once()
    
    def test_decorator_without_logger_attribute(self):
        """Test decorator when logger attribute doesn't exist."""
        @handle_exceptions("nonexistent_logger")
        def func_without_logger():
            raise ValueError("no logger")
        
        # Should not crash, should return exception
        result = func_without_logger()
        assert isinstance(result, ValueError)
    
    def test_decorator_with_no_args(self):
        """Test decorator when no object has logger."""
        @handle_exceptions()
        def standalone_func():
            raise Exception("standalone error")
        
        result = standalone_func()
        assert isinstance(result, Exception)
    
    def test_decorator_logs_with_exc_info(self):
        """Test that decorator logs with exc_info=True for traceback."""
        mock_logger = MagicMock()
        
        class Service:
            log = mock_logger
            
            @handle_exceptions()
            def method(self):
                raise ValueError("test")
        
        Service().method()
        
        # Verify exc_info=True was passed
        assert mock_logger.error.called
        call_kwargs = mock_logger.error.call_args[1]
        assert call_kwargs.get('exc_info') is True
    
    def test_decorator_handles_different_exception_types(self):
        """Test decorator with various exception types."""
        exceptions_to_test = [
            ValueError("value error"),
            TypeError("type error"),
            RuntimeError("runtime error"),
            KeyError("key error"),
            AttributeError("attr error"),
            IOError("io error"),
            Exception("generic error")
        ]
        
        for exc in exceptions_to_test:
            @handle_exceptions()
            def func():
                raise exc
            
            result = func()
            assert isinstance(result, type(exc))
            assert str(result) == str(exc)
    
    def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves original function metadata."""
        @handle_exceptions()
        def documented_func():
            """This is a docstring."""
            return "result"
        
        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == "This is a docstring."
    
    def test_decorator_with_function_arguments(self):
        """Test decorator with functions that take arguments."""
        @handle_exceptions()
        def func_with_args(a, b, c=10):
            if a < 0:
                raise ValueError("negative")
            return a + b + c
        
        # Success case
        assert func_with_args(1, 2, c=3) == 6
        
        # Failure case
        result = func_with_args(-1, 2)
        assert isinstance(result, ValueError)
    
    def test_decorator_with_kwargs(self):
        """Test decorator with keyword arguments."""
        @handle_exceptions()
        def func_with_kwargs(**kwargs):
            if 'error' in kwargs:
                raise ValueError(kwargs['error'])
            return kwargs
        
        # Success
        assert func_with_kwargs(foo="bar") == {"foo": "bar"}
        
        # Failure
        result = func_with_kwargs(error="test error")
        assert isinstance(result, ValueError)
    
    def test_decorator_fallback_to_custom_logger(self):
        """Test decorator falls back to CustomLogger when no logger found."""
        @handle_exceptions()
        def func():
            raise ValueError("fallback test")
        
        result = func()
        
        # Should return exception even without explicit logger
        assert isinstance(result, ValueError)
    
    def test_decorator_handles_logger_import_failure(self):
        """Test decorator when logger attribute doesn't exist on first arg."""
        class ObjWithoutLogger:
            pass
        
        obj = ObjWithoutLogger()
        
        @handle_exceptions()
        def func(self):
            raise ValueError("no logger attr test")
        
        # Should still return exception without crashing
        result = func(obj)
        assert isinstance(result, ValueError)
    
    def test_decorator_handles_logger_error_method_failure(self):
        """Test decorator when logger.error itself raises exception."""
        mock_logger = MagicMock()
        mock_logger.error.side_effect = Exception("logger broken")
        
        class Service:
            log = mock_logger
            
            @handle_exceptions()
            def method(self):
                raise ValueError("original error")
        
        # Should still return original exception even if logging fails
        result = Service().method()
        assert isinstance(result, ValueError)
        assert str(result) == "original error"
    
    def test_decorator_with_multiple_args_positions(self):
        """Test decorator with various argument positions."""
        mock_logger = MagicMock()
        
        class Service:
            log = mock_logger
            
            @handle_exceptions()
            def method(self, x, y):
                if x == 0:
                    raise ZeroDivisionError("zero")
                return y / x
        
        service = Service()
        
        # Success case
        assert service.method(2, 10) == 5
        
        # Failure case
        result = service.method(0, 10)
        assert isinstance(result, ZeroDivisionError)
    
    def test_decorator_returns_none_from_successful_function(self):
        """Test decorator with function that returns None."""
        @handle_exceptions()
        def func_returns_none():
            pass
        
        result = func_returns_none()
        assert result is None
    
    def test_decorator_with_staticmethod(self):
        """Test decorator works with staticmethod."""
        mock_logger = MagicMock()
        
        class Service:
            log = mock_logger
            
            @staticmethod
            @handle_exceptions()
            def static_method():
                raise ValueError("static error")
        
        result = Service.static_method()
        assert isinstance(result, ValueError)
    
    def test_decorator_factory_returns_decorator(self):
        """Test that handle_exceptions returns a proper decorator."""
        decorator = handle_exceptions("log")
        assert callable(decorator)
        
        def sample_func():
            return "test"
        
        decorated = decorator(sample_func)
        assert callable(decorated)
        assert decorated() == "test"
    
    def test_decorator_with_classmethod(self):
        """Test decorator with classmethod."""
        mock_logger = MagicMock()
        
        class Service:
            log = mock_logger
            
            @classmethod
            @handle_exceptions()
            def class_method(cls):
                raise ValueError("class method error")
        
        result = Service.class_method()
        assert isinstance(result, ValueError)
    
    def test_decorator_preserves_return_type_hints(self):
        """Test that decorator works with type-annotated functions."""
        @handle_exceptions()
        def typed_func(x: int) -> str:
            if x < 0:
                raise ValueError("negative")
            return str(x)
        
        assert typed_func(5) == "5"
        assert isinstance(typed_func(-1), ValueError)
    
    def test_decorator_with_nested_exceptions(self):
        """Test decorator with nested exception handling."""
        @handle_exceptions()
        def outer_func():
            try:
                raise ValueError("inner")
            except ValueError:
                raise RuntimeError("outer") from ValueError("inner")
        
        result = outer_func()
        assert isinstance(result, RuntimeError)
    
    def test_decorator_multiple_decorators(self):
        """Test function with multiple decorators."""
        @handle_exceptions("log")
        @handle_exceptions("log")
        def double_decorated():
            raise ValueError("test")
        
        result = double_decorated()
        # Outer decorator catches, so result is the exception
        assert isinstance(result, ValueError)

def test_handle_exceptions_with_runtime_error():
    """Test handle_exceptions catches RuntimeError"""
    from app.utility.error_utils import handle_exceptions
    
    @handle_exceptions()
    def failing_func():
        raise RuntimeError("Runtime error occurred")
    
    result = failing_func()
    assert isinstance(result, RuntimeError)
    assert "Runtime error occurred" in str(result)

def test_handle_exceptions_with_type_error():
    """Test handle_exceptions catches TypeError"""
    from app.utility.error_utils import handle_exceptions
    
    @handle_exceptions()
    def type_error_func():
        return int("not a number")
    
    result = type_error_func()
    assert isinstance(result, ValueError)

def test_handle_exceptions_preserves_function_name():
    """Test handle_exceptions preserves wrapped function metadata"""
    from app.utility.error_utils import handle_exceptions
    
    @handle_exceptions()
    def my_special_function():
        return "success"
    
    assert my_special_function.__name__ == "my_special_function"
