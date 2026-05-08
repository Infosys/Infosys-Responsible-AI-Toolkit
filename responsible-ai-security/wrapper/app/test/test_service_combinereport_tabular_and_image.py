import os
import json
import csv
import datetime
import io
import numpy as np
import pandas as pd
import pytest

import src.service.service as service_mod
from src.service.service import Bulk
from src.service.utility import Utility


def _setup_tmp_db(tmp_path):
    root = tmp_path / 'database'
    for d in ['data', 'model', 'payload', 'report']:
        (root / d).mkdir(parents=True, exist_ok=True)
    return str(tmp_path)


def test_combinereport_tabular_stub(monkeypatch, tmp_path):
    base = _setup_tmp_db(tmp_path)
    monkeypatch.setenv('DB_TYPE', 'mongo')

    # Point Utility.getcurrentDirectory to tmp base
    monkeypatch.setattr(Utility, 'getcurrentDirectory', lambda: base)

    # Stub batch/model/data lookups
    monkeypatch.setattr(service_mod.Batch, 'findall', lambda q: [{'BatchId': 1.0, 'ModelId': 1.0, 'DataId': 1.0, 'TenetId': 1.0}])
    monkeypatch.setattr(service_mod.Model, 'findall', lambda q: [{'ModelId': 1.0, 'ModelName': 'm', 'ModelEndPoint': 'http://api'}])
    monkeypatch.setattr(service_mod.Data, 'findall', lambda q: [{'DataId': 1.0, 'SampleData': 'sample.csv'}])

    # Prepare fake model/data files
    model_csv = tmp_path / 'database' / 'data' / 'data.csv'
    with open(model_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['f1', 'target'])
        w.writerow([1, 0])
        w.writerow([2, 1])

    # Stub Utility reads
    monkeypatch.setattr(Utility, 'readModelFile', lambda batchid: (None, str(tmp_path / 'database' / 'model' / 'm.pkl'), 'm', 'Sklearn'))
    monkeypatch.setattr(Utility, 'readDataFile', lambda payload: (pd.DataFrame({'f1': [1,2], 'target':[0,1]}), str(model_csv)))

    # Stub payload file with meta-data
    def fake_read_payload(batchid):
        path = tmp_path / 'database' / 'payload' / 'm.txt'
        path.write_text(json.dumps({'targetClassifier': 'clf', 'dataType': 'Tabular', 'groundTruthClassLabel': 'target'}))
        return str(path)
    monkeypatch.setattr(Utility, 'readPayloadFile', fake_read_payload)

    # Stub Defence and Utility helpers
    monkeypatch.setattr(service_mod.DF, 'generateCombinedDenfenseModel', lambda payload: (np.zeros((2,2)), {}, {}))
    monkeypatch.setattr(Utility, 'checkAttackListStatus', lambda payload: ([], []))
    monkeypatch.setattr(Utility, 'makeAttackListRow', lambda payload: ([], [], ['AttackA']))
    monkeypatch.setattr(Utility, 'graphForCombineAttack', lambda payload: None)
    monkeypatch.setattr(Utility, 'combineReportFile', lambda payload: 1)
    monkeypatch.setattr(service_mod.Infosys, 'getAttackFuncs', lambda payload: [{'name':'AttackA', 'type':'Evasion'}])

    # Stub FileStoreDb and Html.create
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
    monkeypatch.setattr(service_mod.Html, 'create', lambda data: True)

    res = Bulk.combinereport({'batchid': 1.0, 'attackList': ['AttackA'], 'dateTime': 'now'})
    assert res is None or (isinstance(res, dict) and 'combineReportFileId' in res)


def test_combinereport_image_stub(monkeypatch, tmp_path):
    base = _setup_tmp_db(tmp_path)
    monkeypatch.setenv('DB_TYPE', 'mongo')
    monkeypatch.setattr(Utility, 'getcurrentDirectory', lambda: base)

    # Stub batch/model/data
    monkeypatch.setattr(service_mod.Batch, 'findall', lambda q: [{'BatchId': 2.0, 'ModelId': 1.0, 'DataId': 1.0, 'TenetId': 1.0}])
    monkeypatch.setattr(service_mod.Model, 'findall', lambda q: [{'ModelId': 1.0, 'ModelName': 'm', 'ModelEndPoint': 'http://api'}])
    monkeypatch.setattr(service_mod.Data, 'findall', lambda q: [{'DataId': 1.0, 'SampleData': 'sample.csv'}])

    # Fake image data path
    img_path = tmp_path / 'database' / 'data' / 'img.png'
    img_path.write_bytes(b'fake')

    monkeypatch.setattr(Utility, 'readModelFile', lambda batchid: (None, str(tmp_path / 'database' / 'model' / 'm.pkl'), 'm', 'Sklearn'))
    monkeypatch.setattr(Utility, 'readDataFile', lambda payload: ({'img.png': None}, str(img_path)))

    def fake_read_payload(batchid):
        path = tmp_path / 'database' / 'payload' / 'm.txt'
        path.write_text(json.dumps({'targetClassifier': 'clf', 'dataType': 'Image', 'groundTruthClassLabel': 'target'}))
        return str(path)
    monkeypatch.setattr(Utility, 'readPayloadFile', fake_read_payload)

    monkeypatch.setattr(Utility, 'checkAttackListStatus', lambda payload: [])
    monkeypatch.setattr(Utility, 'makeAttackListRow', lambda payload: ([], ['AttackA']))
    monkeypatch.setattr(Utility, 'graphForCombineAttack', lambda payload: None)
    monkeypatch.setattr(Utility, 'combineReportFile', lambda payload: 1)
    monkeypatch.setattr(service_mod.Infosys, 'getAttackFuncs', lambda payload: [{'name':'AttackA', 'type':'Evasion'}])

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
    monkeypatch.setattr(service_mod.Html, 'create', lambda data: True)

    res = Bulk.combinereport({'batchid': 2.0, 'attackList': ['AttackA'], 'dateTime': 'now'})
    assert res is None or (isinstance(res, dict) and 'combineReportFileId' in res)
