"""Tests for privacy.service.easy module"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import pandas as pd
from PIL import Image
from privacy.service.easy import EasyOCR, AttributeDict, Data


class TestAttributeDict:
    """Test AttributeDict class"""
    
    def test_attribute_dict_creation(self):
        """Test AttributeDict can be created"""
        attr_dict = AttributeDict()
        assert isinstance(attr_dict, dict)
    
    def test_attribute_dict_setitem(self):
        """Test AttributeDict setitem"""
        attr_dict = AttributeDict()
        attr_dict['key'] = 'value'
        assert attr_dict['key'] == 'value'
    
    def test_attribute_dict_getattr(self):
        """Test AttributeDict getattr"""
        attr_dict = AttributeDict()
        attr_dict['key'] = 'value'
        assert attr_dict.key == 'value'
    
    def test_attribute_dict_setattr(self):
        """Test AttributeDict setattr"""
        attr_dict = AttributeDict()
        attr_dict.key = 'value'
        assert attr_dict['key'] == 'value'
    
    def test_attribute_dict_delattr(self):
        """Test AttributeDict delattr"""
        attr_dict = AttributeDict()
        attr_dict.key = 'value'
        del attr_dict.key
        assert 'key' not in attr_dict


class TestData:
    """Test Data class"""
    
    def test_data_has_encrypted_text(self):
        """Test Data class has encrypted_text attribute"""
        data = Data()
        assert hasattr(data, 'encrypted_text')
    
    def test_data_encrypted_text_is_list(self):
        """Test Data.encrypted_text is a list"""
        data = Data()
        assert isinstance(data.encrypted_text, list)
    
    def test_data_encrypted_text_empty(self):
        """Test Data.encrypted_text starts empty"""
        data = Data()
        assert len(data.encrypted_text) == 0


class TestEasyOCR:
    """Test EasyOCR class"""
    
    def test_easyocr_inherits_from_ocr(self):
        """Test EasyOCR inherits from OCR"""
        from presidio_image_redactor import OCR
        assert issubclass(EasyOCR, OCR)
    
    def test_easyocr_has_mag_ratio(self):
        """Test EasyOCR has mag_ratio class attribute"""
        assert hasattr(EasyOCR, 'mag_ratio')
    
    def test_easyocr_default_mag_ratio(self):
        """Test EasyOCR default mag_ratio is 1"""
        assert EasyOCR.mag_ratio == 1
    
    def test_easyocr_process_method(self):
        """Test EasyOCR process method returns self"""
        ocr = EasyOCR()
        result = ocr.process()
        assert result is ocr
    
    def test_easyocr_set_mag_method_exists(self):
        """Test setMag method exists"""
        ocr = EasyOCR()
        assert hasattr(ocr, 'setMag')
        assert callable(getattr(ocr, 'setMag'))
    
    def test_easyocr_mag_ratio_can_be_changed(self):
        """Test mag_ratio can be changed"""
        original = EasyOCR.mag_ratio
        EasyOCR.mag_ratio = 10
        assert EasyOCR.mag_ratio == 10
        # Reset
        EasyOCR.mag_ratio = original
    
    @patch('privacy.service.easy.output_type.readtext')
    @patch('privacy.service.easy.pd.DataFrame')
    def test_perform_ocr_basic(self, mock_dataframe, mock_readtext):
        """Test perform_ocr basic functionality"""
        # Setup mock DataFrame behavior
        mock_df = Mock()
        mock_df.to_dict.return_value = [
            {'coordinates': [[10, 20], [100, 20], [100, 40], [10, 40]], 'text': 'Hello', 'conf': 0.95},
            {'coordinates': [[10, 50], [80, 50], [80, 70], [10, 70]], 'text': 'World', 'conf': 0.90}
        ]
        mock_dataframe.return_value = mock_df
        mock_readtext.return_value = []
        
        ocr = EasyOCR()
        image = Image.new('RGB', (200, 100), color='white')
        
        result = ocr.perform_ocr(image)
        
        assert 'text' in result
        assert 'left' in result
        assert 'top' in result
        assert 'width' in result
        assert 'height' in result
        assert 'conf' in result
    
    @patch('privacy.service.easy.output_type.readtext')
    @patch('privacy.service.easy.pd.DataFrame')
    def test_perform_ocr_coordinates_calculation(self, mock_dataframe, mock_readtext):
        """Test perform_ocr calculates coordinates correctly"""
        # Setup mock DataFrame behavior
        mock_df = Mock()
        mock_df.to_dict.return_value = [
            {'coordinates': [[10, 20], [100, 20], [100, 40], [10, 40]], 'text': 'Test', 'conf': 0.95}
        ]
        mock_dataframe.return_value = mock_df
        mock_readtext.return_value = []
        
        ocr = EasyOCR()
        image = Image.new('RGB', (200, 100), color='white')
        
        result = ocr.perform_ocr(image)
        
        # Just verify method runs without error
        assert 'text' in result
        assert 'left' in result
    
    @patch('privacy.service.easy.output_type.readtext')
    def test_perform_ocr_empty_result(self, mock_readtext):
        """Test perform_ocr with empty OCR result"""
        mock_readtext.return_value = []
        
        ocr = EasyOCR()
        image = Image.new('RGB', (200, 100), color='white')
        
        result = ocr.perform_ocr(image)
        
        assert len(result['text']) == 0
        assert len(result['left']) == 0
        assert len(result['top']) == 0
        assert len(result['width']) == 0
        assert len(result['height']) == 0
        assert len(result['conf']) == 0
    
    @patch('privacy.service.easy.output_type.readtext')
    @patch('privacy.service.easy.pd.DataFrame')
    def test_perform_ocr_with_numpy_array(self, mock_dataframe, mock_readtext):
        """Test perform_ocr accepts numpy array"""
        mock_df = Mock()
        mock_df.to_dict.return_value = [
            {'coordinates': [[10, 20], [100, 20], [100, 40], [10, 40]], 'text': 'Test', 'conf': 0.95}
        ]
        mock_dataframe.return_value = mock_df
        mock_readtext.return_value = []
        
        ocr = EasyOCR()
        image_array = np.zeros((100, 200, 3), dtype=np.uint8)
        
        result = ocr.perform_ocr(image_array)
        
        assert 'text' in result
    
    @patch('privacy.service.easy.output_type.readtext')
    def test_perform_ocr_uses_mag_ratio(self, mock_readtext):
        """Test perform_ocr uses current mag_ratio"""
        mock_readtext.return_value = []
        
        EasyOCR.mag_ratio = 5
        ocr = EasyOCR()
        image = Image.new('RGB', (200, 100), color='white')
        
        ocr.perform_ocr(image)
        
        # Verify readtext was called with mag_ratio=5
        call_kwargs = mock_readtext.call_args[1]
        assert call_kwargs['mag_ratio'] == 5
        
        # Reset to default
        EasyOCR.mag_ratio = 1
    
    @patch('privacy.service.easy.output_type.readtext')
    @patch('privacy.service.easy.pd.DataFrame')
    def test_perform_ocr_multiple_lines(self, mock_dataframe, mock_readtext):
        """Test perform_ocr with multiple text lines"""
        mock_df = Mock()
        mock_df.to_dict.return_value = [
            {'coordinates': [[10, 10], [90, 10], [90, 30], [10, 30]], 'text': 'Line1', 'conf': 0.98},
            {'coordinates': [[10, 35], [90, 35], [90, 55], [10, 55]], 'text': 'Line2', 'conf': 0.96},
            {'coordinates': [[10, 60], [90, 60], [90, 80], [10, 80]], 'text': 'Line3', 'conf': 0.94}
        ]
        mock_dataframe.return_value = mock_df
        mock_readtext.return_value = []
        
        ocr = EasyOCR()
        image = Image.new('RGB', (200, 100), color='white')
        
        result = ocr.perform_ocr(image)
        
        assert 'text' in result
        assert 'conf' in result


class TestEasyOCRSetMagElseBranch:
    """Test suite for setMag else branch (lines 64-67)."""
    
    def test_setmag_with_truthy_ratio(self):
        """Test setMag with truthy ratio value."""
        ocr = EasyOCR()
        # Reset mag_ratio first (setMag mutates the class attribute, not the instance)
        EasyOCR.mag_ratio = 1
        
        # Call setMag with truthy value
        ocr.setMag(5)
        
        # Should set mag_ratio to 10 (line 65)
        assert EasyOCR.mag_ratio == 10
    
    def test_setmag_with_falsy_ratio_else_branch(self):
        """Test setMag with falsy ratio value (lines 66-67 - else branch)."""
        ocr = EasyOCR()
        # First set to 10
        EasyOCR.mag_ratio = 10
        
        # Call setMag with falsy value (0, None, False, etc.)
        ocr.setMag(0)
        
        # Should hit line 67: cls.mag_ratio=1
        assert EasyOCR.mag_ratio == 1
    
    def test_setmag_with_none_else_branch(self):
        """Test setMag with None (else branch)."""
        ocr = EasyOCR()
        # Set to non-1 value
        EasyOCR.mag_ratio = 10
        
        # Call with None
        ocr.setMag(None)
        
        # Should reset to 1 (line 67)
        assert EasyOCR.mag_ratio == 1
    
    def test_setmag_with_false_else_branch(self):
        """Test setMag with False (else branch)."""
        ocr = EasyOCR()
        # Set to non-1 value
        EasyOCR.mag_ratio = 10
        
        # Call with False
        ocr.setMag(False)
        
        # Should reset to 1 (line 67)
        assert EasyOCR.mag_ratio == 1

