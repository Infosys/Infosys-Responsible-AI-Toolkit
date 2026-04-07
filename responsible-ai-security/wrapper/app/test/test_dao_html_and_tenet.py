import time
import pytest

from src.dao.Html import Html
from src.dao.Tenet import Tenet


def test_html_create_find_and_update_delete():
    # Create a document
    doc = {
        'HtmlId': time.time(),
        'BatchId': float(123.0),
        'TenetId': float(456.0),
        'ReportName': 'M.zip',
        'HtmlFileId': 'file-1',
        'ContentType': 'application/zip',
    }
    assert Html.create(doc) is True

    # find_one/find
    fid1 = Html.find_one(doc['BatchId'], doc['TenetId'])
    assert fid1 == 'file-1'
    fid2 = Html.find(doc['BatchId'], doc['TenetId'])
    assert fid2 == 'file-1'

    # Update via underlying collection
    Html.collection.update_one({'BatchId': doc['BatchId'], 'TenetId': doc['TenetId']}, {'$set': {'HtmlFileId': 'file-2'}})
    fid3 = Html.find_one(doc['BatchId'], doc['TenetId'])
    assert fid3 == 'file-2'

    # Delete and ensure no match remains
    Html.collection.delete_many({'BatchId': doc['BatchId'], 'TenetId': doc['TenetId']})
    remaining = list(Html.collection.find({'BatchId': doc['BatchId'], 'TenetId': doc['TenetId']}))
    assert remaining == []


def test_tenet_crud_and_distinct():
    tenet_id = int(time.time() * 1000)

    unique_name = f"Coverage{tenet_id}"
    _id = Tenet.create({'tenetid': tenet_id, 'tenetname': unique_name, 'projectname': 'projX'})
    assert _id is not None

    # findall
    items = Tenet.findall({'Id': tenet_id})
    assert isinstance(items, list) and len(items) == 1

    # findOne by name returns Id
    found_id = Tenet.findOne(unique_name)
    assert found_id == tenet_id

    # update name and project
    assert Tenet.update(_id, {'TenetName': 'Safety'}) is True
    # get_all distinct names includes updated
    names = Tenet.get_all('TenetName')
    assert 'Safety' in names

    # delete
    Tenet.delete({'Id': tenet_id})
    after = Tenet.findall({'Id': tenet_id})
    assert after == []
