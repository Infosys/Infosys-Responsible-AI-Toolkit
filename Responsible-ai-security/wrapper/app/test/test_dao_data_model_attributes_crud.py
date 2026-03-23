import time

from types import SimpleNamespace

from src.dao.DataAttributesDb import DataAttributes
from src.dao.DataAttributesValuesDb import DataAttributesValues
from src.dao.ModelAttributesDb import ModelAttributes
from src.dao.ModelAttributesValuesDb import ModelAttributesValues
from src.dao.DataDb import Data
from src.dao.ModelDb import Model


class DummyCol:
    def __init__(self):
        self.items = []
        self.last_update = None

    def distinct(self, field):
        return list({doc.get(field) for doc in self.items})

    def find(self, query, proj):
        def match(doc):
            return all(doc.get(k) == v for k, v in query.items())
        return [dict(doc) for doc in self.items if match(doc)]

    def find_one(self, query):
        for doc in self.items:
            if all(doc.get(k) == v for k, v in query.items()):
                return dict(doc)
        return None

    def insert_one(self, doc):
        self.items.append(dict(doc))
        return SimpleNamespace(inserted_id=doc.get("_id", time.time()))

    def update_one(self, filt, newvalues):
        for doc in self.items:
            if all(doc.get(k) == v for k, v in filt.items()):
                doc.update(newvalues.get("$set", {}))
                self.last_update = newvalues
                return SimpleNamespace(acknowledged=True)
        return SimpleNamespace(acknowledged=False)

    def delete_many(self, query):
        self.items = [doc for doc in self.items if not all(doc.get(k) == v for k, v in query.items())]


def test_data_attributes_crud(monkeypatch):
    col = DummyCol()
    monkeypatch.setattr(DataAttributes, "mycol", col)

    aid = DataAttributes.create({"dataAttributeName": "gt_label", "tenetId": 1})
    assert aid is not None
    items = DataAttributes.findall({"DataAttributeName": "gt_label"})
    assert len(items) == 1
    updated = DataAttributes.update(items[0]["_id"], {"DataAttributeName": "gt"})
    assert updated is True
    # distinct via get_all
    distinct_vals = DataAttributes.get_all("DataAttributeName")
    assert "gt" in distinct_vals or "gt_label" in distinct_vals
    DataAttributes.delete({"DataAttributeName": "gt"})
    assert DataAttributes.findall({"DataAttributeName": "gt"}) == []


def test_model_attributes_crud(monkeypatch):
    col = DummyCol()
    monkeypatch.setattr(ModelAttributes, "mycol", col)
    mid = ModelAttributes.create({"modelAttributeName": "mf", "tenetId": 1})
    assert mid is not None
    items = ModelAttributes.findall({"ModelAttributeName": "mf"})
    assert len(items) == 1
    assert ModelAttributes.update(items[0]["_id"], {"ModelAttributeName": "mf_v2"}) is True
    ModelAttributes.delete({"ModelAttributeName": "mf_v2"})
    assert ModelAttributes.findall({"ModelAttributeName": "mf_v2"}) == []


def test_data_attributes_values_crud(monkeypatch):
    col = DummyCol()
    monkeypatch.setattr(DataAttributesValues, "mycol", col)
    did = DataAttributesValues.create({
        "dataAttributeId": 10,
        "dataAttributeValues": "label1",
        "tenetId": 1,
        "batchId": 5,
        "dataId": 7,
    })
    assert did is not None
    items = DataAttributesValues.findall({"DataAttributeId": 10})
    assert len(items) == 1
    assert DataAttributesValues.update(items[0]["_id"], {"DataAttributeValues": "label2"}) is True
    DataAttributesValues.delete({"DataAttributeValues": "label2"})
    assert DataAttributesValues.findall({"DataAttributeValues": "label2"}) == []


def test_model_attributes_values_crud(monkeypatch):
    col = DummyCol()
    monkeypatch.setattr(ModelAttributesValues, "mycol", col)
    mid = ModelAttributesValues.create({
        "modelAttributeId": 10,
        "modelAttributeValues": "Yes",
        "tenetId": 1,
        "modelId": 3,
    })
    assert mid is not None
    items = ModelAttributesValues.findall({"ModelAttributeId": 10})
    assert len(items) == 1
    assert ModelAttributesValues.update(items[0]["_id"], {"ModelAttributeValues": "No"}) is True
    ModelAttributesValues.delete({"ModelAttributeValues": "No"})
    assert ModelAttributesValues.findall({"ModelAttributeValues": "No"}) == []


def test_data_and_model_crud(monkeypatch):
    # Data
    dcol = DummyCol()
    monkeypatch.setattr(Data, "mycol", dcol)
    did = Data.create({
        "dataSetName": "demo",
        "sampleData": [],
        "userId": 0,
        "groundTruthImageFileId": "none",
        "tenetId": 1,
    })
    assert did is not None
    assert len(Data.findall({"DataSetName": "demo"})) == 1
    assert Data.update(did, {"DataSetName": "newdemo"}) is True
    Data.delete({"DataSetName": "newdemo"})
    assert Data.findall({"DataSetName": "newdemo"}) == []

    # Model
    mcol = DummyCol()
    monkeypatch.setattr(Model, "mycol", mcol)
    mid = Model.create({
        "modelName": "m1",
        "modelVersion": "v1",
        "modelData": 123,
        "modelEndPoint": "http://api",
        "userId": 0,
        "tenetId": 1,
    })
    assert mid is not None
    assert len(Model.findall({"ModelName": "m1"})) == 1
    assert Model.update(mid, {"ModelName": "m2"}) is True
    Model.delete({"ModelName": "m2"})
    assert Model.findall({"ModelName": "m2"}) == []
