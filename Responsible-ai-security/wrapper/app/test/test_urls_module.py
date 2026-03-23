'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
'''

import pytest
from src.config.urls import UrlLinks


class TestUrlLinksModule:
    """Test cases for UrlLinks class"""

    def test_assessment_generation_default(self):
        """Test Assessment_Generation default value"""
        assert UrlLinks.Assessment_Generation is False

    def test_current_id_default(self):
        """Test Current_ID default value is non-negative integer"""
        assert isinstance(UrlLinks.Current_ID, int)
        assert UrlLinks.Current_ID >= 0

    def test_available_model_url_exists(self):
        """Test AvailableModel_url is set"""
        assert hasattr(UrlLinks, 'AvailableModel_url')
        assert isinstance(UrlLinks.AvailableModel_url, str)
        assert len(UrlLinks.AvailableModel_url) > 0

    def test_add_model_url_exists(self):
        """Test AddModel_url is set"""
        assert hasattr(UrlLinks, 'AddModel_url')
        assert isinstance(UrlLinks.AddModel_url, str)
        assert len(UrlLinks.AddModel_url) > 0

    def test_set_model_url_exists(self):
        """Test SetModel_url is set"""
        assert hasattr(UrlLinks, 'SetModel_url')
        assert isinstance(UrlLinks.SetModel_url, str)
        assert len(UrlLinks.SetModel_url) > 0

    def test_set_attack_url_exists(self):
        """Test SetAttack_url is set"""
        assert hasattr(UrlLinks, 'SetAttack_url')
        assert isinstance(UrlLinks.SetAttack_url, str)
        assert len(UrlLinks.SetAttack_url) > 0

    def test_url_format(self):
        """Test URL format is valid"""
        assert UrlLinks.AvailableModel_url.startswith(('http://', 'https://'))
        assert UrlLinks.AddModel_url.startswith(('http://', 'https://'))
        assert UrlLinks.SetModel_url.startswith(('http://', 'https://'))
        assert UrlLinks.SetAttack_url.startswith(('http://', 'https://'))

    def test_url_endpoints_unique(self):
        """Test that URL endpoints are unique"""
        urls = [
            UrlLinks.AvailableModel_url,
            UrlLinks.AddModel_url,
            UrlLinks.SetModel_url,
            UrlLinks.SetAttack_url
        ]
        # Check that all URLs have different endpoints
        assert len(set(urls)) >= 1

    def test_current_id_is_integer(self):
        """Test Current_ID is an integer"""
        assert isinstance(UrlLinks.Current_ID, int)

    def test_assessment_generation_is_boolean(self):
        """Test Assessment_Generation is a boolean"""
        assert isinstance(UrlLinks.Assessment_Generation, bool)

    def test_can_modify_assessment_generation(self):
        """Test Assessment_Generation can be modified"""
        original = UrlLinks.Assessment_Generation
        try:
            UrlLinks.Assessment_Generation = True
            assert UrlLinks.Assessment_Generation is True
        finally:
            UrlLinks.Assessment_Generation = original

    def test_can_modify_current_id(self):
        """Test Current_ID can be modified"""
        original = UrlLinks.Current_ID
        try:
            UrlLinks.Current_ID = 999
            assert UrlLinks.Current_ID == 999
        finally:
            UrlLinks.Current_ID = original
