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
import pandas as pd

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

# Prepare minimal DAO stub
if 'app.dao.SaveFileDB' not in sys.modules:
    m = types.ModuleType('app.dao.SaveFileDB')
    class FileStoreDb:  # noqa
        fs = types.SimpleNamespace(get=lambda *a, **k: types.SimpleNamespace(read=lambda: b"data"))
        @staticmethod
        def create(*a, **k):
            return 'id'
        @staticmethod
        def read_file(*a, **k):
            return {'data': b'data'}
    m.FileStoreDb = FileStoreDb
    sys.modules['app.dao.SaveFileDB'] = m


def test_tap_batch_missing_required_columns():
    _prep_basic_daos()
    from src.main import app
    client = TestClient(app)
    # Build Excel missing 'goal' column
    df = pd.DataFrame([
        {'target_str': 't', 'category': 'c'}
    ])
    bio = io.BytesIO(); df.to_excel(bio, index=False); bio.seek(0)
    with patch('app.service.service.InfosysRAI.dataAdditiontoDB', return_value=(bio, 'conf-id')):
        import json as _json
        params = {'attack_model': 'am', 'target_model': 'tm', 'evaluator_model': 'em'}
        r = client.post(
            '/v1/redteaming/tap/batch',
            files={'file': ('data.xlsx', bio.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')},
            data={'parameters': _json.dumps(params)}
        )
        assert r.status_code == 400
        body = r.json()
        assert 'detail' in body
