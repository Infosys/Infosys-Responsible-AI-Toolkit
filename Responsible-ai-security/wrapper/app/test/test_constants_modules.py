import pytest
from src.constants import global_constants, local_constants

class TestGlobalConstants:
    def test_http_status_service_unavailable(self):
        assert global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE == 503
    
    def test_http_status_ok(self):
        assert global_constants.HTTP_STATUS_OK == 200
    
    def test_http_status_not_found(self):
        assert global_constants.HTTP_STATUS_NOT_FOUND == 404
    
    def test_database_error(self):
        assert global_constants.DATABASE_ERROR == "DATABASE not Found"
    
    def test_empty_list_err_message(self):
        assert global_constants.EMPTY_LIST_ERR_MESSAGE == "No records found"
    
    def test_http_415_unsupported_media_type(self):
        assert global_constants.HTTP_415_UNSUPPORTED_MEDIA_TYPE == 415

class TestLocalConstants:
    def test_space_delimiter(self):
        assert local_constants.SPACE_DELIMITER == " "
    
    def test_placeholder_text(self):
        assert local_constants.PLACEHOLDER_TEXT == "PLACEHOLDER_TEXT"
