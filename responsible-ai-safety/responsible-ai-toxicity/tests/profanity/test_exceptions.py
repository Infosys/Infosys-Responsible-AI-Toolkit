import importlib
import sys
import types

import pytest
from fastapi import HTTPException


def test_profanity_not_found_and_name_errors(monkeypatch):
    # Import the module
    mod = importlib.import_module("profanity.exception.exception")

    # ProfanityNotFoundError: detail should include provided name
    e = mod.ProfanityNotFoundError("mycase")
    assert e.status_code == mod.global_constants.HTTP_STATUS_NOT_FOUND
    assert "mycase" in e.detail

    # ProfanityNameNotEmptyError
    e2 = mod.ProfanityNameNotEmptyError("any")
    assert e2.status_code == mod.global_constants.HTTP_STATUS_409_CODE
    assert e2.detail == mod.USECASE_NAME_VALIDATION_ERROR


def test_unsupported_media_type_exception_and_handler(monkeypatch):
    mod = importlib.import_module("profanity.exception.exception")

    exc = mod.UnSupportedMediaTypeException("image/png")
    assert exc.status_code == mod.global_constants.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    assert "image/png" in exc.message

    resp = mod.unsupported_mediatype_error_handler(exc)
    assert resp.status_code == exc.status_code
    body = resp.body.decode() if hasattr(resp, "body") else None
    assert "Unsupported media type" in body


def test_validation_error_handler(monkeypatch):
    mod = importlib.import_module("profanity.exception.exception")

    class DummyValidationError(Exception):
        def errors(self):
            return [{"loc": ["body", "field"], "msg": "required"}]

    dummy = DummyValidationError()
    resp = mod.validation_error_handler(dummy)
    assert resp.status_code == int(mod.global_constants.HTTP_422_UNPROCESSABLE_ENTITY)
    assert b"required" in resp.body


def test_http_exception_handler(monkeypatch):
    mod = importlib.import_module("profanity.exception.exception")

    class DummyExc:
        def __init__(self):
            self.status_code = 418
            self.detail = "I'm a teapot"

    exc = DummyExc()
    resp = mod.http_exception_handler(exc)
    assert resp.status_code == 418
    assert b"I'm a teapot" in resp.body
