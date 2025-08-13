"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

"""

app: Project Management service 
fileName: main.py
description: Project management services helps to create Usecase and projects .
             This app handles the services for usecase module which perform CRUD operaions.

"""
from typing import List

import os
import uvicorn
from config.logger import CustomLogger
from fastapi import Depends, FastAPI,  Request, Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from routing.router import router
from routing.gcp_router import gcp_router
from routing.aws_router import aws_router
from exception.exception import RegisterExceptions

log=CustomLogger()

allow_methods = os.getenv("allow_methods")
allow_origins = os.getenv("allow_origin")
content_security_policy = os.getenv("content_security_policy")
cache_control = os.getenv("cache_control")
XSS_header = os.getenv("XSS_header")
Vary_header = os.getenv("Vary_header")
Pragma = os.getenv("Pragma")
X_Content_Type_Options = os.getenv("X-Content-Type-Options")
X_Frame_Options = os.getenv("X-Frame-Options")

## initialize the app with openapi and docs url
app = FastAPI(openapi_url="/api/v1/azureBlob/openapi.json", docs_url="/api/v1/azureBlob/docs")

"""

    Adding the CORS Middleware which handles the requests from different origins

    allow_origins - A list of origins that should be permitted to make cross-origin requests.
                    using ['*'] to allow any origin
    allow_methods - A list of HTTP methods that should be allowed for cross-origin requests.
                    using ['*'] to allow all standard method
    allow_headers - A list of HTTP request headers that should be supported for cross-origin requests. 
                    using ['*'] to allow all headers
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_methods=allow_methods,
    allow_headers=["*"],
)

app=RegisterExceptions(app).register_exception_handlers()

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

"""
incude the routing details of service
"""
app.include_router(router, prefix='/api/v1', tags=['Infosys Responsible AI - Azure Blob Storage'])
app.include_router(gcp_router, prefix='/api/v1', tags=['Infosys Responsible AI - GCP Cloud Storage'])
app.include_router(aws_router, prefix='/api/v1', tags=['Infosys Responsible AI - AWS Cloud Storage'])


if __name__ == "__main__":
    print("************************************main start******************************")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    print("************************************** main end ***************************************")



