"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from rai_backend.config.logger import CustomLogger
from rai_backend.config.config import read_config_yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Depends, FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from rai_backend.exception.exception import UnSupportedMediaTypeException
from rai_backend.exception import exception
# from aicloudlibs.utils.global_exception import UnSupportedMediaTypeException
# from aicloudlibs.utils import global_exception_handler
 
# from aicloudlibs.utils.global_exception import UnSupportedMediaTypeException
# from aicloudlibs.utils import global_exception_handler
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
import os

import uvicorn
from rai_backend.router.router import router

log = CustomLogger()

app = FastAPI()

# Read metadata configuration from the config file
metadata_config = read_config_yaml('../config/metadata.yaml')
app = FastAPI(**metadata_config)

allow_origins = os.getenv("allow_origin")
allow_methods = os.getenv("allow_methods")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods = allow_methods,
    allow_headers=["Content-Type", "Authorization", "X-Pingsession"],  # specify allowed headers
    max_age=31536000,
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


# @app.middleware("http")
# async def add_allowed_methods(request: Request, call_next):
#     response = await call_next(request)
#     response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, HEAD, DELETE"
#     return response

class DisallowNullOriginMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.headers.get("Origin") == "null" and request.headers.get("Authorization"):
            return Response(status_code=403, content="Null origin not allowed with credentials")
        return await call_next(request)

app.add_middleware(DisallowNullOriginMiddleware)


class ContentTypeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        response = await call_next(request)
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        
        return response
# app.add_middleware(ContentTypeMiddleware)


class CustomHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response


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
        if not url_path.startswith("/v1/rai/backend"):
            return Response(status_code=404, content="Invalid URL path")
        return await call_next(request)

app.add_middleware(URLPathValidationMiddleware)


class RemoveRememberMeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        if response.status_code == 422:
            response_body = response.json()
            for error in response_body.get("detail", []):
                if error.get("loc") == ["body", "rememberMe"]:
                    error["msg"] = "Invalid input"
                    error.pop("input", None)  
        return response

app.add_middleware(RemoveRememberMeMiddleware)

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
app.include_router(router, prefix='/v1/rai/backend', tags=["RaiBackend"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=30019)
