import time
import pytest

from src.dao.Security.AttackDb import Attack
from src.dao.Security.AttackAttributesDb import AttackAttributes
from src.dao.Security.AttackAttributesValuesDb import AttackAttributesValues
from src.dao.Security.SecReportDb import SecReport


def test_attack_and_attributes_crud_flow():
    # Create base Attack
    atk_id = Attack.create({'attackName': 'FGSM2'})
    assert atk_id is not None

    # Create an Attribute and link a value to the attack
    attr_id = AttackAttributes.create({'attackAttributeName': 'eps'})
    assert attr_id is not None

    val_id = AttackAttributesValues.create({
        'attackAttributeId': attr_id,
        'attackId': atk_id,
        'attackAttributeValues': '0.2',
    })
    assert val_id is not None

    # findOne/findall
    atk_one = Attack.findOne(atk_id)
    assert atk_one['AttackName'] == 'FGSM2'
    attr_one = AttackAttributes.findOne(attr_id)
    assert attr_one['AttackAttributeName'] == 'eps'
    val_one = AttackAttributesValues.findOne(val_id)
    assert val_one['AttackId'] == atk_id

    # update values
    assert Attack.update(atk_id, {'AttackName': 'FGSM3'}) is True
    assert AttackAttributes.update(attr_id, {'AttackAttributeName': 'eps_new'}) is True
    assert AttackAttributesValues.update(val_id, {'AttackAttributeValues': '0.3'}) is True

    # Prefer direct lookup via AttackAttributesValues to avoid coupling
    vals = AttackAttributesValues.findall({'AttackAttributeId': attr_id})
    assert isinstance(vals, list) and len(vals) >= 1

    # Cleanup
    AttackAttributesValues.delete({'AttackId': atk_id})
    AttackAttributes.delete({'_id': attr_id})
    Attack.delete({'_id': atk_id})


def test_secreport_crud_flow():
    # Create SecReport
    rid = int(time.time() * 1000)
    batch_id = rid + 1
    sr_id = SecReport.create({'reportId': rid, 'batchId': batch_id, 'reportname': 'AttackY'})
    assert sr_id == rid

    one = SecReport.findOne(rid)
    assert one['ReportName'] == 'AttackY.zip' and one['BatchId'] == batch_id

    assert SecReport.update(rid, {'ReportName': 'R2.zip'}) is True

    items = SecReport.findall({'BatchId': batch_id})
    assert isinstance(items, list) and len(items) == 1

    SecReport.delete({'BatchId': batch_id})
    items_after = SecReport.findall({'BatchId': batch_id})
    assert items_after == []
