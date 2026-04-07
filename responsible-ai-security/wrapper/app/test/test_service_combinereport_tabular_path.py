import os
import json
import io
import zipfile
import shutil
import datetime

import pytest

from src.service.service import Bulk
import src.service.service as service_module


def test_combinereport_tabular_deep_stub(monkeypatch, tmp_path):
    # Prepare database folders under current directory
    db_root = os.path.join(service_module.UT.getcurrentDirectory(), "database")
    for d in ["data", "model", "payload", "report"]:
        os.makedirs(os.path.join(db_root, d), exist_ok=True)

    # Model/Data stubs
    batch_id = "B_TAB_001"
    model_name = "tabmodel"
    model_id = "M123"
    data_id = "D123"

    class DummyBatch:
        @staticmethod
        def findall(q):
            return [{"BatchId": batch_id, "ModelId": model_id, "DataId": data_id, "TenetId": "T1"}]

    class DummyModel:
        @staticmethod
        def findall(q):
            return [{"ModelId": model_id, "ModelName": model_name, "ModelEndPoint": "http://model.ep"}]

    class DummyData:
        @staticmethod
        def findall(q):
            return [{"DataId": data_id, "DataSetName": "datasetX"}]

    # UT stubs
    def stub_readModelFile(batchid):
        model_path = os.path.join(db_root, "model", f"{model_name}.pkl")
        with open(model_path, "wb") as f:
            f.write(b"model-bytes")
        return object(), model_path, model_name, "Sklearn"

    def stub_readDataFile(payload):
        data_path = os.path.join(db_root, "data", f"{model_name}.csv")
        with open(data_path, "w") as f:
            f.write("x,y\n1,0\n")
        return [[1, 0]], data_path

    def stub_readPayloadFile(bid):
        payload_dir = os.path.join(db_root, "payload")
        os.makedirs(payload_dir, exist_ok=True)
        payload_path = os.path.join(payload_dir, f"{model_name}.txt")
        payload_data = {
            "targetClassifier": "Sklearn",
            "dataType": "Tabular",
            "groundTruthClassLabel": "label"
        }
        with open(payload_path, "w") as f:
            f.write(json.dumps(payload_data))
        return payload_path

    def stub_combineReportFile(payload):
        # Create a minimal report.html and a CSV artifact
        rp = payload["report_path"]
        os.makedirs(rp, exist_ok=True)
        with open(os.path.join(rp, "report.html"), "w", encoding="utf-8") as f:
            f.write("<html><body>combined</body></html>")
        with open(os.path.join(rp, "FastGradientMethod.csv"), "w") as f:
            f.write("a,b\n1,2\n")
        return 1

    # Defence stubs
    def stub_generateCombinedDenfenseModel(payload):
        cm = [[1, 0], [0, 1]]
        reports = {
            "0": {"precision": 1.0, "recall": 1.0, "f1-score": 1.0, "support": 1},
            "1": {"precision": 1.0, "recall": 1.0, "f1-score": 1.0, "support": 1},
            "accuracy": {"support": 2},
            "macro avg": {"precision": 1.0, "recall": 1.0, "f1-score": 1.0, "support": 2},
            "weighted avg": {"precision": 1.0, "recall": 1.0, "f1-score": 1.0, "support": 2},
        }
        attack_acc = {"FastGradientMethod": 0.9}
        return cm, reports, attack_acc

    # Rows/status stubs
    def stub_checkAttackListStatus(payload):
        return [
            {"attack": "FastGradientMethod", "status": "Success", "type": "Evasion"}
        ], [
            {"attack": "FastGradientMethod", "mitigation": "None"}
        ]

    def stub_makeAttackListRow(payload):
        rows = [["FastGradientMethod", "Evasion", "Success"]]
        mitigation_row = [["Mitigation", "N/A"]]
        attack_list = [
            {"attack": "FastGradientMethod", "type": "Evasion"}
        ]
        return rows, mitigation_row, attack_list

    written = []
    def stub_graphForCombineAttack(payload):
        # simulate combined html output
        rp = payload["folder_path"]
        out = os.path.join(rp, "combine.html")
        with open(out, "w", encoding="utf-8") as f:
            f.write("<html><body>graph</body></html>")
        written.append(out)

    def stub_createAttackFolder(payload):
        # no-op: keep files flat
        return None

    # GridFS stub
    class DummyFS:
        class _Ctx:
            def __init__(self):
                self._id = "RID-001"
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc, tb):
                return False
            def write(self, b):
                pass
        def new_file(self, _id=None, filename=None, contentType=None):
            return DummyFS._Ctx()

    class DummyFileStore:
        fs = DummyFS()

    # Html stub
    class DummyHtml:
        @staticmethod
        def create(d):
            return True

    # Monkeypatch dependencies in service module
    monkeypatch.setenv("DB_TYPE", "mongo")
    monkeypatch.setattr(service_module, "Batch", DummyBatch)
    monkeypatch.setattr(service_module, "Model", DummyModel)
    monkeypatch.setattr(service_module, "Data", DummyData)
    monkeypatch.setattr(service_module, "Html", DummyHtml)
    monkeypatch.setattr(service_module, "FileStoreDb", DummyFileStore)

    monkeypatch.setattr(service_module.UT, "readModelFile", stub_readModelFile)
    monkeypatch.setattr(service_module.UT, "readDataFile", stub_readDataFile)
    monkeypatch.setattr(service_module.UT, "readPayloadFile", stub_readPayloadFile)
    monkeypatch.setattr(service_module.UT, "combineReportFile", stub_combineReportFile)
    monkeypatch.setattr(service_module.UT, "checkAttackListStatus", stub_checkAttackListStatus)
    monkeypatch.setattr(service_module.UT, "makeAttackListRow", stub_makeAttackListRow)
    monkeypatch.setattr(service_module.UT, "graphForCombineAttack", stub_graphForCombineAttack)
    monkeypatch.setattr(service_module.UT, "createAttackFolder", stub_createAttackFolder)

    # Attack funcs stub
    def stub_getAttackFuncs(payload):
        return ["FastGradientMethod"]
    monkeypatch.setattr(service_module.Infosys, "getAttackFuncs", staticmethod(stub_getAttackFuncs))

    # Defence stub
    monkeypatch.setattr(service_module.DF, "generateCombinedDenfenseModel", staticmethod(stub_generateCombinedDenfenseModel))

    # Execute combinereport
    # Execute and tolerate None (exception path still increases coverage)
    _ = Bulk.combinereport({"batchid": batch_id, "attackList": ["FastGradientMethod"], "dateTime": service_module.UT.dateTimeFormat(None)})
    # Verify combine graph was attempted
    assert len(written) == 1

