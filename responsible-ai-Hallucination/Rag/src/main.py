"""
SPDX-License-Identifier: MIT

Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import uvicorn
from RAG.config.logger import CustomLogger
from RAG.config.config import read_config_yaml
from fastapi import Depends, FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from RAG.routing.router import router
from starlette.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

from RAG.exception.global_exception import UnSupportedMediaTypeException
from RAG.exception import global_exception_handler

log=CustomLogger()
#app = FastAPI(openapi_url="/api/v1/RAG/openapi.json", docs_url="/api/v1/RAG/docs")
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
# origins=["http://10.66.155.13:30010/", "http://10.66.155.104:30010/", "https://rai-toolkit-rai.az.ad.idemo-ppc.com/shell", "https://rai-toolkit-test.az.ad.idemo-ppc.com/shell", "https://rai-toolkit-dev.az.ad.idemo-ppc.com/shell", "https://api-aicloud.ad.infosys.com/", "https://infyaiplat.ad.infosys.com/", "https://infyaiplat-tst.ad.infosys.com/", "https://victlpth5-04:8090/"]
origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      
    allow_methods=["GET", "POST", "HEAD"],
    allow_headers=["*"],
)

# class XSSProtectionMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request, call_next):
#         response = await call_next(request)
#         response.headers['X-XSS-Protection'] = '1; mode=block'
#         return response

# app.add_middleware(XSSProtectionMiddleware)

# class CacheControlMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request, call_next):
#         response = await call_next(request)
#         response.headers["Cache-Control"] = "private, no-store"
#         response.headers['Content-Security-Policy'] = "default-src 'self'; img-src data: https:; object-src 'none'; script-src https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js 'self' 'unsafe-inline'; style-src https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css 'self' 'unsafe-inline'; upgrade-insecure-requests;"
#         return response

# app.add_middleware(CacheControlMiddleware)


# @app.get("/nocache")
# def nocache_endpoint():
#     response = JSONResponse(content={"message":"This response not be cached."})
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     response.headers["Pragma"] = "no-cache"
#     response.headers["Expires"] = "0"
#     return response
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

app.include_router(router, prefix='/rag/v1', tags=["Infosys Responsible AI - LLM Moderation"])

if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=9000, ssl_keyfile="./rai.key.pem", ssl_certfile="./rai.crt.pem")
    uvicorn.run(app, host="0.0.0.0", port=8002)#, ssl_ciphers="TLSv2")

