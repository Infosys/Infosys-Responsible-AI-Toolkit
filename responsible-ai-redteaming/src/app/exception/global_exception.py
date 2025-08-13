'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


import sys, traceback

from app.constants import global_constants

from abc import ABC

class AicloudException(Exception, ABC):
    """
    Abstract base class of all Aicloud DB exceptions.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class DbConnectionError(AicloudException):
     def __init__(self,name):
        self.status_code = global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        self.message = global_constants.ERR_CONNECTION_REFUSED + name

class DataError(AicloudException):
     def __init__(self,msg):
        self.status_code = global_constants.HTTP_STATUS_DATA_PROCESSING_ERROR
        if not msg:
            self.message = global_constants.DATA_ERROR
        else: 
            self.message=msg

class OperationalError(AicloudException):
     def __init__(self,msg):
        self.status_code = global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        if not msg:
            self.message = global_constants.OPERATIONAL_ERROR
        else: 
            self.message=msg

class IntegrityError(AicloudException):
     def __init__(self,msg):
        self.status_code = global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        if not msg:
            self.message = global_constants.OPERATIONAL_ERROR
        else: 
            self.message=msg


class InternalError(AicloudException):
     def __init__(self,msg):
        self.status_code = global_constants.HTTP_STATUS_BAD_REQUEST
        if not msg:
            self.message = global_constants.DATA_ERROR
        else: 
            self.message=msg

class NotSupportedError(AicloudException):
     def __init__(self,msg):
        self.status_code = global_constants.HTTP_STATUS_NOT_ALLLOWED
        if not msg:
            self.message = global_constants.NOT_ALLOWED_MESSAGE
        else: 
            self.message=msg

class DatabaseError(AicloudException):
     def __init__(self,name):
        self.status_code = global_constants.HTTP_STATUS_NOT_FOUND
        self.message = name + global_constants.DATABASE_ERROR + name

class ForbiddenError(AicloudException):
     def __init__(self,msg):
        self.status_code = global_constants.HTTP_STATUS_FORBIDDEN
        if not msg:
            self.message = global_constants.FORBIDDEN_ERROR_MESSAGE
        else: 
            self.message=msg

class InternalServerError(AicloudException):
     def __init__(self,msg):
        self.status_code = global_constants.HTTP_STATUS_BAD_REQUEST
        if not msg:
            self.message = global_constants.DATA_ERROR
        else: 
            self.message=msg

class IncompleteRead(AicloudException):
    def __init__(self,msg):
        self.status_code = global_constants.HTTP_STATUS_BAD_REQUEST
        if not msg:
            self.message = global_constants.DATA_ERROR
        else: 
            self.message=msg

class MethodArgumentNotValidException(AicloudException):
    def __init__(self,msg):
        self.status_code = global_constants.HTTP_STATUS_BAD_REQUEST
        if not msg:
            self.message = global_constants.DATA_ERROR
        else: 
            self.message=msg

class UnSupportedMediaTypeException(AicloudException):
    def __init__(self,contentTypeStr):
        self.status_code = global_constants.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        self.message = global_constants.UNSUPPPORTED_MEDIA_TYPE_ERROR + contentTypeStr
        