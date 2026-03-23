import os
import datetime
import numpy as np

from src.service.utility import Utility
import pandas as pd
import json
import joblib
class DummyModel2:
    def predict(self, X):
        # Predict zeros for any input length
        return np.zeros(len(X), dtype=int)



def test_dateTimeFormat_none_and_value():
    s1 = Utility.dateTimeFormat(None)
    assert isinstance(s1, str)
    assert "UTC" in s1

    now = datetime.datetime(2024, 1, 1, 12, 30, 0)
    s2 = Utility.dateTimeFormat(now)
    assert isinstance(s2, str)
    assert "2024" in s2


def test_combineList_evasion_and_inference():
    payload_base = {
        "attack_data": np.array([[0], [1], [0]]),
        "target_data": np.array([[1], [0], [0]]),
        "prediction_data": np.array([1, 0, 0]),
    }

    evasion_payload = dict(payload_base)
    evasion_payload["type"] = "Evasion"
    e, f = Utility.combineList(evasion_payload)
    assert isinstance(e, list) and isinstance(f, list)
    assert len(e) == 3
    # Ensure final flag appended for each row
    assert all(row[-1] in ("True", "False") for row in e)

    inference_payload = dict(payload_base)
    inference_payload["type"] = "Inference"
    e2, f2 = Utility.combineList(inference_payload)
    assert isinstance(e2, list) and isinstance(f2, list)
    assert len(e2) == 3
    assert all(row[-1] in ("True", "False") for row in e2)


def test_checkList_with_dummy_model():
    class DummyModel:
        def predict(self, arr):
            s = float(np.sum(arr))
            # Return two-class probabilities; argmax used to get label
            if s < 0.5:
                return np.array([[1.0, 0.0]])
            else:
                return np.array([[0.0, 1.0]])

    original = np.array([[0], [0], [0]])
    adversarial = np.array([[1], [0], [1]])
    payload = {
        "model": DummyModel(),
        "original_data": original,
        "adversial_data": adversarial,
    }
    result = Utility.checkList(payload)
    assert isinstance(result, list)
    # At least one differing prediction should be recorded
    assert any(row[-1] == "True" for row in result)


def test_htmlCssContentReport_tabular_and_image():
    tab_css = Utility.htmlCssContentReport({"type": "Tabular"})
    assert isinstance(tab_css, str)
    assert ".report-header" in tab_css

    img_css = Utility.htmlCssContentReport({"type": "Image"})
    assert isinstance(img_css, str)
    assert ".attack-header" in img_css


def test_htmlContentReport_tabular_columns_and_image():
    tab_payload_cols = {
        "type": "Tabular",
        "attackName": "FGSM",
        "graph_html": "<div>graph</div>",
        "attack_status_row": "<tr><td>1</td><td>m</td><td>a</td><td>Done</td><td>0.1</td></tr>",
        "column_graph_data": "<div>columns</div>",
    }
    html_tab_cols = Utility.htmlContentReport(tab_payload_cols)
    assert isinstance(html_tab_cols, str)
    assert "Attack Status" in html_tab_cols
    assert "Attacked Columns" in html_tab_cols

    tab_payload_no_cols = dict(tab_payload_cols)
    tab_payload_no_cols["column_graph_data"] = ""
    html_tab_no_cols = Utility.htmlContentReport(tab_payload_no_cols)
    assert isinstance(html_tab_no_cols, str)
    assert "Attack Status" in html_tab_no_cols

    img_payload_graph = {
        "type": "Image",
        "attackName": "FGSM",
        "graph_html": "<img src='x.png' />",
        "attack_ipop_row": "<tr><td>p</td><td>e</td><td>p</td><td>0.9</td><td>True</td></tr>",
    }
    html_img = Utility.htmlContentReport(img_payload_graph)
    assert isinstance(html_img, str)
    assert "Attack Analysis" in html_img


def test_getcurrentDirectory_and_isContentSafe():
    path = Utility.getcurrentDirectory()
    assert isinstance(path, str)
    assert os.path.isdir(path)

    assert Utility.isContentSafe({"file": "Safe_Name-123"}) is True
    assert Utility.isContentSafe({"file": "Bad@Name"}) is False
    # Non-string values should be unsafe
    assert Utility.isContentSafe({"file": 123}) is False


def test_graphForCombineAttack_tabular(tmp_path):
    folder = tmp_path / "combine"
    folder.mkdir()
    (folder / "report.html").write_text("<html><body>combined</body></html>", encoding="utf-8")

    # Create minimal CSVs for one evasion and one inference attack
    df_evasion = pd.DataFrame({"target": [0, 1, 1], "prediction": [0, 0, 1]})
    df_evasion.to_csv(folder / "FastGradientMethod.csv", index=False)

    df_inference = pd.DataFrame({"target": [0, 0, 1], "prediction": [1, 0, 1]})
    df_inference.to_csv(folder / "AttributeInference.csv", index=False)

    payload = {
        "folder_path": str(folder),
        "attack_list": [{"name": "FastGradientMethod"}, {"name": "AttributeInference"}],
        "model_metaData": {"dataType": "Tabular"},
        "modelName": "m",
        "reportTime": "now",
        "success_skipped": {"Success": 1, "Skipped": 0},
        "rows": "<tr></tr>",
        "confusion_matrix": [[1, 1], [1, 2]],
        "classification_reports": {"accuracy": 0.5, "precision": 0.5, "recall": 0.5, "f1-score": 0.5},
        "mitigation_row": "<tr></tr>",
        "target": "target",
    }

    Utility.graphForCombineAttack(payload)
    # Function should complete; report.html should still exist
    assert os.path.isfile(str(folder / "report.html"))


def test_graphForCombineAttack1_tabular(tmp_path):
    folder = tmp_path / "combine1"
    folder.mkdir()
    (folder / "report.html").write_text("<html><body>combined</body></html>", encoding="utf-8")

    # Create CSVs for two attacks
    df_evasion = pd.DataFrame({"target": [0, 1, 1], "prediction": [0, 0, 1]})
    df_evasion.to_csv(folder / "FastGradientMethod.csv", index=False)

    df_inference = pd.DataFrame({"target": [0, 0, 1], "prediction": [1, 0, 1]})
    df_inference.to_csv(folder / "AttributeInference.csv", index=False)

    payload = {
        "folder_path": str(folder),
        "attack_list": [{"name": "FastGradientMethod"}, {"name": "AttributeInference"}],
        "model_metaData": {"dataType": "Tabular"},
        "modelName": "m",
        "reportTime": "now",
        "success_skipped": {"Success": 1, "Skipped": 0},
        "rows": "<tr></tr>",
        "confusion_matrix": [[1, 1], [1, 2]],
        "classification_reports": {"accuracy": 0.5, "precision": 0.5, "recall": 0.5, "f1-score": 0.5},
        "mitigation_row": "<tr></tr>",
        "target": "target",
    }

    Utility.graphForCombineAttack1(payload)
    assert os.path.isfile(str(folder / "report.html"))


def test_generateImage_writes_file(tmp_path):
    # Create simple base and adversarial samples
    base = np.random.rand(1, 10, 10, 3)
    adv = np.random.rand(1, 10, 10, 3)
    payload = {
        "base_sample": base,
        "adversial_sample": adv,
        "report_path": str(tmp_path),
        "attackName": "TestAttack",
    }

    Utility.generateImage(payload)
    assert os.path.isfile(os.path.join(str(tmp_path), "TestAttack.png"))


def test_confusionMatrix_and_generateDefenceAccuracy(tmp_path):
    # Prepare payload directory structure and metadata file under Utility.getcurrentDirectory
    base_dir = Utility.getcurrentDirectory()
    payload_dir = os.path.join(base_dir, "database", "payload")
    os.makedirs(payload_dir, exist_ok=True)
    with open(os.path.join(payload_dir, "m.txt"), "w") as f:
        json.dump({"groundTruthClassLabel": "gt"}, f)

    # Prepare model folder with a joblib-pickled dummy model
    model_dir = os.path.join(str(tmp_path), "model_folder")
    os.makedirs(model_dir, exist_ok=True)

    joblib.dump(DummyModel2(), os.path.join(model_dir, "model.pkl"))

    # CSV for confusionMatrix under model_dir
    df_cm = pd.DataFrame({
        "gt": [0, 1, 0, 1],
        "a": [0.1, 0.2, 0.3, 0.4],
        "b": [1, 0, 1, 0],
        "x": [5, 6, 7, 8],
        "y": [9, 10, 11, 12],
        "z": [13, 14, 15, 16],
    })
    df_cm.to_csv(os.path.join(model_dir, "FastGradientMethod.csv"), index=False)

    # CSV for generateDefenceAccuracy at a direct path
    df_def = pd.DataFrame({
        "gt": [0, 1, 0],
        "a": [0.1, 0.2, 0.3],
        "b": [1, 0, 1],
        "c": [5, 6, 7],
        "d": [8, 9, 10],
        "flag": [True, False, True],
    })
    csv_def_path = os.path.join(str(tmp_path), "def.csv")
    df_def.to_csv(csv_def_path, index=False)

    # Exercise confusionMatrix
    cm = Utility.confusionMatrix({"modelName": "m", "folder_path": model_dir})
    assert isinstance(cm, list) and len(cm) == 4

    # Exercise generateDefenceAccuracy
    acc = Utility.generateDefenceAccuracy({"modelName": "m", "folder_path": model_dir, "csv_path": csv_def_path})
    assert isinstance(acc, float)
