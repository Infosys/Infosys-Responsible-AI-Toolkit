'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
'''

import pytest
from src.exception.exception import aiShieldException, aiShieldNotFoundError, aiShieldNameNotEmptyError
from src.exception.global_exception import (
    AicloudException, DbConnectionError, DataError, OperationalError,
    IntegrityError, InternalError, NotSupportedError, DatabaseError,
    InternalServerError, IncompleteRead,
    MethodArgumentNotValidException, UnSupportedMediaTypeException
)
from src.constants import global_constants

class TestAiShieldExceptions:
    def test_aishield_exception_creation(self):
        exc = aiShieldException("Test error")
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert "Test error" in str(exc)
    
    def test_aishield_not_found_error(self):
        exc = aiShieldNotFoundError("TestModel")
        assert exc.status_code == global_constants.HTTP_STATUS_NOT_FOUND
        assert "TestModel" in exc.detail
        assert "Not Found" in exc.detail
    
    def test_aishield_name_not_empty_error(self):
        exc = aiShieldNameNotEmptyError("TestName")
        assert exc.status_code == global_constants.HTTP_STATUS_409_CODE
        assert "should not be empty" in exc.detail
    
    def test_aishield_exception_inheritance(self):
        exc = aiShieldException("Test")
        assert isinstance(exc, Exception)

class TestGlobalExceptions:
    def test_aicloud_exception_base(self):
        exc = DbConnectionError("testdb")
        assert isinstance(exc, AicloudException)
        assert isinstance(exc, Exception)
    
    def test_db_connection_error(self):
        exc = DbConnectionError("mongodb")
        assert exc.status_code == global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        assert "Unable to connect" in exc.message
        assert "mongodb" in exc.message
    
    def test_data_error_with_message(self):
        exc = DataError("Custom data error")
        assert exc.status_code == global_constants.HTTP_STATUS_DATA_PROCESSING_ERROR
        assert exc.message == "Custom data error"
    
    def test_data_error_without_message(self):
        exc = DataError(None)
        assert exc.status_code == global_constants.HTTP_STATUS_DATA_PROCESSING_ERROR
        assert exc.message == global_constants.DATA_ERROR
    
    def test_data_error_empty_string(self):
        exc = DataError("")
        assert exc.message == global_constants.DATA_ERROR
    
    def test_operational_error_with_message(self):
        exc = OperationalError("DB operation failed")
        assert exc.status_code == global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        assert exc.message == "DB operation failed"
    
    def test_operational_error_without_message(self):
        exc = OperationalError(None)
        assert exc.message == global_constants.OPERATIONAL_ERROR
    
    def test_integrity_error_with_message(self):
        exc = IntegrityError("Constraint violation")
        assert exc.status_code == global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        assert exc.message == "Constraint violation"
    
    def test_integrity_error_without_message(self):
        exc = IntegrityError(None)
        assert exc.message == global_constants.OPERATIONAL_ERROR
    
    def test_internal_error_with_message(self):
        exc = InternalError("Internal processing error")
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == "Internal processing error"
    
    def test_internal_error_without_message(self):
        exc = InternalError(None)
        assert exc.message == global_constants.DATA_ERROR
    
    def test_not_supported_error_with_message(self):
        exc = NotSupportedError("Operation not supported")
        assert exc.status_code == global_constants.HTTP_STATUS_NOT_ALLLOWED
        assert exc.message == "Operation not supported"
    
    def test_not_supported_error_without_message(self):
        exc = NotSupportedError(None)
        assert exc.message == global_constants.NOT_ALLOWED_MESSAGE
    
    def test_database_error(self):
        exc = DatabaseError("testdb")
        assert exc.status_code == global_constants.HTTP_STATUS_NOT_FOUND
        assert "testdb" in exc.message
        assert "DATABASE not Found" in exc.message
    
    def test_internal_server_error_with_message(self):
        exc = InternalServerError("Server crashed")
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == "Server crashed"
    
    def test_internal_server_error_without_message(self):
        exc = InternalServerError(None)
        assert exc.message == global_constants.DATA_ERROR
    
    def test_incomplete_read_with_message(self):
        exc = IncompleteRead("Data read incomplete")
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == "Data read incomplete"
    
    def test_incomplete_read_without_message(self):
        exc = IncompleteRead(None)
        assert exc.message == global_constants.DATA_ERROR
    
    def test_method_argument_not_valid_with_message(self):
        exc = MethodArgumentNotValidException("Invalid argument")
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == "Invalid argument"
    
    def test_method_argument_not_valid_without_message(self):
        exc = MethodArgumentNotValidException(None)
        assert exc.message == global_constants.DATA_ERROR
    
    def test_unsupported_media_type_exception(self):
        exc = UnSupportedMediaTypeException("application/xml")
        assert exc.status_code == global_constants.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        assert "Unsupported media type" in exc.message
        assert "application/xml" in exc.message
    
    def test_exception_hierarchy(self):
        exceptions = [
            DbConnectionError("test"),
            DataError("test"),
            OperationalError("test"),
            IntegrityError("test"),
            InternalError("test"),
            NotSupportedError("test"),
            DatabaseError("test"),
            InternalServerError("test"),
            IncompleteRead("test"),
            MethodArgumentNotValidException("test"),
            UnSupportedMediaTypeException("test")
        ]
        for exc in exceptions:
            assert isinstance(exc, AicloudException)
            assert isinstance(exc, Exception)
            assert hasattr(exc, "status_code")
            assert hasattr(exc, "message")
