'''
MIT License
https://mit-license.org/
Copyright 2025-2026 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''



'''
Utility helpers for determining SSL verification behavior based on the sslVerify environment variable.

Rules:
- If sslVerify is unset or blank -> return True (default secure)
- Accept typical boolean strings (case-insensitive): 'true','1','yes','y','on' => True; 'false','0','no','n','off' => False
- If the value looks like a path to an existing file (e.g. ends with .pem / .crt) and file exists => return that path so requests will use provided CA bundle.
- If the value equals 'system' => return True (use system cert store)
- Any other non-empty string that does not map to boolean and file not found => fallback True for safety and log a warning (without breaking flow).
'''
import os
import logging
from functools import lru_cache

log = logging.getLogger(__name__)

_BOOLEAN_TRUE = {"true","1","yes","y","on"}
_BOOLEAN_FALSE = {"false","0","no","n","off"}

@lru_cache(maxsize=1)
def get_ssl_verify():
    raw = os.getenv("sslVerify")
    if raw is None:
        return True
    raw_stripped = raw.strip().strip('"').strip("'")
    if raw_stripped == "":
        return True
    lower = raw_stripped.lower()
    if lower in _BOOLEAN_TRUE:
        return True
    if lower in _BOOLEAN_FALSE:
        return False
    if lower == "system":
        return True
    
    if os.path.isfile(raw_stripped):
        return raw_stripped
    if any(sep in raw_stripped for sep in ("/","\\")):
        log.warning(f"sslVerify path '{raw_stripped}' not found; falling back to system cert store.")
        return True
    
    log.warning(f"Unrecognized sslVerify value '{raw_stripped}'. Using secure default verify=True.")
    return True

__all__ = ["get_ssl_verify"]
