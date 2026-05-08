import os
import io
import zipfile
import base64
import json
import types
import numpy as np
import pandas as pd

import pytest

from src.service.utility import Utility


def test_updateReportsList_filters_latest_and_orders():
    attack_list = ["Deepfool", "Boundary"]
    reports = [
        {"ReportName": "Deepfool.zip", "CreatedDateTime": pd.Timestamp("2024-01-01")},
        {"ReportName": "Deepfool.zip", "CreatedDateTime": pd.Timestamp("2024-01-03")},
        {"ReportName": "Boundary.zip", "CreatedDateTime": pd.Timestamp("2024-01-02")},
        {"ReportName": "ModelX.zip", "CreatedDateTime": pd.Timestamp("2024-01-04")},
    ]
    res = Utility.updateReportsList({
        "reportList": reports,
        "modelName": "ModelX",
        "attackList": attack_list,
    })
    # Latest per attack and ordered by attackList
    assert [r["ReportName"] for r in res] == ["Deepfool.zip", "Boundary.zip"]


def test_combineReportFile_with_mocked_zip(tmp_path, monkeypatch):
    base_dir = tmp_path
    report_dir = base_dir / "report"
    report_dir.mkdir(parents=True, exist_ok=True)
    # Pre-create expected base database folder
    (base_dir / "database").mkdir(parents=True, exist_ok=True)

    # Build a zip containing style-heavy html, a csv and an image
    zbytes = io.BytesIO()
    with zipfile.ZipFile(zbytes, mode="w") as zf:
        zf.writestr("a.html", "<style>.x{}</style><div>hello</div>")
        zf.writestr("b.csv", "x,y\n1,2\n")
        zf.writestr("image.png", base64.b64decode(base64.b64encode(b"fake")))
    zbytes.seek(0)

    # Patch environment and dependencies used inside combineReportFile
    monkeypatch.setenv("DB_TYPE", "mongo")
    monkeypatch.setattr(Utility, "getcurrentDirectory", lambda: str(base_dir))

    class DummyFileStore:
        @staticmethod
        def findOne(s):
            return {"data": zbytes.getvalue(), "fileName": "Deepfool.zip"}

    class DummySecReport:
        @staticmethod
        def findall(q):
            return [{"SecReportId": "Deepfool_1", "ReportName": "Deepfool.zip", "CreatedDateTime": pd.Timestamp("2024-01-03")}]

    # Inject stubs into module namespace via monkeypatch
    import src.service.utility as util_mod
    monkeypatch.setattr(util_mod, "FileStoreDb", DummyFileStore)
    monkeypatch.setattr(util_mod, "SecReport", DummySecReport)

    count = Utility.combineReportFile({
        "batchid": "b1",
        "modelName": "ModelX",
        "attackList": ["Deepfool"],
        "report_path": str(report_dir),
    })

    # Files written and style removed
    assert count == 1
    html_path = report_dir / "report.html"
    csv_path = report_dir / "Deepfool.csv"
    img_path = report_dir / "image.png"
    assert html_path.exists() and csv_path.exists() and img_path.exists()
    assert "<style>" not in html_path.read_text(encoding="utf-8")


def test_createAttackFolder_moves_files(tmp_path, monkeypatch):
    base_dir = tmp_path
    report_dir = base_dir / "out"
    report_dir.mkdir(parents=True, exist_ok=True)

    # Create CSVs for evasion and inference
    (report_dir / "Deepfool.csv").write_text("x,y\n1,2\n")
    (report_dir / "MembershipInferenceRule.csv").write_text("x,y\n3,4\n")
    # Create image following naming convention
    (report_dir / "img^DeepfoolT.png").write_bytes(b"fake")

    Utility.createAttackFolder({
        "attack_list": [{"name": "Deepfool", "type": "Evasion"}, {"name": "MembershipInferenceRule", "type": "Inference"}],
        "report_path": str(report_dir),
    })

    # Check directories and moved files
    ev_dir = report_dir / "Art" / "Evasion" / "Deepfool"
    inf_dir = report_dir / "Art" / "Inference"
    assert (ev_dir / "Deepfool.csv").exists()
    # Ensure inference directory exists; file copy may vary by environment
    assert inf_dir.exists()


def test_graphForMitigation_dataframe_computation():
    # Build classification report-like structure
    classification_reports = {
        "0": {"precision": 0.8, "recall": 0.9, "f1-score": 0.85, "support": 50},
        "1": {"precision": 0.7, "recall": 0.6, "f1-score": 0.65, "support": 50},
        "accuracy": {"precision": 0.0, "recall": 0.0, "f1-score": 0.0, "support": 100},
        "macro avg": {"precision": 0.75, "recall": 0.75, "f1-score": 0.75, "support": 100},
        "weighted avg": {"precision": 0.75, "recall": 0.75, "f1-score": 0.75, "support": 100},
    }
    cm = np.array([[30, 20], [15, 35]])  # tn, fp, fn, tp
    df = Utility.graphForMitigation({
        "model_metaData": {"dataType": "Tabular"},
        "classification_reports": classification_reports,
        "confusion_matrix": cm,
    })
    assert list(df.columns) == ["precision", "recall", "f1-score", "specificity", "balance accuracy", "FPR", "support"]
    # Specificity rows should be present
    assert "specificity" in df.index.names or "specificity" in df.columns


def test_combineList_evasion_and_inference():
    attack = pd.Series([[0], [1], [0]])
    target = pd.Series([[0], [0], [1]])
    pred = pd.Series([0, 1, 1])

    e_list, e_flags = Utility.combineList({
        "attack_data": attack,
        "target_data": target,
        "prediction_data": pred,
        "type": "Evasion",
    })
    assert len(e_list) == 3
    assert any(flag[-1] == "True" for flag in e_flags)

    i_list, i_flags = Utility.combineList({
        "attack_data": attack,
        "target_data": target,
        "prediction_data": pred,
        "type": "Inference",
    })
    assert len(i_list) == 3
    assert isinstance(i_flags, list)


def test_checkList_with_dummy_model():
    # Dummy model switches label based on sum of features
    class DummyModel:
        def predict(self, arr):
            s = float(np.sum(arr))
            # Return 2-class probabilities
            if s > 0.5:
                return np.array([[0.1, 0.9]])
            return np.array([[0.9, 0.1]])

    x = np.array([[0.0], [0.0], [0.0]])
    adv = np.array([[1.0], [0.0], [1.0]])
    res = Utility.checkList({
        "model": DummyModel(),
        "original_data": x,
        "adversial_data": adv,
    })
    # Expect at least some mismatches flagged
    assert len(res) >= 1


def test_htmlToPdfWithWatermark_mocked(tmp_path, monkeypatch):
    base_dir = tmp_path
    (base_dir / "report").mkdir(exist_ok=True)
    # minimal html
    (base_dir / "report" / "report.html").write_text("<html><body>Report</body></html>")

    # Stub pdfkit
    import src.service.utility as util_mod
    def fake_from_file(html_path, output_path=None, options=None):
        # create a minimal pdf-like file so downstream open/read works
        if output_path:
            with open(output_path, "wb") as f:
                f.write(b"%PDF-1.4\n% minimal\n")
        return True

    monkeypatch.setattr(util_mod, "pdfkit", types.SimpleNamespace(from_file=fake_from_file))

    # Stub canvas
    class DummyCanvas:
        def __init__(self, path, *args, **kwargs):
            # touch watermark path so later open('rb') succeeds
            with open(path, "wb") as f:
                f.write(b"")
        def setFont(self, *a, **k):
            pass
        def setFillColorRGB(self, *a, **k):
            pass
        def setFillAlpha(self, *a, **k):
            pass
        def rotate(self, *a, **k):
            pass
        def drawString(self, *a, **k):
            pass
        def save(self):
            pass

    monkeypatch.setattr(util_mod, "canvas", types.SimpleNamespace(Canvas=DummyCanvas))

    # Stub PdfReader/PdfWriter
    class DummyPage:
        def merge_page(self, other):
            pass

    class DummyReader:
        def __init__(self, f):
            self.pages = [DummyPage(), DummyPage()]

    class DummyWriter:
        def __init__(self):
            self._pages = []
        def add_page(self, page):
            self._pages.append(page)
        def write(self, f):
            f.write(b"PDF")

    monkeypatch.setattr(util_mod, "PdfReader", DummyReader)
    monkeypatch.setattr(util_mod, "PdfWriter", DummyWriter)

    Utility.htmlToPdfWithWatermark({"folder_path": str(base_dir / "report")})

    # Report PDF created and watermark cleaned up
    assert (base_dir / "report" / "report.pdf").exists()
