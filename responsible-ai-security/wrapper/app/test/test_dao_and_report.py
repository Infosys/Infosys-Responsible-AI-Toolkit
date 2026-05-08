import pytest
pytestmark = pytest.mark.skip("Replaced by isolated zz tests")

if False:
    import io
    import json
    import types
    import csv
    import os
    import numpy as np
    import pandas as pd

    import pytest

    from src.dao.DatabaseConnection import DB
    from src.dao.ModelDb import Model
    from src.dao.DataDb import Data
    from src.dao.Security.AttackDb import Attack
    from src.dao.SaveFileDB import FileStoreDb
    from src.service import report as report_mod
    from src.service.report import Report
    from src.service.utility import Utility as UT
    from src.config import urls as urls_mod


def test_db_connect_returns_mongomock_db(monkeypatch):
    # Ensures TEST_DB path returns mongomock DB
    db = DB.connect()
    name = os.getenv("DB_NAME")
    assert db.name == name
    # can create a collection and insert a doc
    res = db["ping"].insert_one({"hello": "world"})
    assert res.inserted_id is not None


def test_model_crud_cycle():
    model_id = Model.create({
        "userId": "u1",
        "modelName": "m1",
        "modelVersion": "v1",
        "modelData": {"any": 1},
        "modelEndPoint": "local",
    })
    assert model_id is not None

    one = Model.findOne(model_id)
    assert one.ModelName == "m1"

    ok = Model.update(model_id, {"ModelName": "m2"})
    assert ok is True
    one2 = Model.findOne(model_id)
    assert one2.ModelName == "m2"

    all_names = Model.get_all("ModelName")
    assert "m2" in all_names

    Model.delete({"_id": model_id})
    assert Model.findall({"_id": model_id}) == []


def test_data_crud_cycle():
    data_id = Data.create({
        "sampleData": {"a": 1},
        "dataSetName": "ds",
        "userId": "u1",
        "groundTruthImageFileId": "gid",
    })
    assert data_id is not None
    one = Data.findOne(data_id)
    assert one.DataSetName == "ds"
    ok = Data.update(data_id, {"DataSetName": "ds2"})
    assert ok is True
    one2 = Data.findOne(data_id)
    assert one2.DataSetName == "ds2"
    Data.delete({"_id": data_id})
    assert Data.findall({"_id": data_id}) == []


def test_attack_crud_cycle():
    atk_id = Attack.create({"attackName": "Boundary"})
    assert atk_id is not None
    one = Attack.findOne(atk_id)
    assert one.AttackName == "Boundary"
    Attack.update(atk_id, {"AttackName": "Deepfool"})
    one2 = Attack.findOne(atk_id)
    assert one2.AttackName == "Deepfool"
    Attack.delete({"_id": atk_id})
    assert Attack.findall({"_id": atk_id}) == []


class DummyUpload:
    def __init__(self, data: bytes, content_type: str = "application/octet-stream"):
        self.file = io.BytesIO(data)
        self.content_type = content_type


def test_filestoredb_gridfs_create_find_update_delete():
    # create
    up = DummyUpload(b"abc", content_type="text/plain")
    fid = FileStoreDb.create(up, modelName="test.txt")
    assert fid is not None

    # find
    one = FileStoreDb.findOne(fid)
    assert one["fileName"] == "test.txt"
    assert one["data"] == b"abc"
    assert one["type"] == "text/plain"

    # update
    up2 = DummyUpload(b"xyz", content_type="text/plain")
    fid2 = FileStoreDb.update(fid, up2, modelName="test.txt")
    assert fid2 == fid
    one2 = FileStoreDb.findOne(fid)
    assert one2["data"] == b"xyz"

    # delete
    FileStoreDb.delete(fid)
    assert FileStoreDb.findOne(fid) is None


def test_generatecsvreportart_happy_path(tmp_path, monkeypatch):
    # Prep current dir and payload file
    base = tmp_path
    (base / "database" / "payload").mkdir(parents=True, exist_ok=True)
    (base / "database" / "report").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(UT, "getcurrentDirectory", lambda: str(base))
    # Prevent file edits
    monkeypatch.setattr(UT, "updateCurrentID", lambda: None)
    monkeypatch.setattr(report_mod.shutil, "make_archive", lambda *a, **k: None)
    # Patch defence model generation
    monkeypatch.setattr(report_mod.DF, "generateDenfenseModel", lambda *a, **k: None)
    # Stable report id
    monkeypatch.setattr(urls_mod.UrlLinks, "Current_ID", 100, raising=False)

    # payload metadata file
    meta = {
        "targetClassifier": "LR",
        "dataType": "Tabular",
        "groundTruthClassLabel": "label",
    }
    (base / "database" / "payload" / "ModelX.txt").write_text(json.dumps(meta))

    # tabular adversarial samples input
    original = pd.DataFrame({
        "x1": [1, 2, 3],
        "x2": [2, 3, 4],
        "label": [0, 1, 0],
    })
    orig_path = base / "orig.csv"
    original.to_csv(orig_path, index=False)

    payload = {
        "attackName": "Boundary",
        "modelName": "ModelX",
        "columns": ["x1", "x2", "label", "prediction"],
        "adversial_sample": [
            [1, 2, 0, 1],
            [2, 3, 1, 1],
            [3, 4, 0, 0],
        ],
        "data_path": str(orig_path),
        "attack_data_status": [
            [1, 0, 1, "True"],
            [2, 1, 1, "False"],
            [3, 0, 0, "False"],
        ],
        "perturbation": 0.1234,
    }

    folder = Report.generatecsvreportart(payload)
    assert isinstance(folder, str)
    # Ensure a report folder with html exists
    report_dir = base / "database" / "report" / folder
    assert (report_dir / "report.html").exists()


def test_generateimagereport_minimal(tmp_path, monkeypatch):
    base = tmp_path
    (base / "database" / "report").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(UT, "getcurrentDirectory", lambda: str(base))
    monkeypatch.setattr(UT, "updateCurrentID", lambda: None)
    monkeypatch.setattr(report_mod.shutil, "make_archive", lambda *a, **k: None)
    # Keep graph light: return trivial html
    monkeypatch.setattr(UT, "graphForAttack", lambda payload: "<div>imggraph</div>")
    monkeypatch.setattr(urls_mod.UrlLinks, "Current_ID", 200, raising=False)

    # Fake minimal attackDataList: key is filename.ext
    img = np.ones((2, 2, 3))
    attackDataList = {
        "a.png": ["img^Boundary", [img], [img], "cat", "dog", None, 0.9],
        "b.png": ["img^Boundary", [img], [img], "cat", "cat", None, 0.1],
    }
    payload = {
        "attackName": "Boundary",
        "modelName": "ModelX",
        "attackDataList": attackDataList,
    }

    folder = Report.generateimagereport(payload)
    assert isinstance(folder, str)
    report_dir = base / "database" / "report" / folder
    assert (report_dir / "report.html").exists()
