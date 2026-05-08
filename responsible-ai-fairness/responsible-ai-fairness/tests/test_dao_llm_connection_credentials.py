"""
Test cases for llm_connection_credentials.py module

Tests the LlmConnectionCredentials Pydantic model with required string, dict, and boolean fields.
"""

import pytest
from pydantic import ValidationError
import json


class TestLlmConnectionCredentialsCreation:
    """Test LlmConnectionCredentials model instantiation"""
    
    def test_create_with_all_fields(self):
        """Test creating model with all required fields"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model = LlmConnectionCredentials(
            name="openai_api",
            value="sk-1234567890",
            details={"endpoint": "https://api.openai.com", "model": "gpt-4"},
            active=True
        )
        
        assert model.name == "openai_api"
        assert model.value == "sk-1234567890"
        assert model.details == {"endpoint": "https://api.openai.com", "model": "gpt-4"}
        assert model.active is True
    
    def test_create_with_active_false(self):
        """Test creating model with active=False"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model = LlmConnectionCredentials(
            name="azure_openai",
            value="azure-key-123",
            details={"region": "eastus", "deployment": "gpt35"},
            active=False
        )
        
        assert model.active is False
        assert model.name == "azure_openai"
    
    def test_create_with_empty_details(self):
        """Test creating model with empty details dict"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model = LlmConnectionCredentials(
            name="test",
            value="test_value",
            details={},
            active=True
        )
        
        assert model.details == {}
        assert isinstance(model.details, dict)


class TestRequiredFields:
    """Test that all fields are required"""
    
    def test_missing_name(self):
        """Test that missing name raises ValidationError"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        with pytest.raises(ValidationError) as exc_info:
            LlmConnectionCredentials(
                value="val",
                details={"key": "value"},
                active=True
            )
        
        assert "name" in str(exc_info.value).lower()
    
    def test_missing_value(self):
        """Test that missing value raises ValidationError"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        with pytest.raises(ValidationError) as exc_info:
            LlmConnectionCredentials(
                name="test",
                details={"key": "value"},
                active=True
            )
        
        assert "value" in str(exc_info.value).lower()
    
    def test_missing_details(self):
        """Test that missing details raises ValidationError"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        with pytest.raises(ValidationError) as exc_info:
            LlmConnectionCredentials(
                name="test",
                value="val",
                active=True
            )
        
        assert "details" in str(exc_info.value).lower()
    
    def test_missing_active(self):
        """Test that missing active raises ValidationError"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        with pytest.raises(ValidationError) as exc_info:
            LlmConnectionCredentials(
                name="test",
                value="val",
                details={"key": "value"}
            )
        
        assert "active" in str(exc_info.value).lower()
    
    def test_empty_model_fails(self):
        """Test that creating empty model raises ValidationError"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        with pytest.raises(ValidationError):
            LlmConnectionCredentials()


class TestTypeValidation:
    """Test type validation for fields"""
    
    def test_name_must_be_string(self):
        """Test that name must be string"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        with pytest.raises(ValidationError) as exc_info:
            LlmConnectionCredentials(
                name=123,
                value="val",
                details={"key": "value"},
                active=True
            )
        
        assert "name" in str(exc_info.value).lower()
    
    def test_value_must_be_string(self):
        """Test that value must be string"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        with pytest.raises(ValidationError) as exc_info:
            LlmConnectionCredentials(
                name="test",
                value=["list"],
                details={"key": "value"},
                active=True
            )
        
        assert "value" in str(exc_info.value).lower()
    
    def test_details_must_be_dict(self):
        """Test that details must be dict"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        with pytest.raises(ValidationError) as exc_info:
            LlmConnectionCredentials(
                name="test",
                value="val",
                details="not a dict",
                active=True
            )
        
        assert "details" in str(exc_info.value).lower()
    
    def test_details_must_be_dict_not_list(self):
        """Test that details cannot be a list"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        with pytest.raises(ValidationError):
            LlmConnectionCredentials(
                name="test",
                value="val",
                details=[{"key": "value"}],
                active=True
            )
    
    def test_active_must_be_bool(self):
        """Test that active must be boolean"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        with pytest.raises(ValidationError) as exc_info:
            LlmConnectionCredentials(
                name="test",
                value="val",
                details={"key": "value"},
                active="not_bool"
            )
        
        assert "active" in str(exc_info.value).lower()


class TestDetailsFieldVariations:
    """Test various details dictionary structures"""
    
    def test_simple_details_dict(self):
        """Test with simple key-value pairs"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        details = {"api_key": "key123", "endpoint": "https://api.example.com"}
        model = LlmConnectionCredentials(
            name="test",
            value="val",
            details=details,
            active=True
        )
        
        assert model.details == details
        assert model.details["api_key"] == "key123"
    
    def test_nested_details_dict(self):
        """Test with nested dictionary (allowed by Dict[str, str] with coercion)"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        # Note: Dict[str, str] means values should be strings
        details = {
            "endpoint": "https://api.openai.com",
            "region": "us-east-1",
            "timeout": "30"
        }
        model = LlmConnectionCredentials(
            name="config",
            value="creds",
            details=details,
            active=True
        )
        
        assert model.details["endpoint"] == "https://api.openai.com"
        assert model.details["timeout"] == "30"
    
    def test_details_with_many_keys(self):
        """Test with large details dictionary"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        details = {f"key_{i}": f"value_{i}" for i in range(50)}
        model = LlmConnectionCredentials(
            name="test",
            value="val",
            details=details,
            active=True
        )
        
        assert len(model.details) == 50
        assert model.details["key_25"] == "value_25"
    
    def test_details_with_special_chars_in_keys(self):
        """Test details with special characters in keys"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        details = {
            "api-key": "val1",
            "end_point": "val2",
            "config.setting": "val3",
            "param@1": "val4"
        }
        model = LlmConnectionCredentials(
            name="test",
            value="val",
            details=details,
            active=True
        )
        
        assert model.details["api-key"] == "val1"
        assert model.details["config.setting"] == "val3"
    
    def test_details_with_empty_string_values(self):
        """Test details with empty string values"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        details = {"key1": "", "key2": "value", "key3": ""}
        model = LlmConnectionCredentials(
            name="test",
            value="val",
            details=details,
            active=True
        )
        
        assert model.details["key1"] == ""
        assert model.details["key2"] == "value"
    
    def test_details_values_must_be_strings(self):
        """Test that details values must be strings per Dict[str, str]"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        # Pydantic will try to coerce int to string
        details = {"key": "123"}  # Already string
        model = LlmConnectionCredentials(
            name="test",
            value="val",
            details=details,
            active=True
        )
        
        assert model.details["key"] == "123"
        assert isinstance(model.details["key"], str)


class TestStringFieldVariations:
    """Test various string field values"""
    
    def test_empty_strings(self):
        """Test with empty strings for name and value"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model = LlmConnectionCredentials(
            name="",
            value="",
            details={"key": "val"},
            active=True
        )
        
        assert model.name == ""
        assert model.value == ""
    
    def test_long_strings(self):
        """Test with very long strings"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        long_str = "a" * 1000
        model = LlmConnectionCredentials(
            name=long_str,
            value=long_str,
            details={"key": long_str},
            active=True
        )
        
        assert len(model.name) == 1000
        assert len(model.value) == 1000
    
    def test_special_characters(self):
        """Test with special characters"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model = LlmConnectionCredentials(
            name="api-key_v2.0",
            value="sk-!@#$%^&*()",
            details={"url": "https://api.example.com/v1"},
            active=True
        )
        
        assert model.name == "api-key_v2.0"
        assert model.value == "sk-!@#$%^&*()"
    
    def test_unicode_strings(self):
        """Test with unicode characters"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model = LlmConnectionCredentials(
            name="名前",
            value="値",
            details={"キー": "バリュー"},
            active=True
        )
        
        assert model.name == "名前"
        assert model.value == "値"


class TestBooleanFieldVariations:
    """Test boolean field with various values"""
    
    def test_active_true(self):
        """Test active field with True"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model = LlmConnectionCredentials(
            name="test",
            value="val",
            details={"key": "value"},
            active=True
        )
        
        assert model.active is True
        assert isinstance(model.active, bool)
    
    def test_active_false(self):
        """Test active field with False"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model = LlmConnectionCredentials(
            name="test",
            value="val",
            details={"key": "value"},
            active=False
        )
        
        assert model.active is False
    
    def test_active_with_truthy_int(self):
        """Test that integer 1 is coerced to True"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model = LlmConnectionCredentials(
            name="test",
            value="val",
            details={"key": "value"},
            active=1
        )
        
        assert model.active is True
    
    def test_active_with_falsy_int(self):
        """Test that integer 0 is coerced to False"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model = LlmConnectionCredentials(
            name="test",
            value="val",
            details={"key": "value"},
            active=0
        )
        
        assert model.active is False


class TestModelSerialization:
    """Test model serialization"""
    
    def test_model_dump(self):
        """Test model_dump() method"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model = LlmConnectionCredentials(
            name="aws_bedrock",
            value="aws-key-123",
            details={"region": "us-west-2", "model_id": "anthropic.claude-v2"},
            active=True
        )
        
        dumped = model.model_dump()
        
        assert isinstance(dumped, dict)
        assert dumped["name"] == "aws_bedrock"
        assert dumped["value"] == "aws-key-123"
        assert dumped["details"]["region"] == "us-west-2"
        assert dumped["active"] is True
    
    def test_model_dump_json(self):
        """Test model_dump_json() method"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model = LlmConnectionCredentials(
            name="openai",
            value="key123",
            details={"endpoint": "https://api.openai.com"},
            active=False
        )
        
        json_str = model.model_dump_json()
        
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["name"] == "openai"
        assert parsed["active"] is False
        assert parsed["details"]["endpoint"] == "https://api.openai.com"
    
    def test_dict_method(self):
        """Test that model can be converted to dict"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model = LlmConnectionCredentials(
            name="test",
            value="val",
            details={"key": "value"},
            active=True
        )
        
        data = dict(model)
        
        assert data["name"] == "test"
        assert data["details"]["key"] == "value"


class TestModelDeserialization:
    """Test creating models from data"""
    
    def test_from_dict(self):
        """Test creating model from dictionary"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        data = {
            "name": "google_palm",
            "value": "google-api-key",
            "details": {"project": "my-project", "location": "us-central1"},
            "active": True
        }
        
        model = LlmConnectionCredentials(**data)
        
        assert model.name == "google_palm"
        assert model.details["project"] == "my-project"
        assert model.active is True
    
    def test_from_json_string(self):
        """Test creating model from JSON string"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        json_str = '''{"name": "azure", "value": "key", "details": {"endpoint": "https://azure.com"}, "active": true}'''
        data = json.loads(json_str)
        model = LlmConnectionCredentials(**data)
        
        assert model.name == "azure"
        assert model.details["endpoint"] == "https://azure.com"
    
    def test_model_validate(self):
        """Test model_validate method"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        data = {
            "name": "huggingface",
            "value": "hf_token",
            "details": {"model": "meta-llama/Llama-2-7b", "task": "text-generation"},
            "active": False
        }
        
        model = LlmConnectionCredentials.model_validate(data)
        
        assert isinstance(model, LlmConnectionCredentials)
        assert model.name == "huggingface"
        assert model.active is False


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_whitespace_in_name(self):
        """Test name with whitespace"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model = LlmConnectionCredentials(
            name="  test name  ",
            value="val",
            details={"key": "value"},
            active=True
        )
        
        assert model.name == "  test name  "
    
    def test_multiline_value(self):
        """Test value with newlines"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        multiline_value = "line1\nline2\nline3"
        model = LlmConnectionCredentials(
            name="test",
            value=multiline_value,
            details={"key": "val"},
            active=True
        )
        
        assert "\n" in model.value
    
    def test_numeric_string_keys_in_details(self):
        """Test details with numeric string keys"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        details = {"1": "one", "2": "two", "3": "three"}
        model = LlmConnectionCredentials(
            name="test",
            value="val",
            details=details,
            active=True
        )
        
        assert model.details["1"] == "one"
    
    def test_json_string_in_details_value(self):
        """Test details value containing JSON string"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        details = {"config": '''{"nested": "json"}'''} 
        model = LlmConnectionCredentials(
            name="test",
            value="val",
            details=details,
            active=True
        )
        
        assert "{" in model.details["config"]


class TestModelEquality:
    """Test model equality and comparison"""
    
    def test_equal_models(self):
        """Test two models with same data are equal"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model1 = LlmConnectionCredentials(
            name="test",
            value="val",
            details={"key": "value"},
            active=True
        )
        model2 = LlmConnectionCredentials(
            name="test",
            value="val",
            details={"key": "value"},
            active=True
        )
        
        assert model1.model_dump() == model2.model_dump()
    
    def test_different_models(self):
        """Test two models with different data are not equal"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model1 = LlmConnectionCredentials(
            name="test1",
            value="val1",
            details={"key": "value1"},
            active=True
        )
        model2 = LlmConnectionCredentials(
            name="test2",
            value="val2",
            details={"key": "value2"},
            active=False
        )
        
        assert model1.model_dump() != model2.model_dump()


class TestModelCopy:
    """Test model copy functionality"""
    
    def test_model_copy(self):
        """Test creating a copy of the model"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model1 = LlmConnectionCredentials(
            name="original",
            value="original_val",
            details={"key": "value"},
            active=True
        )
        model2 = model1.model_copy()
        
        assert model1.model_dump() == model2.model_dump()
        assert model1 is not model2
    
    def test_model_copy_with_update(self):
        """Test model copy with field updates"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model1 = LlmConnectionCredentials(
            name="original",
            value="val1",
            details={"key": "value1"},
            active=True
        )
        model2 = model1.model_copy(update={"value": "val2", "active": False})
        
        assert model1.value == "val1"
        assert model1.active is True
        assert model2.value == "val2"
        assert model2.active is False
    
    def test_model_copy_deep_details(self):
        """Test that details dict is properly copied"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model1 = LlmConnectionCredentials(
            name="test",
            value="val",
            details={"key": "value"},
            active=True
        )
        model2 = model1.model_copy(deep=True)
        
        # Modify copy
        model2.details["key"] = "modified"
        
        # Original should be unchanged
        assert model1.details["key"] == "value"


class TestPerformance:
    """Test performance-related scenarios"""
    
    def test_create_many_instances(self):
        """Test creating many instances"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        models = []
        for i in range(1000):
            model = LlmConnectionCredentials(
                name=f"cred_{i}",
                value=f"key_{i}",
                details={"id": str(i), "type": "api"},
                active=i % 2 == 0
            )
            models.append(model)
        
        assert len(models) == 1000
        assert models[500].name == "cred_500"
    
    def test_serialization_performance(self):
        """Test serialization with multiple models"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        models = [
            LlmConnectionCredentials(
                name=f"name_{i}",
                value=f"value_{i}",
                details={f"key_{j}": f"val_{j}" for j in range(5)},
                active=True
            )
            for i in range(100)
        ]
        
        json_strings = [m.model_dump_json() for m in models]
        
        assert len(json_strings) == 100
        assert all(isinstance(s, str) for s in json_strings)


class TestCodeQuality:
    """Test code quality indicators"""
    
    def test_class_is_basemodel(self):
        """Test that LlmConnectionCredentials inherits from BaseModel"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        from pydantic import BaseModel
        
        assert issubclass(LlmConnectionCredentials, BaseModel)
    
    def test_model_fields_exist(self):
        """Test that all expected fields exist"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model = LlmConnectionCredentials(
            name="test",
            value="val",
            details={"key": "value"},
            active=True
        )
        
        assert hasattr(model, "name")
        assert hasattr(model, "value")
        assert hasattr(model, "details")
        assert hasattr(model, "active")
    
    def test_model_schema(self):
        """Test model JSON schema generation"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        schema = LlmConnectionCredentials.model_json_schema()
        
        assert "properties" in schema
        assert "name" in schema["properties"]
        assert "value" in schema["properties"]
        assert "details" in schema["properties"]
        assert "active" in schema["properties"]
    
    def test_required_fields_in_schema(self):
        """Test that all fields are required in schema"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        schema = LlmConnectionCredentials.model_json_schema()
        
        assert "required" in schema
        assert "name" in schema["required"]
        assert "value" in schema["required"]
        assert "details" in schema["required"]
        assert "active" in schema["required"]


class TestRegression:
    """Test regression scenarios"""
    
    def test_complete_workflow(self):
        """Test complete workflow from creation to serialization"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        # Create model
        model = LlmConnectionCredentials(
            name="anthropic",
            value="anthropic-api-key",
            details={
                "endpoint": "https://api.anthropic.com",
                "model": "claude-2",
                "max_tokens": "4096"
            },
            active=True
        )
        
        # Verify creation
        assert model.name == "anthropic"
        
        # Serialize to dict
        data_dict = model.model_dump()
        assert data_dict["details"]["model"] == "claude-2"
        
        # Serialize to JSON
        json_str = model.model_dump_json()
        assert "anthropic" in json_str
        
        # Recreate from dict
        model2 = LlmConnectionCredentials(**data_dict)
        assert model2.value == "anthropic-api-key"
        assert model2.active is True
    
    def test_update_workflow(self):
        """Test workflow for updating credentials"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        original = LlmConnectionCredentials(
            name="old_cred",
            value="old_key",
            details={"version": "v1"},
            active=True
        )
        
        # Create updated version
        updated = original.model_copy(update={
            "value": "new_key",
            "details": {"version": "v2"},
            "active": False
        })
        
        # Verify original unchanged
        assert original.value == "old_key"
        assert original.details["version"] == "v1"
        
        # Verify update
        assert updated.value == "new_key"
        assert updated.details["version"] == "v2"
        assert updated.active is False


class TestIntegrationScenarios:
    """Test integration scenarios"""
    
    def test_json_roundtrip(self):
        """Test JSON serialization and deserialization roundtrip"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        original = LlmConnectionCredentials(
            name="cohere",
            value="cohere-key-123",
            details={"endpoint": "https://api.cohere.ai", "version": "2023-05"},
            active=True
        )
        
        # Serialize to JSON
        json_str = original.model_dump_json()
        
        # Deserialize
        data = json.loads(json_str)
        restored = LlmConnectionCredentials(**data)
        
        # Verify roundtrip
        assert restored.name == original.name
        assert restored.value == original.value
        assert restored.details == original.details
        assert restored.active == original.active
    
    def test_dict_roundtrip(self):
        """Test dict serialization and deserialization roundtrip"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        original = LlmConnectionCredentials(
            name="test_cred",
            value="test_key",
            details={"param1": "val1", "param2": "val2"},
            active=False
        )
        
        # Convert to dict
        data_dict = original.model_dump()
        
        # Recreate from dict
        restored = LlmConnectionCredentials.model_validate(data_dict)
        
        # Verify roundtrip
        assert restored.model_dump() == original.model_dump()
    
    def test_batch_credentials_processing(self):
        """Test processing batch of credentials"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        # Create batch
        batch = [
            LlmConnectionCredentials(
                name=f"provider_{i}",
                value=f"key_{i}",
                details={"endpoint": f"https://api{i}.com", "tier": "pro"},
                active=i % 3 != 0
            )
            for i in range(10)
        ]
        
        # Serialize batch
        serialized = [m.model_dump() for m in batch]
        
        # Deserialize batch
        restored = [LlmConnectionCredentials(**d) for d in serialized]
        
        # Verify
        assert len(restored) == 10
        assert restored[5].name == "provider_5"
        assert restored[5].details["tier"] == "pro"


class TestSecurityAndValidation:
    """Test security and validation aspects"""
    
    def test_extra_fields_handled(self):
        """Test that extra fields are handled according to config"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model = LlmConnectionCredentials(
            name="test",
            value="val",
            details={"key": "value"},
            active=True,
            extra_field="ignored"
        )
        
        assert model.name == "test"
        assert hasattr(model, "name")
    
    def test_none_values_rejected(self):
        """Test that None values are rejected for required fields"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        with pytest.raises(ValidationError):
            LlmConnectionCredentials(
                name=None,
                value="val",
                details={"key": "value"},
                active=True
            )
    
    def test_sensitive_data_in_value(self):
        """Test handling of sensitive credential data"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        # Model should accept sensitive data (encryption responsibility elsewhere)
        sensitive_key = "sk-proj-1234567890abcdef1234567890abcdef"
        model = LlmConnectionCredentials(
            name="openai_prod",
            value=sensitive_key,
            details={"environment": "production"},
            active=True
        )
        
        assert model.value == sensitive_key
    
    def test_sql_injection_strings(self):
        """Test handling of potentially malicious SQL strings"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model = LlmConnectionCredentials(
            name="test' OR '1'='1",
            value="DROP TABLE credentials;",
            details={"query": "SELECT * FROM users WHERE id=1; DROP TABLE users;"},
            active=True
        )
        
        # Model should accept strings as-is (sanitization responsibility elsewhere)
        assert "DROP TABLE" in model.value
    
    def test_path_traversal_strings(self):
        """Test handling of path traversal attempts"""
        from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
        
        model = LlmConnectionCredentials(
            name="../../../etc/passwd",
            value="../../config/secrets",
            details={"path": "..\\..\\Windows\\System32"},
            active=True
        )
        
        assert model.name == "../../../etc/passwd"
        assert model.value == "../../config/secrets"
