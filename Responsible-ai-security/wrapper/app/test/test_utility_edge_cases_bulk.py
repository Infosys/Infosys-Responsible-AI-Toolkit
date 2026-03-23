import numpy as np
import datetime as dt

from src.service.utility import Utility as UT


def test_attackDesc_known_and_unknown():
    assert "SimBA" in UT.attackDesc("SimBA")
    assert UT.attackDesc("__UNKNOWN__") == ""


def test_dateTimeFormat_none_and_value():
    s1 = UT.dateTimeFormat(None)
    assert isinstance(s1, str)
    t = dt.datetime(2024, 1, 1, 12, 30)
    s2 = UT.dateTimeFormat(t)
    assert "2024" in s2


def test_updateReportsList_and_sortReportsList():
    now = dt.datetime.now()
    older = now - dt.timedelta(days=1)
    reportList = [
        {"ReportName": "PGD.zip", "CreatedDateTime": older},
        {"ReportName": "PGD.zip", "CreatedDateTime": now},
        {"ReportName": "ModelA.zip", "CreatedDateTime": now},
    ]
    out = UT.updateReportsList({"reportList": reportList, "modelName": "ModelA", "attackList": ["PGD"]})
    assert len(out) == 1 and out[0]["CreatedDateTime"] == now
    sorted_out = UT.sortReportsList(out)
    assert sorted_out[0]["CreatedDateTime"] == now


def test_combineList_evasion_and_inference():
    a = np.array([[1], [0]])
    b = np.array([[0], [1]])
    d = np.array([[0], [1]])
    # evasion
    e, f = UT.combineList({"attack_data": a, "target_data": b, "prediction_data": d, "type": "Evasion"})
    assert len(e) == 2 and isinstance(f, list)
    # inference
    e2, f2 = UT.combineList({"attack_data": a, "target_data": b, "prediction_data": d, "type": "Inference"})
    assert len(e2) == 2 and isinstance(f2, list)


def test_checkList_basic():
    class M:
        def predict(self, X):
            # return probabilities for 2 classes
            return np.array([[0.7, 0.3] for _ in range(len(X))])

    model = M()
    x = np.array([[1.0, 2.0], [3.0, 4.0]])
    adv = np.array([[1.1, 2.2], [3.3, 4.4]])
    out = UT.checkList({"model": model, "original_data": x, "adversial_data": adv})
    assert isinstance(out, list)
