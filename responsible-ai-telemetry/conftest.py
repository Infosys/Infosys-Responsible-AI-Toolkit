import sys
import os
from unittest.mock import MagicMock

# Make project root importable
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load env if present (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass


# Mock heavy external modules globally
modules_to_mock = [
    "elasticsearch",
    "elasticsearch.exceptions",
    "dateutil",
    "dateutil.parser",
    "pytz",
]

for m in modules_to_mock:
    sys.modules[m] = MagicMock()

# Compatibility shim: some Starlette versions pass an `app=` kw to httpx.Client
# while newer httpx versions do not accept it. Accept and drop `app` to
# keep TestClient working across environments.
try:
    import httpx

    _httpx_client_init = httpx.Client.__init__

    def _httpx_init_shim(self, *args, **kwargs):
        kwargs.pop('app', None)
        return _httpx_client_init(self, *args, **kwargs)

    httpx.Client.__init__ = _httpx_init_shim
except Exception:
    # If httpx isn't available in this environment, tests that need it will
    # either mock it or fail later; suppress shim errors here.
    pass
