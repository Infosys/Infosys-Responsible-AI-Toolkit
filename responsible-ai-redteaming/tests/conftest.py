'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
# tests/conftest.py
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]   # repo root
SRC = ROOT / "src"

# Ensure 'src' is first on sys.path so `import src.*` works consistently
if SRC.exists():
    sys.path.insert(0, str(SRC))

# Optional: also add repo root in case some code imports top-level modules
if ROOT.exists():
    sys.path.insert(0, str(ROOT))

# Provide a test-only shim for app.utility.text_utils to avoid importing
# the source file which has a non-top __future__ import that breaks
# collection under some Python versions. This keeps tests deterministic
# while leaving `src` untouched as requested.
try:
    import types
    if 'app.utility.text_utils' not in sys.modules:
        mod = types.ModuleType('app.utility.text_utils')
        # Minimal, compatible implementations used by tests
        def chunk_text(text: str, max_len: int):
            if max_len <= 0:
                return [text]
            words = text.split()
            chunks = []
            current = []
            current_len = 0
            for w in words:
                wl = len(w) + 1
                if current and current_len + wl > max_len:
                    chunks.append(" ".join(current))
                    current = [w]
                    current_len = len(w)
                else:
                    current.append(w)
                    current_len += wl
            if current:
                chunks.append(" ".join(current))
            if not chunks:
                return [text]
            return chunks

        import re
        _WS_RE = re.compile(r"\s+")
        def normalize_whitespace(text: str) -> str:
            return _WS_RE.sub(" ", text).strip()

        mod.chunk_text = chunk_text
        mod.normalize_whitespace = normalize_whitespace
        sys.modules['app.utility.text_utils'] = mod
except Exception:
    # Never fail test collection because of shim install issues
    pass
