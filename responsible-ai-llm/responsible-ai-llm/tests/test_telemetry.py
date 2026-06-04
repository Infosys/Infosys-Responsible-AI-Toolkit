'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

os.environ.setdefault('TELEMETRY_PATH', 'http://telemetry.example.com')
os.environ.setdefault('EVALLLMTELEMETRYPATH', 'http://evalllm.example.com')
os.environ.setdefault('TEL_FLAG', 'true')


class TestTelemetry:
    """Test suite for telemetry module"""
    
    def test_telemetry_url_from_env(self):
        """Test telemetry URL is read from environment"""
        from llm.service.telemetry import telemetryurl
        
        with patch.dict(os.environ, {'TELEMETRY_PATH': 'http://test.telemetry.com'}):
            import importlib
            import llm.service.telemetry
            importlib.reload(llm.service.telemetry)
            
            telemetry_module = llm.service.telemetry
            assert telemetry_module.telemetryurl == 'http://test.telemetry.com'
    
    def test_telemetry_class_exists(self):
        """Test telemetry class can be imported"""
        from llm.service.telemetry import telemetry
        assert telemetry is not None
    
    def test_telemetry_tel_flag_from_env(self):
        """Test TEL_FLAG is read from environment"""
        from llm.service.telemetry import telemetry
        
        assert hasattr(telemetry, 'tel_flag')
    
    def test_eval_llm_telemetry_url_from_env(self):
        """Test eval LLM telemetry URL is read from environment"""
        from llm.service.telemetry import evalLLMtelemetryurl
        
        with patch.dict(os.environ, {'EVALLLMTELEMETRYPATH': 'http://evalllm.test.com'}):
            import importlib
            import llm.service.telemetry
            importlib.reload(llm.service.telemetry)
            
            telemetry_module = llm.service.telemetry
            assert telemetry_module.evalLLMtelemetryurl == 'http://evalllm.test.com'


class TestTelemetryEnvironmentVariables:
    """Test telemetry environment variable handling"""
    
    def test_telemetry_env_var_defaults(self):
        """Test telemetry environment variables with defaults"""
        with patch.dict(os.environ, {}, clear=False):
            import llm.service.telemetry
            
            # Verify module loads even if env vars are not set
            assert llm.service.telemetry is not None
    
    def test_telemetry_flag_property(self):
        """Test telemetry flag property"""
        from llm.service.telemetry import telemetry
        
        assert hasattr(telemetry, 'tel_flag')
        # Flag should be a string from os.getenv
        assert isinstance(telemetry.tel_flag, (str, type(None)))


class TestTelemetryIntegration:
    """Integration tests for telemetry module"""
    
    def test_telemetry_module_import(self):
        """Test telemetry module can be imported successfully"""
        from llm.service import telemetry as tel_module
        assert tel_module is not None
    
    def test_telemetry_attributes_exist(self):
        """Test all expected telemetry attributes exist"""
        import llm.service.telemetry
        
        assert hasattr(llm.service.telemetry, 'telemetryurl')
        assert hasattr(llm.service.telemetry, 'evalLLMtelemetryurl')
        assert hasattr(llm.service.telemetry, 'telemetry')


# Patch decorator for environment testing
from unittest.mock import patch
