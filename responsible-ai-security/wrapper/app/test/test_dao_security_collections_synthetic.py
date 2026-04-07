import types
import datetime as dt


class FakeResult:
    def __init__(self, inserted_id=None, acknowledged=True):
        self.inserted_id = inserted_id
        self.acknowledged = acknowledged


class FakeCollection:
    def __init__(self):
        self.rows = []

    def find(self, query, _):
        def match(row, q):
            return all(row.get(k) == v for k, v in q.items())
        return [r for r in self.rows if match(r, query)]

    def find_one(self, query):
        found = self.find(query, {})
        return found[0] if found else None

    def insert_one(self, doc):
        self.rows.append(doc)
        return FakeResult(inserted_id=doc.get("_id"))

    def update_one(self, filt, new):
        doc = self.find_one(filt)
        if doc and "$set" in new:
            doc.update(new["$set"])
        return FakeResult(acknowledged=True)

    def delete_many(self, query):
        self.rows = [r for r in self.rows if not all(r.get(k) == v for k, v in query.items())]

    def distinct(self, key):
        return sorted({r.get(key) for r in self.rows if key in r})


class FakeDB:
    def __init__(self):
        self.cols = {}

    def __getitem__(self, name):
        if name not in self.cols:
            self.cols[name] = FakeCollection()
        return self.cols[name]


def test_attack_dao_crud(monkeypatch):
    import src.dao.Security.AttackDb as AD
    fake = FakeDB()
    monkeypatch.setattr(AD, "mydb", fake)
    monkeypatch.setattr(AD.Attack, "mycol", fake["Attack"])

    # create
    aid = AD.Attack.create({"attackName": "A1"})
    assert aid is not None

    # findall
    got = AD.Attack.findall({"AttackName": "A1"})
    assert len(got) == 1

    # get_all
    names = AD.Attack.get_all("AttackName")
    assert names == ["A1"]

    # update
    ok = AD.Attack.update(aid, {"isActive": "N"})
    assert ok is True

    # delete
    AD.Attack.delete({"_id": aid})
    assert AD.Attack.findall({"_id": aid}) == []


def test_attack_attributes_values_crud(monkeypatch):
    import src.dao.Security.AttackAttributesValuesDb as AAV
    fake = FakeDB()
    monkeypatch.setattr(AAV, "mydb", fake)
    monkeypatch.setattr(AAV.AttackAttributesValues, "mycol", fake["AttackAttributesValues"])

    # create
    vid = AAV.AttackAttributesValues.create({
        "attackAttributeId": 2,
        "attackId": 1,
        "attackAttributeValues": "Sklearn",
    })
    assert vid is not None

    # findall + findOne
    got = AAV.AttackAttributesValues.findall({"AttackId": 1})
    assert len(got) == 1
    one = AAV.AttackAttributesValues.findOne(vid)
    assert one["AttackId"] == 1

    # update
    ok = AAV.AttackAttributesValues.update(vid, {"isActive": "N"})
    assert ok is True

    # delete
    AAV.AttackAttributesValues.delete({"_id": vid})
    assert AAV.AttackAttributesValues.findall({"_id": vid}) == []


def test_attack_attributes_crud_and_get_all(monkeypatch):
    import src.dao.Security.AttackAttributesDb as AAD
    fake = FakeDB()
    monkeypatch.setattr(AAD, "mydb", fake)
    monkeypatch.setattr(AAD.AttackAttributes, "mycol", fake["AttackAttributes"])

    # create
    aid = AAD.AttackAttributes.create({"attackAttributeName": "targetDataType"})
    assert aid is not None

    # seed values for get_all to look into AttackAttributesValues with matching id
    vals = fake["AttackAttributesValues"]
    vals.insert_one({"AttackAttributeId": aid, "AttackAttributeValues": "Tabular"})

    # findall
    got = AAD.AttackAttributes.findall({"AttackAttributeName": "targetDataType"})
    assert len(got) == 1
    # get_all resolves values via mydb
    resolved = AAD.AttackAttributes.get_all("targetDataType")
    assert resolved == ["Tabular"]

    # update
    ok = AAD.AttackAttributes.update(aid, {"isActive": "Y"})
    assert ok is True

    # delete
    AAD.AttackAttributes.delete({"_id": aid})
    assert AAD.AttackAttributes.findall({"_id": aid}) == []


def test_secreport_crud(monkeypatch):
    import src.dao.Security.SecReportDb as SR
    fake = FakeDB()
    monkeypatch.setattr(SR, "mydb", fake)
    monkeypatch.setattr(SR.SecReport, "mycol", fake["SecReport"])

    rid = SR.SecReport.create({"reportId": 123, "batchId": 9, "reportname": "ModelA"})
    assert rid == 123

    rows = SR.SecReport.findall({"BatchId": 9})
    assert len(rows) == 1

    ok = SR.SecReport.update(123, {"LastUpdatedDateTime": dt.datetime.now()})
    assert ok is True

    one = SR.SecReport.findOne(123)
    assert one["SecReportId"] == 123

    SR.SecReport.delete({"_id": 123})
    assert SR.SecReport.findall({"_id": 123}) == []
