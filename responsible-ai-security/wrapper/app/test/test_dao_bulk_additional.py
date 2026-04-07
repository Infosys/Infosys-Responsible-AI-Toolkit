import os
import pytest

from src.dao.ModelAttributesDb import ModelAttributes
from src.dao.ModelAttributesValuesDb import ModelAttributesValues
from src.dao.DataAttributesDb import DataAttributes
from src.dao.DataAttributesValuesDb import DataAttributesValues
from src.dao.Security.SecReportDb import SecReport
from src.dao.Tenet import Tenet


@pytest.fixture(autouse=True)
def set_mongo_env(monkeypatch):
    monkeypatch.setenv('DB_TYPE', 'mongo')


def test_model_attributes_crud_and_lookup():
    # create
    mid = ModelAttributes.create({'modelAttributeName': 'modelFramework', 'tenetId': 'T1'})
    assert mid is not None
    # findOne
    rec = ModelAttributes.findOne(mid)
    assert rec['ModelAttributeName'] == 'modelFramework'
    # findall
    lst = ModelAttributes.findall({'ModelAttributeName': 'modelFramework'})
    assert any(x['ModelAttributeName'] == 'modelFramework' for x in lst)
    # get_all distinct
    distinct = ModelAttributes.get_all('ModelAttributeName')
    assert 'modelFramework' in distinct
    # update
    ok = ModelAttributes.update(mid, {'ModelAttributeName': 'modelFrameworkV2'})
    assert ok
    # findMAVId
    mav_id_lookup = ModelAttributes.findMAVId({'ModelAttributeName': 'modelFrameworkV2'}, {'tenetId': 'T1'})
    assert isinstance(mav_id_lookup, float) or mav_id_lookup is None
    # delete
    ModelAttributes.delete({'_id': mid})


def test_model_attributes_values_crud():
    # need a model attribute id
    aid = ModelAttributes.create({'modelAttributeName': 'useModelApi', 'tenetId': 'T2'})
    vid = ModelAttributesValues.create({'modelAttributeId': aid, 'modelId': 'M1', 'modelAttributeValues': 'No'})
    rec = ModelAttributesValues.findOne(vid)
    assert rec['ModelAttributeValues'] == 'No'
    # update
    assert ModelAttributesValues.update(vid, {'ModelAttributeValues': 'Yes'})
    # findall
    vals = ModelAttributesValues.findall({'ModelId': 'M1'})
    assert any(v['ModelAttributeValues'] in ['Yes','No'] for v in vals)
    # delete
    ModelAttributesValues.delete({'_id': vid})
    ModelAttributes.delete({'_id': aid})


def test_data_attributes_and_values_crud():
    da_id = DataAttributes.create({'dataAttributeName': 'groundTruthClassLabel', 'tenetId': 'T1'})
    dav_id = DataAttributesValues.create({'dataAttributeId': da_id, 'dataId': 'D1', 'dataAttributeValues': 'label'})
    # findOne
    rec = DataAttributesValues.findOne(dav_id)
    assert rec['DataAttributeValues'] == 'label'
    # update
    assert DataAttributesValues.update(dav_id, {'DataAttributeValues': 'label2'})
    # findall
    vals = DataAttributesValues.findall({'DataId': 'D1'})
    assert any(v['DataAttributeValues'] in ['label','label2'] for v in vals)
    # get_all distinct on attributes
    distinct = DataAttributes.get_all('DataAttributeName')
    assert 'groundTruthClassLabel' in distinct
    # findDAVId lookup
    did = DataAttributes.findDAVId({'DataAttributeName': 'groundTruthClassLabel'}, {'tenetId': 'T1'})
    assert isinstance(did, float) or did is None
    # delete
    DataAttributesValues.delete({'_id': dav_id})
    DataAttributes.delete({'_id': da_id})


def test_secreport_crud():
    rid = SecReport.create({'reportId': 'R1', 'batchId': 'B1', 'reportname': 'AttackX'})
    rec = SecReport.findOne('R1')
    assert rec['ReportName'] == 'AttackX.zip'
    # update
    assert SecReport.update('R1', {'ReportName': 'AttackY.zip'})
    # findall
    lst = SecReport.findall({'BatchId': 'B1'})
    assert any(r['ReportName'] in ['AttackX.zip','AttackY.zip'] for r in lst)
    # delete
    SecReport.delete({'_id': 'R1'})


def test_tenet_crud_and_findall():
    tid = Tenet.create({'tenetid': 'T1', 'tenetname': 'security', 'projectname': 'proj'})
    lst = Tenet.findall({'TenetName': 'Security'})
    assert isinstance(lst, list)
    # get_all distinct
    distinct = Tenet.get_all('TenetName')
    assert any(isinstance(n, str) for n in distinct)
    # update and delete
    assert Tenet.update(tid, {'ProjectName': 'proj2'})
    Tenet.delete({'_id': tid})
