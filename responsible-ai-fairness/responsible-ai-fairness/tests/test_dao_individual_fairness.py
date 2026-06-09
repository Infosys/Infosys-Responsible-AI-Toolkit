"""
Test cases for individual_fairness.py module

Tests the Individual_Fairness Pydantic model with optional dict and string fields.
"""

import pytest
from pydantic import ValidationError
import json


class TestIndividualFairnessCreation:
    """Test Individual_Fairness model instantiation"""
    
    def test_empty_model(self):
        """Test creating model with no arguments"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        model = Individual_Fairness()
        
        assert model.features_dict is None
        assert model.local_file_name is None
    
    def test_with_features_dict_only(self):
        """Test creating model with only features_dict"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        features = {"age": 25, "income": 50000}
        model = Individual_Fairness(features_dict=features)
        
        assert model.features_dict == features
        assert model.local_file_name is None
    
    def test_with_local_file_name_only(self):
        """Test creating model with only local_file_name"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        filename = "data.csv"
        model = Individual_Fairness(local_file_name=filename)
        
        assert model.features_dict is None
        assert model.local_file_name == filename
    
    def test_with_both_fields(self):
        """Test creating model with both fields populated"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        features = {"gender": "F", "education": "Masters"}
        filename = "input_data.csv"
        model = Individual_Fairness(features_dict=features, local_file_name=filename)
        
        assert model.features_dict == features
        assert model.local_file_name == filename


class TestFeaturesDictVariations:
    """Test features_dict with various dictionary types"""
    
    def test_empty_dict(self):
        """Test with empty dictionary"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        model = Individual_Fairness(features_dict={})
        
        assert model.features_dict == {}
        assert isinstance(model.features_dict, dict)
    
    def test_nested_dict(self):
        """Test with nested dictionary"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        features = {
            "demographics": {"age": 30, "gender": "M"},
            "financial": {"income": 75000, "credit_score": 720}
        }
        model = Individual_Fairness(features_dict=features)
        
        assert model.features_dict == features
        assert model.features_dict["demographics"]["age"] == 30
    
    def test_mixed_value_types(self):
        """Test dictionary with mixed value types"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        features = {
            "string_val": "test",
            "int_val": 42,
            "float_val": 3.14,
            "bool_val": True,
            "list_val": [1, 2, 3],
            "none_val": None
        }
        model = Individual_Fairness(features_dict=features)
        
        assert model.features_dict == features
        assert model.features_dict["int_val"] == 42
        assert model.features_dict["bool_val"] is True
    
    def test_large_dict(self):
        """Test with large dictionary"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        features = {f"feature_{i}": i for i in range(100)}
        model = Individual_Fairness(features_dict=features)
        
        assert len(model.features_dict) == 100
        assert model.features_dict["feature_50"] == 50


class TestLocalFileNameVariations:
    """Test local_file_name with various string formats"""
    
    def test_simple_filename(self):
        """Test with simple filename"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        model = Individual_Fairness(local_file_name="data.csv")
        
        assert model.local_file_name == "data.csv"
    
    def test_path_with_directories(self):
        """Test with full file path"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        path = "/home/user/data/fairness_data.csv"
        model = Individual_Fairness(local_file_name=path)
        
        assert model.local_file_name == path
    
    def test_windows_path(self):
        """Test with Windows-style path"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        path = "C:\\Users\\data\\file.xlsx"
        model = Individual_Fairness(local_file_name=path)
        
        assert model.local_file_name == path
    
    def test_filename_with_special_chars(self):
        """Test filename with special characters"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        filename = "data_2024-12-23_v1.0.csv"
        model = Individual_Fairness(local_file_name=filename)
        
        assert model.local_file_name == filename
    
    def test_empty_string_filename(self):
        """Test with empty string filename"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        model = Individual_Fairness(local_file_name="")
        
        assert model.local_file_name == ""


class TestModelSerialization:
    """Test Pydantic model serialization features"""
    
    def test_model_dump(self):
        """Test model_dump() method"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        features = {"age": 30, "salary": 50000}
        model = Individual_Fairness(features_dict=features, local_file_name="data.csv")
        
        dumped = model.model_dump()
        
        assert isinstance(dumped, dict)
        assert dumped["features_dict"] == features
        assert dumped["local_file_name"] == "data.csv"
    
    def test_model_dump_json(self):
        """Test model_dump_json() method"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        features = {"age": 30}
        model = Individual_Fairness(features_dict=features, local_file_name="data.csv")
        
        json_str = model.model_dump_json()
        
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["features_dict"]["age"] == 30
    
    def test_model_dump_with_none_values(self):
        """Test serialization with None values"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        model = Individual_Fairness()
        
        dumped = model.model_dump()
        
        assert "features_dict" in dumped
        assert "local_file_name" in dumped
        assert dumped["features_dict"] is None
        assert dumped["local_file_name"] is None


class TestModelDeserialization:
    """Test creating models from dictionaries"""
    
    def test_from_dict(self):
        """Test creating model from dictionary"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        data = {
            "features_dict": {"age": 25, "income": 40000},
            "local_file_name": "input.csv"
        }
        model = Individual_Fairness(**data)
        
        assert model.features_dict == data["features_dict"]
        assert model.local_file_name == data["local_file_name"]
    
    def test_from_json_string(self):
        """Test creating model from JSON string"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        json_str = '''{"features_dict": {"age": 30}, "local_file_name": "data.csv"}'''
        data = json.loads(json_str)
        model = Individual_Fairness(**data)
        
        assert model.features_dict["age"] == 30
        assert model.local_file_name == "data.csv"
    
    def test_model_validate(self):
        """Test model_validate method"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        data = {"features_dict": {"test": "value"}, "local_file_name": "file.txt"}
        model = Individual_Fairness.model_validate(data)
        
        assert isinstance(model, Individual_Fairness)
        assert model.features_dict["test"] == "value"


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_unicode_in_dict_keys(self):
        """Test features_dict with unicode characters in keys"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        features = {"名前": "test", "возраст": 25, "città": "Rome"}
        model = Individual_Fairness(features_dict=features)
        
        assert model.features_dict["名前"] == "test"
        assert model.features_dict["возраст"] == 25
    
    def test_unicode_in_filename(self):
        """Test local_file_name with unicode characters"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        filename = "données_équité_2024.csv"
        model = Individual_Fairness(local_file_name=filename)
        
        assert model.local_file_name == filename
    
    def test_very_long_filename(self):
        """Test with very long filename"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        filename = "a" * 500 + ".csv"
        model = Individual_Fairness(local_file_name=filename)
        
        assert len(model.local_file_name) == 504
        assert model.local_file_name.endswith(".csv")
    
    def test_dict_with_numeric_string_keys(self):
        """Test dictionary with numeric string keys"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        features = {"1": "value1", "2": "value2", "3": "value3"}
        model = Individual_Fairness(features_dict=features)
        
        assert model.features_dict["1"] == "value1"


class TestTypeValidation:
    """Test Pydantic type validation"""
    
    def test_invalid_features_dict_type(self):
        """Test that non-dict type for features_dict raises error"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        with pytest.raises(ValidationError) as exc_info:
            Individual_Fairness(features_dict="not a dict")
        
        assert "features_dict" in str(exc_info.value).lower()
    
    def test_invalid_local_file_name_type(self):
        """Test that non-string type for local_file_name raises error"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        with pytest.raises(ValidationError) as exc_info:
            Individual_Fairness(local_file_name=12345)
        
        assert "local_file_name" in str(exc_info.value).lower()
    
    def test_list_instead_of_dict(self):
        """Test passing list instead of dict"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        with pytest.raises(ValidationError):
            Individual_Fairness(features_dict=[1, 2, 3])


class TestModelEquality:
    """Test model equality and comparison"""
    
    def test_equal_models(self):
        """Test two models with same data are equal"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        features = {"age": 30}
        model1 = Individual_Fairness(features_dict=features, local_file_name="data.csv")
        model2 = Individual_Fairness(features_dict=features, local_file_name="data.csv")
        
        assert model1.model_dump() == model2.model_dump()
    
    def test_different_models(self):
        """Test two models with different data are not equal"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        model1 = Individual_Fairness(features_dict={"age": 30})
        model2 = Individual_Fairness(features_dict={"age": 40})
        
        assert model1.model_dump() != model2.model_dump()


class TestModelCopy:
    """Test model copy functionality"""
    
    def test_model_copy(self):
        """Test creating a copy of the model"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        features = {"age": 30, "salary": 50000}
        model1 = Individual_Fairness(features_dict=features, local_file_name="data.csv")
        model2 = model1.model_copy()
        
        assert model1.model_dump() == model2.model_dump()
        assert model1 is not model2
    
    def test_model_copy_deep(self):
        """Test deep copy behavior with nested dict"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        features = {"nested": {"key": "value"}}
        model1 = Individual_Fairness(features_dict=features)
        model2 = model1.model_copy(deep=True)
        
        # Modify the copy
        model2.features_dict["nested"]["key"] = "modified"
        
        # Original should be unchanged
        assert model1.features_dict["nested"]["key"] == "value"


class TestPerformance:
    """Test performance-related scenarios"""
    
    def test_create_multiple_instances(self):
        """Test creating many instances"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        models = []
        for i in range(1000):
            model = Individual_Fairness(
                features_dict={"id": i},
                local_file_name=f"file_{i}.csv"
            )
            models.append(model)
        
        assert len(models) == 1000
        assert models[500].features_dict["id"] == 500
    
    def test_serialization_performance(self):
        """Test serialization with large data"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        features = {f"feature_{i}": f"value_{i}" for i in range(1000)}
        model = Individual_Fairness(features_dict=features)
        
        json_str = model.model_dump_json()
        assert isinstance(json_str, str)
        assert len(json_str) > 0


class TestCodeQuality:
    """Test code quality indicators"""
    
    def test_class_is_basemodel(self):
        """Test that Individual_Fairness inherits from BaseModel"""
        from fairness.dao.individual_fairness import Individual_Fairness
        from pydantic import BaseModel
        
        assert issubclass(Individual_Fairness, BaseModel)
    
    def test_model_fields_exist(self):
        """Test that expected fields exist"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        model = Individual_Fairness()
        
        assert hasattr(model, "features_dict")
        assert hasattr(model, "local_file_name")
    
    def test_model_config(self):
        """Test model configuration"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        # Create instance to verify model works correctly
        model = Individual_Fairness(features_dict={"test": 1})
        assert model.features_dict == {"test": 1}
    
    def test_model_schema(self):
        """Test model JSON schema generation"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        schema = Individual_Fairness.model_json_schema()
        
        assert "properties" in schema
        assert "features_dict" in schema["properties"]
        assert "local_file_name" in schema["properties"]


class TestRegression:
    """Test regression scenarios"""
    
    def test_complete_workflow(self):
        """Test complete workflow from creation to serialization"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        # Create model
        features = {"age": 35, "income": 60000, "education": "PhD"}
        model = Individual_Fairness(
            features_dict=features,
            local_file_name="fairness_analysis.csv"
        )
        
        # Serialize to dict
        data_dict = model.model_dump()
        assert data_dict["features_dict"]["age"] == 35
        
        # Serialize to JSON
        json_str = model.model_dump_json()
        assert "fairness_analysis.csv" in json_str
        
        # Recreate from dict
        model2 = Individual_Fairness(**data_dict)
        assert model2.features_dict == features
        assert model2.local_file_name == "fairness_analysis.csv"
    
    def test_partial_update_workflow(self):
        """Test updating model fields"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        model = Individual_Fairness(features_dict={"age": 30})
        
        # Update using model_copy
        updated = model.model_copy(update={"local_file_name": "new_file.csv"})
        
        assert updated.features_dict == {"age": 30}
        assert updated.local_file_name == "new_file.csv"
        assert model.local_file_name is None


class TestIntegrationScenarios:
    """Test integration scenarios"""
    
    def test_json_roundtrip(self):
        """Test JSON serialization and deserialization roundtrip"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        original = Individual_Fairness(
            features_dict={"test": "value", "number": 42},
            local_file_name="test.csv"
        )
        
        # Serialize
        json_str = original.model_dump_json()
        
        # Deserialize
        data = json.loads(json_str)
        restored = Individual_Fairness(**data)
        
        assert restored.features_dict == original.features_dict
        assert restored.local_file_name == original.local_file_name
    
    def test_dict_roundtrip(self):
        """Test dict serialization and deserialization roundtrip"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        original = Individual_Fairness(
            features_dict={"key": "value"},
            local_file_name="file.txt"
        )
        
        # Convert to dict
        data_dict = original.model_dump()
        
        # Recreate from dict
        restored = Individual_Fairness.model_validate(data_dict)
        
        assert restored.model_dump() == original.model_dump()


class TestSecurityAndValidation:
    """Test security and validation aspects"""
    
    def test_extra_fields_ignored(self):
        """Test that extra fields are handled according to Pydantic config"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        # By default, Pydantic ignores extra fields
        model = Individual_Fairness(
            features_dict={"age": 30},
            local_file_name="data.csv",
            extra_field="should_be_ignored"
        )
        
        assert hasattr(model, "features_dict")
        assert hasattr(model, "local_file_name")
    
    def test_null_values_accepted(self):
        """Test that None values are accepted for optional fields"""
        from fairness.dao.individual_fairness import Individual_Fairness
        
        model = Individual_Fairness(features_dict=None, local_file_name=None)
        
        assert model.features_dict is None
        assert model.local_file_name is None
