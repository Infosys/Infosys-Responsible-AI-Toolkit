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

# Stub DAOs
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


def test_pair_batch_missing_required_columns():
    _prep_basic_daos()
    from src.main import app
    client = TestClient(app)
    # Build Excel missing 'target_str' column
    df = pd.DataFrame([
        {'goal': 'g', 'category': 'c'}
    ])
    bio = io.BytesIO(); df.to_excel(bio, index=False); bio.seek(0)
    with patch('app.service.service.InfosysRAI.dataAdditiontoDB', return_value=(bio, 'conf-id')),
         patch('pdfkit.from_file') as mock_pdf:
        def _fake_from_file(html_path, pdf_path, options=None):
            with open(pdf_path, 'wb') as fp:
                fp.write(b'%PDF-1.4')
        mock_pdf.side_effect = _fake_from_file
        import json as _json
        params = {'attack_model': 'am', 'target_model': 'tm', 'judge_model': 'jm'}
        r = client.post(
            '/v1/redteaming/pair/batch',
            files={'file': ('data.xlsx', bio.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')},
            data={'parameters': _json.dumps(params)}
        )
        assert r.status_code == 400
        body = r.json()
        assert 'detail' in body
