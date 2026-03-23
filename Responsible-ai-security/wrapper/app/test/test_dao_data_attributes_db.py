import time
import pytest

from src.dao.DataAttributesDb import DataAttributes


def test_dataattributes_create_find_update_delete():
    # Use a unique tenet id to isolate this test's records
    tenet = int(time.time() * 1000)

    # Create a record
    _id = DataAttributes.create({
        'dataAttributeName': 'groundtruthlabel',
        'tenetId': tenet,
    })
    assert _id is not None

    # findall by TenetId
    items = DataAttributes.findall({'TenetId': tenet})
    assert isinstance(items, list) and len(items) == 1
    assert items[0]['DataAttributeName'] == 'groundtruthlabel'

    # findOne by id
    one = DataAttributes.findOne(_id)
    assert one['_id'] == _id and one['TenetId'] == tenet

    # update DataAttributeName
    ok = DataAttributes.update(_id, {'DataAttributeName': 'gt_label'})
    assert ok is True
    one2 = DataAttributes.findOne(_id)
    assert one2['DataAttributeName'] == 'gt_label'

    # get_all distinct names should include our updated name
    names = DataAttributes.get_all('DataAttributeName')
    assert 'gt_label' in names

    # findDAVId should resolve id by name and TenetId
    resolved = DataAttributes.findDAVId({'DataAttributeName': 'gt_label'}, {'tenetId': tenet})
    assert resolved == _id

    # delete all records for our TenetId
    DataAttributes.delete({'TenetId': tenet})
    items_after = DataAttributes.findall({'TenetId': tenet})
    assert items_after == []
