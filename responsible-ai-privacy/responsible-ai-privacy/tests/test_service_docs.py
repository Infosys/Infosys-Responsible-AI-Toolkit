"""Tests for `privacy.service.docs_service` module.

These tests import and execute the REAL src code with mocked dependencies
to provide actual code coverage of the docs_service module.
"""

import sys
import os
import pytest
import io
import base64
from unittest.mock import MagicMock, Mock, patch, mock_open
from docx import Document
from docx.shared import Inches
from PIL import Image

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture(scope='module', autouse=True)
def setup_mocks():
    """Setup mocks for heavy dependencies before importing src."""
    modules_to_remove = [
        'privacy.service.docs_service',
        'privacy.service.imagePrivacy',
        'privacy.service.api_req',
        'privacy.service.textPrivacy',
    ]
    for mod in modules_to_remove:
        sys.modules.pop(mod, None)
    
    yield
    
    # Cleanup
    for mod in modules_to_remove:
        sys.modules.pop(mod, None)


@pytest.fixture
def sample_doc():
    """Create a sample Word document."""
    doc = Document()
    doc.add_paragraph("This is a test document with some text.")
    doc.add_paragraph("John Doe lives at 123 Main Street.")
    doc.add_paragraph("His email is john.doe@example.com")
    
    doc_bytes = io.BytesIO()
    doc.save(doc_bytes)
    doc_bytes.seek(0)
    return doc_bytes


@pytest.fixture
def sample_image_bytes():
    """Create a sample image as bytes."""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


@pytest.fixture
def mock_payload():
    """Create a mock payload."""
    return {
        'file': MagicMock(file=MagicMock()),
        'portfolio': None,
        'account': None,
        'exclusion': None,
        'pii_entities_to_be_redacted': None,
        'nlp': False,
        'score_threshold': 0.5
    }


class TestDOCServiceProcessImages:
    """Tests for DOCService.process_images method."""
    
    def test_process_images_small_image(self):
        """Test process_images skips small images."""
        from privacy.service.docs_service import DOCService
        
        mock_run = MagicMock()
        mock_blip = MagicMock()
        mock_blip.get.return_value = 'rId1'
        mock_run._element.xpath.return_value = [mock_blip]
        
        # Small image (less than 700 bytes)
        small_img_bytes = b'small' * 50  # 250 bytes
        mock_image_part = MagicMock()
        mock_image_part.blob = small_img_bytes
        mock_run.part.related_parts = {'rId1': mock_image_part}
        
        payload = {}
        
        with patch('privacy.service.docs_service.error_dict', {}, create=True), \
             patch('privacy.service.docs_service.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "test_id"
            
            result = DOCService.process_images(mock_run, payload, "test_uid")
            
            # Should return None for small images
            assert result is None


class TestDOCServiceEditText:
    """Tests for DOCService.editText method."""
    
    def test_edittext_replaces_entity(self):
        """Test editText replaces text with entity placeholder."""
        from privacy.service.docs_service import DOCService
        
        mock_result = MagicMock()
        mock_result.start = 0
        mock_result.end = 8
        mock_result.entity_type = "PERSON"
        
        mock_run = MagicMock()
        mock_run.text = "John Doe works here"
        
        text = "John Doe works here"
        
        with patch('privacy.service.docs_service.request_id_var'), \
             patch('builtins.print'):
            
            DOCService.editText(text, mock_result, mock_run)
            
            # Verify text was replaced
            assert "<PERSON>" in mock_run.text


class TestDOCServiceProcessText:
    """Tests for DOCService.process_text method."""
    
    def test_process_text_basic_flow(self):
        """Test process_text with basic paragraph."""
        from privacy.service.docs_service import DOCService
        from privacy.service.__init__ import AttributeDict
        
        mock_paragraph = MagicMock()
        mock_run = MagicMock()
        mock_run.text = "John Doe lives at 123 Main St"
        mock_paragraph.runs = [mock_run]
        
        payload = AttributeDict({
            'portfolio': None,
            'account': None,
            'exclusion': None,
            'pii_entities_to_be_redacted': None,
            'nlp': False,
            'score_threshold': 0.5
        })
        
        with patch('privacy.service.docs_service.TextPrivacy.text_analyze') as mock_analyze, \
             patch('privacy.service.docs_service.anonymizer') as mock_anonymizer, \
             patch('privacy.service.docs_service.error_dict', {}, create=True), \
             patch('privacy.service.docs_service.request_id_var') as mock_request_id, \
             patch('threading.Thread') as mock_thread:
            
            mock_request_id.get.return_value = "test_id"
            mock_analyze.return_value = []
            mock_anonymizer._remove_conflicts_and_get_text_manipulation_data.return_value = []
            mock_anonymizer._merge_entities_with_whitespace_between.return_value = []
            
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            DOCService.process_text(mock_paragraph, payload, "test_uid")
            
            # Verify text analysis was called
            assert mock_analyze.called
    
    def test_process_text_with_portfolio(self):
        """Test process_text with portfolio and account."""
        from privacy.service.docs_service import DOCService
        from privacy.service.__init__ import AttributeDict
        
        mock_paragraph = MagicMock()
        mock_run = MagicMock()
        mock_run.text = "Test text"
        mock_paragraph.runs = [mock_run]
        
        payload = AttributeDict({
            'portfolio': 'test_portfolio',
            'account': 'test_account',
            'exclusion': 'EMAIL,PHONE',
            'pii_entities_to_be_redacted': 'PERSON,LOCATION',
            'nlp': True,
            'score_threshold': 0.7
        })
        
        with patch('privacy.service.docs_service.TextPrivacy.text_analyze') as mock_analyze, \
             patch('privacy.service.docs_service.anonymizer') as mock_anonymizer, \
             patch('privacy.service.docs_service.error_dict', {}, create=True), \
             patch('privacy.service.docs_service.request_id_var') as mock_request_id, \
             patch('threading.Thread') as mock_thread:
            
            mock_request_id.get.return_value = "test_id"
            mock_analyze.return_value = []
            mock_anonymizer._remove_conflicts_and_get_text_manipulation_data.return_value = []
            mock_anonymizer._merge_entities_with_whitespace_between.return_value = []
            
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            DOCService.process_text(mock_paragraph, payload, "test_uid")
            
            # Verify analyze was called with correct parameters
            call_args = mock_analyze.call_args
            assert call_args[1]['exclusion'] == ['EMAIL', 'PHONE']
            assert call_args[1]['pii_entities_to_be_redacted'] == ['PERSON', 'LOCATION']
            assert call_args[1]['nlp'] == True
            assert call_args[1]['score_threshold'] == 0.7
    
    def test_process_text_with_entities(self):
        """Test process_text with detected entities."""
        from privacy.service.docs_service import DOCService
        from privacy.service.__init__ import AttributeDict
        
        mock_paragraph = MagicMock()
        mock_run = MagicMock()
        mock_run.text = "John Doe"
        mock_paragraph.runs = [mock_run]
        
        payload = AttributeDict({
            'portfolio': None,
            'account': None,
            'exclusion': None,
            'pii_entities_to_be_redacted': None,
            'nlp': False,
            'score_threshold': 0.5
        })
        
        mock_entity = MagicMock()
        mock_entity.start = 0
        mock_entity.end = 8
        mock_entity.entity_type = "PERSON"
        
        with patch('privacy.service.docs_service.TextPrivacy.text_analyze') as mock_analyze, \
             patch('privacy.service.docs_service.anonymizer') as mock_anonymizer, \
             patch('privacy.service.docs_service.error_dict', {}, create=True), \
             patch('privacy.service.docs_service.request_id_var') as mock_request_id, \
             patch('threading.Thread') as mock_thread:
            
            mock_request_id.get.return_value = "test_id"
            mock_analyze.return_value = [mock_entity]
            mock_anonymizer._remove_conflicts_and_get_text_manipulation_data.return_value = [mock_entity]
            mock_anonymizer._merge_entities_with_whitespace_between.return_value = [mock_entity]
            
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            DOCService.process_text(mock_paragraph, payload, "test_uid")
            
            # Verify threads were created and joined
            assert mock_thread.called
            assert mock_thread_instance.start.called
            assert mock_thread_instance.join.called
    
    def test_process_text_error_handling(self):
        """Test process_text handles errors correctly."""
        from privacy.service.docs_service import DOCService
        from privacy.service.__init__ import AttributeDict
        
        mock_paragraph = MagicMock()
        mock_run = MagicMock()
        mock_run.text = "Test"
        mock_paragraph.runs = [mock_run]
        
        payload = AttributeDict({
            'portfolio': None,
            'account': None,
            'exclusion': None,
            'pii_entities_to_be_redacted': None,
            'nlp': False,
            'score_threshold': 0.5
        })
        
        with patch('privacy.service.docs_service.TextPrivacy.text_analyze') as mock_analyze, \
             patch('privacy.service.docs_service.error_dict', {}, create=True), \
             patch('privacy.service.docs_service.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = "error_id"
            mock_analyze.side_effect = Exception("Analysis failed")
            
            with pytest.raises(RuntimeError):
                DOCService.process_text(mock_paragraph, payload, "error_uid")


class TestDOCServiceMaskDoc:
    """Tests for DOCService.mask_doc method."""
    
    def test_mask_doc_basic_flow(self, sample_doc):
        """Test mask_doc with valid document."""
        from privacy.service.docs_service import DOCService
        
        mock_file = MagicMock()
        mock_file.file.read.return_value = sample_doc.getvalue()
        
        payload = {
            'file': mock_file,
            'portfolio': None,
            'account': None,
            'exclusion': None,
            'pii_entities_to_be_redacted': None,
            'nlp': False,
            'score_threshold': 0.5
        }
        
        with patch('privacy.service.docs_service.DOCService.process_text'), \
             patch('privacy.service.docs_service.error_dict', {}, create=True), \
             patch('privacy.service.docs_service.request_id_var') as mock_request_id, \
             patch('threading.Thread') as mock_thread:
            
            mock_request_id.set = MagicMock()
            mock_request_id.get.return_value = "test_id"
            
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            result = DOCService.mask_doc(payload)
            
            # Verify result is BytesIO
            assert isinstance(result, io.BytesIO)
            
            # Verify document can be read
            result.seek(0)
            doc = Document(result)
            assert len(doc.paragraphs) > 0
    
    def test_mask_doc_with_portfolio(self, sample_doc):
        """Test mask_doc with portfolio and account."""
        from privacy.service.docs_service import DOCService
        
        mock_file = MagicMock()
        mock_file.file.read.return_value = sample_doc.getvalue()
        
        payload = {
            'file': mock_file,
            'portfolio': 'test_portfolio',
            'account': 'test_account',
            'exclusion': 'EMAIL',
            'pii_entities_to_be_redacted': 'PERSON',
            'nlp': True,
            'score_threshold': 0.8
        }
        
        with patch('privacy.service.docs_service.ApiCall.request') as mock_api, \
             patch('privacy.service.docs_service.DOCService.process_text'), \
             patch('privacy.service.docs_service.error_dict', {}, create=True), \
             patch('privacy.service.docs_service.request_id_var') as mock_request_id, \
             patch('threading.Thread') as mock_thread:
            
            mock_request_id.set = MagicMock()
            mock_request_id.get.return_value = "test_id"
            mock_api.return_value = {'status': 'success'}
            
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            result = DOCService.mask_doc(payload)
            
            # Verify API was called
            assert mock_api.called
            
            # Verify result
            assert isinstance(result, io.BytesIO)
    
    def test_mask_doc_with_invalid_portfolio(self, sample_doc):
        """Test mask_doc returns None when API call fails."""
        from privacy.service.docs_service import DOCService
        
        mock_file = MagicMock()
        mock_file.file.read.return_value = sample_doc.getvalue()
        
        payload = {
            'file': mock_file,
            'portfolio': 'invalid_portfolio',
            'account': 'invalid_account',
            'exclusion': None,
            'pii_entities_to_be_redacted': None,
            'nlp': False,
            'score_threshold': 0.5
        }
        
        with patch('privacy.service.docs_service.ApiCall.request') as mock_api, \
             patch('privacy.service.docs_service.error_dict', {}, create=True), \
             patch('privacy.service.docs_service.request_id_var') as mock_request_id:
            
            mock_request_id.set = MagicMock()
            mock_request_id.get.return_value = "test_id"
            mock_api.return_value = None
            
            result = DOCService.mask_doc(payload)
            
            # Should return None
            assert result is None
    
    def test_mask_doc_error_handling(self):
        """Test mask_doc handles errors correctly."""
        from privacy.service.docs_service import DOCService
        
        mock_file = MagicMock()
        mock_file.file.read.side_effect = Exception("File read error")
        
        payload = {
            'file': mock_file,
            'portfolio': None,
            'account': None,
            'exclusion': None,
            'pii_entities_to_be_redacted': None,
            'nlp': False,
            'score_threshold': 0.5
        }
        
        with patch('privacy.service.docs_service.error_dict', {}, create=True), \
             patch('privacy.service.docs_service.request_id_var') as mock_request_id:
            
            mock_request_id.set = MagicMock()
            mock_request_id.get.return_value = "error_id"
            
            with pytest.raises(RuntimeError):
                DOCService.mask_doc(payload)
    
    def test_mask_doc_multiple_paragraphs(self, sample_doc):
        """Test mask_doc with multiple paragraphs."""
        from privacy.service.docs_service import DOCService
        
        mock_file = MagicMock()
        mock_file.file.read.return_value = sample_doc.getvalue()
        
        payload = {
            'file': mock_file,
            'portfolio': None,
            'account': None,
            'exclusion': 'EMAIL,PHONE',
            'pii_entities_to_be_redacted': 'PERSON,LOCATION,DATE',
            'nlp': True,
            'score_threshold': 0.6
        }
        
        with patch('privacy.service.docs_service.DOCService.process_text'), \
             patch('privacy.service.docs_service.error_dict', {}, create=True), \
             patch('privacy.service.docs_service.request_id_var') as mock_request_id, \
             patch('threading.Thread') as mock_thread:
            
            mock_request_id.set = MagicMock()
            mock_request_id.get.return_value = "test_id"
            
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            result = DOCService.mask_doc(payload)
            
            # Verify result
            assert isinstance(result, io.BytesIO)
            result.seek(0)
            doc = Document(result)
            # Original doc has 3 paragraphs
            assert len(doc.paragraphs) >= 3


class TestDOCServiceIntegration:
    """Integration tests for DOCService."""
    
    def test_full_workflow(self, sample_doc):
        """Test complete document masking workflow."""
        from privacy.service.docs_service import DOCService
        
        mock_file = MagicMock()
        mock_file.file.read.return_value = sample_doc.getvalue()
        
        payload = {
            'file': mock_file,
            'portfolio': None,
            'account': None,
            'exclusion': 'EMAIL',
            'pii_entities_to_be_redacted': 'PERSON',
            'nlp': False,
            'score_threshold': 0.5
        }
        
        with patch('privacy.service.docs_service.TextPrivacy.text_analyze') as mock_analyze, \
             patch('privacy.service.docs_service.anonymizer') as mock_anonymizer, \
             patch('privacy.service.docs_service.error_dict', {}, create=True), \
             patch('privacy.service.docs_service.request_id_var') as mock_request_id, \
             patch('threading.Thread') as mock_thread:
            
            mock_request_id.set = MagicMock()
            mock_request_id.get.return_value = "integration_test_id"
            mock_analyze.return_value = []
            mock_anonymizer._remove_conflicts_and_get_text_manipulation_data.return_value = []
            mock_anonymizer._merge_entities_with_whitespace_between.return_value = []
            
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            result = DOCService.mask_doc(payload)
            
            # Verify complete workflow
            assert isinstance(result, io.BytesIO)
            result.seek(0)
            
            # Verify document structure is maintained
            doc = Document(result)
            assert len(doc.paragraphs) > 0
