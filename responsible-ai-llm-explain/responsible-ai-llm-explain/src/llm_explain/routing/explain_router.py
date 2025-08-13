'''
Copyright 2024 Infosys Ltd.

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

from llm_explain.mappers.mappers import UncertainityResponse, UncertainityRequest, \
        TokenImportanceResponse, TokenImportanceRequest, GoTResponse, GoTRequest, \
        SafeSearchResponse, SafeSearchRequest, SentimentAnalysisRequest, SentimentAnalysisResponse, \
        rereadRequest, rereadResponse, openAIRequest, CoTResponse, CoVRequest, CoVResponse, FileUploadRequest, \
        lotRequest, lotResponse
        
from llm_explain.service.service import ExplainService as service
from llm_explain.utility.utility import Utils
from llm_explain.config.logger import CustomLogger, request_id_var
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from datetime import  datetime
import concurrent.futures
import asyncio
import uuid
import os

explanation = APIRouter()
reasoning = APIRouter()

log = CustomLogger()

telemetry_flag = os.getenv("TELEMETRY_FLAG")
tel_error_url = os.getenv("ERROR_LOG_TELEMETRY_URL")

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
            executor.submit(Utils.send_telemetry_request, error_input, tel_error_url)

@explanation.post('/llm-explainability/sentiment-analysis', 
                  response_model = SentimentAnalysisResponse, 
                  summary = "Sentiment analysis of the prompt along with token importance")
def sentiment_analysis(payload: SentimentAnalysisRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("before invoking sentiment_analysis service ")
        response = asyncio.run(service.sentiment_analysis(payload))
        log.info("after invoking sentiment_analysis service ")
        log.info("exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")
        return response
    
    except Exception as cie:
        log.error(cie)
        telemetry_error_logging(cie, request_id_var, "/llm-explainability/sentiment-analysis")
        log.info("exit router sentiment_analysis method")
        raise HTTPException(status_code=500, detail=str(cie))

@explanation.post('/llm-explainability/uncertainty', 
                  response_model = UncertainityResponse, 
                  summary = "Get uncertainty scores for the given input")
def calculate_uncertainty(payload: UncertainityRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("before invoking local_explanation service ")
        response = asyncio.run(service.local_explanation(payload))
        log.info("after invoking local_explanation service ")
        log.info("exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")
        return response
    except Exception as cie:
        log.error(cie)
        telemetry_error_logging(cie, request_id_var, "/llm-explainability/uncertainty")
        log.info("exit router local_explanation method")
        raise HTTPException(status_code=500, detail=str(cie))

@explanation.post('/llm-explainability/token-importance',
                  response_model = TokenImportanceResponse, 
                  summary = "Get importance for each token in the input prompt")
def token_importance(payload: TokenImportanceRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("before invoking token_importance service ")
        response = asyncio.run(service.token_importance(payload))
        log.info("after invoking token_importance service ")
        log.info("exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")
            
        return response
    except Exception as cie:
        log.error(cie)
        telemetry_error_logging(cie, request_id_var, "/llm-explainability/token-importance")
        log.info("exit router token_importance method")
        raise HTTPException(status_code=500, detail=str(cie))
    
@explanation.post('/llm-explainability/serper_response',
                  response_model = SafeSearchResponse,
                  summary = "Verify LLM response with Google Search")
def searchAugmentation(payload: SafeSearchRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("before invoking search_augmentation service ")
        response = asyncio.run(service.search_augmentation(payload))
        log.info("after invoking search_augmentation service ")
        log.info("exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")
            
        return response
    except Exception as cie:
        log.error(cie)
        telemetry_error_logging(cie, request_id_var, "/llm-explainability/serper_response")
        log.info("exit router search_augmentation method")
        raise HTTPException(status_code=500, detail=str(cie))

@reasoning.post('/llm-explainability/got', 
                  response_model = GoTResponse, 
                  summary = "Graph-of-Thoughts Reasoning")
def graph_of_thoughts(payload: GoTRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("before invoking graph_of_thoughts service ")
        response = asyncio.run(service.graph_of_thoughts(payload))
        log.info("after invoking graph_of_thoughts service ")
        log.info("exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")

        return response
    except Exception as cie:
        log.error(cie)
        telemetry_error_logging(cie, request_id_var, "/llm-explainability/got")
        log.info("exit router graph_of_thoughts method")
        raise HTTPException(status_code=500, detail=str(cie))

@reasoning.post('/llm-explainability/reread_reasoning',
                  response_model = rereadResponse,
                  summary = "ReRead Reasoning")
def reread_reasoning(payload: rereadRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("before invoking search_augmentation service ")
        response = asyncio.run(service.reread_reasoning(payload))
        log.info("after invoking search_augmentation service ")
        log.info("exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")  

        return response
    except Exception as cie:
        log.error(cie)
        telemetry_error_logging(cie, request_id_var, "/llm-explainability/reread_reasoning")
        log.info("exit router search_augmentation method")
        raise HTTPException(status_code=500, detail=str(cie))
    
@reasoning.post("/llm-explainability/thot",
                  response_model = rereadResponse,
                  summary="Thread of Thought Reasoning",)
def generate_Thot(payload: openAIRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("before invoking create usecase service ")
        response = asyncio.run(service.thot_reasoning(payload))
        log.info("after invoking thot usecase service ")
        log.info("exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")  
        return response
    except Exception as cie:
        log.error(cie)
        telemetry_error_logging(cie, request_id_var, "/llm-explainability/ThoT")
        log.info("exit router THOT method")
        raise HTTPException(status_code=500, detail=str(cie))
    
@reasoning.post("/llm-explainability/cot",
                  response_model = CoTResponse,
                  summary="Chain of Thought Reasoning",)
def generate_CoT(payload: openAIRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("before invoking create usecase service ")
        response = asyncio.run(service.cot_reasoning(payload))
        log.info("after invoking CoT usecase service ")
        log.info("exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")  
        return response
    except Exception as cie:
        log.error(cie)
        telemetry_error_logging(cie, request_id_var, "/llm-explainability/CoT")
        log.info("exit router CoT method")
        raise HTTPException(status_code=500, detail=str(cie))
    
@reasoning.post("/llm-explainability/cov",
                response_model = CoVResponse,
                summary="Chain of Verification",)
def generate_CoV(payload: CoVRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("before invoking create usecase service ")
        response = asyncio.run(service.cov_reasoning(payload))
        log.info("after invoking CoV usecase service ")
        log.info("exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")  
        return response
    except Exception as cie:
        log.error(cie)
        telemetry_error_logging(cie, request_id_var, "/llm-explainability/CoV")
        log.info("exit router CoV method")
        raise HTTPException(status_code=500, detail=str(cie))

@reasoning.post('/llm-explainability/LoT',
                  response_model = lotResponse,
                  summary = "Logic Of Thought")   
def generate_LoT(payload: lotRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("before invoking LoT service ")
        response = asyncio.run(service.lot_reasoning(payload))
        log.info("after invoking LoT service ")
        log.info("exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")  

        return response
    except Exception as cie:
        log.error(cie)
        telemetry_error_logging(cie, request_id_var, "/llm-explainability/LoT")
        log.info("exit router LoT method")
        raise HTTPException(status_code=500, detail=str(cie))
        
@reasoning.post("/llm-explainability/bulk_processing",
                response_class = StreamingResponse,
                summary="Bulk Processing for reasoning techniques",)
def bulk_processing_explanation(payload: FileUploadRequest,  file: UploadFile = File(...)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("before invoking create usecase service ")
        payload = {"methods": payload.methods, "response_type": payload.responseFileType, "file" : file, "user_id": payload.userId}
        response = asyncio.run(service.bulk_processing_explanation(payload))
        log.info("after invoking excel upload usecase service ")
        log.info("exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")  
       
        return response
    except Exception as cie:
        log.error(cie)
        telemetry_error_logging(cie, request_id_var, "/llm-explainability/bulk_processing")
        log.info("exit router excel upload method")
        raise HTTPException(status_code=500, detail=str(cie))
