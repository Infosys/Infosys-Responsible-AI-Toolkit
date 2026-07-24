"""
MIT License
Copyright © 2025 Infosys Ltd.

Comprehensive tests for src/setup.py - Package setup and requirements
"""

import ast
import types

import pytest
from unittest.mock import MagicMock
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SETUP_FILE = PROJECT_ROOT / 'src' / 'setup.py'
_REQUIREMENTS_LITERAL = 'requirementS/requirement.txt'


def _patch_requirements_literal(monkeypatch, new_path):
    """Replace the string literal path with a Path for deterministic testing."""
    import src.setup as setup_module

    original = setup_module.get_install_requires
    consts = list(original.__code__.co_consts)
    replaced = False
    for idx, value in enumerate(consts):
        if value == _REQUIREMENTS_LITERAL:
            consts[idx] = new_path
            replaced = True
            break

    if not replaced:
        pytest.fail('requirements literal not found; source structure changed')

    new_code = original.__code__.replace(co_consts=tuple(consts))
    patched_function = types.FunctionType(
        new_code,
        original.__globals__,
        name=original.__name__,
        argdefs=original.__defaults__,
        closure=original.__closure__,
    )

    monkeypatch.setattr(setup_module, 'get_install_requires', patched_function)
    return setup_module


def _get_setup_call_node():
    """Locate the setup() call inside the __main__ guard using AST inspection."""
    source = SETUP_FILE.read_text(encoding='utf-8')
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = node.test
            if not isinstance(test, ast.Compare):
                continue
            if not isinstance(test.left, ast.Name) or test.left.id != '__name__':
                continue
            if not test.comparators or not isinstance(test.comparators[0], ast.Constant):
                continue
            if test.comparators[0].value != '__main__':
                continue
            for stmt in node.body:
                if (
                    isinstance(stmt, ast.Expr)
                    and isinstance(stmt.value, ast.Call)
                    and isinstance(stmt.value.func, ast.Name)
                    and stmt.value.func.id == 'setup'
                ):
                    return stmt.value

    raise AssertionError('setup() call not found in src/setup.py')


class TestSetupBasicBehaviors:
    """Lightweight sanity checks mirrored from the legacy suite."""

    def test_get_install_requires_exists(self):
        from src.setup import get_install_requires

        assert callable(get_install_requires)

    def test_get_install_requires_returns_list(self, tmp_path, monkeypatch):
        setup_module = _patch_requirements_literal(monkeypatch, tmp_path / 'missing.txt')

        result = setup_module.get_install_requires()

        assert isinstance(result, list)


class TestSetupGetInstallRequires:
    """Tests for get_install_requires function"""

    @staticmethod
    def _prepare_requirements(monkeypatch, tmp_path, content: str | None):
        requirements_path = tmp_path / "requirements.txt"
        if content is not None:
            requirements_path.write_text(content, encoding='utf-8')
        elif requirements_path.exists():
            requirements_path.unlink()

        setup_module = _patch_requirements_literal(monkeypatch, requirements_path)
        return setup_module

    def test_get_install_requires_success(self, tmp_path, monkeypatch):
        setup_module = self._prepare_requirements(
            monkeypatch,
            tmp_path,
            "numpy==1.21.0\npandas==1.3.0\nscipy>=1.5.0\n",
        )

        result = setup_module.get_install_requires()

        assert result == [
            'numpy==1.21.0',
            'pandas==1.3.0',
            'scipy>=1.5.0',
        ]

    def test_get_install_requires_single_package(self, tmp_path, monkeypatch):
        setup_module = self._prepare_requirements(
            monkeypatch,
            tmp_path,
            "requests==2.26.0\n",
        )

        result = setup_module.get_install_requires()

        assert result == ['requests==2.26.0']

    def test_get_install_requires_file_not_exists(self, tmp_path, monkeypatch):
        missing_path = tmp_path / "missing.txt"
        setup_module = _patch_requirements_literal(monkeypatch, missing_path)

        result = setup_module.get_install_requires()

        assert result == []

    def test_get_install_requires_empty_file(self, tmp_path, monkeypatch):
        setup_module = self._prepare_requirements(monkeypatch, tmp_path, "")

        result = setup_module.get_install_requires()

        assert result == []

    def test_get_install_requires_with_operators(self, tmp_path, monkeypatch):
        setup_module = self._prepare_requirements(
            monkeypatch,
            tmp_path,
            "numpy>=1.20.0\npandas<2.0.0\n",
        )

        result = setup_module.get_install_requires()

        assert result == ['numpy>=1.20.0', 'pandas<2.0.0']

    def test_get_install_requires_with_comments(self, tmp_path, monkeypatch):
        setup_module = self._prepare_requirements(
            monkeypatch,
            tmp_path,
            "# Comment\nnumpy==1.21.0\n# Another comment\n",
        )

        result = setup_module.get_install_requires()

        assert result == ['# Comment', 'numpy==1.21.0', '# Another comment']

    def test_get_install_requires_with_blank_lines(self, tmp_path, monkeypatch):
        setup_module = self._prepare_requirements(
            monkeypatch,
            tmp_path,
            "numpy==1.21.0\n\n\npandas==1.3.0\n",
        )

        result = setup_module.get_install_requires()

        assert result == ['numpy==1.21.0', '', '', 'pandas==1.3.0']

    def test_get_install_requires_special_names(self, tmp_path, monkeypatch):
        setup_module = self._prepare_requirements(
            monkeypatch,
            tmp_path,
            "package-name==1.0.0\npackage_name==1.0.0\n",
        )

        result = setup_module.get_install_requires()

        assert result == ['package-name==1.0.0', 'package_name==1.0.0']

    def test_get_install_requires_file_read_error(self, monkeypatch):
        import src.setup as setup_module

        fake_path = MagicMock()
        fake_path.exists.return_value = True
        fake_path.__fspath__.return_value = 'fake/path'

        _patch_requirements_literal(monkeypatch, fake_path)

        def failing_open(*_, **__):
            raise IOError("Cannot read file")

        monkeypatch.setattr('builtins.open', failing_open)

        with pytest.raises(IOError):
            setup_module.get_install_requires()

    def test_get_install_requires_no_version(self, tmp_path, monkeypatch):
        setup_module = self._prepare_requirements(
            monkeypatch,
            tmp_path,
            "numpy\npandas\n",
        )

        result = setup_module.get_install_requires()

        assert result == ['numpy', 'pandas']

    def test_get_install_requires_with_extras(self, tmp_path, monkeypatch):
        setup_module = self._prepare_requirements(
            monkeypatch,
            tmp_path,
            "numpy[extra]==1.21.0\n",
        )

        result = setup_module.get_install_requires()

        assert result == ['numpy[extra]==1.21.0']


class TestSetupMain:
    """Static analysis of the __main__ guard and setup() invocation."""

    def test_setup_invokes_helper_functions(self):
        call_node = _get_setup_call_node()
        kwargs = {kw.arg: kw.value for kw in call_node.keywords}

        packages_call = kwargs['packages']
        install_call = kwargs['install_requires']

        assert isinstance(packages_call, ast.Call)
        assert isinstance(packages_call.func, ast.Name)
        assert packages_call.func.id == 'find_packages'

        assert isinstance(install_call, ast.Call)
        assert isinstance(install_call.func, ast.Name)
        assert install_call.func.id == 'get_install_requires'

    def test_setup_specifies_core_arguments(self):
        call_node = _get_setup_call_node()
        provided_args = {kw.arg for kw in call_node.keywords}

        expected = {
            'name',
            'url',
            'packages',
            'include_package_data',
            'python_requires',
            'version',
            'description',
            'install_requires',
            'author',
            'license',
        }

        assert expected.issubset(provided_args)


class TestSetupConfiguration:
    """Tests for setup configuration"""
    
    def test_setup_module_imports(self):
        """Test that setup module imports correctly"""
        try:
            from src.setup import get_install_requires, setup, find_packages, Path
            assert get_install_requires is not None
            assert setup is not None
            assert find_packages is not None
            assert Path is not None
        except ImportError as e:
            pytest.fail(f"Failed to import from setup: {e}")
    
    def test_requirements_file_path_format(self, tmp_path, monkeypatch):
        """Test requirements file path format"""
        setup_module = _patch_requirements_literal(monkeypatch, tmp_path / 'missing.txt')

        result = setup_module.get_install_requires()

        assert result == []
    
    def test_empty_requirements_returns_empty_list(self, tmp_path, monkeypatch):
        """Test that empty requirements returns empty list"""
        setup_module = TestSetupGetInstallRequires._prepare_requirements(
            monkeypatch,
            tmp_path,
            "",
        )

        result = setup_module.get_install_requires()

        assert result == []


class TestSetupMetadataValues:
    """Ensure the setup() invocation uses the expected metadata."""

    def test_setup_metadata_configuration(self):
        call_node = _get_setup_call_node()
        kwargs = {kw.arg: kw.value for kw in call_node.keywords}

        assert ast.literal_eval(kwargs['name']) == 'Foundationmodel-ai-moderation-layer'
        assert ast.literal_eval(kwargs['python_requires']) == '>=3.6'
        assert ast.literal_eval(kwargs['version']) == '0.1.0'
        assert ast.literal_eval(kwargs['license']) == 'MIT'
        assert ast.literal_eval(kwargs['include_package_data']) is True

    def test_setup_callable_is_exposed(self):
        from src.setup import setup

        assert callable(setup)
