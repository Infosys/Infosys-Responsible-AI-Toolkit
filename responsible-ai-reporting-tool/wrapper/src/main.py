'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

"""
app: Project Management service 
fileName: main.py
description: Project management services helps to create Usecase and projects .
             This app handles the services for usecase module which perform CRUD operaions.
"""
from typing import List

import uvicorn
import os
from app.config.logger import CustomLogger
from app.config.config import read_config_yaml
from fastapi import Depends, FastAPI,  Request, Response
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.routing.routers import report 
from fastapi.middleware.cors import CORSMiddleware

from app.exception.exception import UnSupportedMediaTypeException
from app.exception import exception

log=CustomLogger()
import yaml
from fastapi import FastAPI

app = FastAPI(
    **read_config_yaml('../config/metadata.yaml'),
    swagger_ui_parameters={
        "swaggerUiJsUrl": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.52.0/swagger-ui-standalone-preset.js",
        "swaggerUiCssUrl": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.52.0/swagger-ui.css",
        "oauth2RedirectUrl": "/docs/oauth2-redirect",
        "head": """
            <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' https://fonts.googleapis.com; img-src 'self' data:; font-src 'self' https://fonts.gstatic.com;">
        """
    }
)
"""
    Adding the CORS Middleware which handles the requests from different origins

    allow_origins - A list of origins that should be permitted to make cross-origin requests.
                    using ['*'] to allow any origin
    allow_methods - A list of HTTP methods that should be allowed for cross-origin requests.
                    using ['*'] to allow all standard method
    allow_headers - A list of HTTP request headers that should be supported for cross-origin requests. 
                    using ['*'] to allow all headers
"""


allow_origins = os.getenv("allow_origin")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST","HEAD","OPTIONS"],  # only allow safe methods
    allow_headers=["Content-Type", "Authorization", "X-Pingsession"],
    max_age=31536000
)

class XSSProtectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

app.add_middleware(XSSProtectionMiddleware)



class ContentTypeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        response = await call_next(request)
        if response.headers.get("Content-Type") == "application/json":
            response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response

app.add_middleware(ContentTypeMiddleware)

# FAST API raise RequestValidationError in case request contains invalid data.
# A global exception handler function to handle the requests which contains the invalid data

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return  exception.validation_error_handler(exc)

# A global exception handler function to handle the unsupported media type exception

@app.exception_handler(UnSupportedMediaTypeException)
async def unsupported_mediatype_error_handler(request: Request, exc: UnSupportedMediaTypeException):
    return  exception.unsupported_mediatype_error_handler(exc)

# A global exception handler function to handle the http exception
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
     return  exception.http_exception_handler(exc)
     
# incude the routing details of service
app.include_router(report,tags=["Report"])

if __name__ == "__main__":
    
    uvicorn.run("main:app", host="0.0.0.0", port=80)