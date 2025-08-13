"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

"""
fileName: exception.py
description: handles usecase module specific exception
"""

import sys, traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from constants.local_constants  import SPACE_DELIMITER,PLACEHOLDER_TEXT,USECASE_ALREADY_EXISTS,USECASE_NOT_FOUND_ERROR,USECASE_NAME_VALIDATION_ERROR
from starlette.requests import Request
from abc import ABC
import logging
from config.logger import CustomLogger

log = CustomLogger()
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
HTTP_STATUS_BAD_REQUEST = 500

class CustomHTTPException(Exception):
    def __init__(self, error_dict : dict, name: str, msg: str):
        self.error_dict = error_dict
        self.error_dict["errorMessage"] = name
        self.msg = msg
        super().__init__(self.error_dict, self.msg)

async def http_exception_handler(request: Request, exc: CustomHTTPException,):
    return JSONResponse(
        status_code=500,
        content={"message": f"Oops! {exc.msg}"},
    )

async def catch_exceptions_middleware(request: Request, call_next):
    try:
        log.info("inside catch_exceptions_middleware")
        return await call_next(request)
    except Exception as e:
        # you probably want some kind of logging here
        log.info("inside catch_exceptions_middleware exception")
        logger.exception(e)
        return JSONResponse("Internal server error occured", status_code=500)
    
class AzureBlobException(Exception, ABC):
    """
    dscription: Abstract base class of UsecaseException.
    """

    def __init__(self, detail: str) -> None:
        self.status_code = HTTP_STATUS_BAD_REQUEST
        super().__init__(detail)

class RegisterExceptions():
    def __init__(self, app):
        self.app = app

    def register_exception_handlers(self):
        self.app.add_exception_handler(CustomHTTPException, http_exception_handler ) 
        self.app.middleware('http')(catch_exceptions_middleware)
        return self.app