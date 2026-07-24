import io
import base64
import builtins
from unittest.mock import patch, MagicMock, mock_open

import pytest
from PIL import Image
import sys
import os

# Ensure test can import package from local src/ directory
ROOT_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
if ROOT_SRC not in sys.path:
	sys.path.insert(0, ROOT_SRC)
# Prevent importing the real toxicModel which loads Detoxify at import-time.
import types
from unittest.mock import MagicMock
toxic_mod = types.ModuleType('toxicModel')
toxic_mod.Toxic = MagicMock()
toxic_mod.toxicityModel = MagicMock()
sys.modules['toxicModel'] = toxic_mod

# Create a lightweight fake `detoxify` module so importing service doesn't try to load heavy models
detox_mod = types.ModuleType('detoxify')
class DummyDetox:
	def __init__(self, *args, **kwargs):
		self.tokenizer = MagicMock()
	def predict(self, text):
		return {'toxicity': 0.0, 'severe_toxicity':0.0, 'obscene':0.0, 'threat':0.0, 'insult':0.0, 'identity_attack':0.0, 'sexual_explicit':0.0}
detox_mod.Detoxify = DummyDetox
sys.modules['detoxify'] = detox_mod

from profanity.service import service as svc
from profanity.mappers.mappers import ProfanityAnalyzeRequest, ProfanitycensorRequest
import json


class DummyFile:
	def __init__(self, b: bytes):
		self._b = b

	def read(self, *args, **kwargs):
		return self._b


class DummyUpload:
	def __init__(self, b: bytes):
		# service.image_analyze expects payload.image.file to be a file-like
		self.file = io.BytesIO(b)


class DummyNestedUpload:
	# For AddProfaneWordService: payload passed as {"file": upload}
	# inside function they call payload.file.file.read()
	def __init__(self, b: bytes):
		class Inner:
			def __init__(self, data):
				self._data = data

			def read(self):
				return self._data

		self.file = Inner(b)


def make_png_bytes():
	img = Image.new('RGB', (10, 10), color='red')
	buf = io.BytesIO()
	img.save(buf, format='PNG')
	return buf.getvalue()


def test_analyze_toxic_high():
	payload = ProfanityAnalyzeRequest(inputText="some bad text")
	with patch('profanity.service.service.toxicityModel.predict') as mock_predict, \
		 patch('profanity.service.service.profanity.censor') as mock_censor:
		mock_predict.return_value = {
			'toxicity': 0.8,
			'severe_toxicity': 0.12,
			'obscene': 0.0,
			'threat': 0.0,
			'insult': 0.0,
			'identity_attack': 0.0,
			'sexual_explicit': 0.0,
		}
		# mimic censor returning [censored_text, [words], [[begin,end]]]
		mock_censor.return_value = ['censored', ['badword'], [[0, 7]]]

		res = svc.ProfanityService.analyze(payload)

		assert isinstance(res.profanityScoreList, list)
		# profanity list should contain the mocked 'badword'
		assert any(p['profaneWord'] == 'badword' for p in [dict(x) for x in res.profanity])
		# toxicity metric present and rounded
		tox = [x for x in res.profanityScoreList if x.metricName == 'toxicity'][0]
		assert round(float(tox.metricScore), 3) == round(0.8, 3)


def test_analyze_toxic_low():
	payload = ProfanityAnalyzeRequest(inputText="clean text")
	with patch('profanity.service.service.toxicityModel.predict') as mock_predict, \
		 patch('profanity.service.service.profanity.censor') as mock_censor:
		mock_predict.return_value = {
			'toxicity': 0.2,
			'severe_toxicity': 0.0,
			'obscene': 0.0,
			'threat': 0.0,
			'insult': 0.0,
			'identity_attack': 0.0,
			'sexual_explicit': 0.0,
		}
		mock_censor.return_value = ['clean', [], []]

		res = svc.ProfanityService.analyze(payload)

		assert res.profanity == []
		assert isinstance(res.profanityScoreList, list)


def test_censor_toxic_and_non_toxic():
	toxic_payload = ProfanitycensorRequest(inputText="toxic")
	clean_payload = ProfanitycensorRequest(inputText="clean")
	with patch('profanity.service.service.toxicityModel.predict') as mock_predict, \
		 patch('profanity.service.service.profanity.censor') as mock_censor:
		mock_predict.return_value = {'toxicity': 0.9}
		mock_censor.return_value = ['you are ****', [], []]
		res = svc.ProfanityService.censor(toxic_payload)
		assert res.outputText == 'you are ****'

		mock_predict.return_value = {'toxicity': 0.1}
		res2 = svc.ProfanityService.censor(clean_payload)
		assert res2.outputText == 'clean'


def test_image_to_byte_roundtrip():
	img_bytes = make_png_bytes()
	img = Image.open(io.BytesIO(img_bytes))
	b64 = svc.ProfanityService.imageToByte(img)
	assert isinstance(b64, str)
	decoded = base64.b64decode(b64)
	assert decoded[:8].startswith(b'\x89PNG') or decoded[:4] == b'\xff\xd8'  # PNG or JPEG header


def test_image_analyze_calls_detector_and_returns_blurred(monkeypatch):
	img_bytes = make_png_bytes()
	payload = {
		'image': DummyUpload(img_bytes),
		'portfolio': 'p1',
		'account': 'a1',
		'accuracy': 'high'
	}

	# mock ApiCall.request to return config thresholds
	with patch('profanity.service.service.ApiCall.request') as mock_api, \
		 patch('profanity.service.service.Detector.detector') as mock_detector:
		mock_api.return_value = {"drawings": "0.1", "hentai": "0.1", "neutral": "0.1", "porn": "0.1", "sexy": "0.1"}
		# return high sexy score to force blur
		mock_detector.return_value = {"sexy": 0.9, "hentai": 0.0, "porn": 0.0, "neutral": 0.0, "drawings": 0.0}

		res = svc.ProfanityService.imageAnalyze(payload)
		assert 'analyze' in res and 'ORIGINAL' in res and 'BLURRED' in res


def test_image_generate_http_error(monkeypatch):
	img_bytes = make_png_bytes()
	payload = {'prompt': 'hello', 'portfolio': None, 'account': None}
	class DummyResp:
		def __init__(self):
			self.status_code = 500

		def json(self):
			return {}

	with patch('profanity.service.service.requests.request') as mock_req:
		mock_req.return_value = DummyResp()
		# ensure env var used for IMAGEGEN_IP exists        
		monkeypatch.setenv('IMAGEGEN_IP', 'http://example') 
		# ensure safety config exists (module-level var may be None)
		svc.safetyconfig = json.dumps({"drawings":0.1,"hentai":0.1,"neutral":0.1,"porn":0.1,"sexy":0.1})
		# Should raise an exception (wrapped in except in code)
		with pytest.raises(Exception):
			svc.ProfanityService.imageGenerate(payload)


def test_add_profane_word_service_merges_and_loads(monkeypatch):
	sample_bytes = b"x\ny\n"
	payload = {'file': DummyNestedUpload(sample_bytes)}

	# Patch get_profanity_words to return existing list
	with patch('profanity.service.service.LoadData.get_profanity_words') as mock_get, \
		 patch('profanity.service.service.profanity.load_censor_words_from_file') as mock_load, \
		 patch('builtins.open', mock_open()) as mocked_open, \
		 patch('profanity.service.service.os.remove') as mock_remove:
		mock_get.return_value = ['existing']
		mock_load.return_value = None

		res = svc.AddProfaneWordService.addProneWord(payload)
		assert res == 'success'
		mock_load.assert_called()
		mock_remove.assert_called()


def test_apicall_request_admin_off(monkeypatch):
	# set admin connection off
	monkeypatch.setenv('ADMIN_CONNECTION', 'False')

	class D:
		def __init__(self):
			self.portfolio = 'p'
			self.account = 'a'

	res = svc.ApiCall.request(D())
	assert res == 404


def test_apicall_request_success(monkeypatch):
	# ensure admin connection on and mock httpx.post
	monkeypatch.setenv('ADMIN_CONNECTION', 'True')
	monkeypatch.setenv('ADMIN_API', 'http://example')

	class DummyResponse:
		def json(self):
			return {"safetyParameter": [{"drawings": 0.1, "hentai": 0.1, "neutral": 0.1, "porn": 0.1, "sexy": 0.1}]}

	with patch('profanity.service.service.httpx.post') as mock_post:
		mock_post.return_value = DummyResponse()

		class D:
			def __init__(self):
				self.portfolio = 'p'
				self.account = 'a'

		res = svc.ApiCall.request(D())
		assert isinstance(res, dict)
		assert res['porn'] == 0.1


def test_load_data_file_not_found():
	# patch open to raise FileNotFoundError
	with patch('builtins.open', side_effect=FileNotFoundError('no file')):
		with pytest.raises(Exception) as ei:
			svc.LoadData.get_profanity_words('nonexistent.txt')
		assert 'Profanity Word List Not Found' in str(ei.value)


def test_analyze_multiple_profanities():
	payload = ProfanityAnalyzeRequest(inputText="bad bad")
	with patch('profanity.service.service.toxicityModel.predict') as mock_predict, \
		 patch('profanity.service.service.profanity.censor') as mock_censor:
		mock_predict.return_value = {'toxicity': 0.9, 'severe_toxicity': 0.0, 'obscene': 0.0, 'threat': 0.0, 'insult': 0.0, 'identity_attack': 0.0, 'sexual_explicit': 0.0}
		mock_censor.return_value = ['c', ['a','b'], [[0,1],[2,3]]]
		res = svc.ProfanityService.analyze(payload)
		assert len(res.profanity) == 2


def test_analyze_predict_exception():
	payload = ProfanityAnalyzeRequest(inputText="x")
	with patch('profanity.service.service.toxicityModel.predict', side_effect=RuntimeError('fail')):
		with pytest.raises(RuntimeError):
			svc.ProfanityService.analyze(payload)


def test_image_analyze_uses_env_config(monkeypatch):
	img_bytes = make_png_bytes()
	payload = {'image': DummyUpload(img_bytes), 'portfolio': None, 'account': None, 'accuracy': 'high'}
	# service.safetyconfig is read at import time; set it directly on module
	svc.safetyconfig = json.dumps({"drawings":0.1,"hentai":0.1,"neutral":0.1,"porn":0.1,"sexy":0.1})
	monkeypatch.setenv('SAFETY_COFIG', svc.safetyconfig)
	with patch('profanity.service.service.Detector.detector') as mock_detector:
		mock_detector.return_value = {"sexy":0.0, "hentai":0.0, "porn":0.0, "neutral":0.0, "drawings":0.0}
		res = svc.ProfanityService.imageAnalyze(payload)
		assert isinstance(res, dict) and 'ORIGINAL' in res and 'BLURRED' in res


def test_image_analyze_apicall_returns_404():
	img_bytes = make_png_bytes()
	payload = {'image': DummyUpload(img_bytes), 'portfolio': 'p', 'account': 'a', 'accuracy': 'high'}
	with patch('profanity.service.service.ApiCall.request') as mock_api:
		mock_api.return_value = 404
		res = svc.ProfanityService.imageAnalyze(payload)
		assert res == 404


def test_image_analyze_apicall_returns_empty():
	img_bytes = make_png_bytes()
	payload = {'image': DummyUpload(img_bytes), 'portfolio': 'p', 'account': 'a', 'accuracy': 'high'}
	with patch('profanity.service.service.ApiCall.request') as mock_api:
		mock_api.return_value = []
		res = svc.ProfanityService.imageAnalyze(payload)
		assert res is None


def test_image_generate_success(monkeypatch):
	payload = {'prompt':'ok', 'portfolio': None, 'account': None}
	img_bytes = make_png_bytes()
	b64 = base64.b64encode(img_bytes).decode('utf-8')
	class DummyResp:
		status_code = 200
		def json(self):
			return {"image": b64}

	with patch('profanity.service.service.requests.request') as mock_req, \
		 patch('profanity.service.service.Detector.detector') as mock_detector:
		mock_req.return_value = DummyResp()
		mock_detector.return_value = {"sexy": 0.0, "hentai":0.0, "porn":0.0, "neutral":0.0, "drawings":0.0}
		# ensure module-level safetyconfig exists so json.loads won't fail
		svc.safetyconfig = json.dumps({"drawings":0.1,"hentai":0.1,"neutral":0.1,"porn":0.1,"sexy":0.1})
		monkeypatch.setenv('IMAGEGEN_IP', 'http://example')
		res = svc.ProfanityService.imageGenerate(payload)
		assert isinstance(res, dict)
		assert 'analyze' in res and 'ORIGINAL' in res and 'BLURRED' in res


def test_video_censor_and_error():
	payload = {'video': DummyNestedUpload(b'data')}
	with patch('profanity.service.service.process_video') as mock_proc:
		mock_proc.return_value = 'video_base64'
		res = svc.ProfanityService.videoCensor(payload)
		assert res == 'video_base64'

	with patch('profanity.service.service.process_video', side_effect=RuntimeError('bad')):
		with pytest.raises(Exception):
			svc.ProfanityService.videoCensor(payload)


def test_nud_censor_and_video(monkeypatch):
	payload_img = {'image': DummyUpload(make_png_bytes())}
	payload_vid = {'video': DummyNestedUpload(b'data')}
	with patch('profanity.service.service.nudeNetImages') as mock_img:
		mock_img.return_value = {'blurredImage':'b','originalImage':'o','nudanalyze':{}}
		assert svc.ProfanityService.nudCensor(payload_img) == {'blurredImage':'b','originalImage':'o','nudanalyze':{}}

	with patch('profanity.service.service.nudeNetVideo') as mock_vid:
		mock_vid.return_value = {'nudanalyze':{}, 'BLURRED':'v'}
		assert svc.ProfanityService.nudVideoCensor(payload_vid) == {'nudanalyze':{}, 'BLURRED':'v'}

	with patch('profanity.service.service.nudeNetImages', side_effect=RuntimeError('err')):
		with pytest.raises(Exception):
			svc.ProfanityService.nudCensor(payload_img)


def test_check_toxicity_and_add_label_branches(monkeypatch):
	# toxic path should return censored text
	monkeypatch.setattr('profanity.service.service.Toxic.analyze', lambda text: {'toxicity': 0.9, 'severe_toxicity':0,'obscene':0,'threat':0,'insult':0,'identity_attack':0,'sexual_explicit':0})
	monkeypatch.setattr('profanity.service.service.profanity.censor', lambda t: ['censored', [], []])
	assert svc.CheckSafety.check_toxicity_and_add_label('bad') == 'censored'

	# non-toxic path returns original text
	monkeypatch.setattr('profanity.service.service.Toxic.analyze', lambda text: {'toxicity': 0.1, 'severe_toxicity':0,'obscene':0,'threat':0,'insult':0,'identity_attack':0,'sexual_explicit':0})
	assert svc.CheckSafety.check_toxicity_and_add_label('ok') == 'ok'


def test_checkSafety_processes_small_dataframe(monkeypatch, tmp_path):
	# Patch dd.read_csv to return a small dask dataframe built from pandas
	import pandas as pd
	import dask.dataframe as ddf

	def fake_read(csv_file, header=None):
		return ddf.from_pandas(pd.DataFrame({0: ['row1', 'row2']}), npartitions=1)

	monkeypatch.setattr('profanity.service.service.dd.read_csv', fake_read)

	# make the toxicity check deterministic
	monkeypatch.setattr('profanity.service.service.CheckSafety.check_toxicity_and_add_label', lambda text: text + '_checked')

	checker = svc.CheckSafety()
	out = checker.checkSafety('ignored.csv', output_file=None)
	# output is a StringIO-like object
	assert hasattr(out, 'getvalue')
	content = out.getvalue()
	assert 'row1_checked' in content and 'row2_checked' in content


def test_apicall_request_httpx_error(monkeypatch):
	class D:
		def __init__(self):
			self.portfolio = 'p'
			self.account = 'a'

	# simulate httpx.post raising an exception
	monkeypatch.setattr('profanity.service.service.httpx.post', lambda *a, **k: (_ for _ in ()).throw(RuntimeError('net fail')))
	with pytest.raises(Exception):
		svc.ApiCall.request(D())


def test_image_analyze_elif_blur_branch():
	# portfolio/account provided, ApiCall returns config with high thresholds so first 'if' is false
	img_bytes = make_png_bytes()
	payload = {'image': DummyUpload(img_bytes), 'portfolio': 'p', 'account': 'a', 'accuracy': 'high'}
	with patch('profanity.service.service.ApiCall.request') as mock_api, \
		 patch('profanity.service.service.Detector.detector') as mock_detector:
		# set config such that float(config['sexy']) is larger than res['sexy']
		mock_api.return_value = {"drawings": "0.9", "hentai": "0.9", "neutral": "0.9", "porn": "0.9", "sexy": "0.9"}
		# but set detector so sexy > neutral and sexy > drawings to hit elif
		mock_detector.return_value = {"sexy": 0.5, "hentai": 0.0, "porn": 0.0, "neutral": 0.1, "drawings": 0.1}
		res = svc.ProfanityService.imageAnalyze(payload)
		assert 'BLURRED' in res


def test_image_generate_apicall_empty_returns_not_found(monkeypatch):
	# ApiCall returns empty list -> should return 'Portfolio/Account Not Found'
	img_bytes = make_png_bytes()
	b64 = base64.b64encode(img_bytes).decode('utf-8')
	class DummyResp:
		status_code = 200
		def json(self):
			return {"image": b64}

	payload = {'prompt': 'ok', 'portfolio': 'p', 'account': 'a'}
	with patch('profanity.service.service.ApiCall.request') as mock_api, \
		 patch('profanity.service.service.requests.request') as mock_req:
		mock_api.return_value = []
		mock_req.return_value = DummyResp()
		res = svc.ProfanityService.imageGenerate(payload)
		assert res == 'Portfolio/Account Not Found'


def test_image_generate_elif_blur_branch(monkeypatch):
	# successful image generate but second-elif blur path
	img_bytes = make_png_bytes()
	b64 = base64.b64encode(img_bytes).decode('utf-8')
	class DummyResp:
		status_code = 200
		def json(self):
			return {"image": b64}

	payload = {'prompt': 'ok', 'portfolio': None, 'account': None}
	with patch('profanity.service.service.requests.request') as mock_req, \
		 patch('profanity.service.service.Detector.detector') as mock_detector:
		mock_req.return_value = DummyResp()
		# set detector results so second elif triggers
		mock_detector.return_value = {"sexy": 0.5, "hentai":0.0, "porn":0.0, "neutral":0.1, "drawings":0.1}
		svc.safetyconfig = json.dumps({"drawings":0.9,"hentai":0.9,"neutral":0.9,"porn":0.9,"sexy":0.9})
		res = svc.ProfanityService.imageGenerate(payload)
		assert 'BLURRED' in res


def test_apicall_request_json_none_returns_empty(monkeypatch):
	# httpx.post.json returns None -> ApiCall.request should return []
	class DummyResponse:
		def json(self):
			return None

	monkeypatch.setenv('ADMIN_CONNECTION', 'True')
	monkeypatch.setenv('ADMIN_API', 'http://example')
	with patch('profanity.service.service.httpx.post') as mock_post:
		mock_post.return_value = DummyResponse()
		class D:
			def __init__(self):
				self.portfolio = 'p'
				self.account = 'a'
		res = svc.ApiCall.request(D())
		assert res == []


def test_check_toxicity_and_add_label_exception(monkeypatch):
	# simulate Toxic.analyze raising
	monkeypatch.setattr('profanity.service.service.Toxic.analyze', lambda text: (_ for _ in ()).throw(RuntimeError('tox fail')))
	assert svc.CheckSafety.check_toxicity_and_add_label('x') == 'Error'


def test_checkSafety_output_file_saves(monkeypatch, tmp_path):
	# Fake dask-like object to exercise saving branch
	import pandas as pd

	class FakeDask:
		def __init__(self):
			self._df = pd.DataFrame({0: ['a','b']})
		def map_partitions(self, fn):
			return self
		def persist(self):
			return self
		def compute(self):
			return self._df
		def to_csv(self, output_file, index=False, single_file=True):
			# write an output file to simulate Save
			with open(output_file, 'w') as f:
				f.write('a,b')

	def fake_read(csv_file, header=None):
		return FakeDask()

	monkeypatch.setattr('profanity.service.service.dd.read_csv', fake_read)
	monkeypatch.setattr('profanity.service.service.CheckSafety.check_toxicity_and_add_label', lambda x: x + '_c')

	checker = svc.CheckSafety()
	out = checker.checkSafety('ignored.csv', output_file=str(tmp_path / 'out.csv'))
	assert hasattr(out, 'getvalue')


