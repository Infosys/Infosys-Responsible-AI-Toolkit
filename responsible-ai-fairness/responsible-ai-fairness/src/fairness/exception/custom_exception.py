"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response
from traceback import print_exception
from fairness.Telemetry.Telemetry_call import SERVICE_Internal_METADATA
import requests
import logging
from fairness.config.logger import CustomLogger
log = CustomLogger()
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
fairnesstelemetryurl = os.getenv("FAIRNESS_TELEMETRY_URL")
telemetry_flag = os.getenv("tel_Falg")

class CustomHTTPException(Exception):
    def __init__(self, error_dict : dict, name: str, msg: str):
        self.error_dict = error_dict
        self.error_dict["errorMessage"] = name
        self.msg = msg
        super().__init__(self.error_dict, self.msg)

async def http_exception_handler(request: Request, exc: CustomHTTPException,):
    error_dict = exc.error_dict
    error = error_dict["errorMessage"]
    if(telemetry_flag == 'True'):
        log.info("inside telemetry_flag")
        response = requests.post(fairnesstelemetryurl, json=error_dict)
        response_data = response.json()
        log.info(f"{response_data}response_data")
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
        if(telemetry_flag == 'True'):
            log.info("inside telemetry_flag")
            response = requests.post(fairnesstelemetryurl, json=SERVICE_Internal_METADATA)
            log.info(f"{response}response")
            response_data = response.json()
            log.info(f"{response_data}response_data")
        return JSONResponse("Internal server error occured", status_code=500)
    

class RegisterExceptions():
    def __init__(self, app):
        self.app = app

    def register_exception_handlers(self):
        self.app.add_exception_handler(CustomHTTPException, http_exception_handler ) 
        self.app.middleware('http')(catch_exceptions_middleware)
        return self.app       


   