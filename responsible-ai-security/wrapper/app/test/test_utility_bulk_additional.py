import os
import io
import csv
import json
import zipfile
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
import joblib

from src.service.utility import Utility as UT
from src.dao import SaveFileDB as savefile_mod
from src.dao.Security.SecReportDb import SecReport
from src.dao import Batch as batch_mod
from src.dao import ModelDb as model_mod
from src.dao import DataDb as data_mod
from src.dao import ModelAttributesValuesDb as mav_mod
from src.dao import ModelAttributesDb as ma_mod
from src.dao import DataAttributesValuesDb as dav_mod
from src.dao import DataAttributesDb as da_mod


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setenv('DB_TYPE', 'mongo')
    monkeypatch.setattr(UT, 'getcurrentDirectory', lambda: str(tmp_path))
    base = tmp_path / 'database'
    for d in ['cacheMemory','data', 'model', 'payload', 'report']:
        (base / d).mkdir(parents=True, exist_ok=True)
    return base


def test_database_delete_file_and_dir(tmp_db):
    # file
    f = tmp_db / 'cacheMemory' / 't.txt'
    f.write_text('x')
    UT.databaseDelete(str(f))
    assert not f.exists()
    # dir
    d = tmp_db / 'data' / 'sub'
    (d).mkdir(parents=True, exist_ok=True)
    (d / 'a.txt').write_text('a')
    UT.databaseDelete(str(d))
    assert not d.exists()


def test_dateTimeFormat_variants():
    s1 = UT.dateTimeFormat(None)
    assert isinstance(s1, str)
    import datetime
    now = datetime.datetime.now()
    s2 = UT.dateTimeFormat(now)
    assert str(now.strftime('%d-%m-%Y')) in s2


def test_update_and_sort_reports_list():
    # Prepare mixed reports
    reports = [
        {'ReportName': 'AttackA.zip', 'CreatedDateTime': 3},
        {'ReportName': 'ModelX.zip', 'CreatedDateTime': 5},
        {'ReportName': 'AttackB.zip', 'CreatedDateTime': 2},
        {'ReportName': 'AttackA.zip', 'CreatedDateTime': 4},
    ]
    attack_list = ['AttackA', 'AttackB']
    filtered = UT.updateReportsList({'reportList': reports, 'modelName': 'ModelX', 'attackList': attack_list})
    # only AttackA latest (4) and AttackB (2) ordered by attack list
    assert [r['ReportName'] for r in filtered] == ['AttackA.zip', 'AttackB.zip']
    # sort by CreatedDateTime desc
    sorted_reports = UT.sortReportsList(filtered)
    assert [r['CreatedDateTime'] for r in sorted_reports] == [4, 2]


def _make_zip_bytes(files):
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, 'w') as z:
        for name, content in files.items():
            z.writestr(name, content)
    return bio.getvalue()


def test_extract_csv_and_images(tmp_db):
    # CSV zip
    csv_zip = tmp_db / 'cacheMemory' / 'd.zip'
    data_dir = tmp_db / 'data'
    with zipfile.ZipFile(csv_zip, 'w') as z:
        z.writestr('t.csv', 'a,b\n1,2')
    out = UT.extractCSVFromZip(str(csv_zip), str(data_dir))
    assert os.path.exists(out)
    assert out.endswith('t.csv')
    # Images zip
    img_zip = tmp_db / 'cacheMemory' / 'i.zip'
    with zipfile.ZipFile(img_zip, 'w') as z:
        z.writestr('p.png', b'PNGDATA')
        z.writestr('q.jpg', b'JPGDATA')
    out_dir = UT.extractIMAGEFromZip(str(img_zip), str(data_dir))
    assert os.path.isdir(out_dir)
    assert set(os.listdir(out_dir)) == {'p.png', 'q.jpg'}


def test_checkList_with_dummy_model():
    # checkList with dummy model
    class M:
        def predict(self, arr):
            # return scores favoring index of sum parity
            s = int(np.sum(arr))
            if s % 2 == 0:
                return np.array([[0.9, 0.1]])
            return np.array([[0.1, 0.9]])
    x = np.array([[0,0],[1,0]])
    adv = np.array([[1,0],[1,1]])
    plist = UT.checkList({'model': M(), 'original_data': x, 'adversial_data': adv})
    assert isinstance(plist, list)
    assert all(len(p) == 4 for p in plist)


def test_readPayloadFile_writes_payload(tmp_db, monkeypatch):
    # Stubs for DAOs
    batch_id = 'B1'
    monkeypatch.setattr(batch_mod.Batch, 'findall', lambda q: [{'BatchId': batch_id, 'ModelId': 'M1', 'DataId': 'D1'}])
    monkeypatch.setattr(model_mod.Model, 'findall', lambda q: [{'ModelId': 'M1', 'ModelName': 'ModelX', 'ModelData': 'model_blob', 'ModelEndPoint': 'http://m'}])
    monkeypatch.setattr(data_mod.Data, 'findall', lambda q: [{'DataId': 'D1', 'SampleData': 'sample_blob', 'GroundTruthImageFileId': 'NA'}])

    # Model attributes
    mavs = [SimpleNamespace(ModelAttributeId='A1', ModelAttributeValues='sklearn'), SimpleNamespace(ModelAttributeId='A2', ModelAttributeValues='No')]
    monkeypatch.setattr(mav_mod.ModelAttributesValues, 'findall', lambda q: mavs)
    monkeypatch.setattr(ma_mod.ModelAttributes, 'findall', lambda q: [{'ModelAttributeName': 'modelFramework'}] if q.get('ModelAttributeId') == 'A1' else [{'ModelAttributeName': 'useModelApi'}])

    # Data attributes
    davs = [SimpleNamespace(DataAttributeId='DA1', DataAttributeValues='label'), SimpleNamespace(DataAttributeId='DA2', DataAttributeValues='id')]
    monkeypatch.setattr(dav_mod.DataAttributesValues, 'findall', lambda q: davs)
    monkeypatch.setattr(da_mod.DataAttributes, 'findall', lambda q: [{'DataAttributeName': 'groundTruthClassLabel'}] if q.get('DataAttributeId') == 'DA1' else [{'DataAttributeName': 'groundTruthClassNames'}])

    out_path = UT.readPayloadFile(batch_id)
    assert os.path.exists(out_path)
    data = json.loads(open(out_path).read())
    assert data['modelFramework'] == 'sklearn'
    assert data['modelEndPoint'] == 'http://m'


def test_combineReportFile_extracts_html_csv_and_images(tmp_db, monkeypatch):
    # Prepare report path
    report_path = tmp_db / 'report' / 'combined'
    report_path.mkdir(parents=True, exist_ok=True)

    # Fake SecReport list aligned with attack list
    reports = [
        {'ReportName': 'AttackOne.zip', 'SecReportId': 'AttackOne_001', 'CreatedDateTime': 1},
        {'ReportName': 'AttackTwo.zip', 'SecReportId': 'AttackTwo_002', 'CreatedDateTime': 2},
    ]
    monkeypatch.setattr(SecReport, 'findall', lambda q: reports)

    # Zip contents
    files = {
        'report.html': '<style>.x{}</style><div>content</div>',
        'attack.csv': 'a,b\n1,2',
        'image.png': 'PNGDATA',
    }
    zip_bytes = _make_zip_bytes(files)

    # FileStoreDb findOne returns data and fileName
    class DummyFS:
        @staticmethod
        def findOne(key):
            if 'One' in key:
                return {'data': zip_bytes, 'fileName': 'AttackOne.zip'}
            return {'data': zip_bytes, 'fileName': 'AttackTwo.zip'}
    monkeypatch.setattr(savefile_mod.FileStoreDb, 'findOne', DummyFS.findOne)

    payload = {
        'batchid': 'B1',
        'modelName': 'ModelX',
        'attackList': ['AttackOne', 'AttackTwo'],
        'report_path': str(report_path)
    }

    count = UT.combineReportFile(payload)
    assert count == 2
    # HTML appended without style
    html = open(report_path / 'report.html', encoding='utf-8').read()
    assert '<style>' not in html and 'content' in html
    # CSV extracted
    assert (report_path / 'AttackOne.csv').exists()
    # Image extracted
    assert any(p.name.endswith('.png') for p in report_path.rglob('*'))


def test_safe_load_from_file(tmp_db):
    obj = {'x': 1}
    path = tmp_db / 'model' / 'm.joblib'
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(obj, str(path))
    loaded = UT.safe_load_from_file(str(path))
    assert loaded == obj


def test_readModelFile_mongo_joblib(tmp_db, monkeypatch):
    # Arrange DAO stubs similar to readPayload
    batch_id = 'B2'
    monkeypatch.setattr(batch_mod.Batch, 'findall', lambda q: [{'BatchId': batch_id, 'ModelId': 'M1'}])
    monkeypatch.setattr(model_mod.Model, 'findall', lambda q: [{'ModelId': 'M1', 'ModelName': 'ModelY', 'ModelData': 'blobid'}])

    # Model attributes: useModelApi No and framework
    mavs = [SimpleNamespace(ModelAttributeId='A1', ModelAttributeValues='sklearn'), SimpleNamespace(ModelAttributeId='A2', ModelAttributeValues='No')]
    monkeypatch.setattr(mav_mod.ModelAttributesValues, 'findall', lambda q: mavs)
    monkeypatch.setattr(ma_mod.ModelAttributes, 'findall', lambda q: [{'ModelAttributeName': 'modelFramework'}] if q.get('ModelAttributeId') == 'A1' else [{'ModelAttributeName': 'useModelApi'}])

    # Create a joblib file and return its bytes via FileStoreDb.fs.get
    obj = {'y': 2}
    jl_path = tmp_db / 'cacheMemory' / 'temp.joblib'
    jl_path.parent.mkdir(exist_ok=True, parents=True)
    joblib.dump(obj, str(jl_path))
    data_bytes = open(jl_path, 'rb').read()

    class Blob:
        filename = 'model.joblib'
        def read(self):
            return data_bytes
    class DummyFS:
        @staticmethod
        def get(key):
            return Blob()
    monkeypatch.setattr(savefile_mod.FileStoreDb, 'fs', DummyFS)

    data, model_path, model_name, framework = UT.readModelFile(batch_id)
    assert os.path.exists(model_path)
    assert framework == 'sklearn'
    assert model_name == 'ModelY'
    assert isinstance(data, dict) and data['y'] == 2
