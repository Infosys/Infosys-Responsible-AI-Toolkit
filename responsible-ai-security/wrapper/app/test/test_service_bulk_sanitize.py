from src.service.service import Bulk, Infosys


def test_sanitize_valid_filename():
    assert Bulk.sanitize_filenameorfoldername("Valid_Name-123") == "Valid_Name-123"


def test_sanitize_invalid_filename():
    # Invalid chars should lead to None due to internal exception handling
    out = Bulk.sanitize_filenameorfoldername("Invalid!Name?")
    assert out is None
