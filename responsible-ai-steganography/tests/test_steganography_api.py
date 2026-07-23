"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Test Suite for Steganography Detection API
"""

import pytest
import json
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from main import create_app


@pytest.fixture
def app():
    """Create test app"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestSteganographyAPI:
    """Test class for Steganography API endpoints"""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'steganography-detection'
    
    def test_api_health_endpoint(self, client):
        """Test API health endpoint"""
        response = client.get('/rai/v1/steganography/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'version' in data
    
    def test_detect_endpoint_clean_text(self, client):
        """Test detection endpoint with clean text"""
        payload = {
            'text': 'This is a normal text without any steganographic content.',
            'user_id': 'test_user'
        }
        
        response = client.post(
            '/rai/v1/steganography/detect',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] == True
        assert data['result']['is_suspicious'] == False
        assert data['result']['confidence_score'] == 0
        assert len(data['result']['detected_techniques']) == 0
    
    def test_detect_endpoint_zero_width_chars(self, client):
        """Test detection with zero-width characters"""
        payload = {
            'text': 'This text has\u200Bhidden\u200Bmessage\u200Bwith zero-width spaces.',
            'user_id': 'test_user'
        }
        
        response = client.post(
            '/rai/v1/steganography/detect',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] == True
        assert data['result']['is_suspicious'] == True
        assert 'zero_width' in data['result']['detected_techniques']
        assert data['result']['confidence_score'] > 0
    
    def test_detect_endpoint_invalid_input(self, client):
        """Test detection endpoint with invalid input"""
        # Missing text field
        payload = {'user_id': 'test_user'}
        
        response = client.post(
            '/rai/v1/steganography/detect',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_detect_endpoint_empty_text(self, client):
        """Test detection endpoint with empty text"""
        payload = {'text': ''}
        
        response = client.post(
            '/rai/v1/steganography/detect',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_batch_detect_endpoint(self, client):
        """Test batch detection endpoint"""
        payload = {
            'texts': [
                {'text': 'Normal text here', 'id': 'text1'},
                {'text': 'Text with\u200Bhidden\u200Bmessage', 'id': 'text2'}
            ],
            'user_id': 'test_user'
        }
        
        response = client.post(
            '/rai/v1/steganography/detect/batch',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] == True
        assert data['total_items'] == 2
        assert len(data['results']) == 2
        
        # First text should be clean
        assert data['results'][0]['id'] == 'text1'
        assert data['results'][0]['success'] == True
        assert data['results'][0]['result']['is_suspicious'] == False
        
        # Second text should be suspicious
        assert data['results'][1]['id'] == 'text2'
        assert data['results'][1]['success'] == True
        assert data['results'][1]['result']['is_suspicious'] == True
    
    def test_batch_detect_empty_list(self, client):
        """Test batch detection with empty list"""
        payload = {'texts': []}
        
        response = client.post(
            '/rai/v1/steganography/detect/batch',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_batch_detect_oversized(self, client):
        """Test batch detection with too many items"""
        # Create payload with more than 100 items
        texts = [{'text': f'Text number {i}', 'id': f'text_{i}'} for i in range(101)]
        payload = {'texts': texts}
        
        response = client.post(
            '/rai/v1/steganography/detect/batch',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Maximum batch size' in data['error']
    
    def test_techniques_endpoint(self, client):
        """Test techniques information endpoint"""
        response = client.get('/rai/v1/steganography/techniques')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] == True
        assert 'techniques' in data
        assert 'total_techniques' in data
        
        # Check that all expected techniques are present
        expected_techniques = ['zero_width', 'whitespace', 'linguistic', 'frequency', 'unicode']
        for technique in expected_techniques:
            assert technique in data['techniques']
            assert 'name' in data['techniques'][technique]
            assert 'description' in data['techniques'][technique]
    
    def test_non_json_content_type(self, client):
        """Test API with non-JSON content type"""
        response = client.post(
            '/rai/v1/steganography/detect',
            data='text=hello',
            content_type='application/x-www-form-urlencoded'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'application/json' in data['error']
    
    def test_index_endpoint(self, client):
        """Test index endpoint"""
        response = client.get('/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['service'] == 'Responsible AI Steganography Detection'
        assert 'endpoints' in data
        assert len(data['endpoints']) > 0


if __name__ == '__main__':
    pytest.main([__file__])
