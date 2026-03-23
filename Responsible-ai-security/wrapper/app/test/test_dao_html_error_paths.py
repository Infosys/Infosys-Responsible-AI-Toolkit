import pytest

from src.dao.Html import Html


def test_html_create_invalid_document():
    # Invalid MongoDB key should be rejected and handled
    invalid_doc = {'$badkey': 1}
    result = Html.create(invalid_doc)
    assert result is None


def test_html_find_one_invalid_types():
    # Wrong types should be gracefully handled
    assert Html.find_one(None, 1.0) is None
    assert Html.find_one(1.0, None) is None
    assert Html.find_one('1.0', 2.0) is None


def test_html_find_invalid_types():
    # Wrong types should be gracefully handled
    assert Html.find(None, 1.0) is None
    assert Html.find(1.0, None) is None
    assert Html.find('1.0', 2.0) is None
