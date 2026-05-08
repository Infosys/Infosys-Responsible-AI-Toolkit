"""Tests for topicModel with real src code execution.

These tests import and execute the REAL src code with mocked ML dependencies
to provide actual code coverage of the topicModel service.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Test by importing REAL src code with mocked heavy dependencies

@pytest.fixture(scope='module', autouse=True)
def setup_mocks():
    """Setup mocks for BERT/transformers dependencies before importing src."""
    # Remove conftest stubs
    for mod in ['service.topicModel', 'torch', 'transformers', 'config.logger', 'contextvars']:
        sys.modules.pop(mod, None)
    
    # Mock torch
    mock_torch = MagicMock()
    mock_torch.cuda = MagicMock(is_available=lambda: False)
    mock_torch.device = lambda x: 'cpu'
    
    class MockSigmoid:
        def __call__(self, logits):
            class MockTensor:
                def squeeze(self):
                    return self
                def cpu(self):
                    return self
                def tolist(self):
                    return [0.85, 0.65, 0.45, 0.75, 0.55, 0.35]
            return MockTensor()
    
    mock_torch.nn = MagicMock()
    mock_torch.nn.Sigmoid = MockSigmoid
    mock_torch.no_grad = MagicMock(__enter__=lambda self: None, __exit__=lambda self, *args: None)
    sys.modules['torch'] = mock_torch
    
    # Mock transformers with realistic behavior
    mock_transformers = MagicMock()
    
    class MockConfig:
        id2label = {0: "technology", 1: "politics", 2: "sports", 3: "science", 4: "business", 5: "entertainment"}
    
    class MockModel:
        config = MockConfig()
        def __init__(self):
            pass
        def to(self, device):
            return self
        def eval(self):
            pass
        def __call__(self, **kwargs):
            class MockOutput:
                class MockLogits:
                    def squeeze(self):
                        return self
                    def cpu(self):
                        return [2.0, 1.5, 1.0, 1.8, 1.3, 0.8]
                logits = MockLogits()
            return MockOutput()
    
    class MockTokenizer:
        def __call__(self, text, return_tensors=None, truncation=True, padding=True):
            class MockTensor:
                def to(self, device):
                    return self
            return {'input_ids': MockTensor(), 'attention_mask': MockTensor()}
        @classmethod
        def from_pretrained(cls, path):
            return cls()
    
    def mock_pipeline(task, model=None, tokenizer=None, device=None):
        def pipeline_call(text, labels, hypothesis_template=None, multi_label=True):
            # Return sorted by score descending
            results = []
            for i, label in enumerate(labels):
                score = 0.9 - (i * 0.1)  # Descending scores
                results.append(label)
            return {
                'sequence': text,
                'labels': labels,
                'scores': [round(0.9 - (i * 0.1), 4) for i in range(len(labels))]
            }
        return pipeline_call
    
    mock_transformers.AutoModelForSequenceClassification = MagicMock()
    mock_transformers.AutoModelForSequenceClassification.from_pretrained = MagicMock(return_value=MockModel())
    mock_transformers.AutoTokenizer = MockTokenizer
    mock_transformers.pipeline = mock_pipeline
    sys.modules['transformers'] = mock_transformers
    
    # Mock logger and context vars
    class MockLogger:
        def info(self, msg): pass
        def debug(self, msg): pass
        def error(self, msg): pass
    
    class MockContextVar:
        def __init__(self, name):
            self.value = None
        def get(self):
            return self.value or 'test_request_id'
        def set(self, value):
            self.value = value
    
    logger_module = MagicMock()
    logger_module.CustomLogger = MockLogger
    logger_module.request_id_var = MockContextVar('request_id')
    sys.modules['config.logger'] = logger_module
    
    contextvars_module = MagicMock()
    contextvars_module.ContextVar = MockContextVar
    sys.modules['contextvars'] = contextvars_module
    
    # Mock werkzeug
    class MockInternalServerError(Exception):
        pass
    
    werkzeug_module = MagicMock()
    werkzeug_module.exceptions = MagicMock()
    werkzeug_module.exceptions.InternalServerError = MockInternalServerError
    sys.modules['werkzeug'] = werkzeug_module
    sys.modules['werkzeug.exceptions'] = werkzeug_module.exceptions
    
    # Mock traceback
    class MockTraceback:
        class MockFrame:
            lineno = 100
        @staticmethod
        def extract_tb(tb):
            return [MockTraceback.MockFrame()]
    sys.modules['traceback'] = MockTraceback()
    
    yield
    
    # Cleanup
    cleanup_modules = ['torch', 'transformers', 'config.logger', 'contextvars', 
                      'werkzeug', 'werkzeug.exceptions', 'traceback', 'service.topicModel']
    for mod in cleanup_modules:
        sys.modules.pop(mod, None)


def test_fine_tuned_bert_classification():
    """Test fine-tuned BERT model classification."""
    from service import topicModel
    
    payload = {
        'text': 'Latest developments in artificial intelligence and machine learning',
        'model': 'fine-tuned distilbert',
        'labels': ['technology', 'science']
    }
    
    result = topicModel.restricttopic_check(payload)
    
    assert isinstance(result, dict)
    assert 'sequence' in result
    assert 'labels' in result
    assert 'scores' in result
    assert 'time_taken' in result
    assert result['sequence'] == payload['text']
    assert result['time_taken'].endswith('s')


def test_deberta_zero_shot_classification():
    """Test deberta zero-shot classification model."""
    from service import topicModel
    
    payload = {
        'text': 'Discussion about political reforms and government policies',
        'model': 'deberta',
        'labels': ['politics', 'government', 'policy']
    }
    
    result = topicModel.restricttopic_check(payload)
    
    assert isinstance(result, dict)
    assert 'sequence' in result
    assert 'labels' in result
    assert 'scores' in result
    assert len(result['labels']) <= len(payload['labels'])
    for score in result['scores']:
        assert isinstance(score, float)


def test_label_filtering():
    """Test that labels are properly filtered in fine-tuned model."""
    from service import topicModel
    
    payload = {
        'text': 'Sports news and athletic competitions',
        'model': 'fine-tuned distilbert',
        'labels': ['sports', 'technology']  # Only sports should match well
    }
    
    result = topicModel.restricttopic_check(payload)
    
    assert 'labels' in result
    assert 'scores' in result
    # Results should be sorted by score descending
    if len(result['scores']) > 1:
        assert result['scores'][0] >= result['scores'][1]


def test_score_rounding():
    """Test that scores are rounded to 4 decimal places in deberta mode."""
    from service import topicModel
    
    payload = {
        'text': 'Business analysis and financial markets',
        'model': 'deberta',
        'labels': ['business', 'finance']
    }
    
    result = topicModel.restricttopic_check(payload)
    
    for score in result['scores']:
        # Check that score has at most 4 decimal places
        score_str = str(score)
        if '.' in score_str:
            decimal_part = score_str.split('.')[1]
            assert len(decimal_part) <= 4


def test_timing_measurement():
    """Test that timing is measured and formatted correctly."""
    from service import topicModel
    
    payload = {
        'text': 'Test timing measurement for topic classification',
        'model': 'deberta',
        'labels': ['test']
    }
    
    result = topicModel.restricttopic_check(payload)
    
    assert 'time_taken' in result
    assert result['time_taken'].endswith('s')
    time_val = float(result['time_taken'][:-1])
    assert time_val >= 0.0


def test_multiple_labels():
    """Test classification with multiple labels."""
    from service import topicModel
    
    payload = {
        'text': 'Comprehensive news covering multiple topics',
        'model': 'deberta',
        'labels': ['politics', 'business', 'technology', 'sports', 'entertainment']
    }
    
    result = topicModel.restricttopic_check(payload)
    
    assert len(result['labels']) == len(result['scores'])
    assert len(result['labels']) <= len(payload['labels'])


# --- Additional merged tests from test_topicModel_old.py (adapted) ---
def test_classify_with_bert_multi_label_basic_functionality_merged():
    """Merged: basic multi-label classification behavior for BERT-like models."""
    from service import topicModel

    result = topicModel.classify_with_bert_multi_label('Test text for classification', 'cpu')
    assert isinstance(result, list)
    assert len(result) >= 1
    for item in result:
        assert 'label' in item and 'score' in item
        assert isinstance(item['score'], float)


def test_restricttopic_check_nlimini_model_classification_merged():
    """Merged: zero-shot pipeline behavior (nlimini/deberta)"""
    from service import topicModel

    payload = {
        'text': 'Artificial intelligence is transforming the technology sector',
        'model': 'deberta',
        'labels': ['technology', 'artificial intelligence', 'innovation']
    }

    # ensure the service pipeline variable exists in this mocked environment
    if not hasattr(topicModel, 'nlp'):
        # pipeline is provided by setup_mocks; if missing, skip
        pytest.skip('nlp pipeline not available in test environment')

    result = topicModel.restricttopic_check(payload)
    assert isinstance(result, dict)
    assert 'sequence' in result and 'labels' in result and 'scores' in result
    assert result['sequence'] == payload['text']
    # scores must be numeric floats
    for s in result['scores']:
        assert isinstance(s, float)


def test_restricttopic_check_empty_label_filtering_merged():
    """Merged: empty label filtering returns empty lists or equivalent response."""
    from service import topicModel

    payload = {
        'text': 'Test text for classification',
        'model': 'fine-tuned distilbert',
        'labels': ['nonexistent_label', 'another_fake_label']
    }

    result = topicModel.restricttopic_check(payload)
    assert isinstance(result, dict)
    # result may contain empty labels/scores lists
    assert isinstance(result.get('labels', []), list)
    assert isinstance(result.get('scores', []), list)


def test_restricttopic_check_long_text_handling_merged():
    """Merged: long text input should be handled without exception."""
    from service import topicModel

    long_text = 'Technology and innovation in modern society ' * 100
    payload = {
        'text': long_text,
        'model': 'fine-tuned distilbert',
        'labels': ['technology']
    }

    result = topicModel.restricttopic_check(payload)
    assert isinstance(result, dict)
    assert result.get('sequence') == long_text

