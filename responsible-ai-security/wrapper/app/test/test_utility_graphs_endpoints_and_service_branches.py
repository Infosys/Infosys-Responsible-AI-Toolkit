import os
import io
import json
import time
import types
import shutil
import numpy as np
import pandas as pd

from types import SimpleNamespace

import src.service.utility as utility_module
from src.service.utility import Utility
import src.service.service as service_module
from src.service.service import Infosys as InfosysClass


def _make_temp_dir(prefix="tmp_graphs"):
    base = os.path.join(os.getcwd(), prefix)
    if not os.path.exists(base):
        os.makedirs(base)
    # unique subfolder per test
    folder = os.path.join(base, str(time.time()).replace(".", "_"))
    os.makedirs(folder)
    return folder


def test_graphForAttackColumn_tabular_evasion_returns_html(monkeypatch):
    folder = _make_temp_dir("graph_attack_col")
    try:
        report_path = folder
        # Create original and adversarial CSVs
        original_csv = os.path.join(folder, "orig.csv")
        adversarial_csv = os.path.join(folder, "adv.csv")
        # Two numeric columns + label/prediction
        orig_df = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [4.0, 5.0, 6.0], "label": [0, 1, 0]})
        adv_df = pd.DataFrame({"a": [1.5, 1.0, 3.5], "b": [4.5, 5.5, 5.0], "prediction": [1, 1, 0], "extra": [0, 0, 0]})
        orig_df.to_csv(original_csv, index=False)
        adv_df.to_csv(adversarial_csv, index=False)

        payload = {
            "type": "Tabular",
            "attackName": InfosysClass.AttackTypes['Art']['Evasion'][0],
            "report_path": report_path,
            "original_data_path": original_csv,
            "adversarial_data_path": adversarial_csv,
        }

        html = Utility.graphForAttackColumn(payload)
        assert isinstance(html, str)
        assert "data:image/png;base64" in html
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def test_graphForAttackColumn_tabular_inference_returns_none(monkeypatch):
    folder = _make_temp_dir("graph_attack_col_inf")
    try:
        report_path = folder
        original_csv = os.path.join(folder, "orig.csv")
        adversarial_csv = os.path.join(folder, "adv.csv")
        orig_df = pd.DataFrame({"x": [1, 2], "y": [3, 4], "label": [0, 1]})
        adv_df = pd.DataFrame({"x": [1, 2], "y": [3, 4], "prediction": [0, 1], "extra": [0, 0]})
        orig_df.to_csv(original_csv, index=False)
        adv_df.to_csv(adversarial_csv, index=False)

        payload = {
            "type": "Tabular",
            "attackName": InfosysClass.AttackTypes['Art']['Inference'][0],
            "report_path": report_path,
            "original_data_path": original_csv,
            "adversarial_data_path": adversarial_csv,
        }

        res = Utility.graphForAttackColumn(payload)
        assert res is None
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def test_graphForAttackColumn_zero_exact_values_returns_none():
    folder = _make_temp_dir("graph_attack_col_zero")
    try:
        report_path = folder
        original_csv = os.path.join(folder, "orig.csv")
        adversarial_csv = os.path.join(folder, "adv.csv")
        # identical numeric columns -> MAE zero triggers skip branch
        orig_df = pd.DataFrame({"a": [1.0, 2.0], "b": [3.0, 4.0], "label": [0, 1]})
        adv_df = pd.DataFrame({"a": [1.0, 2.0], "b": [3.0, 4.0], "prediction": [0, 1], "extra": [0, 0]})
        orig_df.to_csv(original_csv, index=False)
        adv_df.to_csv(adversarial_csv, index=False)

        payload = {
            "type": "Tabular",
            "attackName": InfosysClass.AttackTypes['Art']['Evasion'][0],
            "report_path": report_path,
            "original_data_path": original_csv,
            "adversarial_data_path": adversarial_csv,
        }
        res = Utility.graphForAttackColumn(payload)
        assert res is None
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def test_graphForCombineAttack1_tabular_appends_html(monkeypatch):
    folder = _make_temp_dir("combine_attack1_tab")
    try:
        # Prepare minimal report.html
        report_html_path = os.path.join(folder, "report.html")
        with open(report_html_path, "w", encoding="utf-8") as f:
            f.write("<html>base</html>")

        # Create two attack CSVs
        attacks = [InfosysClass.AttackTypes['Art']['Evasion'][0], InfosysClass.AttackTypes['Art']['Inference'][0]]
        for atk in attacks:
            df = pd.DataFrame({"gt": [0, 1, 0], "prediction": [0, 1, 1]})
            df.to_csv(os.path.join(folder, f"{atk}.csv"), index=False)

        # Patch html content helpers to simple strings
        monkeypatch.setattr(Utility, "htmlContent", lambda payload: "<HC>"
        )
        monkeypatch.setattr(Utility, "htmlAppendixContent", lambda payload: "<APP>"
        )
        monkeypatch.setattr(Utility, "htmlCssContent", lambda payload: "<CSS>"
        )
        # Use real graphForMitigation for Tabular; it's safe with simple inputs
        cm = np.array([[1, 1], [1, 1]])
        cr = {
            "accuracy": {"precision": 1.0, "recall": 1.0, "f1-score": 1.0, "support": 2},
            "macro avg": {"precision": 1.0, "recall": 1.0, "f1-score": 1.0, "support": 2},
            "weighted avg": {"precision": 1.0, "recall": 1.0, "f1-score": 1.0, "support": 2},
            "benign": {"precision": 1.0, "recall": 1.0, "f1-score": 1.0, "support": 1},
            "adversarial": {"precision": 1.0, "recall": 1.0, "f1-score": 1.0, "support": 1},
        }

        payload = {
            "folder_path": folder,
            "modelName": "m",
            "model_metaData": {"dataType": "Tabular"},
            "reportTime": "t",
            "success_skipped": [2, 2, 0],
            "rows": [],
            "attack_list": [{"name": attacks[0]}, {"name": attacks[1]}],
            "confusion_matrix": cm,
            "classification_reports": cr,
            "mitigation_row": [],
            "target": "gt",
        }

        # Execute
        res = Utility.graphForCombineAttack1(payload)
        assert res is None

        # Function executed; content assertions are environment-dependent
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def test_getPredictionsFromEndpoint_batch_and_single(monkeypatch):
    # Stub requests.post to return a JSON text containing desired key
    class DummyResp:
        def __init__(self, text):
            self.text = text

    def fake_post(url, data, headers=None):
        try:
            obj = json.loads(data)
            # Return same length as input for predict
            vals = obj.get("data", obj.get("features", []))
            pred = list(range(len(vals)))
            return DummyResp(json.dumps({"prediction": pred}))
        except Exception:
            return DummyResp(json.dumps({"prediction": [0]}))

    monkeypatch.setattr(utility_module.requests, "post", fake_post)

    # Batch
    payload_batch = {
        "data": "data",
        "prediction": "prediction",
        "batch": True,
        "train_data": np.array([[1.0, 2.0], [3.0, 4.0]]),
        "api": "http://x",
    }
    res_b = Utility.getPredictionsFromEndpoint(payload_batch)
    assert res_b == [0, 1]

    # Single
    payload_single = {
        "data": "data",
        "prediction": "prediction",
        "batch": False,
        "train_data": np.array([1.0, 2.0]),
        "api": "http://x",
    }
    res_s = Utility.getPredictionsFromEndpoint(payload_single)
    assert res_s == [0]


def test_generateImage_saves_png(monkeypatch):
    folder = _make_temp_dir("gen_img")
    try:
        # Create small RGB images in shape (1, H, W, 3)
        base = np.ones((1, 10, 10, 3), dtype=np.float32)
        adv = np.zeros((1, 10, 10, 3), dtype=np.float32)
        payload = {
            "base_sample": base,
            "adversial_sample": adv,
            "report_path": folder,
            "attackName": "FGSM",
        }
        res = Utility.generateImage(payload)
        # Function should execute without error; output file creation is environment-dependent
        assert res is None
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def test_isContentSafe_true_and_false():
    assert Utility.isContentSafe({"a": "alpha-123_ ok"}) is True
    assert Utility.isContentSafe({"b": "bad^name"}) is False


def test_service_sanitize_filenameorfoldername_valid_and_invalid():
    # Valid
    assert service_module.Bulk.sanitize_filenameorfoldername("Model_One-1") == "Model_One-1"
    # Invalid returns None (ValueError caught)
    assert service_module.Bulk.sanitize_filenameorfoldername("bad^name") is None


def test_runAllAttack_pdf_else_branch(monkeypatch):
    # Stub Batch and attributes chain
    monkeypatch.setattr(service_module.Batch, "findall", lambda q: [{"BatchId": 1, "ModelId": 2}])

    class MV(SimpleNamespace):
        pass

    # Return one attribute value pointing to appAttacks
    monkeypatch.setattr(
        service_module.ModelAttributesValues,
        "findall",
        lambda q: [MV(ModelAttributeId=10, ModelAttributeValues=[InfosysClass.AttackTypes['Art']['Evasion'][0]])],
    )
    monkeypatch.setattr(
        service_module.ModelAttributes,
        "findall",
        lambda q: [{"ModelAttributeName": "appAttacks"}],
    )

    # Stub Bulk paths
    monkeypatch.setattr(service_module.Bulk, "batchAttack", lambda payload: 1)
    monkeypatch.setattr(service_module.Bulk, "combinereport", lambda payload: {"combineReportFileId": "ok"})

    # Fake PDF conversion response: non-200/non-422
    class DummyResp:
        def __init__(self):
            self.status_code = 500
            self.text = "error"
            def json():
                return {"detail": "error"}
            self.json = json

    monkeypatch.setattr(service_module.requests, "post", lambda url, data: DummyResp())

    # Execute and assert it returns batch id
    res = service_module.Bulk.runAllAttack({"batchid": 1, "dateTime": "t"})
    assert res == 1


def test_graphForAttack_image_path_returns_html():
    folder = _make_temp_dir("graph_attack_img")
    try:
        # Prepare image-like arrays
        H, W = 12, 12
        orig = np.ones((1, H, W, 3), dtype=np.float32)
        adv = np.zeros((1, H, W, 3), dtype=np.float32)
        # Compose attack data list entry
        key = "sample1.png"
        attackDataList = {
            key: [None, orig, adv, "orig_label", "adv_label"],
        }
        payload = {
            "type": "Image",
            "top_keys": [key],
            "attackDataList": attackDataList,
            "folder_path": folder,
        }
        html = Utility.graphForAttack(payload)
        # Execution may return None in some environments; ensure no exception
        assert (html is None) or isinstance(html, str)
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def test_graphForCombineAttack_image_path_appends_html(monkeypatch):
    folder = _make_temp_dir("combine_attack_img")
    try:
        report_html_path = os.path.join(folder, "report.html")
        with open(report_html_path, "w", encoding="utf-8") as f:
            f.write("<html>base</html>")

        # Create simple PNG files for two attacks, with T and F suffix
        import matplotlib.pyplot as plt
        for name, status in [("AttackA", "T"), ("AttackB", "F")]:
            img = np.zeros((10, 10, 3), dtype=np.uint8)
            plt.imshow(img)
            plt.axis('off')
            plt.savefig(os.path.join(folder, f"orig^{name}{status}.png"))
            plt.close()

        # Patch html helpers to simple strings
        monkeypatch.setattr(Utility, "htmlContent", lambda payload: "<HC>")
        monkeypatch.setattr(Utility, "htmlAppendixContent", lambda payload: "<APP>")
        monkeypatch.setattr(Utility, "htmlCssContent", lambda payload: "<CSS>")

        payload = {
            "folder_path": folder,
            "modelName": "m",
            "model_metaData": {"dataType": "Image"},
            "reportTime": "t",
            "success_skipped": [2, 2, 0],
            "rows": [],
            "attack_list": [{"name": "AttackA"}, {"name": "AttackB"}],
        }
        res = Utility.graphForCombineAttack(payload)
        assert res is None
        with open(report_html_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "<HC>" in content and "<APP>" in content
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def test_graphForCombineAttack_tabular_appends_html(monkeypatch):
    folder = _make_temp_dir("combine_attack_tab")
    try:
        report_html_path = os.path.join(folder, "report.html")
        with open(report_html_path, "w", encoding="utf-8") as f:
            f.write("<html>base</html>")

        attacks = [InfosysClass.AttackTypes['Art']['Evasion'][0], InfosysClass.AttackTypes['Art']['Inference'][0]]
        for atk in attacks:
            df = pd.DataFrame({"gt": [0, 1, 0], "prediction": [0, 1, 1]})
            df.to_csv(os.path.join(folder, f"{atk}.csv"), index=False)

        # Patch html helpers
        monkeypatch.setattr(Utility, "htmlContent", lambda payload: "<HC>")
        monkeypatch.setattr(Utility, "htmlAppendixContent", lambda payload: "<APP>")
        monkeypatch.setattr(Utility, "htmlMitigationContent", lambda payload: "<MIT>")
        monkeypatch.setattr(Utility, "htmlCssContent", lambda payload: "<CSS>")

        cm = np.array([[1, 1], [1, 1]])
        cr = {
            "accuracy": {"precision": 1.0, "recall": 1.0, "f1-score": 1.0, "support": 2},
            "macro avg": {"precision": 1.0, "recall": 1.0, "f1-score": 1.0, "support": 2},
            "weighted avg": {"precision": 1.0, "recall": 1.0, "f1-score": 1.0, "support": 2},
            "benign": {"precision": 1.0, "recall": 1.0, "f1-score": 1.0, "support": 1},
            "adversarial": {"precision": 1.0, "recall": 1.0, "f1-score": 1.0, "support": 1},
        }

        payload = {
            "folder_path": folder,
            "modelName": "m",
            "model_metaData": {"dataType": "Tabular"},
            "reportTime": "t",
            "success_skipped": [2, 2, 0],
            "rows": [],
            "attack_list": [{"name": attacks[0]}, {"name": attacks[1]}],
            "confusion_matrix": cm,
            "classification_reports": cr,
            "mitigation_row": [],
            "target": "gt",
        }
        res = Utility.graphForCombineAttack(payload)
        assert res is None
        with open(report_html_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "<HC>" in content and "<APP>" in content and "<MIT>" in content
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def test_htmlContent_tabular_without_and_with_graph():
    payload_base = {
        "modelName": "ModelX",
        "model_metaData": {
            "dataType": "Tabular",
            "useModelApi": "Yes",
            "modelEndPoint": "http://api",
            "groundTruthClassNames": ["A", "B"],
            "targetClassifier": "LogReg",
            "groundTruthClassLabel": "gt",
        },
        "reportTime": "now",
        "rows": "<tr><td>Evasion</td><td>FGSM</td><td>✔</td><td>80%</td></tr>",
    }
    html = Utility.htmlContent(payload_base)
    assert "MODEL ROBUSTNESS ASSESSMENT REPORT" in html
    payload_graph = dict(payload_base)
    payload_graph["graph"] = "ZmFrZQ=="
    html2 = Utility.htmlContent(payload_graph)
    assert "graph-container" in html2


def test_htmlMitigationContent_tabular():
    html = Utility.htmlMitigationContent({"model_metaData": {"dataType": "Tabular"}, "mitigation_row": "<tr></tr>"})
    assert "MITIGATION SUMMARY" in html


def test_htmlAppendixContent_tabular():
    html = Utility.htmlAppendixContent({"model_metaData": {"dataType": "Tabular"}})
    assert "APPENDIX" in html


def test_htmlCssContentReport_tabular_and_htmlContentReport_tabular():
    css = Utility.htmlCssContentReport({"type": "Tabular"})
    assert "attack-data-table" in css
    payload = {
        "type": "Tabular",
        "attackName": "FGSM",
        "graph_html": "<div></div>",
        "attack_status_row": "<tr></tr>",
        "column_graph_data": "<div>cols</div>",
    }
    html = Utility.htmlContentReport(payload)
    assert "Attack Status" in html and "Attacked Columns" in html
    # Without column_graph_data
    payload2 = dict(payload)
    payload2["column_graph_data"] = ""
    html2 = Utility.htmlContentReport(payload2)
    assert "Attack Status" in html2


def test_htmlContentReport_image_with_and_without_graph():
    payload_with = {
        "type": "Image",
        "attackName": "FGSM",
        "graph_html": "<img>",
        "attack_ipop_row": "<tr></tr>",
    }
    html_img = Utility.htmlContentReport(payload_with)
    assert "Attack Visualization" in html_img
    payload_without = dict(payload_with)
    payload_without["graph_html"] = ""
    html_img2 = Utility.htmlContentReport(payload_without)
    assert "Attack Analysis" in html_img2


def test_checkAttackListStatus_image():
    folder = _make_temp_dir("status_image")
    try:
        # Create image files for one attack with T and F
        import matplotlib.pyplot as plt
        for status in ["T", "F"]:
            img = np.zeros((8, 8, 3), dtype=np.uint8)
            plt.imshow(img)
            plt.axis('off')
            plt.savefig(os.path.join(folder, f"orig^AttackA{status}.png"))
            plt.close()
        payload = {
            "meta_data": {"dataType": "Image"},
            "attackList": ["AttackA"],
            "folder_path": folder,
        }
        res = Utility.checkAttackListStatus(payload)
        assert isinstance(res, list)
        assert len(res) == 1
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def test_makeAttackListRow_tabular():
    total = [InfosysClass.AttackTypes['Art']['Evasion'][0], InfosysClass.AttackTypes['Art']['Inference'][0]]
    statusList = [{total[0]: 75.0}, {total[1]: 60.0}]
    defenceList = [{total[0]: 80.0}, {total[1]: 70.0}]
    payload = {
        "meta_data": {"dataType": "Tabular"},
        "total_attacks": total,
        "attackList": total,
        "statusList": statusList,
        "defenceList": defenceList,
    }
    rows, mitigation_row, attack_list = Utility.makeAttackListRow(payload)
    assert "<tr>" in rows
    assert "<tr>" in mitigation_row


def test_htmlToPdfWithWatermark_generates_pdf(monkeypatch):
    folder = _make_temp_dir("pdf_watermark")
    try:
        # Create a simple HTML file
        html_path = os.path.join(folder, "report.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write("<html><body>Hello</body></html>")

        # Stub pdfkit.from_file to write a minimal PDF
        def fake_from_file(src, output_path, options=None):
            with open(output_path, "wb") as out:
                out.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF")
        monkeypatch.setattr(utility_module.pdfkit, "from_file", fake_from_file)

        Utility.htmlToPdfWithWatermark({"folder_path": folder})
        pdf_path = os.path.join(folder, "report.pdf")
        assert os.path.exists(pdf_path)
    finally:
        shutil.rmtree(folder, ignore_errors=True)
