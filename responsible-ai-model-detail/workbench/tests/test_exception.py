"""
Unit tests for exception module.
"""

import pytest
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app.exception.exception import (
    aiShieldException,
    aiShieldNotFoundError,
    aiShieldNameNotEmptyError
)
from app.constants import global_constants


class TestAiShieldException:
    """Tests for aiShieldException base class."""
    
    def test_aishield_exception_initialization(self):
        detail = "Test exception detail"
        exc = aiShieldException(detail)
        
        assert str(exc) == detail
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert isinstance(exc, Exception)
    
    def test_aishield_exception_with_empty_detail(self):
        detail = ""
        exc = aiShieldException(detail)
        
        assert str(exc) == detail
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
    
    def test_aishield_exception_with_long_detail(self):
        detail = "A" * 1000
        exc = aiShieldException(detail)
        
        assert str(exc) == detail
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
    
    def test_aishield_exception_inheritance(self):
        exc = aiShieldException("test")
        
        assert isinstance(exc, Exception)
        assert hasattr(exc, 'status_code')
    
    def test_aishield_exception_can_be_raised(self):
        with pytest.raises(aiShieldException) as exc_info:
            raise aiShieldException("Test error")
        
        assert "Test error" in str(exc_info.value)
        assert exc_info.value.status_code == global_constants.HTTP_STATUS_BAD_REQUEST


class TestAiShieldNotFoundError:
    """Tests for aiShieldNotFoundError exception."""
    
    def test_aishield_not_found_error_initialization(self):
        name = "TestUsecase"
        exc = aiShieldNotFoundError(name)
        
        assert exc.status_code == global_constants.HTTP_STATUS_NOT_FOUND
        assert name in exc.detail or "TestUsecase" in exc.detail
        assert isinstance(exc, aiShieldException)
        assert isinstance(exc, Exception)
    
    def test_aishield_not_found_error_with_empty_name(self):
        name = ""
        exc = aiShieldNotFoundError(name)
        
        assert exc.status_code == global_constants.HTTP_STATUS_NOT_FOUND
        assert hasattr(exc, 'detail')
    
    def test_aishield_not_found_error_with_special_characters(self):
        name = "Test@Usecase#123"
        exc = aiShieldNotFoundError(name)
        
        assert exc.status_code == global_constants.HTTP_STATUS_NOT_FOUND
        assert hasattr(exc, 'detail')
    
    def test_aishield_not_found_error_can_be_raised(self):
        with pytest.raises(aiShieldNotFoundError) as exc_info:
            raise aiShieldNotFoundError("MyUsecase")
        
        assert exc_info.value.status_code == global_constants.HTTP_STATUS_NOT_FOUND
        assert hasattr(exc_info.value, 'detail')
    
    def test_aishield_not_found_error_inheritance_chain(self):
        exc = aiShieldNotFoundError("test")
        
        assert isinstance(exc, aiShieldNotFoundError)
        assert isinstance(exc, aiShieldException)
        assert isinstance(exc, Exception)
    
    def test_aishield_not_found_error_with_numeric_name(self):
        name = "12345"
        exc = aiShieldNotFoundError(name)
        
        assert exc.status_code == global_constants.HTTP_STATUS_NOT_FOUND
        assert hasattr(exc, 'detail')


class TestAiShieldNameNotEmptyError:
    """Tests for aiShieldNameNotEmptyError exception."""
    
    def test_aishield_name_not_empty_error_initialization(self):
        name = "TestName"
        exc = aiShieldNameNotEmptyError(name)
        
        assert exc.status_code == global_constants.HTTP_STATUS_409_CODE
        assert hasattr(exc, 'detail')
        assert isinstance(exc, aiShieldException)
        assert isinstance(exc, Exception)
    
    def test_aishield_name_not_empty_error_with_empty_name(self):
        name = ""
        exc = aiShieldNameNotEmptyError(name)
        
        assert exc.status_code == global_constants.HTTP_STATUS_409_CODE
        assert hasattr(exc, 'detail')
    
    def test_aishield_name_not_empty_error_with_none_name(self):
        name = None
        exc = aiShieldNameNotEmptyError(name)
        
        assert exc.status_code == global_constants.HTTP_STATUS_409_CODE
        assert hasattr(exc, 'detail')
    
    def test_aishield_name_not_empty_error_can_be_raised(self):
        with pytest.raises(aiShieldNameNotEmptyError) as exc_info:
            raise aiShieldNameNotEmptyError("TestUsecase")
        
        assert exc_info.value.status_code == global_constants.HTTP_STATUS_409_CODE
        assert hasattr(exc_info.value, 'detail')
    
    def test_aishield_name_not_empty_error_inheritance(self):
        exc = aiShieldNameNotEmptyError("test")
        
        assert isinstance(exc, aiShieldNameNotEmptyError)
        assert isinstance(exc, aiShieldException)
        assert isinstance(exc, Exception)
    
    def test_aishield_name_not_empty_error_with_special_chars(self):
        name = "Test!@#$%"
        exc = aiShieldNameNotEmptyError(name)
        
        assert exc.status_code == global_constants.HTTP_STATUS_409_CODE
        assert hasattr(exc, 'detail')
    
    def test_aishield_name_not_empty_error_with_unicode(self):
        name = "测试用例"
        exc = aiShieldNameNotEmptyError(name)
        
        assert exc.status_code == global_constants.HTTP_STATUS_409_CODE
        assert hasattr(exc, 'detail')


class TestExceptionIntegration:
    """Integration tests for exception handling."""
    
    def test_multiple_exceptions_can_coexist(self):
        exc1 = aiShieldException("Base exception")
        exc2 = aiShieldNotFoundError("NotFound")
        exc3 = aiShieldNameNotEmptyError("NameError")
        
        assert exc1.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc2.status_code == global_constants.HTTP_STATUS_NOT_FOUND
        assert exc3.status_code == global_constants.HTTP_STATUS_409_CODE
    
    def test_exception_type_checking(self):
        base_exc = aiShieldException("base")
        not_found_exc = aiShieldNotFoundError("not_found")
        name_error_exc = aiShieldNameNotEmptyError("name_error")
        
        # Type checking
        assert type(base_exc).__name__ == 'aiShieldException'
        assert type(not_found_exc).__name__ == 'aiShieldNotFoundError'
        assert type(name_error_exc).__name__ == 'aiShieldNameNotEmptyError'
    
    def test_exception_catching_hierarchy(self):
        """Test that child exceptions can be caught by parent exception type."""
        with pytest.raises(aiShieldException):
            raise aiShieldNotFoundError("test")
        
        with pytest.raises(aiShieldException):
            raise aiShieldNameNotEmptyError("test")
    
    def test_exception_attributes_accessible(self):
        exc1 = aiShieldNotFoundError("test1")
        exc2 = aiShieldNameNotEmptyError("test2")
        
        assert hasattr(exc1, 'status_code')
        assert hasattr(exc1, 'detail')
        assert hasattr(exc2, 'status_code')
        assert hasattr(exc2, 'detail')
    
    def test_exceptions_with_same_name_different_types(self):
        """Test exceptions with same name parameter but different exception types."""
        name = "SameName"
        
        exc1 = aiShieldNotFoundError(name)
        exc2 = aiShieldNameNotEmptyError(name)
        
        assert exc1.status_code != exc2.status_code
        assert type(exc1) != type(exc2)
