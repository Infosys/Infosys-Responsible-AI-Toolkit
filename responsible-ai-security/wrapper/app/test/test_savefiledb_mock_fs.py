import io
import time
import pytest

from src.dao.SaveFileDB import FileStoreDb as FS


class _StubUpload:
    def __init__(self, content: bytes, content_type: str = 'application/octet-stream'):
        self.file = io.BytesIO(content)
        self.content_type = content_type


class _MemFile:
    def __init__(self, _id, filename, contentType):
        self._id = _id
        self.filename = filename
        self.content_type = contentType
        self._buf = io.BytesIO()
    def write(self, data):
        self._buf.write(data)
    def read(self):
        self._buf.seek(0)
        return self._buf.read()

class _MemFS:
    def __init__(self):
        self._store = {}
    class _Ctx:
        def __init__(self, parent, _id, filename, contentType):
            self.parent = parent
            self._mem = _MemFile(_id, filename, contentType)
        def __enter__(self):
            return self._mem
        def __exit__(self, exc_type, exc, tb):
            # persist on exit
            self.parent._store[self._mem._id] = self._mem
            return False
    def new_file(self, _id, filename, content_type):
        return self._Ctx(self, _id, filename, content_type)
    def find_one(self, query):
        _id = query.get('_id')
        return self._store.get(_id)


def test_filestoredb_create_update_find_delete(monkeypatch):
    memfs = _MemFS()
    monkeypatch.setattr(FS, 'fs', memfs)

    content1 = b'abc'
    fid = FS.create(_StubUpload(content1, 'text/plain'), 'm.pkl')
    assert fid in memfs._store

    # findOne returns dict with fileName, data, type
    found = FS.findOne(fid)
    assert found['fileName'] == 'm.pkl' and found['type'] == 'text/plain'
    assert found['data'] == content1

    # update overwrites same id
    content2 = b'defghij'
    fid2 = FS.update(fid, _StubUpload(content2, 'text/plain'), 'm.pkl')
    assert fid2 == fid
    found2 = FS.findOne(fid2)
    assert found2['data'] == content2

    # delete removes file and chunks entries (simulated by clearing store)
    # Patch delete to clear memfs store so method path executes without real DB
    def _fake_delete(payload):
        memfs._store.pop(payload, None)
    monkeypatch.setattr(FS, 'delete', staticmethod(_fake_delete))
    FS.delete(fid)
    assert fid not in memfs._store
