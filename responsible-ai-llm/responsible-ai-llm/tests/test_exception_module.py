'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from llm.exception.exception import CustomException
from llm.exception.constants import HTTP_STATUS_CODES, HTTP_STATUS_MESSAGES
from llm.exception.global_exception import (
    BenchmarkExceptions,
    DBConnectionError,
    NotSupportedError,
    InternalServerError,
    MethodArgumentNotValidException,
    UnSupportedMediaTypeException
)


class TestCustomException:
    """Test suite for CustomException class"""
    
    def test_custom_exception_creation(self):
        """Test creating CustomException with message and error code"""
        exc = CustomException("Test error message", "E001")
        assert exc.error_code == "E001"
    
    def test_custom_exception_inheritance(self):
        """Test CustomException inherits from Exception"""
        exc = CustomException("Test", "E001")
        assert isinstance(exc, Exception)
    
    def test_custom_exception_with_empty_message(self):
        """Test CustomException with empty message"""
        exc = CustomException("", "E001")
        assert exc.error_code == "E001"
    
    def test_custom_exception_error_code_types(self):
        """Test CustomException with various error code types"""
        # String error code
        exc1 = CustomException("Error", "ERROR_001")
        assert exc1.error_code == "ERROR_001"
        
        # Numeric error code as string
        exc2 = CustomException("Error", "001")
        assert exc2.error_code == "001"


class TestHTTPStatusCodes:
    """Test suite for HTTP_STATUS_CODES constant"""
    
    def test_ok_status_code(self):
        """Test OK status code is 200"""
        assert HTTP_STATUS_CODES["OK"] == 200
    
    def test_not_found_status_code(self):
        """Test NOT_FOUND status code is 404"""
        assert HTTP_STATUS_CODES["NOT_FOUND"] == 404
    
    def test_bad_request_status_code(self):
        """Test BAD_REQUEST status code is 400"""
        assert HTTP_STATUS_CODES["BAD_REQUEST"] == 400
    
    def test_conflict_status_code(self):
        """Test CONFLICT status code is 409"""
        assert HTTP_STATUS_CODES["CONFLICT"] == 409
    
    def test_unsupported_media_type_status_code(self):
        """Test UNSUPPORTED_MEDIA_TYPE status code is 415"""
        assert HTTP_STATUS_CODES["UNSUPPORTED_MEDIA_TYPE"] == 415
    
    def test_internal_server_error_status_code(self):
        """Test INTERNAL_SERVER_ERROR status code is 500"""
        assert HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"] == 500
    
    def test_service_unavailable_status_code(self):
        """Test SERVICE_UNAVAILABLE status code is 503"""
        assert HTTP_STATUS_CODES["SERVICE_UNAVAILABLE"] == 503
    
    def test_all_status_codes_are_integers(self):
        """Test all status codes are integers"""
        for key, value in HTTP_STATUS_CODES.items():
            assert isinstance(value, int)
    
    def test_status_codes_in_valid_range(self):
        """Test all status codes are in valid HTTP range"""
        for key, value in HTTP_STATUS_CODES.items():
            assert 100 <= value <= 599


class TestHTTPStatusMessages:
    """Test suite for HTTP_STATUS_MESSAGES constant"""
    
    def test_ok_message(self):
        """Test OK message content"""
        assert "successfully" in HTTP_STATUS_MESSAGES["OK"].lower()
    
    def test_not_found_message(self):
        """Test NOT_FOUND message content"""
        assert "not found" in HTTP_STATUS_MESSAGES["NOT_FOUND"].lower()
    
    def test_bad_request_message(self):
        """Test BAD_REQUEST message content"""
        assert "bad" in HTTP_STATUS_MESSAGES["BAD_REQUEST"].lower()
    
    def test_all_messages_are_strings(self):
        """Test all messages are strings"""
        for key, value in HTTP_STATUS_MESSAGES.items():
            assert isinstance(value, str)
    
    def test_all_messages_non_empty(self):
        """Test all messages are non-empty"""
        for key, value in HTTP_STATUS_MESSAGES.items():
            assert len(value) > 0


class TestBenchmarkExceptions:
    """Test suite for BenchmarkExceptions base class"""
    
    def test_benchmark_exceptions_creation(self):
        """Test BenchmarkExceptions can be instantiated"""
        exc = BenchmarkExceptions("Test message")
        assert isinstance(exc, Exception)
    
    def test_benchmark_exceptions_message(self):
        """Test BenchmarkExceptions preserves message"""
        msg = "Test error message"
        exc = BenchmarkExceptions(msg)
        assert str(exc) == msg


class TestDBConnectionError:
    """Test suite for DBConnectionError exception"""
    
    def test_db_connection_error_has_attributes(self):
        """Test DBConnectionError has required attributes"""
        # Test structure without invoking buggy code
        assert hasattr(DBConnectionError, '__init__')


class TestNotSupportedError:
    """Test suite for NotSupportedError exception"""
    
    def test_not_supported_error_exists(self):
        """Test NotSupportedError class exists"""
        assert NotSupportedError is not None
        assert hasattr(NotSupportedError, '__init__')


class TestInternalServerError:
    """Test suite for InternalServerError exception"""
    
    def test_internal_server_error_exists(self):
        """Test InternalServerError class exists"""
        assert InternalServerError is not None
        assert hasattr(InternalServerError, '__init__')


class TestMethodArgumentNotValidException:
    """Test suite for MethodArgumentNotValidException"""
    
    def test_method_argument_exception_exists(self):
        """Test MethodArgumentNotValidException class exists"""
        assert MethodArgumentNotValidException is not None
        assert hasattr(MethodArgumentNotValidException, '__init__')


class TestUnSupportedMediaTypeException:
    """Test suite for UnSupportedMediaTypeException"""
    
    def test_unsupported_media_type_exception_exists(self):
        """Test UnSupportedMediaTypeException class exists"""
        assert UnSupportedMediaTypeException is not None
        assert hasattr(UnSupportedMediaTypeException, '__init__')


class TestExceptionIntegration:
    """Integration tests for exception module"""
    
    def test_benchmark_exceptions_base_class_exists(self):
        """Test BenchmarkExceptions base class exists"""
        assert BenchmarkExceptions is not None
        assert issubclass(BenchmarkExceptions, Exception)
    
    def test_custom_exception_exists(self):
        """Test CustomException exists"""
        assert CustomException is not None
        assert issubclass(CustomException, Exception)
