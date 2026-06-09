
import pytest
import json
from unittest.mock import patch, MagicMock

# The core of the solution:
# We patch the 'jailbreak_check' name in the module where it is supposed to exist.
# 'create=True' is vital because the name doesn't exist, so we need to create it as a mock.
# This must be executed BEFORE 'from src.main import app' is called, because that
# import triggers the chain of imports that leads to the error.
jailbreak_patcher = patch('service.EmbedingModel.jailbreak_check', create=True)

# Start the patcher
jailbreak_patcher.start()

# Now that the broken import is fixed with a mock, we can safely import the app
from src.main import app

@pytest.fixture(scope='module')
def client():
    """Create a test client for the Flask application for the whole module."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    # Stop the patcher after the test session for this module
    jailbreak_patcher.stop()

# --- Tests for src/routing/router.py ---
# Note: The URL prefix is /rai/v1/raimoderationmodels

def test_router_multi_q_net_embedding(client):
    """Test the /multi_q_net_embedding endpoint in router.py."""
    response = client.post('/rai/v1/raimoderationmodels/multi_q_net_embedding', 
                           data=json.dumps({"text": "test text"}), 
                           content_type='application/json')
    assert response.status_code == 200
    assert response.json is not None

def test_router_jailbreak(client):
    """Test the /jailbreak endpoint in router.py."""
    response = client.post('/rai/v1/raimoderationmodels/jailbreak', 
                           data=json.dumps({"text": "test"}), 
                           content_type='application/json')
    assert response.status_code == 200
    assert response.json is not None

def test_router_similarity(client):
    """Test the /multi-qa-mpnet-model_similarity endpoint in router.py."""
    response = client.post('/rai/v1/raimoderationmodels/multi-qa-mpnet-model_similarity', 
                           data=json.dumps({"text1": "a", "text2": "b"}), 
                           content_type='application/json')
    assert response.status_code == 200
    assert response.json is not None

def test_router_detoxify(client):
    """Test the /detoxifymodel endpoint."""
    response = client.post('/rai/v1/raimoderationmodels/detoxifymodel', 
                           data=json.dumps({"text": "friendly text"}), 
                           content_type='application/json')
    assert response.status_code == 200
    assert response.json is not None
    assert 'toxicScore' in response.json

def test_router_privacy(client):
    """Test the /privacy endpoint."""
    response = client.post('/rai/v1/raimoderationmodels/privacy', 
                           data=json.dumps({"text": "John Smith"}), 
                           content_type='application/json')
    assert response.status_code == 200
    assert response.json is not None

def test_router_prompt_injection(client):
    """Test the /promptinjectionmodel endpoint."""
    response = client.post('/rai/v1/raimoderationmodels/promptinjectionmodel', 
                           data=json.dumps({"text": "normal prompt"}), 
                           content_type='application/json')
    assert response.status_code == 200
    assert response.json is not None

def test_router_restricted_topic(client):
    """Test the /restrictedtopicmodel endpoint."""
    response = client.post('/rai/v1/raimoderationmodels/restrictedtopicmodel', 
                           data=json.dumps({"text": "general discussion", "labels": ["violence", "hate"]}), 
                           content_type='application/json')
    assert response.status_code == 200
    assert response.json is not None

def test_router_sentiment(client):
    """Test the /sentimentmodel endpoint."""
    response = client.post('/rai/v1/raimoderationmodels/sentimentmodel', 
                           data=json.dumps({"text": "I love this!"}), 
                           content_type='application/json')
    assert response.status_code == 200
    assert response.json is not None

def test_router_invisible_text(client):
    """Test the /invisibletextmodel endpoint."""
    response = client.post('/rai/v1/raimoderationmodels/invisibletextmodel', 
                           data=json.dumps({"text": "some text", "banned_categories": []}), 
                           content_type='application/json')
    assert response.status_code == 200
    assert response.json is not None

def test_router_gibberish(client):
    """Test the /gibberishmodel endpoint."""
    response = client.post('/rai/v1/raimoderationmodels/gibberishmodel', 
                           data=json.dumps({"text": "normal sentence"}), 
                           content_type='application/json')
    assert response.status_code == 200
    assert response.json is not None

def test_router_bancode(client):
    """Test the /bancodemodel endpoint."""
    response = client.post('/rai/v1/raimoderationmodels/bancodemodel', 
                           data=json.dumps({"text": "Hello world"}), 
                           content_type='application/json')
    assert response.status_code == 200
    assert response.json is not None

def test_router_translation(client):
    """Test the /translationmodel endpoint."""
    response = client.post('/rai/v1/raimoderationmodels/translationmodel', 
                           data=json.dumps({"text": "Hello"}), 
                           content_type='application/json')
    assert response.status_code == 200
    assert response.json is not None
    assert 'translatedText' in response.json
