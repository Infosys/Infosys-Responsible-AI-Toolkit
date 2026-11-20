"""
Tests for docs_service.py to cover missing lines
Targets lines: 59-82 (process_images exception handling), 137-139 (process_text exception handling)
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import io
from docx import Document
from privacy.service.docs_service import DOCService
from privacy.service.__init__ import AttributeDict


class TestProcessImagesExceptionHandling:
    """Test exception handling in process_images (lines 78-82)"""
    
    def test_process_images_with_exception(self):
        """Test process_images exception handling (lines 78-82)"""
        # Create a mock run object
        mock_run = MagicMock()
        mock_element = MagicMock()
        mock_run._element = mock_element
        
        # Mock xpath to raise an exception
        mock_element.xpath.side_effect = Exception("XPath failed")
        
        payload = {"portfolio": None, "account": None}
        uid = "test-uid-123"
        
        # Should catch exception and raise RuntimeError (lines 78-82)
        with pytest.raises(RuntimeError):
            DOCService.process_images(mock_run, payload, uid)
    
    def test_process_images_small_image_returns_none(self):
        """Test process_images returns None for small images (lines 59-60)"""
        # Create a mock run with small image
        mock_run = MagicMock()
        mock_element = MagicMock()
        mock_run._element = mock_element
        
        # Mock xpath to return a blip
        mock_blip = MagicMock()
        mock_blip.get.return_value = "rId1"
        mock_element.xpath.return_value = [mock_blip]
        
        # Mock the document part and image part
        mock_part = MagicMock()
        mock_image_part = MagicMock()
        mock_image_part.blob = b"small"  # Less than 700 bytes
        mock_part.related_parts = {"rId1": mock_image_part}
        mock_run.part = mock_part
        
        payload = {"portfolio": None, "account": None}
        uid = "test-uid-123"
        
        # Should return None for small images (lines 59-60)
        result = DOCService.process_images(mock_run, payload, uid)
        assert result is None


class TestProcessTextExceptionHandling:
    """Test exception handling in process_text (lines 137-139)"""
    
    def test_process_text_with_exception(self):
        """Test process_text exception handling (lines 137-139)"""
        # Create a mock paragraph
        mock_paragraph = MagicMock()
        mock_run = MagicMock()
        mock_run.text = "Test text"
        mock_paragraph.runs = [mock_run]
        
        payload = AttributeDict({
            "portfolio": None,
            "account": None,
            "exclusion": None,
            "pii_entities_to_be_redacted": None,
            "nlp": "spacy",
            "score_threshold": 0.5
        })
        uid = "test-uid-123"
        
        # Mock TextPrivacy.text_analyze to raise an exception
        with patch('privacy.service.docs_service.TextPrivacy.text_analyze') as mock_analyze:
            mock_analyze.side_effect = Exception("Text analysis failed")
            
            # Should catch exception and raise RuntimeError (lines 137-139)
            with pytest.raises(RuntimeError):
                DOCService.process_text(mock_paragraph, payload, uid)
    
    def test_process_text_with_portfolio(self):
        """Test process_text with portfolio details"""
        # Create a mock paragraph
        mock_paragraph = MagicMock()
        mock_run = MagicMock()
        mock_run.text = "Test text with portfolio"
        mock_paragraph.runs = [mock_run]
        
        payload = AttributeDict({
            "portfolio": "test-portfolio",
            "account": "test-account",
            "exclusion": "email,phone",
            "pii_entities_to_be_redacted": "PERSON,LOCATION",
            "nlp": "spacy",
            "score_threshold": 0.7
        })
        uid = "test-uid-456"
        
        with patch('privacy.service.docs_service.TextPrivacy.text_analyze') as mock_analyze, \
             patch('privacy.service.docs_service.anonymizer._remove_conflicts_and_get_text_manipulation_data') as mock_remove, \
             patch('privacy.service.docs_service.anonymizer._merge_entities_with_whitespace_between') as mock_merge:
            
            # Mock return values
            mock_analyze.return_value = []
            mock_remove.return_value = []
            mock_merge.return_value = []
            
            # Should process successfully with portfolio
            DOCService.process_text(mock_paragraph, payload, uid)
            
            # Verify text_analyze was called with acc_details
            assert mock_analyze.called
            call_args = mock_analyze.call_args
            assert call_args[1]['acc_name'] is not None
            assert call_args[1]['acc_name']['portfolio'] == "test-portfolio"
            assert call_args[1]['acc_name']['account'] == "test-account"


class TestMaskDocExceptionHandling:
    """Test exception handling in mask_doc"""
    
    def test_mask_doc_with_api_call_none_response(self):
        """Test mask_doc when API call returns None"""
        payload = {
            "portfolio": "test-portfolio",
            "account": "test-account",
            "file": MagicMock()
        }
        
        with patch('privacy.service.docs_service.ApiCall.request') as mock_api:
            mock_api.return_value = None
            
            # Should return None when API call returns None
            result = DOCService.mask_doc(payload)
            assert result is None
