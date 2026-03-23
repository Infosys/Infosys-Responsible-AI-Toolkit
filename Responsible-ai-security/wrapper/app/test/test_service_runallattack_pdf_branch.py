import json
import datetime

import src.service.service as service_mod
from src.service.service import Bulk


def test_runAllAttack_pdf_branch(monkeypatch):
    # Stub Batch and attributes
    monkeypatch.setattr(service_mod.Batch, 'findall', lambda q: [{'BatchId': 9.0, 'ModelId': 1.0}])
    monkeypatch.setattr(service_mod.ModelAttributesValues, 'findall', lambda q: [type('O', (), {'ModelAttributeId': 1, 'ModelAttributeValues': ['FastGradientMethod']})()])
    monkeypatch.setattr(service_mod.ModelAttributes, 'findall', lambda q: [{'ModelAttributeName': 'appAttacks'}])

    # Stub Bulk internals
    monkeypatch.setattr(service_mod.Bulk, 'batchAttack', lambda payload: payload['batchId'])
    monkeypatch.setattr(service_mod.Bulk, 'combinereport', lambda payload: {'combineReportFileId': 'ok'})

    # PDF conversion request stub
    class DummyResp:
        def __init__(self):
            self.status_code = 200
            self.text = ''
        def json(self):
            return {}
    monkeypatch.setattr(service_mod.requests, 'post', lambda *a, **k: DummyResp())

    # Track updates
    updates = []
    monkeypatch.setattr(service_mod.Batch, 'update', lambda bid, val: updates.append((bid, val)) or True)

    res = Bulk.runAllAttack({'batchid': 9.0, 'dateTime': 'now'})
    assert res == 9.0
    # Ensure updates were called for status and timestamp
    assert any(u[1].get('Status') == 'Completed' for u in updates)
