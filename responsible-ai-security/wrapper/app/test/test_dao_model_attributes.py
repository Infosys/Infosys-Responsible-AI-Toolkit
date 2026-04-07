import time
import pytest

from src.dao.ModelAttributesDb import ModelAttributes


def test_modelattributes_crud_and_distinct():
    tenet = int(time.time() * 1000)

    _id = ModelAttributes.create({
        'modelAttributeName': 'modelFrameworkV2',
        'tenetId': tenet,
    })
    assert _id is not None

    items = ModelAttributes.findall({'TenetId': tenet})
    assert isinstance(items, list) and len(items) == 1

    one = ModelAttributes.findOne(_id)
    assert one['_id'] == _id and one['ModelAttributeName'] == 'modelFrameworkV2'

    ok = ModelAttributes.update(_id, {'ModelAttributeName': 'mf_v2'})
    assert ok is True
    one2 = ModelAttributes.findOne(_id)
    assert one2['ModelAttributeName'] == 'mf_v2'

    names = ModelAttributes.get_all('ModelAttributeName')
    assert 'mf_v2' in names

    resolved = ModelAttributes.findMAVId({'ModelAttributeName': 'mf_v2'}, {'tenetId': tenet})
    assert resolved == _id

    ModelAttributes.delete({'TenetId': tenet})
    items_after = ModelAttributes.findall({'TenetId': tenet})
    assert items_after == []
