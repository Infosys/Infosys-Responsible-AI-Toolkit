import time
from types import SimpleNamespace

from src.dao.Html import Html
from src.dao.Security.SecReportDb import SecReport


class DummyCol:
    def __init__(self):
        self.items = []

    def find_one(self, query, projection=None):
        # Simulate returning HtmlFileId
        for doc in self.items:
            if all(doc.get(k) == v for k, v in query.items()):
                if projection and 'HtmlFileId' in projection:
                    return {'HtmlFileId': doc.get('HtmlFileId'), 'ReportName': doc.get('ReportName')}
                return dict(doc)
        return None

    def insert_one(self, doc):
        self.items.append(dict(doc))
        # Simulate PyMongo's InsertOneResult with inserted_id
        inserted_id = doc.get("_id") or doc.get("id") or doc.get("SecReportId")
        return SimpleNamespace(acknowledged=True, inserted_id=inserted_id)

    def find(self, query, proj):
        def match(doc):
            return all(doc.get(k) == v for k, v in query.items())
        return [dict(doc) for doc in self.items if match(doc)]

    def update_one(self, filt, newvalues):
        for doc in self.items:
            if all(doc.get(k) == v for k, v in filt.items()):
                doc.update(newvalues.get("$set", {}))
                return SimpleNamespace(acknowledged=True)
        return SimpleNamespace(acknowledged=False)

    def delete_many(self, query):
        self.items = [doc for doc in self.items if not all(doc.get(k) == v for k, v in query.items())]


def test_html_find_and_create(monkeypatch):
    col = DummyCol()
    monkeypatch.setattr(Html, "collection", col)

    # Seed document
    col.insert_one({
        "BatchId": 1.0,
        "TenetId": 2.0,
        "HtmlFileId": "blob123",
        "ReportName": "model.zip",
    })

    fid1 = Html.find_one(1.0, 2.0)
    assert fid1 == "blob123"
    fid2 = Html.find(1.0, 2.0)
    assert fid2 == "blob123"

    # Create new document
    ok = Html.create({
        "BatchId": 3.0,
        "TenetId": 2.0,
        "HtmlFileId": "blob456",
        "ReportName": "model2.zip",
    })
    assert ok is True


def test_html_find_negative(monkeypatch):
    col = DummyCol()
    monkeypatch.setattr(Html, "collection", col)

    # No seed; functions should handle internally and return None
    assert Html.find_one(1.0, 2.0) is None
    assert Html.find(1.0, 2.0) is None


def test_html_negative_paths(monkeypatch):
    col = DummyCol()
    monkeypatch.setattr(Html, "collection", col)

    # Missing doc paths return None
    assert Html.find_one(1.0, 2.0) is None
    assert Html.find(1.0, 2.0) is None

    # Invalid types handled internally (return None)
    assert Html.find_one(None, 2.0) is None
    assert Html.find_one(1.0, None) is None
    assert Html.find_one("x", 2.0) is None
    assert Html.find_one(1.0, "y") is None

    # Create with None document returns None
    assert Html.create(None) is None


def test_secreport_crud(monkeypatch):
    col = DummyCol()
    monkeypatch.setattr(SecReport, "mycol", col)

    # Create
    rid = SecReport.create({"reportId": 100.0, "batchId": 9.0, "reportname": "ReportX"})
    assert rid == 100.0

    # Find
    items = SecReport.findall({"BatchId": 9.0})
    assert len(items) == 1

    # Update
    assert SecReport.update(100.0, {"ReportName": "ReportX.zip"}) is True

    # Delete
    SecReport.delete({"BatchId": 9.0})
    assert SecReport.findall({"BatchId": 9.0}) == []


def test_secreport_findOne_and_update_ack(monkeypatch):
    col = DummyCol()
    monkeypatch.setattr(SecReport, "mycol", col)
    rid = SecReport.create({"reportId": 200.0, "batchId": 10.0, "reportname": "ReportY"})
    assert rid == 200.0
    one = SecReport.findOne(200.0)
    assert one["BatchId"] == 10.0
    assert one["ReportName"].endswith(".zip")
    assert SecReport.update(200.0, {"ReportName": "ReportY.zip"}) is True
