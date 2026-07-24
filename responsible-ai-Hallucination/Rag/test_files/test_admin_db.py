# test_admin_db.py
#
# Focused unit tests for RAG.dao.AdminDb.

import os
import sys
import types
import pytest

# Ensure src/RAG is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from RAG.dao import AdminDb as adm


# ------------------- Fakes for Mongo client / DB / collection -------------------


class FakeInsertResult:
    def __init__(self, acknowledged=True):
        self.acknowledged = acknowledged


class FakeUpdateResult:
    def __init__(self, acknowledged=True):
        self.acknowledged = acknowledged


class FakeDeleteResult:
    def __init__(self, acknowledged=True):
        self.acknowledged = acknowledged


class FakeCollection:
    def __init__(self, docs=None, raise_on=None):
        # docs: list of dict documents, like a Mongo cursor would yield
        self._docs = docs or []
        self._raise_on = raise_on or set()

    def find(self, query, projection=None):
        if "find" in self._raise_on:
            raise Exception("fake find error")
        # Return list of dicts, so mycol.find(...)[0] is a dict
        return self._docs

    def insert_one(self, value):
        if "insert_one" in self._raise_on:
            raise Exception("fake insert error")
        self._docs.append(value)
        return FakeInsertResult(acknowledged=True)

    def update_one(self, query, newvalues):
        if "update_one" in self._raise_on:
            raise Exception("fake update error")
        return FakeUpdateResult(acknowledged=True)

    def delete_one(self, query):
        if "delete_one" in self._raise_on:
            raise Exception("fake delete_one error")
        return FakeDeleteResult(acknowledged=True)

    def delete_many(self, query):
        if "delete_many" in self._raise_on:
            raise Exception("fake delete_many error")
        return FakeDeleteResult(acknowledged=True)


class FakeDB(dict):
    # behaves like a Mongo database: myclient["dbname"]
    pass


class FakeMongoClient:
    def __init__(self, dbs):
        # dbs: mapping db_name -> FakeDB
        self._dbs = dbs

    def __getitem__(self, name):
        return self._dbs[name]


# ------------------- DB.connect() branches --------------------------------------


def test_db_connect_cosmos_branch(monkeypatch):
    """Cover DB.connect when DB_TYPE='cosmos'."""

    os.environ["DB_TYPE"] = "cosmos"
    os.environ["COSMOS_PATH"] = "fakecosmos://"
    os.environ["DB_NAME"] = "testdb"
    os.environ["DEFAULT_DB_NAME"] = "defaultdb"

    fake_db = FakeDB()
    fake_default_db = FakeDB()
    fake_client = FakeMongoClient({"testdb": fake_db, "defaultdb": fake_default_db})

    # Patch pymongo.MongoClient to return our fake client
    def fake_mongoclient(uri):
        return fake_client

    monkeypatch.setattr(adm.pymongo, "MongoClient", fake_mongoclient)

    # Patch gridfs.GridFS to something harmless
    class FakeGridFS:
        def __init__(self, db):
            self.db = db

    monkeypatch.setattr(adm, "gridfs", types.SimpleNamespace(GridFS=FakeGridFS))

    mydb = adm.DB.connect()
    assert isinstance(mydb, FakeDB)


def test_db_connect_mongo_branch(monkeypatch):
    """Cover DB.connect when DB_TYPE!='cosmos' (mongo branch)."""

    os.environ["DB_TYPE"] = "mongo"
    os.environ["MONGO_PATH"] = "fakemongo://"
    os.environ["DB_NAME"] = "testdb2"
    os.environ["DEFAULT_DB_NAME"] = "defaultdb2"

    fake_db2 = FakeDB()
    fake_default_db2 = FakeDB()
    fake_client2 = FakeMongoClient({"testdb2": fake_db2, "defaultdb2": fake_default_db2})

    def fake_mongoclient(uri):
        return fake_client2

    monkeypatch.setattr(adm.pymongo, "MongoClient", fake_mongoclient)

    class FakeGridFS:
        def __init__(self, db):
            self.db = db

    monkeypatch.setattr(adm, "gridfs", types.SimpleNamespace(GridFS=FakeGridFS))

    mydb = adm.DB.connect()
    assert isinstance(mydb, FakeDB)


def test_db_connect_exception_path(monkeypatch):
    """Cover the exception handler in DB.connect."""

    # Force MongoClient to raise
    def fake_mongoclient(uri):
        raise Exception("connect failure")

    monkeypatch.setattr(adm.pymongo, "MongoClient", fake_mongoclient)

    # Prevent sys.exit from killing the test run; just capture that it would be called.
    exit_called = {"flag": False}

    def fake_exit(code=0):
        exit_called["flag"] = True
        raise SystemExit(code)

    monkeypatch.setattr(adm.sys, "exit", fake_exit)

    os.environ["DB_TYPE"] = "mongo"
    os.environ["MONGO_PATH"] = "fakemongo://"
    os.environ["DB_NAME"] = "testdb3"
    os.environ["DEFAULT_DB_NAME"] = "defaultdb3"

    with pytest.raises(SystemExit):
        adm.DB.connect()

    assert exit_called["flag"] is True


# ------------------- ProfaneWords / feedbackdb / Results ------------------------


def test_profane_words_findone_success(monkeypatch):
    """Cover ProfaneWords.findOne happy path."""

    docs = [{"_id": "id1", "word": "badword"}]
    fake_col = FakeCollection(docs=docs)

    # ProfaneWords.mycol is set at import; patch it
    monkeypatch.setattr(adm.ProfaneWords, "mycol", fake_col)

    val = adm.ProfaneWords.findOne("id1")
    assert isinstance(val, adm.AttributeDict)
    assert val["_id"] == "id1"
    assert val["word"] == "badword"


def test_profane_words_findone_exception(monkeypatch):
    """Cover ProfaneWords.findOne exception path."""

    class RaisingCollection(FakeCollection):
        def find(self, query, projection=None):
            raise Exception("fake error")

    fake_col = RaisingCollection()
    monkeypatch.setattr(adm.ProfaneWords, "mycol", fake_col)

    # Should not raise; logs error and returns None
    val = adm.ProfaneWords.findOne("idX")
    assert val is None


def test_feedbackdb_create_success(monkeypatch):
    """Cover feedbackdb.create success branch."""

    fake_col = FakeCollection()
    monkeypatch.setattr(adm.feedbackdb, "feedback_collection", fake_col)

    ack = adm.feedbackdb.create({"field": "value"})
    assert ack is True


def test_feedbackdb_create_exception(monkeypatch):
    """Cover feedbackdb.create exception branch."""

    fake_col = FakeCollection(raise_on={"insert_one"})
    monkeypatch.setattr(adm.feedbackdb, "feedback_collection", fake_col)

    # Should not raise; logs error and returns None
    ack = adm.feedbackdb.create({"field": "value"})
    assert ack is None


def test_results_findone_success(monkeypatch):
    """Cover Results.findOne success path."""

    docs = [{"_id": "r1", "data": 123}]
    fake_col = FakeCollection(docs=docs)
    monkeypatch.setattr(adm.Results, "mycol", fake_col)

    val = adm.Results.findOne("r1")
    assert isinstance(val, adm.AttributeDict)
    assert val["_id"] == "r1"
    assert val["data"] == 123


def test_results_findone_exception(monkeypatch):
    """Cover Results.findOne exception path."""

    fake_col = FakeCollection(raise_on={"find"})
    monkeypatch.setattr(adm.Results, "mycol", fake_col)

    val = adm.Results.findOne("rX")
    assert val is None


def test_createwithfeedback_success(monkeypatch):
    """Cover Results.createwithfeedback success path."""

    fake_col2 = FakeCollection()
    monkeypatch.setattr(adm.Results, "mycol2", fake_col2)

    ack = adm.Results.createwithfeedback({"field": "val"})
    assert ack is True


def test_createwithfeedback_exception(monkeypatch):
    """Cover Results.createwithfeedback exception path."""

    fake_col2 = FakeCollection(raise_on={"insert_one"})
    monkeypatch.setattr(adm.Results, "mycol2", fake_col2)

    ack = adm.Results.createwithfeedback({"field": "val"})
    assert ack is None


def test_results_update_success(monkeypatch):
    """Cover Results.update success path."""

    fake_col = FakeCollection()
    monkeypatch.setattr(adm.Results, "mycol", fake_col)

    ack = adm.Results.update({"_id": "r1"}, {"field": "new"})
    assert ack is True


def test_results_update_exception(monkeypatch):
    """Cover Results.update exception path."""

    fake_col = FakeCollection(raise_on={"update_one"})
    monkeypatch.setattr(adm.Results, "mycol", fake_col)

    ack = adm.Results.update({"_id": "r1"}, {"field": "new"})
    assert ack is None


def test_results_delete_success(monkeypatch):
    """Cover Results.delete success path."""

    fake_col = FakeCollection()
    monkeypatch.setattr(adm.Results, "mycol", fake_col)

    res = adm.Results.delete("id1")
    # Returns the delete_one result object
    assert isinstance(res, FakeDeleteResult)


def test_results_delete_exception(monkeypatch):
    """Cover Results.delete exception path."""

    fake_col = FakeCollection(raise_on={"delete_one"})
    monkeypatch.setattr(adm.Results, "mycol", fake_col)

    res = adm.Results.delete("id1")
    assert res is None