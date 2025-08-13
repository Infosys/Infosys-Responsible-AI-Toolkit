'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""
fileName: exception.py
description: handles usecase module specific exception
"""

import sys, traceback

from constants.local_constants  import SPACE_DELIMITER,PLACEHOLDER_TEXT,USECASE_ALREADY_EXISTS,USECASE_NOT_FOUND_ERROR,USECASE_NAME_VALIDATION_ERROR

from aicloudlibs.constants import constants as global_constants
from abc import ABC


class modeldeploymentException(Exception, ABC):
    """
    description: Abstract base class of UsecaseException.
    """

    def __init__(self, detail: str) -> None:
        self.status_code = global_constants.HTTP_STATUS_BAD_REQUEST
        super().__init__(detail)


class modeldeploymentNotFoundError(modeldeploymentException):
    """
    description: UsecaseNotFoundError thrown by usecase service
                 when the requested usecase details not found for a specific user.
    """
    def __init__(self,name):
        self.status_code = global_constants.HTTP_STATUS_NOT_FOUND
        self.detail =  USECASE_NOT_FOUND_ERROR.replace(PLACEHOLDER_TEXT,name)

class modeldeploymentNameNotEmptyError(modeldeploymentException):
    """
    description: UsecaseNameNotEmptyError thrown by create usecase service
                 when the requested usecase details not having usecase name.
    """
    def __init__(self,name):
        self.status_code = global_constants.HTTP_STATUS_409_CODE
        self.detail =  USECASE_NAME_VALIDATION_ERROR
