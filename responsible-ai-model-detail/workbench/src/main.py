'''
MIT license https://opensource.org/licenses/MIT Copyright 2024-2025 Infosys Ltd.

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
import os
from app.config.logger import CustomLogger
from app.config.config import read_config_yaml
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.routing.routers import model,data,tenet,batch,preprocessor
from app.service.utility import Utility
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Depends, FastAPI, Request, Response
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from fastapi.responses import JSONResponse
# from aicloudlibs.utils.global_exception import UnSupportedMediaTypeException
# from aicloudlibs.utils import global_exception_handler
from app.exception.global_exception import UnSupportedMediaTypeException
from app.exception import global_exception_handler

log=CustomLogger()
## initialize the app with openapi and docs url
#app = FastAPI(openapi_url="/api/v1/ai/openapi.json", docs_url="/api/v1/ai/docs")
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
allow_origins = os.getenv("allow_origin")
allow_methods = os.getenv("allow_methods")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods= allow_methods,  # restrict allowed methods
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

class URLPathValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        url_path = request.url.path
        if not url_path.startswith("/v1/workbench"):
            return Response(status_code=404, content="Invalid URL path")
        return await call_next(request)

#app.add_middleware(URLPathValidationMiddleware),

class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        csrf_protect = CsrfProtect()
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            await csrf_protect.validate_csrf(request)
        response = await call_next(request)
        csrf_protect.set_csrf_cookie(response)
        return response

class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Pragma'] = 'no-cache'
        return response

app.add_middleware(NoCacheMiddleware)

"""
FAST API raise RequestValidationError in case request contains invalid data.
A global exception handler function to handle the requests which contains the invalid data

"""
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return  global_exception_handler.validation_error_handler(exc)


"""
A global exception handler function to handle the unsupported media type exception
"""
@app.exception_handler(UnSupportedMediaTypeException)
async def unsupported_mediatype_error_handler(request: Request, exc: UnSupportedMediaTypeException):
    return  global_exception_handler.unsupported_mediatype_error_handler(exc)



"""
A global exception handler function to handle the http exception
"""
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
     return  global_exception_handler.http_exception_handler(exc)

"""
A global exception handler function to handle the CSRF exception
"""

@app.exception_handler(CsrfProtectError)
async def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})



"""
incude the routing details of service
"""
app.include_router(tenet,tags=['Tenets'])
app.include_router(data,tags=["Data"])
app.include_router(model,tags=["Model"])
app.include_router(batch,tags=["Batch"])
app.include_router(preprocessor,tags=["Preprocessor"])
if __name__ == "__main__":
    Utility.loadtenets()
    Utility.loadmodelattributes()
    Utility.loaddataattributes()
    uvicorn.run("main:app", host="0.0.0.0", port=80)


