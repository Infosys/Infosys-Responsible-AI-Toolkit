import os
import tempfile
import pytest

from src.service.utility import Utility


def test_sanitize_filename_valid_cases():
    assert Utility.sanitize_filenameorfoldername('model-1_abc') == 'model-1_abc'
    assert Utility.sanitize_filenameorfoldername('file.name-v1') == 'file.name-v1'
    assert Utility.sanitize_filenameorfoldername('A_B-C.D') == 'A_B-C.D'


def test_sanitize_filename_invalid_cases():
    # Invalid characters return None (exception is swallowed internally)
    assert Utility.sanitize_filenameorfoldername('bad/name') is None
    assert Utility.sanitize_filenameorfoldername('bad\\name') is None


def test_database_delete_file_and_dir(tmp_path):
    # Create a temp file
    fpath = tmp_path / 'temp.txt'
    fpath.write_text('x', encoding='utf-8')
    assert fpath.exists()
    Utility.databaseDelete(str(fpath))
    assert not fpath.exists()

    # Create a temp directory with a file
    dpath = tmp_path / 'd'
    dpath.mkdir()
    (dpath / 'a.txt').write_text('y', encoding='utf-8')
    assert dpath.exists()
    Utility.databaseDelete(str(dpath))
    assert not dpath.exists()


def test_is_content_safe():
    assert Utility.isContentSafe({'a': 'abc-123', 'b': 'OK_name'}) is True
    # Disallow non-str values
    assert Utility.isContentSafe({'a': 1}) is False
    # Disallow illegal characters
    assert Utility.isContentSafe({'a': 'bad*name'}) is False
