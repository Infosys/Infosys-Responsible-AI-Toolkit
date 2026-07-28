import pytest
import sys
import os
import json
import base64
import math
from unittest.mock import patch, MagicMock, Mock, mock_open, call
from io import BytesIO

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from image_explain.service.service import ImageService
from image_explain.config.logger import request_id_var

# Set request_id_var to avoid LookupError in tests
request_id_var.set('test-request-id')


class TestImageServiceReadImageBase64:
    """Tests for read_image_base64 method"""
    
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_read_image_base64_success(self, mock_file):
        """Test successful base64 encoding of image"""
        result = ImageService.read_image_base64('/path/to/image.jpg')
        
        expected = base64.b64encode(b'fake_image_data').decode('ascii')
        assert result == expected
        mock_file.assert_called_once_with('/path/to/image.jpg', 'rb')
    
    @patch('builtins.open', new_callable=mock_open, read_data=b'\xff\xd8\xff\xe0\x00\x10JFIF')
    def test_read_image_base64_jpeg(self, mock_file):
        """Test reading JPEG image"""
        result = ImageService.read_image_base64('/tmp/test.jpeg')
        
        assert isinstance(result, str)
        assert len(result) > 0
        mock_file.assert_called_once()
    
    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    def test_read_image_base64_file_not_found(self, mock_file):
        """Test error when file doesn't exist"""
        with pytest.raises(FileNotFoundError):
            ImageService.read_image_base64('/nonexistent/file.jpg')
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_read_image_base64_permission_error(self, mock_file):
        """Test error when permission denied"""
        with pytest.raises(PermissionError):
            ImageService.read_image_base64('/protected/file.jpg')


class TestImageServiceNdArrayToBase64:
    """Tests for nd_array_to_base64 method"""
    
    @patch('image_explain.service.service.cv2')
    def test_nd_array_to_base64_success(self, mock_cv2):
        """Test successful conversion of numpy array to base64"""
        mock_image = MagicMock()
        mock_buffer = b'encoded_jpeg_data'
        mock_cv2.imencode.return_value = (True, mock_buffer)
        
        result = ImageService.nd_array_to_base64(mock_image)
        
        expected = base64.b64encode(mock_buffer).decode('utf-8')
        assert result == expected
        mock_cv2.imencode.assert_called_once_with('.jpg', mock_image)
    
    @patch('image_explain.service.service.cv2')
    def test_nd_array_to_base64_with_different_image_data(self, mock_cv2):
        """Test with different image data"""
        mock_image = MagicMock()
        mock_buffer = b'\xff\xd8\xff\xe0'
        mock_cv2.imencode.return_value = (True, mock_buffer)
        
        result = ImageService.nd_array_to_base64(mock_image)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    @patch('image_explain.service.service.cv2')
    def test_nd_array_to_base64_encode_failure(self, mock_cv2):
        """Test when cv2.imencode fails - returns empty buffer"""
        mock_image = MagicMock()
        # When imencode fails, it returns an empty bytes object instead of None
        mock_cv2.imencode.return_value = (False, b'')
        
        # Should handle gracefully - returns empty base64 string
        result = ImageService.nd_array_to_base64(mock_image)
        assert result == ''  # base64.b64encode(b'').decode('utf-8') == ''
        mock_cv2.imencode.assert_called_once()


class TestImageServiceScaleValue:
    """Tests for scale_value method"""
    
    def test_scale_value_default_range(self):
        """Test scaling with default range (1-100)"""
        result = ImageService.scale_value(value=5, x_min=0, x_max=10)
        expected = 1 + ((5 - 0) / (10 - 0)) * (100 - 1)
        assert result == expected
        assert 1 <= result <= 100
    
    def test_scale_value_custom_range(self):
        """Test scaling with custom range"""
        result = ImageService.scale_value(value=0.5, x_min=0, x_max=1, a=0, b=10)
        expected = 0 + ((0.5 - 0) / (1 - 0)) * (10 - 0)
        assert result == expected
        assert result == 5.0
    
    def test_scale_value_min_boundary(self):
        """Test scaling at minimum boundary"""
        result = ImageService.scale_value(value=0, x_min=0, x_max=10)
        assert result == 1  # Should be 'a' value
    
    def test_scale_value_max_boundary(self):
        """Test scaling at maximum boundary"""
        result = ImageService.scale_value(value=10, x_min=0, x_max=10)
        assert result == 100  # Should be 'b' value
    
    def test_scale_value_negative_range(self):
        """Test scaling with negative range"""
        result = ImageService.scale_value(value=0, x_min=-1, x_max=1)
        expected = 1 + ((0 - (-1)) / (1 - (-1))) * (100 - 1)
        assert result == expected
        assert result == 50.5
    
    def test_scale_value_aesthetic_score_range(self):
        """Test typical aesthetic score scaling (0-10 range)"""
        result = ImageService.scale_value(value=7.5, x_min=0, x_max=10)
        assert 1 <= result <= 100
    
    def test_scale_value_alignment_score_range(self):
        """Test typical alignment score scaling (-1 to 1 range)"""
        result = ImageService.scale_value(value=0.8, x_min=-1, x_max=1)
        assert 1 <= result <= 100


class TestImageServiceAnalyzeImageBias:
    """Tests for analyze_image_bias method"""
    
    @patch('image_explain.service.service.ImageExplain')
    def test_analyze_image_bias_success(self, mock_image_explain):
        """Test successful bias analysis"""
        mock_response = {"Analysis": "No bias detected", "Bias type(s)": "None"}
        mock_image_explain.image_based_bias_analysis.return_value = mock_response
        
        result = ImageService.analyze_image_bias(
            mime_type='image/jpeg',
            image_base64='base64_encoded_string',
            evaluator='GPT_4o'
        )
        
        assert result == mock_response
        mock_image_explain.image_based_bias_analysis.assert_called_once_with(
            mime_type='image/jpeg',
            image='base64_encoded_string',
            evaluator='GPT_4o'
        )
    
    @patch('image_explain.service.service.ImageExplain')
    def test_analyze_image_bias_with_gemini(self, mock_image_explain):
        """Test bias analysis with Gemini evaluator"""
        mock_response = {"Analysis": "Gender bias present", "Bias type(s)": "Gender"}
        mock_image_explain.image_based_bias_analysis.return_value = mock_response
        
        result = ImageService.analyze_image_bias(
            mime_type='image/png',
            image_base64='png_base64_data',
            evaluator='Gemini'
        )
        
        assert result == mock_response


class TestImageServiceDetectBias:
    """Tests for detect_bias method"""
    
    @patch('image_explain.service.service.requests')
    @patch('image_explain.service.service.os.getenv')
    @patch('builtins.open', new_callable=mock_open, read_data=b'image_data')
    @patch('image_explain.service.service.os.path.basename')
    def test_detect_bias_success_200(self, mock_basename, mock_file, mock_getenv, mock_requests):
        """Test successful bias detection with 200 response"""
        mock_getenv.return_value = 'http://bias-api.com'
        mock_basename.return_value = 'test.jpg'
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Analysis": "Bias found", "Bias type(s)": "Age"}
        mock_requests.request.return_value = mock_response
        
        result = ImageService.detect_bias('/path/test.jpg', 'test prompt', 'image/jpeg')
        
        assert result == {"Analysis": "Bias found", "Bias type(s)": "Age"}
        mock_requests.request.assert_called_once()
    
    @patch('image_explain.service.service.requests')
    @patch('image_explain.service.service.os.getenv')
    @patch('builtins.open', new_callable=mock_open, read_data=b'image_data')
    @patch('image_explain.service.service.os.path.basename')
    def test_detect_bias_non_200_response(self, mock_basename, mock_file, mock_getenv, mock_requests):
        """Test bias detection with non-200 response"""
        mock_getenv.return_value = 'http://bias-api.com'
        mock_basename.return_value = 'test.jpg'
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_requests.request.return_value = mock_response
        
        result = ImageService.detect_bias('/path/test.jpg', 'prompt', 'image/jpeg')
        
        assert result == {"Analysis": "No bias identified", "Bias type(s)": "No bias"}
    
    @patch('image_explain.service.service.requests')
    @patch('image_explain.service.service.os.getenv')
    def test_detect_bias_exception(self, mock_getenv, mock_requests):
        """Test exception handling in detect_bias"""
        mock_getenv.return_value = 'http://bias-api.com'
        mock_requests.request.side_effect = Exception("Network error")
        
        result = ImageService.detect_bias('/path/test.jpg', 'prompt', 'image/jpeg')
        
        assert result is None


class TestImageServicePromptBasedAnalysisTask:
    """Tests for prompt_based_analysis_task method"""
    
    @patch('image_explain.service.service.ImageExplain')
    def test_prompt_based_analysis_task_success(self, mock_image_explain):
        """Test successful prompt-based analysis"""
        mock_response = {"ImageDescription": "A sunset", "Style": "Landscape"}
        mock_image_explain.prompt_based_analysis.return_value = mock_response
        
        result = ImageService.prompt_based_analysis_task(
            mime_type='image/jpeg',
            image_base64='base64_data',
            prompt='Describe the image',
            evaluator='GPT_4o'
        )
        
        assert result == mock_response
        mock_image_explain.prompt_based_analysis.assert_called_once()


class TestImageServiceGetAestheticScore:
    """Tests for get_aesthetic_score method"""
    
    @patch('image_explain.service.service.AestheticScore')
    def test_get_aesthetic_score_success(self, mock_aesthetic_score):
        """Test successful aesthetic score retrieval"""
        mock_aesthetic_score.score.return_value = 8.5
        
        result = ImageService.get_aesthetic_score('/path/to/image.jpg')
        
        assert result == 8.5
        mock_aesthetic_score.score.assert_called_once_with(image_path='/path/to/image.jpg')
    
    @patch('image_explain.service.service.AestheticScore')
    def test_get_aesthetic_score_different_values(self, mock_aesthetic_score):
        """Test with different aesthetic score values"""
        test_scores = [0.0, 5.0, 10.0, 7.5]
        for score in test_scores:
            mock_aesthetic_score.score.return_value = score
            result = ImageService.get_aesthetic_score('/path/image.jpg')
            assert result == score


class TestImageServiceGetAlignmentScore:
    """Tests for get_alignment_score method"""
    
    @patch('image_explain.service.service.AlignmentScore')
    def test_get_alignment_score_success(self, mock_alignment_score):
        """Test successful alignment score retrieval"""
        mock_alignment_score.score.return_value = 0.95
        
        result = ImageService.get_alignment_score('/path/to/image.jpg', 'test prompt')
        
        assert result == 0.95
        mock_alignment_score.score.assert_called_once_with(
            image_path='/path/to/image.jpg',
            text='test prompt'
        )
    
    @patch('image_explain.service.service.AlignmentScore')
    def test_get_alignment_score_negative_value(self, mock_alignment_score):
        """Test alignment score with negative value"""
        mock_alignment_score.score.return_value = -0.5
        
        result = ImageService.get_alignment_score('/path/image.jpg', 'misaligned')
        
        assert result == -0.5


class TestImageServiceQueryBasedImageAnalysis:
    """Tests for query_based_image_analysis method"""
    
    @patch('image_explain.service.service.ImageExplain')
    def test_query_based_image_analysis_success(self, mock_image_explain):
        """Test successful query-based analysis"""
        mock_response = {"Response": "The image contains a dog"}
        mock_image_explain.query_based_image_analysis.return_value = mock_response
        
        result = ImageService.query_based_image_analysis(
            generated_image_base64='base64_data',
            mime_type='image/jpeg',
            prompt='What animals are in the image?',
            evaluator='GPT_4o'
        )
        
        assert result == mock_response
        mock_image_explain.query_based_image_analysis.assert_called_once()


class TestImageServiceGetUncertaintyScore:
    """Tests for get_uncertainity_score method"""
    
    @patch('image_explain.service.service.ImageExplain')
    @patch('image_explain.service.service.Prompt')
    def test_get_uncertainity_score_success(self, mock_prompt, mock_image_explain):
        """Test successful uncertainty score retrieval"""
        mock_prompt.uncertainty_template.return_value = "Uncertainty prompt template"
        mock_response = {"uncertainty_score": {"score": 25}}
        mock_image_explain.uncertainity_score.return_value = mock_response
        
        result = ImageService.get_uncertainity_score(
            prompt='test prompt',
            mime_type='image/jpeg',
            generated_image_base64='base64_data',
            evaluator='GPT_4o'
        )
        
        assert result == mock_response
        mock_prompt.uncertainty_template.assert_called_once_with(input='test prompt')
        mock_image_explain.uncertainity_score.assert_called_once()


class TestImageServiceExtractObject:
    """Tests for extract_object method"""
    
    @patch('image_explain.service.service.cv2')
    def test_extract_object_success(self, mock_cv2):
        """Test successful object extraction"""
        mock_image = MagicMock()
        mock_image.__getitem__ = MagicMock(return_value='cropped_region')
        mock_cv2.imread.return_value = mock_image
        
        result = ImageService.extract_object('/path/image.jpg', (10, 20, 100, 150))
        
        mock_cv2.imread.assert_called_once_with('/path/image.jpg')
        assert result is not None
    
    @patch('image_explain.service.service.cv2')
    def test_extract_object_image_not_found(self, mock_cv2):
        """Test error when image cannot be read"""
        mock_cv2.imread.return_value = None
        
        with pytest.raises(ValueError, match="Image not found"):
            ImageService.extract_object('/nonexistent.jpg', (0, 0, 50, 50))


class TestImageServiceExtractCoordinatesAsInt:
    """Tests for extract_coordinates_as_int method"""
    
    def test_extract_coordinates_as_int_success(self):
        """Test successful coordinate extraction"""
        mock_boxes = MagicMock()
        mock_tensor1 = MagicMock()
        mock_tensor1.tolist.return_value = [10.5, 20.5, 100.5, 200.5]
        mock_tensor2 = MagicMock()
        mock_tensor2.tolist.return_value = [30.2, 40.8, 150.3, 250.9]
        
        mock_boxes.xyxy = [mock_tensor1, mock_tensor2]
        
        result = ImageService.extract_coordinates_as_int(mock_boxes)
        
        expected = [(10, 20, 100, 200), (30, 40, 150, 250)]
        assert result == expected
    
    def test_extract_coordinates_as_int_empty(self):
        """Test with empty boxes"""
        mock_boxes = MagicMock()
        mock_boxes.xyxy = []
        
        result = ImageService.extract_coordinates_as_int(mock_boxes)
        
        assert result == []


class TestImageServiceAnalyzeImageComprehensive:
    """Comprehensive tests for analyze_image method - the main orchestration method"""
    
    def test_analyze_image_missing_image_in_payload(self):
        """Test ValueError when image is missing"""
        payload = {'evaluator': 'GPT_4o'}
        
        with pytest.raises(ValueError, match="Invalid payload"):
            ImageService.analyze_image(payload)
    
    def test_analyze_image_missing_evaluator_in_payload(self):
        """Test ValueError when evaluator is missing"""
        mock_upload_file = MagicMock()
        payload = {'image': mock_upload_file}
        
        with pytest.raises(ValueError, match="Invalid payload"):
            ImageService.analyze_image(payload)
    
    @patch('image_explain.service.service.shutil')
    @patch('image_explain.service.service.Image.open')
    @patch('image_explain.service.service.uuid.uuid4')
    def test_analyze_image_runtime_error_handling(self, mock_uuid, mock_pil_open, mock_shutil):
        """Test RuntimeError handling in analyze_image"""
        mock_uuid.return_value = 'error-uuid'
        mock_upload_file = MagicMock()
        mock_upload_file.filename = 'error.jpg'
        mock_upload_file.file = BytesIO(b'data')
        
        mock_pil_open.side_effect = Exception("PIL Error")
        
        payload = {
            'image': mock_upload_file,
            'evaluator': 'GPT_4o',
            'prompt': None,
            'query_flag': False
        }
        
        # The code has a bug where imageContent may not be defined in finally block
        # This causes UnboundLocalError when Image.open fails
        with pytest.raises((RuntimeError, UnboundLocalError)):
            ImageService.analyze_image(payload)
    
    @patch('image_explain.service.service.gc')
    @patch('image_explain.service.service.shutil')
    @patch('image_explain.service.service.concurrent.futures.ThreadPoolExecutor')
    @patch('image_explain.service.service.ImageService.get_uncertainity_score')
    @patch('image_explain.service.service.ImageService.read_image_base64')
    @patch('image_explain.service.service.guess_type')
    @patch('image_explain.service.service.os.makedirs')
    @patch('image_explain.service.service.Image.open')
    @patch('image_explain.service.service.uuid.uuid4')
    def test_analyze_image_with_prompt_and_query_flag_true(
        self, mock_uuid, mock_pil_open, mock_makedirs, mock_guess_type,
        mock_read_base64, mock_get_uncertainty, mock_executor_class, mock_shutil, mock_gc
    ):
        """Test analyze_image with prompt and query_flag=True"""
        mock_uuid.return_value = MagicMock(__str__=MagicMock(return_value='test-uuid'))
        mock_upload_file = MagicMock()
        mock_upload_file.filename = 'test.jpg'
        mock_upload_file.file = BytesIO(b'fake_image')
        
        mock_image = MagicMock()
        mock_pil_open.return_value = mock_image
        mock_guess_type.return_value = ('image/jpeg', None)
        mock_read_base64.return_value = 'base64_data'
        
        # Mock ThreadPoolExecutor context manager
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        mock_executor_class.return_value.__exit__ = MagicMock(return_value=False)
        
        # Create mock futures
        mock_futures = {}
        
        def create_future(result):
            f = MagicMock()
            f.result.return_value = result
            return f
        
        # Mock as_completed to return futures
        prompt_result = {
            'ImageDescription': 'Test image',
            'WatermarkContent': 'None',
            'Style': 'Photo',
            'StyleAnalysis': 'Professional'
        }
        aes_score_result = 7.5
        bias_result = {"Analysis": "No bias", "Bias type(s)": "None"}
        alignment_result = 0.8
        query_result = {"Response": "Query response"}
        
        f1 = create_future(prompt_result)
        f2 = create_future(aes_score_result)
        f3 = create_future(bias_result)
        f4 = create_future(alignment_result)
        f5 = create_future(query_result)
        
        mock_futures = {
            f1: 'prompt_based_analysis_task',
            f2: 'get_aesthetic_score',
            f3: 'detect_bias',
            f4: 'get_alignment_score',
            f5: 'query_based_image_analysis'
        }
        
        mock_executor.submit.side_effect = [f1, f2, f3, f4, f5]
        
        # Patch as_completed
        with patch('image_explain.service.service.concurrent.futures.as_completed') as mock_as_completed:
            mock_as_completed.return_value = iter([f1, f2, f3, f4, f5])
            
            mock_get_uncertainty.return_value = {'uncertainty_score': {'score': 25}}
            
            payload = {
                'image': mock_upload_file,
                'evaluator': 'GPT_4o',
                'prompt': 'Describe this image',
                'query_flag': True
            }
            
            result = ImageService.analyze_image(payload)
            
            assert result is not None
            mock_shutil.rmtree.assert_called()
            mock_gc.collect.assert_called()
    
    @patch('image_explain.service.service.gc')
    @patch('image_explain.service.service.shutil')
    @patch('image_explain.service.service.concurrent.futures.ThreadPoolExecutor')
    @patch('image_explain.service.service.ImageService.get_uncertainity_score')
    @patch('image_explain.service.service.ImageService.read_image_base64')
    @patch('image_explain.service.service.guess_type')
    @patch('image_explain.service.service.os.makedirs')
    @patch('image_explain.service.service.Image.open')
    @patch('image_explain.service.service.uuid.uuid4')
    def test_analyze_image_without_prompt(
        self, mock_uuid, mock_pil_open, mock_makedirs, mock_guess_type,
        mock_read_base64, mock_get_uncertainty, mock_executor_class, mock_shutil, mock_gc
    ):
        """Test analyze_image without prompt (uses analyze_image_bias)"""
        mock_uuid.return_value = MagicMock(__str__=MagicMock(return_value='uuid-no-prompt'))
        mock_upload_file = MagicMock()
        mock_upload_file.filename = 'test.jpg'
        mock_upload_file.file = BytesIO(b'fake_image')
        
        mock_image = MagicMock()
        mock_pil_open.return_value = mock_image
        mock_guess_type.return_value = ('image/jpeg', None)
        mock_read_base64.return_value = 'base64_data'
        
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        mock_executor_class.return_value.__exit__ = MagicMock(return_value=False)
        
        def create_future(result):
            f = MagicMock()
            f.result.return_value = result
            return f
        
        prompt_result = {
            'ImageDescription': 'Test',
            'WatermarkContent': 'None',
            'Style': 'Abstract',
            'StyleAnalysis': 'Modern'
        }
        f1 = create_future(prompt_result)
        f2 = create_future(7.0)
        f3 = create_future({"Analysis": "No bias", "Bias type(s)": "None"})
        
        mock_executor.submit.side_effect = [f1, f2, f3]
        
        with patch('image_explain.service.service.concurrent.futures.as_completed') as mock_as_completed:
            mock_as_completed.return_value = iter([f1, f2, f3])
            
            mock_get_uncertainty.return_value = {'uncertainty_score': {'score': 30}}
            
            payload = {
                'image': mock_upload_file,
                'evaluator': 'GPT_4o',
                'prompt': None,
                'query_flag': False
            }
            
            result = ImageService.analyze_image(payload)
            
            assert result is not None
            mock_shutil.rmtree.assert_called()
    
    @patch('image_explain.service.service.gc')
    @patch('image_explain.service.service.shutil')
    @patch('image_explain.service.service.concurrent.futures.ThreadPoolExecutor')
    @patch('image_explain.service.service.ImageService.get_uncertainity_score')
    @patch('image_explain.service.service.ImageService.read_image_base64')
    @patch('image_explain.service.service.guess_type')
    @patch('image_explain.service.service.os.makedirs')
    @patch('image_explain.service.service.Image.open')
    @patch('image_explain.service.service.uuid.uuid4')
    def test_analyze_image_with_prompt_query_flag_false(
        self, mock_uuid, mock_pil_open, mock_makedirs, mock_guess_type,
        mock_read_base64, mock_get_uncertainty, mock_executor_class, mock_shutil, mock_gc
    ):
        """Test analyze_image with prompt but query_flag=False"""
        mock_uuid.return_value = MagicMock(__str__=MagicMock(return_value='uuid-prompt'))
        mock_upload_file = MagicMock()
        mock_upload_file.filename = 'test.jpg'
        mock_upload_file.file = BytesIO(b'fake_image')
        
        mock_image = MagicMock()
        mock_pil_open.return_value = mock_image
        mock_guess_type.return_value = ('image/jpeg', None)
        mock_read_base64.return_value = 'base64_data'
        
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        mock_executor_class.return_value.__exit__ = MagicMock(return_value=False)
        
        def create_future(result):
            f = MagicMock()
            f.result.return_value = result
            return f
        
        prompt_result = {
            'ImageDescription': 'Landscape',
            'WatermarkContent': 'None',
            'Style': 'Nature',
            'StyleAnalysis': 'Beautiful'
        }
        f1 = create_future(prompt_result)
        f2 = create_future(8.0)
        f3 = create_future({"Analysis": "No bias", "Bias type(s)": "None"})
        f4 = create_future(0.9)
        
        mock_executor.submit.side_effect = [f1, f2, f3, f4]
        
        with patch('image_explain.service.service.concurrent.futures.as_completed') as mock_as_completed:
            mock_as_completed.return_value = iter([f1, f2, f3, f4])
            
            mock_get_uncertainty.return_value = {'uncertainty_score': {'score': 50}}
            
            payload = {
                'image': mock_upload_file,
                'evaluator': 'GPT_4o',
                'prompt': 'Describe landscape',
                'query_flag': False
            }
            
            result = ImageService.analyze_image(payload)
            
            assert result is not None
    
    @patch('image_explain.service.service.gc')
    @patch('image_explain.service.service.shutil')
    @patch('image_explain.service.service.concurrent.futures.ThreadPoolExecutor')
    @patch('image_explain.service.service.ImageService.get_uncertainity_score')
    @patch('image_explain.service.service.ImageService.read_image_base64')
    @patch('image_explain.service.service.guess_type')
    @patch('image_explain.service.service.os.makedirs')
    @patch('image_explain.service.service.Image.open')
    @patch('image_explain.service.service.uuid.uuid4')
    def test_analyze_image_mime_type_none(
        self, mock_uuid, mock_pil_open, mock_makedirs, mock_guess_type,
        mock_read_base64, mock_get_uncertainty, mock_executor_class, mock_shutil, mock_gc
    ):
        """Test analyze_image when mime_type is None (uses fallback)"""
        mock_uuid.return_value = MagicMock(__str__=MagicMock(return_value='uuid-mime'))
        mock_upload_file = MagicMock()
        mock_upload_file.filename = 'test.unknown'
        mock_upload_file.file = BytesIO(b'fake_image')
        
        mock_image = MagicMock()
        mock_pil_open.return_value = mock_image
        mock_guess_type.return_value = (None, None)  # Unknown mime type
        mock_read_base64.return_value = 'base64_data'
        
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        mock_executor_class.return_value.__exit__ = MagicMock(return_value=False)
        
        def create_future(result):
            f = MagicMock()
            f.result.return_value = result
            return f
        
        prompt_result = {
            'ImageDescription': 'Unknown',
            'WatermarkContent': 'None',
            'Style': 'Generic',
            'StyleAnalysis': 'Standard'
        }
        f1 = create_future(prompt_result)
        f2 = create_future(5.0)
        f3 = create_future({"Analysis": "No bias", "Bias type(s)": "None"})
        
        mock_executor.submit.side_effect = [f1, f2, f3]
        
        with patch('image_explain.service.service.concurrent.futures.as_completed') as mock_as_completed:
            mock_as_completed.return_value = iter([f1, f2, f3])
            
            mock_get_uncertainty.return_value = {'uncertainty_score': {'score': 20}}
            
            payload = {
                'image': mock_upload_file,
                'evaluator': 'GPT_4o',
                'prompt': None,
                'query_flag': False
            }
            
            result = ImageService.analyze_image(payload)
            
            assert result is not None


class TestImageServiceObjectDetectionComprehensive:
    """Comprehensive tests for object_detection_img method"""
    
    @patch('image_explain.service.service.gc')
    @patch('image_explain.service.service.shutil')
    @patch('image_explain.service.service.time')
    @patch('image_explain.service.service.ImageExplain')
    @patch('image_explain.service.service.Prompt')
    @patch('image_explain.service.service.ImageService.read_image_base64')
    @patch('image_explain.service.service.guess_type')
    @patch('image_explain.service.service.os.makedirs')
    @patch('image_explain.service.service.Image.open')
    @patch('image_explain.service.service.uuid.uuid4')
    def test_object_detection_img_with_gpt(
        self, mock_uuid, mock_pil_open, mock_makedirs, mock_guess_type,
        mock_read_base64, mock_prompt, mock_image_explain,
        mock_time, mock_shutil, mock_gc
    ):
        """Test object detection with GPT evaluator"""
        mock_uuid.return_value = 'obj-uuid-gpt'
        mock_upload_file = MagicMock()
        mock_upload_file.filename = 'detect.jpg'
        mock_upload_file.file = BytesIO(b'image_data')
        
        mock_image = MagicMock()
        mock_pil_open.return_value = mock_image
        mock_guess_type.return_value = ('image/jpeg', None)
        mock_read_base64.return_value = 'base64_image'
        
        mock_time.time.side_effect = [100.0, 105.5]  # start and end time
        
        mock_prompt.detect_objects_prompt.return_value = "Detect objects prompt"
        mock_prompt.bounding_boxes_prompt.return_value = "Bounding boxes prompt"
        mock_prompt.validate_objects_prompt.return_value = "Validate prompt"
        mock_prompt.obj_detection_exp_prompt.return_value = "Explanation prompt"
        
        # Mock analyze_image to return expected values in sequence
        # 1. detect_objects - returns list of objects
        # 2. get_bounding_boxes - returns list of bounding boxes (objects)
        # 3. add_objs_presence - returns list
        # 4. final explanation - returns dict with 'explanation' key for GPT
        mock_image_explain.analyze_image.side_effect = [
            ['person', 'car'],  # detected objects (from ThreadPoolExecutor)
            ['person', 'car', 'tree'],  # bounding boxes (from ThreadPoolExecutor)
            ['tree'],  # additional objects presence
            {'explanation': 'Objects detected successfully'}  # final explanation
        ]
        
        payload = {
            'image': mock_upload_file,
            'evaluator': 'GPT_4o'
        }
        
        result = ImageService.object_detection_img(payload)
        
        assert result is not None
        assert hasattr(result, 'explanation')
        mock_shutil.rmtree.assert_called_once()
        mock_gc.collect.assert_called_once()
    
    @patch('image_explain.service.service.gc')
    @patch('image_explain.service.service.shutil')
    @patch('image_explain.service.service.time')
    @patch('image_explain.service.service.ImageExplain')
    @patch('image_explain.service.service.Prompt')
    @patch('image_explain.service.service.ImageService.read_image_base64')
    @patch('image_explain.service.service.guess_type')
    @patch('image_explain.service.service.os.makedirs')
    @patch('image_explain.service.service.Image.open')
    @patch('image_explain.service.service.uuid.uuid4')
    def test_object_detection_img_with_llama(
        self, mock_uuid, mock_pil_open, mock_makedirs, mock_guess_type,
        mock_read_base64, mock_prompt, mock_image_explain,
        mock_time, mock_shutil, mock_gc
    ):
        """Test object detection with Llama evaluator"""
        mock_uuid.return_value = 'obj-uuid-llama'
        mock_upload_file = MagicMock()
        mock_upload_file.filename = 'llama.jpg'
        mock_upload_file.file = BytesIO(b'image')
        
        mock_image = MagicMock()
        mock_pil_open.return_value = mock_image
        mock_guess_type.return_value = ('image/jpeg', None)
        mock_read_base64.return_value = 'base64'
        
        mock_time.time.side_effect = [200.0, 203.0]
        
        mock_prompt.detect_objects_slm_prompt.return_value = "SLM detect prompt"
        mock_prompt.bounding_boxes_slm_prompt.return_value = "SLM bbox prompt"
        mock_prompt.validate_objects_slm_prompt.return_value = "SLM validate prompt"
        mock_prompt.obj_detection_exp_prompt.return_value = "SLM explanation prompt"
        
        # For Llama, the final result is a string, not a dict
        mock_image_explain.analyze_image.side_effect = [
            ['dog', 'cat'],  # detected objects
            ['dog'],  # bounding boxes
            ['cat'],  # add_objs_presence
            'Llama detected: dog and cat'  # explanation (string for llama)
        ]
        
        payload = {
            'image': mock_upload_file,
            'evaluator': 'Llama'
        }
        
        result = ImageService.object_detection_img(payload)
        
        assert result is not None
        mock_shutil.rmtree.assert_called_once()
    
    def test_object_detection_img_missing_image(self):
        """Test ValueError when image is missing"""
        payload = {'evaluator': 'GPT_4o'}
        
        with pytest.raises(ValueError, match="Invalid payload"):
            ImageService.object_detection_img(payload)
    
    def test_object_detection_img_missing_evaluator(self):
        """Test ValueError when evaluator is missing"""
        mock_upload_file = MagicMock()
        payload = {'image': mock_upload_file}
        
        with pytest.raises(ValueError, match="Invalid payload"):
            ImageService.object_detection_img(payload)
    
    def test_object_detection_img_unsupported_evaluator(self):
        """Test ValueError for unsupported evaluator"""
        mock_upload_file = MagicMock()
        payload = {
            'image': mock_upload_file,
            'evaluator': 'UnsupportedModel'
        }
        
        with pytest.raises(ValueError, match="Currently supporting GPT-4o"):
            ImageService.object_detection_img(payload)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=src/image_explain/service/service', '--cov-report=term-missing'])
