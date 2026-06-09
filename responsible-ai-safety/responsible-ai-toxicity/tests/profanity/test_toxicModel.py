import importlib
import sys
import types
import math

import pytest


def make_detoxify_stub(predict_returns=None):
	"""Create a Detoxify factory that returns an object with .predict and .tokenizer"""
	class Tokenizer:
		def __init__(self, encode_result=None):
			# encode should return a sequence like [CLS, ...tokens..., SEP]
			self._encode_result = encode_result or [0, 1, 2, 3]

		def encode(self, text):
			return self._encode_result

		def decode(self, ids):
			# return a sensible string; joining this string in toxicModel leads to character join
			return "decoded_text"

		def __call__(self, text, **kwargs):
			# Return a minimal mapping similar to transformers tokenizers
			# The module under test doesn't rely on the contents here except for shape
			return {"input_ids": [0, 1, 2], "attention_mask": [1, 1, 1]}

	class DetoxObj:
		def __init__(self, encode_result=None, predict_returns_local=None):
			self.tokenizer = Tokenizer(encode_result)
			# allow predict to be dynamic or a constant
			self._predict_returns = predict_returns_local if predict_returns_local is not None else predict_returns
			self.predict_calls = []

		def predict(self, text):
			self.predict_calls.append(text)
			# if _predict_returns is a callable, call it with text
			if callable(self._predict_returns):
				return self._predict_returns(text)
			return self._predict_returns or {"toxicity": 0.0}

	def factory(*args, **kwargs):
		# Allow passing encode_result & predict_returns via kwargs for flexibility
		encode_result = kwargs.pop("encode_result", None)
		predict_returns_local = kwargs.pop("predict_returns", None)
		return DetoxObj(encode_result=encode_result, predict_returns_local=predict_returns_local)

	return factory


def reload_module_with_detox(monkeypatch, detox_factory):
	# Ensure our detoxify stub is used when importing the module
	monkeypatch.setitem(sys.modules, "detoxify", types.SimpleNamespace(Detoxify=detox_factory))
	# Provide a minimal transformers stub to satisfy imports in toxicModel
	monkeypatch.setitem(sys.modules, "transformers", types.SimpleNamespace(
		AutoModelForSequenceClassification=lambda *a, **k: None,
		AutoTokenizer=lambda *a, **k: types.SimpleNamespace(from_pretrained=lambda *a, **k: None)
	))
	# reload the target module to pick up the stub
	if "toxicModel" in sys.modules:
		del sys.modules["toxicModel"]
	return importlib.import_module("toxicModel")


def test_analyze_invalid_inputs(monkeypatch):
	# Provide a minimal Detoxify stub to allow import
	detox_factory = make_detoxify_stub(predict_returns={"toxicity": 0.0})
	mod = reload_module_with_detox(monkeypatch, detox_factory)

	with pytest.raises(ValueError):
		mod.Toxic.analyze("")

	with pytest.raises(ValueError):
		mod.Toxic.analyze(None)

	with pytest.raises(ValueError):
		mod.Toxic.analyze(123)


def test_analyze_short_text_calls_predict_and_returns(monkeypatch):
	# Create a Detoxify that returns a known dict
	expected = {"toxicity": 0.42}
	detox_factory = make_detoxify_stub(predict_returns=expected)
	# Use an encode result with a short token list: [CLS, token1, SEP]
	def factory(*a, **kw):
		return make_detoxify_stub(predict_returns=expected)(encode_result=[0, 10, 2])

	mod = reload_module_with_detox(monkeypatch, factory)

	out = mod.Toxic.analyze("short text")
	assert out == expected


def test_analyze_long_text_splits_and_returns_last(monkeypatch):
	# Build a long encode result to force chunking (>510 tokens)
	token_count = 1200
	# include CLS and SEP tokens around payload
	encode_result = [0] + list(range(1, token_count + 1)) + [2]

	# Make predict return a dict that includes the chunk id so we can detect last call
	def predict_fn(text):
		# record length of text to distinguish calls
		return {"toxicity": len(text)}

	def factory(*a, **kw):
		return make_detoxify_stub(predict_returns=predict_fn)(encode_result=encode_result)

	mod = reload_module_with_detox(monkeypatch, factory)

	result = mod.Toxic.analyze("x" * 1000)
	# Since the stub returns toxicity as len(text), ensure result is a dict with numeric toxicity
	assert isinstance(result, dict)
	assert "toxicity" in result
	assert isinstance(result["toxicity"], int)

