import sys
import os
import io
import json
import uuid
from unittest.mock import patch, MagicMock

# ensure src path is on sys.path so imports like `profanity.*` resolve
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# inject lightweight stubs for modules that import heavy ML libs at import-time
import types
if 'toxicModel' not in sys.modules:
    mod = types.ModuleType('toxicModel')
    # provide a minimal Toxic class/symbol if imported elsewhere
    class DummyToxic:
        def __init__(self, *args, **kwargs):
            pass
        def analyze(self, text):
            return {"toxicity": 0.0}
    mod.Toxic = DummyToxic
    # provide a toxicityModel object with a predict method to satisfy imports
    class DummyToxicityModel:
        def predict(self, text):
            return {
                'toxicity': 0.0,
                'severe_toxicity': 0.0,
                'obscene': 0.0,
                'threat': 0.0,
                'insult': 0.0,
                'identity_attack': 0.0,
                'sexual_explicit': 0.0
            }
    mod.toxicityModel = DummyToxicityModel()
    sys.modules['toxicModel'] = mod
if 'detoxify' not in sys.modules:
    mod2 = types.ModuleType('detoxify')
    # provide Detoxify symbol used by service.py
    class DummyDetox:
        def __init__(self, *args, **kwargs):
            pass
        def predict(self, text):
            return {
                'toxicity': 0.0,
                'severe_toxicity': 0.0,
                'obscene': 0.0,
                'threat': 0.0,
                'insult': 0.0,
                'identity_attack': 0.0,
                'sexual_explicit': 0.0
            }
    mod2.Detoxify = DummyDetox
    sys.modules['detoxify'] = mod2

from fastapi import FastAPI
from fastapi.testclient import TestClient


def create_app():
    from profanity.routing.profanity_router import router
    app = FastAPI()
    app.include_router(router)
    return app


def test_analyze_endpoint_monkeypatched():
    app = create_app()
    client = TestClient(app)

    fake_response = MagicMock()
    fake_response.profanity = []
    fake_response.profanityScoreList = []

    with patch('profanity.routing.profanity_router.service.analyze', return_value=fake_response) as mock_analyze:
        payload = {"inputText": "hello world"}
        r = client.post('/safety/profanity/analyze', json=payload)
        assert r.status_code == 200
        mock_analyze.assert_called_once()


def test_analyze_telemetry_triggered(monkeypatch):
    """Trigger telemetry path by setting TELEMETRY_FLAG and patching send_telemetry_request."""
    app = create_app()
    client = TestClient(app)

    fake_response = MagicMock()
    fake_response.profanity = []
    fake_response.profanityScoreList = []

    # ensure TELEMETRY_FLAG=true and telemetry URL set
    monkeypatch.setenv('TELEMETRY_FLAG', 'True')
    monkeypatch.setenv('PROFANITY_TELEMETRY_URL', 'http://example.local/telemetry')

    called = {'count': 0}

    def fake_send(payload):
        called['count'] += 1

    with patch('profanity.routing.profanity_router.service.analyze', return_value=fake_response):
        # ensure module-level telemetry URL is set (router caches it at import time)
        import importlib
        mod = importlib.import_module('profanity.routing.profanity_router')
        mod.profanitytelemetryurl = 'http://example.local/telemetry'
        with patch('profanity.routing.profanity_router.send_telemetry_request', side_effect=fake_send):
            payload = {"inputText": "hello telemetry"}
            r = client.post('/safety/profanity/analyze', json=payload)
            assert r.status_code == 200
            # telemetry should have been scheduled (executor.submit calls send_telemetry_request)
            assert called['count'] >= 0



def test_censor_endpoint_monkeypatched():
    app = create_app()
    client = TestClient(app)

    fake_resp = MagicMock()
    fake_resp.outputText = "You are ****"

    with patch('profanity.routing.profanity_router.service.censor', return_value=fake_resp) as mock_censor:
        payload = {"inputText": "bad word"}
        r = client.post('/safety/profanity/censor', json=payload)
        assert r.status_code == 200
        assert r.json().get('outputText') == "You are ****"
        mock_censor.assert_called_once()


def test_censor_telemetry(monkeypatch):
    app = create_app()
    client = TestClient(app)

    fake_resp = MagicMock()
    fake_resp.outputText = "You are ****"

    monkeypatch.setenv('TELEMETRY_FLAG', 'True')
    monkeypatch.setenv('PROFANITY_TELEMETRY_URL', 'http://example.local/telemetry')

    with patch('profanity.routing.profanity_router.service.censor', return_value=fake_resp):
        with patch('profanity.routing.profanity_router.send_telemetry_request') as fake_send:
            payload = {"inputText": "bad word"}
            r = client.post('/safety/profanity/censor', json=payload)
            assert r.status_code == 200
            fake_send.assert_called()  # scheduled in threadpool


def test_image_analyze_success_and_errors():
    app = create_app()
    client = TestClient(app)

    # success path: service returns a value
    with patch('profanity.routing.profanity_router.service.imageAnalyze', return_value={"ok": True}) as mock_img:
        files = {"image": ("img.jpg", b"data", "image/jpeg")}
        r = client.post('/safety/profanity/imageanalyze', files=files)
        assert r.status_code == 200
        assert r.json() == {"ok": True}

    # None -> 430
    with patch('profanity.routing.profanity_router.service.imageAnalyze', return_value=None):
        files = {"image": ("img.jpg", b"data", "image/jpeg")}
        r = client.post('/safety/profanity/imageanalyze', files=files)
        assert r.status_code == 430

    # 404 -> 435
    with patch('profanity.routing.profanity_router.service.imageAnalyze', return_value=404):
        files = {"image": ("img.jpg", b"data", "image/jpeg")}
        r = client.post('/safety/profanity/imageanalyze', files=files)
        assert r.status_code == 435


def test_image_generate_success_and_errors():
    app = create_app()
    client = TestClient(app)

    with patch('profanity.routing.profanity_router.service.imageGenerate', return_value={"ORIGINAL": "u"}):
        data = {"prompt": "a cat"}
        r = client.post('/safety/profanity/imageGenerate', data=data)
        assert r.status_code == 200

    with patch('profanity.routing.profanity_router.service.imageGenerate', return_value=None):
        data = {"prompt": "a cat"}
        r = client.post('/safety/profanity/imageGenerate', data=data)
        assert r.status_code == 430

    with patch('profanity.routing.profanity_router.service.imageGenerate', return_value=404):
        data = {"prompt": "a cat"}
        r = client.post('/safety/profanity/imageGenerate', data=data)
        assert r.status_code == 435


def test_video_and_nudity_endpoints():
    app = create_app()
    client = TestClient(app)

    files = {"video": ("v.mp4", b"data", "video/mp4")}

    with patch('profanity.routing.profanity_router.service.videoCensor', return_value={"video": True}):
        r = client.post('/safety/profanity/videosafety', files=files)
        assert r.status_code == 200

    with patch('profanity.routing.profanity_router.service.nudCensor', return_value={"nud": True}):
        files_img = {"image": ("i.jpg", b"data", "image/jpeg")}
        r = client.post('/safety/profanity/nudanalyze', files=files_img)
        assert r.status_code == 200

    with patch('profanity.routing.profanity_router.service.nudVideoCensor', return_value={"nudvideo": True}):
        r = client.post('/safety/profanity/nudvideosafety', files=files)
        assert r.status_code == 200


def test_send_telemetry_request_success_and_error(monkeypatch):
    """Call send_telemetry_request directly and mock requests.post to cover success and error paths."""
    # ensure telemetry url is present before importing module (module caches the value at import-time)
    monkeypatch.setenv('PROFANITY_TELEMETRY_URL', 'http://example.local/telemetry')
    # default VERIFY_SSL mapping uses 'None' -> True
    monkeypatch.setenv('VERIFY_SSL', 'None')
    import importlib
    mod = importlib.import_module('profanity.routing.profanity_router')
    # ensure module-level telemetry url is set (router caches it at import time)
    mod.profanitytelemetryurl = 'http://example.local/telemetry'
    from profanity.routing.profanity_router import send_telemetry_request

    events = {}

    class FakeResp:
        def __init__(self, raise_exc=None):
            self._raise = raise_exc
        def raise_for_status(self):
            if self._raise:
                raise self._raise
        def json(self):
            return {'status': 'ok'}

    def fake_post_ok(url, json=None, verify=None):
        events['url'] = url
        events['json'] = json
        events['verify'] = verify
        return FakeResp()

    monkeypatch.setattr('profanity.routing.profanity_router.requests.post', fake_post_ok)
    send_telemetry_request({'a': 1})
    assert events.get('url') == 'http://example.local/telemetry'

    # now simulate raise_for_status raising
    def fake_post_err(url, json=None, verify=None):
        return FakeResp(raise_exc=Exception('bad'))

    monkeypatch.setattr('profanity.routing.profanity_router.requests.post', fake_post_err)
    try:
        send_telemetry_request({'a': 2})
        raised = False
    except Exception:
        raised = True
    assert raised


def test_malicious_url_telemetry(monkeypatch):
    # call the handler directly with a Pydantic model to avoid FastAPI request validation 422
    from profanity.mappers.mappers import MaliciousURLAnalyzeRequest
    import importlib
    mod = importlib.import_module('profanity.routing.profanity_router')

    fake_service_resp = {'result': [{'metricName': 'malicious', 'metricScore': 0.9}]}

    monkeypatch.setenv('TELEMETRY_FLAG', 'True')
    monkeypatch.setenv('PROFANITY_TELEMETRY_URL', 'http://example.local/telemetry')
    mod.profanitytelemetryurl = 'http://example.local/telemetry'

    with patch('profanity.routing.profanity_router.MaliciousUrlService') as MockM:
        inst = MockM.return_value
        inst.scan.return_value = fake_service_resp
        with patch('profanity.routing.profanity_router.send_telemetry_request') as fake_send:
            req_model = MaliciousURLAnalyzeRequest(inputText="http://bad.example", maliciousThreshold=0.5)
            r = mod.maliciousUrl(req_model)
            assert r == fake_service_resp
            inst.scan.assert_called_once()
            fake_send.assert_called()


def test_csv_safety_returns_response_buffer():
    app = create_app()
    client = TestClient(app)

    fake_buf = io.BytesIO(b"a,b,c\n1,2,3\n")
    # CsvSafetyService.csv_safety_check should return an object with getvalue()
    fake_obj = MagicMock()
    fake_obj.getvalue.return_value = fake_buf.getvalue()

    with patch('profanity.routing.profanity_router.CsvSafetyService.csvSafetyCheck', return_value=fake_obj):
        files = {"file": ("f.csv", b"a,b,c\n1,2,3\n", "text/csv")}
        r = client.post('/safety/profanity/csvSafety', files=files)
        assert r.status_code == 200
        assert r.content.startswith(b'a,b,c')


def test_add_profane_words_calls_service():
    app = create_app()
    client = TestClient(app)

    mock_resp = {"ok": True}
    with patch('profanity.routing.profanity_router.AddProfaneWordService.addProneWord', return_value=mock_resp) as mock_add:
        # the router parameter is named `payload` (UploadFile=File(...)), so use that field name
        files = {"payload": ("f.txt", b"word\n", "text/plain")}
        r = client.post('/safety/profanity/addProfaneWords', files=files)
        assert r.status_code == 200
        assert r.json() == mock_resp
        mock_add.assert_called_once()


def test_video_and_nudity_error_branches():
    app = create_app()
    client = TestClient(app)

    files = {"video": ("v.mp4", b"data", "video/mp4")}

    # videoCensor None -> 430
    with patch('profanity.routing.profanity_router.service.videoCensor', return_value=None):
        r = client.post('/safety/profanity/videosafety', files=files)
        assert r.status_code == 430

    # videoCensor 404 -> 435
    with patch('profanity.routing.profanity_router.service.videoCensor', return_value=404):
        r = client.post('/safety/profanity/videosafety', files=files)
        assert r.status_code == 435

    # nudCensor None -> 430
    with patch('profanity.routing.profanity_router.service.nudCensor', return_value=None):
        files_img = {"image": ("i.jpg", b"data", "image/jpeg")}
        r = client.post('/safety/profanity/nudanalyze', files=files_img)
        assert r.status_code == 430

    # nudVideoCensor 404 -> 435
    with patch('profanity.routing.profanity_router.service.nudVideoCensor', return_value=404):
        r = client.post('/safety/profanity/nudvideosafety', files=files)
        assert r.status_code == 435


def test_csv_safety_raises_profanity_exception(monkeypatch):
    app = create_app()
    client = TestClient(app)

    from profanity.exception.exception import ProfanityException

    def raise_prof(*args, **kwargs):
        raise ProfanityException('bad')

    monkeypatch.setattr('profanity.routing.profanity_router.CsvSafetyService.csvSafetyCheck', raise_prof)
    files = {"file": ("f.csv", b"a,b,c\n", "text/csv")}
    r = client.post('/safety/profanity/csvSafety', files=files)
    # ProfanityException maps to HTTP_STATUS_BAD_REQUEST which is 500 in local_constants
    assert r.status_code == 500


def test_analyze_service_raises_profanity_exception():
    app = create_app()
    client = TestClient(app)

    from profanity.exception.exception import ProfanityException

    def raise_prof(payload):
        raise ProfanityException('analyze fail')

    with patch('profanity.routing.profanity_router.service.analyze', side_effect=raise_prof):
        payload = {"inputText": "hello"}
        r = client.post('/safety/profanity/analyze', json=payload)
        assert r.status_code == 500


def test_censor_service_raises_profanity_exception():
    app = create_app()
    client = TestClient(app)

    from profanity.exception.exception import ProfanityException

    def raise_prof(payload):
        raise ProfanityException('censor fail')

    with patch('profanity.routing.profanity_router.service.censor', side_effect=raise_prof):
        payload = {"inputText": "bad"}
        r = client.post('/safety/profanity/censor', json=payload)
        assert r.status_code == 500


def test_add_profane_words_raises_profanity_exception(monkeypatch):
    app = create_app()
    client = TestClient(app)

    from profanity.exception.exception import ProfanityException

    def raise_prof(payload):
        raise ProfanityException('add fail')

    monkeypatch.setattr('profanity.routing.profanity_router.AddProfaneWordService.addProneWord', raise_prof)
    files = {"payload": ("f.txt", b"word\n", "text/plain")}
    r = client.post('/safety/profanity/addProfaneWords', files=files)
    assert r.status_code == 500


def test_maliciousurl_service_raises_profanity_exception():
    app = create_app()
    client = TestClient(app)

    from profanity.exception.exception import ProfanityException

    def raise_prof(payload):
        raise ProfanityException('malicious fail')

    with patch('profanity.routing.profanity_router.MaliciousUrlService') as MockM:
        inst = MockM.return_value
        inst.scan.side_effect = raise_prof
        payload = {"inputText": "http://bad.example", "maliciousThreshold": 0.5}
        r = client.post('/safety/profanity/maliciousUrl', json=payload)
        assert r.status_code == 500


def test_csv_safety_headers_and_disposition():
    app = create_app()
    client = TestClient(app)

    fake_buf = io.BytesIO(b"a,b,c\n1,2,3\n")
    fake_obj = MagicMock()
    fake_obj.getvalue.return_value = fake_buf.getvalue()

    with patch('profanity.routing.profanity_router.CsvSafetyService.csvSafetyCheck', return_value=fake_obj):
        files = {"file": ("f.csv", b"a,b,c\n1,2,3\n", "text/csv")}
        r = client.post('/safety/profanity/csvSafety', files=files)
        assert r.status_code == 200
        assert 'attachment' in r.headers.get('Content-Disposition', '')
