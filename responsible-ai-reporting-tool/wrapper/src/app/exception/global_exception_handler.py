'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


import os,sys

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .global_exception import UnSupportedMediaTypeException
from fastapi.encoders import jsonable_encoder

from app.constants import global_constants


def validation_error_handler(exc: RequestValidationError):
    return JSONResponse(
        status_code=int(global_constants.HTTP_422_UNPROCESSABLE_ENTITY),
        content=jsonable_encoder({"detail": exc.errors()}),
    )

def  http_exception_handler(exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({"detail": str(exc.detail)})
    )

def unsupported_mediatype_error_handler(exc:UnSupportedMediaTypeException):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({"detail": str(exc.message)})
    )





#def my_except_hook(exctype, value, traceback):
    #sys.__excepthook__(exctype, value, traceback)


#sys.excepthook = my_except_hook




