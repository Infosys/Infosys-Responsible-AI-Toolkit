"""
Test suite for files_service.py to cover lines 14-30.
"""

import pytest
from unittest.mock import MagicMock, patch
from privacy.service.files_service import FileService


class TestFileServiceAnonymizeFile:
    """Test FileService.anonymize_file method with all supported file types."""
    
    def test_anonymize_csv_file(self):
        """Test anonymize_file with CSV extension - line 15."""
        mock_payload = {"data": "test_csv_data"}
        
        with patch('privacy.service.files_service.CSVService') as mock_csv:
            mock_csv.csv_anonymize.return_value = "csv_result"
            
            result = FileService.anonymize_file(mock_payload, 'csv')
            
            assert result == "csv_result"
            mock_csv.csv_anonymize.assert_called_once_with(mock_payload)
    
    def test_anonymize_json_file(self):
        """Test anonymize_file with JSON extension - line 17."""
        mock_payload = {"data": "test_json_data"}
        
        with patch('privacy.service.files_service.JSONService') as mock_json:
            mock_json.anonymize_json.return_value = "json_result"
            
            result = FileService.anonymize_file(mock_payload, 'json')
            
            assert result == "json_result"
            mock_json.anonymize_json.assert_called_once_with(mock_payload)
    
    def test_anonymize_pptx_file(self):
        """Test anonymize_file with PPTX extension - line 24."""
        mock_payload = {"data": "test_pptx_data"}
        
        with patch('privacy.service.files_service.PPTService') as mock_ppt:
            mock_ppt.mask_ppt.return_value = "pptx_result"
            
            result = FileService.anonymize_file(mock_payload, 'pptx')
            
            assert result == "pptx_result"
            mock_ppt.mask_ppt.assert_called_once_with(mock_payload)
    
    def test_anonymize_ppt_file(self):
        """Test anonymize_file with PPT extension - line 24."""
        mock_payload = {"data": "test_ppt_data"}
        
        with patch('privacy.service.files_service.PPTService') as mock_ppt:
            mock_ppt.mask_ppt.return_value = "ppt_result"
            
            result = FileService.anonymize_file(mock_payload, 'ppt')
            
            assert result == "ppt_result"
            mock_ppt.mask_ppt.assert_called_once_with(mock_payload)
    
    def test_anonymize_docx_file(self):
        """Test anonymize_file with DOCX extension - line 27."""
        mock_payload = {"data": "test_docx_data"}
        
        with patch('privacy.service.files_service.DOCService') as mock_doc:
            mock_doc.mask_doc.return_value = "docx_result"
            
            result = FileService.anonymize_file(mock_payload, 'docx')
            
            assert result == "docx_result"
            mock_doc.mask_doc.assert_called_once_with(mock_payload)
    
    def test_anonymize_unsupported_file_extension(self):
        """Test anonymize_file with unsupported extension - line 29."""
        mock_payload = {"data": "test_data"}
        
        with pytest.raises(ValueError) as exc_info:
            FileService.anonymize_file(mock_payload, 'xyz')
        
        assert "Unsupported file extension: xyz" in str(exc_info.value)
    
    def test_anonymize_another_unsupported_extension(self):
        """Test anonymize_file with another unsupported extension."""
        mock_payload = {"data": "test_data"}
        
        with pytest.raises(ValueError) as exc_info:
            FileService.anonymize_file(mock_payload, 'txt')
        
        assert "Unsupported file extension: txt" in str(exc_info.value)
