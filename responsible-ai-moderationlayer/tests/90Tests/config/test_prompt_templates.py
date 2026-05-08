"""
Tests for config.prompt_templates module.
Tests prompt template constants and configurations.
"""

import pytest
from src.config import prompt_templates


class TestPromptTemplates:
    """Test cases for prompt template module."""

    def test_evaluation_criteria_exists(self):
        """Test that evaluation criteria constant exists."""
        assert hasattr(prompt_templates, 'EVALUATION_CRITERIA_NAVI_TONEMODERATION_CORRECTNESS')
        assert isinstance(prompt_templates.EVALUATION_CRITERIA_NAVI_TONEMODERATION_CORRECTNESS, str)
        assert len(prompt_templates.EVALUATION_CRITERIA_NAVI_TONEMODERATION_CORRECTNESS) > 0

    def test_evaluation_criteria_content(self):
        """Test evaluation criteria contains expected content."""
        criteria = prompt_templates.EVALUATION_CRITERIA_NAVI_TONEMODERATION_CORRECTNESS
        assert 'Sentiment analysis' in criteria or 'sentiment' in criteria.lower()

    def test_few_shot_examples_exists(self):
        """Test that few shot examples constant exists."""
        assert hasattr(prompt_templates, 'FEW_SHOT_NAVI_TONEMODERATION_CORRECTNESS')
        assert isinstance(prompt_templates.FEW_SHOT_NAVI_TONEMODERATION_CORRECTNESS, str)
        assert len(prompt_templates.FEW_SHOT_NAVI_TONEMODERATION_CORRECTNESS) > 0

    def test_few_shot_examples_structure(self):
        """Test few shot examples contain expected structure."""
        examples = prompt_templates.FEW_SHOT_NAVI_TONEMODERATION_CORRECTNESS
        # Should contain example query/output patterns
        assert '[User Query]' in examples or 'User Query' in examples
        assert '[Output]' in examples or 'Output' in examples

    def test_few_shot_examples_contains_sentiment_data(self):
        """Test few shot examples contain sentiment-related data."""
        examples = prompt_templates.FEW_SHOT_NAVI_TONEMODERATION_CORRECTNESS
        # Check for common sentiment-related terms
        sentiment_terms = ['emotion', 'Positive', 'Negative', 'Tone', 'Sentiment']
        assert any(term in examples for term in sentiment_terms)

    def test_cls_object_exists(self):
        """Test that cls object is created."""
        assert hasattr(prompt_templates, 'cls')
        assert prompt_templates.cls is not None

    def test_module_imports(self):
        """Test that necessary imports are accessible."""
        # The module should have imported ntt
        assert hasattr(prompt_templates, 'ntt')

    def test_evaluation_criteria_is_non_empty_string(self):
        """Test evaluation criteria is a non-empty string."""
        criteria = prompt_templates.EVALUATION_CRITERIA_NAVI_TONEMODERATION_CORRECTNESS
        assert isinstance(criteria, str)
        assert criteria.strip() != ''

    def test_few_shot_examples_is_non_empty_string(self):
        """Test few shot examples is a non-empty string."""
        examples = prompt_templates.FEW_SHOT_NAVI_TONEMODERATION_CORRECTNESS
        assert isinstance(examples, str)
        assert examples.strip() != ''

    def test_constants_are_strings(self):
        """Test that all expected constants are strings."""
        constants = [
            'EVALUATION_CRITERIA_NAVI_TONEMODERATION_CORRECTNESS',
            'FEW_SHOT_NAVI_TONEMODERATION_CORRECTNESS'
        ]
        
        for const_name in constants:
            if hasattr(prompt_templates, const_name):
                const_value = getattr(prompt_templates, const_name)
                assert isinstance(const_value, str), f"{const_name} should be a string"
