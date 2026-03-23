import os
import io
import csv
import json
import time
import shutil
import zipfile
import tempfile
import datetime

import numpy as np
import pandas as pd

from src.service.utility import Utility
from src.dao.Security import SecReportDb as _SecReportDb
from src.dao.SaveFileDB import FileStoreDb
from src.service.art import Art
from src.service import report as report_module


class DummyModel:
    def __init__(self, benign_label=0, adv_label=1, n_classes=3):
        self.benign_label = benign_label
        self.adv_label = adv_label
        self.n_classes = n_classes

    def _to_one_hot(self, label):
        arr = np.zeros((1, self.n_classes), dtype=float)
        arr[0, label] = 1.0
        return arr

    def predict(self, x):
        # Decide based on the sum of the sample to alternate labels
        if isinstance(x, list):
            x = np.array(x)
        # If called with a single sample shaped (1, n)
        if x.ndim == 2 and x.shape[0] == 1:
            s = int(np.sum(x))
            label = self.benign_label if (s % 2 == 0) else self.adv_label
            return self._to_one_hot(label)
        # Fallback: return the benign label for all
        return np.vstack([self._to_one_hot(self.benign_label) for _ in range(len(x))])


def test_find_duplicates_simple():
    x = np.array([[1, 2], [1, 2], [3, 4]])
    dup = Utility.find_duplicates(x)
    assert dup.tolist() == [0, 1, 0]


def test_calc_precision_recall_various():
    predicted = [1, 0, 1, 1]
    actual = [1, 1, 0, 1]
    precision, recall = Utility.calc_precision_recall(predicted, actual, positive_value=1)
    assert 0 <= precision <= 1 and 0 <= recall <= 1

    # No positives predicted -> precision treated as 1
    p2, r2 = Utility.calc_precision_recall([0, 0], [0, 1], positive_value=1)
    assert p2 == 1 and 0 <= r2 <= 1

    # No positives actual -> recall treated as 1
    p3, r3 = Utility.calc_precision_recall([1, 1], [0, 0], positive_value=1)
    assert r3 == 1 and 0 <= p3 <= 1


def test_safe_load_and_database_delete_file_and_dir(tmp_path):
    obj = {"a": 1, "b": [1, 2, 3]}
    # Use joblib via Utility.safe_load_from_file by dumping with pandas to_pickle
    file_path = tmp_path / "obj.pkl"
    pd.to_pickle(obj, file_path)
    loaded = Utility.safe_load_from_file(str(file_path))
    assert loaded == obj

    # databaseDelete on file
    Utility.databaseDelete(str(file_path))
    assert not file_path.exists()

    # databaseDelete on directory
    subdir = tmp_path / "subdir"
    subdir.mkdir(parents=True, exist_ok=True)
    (subdir / "a.txt").write_text("x")
    Utility.databaseDelete(str(subdir))
    assert not subdir.exists()


def test_extractCSVFromZip_roundtrip(tmp_path):
    # Create a csv inside a zip
    data_dir = tmp_path / "data"
    cache_dir = tmp_path / "cache"
    data_dir.mkdir()
    cache_dir.mkdir()
    csv_name = "sample.csv"
    # Build simple CSV content
    csv_content = "x,y\n1,2\n".encode("utf-8")

    zip_path = cache_dir / "pack.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(csv_name, csv_content)

    out = Utility.extractCSVFromZip(str(zip_path), str(data_dir))
    assert out.endswith(csv_name)
    assert os.path.exists(out)


def test_extractIMAGEFromZip_copies_images(tmp_path):
    data_dir = tmp_path / "data"
    cache_dir = tmp_path / "cache"
    data_dir.mkdir()
    cache_dir.mkdir()

    # Create a fake png and jpg inside zip
    png_name = "img1.png"
    jpg_name = "img2.jpg"
    # Minimal PNG header bytes + dummy data
    png_bytes = b"\x89PNG\r\n\x1a\n" + b"0" * 10
    jpg_bytes = b"\xFF\xD8\xFF" + b"0" * 10

    zip_path = cache_dir / "imgs.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(png_name, png_bytes)
        zf.writestr(jpg_name, jpg_bytes)

    out_dir = Utility.extractIMAGEFromZip(str(zip_path), str(data_dir))
    # Should be a folder derived from zip name under data_dir
    assert os.path.isdir(out_dir)
    assert os.path.exists(os.path.join(out_dir, png_name))
    assert os.path.exists(os.path.join(out_dir, jpg_name))


def test_updateReportsList_and_sortReportsList():
    now = datetime.datetime.now()
    earlier = now - datetime.timedelta(hours=1)

    # Two reports for same attack; newer should be chosen
    reports = [
        {"ReportName": "AttackA.html", "CreatedDateTime": earlier},
        {"ReportName": "AttackA.html", "CreatedDateTime": now},
        {"ReportName": "AttackB.html", "CreatedDateTime": earlier},
        {"ReportName": "ModelName.zip", "CreatedDateTime": now},
    ]

    attack_list = ["AttackA", "AttackB"]
    filtered = Utility.updateReportsList({
        "reportList": reports,
        "modelName": "ModelName",
        "attackList": attack_list,
    })

    # Should skip model zip and include one per attack
    names = [r["ReportName"].split(".")[0] for r in filtered]
    assert names == attack_list

    # sortReportsList should sort descending by CreatedDateTime
    sorted_reports = Utility.sortReportsList(filtered)
    assert sorted_reports[0]["CreatedDateTime"] >= sorted_reports[-1]["CreatedDateTime"]


def test_dateTimeFormat_none_and_value():
    # None -> contains current date format and UTC suffix
    s = Utility.dateTimeFormat(None)
    assert isinstance(s, str) and s.endswith(" UTC")

    dt = datetime.datetime(2020, 1, 2, 15, 4, 5)
    s2 = Utility.dateTimeFormat(dt)
    assert "02-01-2020" in s2 and "03:04:05 PM" in s2


def test_combineList_evasion_and_inference():
    attack = np.array([[0, 1], [1, 0]])
    target = np.array([[1, 1], [1, 1]])
    pred_evasion = np.array([0, 1])  # last col equals target last col for row0 only

    e1, f1 = Utility.combineList({
        "attack_data": attack,
        "target_data": target,
        "prediction_data": pred_evasion,
        "type": "Evasion",
    })
    # For row 1, target last col=1, pred=1 -> no change; row0 mismatch -> flagged
    assert e1[0][-1] in ("True", "False") and isinstance(f1, list)

    pred_inf = np.array([1, 1])
    e2, f2 = Utility.combineList({
        "attack_data": attack,
        "target_data": target,
        "prediction_data": pred_inf,
        "type": "Inference",
    })
    assert e2[0][-1] in ("True", "False") and isinstance(f2, list)


def test_checkList_with_dummy_model():
    model = DummyModel(benign_label=0, adv_label=1, n_classes=3)
    x = np.array([[1.0, 1.0], [2.0, 2.0]])
    adv = np.array([[2.0, 1.0], [3.0, 1.0]])

    out = Utility.checkList({
        "model": model,
        "original_data": x,
        "adversial_data": adv,
    })
    # Expect a list of mismatches with indices and labels
    assert isinstance(out, list)
    if out:
        assert len(out[0]) == 4


def test_combineReportFile_mongo_zip_extraction(tmp_path, monkeypatch):
    # Prepare fake SecReport entries
    now = datetime.datetime.now()
    def fake_findall(query):
        return [
            {"SecReportId": "AttackA_id.zip", "ReportName": "AttackA.html", "CreatedDateTime": now},
            {"SecReportId": "AttackB_id.zip", "ReportName": "AttackB.html", "CreatedDateTime": now},
        ]

    monkeypatch.setenv("DB_TYPE", "mongo")
    monkeypatch.setenv("TELEMETRY_FLAG", "False")
    monkeypatch.setattr(_SecReportDb.SecReport, "findall", staticmethod(fake_findall))

    # Build a small zip payload containing html, csv and image bytes
    def build_zip_bytes(name):
        mem = io.BytesIO()
        with zipfile.ZipFile(mem, "w") as zf:
            zf.writestr(f"{name}.html", "<html><style>xx</style><body>ok</body></html>")
            zf.writestr(f"{name}.csv", "a,b\n1,2\n")
            zf.writestr(f"{name}.png", b"\x89PNG\r\n\x1a\n" + b"0" * 8)
        mem.seek(0)
        return mem.read()

    def fake_findOne(file_id):
        attack = file_id.split("_")[0]
        data = build_zip_bytes(attack)
        return {"data": data, "fileName": f"{attack}.zip"}

    monkeypatch.setattr(FileStoreDb, "findOne", staticmethod(fake_findOne))

    report_dir = tmp_path / "reports"
    report_dir.mkdir()
    # Pre-create expected database directories to avoid os.mkdir on missing parents
    base_db = os.path.join(Utility.getcurrentDirectory(), "database")
    for sub in ("data", "model", "payload", "report"):
        os.makedirs(os.path.join(base_db, sub), exist_ok=True)
    count = Utility.combineReportFile({
        "batchid": 123,
        "modelName": "ModelX",
        "attackList": ["AttackA", "AttackB"],
        "report_path": str(report_dir),
    })
    assert count == 2
    # Combined artifacts should exist under report_dir
    assert (report_dir / "report.html").exists()
    assert (report_dir / "AttackA.csv").exists()
    assert (report_dir / "AttackB.csv").exists()


def test_isContentSafe_happy_and_unhappy():
    assert Utility.isContentSafe({"a": "safe_name-1_2"}) is True
    # Illegal character like '/'
    assert Utility.isContentSafe({"a": "bad/name"}) is False


def test_art_membership_inference_rule_smoke(tmp_path, monkeypatch):
    # Ensure database/payload exists for payload file write
    base_db = os.path.join(Utility.getcurrentDirectory(), "database")
    os.makedirs(os.path.join(base_db, "payload"), exist_ok=True)

    # Create a tiny tabular dataset
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1], [2, 2], [2, 1]], dtype=float)
    y = np.array([0, 0, 0, 1, 1, 1])

    # Fit a simple scikit-learn model
    from sklearn.svm import SVC
    model = SVC(probability=True)
    model.fit(X, y)

    # Mock UT.readModelFile to return our model and metadata
    def fake_readModelFile(_payload):
        model_path = str(tmp_path / "model.pkl")
        open(model_path, "wb").write(b"x")
        return model, model_path, "TestModel", "Sklearn"

    # Mock UT.readDataFile to return a DataFrame and a path
    def fake_readDataFile(payload):
        df = pd.DataFrame({"f1": X[:, 0], "f2": X[:, 1], "label": y})
        data_path = str(tmp_path / "data.csv")
        df.to_csv(data_path, index=False)
        return df, data_path

    # Mock UT.readPayloadFile to create the payload file the art code reads
    def fake_readPayloadFile(_payload):
        payload_path = os.path.join(base_db, "payload", "TestModel.txt")
        with open(payload_path, "w", encoding="utf-8") as f:
            json.dump({"groundTruthClassLabel": "label"}, f)
        return payload_path

    # Avoid actual deletions
    monkeypatch.setenv("TELEMETRY_FLAG", "False")
    monkeypatch.setattr("src.service.utility.Utility.readModelFile", staticmethod(fake_readModelFile))
    monkeypatch.setattr("src.service.utility.Utility.readDataFile", staticmethod(fake_readDataFile))
    monkeypatch.setattr("src.service.utility.Utility.readPayloadFile", staticmethod(fake_readPayloadFile))
    monkeypatch.setattr("src.service.utility.Utility.databaseDelete", lambda *_args, **_kw: None)

    # Stub report generation to a fast return
    monkeypatch.setattr(report_module.Report, "generatecsvreportart", staticmethod(lambda _p: "folder123"))
    # Stub out ART attack class used inside service.art to avoid dependencies/shape issues
    class _StubMIRule:
        def __init__(self, _classifier):
            pass
        def infer(self, x, y):
            # Return all-ones array-like of membership flags for given x
            return np.ones(len(x), dtype=int)

    monkeypatch.setattr("src.service.art.MembershipInferenceBlackBoxRuleBased", _StubMIRule)

    # Execute and assert a Job_Id is produced
    out = Art.MembershipInferenceRule(999)
    assert isinstance(out, dict) and "Job_Id" in out and out["Job_Id"] == "folder123"
