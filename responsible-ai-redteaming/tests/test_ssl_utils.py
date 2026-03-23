'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
"""
Comprehensive tests for ssl_utils module.

Tests SSL/TLS verification configuration handling including:
- Boolean values (true/false, on/off)
- File path validation
- Default behavior
- Error handling for invalid values
"""

import os
import tempfile
from app.utility.ssl_utils import get_ssl_verify
from app.utility import ssl_utils


class TestSSLVerifyBoolean:
    """Tests for boolean SSL verification values."""
    
    def test_ssl_verify_default_true(self, monkeypatch):
        """Test default behavior returns True when env var not set."""
        monkeypatch.delenv('sslVerify', raising=False)
        get_ssl_verify.cache_clear()
        assert get_ssl_verify() is True
    
    def test_ssl_verify_boolean_true(self, monkeypatch):
        """Test 'true' string enables SSL verification."""
        monkeypatch.setenv("sslVerify", "true")
        get_ssl_verify.cache_clear()
        assert get_ssl_verify() is True
    
    def test_ssl_verify_boolean_false(self, monkeypatch):
        """Test 'false' string disables SSL verification."""
        monkeypatch.setenv('sslVerify', 'false')
        get_ssl_verify.cache_clear()
        assert get_ssl_verify() is False
    
    def test_ssl_verify_off(self, monkeypatch):
        """Test 'off' value disables SSL verification."""
        monkeypatch.setenv("sslVerify", "off")
        get_ssl_verify.cache_clear()
        assert get_ssl_verify() is False


class TestSSLVerifyFilePath:
    """Tests for file path SSL verification values."""
    
    def test_ssl_verify_valid_path(self, monkeypatch, tmp_path):
        """Test valid certificate file path is accepted."""
        pem = tmp_path / 'ca.pem'
        pem.write_text('CERT')
        monkeypatch.setenv('sslVerify', str(pem))
        get_ssl_verify.cache_clear()
        assert get_ssl_verify() == str(pem)
    
    def test_ssl_verify_temp_file_path(self, monkeypatch):
        """Test valid temporary certificate file."""
        fd, path = tempfile.mkstemp(suffix=".pem")
        os.close(fd)
        try:
            monkeypatch.setenv("sslVerify", path)
            get_ssl_verify.cache_clear()
            assert get_ssl_verify() == path
        finally:
            os.remove(path)
    
    def test_ssl_verify_missing_path(self, monkeypatch, caplog):
        """Test nonexistent file path falls back to True with warning."""
        monkeypatch.setenv("sslVerify", "C:/nonexistent/cert.pem")
        get_ssl_verify.cache_clear()
        val = get_ssl_verify()
        assert val is True
        assert any("not found" in rec.message for rec in caplog.records)


class TestSSLVerifyEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_ssl_verify_unrecognized_value(self, monkeypatch, caplog):
        """Test unrecognized value falls back to True with warning."""
        monkeypatch.setenv('sslVerify', 'weirdTokenValue')
        get_ssl_verify.cache_clear()
        val = get_ssl_verify()
        assert val is True
        assert any('Unrecognized sslVerify' in r.message for r in caplog.records)
    
    def test_ssl_verify_another_unrecognized(self, monkeypatch, caplog):
        """Test another unrecognized value scenario."""
        monkeypatch.setenv("sslVerify", "weird-token-value")
        get_ssl_verify.cache_clear()
        val = get_ssl_verify()
        assert val is True
        assert any("Unrecognized sslVerify" in rec.message for rec in caplog.records)
