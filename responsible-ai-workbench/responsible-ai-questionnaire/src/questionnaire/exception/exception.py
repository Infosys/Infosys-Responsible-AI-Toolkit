'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""
fileName: exception.py
description: handles usecase module specific exception
"""

import sys, traceback

from questionnaire.constants.local_constants  import SPACE_DELIMITER,PLACEHOLDER_TEXT,USECASE_ALREADY_EXISTS,USECASE_NOT_FOUND_ERROR,USECASE_NAME_VALIDATION_ERROR
from questionnaire.constants.global_constants import *
from abc import ABC
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

class PrivacyException(Exception, ABC):
    """
    dscription: Abstract base class of UsecaseException.
    """

    def __init__(self, detail: str) -> None:
        self.status_code = HTTP_STATUS_BAD_REQUEST
        super().__init__(detail)


class PrivacyNotFoundError(PrivacyException):
    """
    description: UsecaseNotFoundError thrown by usecase service
                 when the requested usecase details not found for a specific user.
    """
    def __init__(self,name):
        self.status_code = HTTP_STATUS_NOT_FOUND
        self.detail =  USECASE_NOT_FOUND_ERROR.replace(PLACEHOLDER_TEXT,name)

class PrivacyNameNotEmptyError(PrivacyException):
    """
    description: UsecaseNameNotEmptyError thrown by create usecase service
                 when the requested usecase details not having usecase name.
    """
    def __init__(self,name):
        self.status_code = HTTP_STATUS_409_CODE
        self.detail =  USECASE_NAME_VALIDATION_ERROR

class UnSupportedMediaTypeException(Exception):
    """Exception raised for unsupported media type."""
    def __init__(self, message: str = "Unsupported media type"):
        self.message = message
        super().__init__(self.message)

def validation_error_handler(exc: RequestValidationError) -> JSONResponse:
    """
    Handle validation errors in request data
    """
    errors = []
    for error in exc.errors():
        error_detail = {
            "location": error.get("loc", ["unknown"]),
            "message": error.get("msg", "Unknown error"),
            "type": error.get("type", "unknown")
        }
        errors.append(error_detail)
    
    return JSONResponse(
        status_code=HTTP_STATUS_UNPROCESSABLE_ENTITY,
        content={"detail": errors, "message": "Validation error"}
    )

def unsupported_mediatype_error_handler(exc: UnSupportedMediaTypeException) -> JSONResponse:
    """
    Handle unsupported media type errors
    """
    return JSONResponse(
        status_code=415,
        content={"detail": exc.message, "message": "Unsupported Media Type"}
    )

def http_exception_handler(exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail), "message": "HTTP Error"}
    )