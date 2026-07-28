"""Tests for sentiment_service with real src code execution.

These tests import and execute the REAL src code with mocked VADER analyzer
to provide actual code coverage of the sentiment service module.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Test by importing REAL src code with mocked heavy dependencies

@pytest.fixture(scope='module', autouse=True)
def setup_mocks():
    """Setup mocks for VADER sentiment analyzer before importing src."""
    # Remove conftest stubs
    for mod in ['service.sentiment_service', 'config.vader', 'config.logger']:
        sys.modules.pop(mod, None)
    
    # Mock VADER analyzer with realistic sentiment detection
    class MockSentimentIntensityAnalyzer:
        def polarity_scores(self, text):
            """Mock that returns realistic sentiment scores based on keywords."""
            if not text or text.strip() == "":
                return {'neg': 0.0, 'neu': 1.0, 'pos': 0.0, 'compound': 0.0}
            
            text_lower = text.lower()
            
            # Positive sentiment keywords
            if any(word in text_lower for word in ['amazing', 'great', 'excellent', 'wonderful', 'best']):
                return {'neg': 0.0, 'neu': 0.2, 'pos': 0.8, 'compound': 0.85}
            
            # Negative sentiment keywords
            if any(word in text_lower for word in ['terrible', 'awful', 'worst', 'hate', 'horrible']):
                return {'neg': 0.8, 'neu': 0.2, 'pos': 0.0, 'compound': -0.85}
            
            # Neutral default
            return {'neg': 0.1, 'neu': 0.8, 'pos': 0.1, 'compound': 0.0}
    
    vader_module = MagicMock()
    vader_module.SentimentIntensityAnalyzer = MockSentimentIntensityAnalyzer
    sys.modules['config.vader'] = vader_module
    
    # Mock logger
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
    
    # Mock werkzeug
    class MockInternalServerError(Exception):
        pass
    
    werkzeug_module = MagicMock()
    werkzeug_module.exceptions = MagicMock()
    werkzeug_module.exceptions.InternalServerError = MockInternalServerError
    sys.modules['werkzeug'] = werkzeug_module
    sys.modules['werkzeug.exceptions'] = werkzeug_module.exceptions
    
    yield
    
    # Cleanup
    for mod in ['config.vader', 'config.logger', 'werkzeug', 'werkzeug.exceptions', 'service.sentiment_service']:
        sys.modules.pop(mod, None)


def test_sentiment_positive():
    """Test positive sentiment detection with positive keywords."""
    from service.sentiment_service import Sentiment
    
    s = Sentiment()
    result = s.scan('This is amazing and wonderful!')
    
    assert isinstance(result, dict)
    assert 'score' in result
    assert 'time_taken' in result
    assert result['score']['compound'] > 0.5
    assert result['time_taken'].endswith('s')


def test_sentiment_negative():
    """Test negative sentiment detection with negative keywords."""
    from service.sentiment_service import Sentiment
    
    s = Sentiment()
    result = s.scan('This is terrible and awful!')
    
    assert isinstance(result, dict)
    assert 'score' in result
    assert result['score']['compound'] < -0.5


def test_sentiment_neutral():
    """Test neutral sentiment detection with neutral text."""
    from service.sentiment_service import Sentiment
    
    s = Sentiment()
    result = s.scan('The meeting is scheduled for tomorrow.')
    
    assert isinstance(result, dict)
    assert 'score' in result
    assert abs(result['score']['compound']) < 0.5


def test_sentiment_score_structure():
    """Test that score dict contains all required VADER components."""
    from service.sentiment_service import Sentiment
    
    s = Sentiment()
    result = s.scan('Test text for structure')
    
    assert 'score' in result
    score = result['score']
    assert 'compound' in score
    assert 'pos' in score
    assert 'neg' in score
    assert 'neu' in score


def test_sentiment_timing():
    """Test that timing information is measured and formatted correctly."""
    from service.sentiment_service import Sentiment
    
    s = Sentiment()
    result = s.scan('Test timing measurement')
    
    assert 'time_taken' in result
    assert result['time_taken'].endswith('s')
    time_val = float(result['time_taken'][:-1])
    assert time_val >= 0.0


def test_sentiment_empty_text():
    """Test handling of empty text input."""
    from service.sentiment_service import Sentiment
    
    s = Sentiment()
    result = s.scan('')
    
    assert isinstance(result, dict)
    assert 'score' in result
    assert result['score']['compound'] == 0.0
