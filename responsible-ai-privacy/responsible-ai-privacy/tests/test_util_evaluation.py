"""
Test suite for privacy utility functions - code_detect evaluation module.
Tests utility functions without heavy ML dependencies.
"""

import pytest
import json
from src.privacy.util.code_detect.utils.evaluation import (
    load_json,
    overlapped,
    compare_intervals,
    recall_precision,
    recall_precision_all_tags,
    evaluate_pii,
    evaluate_pii_ds
)


class TestLoadJson:
    """Test the load_json utility function."""
    
    def test_load_json_valid_list(self):
        """Test loading valid JSON list."""
        json_str = '[{"tag": "EMAIL", "start": 0, "end": 10}]'
        result = load_json(json_str)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["tag"] == "EMAIL"
    
    def test_load_json_invalid(self):
        """Test loading invalid JSON returns empty list."""
        result = load_json("not valid json")
        assert result == []
    
    def test_load_json_empty_string(self):
        """Test loading empty string."""
        result = load_json("")
        assert result == []
    
    def test_load_json_empty_list(self):
        """Test loading empty JSON list."""
        result = load_json("[]")
        assert result == []


class TestOverlapped:
    """Test the overlapped interval comparison function."""
    
    def test_overlapped_fully_contained(self):
        """Test when interval a is fully inside b."""
        # overlap = 5 units, ref_overlap = 5/20 = 0.25, pred_overlap = 5/5 = 1.0
        # Since ref_overlap (0.25) < alpha (0.8), this is False
        assert overlapped((5, 10), (0, 20), 0.8, 0.8) is False
        # With lower threshold, it should pass
        assert overlapped((5, 10), (0, 20), 0.2, 0.8) is True
    
    def test_overlapped_partial_overlap(self):
        """Test partial overlap meeting threshold."""
        # a=(0,10), b=(5,15) -> overlap is (5,10) = 5 units
        # ref_overlap = 5/10 = 0.5, pred_overlap = 5/10 = 0.5
        assert overlapped((0, 10), (5, 15), 0.4, 0.4) is True
        assert overlapped((0, 10), (5, 15), 0.6, 0.6) is False
    
    def test_overlapped_no_overlap(self):
        """Test no overlap."""
        assert overlapped((0, 5), (10, 15), 0.8, 0.8) is False
    
    def test_overlapped_touching_boundaries(self):
        """Test touching boundaries (no actual overlap)."""
        assert overlapped((0, 5), (5, 10), 0.8, 0.8) is False
    
    def test_overlapped_exact_match(self):
        """Test exact matching intervals."""
        assert overlapped((5, 10), (5, 10), 0.8, 0.8) is True
    
    def test_overlapped_custom_thresholds(self):
        """Test with custom alpha and beta thresholds."""
        # (0, 10) and (8, 12) overlap in (8, 10) = 2 units
        # ref_overlap = 2/4 = 0.5, pred_overlap = 2/10 = 0.2
        assert overlapped((0, 10), (8, 12), 0.1, 0.1) is True
        # alpha=0.3 < ref_overlap=0.5, beta=0.1 < pred_overlap=0.2, so True
        assert overlapped((0, 10), (8, 12), 0.3, 0.1) is True
        # But if beta=0.3 > pred_overlap=0.2, then False
        assert overlapped((0, 10), (8, 12), 0.1, 0.3) is False


class TestCompareIntervals:
    """Test the compare_intervals function."""
    
    def test_compare_intervals_perfect_match(self):
        """Test with perfectly matching intervals."""
        references = [(0, 10), (20, 30)]
        predictions = [(0, 10), (20, 30)]
        scores, detected = compare_intervals(references, predictions, 0.8, 0.8)
        assert scores["TP"] == 2
        assert scores["FP"] == 0
        assert scores["FN"] == 0
        assert len(detected) == 2
    
    def test_compare_intervals_no_match(self):
        """Test with no matching intervals."""
        references = [(0, 10)]
        predictions = [(50, 60)]
        scores, detected = compare_intervals(references, predictions, 0.8, 0.8)
        assert scores["TP"] == 0
        assert scores["FP"] == 1
        assert scores["FN"] == 1
        assert len(detected) == 0
    
    def test_compare_intervals_partial_match(self):
        """Test with some matching and some not."""
        references = [(0, 10), (20, 30), (40, 50)]
        # (1,9) vs (0,10): overlap=8, ref_overlap=8/10=0.8, pred_overlap=8/8=1.0 -> matches!
        predictions = [(0, 9), (100, 110)]
        scores, detected = compare_intervals(references, predictions, 0.8, 0.8)
        assert scores["TP"] == 1  # (0,9) matches (0,10)
        assert scores["FP"] == 1  # (100,110) is false positive
        assert scores["FN"] == 2  # (20,30) and (40,50) not detected
    
    def test_compare_intervals_empty_references(self):
        """Test with empty reference list."""
        references = []
        predictions = [(0, 10)]
        scores, detected = compare_intervals(references, predictions, 0.8, 0.8)
        assert scores["TP"] == 0
        assert scores["FP"] == 1
        assert scores["FN"] == 0
    
    def test_compare_intervals_empty_predictions(self):
        """Test with empty prediction list."""
        references = [(0, 10)]
        predictions = []
        scores, detected = compare_intervals(references, predictions, 0.8, 0.8)
        assert scores["TP"] == 0
        assert scores["FP"] == 0
        assert scores["FN"] == 1
    
    def test_compare_intervals_with_low_threshold(self):
        """Test with very low overlap threshold."""
        references = [(0, 10)]
        predictions = [(9, 20)]
        scores, detected = compare_intervals(references, predictions, 0.0, 0.0)
        assert scores["TP"] == 1  # Should match with 0 threshold


class TestRecallPrecision:
    """Test recall and precision calculation functions."""
    
    def test_recall_precision_perfect_scores(self):
        """Test with perfect TP, no FP or FN."""
        metrics_dict = {
            'EMAIL': {'TP': 10, 'FN': 0, 'FP': 0},
            'IP_ADDRESS': {'TP': 5, 'FN': 0, 'FP': 0},
            'KEY': {'TP': 3, 'FN': 0, 'FP': 0}
        }
        result = recall_precision(metrics_dict)
        assert result['EMAIL']['recall'] == 1.0
        assert result['EMAIL']['precision'] == 1.0
        assert result['IP_ADDRESS']['recall'] == 1.0
        assert result['KEY']['precision'] == 1.0
    
    def test_recall_precision_with_errors(self):
        """Test with false positives and false negatives."""
        metrics_dict = {
            'EMAIL': {'TP': 8, 'FN': 2, 'FP': 1},
            'IP_ADDRESS': {'TP': 4, 'FN': 1, 'FP': 2},
            'KEY': {'TP': 0, 'FN': 5, 'FP': 3}
        }
        result = recall_precision(metrics_dict)
        
        # EMAIL: recall = 8/(8+2) = 0.8, precision = 8/(8+1) = 0.889
        assert abs(result['EMAIL']['recall'] - 0.8) < 0.01
        assert abs(result['EMAIL']['precision'] - 0.889) < 0.01
        
        # IP_ADDRESS: recall = 4/(4+1) = 0.8, precision = 4/(4+2) = 0.667
        assert abs(result['IP_ADDRESS']['recall'] - 0.8) < 0.01
        assert abs(result['IP_ADDRESS']['precision'] - 0.667) < 0.01
        
        # KEY: recall = 0/(0+5) = 0, precision = 0/(0+3) = 0
        assert result['KEY']['recall'] == 0
        assert result['KEY']['precision'] == 0
    
    def test_recall_precision_no_annotations(self):
        """Test with no annotations (all zeros)."""
        metrics_dict = {
            'EMAIL': {'TP': 0, 'FN': 0, 'FP': 0},
            'IP_ADDRESS': {'TP': 0, 'FN': 0, 'FP': 0},
            'KEY': {'TP': 0, 'FN': 0, 'FP': 0}
        }
        result = recall_precision(metrics_dict)
        # When no annotations, score should be 1.0
        assert result['EMAIL']['recall'] == 1.0
        assert result['EMAIL']['precision'] == 1.0
    
    def test_recall_precision_all_tags_perfect(self):
        """Test recall_precision_all_tags with perfect scores."""
        metrics_dict = {
            'EMAIL': {'TP': 10, 'FN': 0, 'FP': 0},
            'IP_ADDRESS': {'TP': 5, 'FN': 0, 'FP': 0},
            'KEY': {'TP': 3, 'FN': 0, 'FP': 0}
        }
        result = recall_precision_all_tags(metrics_dict)
        # Total TP=18, FN=0, FP=0
        assert result['recall'] == 1.0
        assert result['precision'] == 1.0
    
    def test_recall_precision_all_tags_with_errors(self):
        """Test recall_precision_all_tags with errors."""
        metrics_dict = {
            'EMAIL': {'TP': 8, 'FN': 2, 'FP': 1},
            'IP_ADDRESS': {'TP': 4, 'FN': 1, 'FP': 2},
            'KEY': {'TP': 2, 'FN': 3, 'FP': 1}
        }
        result = recall_precision_all_tags(metrics_dict)
        # Total TP=14, FN=6, FP=4
        # recall = 14/(14+6) = 0.7
        # precision = 14/(14+4) = 0.778
        assert abs(result['recall'] - 0.7) < 0.01
        assert abs(result['precision'] - 0.778) < 0.01
    
    def test_recall_precision_all_tags_zero_division(self):
        """Test when division by zero would occur."""
        metrics_dict = {
            'EMAIL': {'TP': 0, 'FN': 0, 'FP': 1},
            'IP_ADDRESS': {'TP': 0, 'FN': 0, 'FP': 0},
            'KEY': {'TP': 0, 'FN': 0, 'FP': 0}
        }
        result = recall_precision_all_tags(metrics_dict)
        assert result['recall'] == 0
        assert result['precision'] == 0


class TestEvaluatePii:
    """Test the evaluate_pii function."""
    
    def test_evaluate_pii_single_tag(self):
        """Test evaluation with single tag type."""
        references = [
            {'tag': 'EMAIL', 'start': 0, 'end': 20},
            {'tag': 'EMAIL', 'start': 30, 'end': 50}
        ]
        predictions = [
            {'tag': 'EMAIL', 'start': 1, 'end': 19},
            {'tag': 'EMAIL', 'start': 31, 'end': 49}
        ]
        result = evaluate_pii(references, predictions, 0.8, 0.8)
        
        assert 'EMAIL' in result
        assert result['EMAIL']['TP'] == 2
        assert result['EMAIL']['FP'] == 0
        assert result['EMAIL']['FN'] == 0
    
    def test_evaluate_pii_multiple_tags(self):
        """Test evaluation with multiple tag types."""
        references = [
            {'tag': 'EMAIL', 'start': 0, 'end': 20},
            {'tag': 'IP_ADDRESS', 'start': 30, 'end': 45},
            {'tag': 'KEY', 'start': 50, 'end': 82}
        ]
        predictions = [
            {'tag': 'EMAIL', 'start': 0, 'end': 20},
            {'tag': 'IP_ADDRESS', 'start': 30, 'end': 45}
            # KEY is missing - will be FN
        ]
        result = evaluate_pii(references, predictions, 0.8, 0.8)
        
        assert result['EMAIL']['TP'] == 1
        assert result['EMAIL']['FN'] == 0
        assert result['IP_ADDRESS']['TP'] == 1
        assert result['KEY']['TP'] == 0
        assert result['KEY']['FN'] == 1
    
    def test_evaluate_pii_false_positives(self):
        """Test with false positive predictions."""
        references = [
            {'tag': 'EMAIL', 'start': 0, 'end': 20}
        ]
        predictions = [
            {'tag': 'EMAIL', 'start': 0, 'end': 20},
            {'tag': 'EMAIL', 'start': 100, 'end': 120},  # False positive
            {'tag': 'KEY', 'start': 200, 'end': 232}  # False positive
        ]
        result = evaluate_pii(references, predictions, 0.8, 0.8)
        
        assert result['EMAIL']['TP'] == 1
        assert result['EMAIL']['FP'] == 1
        assert result['KEY']['FP'] == 1
    
    def test_evaluate_pii_empty_predictions(self):
        """Test with no predictions."""
        references = [
            {'tag': 'EMAIL', 'start': 0, 'end': 20},
            {'tag': 'KEY', 'start': 30, 'end': 62}
        ]
        predictions = []
        result = evaluate_pii(references, predictions, 0.8, 0.8)
        
        assert result['EMAIL']['FN'] == 1
        assert result['KEY']['FN'] == 1
        assert result['EMAIL']['TP'] == 0
        assert result['KEY']['TP'] == 0
    
    def test_evaluate_pii_empty_references(self):
        """Test with no references (all predictions are FP)."""
        references = []
        predictions = [
            {'tag': 'EMAIL', 'start': 0, 'end': 20},
            {'tag': 'KEY', 'start': 30, 'end': 62}
        ]
        result = evaluate_pii(references, predictions, 0.8, 0.8)
        
        assert result['EMAIL']['FP'] == 1
        assert result['KEY']['FP'] == 1
        assert result['EMAIL']['FN'] == 0


class TestEvaluatePiiDs:
    """Test the evaluate_pii_ds function for dataset evaluation."""
    
    def test_evaluate_pii_ds_single_sample(self):
        """Test dataset evaluation with single sample."""
        dataset = [{
            'secrets': '[{"tag": "EMAIL", "start": 0, "end": 20}]',
            'pii': '[{"tag": "EMAIL", "start": 0, "end": 20}]'
        }]
        
        metrics, metrics_dict = evaluate_pii_ds(dataset, overall_score=False)
        
        assert metrics['EMAIL']['recall'] == 1.0
        assert metrics['EMAIL']['precision'] == 1.0
    
    def test_evaluate_pii_ds_multiple_samples(self):
        """Test dataset evaluation with multiple samples."""
        dataset = [
            {
                'secrets': '[{"tag": "EMAIL", "start": 0, "end": 20}]',
                'pii': '[{"tag": "EMAIL", "start": 0, "end": 20}]'
            },
            {
                'secrets': '[{"tag": "KEY", "start": 0, "end": 32}]',
                'pii': '[{"tag": "KEY", "start": 0, "end": 32}]'
            }
        ]
        
        metrics, metrics_dict = evaluate_pii_ds(dataset, overall_score=False)
        
        assert metrics['EMAIL']['recall'] == 1.0
        assert metrics['KEY']['recall'] == 1.0
    
    def test_evaluate_pii_ds_overall_score(self):
        """Test dataset evaluation with overall score enabled."""
        dataset = [
            {
                'secrets': '[{"tag": "EMAIL", "start": 0, "end": 20}]',
                'pii': '[{"tag": "EMAIL", "start": 0, "end": 20}]'
            }
        ]
        
        metrics, metrics_dict = evaluate_pii_ds(dataset, overall_score=True)
        
        assert 'recall' in metrics
        assert 'precision' in metrics
        assert metrics['recall'] == 1.0
        assert metrics['precision'] == 1.0
    
    def test_evaluate_pii_ds_custom_columns(self):
        """Test dataset evaluation with custom column names."""
        dataset = [{
            'ground_truth': '[{"tag": "EMAIL", "start": 0, "end": 20}]',
            'predictions': '[{"tag": "EMAIL", "start": 0, "end": 20}]'
        }]
        
        metrics, metrics_dict = evaluate_pii_ds(
            dataset,
            pred_column='predictions',
            ref_column='ground_truth'
        )
        
        assert metrics['EMAIL']['recall'] == 1.0
    
    def test_evaluate_pii_ds_mixed_results(self):
        """Test dataset evaluation with mixed TP/FP/FN."""
        dataset = [
            {
                'secrets': '[{"tag": "EMAIL", "start": 0, "end": 20}]',
                'pii': '[{"tag": "EMAIL", "start": 0, "end": 20}]'  # TP
            },
            {
                'secrets': '[{"tag": "EMAIL", "start": 0, "end": 20}]',
                'pii': '[]'  # FN
            },
            {
                'secrets': '[]',
                'pii': '[{"tag": "EMAIL", "start": 0, "end": 20}]'  # FP
            }
        ]
        
        metrics, metrics_dict = evaluate_pii_ds(dataset)
        
        # TP=1, FN=1, FP=1 for EMAIL
        # recall = 1/(1+1) = 0.5, precision = 1/(1+1) = 0.5
        assert abs(metrics['EMAIL']['recall'] - 0.5) < 0.01
        assert abs(metrics['EMAIL']['precision'] - 0.5) < 0.01
    
    def test_recall_precision_all_tags_with_zero_total(self):
        """Test recall_precision with zero total for a tag (line 61 - else branch that sets metrics[tag] to {'recall': 1.0, 'precision': 1.0})."""
        from src.privacy.util.code_detect.utils.evaluation import recall_precision
        
        metrics_dict = {
            'EMAIL': {
                'TP': 0,
                'FN': 0,
                'FP': 0
            },
            'IP_ADDRESS': {
                'TP': 1,
                'FN': 1,
                'FP': 1
            },
            'KEY': {
                'TP': 2,
                'FN': 0,
                'FP': 0
            }
        }
        
        metrics = recall_precision(metrics_dict)
        
        # Should hit line 61-62: else branch when total is 0 for EMAIL
        # metrics[tag] = {'recall': 1.0, 'precision': 1.0}
        assert metrics['EMAIL'] == {'recall': 1.0, 'precision': 1.0}
        # Other tags should have calculated values
        assert 'recall' in metrics['IP_ADDRESS']
        assert 'precision' in metrics['IP_ADDRESS']
    
    def test_recall_precision_division_by_zero_check(self):
        """Test recall_precision division by zero check (line 55 - if branch checking TP+FN or TP+FP is zero)."""
        from src.privacy.util.code_detect.utils.evaluation import recall_precision
        
        # Case 1: TP=0, FN=0 (but FP>0) - should trigger line 55
        metrics_dict1 = {
            'EMAIL': {
                'TP': 0,
                'FN': 0,
                'FP': 5  # Only FP, no true positives or false negatives
            },
            'IP_ADDRESS': {
                'TP': 1,
                'FN': 1,
                'FP': 1
            },
            'KEY': {
                'TP': 1,
                'FN': 1,
                'FP': 1
            }
        }
        
        metrics = recall_precision(metrics_dict1)
        
        # Line 55-56: Should set recall=0, precision=0 when TP+FN=0
        assert metrics['EMAIL'] == {'recall': 0, 'precision': 0}
    
    def test_recall_precision_division_by_zero_fp_case(self):
        """Test recall_precision when TP+FP is zero (line 55 - second condition)."""
        from src.privacy.util.code_detect.utils.evaluation import recall_precision
        
        # Case 2: TP=0, FP=0 (but FN>0) - should trigger line 55
        metrics_dict2 = {
            'EMAIL': {
                'TP': 0,
                'FN': 5,  # Only FN, no true positives or false positives
                'FP': 0
            },
            'IP_ADDRESS': {
                'TP': 1,
                'FN': 1,
                'FP': 1
            },
            'KEY': {
                'TP': 1,
                'FN': 1,
                'FP': 1
            }
        }
        
        metrics = recall_precision(metrics_dict2)
        
        # Line 55-56: Should set recall=0, precision=0 when TP+FP=0
        assert metrics['EMAIL'] == {'recall': 0, 'precision': 0}
