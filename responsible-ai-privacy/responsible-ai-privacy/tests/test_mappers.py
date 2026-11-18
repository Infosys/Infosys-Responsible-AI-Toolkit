"""
Unit tests for mappers module - Pydantic models
"""
import pytest
from privacy.mappers.mappers import PIIEntity, PIIItems, PIIEntityImages


class TestPIIEntity:
    """Test PIIEntity Pydantic model"""

    def test_pii_entity_creation_with_all_fields(self):
        """Test creating PIIEntity with all fields"""
        entity = PIIEntity(
            type="USA_SSN",
            beginOffset=19,
            endOffset=28,
            score=1.0,
            responseText="012884567"
        )
        assert entity.type == "USA_SSN"
        assert entity.beginOffset == 19
        assert entity.endOffset == 28
        assert entity.score == 1.0
        assert entity.responseText == "012884567"

    def test_pii_entity_with_none_values(self):
        """Test creating PIIEntity with explicit None values"""
        entity = PIIEntity(
            type=None,
            beginOffset=None,
            endOffset=None,
            score=None,
            responseText=None
        )
        assert entity.type is None
        assert entity.beginOffset is None
        assert entity.endOffset is None
        assert entity.score is None
        assert entity.responseText is None

    def test_pii_entity_with_mixed_values(self):
        """Test PIIEntity with some None and some real values"""
        entity = PIIEntity(
            type="EMAIL",
            beginOffset=None,
            endOffset=None,
            score=0.95,
            responseText=None
        )
        assert entity.type == "EMAIL"
        assert entity.score == 0.95
        assert entity.beginOffset is None
        assert entity.endOffset is None
        assert entity.responseText is None

    def test_pii_entity_field_types(self):
        """Test field types are correct"""
        entity = PIIEntity(
            type="PHONE",
            beginOffset=10,
            endOffset=20,
            score=0.8,
            responseText="1234567890"
        )
        assert isinstance(entity.type, str)
        assert isinstance(entity.beginOffset, int)
        assert isinstance(entity.endOffset, int)
        assert isinstance(entity.score, float)
        assert isinstance(entity.responseText, str)

    def test_pii_entity_with_different_types(self):
        """Test PIIEntity with various entity types"""
        entity_types = ["USA_SSN", "EMAIL", "PHONE", "CREDIT_CARD", "PERSON"]
        for entity_type in entity_types:
            entity = PIIEntity(
                type=entity_type,
                beginOffset=0,
                endOffset=10,
                score=0.9,
                responseText="test_text"
            )
            assert entity.type == entity_type


class TestPIIItems:
    """Test PIIItems Pydantic model"""

    def test_pii_items_creation_with_all_fields(self):
        """Test creating PIIItems with all fields"""
        item = PIIItems(
            start=19,
            end=28,
            entity_type="USA_SSN",
            text="Ray William's SSN is 012884567",
            operator="encrypt"
        )
        assert item.start == 19
        assert item.end == 28
        assert item.entity_type == "USA_SSN"
        assert "012884567" in item.text
        assert item.operator == "encrypt"

    def test_pii_items_with_none_values(self):
        """Test creating PIIItems with explicit None values"""
        item = PIIItems(
            start=None,
            end=None,
            entity_type=None,
            text=None,
            operator=None
        )
        assert item.start is None
        assert item.end is None
        assert item.entity_type is None
        assert item.text is None
        assert item.operator is None

    def test_pii_items_with_different_operators(self):
        """Test PIIItems with different operators"""
        operators = ["encrypt", "mask", "redact", "replace", "hash"]
        for op in operators:
            item = PIIItems(
                start=0,
                end=10,
                entity_type="SSN",
                text="test text",
                operator=op
            )
            assert item.operator == op

    def test_pii_items_field_types(self):
        """Test field types are correct"""
        item = PIIItems(
            start=0,
            end=10,
            entity_type="PERSON",
            text="John Doe",
            operator="replace"
        )
        assert isinstance(item.start, int)
        assert isinstance(item.end, int)
        assert isinstance(item.entity_type, str)
        assert isinstance(item.text, str)
        assert isinstance(item.operator, str)

    def test_pii_items_with_partial_none_values(self):
        """Test PIIItems with some fields as None"""
        item = PIIItems(
            start=10,
            end=20,
            entity_type="EMAIL",
            text=None,
            operator=None
        )
        assert item.start == 10
        assert item.end == 20
        assert item.entity_type == "EMAIL"
        assert item.text is None
        assert item.operator is None


class TestPIIEntityImages:
    """Test PIIEntityImages Pydantic model"""

    def test_pii_entity_images_creation_all_fields(self):
        """Test creating PIIEntityImages with all fields"""
        entity = PIIEntityImages(
            type="USA_SSN",
            beginOffset=19,
            endOffset=28,
            score=1.0
        )
        assert entity.type == "USA_SSN"
        assert entity.beginOffset == 19
        assert entity.endOffset == 28
        assert entity.score == 1.0

    def test_pii_entity_images_with_none_values(self):
        """Test creating PIIEntityImages with None values"""
        entity = PIIEntityImages(
            type=None,
            beginOffset=None,
            endOffset=None,
            score=None
        )
        assert entity.type is None
        assert entity.beginOffset is None
        assert entity.endOffset is None
        assert entity.score is None

    def test_pii_entity_images_with_various_types(self):
        """Test PIIEntityImages with different entity types"""
        entity_types = ["EMAIL", "PHONE", "SSN", "CREDIT_CARD", "PERSON"]
        for entity_type in entity_types:
            entity = PIIEntityImages(
                type=entity_type,
                beginOffset=0,
                endOffset=10,
                score=0.9
            )
            assert entity.type == entity_type
            assert entity.beginOffset == 0
            assert entity.endOffset == 10


class TestModelSerialization:
    """Test model serialization and deserialization"""

    def test_pii_entity_to_dict(self):
        """Test PIIEntity serialization to dict"""
        entity = PIIEntity(
            type="SSN",
            beginOffset=0,
            endOffset=10,
            score=0.9,
            responseText="test123"
        )
        entity_dict = entity.model_dump()
        assert isinstance(entity_dict, dict)
        assert entity_dict["type"] == "SSN"
        assert entity_dict["beginOffset"] == 0
        assert entity_dict["endOffset"] == 10
        assert entity_dict["score"] == 0.9
        assert entity_dict["responseText"] == "test123"

    def test_pii_entity_from_dict(self):
        """Test PIIEntity deserialization from dict"""
        data = {
            "type": "EMAIL",
            "beginOffset": 5,
            "endOffset": 20,
            "score": 0.95,
            "responseText": "test@example.com"
        }
        entity = PIIEntity(**data)
        assert entity.type == "EMAIL"
        assert entity.responseText == "test@example.com"

    def test_pii_items_to_dict(self):
        """Test PIIItems serialization"""
        item = PIIItems(
            start=0,
            end=5,
            entity_type="PERSON",
            text="John",
            operator="mask"
        )
        item_dict = item.model_dump()
        assert isinstance(item_dict, dict)
        assert item_dict["entity_type"] == "PERSON"
        assert item_dict["operator"] == "mask"

    def test_pii_items_json_serialization(self):
        """Test PIIItems JSON serialization"""
        item = PIIItems(
            start=0,
            end=10,
            entity_type="SSN",
            text="test text",
            operator="encrypt"
        )
        json_str = item.model_dump_json()
        assert isinstance(json_str, str)
        assert "SSN" in json_str
        assert "encrypt" in json_str

    def test_serialization_with_none_values(self):
        """Test serialization when fields are None"""
        entity = PIIEntity(
            type="SSN",
            beginOffset=None,
            endOffset=None,
            score=None,
            responseText=None
        )
        entity_dict = entity.model_dump()
        assert entity_dict["type"] == "SSN"
        assert entity_dict["beginOffset"] is None
        assert entity_dict["score"] is None


class TestModelValidation:
    """Test model validation"""

    def test_pii_entity_with_score_type_conversion(self):
        """Test PIIEntity handles type conversion for score"""
        # Pydantic will try to coerce the type
        entity = PIIEntity(
            type="SSN",
            beginOffset=0,
            endOffset=10,
            score="0.5",  # String that can be converted to float
            responseText="test"
        )
        assert entity.score == 0.5
        assert isinstance(entity.score, float)

    def test_pii_items_with_int_conversion(self):
        """Test PIIItems handles int conversion"""
        item = PIIItems(
            start="10",  # Strings that can convert to int
            end="20",
            entity_type="SSN",
            text="test",
            operator="mask"
        )
        assert item.start == 10
        assert item.end == 20
        assert isinstance(item.start, int)
        assert isinstance(item.end, int)

    def test_model_with_extra_fields_ignored(self):
        """Test that extra fields are handled properly"""
        # Pydantic by default ignores extra fields in Pydantic v2
        entity = PIIEntity(
            type="SSN",
            beginOffset=0,
            endOffset=10,
            score=0.9,
            responseText="test",
            extra_field="should_be_ignored"
        )
        assert entity.type == "SSN"
        # Extra fields are ignored, not stored
        assert not hasattr(entity, 'extra_field')

    def test_float_to_int_conversion(self):
        """Test that float values can be assigned to int fields"""
        entity = PIIEntity(
            type="SSN",
            beginOffset=10.0,  # Float that can convert to int
            endOffset=20.0,
            score=0.95,
            responseText="test"
        )
        assert entity.beginOffset == 10
        assert entity.endOffset == 20
        assert isinstance(entity.beginOffset, int)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_strings(self):
        """Test models with empty strings"""
        entity = PIIEntity(
            type="",
            beginOffset=0,
            endOffset=0,
            score=0.0,
            responseText=""
        )
        assert entity.type == ""
        assert entity.responseText == ""

    def test_zero_values(self):
        """Test models with zero values"""
        entity = PIIEntity(
            type="SSN",
            beginOffset=0,
            endOffset=0,
            score=0.0,
            responseText="test"
        )
        assert entity.beginOffset == 0
        assert entity.endOffset == 0
        assert entity.score == 0.0

    def test_negative_offsets(self):
        """Test models with negative offsets (allowed in the model)"""
        item = PIIItems(
            start=-1,
            end=-1,
            entity_type="SSN",
            text="test",
            operator="mask"
        )
        assert item.start == -1
        assert item.end == -1

    def test_very_long_text(self):
        """Test with very long text"""
        long_text = "a" * 10000
        item = PIIItems(
            start=0,
            end=10000,
            entity_type="PERSON",
            text=long_text,
            operator="mask"
        )
        assert len(item.text) == 10000
        assert item.text == long_text

    def test_special_characters_in_text(self):
        """Test with special characters"""
        special_text = "Test@#$%^&*(){}[]|\\:;\"'<>,.?/~`"
        entity = PIIEntity(
            type="SSN",
            beginOffset=0,
            endOffset=len(special_text),
            score=0.9,
            responseText=special_text
        )
        assert entity.responseText == special_text

    def test_unicode_characters(self):
        """Test with Unicode characters"""
        unicode_text = "Hello 世界 🌍"
        item = PIIItems(
            start=0,
            end=len(unicode_text),
            entity_type="PERSON",
            text=unicode_text,
            operator="mask"
        )
        assert item.text == unicode_text

    def test_very_large_offsets(self):
        """Test with very large offset values"""
        entity = PIIEntity(
            type="SSN",
            beginOffset=999999,
            endOffset=9999999,
            score=1.0,
            responseText="test"
        )
        assert entity.beginOffset == 999999
        assert entity.endOffset == 9999999

    def test_score_boundary_values(self):
        """Test score with boundary values"""
        # Test score = 0.0
        entity1 = PIIEntity(
            type="SSN",
            beginOffset=0,
            endOffset=10,
            score=0.0,
            responseText="test"
        )
        assert entity1.score == 0.0

        # Test score = 1.0
        entity2 = PIIEntity(
            type="SSN",
            beginOffset=0,
            endOffset=10,
            score=1.0,
            responseText="test"
        )
        assert entity2.score == 1.0

        # Test score > 1.0 (if allowed)
        entity3 = PIIEntity(
            type="SSN",
            beginOffset=0,
            endOffset=10,
            score=1.5,
            responseText="test"
        )
        assert entity3.score == 1.5
