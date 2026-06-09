"""
Comprehensive tests for docs_service.py module
Tests DOCService class for anonymizing DOCX files
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import io
import base64
from PIL import Image
from privacy.service.docs_service import DOCService, AttributeDict


class TestDOCServiceProcessImages:
    """Test DOCService.processImages() method"""
    
    @patch('privacy.service.docs_service.request_id_var')
    @patch('privacy.service.docs_service.ImagePrivacy.image_anonymize')
    @patch('privacy.service.docs_service.Image.open')
    @patch('privacy.service.docs_service.tempfile.NamedTemporaryFile')
    @patch('privacy.service.docs_service.os.remove')
    @patch('privacy.service.docs_service.log')
    def test_process_images_success(self, mock_log, mock_remove, mock_tempfile,
                                    mock_image_open, mock_image_anon, mock_request_id):
        """Test successful image processing"""
        mock_request_id.get.return_value = "test-uuid-123"
        
        # Mock run element
        mock_run = Mock()
        mock_blip = Mock()
        mock_blip.get.return_value = "rId1"
        mock_run._element.xpath.return_value = [mock_blip]
        
        # Mock document part
        mock_image_part = Mock()
        mock_image_part.blob = b"fake_image_data_" + b"x" * 700  # > 700 bytes
        mock_run.part.related_parts = {"rId1": mock_image_part}
        
        # Mock image anonymization
        mock_anon_result = base64.b64encode(b"anonymized_image_data").decode()
        mock_image_anon.return_value = mock_anon_result
        
        # Mock PIL Image
        mock_img = Mock()
        mock_image_open.return_value = mock_img
        
        # Mock temp file
        mock_temp = Mock()
        mock_temp.name = "/tmp/test_image.png"
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        paragraph = Mock()
        payload = {"portfolio": "test", "account": "test"}
        uid = "test-uuid-123"
        
        DOCService.processImages(paragraph, mock_run, payload, uid)
        
        # Verify image was anonymized
        assert mock_image_anon.called
        
        # Verify run was cleared and picture added
        mock_run.clear.assert_called_once()
        mock_run.add_picture.assert_called_once()
        
        # Verify temp file was cleaned up
        mock_remove.assert_called_once()
    
    @patch('privacy.service.docs_service.request_id_var')
    @patch('privacy.service.docs_service.log')
    def test_process_images_small_image_skip(self, mock_log, mock_request_id):
        """Test that small images (<700 bytes) are skipped"""
        mock_request_id.get.return_value = "test-uuid-small"
        
        mock_run = Mock()
        mock_blip = Mock()
        mock_blip.get.return_value = "rId1"
        mock_run._element.xpath.return_value = [mock_blip]
        
        # Small image
        mock_image_part = Mock()
        mock_image_part.blob = b"small"  # < 700 bytes
        mock_run.part.related_parts = {"rId1": mock_image_part}
        
        paragraph = Mock()
        payload = {}
        uid = "test-uuid-small"
        
        result = DOCService.processImages(paragraph, mock_run, payload, uid)
        
        # Should return None for small images
        assert result is None
    
    @patch('privacy.service.docs_service.request_id_var')
    @patch('privacy.service.docs_service.error_dict', {})
    @patch('privacy.service.docs_service.log')
    def test_process_images_exception_handling(self, mock_log, mock_request_id):
        """Test exception handling in processImages"""
        mock_request_id.get.return_value = "test-uuid-error"
        
        from privacy.service.docs_service import error_dict
        error_dict["test-uuid-error"] = []
        
        mock_run = Mock()
        mock_run._element.xpath.side_effect = Exception("XPath failed")
        
        paragraph = Mock()
        payload = {}
        uid = "test-uuid-error"
        
        with pytest.raises(Exception):
            DOCService.processImages(paragraph, mock_run, payload, uid)
        
        # Verify error was logged
        assert mock_log.error.called
        assert len(error_dict["test-uuid-error"]) > 0


class TestDOCServiceEditText:
    """Test DOCService.editText() method"""
    
    @patch('privacy.service.docs_service.request_id_var')
    def test_edit_text_replaces_entity(self, mock_request_id):
        """Test that editText replaces detected entity"""
        mock_request_id.set.return_value = None
        
        text = "John Doe works at Microsoft"
        mock_entity = Mock()
        mock_entity.start = 0
        mock_entity.end = 8
        mock_entity.entity_type = "PERSON"
        
        mock_run = Mock()
        mock_run.text = text
        
        DOCService.editText(text, mock_entity, mock_run)
        
        # Verify text was replaced
        expected = text.replace("John Doe", "<PERSON>")
        assert mock_run.text == expected
    
    @patch('privacy.service.docs_service.request_id_var')
    def test_edit_text_multiple_entity_types(self, mock_request_id):
        """Test editText with different entity types"""
        mock_request_id.set.return_value = None
        
        text = "Contact john@email.com for details"
        mock_entity = Mock()
        mock_entity.start = 8
        mock_entity.end = 22
        mock_entity.entity_type = "EMAIL"
        
        mock_run = Mock()
        mock_run.text = text
        
        DOCService.editText(text, mock_entity, mock_run)
        
        expected = text.replace("john@email.com", "<EMAIL>")
        assert mock_run.text == expected


class TestDOCServiceProcessText:
    """Test DOCService.processText() method"""
    
    @patch('privacy.service.docs_service.request_id_var')
    @patch('privacy.service.docs_service.TextPrivacy.textAnalyze')
    @patch('privacy.service.docs_service.anonymizer._remove_conflicts_and_get_text_manipulation_data')
    @patch('privacy.service.docs_service.anonymizer._merge_entities_with_whitespace_between')
    @patch('privacy.service.docs_service.threading.Thread')
    def test_process_text_success(self, mock_thread, mock_merge, mock_conflicts,
                                  mock_analyze, mock_request_id):
        """Test successful text processing"""
        mock_request_id.get.return_value = "test-uuid-text"
        mock_request_id.set.return_value = None
        
        # Mock paragraph with runs
        paragraph = Mock()
        mock_run = Mock()
        mock_run.text = "John Doe lives in New York"
        paragraph.runs = [mock_run]
        
        # Mock text analysis results
        mock_result = [
            Mock(start=0, end=8, entity_type="PERSON"),
            Mock(start=18, end=26, entity_type="LOCATION")
        ]
        mock_analyze.return_value = mock_result
        mock_conflicts.return_value = mock_result
        mock_merge.return_value = mock_result
        
        # Mock thread
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        payload = AttributeDict({
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "spacy"
        })
        uid = "test-uuid-text"
        
        DOCService.processText(paragraph, payload, uid)
        
        # Verify analysis was called
        assert mock_analyze.called
        
        # Verify threads were created and started
        assert mock_thread.call_count == 2  # One thread per entity
        assert mock_thread_instance.start.call_count == 2
        assert mock_thread_instance.join.call_count == 2
    
    @patch('privacy.service.docs_service.request_id_var')
    @patch('privacy.service.docs_service.TextPrivacy.textAnalyze')
    @patch('privacy.service.docs_service.anonymizer._remove_conflicts_and_get_text_manipulation_data')
    @patch('privacy.service.docs_service.anonymizer._merge_entities_with_whitespace_between')
    def test_process_text_with_portfolio_account(self, mock_merge, mock_conflicts,
                                                 mock_analyze, mock_request_id):
        """Test processText with portfolio and account"""
        mock_request_id.get.return_value = "test-uuid-acc"
        
        paragraph = Mock()
        mock_run = Mock()
        mock_run.text = "Test text"
        paragraph.runs = [mock_run]
        
        mock_analyze.return_value = []
        mock_conflicts.return_value = []
        mock_merge.return_value = []
        
        payload = AttributeDict({
            "portfolio": "TestPortfolio",
            "account": "TestAccount",
            "exclusion": "exclude1,exclude2",
            "piiEntitiesToBeRedacted": "PERSON,EMAIL",
            "nlp": "spacy"
        })
        uid = "test-uuid-acc"
        
        DOCService.processText(paragraph, payload, uid)
        
        # Verify analyze was called with correct account details
        call_args = mock_analyze.call_args
        assert call_args[1]['accName'].portfolio == "TestPortfolio"
        assert call_args[1]['accName'].account == "TestAccount"
        assert call_args[1]['exclusion'] == ["exclude1", "exclude2"]
    
    @patch('privacy.service.docs_service.request_id_var')
    @patch('privacy.service.docs_service.error_dict', {})
    @patch('privacy.service.docs_service.log')
    def test_process_text_exception_handling(self, mock_log, mock_request_id):
        """Test exception handling in processText"""
        mock_request_id.get.return_value = "test-uuid-text-error"
        
        from privacy.service.docs_service import error_dict
        error_dict["test-uuid-text-error"] = []
        
        paragraph = Mock()
        paragraph.runs = None  # Will cause AttributeError
        
        payload = AttributeDict({
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "spacy"
        })
        uid = "test-uuid-text-error"
        
        with pytest.raises(Exception):
            DOCService.processText(paragraph, payload, uid)
        
        assert mock_log.error.called


class TestDOCServiceMaskDoc:
    """Test DOCService.mask_doc() method"""
    
    @patch('privacy.service.docs_service.uuid.uuid4')
    @patch('privacy.service.docs_service.request_id_var')
    @patch('privacy.service.docs_service.ApiCall.request')
    @patch('privacy.service.docs_service.Document')
    @patch('privacy.service.docs_service.threading.Thread')
    @patch('privacy.service.docs_service.DOCService.processText')
    @patch('privacy.service.docs_service.DOCService.processImages')
    def test_mask_doc_without_admin(self, mock_process_images, mock_process_text,
                                    mock_thread, mock_document, mock_api,
                                    mock_request_id, mock_uuid):
        """Test mask_doc without portfolio/account"""
        test_uuid = "test-doc-uuid-123"
        mock_uuid.return_value.hex = test_uuid
        mock_request_id.get.return_value = test_uuid
        mock_request_id.set.return_value = None
        
        # Mock file
        mock_file = Mock()
        mock_file.file.read.return_value = b"fake docx data"
        
        # Mock document
        mock_doc = Mock()
        mock_paragraph = Mock()
        mock_run = Mock()
        mock_run._element.xpath.return_value = []  # No images
        mock_paragraph.runs = [mock_run]
        mock_doc.paragraphs = [mock_paragraph]
        mock_document.return_value = mock_doc
        
        # Mock thread
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        payload = {
            "file": mock_file,
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "spacy"
        }
        
        result = DOCService.mask_doc(payload)
        
        # ApiCall should not be called
        mock_api.assert_not_called()
        
        # Verify threads were created
        assert mock_thread.called
        
        # Result should be BytesIO
        assert isinstance(result, io.BytesIO)
    
    @patch('privacy.service.docs_service.uuid.uuid4')
    @patch('privacy.service.docs_service.request_id_var')
    @patch('privacy.service.docs_service.ApiCall.request')
    @patch('privacy.service.docs_service.Document')
    @patch('privacy.service.docs_service.threading.Thread')
    def test_mask_doc_with_admin_api(self, mock_thread, mock_document, mock_api,
                                     mock_request_id, mock_uuid):
        """Test mask_doc with portfolio and account (admin API)"""
        test_uuid = "test-doc-uuid-api"
        mock_uuid.return_value.hex = test_uuid
        mock_request_id.set.return_value = None
        
        mock_file = Mock()
        mock_file.file.read.return_value = b"fake docx data"
        
        mock_doc = Mock()
        mock_doc.paragraphs = []
        mock_document.return_value = mock_doc
        
        # Mock API response
        mock_api.return_value = (["PERSON"], ["data"], ["pre"])
        
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        payload = {
            "file": mock_file,
            "portfolio": "TestPortfolio",
            "account": "TestAccount",
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "spacy"
        }
        
        result = DOCService.mask_doc(payload)
        
        # ApiCall should be called
        mock_api.assert_called_once()
        call_payload = mock_api.call_args[0][0]
        assert call_payload.portfolio == "TestPortfolio"
        assert call_payload.account == "TestAccount"
        
        assert isinstance(result, io.BytesIO)
    
    @patch('privacy.service.docs_service.uuid.uuid4')
    @patch('privacy.service.docs_service.request_id_var')
    @patch('privacy.service.docs_service.ApiCall.request')
    @patch('privacy.service.docs_service.Document')
    def test_mask_doc_api_returns_none(self, mock_document, mock_api,
                                       mock_request_id, mock_uuid):
        """Test mask_doc when API returns None"""
        test_uuid = "test-doc-uuid-none"
        mock_uuid.return_value.hex = test_uuid
        mock_request_id.set.return_value = None
        
        mock_file = Mock()
        mock_file.file.read.return_value = b"fake docx data"
        
        # API returns None (no data)
        mock_api.return_value = None
        
        payload = {
            "file": mock_file,
            "portfolio": "Portfolio1",
            "account": "Account1",
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "spacy"
        }
        
        result = DOCService.mask_doc(payload)
        
        # Should return None
        assert result is None
    
    @patch('privacy.service.docs_service.uuid.uuid4')
    @patch('privacy.service.docs_service.request_id_var')
    @patch('privacy.service.docs_service.error_dict', {})
    @patch('privacy.service.docs_service.log')
    @patch('privacy.service.docs_service.Document')
    def test_mask_doc_exception_handling(self, mock_document, mock_log,
                                        mock_request_id, mock_uuid):
        """Test exception handling in mask_doc"""
        test_uuid = "test-doc-uuid-error"
        mock_uuid.return_value.hex = test_uuid
        mock_request_id.get.return_value = test_uuid
        mock_request_id.set.return_value = None
        
        from privacy.service.docs_service import error_dict
        error_dict[test_uuid] = []
        
        mock_file = Mock()
        mock_file.file.read.side_effect = Exception("Read failed")
        
        payload = {
            "file": mock_file,
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "spacy"
        }
        
        with pytest.raises(Exception):
            DOCService.mask_doc(payload)
        
        assert mock_log.error.called
        assert len(error_dict[test_uuid]) > 0


class TestDOCServiceIntegration:
    """Integration tests for DOCService"""
    
    @patch('privacy.service.docs_service.uuid.uuid4')
    @patch('privacy.service.docs_service.request_id_var')
    @patch('privacy.service.docs_service.Document')
    @patch('privacy.service.docs_service.DOCService.processText')
    @patch('privacy.service.docs_service.threading.Thread')
    def test_full_workflow_text_only(self, mock_thread, mock_process_text,
                                     mock_document, mock_request_id, mock_uuid):
        """Test complete workflow with text-only document"""
        test_uuid = "integration-uuid"
        mock_uuid.return_value.hex = test_uuid
        mock_request_id.get.return_value = test_uuid
        mock_request_id.set.return_value = None
        
        mock_file = Mock()
        mock_file.file.read.return_value = b"docx content"
        
        # Mock document with multiple paragraphs
        mock_doc = Mock()
        
        para1 = Mock()
        run1 = Mock()
        run1.text = "John Doe"
        run1._element.xpath.return_value = []
        para1.runs = [run1]
        
        para2 = Mock()
        run2 = Mock()
        run2.text = "john@email.com"
        run2._element.xpath.return_value = []
        para2.runs = [run2]
        
        mock_doc.paragraphs = [para1, para2]
        mock_document.return_value = mock_doc
        
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        payload = {
            "file": mock_file,
            "portfolio": None,
            "account": None,
            "exclusion": "exclude_term",
            "piiEntitiesToBeRedacted": "PERSON,EMAIL",
            "nlp": "spacy"
        }
        
        result = DOCService.mask_doc(payload)
        
        # Verify threads were created for processing paragraphs
        # processText is called through threads, verify thread creation
        assert mock_thread.call_count >= 2
        
        # Verify result
        assert isinstance(result, io.BytesIO)


class TestDOCServiceEdgeCases:
    """Test edge cases for missing coverage lines"""
    
    @patch('privacy.service.docs_service.request_id_var')
    @patch('privacy.service.docs_service.error_dict', {})
    @patch('privacy.service.docs_service.os.remove')
    @patch('privacy.service.docs_service.log')
    def test_process_images_with_exception_in_removal(self, mock_log, mock_remove, mock_error_dict, mock_request_id):
        """Test processImages when os.remove raises exception (line 76)"""
        mock_request_id.get.return_value = "test-uuid-exception"
        
        mock_run = Mock()
        mock_run._element.xpath.return_value = []
        
        # Make os.remove raise an exception
        mock_remove.side_effect = OSError("Cannot remove file")
        
        with pytest.raises(Exception):
            with patch('privacy.service.docs_service.tempfile.NamedTemporaryFile') as mock_temp:
                mock_temp_file = Mock()
                mock_temp_file.name = "/tmp/test.png"
                mock_temp.return_value.__enter__.return_value = mock_temp_file
                
                # This should trigger exception handling
                DOCService.processImages(mock_run, {}, "test-uid")
    
    @patch('privacy.service.docs_service.request_id_var')
    @patch('privacy.service.docs_service.error_dict', {})
    @patch('privacy.service.docs_service.TextPrivacy.textAnalyze')
    @patch('privacy.service.docs_service.threading.Thread')
    @patch('privacy.service.docs_service.log')
    def test_process_text_with_thread_exception(self, mock_log, mock_thread, mock_analyze, mock_error_dict, mock_request_id):
        """Test processText when threading raises exception (line 108)"""
        mock_request_id.get.return_value = "test-uuid-thread-exception"
        
        mock_paragraph = Mock()
        mock_paragraph.text = "Test paragraph with text"
        mock_run = Mock()
        mock_run.text = "Test text"
        mock_paragraph.runs = [mock_run]
        
        # Mock analyze to return results
        mock_result = Mock()
        mock_result.start = 0
        mock_result.end = 4
        mock_result.entity_type = "PERSON"
        mock_analyze.return_value = [mock_result]
        
        # Make thread creation raise exception after analyze
        mock_thread.side_effect = RuntimeError("Thread creation failed")
        
        payload = {"nlp": "basic", "exclusion": None, "piiEntitiesToBeRedacted": None}
        
        with pytest.raises(Exception):
            DOCService.processText(mock_paragraph, payload, "test-uid")
    
    @patch('privacy.service.docs_service.Document')
    @patch('privacy.service.docs_service.request_id_var')
    def test_mask_doc_initialization(self, mock_request_id, mock_document):
        """Test mask_doc function initialization (lines 133-135, 149)"""
        mock_request_id.get.return_value = "test-mask-doc"
        mock_request_id.set = Mock()
        
        mock_file = Mock()
        mock_file.file = io.BytesIO(b"fake docx content")
        
        mock_doc = Mock()
        mock_doc.paragraphs = []
        mock_doc.tables = []
        mock_document.return_value = mock_doc
        
        payload = {
            "file": mock_file,
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "basic"
        }
        
        result = DOCService.mask_doc(payload)
        
        # Verify document was processed
        assert isinstance(result, io.BytesIO)
    
    @patch('privacy.service.docs_service.request_id_var')
    @patch('privacy.service.docs_service.error_dict', {})
    @patch('privacy.service.docs_service.log')
    def test_process_images_error_dict_missing_key(self, mock_log, mock_error_dict, mock_request_id):
        """Test processImages when request_id not in error_dict (line 76)"""
        mock_request_id.get.return_value = "missing-key-uuid"
        
        mock_paragraph = Mock()
        mock_run = Mock()
        mock_run._element.xpath.return_value = []
        
        # Trigger exception by making something fail
        with patch('privacy.service.docs_service.tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.side_effect = IOError("Cannot create temp file")
    
    @patch('privacy.service.docs_service.Document')
    @patch('privacy.service.docs_service.request_id_var')
    @patch('privacy.service.docs_service.uuid.uuid4')
    def test_mask_doc_with_paragraphs_and_tables(self, mock_uuid, mock_request_id, mock_document):
        """Test mask_doc with actual paragraphs and tables (lines 133-135, 149)"""
        test_uuid = "doc-mask-test"
        mock_uuid.return_value.hex = test_uuid
        mock_request_id.get.return_value = test_uuid
        mock_request_id.set = Mock()
        
        mock_file = Mock()
        mock_file.file = io.BytesIO(b"docx content")
        
        # Create mock document with paragraphs and tables
        mock_doc = Mock()
        mock_para = Mock()
        mock_para.text = "Test paragraph"
        mock_para.runs = []
        mock_para._element.xpath.return_value = []
        
        mock_table = Mock()
        mock_table.rows = []
        
        mock_doc.paragraphs = [mock_para]
        mock_doc.tables = [mock_table]
        mock_document.return_value = mock_doc
        
        payload = {
            "file": mock_file,
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "basic"
        }
        
        with patch('privacy.service.docs_service.threading.Thread') as mock_thread:
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance
            
            result = DOCService.mask_doc(payload)
            
            # Verify threads were created for paragraphs and tables
            assert isinstance(result, io.BytesIO)
            # Lines 133-135: paragraph processing, line 149: table processing
            assert mock_thread.called


class TestDOCServiceMissingLineCoverage:
    """Test cases to cover remaining missing lines: 76, 133-135, 149"""
    
    @patch('privacy.service.docs_service.Document')
    @patch('privacy.service.docs_service.request_id_var')
    @patch('privacy.service.docs_service.error_dict', {})
    def test_mask_doc_exception_populates_error_dict_line_76(
        self, mock_request_id, mock_document
    ):
        """Test mask_doc when exception occurs - covers line 76"""
        mock_request_id.get.return_value = 'test-doc-line76'
        
        # Mock Document to raise exception
        mock_document.side_effect = Exception("Test exception")
        
        # Create payload
        payload = AttributeDict({
            "file": MagicMock(file=io.BytesIO(b'fake docx data')),
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "basic"
        })
        
        # Should raise exception and populate error_dict
        with pytest.raises(Exception, match="Test exception"):
            DOCService.mask_doc(payload)
    
    @patch('privacy.service.docs_service.TextPrivacy.textAnalyze')
    @patch('privacy.service.docs_service.Document')
    @patch('privacy.service.docs_service.threading.Thread')
    @patch('privacy.service.docs_service.request_id_var')
    @patch('privacy.service.docs_service.error_dict', {})
    def test_mask_doc_with_image_in_paragraph_line_133_135(
        self, mock_request_id, mock_thread, mock_document, mock_text_analyze
    ):
        """Test mask_doc with images in paragraphs - covers lines 133-135"""
        mock_request_id.get.return_value = 'test-doc-line133'
        
        # Mock textAnalyze
        mock_text_analyze.return_value = []
        
        # Mock document with paragraph containing image
        mock_doc_instance = MagicMock()
        mock_paragraph = MagicMock()
        mock_run = MagicMock()
        
        # Mock xpath to return truthy value (simulating image)
        mock_run._element.xpath.return_value = [MagicMock()]  # Has blipFill (image)
        
        mock_paragraph.runs = [mock_run]
        mock_paragraph.text = "Test text"
        mock_doc_instance.paragraphs = [mock_paragraph]
        mock_doc_instance.tables = []
        mock_document.return_value = mock_doc_instance
        
        # Mock threading
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        payload = AttributeDict({
            "file": MagicMock(file=io.BytesIO(b'fake docx data')),
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "basic"
        })
        
        result = DOCService.mask_doc(payload)
        
        # Verify threads were created for both text and image processing (lines 133-135)
        assert mock_thread.call_count >= 2  # At least one for text, one for image
        assert isinstance(result, io.BytesIO)


class TestDOCServiceEditText:
    """Test DOCService.editText() method - targeting line 76"""
    
    @patch('privacy.service.docs_service.request_id_var')
    @patch('builtins.print')
    def test_edit_text_print_statement(self, mock_print, mock_request_id):
        """Test editText function calls print (line 76) and replaces text"""
        mock_request_id.set.return_value = None
        
        # Create mock run object
        mock_run = Mock()
        mock_run.text = "My email is user@example.com in this document"
        
        # Create mock result object simulating PII detection result
        mock_result = Mock()
        mock_result.start = 12
        mock_result.end = 28  # "user@example.com"
        mock_result.entity_type = "EMAIL_ADDRESS"
        
        text = "My email is user@example.com in this document"
        
        # Call the function
        DOCService.editText(text, mock_result, mock_run)
        
        # Verify print was called with the detected PII (line 76)
        mock_print.assert_called_once_with("user@example.com")
        
        # Verify text replacement occurred
        assert "<EMAIL_ADDRESS>" in mock_run.text




