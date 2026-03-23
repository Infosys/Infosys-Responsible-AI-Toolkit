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

from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from .global_exception import UnSupportedMediaTypeException
from .constants import HTTP_STATUS_CODES

def validation_error_handler(exc: RequestValidationError):
    return JSONResponse(
        status_code=HTTP_STATUS_CODES["UNPROCESSABLE_ENTITY"],
        content=jsonable_encoder({"ERROR": exc.errors()}),
    )

def unsupported_mediatype_error_handler(exc: UnSupportedMediaTypeException):
    return JSONResponse(
        status_code=HTTP_STATUS_CODES["UNSUPPORTED_MEDIA_TYPE"],
        content=jsonable_encoder({"ERROR": str(exc.message)}),
    )

def http_exception_handler(exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({"ERROR": str(exc.detail)}),
    )