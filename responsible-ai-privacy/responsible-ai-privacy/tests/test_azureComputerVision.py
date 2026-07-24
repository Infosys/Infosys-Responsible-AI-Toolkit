"""
Tests for privacy.service.azureComputerVision module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
from io import BytesIO
import requests
from privacy.service.azureComputerVision import ComputerVision, AttributeDict, Data


class TestAttributeDict:
    """Test cases for AttributeDict class"""

    def test_attribute_dict_set_get_item(self):
        """Test AttributeDict allows dict-style access"""
        attr_dict = AttributeDict()
        attr_dict['key1'] = 'value1'
        assert attr_dict['key1'] == 'value1'

    def test_attribute_dict_set_get_attribute(self):
        """Test AttributeDict allows attribute-style access"""
        attr_dict = AttributeDict()
        attr_dict.key2 = 'value2'
        assert attr_dict.key2 == 'value2'

    def test_attribute_dict_del_attribute(self):
        """Test AttributeDict allows deletion"""
        attr_dict = AttributeDict()
        attr_dict.key3 = 'value3'
        del attr_dict.key3
        assert 'key3' not in attr_dict

    def test_attribute_dict_init_with_values(self):
        """Test AttributeDict initialization with values"""
        attr_dict = AttributeDict({'a': 1, 'b': 2})
        assert attr_dict.a == 1
        assert attr_dict['b'] == 2


class TestData:
    """Test cases for Data class"""

    def test_data_has_encrypted_text_list(self):
        """Test Data class has encrypted_text attribute"""
        assert hasattr(Data, 'encrypted_text')
        assert isinstance(Data.encrypted_text, list)

    def test_data_encrypted_text_can_append(self):
        """Test encrypted_text list can be modified"""
        Data.encrypted_text = []
        Data.encrypted_text.append('test_text')
        assert 'test_text' in Data.encrypted_text
        # Clean up
        Data.encrypted_text = []


class TestComputerVision:
    """Test cases for ComputerVision class"""

    def test_process_returns_input(self):
        """Test process method returns input unchanged"""
        result = ComputerVision.process("test")
        assert result == "test"
        
        result = ComputerVision.process(123)
        assert result == 123
        
        result = ComputerVision.process({'key': 'value'})
        assert result == {'key': 'value'}

    @patch('privacy.service.azureComputerVision.requests.post')
    @patch('privacy.service.azureComputerVision.apikey', 'test_key')
    @patch('privacy.service.azureComputerVision.apiendpint', 'https://test.cognitiveservices.azure.com/')
    def test_perform_ocr_processes_image(self, mock_post):
        """Test perform_ocr processes image and returns textmap"""
        # Create a mock image
        mock_image = Mock(spec=Image.Image)
        mock_buffer = BytesIO()
        mock_image.save = Mock(side_effect=lambda buf, fmt: buf.write(b'fake_image_data'))
        
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "readResult": {
                "blocks": [
                    {
                        "lines": [
                            {
                                "words": [
                                    {
                                        "text": "Hello",
                                        "boundingPolygon": [
                                            {'x': 10, 'y': 20},
                                            {'x': 50, 'y': 20},
                                            {'x': 50, 'y': 40},
                                            {'x': 10, 'y': 40}
                                        ],
                                        "confidence": 0.95
                                    },
                                    {
                                        "text": "World",
                                        "boundingPolygon": [
                                            {'x': 60, 'y': 20},
                                            {'x': 100, 'y': 20},
                                            {'x': 100, 'y': 40},
                                            {'x': 60, 'y': 40}
                                        ],
                                        "confidence": 0.98
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        mock_post.return_value = mock_response
        
        # Patch BytesIO to track buffer content
        with patch('privacy.service.azureComputerVision.BytesIO') as mock_bytesio_class:
            mock_buffer_instance = BytesIO()
            mock_bytesio_class.return_value = mock_buffer_instance
            
            cv = ComputerVision()
            result = cv.perform_ocr(mock_image)
        
        # Assertions
        assert 'text' in result
        assert 'left' in result
        assert 'top' in result
        assert 'width' in result
        assert 'height' in result
        assert 'conf' in result
        
        assert result['text'] == ['Hello', 'World']
        assert result['left'] == [10, 60]
        assert result['top'] == [20, 20]
        assert result['width'] == [40, 40]
        assert result['height'] == [20, 20]
        assert result['conf'] == [0.95, 0.98]

    @patch('privacy.service.azureComputerVision.requests.post')
    @patch('privacy.service.azureComputerVision.apikey', 'test_key')
    @patch('privacy.service.azureComputerVision.apiendpint', 'https://test.cognitiveservices.azure.com/')
    def test_perform_ocr_with_multiple_blocks(self, mock_post):
        """Test perform_ocr handles multiple text blocks"""
        mock_image = Mock(spec=Image.Image)
        mock_image.save = Mock()
        
        # Mock response with multiple blocks
        mock_response = Mock()
        mock_response.json.return_value = {
            "readResult": {
                "blocks": [
                    {
                        "lines": [
                            {
                                "words": [
                                    {
                                        "text": "First",
                                        "boundingPolygon": [
                                            {'x': 0, 'y': 0},
                                            {'x': 40, 'y': 0},
                                            {'x': 40, 'y': 20},
                                            {'x': 0, 'y': 20}
                                        ],
                                        "confidence": 0.90
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "lines": [
                            {
                                "words": [
                                    {
                                        "text": "Second",
                                        "boundingPolygon": [
                                            {'x': 50, 'y': 30},
                                            {'x': 90, 'y': 30},
                                            {'x': 90, 'y': 50},
                                            {'x': 50, 'y': 50}
                                        ],
                                        "confidence": 0.85
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        mock_post.return_value = mock_response
        
        with patch('privacy.service.azureComputerVision.BytesIO'):
            cv = ComputerVision()
            result = cv.perform_ocr(mock_image)
        
        assert len(result['text']) == 2
        assert result['text'] == ['First', 'Second']
        assert len(result['conf']) == 2

    @patch('privacy.service.azureComputerVision.requests.post')
    @patch('privacy.service.azureComputerVision.apikey', 'test_key')
    @patch('privacy.service.azureComputerVision.apiendpint', 'https://test.cognitiveservices.azure.com/')
    def test_perform_ocr_raises_for_http_error(self, mock_post):
        """Test perform_ocr raises exception on HTTP error"""
        mock_image = Mock(spec=Image.Image)
        mock_image.save = Mock()
        
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("API Error")
        mock_post.return_value = mock_response
        
        with patch('privacy.service.azureComputerVision.BytesIO'):
            cv = ComputerVision()
            with pytest.raises(requests.HTTPError):
                cv.perform_ocr(mock_image)

    @patch('privacy.service.azureComputerVision.requests.post')
    @patch('privacy.service.azureComputerVision.apikey', 'test_key')
    @patch('privacy.service.azureComputerVision.apiendpint', 'https://test.cognitiveservices.azure.com/')
    def test_perform_ocr_with_empty_blocks(self, mock_post):
        """Test perform_ocr handles empty blocks gracefully"""
        mock_image = Mock(spec=Image.Image)
        mock_image.save = Mock()
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "readResult": {
                "blocks": []
            }
        }
        mock_post.return_value = mock_response
        
        with patch('privacy.service.azureComputerVision.BytesIO'):
            cv = ComputerVision()
            result = cv.perform_ocr(mock_image)
        
        assert result['text'] == []
        assert result['left'] == []
        assert result['top'] == []
        assert result['width'] == []
        assert result['height'] == []
        assert result['conf'] == []
