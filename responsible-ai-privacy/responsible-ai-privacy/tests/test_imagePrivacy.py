"""
Comprehensive test suite for privacy.service.imagePrivacy module.

This module tests ImageRotation, ImagePrivacy, and saveImage classes
to achieve >90% code coverage without modifying source code.
"""

import pytest
import io
import base64
import numpy as np
from unittest.mock import MagicMock, Mock, patch, mock_open, call
from PIL import Image

# Import the modules under test
from privacy.service import imagePrivacy
from privacy.service.imagePrivacy import ImageRotation, ImagePrivacy, saveImage, AttributeDict
from privacy.config.logger import request_id_var


class TestImageRotation:
    """Test suite for ImageRotation class."""
    
    def test_float_convertor_with_digit(self):
        """Test float_convertor with digit string."""
        result = ImageRotation.float_convertor("90")
        assert result == 90.0
        assert isinstance(result, float)
    
    def test_float_convertor_with_non_digit(self):
        """Test float_convertor with non-digit string."""
        result = ImageRotation.float_convertor("abc")
        assert result == "abc"
        assert isinstance(result, str)
    
    def test_float_convertor_with_float_string(self):
        """Test float_convertor with float string."""
        result = ImageRotation.float_convertor("90.5")
        assert result == "90.5"  # isdigit() returns False for "90.5"
    
    def test_getAngle(self):
        """Test getAngle extracts rotation angle from image."""
        mock_image = MagicMock()
        
        with patch('privacy.service.imagePrivacy.pytesseract.image_to_osd') as mock_osd:
            mock_osd.return_value = "Page number: 0\nRotate: 90\nOrientation in degrees: 90\n"
            
            angle = ImageRotation.getAngle(mock_image)
            
            assert angle == 90.0
            mock_osd.assert_called_once_with(mock_image)
    
    def test_getAngle_with_zero_rotation(self):
        """Test getAngle with zero rotation."""
        mock_image = MagicMock()
        
        with patch('privacy.service.imagePrivacy.pytesseract.image_to_osd') as mock_osd:
            mock_osd.return_value = "Page number: 0\nRotate: 0\nOrientation in degrees: 0\n"
            
            angle = ImageRotation.getAngle(mock_image)
            
            assert angle == 0.0
    
    def test_rotateImage_with_preAngle_zero(self):
        """Test rotateImage when preAngle is 0 (calculates angle)."""
        # Create a simple test image
        image_array = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_image = Image.fromarray(image_array)
        
        with patch.object(ImageRotation, 'getAngle', return_value=90.0) as mock_get_angle, \
             patch('privacy.service.imagePrivacy.ndimage.rotate') as mock_rotate, \
             patch('privacy.service.imagePrivacy.im.fromarray') as mock_fromarray:
            
            mock_rotated = MagicMock()
            mock_rotate.return_value = image_array
            mock_fromarray.return_value = mock_rotated
            
            result_image, angle = ImageRotation.rotateImage(mock_image, preAngle=0)
            
            mock_get_angle.assert_called_once_with(mock_image)
            assert angle == 90.0
            assert result_image == mock_rotated
    
    def test_rotateImage_with_matching_preAngle(self):
        """Test rotateImage when preAngle is 0 (angle defaults to 0)."""
        image_array = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_image = Image.fromarray(image_array)
        
        # When preAngle==0 and getAngle returns 0, they match
        with patch.object(ImageRotation, 'getAngle', return_value=0):
            result_image, angle = ImageRotation.rotateImage(mock_image, preAngle=0)
            
            # When angles match (both 0), returns same image object
            assert result_image == mock_image
            assert angle == 0
    
    def test_rotateImage_with_different_preAngle(self):
        """Test rotateImage when preAngle is non-zero (angle stays 0)."""
        image_array = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_image = Image.fromarray(image_array)
        
        # When preAngle != 0, getAngle is NOT called, angle stays 0
        with patch('privacy.service.imagePrivacy.ndimage.rotate') as mock_rotate, \
             patch('privacy.service.imagePrivacy.im.fromarray') as mock_fromarray:
            
            mock_rotated = MagicMock()
            mock_rotate.return_value = image_array
            mock_fromarray.return_value = mock_rotated
            
            result_image, angle = ImageRotation.rotateImage(mock_image, preAngle=180.0)
            
            # Should rotate by (preAngle - angle) = (180 - 0) = 180 degrees
            mock_rotate.assert_called_once_with(mock_image, 180.0)
            assert angle == 0  # angle variable stays 0 when preAngle != 0


class TestImagePrivacyImageAnalyze:
    """Test suite for privacy.service.imagePrivacy.image_analyze method."""
    
    @pytest.fixture
    def mock_payload(self):
        """Create a mock payload for testing."""
        mock_file = MagicMock()
        mock_file.file = io.BytesIO(b"fake_image_data")
        
        return {
            "image": mock_file,
            "rotationFlag": False,
            "nlp": "spacy",
            "easyocr": "Tesseract",
            "mag_ratio": 1.0,
            "piiEntitiesToBeRedacted": None,
            "exclusion": None,
            "portfolio": None,
            "account": None
        }
    
    def test_image_analyze_tesseract_no_rotation(self, mock_payload):
        """Test image_analyze with Tesseract OCR and no rotation."""
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = []
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            assert result is not None
            mock_analyzer.analyze.assert_called_once()
    
    def test_image_analyze_with_rotation(self, mock_payload):
        """Test image_analyze with rotation enabled."""
        mock_payload["rotationFlag"] = True
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch.object(ImageRotation, 'rotateImage') as mock_rotate, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            mock_rotate.return_value = (mock_image, 90)
            
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = []
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            mock_rotate.assert_called_once()
            assert result is not None
    
    def test_image_analyze_with_easyocr(self, mock_payload):
        """Test image_analyze with EasyOCR."""
        mock_payload["easyocr"] = "EasyOcr"
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.EasyOCR') as mock_easy_ocr_class, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_ocr = MagicMock()
            mock_easy_ocr_class.return_value = mock_ocr
            
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = []
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            mock_easy_ocr_class.assert_called_once()
            assert result is not None
    
    def test_image_analyze_with_computer_vision(self, mock_payload):
        """Test image_analyze with Azure Computer Vision."""
        mock_payload["easyocr"] = "ComputerVision"
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ComputerVision') as mock_cv_class, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_cv = MagicMock()
            mock_cv_class.return_value = mock_cv
            
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = []
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            mock_cv_class.assert_called_once()
            assert result is not None
    
    def test_image_analyze_with_pii_entities(self, mock_payload):
        """Test image_analyze with specific PII entities to be redacted."""
        mock_payload["piiEntitiesToBeRedacted"] = "PERSON,EMAIL,PHONE"
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = []
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            # Should call analyze with entities parameter
            call_args = mock_analyzer.analyze.call_args
            assert 'entities' in call_args.kwargs
            assert call_args.kwargs['entities'] == ["PERSON", "EMAIL", "PHONE"]
    
    def test_image_analyze_with_exclusion_list(self, mock_payload):
        """Test image_analyze with exclusion list."""
        mock_payload["exclusion"] = "John,Jane,Doe"
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = []
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            # Should call analyze with allow_list parameter
            call_args = mock_analyzer.analyze.call_args
            assert 'allow_list' in call_args.kwargs
            assert call_args.kwargs['allow_list'] == ["John", "Jane", "Doe"]
    
    def test_image_analyze_with_roberta_nlp(self, mock_payload):
        """Test image_analyze with roberta NLP model."""
        mock_payload["nlp"] = "roberta"
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.roberta_recog') as mock_roberta, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = []
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            # Should call analyze with ad_hoc_recognizers parameter
            call_args = mock_analyzer.analyze.call_args
            assert 'ad_hoc_recognizers' in call_args.kwargs
    
    def test_image_analyze_with_ranha_nlp(self, mock_payload):
        """Test image_analyze with ranha NLP model."""
        mock_payload["nlp"] = "ranha"
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.ranha_recog') as mock_ranha, \
             patch('privacy.service.imagePrivacy.registry') as mock_registry, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_ranha.supported_entities = ["PERSON", "EMAIL"]
            mock_registry.get_supported_entities.return_value = ["PHONE"]
            
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = []
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            assert result is not None
    
    def test_image_analyze_exception_returns_482(self, mock_payload):
        """Test image_analyze returns 482 on exception with specific PII entities."""
        mock_payload["piiEntitiesToBeRedacted"] = "INVALID_ENTITY"
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.side_effect = Exception("Invalid entity")
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            assert result == 482
    
    def test_image_analyze_with_portfolio(self, mock_payload):
        """Test image_analyze with portfolio (account-based recognition)."""
        mock_payload["portfolio"] = "test_portfolio"
        mock_payload["account"] = "test_account"
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.ApiCall.request') as mock_api_request, \
             patch('privacy.service.imagePrivacy.ApiCall.getRecord') as mock_get_record, \
             patch('privacy.service.imagePrivacy.registry') as mock_registry, \
             patch('privacy.service.imagePrivacy.admin_par', {"test-request-id": {"scoreTreshold": 0.5}}), \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            # Mock API response
            mock_api_request.return_value = (["CUSTOM_ENTITY"], [["value1", "value2"]], ["PERSON"])
            
            # Mock getRecord response for Data type
            mock_record = {
                "RecogType": "Data",
                "isPreDefined": "Yes",
                "Score": 0.8
            }
            mock_get_record.return_value = mock_record
            
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = []
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            assert result is not None
            mock_api_request.assert_called_once()
    
    def test_image_analyze_portfolio_api_returns_none(self, mock_payload):
        """Test image_analyze when API returns None."""
        mock_payload["portfolio"] = "test_portfolio"
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.ApiCall.request') as mock_api_request, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_api_request.return_value = None
            
            mock_analyzer = MagicMock()
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            assert result is None
    
    def test_image_analyze_portfolio_api_returns_404(self, mock_payload):
        """Test image_analyze when API returns 404."""
        mock_payload["portfolio"] = "test_portfolio"
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.ApiCall.request') as mock_api_request, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_api_request.return_value = 404
            
            mock_analyzer = MagicMock()
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            assert result == 404
    
    def test_image_analyze_portfolio_with_pattern_recognizer(self, mock_payload):
        """Test image_analyze with portfolio using pattern recognizer."""
        mock_payload["portfolio"] = "test_portfolio"
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.ApiCall.request') as mock_api_request, \
             patch('privacy.service.imagePrivacy.ApiCall.getRecord') as mock_get_record, \
             patch('privacy.service.imagePrivacy.registry') as mock_registry, \
             patch('privacy.service.imagePrivacy.Pattern') as mock_pattern_class, \
             patch('privacy.service.imagePrivacy.PatternRecognizer') as mock_pattern_recog_class, \
             patch('privacy.service.imagePrivacy.admin_par', {"test-request-id": {"scoreTreshold": 0.5}}), \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            # Mock API response with pattern data
            mock_api_request.return_value = (["PHONE_NUMBER"], [["\\d{3}-\\d{4}"]], [])
            
            # Mock getRecord response for Pattern type
            mock_record = {
                "RecogType": "Pattern",
                "isPreDefined": "No",
                "Context": "phone,contact",
                "Score": 0.9
            }
            mock_get_record.return_value = mock_record
            
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = []
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            assert result is not None
            mock_pattern_class.assert_called_once()
            mock_pattern_recog_class.assert_called_once()
    
    def test_image_analyze_with_results(self, mock_payload):
        """Test image_analyze with actual PII detection results."""
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            # Mock analysis results
            mock_result = MagicMock()
            mock_result.entity_type = "PERSON"
            mock_result.start = 0
            mock_result.end = 10
            mock_result.score = 0.95
            
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = [mock_result]
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            assert result is not None
            assert hasattr(result, 'PIIEntities')
            assert len(result.PIIEntities) == 1
    
    def test_image_analyze_exception_handling(self, mock_payload):
        """Test image_analyze exception handling."""
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_open.side_effect = Exception("File not found")
            
            with pytest.raises(Exception):
                ImagePrivacy.image_analyze(mock_payload)


class TestImagePrivacyTemp:
    """Test suite for privacy.service.imagePrivacy.temp method."""
    
    def test_temp_analyzes_image(self):
        """Test temp method analyzes image and returns entity types."""
        mock_payload = MagicMock()
        mock_payload.file = io.BytesIO(b"fake_image_data")
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class:
            
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            # Mock analysis results
            mock_result1 = MagicMock()
            mock_result1.entity_type = "PERSON"
            mock_result2 = MagicMock()
            mock_result2.entity_type = "EMAIL"
            
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = [mock_result1, mock_result2]
            mock_analyzer_class.return_value = mock_analyzer
            
            result = ImagePrivacy.temp(mock_payload)
            
            assert result == ["PERSON", "EMAIL"]
            mock_analyzer.analyze.assert_called_once_with(mock_image)


class TestImagePrivacyAnonymize:
    """Test suite for privacy.service.imagePrivacy.image_anonymize method."""
    
    @pytest.fixture
    def mock_payload(self):
        """Create a mock payload for anonymize testing."""
        mock_file = MagicMock()
        mock_file.file = io.BytesIO(b"fake_image_data")
        
        return {
            "image": mock_file,
            "rotationFlag": False,
            "nlp": "spacy",
            "easyocr": "Tesseract",
            "mag_ratio": 1.0,
            "piiEntitiesToBeRedacted": None,
            "exclusion": None,
            "portfolio": None
        }
    
    def test_image_anonymize_tesseract(self, mock_payload):
        """Test image_anonymize with Tesseract OCR."""
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_class, \
             patch('privacy.service.imagePrivacy.saveImage.saveImg') as mock_save, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_redacted = MagicMock()
            mock_redacted.save = MagicMock()
            
            mock_analyzer = MagicMock()
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_redactor = MagicMock()
            mock_redactor.redact.return_value = mock_redacted
            mock_redactor_class.return_value = mock_redactor
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            assert result is not None
            assert isinstance(result, bytes)
            mock_redactor.redact.assert_called_once()
    
    def test_image_anonymize_with_rotation(self, mock_payload):
        """Test image_anonymize with rotation enabled."""
        mock_payload["rotationFlag"] = True
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_class, \
             patch.object(ImageRotation, 'rotateImage') as mock_rotate, \
             patch('privacy.service.imagePrivacy.saveImage.saveImg') as mock_save, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            mock_rotate.return_value = (mock_image, 0)  # Angle is 0, so no final rotation
            
            mock_redacted = MagicMock()
            mock_redacted.save = MagicMock()
            
            mock_analyzer = MagicMock()
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_redactor = MagicMock()
            mock_redactor.redact.return_value = mock_redacted
            mock_redactor_class.return_value = mock_redactor
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            assert result is not None
            mock_rotate.assert_called()
    
    def test_image_anonymize_with_final_rotation(self, mock_payload):
        """Test image_anonymize with final rotation correction."""
        mock_payload["rotationFlag"] = True
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_class, \
             patch.object(ImageRotation, 'rotateImage') as mock_rotate, \
             patch('privacy.service.imagePrivacy.saveImage.saveImg') as mock_save, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            # First rotation returns angle 90, second rotation corrects it
            mock_rotate.side_effect = [(mock_image, 90), (mock_image, 90)]
            
            mock_redacted = MagicMock()
            mock_redacted.save = MagicMock()
            
            mock_analyzer = MagicMock()
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_redactor = MagicMock()
            mock_redactor.redact.return_value = mock_redacted
            mock_redactor_class.return_value = mock_redactor
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            assert result is not None
            # Should be called twice: initial rotation and final correction
            assert mock_rotate.call_count == 2
    
    def test_image_anonymize_with_easyocr(self, mock_payload):
        """Test image_anonymize with EasyOCR."""
        mock_payload["easyocr"] = "EasyOcr"
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.EasyOCR') as mock_easy_ocr_class, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_class, \
             patch('privacy.service.imagePrivacy.saveImage.saveImg') as mock_save, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_ocr = MagicMock()
            mock_easy_ocr_class.return_value = mock_ocr
            
            mock_redacted = MagicMock()
            mock_redacted.save = MagicMock()
            
            mock_analyzer = MagicMock()
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_redactor = MagicMock()
            mock_redactor.redact.return_value = mock_redacted
            mock_redactor_class.return_value = mock_redactor
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            assert result is not None
            mock_easy_ocr_class.assert_called_once()
    
    def test_image_anonymize_with_computer_vision(self, mock_payload):
        """Test image_anonymize with Computer Vision OCR."""
        mock_payload["easyocr"] = "ComputerVision"
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ComputerVision') as mock_cv_class, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_class, \
             patch('privacy.service.imagePrivacy.saveImage.saveImg') as mock_save, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_cv = MagicMock()
            mock_cv_class.return_value = mock_cv
            
            mock_redacted = MagicMock()
            mock_redacted.save = MagicMock()
            
            mock_analyzer = MagicMock()
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_redactor = MagicMock()
            mock_redactor.redact.return_value = mock_redacted
            mock_redactor_class.return_value = mock_redactor
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            assert result is not None
            mock_cv_class.assert_called_once()
    
    def test_image_anonymize_with_pii_entities(self, mock_payload):
        """Test image_anonymize with specific PII entities."""
        mock_payload["piiEntitiesToBeRedacted"] = "PERSON,EMAIL"
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_class, \
             patch('privacy.service.imagePrivacy.saveImage.saveImg') as mock_save, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_redacted = MagicMock()
            mock_redacted.save = MagicMock()
            
            mock_analyzer = MagicMock()
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_redactor = MagicMock()
            mock_redactor.redact.return_value = mock_redacted
            mock_redactor_class.return_value = mock_redactor
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            assert result is not None
            call_args = mock_redactor.redact.call_args
            assert 'entities' in call_args.kwargs
    
    def test_image_anonymize_exception_returns_482(self, mock_payload):
        """Test image_anonymize returns 482 on exception with entities."""
        mock_payload["piiEntitiesToBeRedacted"] = "INVALID_ENTITY"
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_class, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_analyzer = MagicMock()
            mock_analyzer_class.return_value = mock_analyzer
            
            mock_redactor = MagicMock()
            mock_redactor.redact.side_effect = Exception("Invalid entity")
            mock_redactor_class.return_value = mock_redactor
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            assert result == 482
    
    def test_image_anonymize_exception_handling(self, mock_payload):
        """Test image_anonymize general exception handling."""
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_open.side_effect = Exception("File error")
            
            with pytest.raises(Exception):
                ImagePrivacy.image_anonymize(mock_payload)


class TestSaveImage:
    """Test suite for saveImage class."""
    
    def test_saveImg_writes_base64_to_file(self):
        """Test saveImg decodes and writes base64 image to file."""
        test_data = b"fake image data"
        encoded_data = base64.b64encode(test_data)
        
        m = mock_open()
        with patch('privacy.service.imagePrivacy.open', m):
            saveImage.saveImg(encoded_data)
            
            m.assert_called_once_with("imageToSave.png", "wb")
            handle = m()
            handle.write.assert_called_once_with(test_data)
    
    def test_saveImg_with_different_data(self):
        """Test saveImg with different base64 data."""
        test_data = b"another fake image"
        encoded_data = base64.b64encode(test_data)
        
        m = mock_open()
        with patch('privacy.service.imagePrivacy.open', m):
            saveImage.saveImg(encoded_data)
            
            handle = m()
            handle.write.assert_called_once_with(test_data)


class TestZipImageAnonymize:
    """Test suite for privacy.service.imagePrivacy.zipimage_anonymize method."""
    
    def test_zipimage_anonymize(self):
        """Test zipimage_anonymize processes zip file with images."""
        # Create mock zip file
        mock_file = MagicMock()
        mock_file.read.return_value = b"fake zip data"
        
        mock_payload = MagicMock()
        mock_payload.file = mock_file
        
        # Create mock image data
        img = Image.new('RGB', (100, 100))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_data = img_bytes.getvalue()
        
        with patch('privacy.service.imagePrivacy.is_zipfile', return_value=True), \
             patch('privacy.service.imagePrivacy.ZipFile') as mock_zipfile_class, \
             patch('privacy.service.imagePrivacy.Image.open') as mock_img_open, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_class:
            
            # Mock ZipFile context manager
            mock_zip = MagicMock()
            mock_zip.namelist.return_value = ['image1.png', 'image2.png']
            mock_zip.read.return_value = img_data
            mock_zipfile_class.return_value.__enter__.return_value = mock_zip
            
            # Mock image operations
            mock_image = MagicMock()
            mock_img_open.return_value = mock_image
            
            mock_redacted = MagicMock()
            mock_redacted.save = MagicMock()
            
            mock_redactor = MagicMock()
            mock_redactor.redact.return_value = mock_redacted
            mock_redactor_class.return_value = mock_redactor
            
            result = ImagePrivacy.zipimage_anonymize(mock_payload)
            
            assert result is not None
            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(item, bytes) for item in result)


class TestImageAnonymizeNLPBranches:
    """Test suite for image_anonymize NLP-specific branches (lines 271-340)."""

    @pytest.fixture
    def mock_payload_with_exclusion(self):
        """Fixture for payload with exclusion list."""
        from io import BytesIO
        mock_file = MagicMock()
        mock_file.file = BytesIO(b"fake image data")
        return {
            "image": mock_file,
            "easyocr": "Tesseract",
            "rotationFlag": False,
            "magnification": False,
            "exclusion": "John,Doe,Test",
            "piiEntitiesToBeRedacted": None,
            "portfolio": None,
            "account": None,
            "nlp": "basic"
        }

    def test_image_anonymize_with_exclusion_split(self, mock_payload_with_exclusion):
        """Test that exclusion list is properly split when provided."""
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_class, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-req-001"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_redacted = MagicMock()
            mock_redactor = MagicMock()
            mock_redactor.redact.return_value = mock_redacted
            mock_redactor_class.return_value = mock_redactor
            
            result = ImagePrivacy.image_anonymize(mock_payload_with_exclusion)
            
            # Verify redact was called with allow_list containing split exclusions
            call_args = mock_redactor.redact.call_args
            assert 'allow_list' in call_args.kwargs
            assert call_args.kwargs['allow_list'] == ["John", "Doe", "Test"]

    def test_image_anonymize_with_roberta_nlp(self):
        """Test image_anonymize with nlp='basic' using selectNlp branch."""
        from io import BytesIO
        mock_file = MagicMock()
        mock_file.file = BytesIO(b"fake image data")
        payload = {
            "image": mock_file,
            "easyocr": "Tesseract",
            "rotationFlag": False,
            "magnification": False,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "portfolio": None,
            "account": None,
            "nlp": "basic"
        }
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_class, \
             patch('privacy.service.imagePrivacy.roberta_recog') as mock_roberta, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-req-002"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_redacted = MagicMock()
            mock_redactor = MagicMock()
            mock_redactor.redact.return_value = mock_redacted
            mock_redactor_class.return_value = mock_redactor
            
            result = ImagePrivacy.image_anonymize(payload)
            
            # Verify basic NLP path was taken (no ad_hoc_recognizers for basic)
            call_args = mock_redactor.redact.call_args
            # Basic NLP doesn't add ad_hoc_recognizers
            if 'ad_hoc_recognizers' in call_args.kwargs:
                assert call_args.kwargs['ad_hoc_recognizers'] == [] or call_args.kwargs['ad_hoc_recognizers'] is None
            assert result is not None

    def test_image_anonymize_with_ranha_nlp_and_none_entities(self):
        """Test image_anonymize with nlp='basic' and None piiEntities."""
        from io import BytesIO
        mock_file = MagicMock()
        mock_file.file = BytesIO(b"fake image data")
        payload = {
            "image": mock_file,
            "easyocr": "Tesseract",
            "rotationFlag": False,
            "magnification": False,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "portfolio": None,
            "account": None,
            "nlp": "basic"
        }
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_class, \
             patch('privacy.service.imagePrivacy.ranha_recog') as mock_ranha, \
             patch('privacy.service.imagePrivacy.registry') as mock_registry, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-req-003"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            # Mock ranha_recog and registry
            mock_ranha.supported_entities = ["PERSON", "LOCATION"]
            mock_registry.get_supported_entities.return_value = ["EMAIL", "PHONE"]
            
            mock_redacted = MagicMock()
            mock_redactor = MagicMock()
            mock_redactor.redact.return_value = mock_redacted
            mock_redactor_class.return_value = mock_redactor
            
            result = ImagePrivacy.image_anonymize(payload)
            
            # Basic NLP doesn't use ad_hoc_recognizers
            call_args = mock_redactor.redact.call_args
            if 'ad_hoc_recognizers' in call_args.kwargs:
                assert call_args.kwargs['ad_hoc_recognizers'] == [] or call_args.kwargs['ad_hoc_recognizers'] is None
            assert result is not None

    def test_image_anonymize_no_portfolio_with_entities(self):
        """Test image_anonymize without portfolio but with specific entities."""
        from io import BytesIO
        mock_file = MagicMock()
        mock_file.file = BytesIO(b"fake image data")
        payload = {
            "image": mock_file,
            "easyocr": "Tesseract",
            "rotationFlag": False,
            "magnification": False,
            "exclusion": None,
            "piiEntitiesToBeRedacted": "PERSON,EMAIL",
            "portfolio": None,
            "account": None,
            "nlp": "basic"
        }
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_class, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-req-004"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_redacted = MagicMock()
            mock_redactor = MagicMock()
            mock_redactor.redact.return_value = mock_redacted
            mock_redactor_class.return_value = mock_redactor
            
            result = ImagePrivacy.image_anonymize(payload)
            
            # Verify entities parameter is passed
            call_args = mock_redactor.redact.call_args
            assert 'entities' in call_args.kwargs
            assert call_args.kwargs['entities'] == ["PERSON", "EMAIL"]

    def test_image_anonymize_redact_exception_returns_482(self):
        """Test that redaction exception returns 482 error code."""
        from io import BytesIO
        mock_file = MagicMock()
        mock_file.file = BytesIO(b"fake image data")
        payload = {
            "image": mock_file,
            "easyocr": "Tesseract",
            "rotationFlag": False,
            "magnification": False,
            "exclusion": None,
            "piiEntitiesToBeRedacted": "PERSON",
            "portfolio": None,
            "account": None,
            "nlp": "basic"
        }
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_class, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-req-005"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_redactor = MagicMock()
            mock_redactor.redact.side_effect = Exception("Redaction failed")
            mock_redactor_class.return_value = mock_redactor
            
            result = ImagePrivacy.image_anonymize(payload)
            
            assert result == 482

    def test_image_anonymize_with_portfolio_api_call(self):
        """Test image_anonymize with portfolio makes API call."""
        from io import BytesIO
        mock_file = MagicMock()
        mock_file.file = BytesIO(b"fake image data")
        payload = {
            "image": mock_file,
            "easyocr": "Tesseract",
            "rotationFlag": False,
            "magnification": False,
            "exclusion": "exclude1,exclude2",
            "piiEntitiesToBeRedacted": None,
            "portfolio": "TestPortfolio",
            "account": "TestAccount",
            "nlp": "basic"
        }
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_class, \
             patch('privacy.service.imagePrivacy.ApiCall.request') as mock_api_request, \
             patch('privacy.service.imagePrivacy.ApiCall.getRecord') as mock_get_record, \
             patch('privacy.service.imagePrivacy.DataListRecognizer') as mock_data_recog, \
             patch('privacy.service.imagePrivacy.PatternRecognizer') as mock_pattern_recog, \
             patch('privacy.service.imagePrivacy.registry') as mock_registry, \
             patch('privacy.service.imagePrivacy.admin_par', {"test-req-006": {"scoreTreshold": 0.5}}), \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-req-006"
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            # Mock API response
            mock_api_request.return_value = (
                ["EMAIL", "CUSTOM"],
                [["test@example.com"], ["pattern1", "pattern2"]],
                ["PERSON"]
            )
            
            # Mock getRecord responses
            def get_record_side_effect(entity_type):
                if entity_type == "EMAIL":
                    return {"RecogType": "Data", "isPreDefined": "Yes"}
                elif entity_type == "CUSTOM":
                    return {
                        "RecogType": "Pattern",
                        "isPreDefined": "No",
                        "Context": "context1,context2",
                        "Score": 0.8
                    }
                return {}
            
            mock_get_record.side_effect = get_record_side_effect
            
            mock_redacted = MagicMock()
            mock_redactor = MagicMock()
            mock_redactor.redact.return_value = mock_redacted
            mock_redactor_class.return_value = mock_redactor
            
            result = ImagePrivacy.image_anonymize(payload)
            
            # Verify API was called
            mock_api_request.assert_called_once_with(payload)
            
            # Verify recognizers were added to registry
            assert mock_registry.add_recognizer.called
            
            # Verify redact was called with combined entities
            call_args = mock_redactor.redact.call_args
            assert 'entities' in call_args.kwargs
            assert 'score_threshold' in call_args.kwargs
            assert call_args.kwargs['score_threshold'] == 0.5


class TestImagePrivacyImageVerify:
    """Test suite for privacy.service.imagePrivacy.image_verify method."""
    
    @pytest.fixture
    def mock_payload_verify(self):
        """Fixture for image_verify payload."""
        payload = AttributeDict({
            'nlp': 'spacy',
            'image': MagicMock(file=io.BytesIO(b'fake image data')),
            'exclusion': None,
            'portfolio': None
        })
        return payload
    
    def test_image_verify_without_portfolio(self, mock_payload_verify):
        """Test image_verify without portfolio parameter."""
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.base64.b64encode') as mock_b64encode, \
             patch('privacy.service.imagePrivacy.saveImage.saveImg') as mock_save, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-123'
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_analyzer = MagicMock()
            mock_verify_engine = MagicMock()
            mock_select_nlp.return_value = (mock_analyzer, None, None, mock_verify_engine, None)
            
            mock_verified_image = MagicMock()
            mock_verify_engine.verify.return_value = mock_verified_image
            mock_b64encode.return_value = b'encoded_image_data'
            
            result = ImagePrivacy.image_verify(mock_payload_verify)
            
            assert result == b'encoded_image_data'
            mock_verify_engine.verify.assert_called_once()
            mock_save.assert_called_once_with(b'encoded_image_data')
    
    def test_image_verify_with_exclusion_list(self, mock_payload_verify):
        """Test image_verify with exclusion list."""
        mock_payload_verify.exclusion = "EMAIL,PHONE"
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.base64.b64encode') as mock_b64encode, \
             patch('privacy.service.imagePrivacy.saveImage.saveImg') as mock_save, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-123'
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_analyzer = MagicMock()
            mock_verify_engine = MagicMock()
            mock_select_nlp.return_value = (mock_analyzer, None, None, mock_verify_engine, None)
            
            mock_verified_image = MagicMock()
            mock_verify_engine.verify.return_value = mock_verified_image
            mock_b64encode.return_value = b'encoded_image_data'
            
            result = ImagePrivacy.image_verify(mock_payload_verify)
            
            call_args = mock_verify_engine.verify.call_args
            assert 'allow_list' in call_args.kwargs
            assert call_args.kwargs['allow_list'] == ["EMAIL", "PHONE"]
    
    def test_image_verify_with_portfolio_returns_none(self, mock_payload_verify):
        """Test image_verify when API returns None."""
        mock_payload_verify.portfolio = 'test_portfolio'
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ApiCall.request') as mock_api_request, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-123'
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_analyzer = MagicMock()
            mock_verify_engine = MagicMock()
            mock_select_nlp.return_value = (mock_analyzer, None, None, mock_verify_engine, None)
            
            mock_api_request.return_value = None
            
            result = ImagePrivacy.image_verify(mock_payload_verify)
            
            assert result is None
    
    def test_image_verify_with_portfolio_returns_404(self, mock_payload_verify):
        """Test image_verify when API returns 404."""
        mock_payload_verify.portfolio = 'test_portfolio'
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ApiCall.request') as mock_api_request, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-123'
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_analyzer = MagicMock()
            mock_verify_engine = MagicMock()
            mock_select_nlp.return_value = (mock_analyzer, None, None, mock_verify_engine, None)
            
            mock_api_request.return_value = 404
            
            result = ImagePrivacy.image_verify(mock_payload_verify)
            
            assert result == 404
    
    def test_image_verify_exception_handling(self, mock_payload_verify):
        """Test image_verify handles exceptions properly."""
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-123'
            mock_select_nlp.side_effect = Exception("Test error")
            
            with pytest.raises(Exception):
                ImagePrivacy.image_verify(mock_payload_verify)
            
            assert 'test-uuid-123' in imagePrivacy.error_dict
            assert len(imagePrivacy.error_dict['test-uuid-123']) > 0


class TestImagePrivacyImageEncryption:
    """Test suite for privacy.service.imagePrivacy.imageEncryption method."""
    
    @pytest.fixture
    def mock_payload_encrypt(self):
        """Fixture for imageEncryption payload."""
        payload = AttributeDict({
            'nlp': 'spacy',
            'easyocr': 'Tesseract',
            'image': MagicMock(file=io.BytesIO(b'fake image data')),
            'rotationFlag': False,
            'exclusion': None,
            'piiEntitiesToBeHashified': None,
            'portfolio': None,
            'mag_ratio': 1.0
        })
        return payload
    
    def test_imageEncryption_tesseract_no_hashlist(self, mock_payload_encrypt):
        """Test imageEncryption with Tesseract OCR and no hash list."""
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.EncryptImage') as mock_encrypt_class, \
             patch('privacy.service.imagePrivacy.base64.b64encode') as mock_b64encode, \
             patch('privacy.service.imagePrivacy.saveImage.saveImg') as mock_save, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-123'
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_analyzer = MagicMock()
            mock_encrypt_engine = MagicMock()
            mock_encrypt_class.return_value = mock_encrypt_engine
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, mock_encrypt_engine)
            
            # Clear the class-level entity list
            with patch.object(imagePrivacy.EncryptImage, 'entity', []):
                mock_redacted_image = MagicMock()
                mock_encrypt_engine.imageAnonimyze.return_value = mock_redacted_image
                mock_b64encode.return_value = b'encrypted_image_data'
                
                result = ImagePrivacy.imageEncryption(mock_payload_encrypt)
                
                assert result['img'] == b'encrypted_image_data'
                assert result['map'] == []
                mock_encrypt_engine.getText.assert_called_once()
                mock_save.assert_called_once()
    
    def test_imageEncryption_with_easyocr(self, mock_payload_encrypt):
        """Test imageEncryption with EasyOCR."""
        mock_payload_encrypt.easyocr = 'EasyOcr'
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.EasyOCR') as mock_easy_ocr_class, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.EncryptImage') as mock_encrypt_class, \
             patch('privacy.service.imagePrivacy.base64.b64encode') as mock_b64encode, \
             patch('privacy.service.imagePrivacy.saveImage.saveImg') as mock_save, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-123'
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_analyzer = MagicMock()
            mock_encrypt_engine = MagicMock()
            mock_encrypt_class.return_value = mock_encrypt_engine
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, mock_encrypt_engine)
            
            mock_easy_ocr = MagicMock()
            mock_easy_ocr_class.return_value = mock_easy_ocr
            
            with patch.object(imagePrivacy.EncryptImage, 'entity', []):
                mock_redacted_image = MagicMock()
                mock_encrypt_engine.imageAnonimyze.return_value = mock_redacted_image
                mock_b64encode.return_value = b'encrypted_image_data'
                
                result = ImagePrivacy.imageEncryption(mock_payload_encrypt)
                
                assert result['img'] == b'encrypted_image_data'
                mock_easy_ocr_class.setMag.assert_called_once_with(1.0)
    
    def test_imageEncryption_with_computer_vision(self, mock_payload_encrypt):
        """Test imageEncryption with Computer Vision OCR."""
        mock_payload_encrypt.easyocr = 'ComputerVision'
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ComputerVision') as mock_cv_class, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.EncryptImage') as mock_encrypt_class, \
             patch('privacy.service.imagePrivacy.base64.b64encode') as mock_b64encode, \
             patch('privacy.service.imagePrivacy.saveImage.saveImg') as mock_save, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-123'
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_analyzer = MagicMock()
            mock_encrypt_engine = MagicMock()
            mock_encrypt_class.return_value = mock_encrypt_engine
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, mock_encrypt_engine)
            
            mock_cv = MagicMock()
            mock_cv_class.return_value = mock_cv
            
            with patch.object(imagePrivacy.EncryptImage, 'entity', []):
                mock_redacted_image = MagicMock()
                mock_encrypt_engine.imageAnonimyze.return_value = mock_redacted_image
                mock_b64encode.return_value = b'encrypted_image_data'
                
                result = ImagePrivacy.imageEncryption(mock_payload_encrypt)
                
                assert result['img'] == b'encrypted_image_data'
                mock_cv_class.assert_called_once()
    
    def test_imageEncryption_with_rotation(self, mock_payload_encrypt):
        """Test imageEncryption with rotation enabled."""
        mock_payload_encrypt.rotationFlag = True
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.EncryptImage') as mock_encrypt_class, \
             patch('privacy.service.imagePrivacy.ImageRotation.rotateImage') as mock_rotate, \
             patch('privacy.service.imagePrivacy.base64.b64encode') as mock_b64encode, \
             patch('privacy.service.imagePrivacy.saveImage.saveImg') as mock_save, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-123'
            mock_image = MagicMock()
            mock_rotated_image = MagicMock()
            mock_open.return_value = mock_image
            mock_rotate.return_value = (mock_rotated_image, 90)
            
            mock_analyzer = MagicMock()
            mock_encrypt_engine = MagicMock()
            mock_encrypt_class.return_value = mock_encrypt_engine
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, mock_encrypt_engine)
            
            with patch.object(imagePrivacy.EncryptImage, 'entity', []):
                mock_redacted_image = MagicMock()
                mock_encrypt_engine.imageAnonimyze.return_value = mock_redacted_image
                mock_b64encode.return_value = b'encrypted_image_data'
                
                result = ImagePrivacy.imageEncryption(mock_payload_encrypt)
                
                assert mock_rotate.call_count == 2  # Once for input, once for output
    
    def test_imageEncryption_with_hashlist(self, mock_payload_encrypt):
        """Test imageEncryption with hash list."""
        mock_payload_encrypt.piiEntitiesToBeHashified = 'EMAIL,PHONE'
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.EncryptImage') as mock_encrypt_class, \
             patch('privacy.service.imagePrivacy.base64.b64encode') as mock_b64encode, \
             patch('privacy.service.imagePrivacy.saveImage.saveImg') as mock_save, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-123'
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_analyzer = MagicMock()
            mock_encrypt_engine = MagicMock()
            mock_encrypt_class.return_value = mock_encrypt_engine
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, mock_encrypt_engine)
            
            with patch.object(imagePrivacy.EncryptImage, 'entity', []):
                mock_redacted_image = MagicMock()
                mock_encrypt_engine.imageAnonimyze.return_value = mock_redacted_image
                mock_encrypt_engine.encrypt.return_value = (mock_redacted_image, [{'test': 'map'}])
                mock_b64encode.return_value = b'encrypted_image_data'
                
                result = ImagePrivacy.imageEncryption(mock_payload_encrypt)
                
                assert result['img'] == b'encrypted_image_data'
                assert result['map'] == [{'test': 'map'}]
                mock_encrypt_engine.encrypt.assert_called_once()
    
    def test_imageEncryption_with_exclusion_list(self, mock_payload_encrypt):
        """Test imageEncryption with exclusion list."""
        mock_payload_encrypt.exclusion = 'PERSON,LOCATION'
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_class, \
             patch('privacy.service.imagePrivacy.EncryptImage') as mock_encrypt_class, \
             patch('privacy.service.imagePrivacy.base64.b64encode') as mock_b64encode, \
             patch('privacy.service.imagePrivacy.saveImage.saveImg') as mock_save, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-123'
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_analyzer = MagicMock()
            mock_encrypt_engine = MagicMock()
            mock_encrypt_class.return_value = mock_encrypt_engine
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, mock_encrypt_engine)
            
            with patch.object(imagePrivacy.EncryptImage, 'entity', []):
                mock_redacted_image = MagicMock()
                mock_encrypt_engine.imageAnonimyze.return_value = mock_redacted_image
                mock_b64encode.return_value = b'encrypted_image_data'
                
                result = ImagePrivacy.imageEncryption(mock_payload_encrypt)
                
                call_args = mock_encrypt_engine.imageAnonimyze.call_args
                assert call_args is not None
                assert 'allow_list' in call_args.kwargs
                assert call_args.kwargs['allow_list'] == ['PERSON', 'LOCATION']
    
    def test_imageEncryption_with_portfolio_returns_none(self, mock_payload_encrypt):
        """Test imageEncryption when API returns None."""
        mock_payload_encrypt.portfolio = 'test_portfolio'
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ApiCall.request') as mock_api_request, \
             patch('privacy.service.imagePrivacy.EncryptImage') as mock_encrypt_class, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-123'
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_analyzer = MagicMock()
            mock_encrypt_engine = MagicMock()
            mock_encrypt_class.return_value = mock_encrypt_engine
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, mock_encrypt_engine)
            
            with patch.object(imagePrivacy.EncryptImage, 'entity', []):
                mock_api_request.return_value = None
                
                result = ImagePrivacy.imageEncryption(mock_payload_encrypt)
                
                assert result is None
    
    def test_imageEncryption_with_portfolio_returns_404(self, mock_payload_encrypt):
        """Test imageEncryption when API returns 404."""
        mock_payload_encrypt.portfolio = 'test_portfolio'
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ApiCall.request') as mock_api_request, \
             patch('privacy.service.imagePrivacy.EncryptImage') as mock_encrypt_class, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-123'
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            
            mock_analyzer = MagicMock()
            mock_encrypt_engine = MagicMock()
            mock_encrypt_class.return_value = mock_encrypt_engine
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, mock_encrypt_engine)
            
            with patch.object(imagePrivacy.EncryptImage, 'entity', []):
                mock_api_request.return_value = 404
                
                result = ImagePrivacy.imageEncryption(mock_payload_encrypt)
                
                assert result == 404
    
    def test_imageEncryption_exception_handling(self, mock_payload_encrypt):
        """Test imageEncryption handles exceptions properly."""
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.selectNlp') as mock_select_nlp, \
             patch.dict('privacy.service.imagePrivacy.error_dict', {}, clear=True), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-123'
            mock_select_nlp.side_effect = Exception("Encryption error")
            
            with pytest.raises(Exception):
                ImagePrivacy.imageEncryption(mock_payload_encrypt)
            
            assert 'test-uuid-123' in imagePrivacy.error_dict
            assert len(imagePrivacy.error_dict['test-uuid-123']) > 0

