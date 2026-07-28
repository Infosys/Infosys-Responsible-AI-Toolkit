"""
Unit tests for exception module.
Tests custom exception classes and error handling utilities.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import uuid


class TestModelDeploymentExceptions:
    """Test cases for ModelDeployment exception classes."""

    def test_model_deployment_exception_creation(self):
        """Test creating a ModelDeploymentException instance."""
        from exception.exception import ModelDeploymentException

        exc = ModelDeploymentException("Test error message")
        assert str(exc) == "Test error message"
        assert exc.status_code == 400

    def test_model_deployment_not_found_error(self):
        """Test ModelDeploymentNotFoundError exception."""
        from exception.exception import ModelDeploymentNotFoundError

        test_name = "test_usecase_123"
        exc = ModelDeploymentNotFoundError(test_name)
        
        assert exc.status_code == 404
        assert "test_usecase_123" in exc.detail
        assert "Not Found" in exc.detail

    def test_model_deployment_name_not_empty_error(self):
        """Test ModelDeploymentNameNotEmptyError exception."""
        from exception.exception import ModelDeploymentNameNotEmptyError

        exc = ModelDeploymentNameNotEmptyError("test_name")
        
        assert exc.status_code == 409
        assert "should not be empty" in exc.detail


class TestDatabaseExceptions:
    """Test cases for database exception classes."""

    def test_database_error(self):
        """Test DatabaseError exception."""
        from exception.exception import DatabaseError

        exc = DatabaseError("Database connection failed")
        assert str(exc) == "Database connection failed"
        assert isinstance(exc, Exception)

    def test_database_connection_error(self):
        """Test DatabaseConnectionError exception."""
        from exception.exception import DatabaseConnectionError

        exc = DatabaseConnectionError("Cannot connect to database")
        assert str(exc) == "Cannot connect to database"
        assert isinstance(exc, Exception)

    def test_database_configuration_error(self):
        """Test DatabaseConfigurationError exception."""
        from exception.exception import DatabaseConfigurationError

        exc = DatabaseConfigurationError("Invalid database config")
        assert str(exc) == "Invalid database config"
        assert isinstance(exc, Exception)


class TestConfigSectionNotFoundError:
    """Test cases for ConfigSectionNotFoundError exception."""

    def test_config_section_not_found_error(self):
        """Test ConfigSectionNotFoundError exception."""
        from exception.exception import ConfigSectionNotFoundError

        exc = ConfigSectionNotFoundError("Section not found")
        assert str(exc) == "Section not found"
        assert isinstance(exc, Exception)


class TestServiceExceptions:
    """Test cases for service exception classes."""

    def test_service_exception_default(self):
        """Test ServiceException with default values."""
        from exception.exception import ServiceException

        exc = ServiceException()
        assert exc.message == "Service error"
        assert exc.status_code == 500
        assert exc.error_code is None
        assert exc.service_name is None

    def test_service_exception_custom_values(self):
        """Test ServiceException with custom values."""
        from exception.exception import ServiceException

        exc = ServiceException(
            message="Custom error",
            status_code=503,
            error_code="ERR_001",
            service_name="TestService"
        )
        
        assert exc.message == "Custom error"
        assert exc.status_code == 503
        assert exc.error_code == "ERR_001"
        assert exc.service_name == "TestService"

    def test_validation_error_default(self):
        """Test ValidationError with default values."""
        from exception.exception import ValidationError

        exc = ValidationError()
        assert exc.message == "Invalid input data"
        assert exc.status_code == 422
        assert exc.error_code is None
        assert exc.service_name is None

    def test_validation_error_custom_values(self):
        """Test ValidationError with custom values."""
        from exception.exception import ValidationError

        exc = ValidationError(
            message="Invalid field",
            error_code="VAL_001",
            service_name="ValidationService"
        )
        
        assert exc.message == "Invalid field"
        assert exc.status_code == 422
        assert exc.error_code == "VAL_001"
        assert exc.service_name == "ValidationService"

    def test_processing_error_default(self):
        """Test ProcessingError with default values."""
        from exception.exception import ProcessingError

        exc = ProcessingError()
        assert exc.message == "Error processing request"
        assert exc.status_code == 500
        assert exc.service_name is None

    def test_processing_error_custom_values(self):
        """Test ProcessingError with custom values."""
        from exception.exception import ProcessingError

        exc = ProcessingError(
            message="Processing failed",
            service_name="ProcessingService"
        )
        
        assert exc.message == "Processing failed"
        assert exc.status_code == 500
        assert exc.service_name == "ProcessingService"

    def test_processing_error_string_representation(self):
        """Test ProcessingError __str__ method."""
        from exception.exception import ProcessingError

        exc = ProcessingError(
            message="Processing failed",
            service_name="TestService"
        )
        
        assert str(exc) == "[Service: TestService] Processing failed"


class TestErrorUtilities:
    """Test cases for error utility functions."""

    def test_generate_error_id(self):
        """Test generate_error_id function."""
        from exception.exception import generate_error_id

        error_id = generate_error_id()
        
        assert isinstance(error_id, str)
        assert len(error_id) == 8
        
        # Generate another ID and ensure they're different
        error_id2 = generate_error_id()
        assert error_id != error_id2

    def test_generate_error_id_format(self):
        """Test that generated error IDs are valid UUID prefixes."""
        from exception.exception import generate_error_id

        error_id = generate_error_id()
        
        # Should be hexadecimal characters only
        assert all(c in '0123456789abcdef-' for c in error_id)

    @patch('config.logger.CustomLogger')
    @patch('exception.exception.generate_error_id')
    def test_create_secure_error_response_default(self, mock_generate_id, mock_logger, app):
        """Test create_secure_error_response with default values."""
        from exception.exception import create_secure_error_response

        mock_generate_id.return_value = "test1234"
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        error = Exception("Test error")
        
        with app.app_context():
            response, status_code = create_secure_error_response(error)

            assert status_code == 500
            response_data = response.get_json()
            assert response_data["error"] == "Internal Error"
            assert response_data["error_id"] == "test1234"
            assert "timestamp" in response_data
            mock_logger_instance.error.assert_called_once()

    @patch('config.logger.CustomLogger')
    @patch('exception.exception.generate_error_id')
    def test_create_secure_error_response_custom(self, mock_generate_id, mock_logger, app):
        """Test create_secure_error_response with custom values."""
        from exception.exception import create_secure_error_response

        mock_generate_id.return_value = "abc12345"
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        error = Exception("Validation failed")
        
        with app.app_context():
            response, status_code = create_secure_error_response(
                error,
                status_code=422,
                error_type="Validation Error"
            )

            assert status_code == 422
            response_data = response.get_json()
            assert response_data["error"] == "Validation Error"
            assert response_data["error_id"] == "abc12345"
            assert "timestamp" in response_data

    @patch('config.logger.CustomLogger')
    @patch('exception.exception.generate_error_id')
    def test_create_secure_error_response_logs_error(self, mock_generate_id, mock_logger, app):
        """Test that create_secure_error_response logs the error."""
        from exception.exception import create_secure_error_response

        mock_generate_id.return_value = "err12345"
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        error = Exception("Test error message")
        
        with app.app_context():
            create_secure_error_response(error)

            # Verify logger was called with error message containing error ID
            assert mock_logger_instance.error.called
            call_args = str(mock_logger_instance.error.call_args)
            assert "err12345" in call_args
            assert "Test error message" in call_args

    @patch('config.logger.CustomLogger')
    @patch('exception.exception.generate_error_id')
    @patch('exception.exception.datetime')
    def test_create_secure_error_response_timestamp(self, mock_datetime, mock_generate_id, mock_logger, app):
        """Test that create_secure_error_response includes correct timestamp."""
        from exception.exception import create_secure_error_response
        from datetime import datetime, timezone

        mock_generate_id.return_value = "test1234"
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance
        
        # Mock datetime
        mock_now = Mock()
        mock_now.isoformat.return_value = "2026-01-07T10:00:00.000000+00:00"
        mock_datetime.now.return_value = mock_now

        error = Exception("Test error")
        
        with app.app_context():
            response, _ = create_secure_error_response(error)

            response_data = response.get_json()
            assert response_data["timestamp"] == "2026-01-07T10:00:00.000000+00:00"
            mock_datetime.now.assert_called_once_with(timezone.utc)
