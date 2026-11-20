"""
Tests for files_service module.

This module tests the FileService class which routes file anonymization
requests to appropriate service handlers based on file extensions.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock


@pytest.fixture
def mock_payload():
    """Create a mock payload for testing."""
    payload = MagicMock()
    payload.file = MagicMock()
    payload.file.file = b'test file content'
    payload.file.filename = 'test_file.txt'
    return payload


class TestFileServiceAnonymize:
    """Test suite for FileService.anonymize_file method."""
    
    def test_anonymize_csv_file(self, mock_payload):
        """Test anonymize_file routes CSV files correctly."""
        from privacy.service.files_service import FileService
        
        with patch('privacy.service.files_service.CSVService.csv_anonymize') as mock_csv:
            mock_csv.return_value = 'anonymized_csv_path.csv'
            
            result = FileService.anonymize_file(mock_payload, 'csv')
            
            # Verify CSV service was called with correct payload
            mock_csv.assert_called_once_with(mock_payload)
            assert result == 'anonymized_csv_path.csv'
    
    def test_anonymize_json_file(self, mock_payload):
        """Test anonymize_file routes JSON files correctly."""
        from privacy.service.files_service import FileService
        
        with patch('privacy.service.files_service.JSONService.anonymize_json') as mock_json:
            mock_json.return_value = 'anonymized_json_path.json'
            
            result = FileService.anonymize_file(mock_payload, 'json')
            
            # Verify JSON service was called with correct payload
            mock_json.assert_called_once_with(mock_payload)
            assert result == 'anonymized_json_path.json'
    
    def test_anonymize_pptx_file(self, mock_payload):
        """Test anonymize_file routes PPTX files correctly."""
        from privacy.service.files_service import FileService
        
        with patch('privacy.service.files_service.PPTService.mask_ppt') as mock_ppt:
            mock_ppt.return_value = 'anonymized_presentation.pptx'
            
            result = FileService.anonymize_file(mock_payload, 'pptx')
            
            # Verify PPT service was called with correct payload
            mock_ppt.assert_called_once_with(mock_payload)
            assert result == 'anonymized_presentation.pptx'
    
    def test_anonymize_ppt_file(self, mock_payload):
        """Test anonymize_file routes PPT files correctly."""
        from privacy.service.files_service import FileService
        
        with patch('privacy.service.files_service.PPTService.mask_ppt') as mock_ppt:
            mock_ppt.return_value = 'anonymized_presentation.ppt'
            
            result = FileService.anonymize_file(mock_payload, 'ppt')
            
            # Verify PPT service was called with correct payload
            mock_ppt.assert_called_once_with(mock_payload)
            assert result == 'anonymized_presentation.ppt'
    
    def test_anonymize_docx_file(self, mock_payload):
        """Test anonymize_file routes DOCX files correctly."""
        from privacy.service.files_service import FileService
        
        with patch('privacy.service.files_service.DOCService.mask_doc') as mock_doc:
            mock_doc.return_value = 'anonymized_document.docx'
            
            result = FileService.anonymize_file(mock_payload, 'docx')
            
            # Verify DOC service was called with correct payload
            mock_doc.assert_called_once_with(mock_payload)
            assert result == 'anonymized_document.docx'
    
    def test_anonymize_unsupported_file_extension(self, mock_payload):
        """Test anonymize_file raises ValueError for unsupported extensions."""
        from privacy.service.files_service import FileService
        
        unsupported_extensions = ['txt', 'exe', 'zip', 'mp4', 'unknown']
        
        for ext in unsupported_extensions:
            with pytest.raises(ValueError) as exc_info:
                FileService.anonymize_file(mock_payload, ext)
            
            assert f"Unsupported file extension: {ext}" in str(exc_info.value)
    
    def test_anonymize_with_different_payloads(self):
        """Test anonymize_file works with different payload structures."""
        from privacy.service.files_service import FileService
        
        # Test with dictionary payload
        dict_payload = {'file': 'data', 'options': 'test'}
        
        with patch('privacy.service.files_service.CSVService.csv_anonymize') as mock_csv:
            mock_csv.return_value = 'output.csv'
            
            result = FileService.anonymize_file(dict_payload, 'csv')
            
            mock_csv.assert_called_once_with(dict_payload)
            assert result == 'output.csv'
    
    def test_anonymize_file_extension_case_sensitivity(self, mock_payload):
        """Test that file extensions are case-sensitive (lowercase expected)."""
        from privacy.service.files_service import FileService
        
        # These should raise ValueError because they're uppercase
        with pytest.raises(ValueError) as exc_info:
            FileService.anonymize_file(mock_payload, 'CSV')
        assert "Unsupported file extension: CSV" in str(exc_info.value)
        
        with pytest.raises(ValueError):
            FileService.anonymize_file(mock_payload, 'JSON')
        
        with pytest.raises(ValueError):
            FileService.anonymize_file(mock_payload, 'DOCX')
    
    def test_anonymize_empty_extension(self, mock_payload):
        """Test anonymize_file with empty extension."""
        from privacy.service.files_service import FileService
        
        with pytest.raises(ValueError) as exc_info:
            FileService.anonymize_file(mock_payload, '')
        
        assert "Unsupported file extension:" in str(exc_info.value)
    
    def test_anonymize_none_extension(self, mock_payload):
        """Test anonymize_file with None extension."""
        from privacy.service.files_service import FileService
        
        with pytest.raises(ValueError) as exc_info:
            FileService.anonymize_file(mock_payload, None)
        
        assert "Unsupported file extension: None" in str(exc_info.value)


class TestFileServiceIntegration:
    """Integration tests for FileService."""
    
    def test_all_supported_extensions(self, mock_payload):
        """Test all supported file extensions are properly routed."""
        from privacy.service.files_service import FileService
        
        # Map of extensions to their service mocks
        extension_service_map = {
            'csv': 'privacy.service.files_service.CSVService.csv_anonymize',
            'json': 'privacy.service.files_service.JSONService.anonymize_json',
            'pptx': 'privacy.service.files_service.PPTService.mask_ppt',
            'ppt': 'privacy.service.files_service.PPTService.mask_ppt',
            'docx': 'privacy.service.files_service.DOCService.mask_doc',
        }
        
        for ext, service_path in extension_service_map.items():
            with patch(service_path) as mock_service:
                mock_service.return_value = f'anonymized.{ext}'
                
                result = FileService.anonymize_file(mock_payload, ext)
                
                # Verify service was called and returned correctly
                mock_service.assert_called_once()
                assert result == f'anonymized.{ext}'
    
    def test_service_exception_propagation(self, mock_payload):
        """Test that exceptions from services are propagated correctly."""
        from privacy.service.files_service import FileService
        
        with patch('privacy.service.files_service.CSVService.csv_anonymize') as mock_csv:
            mock_csv.side_effect = Exception("CSV processing error")
            
            with pytest.raises(Exception) as exc_info:
                FileService.anonymize_file(mock_payload, 'csv')
            
            assert "CSV processing error" in str(exc_info.value)
    
    def test_file_service_is_static(self):
        """Test that FileService methods are static and don't require instantiation."""
        from privacy.service.files_service import FileService
        
        # Should be able to call without creating instance
        with patch('privacy.service.files_service.CSVService.csv_anonymize') as mock_csv:
            mock_csv.return_value = 'test.csv'
            
            # Call directly on class
            result = FileService.anonymize_file({}, 'csv')
            
            assert result == 'test.csv'
            mock_csv.assert_called_once()
    
    def test_payload_passed_unchanged(self, mock_payload):
        """Test that payload is passed to services without modification."""
        from privacy.service.files_service import FileService
        
        with patch('privacy.service.files_service.DOCService.mask_doc') as mock_doc:
            mock_doc.return_value = 'output.docx'
            
            FileService.anonymize_file(mock_payload, 'docx')
            
            # Verify the exact same payload object was passed
            call_args = mock_doc.call_args[0][0]
            assert call_args is mock_payload
