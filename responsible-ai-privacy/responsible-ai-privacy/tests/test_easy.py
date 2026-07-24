"""
Tests for easy.py module
"""

import pytest
from privacy.service.easy import EasyOCR, Data


class TestEasyOCR:
    """Test suite for EasyOCR class"""

    def test_setMag_with_true_sets_ratio_to_10(self):
        """Test that setMag(True) sets mag_ratio to 10"""
        EasyOCR.mag_ratio = 1  # Reset to default
        EasyOCR.setMag(True)
        assert EasyOCR.mag_ratio == 10

    def test_setMag_with_false_sets_ratio_to_1(self):
        """Test that setMag(False) sets mag_ratio to 1"""
        EasyOCR.mag_ratio = 10  # Set to non-default
        EasyOCR.setMag(False)
        assert EasyOCR.mag_ratio == 1

    def test_setMag_with_none_sets_ratio_to_1(self):
        """Test that setMag(None) sets mag_ratio to 1"""
        EasyOCR.mag_ratio = 10  # Set to non-default
        EasyOCR.setMag(None)
        assert EasyOCR.mag_ratio == 1

    def test_setMag_with_truthy_value_sets_ratio_to_10(self):
        """Test that setMag with truthy value sets mag_ratio to 10"""
        EasyOCR.mag_ratio = 1  # Reset to default
        EasyOCR.setMag(1)  # Truthy value
        assert EasyOCR.mag_ratio == 10

    def test_process_returns_input_unchanged(self):
        """Test that process() returns input unchanged"""
        test_input = "test_data"
        result = EasyOCR.process(test_input)
        assert result == test_input

    def test_process_with_various_types(self):
        """Test that process works with different data types"""
        assert EasyOCR.process(42) == 42
        assert EasyOCR.process([1, 2, 3]) == [1, 2, 3]
        assert EasyOCR.process({"key": "value"}) == {"key": "value"}


class TestData:
    """Test suite for Data class"""

    def test_data_class_has_encrypted_text_attribute(self):
        """Test that Data class has encrypted_text as empty list"""
        assert hasattr(Data, 'encrypted_text')
        assert isinstance(Data.encrypted_text, list)
        assert len(Data.encrypted_text) == 0


class TestEasyOCRPerformOCR:
    """Test suite for EasyOCR perform_ocr method"""

    @pytest.fixture
    def mock_easyocr_response(self):
        """Fixture providing mock easyocr readtext response"""
        return [
            [[[10, 20], [100, 20], [100, 50], [10, 50]], 'Hello', 0.95],
            [[[10, 60], [150, 60], [150, 90], [10, 90]], 'World', 0.92],
        ]

    @pytest.fixture
    def mock_image(self):
        """Fixture providing a mock PIL image"""
        from PIL import Image
        import numpy as np
        # Create a simple image
        return Image.fromarray(np.ones((100, 100, 3), dtype=np.uint8) * 255)

    def test_perform_ocr_processes_coordinates_correctly(self, mock_image, mock_easyocr_response, monkeypatch):
        """Test that perform_ocr correctly processes coordinate transformations"""
        from unittest.mock import Mock
        import pandas as pd
        
        # Mock the easyocr reader output
        mock_reader = Mock()
        mock_reader.readtext.return_value = mock_easyocr_response
        monkeypatch.setattr('privacy.service.easy.output_type', mock_reader)
        
        ocr = EasyOCR()
        result = ocr.perform_ocr(mock_image)
        
        # Verify textmap structure
        assert 'text' in result
        assert 'left' in result
        assert 'top' in result
        assert 'width' in result
        assert 'height' in result
        assert 'conf' in result
        
        # Verify first item (covers lines 99-104)
        assert result['text'][0] == 'Hello'
        assert result['left'][0] == 10  # min(10, 10)
        assert result['top'][0] == 20   # min(20, 20)
        assert result['width'][0] == 90  # abs(100-10)
        assert result['height'][0] == 30  # abs(50-20)
        assert result['conf'][0] == 0.95

    def test_perform_ocr_handles_multiple_words(self, mock_image, monkeypatch):
        """Test that perform_ocr handles multiple words in output"""
        from unittest.mock import Mock
        
        multi_word_response = [
            [[[5, 10], [50, 10], [50, 30], [5, 30]], 'One', 0.98],
            [[[55, 10], [100, 10], [100, 30], [55, 30]], 'Two', 0.97],
            [[[5, 35], [50, 35], [50, 55], [5, 55]], 'Three', 0.96],
        ]
        
        mock_reader = Mock()
        mock_reader.readtext.return_value = multi_word_response
        monkeypatch.setattr('privacy.service.easy.output_type', mock_reader)
        
        ocr = EasyOCR()
        result = ocr.perform_ocr(mock_image)
        
        # Verify all three words were processed
        assert len(result['text']) == 3
        assert result['text'] == ['One', 'Two', 'Three']
        assert len(result['left']) == 3
        assert len(result['conf']) == 3
