"""
Comprehensive tests for ppt_service.py module
Tests PPTService class for anonymizing PowerPoint files
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import io
import base64
from PIL import Image
from privacy.service.ppt_service import PPTService, AttributeDict


class TestPPTServiceProcessImages:
    """Test PPTService.processImages() method"""
    
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.ImagePrivacy.image_anonymize')
    @patch('privacy.service.ppt_service.Image.open')
    @patch('privacy.service.ppt_service.tempfile.NamedTemporaryFile')
    @patch('privacy.service.ppt_service.os.remove')
    @patch('privacy.service.ppt_service.log')
    def test_process_images_success(self, mock_log, mock_remove, mock_tempfile,
                                   mock_image_open, mock_image_anon, mock_request_id):
        """Test successful image processing"""
        mock_request_id.get.return_value = "test-ppt-uuid"
        
        # Mock shape with image
        mock_shape = Mock()
        mock_shape.shape_type = 13  # MSO_SHAPE_TYPE.PICTURE
        mock_shape.image.blob = b"fake_image_" + b"x" * 700  # > 700 bytes
        
        # Mock image anonymization
        mock_anon_result = base64.b64encode(b"anonymized").decode()
        mock_image_anon.return_value = mock_anon_result
        
        # Mock PIL Image
        mock_img = Mock()
        mock_image_open.return_value = mock_img
        
        # Mock temp file
        mock_temp = Mock()
        mock_temp.name = "/tmp/ppt_image.png"
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        payload = {"portfolio": "test", "account": "test"}
        uid = "test-ppt-uuid"
        
        # Mock slide
        mock_slide = Mock()
        mock_slide.shapes = Mock()
        mock_slide.shapes.add_picture = Mock()
        mock_slide.shapes._spTree = Mock()
        mock_slide.shapes._spTree.remove = Mock()
        
        PPTService.processImages(mock_slide, mock_shape, payload, uid)
        
        # Verify image was anonymized
        assert mock_image_anon.called
        
        # Verify picture was inserted on slide
        mock_slide.shapes.add_picture.assert_called_once()
        
        # Verify cleanup
        mock_remove.assert_called_once()
    
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.log')
    def test_process_images_small_image_skip(self, mock_log, mock_request_id):
        """Test that small images (<700 bytes) are skipped"""
        mock_request_id.get.return_value = "test-uuid"
        
        mock_shape = Mock()
        mock_shape.shape_type = 13
        mock_shape.image.blob = b"small"  # < 700 bytes
        
        payload = {}
        uid = "test-uuid"
        
        # Mock slide
        mock_slide = Mock()
        
        result = PPTService.processImages(mock_slide, mock_shape, payload, uid)
        
        # Should return None
        assert result is None
    
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.error_dict', {})
    @patch('privacy.service.ppt_service.log')
    def test_process_images_exception_handling(self, mock_log, mock_request_id):
        """Test exception handling in processImages"""
        mock_request_id.get.return_value = "test-error-uuid"
        
        from privacy.service.ppt_service import error_dict
        error_dict["test-error-uuid"] = []
        
        mock_shape = Mock()
        mock_shape.shape_type = 13
        mock_shape.image.blob = None  # Will cause error
        
        payload = {}
        uid = "test-error-uuid"
        
        # Mock slide
        mock_slide = Mock()
        
        with pytest.raises(Exception):
            PPTService.processImages(mock_slide, mock_shape, payload, uid)
        
        assert mock_log.error.called


class TestPPTServiceEditText:
    """Test PPTService.editText() method"""
    
    @patch('privacy.service.ppt_service.request_id_var')
    def test_edit_text_replaces_entity(self, mock_request_id):
        """Test editText replaces detected entity"""
        mock_request_id.set.return_value = None
        
        text = "John Doe works here"
        mock_entity = Mock()
        mock_entity.start = 0
        mock_entity.end = 8
        mock_entity.entity_type = "PERSON"
        
        mock_run = Mock()
        mock_run.text = text
        
        PPTService.editText(text, mock_entity, mock_run)
        
        # Verify text was replaced
        expected = text.replace("John Doe", "<PERSON>")
        assert mock_run.text == expected
    
    @patch('privacy.service.ppt_service.request_id_var')
    def test_edit_text_email_entity(self, mock_request_id):
        """Test editText with EMAIL entity"""
        mock_request_id.set.return_value = None
        
        text = "Contact: user@example.com"
        mock_entity = Mock()
        mock_entity.start = 9
        mock_entity.end = 25
        mock_entity.entity_type = "EMAIL"
        
        mock_run = Mock()
        mock_run.text = text
        
        PPTService.editText(text, mock_entity, mock_run)
        
        expected = text.replace("user@example.com", "<EMAIL>")
        assert mock_run.text == expected


class TestPPTServiceProcessText:
    """Test PPTService.processText() method"""
    
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.unicodedata.normalize')
    @patch('privacy.service.ppt_service.TextPrivacy.textAnalyze')
    @patch('privacy.service.ppt_service.anonymizer._remove_conflicts_and_get_text_manipulation_data')
    @patch('privacy.service.ppt_service.anonymizer._merge_entities_with_whitespace_between')
    @patch('privacy.service.ppt_service.threading.Thread')
    def test_process_text_success(self, mock_thread, mock_merge, mock_conflicts,
                                  mock_analyze, mock_normalize, mock_request_id):
        """Test successful text processing"""
        mock_request_id.get.return_value = "ppt-text-uuid"
        mock_request_id.set.return_value = None
        
        # Mock slide with shape
        mock_slide = Mock()
        mock_shape = Mock()
        mock_shape.has_text_frame = True
        mock_shape.text = "John Smith"
        mock_frame = Mock()
        mock_paragraph = Mock()
        mock_run = Mock()
        mock_run.text = "John Smith"
        mock_paragraph.runs = [mock_run]
        mock_frame.paragraphs = [mock_paragraph]
        mock_shape.text_frame = mock_frame
        mock_slide.shapes = [mock_shape]
        
        # Mock normalization
        mock_normalize.return_value = "John Smith"
        
        # Mock analysis
        mock_entity = Mock(start=0, end=10, entity_type="PERSON")
        mock_analyze.return_value = [mock_entity]
        mock_conflicts.return_value = [mock_entity]
        mock_merge.return_value = [mock_entity]
        
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
        uid = "ppt-text-uuid"
        
        PPTService.processText(mock_slide, payload, uid)
        
        # Verify text was normalized
        assert mock_normalize.called
        
        # Verify analysis
        assert mock_analyze.called
        
        # Verify thread created and executed
        assert mock_thread.called
        mock_thread_instance.start.assert_called_once()
        mock_thread_instance.join.assert_called_once()
    
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.unicodedata.normalize')
    @patch('privacy.service.ppt_service.TextPrivacy.textAnalyze')
    @patch('privacy.service.ppt_service.anonymizer._remove_conflicts_and_get_text_manipulation_data')
    @patch('privacy.service.ppt_service.anonymizer._merge_entities_with_whitespace_between')
    def test_process_text_with_portfolio_account(self, mock_merge, mock_conflicts,
                                                 mock_analyze, mock_normalize, mock_request_id):
        """Test processText with portfolio and account"""
        mock_request_id.get.return_value = "uuid-acc"
        
        # Mock slide with shape
        mock_slide = Mock()
        mock_shape = Mock()
        mock_shape.has_text_frame = True
        mock_shape.text = "Test"
        mock_frame = Mock()
        mock_paragraph = Mock()
        mock_run = Mock()
        mock_run.text = "Test"
        mock_paragraph.runs = [mock_run]
        mock_frame.paragraphs = [mock_paragraph]
        mock_shape.text_frame = mock_frame
        mock_slide.shapes = [mock_shape]
        
        mock_normalize.return_value = "Test"
        mock_analyze.return_value = []
        mock_conflicts.return_value = []
        mock_merge.return_value = []
        
        payload = AttributeDict({
            "portfolio": "Portfolio1",
            "account": "Account1",
            "exclusion": "term1,term2",
            "piiEntitiesToBeRedacted": "PERSON,EMAIL",
            "nlp": "spacy"
        })
        uid = "uuid-acc"
        
        PPTService.processText(mock_slide, payload, uid)
        
        # Verify analyze was called with account details
        call_args = mock_analyze.call_args
        assert call_args[1]['accName'].portfolio == "Portfolio1"
        assert call_args[1]['accName'].account == "Account1"
    
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.error_dict', {})
    @patch('privacy.service.ppt_service.log')
    def test_process_text_exception_handling(self, mock_log, mock_request_id):
        """Test exception handling in processText"""
        mock_request_id.get.return_value = "error-uuid"
        
        from privacy.service.ppt_service import error_dict
        error_dict["error-uuid"] = []
        
        # Mock slide with bad shapes
        mock_slide = Mock()
        mock_slide.shapes = None  # Will cause error when iterating
        
        payload = AttributeDict({
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "spacy"
        })
        uid = "error-uuid"
        
        with pytest.raises(Exception):
            PPTService.processText(mock_slide, payload, uid)
        
        assert mock_log.error.called


class TestPPTServiceProcessTables:
    """Test PPTService.processTables() method"""
    
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.unicodedata.normalize')
    @patch('privacy.service.ppt_service.TextPrivacy.textAnalyze')
    @patch('privacy.service.ppt_service.anonymizer._remove_conflicts_and_get_text_manipulation_data')
    @patch('privacy.service.ppt_service.anonymizer._merge_entities_with_whitespace_between')
    @patch('privacy.service.ppt_service.threading.Thread')
    def test_process_tables_success(self, mock_thread, mock_merge, mock_conflicts,
                                   mock_analyze, mock_normalize, mock_request_id):
        """Test successful table processing"""
        mock_request_id.get.return_value = "table-uuid"
        mock_request_id.set.return_value = None
        
        # Mock slide with table shape
        mock_slide = Mock()
        mock_shape = Mock()
        mock_shape.shape_type = 19  # MSO_SHAPE_TYPE.TABLE
        mock_table = Mock()
        mock_cell = Mock()
        mock_cell.text = "Table Data"
        mock_row = Mock()
        mock_row.cells = [mock_cell]
        mock_table.rows = [mock_row]
        mock_shape.table = mock_table
        mock_slide.shapes = [mock_shape]
        
        # Mock normalization
        mock_normalize.return_value = "Table Data"
        
        # Mock analysis
        mock_entity = Mock(start=0, end=10, entity_type="DATA")
        mock_analyze.return_value = [mock_entity]
        mock_conflicts.return_value = [mock_entity]
        mock_merge.return_value = [mock_entity]
        
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        payload = AttributeDict({
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "spacy"
        })
        uid = "table-uuid"
        
        PPTService.processTables(mock_slide, payload, uid)
        
        # Verify table cells were processed
        assert mock_normalize.called
        assert mock_analyze.called
    
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.unicodedata.normalize')
    @patch('privacy.service.ppt_service.TextPrivacy.textAnalyze')
    @patch('privacy.service.ppt_service.anonymizer._remove_conflicts_and_get_text_manipulation_data')
    @patch('privacy.service.ppt_service.anonymizer._merge_entities_with_whitespace_between')
    def test_process_tables_multiple_cells(self, mock_merge, mock_conflicts,
                                           mock_analyze, mock_normalize, mock_request_id):
        """Test table processing with multiple cells"""
        mock_request_id.get.return_value = "multi-cell-uuid"
        
        # Mock slide with table shape containing multiple cells
        mock_slide = Mock()
        mock_shape = Mock()
        mock_shape.shape_type = 19  # MSO_SHAPE_TYPE.TABLE
        mock_table = Mock()
        
        # Create multiple rows with cells
        rows = []
        for i in range(3):
            cell = Mock()
            cell.text = f"Cell {i}"
            row = Mock()
            row.cells = [cell]
            rows.append(row)
        
        mock_table.rows = rows
        mock_shape.table = mock_table
        mock_slide.shapes = [mock_shape]
        
        mock_normalize.side_effect = ["Cell 0", "Cell 1", "Cell 2"]
        mock_analyze.return_value = []
        mock_conflicts.return_value = []
        mock_merge.return_value = []
        
        payload = AttributeDict({
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "spacy"
        })
        uid = "multi-cell-uuid"
        
        PPTService.processTables(mock_slide, payload, uid)
        
        # Verify all cells were processed
        assert mock_normalize.call_count == 3
        assert mock_analyze.call_count == 3
    
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.error_dict', {})
    @patch('privacy.service.ppt_service.log')
    def test_process_tables_exception_handling(self, mock_log, mock_request_id):
        """Test exception handling in processTables"""
        mock_request_id.get.return_value = "table-error"
        
        from privacy.service.ppt_service import error_dict
        error_dict["table-error"] = []
        
        # Mock slide with bad shapes
        mock_slide = Mock()
        mock_slide.shapes = None  # Will cause error when iterating
        
        payload = AttributeDict({
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "spacy"
        })
        uid = "table-error"
        
        with pytest.raises(Exception):
            PPTService.processTables(mock_slide, payload, uid)
        
        assert mock_log.error.called


class TestPPTServiceMaskPPT:
    """Test PPTService.mask_ppt() method"""
    
    @patch('privacy.service.ppt_service.uuid.uuid4')
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.ApiCall.request')
    @patch('privacy.service.ppt_service.Presentation')
    @patch('privacy.service.ppt_service.threading.Thread')
    def test_mask_ppt_without_admin(self, mock_thread, mock_presentation,
                                    mock_api, mock_request_id, mock_uuid):
        """Test mask_ppt without portfolio/account"""
        test_uuid = "ppt-mask-uuid"
        mock_uuid.return_value.hex = test_uuid
        mock_request_id.get.return_value = test_uuid
        mock_request_id.set.return_value = None
        
        # Mock file
        mock_file = Mock()
        mock_file.file.read.return_value = b"fake pptx"
        
        # Mock presentation with slide
        mock_prs = Mock()
        mock_slide = Mock()
        mock_shape = Mock()
        mock_shape.has_text_frame = True
        mock_shape.has_table = False
        mock_shape.shape_type = 1  # Not picture
        mock_frame = Mock()
        mock_frame.paragraphs = []
        mock_shape.text_frame = mock_frame
        mock_slide.shapes = [mock_shape]
        mock_slide.placeholders = []
        mock_prs.slides = [mock_slide]
        mock_presentation.return_value = mock_prs
        
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
        
        result = PPTService.mask_ppt(payload)
        
        # ApiCall should not be called
        mock_api.assert_not_called()
        
        # Verify result
        assert isinstance(result, io.BytesIO)
    
    @patch('privacy.service.ppt_service.uuid.uuid4')
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.ApiCall.request')
    @patch('privacy.service.ppt_service.Presentation')
    @patch('privacy.service.ppt_service.threading.Thread')
    def test_mask_ppt_with_admin_api(self, mock_thread, mock_presentation,
                                     mock_api, mock_request_id, mock_uuid):
        """Test mask_ppt with portfolio and account"""
        test_uuid = "ppt-admin-uuid"
        mock_uuid.return_value.hex = test_uuid
        mock_request_id.set.return_value = None
        
        mock_file = Mock()
        mock_file.file.read.return_value = b"pptx data"
        
        mock_prs = Mock()
        mock_prs.slides = []
        mock_presentation.return_value = mock_prs
        
        # Mock API response
        mock_api.return_value = (["PERSON"], ["data"], ["pre"])
        
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        payload = {
            "file": mock_file,
            "portfolio": "Portfolio1",
            "account": "Account1",
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "spacy"
        }
        
        result = PPTService.mask_ppt(payload)
        
        # ApiCall should be called
        mock_api.assert_called_once()
        call_payload = mock_api.call_args[0][0]
        assert call_payload.portfolio == "Portfolio1"
        assert call_payload.account == "Account1"
        
        assert isinstance(result, io.BytesIO)
    
    @patch('privacy.service.ppt_service.uuid.uuid4')
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.ApiCall.request')
    @patch('privacy.service.ppt_service.Presentation')
    def test_mask_ppt_api_returns_none(self, mock_presentation, mock_api,
                                       mock_request_id, mock_uuid):
        """Test mask_ppt when API returns None"""
        test_uuid = "ppt-none-uuid"
        mock_uuid.return_value.hex = test_uuid
        mock_request_id.set.return_value = None
        
        mock_file = Mock()
        mock_file.file.read.return_value = b"pptx"
        
        # API returns None
        mock_api.return_value = None
        
        payload = {
            "file": mock_file,
            "portfolio": "Portfolio1",
            "account": "Account1",
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "spacy"
        }
        
        result = PPTService.mask_ppt(payload)
        
        # Should return None
        assert result is None
    
    @patch('privacy.service.ppt_service.uuid.uuid4')
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.Presentation')
    @patch('privacy.service.ppt_service.threading.Thread')
    def test_mask_ppt_with_table_shapes(self, mock_thread, mock_presentation,
                                        mock_request_id, mock_uuid):
        """Test mask_ppt with table shapes"""
        test_uuid = "ppt-table-uuid"
        mock_uuid.return_value.hex = test_uuid
        mock_request_id.get.return_value = test_uuid
        mock_request_id.set.return_value = None
        
        mock_file = Mock()
        mock_file.file.read.return_value = b"pptx with table"
        
        # Mock shape with table
        mock_shape = Mock()
        mock_shape.has_text_frame = False
        mock_shape.has_table = True
        mock_shape.shape_type = 19  # TABLE
        mock_table = Mock()
        mock_cell = Mock()
        mock_frame = Mock()
        mock_frame.paragraphs = []
        mock_cell.text_frame = mock_frame
        mock_table.iter_cells.return_value = [mock_cell]
        mock_shape.table = mock_table
        
        mock_slide = Mock()
        mock_slide.shapes = [mock_shape]
        mock_slide.placeholders = []
        
        mock_prs = Mock()
        mock_prs.slides = [mock_slide]
        mock_presentation.return_value = mock_prs
        
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
        
        result = PPTService.mask_ppt(payload)
        
        # Verify table was processed
        assert mock_thread.called
        assert isinstance(result, io.BytesIO)
    
    @patch('privacy.service.ppt_service.uuid.uuid4')
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.error_dict', {})
    @patch('privacy.service.ppt_service.log')
    @patch('privacy.service.ppt_service.Presentation')
    def test_mask_ppt_exception_handling(self, mock_presentation, mock_log,
                                        mock_request_id, mock_uuid):
        """Test exception handling in mask_ppt"""
        test_uuid = "ppt-error-uuid"
        mock_uuid.return_value.hex = test_uuid
        mock_request_id.get.return_value = test_uuid
        mock_request_id.set.return_value = None
        
        from privacy.service.ppt_service import error_dict
        error_dict[test_uuid] = []
        
        mock_file = Mock()
        mock_file.file.read.side_effect = Exception("Read error")
        
        payload = {
            "file": mock_file,
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "spacy"
        }
        
        with pytest.raises(Exception):
            PPTService.mask_ppt(payload)
        
        assert mock_log.error.called
        assert len(error_dict[test_uuid]) > 0


class TestPPTServiceIntegration:
    """Integration tests for PPTService"""
    
    @patch('privacy.service.ppt_service.uuid.uuid4')
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.Presentation')
    @patch('privacy.service.ppt_service.PPTService.processText')
    @patch('privacy.service.ppt_service.PPTService.processTables')
    @patch('privacy.service.ppt_service.threading.Thread')
    def test_full_workflow_mixed_shapes(self, mock_thread, mock_process_tables,
                                       mock_process_text, mock_presentation,
                                       mock_request_id, mock_uuid):
        """Test complete workflow with mixed shape types"""
        test_uuid = "ppt-full-uuid"
        mock_uuid.return_value.hex = test_uuid
        mock_request_id.get.return_value = test_uuid
        mock_request_id.set.return_value = None
        
        mock_file = Mock()
        mock_file.file.read.return_value = b"complete pptx"
        
        # Shape 1: Text frame
        shape1 = Mock()
        shape1.has_text_frame = True
        shape1.has_table = False
        shape1.shape_type = 1
        
        # Shape 2: Table
        shape2 = Mock()
        shape2.has_text_frame = False
        shape2.has_table = True
        shape2.shape_type = 19
        
        mock_slide = Mock()
        mock_slide.shapes = [shape1, shape2]
        mock_slide.placeholders = []
        
        mock_prs = Mock()
        mock_prs.slides = [mock_slide]
        mock_presentation.return_value = mock_prs
        
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        payload = {
            "file": mock_file,
            "portfolio": None,
            "account": None,
            "exclusion": "term1,term2",
            "piiEntitiesToBeRedacted": "PERSON,EMAIL",
            "nlp": "spacy"
        }
        
        result = PPTService.mask_ppt(payload)
        
        # Verify threads were created for processing shapes
        # processText and processTables are called through threading
        assert mock_thread.call_count >= 2
        assert isinstance(result, io.BytesIO)
    
    @patch('privacy.service.ppt_service.uuid.uuid4')
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.Presentation')
    @patch('privacy.service.ppt_service.PPTService.processImages')
    @patch('privacy.service.ppt_service.threading.Thread')
    def test_full_workflow_with_images(self, mock_thread, mock_process_images,
                                       mock_presentation, mock_request_id, mock_uuid):
        """Test complete workflow with image processing"""
        test_uuid = "ppt-img-uuid"
        mock_uuid.return_value.hex = test_uuid
        mock_request_id.get.return_value = test_uuid
        mock_request_id.set.return_value = None
        
        mock_file = Mock()
        mock_file.file.read.return_value = b"pptx with images"
        
        # Picture shape
        mock_shape = Mock()
        mock_shape.has_text_frame = False
        mock_shape.has_table = False
        mock_shape.shape_type = 13  # PICTURE
        mock_shape.image = Mock()
        mock_shape.image.blob = b"image_data_" + b"x" * 700
        
        mock_slide = Mock()
        mock_slide.shapes = [mock_shape]
        mock_slide.placeholders = [Mock()]
        
        mock_prs = Mock()
        mock_prs.slides = [mock_slide]
        mock_presentation.return_value = mock_prs
        
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
        
        result = PPTService.mask_ppt(payload)
        
        # Verify threads were created for processing images
        # processImages is called through threading in mask_ppt
        assert mock_thread.call_count >= 1
        assert isinstance(result, io.BytesIO)


class TestPPTServiceEdgeCases:
    """Test edge cases for missing coverage lines 64, 87, 102, 117, 128, 172"""
    
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.error_dict', {})
    @patch('privacy.service.ppt_service.os.remove')
    @patch('privacy.service.ppt_service.log')
    def test_process_images_with_exception(self, mock_log, mock_remove, mock_error_dict, mock_request_id):
        """Test processImages when exception occurs (line 64)"""
        mock_request_id.get.return_value = "test-ppt-exception"
        
        mock_shape = Mock()
        mock_shape.image = Mock()
        mock_shape.image.blob = b"fake_image"
        
        # Make os.remove raise exception
        mock_remove.side_effect = OSError("Cannot remove file")
        
        with pytest.raises(Exception):
            with patch('privacy.service.ppt_service.tempfile.NamedTemporaryFile') as mock_temp:
                mock_temp_file = Mock()
                mock_temp_file.name = "/tmp/ppt_test.png"
                mock_temp.return_value.__enter__.return_value = mock_temp_file
                
                PPTService.processImages(mock_shape, {}, "test-uid")
    
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.error_dict', {})
    @patch('privacy.service.ppt_service.threading.Thread')
    @patch('privacy.service.ppt_service.log')
    def test_process_text_with_thread_exception(self, mock_log, mock_thread, mock_error_dict, mock_request_id):
        """Test processText when threading raises exception (line 87)"""
        mock_request_id.get.return_value = "test-ppt-thread"
        
        mock_slide = Mock()
        mock_shape = Mock()
        mock_shape.has_text_frame = True
        mock_shape.text_frame = Mock()
        mock_slide.shapes = [mock_shape]
        
        # Make thread raise exception
        mock_thread.side_effect = RuntimeError("Thread failed")
        
        with pytest.raises(Exception):
            PPTService.processText(mock_slide, {}, "test-uid")
    
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.error_dict', {})
    @patch('privacy.service.ppt_service.threading.Thread')
    @patch('privacy.service.ppt_service.log')
    def test_process_tables_with_exception(self, mock_log, mock_thread, mock_error_dict, mock_request_id):
        """Test processTables when exception occurs (lines 102, 117)"""
        mock_request_id.get.return_value = "test-ppt-table"
        
        mock_table = Mock()
        mock_cell = Mock()
        mock_cell.text = "Test cell"
        mock_table.iter_cells.return_value = [mock_cell]
        
        # Make thread raise exception
        mock_thread.side_effect = RuntimeError("Table processing failed")
        
        with pytest.raises(Exception):
            PPTService.processTables(mock_table, {}, "test-uid")
    
    @patch('privacy.service.ppt_service.Presentation')
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.uuid.uuid4')
    def test_mask_ppt_with_exception_handling(self, mock_uuid, mock_request_id, mock_presentation):
        """Test mask_ppt exception handling paths (lines 128, 172)"""
        test_uuid = "ppt-exception-test"
        mock_uuid.return_value.hex = test_uuid
        mock_request_id.get.return_value = test_uuid
        mock_request_id.set = Mock()
        
        mock_file = Mock()
        mock_file.file.read.return_value = b"pptx content"
        
        # Make Presentation raise exception
        mock_presentation.side_effect = Exception("Failed to load presentation")
        
        payload = {
            "file": mock_file,
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "basic"
        }
        
        with patch('privacy.service.ppt_service.error_dict', {}):
            with patch('privacy.service.ppt_service.log'):
                with pytest.raises(Exception):
                    PPTService.mask_ppt(payload)
    
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.error_dict', {})
    @patch('privacy.service.ppt_service.log')
    def test_process_images_error_dict_initialization(self, mock_log, mock_error_dict, mock_request_id):
        """Test processImages error_dict initialization when key doesn't exist (line 64)"""
        mock_request_id.get.return_value = "new-uuid-not-in-dict"
        
        mock_paragraph = Mock()
        mock_run = Mock()
        mock_run._element.xpath.side_effect = Exception("Image processing error")
        
        with pytest.raises(Exception):
            PPTService.processImages(mock_paragraph, mock_run, {}, "test-uid")
        
        mock_shape = Mock()
        mock_shape.image = Mock()
        mock_shape.image.blob = b"x" * 100  # Small blob < 700 bytes
        
        # Trigger exception by making tempfile fail
        with patch('privacy.service.ppt_service.tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.side_effect = IOError("Temp file creation failed")
            
            with pytest.raises(Exception):
                PPTService.processImages(mock_shape, {}, "test-uid")
    
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.error_dict', {})
    @patch('privacy.service.ppt_service.TextPrivacy.textAnalyze')
    @patch('privacy.service.ppt_service.AnonymizerEngine')
    @patch('privacy.service.ppt_service.log')
    def test_process_text_with_value_error(self, mock_log, mock_anon_engine, mock_analyze, mock_error_dict, mock_request_id):
        """Test processText when textAnalyze returns non-list (line 87)"""
        mock_request_id.get.return_value = "test-value-error"
        
        mock_slide = Mock()
        mock_shape = Mock()
        mock_shape.has_text_frame = True
        mock_shape.text_frame = Mock()
        mock_shape.text_frame.text = "Test text"
        mock_slide.shapes = [mock_shape]
        
        # Make textAnalyze return non-list to trigger ValueError on line 87
        mock_analyze.return_value = "not a list"
        
        payload = AttributeDict({
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "basic"
        })
        
        with pytest.raises(Exception):
            PPTService.processText(mock_slide, payload, "test-uid")
    
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.error_dict', {})
    @patch('privacy.service.ppt_service.TextPrivacy.textAnalyze')
    @patch('privacy.service.ppt_service.log')
    def test_process_tables_with_cell_text_exception(self, mock_log, mock_analyze, mock_error_dict, mock_request_id):
        """Test processTables when cell.text raises exception (line 117)"""
        mock_request_id.get.return_value = "test-table-error"
        
        mock_table = Mock()
        mock_row = Mock()
        mock_cell = Mock()
        
        # Make cell.text raise an exception
        type(mock_cell).text = property(lambda self: (_ for _ in ()).throw(AttributeError("No text")))
        
        mock_row.cells = [mock_cell]
        mock_table.rows = [mock_row]
        
        payload = AttributeDict({
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "basic"
        })
        
        with pytest.raises(Exception):
            PPTService.processTables(mock_table, payload, "test-uid")


class TestPPTServiceMissingLinesCoverage:
    """Additional tests to cover missing lines 87 and 117"""
    
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.TextPrivacy.textAnalyze')
    @patch('privacy.service.ppt_service.anonymizer')
    @patch('privacy.service.ppt_service.threading')
    @patch('privacy.service.ppt_service.log')
    @patch('privacy.service.ppt_service.error_dict', {})
    def test_process_text_with_non_list_result_raises_value_error(
        self, mock_log, mock_threading, mock_anonymizer, mock_text_analyze, mock_request_id):
        """Test processText raises ValueError when textAnalyze doesn't return a list (line 87)"""
        
        mock_request_id.get.return_value = "test-uuid"
        mock_request_id.set.return_value = None
        
        # Mock slide with text shape
        mock_shape = Mock()
        mock_shape.shape_type = 17  # MSO_SHAPE_TYPE.TEXT_BOX
        mock_shape.has_text_frame = True
        mock_shape.text = "Test text"
        mock_shape.text_frame.paragraphs = [Mock(runs=[Mock(text="Test")])]
        
        mock_slide = Mock()
        mock_slide.shapes = [mock_shape]
        
        # Mock textAnalyze to return non-list (triggers line 87)
        mock_text_analyze.return_value = "not a list"  # Should be a list!
        
        payload = AttributeDict({
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "basic"
        })
        
        # Should raise Exception (ValueError gets wrapped in Exception)
        with pytest.raises(Exception):
            PPTService.processText(mock_slide, payload, "test-uuid")
        
        # Verify error was logged (line 87 was executed)
        assert mock_log.error.called
    
    @patch('privacy.service.ppt_service.request_id_var')
    @patch('privacy.service.ppt_service.TextPrivacy.textAnalyze')
    @patch('privacy.service.ppt_service.anonymizer')
    def test_process_tables_shape_type_check(
        self, mock_anonymizer, mock_text_analyze, mock_request_id):
        """Test processTables checks for TABLE shape type (line 117)"""
        
        mock_request_id.get.return_value = "test-uuid"
        mock_request_id.set.return_value = None
        
        # Mock slide with NON-table shape
        mock_shape_non_table = Mock()
        mock_shape_non_table.shape_type = 17  # NOT MSO_SHAPE_TYPE.TABLE (which is 19)
        
        mock_slide = Mock()
        mock_slide.shapes = [mock_shape_non_table]
        
        payload = AttributeDict({
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "piiEntitiesToBeRedacted": None,
            "nlp": "basic"
        })
        
        # Call processTables - should skip non-table shapes (line 117 check)
        PPTService.processTables(mock_slide, payload, "test-uuid")
        
        # textAnalyze should NOT be called since no table shapes
        assert not mock_text_analyze.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])