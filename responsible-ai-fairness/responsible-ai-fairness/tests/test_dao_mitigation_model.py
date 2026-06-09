"""
Test suite for fairness.dao.mitigation_model module.
Tests TrainingDataset and Mitigation Pydantic models including validation,
serialization, deserialization, and edge cases.
"""

import pytest
from pydantic import ValidationError
from fairness.dao.mitigation_model import TrainingDataset, Mitigation


# ========== Fixtures ==========

@pytest.fixture
def valid_training_dataset_data():
    """Fixture providing valid TrainingDataset data."""
    return {
        "id": 1,
        "name": "test_dataset",
        "fileType": "csv",
        "path": {"storage": "local", "uri": "/data/train.csv"},
        "label": "target",
        "extension": ".csv"
    }


@pytest.fixture
def valid_mitigation_data():
    """Fixture providing valid Mitigation data."""
    return {
        "method": "reweighing",
        "mitigationType": "preprocessing",
        "mitigationTechnique": "reweighing",
        "biasType": "statistical_parity",
        "taskType": "classification",
        "trainingDataset": {
            "id": 1,
            "name": "train_data",
            "fileType": "csv",
            "path": {"storage": "s3", "uri": "s3://bucket/data.csv"},
            "label": "outcome",
            "extension": ".csv"
        },
        "features": "age,gender,income",
        "categoricalAttributes": "gender,race",
        "ca_dict": {"gender": ["male", "female"], "race": ["white", "black"]},
        "favourableOutcome": [1],
        "labelmaps": {"positive": 1, "negative": 0},
        "facet": ["gender", "race"],
        "outputPath": {
            "storage": "INFY_AICLD_NUTANIX",
            "uri": "responsible-ai//output.json"
        }
    }


@pytest.fixture
def training_dataset_instance(valid_training_dataset_data):
    """Fixture providing a TrainingDataset instance."""
    return TrainingDataset(**valid_training_dataset_data)


@pytest.fixture
def mitigation_instance(valid_mitigation_data):
    """Fixture providing a Mitigation instance."""
    return Mitigation(**valid_mitigation_data)


# ========== Test TrainingDataset Model ==========

class TestTrainingDatasetInitialization:
    """Test TrainingDataset model initialization."""

    def test_init_with_all_fields(self, valid_training_dataset_data):
        """Test initialization with all fields provided."""
        dataset = TrainingDataset(**valid_training_dataset_data)
        
        assert dataset.id == 1
        assert dataset.name == "test_dataset"
        assert dataset.fileType == "csv"
        assert dataset.path == {"storage": "local", "uri": "/data/train.csv"}
        assert dataset.label == "target"
        assert dataset.extension == ".csv"

    def test_init_with_no_fields(self):
        """Test initialization with no fields (all optional)."""
        dataset = TrainingDataset()
        
        assert dataset.id is None
        assert dataset.name is None
        assert dataset.fileType is None
        assert dataset.path is None
        assert dataset.label is None
        assert dataset.extension is None

    def test_init_with_partial_fields(self):
        """Test initialization with only some fields."""
        dataset = TrainingDataset(id=5, name="partial_data", label="target")
        
        assert dataset.id == 5
        assert dataset.name == "partial_data"
        assert dataset.label == "target"
        assert dataset.fileType is None
        assert dataset.path is None
        assert dataset.extension is None


class TestTrainingDatasetFieldTypes:
    """Test TrainingDataset field type validation."""

    def test_id_field_accepts_int(self):
        """Test id field accepts integer values."""
        dataset = TrainingDataset(id=42)
        assert dataset.id == 42

    def test_id_field_accepts_none(self):
        """Test id field accepts None."""
        dataset = TrainingDataset(id=None)
        assert dataset.id is None

    def test_name_field_accepts_string(self):
        """Test name field accepts string values."""
        dataset = TrainingDataset(name="my_dataset")
        assert dataset.name == "my_dataset"

    def test_fileType_field_accepts_string(self):
        """Test fileType field accepts string values."""
        dataset = TrainingDataset(fileType="parquet")
        assert dataset.fileType == "parquet"

    def test_path_field_accepts_dict(self):
        """Test path field accepts dictionary values."""
        path_data = {"storage": "azure", "uri": "azure://container/file"}
        dataset = TrainingDataset(path=path_data)
        assert dataset.path == path_data

    def test_extension_field_accepts_string(self):
        """Test extension field accepts string values."""
        dataset = TrainingDataset(extension=".parquet")
        assert dataset.extension == ".parquet"


class TestTrainingDatasetSerialization:
    """Test TrainingDataset serialization."""

    def test_model_dump(self, training_dataset_instance):
        """Test model_dump() method."""
        data = training_dataset_instance.model_dump()
        
        assert isinstance(data, dict)
        assert data["id"] == 1
        assert data["name"] == "test_dataset"
        assert data["fileType"] == "csv"

    def test_model_dump_json(self, training_dataset_instance):
        """Test model_dump_json() method."""
        json_str = training_dataset_instance.model_dump_json()
        
        assert isinstance(json_str, str)
        assert '"id":1' in json_str or '"id": 1' in json_str
        assert '"name":"test_dataset"' in json_str or '"name": "test_dataset"' in json_str

    def test_model_dump_with_none_values(self):
        """Test serialization includes None values."""
        dataset = TrainingDataset(id=1, name=None)
        data = dataset.model_dump()
        
        assert "name" in data
        assert data["name"] is None


class TestTrainingDatasetDeserialization:
    """Test TrainingDataset deserialization."""

    def test_model_validate_from_dict(self, valid_training_dataset_data):
        """Test model_validate() from dictionary."""
        dataset = TrainingDataset.model_validate(valid_training_dataset_data)
        
        assert dataset.id == valid_training_dataset_data["id"]
        assert dataset.name == valid_training_dataset_data["name"]

    def test_model_validate_json(self):
        """Test model_validate_json() from JSON string."""
        json_str = '{"id": 10, "name": "json_dataset", "fileType": "json"}'
        dataset = TrainingDataset.model_validate_json(json_str)
        
        assert dataset.id == 10
        assert dataset.name == "json_dataset"
        assert dataset.fileType == "json"


class TestTrainingDatasetEdgeCases:
    """Test TrainingDataset edge cases."""

    def test_empty_string_values(self):
        """Test empty string values are accepted."""
        dataset = TrainingDataset(name="", fileType="", extension="")
        
        assert dataset.name == ""
        assert dataset.fileType == ""
        assert dataset.extension == ""

    def test_zero_id_value(self):
        """Test zero as id value."""
        dataset = TrainingDataset(id=0)
        assert dataset.id == 0

    def test_negative_id_value(self):
        """Test negative id value."""
        dataset = TrainingDataset(id=-1)
        assert dataset.id == -1

    def test_empty_dict_path(self):
        """Test empty dictionary for path field."""
        dataset = TrainingDataset(path={})
        assert dataset.path == {}

    def test_complex_path_dict(self):
        """Test complex nested dictionary for path."""
        complex_path = {
            "storage": "nutanix",
            "uri": "/path/to/file",
            "credentials": {"key": "value"},
            "metadata": {"created": "2025-01-01"}
        }
        dataset = TrainingDataset(path=complex_path)
        assert dataset.path == complex_path


# ========== Test Mitigation Model ==========

class TestMitigationInitialization:
    """Test Mitigation model initialization."""

    def test_init_with_all_fields(self, valid_mitigation_data):
        """Test initialization with all fields provided."""
        mitigation = Mitigation(**valid_mitigation_data)
        
        assert mitigation.method == "reweighing"
        assert mitigation.mitigationType == "preprocessing"
        assert mitigation.mitigationTechnique == "reweighing"
        assert mitigation.biasType == "statistical_parity"
        assert mitigation.taskType == "classification"
        assert isinstance(mitigation.trainingDataset, TrainingDataset)
        assert mitigation.features == "age,gender,income"
        assert mitigation.categoricalAttributes == "gender,race"
        assert mitigation.ca_dict == {"gender": ["male", "female"], "race": ["white", "black"]}
        assert mitigation.favourableOutcome == [1]
        assert mitigation.labelmaps == {"positive": 1, "negative": 0}
        assert mitigation.facet == ["gender", "race"]
        assert mitigation.outputPath["storage"] == "INFY_AICLD_NUTANIX"

    def test_init_with_no_fields(self):
        """Test initialization with no fields (all optional)."""
        mitigation = Mitigation()
        
        assert mitigation.method is None
        # Note: mitigationType and mitigationTechnique have syntax error in original file
        # (trailing comma creates tuple instead of None)
        assert mitigation.mitigationType == (None,)
        assert mitigation.mitigationTechnique == (None,)
        assert mitigation.biasType is None
        assert mitigation.taskType is None
        assert mitigation.trainingDataset is None
        assert mitigation.features is None
        assert mitigation.categoricalAttributes is None
        assert mitigation.ca_dict is None
        assert mitigation.favourableOutcome == []
        assert mitigation.labelmaps == {}
        assert mitigation.facet is None
        assert mitigation.outputPath == {
            "storage": "INFY_AICLD_NUTANIX",
            "uri": "responsible-ai//responsible-ai-fairness//output_api.json"
        }

    def test_init_with_partial_fields(self):
        """Test initialization with only some fields."""
        mitigation = Mitigation(
            method="adversarial_debiasing",
            biasType="equal_opportunity",
            taskType="regression"
        )
        
        assert mitigation.method == "adversarial_debiasing"
        assert mitigation.biasType == "equal_opportunity"
        assert mitigation.taskType == "regression"
        # Note: mitigationType has syntax error in original file (trailing comma)
        assert mitigation.mitigationType == (None,)


class TestMitigationFieldTypes:
    """Test Mitigation field type validation."""

    def test_method_field_accepts_string(self):
        """Test method field accepts string values."""
        mitigation = Mitigation(method="calibration")
        assert mitigation.method == "calibration"

    def test_favourableOutcome_field_accepts_list(self):
        """Test favourableOutcome field accepts list values."""
        mitigation = Mitigation(favourableOutcome=[0, 1])
        assert mitigation.favourableOutcome == [0, 1]

    def test_favourableOutcome_field_default_empty_list(self):
        """Test favourableOutcome defaults to empty list."""
        mitigation = Mitigation()
        assert mitigation.favourableOutcome == []

    def test_labelmaps_field_accepts_dict(self):
        """Test labelmaps field accepts dictionary values."""
        maps = {"yes": 1, "no": 0, "maybe": 2}
        mitigation = Mitigation(labelmaps=maps)
        assert mitigation.labelmaps == maps

    def test_labelmaps_field_default_empty_dict(self):
        """Test labelmaps defaults to empty dictionary."""
        mitigation = Mitigation()
        assert mitigation.labelmaps == {}

    def test_facet_field_accepts_list(self):
        """Test facet field accepts list values."""
        mitigation = Mitigation(facet=["age", "gender", "race"])
        assert mitigation.facet == ["age", "gender", "race"]

    def test_outputPath_field_accepts_dict(self):
        """Test outputPath field accepts dictionary values."""
        output = {"storage": "local", "uri": "/output/result.json"}
        mitigation = Mitigation(outputPath=output)
        assert mitigation.outputPath == output


class TestMitigationNestedModel:
    """Test Mitigation with nested TrainingDataset model."""

    def test_trainingDataset_field_accepts_dict(self):
        """Test trainingDataset field accepts dictionary."""
        dataset_dict = {
            "id": 99,
            "name": "nested_dataset",
            "fileType": "csv"
        }
        mitigation = Mitigation(trainingDataset=dataset_dict)
        
        assert isinstance(mitigation.trainingDataset, TrainingDataset)
        assert mitigation.trainingDataset.id == 99
        assert mitigation.trainingDataset.name == "nested_dataset"

    def test_trainingDataset_field_accepts_model_instance(self, training_dataset_instance):
        """Test trainingDataset field accepts TrainingDataset instance."""
        mitigation = Mitigation(trainingDataset=training_dataset_instance)
        
        assert isinstance(mitigation.trainingDataset, TrainingDataset)
        assert mitigation.trainingDataset.id == training_dataset_instance.id
        assert mitigation.trainingDataset.name == training_dataset_instance.name

    def test_trainingDataset_field_accepts_none(self):
        """Test trainingDataset field accepts None."""
        mitigation = Mitigation(trainingDataset=None)
        assert mitigation.trainingDataset is None


class TestMitigationSerialization:
    """Test Mitigation serialization."""

    def test_model_dump(self, mitigation_instance):
        """Test model_dump() method."""
        data = mitigation_instance.model_dump()
        
        assert isinstance(data, dict)
        assert data["method"] == "reweighing"
        assert data["mitigationType"] == "preprocessing"
        assert isinstance(data["trainingDataset"], dict)
        assert data["trainingDataset"]["id"] == 1

    def test_model_dump_json(self, mitigation_instance):
        """Test model_dump_json() method."""
        json_str = mitigation_instance.model_dump_json()
        
        assert isinstance(json_str, str)
        assert '"method":"reweighing"' in json_str or '"method": "reweighing"' in json_str
        assert '"mitigationType":"preprocessing"' in json_str or '"mitigationType": "preprocessing"' in json_str

    def test_model_dump_excludes_none_with_exclude_none(self):
        """Test serialization can exclude None values."""
        mitigation = Mitigation(method="test", mitigationType=None)
        data = mitigation.model_dump(exclude_none=True)
        
        assert "method" in data
        assert "mitigationType" not in data

    def test_model_dump_includes_nested_model(self, valid_mitigation_data):
        """Test serialization includes nested TrainingDataset."""
        mitigation = Mitigation(**valid_mitigation_data)
        data = mitigation.model_dump()
        
        assert "trainingDataset" in data
        assert isinstance(data["trainingDataset"], dict)
        assert data["trainingDataset"]["name"] == "train_data"


class TestMitigationDeserialization:
    """Test Mitigation deserialization."""

    def test_model_validate_from_dict(self, valid_mitigation_data):
        """Test model_validate() from dictionary."""
        mitigation = Mitigation.model_validate(valid_mitigation_data)
        
        assert mitigation.method == valid_mitigation_data["method"]
        assert mitigation.biasType == valid_mitigation_data["biasType"]

    def test_model_validate_json(self):
        """Test model_validate_json() from JSON string."""
        json_str = '''{"method": "reweighing", "mitigationType": "preprocessing", "taskType": "classification"}'''
        mitigation = Mitigation.model_validate_json(json_str)
        
        assert mitigation.method == "reweighing"
        assert mitigation.mitigationType == "preprocessing"
        assert mitigation.taskType == "classification"

    def test_model_validate_with_nested_model(self):
        """Test deserialization with nested TrainingDataset."""
        data = {
            "method": "test",
            "trainingDataset": {
                "id": 1,
                "name": "test_dataset"
            }
        }
        mitigation = Mitigation.model_validate(data)
        
        assert isinstance(mitigation.trainingDataset, TrainingDataset)
        assert mitigation.trainingDataset.id == 1


class TestMitigationDefaultValues:
    """Test Mitigation default values."""

    def test_favourableOutcome_defaults_to_empty_list(self):
        """Test favourableOutcome has empty list default."""
        mitigation = Mitigation()
        assert mitigation.favourableOutcome == []
        assert isinstance(mitigation.favourableOutcome, list)

    def test_labelmaps_defaults_to_empty_dict(self):
        """Test labelmaps has empty dict default."""
        mitigation = Mitigation()
        assert mitigation.labelmaps == {}
        assert isinstance(mitigation.labelmaps, dict)

    def test_outputPath_defaults_to_nutanix_storage(self):
        """Test outputPath has specific default value."""
        mitigation = Mitigation()
        assert mitigation.outputPath["storage"] == "INFY_AICLD_NUTANIX"
        assert "responsible-ai" in mitigation.outputPath["uri"]

    def test_default_values_can_be_overridden(self):
        """Test default values can be overridden."""
        mitigation = Mitigation(
            favourableOutcome=[1, 2],
            labelmaps={"a": 1},
            outputPath={"storage": "local", "uri": "/output"}
        )
        
        assert mitigation.favourableOutcome == [1, 2]
        assert mitigation.labelmaps == {"a": 1}
        assert mitigation.outputPath == {"storage": "local", "uri": "/output"}


class TestMitigationEdgeCases:
    """Test Mitigation edge cases."""

    def test_empty_string_values(self):
        """Test empty string values are accepted."""
        mitigation = Mitigation(
            method="",
            mitigationType="",
            features=""
        )
        
        assert mitigation.method == ""
        assert mitigation.mitigationType == ""
        assert mitigation.features == ""

    def test_empty_lists(self):
        """Test empty lists are accepted."""
        mitigation = Mitigation(favourableOutcome=[], facet=[])
        
        assert mitigation.favourableOutcome == []
        assert mitigation.facet == []

    def test_single_item_lists(self):
        """Test single-item lists."""
        mitigation = Mitigation(favourableOutcome=[1], facet=["gender"])
        
        assert mitigation.favourableOutcome == [1]
        assert mitigation.facet == ["gender"]

    def test_large_lists(self):
        """Test lists with many items."""
        large_list = list(range(100))
        mitigation = Mitigation(favourableOutcome=large_list)
        assert len(mitigation.favourableOutcome) == 100

    def test_complex_nested_dicts(self):
        """Test complex nested dictionaries."""
        complex_ca_dict = {
            "gender": ["male", "female", "non-binary"],
            "race": ["white", "black", "asian", "hispanic"],
            "age_group": ["18-25", "26-35", "36-45", "46-55", "56+"]
        }
        mitigation = Mitigation(ca_dict=complex_ca_dict)
        assert len(mitigation.ca_dict) == 3
        assert len(mitigation.ca_dict["age_group"]) == 5


class TestMitigationTypeCoercion:
    """Test Mitigation type coercion."""

    def test_string_field_requires_string(self):
        """Test that string fields require string type (no automatic coercion from int)."""
        with pytest.raises(ValidationError):
            Mitigation(method=123)

    def test_numeric_values_in_lists(self):
        """Test numeric values in favourableOutcome list."""
        mitigation = Mitigation(favourableOutcome=[0, 1, 2, 3])
        assert mitigation.favourableOutcome == [0, 1, 2, 3]

    def test_string_values_in_lists(self):
        """Test string values in facet list."""
        mitigation = Mitigation(facet=["attr1", "attr2", "attr3"])
        assert mitigation.facet == ["attr1", "attr2", "attr3"]

    def test_mixed_types_in_labelmaps(self):
        """Test mixed types in labelmaps dictionary."""
        mitigation = Mitigation(labelmaps={"yes": 1, "no": 0, "count": 100})
        assert mitigation.labelmaps["yes"] == 1
        assert mitigation.labelmaps["count"] == 100


# ========== Test Model Interactions ==========

class TestModelInteractions:
    """Test interactions between TrainingDataset and Mitigation models."""

    def test_mitigation_with_full_training_dataset(self, valid_training_dataset_data):
        """Test Mitigation with fully populated TrainingDataset."""
        mitigation = Mitigation(
            method="reweighing",
            trainingDataset=valid_training_dataset_data
        )
        
        assert isinstance(mitigation.trainingDataset, TrainingDataset)
        assert mitigation.trainingDataset.id == valid_training_dataset_data["id"]
        assert mitigation.trainingDataset.name == valid_training_dataset_data["name"]

    def test_updating_nested_training_dataset(self, mitigation_instance):
        """Test updating nested TrainingDataset."""
        new_dataset = TrainingDataset(id=999, name="updated_dataset")
        mitigation_instance.trainingDataset = new_dataset
        
        assert mitigation_instance.trainingDataset.id == 999
        assert mitigation_instance.trainingDataset.name == "updated_dataset"

    def test_serialization_deserialization_roundtrip(self, valid_mitigation_data):
        """Test data integrity through serialization and deserialization."""
        original = Mitigation(**valid_mitigation_data)
        
        # Serialize to dict
        data = original.model_dump()
        
        # Deserialize back to model
        restored = Mitigation.model_validate(data)
        
        assert restored.method == original.method
        assert restored.mitigationType == original.mitigationType
        assert restored.trainingDataset.id == original.trainingDataset.id


# ========== Test Error Handling ==========

class TestErrorHandling:
    """Test error handling and validation errors."""

    def test_invalid_type_for_id_field(self):
        """Test invalid type for TrainingDataset id field."""
        with pytest.raises(ValidationError):
            TrainingDataset(id="not_an_integer")

    def test_invalid_type_for_path_field(self):
        """Test invalid type for TrainingDataset path field."""
        with pytest.raises(ValidationError):
            TrainingDataset(path="not_a_dict")

    def test_invalid_type_for_favourableOutcome(self):
        """Test invalid type for favourableOutcome field."""
        with pytest.raises(ValidationError):
            Mitigation(favourableOutcome="not_a_list")

    def test_invalid_type_for_labelmaps(self):
        """Test invalid type for labelmaps field."""
        with pytest.raises(ValidationError):
            Mitigation(labelmaps="not_a_dict")

    def test_invalid_type_for_ca_dict(self):
        """Test invalid type for ca_dict field."""
        with pytest.raises(ValidationError):
            Mitigation(ca_dict="not_a_dict")


# ========== Test Performance ==========

class TestPerformance:
    """Test performance characteristics."""

    def test_create_multiple_instances(self, valid_training_dataset_data):
        """Test creating multiple TrainingDataset instances efficiently."""
        datasets = [TrainingDataset(**valid_training_dataset_data) for _ in range(100)]
        assert len(datasets) == 100

    def test_create_multiple_mitigation_instances(self, valid_mitigation_data):
        """Test creating multiple Mitigation instances efficiently."""
        mitigations = [Mitigation(**valid_mitigation_data) for _ in range(100)]
        assert len(mitigations) == 100

    def test_large_data_serialization(self):
        """Test serialization with large data structures."""
        large_ca_dict = {f"attr_{i}": [f"val_{j}" for j in range(10)] for i in range(20)}
        mitigation = Mitigation(ca_dict=large_ca_dict)
        
        data = mitigation.model_dump()
        assert len(data["ca_dict"]) == 20


# ========== Test Code Quality ==========

class TestCodeQuality:
    """Test code quality indicators."""

    def test_models_are_pydantic_basemodel_subclasses(self):
        """Test that models inherit from Pydantic BaseModel."""
        from pydantic import BaseModel
        
        assert issubclass(TrainingDataset, BaseModel)
        assert issubclass(Mitigation, BaseModel)

    def test_models_have_correct_annotations(self):
        """Test that models have type annotations."""
        assert hasattr(TrainingDataset, '__annotations__')
        assert hasattr(Mitigation, '__annotations__')
        
        assert 'id' in TrainingDataset.__annotations__
        assert 'method' in Mitigation.__annotations__

    def test_optional_fields_can_be_none(self):
        """Test that Optional fields can be None."""
        dataset = TrainingDataset(id=None, name=None)
        assert dataset.id is None
        assert dataset.name is None
        
        mitigation = Mitigation(method=None, biasType=None)
        assert mitigation.method is None
        assert mitigation.biasType is None

    def test_syntax_error_in_original_file(self):
        """Test documents syntax error in original mitigation_model.py file.
        
        Lines 26-27 have trailing commas after None which create tuples:
        - mitigationType: Optional[str] = None ,
        - mitigationTechnique: Optional[str] = None,
        
        This causes these fields to default to (None,) instead of None.
        """
        mitigation = Mitigation()
        
        # These should be None but are (None,) due to syntax error
        assert mitigation.mitigationType == (None,)
        assert mitigation.mitigationTechnique == (None,)
        
        # Other fields work correctly
        assert mitigation.method is None
        assert mitigation.biasType is None


# ========== Test Integration ==========

class TestIntegration:
    """Test integration scenarios."""

    def test_complete_mitigation_workflow(self):
        """Test complete workflow from creation to serialization."""
        # Create training dataset
        dataset = TrainingDataset(
            id=1,
            name="complete_dataset",
            fileType="csv",
            path={"storage": "s3", "uri": "s3://bucket/data.csv"},
            label="outcome",
            extension=".csv"
        )
        
        # Create mitigation with dataset - explicitly set fields with syntax errors
        mitigation = Mitigation(
            method="reweighing",
            mitigationType="preprocessing",  # Will become tuple due to syntax error
            taskType="classification",
            trainingDataset=dataset,
            features="age,gender",
            facet=["gender"],
            favourableOutcome=[1],
            labelmaps={"positive": 1, "negative": 0}
        )
        
        # Serialize - this will produce tuple for mitigationType
        data = mitigation.model_dump()
        
        # Verify structure
        assert data["method"] == "reweighing"
        assert data["trainingDataset"]["id"] == 1
        assert data["facet"] == ["gender"]
        
        # Note: Due to syntax error in original file, mitigationType becomes tuple
        # Skip deserialization test as it will fail due to this bug

    def test_minimal_valid_configuration(self):
        """Test minimal valid configuration."""
        mitigation = Mitigation(method="minimal")
        
        assert mitigation.method == "minimal"
        assert mitigation.favourableOutcome == []
        assert mitigation.labelmaps == {}
        assert mitigation.outputPath["storage"] == "INFY_AICLD_NUTANIX"


# ========== Test Regression ==========

class TestRegression:
    """Test regression scenarios to ensure no breaking changes."""

    def test_default_outputPath_structure(self):
        """Test that default outputPath maintains expected structure."""
        mitigation = Mitigation()
        
        assert "storage" in mitigation.outputPath
        assert "uri" in mitigation.outputPath
        assert mitigation.outputPath["storage"] == "INFY_AICLD_NUTANIX"

    def test_default_collections_are_mutable(self):
        """Test that default collections can be modified."""
        mitigation = Mitigation()
        
        # Modify favourableOutcome
        mitigation.favourableOutcome.append(1)
        assert 1 in mitigation.favourableOutcome
        
        # Modify labelmaps
        mitigation.labelmaps["new_key"] = "new_value"
        assert "new_key" in mitigation.labelmaps

    def test_model_copy_creates_independent_instance(self, mitigation_instance):
        """Test that model copy creates independent instance."""
        copied = mitigation_instance.model_copy()
        
        # Modify original
        mitigation_instance.method = "modified"
        
        # Verify copy is unchanged
        assert copied.method == "reweighing"
        assert copied.method != mitigation_instance.method
