'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
"""

app: Project Management service 
fileName: main.py
description: Project management services helps to create Usecase and projects .
             This app handles the services for usecase module which perform CRUD operaions.

"""
from typing import List


import uvicorn
from privacy.config.logger import CustomLogger
from privacy.config.config import read_config_yaml
from fastapi import Depends, FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from privacy.routing.privacy_router import router
from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.middleware.cors import CORSMiddleware
# from starlette.middleware import Middleware
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from fastapi.middleware.cors import CORSMiddleware

from privacy.exception.exception import UnSupportedMediaTypeException
from privacy.exception import exception

import os

log=CustomLogger()
cache_control = os.getenv("cache_control")
allow_methods = os.getenv("allow_methods")
allow_origins = os.getenv("allow_origin")
content_security_policy = os.getenv("content_security_policy")
XSS_header = os.getenv("XSS_header")
Vary_header = os.getenv("Vary_header")
Pragma = os.getenv("Pragma")
X_Content_Type_Options = os.getenv("X-Content-Type-Options")
X_Frame_Options = os.getenv("X-Frame-Options")
## initialize the app with openapi and docs url

## reading metadata configuration from config file



app = FastAPI(**read_config_yaml('../config/metadata.yaml'))

"""

    Adding the CORS Middleware which handles the requests from different origins

    allow_origins - A list of origins that should be permitted to make cross-origin requests.
                    using ['*'] to allow any origin
    allow_methods - A list of HTTP methods that should be allowed for cross-origin requests.
                    using ['*'] to allow all standard method
    allow_headers - A list of HTTP request headers that should be supported for cross-origin requests. 
                    using ['*'] to allow all headers
"""

# origins = [
#     'http://10.66.155.13',
#     'http://10.66.155.13:30010',

# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[allow_origins],
    allow_methods=[allow_methods],
    allow_headers=["*"],
)

class XSSProtectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['Vary'] = Vary_header
        response.headers['X-XSS-Protection'] = XSS_header
        response.headers['Cache-Control'] = cache_control
        response.headers['Content-Security-Policy'] = content_security_policy
        response.headers["X-Frame-Options"] = X_Frame_Options  
        response.headers["X-Content-Type-Options"] = X_Content_Type_Options
        response.headers["Pragma"] = Pragma
        # Verify Content-Type header
        content_type = response.headers.get('Content-Type')
        if 'charset=' not in content_type:
            response.headers['Content-Type'] = f"{content_type}; charset=utf-8"
        return response
 
app.add_middleware(XSSProtectionMiddleware)
# app.add_middleware(
#      CORSMiddleware,
#      allow_origins=["*"],
#      allow_credentials=True,
#      allow_methods=["*"],
#      allow_headers=["*"]
#  )

"""
FAST API raise RequestValidationError in case request contains invalid data.
A global exception handler function to handle the requests which contains the invalid data

"""

# @app.options("/{rest_of_path:path}")
# async def preflight_handler(request: Request, rest_of_path: str) -> Response:
#     """
#     Handles OPTIONS requests to /*.
#     """
#     response = Response()
#     response.headers["Access-Control-Allow-Origin"] = "*"
#     response.headers["Access-Control-Allow-Methods"] = "POST, GET, DELETE, PATCH, OPTIONS"
#     response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
#     return response

# @app.middleware("http")
# async def add_cors_header(request , call_next):
#    """
#    Sets CORS headers.
#   """
#   response = await call_next(request)
#   response.headers["Access-Control-Allow-Origin"] = "http://10.66.155.13:30010"
#  response.headers["Access-Control-Allow-Credentials"] = "true"
#   response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
#   response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
#    return response

# origins = [
#   "http://10.66.155.13",
#   "http://10.66.155.13:30010",
# ]

# app.add_middleware(
#    CORSMiddleware,
#    allow_origins=origins,
#    allow_credentials=True,
#   allow_methods=["*"],
#    allow_headers=["*"],
# )





@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return  exception.validation_error_handler(exc)


"""
A global exception handler function to handle the unsupported media type exception
"""
@app.exception_handler(UnSupportedMediaTypeException)
async def unsupported_mediatype_error_handler(request: Request, exc: UnSupportedMediaTypeException):
    return  exception.unsupported_mediatype_error_handler(exc)



"""
A global exception handler function to handle the http exception
"""
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
     return  exception.http_exception_handler(exc)



"""
incude the routing details of service
"""

app.include_router(router, prefix='/v1', tags=["PII Privacy"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=30002)
