'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from datetime import datetime, timezone, timedelta
from app.utility.language_models import BedrockModel

# We only exercise the static method; constructing BedrockModel fully is avoided.

def test_is_time_difference_inside_window():
    creation = datetime.now(timezone.utc) - timedelta(hours=1)
    assert BedrockModel.is_time_difference_12_hours(creation, 12) is True


def test_is_time_difference_outside_window():
    creation = datetime.now(timezone.utc) - timedelta(hours=13)
    assert BedrockModel.is_time_difference_12_hours(creation, 12) is False


def test_is_time_difference_naive_creation():
    # Provide naive datetime; method should treat as UTC
    creation = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=2)
    assert BedrockModel.is_time_difference_12_hours(creation, 1) is False
