'''
Copyright 2024-2025 Infosys Ltd.
 
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
from docProcess.config.logger import CustomLogger
from fastapi import Depends, FastAPI,  Request, Response
from fastapi.exceptions import RequestValidationError 
from starlette.exceptions import HTTPException as StarletteHTTPException
from docProcess.router.router import router
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from docProcess.exception.exception import UnSupportedMediaTypeException
from docProcess.exception import exception
import os



log=CustomLogger()
allow_origins = os.getenv("allow_origin")
allow_methods = os.getenv("allow_method")
## initialize the app with openapi and docs url
app = FastAPI(openapi_url="/api/v1/docProcess/docs/openapi.json", docs_url="/rai/v1/docProcess/docs")

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
    allow_credentials=True,
    allow_headers=["Content-Type", "Authorization", "X-Pingsession"],  # specify allowed headers
    max_age=31536000,  # set max age for CORS cache
    expose_headers=["Vary"]
)
@app.middleware("http")
async def add_allowed_methods(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Methods"] = allow_methods
    return response
class XSSProtectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

app.add_middleware(XSSProtectionMiddleware)

class DisallowNullOriginMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.headers.get("Origin") == "null" and request.headers.get("Authorization"):
            return Response(status_code=403, content="Null origin not allowed with credentials")
        return await call_next(request)

app.add_middleware(DisallowNullOriginMiddleware)

# Middleware to ensure content type is application/json
class ContentTypeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        response = await call_next(request)
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response

# app.add_middleware(ContentTypeMiddleware)

# Additional security headers
class CustomHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

# Assuming `app` is your FastAPI instance
app.add_middleware(CustomHeaderMiddleware)

class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Pragma'] = 'no-cache'
        return response

app.add_middleware(NoCacheMiddleware)

class URLPathValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        url_path = request.url.path
        if not url_path.startswith("rai/v1/docProcess/"):
            return Response(status_code=404, content="Invalid URL path")
        return await call_next(request)

# app.add_middleware(URLPathValidationMiddleware)
"""
FAST API raise RequestValidationError in case request contains invalid data.
A global exception handler function to handle the requests which contains the invalid data

"""
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
app.include_router(router, prefix='/rai/v1', tags=['Infosys Responsible AI - USECASE-docProcess']) 


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0" ,port=30030)