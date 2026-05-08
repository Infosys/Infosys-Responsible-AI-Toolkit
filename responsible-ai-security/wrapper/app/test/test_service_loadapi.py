import io
import json
import types

import pytest

import src.service.service as svc
from src.service.service import Bulk, Infosys


@pytest.fixture(autouse=True)
def set_mongo_env(monkeypatch):
    monkeypatch.setenv('DB_TYPE', 'mongo')


def test_loadApi_happy_path(monkeypatch):
    # Fake DB with no 'Attack' collection triggers population
    class FakeDB:
        def list_collection_names(self):
            return []

    monkeypatch.setattr(svc.DB, 'connect', lambda: FakeDB())
    # Fake attack.json content
    fake_attacks = [{"attackName": "Boundary"}, {"attackName": "Deepfool"}]

    import builtins as _b
    real_open = _b.open

    def fake_open(path, mode='r', *a, **k):
        if isinstance(path, str) and path.endswith('src/config/attack.json') and 'r' in mode:
            return io.StringIO(json.dumps(fake_attacks))
        return real_open(path, mode, *a, **k)

    monkeypatch.setattr(_b, 'open', fake_open)

    calls = []
    monkeypatch.setattr(Infosys, 'addAttack', lambda attack: calls.append(attack))

    Bulk.loadApi()
    assert len(calls) == len(fake_attacks)


def test_loadApi_noop_when_collection_exists(monkeypatch):
    class FakeDB:
        def list_collection_names(self):
            return ['Attack']

    monkeypatch.setattr(svc.DB, 'connect', lambda: FakeDB())

    # addAttack should not be called
    monkeypatch.setattr(Infosys, 'addAttack', lambda attack: (_ for _ in ()).throw(AssertionError('should not be called')))  # raises if invoked

    Bulk.loadApi()  # should not raise


def test_loadApi_error_path(monkeypatch):
    class FakeDB:
        def list_collection_names(self):
            return []

    monkeypatch.setattr(svc.DB, 'connect', lambda: FakeDB())
    # Force open to raise
    import builtins as _b
    def boom(*a, **k):
        raise FileNotFoundError('no file')
    monkeypatch.setattr(_b, 'open', boom)

    # Should swallow and not raise
    Bulk.loadApi()