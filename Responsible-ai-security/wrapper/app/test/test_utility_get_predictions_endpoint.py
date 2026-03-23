import json

from src.service.utility import Utility
import src.service.utility as utility_mod


def test_getPredictionsFromEndpoint_batch_and_single(monkeypatch):
    # Stub requests.post to return a simple response-like object
    class DummyResponse:
        def __init__(self, data):
            self._data = data
            self.text = data
        def json(self):
            return json.loads(self._data) if isinstance(self._data, str) else self._data

    def fake_post(url, request_data, headers=None):
        data = json.loads(request_data)
        # If provided data is 2D list (batch), return list predictions
        vals = list(data.values())[0]
        if isinstance(vals, list) and len(vals) > 1 and isinstance(vals[0], list):
            return DummyResponse(json.dumps({'prediction': [0.6 for _ in vals]}))
        return DummyResponse(json.dumps({'prediction': 0.7}))

    monkeypatch.setattr(utility_mod.requests, 'post', fake_post)

    # Single item path
    single = Utility.getPredictionsFromEndpoint({
        'api': 'http://api',
        'data': 'x',
        'prediction': 'prediction',
        'batch': False,
        'train_data': __import__('numpy').array([1, 2, 3])
    })
    assert single is not None

    # Batch path
    batch = Utility.getPredictionsFromEndpoint({
        'api': 'http://api',
        'data': 'x',
        'prediction': 'prediction',
        'batch': True,
        'train_data': __import__('numpy').array([[1, 2, 3], [4, 5, 6]])
    })
    assert batch is not None
