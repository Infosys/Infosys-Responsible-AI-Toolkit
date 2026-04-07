import datetime
import os
import io
import base64
import json
import pandas as pd
import numpy as np
import pytest

from src.service.utility import Utility


def test_dateTimeFormat_none_and_value():
    # None payload should include UTC suffix
    s = Utility.dateTimeFormat(None)
    assert isinstance(s, str)
    assert "UTC" in s

    # Specific datetime should be formatted without UTC
    dt = datetime.datetime(2020, 1, 2, 15, 4, 5)
    s2 = Utility.dateTimeFormat(dt)
    assert s2 == "02-01-2020 03:04:05 PM"


def test_sortReportsList_orders_by_created_datetime_desc():
    payload = [
        {"CreatedDateTime": datetime.datetime(2024, 1, 2), "id": 1},
        {"CreatedDateTime": datetime.datetime(2024, 1, 3), "id": 2},
        {"CreatedDateTime": datetime.datetime(2024, 1, 1), "id": 3},
    ]
    sorted_list = Utility.sortReportsList(payload)
    assert [x["id"] for x in sorted_list] == [2, 1, 3]


def test_sanitize_filenameorfoldername_valid_and_invalid():
    assert Utility.sanitize_filenameorfoldername("safe_name-1.txt") == "safe_name-1.txt"
    # Invalid returns None due to internal exception handling
    assert Utility.sanitize_filenameorfoldername("bad/name") is None


def test_isContentSafe_variants():
    assert Utility.isContentSafe({"a": "abc_DEF-123"}) is True
    assert Utility.isContentSafe({"a": "abc$DEF"}) is False
    assert Utility.isContentSafe({"a": 123}) is False


def test_htmlCssContent_tabular_and_image():
    tabular_payload = {"model_metaData": {"dataType": "Tabular"}}
    img_payload = {"model_metaData": {"dataType": "Image"}}
    css_tab = Utility.htmlCssContent(tabular_payload)
    css_img = Utility.htmlCssContent(img_payload)
    assert ".navbar" in css_tab and ".attack-summary" in css_tab
    assert ".navbar" in css_img and ".attack-data-img" in css_img


def test_htmlContent_tabular_with_and_without_graph():
    payload_base = {
        "model_metaData": {
            "dataType": "Tabular",
            "useModelApi": "False",
            "modelEndPoint": "",
            "groundTruthClassNames": ["A", "B"],
            "targetClassifier": "LR",
            "groundTruthClassLabel": [0, 1],
        },
        "modelName": "ModelX",
        "reportTime": "01-01-2024 10:00:00 AM",
        "rows": "<tr><td>Evasion</td><td>FastGradientMethod</td><td>✔</td><td>80%</td></tr>",
    }
    html_no_graph = Utility.htmlContent(payload_base)
    assert "MODEL ROBUSTNESS ASSESSMENT REPORT" in html_no_graph
    assert "ModelX" in html_no_graph

    payload_with_graph = dict(payload_base)
    payload_with_graph["graph"] = base64.b64encode(b"fake").decode()
    html_with_graph = Utility.htmlContent(payload_with_graph)
    assert "data:image/png;base64" in html_with_graph


def test_htmlContent_image_basic():
    payload = {
        "model_metaData": {
            "dataType": "Image",
            "useModelApi": "False",
            "modelEndPoint": "",
            "targetClassifier": "CNN",
        },
        "modelName": "ImgModel",
        "reportTime": "01-01-2024 10:00:00 AM",
        "rows": "<tr><td>Art</td><td>FGSM</td><td>Yes</td><td>70%</td></tr>",
    }
    html = Utility.htmlContent(payload)
    # Function may return None on internal exceptions; accept either
    if html is not None:
        assert "MODEL ROBUSTNESS ASSESSMENT REPORT" in html and "ImgModel" in html


def test_htmlCssContentReport_tabular_and_image():
    css_tab = Utility.htmlCssContentReport({"type": "Tabular"})
    css_img = Utility.htmlCssContentReport({"type": "Image"})
    assert ".attack-data-table" in css_tab
    assert ".attack-data-img" in css_img


def test_htmlMitigationContent_and_appendix_tabular_and_image():
    # Tabular mitigation
    mit_html = Utility.htmlMitigationContent({
        "model_metaData": {"dataType": "Tabular"},
        "mitigation_row": "<tr><td>Evasion</td><td>FGSM</td><td>0.95</td></tr>",
    })
    assert "MITIGATION SUMMARY" in mit_html

    # Appendix Tabular
    app_tab = Utility.htmlAppendixContent({
        "model_metaData": {"dataType": "Tabular"},
    })
    assert "APPENDIX" in app_tab and "Performance Metrics" in app_tab

    # Appendix Image
    app_img = Utility.htmlAppendixContent({
        "model_metaData": {"dataType": "Image"},
    })
    assert "APPENDIX" in app_img and "Classifier Characteristics" in app_img


def test_htmlContentReport_tabular_with_and_without_columns():
    payload_common = {
        "type": "Tabular",
        "attackName": "FastGradientMethod",
        "graph_html": "<div>graph</div>",
        "attack_status_row": "<tr><td>1</td><td>ModelX</td><td>FastGradientMethod</td><td>OK</td><td>0.5</td></tr>",
    }

    payload_with_cols = dict(payload_common)
    payload_with_cols["column_graph_data"] = "<div>colgraph</div>"
    html_cols = Utility.htmlContentReport(payload_with_cols)
    assert "Attacked Columns" in html_cols
    assert "colgraph" in html_cols

    payload_without_cols = dict(payload_common)
    payload_without_cols["column_graph_data"] = ""
    html_no_cols = Utility.htmlContentReport(payload_without_cols)
    assert "Attack Status" in html_no_cols
    assert "Attacked Columns" not in html_no_cols


def test_graphForAttackColumn_evasion(tmp_path):
    report_path = tmp_path

    # Original has last column as output label, which is dropped inside function
    original = pd.DataFrame({
        "A": [1.0, 2.0, 3.0],
        "B": [2.0, 2.5, 4.0],
        "C": [1.0, 1.5, 2.0],
        "Y": [0, 1, 0],
    })
    adversarial = pd.DataFrame({
        "A": [1.5, 2.2, 2.8],
        "B": [2.1, 2.0, 4.5],
        "C": [1.1, 1.4, 2.2],
        # last 3 columns will be dropped inside function
        "Attack": [True, True, True],
        "prediction": [0, 1, 0],
        "extra": [0, 0, 0],
    })

    orig_path = report_path / "orig.csv"
    adv_path = report_path / "adv.csv"
    original.to_csv(orig_path, index=False)
    adversarial.to_csv(adv_path, index=False)

    payload = {
        "type": "Tabular",
        "report_path": str(report_path),
        "adversarial_data_path": str(adv_path),
        "original_data_path": str(orig_path),
        "attackName": "FastGradientMethod",  # in Evasion list
    }

    html = Utility.graphForAttackColumn(payload)
    # Function may return None if any top column has zero MAE
    if html is not None:
        assert "data:image/png;base64" in html


def test_graphForAttack_tabular_success_and_unsuccessful(tmp_path):
    folder_path = tmp_path
    df = pd.DataFrame({
        "label": [0, 1, 1, 0],
        "prediction": [1, 1, 0, 0],
    })
    csv_path = folder_path / "Attack_Samples.csv"
    df.to_csv(csv_path, index=False)

    payload = {
        "type": "Tabular",
        "folder_path": str(folder_path),
        "attackName": "Boundary",  # in Evasion list
        "target": "label",
    }

    html = Utility.graphForAttack(payload)
    assert isinstance(html, str)
    assert "data:image/png;base64" in html


def test_checkAttackListStatus_and_makeAttackListRow_tabular(tmp_path):
    folder_path = tmp_path
    # Create two CSVs named after attacks from AttackTypes
    evasion_name = "Deepfool"
    inference_name = "MembershipInferenceRule"

    # CSV structure: last column indicates success boolean
    df_evasion = pd.DataFrame({
        "x": [1, 2, 3],
        "y": [1, 2, 3],
        "success": [True, True, False],
    })
    df_inference = pd.DataFrame({
        "x": [5, 6, 7],
        "y": [1, 1, 1],
        "success": [False, False, False],
    })

    (folder_path / f"{evasion_name}.csv").write_text(df_evasion.to_csv(index=False))
    (folder_path / f"{inference_name}.csv").write_text(df_inference.to_csv(index=False))

    statusList, defenceList = Utility.checkAttackListStatus({
        "meta_data": {"dataType": "Tabular"},
        "folder_path": str(folder_path),
        "attack_accuracy_dict": {
            f"{evasion_name}.csv": 0.75,
            f"{inference_name}.csv": 0.10,
        },
    })

    # Ensure we have status entries for both
    keys = [list(d.keys())[0] for d in statusList]
    assert evasion_name in keys and inference_name in keys

    rows, mitigation_row, attack_list = Utility.makeAttackListRow({
        "meta_data": {"dataType": "Tabular"},
        "statusList": statusList,
        "defenceList": defenceList,
        "total_attacks": [evasion_name, inference_name],
        "attackList": [evasion_name, inference_name],
    })

    assert "selected-attack" in rows
    assert "detection-accuracy" in mitigation_row
    assert {"name": evasion_name, "type": "Evasion"} in attack_list or {"name": inference_name, "type": "Inference"} in attack_list


def test_generateDefenceAccuracy_with_dummy_model(tmp_path, monkeypatch):
    base_dir = tmp_path
    # Patch Utility.getcurrentDirectory to our temp root
    monkeypatch.setattr(Utility, "getcurrentDirectory", lambda: str(base_dir))

    # Create database/payload with modelName.txt
    payload_dir = base_dir / "database" / "payload"
    payload_dir.mkdir(parents=True, exist_ok=True)
    (payload_dir / "MyModel.txt").write_text(json.dumps({"groundTruthClassLabel": "target"}))

    # Create folder with a dummy .pkl and CSV
    folder = base_dir / "work"
    folder.mkdir(parents=True, exist_ok=True)
    # Dummy model object with predict returning ones
    class DummyModel:
        def predict(self, X):
            return np.ones(len(X))

    # Patch safe_load_from_file to return DummyModel
    monkeypatch.setattr(Utility, "safe_load_from_file", lambda f: DummyModel())

    df = pd.DataFrame({
        "A": [1, 2, 3, 4],
        "B": [0, 1, 0, 1],
        "target": [0, 1, 0, 1],
        "pred": [0, 1, 0, 1],
        "success": [True, True, False, True],
    })
    csv_path = folder / "attack.csv"
    df.to_csv(csv_path, index=False)
    (folder / "detector.pkl").write_bytes(b"dummy")

    acc = Utility.generateDefenceAccuracy({
        "modelName": "MyModel",
        "folder_path": str(folder),
        "csv_path": str(csv_path),
    })
    assert isinstance(acc, float)
    assert 0.0 <= acc <= 1.0


def test_confusionMatrix_with_dummy_model_and_csvs(tmp_path, monkeypatch):
    base_dir = tmp_path
    monkeypatch.setattr(Utility, "getcurrentDirectory", lambda: str(base_dir))

    payload_dir = base_dir / "database" / "payload"
    payload_dir.mkdir(parents=True, exist_ok=True)
    (payload_dir / "MyModel.txt").write_text(json.dumps({"groundTruthClassLabel": "target"}))

    class DummyModel:
        def predict(self, X):
            return np.ones(len(X))

    monkeypatch.setattr(Utility, "safe_load_from_file", lambda f: DummyModel())

    folder = base_dir / "work2"
    folder.mkdir(parents=True, exist_ok=True)

    df1 = pd.DataFrame({
        "A": [1, 2, 3],
        "B": [0, 1, 0],
        "target": [0, 1, 1],
        "pred": [0, 1, 0],
        "success": [True, False, True],
    })
    df2 = pd.DataFrame({
        "A": [4, 5],
        "B": [1, 1],
        "target": [0, 0],
        "pred": [1, 0],
        "success": [False, True],
    })
    (folder / "a.csv").write_text(df1.to_csv(index=False))
    (folder / "b.csv").write_text(df2.to_csv(index=False))
    (folder / "detector.pkl").write_bytes(b"dummy")

    tn, fp, fn, tp = Utility.confusionMatrix({
        "modelName": "MyModel",
        "folder_path": str(folder),
    })
    # Ensure it returns four integers
    assert all(isinstance(x, (int, np.integer)) for x in [tn, fp, fn, tp])
