import os
import shutil
import json
import pytest

import src.service.service as service_mod
from src.service.service import Bulk
from src.service.utility import Utility


def test_batchAttack_stub(monkeypatch, tmp_path):
    monkeypatch.setenv('DB_TYPE', 'mongo')
    base = tmp_path / 'database'
    for d in ['data', 'model', 'payload', 'report']:
        (base / d).mkdir(parents=True, exist_ok=True)

    # Put a dummy zip in report directory the function expects to upload
    report_folder = base / 'report' / 'job_1'
    report_folder.mkdir(parents=True, exist_ok=True)
    zip_path = base / 'report' / 'job_1.zip'
    with open(zip_path, 'wb') as f:
        f.write(b'fakezip')

    # Stub getcurrentDirectory to our tmp
    monkeypatch.setattr(Utility, 'getcurrentDirectory', lambda: str(tmp_path))

    # Stub attack response
    class InfosysStub:
        @staticmethod
        def setAttack(payload):
            return {'Job_Id': 'job_1'}
    monkeypatch.setattr(service_mod, 'Infosys', InfosysStub)

    class DummyNewFile:
        def __init__(self):
            self._id = 'rid'
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def write(self, *a, **k):
            pass
    class DummyFS:
        def new_file(self, _id=None, filename=None, contentType=None):
            return DummyNewFile()
    monkeypatch.setattr(service_mod.FileStoreDb, 'fs', DummyFS())
    monkeypatch.setattr(service_mod.SecReport, 'create', lambda payload: 'secid')

    res = Bulk.batchAttack({'batchId': 3.0, 'modelUrl': 'http://api'})
    assert res is not None
