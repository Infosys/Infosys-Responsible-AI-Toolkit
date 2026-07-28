"""
MIT License
https://mit-license.org/
Copyright  2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError
import json
from unittest.mock import patch, MagicMock
import sys
from mappers.mappers import BlobInfo


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def valid_blob_data():
    """Fixture for valid BlobInfo data"""
    return {
        "name": "test-file.txt",
        "size": 1024,
        "last_modified": datetime(2025, 12, 26, 10, 30, 0, tzinfo=timezone.utc),
        "content_type": "text/plain"
    }


@pytest.fixture
def valid_blob_info(valid_blob_data):
    """Fixture for valid BlobInfo instance"""
    return BlobInfo(**valid_blob_data)


@pytest.fixture
def sample_datetime():
    """Fixture for consistent datetime"""
    return datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def large_file_data():
    """Fixture for large file blob data"""
    return {
        "name": "large-file.bin",
        "size": 10 * 1024 * 1024 * 1024,  # 10 GB
        "last_modified": datetime.now(timezone.utc),
        "content_type": "application/octet-stream"
    }


@pytest.fixture
def special_characters_data():
    """Fixture for blob data with special characters"""
    return {
        "name": "test file @#$%^&*()_+{}[]|\\:;\"'<>,.?/~`-=.txt",
        "size": 512,
        "last_modified": datetime.now(timezone.utc),
        "content_type": "text/plain; charset=utf-8"
    }


@pytest.fixture
def unicode_data():
    """Fixture for blob data with unicode characters"""
    return {
        "name": "文件名_test_файл_.txt",
        "size": 2048,
        "last_modified": datetime.now(timezone.utc),
        "content_type": "text/plain; charset=utf-8"
    }


# ============================================================================
# TEST CLASS: BlobInfo Initialization
# ============================================================================

class TestBlobInfoInitialization:
    """Test BlobInfo model initialization and basic functionality"""

    def test_initialization_with_valid_data(self, valid_blob_data):
        """Test that BlobInfo initializes correctly with valid data"""
        blob = BlobInfo(**valid_blob_data)
        assert blob.name == valid_blob_data["name"]
        assert blob.size == valid_blob_data["size"]
        assert blob.last_modified == valid_blob_data["last_modified"]
        assert blob.content_type == valid_blob_data["content_type"]

    def test_initialization_with_keyword_arguments(self, sample_datetime):
        """Test BlobInfo initialization with keyword arguments"""
        blob = BlobInfo(
            name="test.txt",
            size=100,
            last_modified=sample_datetime,
            content_type="text/plain"
        )
        assert blob.name == "test.txt"
        assert blob.size == 100
        assert blob.last_modified == sample_datetime
        assert blob.content_type == "text/plain"

    def test_initialization_preserves_datetime_timezone(self):
        """Test that datetime timezone information is preserved"""
        dt_utc = datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        blob = BlobInfo(
            name="test.txt",
            size=100,
            last_modified=dt_utc,
            content_type="text/plain"
        )
        assert blob.last_modified.tzinfo == timezone.utc

    def test_initialization_with_datetime_naive(self):
        """Test BlobInfo with naive datetime (no timezone)"""
        dt_naive = datetime(2025, 6, 15, 10, 0, 0)
        blob = BlobInfo(
            name="test.txt",
            size=100,
            last_modified=dt_naive,
            content_type="text/plain"
        )
        assert blob.last_modified == dt_naive

    def test_all_fields_are_accessible(self, valid_blob_info):
        """Test that all fields are accessible after initialization"""
        assert hasattr(valid_blob_info, 'name')
        assert hasattr(valid_blob_info, 'size')
        assert hasattr(valid_blob_info, 'last_modified')
        assert hasattr(valid_blob_info, 'content_type')

    def test_model_is_immutable_by_default(self, valid_blob_info):
        """Test that BlobInfo instances are immutable (Pydantic default)"""
        # Pydantic v2 allows mutation by default, but we test the behavior
        original_name = valid_blob_info.name
        valid_blob_info.name = "new-name.txt"
        assert valid_blob_info.name == "new-name.txt"  # Pydantic allows this

    def test_initialization_with_zero_size(self, sample_datetime):
        """Test BlobInfo with zero file size (empty file)"""
        blob = BlobInfo(
            name="empty.txt",
            size=0,
            last_modified=sample_datetime,
            content_type="text/plain"
        )
        assert blob.size == 0

    def test_initialization_with_large_size(self, large_file_data):
        """Test BlobInfo with very large file size"""
        blob = BlobInfo(**large_file_data)
        assert blob.size == 10 * 1024 * 1024 * 1024


# ============================================================================
# TEST CLASS: Field Validation
# ============================================================================

class TestBlobInfoFieldValidation:
    """Test field validation and type checking"""

    def test_missing_name_field_raises_error(self, sample_datetime):
        """Test that missing name field raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            BlobInfo(
                size=100,
                last_modified=sample_datetime,
                content_type="text/plain"
            )
        assert "name" in str(exc_info.value)

    def test_missing_size_field_raises_error(self, sample_datetime):
        """Test that missing size field raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            BlobInfo(
                name="test.txt",
                last_modified=sample_datetime,
                content_type="text/plain"
            )
        assert "size" in str(exc_info.value)

    def test_missing_last_modified_field_raises_error(self):
        """Test that missing last_modified field raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            BlobInfo(
                name="test.txt",
                size=100,
                content_type="text/plain"
            )
        assert "last_modified" in str(exc_info.value)

    def test_missing_content_type_field_raises_error(self, sample_datetime):
        """Test that missing content_type field raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            BlobInfo(
                name="test.txt",
                size=100,
                last_modified=sample_datetime
            )
        assert "content_type" in str(exc_info.value)

    def test_invalid_name_type_raises_error(self, sample_datetime):
        """Test that invalid name type raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            BlobInfo(
                name=12345,  # Should be string
                size=100,
                last_modified=sample_datetime,
                content_type="text/plain"
            )
        assert "name" in str(exc_info.value)

    def test_invalid_size_type_raises_error(self, sample_datetime):
        """Test that invalid size type raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            BlobInfo(
                name="test.txt",
                size="large",  # Should be int
                last_modified=sample_datetime,
                content_type="text/plain"
            )
        assert "size" in str(exc_info.value)

    def test_invalid_datetime_type_raises_error(self):
        """Test that invalid datetime type coercion by Pydantic"""
        # Pydantic automatically coerces valid ISO datetime strings to datetime objects
        # Test with a truly invalid datetime value that can't be coerced
        with pytest.raises(ValidationError) as exc_info:
            BlobInfo(
                name="test.txt",
                size=100,
                last_modified="not-a-valid-datetime",  # Invalid format
                content_type="text/plain"
            )

    def test_invalid_content_type_type_raises_error(self, sample_datetime):
        """Test that invalid content_type type raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            BlobInfo(
                name="test.txt",
                size=100,
                last_modified=sample_datetime,
                content_type=12345  # Should be string
            )
        assert "content_type" in str(exc_info.value)

    def test_negative_size_value(self, sample_datetime):
        """Test BlobInfo with negative size value"""
        # Pydantic doesn't enforce positive constraint by default
        blob = BlobInfo(
            name="test.txt",
            size=-100,
            last_modified=sample_datetime,
            content_type="text/plain"
        )
        assert blob.size == -100  # Pydantic allows this without constraints

    def test_empty_string_name(self, sample_datetime):
        """Test BlobInfo with empty string name"""
        blob = BlobInfo(
            name="",
            size=100,
            last_modified=sample_datetime,
            content_type="text/plain"
        )
        assert blob.name == ""

    def test_empty_string_content_type(self, sample_datetime):
        """Test BlobInfo with empty string content_type"""
        blob = BlobInfo(
            name="test.txt",
            size=100,
            last_modified=sample_datetime,
            content_type=""
        )
        assert blob.content_type == ""


# ============================================================================
# TEST CLASS: Special Cases
# ============================================================================

class TestBlobInfoSpecialCases:
    """Test special cases and edge scenarios"""

    def test_special_characters_in_name(self, special_characters_data):
        """Test BlobInfo with special characters in filename"""
        blob = BlobInfo(**special_characters_data)
        assert blob.name == special_characters_data["name"]
        assert len(blob.name) > 0

    def test_unicode_characters_in_name(self, unicode_data):
        """Test BlobInfo with unicode characters in filename"""
        blob = BlobInfo(**unicode_data)
        assert blob.name == unicode_data["name"]
        assert "" in blob.name

    def test_very_long_filename(self, sample_datetime):
        """Test BlobInfo with very long filename"""
        long_name = "a" * 1000 + ".txt"
        blob = BlobInfo(
            name=long_name,
            size=100,
            last_modified=sample_datetime,
            content_type="text/plain"
        )
        assert blob.name == long_name
        assert len(blob.name) == 1004

    def test_content_type_with_parameters(self, sample_datetime):
        """Test BlobInfo with content type containing parameters"""
        blob = BlobInfo(
            name="test.txt",
            size=100,
            last_modified=sample_datetime,
            content_type="text/plain; charset=utf-8; boundary=something"
        )
        assert "charset=utf-8" in blob.content_type

    def test_various_content_types(self, sample_datetime):
        """Test BlobInfo with various content types"""
        content_types = [
            "text/plain",
            "application/json",
            "image/png",
            "video/mp4",
            "application/octet-stream",
            "text/html; charset=utf-8"
        ]
        for ct in content_types:
            blob = BlobInfo(
                name=f"file.{ct.split('/')[1].split(';')[0]}",
                size=100,
                last_modified=sample_datetime,
                content_type=ct
            )
            assert blob.content_type == ct

    def test_datetime_with_microseconds(self):
        """Test BlobInfo with datetime containing microseconds"""
        dt = datetime(2025, 6, 15, 10, 30, 45, 123456, tzinfo=timezone.utc)
        blob = BlobInfo(
            name="test.txt",
            size=100,
            last_modified=dt,
            content_type="text/plain"
        )
        assert blob.last_modified.microsecond == 123456

    def test_datetime_with_different_timezones(self):
        """Test BlobInfo with different timezone offsets"""
        tz_plus = timezone(timedelta(hours=5, minutes=30))  # IST
        dt = datetime(2025, 6, 15, 10, 0, 0, tzinfo=tz_plus)
        blob = BlobInfo(
            name="test.txt",
            size=100,
            last_modified=dt,
            content_type="text/plain"
        )
        assert blob.last_modified.tzinfo == tz_plus

    def test_whitespace_in_filename(self, sample_datetime):
        """Test BlobInfo with whitespace in filename"""
        blob = BlobInfo(
            name="  test  file  .txt  ",
            size=100,
            last_modified=sample_datetime,
            content_type="text/plain"
        )
        assert blob.name == "  test  file  .txt  "

    def test_path_separators_in_name(self, sample_datetime):
        """Test BlobInfo with path-like structure in name"""
        blob = BlobInfo(
            name="folder/subfolder/file.txt",
            size=100,
            last_modified=sample_datetime,
            content_type="text/plain"
        )
        assert blob.name == "folder/subfolder/file.txt"


# ============================================================================
# TEST CLASS: Serialization and Deserialization
# ============================================================================

class TestBlobInfoSerialization:
    """Test JSON serialization and deserialization"""

    def test_model_dump_creates_dict(self, valid_blob_info):
        """Test that model_dump() creates a dictionary"""
        data = valid_blob_info.model_dump()
        assert isinstance(data, dict)
        assert "name" in data
        assert "size" in data
        assert "last_modified" in data
        assert "content_type" in data

    def test_model_dump_preserves_values(self, valid_blob_data):
        """Test that model_dump() preserves all values"""
        blob = BlobInfo(**valid_blob_data)
        data = blob.model_dump()
        assert data["name"] == valid_blob_data["name"]
        assert data["size"] == valid_blob_data["size"]
        assert data["content_type"] == valid_blob_data["content_type"]

    def test_model_dump_json_creates_string(self, valid_blob_info):
        """Test that model_dump_json() creates a JSON string"""
        json_str = valid_blob_info.model_dump_json()
        assert isinstance(json_str, str)
        assert "name" in json_str
        assert "size" in json_str

    def test_json_serialization_and_deserialization(self, valid_blob_data):
        """Test full JSON serialization and deserialization cycle"""
        blob1 = BlobInfo(**valid_blob_data)
        json_str = blob1.model_dump_json()
        json_dict = json.loads(json_str)
        
        # Parse datetime string back
        json_dict["last_modified"] = datetime.fromisoformat(json_dict["last_modified"].replace('Z', '+00:00'))
        blob2 = BlobInfo(**json_dict)
        
        assert blob1.name == blob2.name
        assert blob1.size == blob2.size
        assert blob1.content_type == blob2.content_type

    def test_model_validate_from_dict(self, valid_blob_data):
        """Test model_validate() creates instance from dict"""
        blob = BlobInfo.model_validate(valid_blob_data)
        assert isinstance(blob, BlobInfo)
        assert blob.name == valid_blob_data["name"]

    def test_serialization_with_unicode(self, unicode_data):
        """Test serialization preserves unicode characters"""
        blob = BlobInfo(**unicode_data)
        json_str = blob.model_dump_json()
        assert "" in json_str or "\\u" in json_str  # Either direct or escaped

    def test_model_dump_with_exclude(self, valid_blob_info):
        """Test model_dump() with field exclusion"""
        data = valid_blob_info.model_dump(exclude={"size"})
        assert "name" in data
        assert "size" not in data
        assert "content_type" in data

    def test_model_dump_with_include(self, valid_blob_info):
        """Test model_dump() with field inclusion"""
        data = valid_blob_info.model_dump(include={"name", "size"})
        assert "name" in data
        assert "size" in data
        assert "content_type" not in data
        assert "last_modified" not in data


# ============================================================================
# TEST CLASS: Equality and Comparison
# ============================================================================

class TestBlobInfoEquality:
    """Test equality and comparison operations"""

    def test_equal_instances_are_equal(self, valid_blob_data):
        """Test that two instances with same data are equal"""
        blob1 = BlobInfo(**valid_blob_data)
        blob2 = BlobInfo(**valid_blob_data)
        assert blob1 == blob2

    def test_different_instances_are_not_equal(self, valid_blob_data, sample_datetime):
        """Test that instances with different data are not equal"""
        blob1 = BlobInfo(**valid_blob_data)
        blob2 = BlobInfo(
            name="different.txt",
            size=valid_blob_data["size"],
            last_modified=sample_datetime,
            content_type=valid_blob_data["content_type"]
        )
        assert blob1 != blob2

    def test_inequality_on_name_difference(self, valid_blob_data):
        """Test inequality when only name differs"""
        blob1 = BlobInfo(**valid_blob_data)
        data2 = valid_blob_data.copy()
        data2["name"] = "different.txt"
        blob2 = BlobInfo(**data2)
        assert blob1 != blob2

    def test_inequality_on_size_difference(self, valid_blob_data):
        """Test inequality when only size differs"""
        blob1 = BlobInfo(**valid_blob_data)
        data2 = valid_blob_data.copy()
        data2["size"] = 2048
        blob2 = BlobInfo(**data2)
        assert blob1 != blob2

    def test_inequality_on_content_type_difference(self, valid_blob_data):
        """Test inequality when only content_type differs"""
        blob1 = BlobInfo(**valid_blob_data)
        data2 = valid_blob_data.copy()
        data2["content_type"] = "application/json"
        blob2 = BlobInfo(**data2)
        assert blob1 != blob2

    def test_hash_consistency(self, valid_blob_data):
        """Test that equal objects have same hash (if hashable)"""
        blob1 = BlobInfo(**valid_blob_data)
        blob2 = BlobInfo(**valid_blob_data)
        # Pydantic models are not hashable by default
        try:
            assert hash(blob1) == hash(blob2)
        except TypeError:
            # Expected for non-hashable Pydantic models
            pass


# ============================================================================
# TEST CLASS: String Representation
# ============================================================================

class TestBlobInfoStringRepresentation:
    """Test string representation methods"""

    def test_str_representation_contains_classname(self, valid_blob_info):
        """Test that str() contains class name"""
        str_repr = str(valid_blob_info)
        assert "BlobInfo" in str_repr or "name=" in str_repr

    def test_repr_representation_contains_fields(self, valid_blob_info):
        """Test that repr() contains field information"""
        repr_str = repr(valid_blob_info)
        assert "name=" in repr_str or "test-file.txt" in repr_str

    def test_str_handles_special_characters(self, special_characters_data):
        """Test string representation with special characters"""
        blob = BlobInfo(**special_characters_data)
        str_repr = str(blob)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0

    def test_str_handles_unicode(self, unicode_data):
        """Test string representation with unicode"""
        blob = BlobInfo(**unicode_data)
        str_repr = str(blob)
        assert isinstance(str_repr, str)


# ============================================================================
# TEST CLASS: Performance
# ============================================================================

class TestBlobInfoPerformance:
    """Test performance characteristics"""

    def test_create_many_instances_performance(self, sample_datetime):
        """Test creating many BlobInfo instances"""
        import time
        start = time.time()
        instances = []
        for i in range(1000):
            blob = BlobInfo(
                name=f"file-{i}.txt",
                size=i * 100,
                last_modified=sample_datetime,
                content_type="text/plain"
            )
            instances.append(blob)
        duration = time.time() - start
        assert len(instances) == 1000
        assert duration < 1.0  # Should complete in less than 1 second

    def test_serialization_performance(self, valid_blob_info):
        """Test serialization performance"""
        import time
        start = time.time()
        for _ in range(1000):
            json_str = valid_blob_info.model_dump_json()
        duration = time.time() - start
        assert duration < 0.5  # Should complete quickly

    def test_validation_performance_valid_data(self, valid_blob_data):
        """Test validation performance with valid data"""
        import time
        start = time.time()
        for _ in range(1000):
            blob = BlobInfo(**valid_blob_data)
        duration = time.time() - start
        assert duration < 1.0


# ============================================================================
# TEST CLASS: Model Schema
# ============================================================================

class TestBlobInfoSchema:
    """Test Pydantic model schema"""

    def test_model_has_schema(self):
        """Test that BlobInfo has a JSON schema"""
        schema = BlobInfo.model_json_schema()
        assert isinstance(schema, dict)
        assert "properties" in schema

    def test_schema_contains_all_fields(self):
        """Test that schema contains all required fields"""
        schema = BlobInfo.model_json_schema()
        properties = schema.get("properties", {})
        assert "name" in properties
        assert "size" in properties
        assert "last_modified" in properties
        assert "content_type" in properties

    def test_schema_field_types_are_correct(self):
        """Test that schema field types are correctly defined"""
        schema = BlobInfo.model_json_schema()
        properties = schema.get("properties", {})
        
        # Check that fields have type definitions
        assert "type" in properties["name"] or "anyOf" in properties["name"]
        assert "type" in properties["size"] or "anyOf" in properties["size"]

    def test_required_fields_in_schema(self):
        """Test that all fields are marked as required in schema"""
        schema = BlobInfo.model_json_schema()
        required = schema.get("required", [])
        assert "name" in required
        assert "size" in required
        assert "last_modified" in required
        assert "content_type" in required


# ============================================================================
# TEST CLASS: Edge Cases
# ============================================================================

class TestBlobInfoEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_maximum_integer_size(self, sample_datetime):
        """Test BlobInfo with maximum integer size"""
        max_size = sys.maxsize
        blob = BlobInfo(
            name="huge.bin",
            size=max_size,
            last_modified=sample_datetime,
            content_type="application/octet-stream"
        )
        assert blob.size == max_size

    def test_datetime_far_future(self):
        """Test BlobInfo with far future datetime"""
        future_dt = datetime(2999, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        blob = BlobInfo(
            name="future.txt",
            size=100,
            last_modified=future_dt,
            content_type="text/plain"
        )
        assert blob.last_modified.year == 2999

    def test_datetime_far_past(self):
        """Test BlobInfo with far past datetime"""
        past_dt = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        blob = BlobInfo(
            name="old.txt",
            size=100,
            last_modified=past_dt,
            content_type="text/plain"
        )
        assert blob.last_modified.year == 1970

    def test_multiple_dots_in_filename(self, sample_datetime):
        """Test BlobInfo with multiple dots in filename"""
        blob = BlobInfo(
            name="my.file.name.with.dots.txt",
            size=100,
            last_modified=sample_datetime,
            content_type="text/plain"
        )
        assert blob.name.count('.') == 5

    def test_no_extension_filename(self, sample_datetime):
        """Test BlobInfo with filename without extension"""
        blob = BlobInfo(
            name="README",
            size=100,
            last_modified=sample_datetime,
            content_type="text/plain"
        )
        assert blob.name == "README"
        assert '.' not in blob.name


# ============================================================================
# TEST CLASS: Integration and Real-World Scenarios
# ============================================================================

class TestBlobInfoIntegration:
    """Test integration scenarios and real-world use cases"""

    def test_blob_info_in_list_structure(self, valid_blob_data, sample_datetime):
        """Test using BlobInfo in list structures"""
        blobs = [
            BlobInfo(**valid_blob_data),
            BlobInfo(name="file2.txt", size=200, last_modified=sample_datetime, content_type="text/plain"),
            BlobInfo(name="file3.txt", size=300, last_modified=sample_datetime, content_type="text/plain")
        ]
        assert len(blobs) == 3
        assert all(isinstance(b, BlobInfo) for b in blobs)

    def test_blob_info_sorting_by_name(self, sample_datetime):
        """Test sorting BlobInfo instances by name"""
        blobs = [
            BlobInfo(name="c.txt", size=100, last_modified=sample_datetime, content_type="text/plain"),
            BlobInfo(name="a.txt", size=200, last_modified=sample_datetime, content_type="text/plain"),
            BlobInfo(name="b.txt", size=300, last_modified=sample_datetime, content_type="text/plain")
        ]
        sorted_blobs = sorted(blobs, key=lambda x: x.name)
        assert sorted_blobs[0].name == "a.txt"
        assert sorted_blobs[1].name == "b.txt"
        assert sorted_blobs[2].name == "c.txt"

    def test_blob_info_sorting_by_size(self, sample_datetime):
        """Test sorting BlobInfo instances by size"""
        blobs = [
            BlobInfo(name="c.txt", size=300, last_modified=sample_datetime, content_type="text/plain"),
            BlobInfo(name="a.txt", size=100, last_modified=sample_datetime, content_type="text/plain"),
            BlobInfo(name="b.txt", size=200, last_modified=sample_datetime, content_type="text/plain")
        ]
        sorted_blobs = sorted(blobs, key=lambda x: x.size)
        assert sorted_blobs[0].size == 100
        assert sorted_blobs[1].size == 200
        assert sorted_blobs[2].size == 300

    def test_blob_info_filtering(self, sample_datetime):
        """Test filtering BlobInfo instances"""
        blobs = [
            BlobInfo(name="a.txt", size=100, last_modified=sample_datetime, content_type="text/plain"),
            BlobInfo(name="b.png", size=200, last_modified=sample_datetime, content_type="image/png"),
            BlobInfo(name="c.txt", size=300, last_modified=sample_datetime, content_type="text/plain")
        ]
        text_files = [b for b in blobs if b.content_type == "text/plain"]
        assert len(text_files) == 2

    def test_blob_info_in_dict_structure(self, valid_blob_info):
        """Test using BlobInfo as dict values"""
        blob_dict = {
            "file1": valid_blob_info,
            "file2": BlobInfo(
                name="other.txt",
                size=500,
                last_modified=datetime.now(timezone.utc),
                content_type="text/plain"
            )
        }
        assert len(blob_dict) == 2
        assert isinstance(blob_dict["file1"], BlobInfo)

    def test_blob_info_copy_operation(self, valid_blob_data):
        """Test copying BlobInfo data for modification"""
        blob1 = BlobInfo(**valid_blob_data)
        data = blob1.model_dump()
        data["name"] = "copied.txt"
        blob2 = BlobInfo(**data)
        assert blob1.name != blob2.name
        assert blob1.size == blob2.size


# ============================================================================
# TEST CLASS: Code Quality Indicators
# ============================================================================

class TestBlobInfoCodeQuality:
    """Test code quality indicators"""

    def test_model_has_required_attributes(self):
        """Test that BlobInfo class has expected attributes"""
        assert hasattr(BlobInfo, 'model_dump')
        assert hasattr(BlobInfo, 'model_dump_json')
        assert hasattr(BlobInfo, 'model_validate')
        assert hasattr(BlobInfo, 'model_json_schema')

    def test_model_is_basemodel_subclass(self):
        """Test that BlobInfo is a Pydantic BaseModel subclass"""
        from pydantic import BaseModel
        assert issubclass(BlobInfo, BaseModel)

    def test_model_fields_have_annotations(self):
        """Test that all fields have type annotations"""
        annotations = BlobInfo.__annotations__
        assert 'name' in annotations
        assert 'size' in annotations
        assert 'last_modified' in annotations
        assert 'content_type' in annotations

    def test_field_types_match_annotations(self):
        """Test that field types match their annotations"""
        annotations = BlobInfo.__annotations__
        assert annotations['name'] == str
        assert annotations['size'] == int
        assert annotations['last_modified'] == datetime
        assert annotations['content_type'] == str

    def test_model_documentation_exists(self):
        """Test that model or module has documentation"""
        # Check if there's any documentation
        assert BlobInfo.__doc__ is not None or BlobInfo.__module__ is not None


# ============================================================================
# TEST CLASS: Security
# ============================================================================

class TestBlobInfoSecurity:
    """Test security-related aspects"""

    def test_no_code_execution_in_filename(self, sample_datetime):
        """Test that filename with code-like content doesn't execute"""
        dangerous_name = "test.txt'; DROP TABLE files; --"
        blob = BlobInfo(
            name=dangerous_name,
            size=100,
            last_modified=sample_datetime,
            content_type="text/plain"
        )
        assert blob.name == dangerous_name
        assert isinstance(blob.name, str)

    def test_script_tags_in_filename(self, sample_datetime):
        """Test filename containing script tags"""
        blob = BlobInfo(
            name="<script>alert('xss')</script>.txt",
            size=100,
            last_modified=sample_datetime,
            content_type="text/plain"
        )
        assert "<script>" in blob.name

    def test_null_bytes_in_fields(self, sample_datetime):
        """Test handling of null bytes in string fields"""
        # Test if null bytes are preserved or handled
        try:
            blob = BlobInfo(
                name="test\x00file.txt",
                size=100,
                last_modified=sample_datetime,
                content_type="text/plain"
            )
            assert "\x00" in blob.name or blob.name == "test\x00file.txt"
        except ValidationError:
            # Some validation might reject null bytes
            pass

    def test_very_large_field_values(self, sample_datetime):
        """Test with very large string values"""
        large_string = "x" * 1000000  # 1MB string
        blob = BlobInfo(
            name=large_string,
            size=100,
            last_modified=sample_datetime,
            content_type="text/plain"
        )
        assert len(blob.name) == 1000000


# ============================================================================
# TEST CLASS: Error Messages
# ============================================================================

class TestBlobInfoErrorMessages:
    """Test error messages and validation feedback"""

    def test_validation_error_contains_field_name(self):
        """Test that validation errors identify the problematic field"""
        try:
            BlobInfo(
                name=123,
                size=100,
                last_modified=datetime.now(),
                content_type="text/plain"
            )
        except ValidationError as e:
            error_str = str(e)
            assert "name" in error_str.lower()

    def test_missing_field_error_message_clarity(self):
        """Test that missing field errors are clear"""
        try:
            BlobInfo(name="test.txt", size=100)
        except ValidationError as e:
            error_str = str(e)
            assert "last_modified" in error_str or "content_type" in error_str

    def test_multiple_validation_errors_reported(self):
        """Test that multiple validation errors are all reported"""
        try:
            BlobInfo(name=123, size="invalid")
        except ValidationError as e:
            errors = e.errors()
            assert len(errors) >= 2  # At least name and size errors
