'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import os
import sys
import types
import json
from fastapi.testclient import TestClient
import importlib
import pytest

os.environ.setdefault('RAI_ENABLE_RATE_LIMIT', '0')  # disable rate limit for baseline tests

def _prepare_stubs():
    """Insert lightweight stub modules for DAOs & heavy utilities before importing service/main.
    This prevents import-time DB connection attempts during test monkeypatching.
    Safe to call multiple times (idempotent).
    """
    import types
    dao_modules = {
        'app.dao.SaveFileDB': 'FileStoreDb',
        'app.dao.AttackConfiguration': 'AttackConfiguration',
        'app.dao.AttackModel': 'AttackModel',
        'app.dao.JudgeModel': 'JudgeModel',
        'app.dao.TargetModel': 'TargetModel',
        'app.dao.RedTeamingReport': 'RedTeamingReport'
    }
    for mod_name, cls_name in dao_modules.items():
        if mod_name not in sys.modules:
            stub = types.ModuleType(mod_name)
            class _Stub:
                fs = types.SimpleNamespace(get=lambda *a, **k: types.SimpleNamespace(read=lambda: b""))
                def __init__(self, *a, **kw):
                    # Empty stub constructor for DAO classes in tests
                    pass
                @staticmethod
                def create(*a, **kw):
                    return 'stub-id'
                def addReportToDB(self, *a, **kw):
                    return 'stub-report-id'
                def addingReportToDB(self, *a, **kw):
                    return None
                @staticmethod
                def read_file(*a, **kw):
                    return {'data': b''}
            setattr(stub, cls_name, _Stub)
            sys.modules[mod_name] = stub
    if 'app.utility.multifaceted' not in sys.modules:
        mstub = types.ModuleType('app.utility.multifaceted')
        class MultifacetedEvaluation:  # noqa
            def __init__(self, *a, **kw):
                # Empty stub constructor for MultifacetedEvaluation in tests
                pass
        mstub.MultifacetedEvaluation = MultifacetedEvaluation
        sys.modules['app.utility.multifaceted'] = mstub


def _build_client():
    for mod in list(sys.modules):
        if (
            mod.startswith('src.main') or
            mod.startswith('src.app.routing.routers') or
            mod.startswith('src.app.service.service')
        ):
            sys.modules.pop(mod, None)
    _prepare_stubs()
    main_mod = importlib.import_module('src.main')
    return TestClient(main_mod.app, raise_server_exceptions=False)



def test_models_endpoint_legacy():
    client = _build_client()
    r = client.get('/v1/redteaming/models')
    assert r.status_code == 200
    body = r.json()
    assert 'attack_model' in body and 'judge_model' in body


def test_models_endpoint_enveloped():
    client = _build_client()
    r = client.get('/v1/redteaming/models', headers={'X-API-Envelope': 'true'})
    assert r.status_code == 200
    body = r.json()
    assert 'meta' in body and 'data' in body
    assert body['meta']['status'] == 200
    assert 'attack_model' in body['data']



def test_pair_endpoint_enveloped(monkeypatch):
    _prepare_stubs()
    from src.app.routing import routers as routers_module

    def fake_pair(payload):
        return {'scores': ["1", "10"], 'prompts': ['p1','p2'], 'responses': ['r1','r2']}

    # Patch the symbol referenced by the endpoint
    monkeypatch.setattr(routers_module.InfosysRAI, 'GetRedteamListPair', staticmethod(fake_pair))

    client = _build_client()
    payload = { 'goal': 'g', 'target_str': 't', 'category': 'c' }
    r = client.post('/v1/redteaming/pair', json=payload, headers={'X-API-Envelope': 'yes'})
    assert r.status_code == 200
    j = r.json()
    assert 'meta' in j and 'data' in j
    assert j['data']['scores'][1] == '10'




# In tests/test_api_endpoints.py::test_pair_endpoint_legacy
def test_pair_endpoint_legacy(monkeypatch):
    _prepare_stubs()
    from src.app.routing import routers as routers_module

    def fake_pair(payload):
        return {'scores': ["5"], 'prompts': ['p'], 'responses': ['r']}

    # Patch the symbol the router actually uses:
    monkeypatch.setattr(routers_module.InfosysRAI, 'GetRedteamListPair', staticmethod(fake_pair))

    client = _build_client()
    payload = { 'goal': 'g', 'target_str': 't', 'category': 'c' }
    r = client.post('/v1/redteaming/pair', json=payload)
    assert r.status_code == 200
    assert r.json()['scores'][0] == '5'




@pytest.mark.parametrize('header_val', ['true','1','on','yes'])
def test_envelope_header_variants(monkeypatch, header_val):
    _prepare_stubs()
    from src.app.routing import routers as routers_module
    monkeypatch.setattr(routers_module.InfosysRAI, 'GetRedteamListPair', staticmethod(lambda p: {'scores': []}))
    client = _build_client()
    payload = { 'goal': 'g', 'target_str': 't', 'category': 'c' }
    r = client.post('/v1/redteaming/pair', json=payload, headers={'X-API-Envelope': header_val})
    assert r.status_code == 200
    assert 'meta' in r.json()


def test_global_exception_legacy(monkeypatch):
    _prepare_stubs()
    from src.app.routing import routers as routers_module
    def boom(payload):
        raise RuntimeError("forced boom")
    monkeypatch.setattr(routers_module.InfosysRAI, 'GetRedteamListPair', staticmethod(boom))
    client = _build_client()
    payload = { 'goal': 'g', 'target_str': 't', 'category': 'c' }
    r = client.post('/v1/redteaming/pair', json=payload)
    assert r.status_code == 500
    body = r.json()
    assert body.get('error') == 'Internal Server Error'
    assert 'timestamp' in body
    assert 'error_id' in body


def test_global_exception_enveloped(monkeypatch):
    _prepare_stubs()
    from src.app.routing import routers as routers_module
    def boom(payload):
        raise RuntimeError("forced boom")
    monkeypatch.setattr(routers_module.InfosysRAI, 'GetRedteamListPair', staticmethod(boom))
    client = _build_client()
    payload = { 'goal': 'g', 'target_str': 't', 'category': 'c' }
    r = client.post('/v1/redteaming/pair', json=payload, headers={'X-API-Envelope': 'true'})
    assert r.status_code == 500
    body = r.json()
    assert 'meta' in body and 'data' in body
    assert body['meta']['status'] == 500
    assert body['data'].get('error') == 'Internal Server Error'
    assert 'error_id' in body['data']


def test_rate_limit_headers_and_429(monkeypatch):
    os.environ['RAI_ENABLE_RATE_LIMIT'] = '1'
    os.environ['RAI_RATE_LIMIT_PER_MINUTE'] = '3'
    _prepare_stubs()
    from src.app.routing import routers as routers_module
    monkeypatch.setattr(routers_module.InfosysRAI, 'GetRedteamListPair', staticmethod(lambda p: {'scores': []}))
    client = _build_client()
    payload = { 'goal': 'g', 'target_str': 't', 'category': 'c' }
    for _ in range(3):
        res = client.post('/v1/redteaming/pair', json=payload)
        assert res.status_code == 200
        assert 'X-RateLimit-Limit' in res.headers
        assert 'X-RateLimit-Remaining' in res.headers
    res_over = client.post('/v1/redteaming/pair', json=payload, headers={'X-API-Envelope':'1'})
    assert res_over.status_code == 429
    body = res_over.json()
    if 'meta' in body:
        assert body['meta']['status'] == 429
    os.environ['RAI_ENABLE_RATE_LIMIT'] = '0'



def test_pair_batch_endpoint_basic(monkeypatch, tmp_path):
    """Exercise the /v1/redteaming/pair/batch endpoint with a minimal in-memory Excel file.
    Stubs out heavy service methods and pdfkit to avoid external side effects.
    """
    import io
    import pandas as pd
    # Ensure rate limit off for this test
    os.environ['RAI_ENABLE_RATE_LIMIT'] = '0'
    _prepare_stubs()
    from src.app.service import service as service_module
    import src.app.routing.routers as routers_module
    # Stub pair call to return a jailbreak score for first row only
    def fake_pair(payload):
        goal = payload.get('goal')
        if goal == 'g1':
            return {'scores': ['10'], 'prompts': ['p1'], 'responses': ['r1']}
        return {'scores': ['1'], 'prompts': ['p2'], 'responses': ['r2']}
    monkeypatch.setattr(service_module.InfosysRAI, 'GetRedteamListPair', staticmethod(fake_pair))
    # Stub HTML report generator to return constant and avoid heavy rendering
    monkeypatch.setattr(routers_module, 'generate_html_report_pair', lambda data: '<html></html>')
    # Stub DB persistence methods (already stubbed, but ensure attributes exist on stub instance)
    monkeypatch.setattr(service_module.InfosysRAI, 'dataAdditiontoDB', staticmethod(lambda params, file: (io.BytesIO(file.file.read()), 'attack-conf-id')))
    monkeypatch.setattr(service_module.InfosysRAI, 'addReportToDB', staticmethod(lambda reportFile, name: 'rep-id'))
    monkeypatch.setattr(service_module.InfosysRAI, 'addingReportToDB', staticmethod(lambda meta: None))
    # Routers may import a separate reference to the InfosysRAI class; patch that too
    try:
        monkeypatch.setattr(routers_module.InfosysRAI, 'dataAdditiontoDB', staticmethod(lambda params, file: (io.BytesIO(file.file.read()), 'attack-conf-id')))
        monkeypatch.setattr(routers_module.InfosysRAI, 'addReportToDB', staticmethod(lambda reportFile, name: 'rep-id'))
        monkeypatch.setattr(routers_module.InfosysRAI, 'addingReportToDB', staticmethod(lambda meta: None))
    except Exception:
        pass
    # Create in-memory Excel
    df = pd.DataFrame([
        {'goal': 'g1', 'target_str': 't1', 'category': 'c1'},
        {'goal': 'g2', 'target_str': 't2', 'category': 'c1'},
    ])
    bio = io.BytesIO()
    df.to_excel(bio, index=False)
    bio.seek(0)
    # Monkeypatch report generator to avoid heavy plotting and buggy paths
    import src.app.utility.report as report_mod
    monkeypatch.setattr(report_mod, 'generate_html_report_pair', lambda data: '<html></html>')
    # Monkeypatch pdfkit.from_file to just create a dummy pdf file path
    import pdfkit as real_pdfkit
    def fake_from_file(html_path, pdf_path, options=None):
        with open(pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n%stub')
    monkeypatch.setattr(real_pdfkit, 'from_file', fake_from_file)
    # Ensure relative directory used by implementation exists
    os.makedirs('app/routing', exist_ok=True)
    client = _build_client()
    files = {'file': ('data.xlsx', bio.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    params = { 'userId': 'u1' }
    r = client.post('/v1/redteaming/pair/batch', data={'parameters': json.dumps(params)}, files=files, headers={'X-API-Envelope': 'true'})
    assert r.status_code == 200
    body = r.json()
    assert 'meta' in body and 'data' in body
    # Response should include ids (implementation uses camelCase 'reportId' in some versions)
    assert 'RedTeamingId' in body['data'] and ('report_id' in body['data'] or 'reportId' in body['data'])


# ---------------------- Service layer tests ----------------------

def test_service_pair_technique_type_guard():
    """If technique_type != 'pair', service should indicate unsupported."""
    _prepare_stubs()
    from src.app.service import service as service_module
    payload = {
        'goal': 'g', 'target_str': 't', 'category': 'c',
        'technique_type': 'tap',  # not pair
        'n_iterations': 1,
    }
    assert service_module.InfosysRAI.GetRedteamListPair(payload) == 'Technique type not supported'


def test_service_pair_missing_judge_returns_empty(monkeypatch):
    """When no judge is loaded, service should return empty structured lists."""
    _prepare_stubs()
    from src.app.service import service as service_module

    class AttackLM_Stub:
        def __init__(self):
            self.template = object()

    # Ensure attack model loads with a template so we reach judge section
    monkeypatch.setattr(service_module, 'load_attack_and_target_models_pair', lambda payload: (AttackLM_Stub(), None))
    # Return no judges
    monkeypatch.setattr(service_module, 'load_judge', lambda payload: [])

    payload = {
        'goal': 'g', 'target_str': 't', 'category': 'c',
        'technique_type': 'pair', 'n_iterations': 1,
    }
    out = service_module.InfosysRAI.GetRedteamListPair(payload)
    assert isinstance(out, dict)
    assert out == {"improvements": [], "prompts": [], "responses": [], "scores": [], "recommendations": []}


def test_service_apply_moderation_blocks(monkeypatch):
    """_apply_moderation_if_enabled should replace blocked responses with reason."""
    _prepare_stubs()
    from src.app.service import service as service_module
    class ModStub:
        def check_moderation(self, text):
            return {"moderationResults": {"summary": {"status": "FAILED", "reason": ["policy"]}}}
    monkeypatch.setattr(service_module, 'ModerationHandler', ModStub)
    payload = {'enable_moderation': True}
    out = service_module.InfosysRAI._apply_moderation_if_enabled(payload, ["unsafe text"])  # type: ignore[attr-defined]
    assert "Response blocked due to: policy" in out[0]


def test_service_http_session_singleton():
    _prepare_stubs()
    from src.app.service import service as service_module
    s1 = service_module._get_http_session()
    s2 = service_module._get_http_session()
    assert s1 is s2


# ---------------------- Router logic focused tests ----------------------

def test_pair_router_sets_defaults(monkeypatch):
    """Router should fill defaults like userId when missing before calling service."""
    _prepare_stubs()
    from src.app.service import service as service_module
    captured = {}
    def capture(payload):
        captured.update(payload)
        return {'scores': []}
    
    from src.app.routing import routers as routers_module
    monkeypatch.setattr(routers_module.InfosysRAI, 'GetRedteamListPair', staticmethod(capture))

    client = _build_client()
    # Minimal payload omitting userId
    payload = { 'goal': 'g', 'target_str': 't', 'category': 'c' }
    r = client.post('/v1/redteaming/pair', json=payload)
    assert r.status_code == 200
    assert captured.get('userId') == 'admin'
    # A known default should be injected (e.g., n_iterations)
    assert 'n_iterations' in captured


def test_pair_batch_invalid_json_parameters():
    import io
    _prepare_stubs()
    client = _build_client()
    files = {'file': ('data.xlsx', b'xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    # parameters is invalid JSON string
    r = client.post('/v1/redteaming/pair/batch', data={'parameters': '{bad json'}, files=files)
    assert r.status_code == 400
    assert r.json()['detail'] == 'Invalid JSON in parameters'


def test_pair_batch_missing_required_columns(monkeypatch):
    import io
    import pandas as pd
    _prepare_stubs()
    from src.app.service import service as service_module
    # Stub DB addition to just echo BytesIO; also patch routers' reference
    monkeypatch.setattr(service_module.InfosysRAI, 'dataAdditiontoDB', staticmethod(lambda params, file: (io.BytesIO(file.file.read()), 'id')))
    try:
        import src.app.routing.routers as routers_module
        monkeypatch.setattr(routers_module.InfosysRAI, 'dataAdditiontoDB', staticmethod(lambda params, file: (io.BytesIO(file.file.read()), 'id')))
    except Exception:
        pass
    client = _build_client()
    # Build excel WITHOUT 'category' column
    df = pd.DataFrame([{'goal': 'g', 'target_str': 't'}])
    bio = io.BytesIO(); df.to_excel(bio, index=False); bio.seek(0)
    files = {'file': ('data.xlsx', bio.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    # include technique_type so dataAdditiontoDB can run in the implementation
    r = client.post('/v1/redteaming/pair/batch', data={'parameters': json.dumps({'userId':'u1', 'technique_type': 'pair'})}, files=files)
    assert r.status_code == 400
    assert 'Excel file must contain columns' in r.json()['detail']


def test_tap_endpoint_enveloped(monkeypatch):
    _prepare_stubs()
    from src.app.service import service as service_module
    monkeypatch.setattr(service_module.InfosysRAI, 'GetRedteamListTap', staticmethod(lambda p: [{'prompt':'p','response':'r'}]))
    client = _build_client()
    payload = { 'goal': 'g', 'target_str': 't', 'category': 'c' }
    r = client.post('/v1/redteaming/tap', json=payload, headers={'X-API-Envelope':'true'})
    assert r.status_code == 200
    body = r.json()
    assert 'meta' in body and 'data' in body
    assert body['meta']['status'] == 200
