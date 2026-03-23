'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import pytest


def test_usecase_exceptions_status_and_messages():
    from app.exception.exception import aiShieldNotFoundError, aiShieldNameNotEmptyError
    from app.constants import global_constants as gc
    from app.constants.local_constants import USECASE_NOT_FOUND_ERROR, USECASE_NAME_VALIDATION_ERROR, PLACEHOLDER_TEXT

    e1 = aiShieldNotFoundError("CaseA")
    assert e1.status_code == gc.HTTP_STATUS_NOT_FOUND
    assert "CaseA" in e1.detail and USECASE_NOT_FOUND_ERROR.replace(PLACEHOLDER_TEXT, "CaseA") == e1.detail

    e2 = aiShieldNameNotEmptyError("CaseB")
    assert e2.status_code == gc.HTTP_STATUS_409_CODE
    assert e2.detail == USECASE_NAME_VALIDATION_ERROR
