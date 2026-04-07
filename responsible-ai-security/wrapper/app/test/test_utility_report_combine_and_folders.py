import io
import os
import zipfile
import shutil
import datetime
import pandas as pd
import numpy as np

import pytest

from src.service.utility import Utility


def make_zip_bytes(files):
    """
    Create an in-memory zip containing given files.
    files: list of tuples (filename, bytes_content)
    Returns bytes of the zip.
    """
    temp = io.BytesIO()
    with zipfile.ZipFile(temp, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for fname, content in files:
            zf.writestr(fname, content)
    return temp.getvalue()


def test_updateReportsList_and_sortReportsList():
    # Prepare synthetic report list
    now = datetime.datetime.now()
    reports = [
        {"ReportName": "FastGradientMethod.zip", "CreatedDateTime": now - datetime.timedelta(minutes=3)},
        {"ReportName": "AttributeInference.zip", "CreatedDateTime": now - datetime.timedelta(minutes=1)},
        # Should be ignored because equals modelName.zip
        {"ReportName": "mymodel.zip", "CreatedDateTime": now},
    ]

    payload = {
        "reportList": reports,
        "modelName": "mymodel",
        "attackList": ["FastGradientMethod", "AttributeInference"],
    }

    filtered = Utility.updateReportsList(payload)
    # Expect only relevant attacks, order by attackList
    assert [r["ReportName"] for r in filtered] == [
        "FastGradientMethod.zip",
        "AttributeInference.zip",
    ]

    # sortReportsList sorts by CreatedDateTime descending
    sorted_list = Utility.sortReportsList(filtered)
    assert sorted_list[0]["ReportName"] == "AttributeInference.zip"


def test_combineReportFile_mongo_path(monkeypatch, tmp_path):
    # Ensure database folder structure
    db_root = os.path.join(Utility.getcurrentDirectory(), "database")
    os.makedirs(db_root, exist_ok=True)
    for d in ["data", "model", "payload", "report"]:
        os.makedirs(os.path.join(db_root, d), exist_ok=True)

    report_path = os.path.join(db_root, "report", "suite_run")
    os.makedirs(report_path, exist_ok=True)

    # Craft two zipped reports: each contains html (with <style> tag to be stripped), csv and image
    zip1_bytes = make_zip_bytes([
        ("FastGradientMethod.html", "<html><style>.x{}</style><body>FGM</body></html>"),
        ("FastGradientMethod.csv", "a,b\n1,2\n"),
        ("fgm.jpg", b"\xff\xd8\xfftestjpg"),
    ])
    zip2_bytes = make_zip_bytes([
        ("AttributeInference.html", "<html><style>.y{}</style><body>AI</body></html>"),
        ("AttributeInference.csv", "c,d\n3,4\n"),
        ("ai.png", b"\x89PNG\r\n\x1a\n"),
    ])

    # Stub SecReport.findall to return two reports
    class DummySecReport:
        @staticmethod
        def findall(q):
            return [
                {"BatchId": q.get("BatchId"), "SecReportId": "FastGradientMethod_001", "ReportName": "FastGradientMethod.zip", "CreatedDateTime": datetime.datetime.now() - datetime.timedelta(minutes=2)},
                {"BatchId": q.get("BatchId"), "SecReportId": "AttributeInference_002", "ReportName": "AttributeInference.zip", "CreatedDateTime": datetime.datetime.now() - datetime.timedelta(minutes=1)},
            ]

    monkeypatch.setenv("DB_TYPE", "mongo")

    class DummyFileStoreDb:
        @staticmethod
        def findOne(key):
            if key.startswith("FastGradientMethod"):
                return {"data": zip1_bytes, "fileName": "FastGradientMethod.zip"}
            return {"data": zip2_bytes, "fileName": "AttributeInference.zip"}

    # Patch DAO classes used inside Utility.combineReportFile
    # Patch directly in utility module where symbols are used
    import src.service.utility as utility_module
    monkeypatch.setattr(utility_module, "SecReport", DummySecReport)
    monkeypatch.setattr(utility_module, "FileStoreDb", DummyFileStoreDb)

    count = Utility.combineReportFile({
        "batchid": "B123",
        "modelName": "mymodel",
        "attackList": ["FastGradientMethod", "AttributeInference"],
        "report_path": report_path,
    })

    # Assert expected outputs in report_path
    assert count == 2
    report_html = os.path.join(report_path, "report.html")
    assert os.path.exists(report_html)
    content = open(report_html, "r", encoding="utf-8").read()
    # Style tags should be stripped
    assert "<style>" not in content
    assert "FGM" in content and "AI" in content

    # CSV files extracted per attack
    assert os.path.exists(os.path.join(report_path, "FastGradientMethod.csv"))
    assert os.path.exists(os.path.join(report_path, "AttributeInference.csv"))
    # Images extracted as-is
    assert os.path.exists(os.path.join(report_path, "fgm.jpg"))
    assert os.path.exists(os.path.join(report_path, "ai.png"))


def test_createAttackFolder_moves_files(monkeypatch, tmp_path):
    # Prepare report_path with csv and image files
    report_path = tmp_path / "report_files"
    report_path.mkdir(parents=True)

    # CSVs for evasion and inference
    (report_path / "FastGradientMethod.csv").write_text("x,y\n1,2\n")
    (report_path / "AttributeInference.csv").write_text("x,y\n3,4\n")
    # Images: naming pattern "name^AttackType.ext"
    (report_path / "img1^FastGradientMethod.jpg").write_bytes(b"\xff\xd8\xffjpg")
    (report_path / "img2^AttributeInference.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (report_path / "img3^Augly.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    payload = {"report_path": str(report_path), "attack_list": [
        {"attack": "FastGradientMethod", "type": "Evasion"},
        {"attack": "AttributeInference", "type": "Inference"},
        {"attack": "Augly", "type": "Augmentation"},
    ]}

    # Allow filenames with '^' by bypassing strict sanitizer for this test
    monkeypatch.setattr(Utility, "sanitize_filenameorfoldername", lambda x: x)
    Utility.createAttackFolder(payload)

    # Verify folder structure and moved files
    evasion_dir = report_path / "Art" / "Evasion" / "FastGradientMethod"
    inference_dir = report_path / "Art" / "Inference" / "AttributeInference"
    augly_dir = report_path / "Augly" / "Augmentation" / "Augly"

    assert (evasion_dir / "FastGradientMethod.csv").exists()
    assert (evasion_dir / "img1.jpg").exists()

    assert (inference_dir / "AttributeInference.csv").exists()
    assert (inference_dir / "img2.png").exists()

    assert (augly_dir / "img3.png").exists()

    # Source files should be deleted
    assert not (report_path / "FastGradientMethod.csv").exists()
    assert not (report_path / "AttributeInference.csv").exists()
    assert not (report_path / "img1^FastGradientMethod.jpg").exists()
    assert not (report_path / "img2^AttributeInference.png").exists()
    assert not (report_path / "img3^Augly.png").exists()


def test_sanitize_filenameorfoldername_valid_and_invalid():
    # Valid name
    assert Utility.sanitize_filenameorfoldername("Attack-01_File.csv") == "Attack-01_File.csv"
    # Invalid returns None (exception swallowed internally)
    assert Utility.sanitize_filenameorfoldername("invalid<>name.csv") is None
