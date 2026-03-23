"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

"""

app: Project Management service 
fileName: main.py
description: Project management services helps to create Usecase and projects .
             This app handles the services for usecase module which perform CRUD operaions.

"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import uvicorn
import os
from datetime import datetime
from fairness.config.logger import CustomLogger
from fastapi import FastAPI, status
from fairness.routing.fairness_router import llm_router,standalone_apis_router, workbench_router
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fairness.exception.custom_exception import RegisterExceptions
from health.health_check import HealthCheck as Health_Checker
logger=CustomLogger()

allow_methods = os.getenv("allow_methods")
allow_origins = os.getenv("allow_origin")
content_security_policy = os.getenv("content_security_policy")
cache_control = os.getenv("cache_control")
XSS_header = os.getenv("XSS_header")
Vary_header = os.getenv("Vary_header")
Pragma = os.getenv("Pragma")
X_Content_Type_Options = os.getenv("X-Content-Type-Options")
X_Frame_Options = os.getenv("X-Frame-Options")

start_time = datetime.now()

class DependenciesCheck(BaseModel):
    healthy_models: List[str] 
    unhealthy_models: List[str]
    database_health_check: str
    logging_health_check: str 

class HealthCheck(BaseModel):
    dependencies_check: DependenciesCheck
    status: str
    time_taken: str
    timestamp: datetime
    uptime: str

class Liveness(BaseModel):
    "Return a status check for the liveness of fairness service"
    status : str
    uptime : str
    timestamp : datetime

app = FastAPI(
    title='FairnessService',
    openapi_url="/api/v1/fairness/openapi.json", 
    docs_url="/api/v1/fairness/docs",
    redoc_url="/api/v1/fairness/redoc",  
    version='1.0.0'
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
app.add_middleware(
    CORSMiddleware,
    allow_origins= allow_origins,
    allow_methods=allow_methods,
    allow_headers=["*"],
)

app=RegisterExceptions(app).register_exception_handlers()

class XSSProtectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        if "/docs" in str(request.url) or "/openapi.json" in str(request.url):
            response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:; script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net unpkg.com; style-src 'self' 'unsafe-inline' fonts.googleapis.com cdn.jsdelivr.net; font-src 'self' fonts.gstatic.com; img-src 'self' data: validator.swagger.io"
        else:
            csp = content_security_policy or "default-src 'self'"
            response.headers['Content-Security-Policy'] = csp
        
        response.headers['Vary'] = Vary_header or 'Accept-Encoding'
        response.headers['X-XSS-Protection'] = XSS_header or '1; mode=block'
        response.headers['Cache-Control'] = cache_control or 'no-cache, no-store, must-revalidate'
        response.headers["X-Frame-Options"] = X_Frame_Options or 'DENY'
        response.headers["X-Content-Type-Options"] = X_Content_Type_Options or 'nosniff'
        response.headers["Pragma"] = Pragma or 'no-cache'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'        
        content_type = response.headers.get('Content-Type')
        if content_type and 'charset=' not in content_type:
            response.headers['Content-Type'] = f"{content_type}; charset=utf-8"
        return response
app.add_middleware(XSSProtectionMiddleware)


@app.get("/liveness",
         tags = ['Infosys Responsible AI - Fairness Health'],
         summary="Perform a liveness check for the fairness service",
         response_description="Return HTTP status code 200 (OK)",
         status_code=status.HTTP_200_OK,
         response_model=Liveness)
async def root() -> Liveness:
    """Liveness check endpoint"""
    now = datetime.now()
    uptime_seconds = int((now - start_time).total_seconds())
    liveness_ = Liveness(status="ok",
                         uptime=f"{uptime_seconds}s",
                         timestamp=now)
    return liveness_

@app.get("/health",
         tags = ['Infosys Responsible AI - Fairness Health'],
         summary="Perform a health check for fairness service",
         response_description="Return HTTP status code 200 (OK)",
         status_code=status.HTTP_200_OK,
         response_model=HealthCheck)
async def health_check() -> HealthCheck:
    """Health check endpoint"""
    session_start_time = datetime.now()
    hc = Health_Checker()
    azure_openai_health = hc.check_azure_openai()
    # gemini_flash_health = hc.check_gemini_flash()
    # gemini_pro_health = hc.check_gemini_pro()
    database_health = hc.check_database()
    logger_health = hc.check_logger()
    all_healthy = all([azure_openai_health['healthy'], #gemini_flash_health['healthy'], gemini_pro_health['healthy'], 
                       database_health['healthy'], logger_health['healthy']])
    healthy_models = []
    unhealthy_models = []
    
    if azure_openai_health['healthy']:
        healthy_models.append('GPT-4o-mini')
    else:
        unhealthy_models.append('GPT-4o-mini')
        
    # if gemini_flash_health['healthy']:
    #     healthy_models.append("Gemini-2.5-Flash")
    # else:
    #     unhealthy_models.append("Gemini-2.5-Flash")
        
    # if gemini_pro_health['healthy']:
    #     healthy_models.append("Gemini-2.5-Pro")
    # else:
    #     unhealthy_models.append("Gemini-2.5-Pro")
    
    dependency_checks = DependenciesCheck(
        database_health_check=database_health['status'],
        logging_health_check=logger_health['status'],
        healthy_models=healthy_models,
        unhealthy_models=unhealthy_models
    )
    uptime_seconds = int((datetime.now() - start_time).total_seconds())
    healthcheck_ = HealthCheck(
        status="healthy" if all_healthy else "unhealthy",
        uptime=f"{uptime_seconds}s",
        time_taken=f"{int((datetime.now() - session_start_time).total_seconds())}s",
        dependencies_check=dependency_checks,
        timestamp=datetime.now()
    )
    return healthcheck_

"""
incude the routing details of service
"""
app_prefix = '/api/v1'
app.include_router(llm_router, prefix=app_prefix, tags=['Infosys Responsible AI - Fairness Analysis in Text and Images'])
app.include_router(standalone_apis_router, prefix=app_prefix, tags=['Infosys Responsible AI - Analysis and Mitigation for Structured Datasets'])
app.include_router(workbench_router, prefix=app_prefix, tags=['Infosys Responsible AI - Workbench Compatibile Analysis and Mitigation APIs'])


if __name__ == "__main__":
    logger.info("************************************main start******************************")
    uvicorn.run(app, 
                host="0.0.0.0", 
                port=8000)
    logger.info("************************************** main end ***************************************")



