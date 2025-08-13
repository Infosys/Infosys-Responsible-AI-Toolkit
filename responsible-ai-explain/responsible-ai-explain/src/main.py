'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""
app: Project Management service 
fileName: main.py
description: Project management services helps to create Usecase and projects .
             This app handles the services for usecase module which perform CRUD operaions.
"""

from explain.routing.explain_router import report, explanation, config
from explain.config.config import read_config_yaml
from explain.config.logger import CustomLogger
from explain.exception.global_exception import UnSupportedMediaTypeException
from explain.exception import global_exception_handler
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import os
from dotenv import load_dotenv
load_dotenv()

log=CustomLogger()

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv('ALLOWED_ORIGINS'),
    allow_methods=["POST"],
    allow_headers=["*"],
)

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # Adding security headers to the response
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers['Content-Security-Policy'] = "default-src 'self'; img-src data: https:; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Cache-Control'] = 'no-cache; no-store; must-revalidate'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Pragma'] = 'no-cache'
        response.headers['vary'] = 'Origin'
        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        
        # Mask server information
        response.headers['Server'] = 'Hidden'
        
        # Set-Cookie attributes
        response.headers['Set-Cookie'] = 'HttpOnly; Secure; SameSite=Strict'

        # Content-Type handling
        if content_type == 'application/octet-stream':
            response.headers['Content-Type'] = 'application/octet-stream'
            response.headers['Content-Disposition'] = 'attachment; filename=default'
 
        if 'charset=' not in content_type:
            response.headers['Content-Type'] = f"{content_type}; charset=utf-8"
        return response
app.add_middleware(SecurityMiddleware)

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
incude the routing details of service
"""

app.include_router(config,  prefix='/rai/v1', tags=['Configuration Information'])
app.include_router(explanation, prefix='/rai/v1', tags=['Explanation Generation'])
app.include_router(report,  prefix='/rai/v1', tags=['Report Generation'])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
