"""
Comprehensive tests for preprocessing.py to increase coverage from 60% to 100%
Tests focus on missing lines: 57-76, 83-89, 93-97, 111-117, 130
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import itertools
from datasets import Dataset

from privacy.util.code_detect.ner.utils.preprocessing import (
    is_overlap,
    label_tokenized,
    add_special_toks,
    tokenize_and_label_batch,
    _get_chunking_step,
    _chunked_seq,
    chunk_inputs,
    chunk_dataset,
)


class TestIsOverlap:
    """Test is_overlap function"""
    
    def test_overlap_basic(self):
        """Test basic overlap detection"""
        assert is_overlap((0, 5), (3, 8)) is True
        
    def test_no_overlap(self):
        """Test non-overlapping spans"""
        assert is_overlap((0, 2), (5, 8)) is False
        
    def test_contained_span(self):
        """Test one span contained in another"""
        assert is_overlap((2, 4), (0, 8)) is True
        
    def test_same_span(self):
        """Test identical spans"""
        assert is_overlap((2, 4), (2, 4)) is True


class TestLabelTokenized:
    """Test label_tokenized function - covers lines 57-76"""
    
    def test_label_tokenized_basic(self):
        """Test basic labeling with single entity"""
        entry = {
            "text": "John Smith works here",
            "fragments": [{"category": "PERSON", "position": (0, 4)}],
            "offset_mapping": [(0, 4), (5, 10), (11, 16), (17, 21), (0, 0)],
        }
        label2id = {"O": 0, "B-PERSON": 1, "I-PERSON": 2}
        ignore_class = ["NOISE"]
        
        result = label_tokenized(
            entry, target_text="text", pii_column="fragments",
            label2id=label2id, ignore_class=ignore_class
        )
        
        assert result["labels"][0] == 1  # B-PERSON for first token
        assert result["labels"][1] == 0  # O for "Smith"
        
    def test_label_tokenized_with_ignored_class(self):
        """Test labeling with ignored classes"""
        entry = {
            "text": "Some content",
            "fragments": [{"category": "NOISE", "position": (0, 4)}],
            "offset_mapping": [(0, 4), (5, 12), (0, 0)],
        }
        label2id = {"O": 0, "B-NOISE": 1}
        ignore_class = ["NOISE"]
        
        result = label_tokenized(
            entry, target_text="text", pii_column="fragments",
            label2id=label2id, ignore_class=ignore_class
        )
        
        # Ignored classes should get label "O"
        assert result["labels"][0] == 0
        
    def test_label_tokenized_multiple_entities(self):
        """Test labeling with multiple entities and I- prefix"""
        entry = {
            "text": "John Smith is great",
            "fragments": [
                {"category": "PERSON", "position": (0, 10)},  # Covers "John Smith"
            ],
            "offset_mapping": [(0, 4), (5, 10), (11, 13), (14, 19), (0, 0)],
        }
        label2id = {"O": 0, "B-PERSON": 1, "I-PERSON": 2}
        ignore_class = []
        
        result = label_tokenized(
            entry, target_text="text", pii_column="fragments",
            label2id=label2id, ignore_class=ignore_class
        )
        
        assert result["labels"][0] == 1  # B-PERSON
        assert result["labels"][1] == 2  # I-PERSON (same entity span)
        assert result["labels"][2] == 0  # O for "is"
        
    def test_label_tokenized_offset_mapping_edge_case(self):
        """Test offset_mapping with (0,0) at the end"""
        entry = {
            "text": "test",
            "fragments": [],
            "offset_mapping": [(0, 4), (0, 0)],
        }
        label2id = {"O": 0}
        
        result = label_tokenized(
            entry, target_text="text", pii_column="fragments",
            label2id=label2id, ignore_class=[]
        )
        
        # The (0, 0) should be replaced with (len(content), len(content))
        assert result["offset_mapping"][-1] == (4, 4)


class TestAddSpecialToks:
    """Test add_special_toks function - covers lines 83-89"""
    
    def test_add_special_tokens_basic(self):
        """Test adding special tokens"""
        tokenizer = Mock()
        tokenizer.cls_token_id = 101
        tokenizer.sep_token_id = 102
        
        entry = {
            "text": "hello world",
            "input_ids": [1, 2, 3],
            "attention_mask": [1, 1, 1],
            "offset_mapping": [(0, 5), (6, 11)],
            "labels": [0, 1],
        }
        
        result = add_special_toks(entry, "text", tokenizer)
        
        assert result["input_ids"] == [101, 1, 2, 3, 102]
        assert result["attention_mask"] == [1, 1, 1, 1, 1]
        assert result["offset_mapping"] == [(0, 0), (0, 5), (6, 11), (11, 11)]
        assert result["labels"] == [-100, 0, 1, -100]
        
    def test_add_special_toks_empty_input(self):
        """Test with empty input"""
        tokenizer = Mock()
        tokenizer.cls_token_id = 101
        tokenizer.sep_token_id = 102
        
        entry = {
            "text": "",
            "input_ids": [],
            "attention_mask": [],
            "offset_mapping": [],
            "labels": [],
        }
        
        result = add_special_toks(entry, "text", tokenizer)
        
        assert result["input_ids"] == [101, 102]
        assert result["attention_mask"] == [1, 1]
        assert len(result["labels"]) == 2
        assert result["labels"] == [-100, -100]


class TestGetChunkingStep:
    """Test _get_chunking_step function - covers lines 93-97"""
    
    def test_chunking_step_no_overlap(self):
        """Test chunking step with no overlap"""
        step = _get_chunking_step(100, 0)
        assert step == 100
        
    def test_chunking_step_with_overlap_freq_half(self):
        """Test chunking step with overlap frequency of 2"""
        step = _get_chunking_step(100, 2)
        assert step == 50
        
    def test_chunking_step_with_overlap_freq_three(self):
        """Test chunking step with overlap frequency of 3"""
        step = _get_chunking_step(100, 3)
        assert step == 33
        
    def test_chunking_step_with_overlap_freq_one(self):
        """Test chunking step with overlap frequency of 1"""
        step = _get_chunking_step(100, 1)
        assert step == 50


class TestChunkedSeq:
    """Test _chunked_seq generator function"""
    
    def test_chunked_seq_basic(self):
        """Test basic sequence chunking"""
        seq = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        chunks = list(_chunked_seq(seq, 3, overlap_freq=0))
        assert len(chunks) >= 3
        
    def test_chunked_seq_with_overlap(self):
        """Test sequence chunking with overlap"""
        seq = list(range(20))
        chunks = list(_chunked_seq(seq, 10, overlap_freq=2))
        assert len(chunks) > 1
        
    def test_chunked_seq_empty(self):
        """Test empty sequence"""
        chunks = list(_chunked_seq([], 5))
        # Empty sequence returns empty list (no iterations)
        assert len(chunks) == 0


class TestTokenizeAndLabelBatch:
    """Test tokenize_and_label_batch function - covers lines 57-76"""
    
    def test_tokenize_and_label_batch_basic(self):
        """Test basic batch tokenization and labeling"""
        tokenizer = Mock()
        tokenizer.encode_plus.return_value = {
            "input_ids": [1, 2, 3],
            "attention_mask": [1, 1, 1],
            "offset_mapping": [(0, 4), (5, 10), (11, 16)],
        }
        tokenizer.cls_token_id = 101
        tokenizer.sep_token_id = 102
        
        entries = {
            "text": ["hello world"],
            "fragments": [[]],
        }
        
        label2id = {"O": 0, "B-PERSON": 1}
        ignore_class = []
        
        result = tokenize_and_label_batch(
            entries, tokenizer, target_text="text", pii_column="fragments",
            label2id=label2id, ignore_class=ignore_class
        )
        
        assert "input_ids" in result
        assert "attention_mask" in result
        assert "offset_mapping" in result
        assert "labels" in result
        assert len(result["input_ids"]) == 1
        
    def test_tokenize_and_label_batch_multiple_entries(self):
        """Test batch tokenization with multiple entries"""
        tokenizer = Mock()
        tokenizer.encode_plus.return_value = {
            "input_ids": [1, 2, 3],
            "attention_mask": [1, 1, 1],
            "offset_mapping": [(0, 4), (5, 10), (11, 16)],
        }
        tokenizer.cls_token_id = 101
        tokenizer.sep_token_id = 102
        
        entries = {
            "text": ["hello world", "test case"],
            "fragments": [[], []],
        }
        
        label2id = {"O": 0}
        ignore_class = []
        
        result = tokenize_and_label_batch(
            entries, tokenizer, target_text="text", pii_column="fragments",
            label2id=label2id, ignore_class=ignore_class
        )
        
        assert len(result["input_ids"]) == 2
        assert len(result["labels"]) == 2
        
    def test_tokenize_and_label_batch_with_entities(self):
        """Test batch tokenization with actual entities"""
        tokenizer = Mock()
        tokenizer.encode_plus.return_value = {
            "input_ids": [1, 2, 3],
            "attention_mask": [1, 1, 1],
            "offset_mapping": [(0, 4), (5, 10), (11, 16)],
        }
        tokenizer.cls_token_id = 101
        tokenizer.sep_token_id = 102
        
        entries = {
            "text": ["John Smith works"],
            "fragments": [[{"category": "PERSON", "position": (0, 4)}]],
        }
        
        label2id = {"O": 0, "B-PERSON": 1, "I-PERSON": 2}
        ignore_class = []
        
        result = tokenize_and_label_batch(
            entries, tokenizer, target_text="text", pii_column="fragments",
            label2id=label2id, ignore_class=ignore_class
        )
        
        assert len(result["labels"]) == 1
        assert result["labels"][0][0] == -100  # CLS token
        assert result["labels"][0][-1] == -100  # SEP token


class TestChunkInputs:
    """Test chunk_inputs function - covers lines 111-117"""
    
    def test_chunk_inputs_basic(self):
        """Test basic input chunking"""
        tokenizer = Mock()
        tokenizer.model_max_length = 10
        
        result = chunk_inputs(
            input_ids=[1, 2, 3, 4, 5],
            attention_mask=[1, 1, 1, 1, 1],
            labels=[0, 1, 0, 1, 0],
            id="test_1",
            tokenizer=tokenizer,
            max_length=10,
            overlap_freq=0,
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert "input_ids" in result[0]
        assert "chunk_id" in result[0]
        assert result[0]["id"] == "test_1"
        
    def test_chunk_inputs_with_overlap(self):
        """Test chunking with overlap frequency"""
        tokenizer = Mock()
        tokenizer.model_max_length = 5
        
        result = chunk_inputs(
            input_ids=list(range(20)),
            attention_mask=[1] * 20,
            labels=[0] * 20,
            id="test_2",
            tokenizer=tokenizer,
            max_length=5,
            overlap_freq=2,
        )
        
        assert len(result) > 0
        # Verify chunk_id increments
        chunk_ids = [chunk["chunk_id"] for chunk in result]
        assert chunk_ids == sorted(chunk_ids)
        
    def test_chunk_inputs_single_chunk(self):
        """Test when data fits in single chunk"""
        tokenizer = Mock()
        tokenizer.model_max_length = 100
        
        result = chunk_inputs(
            input_ids=[1, 2, 3],
            attention_mask=[1, 1, 1],
            labels=[0, 1, 0],
            id="test_3",
            tokenizer=tokenizer,
            max_length=100,
            overlap_freq=0,
        )
        
        assert len(result) >= 1


class TestChunkDataset:
    """Test chunk_dataset function - covers line 130"""
    
    @patch('privacy.util.code_detect.ner.utils.preprocessing.tqdm')
    def test_chunk_dataset_basic(self, mock_tqdm):
        """Test basic dataset chunking"""
        # Mock tqdm to return list as-is
        mock_tqdm.side_effect = lambda x: x
        
        tokenizer = Mock()
        tokenizer.model_max_length = 10
        
        # Create a simple mock dataset
        mock_dataset = [
            {
                "input_ids": [1, 2, 3],
                "attention_mask": [1, 1, 1],
                "labels": [0, 1, 0],
                "id": "doc_1",
            },
            {
                "input_ids": [4, 5, 6],
                "attention_mask": [1, 1, 1],
                "labels": [0, 0, 1],
                "id": "doc_2",
            },
        ]
        
        # Mock the Dataset constructor to verify it's called
        with patch('privacy.util.code_detect.ner.utils.preprocessing.Dataset.from_list') as mock_from_list:
            mock_from_list.return_value = Mock()
            
            result = chunk_dataset(mock_dataset, tokenizer, overlap_freq=0)
            
            # Verify from_list was called with a list
            assert mock_from_list.called
            call_args = mock_from_list.call_args
            assert isinstance(call_args[0][0], list)
            
    @patch('privacy.util.code_detect.ner.utils.preprocessing.tqdm')
    def test_chunk_dataset_with_overlap(self, mock_tqdm):
        """Test dataset chunking with overlap"""
        mock_tqdm.side_effect = lambda x: x
        
        tokenizer = Mock()
        tokenizer.model_max_length = 5
        
        mock_dataset = [
            {
                "input_ids": list(range(20)),
                "attention_mask": [1] * 20,
                "labels": [0] * 20,
                "id": "doc_1",
            },
        ]
        
        with patch('privacy.util.code_detect.ner.utils.preprocessing.Dataset.from_list') as mock_from_list:
            mock_from_list.return_value = Mock()
            
            result = chunk_dataset(mock_dataset, tokenizer, overlap_freq=2)
            
            assert mock_from_list.called
            # Verify that from_list was called with chunked data
            call_args = mock_from_list.call_args[0][0]
            assert len(call_args) > 0
