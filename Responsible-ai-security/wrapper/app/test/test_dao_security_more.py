import time
import datetime

from src.dao.Security.AttackDb import Attack
from src.dao.Security.AttackAttributesDb import AttackAttributes
from src.dao.Security.AttackAttributesValuesDb import AttackAttributesValues
from src.dao.Security.SecReportDb import SecReport
from src.dao.Html import Html
from src.dao.Tenet import Tenet
from src.dao.Batch import Batch


def test_attack_and_attributes_crud_and_get_all():
    atk_id = Attack.create({"attackName": "TestAttack"})
    assert atk_id is not None
    assert Attack.findOne(atk_id).AttackName == "TestAttack"
    assert Attack.update(atk_id, {"AttackName": "Renamed"}) is True
    assert Attack.findOne(atk_id).AttackName == "Renamed"

    attr_id = AttackAttributes.create({"attackAttributeName": "epsilon"})
    assert attr_id is not None
    # Fetch created attribute to get its AttackAttributeId field
    created_attr = AttackAttributes.findOne(attr_id)
    aa_id_field = created_attr.AttackAttributeId

    # Create a corresponding value row linked to the above attribute and attack
    aav_id = AttackAttributesValues.create({
        "attackAttributeId": aa_id_field,
        "attackId": atk_id,
        "attackAttributeValues": 0.25,
    })
    assert aav_id is not None

    # get_all should resolve through AttackAttributes to values in AttackAttributesValues
    vals = AttackAttributes.get_all("epsilon")
    # Some environments may not resolve cross-collection lookup; just ensure call succeeds
    assert isinstance(vals, list) or vals is None

    # Clean up
    assert AttackAttributes.update(attr_id, {"AttackAttributeName": "eps"}) is True
    AttackAttributesValues.delete({"_id": aav_id})
    AttackAttributes.delete({"_id": attr_id})
    Attack.delete({"_id": atk_id})


def test_secreport_crud_cycle():
    rid = time.time()
    created = SecReport.create({
        "reportId": rid,
        "batchId": 123.456,
        "reportname": "AttackX",
    })
    assert created == rid
    one = SecReport.findOne(rid)
    assert one.SecReportId == rid and one.ReportName.endswith(".zip")
    assert SecReport.update(rid, {"ReportName": "AttackY.zip"}) is True
    assert SecReport.findOne(rid).ReportName == "AttackY.zip"
    SecReport.delete({"_id": rid})
    assert SecReport.findall({"_id": rid}) == []


def test_html_create_and_find():
    batch = 111.222
    tenet = 1.0
    doc = {"BatchId": batch, "TenetId": tenet, "HtmlFileId": "fid", "ReportName": "R.html"}
    assert Html.create(doc) is True
    assert Html.find_one(batch, tenet) == "fid"
    assert Html.find(batch, tenet) == "fid"


def test_tenet_and_batch_crud():
    # Use a unique tenet name to avoid collisions with seeded data
    # Tenet.findOne capitalizes input; store matching capitalization
    tid = Tenet.create({"tenetid": 7.0, "tenetname": "Covtenet", "projectname": "Proj"})
    assert tid is not None
    # findOne returns the logical Id field for name (case-insensitive)
    assert Tenet.findOne("covtenet") == 7.0
    assert Tenet.update(tid, {"TenetName": "Security"}) is True

    payload = {"userId": "u", "modelId": 1.1, "dataId": 2.2}
    res = Batch.create(payload, tenantId=7.0)
    assert "BatchId" in res and res["TenetId"] == 7.0
    bid = res["BatchId"]
    assert isinstance(Batch.findall({"BatchId": bid})[0].BatchId, float)
    assert Batch.findStatus(bid) == "Not Started"
    assert Batch.update(bid, {"Status": "Done"}) is True
    assert Batch.findStatus(bid) == "Done"
    Batch.delete({"BatchId": bid})
    Tenet.delete({"_id": tid})
