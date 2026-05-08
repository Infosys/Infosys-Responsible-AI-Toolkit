import time
import pytest

from src.dao.ModelAttributesValuesDb import ModelAttributesValues


def test_modelattributesvalues_crud_and_batch_create():
    # Create initial record
    model_attr_id = int(time.time() * 1000)
    model_id = model_attr_id + 1
    _id = ModelAttributesValues.create({
        'modelAttributeId': model_attr_id,
        'modelId': model_id,
        'modelAttributeValues': 'Yes',
    })
    assert _id is not None

    one = ModelAttributesValues.findOne(_id)
    assert one['_id'] == _id and one['ModelId'] == model_id

    ok = ModelAttributesValues.update(_id, {'ModelAttributeValues': 'No'})
    assert ok is True

    items = ModelAttributesValues.findall({'ModelId': model_id})
    assert isinstance(items, list) and len(items) >= 1

    # createForBatchData smoke
    data_id = model_id + 100
    ModelAttributesValues.createForBatchData({
        'ModelAttributeId': model_attr_id,
        'ModelAttributevalues': 'X',
        'dataId': data_id,
    })
    items2 = ModelAttributesValues.findall({'DataId': data_id})
    assert isinstance(items2, list)

    # Cleanup
    ModelAttributesValues.delete({'ModelId': model_id})
    ModelAttributesValues.delete({'DataId': data_id})
