"""Tests for `privacy.service.dicom_service` module.

These tests import and execute the REAL src code with mocked dependencies
to provide actual code coverage of the dicom_service module.
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
        'privacy.service.dicom_service',
    ]
    for mod in modules_to_remove:
        sys.modules.pop(mod, None)
    
    yield
    
    # Cleanup after module tests
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


class TestDicomDcmToPng:
    """Tests for DICOM.dcm_to_png static method."""
    
    def test_dcm_to_png_basic_flow(self, mock_dicom_instance):
        """Test basic DICOM to PNG conversion."""
        from privacy.service.dicom_service import DICOM
        
        # Mock the BytesIO and matplotlib
        mock_buffer = io.BytesIO()
        test_image_data = b'fake_png_data'
        mock_buffer.write(test_image_data)
        mock_buffer.seek(0)
        
        with patch('privacy.service.dicom_service.BytesIO', return_value=mock_buffer), \
             patch('privacy.service.dicom_service.plt') as mock_plt:
            
            # Reset buffer
            mock_buffer.seek(0)
            mock_buffer.write(test_image_data)
            mock_buffer.seek(0)
            
            result = DICOM.dcm_to_png(mock_dicom_instance)
            
            # Verify matplotlib functions were called
            mock_plt.imshow.assert_called_once()
            mock_plt.axis.assert_called_once_with('off')
            mock_plt.savefig.assert_called_once()
            
            # Verify result is base64 encoded
            assert result is not None
            assert isinstance(result, bytes)
    
    def test_dcm_to_png_uses_bone_colormap(self, mock_dicom_instance):
        """Test dcm_to_png uses bone colormap for medical imaging."""
        from privacy.service.dicom_service import DICOM
        
        mock_buffer = io.BytesIO(b'test_data')
        
        with patch('privacy.service.dicom_service.BytesIO', return_value=mock_buffer), \
             patch('privacy.service.dicom_service.plt') as mock_plt:
            
            DICOM.dcm_to_png(mock_dicom_instance)
            
            # Verify imshow was called with cmap parameter
            call_args = mock_plt.imshow.call_args
            assert 'cmap' in call_args[1]
    
    def test_dcm_to_png_saves_with_correct_format(self, mock_dicom_instance):
        """Test dcm_to_png saves as PNG format with correct parameters."""
        from privacy.service.dicom_service import DICOM
        
        mock_buffer = io.BytesIO(b'test_data')
        
        with patch('privacy.service.dicom_service.BytesIO', return_value=mock_buffer), \
             patch('privacy.service.dicom_service.plt') as mock_plt:
            
            DICOM.dcm_to_png(mock_dicom_instance)
            
            # Verify savefig was called with correct parameters
            call_args = mock_plt.savefig.call_args
            assert call_args[1]['format'] == 'png'
            assert call_args[1]['bbox_inches'] == 'tight'
            assert call_args[1]['pad_inches'] == 0
    
    def test_dcm_to_png_accesses_pixel_array(self, mock_dicom_instance):
        """Test dcm_to_png accesses DICOM pixel_array."""
        from privacy.service.dicom_service import DICOM
        
        mock_buffer = io.BytesIO(b'test_data')
        
        with patch('privacy.service.dicom_service.BytesIO', return_value=mock_buffer), \
             patch('privacy.service.dicom_service.plt') as mock_plt:
            
            DICOM.dcm_to_png(mock_dicom_instance)
            
            # Verify pixel_array was accessed
            assert mock_dicom_instance.pixel_array is not None


class TestDicomReadDicom:
    """Tests for DICOM.read_dicom static method."""
    
    def test_read_dicom_basic_flow(self, mock_dicom_payload, mock_dicom_instance):
        """Test basic DICOM reading and redaction."""
        from privacy.service.dicom_service import DICOM
        
        with patch('privacy.service.dicom_service.pydicom') as mock_pydicom, \
             patch('privacy.service.dicom_service.DicomImageRedactorEngine') as MockEngine, \
             patch.object(DICOM, 'dcm_to_png') as mock_dcm_to_png, \
             patch('builtins.print'):
            
            # Setup mocks
            mock_pydicom.dcmread.return_value = mock_dicom_instance
            
            mock_engine_instance = MockEngine.return_value
            redacted_instance = MagicMock()
            mock_engine_instance.redact.return_value = redacted_instance
            
            # Mock dcm_to_png to return base64 encoded strings
            original_base64 = b'original_base64_data'
            redacted_base64 = b'redacted_base64_data'
            mock_dcm_to_png.side_effect = [original_base64, redacted_base64]
            
            # Call the method
            result = DICOM.read_dicom(mock_dicom_payload)
            
            # Verify pydicom.dcmread was called
            mock_pydicom.dcmread.assert_called_once_with(mock_dicom_payload.file)
            
            # Verify DicomImageRedactorEngine was instantiated
            MockEngine.assert_called_once()
            
            # Verify redact was called with correct parameters
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
    
    def test_read_dicom_prints_instance_type(self, mock_dicom_payload, mock_dicom_instance):
        """Test read_dicom prints the DICOM instance type."""
        from privacy.service.dicom_service import DICOM
        
        with patch('privacy.service.dicom_service.pydicom') as mock_pydicom, \
             patch('privacy.service.dicom_service.DicomImageRedactorEngine') as MockEngine, \
             patch.object(DICOM, 'dcm_to_png') as mock_dcm_to_png, \
             patch('builtins.print') as mock_print:
            
            mock_pydicom.dcmread.return_value = mock_dicom_instance
            mock_engine_instance = MockEngine.return_value
            mock_engine_instance.redact.return_value = MagicMock()
            mock_dcm_to_png.side_effect = [b'orig', b'redact']
            
            DICOM.read_dicom(mock_dicom_payload)
            
            # Verify print was called
            mock_print.assert_called_once()
    
    def test_read_dicom_creates_engine_and_redacts(self, mock_dicom_payload, mock_dicom_instance):
        """Test read_dicom creates engine and performs redaction."""
        from privacy.service.dicom_service import DICOM
        
        with patch('privacy.service.dicom_service.pydicom') as mock_pydicom, \
             patch('privacy.service.dicom_service.DicomImageRedactorEngine') as MockEngine, \
             patch.object(DICOM, 'dcm_to_png') as mock_dcm_to_png, \
             patch('builtins.print'):
            
            mock_pydicom.dcmread.return_value = mock_dicom_instance
            mock_engine = MockEngine.return_value
            redacted_mock = MagicMock()
            mock_engine.redact.return_value = redacted_mock
            mock_dcm_to_png.side_effect = [b'original', b'redacted']
            
            result = DICOM.read_dicom(mock_dicom_payload)
            
            # Verify engine was created
            MockEngine.assert_called_once()
            
            # Verify redact was called with fill parameter
            mock_engine.redact.assert_called_once()
            call_args = mock_engine.redact.call_args
            assert call_args[1]['fill'] == "contrast"
    
    def test_read_dicom_converts_both_original_and_redacted(self, mock_dicom_payload, mock_dicom_instance):
        """Test read_dicom converts both original and redacted DICOM to PNG."""
        from privacy.service.dicom_service import DICOM
        
        with patch('privacy.service.dicom_service.pydicom') as mock_pydicom, \
             patch('privacy.service.dicom_service.DicomImageRedactorEngine') as MockEngine, \
             patch.object(DICOM, 'dcm_to_png') as mock_dcm_to_png, \
             patch('builtins.print'):
            
            mock_pydicom.dcmread.return_value = mock_dicom_instance
            redacted_instance = MagicMock()
            MockEngine.return_value.redact.return_value = redacted_instance
            
            original_data = b'YWJjZGVmZ2hpams='
            redacted_data = b'MTIzNDU2Nzg5MA=='
            mock_dcm_to_png.side_effect = [original_data, redacted_data]
            
            result = DICOM.read_dicom(mock_dicom_payload)
            
            # Verify both conversions happened
            assert mock_dcm_to_png.call_count == 2
            
            # Verify correct instances were passed
            first_call = mock_dcm_to_png.call_args_list[0][0][0]
            second_call = mock_dcm_to_png.call_args_list[1][0][0]
            assert first_call == mock_dicom_instance
            assert second_call == redacted_instance
            
            # Verify result contains both
            assert result["original"] == original_data
            assert result["anonymize"] == redacted_data


class TestSaveImageClass:
    """Tests for saveImage.save_img method."""
    
    def test_save_img_basic_flow(self):
        """Test basic image saving functionality."""
        from privacy.service.dicom_service import saveImage
        
        # Create test base64 data
        test_data = base64.b64encode(b"fake_image_data")
        
        m = mock_open()
        with patch('privacy.service.dicom_service.open', m):
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
        from privacy.service.dicom_service import saveImage
        
        original_data = b"test image content"
        encoded_data = base64.b64encode(original_data)
        
        m = mock_open()
        with patch('privacy.service.dicom_service.open', m):
            saveImage.save_img(encoded_data)
            
            # Verify decoded data was written
            handle = m()
            written_data = handle.write.call_args[0][0]
            assert written_data == original_data
    
    def test_save_img_saves_to_file_png(self):
        """Test that save_img saves to file.png."""
        from privacy.service.dicom_service import saveImage
        
        test_data = base64.b64encode(b"image_data")
        
        m = mock_open()
        with patch('privacy.service.dicom_service.open', m):
            saveImage.save_img(test_data)
            
            # Verify filename
            m.assert_called_once_with("file.png", "wb")
    
    def test_save_img_with_png_header(self):
        """Test save_img with realistic PNG data."""
        from privacy.service.dicom_service import saveImage
        
        # Create realistic PNG-like data
        png_header = b'\x89PNG\r\n\x1a\n'
        fake_png_data = png_header + b'fake_png_content'
        encoded_data = base64.b64encode(fake_png_data)
        
        m = mock_open()
        with patch('privacy.service.dicom_service.open', m):
            saveImage.save_img(encoded_data)
            
            handle = m()
            written_data = handle.write.call_args[0][0]
            assert written_data == fake_png_data
            assert written_data.startswith(png_header)


class TestDicomIntegration:
    """Integration tests for DICOM workflow."""
    
    def test_full_dicom_workflow(self, mock_dicom_payload):
        """Test complete DICOM reading, redaction, and conversion workflow."""
        from privacy.service.dicom_service import DICOM
        
        with patch('privacy.service.dicom_service.pydicom') as mock_pydicom, \
             patch('privacy.service.dicom_service.DicomImageRedactorEngine') as MockEngine, \
             patch('privacy.service.dicom_service.BytesIO') as MockBytesIO, \
             patch('privacy.service.dicom_service.plt') as mock_plt, \
             patch('builtins.print'):
            
            # Setup DICOM instance
            dicom_instance = MagicMock()
            dicom_instance.pixel_array = MagicMock()
            mock_pydicom.dcmread.return_value = dicom_instance
            
            # Setup redacted instance
            redacted_instance = MagicMock()
            redacted_instance.pixel_array = MagicMock()
            
            mock_engine = MockEngine.return_value
            mock_engine.redact.return_value = redacted_instance
            
            # Setup BytesIO buffers
            buffer1 = io.BytesIO(b'original_png_data')
            buffer2 = io.BytesIO(b'redacted_png_data')
            MockBytesIO.side_effect = [buffer1, buffer2]
            
            # Call the method
            result = DICOM.read_dicom(mock_dicom_payload)
            
            # Verify complete workflow
            assert mock_pydicom.dcmread.called
            assert MockEngine.called
            assert mock_engine.redact.called
            assert mock_plt.imshow.call_count == 2  # Once for original, once for redacted
            assert mock_plt.axis.call_count == 2
            assert mock_plt.savefig.call_count == 2
            
            # Verify result
            assert result is not None
            assert "original" in result
            assert "anonymize" in result
    
    def test_dicom_and_save_image_workflow(self):
        """Test DICOM reading followed by saving image."""
        from privacy.service.dicom_service import DICOM, saveImage
        
        mock_payload = MagicMock()
        
        with patch('privacy.service.dicom_service.pydicom') as mock_pydicom, \
             patch('privacy.service.dicom_service.DicomImageRedactorEngine') as MockEngine, \
             patch.object(DICOM, 'dcm_to_png') as mock_dcm_to_png, \
             patch('builtins.print'):
            
            # Setup mocks for read_dicom
            mock_pydicom.dcmread.return_value = MagicMock()
            MockEngine.return_value.redact.return_value = MagicMock()
            
            original_b64 = base64.b64encode(b'original_image')
            redacted_b64 = base64.b64encode(b'redacted_image')
            mock_dcm_to_png.side_effect = [original_b64, redacted_b64]
            
            # Read DICOM
            result = DICOM.read_dicom(mock_payload)
            
            # Save the redacted image
            m = mock_open()
            with patch('privacy.service.dicom_service.open', m):
                saveImage.save_img(result["anonymize"])
                
                # Verify save was called correctly
                m.assert_called_once_with("file.png", "wb")
                handle = m()
                written_data = handle.write.call_args[0][0]
                assert written_data == b'redacted_image'


class TestDicomEdgeCases:
    """Tests for edge cases in DICOM service."""
    
    def test_dcm_to_png_with_empty_pixel_array(self):
        """Test dcm_to_png handles empty pixel array."""
        from privacy.service.dicom_service import DICOM
        
        mock_instance = MagicMock()
        mock_instance.pixel_array = None
        
        mock_buffer = io.BytesIO(b'data')
        
        with patch('privacy.service.dicom_service.BytesIO', return_value=mock_buffer), \
             patch('privacy.service.dicom_service.plt') as mock_plt:
            
            result = DICOM.dcm_to_png(mock_instance)
            
            # Should still attempt to process
            assert mock_plt.imshow.called
            assert result is not None
    
    def test_read_dicom_with_different_payload_types(self):
        """Test read_dicom works with different payload formats."""
        from privacy.service.dicom_service import DICOM
        
        # Create payload with file attribute
        payload = MagicMock()
        payload.file = "test_file.dcm"
        
        with patch('privacy.service.dicom_service.pydicom') as mock_pydicom, \
             patch('privacy.service.dicom_service.DicomImageRedactorEngine') as MockEngine, \
             patch.object(DICOM, 'dcm_to_png') as mock_dcm_to_png, \
             patch('builtins.print'):
            
            mock_pydicom.dcmread.return_value = MagicMock()
            MockEngine.return_value.redact.return_value = MagicMock()
            mock_dcm_to_png.side_effect = [b'orig', b'redact']
            
            result = DICOM.read_dicom(payload)
            
            # Verify it worked with string file path
            mock_pydicom.dcmread.assert_called_once_with("test_file.dcm")
            assert result is not None
