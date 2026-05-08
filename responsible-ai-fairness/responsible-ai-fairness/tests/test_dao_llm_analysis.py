"""
Test cases for llm_analysis.py module

Tests the LlmAnalysis Pydantic model with required string and boolean fields.
"""

import pytest
from pydantic import ValidationError
import json


class TestLlmAnalysisCreation:
    """Test LlmAnalysis model instantiation"""
    
    def test_create_with_all_fields(self):
        """Test creating model with all required fields"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model = LlmAnalysis(
            category="bias",
            name="gender_bias",
            value="detected",
            active=True,
            addedBy="admin"
        )
        
        assert model.category == "bias"
        assert model.name == "gender_bias"
        assert model.value == "detected"
        assert model.active is True
        assert model.addedBy == "admin"
    
    def test_create_with_active_false(self):
        """Test creating model with active=False"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model = LlmAnalysis(
            category="fairness",
            name="test_metric",
            value="0.95",
            active=False,
            addedBy="user123"
        )
        
        assert model.active is False
        assert model.category == "fairness"
    
    def test_create_minimal_strings(self):
        """Test creating model with minimal string values"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model = LlmAnalysis(
            category="a",
            name="b",
            value="c",
            active=True,
            addedBy="d"
        )
        
        assert model.category == "a"
        assert model.name == "b"
        assert model.value == "c"
        assert model.addedBy == "d"


class TestRequiredFields:
    """Test that all fields are required"""
    
    def test_missing_category(self):
        """Test that missing category raises ValidationError"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        with pytest.raises(ValidationError) as exc_info:
            LlmAnalysis(
                name="test",
                value="val",
                active=True,
                addedBy="user"
            )
        
        error_str = str(exc_info.value)
        assert "category" in error_str.lower()
    
    def test_missing_name(self):
        """Test that missing name raises ValidationError"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        with pytest.raises(ValidationError) as exc_info:
            LlmAnalysis(
                category="cat",
                value="val",
                active=True,
                addedBy="user"
            )
        
        error_str = str(exc_info.value)
        assert "name" in error_str.lower()
    
    def test_missing_value(self):
        """Test that missing value raises ValidationError"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        with pytest.raises(ValidationError) as exc_info:
            LlmAnalysis(
                category="cat",
                name="test",
                active=True,
                addedBy="user"
            )
        
        error_str = str(exc_info.value)
        assert "value" in error_str.lower()
    
    def test_missing_active(self):
        """Test that missing active raises ValidationError"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        with pytest.raises(ValidationError) as exc_info:
            LlmAnalysis(
                category="cat",
                name="test",
                value="val",
                addedBy="user"
            )
        
        error_str = str(exc_info.value)
        assert "active" in error_str.lower()
    
    def test_missing_addedby(self):
        """Test that missing addedBy raises ValidationError"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        with pytest.raises(ValidationError) as exc_info:
            LlmAnalysis(
                category="cat",
                name="test",
                value="val",
                active=True
            )
        
        error_str = str(exc_info.value)
        assert "addedby" in error_str.lower()
    
    def test_empty_model_fails(self):
        """Test that creating empty model raises ValidationError"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        with pytest.raises(ValidationError):
            LlmAnalysis()


class TestTypeValidation:
    """Test type validation for fields"""
    
    def test_category_must_be_string(self):
        """Test that category must be string"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        with pytest.raises(ValidationError) as exc_info:
            LlmAnalysis(
                category=123,
                name="test",
                value="val",
                active=True,
                addedBy="user"
            )
        
        assert "category" in str(exc_info.value).lower()
    
    def test_name_must_be_string(self):
        """Test that name must be string"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        with pytest.raises(ValidationError) as exc_info:
            LlmAnalysis(
                category="cat",
                name=["list"],
                value="val",
                active=True,
                addedBy="user"
            )
        
        assert "name" in str(exc_info.value).lower()
    
    def test_value_must_be_string(self):
        """Test that value must be string"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        with pytest.raises(ValidationError) as exc_info:
            LlmAnalysis(
                category="cat",
                name="test",
                value={"dict": "value"},
                active=True,
                addedBy="user"
            )
        
        assert "value" in str(exc_info.value).lower()
    
    def test_active_must_be_bool(self):
        """Test that active must be boolean"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        with pytest.raises(ValidationError) as exc_info:
            LlmAnalysis(
                category="cat",
                name="test",
                value="val",
                active="not_bool",
                addedBy="user"
            )
        
        assert "active" in str(exc_info.value).lower()
    
    def test_addedby_must_be_string(self):
        """Test that addedBy must be string"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        with pytest.raises(ValidationError) as exc_info:
            LlmAnalysis(
                category="cat",
                name="test",
                value="val",
                active=True,
                addedBy=999
            )
        
        assert "addedby" in str(exc_info.value).lower()


class TestStringFieldVariations:
    """Test various string field values"""
    
    def test_empty_strings(self):
        """Test with empty strings"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model = LlmAnalysis(
            category="",
            name="",
            value="",
            active=True,
            addedBy=""
        )
        
        assert model.category == ""
        assert model.name == ""
        assert model.value == ""
        assert model.addedBy == ""
    
    def test_whitespace_strings(self):
        """Test with whitespace strings"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model = LlmAnalysis(
            category="   ",
            name="\t\t",
            value="\n\n",
            active=False,
            addedBy="  spaces  "
        )
        
        assert model.category == "   "
        assert model.name == "\t\t"
        assert model.value == "\n\n"
        assert model.addedBy == "  spaces  "
    
    def test_special_characters(self):
        """Test with special characters in strings"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model = LlmAnalysis(
            category="!@#$%^&*()",
            name="test-name_123",
            value="val.with.dots",
            active=True,
            addedBy="user@domain.com"
        )
        
        assert model.category == "!@#$%^&*()"
        assert model.name == "test-name_123"
        assert model.value == "val.with.dots"
        assert model.addedBy == "user@domain.com"
    
    def test_unicode_strings(self):
        """Test with unicode characters"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model = LlmAnalysis(
            category="分类",
            name="名称",
            value="値",
            active=True,
            addedBy="пользователь"
        )
        
        assert model.category == "分类"
        assert model.name == "名称"
        assert model.value == "値"
        assert model.addedBy == "пользователь"
    
    def test_long_strings(self):
        """Test with very long strings"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        long_str = "a" * 1000
        model = LlmAnalysis(
            category=long_str,
            name=long_str,
            value=long_str,
            active=True,
            addedBy=long_str
        )
        
        assert len(model.category) == 1000
        assert len(model.name) == 1000
        assert len(model.value) == 1000
        assert len(model.addedBy) == 1000
    
    def test_multiline_strings(self):
        """Test with multiline strings"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        multiline = "line1\nline2\nline3"
        model = LlmAnalysis(
            category=multiline,
            name="single",
            value=multiline,
            active=False,
            addedBy="user"
        )
        
        assert "\n" in model.category
        assert model.category == multiline


class TestBooleanFieldVariations:
    """Test boolean field with various values"""
    
    def test_active_true(self):
        """Test active field with True"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model = LlmAnalysis(
            category="test",
            name="test",
            value="test",
            active=True,
            addedBy="user"
        )
        
        assert model.active is True
        assert isinstance(model.active, bool)
    
    def test_active_false(self):
        """Test active field with False"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model = LlmAnalysis(
            category="test",
            name="test",
            value="test",
            active=False,
            addedBy="user"
        )
        
        assert model.active is False
        assert isinstance(model.active, bool)
    
    def test_active_with_truthy_int(self):
        """Test that integer 1 is coerced to True"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model = LlmAnalysis(
            category="test",
            name="test",
            value="test",
            active=1,
            addedBy="user"
        )
        
        assert model.active is True
    
    def test_active_with_falsy_int(self):
        """Test that integer 0 is coerced to False"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model = LlmAnalysis(
            category="test",
            name="test",
            value="test",
            active=0,
            addedBy="user"
        )
        
        assert model.active is False


class TestModelSerialization:
    """Test model serialization"""
    
    def test_model_dump(self):
        """Test model_dump() method"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model = LlmAnalysis(
            category="bias_detection",
            name="gender_test",
            value="0.85",
            active=True,
            addedBy="analyst"
        )
        
        dumped = model.model_dump()
        
        assert isinstance(dumped, dict)
        assert dumped["category"] == "bias_detection"
        assert dumped["name"] == "gender_test"
        assert dumped["value"] == "0.85"
        assert dumped["active"] is True
        assert dumped["addedBy"] == "analyst"
    
    def test_model_dump_json(self):
        """Test model_dump_json() method"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model = LlmAnalysis(
            category="test",
            name="metric",
            value="1.0",
            active=False,
            addedBy="system"
        )
        
        json_str = model.model_dump_json()
        
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["category"] == "test"
        assert parsed["active"] is False
    
    def test_dict_method(self):
        """Test that model can be converted to dict"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model = LlmAnalysis(
            category="analysis",
            name="test",
            value="result",
            active=True,
            addedBy="user"
        )
        
        data = dict(model)
        
        assert data["category"] == "analysis"
        assert data["name"] == "test"


class TestModelDeserialization:
    """Test creating models from data"""
    
    def test_from_dict(self):
        """Test creating model from dictionary"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        data = {
            "category": "fairness",
            "name": "demographic_parity",
            "value": "0.92",
            "active": True,
            "addedBy": "researcher"
        }
        
        model = LlmAnalysis(**data)
        
        assert model.category == "fairness"
        assert model.name == "demographic_parity"
        assert model.value == "0.92"
        assert model.active is True
        assert model.addedBy == "researcher"
    
    def test_from_json_string(self):
        """Test creating model from JSON string"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        json_str = '''{"category": "test", "name": "name", "value": "val", "active": true, "addedBy": "user"}'''
        data = json.loads(json_str)
        model = LlmAnalysis(**data)
        
        assert model.category == "test"
        assert model.active is True
    
    def test_model_validate(self):
        """Test model_validate method"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        data = {
            "category": "metric",
            "name": "accuracy",
            "value": "0.95",
            "active": False,
            "addedBy": "admin"
        }
        
        model = LlmAnalysis.model_validate(data)
        
        assert isinstance(model, LlmAnalysis)
        assert model.category == "metric"
        assert model.active is False


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_field_names_case_sensitive(self):
        """Test that field names are case sensitive"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        # addedBy vs addedby
        with pytest.raises(ValidationError):
            LlmAnalysis(
                category="test",
                name="test",
                value="test",
                active=True,
                addedby="user"  # lowercase should fail
            )
    
    def test_numeric_string_value(self):
        """Test value field with numeric string"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model = LlmAnalysis(
            category="metric",
            name="score",
            value="99.99",
            active=True,
            addedBy="system"
        )
        
        assert model.value == "99.99"
        assert isinstance(model.value, str)
    
    def test_json_string_in_value(self):
        """Test value field containing JSON string"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        json_value = '''{"nested": "data", "count": 5}'''
        model = LlmAnalysis(
            category="complex",
            name="nested",
            value=json_value,
            active=True,
            addedBy="user"
        )
        
        assert model.value == json_value
        assert "{" in model.value


class TestModelEquality:
    """Test model equality and comparison"""
    
    def test_equal_models(self):
        """Test two models with same data are equal"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model1 = LlmAnalysis(
            category="test",
            name="name",
            value="val",
            active=True,
            addedBy="user"
        )
        model2 = LlmAnalysis(
            category="test",
            name="name",
            value="val",
            active=True,
            addedBy="user"
        )
        
        assert model1.model_dump() == model2.model_dump()
    
    def test_different_models(self):
        """Test two models with different data are not equal"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model1 = LlmAnalysis(
            category="test1",
            name="name1",
            value="val1",
            active=True,
            addedBy="user1"
        )
        model2 = LlmAnalysis(
            category="test2",
            name="name2",
            value="val2",
            active=False,
            addedBy="user2"
        )
        
        assert model1.model_dump() != model2.model_dump()


class TestModelCopy:
    """Test model copy functionality"""
    
    def test_model_copy(self):
        """Test creating a copy of the model"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model1 = LlmAnalysis(
            category="original",
            name="test",
            value="data",
            active=True,
            addedBy="user"
        )
        model2 = model1.model_copy()
        
        assert model1.model_dump() == model2.model_dump()
        assert model1 is not model2
    
    def test_model_copy_with_update(self):
        """Test model copy with field updates"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model1 = LlmAnalysis(
            category="original",
            name="test",
            value="data",
            active=True,
            addedBy="user1"
        )
        model2 = model1.model_copy(update={"addedBy": "user2", "active": False})
        
        assert model1.addedBy == "user1"
        assert model1.active is True
        assert model2.addedBy == "user2"
        assert model2.active is False
        assert model2.category == "original"


class TestPerformance:
    """Test performance-related scenarios"""
    
    def test_create_many_instances(self):
        """Test creating many instances"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        models = []
        for i in range(1000):
            model = LlmAnalysis(
                category=f"cat_{i}",
                name=f"name_{i}",
                value=f"val_{i}",
                active=i % 2 == 0,
                addedBy=f"user_{i}"
            )
            models.append(model)
        
        assert len(models) == 1000
        assert models[500].category == "cat_500"
        assert models[500].active is True
    
    def test_serialization_performance(self):
        """Test serialization with multiple models"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        models = [
            LlmAnalysis(
                category=f"category_{i}",
                name=f"name_{i}",
                value=f"value_{i}",
                active=True,
                addedBy="system"
            )
            for i in range(100)
        ]
        
        json_strings = [m.model_dump_json() for m in models]
        
        assert len(json_strings) == 100
        assert all(isinstance(s, str) for s in json_strings)


class TestCodeQuality:
    """Test code quality indicators"""
    
    def test_class_is_basemodel(self):
        """Test that LlmAnalysis inherits from BaseModel"""
        from fairness.dao.llm_analysis import LlmAnalysis
        from pydantic import BaseModel
        
        assert issubclass(LlmAnalysis, BaseModel)
    
    def test_model_fields_exist(self):
        """Test that all expected fields exist"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model = LlmAnalysis(
            category="test",
            name="test",
            value="test",
            active=True,
            addedBy="user"
        )
        
        assert hasattr(model, "category")
        assert hasattr(model, "name")
        assert hasattr(model, "value")
        assert hasattr(model, "active")
        assert hasattr(model, "addedBy")
    
    def test_model_schema(self):
        """Test model JSON schema generation"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        schema = LlmAnalysis.model_json_schema()
        
        assert "properties" in schema
        assert "category" in schema["properties"]
        assert "name" in schema["properties"]
        assert "value" in schema["properties"]
        assert "active" in schema["properties"]
        assert "addedBy" in schema["properties"]
    
    def test_required_fields_in_schema(self):
        """Test that required fields are marked in schema"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        schema = LlmAnalysis.model_json_schema()
        
        # All fields should be required
        assert "required" in schema
        assert "category" in schema["required"]
        assert "name" in schema["required"]
        assert "value" in schema["required"]
        assert "active" in schema["required"]
        assert "addedBy" in schema["required"]


class TestRegression:
    """Test regression scenarios"""
    
    def test_complete_workflow(self):
        """Test complete workflow from creation to serialization"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        # Create model
        model = LlmAnalysis(
            category="bias_analysis",
            name="demographic_bias",
            value="detected",
            active=True,
            addedBy="ml_engineer"
        )
        
        # Verify creation
        assert model.category == "bias_analysis"
        
        # Serialize to dict
        data_dict = model.model_dump()
        assert data_dict["name"] == "demographic_bias"
        
        # Serialize to JSON
        json_str = model.model_dump_json()
        assert "ml_engineer" in json_str
        
        # Recreate from dict
        model2 = LlmAnalysis(**data_dict)
        assert model2.value == "detected"
        assert model2.active is True
    
    def test_update_workflow(self):
        """Test workflow for updating model"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        original = LlmAnalysis(
            category="test",
            name="original",
            value="old",
            active=True,
            addedBy="user1"
        )
        
        # Create updated version
        updated = original.model_copy(update={
            "value": "new",
            "addedBy": "user2",
            "active": False
        })
        
        # Verify original unchanged
        assert original.value == "old"
        assert original.addedBy == "user1"
        assert original.active is True
        
        # Verify update
        assert updated.value == "new"
        assert updated.addedBy == "user2"
        assert updated.active is False


class TestIntegrationScenarios:
    """Test integration scenarios"""
    
    def test_json_roundtrip(self):
        """Test JSON serialization and deserialization roundtrip"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        original = LlmAnalysis(
            category="fairness_metric",
            name="equal_opportunity",
            value="0.87",
            active=True,
            addedBy="data_scientist"
        )
        
        # Serialize to JSON
        json_str = original.model_dump_json()
        
        # Deserialize
        data = json.loads(json_str)
        restored = LlmAnalysis(**data)
        
        # Verify roundtrip
        assert restored.category == original.category
        assert restored.name == original.name
        assert restored.value == original.value
        assert restored.active == original.active
        assert restored.addedBy == original.addedBy
    
    def test_dict_roundtrip(self):
        """Test dict serialization and deserialization roundtrip"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        original = LlmAnalysis(
            category="test_category",
            name="test_name",
            value="test_value",
            active=False,
            addedBy="test_user"
        )
        
        # Convert to dict
        data_dict = original.model_dump()
        
        # Recreate from dict
        restored = LlmAnalysis.model_validate(data_dict)
        
        # Verify roundtrip
        assert restored.model_dump() == original.model_dump()
    
    def test_batch_processing(self):
        """Test processing batch of models"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        # Create batch
        batch = [
            LlmAnalysis(
                category=f"cat_{i}",
                name=f"name_{i}",
                value=f"val_{i}",
                active=i % 2 == 0,
                addedBy="batch_processor"
            )
            for i in range(10)
        ]
        
        # Serialize batch
        serialized = [m.model_dump() for m in batch]
        
        # Deserialize batch
        restored = [LlmAnalysis(**d) for d in serialized]
        
        # Verify
        assert len(restored) == 10
        assert restored[5].category == "cat_5"
        assert restored[5].active is False


class TestSecurityAndValidation:
    """Test security and validation aspects"""
    
    def test_extra_fields_handled(self):
        """Test that extra fields are handled according to config"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        # By default, Pydantic ignores extra fields
        model = LlmAnalysis(
            category="test",
            name="test",
            value="test",
            active=True,
            addedBy="user",
            extra_field="ignored"
        )
        
        assert model.category == "test"
        assert hasattr(model, "category")
    
    def test_none_values_rejected(self):
        """Test that None values are rejected for required fields"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        with pytest.raises(ValidationError):
            LlmAnalysis(
                category=None,
                name="test",
                value="test",
                active=True,
                addedBy="user"
            )
    
    def test_injection_in_strings(self):
        """Test handling of potentially malicious strings"""
        from fairness.dao.llm_analysis import LlmAnalysis
        
        model = LlmAnalysis(
            category="<script>alert(1)</script>",
            name="DROP TABLE users;",
            value="../../etc/passwd",
            active=True,
            addedBy="admin' OR '1'='1"
        )
        
        # Model should accept the strings as-is (validation responsibility elsewhere)
        assert model.category == "<script>alert(1)</script>"
        assert model.name == "DROP TABLE users;"
        assert model.value == "../../etc/passwd"
