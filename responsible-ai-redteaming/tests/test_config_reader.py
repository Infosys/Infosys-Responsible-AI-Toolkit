'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import tempfile
from configparser import NoSectionError
from app.config.config import read_config

def test_read_config_success():
    # Use delete=False so Windows can reopen the file while still open
    content = """[sample]\nkey=value\n"""
    tmp = tempfile.NamedTemporaryFile('w', delete=False)
    try:
        tmp.write(content)
        tmp.close()  # Close so ConfigParser can re-open reliably on Windows
        data = read_config('sample', tmp.name)
    finally:
        try:
            import os
            os.unlink(tmp.name)
        except OSError:
            pass
    assert data['key'] == 'value'


def test_read_config_missing_section():
    content = """[other]\nkey=value\n"""
    with tempfile.NamedTemporaryFile('w+', delete=True) as f:
        f.write(content)
        f.flush()
        try:
            read_config('missing', f.name)
        except NoSectionError as e:
            assert e.section == 'missing'
        else:
            assert False, "Expected NoSectionError"
