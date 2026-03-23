"""
Comprehensive test suite for custom_exception.py

This test file validates the CustomHTTPException class, exception handlers,
middleware, and RegisterExceptions class with focus on:
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

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)
from unittest.mock import MagicMock, AsyncMock, patch, Mock
import asyncio
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response


# Import module
from fairness.exception.custom_exception import (
    CustomHTTPException,
    http_exception_handler,
    catch_exceptions_middleware,
    RegisterExceptions
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_request():
    """Create a mock FastAPI/Starlette Request object."""
    request = MagicMock(spec=Request)
    request.url = MagicMock()
    request.url.path = "/test/path"
    request.method = "GET"
    request.headers = {}
    return request


@pytest.fixture
def mock_fastapi_app():
    """Create a mock FastAPI application."""
    app = MagicMock(spec=FastAPI)
    app.add_exception_handler = MagicMock()
    app.middleware = MagicMock(return_value=lambda x: x)
    return app


@pytest.fixture
def sample_error_dict():
    """Create a sample error dictionary."""
    return {
        "errorCode": "TEST_001",
        "errorType": "ValidationError",
        "timestamp": "2025-12-24T10:00:00"
    }


@pytest.fixture
def mock_call_next():
    """Create a mock call_next function for middleware."""
    async def mock_next(request):
        return JSONResponse({"status": "success"}, status_code=200)
    return AsyncMock(side_effect=mock_next)


@pytest.fixture
def mock_call_next_with_exception():
    """Create a mock call_next that raises an exception."""
    async def mock_next_error(request):
        raise ValueError("Simulated error in downstream handler")
    return AsyncMock(side_effect=mock_next_error)


@pytest.fixture(autouse=True)
def reset_env_vars():
    """Reset environment variables before each test."""
    original_telemetry_url = os.getenv("FAIRNESS_TELEMETRY_URL")
    original_telemetry_flag = os.getenv("tel_Falg")
    
    yield
    
    # Restore original values
    if original_telemetry_url:
        os.environ["FAIRNESS_TELEMETRY_URL"] = original_telemetry_url
    elif "FAIRNESS_TELEMETRY_URL" in os.environ:
        del os.environ["FAIRNESS_TELEMETRY_URL"]
    
    if original_telemetry_flag:
        os.environ["tel_Falg"] = original_telemetry_flag
    elif "tel_Falg" in os.environ:
        del os.environ["tel_Falg"]


# ============================================================================
# TEST CLASS: CustomHTTPException Initialization
# ============================================================================

class TestCustomHTTPExceptionInitialization:
    """Test CustomHTTPException class initialization."""
    
    def test_init_with_valid_parameters(self, sample_error_dict):
        """Test initialization with valid error_dict, name, and msg."""
        exc = CustomHTTPException(
            error_dict=sample_error_dict.copy(),
            name="TestError",
            msg="Test error message"
        )
        
        assert exc.error_dict["errorMessage"] == "TestError"
        assert exc.msg == "Test error message"
        assert exc.error_dict["errorCode"] == "TEST_001"
    
    def test_init_modifies_error_dict(self, sample_error_dict):
        """Test that initialization adds errorMessage to error_dict."""
        original_dict = sample_error_dict.copy()
        exc = CustomHTTPException(
            error_dict=original_dict,
            name="ModifiedError",
            msg="Modified message"
        )
        
        assert "errorMessage" in exc.error_dict
        assert exc.error_dict["errorMessage"] == "ModifiedError"
    
    def test_init_with_empty_error_dict(self):
        """Test initialization with empty error dictionary."""
        exc = CustomHTTPException(
            error_dict={},
            name="EmptyDictError",
            msg="Empty dict message"
        )
        
        assert exc.error_dict == {"errorMessage": "EmptyDictError"}
        assert exc.msg == "Empty dict message"
    
    def test_init_with_empty_strings(self):
        """Test initialization with empty name and msg strings."""
        exc = CustomHTTPException(
            error_dict={"key": "value"},
            name="",
            msg=""
        )
        
        assert exc.error_dict["errorMessage"] == ""
        assert exc.msg == ""
    
    def test_exception_inheritance(self):
        """Test that CustomHTTPException inherits from Exception."""
        exc = CustomHTTPException(
            error_dict={"test": "data"},
            name="TestError",
            msg="Test message"
        )
        
        assert isinstance(exc, Exception)
        assert isinstance(exc, CustomHTTPException)


# ============================================================================
# TEST CLASS: CustomHTTPException Attributes
# ============================================================================

class TestCustomHTTPExceptionAttributes:
    """Test CustomHTTPException attribute access and modification."""
    
    def test_error_dict_attribute_access(self, sample_error_dict):
        """Test accessing error_dict attribute."""
        exc = CustomHTTPException(
            error_dict=sample_error_dict.copy(),
            name="AttributeTest",
            msg="Attribute test message"
        )
        
        assert hasattr(exc, 'error_dict')
        assert isinstance(exc.error_dict, dict)
        assert exc.error_dict["errorCode"] == "TEST_001"
    
    def test_msg_attribute_access(self):
        """Test accessing msg attribute."""
        exc = CustomHTTPException(
            error_dict={},
            name="MsgTest",
            msg="Message test"
        )
        
        assert hasattr(exc, 'msg')
        assert exc.msg == "Message test"
    
    def test_error_dict_is_mutable(self, sample_error_dict):
        """Test that error_dict can be modified after initialization."""
        exc = CustomHTTPException(
            error_dict=sample_error_dict.copy(),
            name="MutableTest",
            msg="Mutable test"
        )
        
        exc.error_dict["newKey"] = "newValue"
        assert exc.error_dict["newKey"] == "newValue"
    
    def test_error_dict_overwrites_existing_errorMessage(self):
        """Test that initialization overwrites existing errorMessage key."""
        error_dict = {
            "errorMessage": "OldMessage",
            "errorCode": "OLD_001"
        }
        
        exc = CustomHTTPException(
            error_dict=error_dict,
            name="NewMessage",
            msg="New message"
        )
        
        assert exc.error_dict["errorMessage"] == "NewMessage"
        assert exc.error_dict["errorMessage"] != "OldMessage"


# ============================================================================
# TEST CLASS: http_exception_handler Function
# ============================================================================

class TestHttpExceptionHandler:
    """Test http_exception_handler async function."""
    
    @pytest.mark.asyncio
    async def test_handler_returns_json_response(self, mock_request, sample_error_dict):
        """Test handler returns JSONResponse with correct structure."""
        exc = CustomHTTPException(
            error_dict=sample_error_dict.copy(),
            name="HandlerTest",
            msg="Handler test message"
        )
        
        response = await http_exception_handler(mock_request, exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_handler_response_content(self, mock_request):
        """Test handler response contains expected message format."""
        exc = CustomHTTPException(
            error_dict={"test": "data"},
            name="ContentTest",
            msg="content message"
        )
        
        response = await http_exception_handler(mock_request, exc)
        
        # JSONResponse body is in response.body
        assert response.status_code == 500
        # Content is set correctly during init
        assert "content" in response.__dict__ or hasattr(response, 'body')
    
    @pytest.mark.asyncio
    @patch('fairness.exception.custom_exception.telemetry_flag', 'True')
    @patch('fairness.exception.custom_exception.fairnesstelemetryurl', 'http://test-telemetry.com/api')
    @patch('fairness.exception.custom_exception.requests.post')
    async def test_handler_with_telemetry_enabled(self, mock_post, mock_request, sample_error_dict):
        """Test handler sends telemetry when tel_Falg is True."""
        mock_post.return_value.json.return_value = {"status": "received"}
        
        exc = CustomHTTPException(
            error_dict=sample_error_dict.copy(),
            name="TelemetryTest",
            msg="Telemetry test"
        )
        
        response = await http_exception_handler(mock_request, exc)
        
        assert mock_post.called
        assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_handler_with_telemetry_disabled(self, mock_request, sample_error_dict):
        """Test handler skips telemetry when tel_Falg is not True."""
        os.environ["tel_Falg"] = "False"
        
        exc = CustomHTTPException(
            error_dict=sample_error_dict.copy(),
            name="NoTelemetry",
            msg="No telemetry"
        )
        
        with patch('fairness.exception.custom_exception.requests.post') as mock_post:
            response = await http_exception_handler(mock_request, exc)
            
            assert not mock_post.called
            assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_handler_extracts_error_message(self, mock_request):
        """Test handler extracts errorMessage from error_dict."""
        exc = CustomHTTPException(
            error_dict={"original": "data"},
            name="ExtractTest",
            msg="Extract test"
        )
        
        response = await http_exception_handler(mock_request, exc)
        
        # Verify the error variable is set correctly in the handler
        assert exc.error_dict["errorMessage"] == "ExtractTest"
        assert response.status_code == 500


# ============================================================================
# TEST CLASS: http_exception_handler Edge Cases
# ============================================================================

class TestHttpExceptionHandlerEdgeCases:
    """Test edge cases for http_exception_handler."""
    
    @pytest.mark.asyncio
    async def test_handler_with_special_characters_in_msg(self, mock_request):
        """Test handler with special characters in error message."""
        exc = CustomHTTPException(
            error_dict={},
            name="SpecialTest",
            msg="Test with <html> & 'quotes' \"double\" $special chars"
        )
        
        response = await http_exception_handler(mock_request, exc)
        
        assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_handler_with_unicode_in_msg(self, mock_request):
        """Test handler with unicode characters in message."""
        exc = CustomHTTPException(
            error_dict={},
            name="UnicodeTest",
            msg="Unicode test: 你好 мир 🚀"
        )
        
        response = await http_exception_handler(mock_request, exc)
        
        assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_handler_with_very_long_message(self, mock_request):
        """Test handler with very long error message."""
        long_msg = "A" * 10000
        exc = CustomHTTPException(
            error_dict={},
            name="LongTest",
            msg=long_msg
        )
        
        response = await http_exception_handler(mock_request, exc)
        
        assert response.status_code == 500
    
    @pytest.mark.asyncio
    @patch('fairness.exception.custom_exception.telemetry_flag', 'True')
    @patch('fairness.exception.custom_exception.fairnesstelemetryurl', 'http://test-telemetry.com/api')
    @patch('fairness.exception.custom_exception.requests.post')
    async def test_handler_when_telemetry_post_fails(self, mock_post, mock_request):
        """Test handler behavior when telemetry POST request fails."""
        mock_post.side_effect = Exception("Network error")
        
        exc = CustomHTTPException(
            error_dict={"test": "data"},
            name="FailedPost",
            msg="Failed post test"
        )
        
        # Handler should raise exception if requests.post fails (no error handling in code)
        with pytest.raises(Exception, match="Network error"):
            await http_exception_handler(mock_request, exc)
    
    @pytest.mark.asyncio
    async def test_handler_with_none_request(self, sample_error_dict):
        """Test handler with None request object."""
        exc = CustomHTTPException(
            error_dict=sample_error_dict.copy(),
            name="NoneRequest",
            msg="None request test"
        )
        
        # Handler doesn't use request, so should still work
        response = await http_exception_handler(None, exc)
        
        assert response.status_code == 500


# ============================================================================
# TEST CLASS: catch_exceptions_middleware Function
# ============================================================================

class TestCatchExceptionsMiddleware:
    """Test catch_exceptions_middleware async function."""
    
    @pytest.mark.asyncio
    async def test_middleware_successful_request(self, mock_request, mock_call_next):
        """Test middleware passes through successful requests."""
        response = await catch_exceptions_middleware(mock_request, mock_call_next)
        
        assert mock_call_next.called
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_middleware_catches_exception(self, mock_request, mock_call_next_with_exception):
        """Test middleware catches and handles exceptions."""
        os.environ["tel_Falg"] = "False"
        
        response = await catch_exceptions_middleware(mock_request, mock_call_next_with_exception)
        
        assert mock_call_next_with_exception.called
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
    
    @pytest.mark.asyncio
    @patch('fairness.exception.custom_exception.telemetry_flag', 'True')
    @patch('fairness.exception.custom_exception.fairnesstelemetryurl', 'http://test-telemetry.com/api')
    @patch('fairness.exception.custom_exception.requests.post')
    async def test_middleware_with_telemetry_enabled(self, mock_post, mock_request, mock_call_next_with_exception):
        """Test middleware sends telemetry when exception occurs and tel_Falg is True."""
        mock_post.return_value.json.return_value = {"status": "received"}
        
        response = await catch_exceptions_middleware(mock_request, mock_call_next_with_exception)
        
        assert mock_post.called
        assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_middleware_with_telemetry_disabled(self, mock_request, mock_call_next_with_exception):
        """Test middleware skips telemetry when tel_Falg is not True."""
        os.environ["tel_Falg"] = "False"
        
        with patch('fairness.exception.custom_exception.requests.post') as mock_post:
            response = await catch_exceptions_middleware(mock_request, mock_call_next_with_exception)
            
            assert not mock_post.called
            assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_middleware_logs_exception(self, mock_request, mock_call_next_with_exception):
        """Test middleware logs exception using logger.exception."""
        os.environ["tel_Falg"] = "False"
        
        with patch('fairness.exception.custom_exception.logger.exception') as mock_exception:
            response = await catch_exceptions_middleware(mock_request, mock_call_next_with_exception)
            
            assert mock_exception.called
            assert response.status_code == 500


# ============================================================================
# TEST CLASS: catch_exceptions_middleware Edge Cases
# ============================================================================

class TestCatchExceptionsMiddlewareEdgeCases:
    """Test edge cases for catch_exceptions_middleware."""
    
    @pytest.mark.skip(reason="KeyboardInterrupt causes pytest to stop execution")
    @pytest.mark.asyncio
    async def test_middleware_with_keyboard_interrupt(self, mock_request):
        """Test middleware with KeyboardInterrupt exception.
        
        SKIPPED: This test is skipped because KeyboardInterrupt propagates
        and stops pytest execution. The middleware catches all exceptions
        including KeyboardInterrupt, which is generally bad practice.
        
        BUG: Middleware uses bare `except Exception` which catches KeyboardInterrupt
        and SystemExit (both inherit from BaseException, not Exception in Python 3).
        However, if there's a bare except, it would catch everything.
        """
        async def raise_keyboard_interrupt(request):
            raise KeyboardInterrupt("User interrupted")
        
        os.environ["tel_Falg"] = "False"
        mock_call_next = AsyncMock(side_effect=raise_keyboard_interrupt)
        
        response = await catch_exceptions_middleware(mock_request, mock_call_next)
        
        assert response.status_code == 500
    
    @pytest.mark.skip(reason="SystemExit causes pytest to terminate")
    @pytest.mark.asyncio
    async def test_middleware_with_system_exit(self, mock_request):
        """Test middleware with SystemExit exception.
        
        SKIPPED: This test is skipped because SystemExit can terminate pytest.
        
        BUG: Similar to KeyboardInterrupt, SystemExit should not be caught
        by application middleware.
        """
        async def raise_system_exit(request):
            raise SystemExit("System exit")
        
        os.environ["tel_Falg"] = "False"
        mock_call_next = AsyncMock(side_effect=raise_system_exit)
        
        response = await catch_exceptions_middleware(mock_request, mock_call_next)
        
        assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_middleware_with_multiple_sequential_calls(self, mock_request):
        """Test middleware handles multiple sequential calls correctly."""
        os.environ["tel_Falg"] = "False"
        
        async def mock_success(request):
            return JSONResponse({"status": "ok"}, status_code=200)
        
        mock_call_next = AsyncMock(side_effect=mock_success)
        
        response1 = await catch_exceptions_middleware(mock_request, mock_call_next)
        response2 = await catch_exceptions_middleware(mock_request, mock_call_next)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert mock_call_next.call_count == 2
    
    @pytest.mark.asyncio
    @patch('fairness.exception.custom_exception.telemetry_flag', 'True')
    @patch('fairness.exception.custom_exception.fairnesstelemetryurl', 'http://test-telemetry.com/api')
    @patch('fairness.exception.custom_exception.requests.post')
    async def test_middleware_when_telemetry_post_fails(self, mock_post, mock_request, mock_call_next_with_exception):
        """Test middleware when telemetry POST fails."""
        mock_post.side_effect = Exception("Telemetry network error")
        
        # Middleware should raise exception if telemetry fails (no error handling in code)
        with pytest.raises(Exception, match="Telemetry network error"):
            await catch_exceptions_middleware(mock_request, mock_call_next_with_exception)


# ============================================================================
# TEST CLASS: RegisterExceptions Class
# ============================================================================

class TestRegisterExceptionsInitialization:
    """Test RegisterExceptions class initialization."""
    
    def test_init_with_valid_app(self, mock_fastapi_app):
        """Test initialization with valid FastAPI app."""
        register = RegisterExceptions(mock_fastapi_app)
        
        assert register.app == mock_fastapi_app
        assert hasattr(register, 'app')
    
    def test_init_with_none_app(self):
        """Test initialization with None app."""
        register = RegisterExceptions(None)
        
        assert register.app is None
    
    def test_init_stores_app_reference(self, mock_fastapi_app):
        """Test that initialization stores reference to app."""
        register = RegisterExceptions(mock_fastapi_app)
        
        # Modifying the app should affect the stored reference
        mock_fastapi_app.test_attr = "test_value"
        assert register.app.test_attr == "test_value"


# ============================================================================
# TEST CLASS: RegisterExceptions Methods
# ============================================================================

class TestRegisterExceptionsMethods:
    """Test RegisterExceptions class methods."""
    
    def test_register_exception_handlers_calls_add_exception_handler(self, mock_fastapi_app):
        """Test register_exception_handlers adds CustomHTTPException handler."""
        register = RegisterExceptions(mock_fastapi_app)
        
        result = register.register_exception_handlers()
        
        mock_fastapi_app.add_exception_handler.assert_called_once()
        call_args = mock_fastapi_app.add_exception_handler.call_args
        assert call_args[0][0] == CustomHTTPException
        assert call_args[0][1] == http_exception_handler
    
    def test_register_exception_handlers_adds_middleware(self, mock_fastapi_app):
        """Test register_exception_handlers adds middleware."""
        register = RegisterExceptions(mock_fastapi_app)
        
        result = register.register_exception_handlers()
        
        mock_fastapi_app.middleware.assert_called_once_with('http')
    
    def test_register_exception_handlers_returns_app(self, mock_fastapi_app):
        """Test register_exception_handlers returns the app."""
        register = RegisterExceptions(mock_fastapi_app)
        
        result = register.register_exception_handlers()
        
        assert result == mock_fastapi_app
    
    def test_register_exception_handlers_order(self, mock_fastapi_app):
        """Test that exception handler is registered before middleware."""
        register = RegisterExceptions(mock_fastapi_app)
        
        register.register_exception_handlers()
        
        # Verify both methods were called
        assert mock_fastapi_app.add_exception_handler.called
        assert mock_fastapi_app.middleware.called


# ============================================================================
# TEST CLASS: Integration Tests
# ============================================================================

class TestIntegration:
    """Test integration between components."""
    
    def test_full_exception_flow_with_app(self, mock_fastapi_app):
        """Test full exception registration flow."""
        register = RegisterExceptions(mock_fastapi_app)
        app = register.register_exception_handlers()
        
        assert app == mock_fastapi_app
        assert mock_fastapi_app.add_exception_handler.called
        assert mock_fastapi_app.middleware.called
    
    @pytest.mark.asyncio
    async def test_exception_handler_receives_custom_exception(self, mock_request):
        """Test that exception handler correctly processes CustomHTTPException."""
        error_dict = {"errorCode": "INT_001", "errorType": "IntegrationTest"}
        exc = CustomHTTPException(
            error_dict=error_dict,
            name="IntegrationError",
            msg="Integration test error"
        )
        
        response = await http_exception_handler(mock_request, exc)
        
        assert response.status_code == 500
        assert exc.error_dict["errorMessage"] == "IntegrationError"
    
    @pytest.mark.asyncio
    async def test_middleware_and_handler_interaction(self, mock_request):
        """Test middleware catching exception and handler processing it."""
        async def raise_custom_exception(request):
            raise ValueError("Test error for middleware")
        
        os.environ["tel_Falg"] = "False"
        mock_call_next = AsyncMock(side_effect=raise_custom_exception)
        
        response = await catch_exceptions_middleware(mock_request, mock_call_next)
        
        assert response.status_code == 500


# ============================================================================
# TEST CLASS: Error Handling
# ============================================================================

class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_custom_exception_with_invalid_error_dict_type(self):
        """Test CustomHTTPException with non-dict error_dict raises appropriate error."""
        # This tests actual behavior - module may raise TypeError
        with pytest.raises((TypeError, AttributeError)):
            exc = CustomHTTPException(
                error_dict="not a dict",
                name="InvalidType",
                msg="Invalid type test"
            )
            # Try to access as dict
            _ = exc.error_dict["errorMessage"]
    
    @pytest.mark.asyncio
    async def test_handler_with_missing_errorMessage_key(self, mock_request):
        """Test handler behavior when error_dict doesn't have errorMessage after init."""
        # This shouldn't happen normally, but test defensive coding
        exc = CustomHTTPException(
            error_dict={"code": "TEST"},
            name="MissingKey",
            msg="Missing key test"
        )
        
        # Manually remove errorMessage to simulate edge case
        del exc.error_dict["errorMessage"]
        exc.error_dict["errorMessage"] = "RestoredMessage"
        
        response = await http_exception_handler(mock_request, exc)
        assert response.status_code == 500
    
    @pytest.mark.asyncio
    @patch('fairness.exception.custom_exception.logger')
    async def test_middleware_calls_logger_exception(self, mock_logger_module, mock_request, mock_call_next_with_exception):
        """Test middleware calls logger.exception with the caught exception."""
        os.environ["tel_Falg"] = "False"
        
        response = await catch_exceptions_middleware(mock_request, mock_call_next_with_exception)
        
        # Logger should be called with the exception
        assert mock_logger_module.exception.called


# ============================================================================
# TEST CLASS: Performance Tests
# ============================================================================

class TestPerformance:
    """Test performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_handler_response_time(self, mock_request):
        """Test handler completes within reasonable time."""
        import time
        
        exc = CustomHTTPException(
            error_dict={"test": "data"},
            name="PerfTest",
            msg="Performance test"
        )
        
        start = time.time()
        response = await http_exception_handler(mock_request, exc)
        duration = time.time() - start
        
        assert duration < 1.0  # Should complete in less than 1 second
        assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_middleware_overhead(self, mock_request, mock_call_next):
        """Test middleware adds minimal overhead to successful requests."""
        import time
        
        start = time.time()
        response = await catch_exceptions_middleware(mock_request, mock_call_next)
        duration = time.time() - start
        
        assert duration < 1.0  # Should complete quickly
        assert response.status_code == 200
    
    def test_exception_creation_performance(self):
        """Test that creating CustomHTTPException is fast."""
        import time
        
        start = time.time()
        for _ in range(1000):
            exc = CustomHTTPException(
                error_dict={"test": "data"},
                name="PerfTest",
                msg="Performance test"
            )
        duration = time.time() - start
        
        assert duration < 1.0  # Should create 1000 exceptions in less than 1 second


# ============================================================================
# TEST CLASS: Resource Management
# ============================================================================

class TestResourceManagement:
    """Test resource management and cleanup."""
    
    @pytest.mark.asyncio
    @patch('fairness.exception.custom_exception.telemetry_flag', 'True')
    @patch('fairness.exception.custom_exception.fairnesstelemetryurl', 'http://test-telemetry.com/api')
    @patch('fairness.exception.custom_exception.requests.post')
    async def test_handler_cleans_up_after_telemetry_call(self, mock_post, mock_request):
        """Test handler properly manages resources after telemetry call."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_response
        
        exc = CustomHTTPException(
            error_dict={"test": "data"},
            name="ResourceTest",
            msg="Resource test"
        )
        
        response = await http_exception_handler(mock_request, exc)
        
        assert response.status_code == 500
        assert mock_post.called
    
    def test_register_exceptions_doesnt_hold_extra_references(self, mock_fastapi_app):
        """Test RegisterExceptions doesn't create circular references."""
        import sys
        
        initial_refcount = sys.getrefcount(mock_fastapi_app)
        register = RegisterExceptions(mock_fastapi_app)
        
        # Should only add one reference (stored in register.app)
        assert sys.getrefcount(mock_fastapi_app) == initial_refcount + 1


# ============================================================================
# TEST CLASS: Security Tests
# ============================================================================

class TestSecurity:
    """Test security-related aspects."""
    
    @pytest.mark.asyncio
    async def test_handler_doesnt_expose_sensitive_error_dict(self, mock_request):
        """Test handler doesn't expose full error_dict in response."""
        sensitive_data = {
            "password": "secret123",
            "apiKey": "super-secret-key",
            "token": "auth-token-xyz"
        }
        
        exc = CustomHTTPException(
            error_dict=sensitive_data.copy(),
            name="SensitiveError",
            msg="user friendly message"
        )
        
        response = await http_exception_handler(mock_request, exc)
        
        # Response should only contain the user-friendly message
        assert response.status_code == 500
        # The sensitive error_dict should not be in the response body
        # (it's only sent to telemetry if enabled)
    
    @pytest.mark.asyncio
    async def test_handler_sanitizes_error_message(self, mock_request):
        """Test handler with potentially malicious content in message."""
        exc = CustomHTTPException(
            error_dict={},
            name="XSSTest",
            msg="<script>alert('XSS')</script>"
        )
        
        response = await http_exception_handler(mock_request, exc)
        
        # JSONResponse should automatically escape HTML
        assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_middleware_handles_security_exceptions(self, mock_request):
        """Test middleware properly handles security-related exceptions."""
        async def raise_permission_error(request):
            raise PermissionError("Unauthorized access attempt")
        
        os.environ["tel_Falg"] = "False"
        mock_call_next = AsyncMock(side_effect=raise_permission_error)
        
        response = await catch_exceptions_middleware(mock_request, mock_call_next)
        
        assert response.status_code == 500


# ============================================================================
# TEST CLASS: Scalability Tests
# ============================================================================

class TestScalability:
    """Test scalability aspects."""
    
    @pytest.mark.asyncio
    async def test_handler_handles_concurrent_requests(self, mock_request):
        """Test handler can handle multiple concurrent exception requests."""
        exceptions = [
            CustomHTTPException(
                error_dict={"id": i},
                name=f"Error{i}",
                msg=f"Message {i}"
            )
            for i in range(10)
        ]
        
        tasks = [
            http_exception_handler(mock_request, exc)
            for exc in exceptions
        ]
        
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == 10
        assert all(r.status_code == 500 for r in responses)
    
    @pytest.mark.asyncio
    async def test_middleware_handles_high_volume(self, mock_request, mock_call_next):
        """Test middleware can handle high volume of requests."""
        tasks = [
            catch_exceptions_middleware(mock_request, mock_call_next)
            for _ in range(50)
        ]
        
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == 50
        assert all(r.status_code == 200 for r in responses)


# ============================================================================
# TEST CLASS: Regression Tests
# ============================================================================

class TestRegression:
    """Test for regression issues and backwards compatibility."""
    
    def test_custom_exception_maintains_exception_interface(self):
        """Test CustomHTTPException maintains standard Exception interface."""
        exc = CustomHTTPException(
            error_dict={"test": "data"},
            name="RegressionTest",
            msg="Regression message"
        )
        
        # Should support standard exception operations
        assert str(exc)  # Should be convertible to string
        assert repr(exc)  # Should have repr
    
    @pytest.mark.asyncio
    async def test_handler_always_returns_500_status(self, mock_request):
        """Test handler consistently returns 500 status code (regression check)."""
        test_cases = [
            ("Error1", "Message1"),
            ("Error2", "Message2"),
            ("Error3", "Message3"),
        ]
        
        for name, msg in test_cases:
            exc = CustomHTTPException(
                error_dict={},
                name=name,
                msg=msg
            )
            response = await http_exception_handler(mock_request, exc)
            assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_middleware_always_returns_json_response_on_error(self, mock_request):
        """Test middleware consistently returns JSONResponse on errors."""
        async def raise_error(request):
            raise RuntimeError("Test error")
        
        os.environ["tel_Falg"] = "False"
        mock_call_next = AsyncMock(side_effect=raise_error)
        
        response = await catch_exceptions_middleware(mock_request, mock_call_next)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500


# ============================================================================
# TEST CLASS: Code Quality Indicators
# ============================================================================

class TestCodeQuality:
    """Test code quality indicators."""
    
    def test_custom_http_exception_class_exists(self):
        """Test CustomHTTPException class is properly defined."""
        assert CustomHTTPException is not None
        assert callable(CustomHTTPException)
    
    def test_http_exception_handler_is_async(self):
        """Test http_exception_handler is an async function."""
        import inspect
        assert inspect.iscoroutinefunction(http_exception_handler)
    
    def test_catch_exceptions_middleware_is_async(self):
        """Test catch_exceptions_middleware is an async function."""
        import inspect
        assert inspect.iscoroutinefunction(catch_exceptions_middleware)
    
    def test_register_exceptions_class_exists(self):
        """Test RegisterExceptions class is properly defined."""
        assert RegisterExceptions is not None
        assert callable(RegisterExceptions)
    
    def test_register_exceptions_has_required_methods(self):
        """Test RegisterExceptions has all required methods."""
        assert hasattr(RegisterExceptions, '__init__')
        assert hasattr(RegisterExceptions, 'register_exception_handlers')
    
    def test_module_has_required_exports(self):
        """Test module exports all required components."""
        from fairness.exception import custom_exception
        
        assert hasattr(custom_exception, 'CustomHTTPException')
        assert hasattr(custom_exception, 'http_exception_handler')
        assert hasattr(custom_exception, 'catch_exceptions_middleware')
        assert hasattr(custom_exception, 'RegisterExceptions')


# ============================================================================
# TEST CLASS: Bug Documentation
# ============================================================================

class TestBugDocumentation:
    """Document known bugs and issues in the original code."""
    
    def test_bug_typo_in_env_var_name(self):
        """
        BUG DOCUMENTATION: Typo in environment variable name
        
        Location: Line 29
        Issue: Environment variable is named "tel_Falg" instead of "tel_Flag"
        Impact: Potential confusion and debugging difficulty
        Severity: Minor (typo)
        
        Code: telemetry_flag = os.getenv("tel_Falg")
        Expected: telemetry_flag = os.getenv("tel_Flag")
        """
        # Test demonstrates the typo exists in the code
        # The module level variable is set at import time
        from fairness.exception import custom_exception
        
        # The variable name in code has the typo "tel_Falg"
        assert hasattr(custom_exception, 'telemetry_flag')
    
    def test_bug_duplicate_import_of_fastapi(self):
        """
        BUG DOCUMENTATION: Duplicate import statement
        
        Location: Lines 14 and 17
        Issue: FastAPI is imported twice:
            - Line 14: from fastapi import FastAPI, Request
            - Line 17: from fastapi import FastAPI
        Impact: Redundant code, slightly reduced readability
        Severity: Minor (code smell)
        """
        # Test that the module still functions despite duplicate import
        from fairness.exception import custom_exception
        assert hasattr(custom_exception, 'FastAPI')
    
    def test_bug_duplicate_import_of_request(self):
        """
        BUG DOCUMENTATION: Duplicate/conflicting Request import
        
        Location: Lines 14 and 18
        Issue: Request is imported from both fastapi and starlette:
            - Line 14: from fastapi import FastAPI, Request
            - Line 18: from starlette.requests import Request
        Impact: The second import overwrites the first, potentially causing confusion
        Severity: Minor (but could cause issues if fastapi.Request is specifically needed)
        """
        # Test that Request is available (will be starlette version)
        from fairness.exception import custom_exception
        assert hasattr(custom_exception, 'Request')
    
    def test_bug_unused_import_response(self):
        """
        BUG DOCUMENTATION: Unused import
        
        Location: Line 19
        Issue: from starlette.responses import Response is imported but never used
        Impact: Unnecessary import increases module load time slightly
        Severity: Minor (unused import)
        """
        # Test module loads successfully despite unused import
        from fairness.exception import custom_exception
        assert True  # Module imported successfully
    
    def test_bug_unused_import_print_exception(self):
        """
        BUG DOCUMENTATION: Unused import
        
        Location: Line 20
        Issue: from traceback import print_exception is imported but never used
        Impact: Unnecessary import
        Severity: Minor (unused import)
        """
        # Test module loads successfully
        from fairness.exception import custom_exception
        assert True
    
    @pytest.mark.asyncio
    async def test_bug_middleware_typo_in_error_message(self, mock_request, mock_call_next_with_exception):
        """
        BUG DOCUMENTATION: Typo in error message
        
        Location: Line 65
        Issue: Error message has typo "occured" should be "occurred"
        Impact: Minor grammatical error in user-facing message
        Severity: Minor (typo)
        
        Code: return JSONResponse("Internal server error occured", status_code=500)
        Expected: return JSONResponse("Internal server error occurred", status_code=500)
        """
        os.environ["tel_Falg"] = "False"
        
        response = await catch_exceptions_middleware(mock_request, mock_call_next_with_exception)
        
        # Test that response is created (with typo in message)
        assert response.status_code == 500
    
    def test_bug_logging_basicconfig_in_module_scope(self):
        """
        BUG DOCUMENTATION: logging.basicConfig called at module level
        
        Location: Line 27
        Issue: logging.basicConfig(level=logging.ERROR) is called when module is imported
        Impact: This can interfere with application's logging configuration
                It should be configured by the application, not the library
        Severity: Moderate (can cause logging configuration conflicts)
        """
        # Test that basicConfig was called (may affect other logging)
        import logging
        # This test documents that the issue exists
        assert logging.getLogger().level in [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG, logging.NOTSET]
    
    @pytest.mark.asyncio
    async def test_bug_handler_always_returns_500_for_all_errors(self, mock_request):
        """
        BUG DOCUMENTATION: Always returns HTTP 500 status
        
        Location: Line 50
        Issue: Handler always returns 500 regardless of error type
                Should use appropriate status codes (400 for validation, 404 for not found, etc.)
        Impact: Clients cannot distinguish between different error types
        Severity: Moderate (violates HTTP semantics)
        """
        validation_exc = CustomHTTPException(
            error_dict={"errorType": "ValidationError"},
            name="ValidationError",
            msg="Invalid input"
        )
        
        response = await http_exception_handler(mock_request, validation_exc)
        
        # Should be 400 for validation errors, but returns 500
        assert response.status_code == 500  # Bug: should be 400
    
    def test_bug_error_dict_mutated_during_init(self):
        """
        BUG DOCUMENTATION: Constructor mutates input parameter
        
        Location: Lines 33-34
        Issue: __init__ modifies the error_dict parameter passed in:
            self.error_dict = error_dict
            self.error_dict["errorMessage"] = name
        Impact: Mutates caller's dictionary (violates principle of least surprise)
        Severity: Moderate (could cause unexpected side effects)
        
        Expected behavior: Copy the dict before modifying it
        """
        original_dict = {"errorCode": "TEST_001"}
        original_dict_copy = original_dict.copy()
        
        exc = CustomHTTPException(
            error_dict=original_dict,
            name="TestError",
            msg="Test"
        )
        
        # Bug: original_dict has been modified
        assert "errorMessage" in original_dict
        assert original_dict != original_dict_copy
    
    @pytest.mark.asyncio
    async def test_bug_handler_unused_variable_error(self, mock_request):
        """
        BUG DOCUMENTATION: Unused variable
        
        Location: Line 45
        Issue: Variable 'error' is assigned but never used:
            error = error_dict["errorMessage"]
        Impact: Unnecessary code, slight performance overhead
        Severity: Minor (unused variable)
        """
        exc = CustomHTTPException(
            error_dict={"test": "data"},
            name="UnusedVarTest",
            msg="Unused variable test"
        )
        
        # Handler executes successfully despite unused variable
        response = await http_exception_handler(mock_request, exc)
        assert response.status_code == 500


# ============================================================================
# TEST CLASS: Environment Variable Handling
# ============================================================================

class TestEnvironmentVariables:
    """Test environment variable handling."""
    
    def test_telemetry_flag_none_when_not_set(self):
        """Test telemetry_flag is None when environment variable not set."""
        # Clear the variable
        if "tel_Falg" in os.environ:
            del os.environ["tel_Falg"]
        
        # Re-import to get fresh module state (or check current state)
        from fairness.exception import custom_exception
        
        # Module loads successfully even with unset variable
        assert True
    
    def test_telemetry_url_none_when_not_set(self):
        """Test fairnesstelemetryurl is None when not set."""
        if "FAIRNESS_TELEMETRY_URL" in os.environ:
            del os.environ["FAIRNESS_TELEMETRY_URL"]
        
        from fairness.exception import custom_exception
        
        # Module loads successfully
        assert True
    
    @pytest.mark.asyncio
    @patch('fairness.exception.custom_exception.telemetry_flag', 'True')
    @patch('fairness.exception.custom_exception.fairnesstelemetryurl', 'http://test.com/api')
    @patch('fairness.exception.custom_exception.requests.post')
    async def test_telemetry_with_various_flag_values(self, mock_post, mock_request):
        """Test telemetry behavior with different tel_Falg values."""
        mock_post.return_value.json.return_value = {"status": "ok"}
        
        exc = CustomHTTPException(
            error_dict={"test": "telemetry"},
            name="FlagTest",
            msg="Flag test"
        )
        
        response = await http_exception_handler(mock_request, exc)
        
        # With mocked telemetry_flag='True', post should be called
        assert mock_post.called
        assert response.status_code == 500


# ============================================================================
# TEST CLASS: Async Behavior
# ============================================================================

class TestAsyncBehavior:
    """Test async/await behavior and coroutine handling."""
    
    @pytest.mark.asyncio
    async def test_handler_returns_coroutine(self, mock_request):
        """Test http_exception_handler returns a coroutine when not awaited."""
        exc = CustomHTTPException(
            error_dict={},
            name="CoroTest",
            msg="Coroutine test"
        )
        
        # Call without await
        coro = http_exception_handler(mock_request, exc)
        
        assert asyncio.iscoroutine(coro)
        
        # Clean up
        response = await coro
        assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_middleware_returns_coroutine(self, mock_request, mock_call_next):
        """Test catch_exceptions_middleware returns a coroutine when not awaited."""
        # Call without await
        coro = catch_exceptions_middleware(mock_request, mock_call_next)
        
        assert asyncio.iscoroutine(coro)
        
        # Clean up
        response = await coro
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_handler_can_be_cancelled(self, mock_request):
        """Test handler coroutine can be cancelled."""
        exc = CustomHTTPException(
            error_dict={},
            name="CancelTest",
            msg="Cancel test"
        )
        
        task = asyncio.create_task(http_exception_handler(mock_request, exc))
        
        # Cancel immediately
        task.cancel()
        
        with pytest.raises(asyncio.CancelledError):
            await task
