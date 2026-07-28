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
from profanity.config.logger import CustomLogger
from fastapi import Depends, FastAPI,  Request, Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from profanity.routing.profanity_router import router
from fastapi.middleware.cors import CORSMiddleware

from profanity.exception.exception import UnSupportedMediaTypeException
from profanity.exception import exception
from starlette.middleware.base import BaseHTTPMiddleware


log=CustomLogger()

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all HTTP responses.
    
    This middleware adds essential security headers to protect against
    common web vulnerabilities while being optimized for API usage.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add security headers to all responses
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
## initialize the app with openapi and docs url
app = FastAPI(openapi_url="/api/v1/safety/openapi.json", docs_url="/api/v1/safety/docs")

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
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

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
app.include_router(router, prefix='/api/v1', tags=['Infosys Responsible AI - Profanity'])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)



