"""Tests for `privacy.service.excel_service` module.

These tests import and execute the REAL src code with mocked dependencies
to provide actual code coverage of the excel_service module.
"""

import sys
import os
import pytest
import io
from unittest.mock import MagicMock, Mock, patch, mock_open, PropertyMock
import openpyxl
from openpyxl import Workbook

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture(scope='module', autouse=True)
def setup_mocks():
    """Setup mocks for heavy dependencies before importing src."""
    modules_to_remove = [
        'privacy.service.excel_service',
        'privacy.service.textPrivacy',
    ]
    for mod in modules_to_remove:
        sys.modules.pop(mod, None)
    
    yield
    
    # Cleanup
    for mod in modules_to_remove:
        sys.modules.pop(mod, None)


@pytest.fixture
def mock_payload():
    """Create a mock payload."""
    mock_file = MagicMock()
    mock_file.file = io.BytesIO(b'mock excel data')
    
    return {
        'file': mock_file
    }


class TestAttributeDict:
    """Tests for AttributeDict class."""
    
    def test_attribute_dict_creation(self):
        """Test AttributeDict can be created and accessed."""
        from privacy.service.excel_service import AttributeDict
        
        data = {'key1': 'value1', 'key2': 'value2'}
        attr_dict = AttributeDict(data)
        
        assert attr_dict.key1 == 'value1'
        assert attr_dict.key2 == 'value2'
    
    def test_attribute_dict_setitem(self):
        """Test AttributeDict __setitem__."""
        from privacy.service.excel_service import AttributeDict
        
        attr_dict = AttributeDict()
        attr_dict['new_key'] = 'new_value'
        
        assert attr_dict['new_key'] == 'new_value'
    
    def test_attribute_dict_setattr(self):
        """Test AttributeDict __setattr__."""
        from privacy.service.excel_service import AttributeDict
        
        attr_dict = AttributeDict()
        attr_dict.new_key = 'new_value'
        
        assert attr_dict.new_key == 'new_value'
    
    def test_attribute_dict_delitem(self):
        """Test AttributeDict __delitem__."""
        from privacy.service.excel_service import AttributeDict
        
        attr_dict = AttributeDict({'key': 'value'})
        del attr_dict['key']
        
        assert 'key' not in attr_dict


class TestExcelAnonymize:
    """Tests for Excel.excelanonymize method."""
    
    def test_excelanonymize_basic_flow(self, mock_payload):
        """Test excelanonymize with valid Excel file."""
        from privacy.service.excel_service import Excel
        
        mock_anonymize_result = MagicMock()
        mock_anonymize_result.anonymizedText = '<REDACTED>'
        
        with patch('privacy.service.excel_service.TextPrivacy.anonymize', return_value=mock_anonymize_result), \
             patch('openpyxl.load_workbook') as mock_load, \
             patch('xlsxwriter.Workbook') as mock_workbook, \
             patch('os.makedirs'), \
             patch('os.path.exists', return_value=True), \
             patch('os.remove'), \
             patch('builtins.open', mock_open()), \
             patch('shutil.copyfileobj'):
            
            # Mock workbook and sheet
            mock_wb = MagicMock()
            mock_sheet = MagicMock()
            mock_wb.active = mock_sheet
            
            # Mock cells
            mock_cell1 = MagicMock()
            mock_cell1.coordinate = 'A1'
            mock_cell1.value = 'Name'
            
            mock_cell2 = MagicMock()
            mock_cell2.coordinate = 'B1'
            mock_cell2.value = 'Email'
            
            mock_row = [mock_cell1, mock_cell2]
            mock_sheet.iter_rows.return_value = [mock_row]
            
            mock_load.return_value = mock_wb
            
            # Mock xlsxwriter workbook
            mock_xlsx_wb = MagicMock()
            mock_workbook.return_value = mock_xlsx_wb
            
            result = Excel.excelanonymize(mock_payload)
            
            # Verify result is a file path
            assert isinstance(result, str)
            assert 'ExcelOutput.xlsx' in result or 'x.xlsx' in result
    
    def test_excelanonymize_processes_cells(self, mock_payload):
        """Test excelanonymize processes each cell."""
        from privacy.service.excel_service import Excel
        
        mock_anonymize_result = MagicMock()
        mock_anonymize_result.anonymizedText = '<PERSON>'
        
        with patch('privacy.service.excel_service.TextPrivacy.anonymize', return_value=mock_anonymize_result) as mock_anon, \
             patch('openpyxl.load_workbook') as mock_load, \
             patch('xlsxwriter.Workbook') as mock_workbook, \
             patch('os.makedirs'), \
             patch('os.path.exists', return_value=True), \
             patch('os.remove'), \
             patch('builtins.open', mock_open()), \
             patch('shutil.copyfileobj'), \
             patch('builtins.print'):
            
            # Mock workbook and sheet
            mock_wb = MagicMock()
            mock_sheet = MagicMock()
            mock_wb.active = mock_sheet
            
            # Mock cells with actual data
            mock_cell = MagicMock()
            mock_cell.coordinate = 'A1'
            mock_cell.value = 'John Doe'
            
            mock_row = [mock_cell]
            mock_sheet.iter_rows.return_value = [mock_row]
            
            mock_load.return_value = mock_wb
            
            # Mock xlsxwriter workbook
            mock_xlsx_wb = MagicMock()
            mock_workbook.return_value = mock_xlsx_wb
            
            result = Excel.excelanonymize(mock_payload)
            
            # Verify TextPrivacy.anonymize was called
            assert mock_anon.called
            call_args = mock_anon.call_args[0][0]
            assert call_args.input_text == 'John Doe'
            assert call_args.exclusion_list is None
            assert call_args.portfolio is None
            assert call_args.account is None
            assert call_args.fakeData is False
    
    def test_excelanonymize_multiple_rows(self, mock_payload):
        """Test excelanonymize with multiple rows."""
        from privacy.service.excel_service import Excel
        
        mock_anonymize_result = MagicMock()
        mock_anonymize_result.anonymizedText = '<REDACTED>'
        
        with patch('privacy.service.excel_service.TextPrivacy.anonymize', return_value=mock_anonymize_result), \
             patch('openpyxl.load_workbook') as mock_load, \
             patch('xlsxwriter.Workbook') as mock_workbook, \
             patch('os.makedirs'), \
             patch('os.path.exists', return_value=True), \
             patch('os.remove'), \
             patch('builtins.open', mock_open()), \
             patch('shutil.copyfileobj'), \
             patch('builtins.print'):
            
            # Mock workbook and sheet
            mock_wb = MagicMock()
            mock_sheet = MagicMock()
            mock_wb.active = mock_sheet
            
            # Create multiple rows with multiple cells
            mock_cells_row1 = []
            for i, val in enumerate(['Name', 'Email', 'Phone']):
                cell = MagicMock()
                cell.coordinate = f'{chr(65+i)}1'
                cell.value = val
                mock_cells_row1.append(cell)
            
            mock_cells_row2 = []
            for i, val in enumerate(['John', 'john@example.com', '555-1234']):
                cell = MagicMock()
                cell.coordinate = f'{chr(65+i)}2'
                cell.value = val
                mock_cells_row2.append(cell)
            
            mock_sheet.iter_rows.return_value = [mock_cells_row1, mock_cells_row2]
            
            mock_load.return_value = mock_wb
            
            # Mock xlsxwriter workbook
            mock_xlsx_wb = MagicMock()
            mock_workbook.return_value = mock_xlsx_wb
            
            result = Excel.excelanonymize(mock_payload)
            
            # Verify workbook was saved
            assert mock_wb.save.called
            assert isinstance(result, str)
    
    def test_excelanonymize_with_none_values(self, mock_payload):
        """Test excelanonymize handles None cell values."""
        from privacy.service.excel_service import Excel
        
        mock_anonymize_result = MagicMock()
        mock_anonymize_result.anonymizedText = '<NONE>'
        
        with patch('privacy.service.excel_service.TextPrivacy.anonymize', return_value=mock_anonymize_result), \
             patch('openpyxl.load_workbook') as mock_load, \
             patch('xlsxwriter.Workbook') as mock_workbook, \
             patch('os.makedirs'), \
             patch('os.path.exists', return_value=True), \
             patch('os.remove'), \
             patch('builtins.open', mock_open()), \
             patch('shutil.copyfileobj'), \
             patch('builtins.print'):
            
            # Mock workbook and sheet
            mock_wb = MagicMock()
            mock_sheet = MagicMock()
            mock_wb.active = mock_sheet
            
            # Mock cell with None value
            mock_cell = MagicMock()
            mock_cell.coordinate = 'A1'
            mock_cell.value = None
            
            mock_row = [mock_cell]
            mock_sheet.iter_rows.return_value = [mock_row]
            
            mock_load.return_value = mock_wb
            
            # Mock xlsxwriter workbook
            mock_xlsx_wb = MagicMock()
            mock_workbook.return_value = mock_xlsx_wb
            
            result = Excel.excelanonymize(mock_payload)
            
            # Verify it handled None value
            assert isinstance(result, str)
    
    def test_excelanonymize_temp_directory_created(self, mock_payload):
        """Test excelanonymize creates temp directory."""
        from privacy.service.excel_service import Excel
        
        mock_anonymize_result = MagicMock()
        mock_anonymize_result.anonymizedText = '<REDACTED>'
        
        with patch('privacy.service.excel_service.TextPrivacy.anonymize', return_value=mock_anonymize_result), \
             patch('openpyxl.load_workbook') as mock_load, \
             patch('xlsxwriter.Workbook') as mock_workbook, \
             patch('os.makedirs') as mock_makedirs, \
             patch('os.path.exists', return_value=True), \
             patch('os.remove'), \
             patch('builtins.open', mock_open()), \
             patch('shutil.copyfileobj'), \
             patch('builtins.print'):
            
            # Mock workbook and sheet
            mock_wb = MagicMock()
            mock_sheet = MagicMock()
            mock_wb.active = mock_sheet
            
            mock_cell = MagicMock()
            mock_cell.coordinate = 'A1'
            mock_cell.value = 'Test'
            
            mock_sheet.iter_rows.return_value = [[mock_cell]]
            
            mock_load.return_value = mock_wb
            
            # Mock xlsxwriter workbook
            mock_xlsx_wb = MagicMock()
            mock_workbook.return_value = mock_xlsx_wb
            
            result = Excel.excelanonymize(mock_payload)
            
            # Verify temp directory was created
            mock_makedirs.assert_called_with('temp_excel_files', exist_ok=True)
    
    def test_excelanonymize_cleanup_temp_file(self, mock_payload):
        """Test excelanonymize cleans up temporary file."""
        from privacy.service.excel_service import Excel
        
        mock_anonymize_result = MagicMock()
        mock_anonymize_result.anonymizedText = '<REDACTED>'
        
        with patch('privacy.service.excel_service.TextPrivacy.anonymize', return_value=mock_anonymize_result), \
             patch('openpyxl.load_workbook') as mock_load, \
             patch('xlsxwriter.Workbook') as mock_workbook, \
             patch('os.makedirs'), \
             patch('os.path.exists', return_value=True), \
             patch('os.remove') as mock_remove, \
             patch('builtins.open', mock_open()), \
             patch('shutil.copyfileobj'), \
             patch('builtins.print'):
            
            # Mock workbook and sheet
            mock_wb = MagicMock()
            mock_sheet = MagicMock()
            mock_wb.active = mock_sheet
            
            mock_cell = MagicMock()
            mock_cell.coordinate = 'A1'
            mock_cell.value = 'Test'
            
            mock_sheet.iter_rows.return_value = [[mock_cell]]
            
            mock_load.return_value = mock_wb
            
            # Mock xlsxwriter workbook
            mock_xlsx_wb = MagicMock()
            mock_workbook.return_value = mock_xlsx_wb
            
            result = Excel.excelanonymize(mock_payload)
            
            # Verify temp file was removed
            assert mock_remove.called
    
    def test_excelanonymize_error_handling(self, mock_payload):
        """Test excelanonymize handles errors correctly."""
        from privacy.service.excel_service import Excel
        
        with patch('openpyxl.load_workbook', side_effect=Exception("Load error")), \
             patch('os.makedirs'), \
             patch('os.path.exists', return_value=True), \
             patch('os.remove'), \
             patch('builtins.open', mock_open()), \
             patch('shutil.copyfileobj'):
            
            with pytest.raises(Exception) as exc_info:
                Excel.excelanonymize(mock_payload)
            
            assert "Load error" in str(exc_info.value)
    
    def test_excelanonymize_cleanup_on_error(self, mock_payload):
        """Test excelanonymize cleans up temp file even on error."""
        from privacy.service.excel_service import Excel
        
        with patch('openpyxl.load_workbook', side_effect=Exception("Error")), \
             patch('os.makedirs'), \
             patch('os.path.exists', return_value=True), \
             patch('os.remove') as mock_remove, \
             patch('builtins.open', mock_open()), \
             patch('shutil.copyfileobj'):
            
            try:
                Excel.excelanonymize(mock_payload)
            except Exception:
                pass
            
            # Verify cleanup was attempted
            assert mock_remove.called
    
    def test_excelanonymize_workbook_close(self, mock_payload):
        """Test excelanonymize closes xlsxwriter workbook."""
        from privacy.service.excel_service import Excel
        
        mock_anonymize_result = MagicMock()
        mock_anonymize_result.anonymizedText = '<REDACTED>'
        
        with patch('privacy.service.excel_service.TextPrivacy.anonymize', return_value=mock_anonymize_result), \
             patch('openpyxl.load_workbook') as mock_load, \
             patch('xlsxwriter.Workbook') as mock_workbook, \
             patch('os.makedirs'), \
             patch('os.path.exists', return_value=True), \
             patch('os.remove'), \
             patch('builtins.open', mock_open()), \
             patch('shutil.copyfileobj'), \
             patch('builtins.print'):
            
            # Mock workbook and sheet
            mock_wb = MagicMock()
            mock_sheet = MagicMock()
            mock_wb.active = mock_sheet
            
            mock_cell = MagicMock()
            mock_cell.coordinate = 'A1'
            mock_cell.value = 'Test'
            
            mock_sheet.iter_rows.return_value = [[mock_cell]]
            
            mock_load.return_value = mock_wb
            
            # Mock xlsxwriter workbook
            mock_xlsx_wb = MagicMock()
            mock_workbook.return_value = mock_xlsx_wb
            
            result = Excel.excelanonymize(mock_payload)
            
            # Verify workbook was closed
            assert mock_xlsx_wb.close.called
    
    def test_excelanonymize_cleanup_error_handling(self, mock_payload):
        """Test excelanonymize handles cleanup errors gracefully."""
        from privacy.service.excel_service import Excel
        
        mock_anonymize_result = MagicMock()
        mock_anonymize_result.anonymizedText = '<REDACTED>'
        
        with patch('privacy.service.excel_service.TextPrivacy.anonymize', return_value=mock_anonymize_result), \
             patch('openpyxl.load_workbook') as mock_load, \
             patch('xlsxwriter.Workbook') as mock_workbook, \
             patch('os.makedirs'), \
             patch('os.path.exists', return_value=True), \
             patch('os.remove', side_effect=Exception("Removal error")), \
             patch('builtins.open', mock_open()), \
             patch('shutil.copyfileobj'), \
             patch('builtins.print'):
            
            # Mock workbook and sheet
            mock_wb = MagicMock()
            mock_sheet = MagicMock()
            mock_wb.active = mock_sheet
            
            mock_cell = MagicMock()
            mock_cell.coordinate = 'A1'
            mock_cell.value = 'Test'
            
            mock_sheet.iter_rows.return_value = [[mock_cell]]
            
            mock_load.return_value = mock_wb
            
            # Mock xlsxwriter workbook
            mock_xlsx_wb = MagicMock()
            mock_workbook.return_value = mock_xlsx_wb
            
            # Should not raise, even if cleanup fails
            result = Excel.excelanonymize(mock_payload)
            assert isinstance(result, str)


class TestExcelIntegration:
    """Integration tests for Excel service."""
    
    def test_full_anonymization_workflow(self, mock_payload):
        """Test complete Excel anonymization workflow."""
        from privacy.service.excel_service import Excel
        
        mock_anonymize_result = MagicMock()
        mock_anonymize_result.anonymizedText = '<REDACTED>'
        
        with patch('privacy.service.excel_service.TextPrivacy.anonymize', return_value=mock_anonymize_result) as mock_anon, \
             patch('openpyxl.load_workbook') as mock_load, \
             patch('xlsxwriter.Workbook') as mock_workbook, \
             patch('os.makedirs'), \
             patch('os.path.exists', return_value=True), \
             patch('os.remove'), \
             patch('builtins.open', mock_open()), \
             patch('shutil.copyfileobj'), \
             patch('builtins.print'):
            
            # Mock workbook and sheet with realistic data
            mock_wb = MagicMock()
            mock_sheet = MagicMock()
            mock_wb.active = mock_sheet
            
            # Create cells with PII data
            cells = []
            test_data = [
                ('A1', 'John Doe'),
                ('B1', 'john.doe@example.com'),
                ('C1', '555-1234')
            ]
            
            for coord, value in test_data:
                cell = MagicMock()
                cell.coordinate = coord
                cell.value = value
                cells.append(cell)
            
            mock_sheet.iter_rows.return_value = [cells]
            
            mock_load.return_value = mock_wb
            
            # Mock xlsxwriter workbook
            mock_xlsx_wb = MagicMock()
            mock_workbook.return_value = mock_xlsx_wb
            
            result = Excel.excelanonymize(mock_payload)
            
            # Verify the full workflow
            assert isinstance(result, str)
            assert mock_anon.call_count == len(test_data)
            assert mock_wb.save.called
            assert mock_xlsx_wb.close.called
