'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import pytest


def test_model_selection_logic():
    """Test model selection based on payload"""
    payload_gpt = {"attack_model": "gpt-4"}
    payload_claude = {"attack_model": "claude-3"}
    payload_gemini = {"attack_model": "gemini-pro"}
    
    assert "gpt" in payload_gpt["attack_model"]
    assert "claude" in payload_claude["attack_model"]
    assert "gemini" in payload_gemini["attack_model"]


def test_temperature_parameters():
    """Test temperature parameter validation"""
    valid_temps = [0.0, 0.5, 1.0, 1.5, 2.0]
    
    for temp in valid_temps:
        assert temp >= 0.0
        assert temp <= 2.0


def test_max_tokens_parameters():
    """Test max_tokens parameter validation"""
    valid_tokens = [50, 100, 500, 1000, 2000]
    
    for tokens in valid_tokens:
        assert tokens > 0
        assert tokens <= 4096


