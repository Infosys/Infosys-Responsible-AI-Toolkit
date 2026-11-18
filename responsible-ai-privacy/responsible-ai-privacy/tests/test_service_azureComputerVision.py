"""Tests for privacy.service.azureComputerVision.ComputerVision"""

import sys
import os
import pytest
from unittest.mock import MagicMock, patch, Mock
from PIL import Image
from io import BytesIO

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def mock_azure_env():
    """Mock Azure environment variables"""
    with patch.dict(os.environ, {
        'API_KEY': 'test-api-key-12345',
        'API_ENDPOINT': 'https://test-region.api.cognitive.microsoft.com/vision/v3.2/read/analyze'
    }):
        yield


@pytest.fixture
def sample_image():
    """Create a sample PIL Image for testing"""
    img = Image.new('RGB', (100, 100), color='white')
    return img


@pytest.fixture
def mock_azure_response():
    """Mock Azure Computer Vision API response"""
    return {
        'readResult': {
            'blocks': [
                {
                    'lines': [
                        {
                            'words': [
                                {
                                    'text': 'Hello',
                                    'boundingPolygon': [
                                        {'x': 10, 'y': 20},
                                        {'x': 50, 'y': 20},
                                        {'x': 50, 'y': 40},
                                        {'x': 10, 'y': 40}
                                    ],
                                    'confidence': 0.98
                                },
                                {
                                    'text': 'World',
                                    'boundingPolygon': [
                                        {'x': 60, 'y': 20},
                                        {'x': 100, 'y': 20},
                                        {'x': 100, 'y': 40},
                                        {'x': 60, 'y': 40}
                                    ],
                                    'confidence': 0.95
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }


def test_computer_vision_process():
    """Test ComputerVision process method"""
    from privacy.service.azureComputerVision import ComputerVision
    
    cv = ComputerVision()
    result = cv.process()
    
    # process() should return self
    assert result is cv


def test_computer_vision_perform_ocr_success(mock_azure_env, sample_image, mock_azure_response):
    """Test successful OCR operation"""
    from privacy.service.azureComputerVision import ComputerVision
    
    # Mock the requests.post response
    mock_response = MagicMock()
    mock_response.json.return_value = mock_azure_response
    mock_response.raise_for_status = MagicMock()
    
    with patch('privacy.service.azureComputerVision.requests.post', return_value=mock_response):
        cv = ComputerVision()
        result = cv.perform_ocr(sample_image)
        
        assert result is not None
        assert isinstance(result, dict)
        assert 'text' in result
        assert 'left' in result
        assert 'top' in result
        assert 'width' in result
        assert 'height' in result
        assert 'conf' in result
        
        # Verify the extracted text
        assert 'Hello' in result['text']
        assert 'World' in result['text']
        assert len(result['text']) == 2
        
        # Verify confidence scores
        assert 0.98 in result['conf']
        assert 0.95 in result['conf']


def test_computer_vision_perform_ocr_bounding_box_calculation(mock_azure_env, sample_image, mock_azure_response):
    """Test bounding box calculation in OCR"""
    from privacy.service.azureComputerVision import ComputerVision
    
    mock_response = MagicMock()
    mock_response.json.return_value = mock_azure_response
    mock_response.raise_for_status = MagicMock()
    
    with patch('privacy.service.azureComputerVision.requests.post', return_value=mock_response):
        cv = ComputerVision()
        result = cv.perform_ocr(sample_image)
        
        # Check first word bounding box
        assert result['left'][0] == 10  # min(10, 10)
        assert result['top'][0] == 20   # min(20, 20)
        assert result['width'][0] == 40  # abs(50 - 10)
        assert result['height'][0] == 20  # abs(40 - 20)


def test_computer_vision_perform_ocr_multiple_lines(mock_azure_env, sample_image):
    """Test OCR with multiple lines of text"""
    from privacy.service.azureComputerVision import ComputerVision
    
    response_multiple_lines = {
        'readResult': {
            'blocks': [
                {
                    'lines': [
                        {
                            'words': [
                                {
                                    'text': 'Line1',
                                    'boundingPolygon': [
                                        {'x': 10, 'y': 10},
                                        {'x': 50, 'y': 10},
                                        {'x': 50, 'y': 30},
                                        {'x': 10, 'y': 30}
                                    ],
                                    'confidence': 0.99
                                }
                            ]
                        },
                        {
                            'words': [
                                {
                                    'text': 'Line2',
                                    'boundingPolygon': [
                                        {'x': 10, 'y': 40},
                                        {'x': 50, 'y': 40},
                                        {'x': 50, 'y': 60},
                                        {'x': 10, 'y': 60}
                                    ],
                                    'confidence': 0.97
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }
    
    mock_response = MagicMock()
    mock_response.json.return_value = response_multiple_lines
    mock_response.raise_for_status = MagicMock()
    
    with patch('privacy.service.azureComputerVision.requests.post', return_value=mock_response):
        cv = ComputerVision()
        result = cv.perform_ocr(sample_image)
        
        assert len(result['text']) == 2
        assert 'Line1' in result['text']
        assert 'Line2' in result['text']


def test_computer_vision_perform_ocr_empty_result(mock_azure_env, sample_image):
    """Test OCR with empty result"""
    from privacy.service.azureComputerVision import ComputerVision
    
    empty_response = {
        'readResult': {
            'blocks': []
        }
    }
    
    mock_response = MagicMock()
    mock_response.json.return_value = empty_response
    mock_response.raise_for_status = MagicMock()
    
    with patch('privacy.service.azureComputerVision.requests.post', return_value=mock_response):
        cv = ComputerVision()
        result = cv.perform_ocr(sample_image)
        
        assert result is not None
        assert len(result['text']) == 0
        assert len(result['left']) == 0


def test_computer_vision_perform_ocr_http_error(mock_azure_env, sample_image):
    """Test OCR when HTTP error occurs"""
    from privacy.service.azureComputerVision import ComputerVision
    import requests
    
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
    
    with patch('privacy.service.azureComputerVision.requests.post', return_value=mock_response):
        cv = ComputerVision()
        
        with pytest.raises(requests.exceptions.HTTPError):
            cv.perform_ocr(sample_image)


def test_computer_vision_perform_ocr_connection_error(mock_azure_env, sample_image):
    """Test OCR when connection error occurs"""
    from privacy.service.azureComputerVision import ComputerVision
    import requests
    
    with patch('privacy.service.azureComputerVision.requests.post', 
               side_effect=requests.exceptions.ConnectionError("Connection failed")):
        cv = ComputerVision()
        
        with pytest.raises(requests.exceptions.ConnectionError):
            cv.perform_ocr(sample_image)


def test_computer_vision_perform_ocr_timeout(mock_azure_env, sample_image):
    """Test OCR when timeout occurs"""
    from privacy.service.azureComputerVision import ComputerVision
    import requests
    
    with patch('privacy.service.azureComputerVision.requests.post', 
               side_effect=requests.exceptions.Timeout("Request timeout")):
        cv = ComputerVision()
        
        with pytest.raises(requests.exceptions.Timeout):
            cv.perform_ocr(sample_image)


def test_computer_vision_perform_ocr_image_conversion(mock_azure_env, sample_image, mock_azure_response):
    """Test that image is properly converted to binary data"""
    from privacy.service.azureComputerVision import ComputerVision
    
    mock_response = MagicMock()
    mock_response.json.return_value = mock_azure_response
    mock_response.raise_for_status = MagicMock()
    
    with patch('privacy.service.azureComputerVision.requests.post', return_value=mock_response) as mock_post:
        cv = ComputerVision()
        cv.perform_ocr(sample_image)
        
        # Verify requests.post was called
        assert mock_post.called
        
        # Verify binary data was sent
        call_kwargs = mock_post.call_args[1]
        assert 'data' in call_kwargs
        assert isinstance(call_kwargs['data'], bytes)


def test_computer_vision_perform_ocr_headers_and_params(mock_azure_env, sample_image, mock_azure_response):
    """Test that correct headers and params are sent"""
    from privacy.service.azureComputerVision import ComputerVision
    
    mock_response = MagicMock()
    mock_response.json.return_value = mock_azure_response
    mock_response.raise_for_status = MagicMock()
    
    with patch('privacy.service.azureComputerVision.requests.post', return_value=mock_response) as mock_post:
        cv = ComputerVision()
        cv.perform_ocr(sample_image)
        
        call_kwargs = mock_post.call_args[1]
        
        # Verify headers exist
        assert 'headers' in call_kwargs
        # Subscription key comes from environment variable, just verify it's present
        assert 'Ocp-Apim-Subscription-Key' in call_kwargs['headers']
        assert call_kwargs['headers']['Content-Type'] == 'application/octet-stream'
        
        # Verify params
        assert 'params' in call_kwargs
        assert call_kwargs['params']['language'] == 'en'
        assert call_kwargs['params']['detectOrientation'] == 'true'


def test_computer_vision_perform_ocr_json_decode_error(mock_azure_env, sample_image):
    """Test OCR when JSON decode fails"""
    from privacy.service.azureComputerVision import ComputerVision
    
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_response.raise_for_status = MagicMock()
    
    with patch('privacy.service.azureComputerVision.requests.post', return_value=mock_response):
        cv = ComputerVision()
        
        with pytest.raises(ValueError):
            cv.perform_ocr(sample_image)


def test_attribute_dict():
    """Test AttributeDict class"""
    from privacy.service.azureComputerVision import AttributeDict
    
    attr_dict = AttributeDict({'key1': 'value1', 'key2': 'value2'})
    
    # Test __getattr__
    assert attr_dict.key1 == 'value1'
    assert attr_dict.key2 == 'value2'
    
    # Test __setattr__
    attr_dict.key3 = 'value3'
    assert attr_dict['key3'] == 'value3'
    
    # Test __delattr__
    del attr_dict.key3
    assert 'key3' not in attr_dict


def test_data_class():
    """Test Data class"""
    from privacy.service.azureComputerVision import Data
    
    # Test class attribute
    assert hasattr(Data, 'encrypted_text')
    assert isinstance(Data.encrypted_text, list)


def test_computer_vision_perform_ocr_with_different_image_formats(mock_azure_env, mock_azure_response):
    """Test OCR with different image formats"""
    from privacy.service.azureComputerVision import ComputerVision
    
    # Create images in different modes
    for mode in ['RGB', 'RGBA', 'L']:
        img = Image.new(mode, (100, 100), color='white')
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_azure_response
        mock_response.raise_for_status = MagicMock()
        
        with patch('privacy.service.azureComputerVision.requests.post', return_value=mock_response):
            cv = ComputerVision()
            result = cv.perform_ocr(img)
            
            assert result is not None
            assert isinstance(result, dict)


def test_computer_vision_perform_ocr_with_kwargs(mock_azure_env, sample_image, mock_azure_response):
    """Test OCR with additional kwargs (even if not used)"""
    from privacy.service.azureComputerVision import ComputerVision
    
    mock_response = MagicMock()
    mock_response.json.return_value = mock_azure_response
    mock_response.raise_for_status = MagicMock()
    
    with patch('privacy.service.azureComputerVision.requests.post', return_value=mock_response):
        cv = ComputerVision()
        result = cv.perform_ocr(sample_image, custom_param='value')
        
        assert result is not None
        assert isinstance(result, dict)
