'''
License textMIT Licensehttps://mit-license.org/Copyright © 2025 Infosys Ltd.
'''
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import base64
from io import BytesIO
import pydicom


class TestDICOMService:
    """Test cases for DICOM service module"""

    @patch('privacy.service.dicom_service.plt')
    def test_dcmToPng_converts_dicom_to_png(self, mock_plt):
        """Test dcmToPng converts DICOM pixel array to base64 PNG"""
        from privacy.service.dicom_service import DICOM
        
        # Create mock DICOM object
        mock_dcm = Mock()
        mock_dcm.pixel_array = [[0, 128, 255]]
        
        # Mock BytesIO and savefig
        fake_bytes = b'fake_png_data_12345'
        mock_bytesio = BytesIO()
        mock_bytesio.write(fake_bytes)
        mock_bytesio.seek(0)
        
        with patch('privacy.service.dicom_service.BytesIO', return_value=mock_bytesio):
            # Mock savefig to write data
            def mock_savefig(buf, format, bbox_inches, pad_inches):
                buf.write(fake_bytes)
                buf.seek(0)
            
            mock_plt.savefig = mock_savefig
            
            result = DICOM.dcmToPng(mock_dcm)
        
        # Verify result is base64 encoded
        assert result == base64.b64encode(fake_bytes)
        mock_plt.imshow.assert_called_once()
        mock_plt.axis.assert_called_once_with('off')

    @patch('privacy.service.dicom_service.DICOM.dcmToPng')
    @patch('privacy.service.dicom_service.DicomImageRedactorEngine')
    @patch('privacy.service.dicom_service.pydicom')
    def test_readDicom_processes_and_returns_both_images(self, mock_pydicom, mock_engine_class, mock_dcmToPng):
        """Test readDicom processes DICOM file and returns original and anonymized images"""
        from privacy.service.dicom_service import DICOM
        
        # Mock payload
        mock_payload = Mock()
        mock_payload.file = "test_dicom_file.dcm"
        
        # Mock DICOM instance
        mock_dicom_instance = Mock()
        mock_pydicom.dcmread.return_value = mock_dicom_instance
        
        # Mock redaction engine
        mock_engine = Mock()
        mock_redacted = Mock()
        mock_engine.redact.return_value = mock_redacted
        mock_engine_class.return_value = mock_engine
        
        # Mock dcmToPng to return different values
        mock_dcmToPng.side_effect = [b'original_png', b'redacted_png']
        
        result = DICOM.readDicom(mock_payload)
        
        # Verify DICOM was read
        mock_pydicom.dcmread.assert_called_once_with("test_dicom_file.dcm")
        
        # Verify redaction was performed
        mock_engine.redact.assert_called_once_with(mock_dicom_instance, fill="contrast")
        
        # Verify dcmToPng was called for both original and redacted
        assert mock_dcmToPng.call_count == 2
        mock_dcmToPng.assert_any_call(mock_dicom_instance)
        mock_dcmToPng.assert_any_call(mock_redacted)
        
        # Verify result structure
        assert result == {"original": b'original_png', "anonymize": b'redacted_png'}

    @patch('builtins.open', new_callable=mock_open)
    @patch('privacy.service.dicom_service.base64')
    def test_saveImg_writes_decoded_image(self, mock_b64, mock_file):
        """Test saveImg decodes and writes image data to file"""
        from privacy.service.dicom_service import saveImage
        
        # Mock base64 encoded data
        mock_img_data = b'base64_encoded_data'
        mock_decoded = b'decoded_image_data'
        mock_b64.decodebytes.return_value = mock_decoded
        
        saveImage.saveImg(mock_img_data)
        
        # Verify file was opened for writing
        mock_file.assert_called_once_with("file.png", "wb")
        
        # Verify data was decoded
        mock_b64.decodebytes.assert_called_once_with(mock_img_data)
        
        # Verify decoded data was written
        mock_file().write.assert_called_once_with(mock_decoded)


class TestDICOMIntegration:
    """Integration tests for DICOM service workflow"""

    @patch('privacy.service.dicom_service.plt')
    @patch('privacy.service.dicom_service.DicomImageRedactorEngine')
    @patch('privacy.service.dicom_service.pydicom')
    def test_full_dicom_workflow(self, mock_pydicom, mock_engine_class, mock_plt):
        """Test complete DICOM processing workflow from file to base64 output"""
        from privacy.service.dicom_service import DICOM
        
        # Setup mocks
        mock_payload = Mock()
        mock_payload.file = "patient_scan.dcm"
        
        mock_dicom = Mock()
        mock_dicom.pixel_array = [[100, 150, 200]]
        mock_pydicom.dcmread.return_value = mock_dicom
        
        mock_redacted = Mock()
        mock_redacted.pixel_array = [[0, 0, 0]]
        mock_engine = Mock()
        mock_engine.redact.return_value = mock_redacted
        mock_engine_class.return_value = mock_engine
        
        # Mock BytesIO for dcmToPng
        original_bytes = b'original_png_12345'
        redacted_bytes = b'redacted_png_67890'
        
        def create_bytesio(data):
            bio = BytesIO()
            bio.write(data)
            bio.seek(0)
            return bio
        
        bytesio_calls = [create_bytesio(original_bytes), create_bytesio(redacted_bytes)]
        
        with patch('privacy.service.dicom_service.BytesIO', side_effect=bytesio_calls):
            result = DICOM.readDicom(mock_payload)
        
        # Verify workflow
        assert "original" in result
        assert "anonymize" in result
        assert isinstance(result["original"], bytes)
        assert isinstance(result["anonymize"], bytes)
