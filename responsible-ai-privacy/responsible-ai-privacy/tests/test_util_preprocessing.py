"""Tests for preprocessing utility functions"""
import pytest
from unittest.mock import Mock, MagicMock


class TestIsOverlap:
    '''Test is_overlap function'''
    
    def test_is_overlap_overlapping_spans(self):
        '''Test overlapping spans'''
        from privacy.util.code_detect.ner.utils.preprocessing import is_overlap
        
        assert is_overlap((5, 10), (8, 15)) == True
        assert is_overlap((10, 20), (5, 12)) == True
    
    def test_is_overlap_non_overlapping_spans(self):
        '''Test non-overlapping spans'''
        from privacy.util.code_detect.ner.utils.preprocessing import is_overlap
        
        assert is_overlap((5, 10), (11, 15)) == False
        assert is_overlap((20, 30), (5, 10)) == False
    
    def test_is_overlap_adjacent_spans(self):
        '''Test adjacent spans (touching but not overlapping)'''
        from privacy.util.code_detect.ner.utils.preprocessing import is_overlap
        
        assert is_overlap((5, 10), (10, 15)) == False
    
    def test_is_overlap_nested_spans(self):
        '''Test nested spans'''
        from privacy.util.code_detect.ner.utils.preprocessing import is_overlap
        
        assert is_overlap((5, 20), (10, 15)) == True
        assert is_overlap((10, 15), (5, 20)) == True
    
    def test_is_overlap_same_spans(self):
        '''Test identical spans'''
        from privacy.util.code_detect.ner.utils.preprocessing import is_overlap
        
        assert is_overlap((5, 10), (5, 10)) == True
    
    def test_is_overlap_reversed_span(self):
        '''Test reversed spans (max, min)'''
        from privacy.util.code_detect.ner.utils.preprocessing import is_overlap
        
        assert is_overlap((10, 5), (8, 15)) == True
        assert is_overlap((5, 10), (15, 8)) == True
    
    def test_is_overlap_single_point(self):
        '''Test single point spans'''
        from privacy.util.code_detect.ner.utils.preprocessing import is_overlap
        
        assert is_overlap((5, 5), (5, 10)) == False
        assert is_overlap((5, 10), (10, 10)) == False


class TestLabelTokenized:
    '''Test label_tokenized function'''
    
    def test_label_tokenized_no_pii(self):
        '''Test labeling with no PII entities'''
        from privacy.util.code_detect.ner.utils.preprocessing import label_tokenized
        
        entry = {
            'text': 'Hello world',
            'fragments': [],
            'offset_mapping': [(0, 5), (6, 11)]
        }
        label2id = {'O': 0}
        
        result = label_tokenized(entry, label2id=label2id, ignore_class=[])
        
        assert result['labels'] == [0, 0]
    
    def test_label_tokenized_single_entity(self):
        '''Test labeling with single PII entity'''
        from privacy.util.code_detect.ner.utils.preprocessing import label_tokenized
        
        entry = {
            'text': 'John Smith works here',
            'fragments': [{'category': 'PERSON', 'position': [0, 10]}],
            'offset_mapping': [(0, 4), (5, 10), (11, 16), (17, 21)]
        }
        label2id = {'O': 0, 'B-PERSON': 1, 'I-PERSON': 2}
        
        result = label_tokenized(entry, label2id=label2id, ignore_class=[])
        
        assert result['labels'][0] == 1  # B-PERSON
        assert result['labels'][1] == 2  # I-PERSON
    
    def test_label_tokenized_ignored_category(self):
        '''Test labeling with ignored category'''
        from privacy.util.code_detect.ner.utils.preprocessing import label_tokenized
        
        entry = {
            'text': 'John Smith',
            'fragments': [{'category': 'IGNORE', 'position': [0, 10]}],
            'offset_mapping': [(0, 4), (5, 10)]
        }
        label2id = {'O': 0, 'B-IGNORE': 1}
        
        result = label_tokenized(entry, label2id=label2id, ignore_class=['IGNORE'])
        
        assert result['labels'] == [0, 0]  # All O labels
    
    def test_label_tokenized_fixes_last_offset(self):
        '''Test fixing last offset mapping'''
        from privacy.util.code_detect.ner.utils.preprocessing import label_tokenized
        
        entry = {
            'text': 'Hello world',
            'fragments': [],
            'offset_mapping': [(0, 5), (6, 11), (0, 0)]
        }
        label2id = {'O': 0}
        
        result = label_tokenized(entry, label2id=label2id, ignore_class=[])
        
        assert result['offset_mapping'][-1] == (11, 11)


class TestAddSpecialToks:
    '''Test add_special_toks function'''
    
    def test_add_special_toks_adds_cls_sep(self):
        '''Test adding CLS and SEP tokens'''
        from privacy.util.code_detect.ner.utils.preprocessing import add_special_toks
        
        tokenizer = Mock()
        tokenizer.cls_token_id = 101
        tokenizer.sep_token_id = 102
        
        entry = {
            'text': 'Hello',
            'input_ids': [1000, 2000],
            'attention_mask': [1, 1],
            'offset_mapping': [(0, 2), (3, 5)],
            'labels': [0, 0]
        }
        
        result = add_special_toks(entry, 'text', tokenizer)
        
        assert result['input_ids'] == [101, 1000, 2000, 102]
        assert result['attention_mask'] == [1, 1, 1, 1]
        assert result['labels'] == [-100, 0, 0, -100]
    
    def test_add_special_toks_offset_mapping(self):
        '''Test offset mapping with special tokens'''
        from privacy.util.code_detect.ner.utils.preprocessing import add_special_toks
        
        tokenizer = Mock()
        tokenizer.cls_token_id = 101
        tokenizer.sep_token_id = 102
        
        entry = {
            'text': 'Test',
            'input_ids': [1000],
            'attention_mask': [1],
            'offset_mapping': [(0, 4)],
            'labels': [0]
        }
        
        result = add_special_toks(entry, 'text', tokenizer)
        
        assert result['offset_mapping'] == [(0, 0), (0, 4), (4, 4)]
    
    def test_add_special_toks_empty_input(self):
        '''Test with empty input'''
        from privacy.util.code_detect.ner.utils.preprocessing import add_special_toks
        
        tokenizer = Mock()
        tokenizer.cls_token_id = 101
        tokenizer.sep_token_id = 102
        
        entry = {
            'text': '',
            'input_ids': [],
            'attention_mask': [],
            'offset_mapping': [],
            'labels': []
        }
        
        result = add_special_toks(entry, 'text', tokenizer)
        
        assert result['input_ids'] == [101, 102]
        assert result['attention_mask'] == [1, 1]
        assert result['labels'] == [-100, -100]
