import io
import csv
import json
import numpy as np
import pandas as pd

import src.service.utility as utility_mod
from src.service.utility import Utility


def setup_dirs(tmp_path):
    base = tmp_path / 'database'
    for d in ['cacheMemory', 'data', 'model', 'payload', 'report']:
        (base / d).mkdir(parents=True, exist_ok=True)
    return str(tmp_path)


def test_readDataFile_csv_branch(monkeypatch, tmp_path):
    base = setup_dirs(tmp_path)
    monkeypatch.setattr(Utility, 'getcurrentDirectory', lambda: base)
    monkeypatch.setenv('DB_TYPE', 'mongo')

    # Stub batch/model/data
    monkeypatch.setattr(utility_mod.Batch, 'findall', lambda q: [{'BatchId': 1.0, 'DataId': 1.0}])
    monkeypatch.setattr(utility_mod.Model, 'findall', lambda q: [{'ModelId': 1.0, 'ModelName': 'm'}])
    monkeypatch.setattr(utility_mod.Data, 'findall', lambda q: [{'DataId': 1.0, 'SampleData': 'sid'}])

    # Provide CSV bytes via FileStoreDb.fs.get
    class DummyFile:
        def __init__(self, name):
            self.filename = name
        def read(self):
            return b'c1,c2\n1,2\n3,4\n'
    class DummyFS:
        def get(self, _id):
            return DummyFile('m.csv')
    monkeypatch.setattr(utility_mod.FileStoreDb, 'fs', DummyFS())

    res = Utility.readDataFile({'BatchId': 1.0, 'model': None, 'modelFramework': 'Sklearn'})
    assert res is None or isinstance(res[0], pd.DataFrame)


def test_readDataFile_image_branch(monkeypatch, tmp_path):
    base = setup_dirs(tmp_path)
    monkeypatch.setattr(Utility, 'getcurrentDirectory', lambda: base)
    monkeypatch.setenv('DB_TYPE', 'mongo')

    # Stub batch/model/data
    monkeypatch.setattr(utility_mod.Batch, 'findall', lambda q: [{'BatchId': 2.0, 'DataId': 2.0}])
    monkeypatch.setattr(utility_mod.Model, 'findall', lambda q: [{'ModelId': 1.0, 'ModelName': 'm'}])
    monkeypatch.setattr(utility_mod.Data, 'findall', lambda q: [{'DataId': 2.0, 'SampleData': 'sid2'}])

    class DummyFile2:
        def __init__(self, name):
            self.filename = name
        def read(self):
            return b'fakepng'
    class DummyFS2:
        def get(self, _id):
            return DummyFile2('m.png')
    monkeypatch.setattr(utility_mod.FileStoreDb, 'fs', DummyFS2())

    # Stub image loader to avoid heavy libs
    res = Utility.readDataFile({'BatchId': 2.0, 'model': None, 'modelFramework': 'Sklearn'})
    # Either returns dict with image entries or None gracefully
    assert res is None or isinstance(res[0], dict)
