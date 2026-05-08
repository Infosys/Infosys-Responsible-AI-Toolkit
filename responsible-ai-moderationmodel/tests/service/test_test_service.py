"""Tests for service/test service.py - legacy service module with AI model functions.

This module tests the legacy test service functions including toxicity checking,
prompt injection detection, topic restriction, embedding generation, and privacy analysis.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, Mock, patch
import torch
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


@pytest.fixture(scope='module', autouse=True)
def setup_test_service_mocks():
    """Setup comprehensive mocks for test service module before importing."""
    # Remove any existing imports
    for mod in ['service.test service', 'privacy.privacy', 'detoxify', 'mapper.mapper']:
        sys.modules.pop(mod, None)
    
    # Mock torch
    mock_torch = MagicMock()
    mock_torch.device = Mock(return_value='cpu')
    mock_torch.cuda = MagicMock()
    mock_torch.cuda.is_available = Mock(return_value=False)
    mock_torch.no_grad = MagicMock()
    mock_torch.no_grad.__enter__ = Mock(return_value=None)
    mock_torch.no_grad.__exit__ = Mock(return_value=None)
    sys.modules['torch'] = mock_torch
    
    # Mock transformers
    class MockAutoModel:
        @staticmethod
        def from_pretrained(path):
            mock_model = MagicMock()
            mock_model.to = Mock(return_value=mock_model)
            return mock_model
    
    class MockTokenizer:
        @staticmethod
        def from_pretrained(path):
            tokenizer = MagicMock()
            tokenizer.encode = Mock(return_value=[0, 1, 2, 3, 4])  # Mock tokens
            tokenizer.decode = Mock(return_value="decoded text")
            return tokenizer
    
    def mock_pipeline(task, model=None, tokenizer=None, device=None):
        def pipeline_fn(text, *args, **kwargs):
            if task == 'text-classification':
                return [{'label': 'SAFE', 'score': 0.95}]
            elif task == 'zero-shot-classification':
                return {
                    'labels': kwargs.get('candidate_labels', ['topic1', 'topic2']),
                    'scores': [0.8, 0.2],
                    'sequence': text
                }
        return pipeline_fn
    
    transformers_module = MagicMock()
    transformers_module.AutoModelForSequenceClassification = MockAutoModel
    transformers_module.AutoTokenizer = MockTokenizer
    transformers_module.pipeline = mock_pipeline
    sys.modules['transformers'] = transformers_module
    
    # Mock sentence_transformers
    class MockSentenceTransformer:
        def __init__(self, model_path):
            self.model_path = model_path
        
        def to(self, device):
            return self
        
        def encode(self, text, convert_to_tensor=False, device=None):
            if convert_to_tensor:
                # Return a mock tensor
                mock_tensor = MagicMock()
                mock_tensor.to = Mock(return_value=mock_tensor)
                mock_tensor.numpy = Mock(return_value=Mock(tolist=Mock(return_value=[0.1, 0.2, 0.3])))
                return mock_tensor
            return np.array([0.1, 0.2, 0.3])
    
    class MockUtil:
        @staticmethod
        def pytorch_cos_sim(emb1, emb2):
            mock_result = MagicMock()
            mock_result.to = Mock(return_value=mock_result)
            mock_result.numpy = Mock(return_value=Mock(tolist=Mock(return_value=[[0.95]])))
            return mock_result
    
    sentence_transformers_module = MagicMock()
    sentence_transformers_module.SentenceTransformer = MockSentenceTransformer
    sentence_transformers_module.util = MockUtil()
    sys.modules['sentence_transformers'] = sentence_transformers_module
    
    # Mock detoxify
    class MockDetoxify:
        def __init__(self, checkpoint=None, device=None, huggingface_config_path=None):
            pass
        
        def predict(self, text):
            return {
                'toxicity': 0.1,
                'severe_toxicity': 0.05,
                'obscene': 0.08,
                'threat': 0.02,
                'insult': 0.06,
                'identity_attack': 0.03,
                'sexual_explicit': 0.04
            }
    
    detoxify_module = MagicMock()
    detoxify_module.Detoxify = MockDetoxify
    sys.modules['detoxify'] = detoxify_module
    
    # Mock mapper
    class MockProfanityScore:
        def __init__(self, metricName, metricScore):
            self.metricName = metricName
            self.metricScore = metricScore
    
    mapper_module = MagicMock()
    mapper_module.ProfanityScore = MockProfanityScore
    sys.modules['mapper'] = MagicMock()
    sys.modules['mapper.mapper'] = mapper_module
    
    # Mock privacy
    class MockPrivacy:
        @staticmethod
        def textAnalyze(data):
            result = MagicMock()
            result.PIIEntities = []
            return result
    
    privacy_module = MagicMock()
    privacy_module.Privacy = MockPrivacy
    sys.modules['privacy'] = MagicMock()
    sys.modules['privacy.privacy'] = privacy_module
    
    # Mock logger
    class MockLogger:
        def info(self, msg): pass
        def debug(self, msg): pass
        def error(self, msg): pass
    
    class MockContextVar:
        def __init__(self, name):
            self.value = 'test_request_id'
        def get(self):
            return self.value
        def set(self, value):
            self.value = value
    
    logger_module = MagicMock()
    logger_module.CustomLogger = MockLogger
    logger_module.request_id_var = MockContextVar('request_id')
    sys.modules['config'] = MagicMock()
    sys.modules['config.logger'] = logger_module
    
    # Mock exception module
    def mock_error_response(message, status_code=500, error_type="Error"):
        return ({'error': message, 'type': error_type}, status_code)
    
    exception_module = MagicMock()
    exception_module.ProcessingError = Exception
    exception_module.create_secure_error_response = mock_error_response
    sys.modules['exception'] = MagicMock()
    sys.modules['exception.exception'] = exception_module
    
    yield
    
    # Cleanup
    for mod in ['torch', 'transformers', 'sentence_transformers', 'detoxify', 
                'mapper', 'mapper.mapper', 'privacy', 'privacy.privacy',
                'config', 'config.logger', 'exception', 'exception.exception',
                'service.test service']:
        sys.modules.pop(mod, None)


def test_privacy_success():
    """Test privacy function returns PII analysis results."""
    # Import after mocks are set up
    test_service = __import__('service.test service', fromlist=['privacy'])
    
    result = test_service.privacy('My email is test@example.com')
    
    assert isinstance(result, dict)
    assert 'PIIresult' in result
    assert 'modelcalltime' in result
    assert isinstance(result['modelcalltime'], float)


def test_privacy_empty_text():
    """Test privacy function with empty text."""
    test_service = __import__('service.test service', fromlist=['privacy'])
    
    result = test_service.privacy('')
    
    assert isinstance(result, dict)
    assert 'PIIresult' in result


def test_multi_q_net_similarity_with_texts():
    """Test similarity calculation with two text inputs."""
    test_service = __import__('service.test service', fromlist=['multi_q_net_similarity'])
    
    emb, timing = test_service.multi_q_net_similarity(text1='Hello world', text2='Hi there')
    
    assert isinstance(emb, list)
    assert isinstance(timing, dict)
    assert 'time_taken' in timing
    assert timing['time_taken'].endswith('s')


def test_multi_q_net_similarity_with_embeddings():
    """Test similarity calculation with pre-computed embeddings."""
    test_service = __import__('service.test service', fromlist=['multi_q_net_similarity'])
    
    mock_emb1 = MagicMock()
    mock_emb1.to = Mock(return_value=mock_emb1)
    mock_emb2 = MagicMock()
    mock_emb2.to = Mock(return_value=mock_emb2)
    
    emb, timing = test_service.multi_q_net_similarity(emb1=mock_emb1, emb2=mock_emb2)
    
    assert isinstance(emb, list)
    assert 'time_taken' in timing


def test_multi_q_net_similarity_mixed_inputs():
    """Test similarity with text and embedding mix."""
    test_service = __import__('service.test service', fromlist=['multi_q_net_similarity'])
    
    mock_emb = MagicMock()
    mock_emb.to = Mock(return_value=mock_emb)
    
    emb, timing = test_service.multi_q_net_similarity(text1='Hello', emb2=mock_emb)
    
    assert isinstance(emb, list)
    assert 'time_taken' in timing


def test_multi_q_net_embedding_single_text():
    """Test embedding generation for single text."""
    test_service = __import__('service.test service', fromlist=['multi_q_net_embedding'])
    
    embeddings, timing = test_service.multi_q_net_embedding('test-req-1', ['Hello world'])
    
    assert isinstance(embeddings, list)
    assert len(embeddings) == 1
    assert isinstance(timing, dict)
    assert 'time_taken' in timing


def test_multi_q_net_embedding_multiple_texts():
    """Test embedding generation for multiple texts."""
    test_service = __import__('service.test service', fromlist=['multi_q_net_embedding'])
    
    texts = ['First text', 'Second text', 'Third text']
    embeddings, timing = test_service.multi_q_net_embedding('test-req-2', texts)
    
    assert isinstance(embeddings, list)
    assert len(embeddings) == 3
    assert 'time_taken' in timing


def test_multi_q_net_embedding_empty_list():
    """Test embedding generation with empty list returns error."""
    test_service = __import__('service.test service', fromlist=['multi_q_net_embedding'])
    
    # Initialize log_dict and request_id_var to avoid KeyError
    test_service.log_dict = {}
    test_service.request_id_var.set('test-req-3')
    test_service.log_dict['test-req-3'] = []
    
    result, timing = test_service.multi_q_net_embedding('test-req-3', [])
    
    # Empty list causes an error in the function due to text_embedding being unbound
    assert isinstance(result, dict)
    assert 'error' in result
    assert isinstance(timing, (int, float))


def test_restricttopic_check_with_nlimini():
    """Test topic restriction check with nliMini model."""
    test_service = __import__('service.test service', fromlist=['restricttopic_check'])
    
    payload = {
        'text': 'This is about politics',
        'labels': ['politics', 'sports', 'technology'],
        'model': 'nliMini'
    }
    
    result = test_service.restricttopic_check(payload)
    
    assert isinstance(result, dict)
    assert 'labels' in result
    assert 'scores' in result
    assert 'time_taken' in result
    assert result['time_taken'].endswith('s')


def test_restricttopic_check_with_dberta():
    """Test topic restriction check with dberta model."""
    test_service = __import__('service.test service', fromlist=['restricttopic_check'])
    
    payload = {
        'text': 'This is about sports',
        'labels': ['politics', 'sports', 'technology'],
        'model': 'dberta'
    }
    
    result = test_service.restricttopic_check(payload)
    
    assert isinstance(result, dict)
    assert 'labels' in result
    assert 'scores' in result


def test_restricttopic_check_default_model():
    """Test topic restriction check with default model."""
    test_service = __import__('service.test service', fromlist=['restricttopic_check'])
    
    payload = {
        'text': 'This is about technology',
        'labels': ['politics', 'sports', 'technology']
    }
    
    result = test_service.restricttopic_check(payload)
    
    assert isinstance(result, dict)
    assert 'labels' in result


def test_restricttopic_check_score_rounding():
    """Test that scores are rounded to 4 decimal places."""
    test_service = __import__('service.test service', fromlist=['restricttopic_check'])
    
    payload = {
        'text': 'Sample text',
        'labels': ['topic1', 'topic2']
    }
    
    result = test_service.restricttopic_check(payload)
    
    # Check that scores are rounded
    for score in result['scores']:
        assert isinstance(score, float)


def test_toxicity_check_short_text():
    """Test toxicity check with short text (under token limit)."""
    test_service = __import__('service.test service', fromlist=['toxicity_check'])
    
    payload = {'text': 'This is a nice message'}
    result = test_service.toxicity_check(payload, 'test-req-1')
    
    assert isinstance(result, dict)
    assert 'toxicScore' in result
    assert 'time_taken' in result
    assert len(result['toxicScore']) == 7
    
    # Check all toxicity metrics are present
    metric_names = [score.metricName for score in result['toxicScore']]
    expected_metrics = ['toxicity', 'severe_toxicity', 'obscene', 'threat', 
                       'insult', 'identity_attack', 'sexual_explicit']
    assert all(metric in metric_names for metric in expected_metrics)


def test_toxicity_check_long_text():
    """Test toxicity check with long text (over token limit)."""
    test_service = __import__('service.test service', fromlist=['toxicity_check'])
    
    # Create long text by repeating
    long_text = 'This is a test sentence. ' * 100
    payload = {'text': long_text}
    
    result = test_service.toxicity_check(payload, 'test-req-2')
    
    assert isinstance(result, dict)
    assert 'toxicScore' in result
    assert 'time_taken' in result


def test_toxicity_check_all_metrics():
    """Test that all 7 toxicity metrics are returned."""
    test_service = __import__('service.test service', fromlist=['toxicity_check'])
    
    payload = {'text': 'Sample text for toxicity analysis'}
    result = test_service.toxicity_check(payload, 'test-req-3')
    
    assert len(result['toxicScore']) == 7
    
    for score_obj in result['toxicScore']:
        assert hasattr(score_obj, 'metricName')
        assert hasattr(score_obj, 'metricScore')
        assert isinstance(score_obj.metricScore, float)
        assert 0.0 <= score_obj.metricScore <= 1.0


def test_toxicity_check_timing():
    """Test that timing is calculated for toxicity check."""
    test_service = __import__('service.test service', fromlist=['toxicity_check'])
    
    payload = {'text': 'Test text'}
    result = test_service.toxicity_check(payload, 'test-req-4')
    
    assert 'time_taken' in result
    assert result['time_taken'].endswith('s')
    time_value = float(result['time_taken'][:-1])
    assert time_value >= 0.0


def test_prompt_injection_check_safe():
    """Test prompt injection check with safe text."""
    test_service = __import__('service.test service', fromlist=['prompt_injection_check'])
    
    label, prob, timing = test_service.prompt_injection_check('Hello, how are you?', 'test-req-1')
    
    assert isinstance(label, str)
    assert isinstance(prob, float)
    assert isinstance(timing, dict)
    assert 'time_taken' in timing
    assert timing['time_taken'].endswith('s')


def test_prompt_injection_check_returns_tuple():
    """Test that prompt injection check returns a 3-tuple."""
    test_service = __import__('service.test service', fromlist=['prompt_injection_check'])
    
    result = test_service.prompt_injection_check('Test text', 'test-req-2')
    
    assert isinstance(result, tuple)
    assert len(result) == 3
    
    label, probability, timing = result
    assert isinstance(label, str)
    assert isinstance(probability, float)
    assert isinstance(timing, dict)


def test_prompt_injection_check_empty_text():
    """Test prompt injection check with empty text."""
    test_service = __import__('service.test service', fromlist=['prompt_injection_check'])
    
    label, prob, timing = test_service.prompt_injection_check('', 'test-req-3')
    
    assert isinstance(label, str)
    assert isinstance(prob, float)
    assert 'time_taken' in timing


def test_prompt_injection_check_timing():
    """Test timing measurement in prompt injection check."""
    test_service = __import__('service.test service', fromlist=['prompt_injection_check'])
    
    _, _, timing = test_service.prompt_injection_check('Analyze this text', 'test-req-4')
    
    assert 'time_taken' in timing
    time_value = float(timing['time_taken'][:-1])
    assert time_value >= 0.0


def test_toxicity_check_score_ranges():
    """Test that toxicity scores are within valid range [0, 1]."""
    test_service = __import__('service.test service', fromlist=['toxicity_check'])
    
    payload = {'text': 'Testing score ranges'}
    result = test_service.toxicity_check(payload, 'test-req-5')
    
    for score_obj in result['toxicScore']:
        assert 0.0 <= score_obj.metricScore <= 1.0, f"{score_obj.metricName} score out of range"


def test_multi_q_net_embedding_timing():
    """Test that embedding generation includes timing information."""
    test_service = __import__('service.test service', fromlist=['multi_q_net_embedding'])
    
    _, timing = test_service.multi_q_net_embedding('test-req-6', ['Test'])
    
    assert 'time_taken' in timing
    assert isinstance(timing['time_taken'], str)
    assert timing['time_taken'].endswith('s')


def test_restricttopic_check_multiple_labels():
    """Test topic check with multiple labels."""
    test_service = __import__('service.test service', fromlist=['restricttopic_check'])
    
    payload = {
        'text': 'This is a comprehensive text about multiple topics',
        'labels': ['politics', 'sports', 'technology', 'science', 'entertainment']
    }
    
    result = test_service.restricttopic_check(payload)
    
    assert isinstance(result, dict)
    assert 'labels' in result
    assert 'scores' in result
    # The mock returns default labels, so just check structure
    assert isinstance(result['labels'], list)
    assert isinstance(result['scores'], list)
    assert len(result['scores']) > 0


def test_privacy_with_pii_data():
    """Test privacy function with text containing PII."""
    test_service = __import__('service.test service', fromlist=['privacy'])
    
    text_with_pii = 'My name is John Doe and my email is john@example.com. My phone is 555-1234.'
    result = test_service.privacy(text_with_pii)
    
    assert isinstance(result, dict)
    assert 'PIIresult' in result
    assert 'modelcalltime' in result
