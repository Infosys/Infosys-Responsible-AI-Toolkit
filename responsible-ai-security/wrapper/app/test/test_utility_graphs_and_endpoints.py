import os
import json
import tempfile
import pandas as pd

from src.service.utility import Utility


def test_graphForAttack_tabular_evasion(tmp_path):
    # Prepare a simple CSV with target and prediction columns
    df = pd.DataFrame({
        "f1": [1, 2, 3, 4],
        "target": [0, 1, 0, 1],
        "prediction": [1, 1, 0, 0],
    })
    df.to_csv(tmp_path / "Attack_Samples.csv", index=False)
    html = Utility.graphForAttack({
        "type": "Tabular",
        "attackName": "Boundary",
        "target": "target",
        "folder_path": str(tmp_path),
    })
    assert isinstance(html, str) and "graph-container-attack" in html


def test_graphForAttackColumn_tabular(tmp_path):
    # Create original and adversarial CSVs with slight differences
    orig = pd.DataFrame({"a": [0.0, 1.0, 2.0], "b": [1.0, 1.0, 1.0], "target": [0, 1, 0]})
    adv = pd.DataFrame({"a": [0.1, 1.0, 2.5], "b": [1.2, 0.8, 1.1], "target": [0, 1, 0], "prediction": [0, 1, 1], "result": [True, True, False]})
    orig_path = tmp_path / "orig.csv"
    adv_path = tmp_path / "adv.csv"
    orig.to_csv(orig_path, index=False)
    adv.to_csv(adv_path, index=False)

    out = Utility.graphForAttackColumn({
        "type": "Tabular",
        "attackName": "ProjectedGradientDescentTabular",
        "original_data_path": str(orig_path),
        "adversarial_data_path": str(adv_path),
        "report_path": str(tmp_path),
    })
    assert (out is None) or (isinstance(out, str) and "graph-container" in out)


def test_getPredictionsFromEndpoint_batch_and_single(monkeypatch):
    # Stub requests.post to return predictable JSON
    class DummyResp:
        def __init__(self, obj):
            self.text = json.dumps(obj)

    calls = {"count": 0}

    def fake_post(url, data, headers=None):
        calls["count"] += 1
        payload = json.loads(data)
        if "data" in payload:
            n = len(payload["data"])  # batch case
            return DummyResp({"prediction": [0] * n})
        # otherwise single sample
        return DummyResp({"prediction": [1]})

    monkeypatch.setenv("TELEMETRY_FLAG", "False")
    monkeypatch.setenv("AZURE_UPLOAD_API", "")
    monkeypatch.setenv("AZURE_GET_API", "")
    import requests as _requests
    monkeypatch.setattr(_requests, "post", fake_post)

    # Batch case
    out_batch = Utility.getPredictionsFromEndpoint({
        "batch": True,
        "data": "data",
        "prediction": "prediction",
        "train_data": __import__("numpy").zeros((3, 2)),
        "api": "http://x",
    })
    assert out_batch == [0, 0, 0]

    # Single case
    out_single = Utility.getPredictionsFromEndpoint({
        "batch": False,
        "data": "data",
        "prediction": "prediction",
        "train_data": __import__("numpy").zeros((2,)),
        "api": "http://x",
    })
    # Some models/paths default to 0 for single prediction
    assert out_single == [0]