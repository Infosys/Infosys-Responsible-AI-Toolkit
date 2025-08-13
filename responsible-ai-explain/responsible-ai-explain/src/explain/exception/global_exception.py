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

from .constants import HTTP_STATUS_CODES
from abc import ABC

class BenchmarkExceptions(Exception, ABC):
    """
    Abstract base class of all Aicloud DB exceptions.
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)

class DBConnectionError(BenchmarkExceptions):
     def __init__(self, name):
        self.status_code = HTTP_STATUS_CODES.SERVICE_UNAVAILABLE
        self.message = HTTP_STATUS_CODES.DATABASE_CONNECTION_REFUSED + name

class NotSupportedError(BenchmarkExceptions):
     def __init__(self, msg):
        self.status_code = HTTP_STATUS_CODES.METHOD_NOT_ALLOWED
        if not msg:
            self.message = HTTP_STATUS_CODES.METHOD_NOT_ALLOWED
        else: 
            self.message=msg

class InternalServerError(BenchmarkExceptions):
     def __init__(self, msg):
        self.status_code = HTTP_STATUS_CODES.INTERNAL_SERVER_ERROR
        if not msg:
            self.message = HTTP_STATUS_CODES.INTERNAL_SERVER_ERROR
        else: 
            self.message=msg

class MethodArgumentNotValidException(BenchmarkExceptions):
    def __init__(self, msg):
        self.status_code = HTTP_STATUS_CODES.BAD_REQUEST
        if not msg:
            self.message = HTTP_STATUS_CODES.BAD_REQUEST
        else: 
            self.message=msg

class UnSupportedMediaTypeException(BenchmarkExceptions):
    def __init__(self, contentTypeStr):
        self.status_code = HTTP_STATUS_CODES.UNSUPPORTED_MEDIA_TYPE
        self.message = HTTP_STATUS_CODES.UNSUPPORTED_MEDIA_TYPE + contentTypeStr