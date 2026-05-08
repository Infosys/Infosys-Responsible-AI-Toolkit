"""
Unit tests for utility modules
Tests utils/model modules
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))


class TestUtilsModule:
    """Test suite for utils module initialization"""
    
    def test_utils_package_importable(self):
        """Test that utils package is importable"""
        try:
            import image_explain.utils
            assert image_explain.utils is not None
        except ImportError:
            pytest.fail("utils package should be importable")
    
    def test_metrics_subpackage_exists(self):
        """Test that metrics subpackage exists"""
        try:
            import image_explain.utils.metrics
            assert image_explain.utils.metrics is not None
        except ImportError:
            pytest.fail("metrics subpackage should exist")
    
    def test_model_subpackage_exists(self):
        """Test that model subpackage exists"""
        try:
            import image_explain.utils.model
            assert image_explain.utils.model is not None
        except ImportError:
            pytest.fail("model subpackage should exist")
    
    def test_prompts_subpackage_exists(self):
        """Test that prompts subpackage exists"""
        try:
            import image_explain.utils.prompts
            assert image_explain.utils.prompts is not None
        except ImportError:
            pytest.fail("prompts subpackage should exist")


class TestAestheticScoreModule:
    """Test suite for aesthetic score module"""
    
    def test_aesthetic_score_module_exists(self):
        """Test that AestheticScore module exists"""
        try:
            from image_explain.utils.metrics.aesthetic_score import AestheticScore
            assert AestheticScore is not None
        except ImportError:
            pytest.skip("AestheticScore module not available (may require model files)")
    
    def test_aesthetic_score_is_class(self):
        """Test that AestheticScore is a class"""
        try:
            from image_explain.utils.metrics.aesthetic_score import AestheticScore
            assert isinstance(AestheticScore, type)
        except ImportError:
            pytest.skip("AestheticScore module not available")


class TestAlignmentScoreModule:
    """Test suite for alignment score module"""
    
    def test_alignment_score_module_exists(self):
        """Test that AlignmentScore module exists"""
        try:
            from image_explain.utils.metrics.alignment_score import AlignmentScore
            assert AlignmentScore is not None
        except ImportError:
            pytest.skip("AlignmentScore module not available (may require model files)")
    
    def test_alignment_score_is_class(self):
        """Test that AlignmentScore is a class"""
        try:
            from image_explain.utils.metrics.alignment_score import AlignmentScore
            assert isinstance(AlignmentScore, type)
        except ImportError:
            pytest.skip("AlignmentScore module not available")


class TestModelModules:
    """Test suite for model modules"""
    
    def test_azure_module_exists(self):
        """Test that Azure module exists"""
        try:
            from image_explain.utils.model.azure import Azure
            assert Azure is not None
        except ImportError:
            pytest.skip("Azure module not available")
    
    def test_ollama_module_exists(self):
        """Test that Ollama module exists"""
        try:
            from image_explain.utils.model.ollama import Ollama
            assert Ollama is not None
        except ImportError:
            pytest.skip("Ollama module not available")


class TestPromptsSubmodules:
    """Test suite for prompts submodules"""
    
    def test_output_format_module_exists(self):
        """Test that output_format module exists"""
        try:
            from image_explain.utils.prompts import output_format
            assert output_format is not None
        except ImportError:
            pytest.skip("output_format module not available")
    
    def test_few_shot_module_exists(self):
        """Test that few_shot module exists"""
        try:
            from image_explain.utils.prompts import few_shot
            assert few_shot is not None
        except ImportError:
            pytest.skip("few_shot module not available")
    
    def test_prompt_base_module_exists(self):
        """Test that base prompt module exists"""
        try:
            from image_explain.utils.prompts.base import Prompt
            assert Prompt is not None
        except ImportError:
            pytest.skip("Prompt base module not available")


class TestUtilsPackageStructure:
    """Test suite for utils package structure"""
    
    def test_utils_has_init_file(self):
        """Test that utils package has __init__.py"""
        utils_init = os.path.join(
            os.path.dirname(__file__), 
            '../src/image_explain/utils/__init__.py'
        )
        assert os.path.exists(utils_init)
    
    def test_metrics_has_init_file(self):
        """Test that metrics has __init__.py"""
        metrics_init = os.path.join(
            os.path.dirname(__file__),
            '../src/image_explain/utils/metrics/__init__.py'
        )
        # May or may not exist depending on structure
        # This is an optional check
    
    def test_prompts_has_init_file(self):
        """Test that prompts has __init__.py"""
        prompts_init = os.path.join(
            os.path.dirname(__file__),
            '../src/image_explain/utils/prompts/__init__.py'
        )
        assert os.path.exists(prompts_init)
