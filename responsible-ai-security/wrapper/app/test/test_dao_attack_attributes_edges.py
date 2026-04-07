import datetime

from src.dao.Security.AttackAttributesDb import AttackAttributes
from src.dao.Security.AttackAttributesValuesDb import AttackAttributesValues


class DummyResult:
    def __init__(self, inserted_id=None, acknowledged=True):
        self.inserted_id = inserted_id
        self.acknowledged = acknowledged


class DummyCollection:
    def __init__(self):
        self._docs = []

    def find(self, query, projection):
        if not query:
            return list(self._docs)
        key, val = next(iter(query.items()))
        return [doc for doc in self._docs if doc.get(key) == val]

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


def test_attackattributes_findall_and_crud(monkeypatch):
    dummy = DummyCollection()
    now = datetime.datetime.now()
    dummy.insert_one({
        "_id": 10,
        "id": 10,
        "AttackAttributeId": 10,
        "AttackAttributeName": "classifier",
        "CreatedDateTime": now,
        "LastUpdatedDateTime": now,
    })
    monkeypatch.setattr(AttackAttributes, "mycol", dummy)

    res = AttackAttributes.findall({"AttackAttributeName": "classifier"})
    assert len(res) == 1

    new_id = AttackAttributes.create({"attackAttributeName": "dataType"})
    assert new_id is not None
    ack = AttackAttributes.update(new_id, {"AttackAttributeName": "dtype"})
    assert ack is True
    AttackAttributes.delete({"_id": new_id})
    assert all(doc.get("_id") != new_id for doc in AttackAttributes.findall({}))


def test_attackattributesvalues_findall_edges(monkeypatch):
    dummy = DummyCollection()
    now = datetime.datetime.now()
    dummy.insert_one({
        "_id": 20,
        "id": 20,
        "AttackAttributeValuesId": 20,
        "AttackAttributeId": 10,
        "AttackId": 100,
        "AttackAttributeValues": "Sklearn",
        "CreatedDateTime": now,
        "LastUpdatedDateTime": now,
    })
    dummy.insert_one({
        "_id": 21,
        "id": 21,
        "AttackAttributeValuesId": 21,
        "AttackAttributeId": 10,
        "AttackId": 100,
        "AttackAttributeValues": "Tabular",
        "CreatedDateTime": now,
        "LastUpdatedDateTime": now,
    })
    monkeypatch.setattr(AttackAttributesValues, "mycol", dummy)

    # Find by different queries
    assert len(AttackAttributesValues.findall({"AttackId": 100})) == 2
    assert len(AttackAttributesValues.findall({"AttackAttributeValues": "Sklearn"})) == 1

    # Create/Update/Delete
    new_id = AttackAttributesValues.create({"attackAttributeId": 10, "attackId": 101, "attackAttributeValues": "Image"})
    assert new_id is not None
    ack = AttackAttributesValues.update(new_id, {"AttackAttributeValues": "ImageUpdated"})
    assert ack is True
    AttackAttributesValues.delete({"_id": new_id})
    assert all(doc.get("_id") != new_id for doc in AttackAttributesValues.findall({}))
