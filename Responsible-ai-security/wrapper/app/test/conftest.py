import os
import pytest
import gc

## Ensure tests use the in-memory mock DB and no telemetry
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("TEST_DB", "test_db")
os.environ.setdefault("TELEMETRY_FLAG", "False")
# Provide benign defaults to avoid real connections being attempted
os.environ.setdefault("MONGO_PATH", "mongodb://localhost:27017")
os.environ.setdefault("COSMOS_PATH", "")
os.environ.setdefault("DB_TYPE", "mongo")

# Hard patch pymongo at import time so any early imports use mongomock
try:
    from mongomock import MongoClient as _MockClient
    import pymongo as _pymongo
    _pymongo.MongoClient = _MockClient
except Exception:
    pass

# Prevent router endpoints from triggering real GC during requests (stability on Windows)
try:
    def _no_gc(*_a, **_k):
        return 0
    gc.collect = _no_gc  # type: ignore[attr-defined]
except Exception:
    pass

# Normalize working directory so tests relying on 'wrapper' path succeed
try:
    _here = os.path.abspath(os.path.dirname(__file__))
    _app_dir = os.path.dirname(_here)  # .../wrapper/app
    if os.path.basename(os.path.dirname(_app_dir)) == 'wrapper':
        os.chdir(_app_dir)
except Exception:
    pass

# Short-circuit heavy TF/Keras-dependent addModel helpers to avoid fatal DLL crashes
try:
    from test.service.addModelToMockDatabase import AddModel as _AddModel
    def _skip_heavy(*_args, **_kwargs):
        raise RuntimeError("Heavy TF/Keras path skipped for test stability")
    _AddModel.KerasClassifierImage = staticmethod(_skip_heavy)
    _AddModel.TensorFlowV2ClassifierImage = staticmethod(_skip_heavy)
except Exception:
    pass

@pytest.fixture(autouse=True)
def _mock_msal_confidential_client(monkeypatch):
    """Stub MSAL ConfidentialClientApplication to prevent network calls at import time.
    Some modules instantiate Azure clients at import; replacing MSAL with a noop avoids
    authority discovery against real endpoints.
    """
    try:
        import msal
        class _StubMSALApp:
            def __init__(self, *args, **kwargs):
                pass
            def acquire_token_for_client(self, *args, **kwargs):
                # Return a deterministic token structure
                return {"access_token": "stub-token", "expires_in": 3600}
        monkeypatch.setattr(msal, "ConfidentialClientApplication", _StubMSALApp)
    except Exception:
        pass
    # Provide benign Azure environment values to avoid None usage
    monkeypatch.setenv("AZURE_TENANT_ID", "stub-tenant")
    monkeypatch.setenv("AZURE_CLIENT_ID", "stub-client")
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "stub-secret")
    yield

@pytest.fixture(autouse=True)
def _mock_pymongo_client(monkeypatch):
    """Force any use of pymongo.MongoClient to use mongomock's client.
    This prevents background monitor threads and real network calls during tests.
    """
    try:
        from mongomock import MongoClient as MockClient
        import pymongo
        monkeypatch.setattr(pymongo, "MongoClient", MockClient)
    except Exception:
        # If mongomock is unavailable or import errors occur, fallback to a no-op stub
        class _StubClient:
            def __init__(self, *args, **kwargs):
                self._dbs = {}
            def __getitem__(self, name):
                return {}
        import pymongo
        monkeypatch.setattr(pymongo, "MongoClient", _StubClient)
    yield

@pytest.fixture(autouse=True)
def _disable_tqdm_monitor(monkeypatch):
    """Disable tqdm's background monitor thread to avoid Windows fatal exceptions.
    Some libraries start a tqdm monitor thread globally; turning off monitoring
    prevents thread lifecycle crashes under strict asyncio/TestClient usage.
    """
    try:
        import tqdm
        # Disable monitor thread creation
        tqdm.tqdm.monitor_interval = 0
        # If a monitor already exists, attempt to stop it
        try:
            from tqdm._monitor import TMonitor
            m = getattr(tqdm, 'monitor', None)
            if m and isinstance(m, TMonitor):
                m.exit()
        except Exception:
            pass
    except Exception:
        pass
    yield
