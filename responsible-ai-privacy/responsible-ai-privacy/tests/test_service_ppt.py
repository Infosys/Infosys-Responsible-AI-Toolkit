"""
Tests for PPTService class in privacy.service.ppt_service module
Tests PowerPoint text/image anonymization, table processing, and notes handling
"""
import pytest
import sys
import io
import base64
import tempfile
import os
from unittest.mock import MagicMock, patch, Mock, PropertyMock
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def mock_attribute_dict():
    """Create AttributeDict mock fixture"""
    def _create_attribute_dict(data):
        from privacy.service import AttributeDict
        return AttributeDict(data)
    return _create_attribute_dict


@pytest.fixture
def mock_payload(mock_attribute_dict):
    """Create mock payload for PPT operations"""
    return mock_attribute_dict({
        "file": MagicMock(file=MagicMock(read=MagicMock(return_value=b"fake_ppt_data"))),
        "portfolio": "test_portfolio",
        "account": "test_account",
        "exclusion": "PHONE_NUMBER,CREDIT_CARD",
        "pii_entities_to_be_redacted": "PERSON,EMAIL_ADDRESS",
        "nlp": "spacy",
        "score_threshold": 0.5
    })


@pytest.fixture
def mock_payload_minimal(mock_attribute_dict):
    """Create minimal mock payload (no portfolio/account)"""
    return mock_attribute_dict({
        "file": MagicMock(file=MagicMock(read=MagicMock(return_value=b"fake_ppt_data"))),
        "portfolio": None,
        "account": None,
        "exclusion": None,
        "pii_entities_to_be_redacted": None,
        "nlp": None,
        "score_threshold": None
    })


@pytest.fixture
def mock_entity():
    """Create mock PII entity"""
    entity = MagicMock()
    entity.start = 5
    entity.end = 15
    entity.entity_type = "PERSON"
    return entity


@pytest.fixture
def mock_entity_invalid():
    """Create mock entity with invalid range"""
    entity = MagicMock()
    entity.start = 10
    entity.end = 5  # end < start
    entity.entity_type = "PERSON"
    return entity


class TestPPTServiceNormalizeText:
    """Tests for PPTService.normalize_text_with_mapping method"""
    
    def test_normalize_ascii_text(self):
        """Test normalizing plain ASCII text"""
        from privacy.service.ppt_service import PPTService
        
        text = "Hello World"
        normalized, index_map, boundary_map = PPTService.normalize_text_with_mapping(text)
        
        assert normalized == "Hello World"
        assert len(index_map) > 0
        assert len(boundary_map) > 0
    
    def test_normalize_text_with_special_chars(self):
        """Test normalizing text with special characters"""
        from privacy.service.ppt_service import PPTService
        
        text = "Test@Email.com"
        normalized, index_map, boundary_map = PPTService.normalize_text_with_mapping(text)
        
        assert isinstance(normalized, str)
        assert len(index_map) == len(normalized)
    
    def test_normalize_empty_text(self):
        """Test normalizing empty text"""
        from privacy.service.ppt_service import PPTService
        
        text = ""
        normalized, index_map, boundary_map = PPTService.normalize_text_with_mapping(text)
        
        assert normalized == ""
        assert len(index_map) == 0
        assert boundary_map == [0]
    
    def test_normalize_unicode_text(self):
        """Test normalizing unicode/accented text"""
        from privacy.service.ppt_service import PPTService
        
        text = "Café François"
        normalized, index_map, boundary_map = PPTService.normalize_text_with_mapping(text)
        
        # Should normalize accented characters to ASCII equivalents
        assert isinstance(normalized, str)
        assert len(boundary_map) > 0


class TestPPTServiceGetOriginalSubstring:
    """Tests for PPTService.get_original_substring method"""
    
    def test_get_original_substring_valid(self):
        """Test getting original substring with valid entity"""
        from privacy.service.ppt_service import PPTService
        
        source_text = "John Doe is here"
        normalized_text = "John Doe is here"
        index_map = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        boundary_map = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        
        entity = MagicMock()
        entity.start = 0
        entity.end = 4
        
        result = PPTService.get_original_substring(source_text, entity, index_map, boundary_map)
        assert result == "John"
    
    def test_get_original_substring_empty_maps(self):
        """Test get_original_substring with empty maps"""
        from privacy.service.ppt_service import PPTService
        
        source_text = "Some text"
        entity = MagicMock()
        entity.start = 0
        entity.end = 4
        
        result = PPTService.get_original_substring(source_text, entity, [], [])
        assert result is None
    
    def test_get_original_substring_invalid_range(self):
        """Test get_original_substring with start >= end"""
        from privacy.service.ppt_service import PPTService
        
        source_text = "Test text"
        entity = MagicMock()
        entity.start = 10
        entity.end = 5
        
        index_map = list(range(20))
        boundary_map = list(range(21))
        
        result = PPTService.get_original_substring(source_text, entity, index_map, boundary_map)
        assert result is None
    
    def test_get_original_substring_out_of_bounds(self):
        """Test get_original_substring with out of bounds entity"""
        from privacy.service.ppt_service import PPTService
        
        source_text = "Test"
        entity = MagicMock()
        entity.start = 10
        entity.end = 20
        
        index_map = [0, 1, 2, 3]
        boundary_map = [0, 1, 2, 3, 4]
        
        result = PPTService.get_original_substring(source_text, entity, index_map, boundary_map)
        assert result is None


class TestPPTServiceProcessImages:
    """Tests for PPTService.process_images method"""
    
    def test_process_images_small_image(self, mock_payload, mock_attribute_dict):
        """Test process_images skips small images"""
        from privacy.service.ppt_service import PPTService
        
        mock_slide = MagicMock()
        mock_shape = MagicMock()
        mock_shape.image = MagicMock()
        mock_shape.image.blob = b"small"  # Less than 700 bytes
        
        result = PPTService.process_images(mock_slide, mock_shape, {}, "test-uid")
        assert result is None
    
    def test_process_images_large_image_success(self, mock_payload, mock_attribute_dict):
        """Test process_images processes large images successfully"""
        from privacy.service.ppt_service import PPTService
        from PIL import Image
        
        # Create fake image bytes
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        fake_img_data = img_bytes.getvalue()
        
        # Ensure it's large enough
        fake_img_data = fake_img_data + b"x" * 1000  # Make it > 700 bytes
        
        mock_slide = MagicMock()
        mock_shape = MagicMock()
        mock_shape.image = MagicMock()
        mock_shape.image.blob = fake_img_data
        mock_shape.left = 100
        mock_shape.top = 100
        mock_shape.width = 200
        mock_shape.height = 200
        
        payload = mock_attribute_dict({
            "image": mock_attribute_dict({"file": io.BytesIO(fake_img_data)})
        })
        
        with patch('privacy.service.ppt_service.ImagePrivacy.image_anonymize') as mock_anon, \
             patch('privacy.service.ppt_service.base64.b64decode') as mock_decode, \
             patch('privacy.service.ppt_service.Image.open') as mock_img_open, \
             patch('privacy.service.ppt_service.tempfile.NamedTemporaryFile'), \
             patch('privacy.service.ppt_service.os.remove'), \
             patch('privacy.service.ppt_service.request_id_var'), \
             patch('privacy.service.ppt_service.error_dict', {}):
            
            mock_anon.return_value = base64.b64encode(fake_img_data).decode()
            mock_decode.return_value = fake_img_data
            mock_img_obj = MagicMock()
            mock_img_open.return_value = mock_img_obj
            
            # Should not raise
            PPTService.process_images(mock_slide, mock_shape, payload, "test-uid")
    
    def test_process_images_exception_handling(self, mock_payload):
        """Test process_images handles exceptions properly"""
        from privacy.service.ppt_service import PPTService
        
        mock_slide = MagicMock()
        mock_shape = MagicMock()
        # Setup the image mock with blob property that raises
        mock_image = MagicMock()
        type(mock_image).blob = PropertyMock(side_effect=Exception("Image read error"))
        mock_shape.image = mock_image
        
        with patch('privacy.service.ppt_service.request_id_var') as mock_request_id, \
             patch('privacy.service.ppt_service.error_dict', {}), \
             patch('privacy.service.ppt_service.log'):
            
            mock_request_id.get.return_value = "test-id"
            
            with pytest.raises(RuntimeError):
                PPTService.process_images(mock_slide, mock_shape, {}, "test-uid")


class TestPPTServiceEditText:
    """Tests for PPTService.edit_text method"""
    
    def test_edit_text_replace_success(self):
        """Test edit_text successfully replaces PII with tags"""
        from privacy.service.ppt_service import PPTService
        
        mock_shape = MagicMock()
        mock_shape.text = "John Doe lives here"
        
        entity = MagicMock()
        entity.start = 0
        entity.end = 4
        entity.entity_type = "PERSON"
        
        source_text = "John Doe lives here"
        index_map = list(range(19))
        boundary_map = list(range(20))
        
        with patch('privacy.service.ppt_service.PPTService.get_original_substring') as mock_get:
            mock_get.return_value = "John"
            
            PPTService.edit_text("John Doe lives here", entity, mock_shape, source_text, index_map, boundary_map)
            
            # Verify replacement was attempted
            assert "<PERSON>" in mock_shape.text
    
    def test_edit_text_no_replacement_text(self):
        """Test edit_text when get_original_substring returns None"""
        from privacy.service.ppt_service import PPTService
        
        mock_shape = MagicMock()
        mock_shape.text = "Original text"
        
        entity = MagicMock()
        entity.entity_type = "PERSON"
        
        with patch('privacy.service.ppt_service.PPTService.get_original_substring') as mock_get, \
             patch('privacy.service.ppt_service.request_id_var'), \
             patch('privacy.service.ppt_service.log'):
            
            mock_get.return_value = None
            
            PPTService.edit_text("text", entity, mock_shape, "text", [], [])
            
            # Verify text was not changed
            assert mock_shape.text == "Original text"


class TestPPTServiceProcessText:
    """Tests for PPTService.process_text method"""
    
    def test_process_text_simple(self, mock_payload):
        """Test processing text in slide shapes"""
        from privacy.service.ppt_service import PPTService
        
        mock_slide = MagicMock()
        mock_shape = MagicMock()
        mock_shape.has_text_frame = True
        mock_shape.text = "John Doe email@test.com"
        mock_slide.shapes = [mock_shape]
        
        mock_entity = MagicMock()
        mock_entity.start = 0
        mock_entity.end = 4
        mock_entity.entity_type = "PERSON"
        
        with patch('privacy.service.ppt_service.PPTService.normalize_text_with_mapping') as mock_norm, \
             patch('privacy.service.ppt_service.TextPrivacy.text_analyze') as mock_analyze, \
             patch('privacy.service.ppt_service.anonymizer._remove_conflicts_and_get_text_manipulation_data') as mock_remove, \
             patch('privacy.service.ppt_service.anonymizer._merge_entities_with_whitespace_between') as mock_merge, \
             patch('privacy.service.ppt_service.PPTService.edit_text'), \
             patch('privacy.service.ppt_service.request_id_var'), \
             patch('privacy.service.ppt_service.threading.Thread'), \
             patch('privacy.service.ppt_service.error_dict', {}):
            
            mock_norm.return_value = ("John Doe email@test.com", list(range(23)), list(range(24)))
            mock_analyze.return_value = [mock_entity]
            mock_remove.return_value = [mock_entity]
            mock_merge.return_value = [mock_entity]
            
            # Mock Thread to run immediately
            def mock_thread_run(*args, **kwargs):
                mock_thread = MagicMock()
                if 'target' in kwargs:
                    kwargs['target'](*kwargs.get('args', []))
                mock_thread.start = MagicMock()
                mock_thread.join = MagicMock()
                return mock_thread
            
            with patch('privacy.service.ppt_service.threading.Thread', side_effect=mock_thread_run):
                PPTService.process_text(mock_slide, mock_payload, "test-uid")
    
    def test_process_text_invalid_analyze_result(self, mock_payload):
        """Test process_text with invalid text_analyze result"""
        from privacy.service.ppt_service import PPTService
        
        mock_slide = MagicMock()
        mock_shape = MagicMock()
        mock_shape.has_text_frame = True
        mock_shape.text = "Some text"
        mock_slide.shapes = [mock_shape]
        
        with patch('privacy.service.ppt_service.PPTService.normalize_text_with_mapping') as mock_norm, \
             patch('privacy.service.ppt_service.TextPrivacy.text_analyze') as mock_analyze, \
             patch('privacy.service.ppt_service.request_id_var') as mock_req_id, \
             patch('privacy.service.ppt_service.error_dict', {}), \
             patch('privacy.service.ppt_service.log'):
            
            mock_norm.return_value = ("Some text", [0]*9, [0]*10)
            mock_analyze.return_value = "not a list"  # Invalid return type
            mock_req_id.get.return_value = "test-id"
            
            with pytest.raises(RuntimeError):
                PPTService.process_text(mock_slide, mock_payload, "test-uid")
    
    def test_process_text_exception_handling(self, mock_payload):
        """Test process_text handles exceptions"""
        from privacy.service.ppt_service import PPTService
        
        mock_slide = MagicMock()
        mock_shape = MagicMock()
        mock_shape.has_text_frame = True
        mock_shape.text = "Text"
        mock_slide.shapes = [mock_shape]
        
        with patch('privacy.service.ppt_service.PPTService.normalize_text_with_mapping', 
                  side_effect=Exception("Normalization error")), \
             patch('privacy.service.ppt_service.request_id_var') as mock_req_id, \
             patch('privacy.service.ppt_service.error_dict', {}), \
             patch('privacy.service.ppt_service.log'):
            
            mock_req_id.get.return_value = "test-id"
            
            with pytest.raises(RuntimeError):
                PPTService.process_text(mock_slide, mock_payload, "test-uid")


class TestPPTServiceProcessTables:
    """Tests for PPTService.process_tables method"""
    
    def test_process_tables_simple(self, mock_payload):
        """Test processing tables in slides"""
        from privacy.service.ppt_service import PPTService
        from pptx.enum.shapes import MSO_SHAPE_TYPE
        
        # Create mock table structure
        mock_cell = MagicMock()
        mock_cell.text = "John Doe"
        
        mock_row = MagicMock()
        mock_row.cells = [mock_cell]
        
        mock_table = MagicMock()
        mock_table.rows = [mock_row]
        
        mock_shape = MagicMock()
        mock_shape.shape_type = MSO_SHAPE_TYPE.TABLE
        mock_shape.table = mock_table
        
        mock_slide = MagicMock()
        mock_slide.shapes = [mock_shape]
        
        mock_entity = MagicMock()
        mock_entity.start = 0
        mock_entity.end = 4
        mock_entity.entity_type = "PERSON"
        
        with patch('privacy.service.ppt_service.PPTService.normalize_text_with_mapping') as mock_norm, \
             patch('privacy.service.ppt_service.TextPrivacy.text_analyze') as mock_analyze, \
             patch('privacy.service.ppt_service.anonymizer._remove_conflicts_and_get_text_manipulation_data') as mock_remove, \
             patch('privacy.service.ppt_service.anonymizer._merge_entities_with_whitespace_between') as mock_merge, \
             patch('privacy.service.ppt_service.PPTService.get_original_substring') as mock_get, \
             patch('privacy.service.ppt_service.request_id_var'), \
             patch('privacy.service.ppt_service.error_dict', {}):
            
            mock_norm.return_value = ("John Doe ,", list(range(10)), list(range(11)))
            mock_analyze.return_value = [mock_entity]
            mock_remove.return_value = [mock_entity]
            mock_merge.return_value = [mock_entity]
            mock_get.return_value = "John"
            
            PPTService.process_tables(mock_slide, mock_payload, "test-uid")
            
            # Verify replacement was attempted
            assert "<PERSON>" in mock_cell.text
    
    def test_process_tables_no_tables(self, mock_payload):
        """Test process_tables with no tables in slide"""
        from privacy.service.ppt_service import PPTService
        from pptx.enum.shapes import MSO_SHAPE_TYPE
        
        mock_shape = MagicMock()
        mock_shape.shape_type = MSO_SHAPE_TYPE.TEXT_BOX  # Not a table
        
        mock_slide = MagicMock()
        mock_slide.shapes = [mock_shape]
        
        with patch('privacy.service.ppt_service.request_id_var'), \
             patch('privacy.service.ppt_service.error_dict', {}):
            
            # Should not raise
            PPTService.process_tables(mock_slide, mock_payload, "test-uid")


class TestPPTServiceProcessNotes:
    """Tests for PPTService.process_notes method"""
    
    def test_process_notes_with_text(self, mock_payload):
        """Test processing notes with text"""
        from privacy.service.ppt_service import PPTService
        
        mock_paragraph = MagicMock()
        mock_paragraph.text = "Speaker notes with John Doe"
        
        mock_notes_text_frame = MagicMock()
        mock_notes_text_frame.paragraphs = [mock_paragraph]
        
        mock_notes_slide = MagicMock()
        mock_notes_slide.notes_text_frame = mock_notes_text_frame
        
        mock_slide = MagicMock()
        mock_slide.notes_slide = mock_notes_slide
        
        mock_entity = MagicMock()
        mock_entity.start = 20
        mock_entity.end = 29
        mock_entity.entity_type = "PERSON"
        
        with patch('privacy.service.ppt_service.PPTService.normalize_text_with_mapping') as mock_norm, \
             patch('privacy.service.ppt_service.TextPrivacy.text_analyze') as mock_analyze, \
             patch('privacy.service.ppt_service.anonymizer._remove_conflicts_and_get_text_manipulation_data') as mock_remove, \
             patch('privacy.service.ppt_service.anonymizer._merge_entities_with_whitespace_between') as mock_merge, \
             patch('privacy.service.ppt_service.PPTService.get_original_substring') as mock_get, \
             patch('privacy.service.ppt_service.request_id_var'), \
             patch('privacy.service.ppt_service.error_dict', {}):
            
            mock_norm.return_value = ("Speaker notes with John Doe", list(range(29)), list(range(30)))
            mock_analyze.return_value = [mock_entity]
            mock_remove.return_value = [mock_entity]
            mock_merge.return_value = [mock_entity]
            mock_get.return_value = "John Doe"
            
            PPTService.process_notes(mock_slide, mock_payload, "test-uid")
            
            # Verify replacement was attempted
            assert "<PERSON>" in mock_paragraph.text
    
    def test_process_notes_no_notes_slide(self, mock_payload):
        """Test process_notes with no notes slide"""
        from privacy.service.ppt_service import PPTService
        
        mock_slide = MagicMock()
        mock_slide.notes_slide = None
        
        with patch('privacy.service.ppt_service.request_id_var'), \
             patch('privacy.service.ppt_service.error_dict', {}):
            
            # Should not raise
            PPTService.process_notes(mock_slide, mock_payload, "test-uid")
    
    def test_process_notes_empty_paragraphs(self, mock_payload):
        """Test process_notes with empty text frames"""
        from privacy.service.ppt_service import PPTService
        
        mock_paragraph = MagicMock()
        mock_paragraph.text = "   "  # Whitespace only
        
        mock_notes_text_frame = MagicMock()
        mock_notes_text_frame.paragraphs = [mock_paragraph]
        
        mock_notes_slide = MagicMock()
        mock_notes_slide.notes_text_frame = mock_notes_text_frame
        
        mock_slide = MagicMock()
        mock_slide.notes_slide = mock_notes_slide
        
        with patch('privacy.service.ppt_service.request_id_var'), \
             patch('privacy.service.ppt_service.error_dict', {}):
            
            # Should not raise (empty paragraphs are skipped)
            PPTService.process_notes(mock_slide, mock_payload, "test-uid")


class TestPPTServiceMaskPPT:
    """Tests for PPTService.mask_ppt main method"""
    
    def test_mask_ppt_minimal_payload(self, mock_payload_minimal):
        """Test mask_ppt with minimal payload"""
        from privacy.service.ppt_service import PPTService
        
        mock_presentation = MagicMock()
        mock_slide = MagicMock()
        mock_slide.shapes = []
        mock_presentation.slides = [mock_slide]
        
        ppt_bytes = io.BytesIO()
        mock_presentation.save = MagicMock(side_effect=lambda x: x.write(b"fake_ppt"))
        
        with patch('privacy.service.ppt_service.Presentation') as mock_pres, \
             patch('privacy.service.ppt_service.PPTService.process_text'), \
             patch('privacy.service.ppt_service.PPTService.process_images'), \
             patch('privacy.service.ppt_service.PPTService.process_tables'), \
             patch('privacy.service.ppt_service.PPTService.process_notes'), \
             patch('privacy.service.ppt_service.threading.Thread') as mock_thread, \
             patch('privacy.service.ppt_service.uuid.uuid4') as mock_uuid, \
             patch('privacy.service.ppt_service.request_id_var'), \
             patch('privacy.service.ppt_service.error_dict', {}):
            
            mock_uuid.return_value.hex = "test-request-id"
            mock_pres.return_value = mock_presentation
            
            # Mock Thread to run immediately
            def mock_thread_run(*args, **kwargs):
                mock_t = MagicMock()
                if 'target' in kwargs:
                    kwargs['target'](*kwargs.get('args', []))
                mock_t.start = MagicMock()
                mock_t.join = MagicMock()
                return mock_t
            
            mock_thread.side_effect = mock_thread_run
            
            result = PPTService.mask_ppt(mock_payload_minimal)
            
            assert result is not None
    
    def test_mask_ppt_with_portfolio_api_call(self, mock_payload):
        """Test mask_ppt calls API when portfolio is provided"""
        from privacy.service.ppt_service import PPTService
        
        mock_presentation = MagicMock()
        mock_slide = MagicMock()
        mock_slide.shapes = []
        mock_presentation.slides = [mock_slide]
        
        with patch('privacy.service.ppt_service.Presentation') as mock_pres, \
             patch('privacy.service.ppt_service.ApiCall.request') as mock_api, \
             patch('privacy.service.ppt_service.PPTService.process_text'), \
             patch('privacy.service.ppt_service.PPTService.process_images'), \
             patch('privacy.service.ppt_service.PPTService.process_tables'), \
             patch('privacy.service.ppt_service.PPTService.process_notes'), \
             patch('privacy.service.ppt_service.threading.Thread') as mock_thread, \
             patch('privacy.service.ppt_service.uuid.uuid4') as mock_uuid, \
             patch('privacy.service.ppt_service.request_id_var'), \
             patch('privacy.service.ppt_service.error_dict', {}):
            
            mock_uuid.return_value.hex = "test-request-id"
            mock_pres.return_value = mock_presentation
            mock_api.return_value = {"status": "success"}  # Non-None response
            
            # Mock Thread to run immediately
            def mock_thread_run(*args, **kwargs):
                mock_t = MagicMock()
                if 'target' in kwargs:
                    kwargs['target'](*kwargs.get('args', []))
                mock_t.start = MagicMock()
                mock_t.join = MagicMock()
                return mock_t
            
            mock_thread.side_effect = mock_thread_run
            
            result = PPTService.mask_ppt(mock_payload)
            
            # Verify API was called
            mock_api.assert_called_once()
            assert result is not None
    
    def test_mask_ppt_api_call_returns_none(self, mock_payload):
        """Test mask_ppt returns None when API call fails"""
        from privacy.service.ppt_service import PPTService
        
        with patch('privacy.service.ppt_service.ApiCall.request') as mock_api, \
             patch('privacy.service.ppt_service.request_id_var'), \
             patch('privacy.service.ppt_service.error_dict', {}):
            
            mock_api.return_value = None  # API call fails
            
            result = PPTService.mask_ppt(mock_payload)
            
            assert result is None
    
    def test_mask_ppt_exception_handling(self, mock_payload):
        """Test mask_ppt handles exceptions"""
        from privacy.service.ppt_service import PPTService
        
        with patch('privacy.service.ppt_service.Presentation', 
                  side_effect=Exception("PPT read error")), \
             patch('privacy.service.ppt_service.ApiCall.request') as mock_api, \
             patch('privacy.service.ppt_service.uuid.uuid4') as mock_uuid, \
             patch('privacy.service.ppt_service.request_id_var') as mock_req_id, \
             patch('privacy.service.ppt_service.error_dict', {}), \
             patch('privacy.service.ppt_service.log'):
            
            mock_uuid.return_value.hex = "test-request-id"
            mock_api.return_value = {"status": "success"}
            mock_req_id.get.return_value = "test-request-id"
            
            with pytest.raises(RuntimeError):
                PPTService.mask_ppt(mock_payload)
    
    def test_mask_ppt_multiple_slides(self, mock_payload_minimal):
        """Test mask_ppt processes multiple slides"""
        from privacy.service.ppt_service import PPTService
        from pptx.enum.shapes import MSO_SHAPE_TYPE
        
        # Create mock slides with different shapes
        mock_slide1 = MagicMock()
        mock_slide1.shapes = []
        
        mock_slide2 = MagicMock()
        mock_shape = MagicMock()
        mock_shape.shape_type = MSO_SHAPE_TYPE.PICTURE
        mock_slide2.shapes = [mock_shape]
        
        mock_presentation = MagicMock()
        mock_presentation.slides = [mock_slide1, mock_slide2]
        
        with patch('privacy.service.ppt_service.Presentation') as mock_pres, \
             patch('privacy.service.ppt_service.PPTService.process_text'), \
             patch('privacy.service.ppt_service.PPTService.process_images'), \
             patch('privacy.service.ppt_service.PPTService.process_tables'), \
             patch('privacy.service.ppt_service.PPTService.process_notes'), \
             patch('privacy.service.ppt_service.threading.Thread') as mock_thread, \
             patch('privacy.service.ppt_service.uuid.uuid4') as mock_uuid, \
             patch('privacy.service.ppt_service.request_id_var'), \
             patch('privacy.service.ppt_service.error_dict', {}):
            
            mock_uuid.return_value.hex = "test-request-id"
            mock_pres.return_value = mock_presentation
            
            # Mock Thread to run immediately
            def mock_thread_run(*args, **kwargs):
                mock_t = MagicMock()
                if 'target' in kwargs:
                    kwargs['target'](*kwargs.get('args', []))
                mock_t.start = MagicMock()
                mock_t.join = MagicMock()
                return mock_t
            
            mock_thread.side_effect = mock_thread_run
            
            result = PPTService.mask_ppt(mock_payload_minimal)
            
            assert result is not None


class TestPPTServiceIntegration:
    """Integration tests for PPTService"""
    
    def test_full_ppt_processing_workflow(self, mock_payload):
        """Test complete PPT processing workflow"""
        from privacy.service.ppt_service import PPTService
        from pptx.enum.shapes import MSO_SHAPE_TYPE
        
        # Setup complex slide structure
        mock_cell = MagicMock()
        mock_cell.text = "John Doe"
        
        mock_row = MagicMock()
        mock_row.cells = [mock_cell]
        
        mock_table = MagicMock()
        mock_table.rows = [mock_row]
        
        mock_text_shape = MagicMock()
        mock_text_shape.has_text_frame = True
        mock_text_shape.text = "Email: john@test.com"
        
        mock_table_shape = MagicMock()
        mock_table_shape.shape_type = MSO_SHAPE_TYPE.TABLE
        mock_table_shape.table = mock_table
        
        mock_slide = MagicMock()
        mock_slide.shapes = [mock_text_shape, mock_table_shape]
        mock_slide.notes_slide = None
        
        mock_presentation = MagicMock()
        mock_presentation.slides = [mock_slide]
        
        mock_entity = MagicMock()
        mock_entity.start = 0
        mock_entity.end = 4
        mock_entity.entity_type = "PERSON"
        
        with patch('privacy.service.ppt_service.Presentation') as mock_pres, \
             patch('privacy.service.ppt_service.ApiCall.request') as mock_api_call, \
             patch('privacy.service.ppt_service.PPTService.normalize_text_with_mapping') as mock_norm, \
             patch('privacy.service.ppt_service.TextPrivacy.text_analyze') as mock_analyze, \
             patch('privacy.service.ppt_service.anonymizer._remove_conflicts_and_get_text_manipulation_data') as mock_remove, \
             patch('privacy.service.ppt_service.anonymizer._merge_entities_with_whitespace_between') as mock_merge, \
             patch('privacy.service.ppt_service.threading.Thread') as mock_thread, \
             patch('privacy.service.ppt_service.uuid.uuid4') as mock_uuid, \
             patch('privacy.service.ppt_service.request_id_var'), \
             patch('privacy.service.ppt_service.error_dict', {}):
            
            mock_uuid.return_value.hex = "test-request-id"
            mock_pres.return_value = mock_presentation
            mock_api_call.return_value = {"status": "success"}  # Mock the API call return
            mock_norm.return_value = ("Email: john@test.com", list(range(20)), list(range(21)))
            mock_analyze.return_value = [mock_entity]
            mock_remove.return_value = [mock_entity]
            mock_merge.return_value = [mock_entity]
            
            # Mock Thread to run immediately
            def mock_thread_run(*args, **kwargs):
                mock_t = MagicMock()
                if 'target' in kwargs:
                    kwargs['target'](*kwargs.get('args', []))
                mock_t.start = MagicMock()
                mock_t.join = MagicMock()
                return mock_t
            
            mock_thread.side_effect = mock_thread_run
            
            result = PPTService.mask_ppt(mock_payload)
            
            assert result is not None
