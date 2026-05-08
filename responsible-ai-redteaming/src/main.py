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
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.routing.routers import redteam
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Depends, FastAPI, Request, Response
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from fastapi.responses import JSONResponse
from app.exception.global_exception import UnSupportedMediaTypeException
from app.exception import global_exception_handler
log=CustomLogger()
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_METADATA_PATH = os.path.normpath(os.path.join(_BASE_DIR, '..', 'config', 'metadata.yaml'))
def _load_metadata():
    try:
        raw = read_config_yaml(_METADATA_PATH)
    except FileNotFoundError:
        return {
            'title': 'AI Red Teaming API',
            'version': '0.0.0-test',
            'description': 'Metadata file not found; using fallback. Ensure config/metadata.yaml exists.'
        }
    
    accepted = ['title','summary','description','version','openapi_url','docs_url','terms_of_service','contact','license_info','openapi_tags']
    cleaned = {k: raw[k] for k in accepted if k in raw}
    
    ver = cleaned.get('version')
    if isinstance(ver, str) and '$' in ver:
        cleaned['version'] = ver.replace('$version', '1.0.0')
    return cleaned

app = FastAPI(**_load_metadata())
"""

    Adding the CORS Middleware which handles the requests from different origins

    allow_origins - A list of origins that should be permitted to make cross-origin requests.
                    using ['*'] to allow any origin
    allow_methods - A list of HTTP methods that should be allowed for cross-origin requests.
                    using ['*'] to allow all standard method
    allow_headers - A list of HTTP request headers that should be supported for cross-origin requests. 
                    using ['*'] to allow all headers
"""
raw_allow_origins = os.getenv("allow_origin", "*")
raw_allow_methods = os.getenv("allow_methods", "*")

def _split_csv(val: str):
    if not val:
        return ["*"]
    if val.strip() == "*":
        return ["*"]
    return [v.strip() for v in val.split(',') if v.strip()]

allow_origins = _split_csv(raw_allow_origins)
allow_methods = _split_csv(raw_allow_methods)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods= allow_methods,  
    allow_headers=["Content-Type", "Authorization", "X-Pingsession"],  # specify allowed headers
    max_age=31536000,
    expose_headers=["Vary"]
)

@app.middleware("http")
async def add_allowed_methods(request: Request, call_next):
    response = await call_next(request)
    if allow_methods == ["*"]:
        response.headers["Access-Control-Allow-Methods"] = "*"
    else:
        response.headers["Access-Control-Allow-Methods"] = ", ".join(allow_methods)
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
        if not url_path.startswith("/v1/redteaming"):
            return Response(status_code=404, content="Invalid URL path")
        return await call_next(request)


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        csrf_protect = CsrfProtect()
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            await csrf_protect.validate_csrf(request)
        response = await call_next(request)
       
        try:  
            csrf_protect.set_csrf_cookie(response) 
        except TypeError:
            try:
                csrf_protect.set_csrf_cookie(request, response)  
            except Exception:
                pass 
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
app.include_router(redteam, tags=["AI Red Teaming"])

if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=80)

from uuid import uuid4
import time
from collections import defaultdict


ENABLE_SEC_HEADERS = os.getenv("RAI_ENABLE_SECURITY_HEADERS", "1") == "1"
ENABLE_RATE_LIMIT = os.getenv("RAI_ENABLE_RATE_LIMIT", "0") == "1"
HSTS_ENABLED = os.getenv("RAI_HSTS", "0") == "1"
RATE_LIMIT_PER_MIN = int(os.getenv("RAI_RATE_LIMIT_PER_MINUTE", "60"))  # simple global per-IP+path

if ENABLE_SEC_HEADERS:
    class SecurityHeadersMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
            response = await call_next(request)
           
            response.headers.setdefault('X-Content-Type-Options', 'nosniff')
            response.headers.setdefault('X-Frame-Options', 'DENY')
            response.headers.setdefault('Referrer-Policy', 'no-referrer')
            
            # Allow CDN resources for Swagger UI documentation
            url_path = request.url.path
            if '/docs' in url_path or '/redoc' in url_path or '/openapi.json' in url_path:
                # Relaxed CSP for documentation pages to allow Swagger UI from CDN
                csp = "default-src 'self'; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https://cdn.jsdelivr.net; font-src 'self' https://cdn.jsdelivr.net; object-src 'none'; frame-ancestors 'none'"
            else:
                # Strict CSP for API endpoints
                csp = "default-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'"
            
            if 'Content-Security-Policy' not in response.headers:
                response.headers['Content-Security-Policy'] = csp
            if HSTS_ENABLED:
                response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
            # Permissions-Policy minimal hardening
            response.headers.setdefault('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
            return response
    app.add_middleware(SecurityHeadersMiddleware)


_rate_window: dict = defaultdict(lambda: {'count': 0, 'window_start': 0.0})
WINDOW_SECONDS = 60
if ENABLE_RATE_LIMIT:
    class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
            client_ip = request.client.host if request.client else 'unknown'
            key = f"{client_ip}:{request.url.path}"
            now = time.time()
            entry = _rate_window[key]
            if now - entry['window_start'] >= WINDOW_SECONDS:
                entry['window_start'] = now
                entry['count'] = 0
            entry['count'] += 1
            remaining = max(0, RATE_LIMIT_PER_MIN - entry['count'])
            request.state.rate_limit_remaining = remaining
            if entry['count'] > RATE_LIMIT_PER_MIN:
                response = JSONResponse(status_code=429, content={
                    'detail': 'Rate limit exceeded',
                    'limit_per_minute': RATE_LIMIT_PER_MIN
                })
                response.headers['X-RateLimit-Limit'] = str(RATE_LIMIT_PER_MIN)
                response.headers['X-RateLimit-Remaining'] = '0'
                return response
            response = await call_next(request)
            # Attach standard headers for successful responses
            response.headers.setdefault('X-RateLimit-Limit', str(RATE_LIMIT_PER_MIN))
            response.headers.setdefault('X-RateLimit-Remaining', str(remaining))
            return response
    app.add_middleware(SimpleRateLimitMiddleware)

# Lightweight request ID middleware (placed after rate limit so limit logic unaffected)
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.request_id = str(uuid4())
        response = await call_next(request)
        response.headers.setdefault('X-Request-ID', request.state.request_id)
        return response

app.add_middleware(RequestIDMiddleware)

# Global fallback exception handler (after specific ones). Avoid leaking internals.
from fastapi.responses import JSONResponse
from datetime import datetime, timezone

def _build_envelope(request: Request, data, status_code: int):
    """Internal helper to build an API response envelope when requested.

    Opt-in via X-API-Envelope header with truthy value (1,true,yes,on).
    """
    header_val = request.headers.get('X-API-Envelope', '').lower()
    if header_val not in ("1", "true", "yes", "on"): 
        return data
    meta = {
        'path': request.url.path,
        'status': status_code,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'request_id': getattr(request.state, 'request_id', None)
    }
    if ENABLE_RATE_LIMIT:
        remaining = getattr(request.state, 'rate_limit_remaining', None)
        meta['rate_limit'] = {
            'limit_per_minute': RATE_LIMIT_PER_MIN,
            'remaining': remaining
        }
    return {'meta': meta, 'data': data}

@app.exception_handler(Exception)
async def global_unhandled_exception_handler(request: Request, exc: Exception):
    error_id = str(uuid4())
    log.error(f"Unhandled error {error_id}: {exc}", exc_info=True)
    base_body = {
        'error': 'Internal Server Error',
        'error_id': error_id
    }
    body = _build_envelope(request, base_body, 500)
    if isinstance(body, dict) and 'meta' not in body:
        body['timestamp'] = datetime.now(timezone.utc).isoformat()
    return JSONResponse(status_code=500, content=body)