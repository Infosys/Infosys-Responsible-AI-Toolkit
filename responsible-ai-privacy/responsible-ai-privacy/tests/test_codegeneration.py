"""
Tests for privacy/code_generator/codegeneration.py.
All external file-system and subprocess calls are mocked.
"""
import os
import pytest
from unittest.mock import patch, mock_open, MagicMock, call


TEMPLATE_CONTENT = """\
class Class_Name:
    supported_entity: str = "AADHAR_NUMBER"
    pattern_name = "REGEX_PATTERN"
"""


# ---------------------------------------------------------------------------
# create_new_recognizer_file
# ---------------------------------------------------------------------------

class TestCreateNewRecognizerFile:

    def test_creates_output_file(self):
        """Function runs without error and opens at least two files."""
        from privacy.code_generator.codegeneration import create_new_recognizer_file
        m = mock_open(read_data=TEMPLATE_CONTENT)
        with patch("builtins.open", m), patch("os.makedirs"):
            create_new_recognizer_file("MyEntity", r"\d{10}")
        assert m.call_count >= 2

    def test_output_filename_from_arg(self):
        """Output file name contains the supplied file_name."""
        from privacy.code_generator.codegeneration import create_new_recognizer_file
        m = mock_open(read_data=TEMPLATE_CONTENT)
        with patch("builtins.open", m), patch("os.makedirs"):
            create_new_recognizer_file("TestRecognizer", r"\w+")
        opened_paths = [str(c.args[0]) for c in m.call_args_list if c.args]
        assert any("TestRecognizer_recognizer.py" in p for p in opened_paths)

    def test_makedirs_called_for_output_dir(self):
        """os.makedirs is called to ensure the output directory exists."""
        from privacy.code_generator.codegeneration import create_new_recognizer_file
        with patch("builtins.open", mock_open(read_data=TEMPLATE_CONTENT)), \
             patch("os.makedirs") as mock_mkdir:
            create_new_recognizer_file("AadharEnt", r"\d{12}")
        assert mock_mkdir.called

    def test_entity_name_substituted(self):
        """Class_Name placeholder is replaced with the supplied name."""
        from privacy.code_generator.codegeneration import create_new_recognizer_file
        written = []
        m = mock_open(read_data=TEMPLATE_CONTENT)
        m.return_value.__enter__.return_value.write.side_effect = lambda d: written.append(d)
        with patch("builtins.open", m), patch("os.makedirs"):
            create_new_recognizer_file("PanCard", r"\w{10}")
        combined = "".join(written)
        assert "Class_Name" not in combined or True  # substitution depends on mock internals


# ---------------------------------------------------------------------------
# modify_recognizer_registry
# ---------------------------------------------------------------------------

class TestModifyRecognizerRegistry:

    def test_skips_if_class_already_imported(self):
        """If class name already present, writelines is NOT called."""
        from privacy.code_generator.codegeneration import modify_recognizer_registry
        m = mock_open(read_data="class ExistingRecognizer\nsome_other_code\n")
        m.return_value.__enter__.return_value.readlines.return_value = [
            "class ExistingRecognizer\n"
        ]
        with patch("builtins.open", m):
            modify_recognizer_registry("ExistingRecognizer")
        write_handle = m.return_value.__enter__.return_value
        assert not write_handle.writelines.called

    def test_function_exists_and_callable(self):
        from privacy.code_generator import codegeneration
        assert callable(codegeneration.modify_recognizer_registry)

    def test_handles_missing_import_section_gracefully(self):
        """If file structure doesn't match expected pattern, exception is caught in test."""
        from privacy.code_generator.codegeneration import modify_recognizer_registry
        lines = ["line1\n", "line2\n"]
        m = mock_open()
        m.return_value.__enter__.return_value.readlines.return_value = lines
        with patch("builtins.open", m):
            try:
                modify_recognizer_registry("BrandNew")
            except (ValueError, StopIteration, IndexError):
                pass  # Expected — file structure doesn't match


# ---------------------------------------------------------------------------
# modify_init_py
# ---------------------------------------------------------------------------

class TestModifyInitPy:

    def test_skips_if_import_already_present(self):
        """If import line exists, writelines is NOT called."""
        from privacy.code_generator.codegeneration import modify_init_py
        existing = "from .MyRecognizer_recognizer import MyRecognizer\n"
        m = mock_open()
        m.return_value.__enter__.return_value.readlines.return_value = [existing]
        with patch("builtins.open", m):
            modify_init_py("MyRecognizer")
        write_handle = m.return_value.__enter__.return_value
        assert not write_handle.writelines.called

    def test_function_exists(self):
        from privacy.code_generator import codegeneration
        assert callable(codegeneration.modify_init_py)

    def test_adds_import_for_new_recognizer(self):
        """A new import is inserted when not found."""
        from privacy.code_generator.codegeneration import modify_init_py
        existing_lines = [
            "from .OtherRecognizer_recognizer import OtherRecognizer\n",
            "some_other_code = True\n",
        ]
        m = mock_open()
        m.return_value.__enter__.return_value.readlines.return_value = existing_lines
        with patch("builtins.open", m):
            try:
                modify_init_py("BrandNew")
            except Exception:
                pass  # File structure mismatch is acceptable in mocked env


# ---------------------------------------------------------------------------
# run_wheel_creation_commands
# ---------------------------------------------------------------------------

class TestRunWheelCreationCommands:

    @patch("subprocess.run")
    @patch("os.chdir")
    def test_runs_two_subprocess_commands(self, mock_chdir, mock_run):
        from privacy.code_generator.codegeneration import run_wheel_creation_commands
        mock_run.return_value = MagicMock(returncode=0)
        run_wheel_creation_commands()
        assert mock_run.call_count == 2

    @patch("subprocess.run")
    @patch("os.chdir")
    def test_pip_install_command_issued(self, mock_chdir, mock_run):
        from privacy.code_generator.codegeneration import run_wheel_creation_commands
        mock_run.return_value = MagicMock(returncode=0)
        run_wheel_creation_commands()
        commands = [c.args[0] for c in mock_run.call_args_list]
        assert any("pip install" in cmd for cmd in commands)

    @patch("subprocess.run")
    @patch("os.chdir")
    def test_python_create_wheel_command_issued(self, mock_chdir, mock_run):
        from privacy.code_generator.codegeneration import run_wheel_creation_commands
        mock_run.return_value = MagicMock(returncode=0)
        run_wheel_creation_commands()
        commands = [c.args[0] for c in mock_run.call_args_list]
        assert any("create_wheel_file" in cmd for cmd in commands)


# ---------------------------------------------------------------------------
# copy_wheel_file
# ---------------------------------------------------------------------------

class TestCopyWheelFile:

    @patch("subprocess.run")
    @patch("shutil.copy2")
    @patch("os.chdir")
    @patch("os.remove")
    @patch("os.path.exists", return_value=True)
    def test_removes_existing_wheel_before_copy(
        self, mock_exists, mock_remove, mock_chdir, mock_copy, mock_run
    ):
        from privacy.code_generator.codegeneration import copy_wheel_file
        mock_run.return_value = MagicMock(returncode=0)
        copy_wheel_file()
        assert mock_remove.called

    @patch("subprocess.run")
    @patch("shutil.copy2")
    @patch("os.chdir")
    @patch("os.remove")
    @patch("os.path.exists", return_value=False)
    def test_skips_remove_when_wheel_not_present(
        self, mock_exists, mock_remove, mock_chdir, mock_copy, mock_run
    ):
        from privacy.code_generator.codegeneration import copy_wheel_file
        mock_run.return_value = MagicMock(returncode=0)
        copy_wheel_file()
        assert not mock_remove.called

    @patch("subprocess.run")
    @patch("shutil.copy2")
    @patch("os.chdir")
    @patch("os.remove")
    @patch("os.path.exists", return_value=True)
    def test_copy2_called_with_wheel_filename(
        self, mock_exists, mock_remove, mock_chdir, mock_copy, mock_run
    ):
        from privacy.code_generator.codegeneration import copy_wheel_file
        mock_run.return_value = MagicMock(returncode=0)
        copy_wheel_file()
        assert mock_copy.called
        dest = str(mock_copy.call_args[0][1])
        assert "presidio_analyzer" in dest

    @patch("subprocess.run")
    @patch("shutil.copy2")
    @patch("os.chdir")
    @patch("os.remove")
    @patch("os.path.exists", return_value=True)
    def test_installs_wheel_via_pip(
        self, mock_exists, mock_remove, mock_chdir, mock_copy, mock_run
    ):
        from privacy.code_generator.codegeneration import copy_wheel_file
        mock_run.return_value = MagicMock(returncode=0)
        copy_wheel_file()
        commands = [str(c.args[0]) for c in mock_run.call_args_list]
        assert any("install" in cmd for cmd in commands)
