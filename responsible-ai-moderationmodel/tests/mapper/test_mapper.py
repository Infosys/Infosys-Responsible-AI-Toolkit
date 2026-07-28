"""
Unit tests for mapper module.
Tests the Pydantic models used for data validation.
"""
import pytest
from pydantic import ValidationError


class TestProfanityScore:
    """Test cases for ProfanityScore model."""

    def test_profanity_score_creation(self):
        """Test creating a valid ProfanityScore instance."""
        from mapper.mapper import ProfanityScore

        score = ProfanityScore(metricName="toxicity", metricScore=0.78326)
        
        assert score.metricName == "toxicity"
        assert score.metricScore == 0.78326

    def test_profanity_score_with_different_metrics(self):
        """Test ProfanityScore with different metric names."""
        from mapper.mapper import ProfanityScore

        metrics = [
            ("toxicity", 0.5),
            ("severe_toxicity", 0.1),
            ("obscene", 0.8),
            ("threat", 0.3),
            ("insult", 0.6),
            ("identity_attack", 0.2),
        ]

        for metric_name, metric_score in metrics:
            score = ProfanityScore(metricName=metric_name, metricScore=metric_score)
            assert score.metricName == metric_name
            assert score.metricScore == metric_score

    def test_profanity_score_with_zero_score(self):
        """Test ProfanityScore with zero score."""
        from mapper.mapper import ProfanityScore

        score = ProfanityScore(metricName="toxicity", metricScore=0.0)
        assert score.metricScore == 0.0

    def test_profanity_score_with_max_score(self):
        """Test ProfanityScore with maximum score."""
        from mapper.mapper import ProfanityScore

        score = ProfanityScore(metricName="toxicity", metricScore=1.0)
        assert score.metricScore == 1.0

    def test_profanity_score_json_serialization(self):
        """Test that ProfanityScore can be serialized to JSON."""
        from mapper.mapper import ProfanityScore

        score = ProfanityScore(metricName="toxicity", metricScore=0.78326)
        json_data = score.model_dump()
        
        assert json_data["metricName"] == "toxicity"
        assert json_data["metricScore"] == 0.78326

    def test_profanity_score_from_dict(self):
        """Test creating ProfanityScore from dictionary."""
        from mapper.mapper import ProfanityScore

        data = {"metricName": "toxicity", "metricScore": 0.78326}
        score = ProfanityScore(**data)
        
        assert score.metricName == "toxicity"
        assert score.metricScore == 0.78326

    def test_profanity_score_invalid_metric_score_type(self):
        """Test that invalid metricScore type raises validation error."""
        from mapper.mapper import ProfanityScore

        with pytest.raises(ValidationError):
            ProfanityScore(metricName="toxicity", metricScore="invalid")

    def test_profanity_score_missing_required_field(self):
        """Test that missing required fields raise validation error."""
        from mapper.mapper import ProfanityScore

        with pytest.raises(ValidationError):
            ProfanityScore(metricName="toxicity")

        with pytest.raises(ValidationError):
            ProfanityScore(metricScore=0.5)

    def test_profanity_score_negative_score(self):
        """Test ProfanityScore with negative score (should be allowed by model)."""
        from mapper.mapper import ProfanityScore

        # Note: The model doesn't enforce 0-1 range, so negative values are technically valid
        score = ProfanityScore(metricName="toxicity", metricScore=-0.1)
        assert score.metricScore == -0.1

    def test_profanity_score_score_above_one(self):
        """Test ProfanityScore with score above 1.0 (should be allowed by model)."""
        from mapper.mapper import ProfanityScore

        # Note: The model doesn't enforce 0-1 range, so values > 1 are technically valid
        score = ProfanityScore(metricName="toxicity", metricScore=1.5)
        assert score.metricScore == 1.5

    def test_profanity_score_empty_metric_name(self):
        """Test ProfanityScore with empty metric name."""
        from mapper.mapper import ProfanityScore

        score = ProfanityScore(metricName="", metricScore=0.5)
        assert score.metricName == ""

    def test_profanity_score_type_conversion(self):
        """Test that numeric strings are converted to float."""
        from mapper.mapper import ProfanityScore

        score = ProfanityScore(metricName="toxicity", metricScore="0.78326")
        assert isinstance(score.metricScore, float)
        assert score.metricScore == 0.78326
