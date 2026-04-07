import time

from types import SimpleNamespace

from src.dao.ModelAttributesDb import ModelAttributes
from src.dao.DataAttributesDb import DataAttributes


class DummyCollection:
    def __init__(self):
        self.docs = []

    def insert_one(self, doc):
        self.docs.append(doc)
        return SimpleNamespace(inserted_id=doc.get("_id"))

    def update_one(self, filt, newvalues):
        for d in self.docs:
            if d.get("_id") == filt.get("_id"):
                d.update(newvalues.get("$set", {}))
        return SimpleNamespace(acknowledged=True)

    def find(self, query, proj):
        def match(d, q):
            return all(d.get(k) == v for k, v in q.items())
        return [d for d in self.docs if match(d, query)]

    def find_one(self, query):
        fs = self.find(query, {})
        return fs[0] if fs else None

    def distinct(self, field):
        seen = set()
        for d in self.docs:
            val = d.get(field)
            if val is not None:
                seen.add(val)
        return list(seen)

    def delete_many(self, query):
        before = len(self.docs)
        self.docs = [d for d in self.docs if any(d.get(k) != v for k, v in query.items())]
        return SimpleNamespace(deleted_count=before - len(self.docs))


def test_model_attributes_crud_and_queries(monkeypatch):
    col = DummyCollection()
    monkeypatch.setattr(ModelAttributes, "mycol", col)

    # Create
    new_id = ModelAttributes.create({"modelAttributeName": "mf_v2", "tenetId": "T1"})
    assert new_id is not None

    # Update
    assert ModelAttributes.update(new_id, {"ModelAttributeName": "mf_v3"}) is True

    # Findall
    res = ModelAttributes.findall({"ModelAttributeName": "mf_v3"})
    assert len(res) == 1

    # Distinct
    names = ModelAttributes.get_all("ModelAttributeName")
    assert "mf_v3" in names

    # FindOne
    one = ModelAttributes.findOne(new_id)
    assert one["ModelAttributeName"] == "mf_v3"

    # findMAVId
    mid = ModelAttributes.findMAVId({"ModelAttributeName": "mf_v3"}, {"tenetId": "T1"})
    assert mid == new_id

    # Delete
    ModelAttributes.delete({"ModelAttributeName": "mf_v3"})
    assert len(col.docs) == 0


def test_data_attributes_crud_and_queries(monkeypatch):
    col = DummyCollection()
    monkeypatch.setattr(DataAttributes, "mycol", col)

    # Create
    new_id = DataAttributes.create({"dataAttributeName": "gt_label", "tenetId": "T1"})
    assert new_id is not None

    # Update
    assert DataAttributes.update(new_id, {"DataAttributeName": "gt_label2"}) is True

    # Findall
    res = DataAttributes.findall({"DataAttributeName": "gt_label2"})
    assert len(res) == 1

    # Distinct
    names = DataAttributes.get_all("DataAttributeName")
    assert "gt_label2" in names

    # FindOne
    one = DataAttributes.findOne(new_id)
    assert one["DataAttributeName"] == "gt_label2"

    # findDAVId
    did = DataAttributes.findDAVId({"DataAttributeName": "gt_label2"}, {"tenetId": "T1"})
    assert did == new_id

    # Delete
    DataAttributes.delete({"DataAttributeName": "gt_label2"})
    assert len(col.docs) == 0
