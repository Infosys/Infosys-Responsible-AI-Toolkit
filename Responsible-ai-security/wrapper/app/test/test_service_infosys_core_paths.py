import types

from src.service.service import Infosys


def test_getavailableAttack_returns_list(monkeypatch):
    # Force assessment generation off to return full list
    from src.config import urls as urls_mod
    monkeypatch.setattr(urls_mod.UrlLinks, "Assessment_Generation", False)
    out = Infosys.getavailableAttack()
    assert isinstance(out, list)
    assert "Augly" in out


def test_logUI_returns_empty():
    assert Infosys.logUI({}) == ""


def test_getAttackFuncs_returns_sorted(monkeypatch):
    # Simulate classifier and datatype matching with value lookups
    import src.service.service as svc

    # First, findall for classifier
    classifier_matches = [
        {"AttackId": 1, "AttackAttributeId": 10, "AttackAttributeValues": "Sklearn"},
    ]
    # Then for datatype
    data_matches = [
        {"AttackId": 1, "AttackAttributeId": 11, "AttackAttributeValues": "Tabular"},
    ]
    # Values listing for AttackId -> include additional attack names beyond classifier/dataType
    values_for_attack = [
        {"AttackId": 1, "AttackAttributeId": 12, "AttackAttributeValues": "ProjectedGradientDescentTabular"},
        {"AttackId": 1, "AttackAttributeId": 13, "AttackAttributeValues": "MembershipInferenceRule"},
    ]

    def fake_findall(query):
        if "AttackAttributeValues" in query and query["AttackAttributeValues"] == "Sklearn":
            return classifier_matches
        if "AttackAttributeValues" in query and query["AttackAttributeValues"] == "Tabular":
            return data_matches
        if "AttackId" in query:
            return values_for_attack
        return []

    monkeypatch.setattr(svc.AttackAttributesValues, "findall", fake_findall)

    out = Infosys.getAttackFuncs({"targetClassifier": "Sklearn", "targetDataType": "Tabular"})
    assert out == sorted(["ProjectedGradientDescentTabular", "MembershipInferenceRule"])


def test_addAttack_existing(monkeypatch):
    from src.dao.Security import AttackDb as AD
    monkeypatch.setattr(AD.Attack, "mycol", types.SimpleNamespace(find_one=lambda q: {"AttackName": "Foo"}))
    out = Infosys.addAttack({"attackName": "Foo"})
    assert out == "Attack Already Exists"


def test_addAttack_new(monkeypatch):
    import src.service.service as svc
    monkeypatch.setattr(svc.Attack, "mycol", types.SimpleNamespace(find_one=lambda q: None))
    monkeypatch.setattr(svc.Attack, "create", lambda doc: 1)
    monkeypatch.setattr(svc.AttackAttributes, "create", lambda doc: 2)
    monkeypatch.setattr(svc.AttackAttributesValues, "create", lambda doc: 3)

    payload = {"attackName": "Bar", "targetClassifier": "Sklearn", "targetDataType": "Tabular"}
    out = Infosys.addAttack(payload)
    assert out == "Attack Added Sucessfully"


def test_deleteAttack_none(monkeypatch):
    import src.service.service as svc
    monkeypatch.setattr(svc.AttackAttributesValues, "findall", lambda q: [])
    out = Infosys.deleteAttack({"attackName": "Nope"})
    assert out == "No Attack Available to Delete"


def test_deleteAttack_success(monkeypatch):
    import src.service.service as svc
    matches = [{"AttackId": 1, "AttackAttributeId": 2, "AttackAttributeValuesId": 3}]
    monkeypatch.setattr(svc.AttackAttributesValues, "findall", lambda q: matches)
    monkeypatch.setattr(svc.AttackAttributesValues, "delete", lambda q: None)
    monkeypatch.setattr(svc.AttackAttributes, "delete", lambda q: None)
    monkeypatch.setattr(svc.Attack, "delete", lambda q: None)

    out = Infosys.deleteAttack({"attackName": "Foo"})
    assert out == "Attack Deleted Sucessfully"
