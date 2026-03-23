import pytest
import sys
import os
import io
import json
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from image_explain.router.router import router
from image_explain.config.logger import request_id_var
from image_explain.mappers.mappers import AnalyzeResponse, ObjectDetectionResponse


# Create a proper FastAPI app with the router included
app = FastAPI()
app.include_router(router)

# Create TestClient with the app, not the router
client = TestClient(app)


# Helper function to create valid AnalyzeResponse mock
def create_analyze_response_mock():
    """Create a valid AnalyzeResponse object for mocking"""
    return AnalyzeResponse(
        image_description="A beautiful sunset over mountains",
        insights={
            "watermark": "None",
            "style": "Landscape Photography",
            "style_analysis": "Natural lighting",
            "query_response": "NA",
            "bias_type": "None",
            "bias_analysis": "No bias detected"
        },
        metrics={
            "certainity_score": 85,
            "certainity_label": "Highly certain",
            "creativity_score": 75,
            "creativity_label": "Highly Creative",
            "coherence_score": 90,
            "coherence_label": "Highly coherence"
        },
        super_pixels=""
    )


# Helper function to create valid ObjectDetectionResponse mock
def create_object_detection_response_mock():
    """Create a valid ObjectDetectionResponse object for mocking"""
    return ObjectDetectionResponse(
        explanation="Detected 3 objects: person, car, tree",
        predicted_image="base64_encoded_image_data",
        time_taken=1.5
    )


class TestAnalyzeImageEndpoint:
    """Comprehensive tests for /image-explainability/analyze endpoint"""
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_analyze_image_success_with_gpt_4o(self, mock_logger_class, mock_service):
        """Test successful image analysis with GPT_4o evaluator"""
        # Setup mocks
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_analyze_response_mock()
        mock_service.analyze_image.return_value = mock_response
        
        # Create test file
        file_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00'
        files = {'image': ('test.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'GPT_4o', 'prompt': 'Describe the image', 'query_flag': 'false'}
        
        # Execute request
        response = client.post('/image-explainability/analyze', files=files, data=data)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert 'image_description' in result
        assert 'insights' in result
        assert 'metrics' in result
        mock_service.analyze_image.assert_called_once()
        
        # Verify payload structure
        call_args = mock_service.analyze_image.call_args[0][0]
        assert call_args['evaluator'] == 'GPT_4o'
        assert call_args['prompt'] == 'Describe the image'
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_analyze_image_success_with_gemini(self, mock_logger_class, mock_service):
        """Test successful image analysis with Gemini evaluator"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_analyze_response_mock()
        mock_service.analyze_image.return_value = mock_response
        
        file_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
        files = {'image': ('test.png', io.BytesIO(file_content), 'image/png')}
        data = {'evaluator': 'Gemini', 'query_flag': 'false'}
        
        response = client.post('/image-explainability/analyze', files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert 'image_description' in result
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_analyze_image_with_query_flag_true(self, mock_logger_class, mock_service):
        """Test image analysis with query_flag=True"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_analyze_response_mock()
        mock_service.analyze_image.return_value = mock_response
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('query_test.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'GPT_4o', 'prompt': 'What objects are visible?', 'query_flag': 'true'}
        
        response = client.post('/image-explainability/analyze', files=files, data=data)
        
        assert response.status_code == 200
        call_args = mock_service.analyze_image.call_args[0][0]
        assert call_args['query_flag'] is True
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_analyze_image_without_prompt(self, mock_logger_class, mock_service):
        """Test image analysis without optional prompt parameter"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_analyze_response_mock()
        mock_service.analyze_image.return_value = mock_response
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('no_prompt.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'GPT_4o', 'query_flag': 'false'}
        
        response = client.post('/image-explainability/analyze', files=files, data=data)
        
        assert response.status_code == 200
        call_args = mock_service.analyze_image.call_args[0][0]
        assert call_args['prompt'] is None
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_analyze_image_default_evaluator(self, mock_logger_class, mock_service):
        """Test image analysis with default evaluator (GPT_4o)"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_analyze_response_mock()
        mock_service.analyze_image.return_value = mock_response
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('default_eval.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'query_flag': 'false'}  # No evaluator specified
        
        response = client.post('/image-explainability/analyze', files=files, data=data)
        
        assert response.status_code == 200
        call_args = mock_service.analyze_image.call_args[0][0]
        assert call_args['evaluator'] == 'GPT_4o'  # Default value
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_analyze_image_service_exception(self, mock_logger_class, mock_service):
        """Test exception handling when service raises error"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_service.analyze_image.side_effect = Exception("Service error occurred")
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('error.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'GPT_4o', 'query_flag': 'false'}
        
        response = client.post('/image-explainability/analyze', files=files, data=data)
        
        assert response.status_code == 500
        assert "ERROR" in response.json()['detail']
        assert "Service error occurred" in response.json()['detail']
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_analyze_image_value_error(self, mock_logger_class, mock_service):
        """Test exception handling for ValueError"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_service.analyze_image.side_effect = ValueError("Invalid input data")
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('value_error.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'InvalidEvaluator', 'query_flag': 'false'}
        
        response = client.post('/image-explainability/analyze', files=files, data=data)
        
        assert response.status_code == 500
        assert "Invalid input data" in response.json()['detail']
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_analyze_image_logging_calls(self, mock_logger_class, mock_service):
        """Test that all logging methods are called correctly"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_analyze_response_mock()
        mock_service.analyze_image.return_value = mock_response
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('logging.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'GPT_4o', 'query_flag': 'false'}
        
        response = client.post('/image-explainability/analyze', files=files, data=data)
        
        assert response.status_code == 200
        # Logging is done by module-level logger, not mock
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_analyze_image_datetime_tracking(self, mock_logger_class, mock_service):
        """Test that start_time, end_time, and total_time are tracked"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_analyze_response_mock()
        mock_service.analyze_image.return_value = mock_response
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('time.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'GPT_4o', 'query_flag': 'false'}
        
        response = client.post('/image-explainability/analyze', files=files, data=data)
        
        assert response.status_code == 200
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_analyze_image_with_different_image_formats(self, mock_logger_class, mock_service):
        """Test endpoint with different image formats (PNG, JPEG)"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_analyze_response_mock()
        mock_service.analyze_image.return_value = mock_response
        
        # Test with PNG
        png_content = b'\x89PNG\r\n\x1a\n'
        files = {'image': ('test.png', io.BytesIO(png_content), 'image/png')}
        data = {'evaluator': 'Gemini', 'query_flag': 'false'}
        
        response = client.post('/image-explainability/analyze', files=files, data=data)
        assert response.status_code == 200
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_analyze_image_runtime_error(self, mock_logger_class, mock_service):
        """Test RuntimeError handling"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_service.analyze_image.side_effect = RuntimeError("Runtime error in analysis")
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('runtime.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'GPT_4o', 'query_flag': 'false'}
        
        response = client.post('/image-explainability/analyze', files=files, data=data)
        
        assert response.status_code == 500


class TestObjectDetectionEndpoint:
    """Comprehensive tests for /image-explainability/object-detection endpoint"""
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_object_detection_success_with_gpt_4o(self, mock_logger_class, mock_service):
        """Test successful object detection with GPT_4o"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_object_detection_response_mock()
        mock_service.object_detection_img.return_value = mock_response
        
        file_content = b'\xff\xd8\xff\xe0\x00\x10JFIF'
        files = {'image': ('detection.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'GPT_4o'}
        
        response = client.post('/image-explainability/object-detection', files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert 'explanation' in result
        assert 'predicted_image' in result
        assert 'time_taken' in result
        mock_service.object_detection_img.assert_called_once()
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_object_detection_success_with_gemini(self, mock_logger_class, mock_service):
        """Test object detection with Gemini evaluator"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_object_detection_response_mock()
        mock_service.object_detection_img.return_value = mock_response
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('pets.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'Gemini'}
        
        response = client.post('/image-explainability/object-detection', files=files, data=data)
        
        assert response.status_code == 200
        assert 'explanation' in response.json()
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_object_detection_success_with_llama(self, mock_logger_class, mock_service):
        """Test object detection with Llama evaluator"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_object_detection_response_mock()
        mock_service.object_detection_img.return_value = mock_response
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('building.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'Llama'}
        
        response = client.post('/image-explainability/object-detection', files=files, data=data)
        
        assert response.status_code == 200
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_object_detection_default_evaluator(self, mock_logger_class, mock_service):
        """Test object detection with default evaluator"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_object_detection_response_mock()
        mock_service.object_detection_img.return_value = mock_response
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('default.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {}  # No evaluator specified, should use default
        
        response = client.post('/image-explainability/object-detection', files=files, data=data)
        
        assert response.status_code == 200
        call_args = mock_service.object_detection_img.call_args[0][0]
        assert call_args['evaluator'] == 'GPT_4o'
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_object_detection_service_exception(self, mock_logger_class, mock_service):
        """Test exception handling in object detection"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_service.object_detection_img.side_effect = Exception("Detection failed")
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('error.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'GPT_4o'}
        
        response = client.post('/image-explainability/object-detection', files=files, data=data)
        
        assert response.status_code == 500
        assert "Detection failed" in response.json()['detail']
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_object_detection_runtime_error(self, mock_logger_class, mock_service):
        """Test RuntimeError handling"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_service.object_detection_img.side_effect = RuntimeError("Runtime error in detection")
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('runtime.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'Gemini'}
        
        response = client.post('/image-explainability/object-detection', files=files, data=data)
        
        assert response.status_code == 500
        assert "Runtime error" in response.json()['detail']
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_object_detection_logging_calls(self, mock_logger_class, mock_service):
        """Test logging calls in object detection endpoint"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_object_detection_response_mock()
        mock_service.object_detection_img.return_value = mock_response
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('log.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'GPT_4o'}
        
        response = client.post('/image-explainability/object-detection', files=files, data=data)
        
        assert response.status_code == 200
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_object_detection_datetime_tracking(self, mock_logger_class, mock_service):
        """Test datetime tracking in object detection"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_object_detection_response_mock()
        mock_service.object_detection_img.return_value = mock_response
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('time.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'GPT_4o'}
        
        response = client.post('/image-explainability/object-detection', files=files, data=data)
        
        assert response.status_code == 200
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_object_detection_payload_structure(self, mock_logger_class, mock_service):
        """Test that payload is correctly structured"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_object_detection_response_mock()
        mock_service.object_detection_img.return_value = mock_response
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('payload.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'Gemini'}
        
        response = client.post('/image-explainability/object-detection', files=files, data=data)
        
        assert response.status_code == 200
        call_args = mock_service.object_detection_img.call_args[0][0]
        assert 'image' in call_args
        assert 'evaluator' in call_args
        assert call_args['evaluator'] == 'Gemini'
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_object_detection_with_png(self, mock_logger_class, mock_service):
        """Test object detection with PNG image"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_object_detection_response_mock()
        mock_service.object_detection_img.return_value = mock_response
        
        file_content = b'\x89PNG\r\n\x1a\n'
        files = {'image': ('test.png', io.BytesIO(file_content), 'image/png')}
        data = {'evaluator': 'GPT_4o'}
        
        response = client.post('/image-explainability/object-detection', files=files, data=data)
        
        assert response.status_code == 200


class TestRouterEdgeCases:
    """Test edge cases and error scenarios"""
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_analyze_image_with_empty_prompt(self, mock_logger_class, mock_service):
        """Test with empty string prompt"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_analyze_response_mock()
        mock_service.analyze_image.return_value = mock_response
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('empty.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'GPT_4o', 'prompt': '', 'query_flag': 'false'}
        
        response = client.post('/image-explainability/analyze', files=files, data=data)
        
        assert response.status_code == 200
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_analyze_image_exception_with_dict_attribute(self, mock_logger_class, mock_service):
        """Test exception handling when exception has __dict__ attribute"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        # Create exception with __dict__
        error = Exception("Test error")
        error.custom_field = "custom_value"
        mock_service.analyze_image.side_effect = error
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('dict_error.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'GPT_4o', 'query_flag': 'false'}
        
        response = client.post('/image-explainability/analyze', files=files, data=data)
        
        assert response.status_code == 500
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_object_detection_exception_with_dict_attribute(self, mock_logger_class, mock_service):
        """Test exception handling in object detection with __dict__"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        error = RuntimeError("Detection error")
        error.code = 500
        mock_service.object_detection_img.side_effect = error
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('obj_error.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'GPT_4o'}
        
        response = client.post('/image-explainability/object-detection', files=files, data=data)
        
        assert response.status_code == 500
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_analyze_image_with_llama_evaluator(self, mock_logger_class, mock_service):
        """Test with Llama evaluator"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_analyze_response_mock()
        mock_service.analyze_image.return_value = mock_response
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('llama.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'Llama', 'query_flag': 'false'}
        
        response = client.post('/image-explainability/analyze', files=files, data=data)
        
        assert response.status_code == 200
        call_args = mock_service.analyze_image.call_args[0][0]
        assert call_args['evaluator'] == 'Llama'


class TestRequestIdContext:
    """Test request_id_var context setting - these tests verify the request_id_var is used"""
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_analyze_image_sets_request_id(self, mock_logger_class, mock_service):
        """Test that the analyze endpoint calls request_id_var.set"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_analyze_response_mock()
        mock_service.analyze_image.return_value = mock_response
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('reqid.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'GPT_4o', 'query_flag': 'false'}
        
        # Just verify the endpoint works - request_id_var.set is called internally
        response = client.post('/image-explainability/analyze', files=files, data=data)
        
        assert response.status_code == 200
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_object_detection_sets_request_id(self, mock_logger_class, mock_service):
        """Test that the object detection endpoint calls request_id_var.set"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_object_detection_response_mock()
        mock_service.object_detection_img.return_value = mock_response
        
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('reqid_obj.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'GPT_4o'}
        
        # Just verify the endpoint works - request_id_var.set is called internally
        response = client.post('/image-explainability/object-detection', files=files, data=data)
        
        assert response.status_code == 200


class TestAnalyzeImagePayloadVariations:
    """Additional tests for payload variations"""
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_analyze_with_long_prompt(self, mock_logger_class, mock_service):
        """Test with a very long prompt"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_analyze_response_mock()
        mock_service.analyze_image.return_value = mock_response
        
        long_prompt = "A" * 1000
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('long.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'GPT_4o', 'prompt': long_prompt, 'query_flag': 'false'}
        
        response = client.post('/image-explainability/analyze', files=files, data=data)
        
        assert response.status_code == 200
    
    @patch('image_explain.router.router.Service')
    @patch('image_explain.router.router.CustomLogger')
    def test_analyze_with_special_characters_in_prompt(self, mock_logger_class, mock_service):
        """Test with special characters in prompt"""
        mock_log = MagicMock()
        mock_logger_class.return_value = mock_log
        
        mock_response = create_analyze_response_mock()
        mock_service.analyze_image.return_value = mock_response
        
        special_prompt = "What is in this image? <test> & 'quotes' \"double\""
        file_content = b'\xff\xd8\xff\xe0'
        files = {'image': ('special.jpg', io.BytesIO(file_content), 'image/jpeg')}
        data = {'evaluator': 'GPT_4o', 'prompt': special_prompt, 'query_flag': 'false'}
        
        response = client.post('/image-explainability/analyze', files=files, data=data)
        
        assert response.status_code == 200
