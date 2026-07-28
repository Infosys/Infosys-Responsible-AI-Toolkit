"""Comprehensive tests for topicModel service with business logic coverage.

Tests topic classification functionality including fine-tuned BERT and nlimini models,
label filtering, score sorting, timing measurements, and exception handling.
"""

import pytest
pytest.skip("Legacy tests merged into test_topicModel.py - file kept for reference", allow_module_level=True)
import sys
import os
from unittest.mock import MagicMock, patch
from types import SimpleNamespace

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from tests.utils.mock_helpers import make_aicloud_modules, make_local_constants, isolate_and_reload
from tests.utils.isolate_module import reload_module


class TensorLikeResult:
    """Helper class to simulate tensor-like objects with tolist() method."""
    def __init__(self, data):
        self.data = data
    def tolist(self):
        return self.data


def create_topic_stubs():
    """Create deterministic stubs for topic service dependencies."""
    
    def make_bert_model_stub():
        """Create stub for fine-tuned BERT model with predictable outputs."""
        class BertModelStub:
            def __init__(self):
                self.config = SimpleNamespace(id2label={
                    0: "technology", 1: "politics", 2: "sports", 
                    3: "science", 4: "business", 5: "entertainment"
                })
            
            def __call__(self, **kwargs):
                # Return deterministic logits based on input
                return SimpleNamespace(
                    logits=SimpleNamespace(squeeze=lambda: SimpleNamespace(cpu=lambda: [0.8, 0.6, 0.3, 0.7, 0.4, 0.2]))
                )
            
            def eval(self):
                pass
            
            def to(self, device):
                return self
        
        return BertModelStub()
    
    def make_tokenizer_stub():
        """Create stub tokenizer that returns predictable encodings."""
        class TensorLikeStub:
            def __init__(self, data):
                self.data = data
            
            def to(self, device):
                return self  # Return self for chaining
        
        class TokenizerStub:
            def __call__(self, text, return_tensors=None, truncation=True, padding=True):
                return {
                    'input_ids': TensorLikeStub([[101, 2023, 102]]),
                    'attention_mask': TensorLikeStub([[1, 1, 1]])
                }
            
            @classmethod
            def from_pretrained(cls, model_path):
                return cls()
        
        return TokenizerStub()
    
    def make_nlimini_pipeline_stub():
        """Create stub for nlimini zero-shot classification pipeline."""
        class NliminiStub:
            def __call__(self, text, labels, hypothesis_template=None, multi_label=True):
                # Return deterministic classification based on text and labels
                if "technology" in labels and "artificial intelligence" in text.lower():
                    return {
                        "sequence": text,
                        "labels": labels[:3],  # Return first 3 labels
                        "scores": [0.9234567, 0.8456789, 0.7123456]
                    }
                elif "finance" in labels and "market" in text.lower():
                    return {
                        "sequence": text,
                        "labels": labels[:2],
                        "scores": [0.8876543, 0.7654321]
                    }
                else:
                    # Default behavior
                    return {
                        "sequence": text,
                        "labels": labels[:len(labels)],
                        "scores": [0.5 + i * 0.1 for i in range(len(labels))]
                    }
        
        return NliminiStub()
    
    def make_torch_stub():
        """Create stub for torch with tensor operations."""
        class TorchStub:
            class nn:
                class Sigmoid:
                    def __call__(self, x):
                        # Return predictable sigmoid outputs
                        return [0.8456, 0.6789, 0.2341, 0.7234, 0.4567, 0.1234]
            
            @staticmethod
            def device(device_type):
                return f"mock_{device_type}"
            
            @staticmethod
            def cuda_is_available():
                return False  # Force CPU for deterministic testing
            
            class no_grad:
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    pass
        
        return TorchStub()
    
    def make_transformers_stub():
        """Create stub for transformers with model classes."""
        class TransformersStub:
            class AutoModelForSequenceClassification:
                @staticmethod
                def from_pretrained(model_path):
                    return make_bert_model_stub()
            
            class AutoTokenizer:
                @staticmethod
                def from_pretrained(model_path):
                    return make_tokenizer_stub()
                
            def pipeline(task, model=None, tokenizer=None, device=None):
                return make_nlimini_pipeline_stub()
        
        return TransformersStub()
    
    def make_time_stub():
        """Create stub for time module with controllable timing."""
        class TimeStub:
            def __init__(self):
                self.call_count = 0
                
            def time(self):
                # Return predictable timing sequence
                times = [1000.0, 1000.250, 1000.500, 1000.750, 1001.0, 1001.250, 1001.500]
                result = times[self.call_count % len(times)]
                self.call_count += 1
                return result
        
        return TimeStub()
    
    def make_request_id_var_stub():
        """Create stub for request_id_var context variable."""
        class RequestIdVarStub:
            def __init__(self):
                self.current_id = None
                
            def get(self):
                return self.current_id or 'test_topic_id_456'
                
            def set(self, value):
                self.current_id = value
        
        return RequestIdVarStub()
    
    def make_log_stub():
        """Create stub logger that tracks calls."""
        class LogStub:
            def __init__(self):
                self.calls = []
                
            def info(self, msg): self.calls.append(('info', msg))
            def debug(self, msg): self.calls.append(('debug', msg))
            def error(self, msg): self.calls.append(('error', msg))
        
        return LogStub()
    
    def make_werkzeug_stub():
        """Create stub for werkzeug exceptions."""
        class InternalServerErrorStub(Exception):
            pass
        
        return SimpleNamespace(InternalServerError=InternalServerErrorStub)
    
    def make_traceback_stub():
        """Create stub for traceback module."""
        class TracebackStub:
            def extract_tb(self, tb):
                return [SimpleNamespace(lineno=89)]
        
        return TracebackStub()
    
    return {
        'torch': make_torch_stub(),
        'transformers': make_transformers_stub(),
        'time': make_time_stub(),
        'werkzeug.exceptions': make_werkzeug_stub(),
        'config.logger': SimpleNamespace(
            CustomLogger=lambda: make_log_stub(),
            request_id_var=make_request_id_var_stub()
        ),
        'traceback': make_traceback_stub(),
        'contextvars': SimpleNamespace(
            ContextVar=lambda name: make_request_id_var_stub()
        ),
        'fastapi.encoders': SimpleNamespace(jsonable_encoder=lambda x: x),
        'mapper.mapper': SimpleNamespace(),
        'os': SimpleNamespace(
            path=SimpleNamespace(
                join=lambda *args: "/fake/path",
                dirname=lambda x: "/fake",
                abspath=lambda x: "/fake/abs"
            )
        ),
        'sys': SimpleNamespace(
            frozen=False,
            _MEIPASS="/fake/path"
        )
    }


def test_classify_with_bert_multi_label_basic_functionality():
    """Test basic BERT multi-label classification functionality."""
    topic_stubs = create_topic_stubs()
    replacements = {**make_aicloud_modules(), **topic_stubs}
    
    with isolate_and_reload('service.topicModel', replacements) as context:
        mod = reload_module('service.topicModel')
        
        # Set up module-level variables after loading
        mod.tokenizer = topic_stubs['transformers'].AutoTokenizer.from_pretrained("")
        mod.model = topic_stubs['transformers'].AutoModelForSequenceClassification.from_pretrained("")
        mod.device = "cpu"
        
        mod.global_sigmoid_fn = lambda x: TensorLikeResult([0.8456, 0.6789, 0.2341, 0.7234, 0.4567, 0.1234])
        
        result = mod.classify_with_bert_multi_label("Test text for classification", "cpu")
        
        # Verify structure and content
        assert isinstance(result, list)
        assert len(result) == 6  # Should have 6 labels from id2label
        
        # Verify each result has required fields
        for item in result:
            assert "label" in item
            assert "score" in item
            assert isinstance(item["score"], float)
        
        # Verify specific labels and scores (rounded to 4 decimals)
        expected_labels = ["technology", "politics", "sports", "science", "business", "entertainment"]
        actual_labels = [item["label"] for item in result]
        assert actual_labels == expected_labels
        
        # Verify scores are properly rounded
        assert result[0]["score"] == 0.8456
        assert result[1]["score"] == 0.6789


def test_restricttopic_check_fine_tuned_bert_with_filtering():
    """Test restrict topic check with fine-tuned BERT and label filtering."""
    topic_stubs = create_topic_stubs()
    replacements = {**make_aicloud_modules(), **topic_stubs}
    
    with isolate_and_reload('service.topicModel', replacements) as context:
        mod = reload_module('service.topicModel')
        
        # Set up module-level variables
        mod.tokenizer = topic_stubs['transformers'].AutoTokenizer.from_pretrained("")
        mod.model = topic_stubs['transformers'].AutoModelForSequenceClassification.from_pretrained("")
        mod.device = "cpu"
        mod.global_sigmoid_fn = lambda x: TensorLikeResult([0.8456, 0.6789, 0.2341, 0.7234, 0.4567, 0.1234])
        
        payload = {
            "text": "Latest developments in artificial intelligence technology",
            "model": "fine-tuned distilbert",
            "labels": ["technology", "science", "business"]
        }
        
        mod.request_id_var.set("test_id_123")
        result = mod.restricttopic_check(payload)
        
        # Verify structure
        assert isinstance(result, dict)
        assert "sequence" in result
        assert "labels" in result
        assert "scores" in result
        assert "time_taken" in result
        
        # Verify filtering and sorting (by score descending)
        assert result["sequence"] == payload["text"]
        assert result["labels"] == ["technology", "science", "business"]  # Sorted by score
        assert result["scores"] == [0.8456, 0.7234, 0.4567]  # Corresponding scores
        
        # Verify timing format
        assert result["time_taken"].endswith("s")
        time_val = float(result["time_taken"].rstrip("s"))
        assert time_val > 0


def test_restricttopic_check_nlimini_model_classification():
    """Test restrict topic check with nlimini zero-shot classification."""
    topic_stubs = create_topic_stubs()
    replacements = {**make_aicloud_modules(), **topic_stubs}
    
    with isolate_and_reload('service.topicModel', replacements) as context:
        mod = reload_module('service.topicModel')
        
        # Set up module-level variables
        mod.nlimini = topic_stubs['transformers'].pipeline("zero-shot-classification")
        
        payload = {
            "text": "Artificial intelligence is transforming the technology sector",
            "model": "deberta",
            "labels": ["technology", "artificial intelligence", "innovation"]
        }
        
        # ensure the service's expected name 'nlp' is set to our pipeline stub
        mod.nlp = topic_stubs['transformers'].pipeline("zero-shot-classification")
        mod.request_id_var.set("nlimini_test_789")
        result = mod.restricttopic_check(payload)
        
        # Verify structure
        assert isinstance(result, dict)
        assert "sequence" in result
        assert "labels" in result
        assert "scores" in result
        assert "time_taken" in result
        
        # Verify nlimini-specific behavior
        assert result["sequence"] == payload["text"]
        assert len(result["labels"]) <= len(payload["labels"])
        
        # Verify score precision (rounded to 4 decimals)
        for score in result["scores"]:
            assert isinstance(score, float)
            # Check that score precision is 4 decimal places or fewer
            assert len(str(score).split('.')[-1]) <= 4


def test_restricttopic_check_default_model_behavior():
    """Test restrict topic check with default model (defaults to fine-tuned bert)."""
    topic_stubs = create_topic_stubs()
    replacements = {**make_aicloud_modules(), **topic_stubs}
    
    with isolate_and_reload('service.topicModel', replacements) as context:
        mod = reload_module('service.topicModel')
        
        # Set up module-level variables
        mod.tokenizer = topic_stubs['transformers'].AutoTokenizer.from_pretrained("")
        mod.model = topic_stubs['transformers'].AutoModelForSequenceClassification.from_pretrained("")
        mod.device = "cpu"
        mod.global_sigmoid_fn = lambda x: TensorLikeResult([0.8456, 0.6789, 0.2341, 0.7234, 0.4567, 0.1234])
        
        payload = {
            "text": "Business analysis and financial reporting",
            "labels": ["business", "politics"]  # No model specified
        }
        
        # The default model path uses 'nlp' zero-shot pipeline
        mod.nlp = topic_stubs['transformers'].pipeline("zero-shot-classification")
        mod.request_id_var.set("default_test_456")
        result = mod.restricttopic_check(payload)
        
    # The service defaults to the 'deberta' zero-shot pipeline when no model is specified.
    # Expect the pipeline to return labels in the same order as provided and numeric scores.
    assert result["labels"] == payload["labels"]
    assert isinstance(result["scores"], list)
    assert all(isinstance(s, float) for s in result["scores"])


def test_restricttopic_check_empty_label_filtering():
    """Test restrict topic check when no labels match the results."""
    topic_stubs = create_topic_stubs()
    replacements = {**make_aicloud_modules(), **topic_stubs}
    
    with isolate_and_reload('service.topicModel', replacements) as context:
        mod = reload_module('service.topicModel')
        
        # Set up module-level variables
        mod.tokenizer = topic_stubs['transformers'].AutoTokenizer.from_pretrained("")
        mod.model = topic_stubs['transformers'].AutoModelForSequenceClassification.from_pretrained("")
        mod.device = "cpu"
        mod.global_sigmoid_fn = lambda x: TensorLikeResult([0.8456, 0.6789, 0.2341, 0.7234, 0.4567, 0.1234])
        
        payload = {
            "text": "Test text for classification",
            "model": "fine-tuned distilbert",
            "labels": ["nonexistent_label", "another_fake_label"]
        }
        
        mod.request_id_var.set("empty_filter_test")
        result = mod.restricttopic_check(payload)
        
        # Should return empty arrays when no labels match
        assert result["labels"] == []
        assert result["scores"] == []
        assert result["sequence"] == payload["text"]


def test_restricttopic_check_case_insensitive_matching():
    """Test that label matching is case-insensitive."""
    topic_stubs = create_topic_stubs()
    replacements = {**make_aicloud_modules(), **topic_stubs}
    
    with isolate_and_reload('service.topicModel', replacements) as context:
        mod = reload_module('service.topicModel')
        
        # Set up module-level variables
        mod.tokenizer = topic_stubs['transformers'].AutoTokenizer.from_pretrained("")
        mod.model = topic_stubs['transformers'].AutoModelForSequenceClassification.from_pretrained("")
        mod.device = "cpu"
        mod.global_sigmoid_fn = lambda x: TensorLikeResult([0.8456, 0.6789, 0.2341, 0.7234, 0.4567, 0.1234])
        
        payload = {
            "text": "Technology and science developments",
            "model": "fine-tuned distilbert",
            "labels": ["TECHNOLOGY", "Science", "SPORTS"]  # Mixed case
        }
        
        mod.request_id_var.set("case_test_321")
        result = mod.restricttopic_check(payload)
        
        # Should match case-insensitively and sort by score desc
        assert result["labels"] == ["technology", "science", "sports"]  # Sorted by scores: 0.8456, 0.7234, 0.2341
        assert result["scores"] == [0.8456, 0.7234, 0.2341]
        assert len(result["labels"]) == 3


def test_restricttopic_check_score_sorting_behavior():
    """Test that results are properly sorted by score in descending order."""
    topic_stubs = create_topic_stubs()
    replacements = {**make_aicloud_modules(), **topic_stubs}
    
    with isolate_and_reload('service.topicModel', replacements) as context:
        mod = reload_module('service.topicModel')
        
        # Set up module-level variables
        mod.tokenizer = topic_stubs['transformers'].AutoTokenizer.from_pretrained("")
        mod.model = topic_stubs['transformers'].AutoModelForSequenceClassification.from_pretrained("")
        mod.device = "cpu"
        mod.global_sigmoid_fn = lambda x: TensorLikeResult([0.8456, 0.6789, 0.2341, 0.7234, 0.4567, 0.1234])
        
        payload = {
            "text": "Multi-topic content covering various subjects",
            "model": "fine-tuned distilbert",
            "labels": ["entertainment", "business", "technology", "science"]
        }
        
        mod.request_id_var.set("sort_test_654")
        result = mod.restricttopic_check(payload)
        
        # Verify descending score order
        scores = result["scores"]
        assert scores == sorted(scores, reverse=True)
        
        # Verify corresponding labels are in correct order
        expected_order = ["technology", "science", "business", "entertainment"]  # By score desc
        assert result["labels"] == expected_order


def test_restricttopic_check_timing_precision():
    """Test timing measurement precision and format."""
    topic_stubs = create_topic_stubs()
    replacements = {**make_aicloud_modules(), **topic_stubs}
    
    with isolate_and_reload('service.topicModel', replacements) as context:
        mod = reload_module('service.topicModel')
        
        # Set up module-level variables
        mod.tokenizer = topic_stubs['transformers'].AutoTokenizer.from_pretrained("")
        mod.model = topic_stubs['transformers'].AutoModelForSequenceClassification.from_pretrained("")
        mod.device = "cpu"
        mod.global_sigmoid_fn = lambda x: TensorLikeResult([0.8456, 0.6789, 0.2341, 0.7234, 0.4567, 0.1234])
        
        payload = {
            "text": "Testing timing precision",
            "model": "fine-tuned distilbert",
            "labels": ["technology"]
        }
        
        mod.request_id_var.set("timing_test")
        result = mod.restricttopic_check(payload)
        
        # Verify timing format
        time_taken = result["time_taken"]
        assert time_taken.endswith("s")
        
        # Verify precision (3 decimal places as per source code)
        time_value = float(time_taken.rstrip("s"))
        assert time_value > 0
        
        # Check decimal precision
        decimal_part = str(time_value).split('.')[1] if '.' in str(time_value) else ""
        assert len(decimal_part) <= 3


def test_restricttopic_check_nlimini_score_rounding():
    """Test that nlimini scores are properly rounded to 4 decimal places."""
    topic_stubs = create_topic_stubs()
    replacements = {**make_aicloud_modules(), **topic_stubs}
    
    with isolate_and_reload('service.topicModel', replacements) as context:
        mod = reload_module('service.topicModel')
        
        # Set up module-level variables
        mod.nlimini = topic_stubs['transformers'].pipeline("zero-shot-classification")
        
        payload = {
            "text": "Financial markets and investment strategies analysis",
            "model": "deberta",
            "labels": ["finance", "business", "economics"]
        }
        
        # ensure nlimini/deberta pipeline is assigned to service variable 'nlp'
        mod.nlp = topic_stubs['transformers'].pipeline("zero-shot-classification")
        mod.request_id_var.set("rounding_test")
        result = mod.restricttopic_check(payload)
        
        # Verify all scores are rounded to 4 decimal places
        for score in result["scores"]:
            # Convert to string and check decimal places
            score_str = str(score)
            if '.' in score_str:
                decimal_places = len(score_str.split('.')[1])
                assert decimal_places <= 4


def test_restricttopic_check_long_text_handling():
    """Test topic classification with very long text input."""
    topic_stubs = create_topic_stubs()
    replacements = {**make_aicloud_modules(), **topic_stubs}
    
    with isolate_and_reload('service.topicModel', replacements) as context:
        mod = reload_module('service.topicModel')
        
        # Set up module-level variables
        mod.tokenizer = topic_stubs['transformers'].AutoTokenizer.from_pretrained("")
        mod.model = topic_stubs['transformers'].AutoModelForSequenceClassification.from_pretrained("")
        mod.device = "cpu"
        mod.global_sigmoid_fn = lambda x: TensorLikeResult([0.8456, 0.6789, 0.2341, 0.7234, 0.4567, 0.1234])
        
        # Create very long text
        long_text = "Technology and innovation in modern society " * 100
        
        payload = {
            "text": long_text,
            "model": "fine-tuned distilbert",
            "labels": ["technology"]
        }
        
        mod.request_id_var.set("long_text_test")
        result = mod.restricttopic_check(payload)
        
        # Should handle long text without issues
        assert result["sequence"] == long_text
        assert "technology" in result["labels"]
        assert len(result["scores"]) > 0


def test_restricttopic_check_unicode_text_support():
    """Test topic classification with unicode and special characters."""
    topic_stubs = create_topic_stubs()
    replacements = {**make_aicloud_modules(), **topic_stubs}
    
    with isolate_and_reload('service.topicModel', replacements) as context:
        mod = reload_module('service.topicModel')
        
        # Set up module-level variables
        mod.tokenizer = topic_stubs['transformers'].AutoTokenizer.from_pretrained("")
        mod.model = topic_stubs['transformers'].AutoModelForSequenceClassification.from_pretrained("")
        mod.device = "cpu"
        mod.global_sigmoid_fn = lambda x: TensorLikeResult([0.8456, 0.6789, 0.2341, 0.7234, 0.4567, 0.1234])
        
        unicode_text = "Tecnología avanzada con inteligencia artificial 人工智能 🤖 émoticons"
        
        payload = {
            "text": unicode_text,
            "model": "fine-tuned distilbert",
            "labels": ["technology", "science"]
        }
        
        mod.request_id_var.set("unicode_test")
        result = mod.restricttopic_check(payload)
        
        # Should handle unicode text properly
        assert result["sequence"] == unicode_text
        assert len(result["labels"]) > 0


def test_restricttopic_check_unknown_model_exception():
    """Test exception handling for unknown model types."""
    topic_stubs = create_topic_stubs()
    replacements = {**make_aicloud_modules(), **topic_stubs}
    
    with isolate_and_reload('service.topicModel', replacements) as context:
        mod = reload_module('service.topicModel')
        
        payload = {
            "text": "Test text for unknown model",
            "model": "unknown_model_type",
            "labels": ["test"]
        }
        
        # Should raise InternalServerError due to unknown model
        with pytest.raises(Exception):  # Will be InternalServerErrorStub
            mod.request_id_var.set("error_test")
            mod.restricttopic_check(payload)


def test_restricttopic_check_missing_text_exception():
    """Test exception handling when text is missing from payload."""
    topic_stubs = create_topic_stubs()
    replacements = {**make_aicloud_modules(), **topic_stubs}
    
    with isolate_and_reload('service.topicModel', replacements) as context:
        mod = reload_module('service.topicModel')
        
        payload = {
            "model": "fine-tuned distilbert",
            "labels": ["test"]
            # Missing 'text' key
        }
        
        # Should raise exception due to missing text
        with pytest.raises(Exception):
            mod.request_id_var.set("missing_text_test")
            mod.restricttopic_check(payload)


def test_restricttopic_check_context_and_logging_management():
    """Test that context variables and logging are properly managed."""
    topic_stubs = create_topic_stubs()
    replacements = {**make_aicloud_modules(), **topic_stubs}
    
    with isolate_and_reload('service.topicModel', replacements) as context:
        mod = reload_module('service.topicModel')
        
        # Set up module-level variables
        mod.tokenizer = topic_stubs['transformers'].AutoTokenizer.from_pretrained("")
        mod.model = topic_stubs['transformers'].AutoModelForSequenceClassification.from_pretrained("")
        mod.device = "cpu"
        mod.global_sigmoid_fn = lambda x: TensorLikeResult([0.8456, 0.6789, 0.2341, 0.7234, 0.4567, 0.1234])
        
        payload = {
            "text": "Testing context management",
            "model": "fine-tuned distilbert",
            "labels": ["technology"]
        }
        
        # default model uses the zero-shot pipeline assigned to 'nlp'
        mod.nlp = topic_stubs['transformers'].pipeline("zero-shot-classification")
        mod.request_id_var.set("context_test")
        result = mod.restricttopic_check(payload)
        
        # Should complete successfully with proper context management
        assert isinstance(result, dict)
        assert "time_taken" in result
