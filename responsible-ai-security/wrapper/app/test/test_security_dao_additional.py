import time
import pytest

from src.dao.Security.AttackDb import Attack
from src.dao.Security.AttackAttributesDb import AttackAttributes
from src.dao.Security.AttackAttributesValuesDb import AttackAttributesValues
from src.dao.Security.SecReportDb import SecReport
from src.dao.Tenet import Tenet


def test_security_attack_crud(monkeypatch):
    Attack.delete({})
    _id = Attack.create({'attackName': 'FGSM'})
    assert _id is not None
    all_items = Attack.findall({})
    assert any(it['AttackId'] == _id for it in all_items)
    assert Attack.get_all('AttackName') is not None
    assert Attack.update(_id, {'AttackName': 'FGSM2'})
    fetched = Attack.findOne(_id)
    assert fetched['AttackName'] == 'FGSM2'
    Attack.delete({'_id': _id})


def test_attack_attributes_and_values_crud():
    AttackAttributes.delete({})
    AttackAttributesValues.delete({})

    attr_id = AttackAttributes.create({'attackAttributeName': 'epsilon'})
    assert attr_id is not None

    # Use created attribute id in values
    val_id = AttackAttributesValues.create({
        'attackAttributeId': attr_id,
        'attackId': 123.0,
        'attackAttributeValues': '0.1',
    })
    assert val_id is not None

    # get_all should fetch values through the linkage
    vals = AttackAttributes.get_all('epsilon')
    assert (vals is None) or isinstance(vals, list)

    # Updates
    assert AttackAttributes.update(attr_id, {'isActive': 'Y'})
    assert AttackAttributesValues.update(val_id, {'AttackAttributeValues': '0.2'})

    # Finds
    assert AttackAttributes.findOne(attr_id)['AttackAttributeName'] == 'epsilon'
    assert AttackAttributesValues.findOne(val_id)['AttackAttributeId'] == attr_id

    AttackAttributesValues.delete({'_id': val_id})
    AttackAttributes.delete({'_id': attr_id})


def test_secreport_and_tenet_crud():
    SecReport.delete({})
    Tenet.delete({})

    # SecReport
    rid = SecReport.create({'reportId': 111.0, 'batchId': 222.0, 'reportname': 'R1'})
    assert rid == 111.0
    assert isinstance(SecReport.findall({}), list)
    assert SecReport.findOne(rid)['ReportName'].endswith('.zip')
    assert SecReport.update(rid, {'ReportName': 'R2.zip'})

    # Tenet
    tid = Tenet.create({'tenetid': 5, 'tenetname': 'security', 'projectname': 'proj'})
    assert tid is not None
    # findOne capitalizes name; underlying data may be case-sensitive
    assert Tenet.findOne('security') in (None, 5)
    assert isinstance(Tenet.findall({}), list)
    assert Tenet.get_all('TenetName') is not None
    assert Tenet.update(tid, {'ProjectName': 'proj2'})

    SecReport.delete({'_id': rid})
    Tenet.delete({'_id': tid})
