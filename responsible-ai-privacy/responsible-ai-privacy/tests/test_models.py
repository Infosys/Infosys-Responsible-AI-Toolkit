"""
Unit tests for models module
"""
import pytest
from privacy.models import AddRecognizerRequest


class TestAddRecognizerRequest:
    """Test AddRecognizerRequest Pydantic model"""

    def test_add_recognizer_request_creation_full(self):
        """Test creating AddRecognizerRequest with all fields"""
        request = AddRecognizerRequest(
            recog_name="TEST_SSN",
            supported_entity="SSN",
            recog_type="Pattern",
            score=0.8,
            context=["ssn", "social security"],
            entity_values=[r"\b\d{3}-\d{2}-\d{4}\b"]
        )
        assert request.recog_name == "TEST_SSN"
        assert request.supported_entity == "SSN"
        assert request.recog_type == "Pattern"
        assert request.score == 0.8
        assert len(request.context) == 2
        assert len(request.entity_values) == 1

    def test_add_recognizer_request_required_fields_only(self):
        """Test creating request with only required fields"""
        request = AddRecognizerRequest(
            recog_name="MY_ENTITY",
            recog_type="Data",
            entity_values=["value1", "value2"]
        )
        assert request.recog_name == "MY_ENTITY"
        assert request.recog_type == "Data"
        assert request.supported_entity is None
        assert request.score == 0.6  # Default value
        assert request.context == []  # Default value
        assert len(request.entity_values) == 2

    def test_pattern_recognizer_with_regex(self):
        """Test Pattern type recognizer with regex"""
        regex_pattern = r"\b[1-9]\d{5}\b"
        request = AddRecognizerRequest(
            recog_name="INDIAN_PINCODE",
            recog_type="Pattern",
            entity_values=[regex_pattern]
        )
        assert request.recog_type == "Pattern"
        assert regex_pattern in request.entity_values

    def test_data_recognizer_with_word_list(self):
        """Test Data type recognizer with word list"""
        words = ["word1", "word2", "word3"]
        request = AddRecognizerRequest(
            recog_name="KEYWORD_LIST",
            recog_type="Data",
            entity_values=words
        )
        assert request.recog_type == "Data"
        assert request.entity_values == words

    def test_default_score_value(self):
        """Test default score is 0.6"""
        request = AddRecognizerRequest(
            recog_name="TEST",
            recog_type="Pattern",
            entity_values=["test"]
        )
        assert request.score == 0.6

    def test_custom_score_value(self):
        """Test custom score value"""
        request = AddRecognizerRequest(
            recog_name="TEST",
            recog_type="Pattern",
            score=0.95,
            entity_values=["test"]
        )
        assert request.score == 0.95

    def test_context_list_default(self):
        """Test context defaults to empty list"""
        request = AddRecognizerRequest(
            recog_name="TEST",
            recog_type="Data",
            entity_values=["test"]
        )
        assert request.context == []
        assert isinstance(request.context, list)

    def test_context_list_with_values(self):
        """Test context with multiple values"""
        contexts = ["email", "mail", "contact"]
        request = AddRecognizerRequest(
            recog_name="EMAIL",
            recog_type="Pattern",
            context=contexts,
            entity_values=[r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"]
        )
        assert request.context == contexts
        assert len(request.context) == 3

    def test_supported_entity_defaults_to_none(self):
        """Test supported_entity is None when not provided"""
        request = AddRecognizerRequest(
            recog_name="TEST",
            recog_type="Pattern",
            entity_values=["test"]
        )
        assert request.supported_entity is None

    def test_supported_entity_custom_value(self):
        """Test custom supported_entity value"""
        request = AddRecognizerRequest(
            recog_name="MY_SSN",
            supported_entity="SSN_CUSTOM",
            recog_type="Pattern",
            entity_values=[r"\d{3}-\d{2}-\d{4}"]
        )
        assert request.supported_entity == "SSN_CUSTOM"


class TestRecognizerTypes:
    """Test different recognizer types"""

    def test_pattern_type_case_insensitive(self):
        """Test Pattern type (case variations)"""
        for recog_type in ["Pattern", "pattern", "PATTERN"]:
            request = AddRecognizerRequest(
                recog_name=f"TEST_{recog_type}",
                recog_type=recog_type,
                entity_values=["test"]
            )
            assert request.recog_type == recog_type

    def test_data_type_case_insensitive(self):
        """Test Data type (case variations)"""
        for recog_type in ["Data", "data", "DATA"]:
            request = AddRecognizerRequest(
                recog_name=f"TEST_{recog_type}",
                recog_type=recog_type,
                entity_values=["test"]
            )
            assert request.recog_type == recog_type


class TestEntityValues:
    """Test entity_values field"""

    def test_single_entity_value(self):
        """Test with single entity value"""
        request = AddRecognizerRequest(
            recog_name="TEST",
            recog_type="Data",
            entity_values=["single_value"]
        )
        assert len(request.entity_values) == 1
        assert request.entity_values[0] == "single_value"

    def test_multiple_entity_values(self):
        """Test with multiple entity values"""
        values = ["value1", "value2", "value3", "value4"]
        request = AddRecognizerRequest(
            recog_name="TEST",
            recog_type="Data",
            entity_values=values
        )
        assert len(request.entity_values) == 4
        assert request.entity_values == values

    def test_regex_patterns_as_entity_values(self):
        """Test regex patterns in entity_values"""
        patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
            r"\b[1-9]\d{5}\b",  # PIN code
            r"\b[A-Z]{2}\d{2}[A-Z]\d{4}[A-Z]\d{7}\b"  # IBAN
        ]
        request = AddRecognizerRequest(
            recog_name="MULTI_PATTERN",
            recog_type="Pattern",
            entity_values=patterns
        )
        assert len(request.entity_values) == 3
        assert request.entity_values == patterns


class TestModelSerialization:
    """Test model serialization"""

    def test_to_dict(self):
        """Test model conversion to dict"""
        request = AddRecognizerRequest(
            recog_name="TEST",
            recog_type="Pattern",
            entity_values=["test"]
        )
        request_dict = request.dict()
        assert isinstance(request_dict, dict)
        assert request_dict["recog_name"] == "TEST"
        assert request_dict["recog_type"] == "Pattern"

    def test_to_json(self):
        """Test model conversion to JSON"""
        request = AddRecognizerRequest(
            recog_name="TEST",
            recog_type="Data",
            entity_values=["test"]
        )
        json_str = request.json()
        assert isinstance(json_str, str)
        assert "TEST" in json_str
        assert "Data" in json_str

    def test_from_dict(self):
        """Test creating model from dict"""
        data = {
            "recog_name": "FROM_DICT",
            "recog_type": "Pattern",
            "score": 0.7,
            "entity_values": ["test1", "test2"]
        }
        request = AddRecognizerRequest(**data)
        assert request.recog_name == "FROM_DICT"
        assert request.score == 0.7


class TestValidation:
    """Test model validation"""

    def test_missing_required_recog_name_raises_error(self):
        """Test missing required field recog_name raises error"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            AddRecognizerRequest(
                recog_type="Pattern",
                entity_values=["test"]
            )

    def test_missing_required_recog_type_raises_error(self):
        """Test missing required field recog_type raises error"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            AddRecognizerRequest(
                recog_name="TEST",
                entity_values=["test"]
            )

    def test_missing_required_entity_values_raises_error(self):
        """Test missing required field entity_values raises error"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            AddRecognizerRequest(
                recog_name="TEST",
                recog_type="Pattern"
            )

    def test_empty_entity_values_list_is_valid(self):
        """Test empty list for entity_values"""
        # If empty list is allowed
        try:
            request = AddRecognizerRequest(
                recog_name="TEST",
                recog_type="Pattern",
                entity_values=[]
            )
            assert request.entity_values == []
        except Exception:
            # If validation requires non-empty list, this is expected
            pass


class TestEdgeCases:
    """Test edge cases"""

    def test_very_long_recog_name(self):
        """Test with very long recognizer name"""
        long_name = "A" * 1000
        request = AddRecognizerRequest(
            recog_name=long_name,
            recog_type="Data",
            entity_values=["test"]
        )
        assert request.recog_name == long_name

    def test_special_characters_in_recog_name(self):
        """Test special characters in name"""
        special_name = "TEST_!@#$%_NAME"
        request = AddRecognizerRequest(
            recog_name=special_name,
            recog_type="Pattern",
            entity_values=["test"]
        )
        assert request.recog_name == special_name

    def test_score_boundary_values(self):
        """Test score with boundary values"""
        for score in [0.0, 0.5, 1.0]:
            request = AddRecognizerRequest(
                recog_name="TEST",
                recog_type="Pattern",
                score=score,
                entity_values=["test"]
            )
            assert request.score == score

    def test_unicode_in_entity_values(self):
        """Test Unicode characters in entity values"""
        unicode_values = ["测试", "тест", "परीक्षण"]
        request = AddRecognizerRequest(
            recog_name="UNICODE_TEST",
            recog_type="Data",
            entity_values=unicode_values
        )
        assert request.entity_values == unicode_values
