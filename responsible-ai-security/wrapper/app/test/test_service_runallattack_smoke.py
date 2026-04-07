import time

from src.service.service import Bulk
import src.service.service as service_mod


def test_runAllAttack_smoke(monkeypatch, tmp_path):
    # Stub heavy operations inside Bulk
    def no_op(*args, **kwargs):
        return None

    monkeypatch.setattr(Bulk, 'batchAttack', lambda payload: payload.get('batchId') or payload.get('batchid'))
    monkeypatch.setattr(Bulk, 'combinereport', lambda payload: {'combineReportFileId': 'ok'})

    # Stub Batch and ModelAttributes lookups used inside runAllAttack
    class AttrObj:
        def __init__(self, **kw):
            for k, v in kw.items():
                setattr(self, k, v)

    monkeypatch.setattr(service_mod.Batch, 'findall', lambda q: [
        {'BatchId': q.get('BatchId') or q.get('batchid'), 'ModelId': 1}
    ])
    monkeypatch.setattr(service_mod.Batch, 'update', lambda *a, **k: True)
    monkeypatch.setattr(service_mod.ModelAttributesValues, 'findall', lambda q: [AttrObj(ModelAttributeId=1, ModelAttributeValues=['AttackA'])])
    monkeypatch.setattr(service_mod.ModelAttributes, 'findall', lambda q: [{'ModelAttributeName': 'appAttacks'}])

    # Stub PDF conversion request
    class DummyResponse:
        def __init__(self):
            self.status_code = 200
            self.text = ''
        def json(self):
            return {}
    monkeypatch.setattr(service_mod.requests, 'post', lambda *a, **k: DummyResponse())

    payload = {
        'batchid': float(888.0),
        'dateTime': 'now'
    }

    # Should return the batch id or truthy result without raising
    result = Bulk.runAllAttack(payload)
    assert result is not None
