# Test for exception handlers
test_exceptions_handlers = '''import pytest
from unittest.mock import MagicMock
from fastapi.exceptions import RequestValidationError
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from src.exception.global_exception_handler import validation_error_handler, http_exception_handler, unsupported_mediatype_error_handler
from src.exception.global_exception import UnSupportedMediaTypeException

class TestExceptionHandlers:
    def test_validation_error_handler(self):
        exc = MagicMock(spec=RequestValidationError)
        exc.errors.return_value = [{'loc': ['body', 'field'], 'msg': 'field required', 'type': 'value_error.missing'}]
        
        response = validation_error_handler(exc)
        assert response.status_code == 422
    
    def test_http_exception_handler(self):
        exc = MagicMock(spec=FastAPIHTTPException)
        exc.status_code = 404
        exc.detail = 'Not found'
        
        response = http_exception_handler(exc)
        assert response.status_code == 404
    
    def test_http_exception_handler_500(self):
        exc = MagicMock(spec=FastAPIHTTPException)
        exc.status_code = 500
        exc.detail = 'Internal server error'
        
        response = http_exception_handler(exc)
        assert response.status_code == 500
    
    def test_unsupported_mediatype_error_handler(self):
        exc = UnSupportedMediaTypeException('application/xml')
        response = unsupported_mediatype_error_handler(exc)
        assert response.status_code == 415
'''

with open('test_exception_handlers.py', 'w', encoding='utf-8') as f:
    f.write(test_exceptions_handlers)

print('Created test_exception_handlers.py')
