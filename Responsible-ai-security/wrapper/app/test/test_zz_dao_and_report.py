import io
import os

import pytest

from src.dao.DatabaseConnection import DB
from src.dao.ModelDb import Model
from src.dao.DataDb import Data
from src.dao.Security.AttackDb import Attack
from src.dao.SaveFileDB import FileStoreDb


def test_db_connect_returns_mongomock_db():
    db = DB.connect()
    assert db is not None
    assert hasattr(db, "name")
    # ensure inserts work and are isolated
    inserted_id = db["ping"].insert_one({"ok": 1}).inserted_id
    assert inserted_id is not None


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
    assert Model.update(model_id, {"ModelName": "m2"}) is True
    assert Model.findOne(model_id).ModelName == "m2"
    assert "m2" in Model.get_all("ModelName")
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
    assert Data.findOne(data_id).DataSetName == "ds"
    assert Data.update(data_id, {"DataSetName": "ds2"}) is True
    assert Data.findOne(data_id).DataSetName == "ds2"
    Data.delete({"_id": data_id})
    assert Data.findall({"_id": data_id}) == []


def test_attack_crud_cycle():
    atk_id = Attack.create({"attackName": "Boundary"})
    assert atk_id is not None
    assert Attack.findOne(atk_id).AttackName == "Boundary"
    assert Attack.update(atk_id, {"AttackName": "Deepfool"}) is True
    assert Attack.findOne(atk_id).AttackName == "Deepfool"
    Attack.delete({"_id": atk_id})
    assert Attack.findall({"_id": atk_id}) == []


class DummyUpload:
    def __init__(self, data: bytes, content_type: str = "application/octet-stream"):
        self.file = io.BytesIO(data)
        self.content_type = content_type


def test_filestoredb_gridfs_create_find_update_delete():
    up = DummyUpload(b"abc", content_type="text/plain")
    fid = FileStoreDb.create(up, modelName="test.txt")
    assert fid is not None
    one = FileStoreDb.findOne(fid)
    assert one["fileName"] == "test.txt"
    assert one["data"] == b"abc"
    assert one["type"] == "text/plain"
    up2 = DummyUpload(b"xyz", content_type="text/plain")
    fid2 = FileStoreDb.update(fid, up2, modelName="test.txt")
    assert fid2 == fid
    assert FileStoreDb.findOne(fid)["data"] == b"xyz"
    FileStoreDb.delete(fid)
    assert FileStoreDb.findOne(fid) is None
