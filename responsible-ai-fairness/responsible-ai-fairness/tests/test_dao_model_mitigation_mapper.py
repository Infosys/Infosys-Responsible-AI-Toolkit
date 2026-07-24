"""
Test suite for fairness.dao.model_mitigation_mapper module.
Tests MitigationModel Pydantic model including validation,
serialization, deserialization, and edge cases.
"""

import pytest
from pydantic import ValidationError
from fairness.dao.model_mitigation_mapper import MitigationModel


# ========== Fixtures ==========

@pytest.fixture
def valid_mitigation_model_data():
    """Fixture providing valid MitigationModel data."""
    return {
        "modelURL": "https://storage.example.com/models/trained_model.pkl",
        "trainingDatasetURL": "https://storage.example.com/datasets/train_data.csv",
        "testingDatasetURL": "https://storage.example.com/datasets/test_data.csv"
    }


@pytest.fixture
def mitigation_model_instance(valid_mitigation_model_data):
    """Fixture providing a MitigationModel instance."""
    return MitigationModel(**valid_mitigation_model_data)


@pytest.fixture
def local_file_paths():
    """Fixture providing local file path examples."""
    return {
        "modelURL": "/data/models/trained_model.pkl",
        "trainingDatasetURL": "/data/train/dataset.csv",
        "testingDatasetURL": "/data/test/dataset.csv"
    }


@pytest.fixture
def s3_urls():
    """Fixture providing S3 URL examples."""
    return {
        "modelURL": "s3://ml-bucket/models/model.pkl",
        "trainingDatasetURL": "s3://ml-bucket/data/train.csv",
        "testingDatasetURL": "s3://ml-bucket/data/test.csv"
    }


@pytest.fixture
def azure_blob_urls():
    """Fixture providing Azure Blob Storage URL examples."""
    return {
        "modelURL": "https://storageaccount.blob.core.windows.net/models/model.pkl",
        "trainingDatasetURL": "https://storageaccount.blob.core.windows.net/data/train.csv",
        "testingDatasetURL": "https://storageaccount.blob.core.windows.net/data/test.csv"
    }


# ========== Test Initialization ==========

class TestMitigationModelInitialization:
    """Test MitigationModel initialization."""

    def test_init_with_all_required_fields(self, valid_mitigation_model_data):
        """Test initialization with all required fields provided."""
        model = MitigationModel(**valid_mitigation_model_data)
        
        assert model.modelURL == valid_mitigation_model_data["modelURL"]
        assert model.trainingDatasetURL == valid_mitigation_model_data["trainingDatasetURL"]
        assert model.testingDatasetURL == valid_mitigation_model_data["testingDatasetURL"]

    def test_init_with_http_urls(self):
        """Test initialization with HTTP URLs."""
        model = MitigationModel(
            modelURL="http://example.com/model.pkl",
            trainingDatasetURL="http://example.com/train.csv",
            testingDatasetURL="http://example.com/test.csv"
        )
        
        assert model.modelURL == "http://example.com/model.pkl"
        assert model.trainingDatasetURL == "http://example.com/train.csv"
        assert model.testingDatasetURL == "http://example.com/test.csv"

    def test_init_with_https_urls(self):
        """Test initialization with HTTPS URLs."""
        model = MitigationModel(
            modelURL="https://secure.example.com/model.pkl",
            trainingDatasetURL="https://secure.example.com/train.csv",
            testingDatasetURL="https://secure.example.com/test.csv"
        )
        
        assert model.modelURL.startswith("https://")
        assert model.trainingDatasetURL.startswith("https://")
        assert model.testingDatasetURL.startswith("https://")

    def test_init_with_local_file_paths(self, local_file_paths):
        """Test initialization with local file paths."""
        model = MitigationModel(**local_file_paths)
        
        assert model.modelURL == local_file_paths["modelURL"]
        assert model.trainingDatasetURL == local_file_paths["trainingDatasetURL"]
        assert model.testingDatasetURL == local_file_paths["testingDatasetURL"]

    def test_init_with_s3_urls(self, s3_urls):
        """Test initialization with S3 URLs."""
        model = MitigationModel(**s3_urls)
        
        assert model.modelURL.startswith("s3://")
        assert model.trainingDatasetURL.startswith("s3://")
        assert model.testingDatasetURL.startswith("s3://")

    def test_init_with_azure_blob_urls(self, azure_blob_urls):
        """Test initialization with Azure Blob Storage URLs."""
        model = MitigationModel(**azure_blob_urls)
        
        assert "blob.core.windows.net" in model.modelURL
        assert "blob.core.windows.net" in model.trainingDatasetURL
        assert "blob.core.windows.net" in model.testingDatasetURL


# ========== Test Required Fields ==========

class TestMitigationModelRequiredFields:
    """Test MitigationModel required field validation."""

    def test_missing_modelURL_raises_error(self):
        """Test that missing modelURL raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            MitigationModel(
                trainingDatasetURL="https://example.com/train.csv",
                testingDatasetURL="https://example.com/test.csv"
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("modelURL",) for error in errors)
        assert any(error["type"] == "missing" for error in errors)

    def test_missing_trainingDatasetURL_raises_error(self):
        """Test that missing trainingDatasetURL raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            MitigationModel(
                modelURL="https://example.com/model.pkl",
                testingDatasetURL="https://example.com/test.csv"
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("trainingDatasetURL",) for error in errors)
        assert any(error["type"] == "missing" for error in errors)

    def test_missing_testingDatasetURL_raises_error(self):
        """Test that missing testingDatasetURL raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            MitigationModel(
                modelURL="https://example.com/model.pkl",
                trainingDatasetURL="https://example.com/train.csv"
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("testingDatasetURL",) for error in errors)
        assert any(error["type"] == "missing" for error in errors)

    def test_missing_all_fields_raises_error(self):
        """Test that missing all fields raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            MitigationModel()
        
        errors = exc_info.value.errors()
        assert len(errors) == 3
        field_names = {error["loc"][0] for error in errors}
        assert field_names == {"modelURL", "trainingDatasetURL", "testingDatasetURL"}


# ========== Test Field Types ==========

class TestMitigationModelFieldTypes:
    """Test MitigationModel field type validation."""

    def test_modelURL_accepts_string(self):
        """Test modelURL field accepts string values."""
        model = MitigationModel(
            modelURL="valid_string",
            trainingDatasetURL="train",
            testingDatasetURL="test"
        )
        assert isinstance(model.modelURL, str)
        assert model.modelURL == "valid_string"

    def test_trainingDatasetURL_accepts_string(self):
        """Test trainingDatasetURL field accepts string values."""
        model = MitigationModel(
            modelURL="model",
            trainingDatasetURL="valid_train_string",
            testingDatasetURL="test"
        )
        assert isinstance(model.trainingDatasetURL, str)
        assert model.trainingDatasetURL == "valid_train_string"

    def test_testingDatasetURL_accepts_string(self):
        """Test testingDatasetURL field accepts string values."""
        model = MitigationModel(
            modelURL="model",
            trainingDatasetURL="train",
            testingDatasetURL="valid_test_string"
        )
        assert isinstance(model.testingDatasetURL, str)
        assert model.testingDatasetURL == "valid_test_string"

    def test_modelURL_rejects_non_string(self):
        """Test modelURL field rejects non-string values."""
        with pytest.raises(ValidationError):
            MitigationModel(
                modelURL=123,
                trainingDatasetURL="train",
                testingDatasetURL="test"
            )

    def test_trainingDatasetURL_rejects_non_string(self):
        """Test trainingDatasetURL field rejects non-string values."""
        with pytest.raises(ValidationError):
            MitigationModel(
                modelURL="model",
                trainingDatasetURL=["list", "value"],
                testingDatasetURL="test"
            )

    def test_testingDatasetURL_rejects_non_string(self):
        """Test testingDatasetURL field rejects non-string values."""
        with pytest.raises(ValidationError):
            MitigationModel(
                modelURL="model",
                trainingDatasetURL="train",
                testingDatasetURL={"dict": "value"}
            )

    def test_all_fields_reject_none(self):
        """Test that None is not accepted for required string fields."""
        with pytest.raises(ValidationError):
            MitigationModel(
                modelURL=None,
                trainingDatasetURL=None,
                testingDatasetURL=None
            )


# ========== Test Serialization ==========

class TestMitigationModelSerialization:
    """Test MitigationModel serialization."""

    def test_model_dump(self, mitigation_model_instance, valid_mitigation_model_data):
        """Test model_dump() method."""
        data = mitigation_model_instance.model_dump()
        
        assert isinstance(data, dict)
        assert data == valid_mitigation_model_data
        assert "modelURL" in data
        assert "trainingDatasetURL" in data
        assert "testingDatasetURL" in data

    def test_model_dump_json(self, mitigation_model_instance):
        """Test model_dump_json() method."""
        json_str = mitigation_model_instance.model_dump_json()
        
        assert isinstance(json_str, str)
        assert '"modelURL"' in json_str
        assert '"trainingDatasetURL"' in json_str
        assert '"testingDatasetURL"' in json_str

    def test_model_dump_preserves_url_format(self):
        """Test that serialization preserves URL format."""
        original_urls = {
            "modelURL": "https://example.com/model.pkl?version=1&token=abc",
            "trainingDatasetURL": "s3://bucket/path/to/train.csv",
            "testingDatasetURL": "/local/path/to/test.csv"
        }
        model = MitigationModel(**original_urls)
        data = model.model_dump()
        
        assert data["modelURL"] == original_urls["modelURL"]
        assert data["trainingDatasetURL"] == original_urls["trainingDatasetURL"]
        assert data["testingDatasetURL"] == original_urls["testingDatasetURL"]


# ========== Test Deserialization ==========

class TestMitigationModelDeserialization:
    """Test MitigationModel deserialization."""

    def test_model_validate_from_dict(self, valid_mitigation_model_data):
        """Test model_validate() from dictionary."""
        model = MitigationModel.model_validate(valid_mitigation_model_data)
        
        assert model.modelURL == valid_mitigation_model_data["modelURL"]
        assert model.trainingDatasetURL == valid_mitigation_model_data["trainingDatasetURL"]
        assert model.testingDatasetURL == valid_mitigation_model_data["testingDatasetURL"]

    def test_model_validate_json(self):
        """Test model_validate_json() from JSON string."""
        json_str = '''{"modelURL": "https://example.com/model.pkl", "trainingDatasetURL": "https://example.com/train.csv", "testingDatasetURL": "https://example.com/test.csv"}'''
        model = MitigationModel.model_validate_json(json_str)
        
        assert model.modelURL == "https://example.com/model.pkl"
        assert model.trainingDatasetURL == "https://example.com/train.csv"
        assert model.testingDatasetURL == "https://example.com/test.csv"

    def test_serialization_deserialization_roundtrip(self, valid_mitigation_model_data):
        """Test data integrity through serialization and deserialization."""
        original = MitigationModel(**valid_mitigation_model_data)
        
        # Serialize to dict
        data = original.model_dump()
        
        # Deserialize back to model
        restored = MitigationModel.model_validate(data)
        
        assert restored.modelURL == original.modelURL
        assert restored.trainingDatasetURL == original.trainingDatasetURL
        assert restored.testingDatasetURL == original.testingDatasetURL


# ========== Test Edge Cases ==========

class TestMitigationModelEdgeCases:
    """Test MitigationModel edge cases."""

    def test_empty_string_values_are_accepted(self):
        """Test that empty strings are accepted for all fields."""
        model = MitigationModel(
            modelURL="",
            trainingDatasetURL="",
            testingDatasetURL=""
        )
        
        assert model.modelURL == ""
        assert model.trainingDatasetURL == ""
        assert model.testingDatasetURL == ""

    def test_very_long_url_strings(self):
        """Test handling of very long URL strings."""
        long_url = "https://example.com/" + "a" * 1000 + "/file.pkl"
        model = MitigationModel(
            modelURL=long_url,
            trainingDatasetURL="https://example.com/train.csv",
            testingDatasetURL="https://example.com/test.csv"
        )
        
        assert len(model.modelURL) > 1000
        assert model.modelURL == long_url

    def test_urls_with_special_characters(self):
        """Test URLs with special characters."""
        model = MitigationModel(
            modelURL="https://example.com/model%20file.pkl?param=value&other=123",
            trainingDatasetURL="https://example.com/train-data_v2.csv#section",
            testingDatasetURL="https://example.com/test.csv?token=abc123&timestamp=2025-01-01"
        )
        
        assert "%20" in model.modelURL
        assert "&" in model.modelURL
        assert "-" in model.trainingDatasetURL
        assert "_" in model.trainingDatasetURL
        assert "#" in model.trainingDatasetURL

    def test_unicode_characters_in_urls(self):
        """Test URLs with unicode characters."""
        model = MitigationModel(
            modelURL="https://example.com/модель.pkl",
            trainingDatasetURL="https://example.com/训练数据.csv",
            testingDatasetURL="https://example.com/テスト.csv"
        )
        
        assert model.modelURL == "https://example.com/модель.pkl"
        assert model.trainingDatasetURL == "https://example.com/训练数据.csv"
        assert model.testingDatasetURL == "https://example.com/テスト.csv"

    def test_whitespace_in_urls(self):
        """Test URLs with leading/trailing whitespace."""
        model = MitigationModel(
            modelURL="  https://example.com/model.pkl  ",
            trainingDatasetURL="\thttps://example.com/train.csv\t",
            testingDatasetURL="\nhttps://example.com/test.csv\n"
        )
        
        # Pydantic doesn't strip whitespace by default for str fields
        assert model.modelURL == "  https://example.com/model.pkl  "
        assert model.trainingDatasetURL == "\thttps://example.com/train.csv\t"

    def test_relative_file_paths(self):
        """Test relative file paths."""
        model = MitigationModel(
            modelURL="./models/trained_model.pkl",
            trainingDatasetURL="../data/train.csv",
            testingDatasetURL="../../test/data.csv"
        )
        
        assert model.modelURL.startswith("./")
        assert model.trainingDatasetURL.startswith("../")
        assert model.testingDatasetURL.startswith("../../")

    def test_windows_file_paths(self):
        """Test Windows-style file paths."""
        model = MitigationModel(
            modelURL="C:\\Models\\trained_model.pkl",
            trainingDatasetURL="D:\\Data\\train.csv",
            testingDatasetURL="E:\\Test\\test.csv"
        )
        
        assert "\\" in model.modelURL
        assert "\\" in model.trainingDatasetURL
        assert "\\" in model.testingDatasetURL


# ========== Test URL Formats ==========

class TestMitigationModelURLFormats:
    """Test various URL format support."""

    def test_file_protocol_urls(self):
        """Test file:// protocol URLs."""
        model = MitigationModel(
            modelURL="file:///data/models/model.pkl",
            trainingDatasetURL="file:///data/train.csv",
            testingDatasetURL="file:///data/test.csv"
        )
        
        assert model.modelURL.startswith("file://")
        assert model.trainingDatasetURL.startswith("file://")
        assert model.testingDatasetURL.startswith("file://")

    def test_ftp_protocol_urls(self):
        """Test FTP protocol URLs."""
        model = MitigationModel(
            modelURL="ftp://ftp.example.com/models/model.pkl",
            trainingDatasetURL="ftp://ftp.example.com/data/train.csv",
            testingDatasetURL="ftp://ftp.example.com/data/test.csv"
        )
        
        assert model.modelURL.startswith("ftp://")
        assert model.trainingDatasetURL.startswith("ftp://")
        assert model.testingDatasetURL.startswith("ftp://")

    def test_gcs_urls(self):
        """Test Google Cloud Storage URLs."""
        model = MitigationModel(
            modelURL="gs://ml-bucket/models/model.pkl",
            trainingDatasetURL="gs://ml-bucket/data/train.csv",
            testingDatasetURL="gs://ml-bucket/data/test.csv"
        )
        
        assert model.modelURL.startswith("gs://")
        assert model.trainingDatasetURL.startswith("gs://")
        assert model.testingDatasetURL.startswith("gs://")

    def test_hdfs_urls(self):
        """Test HDFS URLs."""
        model = MitigationModel(
            modelURL="hdfs://namenode:8020/models/model.pkl",
            trainingDatasetURL="hdfs://namenode:8020/data/train.csv",
            testingDatasetURL="hdfs://namenode:8020/data/test.csv"
        )
        
        assert model.modelURL.startswith("hdfs://")
        assert "8020" in model.modelURL

    def test_mixed_url_formats(self):
        """Test that different URL formats can be mixed."""
        model = MitigationModel(
            modelURL="s3://bucket/model.pkl",
            trainingDatasetURL="https://example.com/train.csv",
            testingDatasetURL="/local/path/test.csv"
        )
        
        assert model.modelURL.startswith("s3://")
        assert model.trainingDatasetURL.startswith("https://")
        assert model.testingDatasetURL.startswith("/")


# ========== Test Error Handling ==========

class TestMitigationModelErrorHandling:
    """Test error handling and validation errors."""

    def test_invalid_type_for_modelURL(self):
        """Test that invalid type for modelURL raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            MitigationModel(
                modelURL=123,
                trainingDatasetURL="train",
                testingDatasetURL="test"
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("modelURL",) for error in errors)
        assert any(error["type"] == "string_type" for error in errors)

    def test_invalid_type_for_trainingDatasetURL(self):
        """Test that invalid type for trainingDatasetURL raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            MitigationModel(
                modelURL="model",
                trainingDatasetURL=True,
                testingDatasetURL="test"
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("trainingDatasetURL",) for error in errors)

    def test_invalid_type_for_testingDatasetURL(self):
        """Test that invalid type for testingDatasetURL raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            MitigationModel(
                modelURL="model",
                trainingDatasetURL="train",
                testingDatasetURL=3.14
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("testingDatasetURL",) for error in errors)

    def test_multiple_validation_errors(self):
        """Test that multiple validation errors are reported together."""
        with pytest.raises(ValidationError) as exc_info:
            MitigationModel(
                modelURL=123,
                trainingDatasetURL=["list"],
                testingDatasetURL={"dict": "value"}
            )
        
        errors = exc_info.value.errors()
        assert len(errors) == 3

    def test_extra_fields_are_ignored(self):
        """Test that extra fields are ignored by default."""
        model = MitigationModel(
            modelURL="https://example.com/model.pkl",
            trainingDatasetURL="https://example.com/train.csv",
            testingDatasetURL="https://example.com/test.csv",
            extraField="should be ignored"
        )
        
        assert not hasattr(model, "extraField")
        assert model.modelURL == "https://example.com/model.pkl"


# ========== Test Performance ==========

class TestMitigationModelPerformance:
    """Test performance characteristics."""

    def test_create_multiple_instances(self, valid_mitigation_model_data):
        """Test creating multiple MitigationModel instances efficiently."""
        models = [MitigationModel(**valid_mitigation_model_data) for _ in range(1000)]
        
        assert len(models) == 1000
        assert all(m.modelURL == valid_mitigation_model_data["modelURL"] for m in models)

    def test_serialization_performance(self, mitigation_model_instance):
        """Test serialization performance with multiple calls."""
        results = [mitigation_model_instance.model_dump() for _ in range(1000)]
        
        assert len(results) == 1000
        assert all(isinstance(r, dict) for r in results)

    def test_deserialization_performance(self, valid_mitigation_model_data):
        """Test deserialization performance with multiple calls."""
        models = [MitigationModel.model_validate(valid_mitigation_model_data) for _ in range(1000)]
        
        assert len(models) == 1000
        assert all(isinstance(m, MitigationModel) for m in models)


# ========== Test Code Quality ==========

class TestMitigationModelCodeQuality:
    """Test code quality indicators."""

    def test_model_is_pydantic_basemodel_subclass(self):
        """Test that MitigationModel inherits from Pydantic BaseModel."""
        from pydantic import BaseModel
        
        assert issubclass(MitigationModel, BaseModel)

    def test_model_has_correct_annotations(self):
        """Test that model has type annotations."""
        assert hasattr(MitigationModel, '__annotations__')
        
        annotations = MitigationModel.__annotations__
        assert 'modelURL' in annotations
        assert 'trainingDatasetURL' in annotations
        assert 'testingDatasetURL' in annotations
        assert annotations['modelURL'] == str
        assert annotations['trainingDatasetURL'] == str
        assert annotations['testingDatasetURL'] == str

    def test_all_fields_are_required(self):
        """Test that all fields are required (no defaults)."""
        fields = MitigationModel.model_fields
        
        assert fields['modelURL'].is_required()
        assert fields['trainingDatasetURL'].is_required()
        assert fields['testingDatasetURL'].is_required()

    def test_model_schema_structure(self):
        """Test that model schema has correct structure."""
        schema = MitigationModel.model_json_schema()
        
        assert 'properties' in schema
        assert 'modelURL' in schema['properties']
        assert 'trainingDatasetURL' in schema['properties']
        assert 'testingDatasetURL' in schema['properties']
        assert 'required' in schema
        assert len(schema['required']) == 3


# ========== Test Integration ==========

class TestMitigationModelIntegration:
    """Test integration scenarios."""

    def test_model_usage_in_api_context(self):
        """Test model usage in an API-like context."""
        # Simulate receiving data from an API
        api_response = {
            "modelURL": "https://api.example.com/models/123",
            "trainingDatasetURL": "https://api.example.com/datasets/train/456",
            "testingDatasetURL": "https://api.example.com/datasets/test/789"
        }
        
        model = MitigationModel(**api_response)
        
        # Simulate sending data to another service
        output = model.model_dump()
        
        assert output == api_response

    def test_model_with_different_storage_backends(self):
        """Test model with URLs from different storage backends."""
        model = MitigationModel(
            modelURL="s3://ml-models/production/model_v2.pkl",
            trainingDatasetURL="gs://training-data/2025/train_batch_1.csv",
            testingDatasetURL="https://cdn.example.com/datasets/test_v1.csv"
        )
        
        assert "s3://" in model.modelURL
        assert "gs://" in model.trainingDatasetURL
        assert "https://" in model.testingDatasetURL

    def test_json_serialization_for_api_response(self, mitigation_model_instance):
        """Test JSON serialization suitable for API responses."""
        json_output = mitigation_model_instance.model_dump_json()
        
        # Should be valid JSON
        import json
        parsed = json.loads(json_output)
        
        assert isinstance(parsed, dict)
        assert "modelURL" in parsed
        assert "trainingDatasetURL" in parsed
        assert "testingDatasetURL" in parsed


# ========== Test Regression ==========

class TestMitigationModelRegression:
    """Test regression scenarios to ensure no breaking changes."""

    def test_field_names_unchanged(self):
        """Test that field names remain unchanged."""
        model = MitigationModel(
            modelURL="test",
            trainingDatasetURL="test",
            testingDatasetURL="test"
        )
        
        assert hasattr(model, "modelURL")
        assert hasattr(model, "trainingDatasetURL")
        assert hasattr(model, "testingDatasetURL")

    def test_model_copy_creates_independent_instance(self, mitigation_model_instance):
        """Test that model copy creates independent instance."""
        copied = mitigation_model_instance.model_copy()
        
        # Modify original
        mitigation_model_instance.modelURL = "modified"
        
        # Verify copy is unchanged
        assert copied.modelURL != "modified"

    def test_model_equality(self, valid_mitigation_model_data):
        """Test model equality comparison."""
        model1 = MitigationModel(**valid_mitigation_model_data)
        model2 = MitigationModel(**valid_mitigation_model_data)
        
        assert model1.modelURL == model2.modelURL
        assert model1.trainingDatasetURL == model2.trainingDatasetURL
        assert model1.testingDatasetURL == model2.testingDatasetURL

    def test_backward_compatibility_with_dict_unpacking(self, valid_mitigation_model_data):
        """Test backward compatibility with dict unpacking."""
        model = MitigationModel(**valid_mitigation_model_data)
        
        # Should be able to unpack back to dict
        data = {**model.model_dump()}
        
        assert data == valid_mitigation_model_data


# ========== Test Security ==========

class TestMitigationModelSecurity:
    """Test security-related aspects."""

    def test_injection_characters_in_urls(self):
        """Test that injection characters are stored as-is (validation is external)."""
        model = MitigationModel(
            modelURL="https://example.com/model.pkl?'; DROP TABLE users; --",
            trainingDatasetURL="https://example.com/train.csv",
            testingDatasetURL="https://example.com/test.csv"
        )
        
        # Model should store the value as-is; validation is responsibility of consumer
        assert "DROP TABLE" in model.modelURL

    def test_script_tags_in_urls(self):
        """Test that script tags in URLs are stored as-is."""
        model = MitigationModel(
            modelURL="<script>alert('xss')</script>",
            trainingDatasetURL="train",
            testingDatasetURL="test"
        )
        
        # Model stores as-is; XSS protection is responsibility of consumer
        assert "<script>" in model.modelURL

    def test_sensitive_info_in_urls(self):
        """Test handling of sensitive information in URLs."""
        model = MitigationModel(
            modelURL="https://user:password@example.com/model.pkl",
            trainingDatasetURL="https://example.com/train.csv?api_key=secret123",
            testingDatasetURL="s3://bucket/test.csv?aws_access_key_id=AKIA..."
        )
        
        # Model stores credentials as-is; credential management is external
        assert "password" in model.modelURL
        assert "api_key" in model.trainingDatasetURL
        assert "aws_access_key_id" in model.testingDatasetURL


# ========== Test Field Immutability ==========

class TestMitigationModelMutability:
    """Test field mutability and updates."""

    def test_fields_can_be_updated(self, mitigation_model_instance):
        """Test that fields can be updated after initialization."""
        original_url = mitigation_model_instance.modelURL
        
        mitigation_model_instance.modelURL = "https://new.example.com/model.pkl"
        
        assert mitigation_model_instance.modelURL != original_url
        assert mitigation_model_instance.modelURL == "https://new.example.com/model.pkl"

    def test_update_preserves_other_fields(self, mitigation_model_instance):
        """Test that updating one field preserves others."""
        original_train = mitigation_model_instance.trainingDatasetURL
        original_test = mitigation_model_instance.testingDatasetURL
        
        mitigation_model_instance.modelURL = "new_url"
        
        assert mitigation_model_instance.trainingDatasetURL == original_train
        assert mitigation_model_instance.testingDatasetURL == original_test

    def test_model_update_with_dict(self, mitigation_model_instance):
        """Test updating model with dictionary."""
        updates = {"modelURL": "https://updated.example.com/model.pkl"}
        
        for key, value in updates.items():
            setattr(mitigation_model_instance, key, value)
        
        assert mitigation_model_instance.modelURL == updates["modelURL"]
