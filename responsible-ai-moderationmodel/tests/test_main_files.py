"""
Tests for main_*.py entry point files
These files are Flask application entry points - testing by syntax check and structure validation
"""

import pytest
import sys
import os
import subprocess


class TestMainFilesSyntax:
    """Test that main files have valid Python syntax"""
    
    def test_main_py_syntax(self):
        """Test main.py has valid syntax"""
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', 'src/main.py'],
            cwd=os.path.join(os.path.dirname(__file__), '..'),
            capture_output=True
        )
        assert result.returncode == 0, f"Syntax error in main.py: {result.stderr.decode()}"
    
    def test_main_mm_syntax(self):
        """Test main_MM.py has valid syntax"""
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', 'src/main_MM.py'],
            cwd=os.path.join(os.path.dirname(__file__), '..'),
            capture_output=True
        )
        assert result.returncode == 0, f"Syntax error in main_MM.py: {result.stderr.decode()}"
    
    def test_main_detoxify_syntax(self):
        """Test main_detoxify.py has valid syntax"""
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', 'src/main_detoxify.py'],
            cwd=os.path.join(os.path.dirname(__file__), '..'),
            capture_output=True
        )
        assert result.returncode == 0, f"Syntax error in main_detoxify.py: {result.stderr.decode()}"
    
    def test_main_embeding_syntax(self):
        """Test main_embeding.py has valid syntax"""
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', 'src/main_embeding.py'],
            cwd=os.path.join(os.path.dirname(__file__), '..'),
            capture_output=True
        )
        assert result.returncode == 0, f"Syntax error in main_embeding.py: {result.stderr.decode()}"
    
    def test_main_injection_syntax(self):
        """Test main_injection.py has valid syntax"""
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', 'src/main_injection.py'],
            cwd=os.path.join(os.path.dirname(__file__), '..'),
            capture_output=True
        )
        assert result.returncode == 0, f"Syntax error in main_injection.py: {result.stderr.decode()}"
    
    def test_main_privacy_syntax(self):
        """Test main_privacy.py has valid syntax"""
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', 'src/main_privacy.py'],
            cwd=os.path.join(os.path.dirname(__file__), '..'),
            capture_output=True
        )
        assert result.returncode == 0, f"Syntax error in main_privacy.py: {result.stderr.decode()}"
    
    def test_main_topic_syntax(self):
        """Test main_topic.py has valid syntax"""
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', 'src/main_topic.py'],
            cwd=os.path.join(os.path.dirname(__file__), '..'),
            capture_output=True
        )
        assert result.returncode == 0, f"Syntax error in main_topic.py: {result.stderr.decode()}"


class TestMainFilesStructure:
    """Test that main files contain expected components"""
    
    def test_main_mm_contains_security_headers(self):
        """Test main_MM.py contains add_security_headers function"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'main_MM.py'), 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'def add_security_headers' in content
            assert "X-Content-Type-Options" in content
            assert "X-Frame-Options" in content
    
    def test_main_mm_contains_error_handlers(self):
        """Test main_MM.py contains error handlers"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'main_MM.py'), 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'def handle_http_exception' in content
            assert 'def handle_unsupported_mediatype' in content
    
    def test_main_mm_contains_router_config(self):
        """Test main_MM.py contains ROUTER_CONFIG"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'main_MM.py'), 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'ROUTER_CONFIG' in content
            assert 'INJECTION_MODEL' in content
            assert 'DETOXIFY_MODEL' in content
    
    def test_main_detoxify_contains_security_headers(self):
        """Test main_detoxify.py contains add_security_headers function"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'main_detoxify.py'), 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'def add_security_headers' in content
            assert "X-XSS-Protection" in content
    
    def test_main_detoxify_contains_swagger_config(self):
        """Test main_detoxify.py contains Swagger configuration"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'main_detoxify.py'), 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'SWAGGER_URL' in content
            assert 'detoxifymodel/docs' in content
    
    def test_main_injection_contains_security_headers(self):
        """Test main_injection.py contains security headers"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'main_injection.py'), 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'def add_security_headers' in content
            assert "Content-Security-Policy" in content
    
    def test_main_injection_contains_swagger_config(self):
        """Test main_injection.py contains Swagger configuration"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'main_injection.py'), 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'promptinjectionmodel/docs' in content
    
    def test_main_privacy_contains_security_headers(self):
        """Test main_privacy.py contains security headers"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'main_privacy.py'), 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'def add_security_headers' in content
    
    def test_main_privacy_contains_swagger_config(self):
        """Test main_privacy.py contains Swagger configuration"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'main_privacy.py'), 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'privacy/docs' in content
    
    def test_main_topic_contains_security_headers(self):
        """Test main_topic.py contains security headers"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'main_topic.py'), 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'def add_security_headers' in content
    
    def test_main_topic_contains_swagger_config(self):
        """Test main_topic.py contains Swagger configuration"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'main_topic.py'), 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'restrictedtopicmodel/docs' in content
    
    def test_main_embeding_contains_security_headers(self):
        """Test main_embeding.py contains security headers"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'main_embeding.py'), 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'def add_security_headers' in content
    
    def test_main_embeding_contains_swagger_config(self):
        """Test main_embeding.py contains Swagger configuration"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'main_embeding.py'), 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'embeding/docs' in content


class TestMainFilesServerConfig:
    """Test that main files contain server configuration"""
    
    def test_main_files_use_waitress(self):
        """Test that main files use waitress server"""
        main_files = ['main_detoxify.py', 'main_embeding.py', 'main_injection.py', 'main_privacy.py', 'main_topic.py', 'main_MM.py']
        
        for filename in main_files:
            with open(os.path.join(os.path.dirname(__file__), '..', 'src', filename), 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'from waitress import serve' in content, f"{filename} should import waitress.serve"
                assert 'serve(' in content, f"{filename} should call serve()"
    
    def test_main_files_register_blueprints(self):
        """Test that main files register Flask blueprints"""
        main_files = ['main_detoxify.py', 'main_embeding.py', 'main_injection.py', 'main_privacy.py', 'main_topic.py', 'main_MM.py']
        
        for filename in main_files:
            with open(os.path.join(os.path.dirname(__file__), '..', 'src', filename), 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'app.register_blueprint' in content, f"{filename} should register blueprints"
    
    def test_main_files_have_error_handlers(self):
        """Test that main files have error handlers"""
        main_files = ['main_detoxify.py', 'main_embeding.py', 'main_injection.py', 'main_privacy.py', 'main_topic.py', 'main_MM.py']
        
        for filename in main_files:
            with open(os.path.join(os.path.dirname(__file__), '..', 'src', filename), 'r', encoding='utf-8') as f:
                content = f.read()
                assert '@app.errorhandler' in content or 'handle_http_exception' in content, \
                    f"{filename} should have error handlers"
    
    def test_main_files_apply_security_headers(self):
        """Test that main files apply security headers to responses"""
        main_files = ['main_detoxify.py', 'main_embeding.py', 'main_injection.py', 'main_privacy.py', 'main_topic.py', 'main_MM.py']
        
        for filename in main_files:
            with open(os.path.join(os.path.dirname(__file__), '..', 'src', filename), 'r', encoding='utf-8') as f:
                content = f.read()
                assert '@app.after_request' in content, f"{filename} should have after_request decorator"
                assert 'add_security_headers' in content, f"{filename} should call add_security_headers"
