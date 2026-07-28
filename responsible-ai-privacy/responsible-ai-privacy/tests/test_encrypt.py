'''
MIT License https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Test cases for privacy.util.encrypt module
Testing Detect and EncryptImage classes
'''

import pytest
import cv2
import numpy as np
from PIL import Image
from unittest.mock import Mock, MagicMock, patch, PropertyMock, call
from io import BytesIO
import matplotlib.pyplot as plt

from privacy.util.encrypt import Detect, EncryptImage, fig2img


class TestEncryptImage:
    """Test cases for EncryptImage class"""
    
    @pytest.fixture
    def encrypt_image_instance(self):
        """Fixture to create EncryptImage instance"""
        with patch('privacy.util.encrypt.ImageAnalyzerEngine'):
            instance = EncryptImage()
            return instance
    
    @pytest.fixture
    def sample_image(self):
        """Fixture to create a sample PIL image"""
        # Create a mock image with proper size attribute
        mock_image = Mock(spec=Image.Image)
        mock_image.size = (100, 100)  # Return tuple, not mock
        mock_image.mode = 'RGB'
        mock_image.width = 100
        mock_image.height = 100
        # Add copy method that returns a new mock image with same properties
        mock_copy = Mock(spec=Image.Image)
        mock_copy.size = (100, 100)
        mock_copy.mode = 'RGB'
        mock_copy.width = 100
        mock_copy.height = 100
        mock_image.copy.return_value = mock_copy
        return mock_image
    
    def test_init_with_default_analyzer(self, encrypt_image_instance):
        """Test EncryptImage initialization with default analyzer"""
        assert encrypt_image_instance is not None
        assert hasattr(encrypt_image_instance, 'image_analyzer_engine')
        assert hasattr(encrypt_image_instance, 'bbox_processor')
    
    def test_init_with_custom_analyzer(self):
        """Test EncryptImage initialization with custom analyzer"""
        mock_analyzer = Mock()
        instance = EncryptImage(image_analyzer_engine=mock_analyzer)
        
        assert instance.image_analyzer_engine == mock_analyzer
        assert hasattr(instance, 'bbox_processor')
    
    def test_dis_prints_text_info(self, capsys):
        """Test dis method prints text information"""
        EncryptImage.text = "test text"
        
        EncryptImage.dis()
        
        captured = capsys.readouterr()
        assert "test text" in captured.out
        assert "Test Text" in captured.out  # title case


class TestPlt2Img:
    """Test fig2img function to increase coverage."""
    
    def test_plt2img_converts_matplotlib_figure_to_image(self):
        """Test fig2img converts matplotlib figure to PIL Image."""
        from privacy.util.encrypt import fig2img
        
        with patch('privacy.util.encrypt.io.BytesIO') as mock_bytesio, \
             patch('privacy.util.encrypt.Image.open') as mock_image_open:
            
            mock_fig = MagicMock()
            mock_buf = MagicMock()
            mock_bytesio.return_value = mock_buf
            
            mock_img = MagicMock()
            mock_image_open.return_value = mock_img
            
            result = fig2img(mock_fig)
            
            # Verify figure was saved to buffer
            mock_fig.savefig.assert_called_once_with(mock_buf)
            mock_buf.seek.assert_called_once_with(0)
            
            # Verify image was opened from buffer
            mock_image_open.assert_called_once_with(mock_buf)
            assert result == mock_img


class TestDetectGetFace:
    """Test Detect.getFace method with different image types."""
    
    def test_getFace_with_3d_image_bgr(self):
        """Test getFace with 3D BGR image."""
        from privacy.util.encrypt import Detect
        import numpy as np
        
        # Create a mock 3D image (BGR)
        mock_image_3d = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        with patch('privacy.util.encrypt.asarray', return_value=mock_image_3d), \
             patch('privacy.util.encrypt.cv2.CascadeClassifier') as mock_cascade:
            
            # Mock face detection to return one face
            mock_detector = MagicMock()
            mock_detector.detectMultiScale.return_value = [(10, 20, 50, 60)]
            mock_cascade.return_value = mock_detector
            
            result = Detect.getFace(Image.new('RGB', (100, 100)))
            
            # Verify a face was detected and coordinates returned
            assert result == (10, 20, 50, 60)
    
    def test_getFace_with_2d_image_gray(self):
        """Test getFace with 2D grayscale image."""
        from privacy.util.encrypt import Detect
        import numpy as np
        
        # Create a mock 2D image (grayscale)
        mock_image_2d = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        
        with patch('privacy.util.encrypt.asarray', return_value=mock_image_2d), \
             patch('privacy.util.encrypt.cv2.CascadeClassifier') as mock_cascade:
            
            mock_detector = MagicMock()
            mock_detector.detectMultiScale.return_value = [(15, 25, 40, 50)]
            mock_cascade.return_value = mock_detector
            
            result = Detect.getFace(Image.new('L', (100, 100)))
            
            assert result == (15, 25, 40, 50)
    
    def test_getFace_with_other_dimensions(self):
        """Test getFace with image of other dimensions."""
        from privacy.util.encrypt import Detect
        import numpy as np
        
        # Create a mock 1D image
        mock_image_other = np.random.randint(0, 255, (100,), dtype=np.uint8)
        
        with patch('privacy.util.encrypt.asarray', return_value=mock_image_other), \
             patch('privacy.util.encrypt.cv2.CascadeClassifier') as mock_cascade:
            
            mock_detector = MagicMock()
            mock_detector.detectMultiScale.return_value = [(5, 10, 30, 40)]
            mock_cascade.return_value = mock_detector
            
            result = Detect.getFace(Image.new('RGB', (100, 100)))
            
            assert result == (5, 10, 30, 40)
    
    def test_getFace_no_faces_detected(self):
        """Test getFace when no faces are detected."""
        from privacy.util.encrypt import Detect
        import numpy as np
        
        mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        with patch('privacy.util.encrypt.asarray', return_value=mock_image), \
             patch('privacy.util.encrypt.cv2.CascadeClassifier') as mock_cascade:
            
            # Mock face detection to return empty list (no faces)
            mock_detector = MagicMock()
            mock_detector.detectMultiScale.return_value = []
            mock_cascade.return_value = mock_detector
            
            result = Detect.getFace(Image.new('RGB', (100, 100)))
            
            # Should return None when no faces detected
            assert result is None


class TestEncryptImageGetText:
    """Test EncryptImage.getText method."""
    
    def test_getText_extracts_text_from_image(self):
        """Test getText method extracts text using OCR."""
        mock_image = MagicMock()
        
        with patch('privacy.util.encrypt.ImageAnalyzerEngine') as mock_engine_class:
            # Setup mock engine
            mock_engine = MagicMock()
            mock_ocr = MagicMock()
            
            # Mock OCR result
            mock_ocr_result = {"text": "Sample OCR Text"}
            mock_ocr.perform_ocr.return_value = mock_ocr_result
            mock_ocr.get_text_from_ocr_dict.return_value = "Sample OCR Text"
            
            mock_engine.ocr = mock_ocr
            mock_engine._parse_ocr_kwargs.return_value = ({}, None)
            mock_engine.threshold_ocr_result.return_value = mock_ocr_result
            
            mock_engine_class.return_value = mock_engine
            
            # Create EncryptImage instance
            from privacy.util.encrypt import EncryptImage
            encrypt_img = EncryptImage(image_analyzer_engine=mock_engine)
            
            # Call getText
            encrypt_img.getText(mock_image)
            
            # Verify OCR was performed
            mock_ocr.perform_ocr.assert_called_once()
            mock_ocr.get_text_from_ocr_dict.assert_called_once()
            
            # Verify text was stored
            assert EncryptImage.text == "Sample OCR Text"
    
    def test_getText_with_ocr_threshold(self):
        """Test getText with OCR threshold."""
        mock_image = MagicMock()
        
        with patch('privacy.util.encrypt.ImageAnalyzerEngine') as mock_engine_class:
            mock_engine = MagicMock()
            mock_ocr = MagicMock()
            
            mock_ocr_result = {"text": "Threshold Text", "confidence": 0.9}
            mock_ocr.perform_ocr.return_value = mock_ocr_result
            mock_ocr.get_text_from_ocr_dict.return_value = "Threshold Text"
            
            mock_engine.ocr = mock_ocr
            mock_engine._parse_ocr_kwargs.return_value = ({}, 0.8)  # with threshold
            mock_engine.threshold_ocr_result.return_value = mock_ocr_result
            
            mock_engine_class.return_value = mock_engine
            
            from privacy.util.encrypt import EncryptImage
            encrypt_img = EncryptImage(image_analyzer_engine=mock_engine)
            encrypt_img.getText(mock_image, ocr_kwargs={"ocr_threshold": 0.8})
            
            # Verify threshold was applied
            mock_engine.threshold_ocr_result.assert_called_once_with(mock_ocr_result, 0.8)


class TestEncryptImageAnonimyze:
    """Test EncryptImage.imageAnonimyze method."""
    
    def test_imageAnonimyze_basic(self):
        """Test basic imageAnonimyze functionality."""
        from privacy.util.encrypt import EncryptImage
        
        mock_image = MagicMock()
        mock_copy = MagicMock()
        
        mock_box = MagicMock()
        mock_box.entity_type = "PERSON"
        mock_box.left = 10
        mock_box.top = 20
        mock_box.width = 50
        mock_box.height = 30
        
        with patch('privacy.util.encrypt.ImageChops.duplicate', return_value=mock_copy), \
             patch('privacy.util.encrypt.ImageDraw.Draw') as mock_draw, \
             patch('privacy.util.encrypt.ImageAnalyzerEngine') as mock_engine_class:
            
            mock_engine = MagicMock()
            mock_engine.analyze.return_value = [mock_box]
            mock_engine_class.return_value = mock_engine
            
            mock_drawer = MagicMock()
            mock_draw.return_value = mock_drawer
            
            instance = EncryptImage(image_analyzer_engine=mock_engine)
            result = instance.imageAnonimyze(mock_image, encryptionList=["PERSON"])
            
            # Verify analyze was called
            mock_engine.analyze.assert_called_once()
            
            # Verify rectangle was drawn
            mock_drawer.rectangle.assert_called()
            
            # Verify entity was added to list
            assert len(EncryptImage.entity) > 0
    
    def test_imageAnonimyze_with_face_detection(self):
        """Test imageAnonimyze with face detection."""
        from privacy.util.encrypt import EncryptImage, Detect
        
        mock_image = MagicMock()
        mock_copy = MagicMock()
        
        with patch('privacy.util.encrypt.ImageChops.duplicate', return_value=mock_copy), \
             patch('privacy.util.encrypt.ImageDraw.Draw') as mock_draw, \
             patch.object(Detect, 'getFace', return_value=(10, 20, 50, 60)), \
             patch('privacy.util.encrypt.ImageAnalyzerEngine') as mock_engine_class:
            
            mock_engine = MagicMock()
            mock_engine.analyze.return_value = []
            mock_engine_class.return_value = mock_engine
            
            mock_drawer = MagicMock()
            mock_draw.return_value = mock_drawer
            
            instance = EncryptImage(image_analyzer_engine=mock_engine)
            result = instance.imageAnonimyze(mock_image, entities=["Face_Detect"])
            
            # Verify face detection was called
            Detect.getFace.assert_called_once()
            
            # Verify rectangle was drawn for face
            assert mock_drawer.rectangle.call_count >= 1
    
    def test_imageAnonimyze_no_face_detected(self):
        """Test imageAnonimyze when no face is detected."""
        from privacy.util.encrypt import EncryptImage, Detect
        
        mock_image = MagicMock()
        mock_copy = MagicMock()
        
        with patch('privacy.util.encrypt.ImageChops.duplicate', return_value=mock_copy), \
             patch('privacy.util.encrypt.ImageDraw.Draw'), \
             patch.object(Detect, 'getFace', return_value=None), \
             patch('privacy.util.encrypt.ImageAnalyzerEngine') as mock_engine_class:
            
            mock_engine = MagicMock()
            mock_engine.analyze.return_value = []
            mock_engine_class.return_value = mock_engine
            
            instance = EncryptImage(image_analyzer_engine=mock_engine)
            result = instance.imageAnonimyze(mock_image, entities=["Face_Detect"])
            
            # Should handle None gracefully
            assert result is not None


class TestEncryptImageEncrypt:
    """Test EncryptImage.encrypt method."""
    
    def test_encrypt_with_hashlist(self):
        """Test encrypt method with hash-based encryption."""
        from privacy.util.encrypt import EncryptImage
        
        mock_image = MagicMock()
        mock_image.size = (200, 100)
        mock_copy = MagicMock()
        mock_copy.size = (200, 100)
        
        # Create mock bounding boxes
        mock_box = MagicMock()
        mock_box.entity_type = "PERSON"
        mock_box.left = 10
        mock_box.top = 20
        mock_box.width = 50
        mock_box.height = 30
        mock_box.start = 0
        mock_box.end = 10
        
        EncryptImage.entity = [mock_box]
        EncryptImage.text = "John Smith"
        
        mock_anonymized_item = MagicMock()
        mock_anonymized_item.text = "abc123def"
        mock_anonymized_item.entity_type = "PERSON"
        mock_anonymized_item.start = 0
        mock_anonymized_item.end = 10
        
        mock_anonymized_result = MagicMock()
        mock_anonymized_result.items = [mock_anonymized_item]
        
        with patch('privacy.util.encrypt.ImageChops.duplicate', return_value=mock_copy), \
             patch('privacy.util.encrypt.AnonymizerEngine') as mock_anon_class, \
             patch('privacy.util.encrypt.plt') as mock_plt, \
             patch('privacy.util.encrypt.fig2img') as mock_fig2img:
            
            mock_anonymizer = MagicMock()
            mock_anonymizer.anonymize.return_value = mock_anonymized_result
            mock_anon_class.return_value = mock_anonymizer
            
            # Mock matplotlib
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_plt.subplots.return_value = (mock_fig, mock_ax)
            
            mock_result_image = MagicMock()
            mock_fig2img.return_value = mock_result_image
            
            instance = EncryptImage()
            result_image, result_data = instance.encrypt(mock_image, encryptionList=["PERSON"])
            
            # Verify anonymizer was called
            mock_anonymizer.anonymize.assert_called_once()
            
            # Verify result contains mapped data
            assert len(result_data) > 0
            assert result_image is not None
    
    def test_encrypt_with_duplicate_entities(self):
        """Test encrypt handles duplicate entity positions."""
        from privacy.util.encrypt import EncryptImage
        
        mock_image = MagicMock()
        mock_image.size = (200, 100)
        mock_copy = MagicMock()
        mock_copy.size = (200, 100)
        
        # Create duplicate boxes
        mock_box1 = MagicMock()
        mock_box1.entity_type = "PERSON"
        mock_box1.left = 10
        mock_box1.top = 20
        mock_box1.width = 50
        mock_box1.height = 30
        mock_box1.start = 0
        mock_box1.end = 10
        
        mock_box2 = MagicMock()
        mock_box2.entity_type = "PERSON"
        mock_box2.left = 10
        mock_box2.top = 20
        mock_box2.width = 50
        mock_box2.height = 30
        mock_box2.start = 0
        mock_box2.end = 10
        
        EncryptImage.entity = [mock_box1, mock_box2]
        EncryptImage.text = "John Smith"
        
        mock_anonymized_item = MagicMock()
        mock_anonymized_item.text = "abc123"
        mock_anonymized_item.entity_type = "PERSON"
        mock_anonymized_item.start = 0
        mock_anonymized_item.end = 10
        
        mock_anonymized_result = MagicMock()
        mock_anonymized_result.items = [mock_anonymized_item]
        
        with patch('privacy.util.encrypt.ImageChops.duplicate', return_value=mock_copy), \
             patch('privacy.util.encrypt.AnonymizerEngine') as mock_anon_class, \
             patch('privacy.util.encrypt.plt') as mock_plt, \
             patch('privacy.util.encrypt.fig2img') as mock_fig2img:
            
            mock_anonymizer = MagicMock()
            mock_anonymizer.anonymize.return_value = mock_anonymized_result
            mock_anon_class.return_value = mock_anonymizer
            
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_plt.subplots.return_value = (mock_fig, mock_ax)
            
            mock_result_image = MagicMock()
            mock_fig2img.return_value = mock_result_image
            
            instance = EncryptImage()
            result_image, result_data = instance.encrypt(mock_image)
            
            # Should handle duplicates without errors
            assert result_image is not None
    
    def test_encrypt_without_encryption_list(self):
        """Test encrypt method without encryption list."""
        from privacy.util.encrypt import EncryptImage
        
        mock_image = MagicMock()
        mock_image.size = (200, 100)
        mock_copy = MagicMock()
        mock_copy.size = (200, 100)
        
        mock_box = MagicMock()
        mock_box.entity_type = "PERSON"
        mock_box.left = 10
        mock_box.top = 20
        mock_box.width = 50
        mock_box.height = 30
        mock_box.start = 0
        mock_box.end = 10
        
        EncryptImage.entity = [mock_box]
        EncryptImage.text = "John Smith"
        
        mock_anonymized_item = MagicMock()
        mock_anonymized_item.text = "John Smith"
        mock_anonymized_item.entity_type = "PERSON"
        mock_anonymized_item.start = 0
        mock_anonymized_item.end = 10
        
        mock_anonymized_result = MagicMock()
        mock_anonymized_result.items = [mock_anonymized_item]
        
        with patch('privacy.util.encrypt.ImageChops.duplicate', return_value=mock_copy), \
             patch('privacy.util.encrypt.AnonymizerEngine') as mock_anon_class, \
             patch('privacy.util.encrypt.plt') as mock_plt, \
             patch('privacy.util.encrypt.fig2img') as mock_fig2img:
            
            mock_anonymizer = MagicMock()
            mock_anonymizer.anonymize.return_value = mock_anonymized_result
            mock_anon_class.return_value = mock_anonymizer
            
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_plt.subplots.return_value = (mock_fig, mock_ax)
            
            mock_result_image = MagicMock()
            mock_fig2img.return_value = mock_result_image
            
            instance = EncryptImage()
            result_image, result_data = instance.encrypt(mock_image, encryptionList=None)
            
            # Should work with no encryption list
            assert result_image is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

