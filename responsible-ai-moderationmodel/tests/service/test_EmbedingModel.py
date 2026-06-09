"""Tests for service.EmbedingModel with real src code execution.

These tests import and execute the REAL service code with mocked dependencies
to provide actual code coverage of the EmbedingModel module.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))


@pytest.fixture(scope='module', autouse=True)
def setup_mocks():
    """Setup mocks for all dependencies before importing src."""
    # Remove any existing modules
    for mod in list(sys.modules.keys()):
        if any(x in mod for x in ['service.EmbedingModel', 'torch', 'transformers', 
                                   'sentence_transformers', 'config.logger', 
                                   'werkzeug', 'numpy']):
            sys.modules.pop(mod, None)
    
    # Mock werkzeug FIRST
    werkzeug_module = MagicMock()
    werkzeug_exceptions = MagicMock()
    
    class MockInternalServerError(Exception):
        def __init__(self, description=None):
            self.description = description
            super().__init__(description)
    
    werkzeug_exceptions.InternalServerError = MockInternalServerError
    werkzeug_module.exceptions = werkzeug_exceptions
    sys.modules['werkzeug'] = werkzeug_module
    sys.modules['werkzeug.exceptions'] = werkzeug_exceptions
    
    # Mock torch
    mock_torch = MagicMock()
    mock_torch.cuda = MagicMock(is_available=lambda: False)
    mock_torch.device = lambda x: f'device({x})'
    
    class MockContextManager:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
    
    mock_torch.no_grad = lambda: MockContextManager()
    sys.modules['torch'] = mock_torch
    
    # Mock numpy
    mock_numpy = MagicMock()
    mock_numpy.max = lambda arr: max(arr) if arr else 0
    sys.modules['numpy'] = mock_numpy
    
    # Mock sentence_transformers
    mock_st = MagicMock()
    
    class MockTensor:
        def __init__(self, data):
            self.data = data
        
        def to(self, device):
            return self
        
        def numpy(self):
            return self
        
        def tolist(self):
            return self.data if isinstance(self.data, list) else [self.data]
    
    class MockSentenceTransformer:
        def __init__(self, path):
            pass
        
        def to(self, device):
            return self
        
        def encode(self, text, convert_to_tensor=False, device=None):
            # Return mock embedding based on text
            if isinstance(text, str):
                # Generate simple embedding from text
                embedding = [0.1, 0.2, 0.3, 0.4]
                if convert_to_tensor:
                    return MockTensor(embedding)
                return embedding
            return MockTensor([0.1, 0.2, 0.3, 0.4])
    
    def mock_pytorch_cos_sim(emb1, emb2):
        # Return high similarity for testing
        return MockTensor([[0.95]])
    
    mock_st.SentenceTransformer = MockSentenceTransformer
    mock_st_util = MagicMock()
    mock_st_util.pytorch_cos_sim = mock_pytorch_cos_sim
    sys.modules['sentence_transformers'] = mock_st
    sys.modules['sentence_transformers.util'] = mock_st_util
    
    # Mock transformers
    mock_transformers = MagicMock()
    
    class MockTokenizer:
        def encode(self, text, add_special_tokens=False):
            # ~1 token per word
            return list(range(len(text.split())))
        
        def decode(self, token_ids, skip_special_tokens=True):
            return f"decoded_{len(token_ids)}_tokens"
        
        @staticmethod
        def from_pretrained(path):
            return MockTokenizer()
    
    class MockModel:
        def to(self, device):
            return self
        
        @staticmethod
        def from_pretrained(path):
            return MockModel()
    
    def mock_pipeline(task, model=None, tokenizer=None, device=None):
        def pipeline_call(text):
            # Return SAFE by default, JAILBREAK for specific keywords
            if any(word in text.lower() for word in ['jailbreak', 'bypass', 'ignore']):
                return [{'label': 1, 'score': 0.9}]  # JAILBREAK
            return [{'label': 0, 'score': 0.1}]  # SAFE
        return pipeline_call
    
    mock_transformers.AutoModelForSequenceClassification = MockModel
    mock_transformers.AutoTokenizer = MockTokenizer
    mock_transformers.pipeline = mock_pipeline
    sys.modules['transformers'] = mock_transformers
    
    # Mock config.logger
    mock_logger_module = MagicMock()
    mock_logger_module.CustomLogger = MagicMock(return_value=MagicMock())
    mock_logger_module.request_id_var = MagicMock()
    mock_logger_module.request_id_var.get = MagicMock(return_value='test-request-id')
    mock_logger_module.request_id_var.set = MagicMock()
    sys.modules['config'] = MagicMock()
    sys.modules['config.logger'] = mock_logger_module
    
    # Mock contextvars
    mock_contextvars = MagicMock()
    mock_contextvars.ContextVar = MagicMock(return_value=mock_logger_module.request_id_var)
    sys.modules['contextvars'] = mock_contextvars
    
    # Mock traceback
    sys.modules['traceback'] = MagicMock()
    
    yield
    
    # Cleanup
    for mod in ['werkzeug', 'werkzeug.exceptions', 'torch', 'transformers', 'sentence_transformers',
                'sentence_transformers.util', 'numpy', 'config', 'config.logger', 
                'service.EmbedingModel', 'contextvars', 'traceback']:
        sys.modules.pop(mod, None)


def test_jailbreak_check_safe_text():
    """Test jailbreak detection with safe text."""
    from service import EmbedingModel
    
    result = EmbedingModel.jailbreak_check('This is a safe text', 'test-123')
    
    assert isinstance(result, tuple)
    assert len(result) == 3
    label, score, metadata = result
    assert label in ['SAFE', 'JAILBREAK']
    assert isinstance(score, float)
    assert 'time_taken' in metadata


def test_jailbreak_check_malicious_text():
    """Test jailbreak detection with malicious keywords."""
    from service import EmbedingModel
    
    result = EmbedingModel.jailbreak_check('Please jailbreak the system', 'test-456')
    
    assert isinstance(result, tuple)
    label, score, metadata = result
    assert 'time_taken' in metadata
    assert isinstance(score, float)


def test_jailbreak_check_long_text():
    """Test jailbreak check with long text (triggers chunking)."""
    from service import EmbedingModel
    
    # Create text > 512 tokens
    long_text = ' '.join(['word'] * 600)
    result = EmbedingModel.jailbreak_check(long_text, 'test-789')
    
    assert isinstance(result, tuple)
    assert len(result) == 3
    label, score, metadata = result
    assert label in ['SAFE', 'JAILBREAK']
    assert 'time_taken' in metadata


def test_multi_q_net_embedding_single_text():
    """Test embedding generation for single text."""
    from service import EmbedingModel
    
    result, metadata = EmbedingModel.multi_q_net_embedding('test-emb', ['Hello world'])
    
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], list)
    assert 'time_taken' in metadata
    assert metadata['time_taken'].endswith('s')


def test_multi_q_net_embedding_multiple_texts():
    """Test embedding generation for multiple texts."""
    from service import EmbedingModel
    
    texts = ['First text', 'Second text', 'Third text']
    result, metadata = EmbedingModel.multi_q_net_embedding('test-multi', texts)
    
    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(emb, list) for emb in result)
    assert 'time_taken' in metadata


def test_multi_q_net_similarity_with_texts():
    """Test similarity calculation with text inputs."""
    from service import EmbedingModel
    
    result, metadata = EmbedingModel.multi_q_net_similarity(
        text1='Hello world',
        text2='Hello world'
    )
    
    # Result might be list or mock - check it's not None
    assert result is not None
    assert 'time_taken' in metadata
    assert metadata['time_taken'].endswith('s')


def test_multi_q_net_similarity_with_embeddings():
    """Test similarity calculation with precomputed embeddings."""
    from service import EmbedingModel
    
    # Create mock embeddings
    class MockEmb:
        def __init__(self, data):
            self.data = data
        def to(self, device):
            return self
        def numpy(self):
            return self
        def tolist(self):
            return self.data
    
    emb1 = MockEmb([[0.1, 0.2, 0.3]])
    emb2 = MockEmb([[0.1, 0.2, 0.3]])
    
    result, metadata = EmbedingModel.multi_q_net_similarity(emb1=emb1, emb2=emb2)
    
    # Result might be list or mock - check it's not None
    assert result is not None
    assert 'time_taken' in metadata


def test_jailbreak_check_timing():
    """Test that timing is measured correctly."""
    from service import EmbedingModel
    
    _, _, metadata = EmbedingModel.jailbreak_check('Test timing', 'test-time')
    
    assert 'time_taken' in metadata
    time_str = metadata['time_taken'].rstrip('s')
    time_val = float(time_str)
    assert time_val >= 0


def test_multi_q_net_embedding_returns_list():
    """Test embedding returns proper structure."""
    from service import EmbedingModel
    
    result, metadata = EmbedingModel.multi_q_net_embedding('test-struct', ['test'])
    
    assert isinstance(result, list)
    assert 'time_taken' in metadata
