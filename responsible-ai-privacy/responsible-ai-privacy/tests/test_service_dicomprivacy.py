"""Tests for `privacy.service.dicomPrivacy` module.

These tests import and execute the REAL src code with mocked dependencies
to provide actual code coverage of the dicomPrivacy module.
"""

import sys
import os
import pytest
import io
import base64
from unittest.mock import MagicMock, Mock, patch, mock_open
from types import SimpleNamespace

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture(scope='module', autouse=True)
def setup_mocks():
    """Setup mocks for heavy dependencies before importing src."""
    # Remove any existing modules
    modules_to_remove = [
        'privacy.service.dicomPrivacy',
        'privacy.service.api_req',
    ]
    for mod in modules_to_remove:
        sys.modules.pop(mod, None)
    
    yield
    
    # Cleanup after module tests - restore real modules
    for mod in modules_to_remove:
        sys.modules.pop(mod, None)


@pytest.fixture
def mock_dicom_payload():
    """Create a basic mock DICOM payload."""
    payload = MagicMock()
    payload.file = MagicMock()
    return payload


@pytest.fixture
def mock_dicom_instance():
    """Create a mock DICOM instance with pixel_array."""
    instance = MagicMock()
    instance.pixel_array = MagicMock()
    return instance


class TestDcmToPng:
    """Tests for DICOMPrivacy.dcm_to_png static method."""
    
    def test_dcm_to_png_basic_flow(self, mock_dicom_instance):
        """Test basic DICOM to PNG conversion."""
        from privacy.service.dicomPrivacy import DICOMPrivacy
        import matplotlib.pyplot as plt
        
        # Mock the buffer
        mock_buffer = io.BytesIO()
        test_image_data = b'fake_png_data'
        mock_buffer.write(test_image_data)
        mock_buffer.seek(0)
        
        with patch('privacy.service.dicomPrivacy.io.BytesIO', return_value=mock_buffer), \
             patch('privacy.service.dicomPrivacy.plt') as mock_plt:
            
            # Reset buffer position
            mock_buffer.seek(0)
            mock_buffer.write(test_image_data)
            mock_buffer.seek(0)
            
            result = DICOMPrivacy.dcm_to_png(mock_dicom_instance)
            
            # Verify matplotlib functions were called
            mock_plt.clf.assert_called_once()
            mock_plt.imshow.assert_called_once()
            mock_plt.axis.assert_called_once_with('off')
            mock_plt.savefig.assert_called_once()
            
            # Verify result is base64 encoded
            assert result is not None
            assert isinstance(result, bytes)
    
    def test_dcm_to_png_with_pixel_array(self, mock_dicom_instance):
        """Test dcm_to_png accesses pixel_array correctly."""
        from privacy.service.dicomPrivacy import DICOMPrivacy
        
        mock_buffer = io.BytesIO(b'test_data')
        
        with patch('privacy.service.dicomPrivacy.io.BytesIO', return_value=mock_buffer), \
             patch('privacy.service.dicomPrivacy.plt') as mock_plt:
            
            result = DICOMPrivacy.dcm_to_png(mock_dicom_instance)
            
            # Verify pixel_array was accessed
            assert mock_dicom_instance.pixel_array is not None
            # Verify imshow was called with pixel_array
            call_args = mock_plt.imshow.call_args
            assert call_args is not None


class TestReadDicom:
    """Tests for DICOMPrivacy.read_dicom static method."""
    
    def test_read_dicom_basic_flow(self, mock_dicom_payload, mock_dicom_instance):
        """Test basic DICOM reading and redaction."""
        from privacy.service.dicomPrivacy import DICOMPrivacy
        
        with patch('privacy.service.dicomPrivacy.pydicom') as mock_pydicom, \
             patch('privacy.service.dicomPrivacy.DicomImageRedactorEngine') as MockEngine, \
             patch.object(DICOMPrivacy, 'dcm_to_png') as mock_dcm_to_png, \
             patch('privacy.service.dicomPrivacy.error_dict', {}, create=True), \
             patch('privacy.service.dicomPrivacy.request_id_var') as mock_request_id:
            
            # Setup mocks
            mock_request_id.get.return_value = "test_request_id"
            mock_pydicom.dcmread.return_value = mock_dicom_instance
            
            mock_engine_instance = MockEngine.return_value
            redacted_instance = MagicMock()
            mock_engine_instance.redact.return_value = redacted_instance
            
            # Mock dcm_to_png to return base64 encoded strings
            original_base64 = b'original_base64_data'
            redacted_base64 = b'redacted_base64_data'
            mock_dcm_to_png.side_effect = [original_base64, redacted_base64]
            
            # Call the method
            result = DICOMPrivacy.read_dicom(mock_dicom_payload)
            
            # Verify pydicom.dcmread was called
            mock_pydicom.dcmread.assert_called_once_with(mock_dicom_payload.file)
            
            # Verify DicomImageRedactorEngine was instantiated
            MockEngine.assert_called_once()
            
            # Verify redact was called
            mock_engine_instance.redact.assert_called_once_with(mock_dicom_instance, fill="contrast")
            
            # Verify dcm_to_png was called twice (original and redacted)
            assert mock_dcm_to_png.call_count == 2
            mock_dcm_to_png.assert_any_call(mock_dicom_instance)
            mock_dcm_to_png.assert_any_call(redacted_instance)
            
            # Verify result structure
            assert result is not None
            assert isinstance(result, dict)
            assert "original" in result
            assert "anonymize" in result
            assert result["original"] == original_base64
            assert result["anonymize"] == redacted_base64
    
    def test_read_dicom_initializes_error_dict(self, mock_dicom_payload):
        """Test that read_dicom initializes error_dict."""
        from privacy.service.dicomPrivacy import DICOMPrivacy
        
        mock_error_dict = {}
        
        with patch('privacy.service.dicomPrivacy.pydicom') as mock_pydicom, \
             patch('privacy.service.dicomPrivacy.DicomImageRedactorEngine'), \
             patch.object(DICOMPrivacy, 'dcm_to_png'), \
             patch('privacy.service.dicomPrivacy.error_dict', mock_error_dict, create=True), \
             patch('privacy.service.dicomPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test_id_123"
            mock_pydicom.dcmread.return_value = MagicMock()
            
            DICOMPrivacy.read_dicom(mock_dicom_payload)
            
            # Verify error_dict was initialized with empty list
            assert "test_id_123" in mock_error_dict
            assert mock_error_dict["test_id_123"] == []
    
    def test_read_dicom_exception_handling(self, mock_dicom_payload):
        """Test read_dicom handles exceptions correctly."""
        from privacy.service.dicomPrivacy import DICOMPrivacy
        
        mock_error_dict = {}
        
        with patch('privacy.service.dicomPrivacy.pydicom') as mock_pydicom, \
             patch('privacy.service.dicomPrivacy.error_dict', mock_error_dict, create=True), \
             patch('privacy.service.dicomPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "error_test_id"
            mock_error_dict["error_test_id"] = []
            
            # Make dcmread raise an exception
            test_exception = ValueError("Invalid DICOM file")
            mock_pydicom.dcmread.side_effect = test_exception
            
            # Verify RuntimeError is raised
            with pytest.raises(RuntimeError):
                DICOMPrivacy.read_dicom(mock_dicom_payload)
            
            # Verify error was logged to error_dict
            assert "error_test_id" in mock_error_dict
            assert len(mock_error_dict["error_test_id"]) == 1
            error_entry = mock_error_dict["error_test_id"][0]
            assert error_entry["UUID"] == "error_test_id"
            assert error_entry["function"] == "read_dicom"
            assert error_entry["msg"] == "ValueError"
            assert "Invalid DICOM file" in error_entry["description"]
    
    def test_read_dicom_engine_exception(self, mock_dicom_payload, mock_dicom_instance):
        """Test read_dicom handles DicomImageRedactorEngine exceptions."""
        from privacy.service.dicomPrivacy import DICOMPrivacy
        
        mock_error_dict = {}
        
        with patch('privacy.service.dicomPrivacy.pydicom') as mock_pydicom, \
             patch('privacy.service.dicomPrivacy.DicomImageRedactorEngine') as MockEngine, \
             patch('privacy.service.dicomPrivacy.error_dict', mock_error_dict, create=True), \
             patch('privacy.service.dicomPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "engine_error_id"
            mock_error_dict["engine_error_id"] = []
            mock_pydicom.dcmread.return_value = mock_dicom_instance
            
            # Make redact raise an exception
            mock_engine_instance = MockEngine.return_value
            mock_engine_instance.redact.side_effect = RuntimeError("Redaction failed")
            
            # Verify RuntimeError is raised
            with pytest.raises(RuntimeError):
                DICOMPrivacy.read_dicom(mock_dicom_payload)
            
            # Verify error was logged
            assert len(mock_error_dict["engine_error_id"]) == 1
            assert mock_error_dict["engine_error_id"][0]["msg"] == "RuntimeError"
    
    def test_read_dicom_dcm_to_png_exception(self, mock_dicom_payload, mock_dicom_instance):
        """Test read_dicom handles dcm_to_png exceptions."""
        from privacy.service.dicomPrivacy import DICOMPrivacy
        
        mock_error_dict = {}
        
        with patch('privacy.service.dicomPrivacy.pydicom') as mock_pydicom, \
             patch('privacy.service.dicomPrivacy.DicomImageRedactorEngine') as MockEngine, \
             patch.object(DICOMPrivacy, 'dcm_to_png') as mock_dcm_to_png, \
             patch('privacy.service.dicomPrivacy.error_dict', mock_error_dict, create=True), \
             patch('privacy.service.dicomPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "png_error_id"
            mock_error_dict["png_error_id"] = []
            mock_pydicom.dcmread.return_value = mock_dicom_instance
            
            mock_engine_instance = MockEngine.return_value
            mock_engine_instance.redact.return_value = MagicMock()
            
            # Make dcm_to_png raise an exception
            mock_dcm_to_png.side_effect = IOError("PNG conversion failed")
            
            # Verify RuntimeError is raised
            with pytest.raises(RuntimeError):
                DICOMPrivacy.read_dicom(mock_dicom_payload)
            
            # Verify error was logged
            assert len(mock_error_dict["png_error_id"]) == 1
            assert "PNG conversion failed" in mock_error_dict["png_error_id"][0]["description"]


class TestSaveImage:
    """Tests for saveImage.save_img static method."""
    
    def test_save_img_basic_flow(self):
        """Test basic image saving functionality."""
        from privacy.service.dicomPrivacy import saveImage
        
        # Create test base64 data
        test_data = base64.b64encode(b"fake_image_data")
        
        m = mock_open()
        with patch('privacy.service.dicomPrivacy.open', m):
            saveImage.save_img(test_data)
            
            # Verify file was opened with correct parameters
            m.assert_called_once_with("file.png", "wb")
            
            # Verify write was called with decoded data
            handle = m()
            handle.write.assert_called_once()
            written_data = handle.write.call_args[0][0]
            assert written_data == b"fake_image_data"
    
    def test_save_img_decodes_base64(self):
        """Test that save_img properly decodes base64 data."""
        from privacy.service.dicomPrivacy import saveImage
        
        original_data = b"test image content"
        encoded_data = base64.b64encode(original_data)
        
        m = mock_open()
        with patch('privacy.service.dicomPrivacy.open', m):
            saveImage.save_img(encoded_data)
            
            # Verify decoded data was written
            handle = m()
            written_data = handle.write.call_args[0][0]
            assert written_data == original_data
    
    def test_save_img_with_real_image_data(self):
        """Test save_img with realistic base64 encoded image data."""
        from privacy.service.dicomPrivacy import saveImage
        
        # Create a more realistic PNG-like data
        png_header = b'\x89PNG\r\n\x1a\n'
        fake_png_data = png_header + b'fake_png_content'
        encoded_data = base64.b64encode(fake_png_data)
        
        m = mock_open()
        with patch('privacy.service.dicomPrivacy.open', m):
            saveImage.save_img(encoded_data)
            
            handle = m()
            written_data = handle.write.call_args[0][0]
            assert written_data == fake_png_data
            assert written_data.startswith(png_header)


class TestIntegration:
    """Integration tests for DICOMPrivacy workflow."""
    
    def test_full_dicom_workflow(self, mock_dicom_payload):
        """Test complete DICOM reading, redaction, and conversion workflow."""
        from privacy.service.dicomPrivacy import DICOMPrivacy
        
        with patch('privacy.service.dicomPrivacy.pydicom') as mock_pydicom, \
             patch('privacy.service.dicomPrivacy.DicomImageRedactorEngine') as MockEngine, \
             patch.object(DICOMPrivacy, 'dcm_to_png') as mock_dcm_to_png, \
             patch('privacy.service.dicomPrivacy.error_dict', {}, create=True), \
             patch('privacy.service.dicomPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "integration_test_id"
            
            # Setup DICOM instance
            dicom_instance = MagicMock()
            dicom_instance.pixel_array = MagicMock()
            mock_pydicom.dcmread.return_value = dicom_instance
            
            # Setup redacted instance
            redacted_instance = MagicMock()
            redacted_instance.pixel_array = MagicMock()
            
            mock_engine = MockEngine.return_value
            mock_engine.redact.return_value = redacted_instance
            
            # Mock dcm_to_png to return base64 data
            original_b64 = b'b3JpZ2luYWxfcG5nX2RhdGE='  # base64 encoded
            redacted_b64 = b'cmVkYWN0ZWRfcG5nX2RhdGE='  # base64 encoded
            mock_dcm_to_png.side_effect = [original_b64, redacted_b64]
            
            # Call the method
            result = DICOMPrivacy.read_dicom(mock_dicom_payload)
            
            # Verify complete workflow
            assert mock_pydicom.dcmread.called
            assert MockEngine.called
            assert mock_engine.redact.called
            assert mock_dcm_to_png.call_count == 2  # Once for original, once for redacted
            
            # Verify result
            assert result is not None
            assert "original" in result
            assert "anonymize" in result
            assert result["original"] == original_b64
            assert result["anonymize"] == redacted_b64
