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


from fastapi import APIRouter, HTTPException
from explain.mappers.mappers import GetExplanationMethodsRequest, GetExplanationMethodsResponse, \
    GetReportRequest, GetReportResponse,GetExplanationRequest, GetExplanationResponse
from explain.service.service import ExplainService as service
from explain.config.logger import CustomLogger,request_id_var
from explain.dao.explainability.TblException import Tbl_Exception
from datetime import  datetime
import concurrent.futures
import os
import requests
import uuid
import traceback


config = APIRouter()
report = APIRouter()
explanation = APIRouter()

log=CustomLogger()

telemetry_flag = os.getenv("TELEMETRY_FLAG")
tel_error_url = os.getenv("ERROR_LOG_TELEMETRY_URL")

## FUNCTION FOR FAIL_SAFE TELEMETRY
def send_telemetry_request(explainability_telemetry_request, url):
    try:
        response = requests.post(url, json=explainability_telemetry_request)
        response.raise_for_status()
        response_data = response.json()
        log.info(f"Telemetry response: {response_data}")
    except Exception as e:
        log.error(str(e))
        Tbl_Exception.create({"UUID":request_id_var.get(),"function":"send_telemetry_requestFunction","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

def telemetry_error_logging(cie, request_id_var, api_endpoint):
    function_name = None
    # Get the traceback of the exception
    current_tb = cie.__traceback__
    # Traverse to the first traceback not from site-packages
    while current_tb:
        # Check if the traceback is not from site-packages
        if "site-packages" not in current_tb.tb_frame.f_code.co_filename:
            # Get the function name and file name
            function_name = current_tb.tb_frame.f_code.co_name
        # Move to the next traceback
        current_tb = current_tb.tb_next
    
    if telemetry_flag== "True":
        error_input = {
            "tenetName": "Explainability",
            "errorCode": function_name +'_'+ request_id_var.get(),
            "errorMessage": str(cie),
            "apiEndPoint": api_endpoint,
            "errorRequestMethod": "POST"
        }
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(send_telemetry_request, error_input, tel_error_url)
 
@config.post('/explainability/methods/get',
             response_model= GetExplanationMethodsResponse,
             summary="Returns list of explanation methods applicable for the choosen Model and Dataset")
def get_explanation_methods(payload: GetExplanationMethodsRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("Before invoking create usecase service ")
        log.debug("Request payload: "+ str(payload))
        response = service.get_explanation_methods(payload)
        log.info("After invoking create usecase service ")
        log.debug("Response : "+ str(response))
        log.info("Exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")
        return response
    
    except Exception as cie:
        log.error(f"UUID: {request_id_var.get()}, Error: {cie}")
        telemetry_error_logging(cie, request_id_var, "/explainability/methods/get")
        Tbl_Exception.create({"UUID":request_id_var.get(),"function":"get_explanation_methodsFunction","msg":str(cie),"description":traceback.format_exc()})
        log.info("exit create usecase routing method")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(cie)}")

@explanation.post('/explainability/explanation/get',
             response_model= GetExplanationResponse,
             summary="Get explanation for the given model and dataset")
def generate_explanation(payload: GetExplanationRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("Before invoking create usecase service ")
        log.debug("Request payload: "+ str(payload))
        response = service.generate_explanation(payload)
        log.info("After invoking create usecase service ")
        log.debug("Response : "+ str(response))
        log.info("Exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")
        return response
    
    except Exception as cie:
        log.error(f"UUID: {request_id_var.get()}, Error: {cie}")
        telemetry_error_logging(cie, request_id_var, "/explainability/explanation/get")
        Tbl_Exception.create({"UUID":request_id_var.get(),"function":"generate_explanationFunction","msg":str(cie),"description":traceback.format_exc()})
        log.info("Exit create usecase routing method")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(cie)}")
    
@report.post('/explainability/report/generate',
             response_model= GetReportResponse,
             summary="Generate report for the given usecase")
def generate_report(payload: GetReportRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("Before invoking create usecase service ")
        log.debug("Request payload: "+ str(payload))
        response = service.generate_report(payload)
        log.info("After invoking create usecase service ")
        log.debug("Response : "+ str(response))
        log.info("Exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")
        return response
    
    except Exception as cie:
        log.error(f"UUID: {request_id_var.get()}, Error: {cie}")
        telemetry_error_logging(cie, request_id_var, "/explainability/report/generate")
        Tbl_Exception.create({"UUID":request_id_var.get(),"function":"generate_reportFunction","msg":str(cie),"description":traceback.format_exc()})
        log.info("Exit create usecase routing method")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(cie)}")