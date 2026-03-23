import time
import pytest

from src.dao.DataDb import Data as DataDb


def test_datadb_create_find_update_delete_and_distinct():
    # Create a document with required fields for Data
    values = {
        'sampleData': {'a': 1},
        'dataSetName': 'demo',
        'userId': 'user-1',
        'groundTruthImageFileId': 'file-gt',
    }
    _id = DataDb.create(values)
    assert _id is not None

    # findOne returns the saved document
    doc = DataDb.findOne(_id)
    assert doc is not None and doc.get('DataSetName') == 'demo'

    # findall via UserId
    items = DataDb.findall({'UserId': 'user-1'})
    assert isinstance(items, list) and len(items) >= 1

    # update
    assert DataDb.update(_id, {'DataSetName': 'newdemo'}) is True

    # get_all distinct
    names = DataDb.get_all('DataSetName')
    assert 'newdemo' in names

    # delete
    DataDb.delete({'_id': _id})
    after = DataDb.findall({'_id': _id})
    assert after == []
