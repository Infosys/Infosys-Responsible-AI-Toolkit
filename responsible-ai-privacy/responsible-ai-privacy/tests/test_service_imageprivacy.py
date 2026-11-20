"""
Tests for ImagePrivacy class in privacy.service.imagePrivacy module
Uses conftest.py mocking to handle heavy dependencies
"""
import pytest
import sys
import io
import base64
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_image_file():
    """Create a mock image file object"""
    return io.BytesIO(b"fake_image_data")


@pytest.fixture
def mock_payload(mock_image_file):
    """Create a mock payload dict for image operations (will be converted to AttributeDict)"""
    # Import AttributeDict to create nested structure properly
    from privacy.service import AttributeDict
    
    # Create the payload with nested AttributeDict for image
    payload = AttributeDict({
        "image": AttributeDict({
            "file": mock_image_file
        }),
        "nlp": "spacy",
        "easyocr": "Tesseract",
        "pii_entities_to_be_redacted": None,
        "exclusion": None,
        "portfolio": None,
        "account": None,
        "score_threshold": 0.5,
        "rotation_flag": False,
        "mag_ratio": 1.0,
        "pii_entities_to_be_hashified": None
    })
    return payload


class TestImageRotation:
    """Tests for ImageRotation helper class"""
    
    def test_float_convertor_with_digit(self):
        """Test float_convertor converts digit string to float"""
        from privacy.service.imagePrivacy import ImageRotation
        
        result = ImageRotation.float_convertor("90")
        assert result == 90.0
        assert isinstance(result, float)
    
    def test_float_convertor_with_non_digit(self):
        """Test float_convertor returns string unchanged for non-digits"""
        from privacy.service.imagePrivacy import ImageRotation
        
        result = ImageRotation.float_convertor("abc")
        assert result == "abc"
        assert isinstance(result, str)
    
    def test_float_convertor_with_decimal(self):
        """Test float_convertor with decimal string - returns string since isdigit() is False"""
        from privacy.service.imagePrivacy import ImageRotation
        
        result = ImageRotation.float_convertor("90.5")
        assert result == "90.5"  # Decimal strings are not converted (isdigit() returns False)


class TestImagePrivacyAnalyze:
    """Tests for ImagePrivacy.image_analyze method"""
    
    def test_image_analyze_basic(self, mock_payload):
        """Test basic image analysis"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_engine, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            # Setup mocks
            mock_request_id.get.return_value = "test-request-id"
            mock_analyzer = MagicMock()
            mock_result = MagicMock()
            mock_result.entity_type = "EMAIL_ADDRESS"
            mock_result.start = 0
            mock_result.end = 17
            mock_result.score = 0.95
            mock_analyzer.analyze.return_value = [mock_result]
            mock_analyzer_engine.return_value = mock_analyzer
            mock_select_nlp.return_value = (MagicMock(), mock_analyzer, MagicMock(), MagicMock(), MagicMock())
            
            # Test
            result = ImagePrivacy.image_analyze(mock_payload)
            
            # Verify
            assert result is not None
            assert hasattr(result, 'PIIEntities')
    
    def test_image_analyze_with_entities_filter(self, mock_payload):
        """Test image analysis with specific entities filter"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.pii_entities_to_be_redacted = "EMAIL_ADDRESS,PHONE_NUMBER"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_engine, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = []
            mock_analyzer_engine.return_value = mock_analyzer
            mock_select_nlp.return_value = (MagicMock(), mock_analyzer, MagicMock(), MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            # Verify entities parameter was passed
            call_args = mock_analyzer.analyze.call_args
            assert 'entities' in call_args[1]
            assert call_args[1]['entities'] == ['EMAIL_ADDRESS', 'PHONE_NUMBER']


class TestImagePrivacyAnonymize:
    """Tests for ImagePrivacy.image_anonymize method"""
    
    def test_image_anonymize_basic(self, mock_payload):
        """Test basic image anonymization"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_engine, \
             patch('privacy.service.imagePrivacy.SaveImage') as mock_save_image, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            # Setup mocks
            mock_request_id.get.return_value = "test-request-id"
            mock_redactor = MagicMock()
            mock_redacted_img = MagicMock()
            mock_redacted_img.save = MagicMock()
            mock_redactor.redact.return_value = mock_redacted_img
            mock_redactor_engine.return_value = mock_redactor
            mock_select_nlp.return_value = (MagicMock(), MagicMock(), mock_redactor, MagicMock(), MagicMock())
            
            # Test
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            # Verify
            assert result is not None
            assert isinstance(result, bytes)
            mock_save_image.save_img.assert_called_once()


class TestSaveImage:
    """Tests for SaveImage helper class"""
    
    def test_save_img(self):
        """Test SaveImage.save_img processes base64 image data in-memory, without disk persistence"""
        from privacy.service.imagePrivacy import SaveImage
        
        test_data = base64.b64encode(b"test_image_data")
        
        with patch('builtins.open', create=True) as mock_open:
            result = SaveImage.save_img(test_data)
            
            # No file should be written to disk (in-memory only)
            mock_open.assert_not_called()
            assert result == test_data


class TestImageRotationAdvanced:
    """Additional tests for ImageRotation methods"""
    
    def test_get_angle(self):
        """Test get_angle extracts rotation angle from image"""
        from privacy.service.imagePrivacy import ImageRotation
        
        with patch('privacy.service.imagePrivacy.pytesseract') as mock_pytesseract:
            mock_pytesseract.image_to_osd.return_value = "Page number: 0\nOrientation in degrees: 0\nRotate: 90\nOrientation confidence: 12.00"
            
            mock_image = MagicMock()
            angle = ImageRotation.get_angle(mock_image)
            
            assert angle == 90.0
            mock_pytesseract.image_to_osd.assert_called_once_with(mock_image)
    
    def test_rotate_image(self):
        """Test rotate_image rotates and returns image with angle"""
        from privacy.service.imagePrivacy import ImageRotation
        
        with patch('privacy.service.imagePrivacy.pytesseract') as mock_pytesseract, \
             patch('privacy.service.imagePrivacy.ndimage') as mock_ndimage:
            
            mock_pytesseract.image_to_osd.return_value = "Page number: 0\nOrientation in degrees: 0\nRotate: 90\nOrientation confidence: 12.00"
            mock_image = MagicMock()
            mock_rotated = MagicMock()
            mock_ndimage.rotate.return_value = mock_rotated
            
            result_image, angle = ImageRotation.rotate_image(mock_image)
            
            assert angle == 90.0
            mock_ndimage.rotate.assert_called_once()
    
    def test_rotate_image_with_specified_angle(self):
        """Test rotate_image with pre_angle parameter"""
        from privacy.service.imagePrivacy import ImageRotation
        
        with patch('privacy.service.imagePrivacy.ndimage') as mock_ndimage, \
             patch('privacy.service.imagePrivacy.im') as mock_im:
            mock_image = MagicMock()
            mock_rotated_array = MagicMock()
            mock_ndimage.rotate.return_value = mock_rotated_array
            mock_result_image = MagicMock()
            mock_im.fromarray.return_value = mock_result_image
            
            result_image, angle = ImageRotation.rotate_image(mock_image, pre_angle=-90.0)
            
            # When pre_angle != 0, angle should be 0 (since get_angle is not called)
            assert angle == 0
            mock_ndimage.rotate.assert_called_once()


class TestImagePrivacyWithRotation:
    """Tests for image operations with rotation enabled"""
    
    def test_image_analyze_with_rotation(self, mock_payload):
        """Test image_analyze with rotation_flag=True"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.rotation_flag = True
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_engine, \
             patch('privacy.service.imagePrivacy.ImageRotation.rotate_image') as mock_rotate, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_rotated_img = MagicMock()
            mock_rotate.return_value = (mock_rotated_img, 90.0)
            
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = []
            mock_analyzer_engine.return_value = mock_analyzer
            mock_select_nlp.return_value = (MagicMock(), mock_analyzer, MagicMock(), MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            mock_rotate.assert_called_once()
            assert result is not None


class TestImagePrivacyWithDifferentOCR:
    """Tests for different OCR engine options"""
    
    def test_image_analyze_with_easyocr(self, mock_payload):
        """Test image_analyze with EasyOcr engine"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.easyocr = "EasyOcr"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_engine, \
             patch('privacy.service.imagePrivacy.EasyOCR') as mock_easyocr_class, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_ocr = MagicMock()
            mock_easyocr_class.return_value = mock_ocr
            
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = []
            mock_analyzer_engine.return_value = mock_analyzer
            mock_select_nlp.return_value = (MagicMock(), mock_analyzer, MagicMock(), MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            assert result is not None
            mock_easyocr_class.assert_called()
    
    def test_image_analyze_with_computer_vision(self, mock_payload):
        """Test image_analyze with ComputerVision engine"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.easyocr = "ComputerVision"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_engine, \
             patch('privacy.service.imagePrivacy.ComputerVision') as mock_cv_class, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_cv = MagicMock()
            mock_cv_class.return_value = mock_cv
            
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = []
            mock_analyzer_engine.return_value = mock_analyzer
            mock_select_nlp.return_value = (MagicMock(), mock_analyzer, MagicMock(), MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            assert result is not None
            mock_cv_class.assert_called()


class TestImagePrivacyWithExclusion:
    """Tests for exclusion list handling"""
    
    def test_image_analyze_with_exclusion_list(self, mock_payload):
        """Test image_analyze with exclusion list"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.exclusion = "john,doe,example"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_engine, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = []
            mock_analyzer_engine.return_value = mock_analyzer
            mock_select_nlp.return_value = (MagicMock(), mock_analyzer, MagicMock(), MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            call_args = mock_analyzer.analyze.call_args
            assert 'allow_list' in call_args[1]
            assert call_args[1]['allow_list'] == ['john', 'doe', 'example']


class TestImagePrivacyAnonymizeAdvanced:
    """Advanced anonymization tests"""
    
    def test_image_anonymize_with_entities(self, mock_payload):
        """Test image_anonymize with specific entities"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.pii_entities_to_be_redacted = "EMAIL_ADDRESS,PHONE_NUMBER"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_engine, \
             patch('privacy.service.imagePrivacy.SaveImage') as mock_save_image, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_redactor = MagicMock()
            mock_redacted_img = MagicMock()
            mock_redacted_img.save = MagicMock()
            mock_redactor.redact.return_value = mock_redacted_img
            mock_redactor_engine.return_value = mock_redactor
            mock_select_nlp.return_value = (MagicMock(), MagicMock(), mock_redactor, MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            call_args = mock_redactor.redact.call_args
            assert 'entities' in call_args[1]
            assert call_args[1]['entities'] == ['EMAIL_ADDRESS', 'PHONE_NUMBER']
    
    def test_image_anonymize_with_rotation_flag(self, mock_payload):
        """Test image_anonymize with rotation and rotation_flag"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.rotation_flag = True
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_engine, \
             patch('privacy.service.imagePrivacy.ImageRotation.rotate_image') as mock_rotate, \
             patch('privacy.service.imagePrivacy.SaveImage') as mock_save_image, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_rotated_img = MagicMock()
            mock_rotate.return_value = (mock_rotated_img, 90.0)
            
            mock_redactor = MagicMock()
            mock_redacted_img = MagicMock()
            mock_redacted_img.save = MagicMock()
            mock_redactor.redact.return_value = mock_redacted_img
            mock_redactor_engine.return_value = mock_redactor
            mock_select_nlp.return_value = (MagicMock(), MagicMock(), mock_redactor, MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            # Should be called twice - once before and once after redaction
            assert mock_rotate.call_count == 2
    
    def test_image_anonymize_with_easyocr(self, mock_payload):
        """Test image_anonymize with EasyOcr engine"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.easyocr = "EasyOcr"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_engine, \
             patch('privacy.service.imagePrivacy.EasyOCR') as mock_easyocr_class, \
             patch('privacy.service.imagePrivacy.SaveImage') as mock_save_image, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_ocr = MagicMock()
            mock_easyocr_class.return_value = mock_ocr
            
            mock_redactor = MagicMock()
            mock_redacted_img = MagicMock()
            mock_redacted_img.save = MagicMock()
            mock_redactor.redact.return_value = mock_redacted_img
            mock_redactor_engine.return_value = mock_redactor
            mock_select_nlp.return_value = (MagicMock(), MagicMock(), mock_redactor, MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            assert result is not None
            mock_easyocr_class.assert_called()


class TestImagePrivacyWithRobertaRanha:
    """Tests for Roberta and Ranha NLP models"""
    
    def test_image_analyze_with_roberta(self, mock_payload):
        """Test image_analyze with roberta NLP model"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.nlp = "roberta"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_engine, \
             patch('privacy.service.imagePrivacy.roberta_recog') as mock_roberta, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = []
            mock_analyzer_engine.return_value = mock_analyzer
            mock_select_nlp.return_value = (MagicMock(), mock_analyzer, MagicMock(), MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            # Verify roberta recognizer was passed
            call_args = mock_analyzer.analyze.call_args
            assert 'ad_hoc_recognizers' in call_args[1]
            assert call_args[1]['ad_hoc_recognizers'] == [mock_roberta]
    
    def test_image_analyze_with_ranha(self, mock_payload):
        """Test image_analyze with ranha NLP model"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.nlp = "ranha"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_engine, \
             patch('privacy.service.imagePrivacy.ranha_recog') as mock_ranha, \
             patch('privacy.service.imagePrivacy.registry') as mock_registry, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_ranha.supported_entities = ["PERSON", "EMAIL"]
            mock_registry.get_supported_entities.return_value = ["PHONE"]
            
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = []
            mock_analyzer_engine.return_value = mock_analyzer
            mock_select_nlp.return_value = (MagicMock(), mock_analyzer, MagicMock(), MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            # Verify ranha recognizer was passed
            call_args = mock_analyzer.analyze.call_args
            assert 'ad_hoc_recognizers' in call_args[1]
    
    def test_image_anonymize_with_roberta(self, mock_payload):
        """Test image_anonymize with roberta NLP model"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.nlp = "roberta"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_engine, \
             patch('privacy.service.imagePrivacy.roberta_recog') as mock_roberta, \
             patch('privacy.service.imagePrivacy.SaveImage') as mock_save_image, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_redactor = MagicMock()
            mock_redacted_img = MagicMock()
            mock_redacted_img.save = MagicMock()
            mock_redactor.redact.return_value = mock_redacted_img
            mock_redactor_engine.return_value = mock_redactor
            mock_select_nlp.return_value = (MagicMock(), MagicMock(), mock_redactor, MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            call_args = mock_redactor.redact.call_args
            assert 'ad_hoc_recognizers' in call_args[1]
            assert call_args[1]['ad_hoc_recognizers'] == [mock_roberta]


class TestImagePrivacyErrorHandling:
    """Tests for error handling paths"""
    
    def test_image_analyze_with_invalid_entities_returns_482(self, mock_payload):
        """Test that invalid entities returns error code 482"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.pii_entities_to_be_redacted = "INVALID_ENTITY"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_engine, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_analyzer = MagicMock()
            # Simulate exception for invalid entity
            mock_analyzer.analyze.side_effect = Exception("Invalid entity")
            mock_analyzer_engine.return_value = mock_analyzer
            mock_select_nlp.return_value = (MagicMock(), mock_analyzer, MagicMock(), MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            assert result == 482
    
    def test_image_anonymize_with_invalid_entities_returns_482(self, mock_payload):
        """Test that invalid entities in anonymize returns error code 482"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.pii_entities_to_be_redacted = "INVALID_ENTITY"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_engine, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_redactor = MagicMock()
            # Simulate exception for invalid entity
            mock_redactor.redact.side_effect = Exception("Invalid entity")
            mock_redactor_engine.return_value = mock_redactor
            mock_select_nlp.return_value = (MagicMock(), MagicMock(), mock_redactor, MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            assert result == 482


class TestImagePrivacyWithPortfolio:
    """Tests for portfolio/account API integration"""
    
    def test_image_analyze_with_portfolio_returns_none(self, mock_payload):
        """Test image_analyze with portfolio when API returns None"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.portfolio = "test_portfolio"
        mock_payload.account = "test_account"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_engine, \
             patch('privacy.service.imagePrivacy.ApiCall') as mock_api, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            # API returns None
            mock_api.request.return_value = None
            mock_select_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            assert result is None
    
    def test_image_analyze_with_portfolio_returns_404(self, mock_payload):
        """Test image_analyze with portfolio when API returns 404"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.portfolio = "test_portfolio"
        mock_payload.account = "test_account"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_engine, \
             patch('privacy.service.imagePrivacy.ApiCall') as mock_api, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            # API returns 404
            mock_api.request.return_value = 404
            mock_select_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            assert result == 404
    
    def test_image_anonymize_with_portfolio_returns_none(self, mock_payload):
        """Test image_anonymize with portfolio when API returns None"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.portfolio = "test_portfolio"
        mock_payload.account = "test_account"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_engine, \
             patch('privacy.service.imagePrivacy.ApiCall') as mock_api, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            
            mock_request_id.get.return_value = "test-request-id"
            # API returns None
            mock_api.request.return_value = None
            mock_select_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            assert result is None


class TestImagePrivacyPortfolioWithRecognizers:
    """Tests for portfolio integration with Data and Pattern recognizers"""
    
    def test_image_analyze_with_portfolio_data_recognizer(self, mock_image_file, mock_payload):
        """Test image_analyze with portfolio creating DataListRecognizer"""
        from privacy.service.imagePrivacy import ImagePrivacy
        from privacy.service import AttributeDict
        
        mock_payload.portfolio = "test_portfolio"
        mock_payload.account = "test_account"
        mock_payload.exclusion = None
        mock_payload.easyocr = "Tesseract"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.ApiCall') as mock_api_call, \
             patch('privacy.service.imagePrivacy.registry') as mock_registry, \
             patch('privacy.service.imagePrivacy.DataListRecognizer') as mock_data_recog, \
             patch('privacy.service.imagePrivacy.admin_par', {"test-request-id": {"scoreTreshold": 0.5}}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_analyzer_engine = MagicMock()
            mock_analyzer_engine.analyze.return_value = []
            mock_nlp.return_value = (MagicMock(), mock_analyzer_engine, MagicMock(), MagicMock(), MagicMock())
            
            # API returns entity type, datalist, pre_entity
            mock_api_call.request.return_value = (["CUSTOM_ENTITY"], [["data1", "data2"]], ["PRE_ENTITY"])
            
            # getRecord returns Data recognizer type
            mock_record = AttributeDict({"RecogType": "Data"})
            mock_api_call.getRecord.return_value = mock_record
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            # Verify DataListRecognizer was created and added
            mock_data_recog.assert_called_once()
            mock_registry.add_recognizer.assert_called_once()
            # Result is PIIAnalyzeResponse class, not an instance
            assert result is not None
    
    def test_image_analyze_with_portfolio_pattern_recognizer(self, mock_image_file, mock_payload):
        """Test image_analyze with portfolio creating PatternRecognizer"""
        from privacy.service.imagePrivacy import ImagePrivacy
        from privacy.service import AttributeDict
        
        mock_payload.portfolio = "test_portfolio"
        mock_payload.account = "test_account"
        mock_payload.exclusion = None
        mock_payload.easyocr = "Tesseract"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.ApiCall') as mock_api_call, \
             patch('privacy.service.imagePrivacy.registry') as mock_registry, \
             patch('privacy.service.imagePrivacy.Pattern') as mock_pattern, \
             patch('privacy.service.imagePrivacy.PatternRecognizer') as mock_pattern_recog, \
             patch('privacy.service.imagePrivacy.admin_par', {"test-request-id": {"scoreTreshold": 0.5}}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_analyzer_engine = MagicMock()
            mock_analyzer_engine.analyze.return_value = []
            mock_nlp.return_value = (MagicMock(), mock_analyzer_engine, MagicMock(), MagicMock(), MagicMock())
            
            # API returns entity type, datalist, pre_entity
            mock_api_call.request.return_value = (["CUSTOM_PATTERN"], [["pattern1", "pattern2"]], ["PRE_ENTITY"])
            
            # getRecord returns Pattern recognizer type
            mock_record = AttributeDict({
                "RecogType": "Pattern",
                "isPreDefined": "No",
                "Context": "context1,context2",
                "Score": 0.8
            })
            mock_api_call.getRecord.return_value = mock_record
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            # Verify Pattern and PatternRecognizer were created
            mock_pattern.assert_called_once()
            mock_pattern_recog.assert_called_once()
            mock_registry.add_recognizer.assert_called_once()
            # Result is PIIAnalyzeResponse class, not an instance
            assert result is not None
    
    def test_image_anonymize_with_portfolio_data_recognizer(self, mock_image_file, mock_payload):
        """Test image_anonymize with portfolio creating DataListRecognizer"""
        from privacy.service.imagePrivacy import ImagePrivacy
        from privacy.service import AttributeDict
        
        mock_payload.portfolio = "test_portfolio"
        mock_payload.account = "test_account"
        mock_payload.exclusion = None
        mock_payload.easyocr = "Tesseract"
        mock_payload.rotation_flag = False
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.ApiCall') as mock_api_call, \
             patch('privacy.service.imagePrivacy.registry') as mock_registry, \
             patch('privacy.service.imagePrivacy.DataListRecognizer') as mock_data_recog, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.admin_par', {"test-request-id": {"scoreTreshold": 0.5}}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id, \
             patch('privacy.service.imagePrivacy.error_dict', {}):
            
            mock_request_id.get.return_value = "test-request-id"
            mock_redactor_engine = MagicMock()
            mock_redacted_image = MagicMock()
            mock_redacted_image.save = MagicMock()
            mock_redactor_engine.redact.return_value = mock_redacted_image
            mock_nlp.return_value = (MagicMock(), MagicMock(), mock_redactor_engine, MagicMock(), MagicMock())
            
            # API returns entity type, datalist, pre_entity
            mock_api_call.request.return_value = (["CUSTOM_ENTITY"], [["data1", "data2"]], ["PRE_ENTITY"])
            
            # getRecord returns Data recognizer type
            mock_record = AttributeDict({"RecogType": "Data"})
            mock_api_call.getRecord.return_value = mock_record
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            # Verify DataListRecognizer was created and added
            mock_data_recog.assert_called_once()
            mock_registry.add_recognizer.assert_called_once()
            assert result is not None
    
    def test_image_anonymize_with_portfolio_pattern_recognizer(self, mock_image_file, mock_payload):
        """Test image_anonymize with portfolio creating PatternRecognizer"""
        from privacy.service.imagePrivacy import ImagePrivacy
        from privacy.service import AttributeDict
        
        mock_payload.portfolio = "test_portfolio"
        mock_payload.account = "test_account"
        mock_payload.exclusion = None
        mock_payload.easyocr = "Tesseract"
        mock_payload.rotation_flag = False
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.ApiCall') as mock_api_call, \
             patch('privacy.service.imagePrivacy.registry') as mock_registry, \
             patch('privacy.service.imagePrivacy.Pattern') as mock_pattern, \
             patch('privacy.service.imagePrivacy.PatternRecognizer') as mock_pattern_recog, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.admin_par', {"test-request-id": {"scoreTreshold": 0.5}}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id, \
             patch('privacy.service.imagePrivacy.error_dict', {}):
            
            mock_request_id.get.return_value = "test-request-id"
            mock_redactor_engine = MagicMock()
            mock_redacted_image = MagicMock()
            mock_redacted_image.save = MagicMock()
            mock_redactor_engine.redact.return_value = mock_redacted_image
            mock_nlp.return_value = (MagicMock(), MagicMock(), mock_redactor_engine, MagicMock(), MagicMock())
            
            # API returns entity type, datalist, pre_entity
            mock_api_call.request.return_value = (["CUSTOM_PATTERN"], [["pattern1", "pattern2"]], ["PRE_ENTITY"])
            
            # getRecord returns Pattern recognizer type
            mock_record = AttributeDict({
                "RecogType": "Pattern",
                "isPreDefined": "No",
                "Context": "context1,context2",
                "Score": 0.8
            })
            mock_api_call.getRecord.return_value = mock_record
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            # Verify Pattern and PatternRecognizer were created
            mock_pattern.assert_called_once()
            mock_pattern_recog.assert_called_once()
            mock_registry.add_recognizer.assert_called_once()
            assert result is not None


class TestImagePrivacyTemp:
    """Tests for temp() standalone method"""
    
    def test_temp_basic(self, mock_image_file):
        """Test temp method with basic payload"""
        from privacy.service.imagePrivacy import ImagePrivacy
        from privacy.service import AttributeDict
        
        # Create simple payload with file attribute
        payload = AttributeDict({"file": mock_image_file})
        
        with patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_engine:
            mock_analyzer = MagicMock()
            mock_result = MagicMock()
            mock_result.entity_type = "PERSON"
            mock_analyzer.analyze.return_value = [mock_result]
            mock_engine.return_value = mock_analyzer
            
            result = ImagePrivacy.temp(payload)
            
            assert result == ["PERSON"]
            mock_engine.assert_called_once()


class TestImagePrivacyAnonymizePostRotation:
    """Tests for post-anonymization rotation handling"""
    
    def test_image_anonymize_with_post_rotation(self, mock_image_file, mock_payload):
        """Test image_anonymize with rotation reversal after redaction"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.rotation_flag = True
        mock_payload.exclusion = None
        mock_payload.pii_entities_to_be_redacted = None
        mock_payload.portfolio = None
        mock_payload.easyocr = "Tesseract"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.ImageRotation.rotate_image') as mock_rotate, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_redactor_engine = MagicMock()
            mock_redacted_image = MagicMock()
            mock_redacted_image.save = MagicMock()
            mock_redactor_engine.redact.return_value = mock_redacted_image
            mock_nlp.return_value = (MagicMock(), MagicMock(), mock_redactor_engine, MagicMock(), MagicMock())
            
            # Mock rotation to return non-zero angle on first call, then reverse on second call
            mock_rotated_image = MagicMock()
            mock_rotate.side_effect = [
                (mock_rotated_image, 15),  # First rotation
                (mock_redacted_image, 0)   # Post-anonymize rotation reversal
            ]
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            # Verify rotate_image was called twice (before and after anonymization)
            assert mock_rotate.call_count == 2
            assert result is not None


class TestImagePrivacyAnonymizeComputerVision:
    """Tests for ComputerVision OCR in anonymize"""
    
    def test_image_anonymize_with_computer_vision(self, mock_image_file, mock_payload):
        """Test image_anonymize with ComputerVision OCR engine"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.rotation_flag = False
        mock_payload.exclusion = None
        mock_payload.pii_entities_to_be_redacted = None
        mock_payload.portfolio = None
        mock_payload.easyocr = "ComputerVision"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.ComputerVision') as mock_cv, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_cv_instance = MagicMock()
            mock_cv.return_value = mock_cv_instance
            
            mock_redactor_engine = MagicMock()
            mock_redacted_image = MagicMock()
            mock_redacted_image.save = MagicMock()
            mock_redactor_engine.redact.return_value = mock_redacted_image
            mock_nlp.return_value = (MagicMock(), MagicMock(), mock_redactor_engine, MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            # Verify ComputerVision was instantiated
            mock_cv.assert_called_once()
            assert result is not None


class TestImagePrivacyVerify:
    """Tests for image_verify method"""
    
    def test_image_verify_basic(self, mock_image_file, mock_payload):
        """Test image_verify with basic configuration"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.exclusion = None
        mock_payload.portfolio = None
        mock_payload.nlp = "spacy"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_verify_engine = MagicMock()
            mock_verified_image = MagicMock()
            mock_verified_image.save = MagicMock()
            mock_verify_engine.verify.return_value = mock_verified_image
            mock_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), mock_verify_engine, MagicMock())
            
            result = ImagePrivacy.image_verify(mock_payload)
            
            assert result is not None
            mock_verify_engine.verify.assert_called_once()
            mock_save.assert_called_once()
    
    def test_image_verify_with_exclusion(self, mock_image_file, mock_payload):
        """Test image_verify with exclusion list"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.exclusion = "PERSON,EMAIL"
        mock_payload.portfolio = None
        mock_payload.nlp = "spacy"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_verify_engine = MagicMock()
            mock_verified_image = MagicMock()
            mock_verified_image.save = MagicMock()
            mock_verify_engine.verify.return_value = mock_verified_image
            mock_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), mock_verify_engine, MagicMock())
            
            result = ImagePrivacy.image_verify(mock_payload)
            
            assert result is not None
            # Verify exclusion list was passed
            call_args = mock_verify_engine.verify.call_args
            assert 'allow_list' in call_args.kwargs
            assert call_args.kwargs['allow_list'] == ["PERSON", "EMAIL"]
    
    def test_image_verify_with_portfolio_returns_none(self, mock_image_file, mock_payload):
        """Test image_verify when portfolio API returns None"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.portfolio = "test_portfolio"
        mock_payload.account = "test_account"
        mock_payload.exclusion = None
        mock_payload.nlp = "spacy"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.ApiCall') as mock_api_call, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_api_call.request.return_value = None
            mock_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_verify(mock_payload)
            
            assert result is None
    
    def test_image_verify_with_portfolio_data_recognizer(self, mock_image_file, mock_payload):
        """Test image_verify with portfolio creating DataListRecognizer"""
        from privacy.service.imagePrivacy import ImagePrivacy
        from privacy.service import AttributeDict
        
        mock_payload.portfolio = "test_portfolio"
        mock_payload.account = "test_account"
        mock_payload.exclusion = None
        mock_payload.nlp = "spacy"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.ApiCall') as mock_api_call, \
             patch('privacy.service.imagePrivacy.registry') as mock_registry, \
             patch('privacy.service.imagePrivacy.DataListRecognizer') as mock_data_recog, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.admin_par', {"test-request-id": {"scoreTreshold": 0.5}}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id, \
             patch('privacy.service.imagePrivacy.error_dict', {}):
            
            mock_request_id.get.return_value = "test-request-id"
            mock_verify_engine = MagicMock()
            mock_verified_image = MagicMock()
            mock_verified_image.save = MagicMock()
            mock_verify_engine.verify.return_value = mock_verified_image
            mock_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), mock_verify_engine, MagicMock())
            
            mock_api_call.request.return_value = (["CUSTOM_ENTITY"], [["data1", "data2"]], ["PRE_ENTITY"])
            mock_record = AttributeDict({"RecogType": "Data"})
            mock_api_call.getRecord.return_value = mock_record
            
            result = ImagePrivacy.image_verify(mock_payload)
            
            assert result is not None
            mock_data_recog.assert_called_once()
            mock_registry.add_recognizer.assert_called_once()


class TestImagePrivacyEncryption:
    """Tests for image_encryption method"""
    
    def test_image_encryption_basic_tesseract(self, mock_image_file, mock_payload):
        """Test image_encryption with Tesseract OCR"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.easyocr = "Tesseract"
        mock_payload.rotation_flag = False
        mock_payload.exclusion = None
        mock_payload.pii_entities_to_be_hashified = None
        mock_payload.portfolio = None
        mock_payload.nlp = "spacy"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.EncryptImage') as mock_encrypt_image, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            
            # Mock EncryptImage instance
            mock_encrypt_instance = MagicMock()
            mock_encrypt_instance.entity = MagicMock()
            mock_encrypt_instance.entity.clear = MagicMock()
            mock_redacted_image = MagicMock()
            mock_redacted_image.save = MagicMock()
            mock_encrypt_instance.image_anonymize.return_value = mock_redacted_image
            mock_encrypt_image.return_value = mock_encrypt_instance
            
            mock_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock(), mock_encrypt_instance)
            
            result = ImagePrivacy.image_encryption(mock_payload)
            
            assert result is not None
            assert "map" in result
            assert "img" in result
    
    def test_image_encryption_with_easyocr(self, mock_image_file, mock_payload):
        """Test image_encryption with EasyOCR"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.easyocr = "EasyOcr"
        mock_payload.mag_ratio = 2.0
        mock_payload.rotation_flag = False
        mock_payload.exclusion = None
        mock_payload.pii_entities_to_be_hashified = None
        mock_payload.portfolio = None
        mock_payload.nlp = "spacy"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.EasyOCR') as mock_easyocr, \
             patch('privacy.service.imagePrivacy.EncryptImage') as mock_encrypt_image, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_engine, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            
            # Mock EasyOCR
            mock_ocr_instance = MagicMock()
            mock_easyocr.return_value = mock_ocr_instance
            mock_easyocr.setMag = MagicMock()
            
            # Mock EncryptImage instance
            mock_encrypt_instance = MagicMock()
            mock_encrypt_instance.entity = MagicMock()
            mock_encrypt_instance.entity.clear = MagicMock()
            mock_redacted_image = MagicMock()
            mock_redacted_image.save = MagicMock()
            mock_encrypt_instance.image_anonymize.return_value = mock_redacted_image
            mock_encrypt_image.return_value = mock_encrypt_instance
            
            mock_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock(), mock_encrypt_instance)
            
            result = ImagePrivacy.image_encryption(mock_payload)
            
            assert result is not None
            mock_easyocr.assert_called_once()
    
    def test_image_encryption_with_hashify_entities(self, mock_image_file, mock_payload):
        """Test image_encryption with entities to be hashified"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.easyocr = "Tesseract"
        mock_payload.rotation_flag = False
        mock_payload.exclusion = None
        mock_payload.pii_entities_to_be_hashified = "PERSON,EMAIL"
        mock_payload.portfolio = None
        mock_payload.nlp = "spacy"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.EncryptImage') as mock_encrypt_image, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            
            # Mock EncryptImage instance with encrypt method
            mock_encrypt_instance = MagicMock()
            mock_encrypt_instance.entity = MagicMock()
            mock_encrypt_instance.entity.clear = MagicMock()
            mock_redacted_image = MagicMock()
            mock_redacted_image.save = MagicMock()
            mock_encrypt_instance.image_anonymize.return_value = mock_redacted_image
            mock_encrypt_instance.encrypt.return_value = (mock_redacted_image, [{"entity": "PERSON", "hash": "xyz"}])
            mock_encrypt_image.return_value = mock_encrypt_instance
            
            mock_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock(), mock_encrypt_instance)
            
            result = ImagePrivacy.image_encryption(mock_payload)
            
            assert result is not None
            assert "map" in result
            assert "img" in result
            # Verify encrypt was called with hash_list
            mock_encrypt_instance.encrypt.assert_called()
    
    def test_image_encryption_with_rotation(self, mock_image_file, mock_payload):
        """Test image_encryption with rotation"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.easyocr = "Tesseract"
        mock_payload.rotation_flag = True
        mock_payload.exclusion = None
        mock_payload.pii_entities_to_be_hashified = None
        mock_payload.portfolio = None
        mock_payload.nlp = "spacy"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.ImageRotation.rotate_image') as mock_rotate, \
             patch('privacy.service.imagePrivacy.EncryptImage') as mock_encrypt_image, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            
            # Mock rotation
            mock_rotated_image = MagicMock()
            mock_rotate.side_effect = [
                (mock_rotated_image, 15),  # First rotation
                (mock_rotated_image, 0)   # Post-encryption rotation
            ]
            
            # Mock EncryptImage instance
            mock_encrypt_instance = MagicMock()
            mock_encrypt_instance.entity = MagicMock()
            mock_encrypt_instance.entity.clear = MagicMock()
            mock_redacted_image = MagicMock()
            mock_redacted_image.save = MagicMock()
            mock_encrypt_instance.image_anonymize.return_value = mock_redacted_image
            mock_encrypt_image.return_value = mock_encrypt_instance
            
            mock_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock(), mock_encrypt_instance)
            
            result = ImagePrivacy.image_encryption(mock_payload)
            
            assert result is not None
            # Verify rotation was called twice
            assert mock_rotate.call_count == 2
    
    def test_image_encryption_with_portfolio_data_recognizer(self, mock_image_file, mock_payload):
        """Test image_encryption with portfolio creating DataListRecognizer"""
        from privacy.service.imagePrivacy import ImagePrivacy
        from privacy.service import AttributeDict
        
        mock_payload.easyocr = "Tesseract"
        mock_payload.rotation_flag = False
        mock_payload.exclusion = None
        mock_payload.pii_entities_to_be_hashified = None
        mock_payload.portfolio = "test_portfolio"
        mock_payload.account = "test_account"
        mock_payload.nlp = "spacy"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.ApiCall') as mock_api_call, \
             patch('privacy.service.imagePrivacy.registry') as mock_registry, \
             patch('privacy.service.imagePrivacy.DataListRecognizer') as mock_data_recog, \
             patch('privacy.service.imagePrivacy.EncryptImage') as mock_encrypt_image, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.admin_par', {"test-request-id": {"scoreTreshold": 0.5, "encryptionList": ["PERSON"]}}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id, \
             patch('privacy.service.imagePrivacy.error_dict', {}):
            
            mock_request_id.get.return_value = "test-request-id"
            
            # Mock EncryptImage instance
            mock_encrypt_instance = MagicMock()
            mock_encrypt_instance.entity = MagicMock()
            mock_encrypt_instance.entity.clear = MagicMock()
            mock_redacted_image = MagicMock()
            mock_redacted_image.save = MagicMock()
            mock_encrypt_instance.imageAnonimyze.return_value = mock_redacted_image
            mock_encrypt_instance.encrypt.return_value = (mock_redacted_image, [{"entity": "PERSON"}])
            mock_encrypt_instance.dis = MagicMock()
            mock_encrypt_image.return_value = mock_encrypt_instance
            
            mock_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock(), mock_encrypt_instance)
            
            # API returns entity type, datalist, pre_entity
            mock_api_call.request.return_value = (["CUSTOM_ENTITY"], [["data1", "data2"]], ["PRE_ENTITY"])
            mock_record = AttributeDict({"RecogType": "Data"})
            mock_api_call.getRecord.return_value = mock_record
            
            result = ImagePrivacy.image_encryption(mock_payload)
            
            assert result is not None
            mock_data_recog.assert_called_once()
            mock_registry.add_recognizer.assert_called_once()
            # EncryptImage.dis() is called after imageAnonimyze in portfolio path
            assert "map" in result
            assert "img" in result
    
    def test_image_encryption_with_roberta(self, mock_image_file, mock_payload):
        """Test image_encryption with roberta NLP"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.easyocr = "Tesseract"
        mock_payload.rotation_flag = False
        mock_payload.exclusion = None
        mock_payload.pii_entities_to_be_hashified = "PERSON"
        mock_payload.portfolio = None
        mock_payload.account = None
        mock_payload.nlp = "roberta"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.roberta_recog') as mock_roberta, \
             patch('privacy.service.imagePrivacy.EncryptImage') as mock_encrypt_image, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            
            # Mock EncryptImage instance
            mock_encrypt_instance = MagicMock()
            mock_encrypt_instance.entity = MagicMock()
            mock_encrypt_instance.entity.clear = MagicMock()
            mock_redacted_image = MagicMock()
            mock_redacted_image.save = MagicMock()
            mock_encrypt_instance.image_anonymize.return_value = mock_redacted_image
            mock_encrypt_instance.encrypt.return_value = (mock_redacted_image, [])
            mock_encrypt_image.return_value = mock_encrypt_instance
            
            mock_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock(), mock_encrypt_instance)
            
            result = ImagePrivacy.image_encryption(mock_payload)
            
            assert result is not None
    
    def test_image_encryption_with_ranha(self, mock_image_file, mock_payload):
        """Test image_encryption with ranha NLP"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.easyocr = "Tesseract"
        mock_payload.rotation_flag = False
        mock_payload.exclusion = None
        mock_payload.pii_entities_to_be_hashified = None
        mock_payload.portfolio = None
        mock_payload.account = None
        mock_payload.nlp = "ranha"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.ranha_recog') as mock_ranha, \
             patch('privacy.service.imagePrivacy.registry') as mock_registry, \
             patch('privacy.service.imagePrivacy.EncryptImage') as mock_encrypt_image, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            
            # Mock ranha_recog with supported_entities
            mock_ranha.supported_entities = ["PERSON", "EMAIL"]
            mock_registry.get_supported_entities.return_value = ["PHONE"]
            
            # Mock EncryptImage instance
            mock_encrypt_instance = MagicMock()
            mock_encrypt_instance.entity = MagicMock()
            mock_encrypt_instance.entity.clear = MagicMock()
            mock_redacted_image = MagicMock()
            mock_redacted_image.save = MagicMock()
            mock_encrypt_instance.image_anonymize.return_value = mock_redacted_image
            mock_encrypt_image.return_value = mock_encrypt_instance
            
            mock_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock(), mock_encrypt_instance)
            
            result = ImagePrivacy.image_encryption(mock_payload)
            
            assert result is not None


class TestImagePrivacyZipAnonymize:
    """Tests for zip_image_anonymize method"""
    
    def test_zip_image_anonymize_basic(self, mock_image_file):
        """Test zip_image_anonymize with zip file containing images"""
        from privacy.service.imagePrivacy import ImagePrivacy
        from privacy.service import AttributeDict
        from zipfile import ZipFile
        import io
        
        # Create a mock zip file
        mock_zip_bytes = io.BytesIO()
        with ZipFile(mock_zip_bytes, 'w') as zf:
            zf.writestr("image1.png", b"fake_image_data_1")
            zf.writestr("image2.png", b"fake_image_data_2")
        mock_zip_bytes.seek(0)
        
        payload = AttributeDict({"file": mock_zip_bytes})
        
        with patch('privacy.service.imagePrivacy.is_zipfile', return_value=True), \
             patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor:
            
            mock_redactor_instance = MagicMock()
            mock_redacted_image = MagicMock()
            mock_redacted_image.save = MagicMock()
            mock_redactor_instance.redact.return_value = mock_redacted_image
            mock_redactor.return_value = mock_redactor_instance
            
            result = ImagePrivacy.zip_image_anonymize(payload)
            
            assert isinstance(result, list)
            assert len(result) == 2  # Two images in the zip


class TestImagePrivacyAnalyzeEdgeCases:
    """Additional edge case tests for image_analyze"""
    
    def test_image_analyze_with_entities_filter_and_rotation(self, mock_image_file, mock_payload):
        """Test image_analyze with both entities filter and rotation"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.pii_entities_to_be_redacted = "PERSON,EMAIL"
        mock_payload.rotation_flag = True
        mock_payload.exclusion = "PHONE"
        mock_payload.portfolio = None
        mock_payload.easyocr = "Tesseract"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.ImageRotation.rotate_image') as mock_rotate:
            
            mock_analyzer_engine = MagicMock()
            mock_result = MagicMock()
            mock_result.entity_type = "PERSON"
            mock_result.start = 0
            mock_result.end = 5
            mock_result.score = 0.9
            mock_analyzer_engine.analyze.return_value = [mock_result]
            mock_nlp.return_value = (MagicMock(), mock_analyzer_engine, MagicMock(), MagicMock(), MagicMock())
            
            mock_rotated_image = MagicMock()
            mock_rotate.return_value = (mock_rotated_image, 10)
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            assert result is not None
            mock_rotate.assert_called_once()
    
    def test_image_analyze_with_multiple_duplicate_entities(self, mock_image_file, mock_payload):
        """Test image_analyze with duplicate entities (same type and start position)"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.pii_entities_to_be_redacted = None
        mock_payload.rotation_flag = False
        mock_payload.exclusion = None
        mock_payload.portfolio = None
        mock_payload.easyocr = "Tesseract"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp:
            
            mock_analyzer_engine = MagicMock()
            
            # Create duplicate results with same entity_type and start
            mock_result1 = MagicMock()
            mock_result1.entity_type = "PERSON"
            mock_result1.start = 0
            mock_result1.end = 5
            mock_result1.score = 0.9
            
            mock_result2 = MagicMock()
            mock_result2.entity_type = "PERSON"
            mock_result2.start = 0  # Same start as result1
            mock_result2.end = 5
            mock_result2.score = 0.8
            
            mock_result3 = MagicMock()
            mock_result3.entity_type = "EMAIL"
            mock_result3.start = 10
            mock_result3.end = 20
            mock_result3.score = 0.95
            
            mock_analyzer_engine.analyze.return_value = [mock_result1, mock_result2, mock_result3]
            mock_nlp.return_value = (MagicMock(), mock_analyzer_engine, MagicMock(), MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            assert result is not None


class TestImagePrivacyAnonymizeEdgeCases:
    """Additional edge case tests for image_anonymize"""
    
    def test_image_anonymize_with_entities_and_exclusion(self, mock_image_file, mock_payload):
        """Test image_anonymize with both entities filter and exclusion list"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.pii_entities_to_be_redacted = "PERSON,EMAIL"
        mock_payload.exclusion = "PHONE,ADDRESS"
        mock_payload.rotation_flag = False
        mock_payload.portfolio = None
        mock_payload.easyocr = "Tesseract"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_redactor_engine = MagicMock()
            mock_redacted_image = MagicMock()
            mock_redacted_image.save = MagicMock()
            mock_redactor_engine.redact.return_value = mock_redacted_image
            mock_nlp.return_value = (MagicMock(), MagicMock(), mock_redactor_engine, MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            assert result is not None
            # Successfully completed anonymization with entities and exclusion
            mock_save.assert_called_once()
    
    def test_image_anonymize_with_portfolio_pattern_and_exclusion(self, mock_image_file, mock_payload):
        """Test image_anonymize with portfolio Pattern recognizer and exclusion"""
        from privacy.service.imagePrivacy import ImagePrivacy
        from privacy.service import AttributeDict
        
        mock_payload.portfolio = "test_portfolio"
        mock_payload.account = "test_account"
        mock_payload.exclusion = "EMAIL"
        mock_payload.easyocr = "Tesseract"
        mock_payload.rotation_flag = False
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_nlp, \
             patch('privacy.service.imagePrivacy.ApiCall') as mock_api_call, \
             patch('privacy.service.imagePrivacy.registry') as mock_registry, \
             patch('privacy.service.imagePrivacy.Pattern') as mock_pattern, \
             patch('privacy.service.imagePrivacy.PatternRecognizer') as mock_pattern_recog, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.admin_par', {"test-request-id": {"scoreTreshold": 0.6}}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id, \
             patch('privacy.service.imagePrivacy.error_dict', {}):
            
            mock_request_id.get.return_value = "test-request-id"
            mock_redactor_engine = MagicMock()
            mock_redacted_image = MagicMock()
            mock_redacted_image.save = MagicMock()
            mock_redactor_engine.redact.return_value = mock_redacted_image
            mock_nlp.return_value = (MagicMock(), MagicMock(), mock_redactor_engine, MagicMock(), MagicMock())
            
            # API returns Pattern entity
            mock_api_call.request.return_value = (["CUSTOM_PATTERN"], [["pat1", "pat2"]], ["PRE"])
            mock_record = AttributeDict({
                "RecogType": "Pattern",
                "isPreDefined": "No",
                "Context": "ctx1,ctx2",
                "Score": 0.7
            })
            mock_api_call.getRecord.return_value = mock_record
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            assert result is not None
            mock_pattern.assert_called_once()
            mock_pattern_recog.assert_called_once()


class TestImagePrivacyVerify:
    """Tests for ImagePrivacy.image_verify method"""
    
    def test_image_verify_basic(self, mock_payload):
        """Test basic image verification"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_verify_engine = MagicMock()
            mock_verified_img = MagicMock()
            mock_verified_img.save = MagicMock()
            mock_verify_engine.verify.return_value = mock_verified_img
            mock_select_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), mock_verify_engine, MagicMock())
            
            result = ImagePrivacy.image_verify(mock_payload)
            
            assert result is not None
            mock_verify_engine.verify.assert_called_once()
            mock_save.assert_called_once()
    
    def test_image_verify_with_exclusion(self, mock_payload):
        """Test image_verify with exclusion list"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.exclusion = "EMAIL,PHONE_NUMBER"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_verify_engine = MagicMock()
            mock_verified_img = MagicMock()
            mock_verified_img.save = MagicMock()
            mock_verify_engine.verify.return_value = mock_verified_img
            mock_select_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), mock_verify_engine, MagicMock())
            
            result = ImagePrivacy.image_verify(mock_payload)
            
            # Verify exclusion list was passed
            call_kwargs = mock_verify_engine.verify.call_args[1]
            assert 'allow_list' in call_kwargs
            assert call_kwargs['allow_list'] == ["EMAIL", "PHONE_NUMBER"]


class TestImagePrivacyEncryption:
    """Tests for ImagePrivacy.image_encryption method"""
    
    def test_image_encryption_basic(self, mock_payload):
        """Test basic image encryption"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.EncryptImage') as mock_encrypt, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_encrypt_engine = MagicMock()
            mock_encrypted_img = MagicMock()
            mock_encrypted_img.save = MagicMock()
            mock_encrypt_engine.encrypt.return_value = mock_encrypted_img
            mock_select_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock(), mock_encrypt_engine)
            mock_encrypt.entity = MagicMock()
            
            result = ImagePrivacy.image_encryption(mock_payload)
            
            assert result is not None
            mock_save.assert_called_once()
    
    def test_image_encryption_with_easyocr(self, mock_payload):
        """Test image_encryption with EasyOcr"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.easyocr = "EasyOcr"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ImageAnalyzerEngine') as mock_analyzer_engine, \
             patch('privacy.service.imagePrivacy.EncryptImage') as mock_encrypt, \
             patch('privacy.service.imagePrivacy.EasyOCR') as mock_easy_ocr, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_ocr = MagicMock()
            mock_easy_ocr.return_value = mock_ocr
            
            mock_encrypt_engine = MagicMock()
            mock_encrypted_img = MagicMock()
            mock_encrypted_img.save = MagicMock()
            mock_encrypt_engine.encrypt.return_value = mock_encrypted_img
            mock_select_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock(), mock_encrypt_engine)
            mock_encrypt.entity = MagicMock()
            
            result = ImagePrivacy.image_encryption(mock_payload)
            
            # EasyOCR should have been instantiated
            mock_easy_ocr.assert_called_once()


class TestImagePrivacyZipProcessing:
    """Tests for ImagePrivacy.zip_image_anonymize method"""
    
    def test_zip_image_anonymize_basic(self, mock_payload):
        """Test basic ZIP file anonymization"""
        from privacy.service.imagePrivacy import ImagePrivacy
        import zipfile
        import io
        
        # Create a zip file with mock images
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr("image1.png", b"fake_image_data_1")
            zf.writestr("image2.png", b"fake_image_data_2")
        zip_buffer.seek(0)
        
        mock_payload.file = zip_buffer
        
        with patch('privacy.service.imagePrivacy.ImageRedactorEngine') as mock_redactor_engine, \
             patch('privacy.service.imagePrivacy.Image.open') as mock_image_open:
            
            mock_redactor = MagicMock()
            mock_redacted_img = MagicMock()
            mock_redacted_img.save = MagicMock()
            mock_redactor.redact.return_value = mock_redacted_img
            mock_redactor_engine.return_value = mock_redactor
            
            mock_pil_img = MagicMock()
            mock_image_open.return_value = mock_pil_img
            
            result = ImagePrivacy.zip_image_anonymize(mock_payload)
            
            # Should process both images
            assert isinstance(result, list)
            assert len(result) == 2


class TestImagePrivacyAnalyzeLlama:
    """Tests for ImagePrivacy with LLaMA model"""
    
    def test_image_analyze_with_llama_model(self, mock_payload):
        """Test image_analyze with LLaMA model"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.nlp = "llama"
        mock_payload.easyocr = "Tesseract"
        
        with patch('privacy.service.imagePrivacy.pytesseract.image_to_string') as mock_ocr, \
             patch('privacy.service.imagePrivacy.TextPrivacy') as mock_text_privacy, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_ocr.return_value = "user@example.com"
            
            mock_privacy = MagicMock()
            mock_result = MagicMock()
            mock_result.entity_type = "EMAIL_ADDRESS"
            mock_result.start = 0
            mock_result.end = 17
            mock_result.score = 0.95
            mock_privacy.llama_analyze.return_value = [mock_result]
            mock_text_privacy.return_value = mock_privacy
            
            result = ImagePrivacy.image_analyze(mock_payload)
            
            assert result is not None
            assert hasattr(result, 'PIIEntities')
    
    def test_image_anonymize_with_llama_model(self, mock_payload):
        """Test image_anonymize with LLaMA model"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.nlp = "llama"
        mock_payload.easyocr = "Tesseract"
        mock_payload.rotation_flag = False
        
        with patch('privacy.service.imagePrivacy.pytesseract.image_to_string') as mock_ocr_text, \
             patch('privacy.service.imagePrivacy.pytesseract.image_to_data') as mock_ocr_data, \
             patch('privacy.service.imagePrivacy.TextPrivacy') as mock_text_privacy, \
             patch('privacy.service.imagePrivacy.ImageDraw.Draw') as mock_draw, \
             patch('privacy.service.imagePrivacy.SaveImage.save_img') as mock_save, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_ocr_text.return_value = "test email@example.com here"
            mock_ocr_data.return_value = {
                "text": ["test", "email@example.com", "here"],
                "left": [0, 5, 22],
                "top": [0, 0, 0],
                "width": [4, 17, 4],
                "height": [10, 10, 10]
            }
            
            mock_privacy = MagicMock()
            mock_pii = MagicMock()
            mock_pii.start = 5
            mock_pii.end = 22
            mock_privacy.llama_analyze.return_value = [mock_pii]
            mock_text_privacy.return_value = mock_privacy
            
            draw_instance = MagicMock()
            mock_draw.return_value = draw_instance
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            assert result is not None
            mock_save.assert_called_once()


class TestImagePrivacyExceptionHandling:
    """Tests for ImagePrivacy exception handling"""
    
    def test_image_analyze_with_exception(self, mock_payload):
        """Test image_analyze handles exceptions gracefully"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        with patch('privacy.service.imagePrivacy.Image.open') as mock_open, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_open.side_effect = Exception("File read error")
            
            with pytest.raises(RuntimeError):
                ImagePrivacy.image_analyze(mock_payload)
    
    def test_image_anonymize_with_api_error(self, mock_payload):
        """Test image_anonymize when API returns error code"""
        from privacy.service.imagePrivacy import ImagePrivacy
        
        mock_payload.portfolio = "test_portfolio"
        
        with patch('privacy.service.imagePrivacy.select_nlp') as mock_select_nlp, \
             patch('privacy.service.imagePrivacy.ApiCall.request') as mock_api_request, \
             patch('privacy.service.imagePrivacy.error_dict', {}), \
             patch('privacy.service.imagePrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-request-id"
            mock_api_request.return_value = 404  # API error code
            mock_select_nlp.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock())
            
            result = ImagePrivacy.image_anonymize(mock_payload)
            
            # Should return the error code
            assert result == 404


