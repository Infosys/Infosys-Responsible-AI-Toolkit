import src.dao.SaveFileDB as savefile_mod
from src.dao.SaveFileDB import FileStoreDb


def test_savefiledb_findOne_and_delete(monkeypatch):
    class DummyFile:
        def __init__(self):
            self.filename = 'file.bin'
            self.content_type = 'application/octet-stream'
        def read(self):
            return b'bytes'
    class DummyFS:
        def find_one(self, q):
            return DummyFile()
    monkeypatch.setattr(savefile_mod.FileStoreDb, 'fs', DummyFS())

    doc = FileStoreDb.findOne('id')
    assert doc['fileName'] == 'file.bin' and doc['type'] == 'application/octet-stream'

    # Delete path should not raise even for missing id
    FileStoreDb.delete('id')
