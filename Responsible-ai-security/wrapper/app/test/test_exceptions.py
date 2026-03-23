from types import SimpleNamespace
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException

from src.exception.global_exception import UnSupportedMediaTypeException
from src.exception.global_exception_handler import (
    validation_error_handler,
    http_exception_handler,
    unsupported_mediatype_error_handler,
)
from src.exception import global_exception as ge
from src.constants import global_constants as gc
from src.config.logger import CustomLogger
import src.config.logger as logger_module
import pytest


def test_validation_error_handler_returns_422_json():
    exc = RequestValidationError(errors=[{"loc": ["body", "field"], "msg": "invalid", "type": "value_error"}])
    resp = validation_error_handler(exc)
    assert resp.status_code == 422
    body = resp.body.decode()
    assert "invalid" in body


def test_http_exception_handler_serializes_detail():
    exc = HTTPException(status_code=400, detail="Bad Request")
    resp = http_exception_handler(exc)
    assert resp.status_code == 400
    body = resp.body.decode()
    assert "Bad Request" in body


def test_unsupported_mediatype_error_handler_uses_custom_exception():
    exc = UnSupportedMediaTypeException("application/xml")
    resp = unsupported_mediatype_error_handler(exc)
    assert resp.status_code == 415
    body = resp.body.decode()
    assert "application/xml" in body


def test_global_exception_classes_status_codes():
    assert ge.DbConnectionError('DB').status_code == gc.HTTP_STATUS_SERVICE_UNAVAILBLE
    assert ge.DataError(None).status_code == gc.HTTP_STATUS_DATA_PROCESSING_ERROR
    assert ge.OperationalError('').status_code == gc.HTTP_STATUS_SERVICE_UNAVAILBLE
    assert ge.IntegrityError('x').status_code == gc.HTTP_STATUS_SERVICE_UNAVAILBLE
    assert ge.InternalError('').status_code == gc.HTTP_STATUS_BAD_REQUEST
    assert ge.NotSupportedError('').status_code == gc.HTTP_STATUS_NOT_ALLLOWED
    assert ge.DatabaseError('DB').status_code == gc.HTTP_STATUS_NOT_FOUND
    assert ge.InternalServerError('').status_code == gc.HTTP_STATUS_BAD_REQUEST
    assert ge.IncompleteRead('').status_code == gc.HTTP_STATUS_BAD_REQUEST
    assert ge.MethodArgumentNotValidException('').status_code == gc.HTTP_STATUS_BAD_REQUEST
    assert ge.UnSupportedMediaTypeException('ct').status_code == gc.HTTP_415_UNSUPPORTED_MEDIA_TYPE


@pytest.fixture()
def logger_instance(tmp_path, monkeypatch):
    def fake_read(section, path):
        # Unique logger name per test; no file handler by default
        return {'file_name': f'test_log_{tmp_path.name}', 'verbose': 'True', 'log_dir': ''}
    monkeypatch.setattr(logger_module, 'readConfig', fake_read)
    return CustomLogger()


def test_logger_handlers_toggle_and_file(tmp_path, logger_instance):
    log = logger_instance
    assert log.has_console_handler()
    log.add_file_handler('test_log', str(tmp_path))
    assert log.has_file_handler()
    log.disable_console_output()
    assert not log.has_console_handler()
    log.enable_console_output()
    assert log.has_console_handler()
    log.disable_file_output()
    assert not log.has_file_handler()


def test_logger_telemetry_calls(logger_instance, monkeypatch):
    class DummyResp:
        def __init__(self, status_code): self.status_code = status_code
    import requests as req_mod
    # success
    monkeypatch.setattr(req_mod, 'post', lambda *a, **k: DummyResp(200))
    logger_instance.log_error_to_telemetry('E1', Exception('e'), '/a', 'GET')
    # failure (non-200)
    monkeypatch.setattr(req_mod, 'post', lambda *a, **k: DummyResp(500))
    logger_instance.log_error_to_telemetry('E2', Exception('e'), '/b', 'POST')
