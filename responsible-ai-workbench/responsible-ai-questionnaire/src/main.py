'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
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
import os
import json
import uvicorn

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from questionnaire.config.logger import CustomLogger
from questionnaire.router.router import router
from questionnaire.exception.exception import UnSupportedMediaTypeException
from questionnaire.exception import exception

# Initialize logger
log = CustomLogger()

# Load and validate environment variables
allow_origins = json.loads(os.getenv("ALLOW_ORIGIN", '["*"]'))
allow_methods = json.loads(os.getenv("ALLOW_METHOD", '["GET", "POST", "OPTIONS", "HEAD"]'))

if not isinstance(allow_origins, list) or not isinstance(allow_methods, list):
    raise ValueError("ALLOW_ORIGIN and ALLOW_METHOD must be JSON arrays.")

# Initialize FastAPI app
app = FastAPI(
    openapi_url="/v1/questionnaire/docs/openapi.json",
    docs_url="/v1/questionnaire/docs",
    title="Infosys Responsible AI - Questionnaire",
    version="1.0.0"
)

# Middleware: CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=allow_methods,
    allow_headers=["Content-Type", "Authorization", "X-Pingsession"],
    expose_headers=["Vary"],
    max_age=31536000
)

# Middleware: Add allowed methods to response headers
@app.middleware("http")
async def add_allowed_methods(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Methods"] = ", ".join(allow_methods)
    return response

# Middleware: Logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    log.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    log.info(f"Response status: {response.status_code}")
    return response

# Middleware: XSS Protection
class XSSProtectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

# Middleware: Disallow null origin with credentials
class DisallowNullOriginMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.headers.get("Origin") == "null" and request.headers.get("Authorization"):
            return Response(status_code=403, content="Null origin not allowed with credentials")
        return await call_next(request)

# Middleware: Enforce JSON content type
class ContentTypeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        response = await call_next(request)
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response

# Middleware: Add security headers
class CustomHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

# Middleware: No cache
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Pragma'] = 'no-cache'
        return response

# Middleware: Secure headers
class SecureHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
        return response

# Register custom middlewares
middlewares = [
    XSSProtectionMiddleware,
    DisallowNullOriginMiddleware,
    ContentTypeMiddleware,
    CustomHeaderMiddleware,
    NoCacheMiddleware,
    SecureHeadersMiddleware
]

for middleware in middlewares:
    app.add_middleware(middleware)

# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return exception.validation_error_handler(exc)

@app.exception_handler(UnSupportedMediaTypeException)
async def unsupported_mediatype_error_handler(request: Request, exc: UnSupportedMediaTypeException):
    return exception.unsupported_mediatype_error_handler(exc)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return exception.http_exception_handler(exc)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

# Startup and shutdown events
@app.on_event("startup")
async def on_startup():
    log.info("Responsible AI Questionnaire service started.")

@app.on_event("shutdown")
async def on_shutdown():
    log.info("Responsible AI Questionnaire service stopped.")

# Include router
app.include_router(router, prefix="/v1", tags=["Questionnaire"])

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=30080)
``
