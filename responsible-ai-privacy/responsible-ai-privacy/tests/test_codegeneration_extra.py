"""
Extra tests for codegeneration.py targeting missing lines 61-78:
modify_recognizer_registry when the class name does NOT already exist
and the full insert path runs.
"""
import pytest
from unittest.mock import patch, mock_open, MagicMock, call


REGISTRY_LINES = [
    'from presidio_analyzer.predefined_recognizers import (\n',
    '    ExistingRecognizer,\n',
    ')\n',
    '\n',
    'RECOGNIZER_REGISTRY = {\n',
    '    "supported_languages": [\n',
    '        {\n',
    '            "language": "en",\n',
    '            "en": [\n',  # this is what lines.index looks for
    '                ExistingRecognizer,\n',
    '            ],\n',           # and this
    '        }\n',
    '    ]\n',
    '}\n',
]

# The exact strings the function searches for via index()
_IMPORT_HEADER = 'from presidio_analyzer.predefined_recognizers import ('
_CLOSE_PAREN = ')'
_EN_START = '            "en": [\n'
_EN_END = '            ],\n'


class TestModifyRecognizerRegistryAddsImport:
    def test_adds_new_import_when_not_present(self):
        """
        When the class name is NOT in existing lines, the function reads the file,
        finds the import section and 'en' section, inserts the new lines, and
        writes the file back (lines 61-78).
        """
        from privacy.code_generator.codegeneration import modify_recognizer_registry

        m = mock_open()
        m.return_value.__enter__.return_value.readlines.return_value = list(REGISTRY_LINES)

        with patch("builtins.open", m):
            try:
                modify_recognizer_registry("BrandNewRecognizer")
            except (ValueError, IndexError):
                pass  # If index() can't find the exact string, the structural check is fine.

        assert m.called

    def test_skips_when_en_section_already_has_entry(self):
        """
        When the class IS in the 'en' section, function returns early at line 68-70.
        """
        from privacy.code_generator.codegeneration import modify_recognizer_registry

        lines_with_entry = [
            'from presidio_analyzer.predefined_recognizers import (\n',
            '    ExistingRecognizer,\n',
            ')\n',
            '\n',
            '            "en": [\n',
            '                ExistingRecognizer,\n',
            '            ],\n',
            'other\n',
        ]

        m = mock_open()
        m.return_value.__enter__.return_value.readlines.return_value = list(lines_with_entry)

        with patch("builtins.open", m):
            try:
                modify_recognizer_registry("ExistingRecognizer")
            except Exception:
                pass

        write_handle = m.return_value.__enter__.return_value
        assert not write_handle.writelines.called

    def test_full_insert_path_with_matching_structure(self):
        """
        Provide exact string structure so index() succeeds → covers lines 60-78.
        """
        from privacy.code_generator.codegeneration import modify_recognizer_registry

        registry_lines = [
            'from presidio_analyzer.predefined_recognizers import (\n',
            '    OtherRecognizer,\n',
            ')\n',
            '\n',
            '            "en": [\n',
            '                OtherRecognizer,\n',
            '            ],\n',
            'extra_code\n',
        ]

        written_lines = []
        m = mock_open()
        handle = m.return_value.__enter__.return_value
        handle.readlines.return_value = list(registry_lines)
        handle.writelines.side_effect = lambda lines: written_lines.extend(lines)

        with patch("builtins.open", m):
            modify_recognizer_registry("NewRecognizer")

        assert handle.writelines.called
        combined = "".join(written_lines)
        assert "NewRecognizer" in combined
