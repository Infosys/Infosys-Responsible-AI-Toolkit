'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import sys
import types
from fastapi.testclient import TestClient

# Lightweight stubs to avoid DB connections
if 'app.dao.SaveFileDB' not in sys.modules:
    m = types.ModuleType('app.dao.SaveFileDB')
    class FileStoreDb:  # noqa
        fs = types.SimpleNamespace(get=lambda *a, **k: types.SimpleNamespace(read=lambda: b"data"))
        @staticmethod
        def create(*a, **k): return 'id'
        @staticmethod
        def read_file(*a, **k): return {'data': b'data'}
    m.FileStoreDb = FileStoreDb
    sys.modules['app.dao.SaveFileDB'] = m
for _mod, _cls in [
    ('app.dao.AttackConfiguration', 'AttackConfiguration'),
    ('app.dao.AttackModel', 'AttackModel'),
    ('app.dao.JudgeModel', 'JudgeModel'),
    ('app.dao.TargetModel', 'TargetModel'),
    ('app.dao.RedTeamingReport', 'RedTeamingReport'),
]:
    if _mod not in sys.modules:
        mm = types.ModuleType(_mod)
        setattr(mm, _cls, type(_cls, (), { 'create': staticmethod(lambda *a, **k: 'id') }))
        sys.modules[_mod] = mm


def _client():
    from src.main import app
    return TestClient(app, raise_server_exceptions=False)


def test_models_endpoint_plain_and_enveloped():
    c = _client()
    r1 = c.get('/v1/redteaming/models')
    assert r1.status_code == 200
    body1 = r1.json()
    assert 'attack_model' in body1 and 'judge_model' in body1
    r2 = c.get('/v1/redteaming/models', headers={'X-API-Envelope':'true'})
    assert r2.status_code == 200
    body2 = r2.json()
    assert 'meta' in body2 and 'data' in body2 and 'attack_model' in body2['data']


def test_pair_endpoint_envelope():
    from unittest.mock import patch
    c = _client()
    with patch('app.service.service.InfosysRAI.GetRedteamListPair') as mock_get:
        mock_get.return_value = {'id':'x','jailbroken':0,'scores':[],'prompts':[],'responses':[]}
        r = c.post('/v1/redteaming/pair', json={
            'goal':'g', 'target_str':'t', 'attack_model':'a', 'target_model':'b'
        }, headers={'X-API-Envelope':'1'})
        assert r.status_code == 200
        b = r.json()
        assert 'meta' in b and 'data' in b and 'id' in b['data']


def test_report_endpoint_envelope():
    from unittest.mock import patch
    c = _client()
    with patch('app.service.service.InfosysRAI.download_report') as mock_dl:
        mock_dl.return_value = {'ok': True}
        r = c.post('/v1/redteaming/report', json={'reportId':'rid','redTeamingType':'PAIR'}, headers={'X-API-Envelope':'yes'})
        assert r.status_code == 200
        b = r.json()
        assert 'meta' in b and 'data' in b and b['data']['ok'] is True
