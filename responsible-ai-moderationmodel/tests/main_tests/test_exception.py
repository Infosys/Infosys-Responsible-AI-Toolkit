"""
Tests for exception module (exception.py)
"""
import pytest


def test_modeldeploymentException_basic():
    """Test basic modeldeploymentException"""
    # source uses ModelDeploymentException; alias to expected test name
    from src.exception.exception import ModelDeploymentException as modeldeploymentException
    
    exc = modeldeploymentException("Test error message")
    assert str(exc) == "Test error message"
    assert hasattr(exc, 'status_code')


def test_modeldeploymentNotFoundError_creation():
    """Test modeldeploymentNotFoundError with name"""
    from src.exception.exception import ModelDeploymentNotFoundError as modeldeploymentNotFoundError
    
    exc = modeldeploymentNotFoundError("TestModel")
    assert "TestModel" in exc.detail
    assert hasattr(exc, 'status_code')
    assert hasattr(exc, 'detail')


def test_modeldeploymentNotFoundError_different_names():
    """Test modeldeploymentNotFoundError with different names"""
    from src.exception.exception import ModelDeploymentNotFoundError as modeldeploymentNotFoundError
    
    names = ["Model1", "Test_Model", "model-123", "ComplexModelName"]
    for name in names:
        exc = modeldeploymentNotFoundError(name)
        assert hasattr(exc, 'detail')
        assert isinstance(exc.detail, str)


def test_modeldeploymentNameNotEmptyError_creation():
    """Test modeldeploymentNameNotEmptyError"""
    from src.exception.exception import ModelDeploymentNameNotEmptyError as modeldeploymentNameNotEmptyError
    
    exc = modeldeploymentNameNotEmptyError("TestName")
    assert hasattr(exc, 'status_code')
    assert hasattr(exc, 'detail')


def test_modeldeploymentNameNotEmptyError_empty_name():
    """Test modeldeploymentNameNotEmptyError with empty name"""
    from src.exception.exception import ModelDeploymentNameNotEmptyError as modeldeploymentNameNotEmptyError
    
    exc = modeldeploymentNameNotEmptyError("")
    assert hasattr(exc, 'detail')


def test_exception_inheritance():
    """Test that custom exceptions inherit from Exception"""
    from src.exception.exception import ModelDeploymentException as modeldeploymentException, ModelDeploymentNotFoundError as modeldeploymentNotFoundError, ModelDeploymentNameNotEmptyError as modeldeploymentNameNotEmptyError
    
    assert issubclass(modeldeploymentException, Exception)
    assert issubclass(modeldeploymentNotFoundError, modeldeploymentException)
    assert issubclass(modeldeploymentNameNotEmptyError, modeldeploymentException)


def test_exception_can_be_raised():
    """Test that exceptions can be raised and caught"""
    from src.exception.exception import ModelDeploymentException as modeldeploymentException
    
    with pytest.raises(modeldeploymentException) as exc_info:
        raise modeldeploymentException("Test error")
    
    assert "Test error" in str(exc_info.value)


def test_not_found_error_can_be_raised():
    """Test modeldeploymentNotFoundError can be raised"""
    from src.exception.exception import ModelDeploymentNotFoundError as modeldeploymentNotFoundError
    
    with pytest.raises(modeldeploymentNotFoundError):
        raise modeldeploymentNotFoundError("TestModel")


def test_name_not_empty_error_can_be_raised():
    """Test modeldeploymentNameNotEmptyError can be raised"""
    from src.exception.exception import ModelDeploymentNameNotEmptyError as modeldeploymentNameNotEmptyError
    
    with pytest.raises(modeldeploymentNameNotEmptyError):
        raise modeldeploymentNameNotEmptyError("TestName")


def test_exception_with_special_characters():
    """Test exceptions with special characters in messages"""
    from src.exception.exception import ModelDeploymentNotFoundError as modeldeploymentNotFoundError
    
    special_names = ["Model@123", "Test-Model_v2", "模型", "Модель"]
    for name in special_names:
        exc = modeldeploymentNotFoundError(name)
        assert hasattr(exc, 'detail')


def test_exception_status_codes():
    """Test that exceptions have appropriate status codes"""
    from src.exception.exception import ModelDeploymentNotFoundError as modeldeploymentNotFoundError, ModelDeploymentNameNotEmptyError as modeldeploymentNameNotEmptyError
    
    not_found = modeldeploymentNotFoundError("Test")
    name_empty = modeldeploymentNameNotEmptyError("Test")
    
    # Check status codes are set
    assert hasattr(not_found, 'status_code')
    assert hasattr(name_empty, 'status_code')


def test_exception_caught_as_base_exception():
    """Test that custom exceptions can be caught as base Exception"""
    from src.exception.exception import ModelDeploymentNotFoundError as modeldeploymentNotFoundError
    
    with pytest.raises(Exception):
        raise modeldeploymentNotFoundError("TestModel")


def test_exception_caught_as_parent_class():
    """Test that derived exceptions can be caught as parent class"""
    from src.exception.exception import ModelDeploymentException as modeldeploymentException, ModelDeploymentNotFoundError as modeldeploymentNotFoundError
    
    with pytest.raises(modeldeploymentException):
        raise modeldeploymentNotFoundError("TestModel")


def test_multiple_exception_types():
    """Test handling multiple exception types"""
    from src.exception.exception import ModelDeploymentNotFoundError as modeldeploymentNotFoundError, ModelDeploymentNameNotEmptyError as modeldeploymentNameNotEmptyError
    
    exceptions = [
        modeldeploymentNotFoundError("Model1"),
        modeldeploymentNameNotEmptyError("Model2")
    ]
    
    for exc in exceptions:
        assert hasattr(exc, 'status_code')
        assert hasattr(exc, 'detail')
