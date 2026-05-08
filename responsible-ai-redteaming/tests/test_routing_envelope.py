'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import io
import sys
import types
from fastapi.testclient import TestClient
from unittest.mock import patch

# Ensure lightweight FileStoreDb stub to avoid external FS
def _prep_basic_daos():
    # Minimal DAO stubs to avoid real DB and file systems
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


def test_models_info_envelope():
    _prep_basic_daos()
    from src.main import app
    client = TestClient(app)
    r = client.get('/v1/redteaming/models', headers={'X-API-Envelope': 'true'})
    assert r.status_code == 200
    body = r.json()
    assert 'meta' in body and 'data' in body
    assert 'path' in body['meta'] and body['meta']['path'].endswith('/v1/redteaming/models')


def test_report_endpoint_envelope():
    _prep_basic_daos()
    from src.main import app
    client = TestClient(app)
    # Patch download_report to return a JSON-serializable dict so envelope can be applied
    with patch('app.service.service.InfosysRAI.download_report', return_value={'ok': True, 'reportId': 'rid'}):
        r = client.post('/v1/redteaming/report', json={'reportId': 'rid', 'redTeamingType': 'PAIR'}, headers={'X-API-Envelope': 'true'})
        assert r.status_code == 200
        body = r.json()
        assert 'meta' in body and 'data' in body
        assert body['data'].get('ok') is True


def test_pair_models_endpoint_plain():
    _prep_basic_daos()
    from src.main import app
    client = TestClient(app)
    r = client.get('/v1/redteaming/models')
    assert r.status_code == 200
    body = r.json()
    assert 'attack_model' in body and 'judge_model' in body
