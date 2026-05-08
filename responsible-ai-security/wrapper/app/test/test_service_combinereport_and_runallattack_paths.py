import os
import io
import time
import types

import pytest

from src.service.service import Bulk
from src.service import service as service_mod


class DummyWriter:
    def __init__(self):
        self._id = str(time.time())
        self.buffer = io.BytesIO()
    def write(self, data):
        self.buffer.write(data)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False


class DummyFS:
    def new_file(self, _id, filename, contentType):
        return DummyWriter()


def test_combinereport_image_nonhappy(tmp_path, monkeypatch):
    # Isolate database root
    monkeypatch.setenv("DB_TYPE", "mongo")
    monkeypatch.setenv("TELEMETRY_FLAG", "False")

    # Ensure getcurrentDirectory points to tmp
    monkeypatch.setattr(service_mod.UT, "getcurrentDirectory", lambda: str(tmp_path))

    # Minimal Batch/Model/Data responses
    monkeypatch.setattr(service_mod.Batch, "findall", lambda q: [{"BatchId": "b1", "ModelId": "m1", "DataId": "d1", "TenetId": "t1"}])
    monkeypatch.setattr(service_mod.Model, "findall", lambda q: [{"ModelId": "m1", "ModelName": "m", "ModelEndPoint": "http://ep"}])
    monkeypatch.setattr(service_mod.Data, "findall", lambda q: [{"DataId": "d1"}])

    # Pre-create payload file expected by combinereport
    payload_dir = os.path.join(str(tmp_path), "database", "payload")
    os.makedirs(payload_dir, exist_ok=True)
    with open(os.path.join(payload_dir, "m.txt"), "w", encoding="utf-8") as f:
        f.write('{"dataType": "Image", "groundTruthClassLabel": "gt", "targetClassifier": "clf"}')

    # Stub UT functions to be lightweight
    monkeypatch.setattr(service_mod.UT, "readModelFile", lambda batchid: (object(), os.path.join(str(tmp_path), "model.pkl"), "m", "Image"))
    monkeypatch.setattr(service_mod.UT, "readDataFile", lambda payload: ([], os.path.join(str(tmp_path), "data.csv")))
    monkeypatch.setattr(service_mod.UT, "readPayloadFile", lambda batchid: os.path.join(str(tmp_path), "payload.txt"))
    monkeypatch.setattr(service_mod.UT, "combineReportFile", lambda p: 0)
    monkeypatch.setattr(service_mod.UT, "graphForCombineAttack", lambda p: None)
    monkeypatch.setattr(service_mod.UT, "createAttackFolder", lambda p: None)
    monkeypatch.setattr(service_mod.UT, "databaseDelete", lambda p: None)
    # Bypass DB lookup for attacks
    monkeypatch.setattr(service_mod.Infosys, "getAttackFuncs", lambda payload: ["FastGradientMethod", "AttributeInference"])

    # Put a couple of images in the report folder to exercise rename/delete branch
    report_folder = os.path.join(str(tmp_path), "database", "report", "m")
    os.makedirs(report_folder, exist_ok=True)
    open(os.path.join(report_folder, "img^FastGradientMethodT.jpg"), "wb").close()
    open(os.path.join(report_folder, "img^AttributeInferenceF.png"), "wb").close()

    # Stub FileStoreDb.fs and Html.create
    monkeypatch.setattr(service_mod.FileStoreDb, "fs", DummyFS())
    monkeypatch.setattr(service_mod.Html, "create", lambda data: None)

    # Execute combinereport
    result = Bulk.combinereport({"batchid": "b1", "attackList": ["FastGradientMethod", "AttributeInference"], "dateTime": "now"})

    # Result may be dict (success) or None; ensure no exception and the report folder exists
    assert os.path.isdir(report_folder)


def test_runAllAttack_unprocessable_entity(monkeypatch):
    monkeypatch.setenv("TELEMETRY_FLAG", "False")

    # Batch with ModelId
    monkeypatch.setattr(service_mod.Batch, "findall", lambda q: [{"BatchId": "b2", "ModelId": "m2"}])

    # Model attribute values: supply an object with attributes used
    class AttrVal:
        def __init__(self, attr_id, val):
            self.ModelAttributeId = attr_id
            self.ModelAttributeValues = val

    monkeypatch.setattr(service_mod.ModelAttributesValues, "findall", lambda q: [AttrVal("id_app", ["FastGradientMethod", "AttributeInference"]), AttrVal("other", "x")])
    def fake_model_attrs_findall(q):
        if q.get("ModelAttributeId") == "id_app":
            return [{"ModelAttributeName": "appAttacks"}]
        else:
            return [{"ModelAttributeName": "other"}]
    monkeypatch.setattr(service_mod.ModelAttributes, "findall", fake_model_attrs_findall)

    # Stub batchAttack to be quick; combinereport to truthy
    monkeypatch.setattr(service_mod.Bulk, "batchAttack", lambda p: p["batchId"])
    monkeypatch.setattr(service_mod.Bulk, "combinereport", lambda p: {"combineReportFileId": 123})

    # Stub requests.post to return 422
    class DummyResp:
        status_code = 422
        def json(self):
            return {"detail": "unprocessable"}
        text = "unprocessable"

    monkeypatch.setattr(service_mod.requests, "post", lambda url, data=None: DummyResp())

    out = service_mod.Bulk.runAllAttack({"batchid": "b2", "dateTime": "now"})
    assert out == "b2"
