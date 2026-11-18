"""
Tests for encrypt module.

This module tests the EncryptImage and Detect classes which handle
image anonymization, encryption.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock, call
from PIL import Image
import numpy as np
import io

from privacy.util.encrypt import EncryptImage, fig2img
    

class TestFig2Img:
    """Test fig2img utility function."""
    
    def test_fig2img_converts_figure_to_image(self):
        """Test that matplotlib figure converts to PIL Image."""
        with patch('privacy.util.encrypt.io.BytesIO') as mock_bytesio:
            with patch('privacy.util.encrypt.Image.open') as mock_image_open:
                mock_fig = MagicMock()
                mock_buf = MagicMock()
                mock_bytesio.return_value.__enter__.return_value = mock_buf
                mock_img = MagicMock()
                mock_image_open.return_value.copy.return_value = mock_img
                
                result = fig2img(mock_fig)
                
                # Verify the figure was saved to buffer
                mock_fig.savefig.assert_called_once_with(mock_buf)
                # Verify buffer seek was called
                mock_buf.seek.assert_called_once_with(0)
                # Verify image was opened from buffer
                mock_image_open.assert_called_once_with(mock_buf)
                assert result == mock_img



class TestEncryptImageInit:
    """Test EncryptImage initialization."""
    
    def test_init_with_default_analyzer(self):
        """Test initialization with default ImageAnalyzerEngine."""
        with patch('privacy.util.encrypt.ImageAnalyzerEngine') as mock_engine:
            with patch('privacy.util.encrypt.BboxProcessor') as mock_bbox:
                mock_analyzer = MagicMock()
                mock_engine.return_value = mock_analyzer
                mock_processor = MagicMock()
                mock_bbox.return_value = mock_processor
                
                encryptor = EncryptImage()
                
                # Verify default analyzer was created
                mock_engine.assert_called_once()
                assert encryptor.image_analyzer_engine == mock_analyzer
                assert encryptor.bbox_processor == mock_processor
    
    def test_init_with_custom_analyzer(self):
        """Test initialization with custom ImageAnalyzerEngine."""
        with patch('privacy.util.encrypt.BboxProcessor') as mock_bbox:
            custom_analyzer = MagicMock()
            mock_processor = MagicMock()
            mock_bbox.return_value = mock_processor
            
            encryptor = EncryptImage(image_analyzer_engine=custom_analyzer)
            
            # Verify custom analyzer was used
            assert encryptor.image_analyzer_engine == custom_analyzer
            assert encryptor.bbox_processor == mock_processor


class TestEncryptImageGetText:
    """Test EncryptImage.get_text method."""
    
    def test_get_text_basic(self):
        """Test basic text extraction from image."""
        with patch('privacy.util.encrypt.ImageAnalyzerEngine'):
            with patch('privacy.util.encrypt.BboxProcessor'):
                encryptor = EncryptImage()
                
                mock_image = MagicMock()
                mock_ocr = MagicMock()
                encryptor.image_analyzer_engine.ocr = mock_ocr
                
                # Mock OCR results
                mock_ocr_result = {"text": ["Hello", "World"]}
                mock_ocr.perform_ocr.return_value = mock_ocr_result
                mock_ocr.get_text_from_ocr_dict.return_value = "Hello World"
                
                # Mock parse method
                encryptor.image_analyzer_engine._parse_ocr_kwargs = MagicMock(
                    return_value=({}, None)
                )
                
                encryptor.get_text(mock_image)
                
                # Verify OCR was performed
                mock_ocr.perform_ocr.assert_called_once()
                # Verify text was extracted
                mock_ocr.get_text_from_ocr_dict.assert_called_once()
                # Verify class variable was set
                assert EncryptImage.text == "Hello World"
    
    def test_get_text_with_threshold(self):
        """Test text extraction with OCR threshold."""
        with patch('privacy.util.encrypt.ImageAnalyzerEngine'):
            with patch('privacy.util.encrypt.BboxProcessor'):
                encryptor = EncryptImage()
                
                mock_image = MagicMock()
                mock_ocr = MagicMock()
                encryptor.image_analyzer_engine.ocr = mock_ocr
                
                mock_ocr_result = {"text": ["Test"]}
                mock_ocr.perform_ocr.return_value = mock_ocr_result
                mock_ocr.get_text_from_ocr_dict.return_value = "Test"
                
                # Mock parse method with threshold
                encryptor.image_analyzer_engine._parse_ocr_kwargs = MagicMock(
                    return_value=({}, 0.5)
                )
                encryptor.image_analyzer_engine.threshold_ocr_result = MagicMock(
                    return_value=mock_ocr_result
                )
                
                encryptor.get_text(mock_image, ocr_kwargs={"threshold": 0.5})
                
                # Verify threshold was applied
                encryptor.image_analyzer_engine.threshold_ocr_result.assert_called_once()
                assert EncryptImage.text == "Test"
    
    def test_get_text_with_custom_ocr_kwargs(self):
        """Test text extraction with custom OCR parameters."""
        with patch('privacy.util.encrypt.ImageAnalyzerEngine'):
            with patch('privacy.util.encrypt.BboxProcessor'):
                encryptor = EncryptImage()
                
                mock_image = MagicMock()
                mock_ocr = MagicMock()
                encryptor.image_analyzer_engine.ocr = mock_ocr
                
                mock_ocr_result = {"text": ["Custom"]}
                mock_ocr.perform_ocr.return_value = mock_ocr_result
                mock_ocr.get_text_from_ocr_dict.return_value = "Custom"
                
                custom_kwargs = {"lang": "en"}
                encryptor.image_analyzer_engine._parse_ocr_kwargs = MagicMock(
                    return_value=(custom_kwargs, None)
                )
                
                encryptor.get_text(mock_image, ocr_kwargs=custom_kwargs)
                
                # Verify custom kwargs were passed
                mock_ocr.perform_ocr.assert_called_once_with(mock_image, **custom_kwargs)


class TestEncryptImageAnonymize:
    """Test EncryptImage.image_anonymize method."""
    
    def test_image_anonymize_basic(self):
        """Test basic image anonymization."""
        with patch('privacy.util.encrypt.ImageAnalyzerEngine'):
            with patch('privacy.util.encrypt.BboxProcessor'):
                with patch('privacy.util.encrypt.ImageChops.duplicate') as mock_dup:
                    with patch('privacy.util.encrypt.ImageDraw.Draw') as mock_draw:
                        encryptor = EncryptImage()
                        
                        mock_image = MagicMock()
                        mock_duplicated = MagicMock()
                        mock_dup.return_value = mock_duplicated
                        
                        mock_drawer = MagicMock()
                        mock_draw.return_value = mock_drawer
                        
                        # Mock bounding box
                        mock_box = MagicMock()
                        mock_box.entity_type = "PERSON"
                        mock_box.left = 10
                        mock_box.top = 20
                        mock_box.width = 30
                        mock_box.height = 40
                        
                        encryptor.image_analyzer_engine.analyze = MagicMock(
                            return_value=[mock_box]
                        )
                        
                        result = encryptor.image_anonymize(mock_image)
                        
                        # Verify image was analyzed
                        encryptor.image_analyzer_engine.analyze.assert_called_once()
                        # Verify rectangle was drawn
                        mock_drawer.rectangle.assert_called()
                        assert result == mock_duplicated
    
    def test_image_anonymize_with_encryption_list(self):
        """Test anonymization with specific entities to encrypt."""
        with patch('privacy.util.encrypt.ImageAnalyzerEngine'):
            with patch('privacy.util.encrypt.BboxProcessor'):
                with patch('privacy.util.encrypt.ImageChops.duplicate') as mock_dup:
                    with patch('privacy.util.encrypt.ImageDraw.Draw'):
                        encryptor = EncryptImage()
                        
                        mock_image = MagicMock()
                        mock_duplicated = MagicMock()
                        mock_dup.return_value = mock_duplicated
                        
                        # Mock boxes with different entity types
                        mock_box1 = MagicMock()
                        mock_box1.entity_type = "PERSON"
                        mock_box1.left = 10
                        mock_box1.top = 20
                        mock_box1.width = 30
                        mock_box1.height = 40
                        
                        mock_box2 = MagicMock()
                        mock_box2.entity_type = "EMAIL"
                        mock_box2.left = 50
                        mock_box2.top = 60
                        mock_box2.width = 70
                        mock_box2.height = 80
                        
                        encryptor.image_analyzer_engine.analyze = MagicMock(
                            return_value=[mock_box1, mock_box2]
                        )
                        
                        # Reset class variable
                        EncryptImage.entity = []
                        
                        result = encryptor.image_anonymize(
                            mock_image,
                            encryption_list=["PERSON"]
                        )
                        
                        # Verify only PERSON was added to encryption list
                        assert len(EncryptImage.entity) == 1
                        assert EncryptImage.entity[0] == mock_box1
    
    
    def test_image_anonymize_with_custom_fill(self):
        """Test anonymization with custom fill color."""
        with patch('privacy.util.encrypt.ImageAnalyzerEngine'):
            with patch('privacy.util.encrypt.BboxProcessor'):
                with patch('privacy.util.encrypt.ImageChops.duplicate') as mock_dup:
                    with patch('privacy.util.encrypt.ImageDraw.Draw') as mock_draw:
                        encryptor = EncryptImage()
                        
                        mock_image = MagicMock()
                        mock_duplicated = MagicMock()
                        mock_dup.return_value = mock_duplicated
                        
                        mock_drawer = MagicMock()
                        mock_draw.return_value = mock_drawer
                        
                        mock_box = MagicMock()
                        mock_box.entity_type = "PERSON"
                        mock_box.left = 10
                        mock_box.top = 20
                        mock_box.width = 30
                        mock_box.height = 40
                        
                        encryptor.image_analyzer_engine.analyze = MagicMock(
                            return_value=[mock_box]
                        )
                        
                        result = encryptor.image_anonymize(
                            mock_image,
                            fill=(255, 0, 0)  # Red fill
                        )
                        
                        # Verify rectangle was drawn with red color
                        assert mock_drawer.rectangle.called
                        call_args = mock_drawer.rectangle.call_args
                        assert call_args[1]['fill'] == (255, 0, 0)
    

class TestEncryptImageDis:
    """Test EncryptImage.dis static method."""
    
    def test_dis_prints_text(self):
        """Test dis method prints stored text."""
        # Set up class variable
        EncryptImage.text = "Test Text"
        
        with patch('builtins.print') as mock_print:
            EncryptImage.dis()
            
            # Verify print was called multiple times
            assert mock_print.call_count >= 2


class TestEncryptImageEncrypt:
    """Test EncryptImage.encrypt method."""
    
    def test_encrypt_with_empty_bboxes(self):
        """Test encryption with no bounding boxes."""
        with patch('privacy.util.encrypt.ImageAnalyzerEngine'):
            with patch('privacy.util.encrypt.BboxProcessor'):
                with patch('privacy.util.encrypt.ImageChops.duplicate') as mock_dup:
                    with patch('privacy.util.encrypt.plt.subplots') as mock_subplots:
                        encryptor = EncryptImage()
                        
                        mock_image = MagicMock()
                        mock_duplicated = MagicMock()
                        mock_duplicated.size = (800, 600)
                        mock_dup.return_value = mock_duplicated
                        
                        # Reset class variables
                        EncryptImage.entity = []
                        EncryptImage.text = "Test"
                        
                        # Mock matplotlib
                        mock_fig = MagicMock()
                        mock_ax = MagicMock()
                        mock_subplots.return_value = (mock_fig, mock_ax)
                        
                        result_image, result_data = encryptor.encrypt(mock_image)
                        
                        # Should return original image and empty list
                        assert result_image == mock_duplicated
                        assert result_data == []
    
    def test_encrypt_with_bboxes(self):
        """Test encryption with bounding boxes."""
        with patch('privacy.util.encrypt.ImageAnalyzerEngine'):
            with patch('privacy.util.encrypt.BboxProcessor'):
                with patch('privacy.util.encrypt.ImageChops.duplicate') as mock_dup:
                    with patch('privacy.util.encrypt.AnonymizerEngine') as mock_anon_engine:
                        with patch('privacy.util.encrypt.plt.subplots') as mock_subplots:
                            with patch('privacy.util.encrypt.fig2img') as mock_fig2img:
                                encryptor = EncryptImage()
                                
                                mock_image = MagicMock()
                                mock_duplicated = MagicMock()
                                mock_duplicated.size = (800, 600)
                                mock_dup.return_value = mock_duplicated
                                
                                # Mock bbox
                                mock_box = MagicMock()
                                mock_box.entity_type = "PERSON"
                                mock_box.left = 10
                                mock_box.top = 20
                                mock_box.width = 30
                                mock_box.height = 40
                                mock_box.start = 0
                                mock_box.end = 4
                                
                                EncryptImage.entity = [mock_box]
                                EncryptImage.text = "John"
                                
                                # Mock anonymizer
                                mock_engine = MagicMock()
                                mock_anon_engine.return_value = mock_engine
                                
                                mock_result_item = MagicMock()
                                mock_result_item.text = "XXXX"
                                mock_result_item.entity_type = "PERSON"
                                mock_result_item.start = 0
                                mock_result_item.end = 4
                                
                                mock_anon_result = MagicMock()
                                mock_anon_result.items = [mock_result_item]
                                mock_engine.anonymize.return_value = mock_anon_result
                                
                                # Mock matplotlib
                                mock_fig = MagicMock()
                                mock_ax = MagicMock()
                                mock_subplots.return_value = (mock_fig, mock_ax)
                                
                                mock_encrypted_img = MagicMock()
                                mock_resized = MagicMock()
                                mock_fig2img.return_value = mock_encrypted_img
                                mock_encrypted_img.resize.return_value = mock_resized
                                
                                result_image, result_data = encryptor.encrypt(
                                    mock_image,
                                    encryption_list=["PERSON"]
                                )
                                
                                # Verify anonymizer was called
                                mock_engine.anonymize.assert_called_once()
                                # Verify result contains entity info
                                assert len(result_data) == 1
                                assert result_data[0]["entity_type"] == "PERSON"
                                assert result_image == mock_resized
    
    def test_encrypt_with_duplicate_entities(self):
        """Test encryption handles duplicate entity positions."""
        with patch('privacy.util.encrypt.ImageAnalyzerEngine'):
            with patch('privacy.util.encrypt.BboxProcessor'):
                with patch('privacy.util.encrypt.ImageChops.duplicate') as mock_dup:
                    with patch('privacy.util.encrypt.AnonymizerEngine') as mock_anon_engine:
                        with patch('privacy.util.encrypt.plt.subplots') as mock_subplots:
                            with patch('privacy.util.encrypt.fig2img') as mock_fig2img:
                                encryptor = EncryptImage()
                                
                                mock_image = MagicMock()
                                mock_duplicated = MagicMock()
                                mock_duplicated.size = (800, 600)
                                mock_dup.return_value = mock_duplicated
                                
                                # Two boxes with same start/end positions
                                mock_box1 = MagicMock()
                                mock_box1.entity_type = "PERSON"
                                mock_box1.left = 10
                                mock_box1.top = 20
                                mock_box1.width = 30
                                mock_box1.height = 40
                                mock_box1.start = 0
                                mock_box1.end = 4
                                
                                mock_box2 = MagicMock()
                                mock_box2.entity_type = "PERSON"
                                mock_box2.left = 10
                                mock_box2.top = 20
                                mock_box2.width = 30
                                mock_box2.height = 40
                                mock_box2.start = 0
                                mock_box2.end = 4
                                
                                EncryptImage.entity = [mock_box1, mock_box2]
                                EncryptImage.text = "John"
                                
                                # Mock anonymizer
                                mock_engine = MagicMock()
                                mock_anon_engine.return_value = mock_engine
                                
                                mock_result_item = MagicMock()
                                mock_result_item.text = "XXXX"
                                mock_result_item.entity_type = "PERSON"
                                
                                mock_anon_result = MagicMock()
                                mock_anon_result.items = [mock_result_item]
                                mock_engine.anonymize.return_value = mock_anon_result
                                
                                # Mock matplotlib
                                mock_fig = MagicMock()
                                mock_ax = MagicMock()
                                mock_subplots.return_value = (mock_fig, mock_ax)
                                
                                mock_encrypted_img = MagicMock()
                                mock_resized = MagicMock()
                                mock_fig2img.return_value = mock_encrypted_img
                                mock_encrypted_img.resize.return_value = mock_resized
                                
                                result_image, result_data = encryptor.encrypt(mock_image)
                                
                                # Should only process one due to duplicate detection
                                assert len(result_data) == 1
    
    def test_encrypt_with_no_encryption_list(self):
        """Test encryption with None encryption_list."""
        with patch('privacy.util.encrypt.ImageAnalyzerEngine'):
            with patch('privacy.util.encrypt.BboxProcessor'):
                with patch('privacy.util.encrypt.ImageChops.duplicate') as mock_dup:
                    with patch('privacy.util.encrypt.AnonymizerEngine') as mock_anon_engine:
                        with patch('privacy.util.encrypt.plt.subplots') as mock_subplots:
                            with patch('privacy.util.encrypt.fig2img') as mock_fig2img:
                                encryptor = EncryptImage()
                                
                                mock_image = MagicMock()
                                mock_duplicated = MagicMock()
                                mock_duplicated.size = (800, 600)
                                mock_dup.return_value = mock_duplicated
                                
                                mock_box = MagicMock()
                                mock_box.entity_type = "PERSON"
                                mock_box.left = 10
                                mock_box.top = 20
                                mock_box.width = 30
                                mock_box.height = 40
                                mock_box.start = 0
                                mock_box.end = 4
                                
                                EncryptImage.entity = [mock_box]
                                EncryptImage.text = "John"
                                
                                mock_engine = MagicMock()
                                mock_anon_engine.return_value = mock_engine
                                
                                mock_result_item = MagicMock()
                                mock_result_item.text = "XXXX"
                                mock_result_item.entity_type = "PERSON"
                                
                                mock_anon_result = MagicMock()
                                mock_anon_result.items = [mock_result_item]
                                mock_engine.anonymize.return_value = mock_anon_result
                                
                                mock_fig = MagicMock()
                                mock_ax = MagicMock()
                                mock_subplots.return_value = (mock_fig, mock_ax)
                                
                                mock_encrypted_img = MagicMock()
                                mock_resized = MagicMock()
                                mock_fig2img.return_value = mock_encrypted_img
                                mock_encrypted_img.resize.return_value = mock_resized
                                
                                # Call with empty list
                                result_image, result_data = encryptor.encrypt(
                                    mock_image,
                                    encryption_list=[]
                                )
                                
                                # Verify anonymize was called with None operators
                                call_kwargs = mock_engine.anonymize.call_args[1]
                                assert call_kwargs['operators'] is None


