import pytest

from src.dao.Html import Html
from src.dao.DataDb import Data
from src.dao.Batch import Batch
from src.dao.DataAttributesDb import DataAttributes
from src.dao.DataAttributesValuesDb import DataAttributesValues


@pytest.fixture(autouse=True)
def mongo_env(monkeypatch):
    monkeypatch.setenv('DB_TYPE', 'mongo')


def test_html_create_find_and_invalid_lookup():
    # create
    ok = Html.create({
        'BatchId': 1.0,
        'TenetId': 2.0,
        'HtmlFileId': 'H-1',
        'ReportName': 'R.html',
    })
    assert ok is True
    # find_one expect HtmlFileId
    hid1 = Html.find_one(1.0, 2.0)
    assert hid1 == 'H-1'
    # find behaves similarly
    hid2 = Html.find(1.0, 2.0)
    assert hid2 == 'H-1'
    # invalid types return None (handled internally with telemetry)
    assert Html.find_one(None, None) is None


def test_data_get_all_and_findall():
    id1 = Data.create({
        'sampleData': {'a': 1},
        'dataSetName': 'dsA',
        'userId': 'u1',
        'groundTruthImageFileId': 'g1',
    })
    id2 = Data.create({
        'sampleData': {'b': 2},
        'dataSetName': 'dsB',
        'userId': 'u2',
        'groundTruthImageFileId': 'g2',
    })
    assert id1 and id2
    # distinct get_all
    names = Data.get_all('DataSetName')
    assert 'dsA' in names and 'dsB' in names
    # findall by user
    lst = Data.findall({'UserId': 'u1'})
    assert any(x['UserId'] == 'u1' for x in lst)


def test_batch_create_update_findstatus_and_get_all():
    result = Batch.create({
        'userId': 'U',
        'modelId': 'M',
        'dataId': 'D',
    }, tenantId:=1.0)
    assert isinstance(result, dict) and 'BatchId' in result
    bid = result['BatchId']
    # update status
    assert Batch.update(bid, {'Status': 'Done'})
    assert Batch.findStatus(bid) == 'Done'
    # distinct list on TenetId
    tenets = Batch.get_all('TenetId')
    assert 1.0 in tenets


def test_data_attributes_values_createForBatchData():
    # Create a data attribute to reference
    da_id = DataAttributes.create({'dataAttributeName': 'attrX', 'tenetId': 'T'})
    dav_id = DataAttributesValues.createForBatchData({
        'DataAttributeId': da_id,
        'dataId': 'D9',
        'DataAttributevalues': 'valX',
    })
    rec = DataAttributesValues.findOne(dav_id)
    assert rec['DataAttributeValues'] == 'valX'
