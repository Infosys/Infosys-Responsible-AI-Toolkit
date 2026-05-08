import pytest

from src.service.service import Bulk


def test_sanitize_filename_valid():
    assert Bulk.sanitize_filenameorfoldername('abc_123-file') == 'abc_123-file'


def test_sanitize_filename_invalid_returns_none():
    # invalid due to space and special char
    assert Bulk.sanitize_filenameorfoldername('bad name!') is None
