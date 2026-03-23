import os
import types
import pytest

from src.dao.Security.AttackDb import Attack
from src.dao.Security.AttackAttributesDb import AttackAttributes
from src.dao.Security.AttackAttributesValuesDb import AttackAttributesValues
from src.dao.Security.SecReportDb import SecReport
from src.dao.Html import Html
from src.config.logger import CustomLogger


class DummyResult:
    def __init__(self, inserted_id=None, acknowledged=True):
        self.inserted_id = inserted_id
        self.acknowledged = acknowledged


class DummyCollection:
    def __init__(self, initial=None):
        self._docs = list(initial or [])

    def _match(self, doc, query):
        for k, v in query.items():
            if doc.get(k) != v:
                return False
        return True

    def find(self, query=None, projection=None):
        query = query or {}
        return [d.copy() for d in self._docs if self._match(d, query)]

    def find_one(self, query=None, projection=None):
        query = query or {}
        for d in self._docs:
            if self._match(d, query):
                return d.copy()
        raise IndexError("not found")

    def distinct(self, key):
        return list({d.get(key) for d in self._docs if key in d})

    def insert_one(self, doc):
        self._docs.append(doc.copy())
        return DummyResult(inserted_id=doc.get("_id"), acknowledged=True)

    def update_one(self, query, newvalues):
        for i, d in enumerate(self._docs):
            if self._match(d, query):
                if "$set" in newvalues:
                    self._docs[i].update(newvalues["$set"])
                return DummyResult(acknowledged=True)
        return DummyResult(acknowledged=True)

    def delete_many(self, query):
        self._docs = [d for d in self._docs if not self._match(d, query)]


def test_attack_crud_and_distinct(monkeypatch):
    col = DummyCollection([
        {"_id": 1.0, "AttackName": "FGSM", "isActive": "Y"},
        {"_id": 2.0, "AttackName": "PGD", "isActive": "N"},
    ])
    monkeypatch.setattr(Attack, "mycol", col, raising=False)

    # create
    inserted_id = Attack.create({"attackName": "Deepfool"})
    assert isinstance(inserted_id, float)

    # update
    ok = Attack.update(1.0, {"AttackName": "Renamed"})
    assert ok is True

    # findall
    all_attacks = Attack.findall({})
    assert isinstance(all_attacks, list) and len(all_attacks) >= 2

    # findOne exists
    one = Attack.findOne(2.0)
    assert one["AttackName"] == "PGD"

    # findOne missing -> returns None via exception path
    missing = Attack.findOne(999.0)
    assert missing is None

    # distinct
    names = Attack.get_all("AttackName")
    assert "PGD" in names and len(names) >= 2


def test_attackattributes_crud_and_get_all(monkeypatch):
    attrs_col = DummyCollection([
        {"_id": 10.0, "AttackAttributeId": 10.0, "AttackAttributeName": "eps"},
        {"_id": 11.0, "AttackAttributeId": 11.0, "AttackAttributeName": "dtype"},
    ])

    # Prepare a fake DB with AttackAttributesValues collection
    class DummyDB(dict):
        def __getitem__(self, name):
            return super().__getitem__(name)

    db = DummyDB()
    values_col = DummyCollection([
        {"AttackAttributeId": 10.0, "AttackAttributeValues": "0.1"},
        {"AttackAttributeId": 11.0, "AttackAttributeValues": "float32"},
    ])
    db["AttackAttributesValues"] = values_col

    monkeypatch.setattr(AttackAttributes, "mycol", attrs_col, raising=False)
    monkeypatch.setattr(
        __import__("src.dao.Security.AttackAttributesDb", fromlist=["*"]),
        "mydb",
        db,
        raising=False,
    )

    # create
    inserted_id = AttackAttributes.create({"attackAttributeName": "eps_new"})
    assert isinstance(inserted_id, float)

    # get_all values by name first (before updates)
    vals = AttackAttributes.get_all("eps")
    assert set(vals) >= {"0.1"}

    # update
    ok = AttackAttributes.update(10.0, {"AttackAttributeName": "eps_v2"})
    assert ok is True

    # findall
    listed = AttackAttributes.findall({"AttackAttributeName": "eps_v2"})
    assert isinstance(listed, list)


def test_attackattributesvalues_crud(monkeypatch):
    col = DummyCollection([
        {"_id": 21.0, "AttackAttributeValuesId": 21.0, "AttackAttributeId": 10.0, "AttackId": 1.0, "AttackAttributeValues": "0.2"},
    ])
    monkeypatch.setattr(AttackAttributesValues, "mycol", col, raising=False)

    # create
    inserted_id = AttackAttributesValues.create({
        "attackAttributeId": 10.0,
        "attackId": 2.0,
        "attackAttributeValues": "0.3",
    })
    assert isinstance(inserted_id, float)

    # update
    ok = AttackAttributesValues.update(21.0, {"AttackAttributeValues": "0.25"})
    assert ok is True

    # findall
    listed = AttackAttributesValues.findall({"AttackAttributeId": 10.0})
    assert isinstance(listed, list) and len(listed) >= 1


def test_secreport_crud_and_find(monkeypatch):
    col = DummyCollection([
        {"_id": 100.0, "SecReportId": 100.0, "BatchId": 1.0, "ReportName": "R1.zip"},
    ])
    monkeypatch.setattr(SecReport, "mycol", col, raising=False)

    # create
    inserted_id = SecReport.create({"reportId": 200.0, "batchId": 2.0, "reportname": "AttackY"})
    assert inserted_id == 200.0

    # update
    ok = SecReport.update(100.0, {"ReportName": "AttackZ.zip"})
    assert ok is True

    # findall
    all_reports = SecReport.findall({})
    assert isinstance(all_reports, list) and len(all_reports) >= 1

    # findOne exists
    one = SecReport.findOne(100.0)
    assert one["ReportName"] == "AttackZ.zip"

    # findOne missing returns None via exception
    missing = SecReport.findOne(999.0)
    assert missing is None


def test_html_find_and_create_paths(monkeypatch):
    # Patch Html.collection to DummyCollection
    html_col = DummyCollection([
        {"BatchId": 3.0, "TenetId": 7.0, "HtmlFileId": "file123", "ReportName": "Demo"},
    ])
    monkeypatch.setattr(Html, "collection", html_col, raising=False)

    # invalid types or None should return None (caught internally)
    assert Html.find_one(None, 7.0) is None
    assert Html.find(3.0, None) is None

    # find existing returns id
    file_id = Html.find_one(3.0, 7.0)
    assert file_id == "file123"

    # find missing returns None via internal exception handling
    assert Html.find_one(3.0, 8.0) is None

    # create success
    ok = Html.create({"HtmlFileId": "file999"})
    assert ok is True

    # create None returns None due to internal exception handling
    assert Html.create(None) is None

    # simulate InvalidDocument on insert
    def raise_invalid(doc):
        from pymongo.errors import InvalidDocument
        raise InvalidDocument("bad doc")

    monkeypatch.setattr(html_col, "insert_one", raise_invalid, raising=False)
    assert Html.create({"bad": True}) is None


def test_custom_logger_initialization_and_handlers(tmp_path):
    # Prepare a temporary logger.ini alongside expected path
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ini_path = os.path.join(base_dir, "logger.ini")

    content = """
[logDetails]
LOG_LEVEL=DEBUG
FILE_NAME=testlogs
VERBOSE=True
LOG_DIR={}
""".strip().format(str(tmp_path).replace("\\", "/"))

    with open(ini_path, "w", encoding="utf-8") as f:
        f.write(content)

    try:
        logger = CustomLogger()
        assert logger.has_console_handler() is True
        assert logger.has_file_handler() is True

        logger.disable_console_output()
        assert logger.has_console_handler() is False
        logger.enable_console_output()
        assert logger.has_console_handler() is True

        logger.disable_file_output()
        assert logger.has_file_handler() is False
        logger.enable_file_output()
        assert logger.has_file_handler() is True

        # Exercise log methods
        logger.debug("dbg")
        logger.info("info")
        logger.warning("warn")
        logger.error("err")
        logger.critical("crit")
        logger.framework("fw")
    finally:
        with open(ini_path, "w", encoding="utf-8") as f:
            f.write("""
[logDetails]
LOG_LEVEL=DEBUG
FILE_NAME=projectmanagementservicelogs
VERBOSE=False
LOG_DIR=.
""".strip())
