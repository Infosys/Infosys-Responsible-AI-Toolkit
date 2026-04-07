import datetime

from src.dao.Security.AttackDb import Attack
from src.dao.Security.SecReportDb import SecReport


class DummyResult:
    def __init__(self, inserted_id=None, acknowledged=True):
        self.inserted_id = inserted_id
        self.acknowledged = acknowledged


class DummyCollection:
    def __init__(self):
        self._docs = []

    def find(self, query, projection):
        # naive filter: support equality on single key
        if not query:
            return list(self._docs)
        key, val = next(iter(query.items()))
        return [doc for doc in self._docs if doc.get(key) == val]

    def distinct(self, field):
        return list({doc.get(field) for doc in self._docs if field in doc})

    def insert_one(self, doc):
        self._docs.append(doc)
        return DummyResult(inserted_id=doc.get("_id"))

    def update_one(self, filter_query, newvalues):
        key, val = next(iter(filter_query.items()))
        for doc in self._docs:
            if doc.get(key) == val:
                if "$set" in newvalues:
                    for k, v in newvalues["$set"].items():
                        doc[k] = v
        return DummyResult(acknowledged=True)

    def delete_many(self, query):
        key, val = next(iter(query.items()))
        self._docs = [doc for doc in self._docs if doc.get(key) != val]


def test_attackdao_crud(monkeypatch):
    dummy = DummyCollection()
    # Pre-populate one doc to exercise find and distinct
    now = datetime.datetime.now()
    dummy.insert_one({
        "_id": 1.0,
        "id": 1.0,
        "AttackId": 1.0,
        "AttackName": "FastGradientMethod",
        "isActive": "Y",
        "CreatedDateTime": now,
        "LastUpdatedDateTime": now,
    })
    monkeypatch.setattr(Attack, "mycol", dummy)

    # findall
    res = Attack.findall({"_id": 1.0})
    assert len(res) == 1 and res[0]["AttackName"] == "FastGradientMethod"

    # get_all distinct
    assert Attack.get_all("AttackName") == ["FastGradientMethod"]

    # create new
    inserted_id = Attack.create({"attackName": "Boundary"})
    assert inserted_id is not None

    # update
    ack = Attack.update(inserted_id, {"AttackName": "Renamed"})
    assert ack is True

    # delete
    Attack.delete({"_id": inserted_id})
    remaining = Attack.findall({})
    assert all(doc.get("_id") != inserted_id for doc in remaining)


def test_secreportdao_crud(monkeypatch):
    dummy = DummyCollection()
    now = datetime.datetime.now()
    dummy.insert_one({
        "_id": "R1",
        "id": "R1",
        "SecReportId": "R1",
        "BatchId": "B123",
        "ReportName": "FastGradientMethod.zip",
        "CreatedDateTime": now,
        "LastUpdatedDateTime": now,
    })
    monkeypatch.setattr(SecReport, "mycol", dummy)

    # findall
    res = SecReport.findall({"BatchId": "B123"})
    assert len(res) == 1 and res[0]["ReportName"] == "FastGradientMethod.zip"

    # findOne
    one = SecReport.findOne("R1")
    assert one["SecReportId"] == "R1"

    # create new
    new_id = SecReport.create({"reportId": "R2", "batchId": "B123", "reportname": "AttackY"})
    assert new_id == "R2"

    # update
    ack = SecReport.update("R2", {"ReportName": "AttackZ.zip"})
    assert ack is True

    # delete
    SecReport.delete({"BatchId": "B123"})
    assert SecReport.findall({"BatchId": "B123"}) == []
