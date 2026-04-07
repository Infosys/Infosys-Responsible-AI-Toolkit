import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from src.routing import routers as r


# Build a TestClient app including the routers under test
app = FastAPI()
app.include_router(r.attack)
app.include_router(r.bulk)


def test_get_attacks_endpoint(monkeypatch):
    monkeypatch.setattr(r.Infosys, "getAttackFuncs", lambda payload: ["A1", "A2"])  # simple list
    form = {"TargetClassifier": "Sklearn", "TargetDataType": "Tabular"}
    with TestClient(app) as client:
        resp = client.post("/rai/v1/security_workbench/attack", data=form)
    assert resp.status_code == 200
    assert resp.json() == ["A1", "A2"]


def test_add_attack_endpoint(monkeypatch):
    monkeypatch.setattr(r.Infosys, "addAttack", lambda payload: "Attack Added Sucessfully")
    payload = {"attackName": "FooAttack", "targetClassifier": "Sklearn", "targetDataType": "Tabular"}
    with TestClient(app) as client:
        resp = client.post("/rai/v1/security_workbench/addattack", json=payload)
    assert resp.status_code == 200
    assert resp.json() == "Attack Added Sucessfully"


def test_delete_attack_endpoint(monkeypatch):
    monkeypatch.setattr(r.Infosys, "deleteAttack", lambda payload: "Attack Deleted Sucessfully")
    with TestClient(app) as client:
        resp = client.delete("/rai/v1/security_workbench/deleteattack", params={"AttacFunc": "FooAttack"})
    assert resp.status_code == 200
    assert resp.json() == "Attack Deleted Sucessfully"


def test_run_all_attacks_endpoint(monkeypatch):
    monkeypatch.setattr(r.Bulk, "runAllAttack", lambda payload: 123.0)
    with TestClient(app) as client:
        resp = client.post("/rai/v1/security_workbench/runallattacks", data={"batchId": 99.0})
    assert resp.status_code == 200
    assert resp.json() == {"BatchId": 123.0}


def test_endpoints_error_paths(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("boom")

    with TestClient(app) as client:
        monkeypatch.setattr(r.Infosys, "getAttackFuncs", boom)
        resp = client.post("/rai/v1/security_workbench/attack", data={"TargetClassifier": "Sk", "TargetDataType": "Tab"})
        assert resp.status_code == 500

        monkeypatch.setattr(r.Infosys, "addAttack", boom)
        resp = client.post("/rai/v1/security_workbench/addattack", json={"attackName": "A"})
        assert resp.status_code == 500

        monkeypatch.setattr(r.Infosys, "deleteAttack", boom)
        resp = client.delete("/rai/v1/security_workbench/deleteattack", params={"AttacFunc": "A"})
        assert resp.status_code == 500

        monkeypatch.setattr(r.Bulk, "runAllAttack", boom)
        resp = client.post("/rai/v1/security_workbench/runallattacks", data={"batchId": 1.0})
        assert resp.status_code == 500
