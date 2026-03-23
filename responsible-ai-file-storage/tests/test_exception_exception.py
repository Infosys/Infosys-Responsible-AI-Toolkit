"""
MIT License
https://mit-license.org/
Copyright  2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import pytest
import sys
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.datastructures import Headers

sys.path.insert(0, str(Path(__file__).parent.parent))
from exception.exception import (
    CustomHTTPException,
    AzureBlobException,
    RegisterExceptions,
    http_exception_handler,
    catch_exceptions_middleware
)

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_request():
    """Fixture to create a mock FastAPI Request object."""
    request = Mock(spec=Request)
    request.url = Mock()
    request.url.path = "/test/path"
    request.method = "GET"
    request.headers = Headers({})
    return request

@pytest.fixture
def sample_error_dict():
    """Fixture for sample error dictionary."""
    return {
        "errorCode": "ERR001",
        "errorType": "ValidationError",
        "timestamp": "2025-12-26T12:00:00"
    }

@pytest.fixture
def fastapi_app():
    """Fixture to create a FastAPI application for testing."""
    app = FastAPI()
    return app

@pytest.fixture
def mock_call_next():
    """Fixture for mocking call_next in middleware."""
    async def _call_next(request):
        return JSONResponse(content={"status": "success"}, status_code=200)
    return _call_next

@pytest.fixture
def mock_call_next_with_exception():
    """Fixture for call_next that raises an exception."""
    async def _call_next(request):
        raise Exception("Test exception in middleware")
    return _call_next

# ============================================================================
# CUSTOMHTTPEXCEPTION TESTS
# ============================================================================

class TestCustomHTTPException:
    """Test CustomHTTPException class functionality."""
    
    def test_initialization_basic(self, sample_error_dict):
        """Test basic initialization of CustomHTTPException."""
        exc = CustomHTTPException(
            error_dict=sample_error_dict,
            name="TestError",
            msg="Test error message"
        )
        assert exc.error_dict == sample_error_dict
        assert exc.error_dict["errorMessage"] == "TestError"
        assert exc.msg == "Test error message"
    
    def test_error_dict_mutation(self, sample_error_dict):
        """Test that errorMessage is added to error_dict."""
        original_keys = set(sample_error_dict.keys())
        exc = CustomHTTPException(
            error_dict=sample_error_dict,
            name="MutationTest",
            msg="Testing mutation"
        )
        assert "errorMessage" in exc.error_dict
        assert exc.error_dict["errorMessage"] == "MutationTest"
        assert len(exc.error_dict) == len(original_keys) + 1
    
    def test_empty_error_dict(self):
        """Test CustomHTTPException with empty error dictionary."""
        exc = CustomHTTPException(
            error_dict={},
            name="EmptyDictError",
            msg="Empty dict test"
        )
        assert exc.error_dict == {"errorMessage": "EmptyDictError"}
        assert exc.msg == "Empty dict test"
    
    def test_exception_inheritance(self):
        """Test that CustomHTTPException inherits from Exception."""
        exc = CustomHTTPException({}, "Test", "msg")
        assert isinstance(exc, Exception)
    
    def test_special_characters_in_message(self):
        """Test handling of special characters in error messages."""
        exc = CustomHTTPException(
            error_dict={},
            name="Special@#$%",
            msg="Message with special chars: <>?/"
        )
        assert exc.error_dict["errorMessage"] == "Special@#$%"
        assert "<>?/" in exc.msg
    
    def test_unicode_in_error_dict(self):
        """Test handling of Unicode characters in error dictionary."""
        error_dict = {"field": "测试", "value": "テスト"}
        exc = CustomHTTPException(
            error_dict=error_dict,
            name="UnicodeError",
            msg="Unicode message: "
        )
        assert "测试" in str(exc.error_dict.values())
        assert "" in exc.msg
    
    def test_long_error_message(self):
        """Test CustomHTTPException with very long error message."""
        long_msg = "A" * 10000
        exc = CustomHTTPException({}, "LongMsg", long_msg)
        assert len(exc.msg) == 10000
        assert exc.msg == long_msg
    
    def test_error_dict_with_nested_structures(self):
        """Test error_dict with nested dictionaries and lists."""
        complex_dict = {
            "nested": {"level1": {"level2": "value"}},
            "list": [1, 2, 3],
            "mixed": {"arr": [{"key": "val"}]}
        }
        exc = CustomHTTPException(complex_dict, "Nested", "msg")
        assert exc.error_dict["nested"]["level1"]["level2"] == "value"
        assert exc.error_dict["list"] == [1, 2, 3]


# ============================================================================
# HTTP_EXCEPTION_HANDLER TESTS
# ============================================================================

class TestHttpExceptionHandler:
    """Test http_exception_handler async function."""
    
    @pytest.mark.asyncio
    async def test_handler_returns_json_response(self, mock_request, sample_error_dict):
        """Test that handler returns JSONResponse."""
        exc = CustomHTTPException(sample_error_dict, "TestError", "test message")
        response = await http_exception_handler(mock_request, exc)
        assert isinstance(response, JSONResponse)
    
    @pytest.mark.asyncio
    async def test_handler_status_code_500(self, mock_request, sample_error_dict):
        """Test that handler returns status code 500."""
        exc = CustomHTTPException(sample_error_dict, "TestError", "test message")
        response = await http_exception_handler(mock_request, exc)
        assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_handler_response_content(self, mock_request, sample_error_dict):
        """Test that handler response contains expected message format."""
        exc = CustomHTTPException(sample_error_dict, "TestError", "custom error")
        response = await http_exception_handler(mock_request, exc)
        # Check response body structure
        assert response.body is not None
        body_json = json.loads(response.body.decode())
        assert "message" in body_json
        assert "Oops!" in body_json["message"]
        assert "custom error" in body_json["message"]
    
    @pytest.mark.asyncio
    async def test_handler_with_empty_message(self, mock_request):
        """Test handler with empty error message."""
        exc = CustomHTTPException({}, "EmptyMsg", "")
        response = await http_exception_handler(mock_request, exc)
        body_json = json.loads(response.body.decode())
        assert body_json["message"] == "Oops! "
    
    @pytest.mark.asyncio
    async def test_handler_with_special_characters(self, mock_request):
        """Test handler with special characters in message."""
        exc = CustomHTTPException({}, "Special", "Error: <>&\"'")
        response = await http_exception_handler(mock_request, exc)
        body_json = json.loads(response.body.decode())
        assert "Error:" in body_json["message"]
    
    @pytest.mark.asyncio
    async def test_handler_multiple_calls(self, mock_request, sample_error_dict):
        """Test that handler can be called multiple times consistently."""
        exc1 = CustomHTTPException(sample_error_dict, "Error1", "msg1")
        exc2 = CustomHTTPException(sample_error_dict, "Error2", "msg2")
        
        response1 = await http_exception_handler(mock_request, exc1)
        response2 = await http_exception_handler(mock_request, exc2)
        
        assert response1.status_code == response2.status_code == 500
        body1 = json.loads(response1.body.decode())
        body2 = json.loads(response2.body.decode())
        assert "msg1" in body1["message"]
        assert "msg2" in body2["message"]


# ============================================================================
# CATCH_EXCEPTIONS_MIDDLEWARE TESTS
# ============================================================================

class TestCatchExceptionsMiddleware:
    """Test catch_exceptions_middleware async function."""
    
    @pytest.mark.asyncio
    @patch("exception.exception.log")
    async def test_middleware_success_path(self, mock_log, mock_request, mock_call_next):
        """Test middleware with successful request processing."""
        response = await catch_exceptions_middleware(mock_request, mock_call_next)
        assert response.status_code == 200
        mock_log.info.assert_called_with("inside catch_exceptions_middleware")
    
    @pytest.mark.asyncio
    @patch("exception.exception.logger")
    @patch("exception.exception.log")
    async def test_middleware_catches_exception(self, mock_log, mock_logger, mock_request, mock_call_next_with_exception):
        """Test middleware catches and handles exceptions."""
        response = await catch_exceptions_middleware(mock_request, mock_call_next_with_exception)
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        mock_log.info.assert_any_call("inside catch_exceptions_middleware exception")
        mock_logger.exception.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("exception.exception.logger")
    @patch("exception.exception.log")
    async def test_middleware_logs_exception(self, mock_log, mock_logger, mock_request):
        """Test that middleware logs exceptions properly."""
        async def failing_call_next(request):
            raise ValueError("Test value error")
        
        response = await catch_exceptions_middleware(mock_request, failing_call_next)
        assert mock_logger.exception.called
        args = mock_logger.exception.call_args[0]
        assert isinstance(args[0], ValueError)
    
    @pytest.mark.asyncio
    @patch("exception.exception.log")
    async def test_middleware_returns_json_response_on_error(self, mock_log, mock_request, mock_call_next_with_exception):
        """Test middleware returns JSONResponse on exception."""
        response = await catch_exceptions_middleware(mock_request, mock_call_next_with_exception)
        assert isinstance(response, JSONResponse)
        body = json.loads(response.body.decode())
        assert body == "Internal server error occured"
    
    @pytest.mark.asyncio
    @patch("exception.exception.log")
    async def test_middleware_with_different_exception_types(self, mock_log, mock_request):
        """Test middleware handles different exception types."""
        exceptions_to_test = [
            ValueError("value error"),
            TypeError("type error"),
            KeyError("key error"),
            RuntimeError("runtime error")
        ]
        
        for exc in exceptions_to_test:
            async def failing_call_next(request):
                raise exc
            
            response = await catch_exceptions_middleware(mock_request, failing_call_next)
            assert response.status_code == 500
            assert isinstance(response, JSONResponse)


# ============================================================================
# AZUREBLOBEXCEPTION TESTS
# ============================================================================

class TestAzureBlobException:
    """Test AzureBlobException class."""
    
    def test_initialization(self):
        """Test basic initialization of AzureBlobException."""
        exc = AzureBlobException("Azure blob error")
        assert exc.status_code == 500
        assert str(exc) == "Azure blob error"
    
    def test_inherits_from_exception(self):
        """Test that AzureBlobException inherits from Exception."""
        exc = AzureBlobException("test")
        assert isinstance(exc, Exception)
    
    def test_status_code_is_500(self):
        """Test that status_code is set to 500."""
        exc = AzureBlobException("error detail")
        assert exc.status_code == 500
    
    def test_empty_detail(self):
        """Test AzureBlobException with empty detail string."""
        exc = AzureBlobException("")
        assert exc.status_code == 500
        assert str(exc) == ""
    
    def test_long_detail_message(self):
        """Test with very long detail message."""
        long_detail = "A" * 5000
        exc = AzureBlobException(long_detail)
        assert len(str(exc)) == 5000
    
    def test_special_characters_in_detail(self):
        """Test detail with special characters."""
        detail = "Error: <>&\"' @#$%^&*()"
        exc = AzureBlobException(detail)
        assert str(exc) == detail
    
    def test_unicode_in_detail(self):
        """Test Unicode characters in detail."""
        detail = "Azure 错误: テストエラー "
        exc = AzureBlobException(detail)
        assert "错误" in str(exc)
    
    def test_multiline_detail(self):
        """Test multiline detail message."""
        detail = "Line 1\\nLine 2\\nLine 3"
        exc = AzureBlobException(detail)
        assert "Line 1" in str(exc)


# ============================================================================
# REGISTEREXCEPTIONS TESTS
# ============================================================================

class TestRegisterExceptions:
    """Test RegisterExceptions class."""
    
    def test_initialization(self, fastapi_app):
        """Test RegisterExceptions initialization."""
        reg = RegisterExceptions(fastapi_app)
        assert reg.app is fastapi_app
    
    def test_register_exception_handlers_returns_app(self, fastapi_app):
        """Test that register_exception_handlers returns the app."""
        reg = RegisterExceptions(fastapi_app)
        returned_app = reg.register_exception_handlers()
        assert returned_app is fastapi_app
    
    @patch.object(FastAPI, "add_exception_handler")
    def test_adds_custom_exception_handler(self, mock_add_handler, fastapi_app):
        """Test that CustomHTTPException handler is added."""
        reg = RegisterExceptions(fastapi_app)
        reg.register_exception_handlers()
        mock_add_handler.assert_called_once_with(CustomHTTPException, http_exception_handler)
    
    @patch.object(FastAPI, "middleware")
    def test_adds_middleware(self, mock_middleware, fastapi_app):
        """Test that catch_exceptions_middleware is added."""
        reg = RegisterExceptions(fastapi_app)
        reg.register_exception_handlers()
        mock_middleware.assert_called_once_with("http")
    
    def test_multiple_registrations(self, fastapi_app):
        """Test calling register_exception_handlers multiple times."""
        reg = RegisterExceptions(fastapi_app)
        app1 = reg.register_exception_handlers()
        app2 = reg.register_exception_handlers()
        assert app1 is app2 is fastapi_app
    
    def test_with_none_app(self):
        """Test initialization with None app."""
        reg = RegisterExceptions(None)
        assert reg.app is None


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for exception handling workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_exception_flow(self, mock_request, sample_error_dict):
        """Test complete flow from exception creation to handler response."""
        # Create exception
        exc = CustomHTTPException(sample_error_dict, "IntegrationError", "integration test")
        
        # Handle exception
        response = await http_exception_handler(mock_request, exc)
        
        # Verify complete flow
        assert response.status_code == 500
        body = json.loads(response.body.decode())
        assert "integration test" in body["message"]
        assert "errorMessage" in exc.error_dict
    
    @pytest.mark.asyncio
    @patch("exception.exception.log")
    async def test_middleware_to_handler_flow(self, mock_log, mock_request):
        """Test flow from middleware exception to error response."""
        async def failing_handler(request):
            raise CustomHTTPException({"code": "ERR"}, "MiddlewareError", "from middleware")
        
        response = await catch_exceptions_middleware(mock_request, failing_handler)
        assert response.status_code == 500
    
    def test_register_and_use_exceptions(self):
        """Test registering exception handlers on FastAPI app."""
        app = FastAPI()
        reg = RegisterExceptions(app)
        configured_app = reg.register_exception_handlers()
        
        assert configured_app is app
        # App should have exception handlers registered


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_custom_exception_with_none_values(self):
        """Test CustomHTTPException with None values."""
        exc = CustomHTTPException({"key": None}, "NoneError", None)
        assert exc.error_dict["key"] is None
        assert exc.msg is None
    
    @pytest.mark.asyncio
    async def test_handler_with_none_request(self, sample_error_dict):
        """Test handler with None request object."""
        exc = CustomHTTPException(sample_error_dict, "Test", "msg")
        response = await http_exception_handler(None, exc)
        assert response.status_code == 500
    
    def test_azure_exception_with_none_detail(self):
        """Test AzureBlobException with None detail."""
        exc = AzureBlobException(None)
        assert exc.status_code == 500
    
    @pytest.mark.asyncio
    @patch("exception.exception.log")
    async def test_middleware_with_async_exception(self, mock_log, mock_request):
        """Test middleware handling async exceptions."""
        async def async_failing(request):
            await asyncio_sleep(0.001)
            raise Exception("Async error")
        
        # Import asyncio for sleep
        import asyncio
        async def asyncio_sleep(seconds):
            await asyncio.sleep(seconds)
        
        response = await catch_exceptions_middleware(mock_request, async_failing)
        assert response.status_code == 500
    
    def test_error_dict_is_mutable(self):
        """Test that error_dict can be modified after exception creation."""
        exc = CustomHTTPException({"initial": "value"}, "Test", "msg")
        exc.error_dict["new_key"] = "new_value"
        assert exc.error_dict["new_key"] == "new_value"


# ============================================================================
# SECURITY TESTS
# ============================================================================

class TestSecurity:
    """Test security-related aspects of exception handling."""
    
    def test_no_code_execution_in_error_message(self):
        """Test that error messages don not execute code."""
        dangerous_msg = "__import__(os).system(echo hacked)"
        exc = CustomHTTPException({}, "SecurityTest", dangerous_msg)
        assert "__import__" in exc.msg
        # Message should be stored as string, not executed
    
    @pytest.mark.asyncio
    async def test_handler_sanitizes_output(self, mock_request):
        """Test that handler does not expose sensitive information."""
        sensitive_data = "password=secret123"
        exc = CustomHTTPException({"data": sensitive_data}, "Sensitive", "public msg")
        response = await http_exception_handler(mock_request, exc)
        body = json.loads(response.body.decode())
        # Only public message should be in response
        assert "public msg" in body["message"]
        assert "password" not in body["message"]
    
    def test_sql_injection_in_error_message(self):
        """Test handling of SQL injection attempts in error messages."""
        sql_injection = "'; DROP TABLE users; --"
        exc = CustomHTTPException({}, "SQLTest", sql_injection)
        assert exc.msg == sql_injection
        # Should be treated as plain string


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test performance aspects of exception handling."""
    
    @pytest.mark.asyncio
    @patch("exception.exception.log")
    async def test_middleware_performance_with_many_requests(self, mock_log, mock_request):
        """Test middleware performance with multiple requests."""
        async def fast_handler(request):
            return JSONResponse({"status": "ok"})
        
        responses = []
        for _ in range(100):
            response = await catch_exceptions_middleware(mock_request, fast_handler)
            responses.append(response)
        
        assert len(responses) == 100
        assert all(r.status_code == 200 for r in responses)
    
    def test_exception_creation_performance(self):
        """Test that exception creation is efficient."""
        exceptions = []
        for i in range(1000):
            exc = CustomHTTPException({"index": i}, f"Error{i}", f"msg{i}")
            exceptions.append(exc)
        
        assert len(exceptions) == 1000
        assert exceptions[0].error_dict["index"] == 0
        assert exceptions[999].error_dict["index"] == 999


# ============================================================================
# CODE QUALITY TESTS
# ============================================================================

class TestCodeQuality:
    """Test code quality indicators."""
    
    def test_custom_exception_has_required_attributes(self):
        """Test that CustomHTTPException has all required attributes."""
        exc = CustomHTTPException({}, "Test", "msg")
        assert hasattr(exc, "error_dict")
        assert hasattr(exc, "msg")
    
    def test_azure_exception_has_status_code(self):
        """Test that AzureBlobException has status_code attribute."""
        exc = AzureBlobException("test")
        assert hasattr(exc, "status_code")
        assert exc.status_code == 500
    
    def test_register_exceptions_has_app_attribute(self):
        """Test that RegisterExceptions stores app reference."""
        app = FastAPI()
        reg = RegisterExceptions(app)
        assert hasattr(reg, "app")
        assert reg.app is app
    
    @pytest.mark.asyncio
    async def test_handlers_are_async(self):
        """Test that exception handlers are async functions."""
        import inspect
        assert inspect.iscoroutinefunction(http_exception_handler)
        assert inspect.iscoroutinefunction(catch_exceptions_middleware)
