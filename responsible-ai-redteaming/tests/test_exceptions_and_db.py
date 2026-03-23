'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import types
import pytest


def test_global_exception_classes_defaults_and_messages():
    from app.exception import global_exception as ge
    from app.constants import global_constants as gc

    # Defaults when msg is falsy
    e_data = ge.DataError("")
    assert e_data.status_code == gc.HTTP_STATUS_DATA_PROCESSING_ERROR
    assert e_data.message == gc.DATA_ERROR

    e_oper = ge.OperationalError(None)
    assert e_oper.status_code == gc.HTTP_STATUS_SERVICE_UNAVAILBLE
    assert e_oper.message == gc.OPERATIONAL_ERROR

    e_integrity = ge.IntegrityError("")
    assert e_integrity.status_code == gc.HTTP_STATUS_SERVICE_UNAVAILBLE
    assert e_integrity.message == gc.OPERATIONAL_ERROR

    e_internal = ge.InternalError("")
    assert e_internal.status_code == gc.HTTP_STATUS_BAD_REQUEST
    assert e_internal.message == gc.DATA_ERROR

    e_not_supported = ge.NotSupportedError("")
    assert e_not_supported.status_code == gc.HTTP_STATUS_NOT_ALLLOWED
    assert e_not_supported.message == gc.NOT_ALLOWED_MESSAGE

    e_forbidden = ge.ForbiddenError("")
    assert e_forbidden.status_code == gc.HTTP_STATUS_FORBIDDEN
    assert e_forbidden.message == gc.FORBIDDEN_ERROR_MESSAGE

    e_incomplete = ge.IncompleteRead("")
    assert e_incomplete.status_code == gc.HTTP_STATUS_BAD_REQUEST
    assert e_incomplete.message == gc.DATA_ERROR

    e_method_arg = ge.MethodArgumentNotValidException("")
    assert e_method_arg.status_code == gc.HTTP_STATUS_BAD_REQUEST
    assert e_method_arg.message == gc.DATA_ERROR

    # Explicit messages
    e_db = ge.DatabaseError("X")
    assert e_db.status_code == gc.HTTP_STATUS_NOT_FOUND
    assert e_db.message.startswith("X") and "DATABASE" in e_db.message.upper()

    e_conn = ge.DbConnectionError("mongo")
    assert e_conn.status_code == gc.HTTP_STATUS_SERVICE_UNAVAILBLE
    assert "mongo" in e_conn.message

    e_media = ge.UnSupportedMediaTypeException("text/plain")
    assert e_media.status_code == gc.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    assert "text/plain" in e_media.message


def test_global_exception_handlers(monkeypatch):
    from app.exception import global_exception_handler as geh
    from fastapi.exceptions import RequestValidationError

    # RequestValidationError handler
    rve = RequestValidationError(errors=[{"loc":["body"], "msg":"bad", "type":"value_error"}])
    resp = geh.validation_error_handler(rve)
    assert resp.status_code == 422
    body = resp.body.decode()
    assert "bad" in body and "detail" in body

    # http_exception_handler with stub
    exc = types.SimpleNamespace(status_code=400, detail="oops")
    resp2 = geh.http_exception_handler(exc)
    assert resp2.status_code == 400 and b"oops" in resp2.body

    # unsupported_mediatype_error_handler with real exception type
    from app.exception.global_exception import UnSupportedMediaTypeException
    exc2 = UnSupportedMediaTypeException("application/xml")
    resp3 = geh.unsupported_mediatype_error_handler(exc2)
    assert resp3.status_code == 415
    assert b"application/xml" in resp3.body


def test_database_connection_connect_happy_and_error_paths(monkeypatch):
    import app.dao.DatabaseConnection as dc

    # Fake MongoClient to return a fake DB object
    class FakeDB(dict):
        pass
    class FakeClient:
        def __init__(self, uri):
            self._uri = uri
        def __getitem__(self, name):
            db = FakeDB()
            db["__name__"] = name
            return db

    monkeypatch.setattr(dc, 'pymongo', types.SimpleNamespace(MongoClient=lambda uri: FakeClient(uri)), raising=True)

    secrets = {
        'DB_TYPE': 'mongo',
        'MONGO_PATH': 'mongodb://x',
        'DB_NAME': 'testdb',
    }
    monkeypatch.setattr(dc, 'get_secret', lambda k: secrets.get(k), raising=True)
    db = dc.DB.connect()
    assert isinstance(db, dict) and db.get('__name__') == 'testdb'

    # Cosmos path variant
    secrets2 = {
        'DB_TYPE': 'cosmos',
        'COSMOS_PATH': 'mongodb://y',
        'DB_NAME': 'cdb',
    }
    monkeypatch.setattr(dc, 'get_secret', lambda k: secrets2.get(k), raising=True)
    db2 = dc.DB.connect()
    assert isinstance(db2, dict) and db2.get('__name__') == 'cdb'

    # Missing path -> returns None
    secrets3 = {
        'DB_TYPE': 'mongo',
        'MONGO_PATH': None,
        'DB_NAME': 'db',
    }
    monkeypatch.setattr(dc, 'get_secret', lambda k: secrets3.get(k), raising=True)
    assert dc.DB.connect() is None

    # Unsupported db type -> None
    secrets4 = {'DB_TYPE': 'sqlite'}
    monkeypatch.setattr(dc, 'get_secret', lambda k: secrets4.get(k), raising=True)
    assert dc.DB.connect() is None
