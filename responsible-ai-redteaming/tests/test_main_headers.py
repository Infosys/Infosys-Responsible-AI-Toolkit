'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from fastapi.testclient import TestClient
import os
import sys
import types

def _prep_basic_daos():
    class _Stub:
        @staticmethod
        def create(*a, **k):
            return 'id'
        fs = types.SimpleNamespace(get=lambda *a, **k: types.SimpleNamespace(read=lambda: b"data"))
        @staticmethod
        def read_file(*a, **k):
            return {'data': b'data'}

    for mod_name, cls_name in [
        ('app.dao.SaveFileDB', 'FileStoreDb'),
        ('app.dao.AttackConfiguration', 'AttackConfiguration'),
        ('app.dao.AttackModel', 'AttackModel'),
        ('app.dao.JudgeModel', 'JudgeModel'),
        ('app.dao.TargetModel', 'TargetModel'),
        ('app.dao.RedTeamingReport', 'RedTeamingReport'),
    ]:
        if mod_name not in sys.modules:
            m = types.ModuleType(mod_name)
            setattr(m, cls_name, _Stub)
            sys.modules[mod_name] = m


def test_request_id_header_present():
    _prep_basic_daos()
    from src.main import app
    client = TestClient(app)
    r = client.get('/v1/redteaming/models')
    assert r.status_code == 200
    assert 'X-Request-ID' in r.headers and r.headers['X-Request-ID']


def test_csp_header_present():
    # Ensure security headers enabled
    os.environ['RAI_ENABLE_SECURITY_HEADERS'] = '1'
    from importlib import reload
    import src.main as main
    reload(main)
    client = TestClient(main.app)
    r = client.get('/v1/redteaming/models')
    assert r.status_code == 200
    assert 'Content-Security-Policy' in r.headers


def test_null_origin_with_auth_blocked():
    _prep_basic_daos()
    from src.main import app
    client = TestClient(app)
    r = client.get('/v1/redteaming/models', headers={'Origin': 'null', 'Authorization': 'Bearer x'})
    assert r.status_code == 403
    assert r.text == 'Null origin not allowed with credentials'


def test_invalid_url_path_404():
    _prep_basic_daos()
    from src.main import app
    client = TestClient(app)
    r = client.get('/v2/other')
    assert r.status_code == 404
