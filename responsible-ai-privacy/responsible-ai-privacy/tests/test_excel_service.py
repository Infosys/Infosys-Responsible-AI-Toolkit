"""
Comprehensive tests for excel_service.py module
Tests Excel class for anonymizing Excel files
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import io
import os
from privacy.service.excel_service import Excel, AttributeDict


class TestAttributeDict:
    """Test AttributeDict functionality"""
    
    def test_attribute_dict_basic(self):
        """Test basic AttributeDict operations"""
        ad = AttributeDict({"key1": "value1", "key2": "value2"})
        
        assert ad.key1 == "value1"
        assert ad.key2 == "value2"
        assert ad["key1"] == "value1"


class TestExcelAnonymize:
    """Test Excel.excelanonymize() method"""
    
    @patch('privacy.service.excel_service.xlsxwriter.Workbook')
    @patch('privacy.service.excel_service.openpyxl.load_workbook')
    @patch('privacy.service.excel_service.TextPrivacy.anonymize')
    @patch('privacy.service.excel_service.shutil.copyfileobj')
    @patch('privacy.service.excel_service.os.makedirs')
    @patch('privacy.service.excel_service.os.path.exists')
    @patch('privacy.service.excel_service.os.remove')
    @patch('builtins.open', new_callable=mock_open)
    def test_excelanonymize_basic_workflow(self, mock_file_open, mock_remove, mock_exists, 
                                           mock_makedirs, mock_copyfile, mock_anonymize, 
                                           mock_load_wb, mock_xlsxwriter):
        """Test basic Excel anonymization workflow"""
        # Mock file object
        mock_excel_file = Mock()
        mock_excel_file.file = io.BytesIO(b"fake excel data")
        
        payload = {"excel": mock_excel_file}
        
        # Mock workbook and sheet
        mock_workbook = Mock()
        mock_sheet = MagicMock()  # Use MagicMock for __setitem__ support
        mock_workbook.active = mock_sheet
        mock_load_wb.return_value = mock_workbook
        
        # Mock cell iteration
        mock_cell = Mock()
        mock_cell.coordinate = "A1"
        mock_cell.value = "Test Data"
        mock_sheet.iter_rows.return_value = [[mock_cell]]
        
        # Mock anonymization response
        mock_anon_response = AttributeDict({"anonymizedText": "<REDACTED>"})
        mock_anonymize.return_value = mock_anon_response
        
        # Mock xlsxwriter workbook
        mock_output_wb = Mock()
        mock_worksheet = Mock()
        mock_output_wb.add_worksheet.return_value = mock_worksheet
        mock_xlsxwriter.return_value = mock_output_wb
        
        # Mock file operations
        mock_exists.return_value = True
        
        result = Excel.excelanonymize(payload)
        
        # Verify directory creation
        mock_makedirs.assert_called_once_with("temp_excel_files", exist_ok=True)
        
        # Verify file copy
        assert mock_copyfile.called
        
        # Verify workbook operations
        assert mock_load_wb.called
        assert mock_anonymize.called
        
        # Verify result is a file path
        assert "temp_excel_files" in result or result.endswith(".xlsx")
    
    @patch('privacy.service.excel_service.xlsxwriter.Workbook')
    @patch('privacy.service.excel_service.openpyxl.load_workbook')
    @patch('privacy.service.excel_service.TextPrivacy.anonymize')
    @patch('privacy.service.excel_service.shutil.copyfileobj')
    @patch('privacy.service.excel_service.os.makedirs')
    @patch('privacy.service.excel_service.os.path.exists')
    @patch('privacy.service.excel_service.os.remove')
    @patch('builtins.open', new_callable=mock_open)
    def test_excelanonymize_multiple_cells(self, mock_file_open, mock_remove, mock_exists,
                                          mock_makedirs, mock_copyfile, mock_anonymize,
                                          mock_load_wb, mock_xlsxwriter):
        """Test Excel anonymization with multiple cells"""
        mock_excel_file = Mock()
        mock_excel_file.file = io.BytesIO(b"fake excel data")
        
        payload = {"excel": mock_excel_file}
        
        # Mock workbook with multiple cells
        mock_workbook = Mock()
        mock_sheet = MagicMock()  # Use MagicMock for __setitem__ support
        mock_workbook.active = mock_sheet
        mock_load_wb.return_value = mock_workbook
        
        # Create multiple cells
        mock_cell1 = Mock()
        mock_cell1.coordinate = "A1"
        mock_cell1.value = "John Doe"
        
        mock_cell2 = Mock()
        mock_cell2.coordinate = "B1"
        mock_cell2.value = "john@example.com"
        
        mock_cell3 = Mock()
        mock_cell3.coordinate = "A2"
        mock_cell3.value = "123-45-6789"
        
        mock_sheet.iter_rows.return_value = [
            [mock_cell1, mock_cell2],
            [mock_cell3]
        ]
        
        # Mock anonymization
        mock_anonymize.side_effect = [
            AttributeDict({"anonymizedText": "<PERSON>"}),
            AttributeDict({"anonymizedText": "<EMAIL>"}),
            AttributeDict({"anonymizedText": "<SSN>"})
        ]
        
        mock_output_wb = Mock()
        mock_worksheet = Mock()
        mock_output_wb.add_worksheet.return_value = mock_worksheet
        mock_xlsxwriter.return_value = mock_output_wb
        
        mock_exists.return_value = True
        
        result = Excel.excelanonymize(payload)
        
        # Verify all cells were processed
        assert mock_anonymize.call_count == 3
        
        # Verify anonymize was called with correct payloads
        calls = mock_anonymize.call_args_list
        assert calls[0][0][0].inputText == "John Doe"
        assert calls[1][0][0].inputText == "john@example.com"
        assert calls[2][0][0].inputText == "123-45-6789"
    
    @patch('privacy.service.excel_service.xlsxwriter.Workbook')
    @patch('privacy.service.excel_service.openpyxl.load_workbook')
    @patch('privacy.service.excel_service.TextPrivacy.anonymize')
    @patch('privacy.service.excel_service.shutil.copyfileobj')
    @patch('privacy.service.excel_service.os.makedirs')
    @patch('privacy.service.excel_service.os.path.exists')
    @patch('privacy.service.excel_service.os.remove')
    @patch('privacy.service.excel_service.log')
    @patch('builtins.open', new_callable=mock_open)
    def test_excelanonymize_exception_handling(self, mock_file_open, mock_log, mock_remove,
                                               mock_exists, mock_makedirs, mock_copyfile,
                                               mock_anonymize, mock_load_wb, mock_xlsxwriter):
        """Test exception handling in excelanonymize"""
        mock_excel_file = Mock()
        mock_excel_file.file = io.BytesIO(b"fake excel data")
        
        payload = {"excel": mock_excel_file}
        
        # Make load_workbook raise exception
        mock_load_wb.side_effect = Exception("Failed to load workbook")
        
        mock_exists.return_value = True
        
        with pytest.raises(Exception) as exc_info:
            Excel.excelanonymize(payload)
        
        assert "Failed to load workbook" in str(exc_info.value)
        assert mock_log.error.called
    
    @patch('privacy.service.excel_service.xlsxwriter.Workbook')
    @patch('privacy.service.excel_service.openpyxl.load_workbook')
    @patch('privacy.service.excel_service.TextPrivacy.anonymize')
    @patch('privacy.service.excel_service.shutil.copyfileobj')
    @patch('privacy.service.excel_service.os.makedirs')
    @patch('privacy.service.excel_service.os.path.exists')
    @patch('privacy.service.excel_service.os.remove')
    @patch('builtins.open', new_callable=mock_open)
    def test_excelanonymize_temp_file_cleanup(self, mock_file_open, mock_remove, mock_exists,
                                              mock_makedirs, mock_copyfile, mock_anonymize,
                                              mock_load_wb, mock_xlsxwriter):
        """Test temporary file cleanup in finally block"""
        mock_excel_file = Mock()
        mock_excel_file.file = io.BytesIO(b"fake excel data")
        
        payload = {"excel": mock_excel_file}
        
        mock_workbook = Mock()
        mock_sheet = MagicMock()  # Use MagicMock for __setitem__ support
        mock_workbook.active = mock_sheet
        mock_load_wb.return_value = mock_workbook
        
        mock_cell = Mock()
        mock_cell.coordinate = "A1"
        mock_cell.value = "Test"
        mock_sheet.iter_rows.return_value = [[mock_cell]]
        
        mock_anonymize.return_value = AttributeDict({"anonymizedText": "Redacted"})
        
        mock_output_wb = Mock()
        mock_worksheet = Mock()
        mock_output_wb.add_worksheet.return_value = mock_worksheet
        mock_xlsxwriter.return_value = mock_output_wb
        
        # File exists for cleanup
        mock_exists.return_value = True
        
        Excel.excelanonymize(payload)
        
        # Verify cleanup was attempted
        assert mock_remove.called
    
    @patch('privacy.service.excel_service.xlsxwriter.Workbook')
    @patch('privacy.service.excel_service.openpyxl.load_workbook')
    @patch('privacy.service.excel_service.TextPrivacy.anonymize')
    @patch('privacy.service.excel_service.shutil.copyfileobj')
    @patch('privacy.service.excel_service.os.makedirs')
    @patch('privacy.service.excel_service.os.path.exists')
    @patch('privacy.service.excel_service.os.remove')
    @patch('privacy.service.excel_service.log')
    @patch('builtins.open', new_callable=mock_open)
    def test_excelanonymize_cleanup_error_handling(self, mock_file_open, mock_log, mock_remove,
                                                   mock_exists, mock_makedirs, mock_copyfile,
                                                   mock_anonymize, mock_load_wb, mock_xlsxwriter):
        """Test error handling during file cleanup"""
        mock_excel_file = Mock()
        mock_excel_file.file = io.BytesIO(b"fake excel data")
        
        payload = {"excel": mock_excel_file}
        
        mock_workbook = Mock()
        mock_sheet = MagicMock()  # Use MagicMock for __setitem__ support
        mock_workbook.active = mock_sheet
        mock_load_wb.return_value = mock_workbook
        
        mock_cell = Mock()
        mock_cell.coordinate = "A1"
        mock_cell.value = "Data"
        mock_sheet.iter_rows.return_value = [[mock_cell]]
        
        mock_anonymize.return_value = AttributeDict({"anonymizedText": "Anon"})
        
        mock_output_wb = Mock()
        mock_worksheet = Mock()
        mock_output_wb.add_worksheet.return_value = mock_worksheet
        mock_xlsxwriter.return_value = mock_output_wb
        
        mock_exists.return_value = True
        mock_remove.side_effect = OSError("Permission denied")
        
        # Should complete successfully despite cleanup error
        result = Excel.excelanonymize(payload)
        
        # Verify error was logged
        assert mock_log.error.called


class TestExcelCreateExcel:
    """Test Excel.createExcel() static method"""
    
    def test_create_excel_single_value(self):
        """Test createExcel with single value"""
        mock_worksheet = Mock()
        
        s = "Value1"
        x = ""
        row = 0
        col = 0
        
        Excel.createExcel(s, x, row, col, mock_worksheet)
        
        # Verify write was called
        mock_worksheet.write.assert_called_once_with(0, 0, "Value1")
    
    def test_create_excel_multiple_values(self):
        """Test createExcel with multiple values separated by ;*"""
        mock_worksheet = Mock()
        
        s = "Value1;*Value2;*Value3"
        x = ""
        row = 5
        col = 2
        
        Excel.createExcel(s, x, row, col, mock_worksheet)
        
        # Verify write was called 3 times with incrementing columns
        calls = mock_worksheet.write.call_args_list
        assert len(calls) == 3
        assert calls[0] == ((5, 2, "Value1"),)
        assert calls[1] == ((5, 3, "Value2"),)
        assert calls[2] == ((5, 4, "Value3"),)
    
    def test_create_excel_empty_string(self):
        """Test createExcel with empty string"""
        mock_worksheet = Mock()
        
        s = ""
        x = ""
        row = 0
        col = 0
        
        Excel.createExcel(s, x, row, col, mock_worksheet)
        
        # Should write empty string
        mock_worksheet.write.assert_called_once_with(0, 0, "")
    
    def test_create_excel_special_characters(self):
        """Test createExcel with special characters"""
        mock_worksheet = Mock()
        
        s = "Value with spaces;*Value@#$;*123.45"
        x = ""
        row = 1
        col = 1
        
        Excel.createExcel(s, x, row, col, mock_worksheet)
        
        calls = mock_worksheet.write.call_args_list
        assert len(calls) == 3
        assert calls[0] == ((1, 1, "Value with spaces"),)
        assert calls[1] == ((1, 2, "Value@#$"),)
        assert calls[2] == ((1, 3, "123.45"),)


class TestExcelIntegration:
    """Integration tests for Excel service"""
    
    @patch('privacy.service.excel_service.xlsxwriter.Workbook')
    @patch('privacy.service.excel_service.openpyxl.load_workbook')
    @patch('privacy.service.excel_service.TextPrivacy.anonymize')
    @patch('privacy.service.excel_service.shutil.copyfileobj')
    @patch('privacy.service.excel_service.os.makedirs')
    @patch('privacy.service.excel_service.os.path.exists')
    @patch('privacy.service.excel_service.os.remove')
    @patch('builtins.open', new_callable=mock_open)
    def test_full_workflow_with_pii_data(self, mock_file_open, mock_remove, mock_exists,
                                         mock_makedirs, mock_copyfile, mock_anonymize,
                                         mock_load_wb, mock_xlsxwriter):
        """Test complete workflow with PII data"""
        mock_excel_file = Mock()
        mock_excel_file.file = io.BytesIO(b"fake excel with PII")
        
        payload = {"excel": mock_excel_file}
        
        # Setup workbook with PII data
        mock_workbook = Mock()
        mock_sheet = MagicMock()  # Use MagicMock for __setitem__ support
        mock_workbook.active = mock_sheet
        mock_load_wb.return_value = mock_workbook
        
        # Create cells with different PII types
        cells = []
        pii_data = [
            ("A1", "John Smith"),
            ("B1", "john.smith@email.com"),
            ("C1", "555-123-4567"),
            ("A2", "Jane Doe"),
            ("B2", "jane.doe@email.com"),
        ]
        
        for coord, value in pii_data:
            cell = Mock()
            cell.coordinate = coord
            cell.value = value
            cells.append(cell)
        
        mock_sheet.iter_rows.return_value = [
            [cells[0], cells[1], cells[2]],
            [cells[3], cells[4]]
        ]
        
        # Mock anonymization responses
        anon_responses = [
            "<PERSON>", "<EMAIL>", "<PHONE>", "<PERSON>", "<EMAIL>"
        ]
        mock_anonymize.side_effect = [
            AttributeDict({"anonymizedText": text}) for text in anon_responses
        ]
        
        mock_output_wb = Mock()
        mock_worksheet = Mock()
        mock_output_wb.add_worksheet.return_value = mock_worksheet
        mock_xlsxwriter.return_value = mock_output_wb
        
        mock_exists.return_value = True
        
        result = Excel.excelanonymize(payload)
        
        # Verify all PII was anonymized
        assert mock_anonymize.call_count == 5
        
        # Verify cell values were updated
        for i, (coord, original) in enumerate(pii_data):
            call_payload = mock_anonymize.call_args_list[i][0][0]
            assert call_payload.inputText == original
            assert call_payload.fakeData == False
            assert call_payload.exclusionList is None
    
    @patch('privacy.service.excel_service.xlsxwriter.Workbook')
    @patch('privacy.service.excel_service.openpyxl.load_workbook')
    @patch('privacy.service.excel_service.TextPrivacy.anonymize')
    @patch('privacy.service.excel_service.shutil.copyfileobj')
    @patch('privacy.service.excel_service.os.makedirs')
    @patch('privacy.service.excel_service.os.path.exists')
    @patch('privacy.service.excel_service.os.remove')
    @patch('builtins.open', new_callable=mock_open)
    def test_excelanonymize_with_none_values(self, mock_file_open, mock_remove, mock_exists,
                                             mock_makedirs, mock_copyfile, mock_anonymize,
                                             mock_load_wb, mock_xlsxwriter):
        """Test Excel anonymization with None cell values"""
        mock_excel_file = Mock()
        mock_excel_file.file = io.BytesIO(b"fake excel data")
        
        payload = {"excel": mock_excel_file}
        
        mock_workbook = Mock()
        mock_sheet = MagicMock()  # Use MagicMock for __setitem__ support
        mock_workbook.active = mock_sheet
        mock_load_wb.return_value = mock_workbook
        
        # Cell with None value
        mock_cell = Mock()
        mock_cell.coordinate = "A1"
        mock_cell.value = None
        mock_sheet.iter_rows.return_value = [[mock_cell]]
        
        # Anonymize should convert None to "None" string
        mock_anonymize.return_value = AttributeDict({"anonymizedText": "None"})
        
        mock_output_wb = Mock()
        mock_worksheet = Mock()
        mock_output_wb.add_worksheet.return_value = mock_worksheet
        mock_xlsxwriter.return_value = mock_output_wb
        
        mock_exists.return_value = True
        
        result = Excel.excelanonymize(payload)
        
        # Verify anonymize was called with "None" as string
        call_payload = mock_anonymize.call_args[0][0]
        assert call_payload.inputText == "None"
