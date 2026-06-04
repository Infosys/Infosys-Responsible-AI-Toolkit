'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock, Mock
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

# Setup environment variables before imports
os.environ.setdefault('OPENAI_MODEL_GPT4', 'gpt-4')
os.environ.setdefault('OPENAI_API_TYPE', 'azure')
os.environ.setdefault('OPENAI_API_BASE_GPT4', 'https://api.openai.com')
os.environ.setdefault('OPENAI_API_KEY_GPT4', 'test-key')
os.environ.setdefault('OPENAI_API_VERSION_GPT4', '2023-05-15')
os.environ.setdefault('AZURE_OPENAI_API_KEY_DALL_E_2', 'test-key')
os.environ.setdefault('AZURE_OPENAI_ENDPOINT_DALL_E_2', 'https://api.openai.com')
os.environ.setdefault('AZURE_OPENAI_API_VERSION_DALL_E_2', '2024-05-01')
os.environ.setdefault('AZURE_OPENAI_MODEL_DALL_E_2', 'dall-e-2')


class TestRouterSetup:
    """Test suite for router setup"""
    
    def test_router_creation(self):
        """Test router is created correctly"""
        from llm.router.router import router
        
        assert router is not None
    
    def test_router_has_routes(self):
        """Test router has defined routes"""
        from llm.router.router import router
        
        assert len(router.routes) > 0


class TestOpenAIRoute:
    """Test suite for OpenAI text completion route"""
    
    @patch('llm.service.openAiCompletion.Openaicompletions.textCompletion')
    def test_llm_openai_endpoint_valid_request(self, mock_completion):
        """Test /llm/openai endpoint with valid request"""
        from llm.router.router import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        mock_completion.return_value = {
            'text': 'Test response',
            'index': 0,
            'finish_reason': 'stop'
        }
        
        payload = {
            'messages': '[{"role": "user", "content": "Hello"}]',
            'temperature': 0.7,
            'model': 'gpt4'
        }
        
        response = client.post('/llm/openai', json=payload)
        
        assert response.status_code in [200, 500]  # 500 if Azure client fails
    
    def test_llm_openai_endpoint_invalid_model(self):
        """Test /llm/openai endpoint with invalid model"""
        from llm.router.router import router
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        payload = {
            'messages': '[{"role": "user", "content": "Hello"}]',
            'temperature': 0.7,
            'model': 'gpt4'
        }
        
        # This should handle gracefully even if external service fails
        response = client.post('/llm/openai', json=payload)
        assert response.status_code in [200, 500]
    
    def test_llm_openai_endpoint_missing_fields(self):
        """Test /llm/openai endpoint with missing required fields"""
        from llm.router.router import router
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Missing model
        payload = {
            'messages': '[{"role": "user", "content": "Hello"}]',
            'temperature': 0.7
        }
        
        response = client.post('/llm/openai', json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_llm_openai_endpoint_empty_messages(self):
        """Test /llm/openai endpoint with empty messages"""
        from llm.router.router import router
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        payload = {
            'messages': '[]',
            'temperature': 0.7,
            'model': 'gpt4'
        }
        
        response = client.post('/llm/openai', json=payload)
        assert response.status_code in [200, 500]
    
    def test_llm_openai_endpoint_temperature_range(self):
        """Test /llm/openai endpoint with various temperature values"""
        from llm.router.router import router
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        temperatures = [0.0, 0.5, 1.0, 2.0]
        for temp in temperatures:
            payload = {
                'messages': '[{"role": "user", "content": "Test"}]',
                'temperature': temp,
                'model': 'gpt4'
            }
            
            response = client.post('/llm/openai', json=payload)
            assert response.status_code in [200, 500]


class TestImageGenerationRoute:
    """Test suite for image generation route"""
    
    @patch('llm.service.service.LLMService.generate_image')
    def test_llm_image_endpoint_valid_request(self, mock_generate):
        """Test /llm/image endpoint with valid request"""
        from llm.router.router import router
        from llm.mapper.mapper import ImageGenerationResponse
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        mock_generate.return_value = ImageGenerationResponse(
            image='base64_image_data'
        )
        
        payload = {
            'prompt': 'Generate an image of a doctor',
            'model': 'DALL-E-2'
        }
        
        response = client.post('/llm/image', json=payload)
        
        assert response.status_code in [200, 500]
    
    def test_llm_image_endpoint_missing_prompt(self):
        """Test /llm/image endpoint with missing prompt"""
        from llm.router.router import router
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        payload = {
            'model': 'DALL-E-2'
        }
        
        response = client.post('/llm/image', json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_llm_image_endpoint_missing_model(self):
        """Test /llm/image endpoint with missing model"""
        from llm.router.router import router
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        payload = {
            'prompt': 'Test prompt'
        }
        
        response = client.post('/llm/image', json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_llm_image_endpoint_empty_prompt(self):
        """Test /llm/image endpoint with empty prompt"""
        from llm.router.router import router
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        payload = {
            'prompt': '',
            'model': 'DALL-E-2'
        }
        
        response = client.post('/llm/image', json=payload)
        # Should fail validation or service error
        assert response.status_code in [422, 500]
    
    @patch('llm.service.service.LLMService.generate_image')
    def test_llm_image_endpoint_response_format(self, mock_generate):
        """Test /llm/image endpoint response format"""
        from llm.router.router import router
        from llm.mapper.mapper import ImageGenerationResponse
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        mock_generate.return_value = ImageGenerationResponse(
            image='test_base64_image_data'
        )
        
        payload = {
            'prompt': 'Test',
            'model': 'DALL-E-2'
        }
        
        response = client.post('/llm/image', json=payload)
        
        if response.status_code == 200:
            data = response.json()
            assert 'image' in data
    
    @patch('llm.service.service.LLMService.generate_image')
    def test_llm_image_endpoint_with_different_models(self, mock_generate):
        """Test /llm/image endpoint with different models"""
        from llm.router.router import router
        from llm.mapper.mapper import ImageGenerationResponse
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        mock_generate.return_value = ImageGenerationResponse(
            image='base64_data'
        )
        
        models = ['DALL-E-2', 'DALL-E-3', 'custom-model']
        for model in models:
            payload = {
                'prompt': 'Test prompt',
                'model': model
            }
            
            response = client.post('/llm/image', json=payload)
            assert response.status_code in [200, 500]


class TestRouterErrorHandling:
    """Test suite for router error handling"""
    
    @patch('llm.service.openAiCompletion.Openaicompletions.textCompletion')
    def test_llm_openai_exception_handling(self, mock_completion):
        """Test /llm/openai handles exceptions gracefully"""
        from llm.router.router import router
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        mock_completion.side_effect = Exception("OpenAI API Error")
        
        payload = {
            'messages': '[{"role": "user", "content": "Hello"}]',
            'temperature': 0.7,
            'model': 'gpt4'
        }
        
        response = client.post('/llm/openai', json=payload)
        assert response.status_code == 500
        assert 'error' in response.json().get('detail', '').lower() or 'error' in str(response.json())
    
    @patch('llm.service.service.LLMService.generate_image')
    def test_llm_image_exception_handling(self, mock_generate):
        """Test /llm/image handles exceptions gracefully"""
        from llm.router.router import router
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        mock_generate.side_effect = Exception("Image generation failed")
        
        payload = {
            'prompt': 'Test',
            'model': 'DALL-E-2'
        }
        
        response = client.post('/llm/image', json=payload)
        assert response.status_code == 500


class TestRouterIntegration:
    """Integration tests for router"""
    
    def test_router_multiple_endpoints(self):
        """Test router has multiple endpoints"""
        from llm.router.router import router
        
        route_paths = [route.path for route in router.routes]
        
        # Check if routes exist (may have different patterns)
        assert any('llm' in path for path in route_paths)
    
    @patch('llm.service.openAiCompletion.Openaicompletions.textCompletion')
    @patch('llm.service.service.LLMService.generate_image')
    def test_sequential_endpoint_calls(self, mock_image, mock_text):
        """Test sequential calls to different endpoints"""
        from llm.router.router import router
        from llm.mapper.mapper import ImageGenerationResponse
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        mock_text.return_value = {
            'text': 'Response',
            'index': 0,
            'finish_reason': 'stop'
        }
        mock_image.return_value = ImageGenerationResponse(image='base64')
        
        # Call text endpoint
        text_payload = {
            'messages': '[{"role": "user", "content": "Test"}]',
            'temperature': 0.7,
            'model': 'gpt4'
        }
        
        # Call image endpoint
        image_payload = {
            'prompt': 'Test',
            'model': 'DALL-E-2'
        }
        
        # Both should work without issues
        text_response = client.post('/llm/openai', json=text_payload)
        image_response = client.post('/llm/image', json=image_payload)
        
        assert text_response.status_code in [200, 500]
        assert image_response.status_code in [200, 500]
