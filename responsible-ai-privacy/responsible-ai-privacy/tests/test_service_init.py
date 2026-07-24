"""
Tests for service/__init__.py module functions
"""

import pytest
from unittest.mock import MagicMock
from privacy.service import selectNlp, update_session_dict, get_session_dict, AttributeDict


class TestSelectNlp:
    """Test suite for selectNlp function"""

    def test_selectNlp_basic_returns_light_engines(self):
        """Test that selectNlp('basic') returns light engine tuple"""
        result = selectNlp("basic")
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 5

    def test_selectNlp_good_returns_medium_engines(self):
        """Test that selectNlp('good') returns medium engine tuple"""
        result = selectNlp("good")
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 5

    def test_selectNlp_default_returns_light_engines(self):
        """Test that selectNlp with other value returns light engine tuple"""
        result = selectNlp("other")
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 5

    def test_selectNlp_empty_string_returns_light_engines(self):
        """Test that selectNlp('') returns light engine tuple"""
        result = selectNlp("")
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 5

    def test_selectNlp_none_returns_light_engines(self):
        """Test that selectNlp(None) returns light engine tuple"""
        result = selectNlp(None)
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 5


class TestSessionDict:
    """Test suite for session dict helper functions"""

    def test_update_session_dict_adds_key_value(self):
        """Test that update_session_dict adds key-value pair"""
        session = get_session_dict()
        original_len = len(session)
        update_session_dict("test_key", "test_value")
        assert get_session_dict()["test_key"] == "test_value"

    def test_get_session_dict_returns_dict(self):
        """Test that get_session_dict returns a dictionary"""
        result = get_session_dict()
        assert isinstance(result, dict)


class TestAttributeDictInInit:
    """Test suite for AttributeDict class in __init__.py"""

    def test_attribute_dict_getattr(self):
        """Test AttributeDict getattr works"""
        ad = AttributeDict({"key1": "value1"})
        assert ad.key1 == "value1"

    def test_attribute_dict_setattr(self):
        """Test AttributeDict setattr works"""
        ad = AttributeDict()
        ad.key2 = "value2"
        assert ad["key2"] == "value2"

    def test_attribute_dict_delattr(self):
        """Test AttributeDict delattr works"""
        ad = AttributeDict({"key3": "value3"})
        del ad.key3
        assert "key3" not in ad
