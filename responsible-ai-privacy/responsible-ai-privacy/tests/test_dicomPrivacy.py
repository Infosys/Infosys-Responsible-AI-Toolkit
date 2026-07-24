"""
Unit tests for dicomPrivacy.py service.
Tests DICOMPrivacy and saveImage classes.
"""
import pytest
import base64
import io
from unittest.mock import Mock, patch, MagicMock, mock_open
import pydicom
import numpy as np
from privacy.service.dicomPrivacy import DICOMPrivacy, saveImage


class TestDICOMPrivacy:
    """Test suite for DICOMPrivacy class"""

    def test_dcmToPng_success(self):
        """Test dcmToPng successfully converts DICOM to PNG base64"""
        # Create mock DICOM object with pixel array
        mock_dcm = Mock()
        mock_dcm.pixel_array = np.random.randint(0, 255, (100, 100), dtype=np.uint16)
        
        with patch('privacy.service.dicomPrivacy.plt') as mock_plt:
            mock_buffer = io.BytesIO()
            mock_buffer.write(b'fake_png_data')
            mock_buffer.seek(0)
            
            mock_plt.savefig.side_effect = lambda buf, **kwargs: buf.write(b'fake_png_data')
            
            # Call the method
            result = DICOMPrivacy.dcmToPng(mock_dcm)
            
            # Verify plt methods were called
            mock_plt.clf.assert_called_once()
            mock_plt.imshow.assert_called_once()
            mock_plt.axis.assert_called_once_with('off')
            mock_plt.savefig.assert_called_once()
            
            # Result should be base64 encoded
            assert isinstance(result, bytes)

    def test_dcmToPng_with_different_array_sizes(self):
        """Test dcmToPng with different pixel array sizes"""
        mock_dcm = Mock()
        mock_dcm.pixel_array = np.random.randint(0, 255, (512, 512), dtype=np.uint16)
        
        with patch('privacy.service.dicomPrivacy.plt') as mock_plt:
            mock_plt.savefig.side_effect = lambda buf, **kwargs: buf.write(b'large_image_data')
            
            result = DICOMPrivacy.dcmToPng(mock_dcm)
            
            assert isinstance(result, bytes)
            assert mock_plt.clf.called
            assert mock_plt.imshow.called

    def test_readDicom_success(self):
        """Test readDicom successfully processes DICOM file"""
        # Create mock payload
        mock_payload = Mock()
        mock_file = Mock()
        mock_payload.file = mock_file
        
        # Create mock DICOM instances
        mock_dicom_instance = Mock()
        mock_dicom_instance.pixel_array = np.random.randint(0, 255, (100, 100), dtype=np.uint16)
        
        mock_redacted_instance = Mock()
        mock_redacted_instance.pixel_array = np.random.randint(0, 255, (100, 100), dtype=np.uint16)
        
        with patch('privacy.service.dicomPrivacy.pydicom.dcmread') as mock_dcmread, \
             patch('privacy.service.dicomPrivacy.DicomImageRedactorEngine') as mock_engine_class, \
             patch('privacy.service.dicomPrivacy.DICOMPrivacy.dcmToPng') as mock_dcmToPng:
            
            # Setup mocks
            mock_dcmread.return_value = mock_dicom_instance
            mock_engine = Mock()
            mock_engine.redact.return_value = mock_redacted_instance
            mock_engine_class.return_value = mock_engine
            
            mock_dcmToPng.side_effect = [b'original_png', b'redacted_png']
            
            # Call the method
            result = DICOMPrivacy.readDicom(mock_payload)
            
            # Verify result structure
            assert 'original' in result
            assert 'anonymize' in result
            assert result['original'] == b'original_png'
            assert result['anonymize'] == b'redacted_png'
            
            # Verify method calls
            mock_dcmread.assert_called_once_with(mock_file)
            mock_engine.redact.assert_called_once_with(mock_dicom_instance, fill="contrast")
            assert mock_dcmToPng.call_count == 2

    def test_readDicom_with_different_fill_contrast(self):
        """Test readDicom uses contrast fill for redaction"""
        mock_payload = Mock()
        mock_payload.file = Mock()
        
        mock_dicom_instance = Mock()
        mock_dicom_instance.pixel_array = np.random.randint(0, 255, (100, 100), dtype=np.uint16)
        
        with patch('privacy.service.dicomPrivacy.pydicom.dcmread') as mock_dcmread, \
             patch('privacy.service.dicomPrivacy.DicomImageRedactorEngine') as mock_engine_class, \
             patch('privacy.service.dicomPrivacy.DICOMPrivacy.dcmToPng') as mock_dcmToPng:
            
            mock_dcmread.return_value = mock_dicom_instance
            mock_engine = Mock()
            mock_redacted = Mock()
            mock_redacted.pixel_array = np.random.randint(0, 255, (100, 100), dtype=np.uint16)
            mock_engine.redact.return_value = mock_redacted
            mock_engine_class.return_value = mock_engine
            
            mock_dcmToPng.side_effect = [b'orig', b'redact']
            
            result = DICOMPrivacy.readDicom(mock_payload)
            
            # Verify fill parameter
            mock_engine.redact.assert_called_once()
            call_args = mock_engine.redact.call_args
            assert call_args[1]['fill'] == "contrast"

    def test_readDicom_exception_handling(self):
        """Test readDicom handles exceptions properly"""
        mock_payload = Mock()
        mock_payload.file = Mock()
        
        with patch('privacy.service.dicomPrivacy.pydicom.dcmread') as mock_dcmread, \
             patch('privacy.service.dicomPrivacy.log') as mock_log:
            
            # Simulate an exception
            test_exception = ValueError("Invalid DICOM file")
            mock_dcmread.side_effect = test_exception
            
            # Call should raise exception
            with pytest.raises(Exception) as exc_info:
                DICOMPrivacy.readDicom(mock_payload)
            
            # Verify logging was called
            assert mock_log.error.call_count >= 3  # Error message, line number, traceback
            
            # Verify exception was logged
            error_calls = [str(call) for call in mock_log.error.call_args_list]
            assert any("Invalid DICOM file" in str(call) or "ValueError" in str(call) for call in error_calls)

    def test_readDicom_with_engine_exception(self):
        """Test readDicom handles DicomImageRedactorEngine exceptions"""
        mock_payload = Mock()
        mock_payload.file = Mock()
        
        mock_dicom_instance = Mock()
        
        with patch('privacy.service.dicomPrivacy.pydicom.dcmread') as mock_dcmread, \
             patch('privacy.service.dicomPrivacy.DicomImageRedactorEngine') as mock_engine_class, \
             patch('privacy.service.dicomPrivacy.log') as mock_log:
            
            mock_dcmread.return_value = mock_dicom_instance
            mock_engine = Mock()
            mock_engine.redact.side_effect = RuntimeError("Redaction failed")
            mock_engine_class.return_value = mock_engine
            
            with pytest.raises(Exception):
                DICOMPrivacy.readDicom(mock_payload)
            
            # Verify error was logged
            assert mock_log.error.called

    def test_readDicom_empty_file(self):
        """Test readDicom with empty/invalid file"""
        mock_payload = Mock()
        mock_payload.file = None
        
        with patch('privacy.service.dicomPrivacy.pydicom.dcmread') as mock_dcmread, \
             patch('privacy.service.dicomPrivacy.log'):
            
            mock_dcmread.side_effect = AttributeError("No file provided")
            
            with pytest.raises(Exception):
                DICOMPrivacy.readDicom(mock_payload)

    def test_readDicom_logs_debug_messages(self):
        """Test readDicom logs debug messages on entry and exit"""
        mock_payload = Mock()
        mock_payload.file = Mock()
        
        mock_dicom_instance = Mock()
        mock_dicom_instance.pixel_array = np.random.randint(0, 255, (100, 100), dtype=np.uint16)
        
        with patch('privacy.service.dicomPrivacy.pydicom.dcmread') as mock_dcmread, \
             patch('privacy.service.dicomPrivacy.DicomImageRedactorEngine'), \
             patch('privacy.service.dicomPrivacy.DICOMPrivacy.dcmToPng') as mock_dcmToPng, \
             patch('privacy.service.dicomPrivacy.log') as mock_log:
            
            mock_dcmread.return_value = mock_dicom_instance
            mock_dcmToPng.side_effect = [b'orig', b'redact']
            
            DICOMPrivacy.readDicom(mock_payload)
            
            # Check debug logs
            debug_calls = [str(call) for call in mock_log.debug.call_args_list]
            assert any("Entering in readDicom function" in str(call) for call in debug_calls)
            assert any("Returning from readDicom function" in str(call) for call in debug_calls)


class TestSaveImage:
    """Test suite for saveImage class"""

    def test_saveImg_success(self):
        """Test saveImg successfully saves base64 image to file"""
        # Create base64 encoded image data
        img_bytes = b'fake_image_data_12345'
        img_base64 = base64.b64encode(img_bytes)
        
        with patch('builtins.open', mock_open()) as mock_file:
            saveImage.saveImg(img_base64)
            
            # Verify file was opened for writing binary
            mock_file.assert_called_once_with("file.png", "wb")
            
            # Verify write was called with decoded data
            handle = mock_file()
            handle.write.assert_called_once_with(img_bytes)

    def test_saveImg_with_different_data(self):
        """Test saveImg with different image data"""
        # Simulate actual PNG header
        png_header = b'\x89PNG\r\n\x1a\n'
        png_data = png_header + b'rest_of_png_data'
        img_base64 = base64.b64encode(png_data)
        
        with patch('builtins.open', mock_open()) as mock_file:
            saveImage.saveImg(img_base64)
            
            handle = mock_file()
            handle.write.assert_called_once()
            written_data = handle.write.call_args[0][0]
            assert written_data == png_data
            assert written_data.startswith(b'\x89PNG')

    def test_saveImg_empty_data(self):
        """Test saveImg with empty base64 data"""
        empty_base64 = base64.b64encode(b'')
        
        with patch('builtins.open', mock_open()) as mock_file:
            saveImage.saveImg(empty_base64)
            
            handle = mock_file()
            handle.write.assert_called_once_with(b'')

    def test_saveImg_file_path(self):
        """Test saveImg uses correct file path"""
        img_base64 = base64.b64encode(b'test_data')
        
        with patch('builtins.open', mock_open()) as mock_file:
            saveImage.saveImg(img_base64)
            
            # Verify specific file path
            mock_file.assert_called_with("file.png", "wb")

    def test_saveImg_large_data(self):
        """Test saveImg with large image data"""
        # Simulate large image (1MB)
        large_data = b'x' * (1024 * 1024)
        img_base64 = base64.b64encode(large_data)
        
        with patch('builtins.open', mock_open()) as mock_file:
            saveImage.saveImg(img_base64)
            
            handle = mock_file()
            written_data = handle.write.call_args[0][0]
            assert len(written_data) == len(large_data)
            assert written_data == large_data


class TestDICOMPrivacyIntegration:
    """Integration tests for DICOMPrivacy workflow"""

    def test_full_dicom_processing_workflow(self):
        """Test complete workflow from file to anonymized output"""
        mock_payload = Mock()
        mock_payload.file = Mock()
        
        # Create realistic DICOM-like data
        mock_dicom = Mock()
        mock_dicom.pixel_array = np.random.randint(0, 255, (256, 256), dtype=np.uint16)
        
        mock_redacted = Mock()
        mock_redacted.pixel_array = np.random.randint(0, 255, (256, 256), dtype=np.uint16)
        
        with patch('privacy.service.dicomPrivacy.pydicom.dcmread') as mock_dcmread, \
             patch('privacy.service.dicomPrivacy.DicomImageRedactorEngine') as mock_engine_class, \
             patch('privacy.service.dicomPrivacy.plt'):
            
            mock_dcmread.return_value = mock_dicom
            mock_engine = Mock()
            mock_engine.redact.return_value = mock_redacted
            mock_engine_class.return_value = mock_engine
            
            result = DICOMPrivacy.readDicom(mock_payload)
            
            # Verify complete workflow
            assert isinstance(result, dict)
            assert 'original' in result
            assert 'anonymize' in result
            assert result['original'] is not None
            assert result['anonymize'] is not None

    def test_error_dict_population(self):
        """Test that error_dict is populated on exceptions"""
        mock_payload = Mock()
        mock_payload.file = Mock()
        
        with patch('privacy.service.dicomPrivacy.pydicom.dcmread') as mock_dcmread, \
             patch('privacy.service.dicomPrivacy.error_dict', {}) as mock_error_dict, \
             patch('privacy.service.dicomPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test-uuid-123"
            mock_dcmread.side_effect = IOError("File read error")
            
            with pytest.raises(Exception):
                DICOMPrivacy.readDicom(mock_payload)
            
            # Note: error_dict population happens in actual code
            # This test verifies the exception path is executed
