'''
License textMIT Licensehttps://mit-license.org/Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

from io import BytesIO
from tempfile import NamedTemporaryFile
import threading
import time
import uuid
import json
import requests
from privacy.util.code_detect.ner.pii_inference.netcustom import code_detect_ner
from privacy.util.code_detect.ner.CodePIINER import CodeNer
from fastapi import Depends, Query,Request,APIRouter, HTTPException, Response, WebSocket,websockets,FastAPI,Cookie,Body
from typing import List, Union
from typing import Optional
from privacy.service.privacytelemetryservice import PrivacyTelemetryRequest
from privacy.service.Video_service import VideoService
from privacy.service.csv_service import CSVService
from privacy.service.json_service import JSONService
from fastapi.params import Form
from privacy.mappers.mappers import (
    PIIAnalyzeRequest,
    PIIAnalyzeResponse,
    PIIAnonymizeRequest,
    PIIAnonymizeResponse,
    PIIEncryptResponse,
    PIIDecryptRequest,
    PIIDecryptResponse,
    PIIImageAnalyzeResponse
)

from privacy.service.Video_service import VideoService
from privacy.service.code_detect_service import CodeDetect
from privacy.service.excel_service import Excel

from privacy.exception.exception import PrivacyException
from privacy.config.logger import CustomLogger

from fastapi import FastAPI, UploadFile,File
from fastapi.responses import FileResponse
from datetime import date
import concurrent.futures
from fastapi import Request
from fastapi.responses import StreamingResponse
from privacy.util.code_detect.ner.pii_inference.netcustom import code_detect_ner
import logging
from privacy.service.api_req import ApiCall, admin_par, error_dict
from privacy.service.__init__ import AttributeDict,registry
from privacy.service.textPrivacy import TextPrivacy,Shield
from privacy.service.imagePrivacy import ImagePrivacy
from privacy.service.dicomPrivacy import DICOMPrivacy
from privacy.service.loadRecognizer import LoadRecognizer

import cv2
import numpy as np
from PIL import Image
router = APIRouter()
log=CustomLogger()
app = FastAPI()


fileRouter=APIRouter()


import tracemalloc
from transformers import AutoModelForTokenClassification, AutoTokenizer
today = date.today()
from datetime import datetime
import asyncio
from dotenv import load_dotenv
load_dotenv()
from privacy.models import (AddRecognizerRequest)

import os
from uuid import UUID, uuid4
from privacy.config.logger import request_id_var
import traceback
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from privacy.util.auth.auth_client_id import get_auth_client_id
from privacy.util.auth.auth_jwt import get_auth_jwt
from privacy.util.auth.auth_none import get_auth_none
RECOG_JSON_PATH = "recogList.json"


now = datetime.now()

magMap = {"True": True, "False": False,"true": True, "false": False}
tel_Falg=os.getenv("TELE_FLAG")
tel_Falg=magMap[tel_Falg]
privacytelemetryurl = os.getenv("PRIVACY_TELEMETRY_URL")
privacyerrorteleurl = os.getenv("PRIVACY_ERROR_URL")


 
# Load the model and tokenizer for CODEFILE API
local_model_directory = "privacy/util/code_detect/ner/pii_inference/nermodel"
model = AutoModelForTokenClassification.from_pretrained(local_model_directory)
tokenizer = AutoTokenizer.from_pretrained(local_model_directory, model_max_length=10000)
TELEMETRY_LOG_PREFIX = "teleReq="
ADMIN_ERROR_MESSAGE = "Please check with administration!!"
ADMIN_ERROR_HEADER = {"X-Error": ADMIN_ERROR_MESSAGE}
VERIFY_SSL_ENV = "VERIFY_SSL"
VERIFY_SSL_DEFAULT = "None"
ENTERED_ANALYZE_METHOD="Entered into analyze routing method"
REQUEST_PAYLOAD_LOG = "request payload: "
TOTAL_TIME_LOG = "Total Time taken "
TELEMETRY_FLAG_LOG = "TelFlag==="
TELEMETRY_COMPLETED_LOG = "******TELEMETRY REQUEST COMPLETED********"
LINE_NO_PREFIX = "Line No:"
PORTFOLIO_ACCOUNT_INCORRECT = "Portfolio/Account Is Incorrect"
ERROR_HEADER_MESSAGE = "There goes my error"
NO_ADMIN_CONNECTION = " Accounts and Portfolio not available with the Subscription!!"
ADMIN_CONNECTION_ERROR = "Admin Connection is not established,"
NO_MATCHING_RECOGNIZERS = " No matching recognizers were found to serve the request."
CHECK_RECOGNIZER = "Check Recognizer"
sslv = {"True": True, "False": False, "true": True, "false": False, "None": False}
INSIDE_TELEMETRY_FLAG = "Inside Telemetry Flag"
EXIT_ENCRYPT_METHOD = "exit create from encrypt routing method"
EXIT_IMAGE_ANALYZE_METHOD = "exit create from image_analyze routing method"
EXIT_IMAGE_ANONYMIZE_METHOD = "exit create from image_anonymize routing method"
EXCEPTION_ENCRYPT = "Exception for encrypt"
DEFAULT_NLP_EXAMPLE = "basic/good/roberta/ranha" 
DIFF_PRIVACY_ANONYMIZE_ENDPOINT = "/privacy/DifferentialPrivacy/anonymize" 
EXIT_USECASE_METHOD = "exit create usecase routing method"

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'tif', 'pdf'}
MAX_FILE_SIZE = 500 * 1024 * 1024


class NoAccountException(Exception):
    pass

class NoAdminConnException(Exception):
    pass

class NoMatchingRecognizer(Exception):
    pass



## FUNCTION FOR FAIL_SAFE TELEMETRY
def send_telemetry_request(privacy_telemetry_request):
    request_id = uuid.uuid4().hex
    request_id_var.set("telemetry")

    try:

        log.debug(TELEMETRY_LOG_PREFIX + json.dumps(privacy_telemetry_request, indent=4))
        
        response = requests.post(privacytelemetryurl, json=privacy_telemetry_request,verify=sslv[os.getenv(VERIFY_SSL_ENV, VERIFY_SSL_DEFAULT)])
 
        response.raise_for_status()
        log.debug("tele data response: "+ str(response))
 
    except Exception as e:
        log.error(str(e))
        raise HTTPException(
            status_code=500,    
            detail=ADMIN_ERROR_MESSAGE,
            headers=ADMIN_ERROR_HEADER)
        
        
class Telemetry:
    @staticmethod
    def error_telemetry_request(errobj,id):
        request_id_var.set(id)

        try:

            log.debug(TELEMETRY_LOG_PREFIX + str(errobj))
            log.debug(TELEMETRY_LOG_PREFIX + str(errobj['error']))  # Convert list to string before concatenating
            error_request = errobj['error'][0]
 
            if(tel_Falg):
                response = requests.post(privacyerrorteleurl, json=error_request,verify=sslv[os.getenv(VERIFY_SSL_ENV, VERIFY_SSL_DEFAULT)])

                response.raise_for_status()
                log.debug("tele error response: "+ str(response))
 
        except Exception as e:
            log.error(str(e))
            raise HTTPException(
                status_code=500,    
                detail=ADMIN_ERROR_MESSAGE,
                headers=ADMIN_ERROR_HEADER)
        


# Authentication 

auth_type = os.environ.get("AUTH_TYPE")

if auth_type == "azure":
    auth = get_auth_client_id()
elif auth_type == "jwt":
    auth = get_auth_jwt()

elif auth_type == 'none':
    auth = get_auth_none()
else:
    raise HTTPException(status_code=500, detail="Invalid authentication type configured")
    

router = APIRouter()


@router.post('/privacy/loadRecognizer')
def load_recognizer_post(payload:UploadFile = File(...)):
    
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    log.info(ENTERED_ANALYZE_METHOD)

    try:
        log.debug(REQUEST_PAYLOAD_LOG+ str(payload))
        payload = {"file":payload}
        response = LoadRecognizer.set_recognizer(payload)
        return response
    except Exception as e:
        log.error(str(e))
        raise HTTPException(
            status_code=500,
            detail=ADMIN_ERROR_MESSAGE,
            headers=ADMIN_ERROR_HEADER)

@router.get('/privacy/getRecognizer')
def load_recognizer_get():
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    try:
        response = LoadRecognizer.load_recognizer()
        return response
    except Exception as e:
        log.error(str(e))
        raise HTTPException(
            status_code=500,
            detail=ADMIN_ERROR_MESSAGE,
            headers=ADMIN_ERROR_HEADER)
def _validate_response(response):
    """Helper function to validate API response and raise appropriate exceptions."""
    if response == 482:
        raise NoMatchingRecognizer
    if response is None:
        raise NoAccountException
    if response == 404:
        raise NoAdminConnException
def _send_analyze_telemetry(request_id, payload, response):
    """Helper function to send telemetry for analyze endpoint."""
    if not tel_Falg:
        return
        
    response_list = list(map(lambda obj: obj.__dict__, response.PIIEntities))
    request_list = payload.__dict__
    request_obj = {
        "portfolio_name": payload.portfolio if payload.portfolio is not None else "None",
        "account_name": payload.account if payload.account is not None else "None",
        "input_text": request_list["input_text"],
        "exclusion_list": request_list["exclusion_list"].split(',') if request_list["exclusion_list"] is not None else [],
    }
    
    telemetry_payload = {
        "uniqueid": request_id,
        "tenant": "privacy",
        "apiname": "analyze",
        "user": payload.user if payload.user is not None else "None",
        "date": now.isoformat(),
        "lotNumber": payload.lotNumber if payload.lotNumber is not None else "None",
        "request": request_obj,
         "response": response_list
    } 
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(send_telemetry_request, telemetry_payload)
    log.info(TELEMETRY_COMPLETED_LOG)
def _handle_privacy_exception(cie, request_id):
    """Helper function to handle PrivacyException."""
    log.debug("Exception for analyze")
    log.error(cie.__dict__)
    er = [{"tenetName": "Privacy", "errorCode": "textAnalyzeRouter", "errorMessage": str(cie) + LINE_NO_PREFIX + str(cie.__traceback__.tb_lineno), "apiEndPoint": "/privacy/text/analyze", "errorRequestMethod": "POST"}]
    er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
    logobj = {"uniqueid": request_id, "error": er}
    
    if len(er) != 0:
        thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj, request_id))
        thread.start()
        if request_id_var.get() in error_dict:
            del error_dict[request_id]
    
    log.error(cie, exc_info=True)
    log.info("exit create from analyze routing method")
    raise HTTPException(**cie.__dict__)

def _handle_generic_exception(e, request_id):
    """Helper function to handle generic exceptions."""
    log.error(str(e))
    er = [{"tenetName": "Privacy", "errorCode": "textAnalyzeRouter", "errorMessage": str(e) + LINE_NO_PREFIX + str(e.__traceback__.tb_lineno), "apiEndPoint": "/privacy/text/analyze", "errorRequestMethod": "POST"}]
    er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
    logobj = {"uniqueid": request_id, "error": er}
    
    if len(er) != 0:
        thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj, request_id))
        thread.start()
        if request_id_var.get() in error_dict:
            del error_dict[request_id]
    
    raise HTTPException(
        status_code=500,
        detail=ADMIN_ERROR_MESSAGE,
        headers=ADMIN_ERROR_HEADER)

@router.post('/privacy/text/analyze', response_model= PIIAnalyzeResponse)
def analyze(payload: PIIAnalyzeRequest,auth= Depends(auth)):

    
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    log.info("Entered into analyze routing method" )

    try:
        log.debug(REQUEST_PAYLOAD_LOG+ str(payload))
        if payload.input_text:
            payload.input_text = payload.input_text.lower()
            log.debug("Converted input_text to lowercase: " + payload.input_text)

        start_time = time.time()
        log.debug("Entered into analyze function")
        tracemalloc.start()
        response = TextPrivacy.analyze(payload)
        ApiCall.del_admin_list()
        tracemalloc.stop()
        log.debug("Returned from analyze function")
        end_time = time.time()
        total_time = end_time - start_time
        log.info(TOTAL_TIME_LOG+str(total_time))
        _validate_response(response)
        
    
        log.debug("response : "+ str(response))
        log.info("exit create from analyze routing method")
        log.debug(TELEMETRY_FLAG_LOG+ str(tel_Falg))
        _send_analyze_telemetry(request_id, payload, response)
        
        return response
    except PrivacyException as cie:
        _handle_privacy_exception(cie, request_id)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail=PORTFOLIO_ACCOUNT_INCORRECT,
            headers={"X-Error": ERROR_HEADER_MESSAGE},
        )
    except NoAdminConnException:
        raise HTTPException(
            status_code=435,
            detail=NO_ADMIN_CONNECTION,
            headers={"X-Error": ADMIN_CONNECTION_ERROR},
        )
    except NoMatchingRecognizer:
        raise HTTPException(
            status_code=482,
            detail=NO_MATCHING_RECOGNIZERS,
            headers={"X-Error": CHECK_RECOGNIZER},
        )
    except Exception as e:
        _handle_generic_exception(e, request_id)
    
@router.post('/privacy/text/anonymize', response_model= PIIAnonymizeResponse)
def anonymize(payload: PIIAnonymizeRequest,auth= Depends(auth)):
    
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    
    log.info("Entered create into anonymize routing method")
    try:
        log.debug(REQUEST_PAYLOAD_LOG+ str(payload))
        if payload.input_text:
            payload.input_text = payload.input_text.lower()
            log.debug("Converted input_text to lowercase: " + payload.input_text)
        start_time = time.time()
        log.debug("Entered into anonymize function")
        response = TextPrivacy.anonymize(payload)
 
        ApiCall.del_admin_list()
        log.debug("Returned from anonymize function")
        end_time = time.time()
        total_time = end_time - start_time
        log.info(TOTAL_TIME_LOG+str(total_time))
        if(response==482):
            raise NoMatchingRecognizer
        if(response==None):
            raise NoAccountException
        if(response==404):
            raise NoAdminConnException
        log.debug("response : "+ str(response))
        log.info("exit create from anonymize routing method")
        if(tel_Falg == True):
            log.debug(INSIDE_TELEMETRY_FLAG)
            request_list = payload.__dict__
            request_obj = {
               "portfolio_name": payload.portfolio if payload.portfolio is not None else "None",
                "account_name": payload.account if payload.account is not None else "None",
                "input_text": request_list["input_text"],
                "exclusion_list": request_list["exclusion_list"].split(',') if request_list["exclusion_list"] is not None else [],
            }
            response_obj = {
                "type": "None",
                "beginOffset": 0,
                "endOffset": 0,
                "score": 0,
                "responseText": response.anonymizedText
            }
            telemetry_payload = {
                "uniqueid": request_id,
                "tenant": "privacy",
                "apiname": anonymize.__name__,
                "user": payload.user if payload.user is not None else "None",
                "date":now.isoformat(),
                "lotNumber": payload.lotNumber if payload.lotNumber is not None else "None",
                "request": request_obj,
                "response": [response_obj]
            }
           
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, telemetry_payload)
            log.info(TELEMETRY_COMPLETED_LOG)
        return response
    except PrivacyException as cie:
        log.error("Exception for anonymize")
        log.error(cie.__dict__)
        er=[{"tenetName":"Privacy","errorCode":"textAnonimyzeRouter","errorMessage":str(cie)+LINE_NO_PREFIX+str(cie.__traceback__.tb_lineno),"apiEndPoint":"/privacy/text/annonymize", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id] 
        log.error(cie, exc_info=True)
        log.info("exit create from anonymize routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail=PORTFOLIO_ACCOUNT_INCORRECT,
            headers={"X-Error": ERROR_HEADER_MESSAGE},
        )
    except NoAdminConnException:
        raise HTTPException(
            status_code=435,
            detail=NO_ADMIN_CONNECTION,
            headers={"X-Error": ADMIN_CONNECTION_ERROR},
        )
    except NoMatchingRecognizer:
        raise HTTPException(
            status_code=482,
            detail=NO_MATCHING_RECOGNIZERS,
            headers={"X-Error": CHECK_RECOGNIZER},
        )
    except Exception as e:
        log.error(str(e))
        er=[{"tenetName":"Privacy","errorCode":"textAnonimyzeRouter","errorMessage":str(e)+LINE_NO_PREFIX+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/text/annonymize", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id] 
        raise HTTPException(
            status_code=500,
            detail=ADMIN_ERROR_MESSAGE,
            headers=ADMIN_ERROR_HEADER)

@router.post('/privacy/text/encrpyt',response_model=PIIEncryptResponse)
def encrypt(payload: PIIAnonymizeRequest,auth= Depends(auth)):
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)

    log.info("Entered create into encrypt routing method")
    try:
        log.debug(REQUEST_PAYLOAD_LOG+ str(payload))
        if payload.input_text:
            payload.input_text = payload.input_text.lower()
            log.debug("Converted input_text to lowercase: " + payload.input_text)
        start_time = time.time()
        log.debug("Entered into encrypt function")
        response = TextPrivacy.encrypt(payload)
        log.debug("Returned from encrypt function")
        end_time = time.time()
        total_time = end_time - start_time

        log.info(TOTAL_TIME_LOG+str(total_time))

        if(response==None):
            raise NoAccountException
        log.info(EXIT_ENCRYPT_METHOD)
        if(tel_Falg == True):
            log.debug(INSIDE_TELEMETRY_FLAG)
            request_list = payload.__dict__
            request_obj = {
               "portfolio_name": payload.portfolio if payload.portfolio is not None else "None",
                "account_name": payload.account if payload.account is not None else "None",
                "input_text": request_list["input_text"],
                "exclusion_list": request_list["exclusion_list"].split(',') if request_list["exclusion_list"] is not None else [],
            }
            response_obj = {
                "type": "None",
                "beginOffset": 0,
                "endOffset": 0,
                "score": 0,
                "responseText": response.text
            }
            telemetry_payload = {
                "uniqueid": request_id,
                "tenant": "privacy",
                "apiname": anonymize.__name__,
                "user": payload.user if payload.user is not None else "None",
                "date":now.isoformat(),
                "lotNumber": payload.lotNumber if payload.lotNumber is not None else "None",
                "request": request_obj,
                "response": [response_obj]
            }
           
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, telemetry_payload)
            log.info(TELEMETRY_COMPLETED_LOG)
        return response
       
    except PrivacyException as cie:
        log.error(EXCEPTION_ENCRYPT)
        log.error(cie.__dict__)
        er=[{"tenetName":"Privacy","errorCode":"textEncryptRouter","errorMessage":str(cie)+LINE_NO_PREFIX+str(cie.__traceback__.tb_lineno),"apiEndPoint":"/privacy/text/encrpyt", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id] 
        log.error(cie, exc_info=True)
        log.info(EXIT_ENCRYPT_METHOD)
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail=PORTFOLIO_ACCOUNT_INCORRECT,
            headers={"X-Error": ERROR_HEADER_MESSAGE},
        )
    except Exception as e:
        log.error(str(e))
        er=[{"tenetName":"Privacy","errorCode":"textEncryptRouter","errorMessage":str(e)+LINE_NO_PREFIX+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/text/encrpyt", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id] 
        raise HTTPException(
            status_code=500,
            detail=ADMIN_ERROR_MESSAGE,
            headers=ADMIN_ERROR_HEADER)

@router.post('/privacy/text/decrpyt',response_model= PIIDecryptResponse)
def decrypt(payload: PIIDecryptRequest,auth= Depends(auth)):
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    log.info("Entered create into decrypt routing method")
    try:
        log.debug(REQUEST_PAYLOAD_LOG+ str(payload))
        start_time = time.time()
        log.debug("Entered into decrypt function")
        response = TextPrivacy.decryption(payload)
        log.debug("Returned from decrypt function")
        end_time = time.time()
        total_time = end_time - start_time
        log.info(TOTAL_TIME_LOG+str(total_time))
        return response
    except PrivacyException as cie:
        log.error("Exception for decrypt")
        log.error(cie.__dict__)
        er=[{"tenetName":"Privacy","errorCode":"textDecryptRouter","errorMessage":str(cie)+LINE_NO_PREFIX+str(cie.__traceback__.tb_lineno),"apiEndPoint":"/privacy/text/decrpyt", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id] 
        log.error(cie, exc_info=True)
        log.info("exit create from decrypt routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail=PORTFOLIO_ACCOUNT_INCORRECT,
            headers={"X-Error": ERROR_HEADER_MESSAGE},
        )
    except Exception as e:
        log.error(str(e))
        er=[{"tenetName":"Privacy","errorCode":"textDecryptRouter","errorMessage":str(e)+LINE_NO_PREFIX+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/text/decrpyt", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id]
        raise HTTPException(
            status_code=500,
            detail=ADMIN_ERROR_MESSAGE,
            headers=ADMIN_ERROR_HEADER)

@router.post('/privacy/image/analyze', response_model=List[PIIImageAnalyzeResponse])
def image_analyze(
    ocr: str = Query('Tesseract', enum=['Tesseract', "EasyOcr", "ComputerVision"]),
    magnification: str = Form(...),
    rotation_flag: str = Form(...),
    images: List[UploadFile] = File(...),
    nlp: str = Form(default=None, example=DEFAULT_NLP_EXAMPLE),
    portfolio: Optional[str] = Form(None),
    account: Optional[str] = Form(None),
    exclusion_list: Optional[str] = Form(None),
    pii_entities_to_be_redacted: Optional[str] = Form(None),
    score_threshold:Optional[float] = Form(default=float(0.7)),
    auth=Depends(auth)
):
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    log.info("Entered create into image_analyze routing method")
    try:
        payloads = []
        for image in images:
            payload = {
                "easyocr": ocr,
                "mag_ratio": magMap[magnification],
                "rotation_flag": magMap[rotation_flag],
                "image": image,
                "nlp": nlp if nlp != "" else None,
                "portfolio": portfolio if portfolio != "" else None,
                "account": account if account != "" else None,
                "pii_entities_to_be_redacted": pii_entities_to_be_redacted if pii_entities_to_be_redacted != "" else None,
                "exclusion": exclusion_list if exclusion_list != "" else None,
                'score_threshold':score_threshold
            }
            payloads.append(payload)
        
        log.debug("Requested payloads: " + str(payloads))
        start_time = time.time()
        log.debug("Entered into image_analyze function")
        
        responses = []
        for payload in payloads:
            response = ImagePrivacy.image_analyze(payload)
            responses.append(response)
        
        ApiCall.del_admin_list()
        log.debug("Returned from image_analyze function")
        end_time = time.time()
        total_time = end_time - start_time
        log.info(TOTAL_TIME_LOG + str(total_time))

        for response in responses:
            if response == 482:
                raise NoMatchingRecognizer
            if response is None:
                raise NoAccountException
            if response == 404:
                raise NoAdminConnException        
        log.info(EXIT_IMAGE_ANALYZE_METHOD)
        log.debug(TELEMETRY_FLAG_LOG+str(tel_Falg))
        if(tel_Falg == True):
            log.debug(INSIDE_TELEMETRY_FLAG)
            log.info(TELEMETRY_COMPLETED_LOG)
        return responses
        
    except PrivacyException as cie:
        log.error("Exception for image_analyze")
        log.error(cie.__dict__)
        er=[{"tenetName":"Privacy","errorCode":"imageAnalyzeRouter","errorMessage":str(cie)+LINE_NO_PREFIX+str(cie.__traceback__.tb_lineno),"apiEndPoint":"/privacy/image/analyze", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id] 
        log.error(cie, exc_info=True)
        log.info(EXIT_IMAGE_ANALYZE_METHOD)
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail=PORTFOLIO_ACCOUNT_INCORRECT,
            headers={"X-Error": ERROR_HEADER_MESSAGE},
        )
    except NoAdminConnException:
        raise HTTPException(
            status_code=435,
            detail=NO_ADMIN_CONNECTION,
            headers={"X-Error": ADMIN_CONNECTION_ERROR},
        )
    except NoMatchingRecognizer:
        raise HTTPException(
            status_code=482,
            detail=NO_MATCHING_RECOGNIZERS,
            headers={"X-Error": CHECK_RECOGNIZER},
        )
    except Exception as e:
        log.error(str(e))
        er=[{"tenetName":"Privacy","errorCode":"imageAnalyzeRouter","errorMessage":str(e)+LINE_NO_PREFIX+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/image/analyze", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id] 
        raise HTTPException(
            status_code=500,
            detail=ADMIN_ERROR_MESSAGE,
            headers=ADMIN_ERROR_HEADER
        )

@router.post('/privacy/image/anonymize')
def image_anonymize(
    ocr: str = Query('Tesseract', enum=['Tesseract', "EasyOcr", "ComputerVision"]),
    magnification: str = Form(...),
    rotation_flag: str = Form(...),
    images: List[UploadFile] = File(...),
    nlp: str = Form(default=None, example=DEFAULT_NLP_EXAMPLE),
    portfolio: Union[str, None] = Form(None),
    account: Union[str, None] = Form(None),
    exclusion_list : Union[str, None] = Form(None),
    pii_entities_to_be_redacted: Union[str, None] = Form(None),
    score_threshold:Optional[float] = Form(default=float(0.7)),
    auth=Depends(auth)
):
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    log.info("Entered create into image_anonymize routing method")
    try:
        payloads = []
        for image in images:
            payload = {
                "easyocr": ocr,
                "mag_ratio": magMap[magnification],
                "rotation_flag": magMap[rotation_flag],
                "image": image,
                "nlp": nlp if nlp != "" else None,
                "portfolio": portfolio if portfolio != "" else None,
                "account": account if account != "" else None,
                "pii_entities_to_be_redacted": pii_entities_to_be_redacted if pii_entities_to_be_redacted != "" else None,
                "exclusion": exclusion_list if exclusion_list != "" else None,
                "score_threshold":score_threshold
            }
            payloads.append(payload)
        
        log.debug("Payloads: " + str(payloads))
        start_time = time.time()
        log.debug("Entered into image_anonymize function")
        responses = []
        for payload in payloads:
            response = ImagePrivacy.image_anonymize(payload)
            responses.append(response)
        ApiCall.del_admin_list()
        log.debug("Returned from image_anonymize function")
        end_time = time.time()
        total_time = end_time - start_time
        log.info(TOTAL_TIME_LOG + str(total_time))
        for response in responses:
            if response == 482:
                raise NoMatchingRecognizer
            if response is None:
                raise NoAccountException
            if response == 404:
                raise NoAdminConnException
        
        log.info(EXIT_IMAGE_ANONYMIZE_METHOD)
        log.debug(TELEMETRY_FLAG_LOG+str(tel_Falg))
        if(tel_Falg == True):
            log.debug(INSIDE_TELEMETRY_FLAG)
            log.info(TELEMETRY_COMPLETED_LOG)
        return responses
        
    except PrivacyException as cie:
        log.error("Exception for image_anonymize")
        log.error(cie.__dict__)
        er=[{"tenetName":"Privacy","errorCode":"imageAnonimyzeRouter","errorMessage":str(cie)+LINE_NO_PREFIX+str(cie.__traceback__.tb_lineno),"apiEndPoint":"/privacy/image/anonymize", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id] 
        log.error(cie, exc_info=True)
        log.info(EXIT_USECASE_METHOD)
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail=PORTFOLIO_ACCOUNT_INCORRECT,
            headers={"X-Error": ERROR_HEADER_MESSAGE},
        )
    except NoAdminConnException:
        raise HTTPException(
            status_code=435,
            detail=NO_ADMIN_CONNECTION,
            headers={"X-Error": ADMIN_CONNECTION_ERROR},
        )
    except NoMatchingRecognizer:
        raise HTTPException(
            status_code=482,
            detail=NO_MATCHING_RECOGNIZERS,
            headers={"X-Error": CHECK_RECOGNIZER},
        )
    except Exception as e:
        log.error(str(e))
        er=[{"tenetName":"Privacy","errorCode":"imageAnonimyzeRouter","errorMessage":str(e)+LINE_NO_PREFIX+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/image/anonymize", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id] 
        raise HTTPException(
            status_code=500,
            detail=ADMIN_ERROR_MESSAGE,
            headers=ADMIN_ERROR_HEADER
        )

@router.post('/privacy/image/hashify')
def image_hashify(ocr: str = Query('Tesseract', enum=['Tesseract',"EasyOcr","ComputerVision"]),magnification:str=Form(...),rotation_flag:str=Form(...),image: List[UploadFile] = File(...),nlp:str=Form(default=None,example=DEFAULT_NLP_EXAMPLE),pii_entities_to_be_hashified:Union[str|None]=Form(None),portfolio:Optional[str]=Form(None),account:Optional[str]=Form(None),exclusion_list:Optional[str]=Form(None),score_threshold:Optional[float] = Form(default=float(0.7)),auth= Depends(auth)):
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    log.info("Entered create into imageEncryption routing method" )
    try:
        payloads=[]
        for i in image:
            payload={"easyocr":ocr,"mag_ratio":magMap[magnification],"rotation_flag":magMap[rotation_flag],"image":i,"nlp":nlp if nlp!="" else None,"pii_entities_to_be_hashified":pii_entities_to_be_hashified if pii_entities_to_be_hashified !="" else None,"portfolio":portfolio,"account":account,"exclusion":exclusion_list,"score_threshold":score_threshold}
            payloads.append(payload)
        log.debug(REQUEST_PAYLOAD_LOG+str(payload))
        start_time= time.time()
        log.debug("Entered into imageEncryption function")
        responses=[]
        for payload in payloads:
            response = ImagePrivacy.image_encryption(payload)
            responses.append(response)
        ApiCall.del_admin_list()
        log.debug("Returned from imageEncryption function")
        end_time = time.time()
        total_time = end_time - start_time
        log.info(TOTAL_TIME_LOG + str(total_time))
        for response in responses:
            if response is None:
                raise NoAccountException
            if response == 404:
                raise NoAdminConnException        
        log.info(TELEMETRY_FLAG_LOG+str(tel_Falg))
        if(tel_Falg == True):
            log.debug(INSIDE_TELEMETRY_FLAG)
            log.info(TELEMETRY_COMPLETED_LOG)
        return responses
        
    except PrivacyException as cie:
        log.error("Exception for imageEncryption")
        log.error(cie.__dict__)
        er=[{"tenetName":"Privacy","errorCode":"imageVerifyRouter","errorMessage":str(cie)+LINE_NO_PREFIX+str(cie.__traceback__.tb_lineno),"apiEndPoint":"/privacy/image/verify", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id] 
        log.error(cie, exc_info=True)
        log.info(EXIT_USECASE_METHOD)
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail=PORTFOLIO_ACCOUNT_INCORRECT,
            headers={"X-Error": ERROR_HEADER_MESSAGE},
        )
    except NoAdminConnException:
        raise HTTPException(
            status_code=435,
            detail=NO_ADMIN_CONNECTION,
            headers={"X-Error": ADMIN_CONNECTION_ERROR},
        )
    except Exception as e:
        log.error(str(e))
        er=[{"tenetName":"Privacy","errorCode":"imageVerifyRouter","errorMessage":str(e)+LINE_NO_PREFIX+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/image/verify", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id] 
        raise HTTPException(
            status_code=500,
            detail=ADMIN_ERROR_MESSAGE,
            headers=ADMIN_ERROR_HEADER)
     
   
@router.post('/privacy/dicom/anonymize')
def dicom_anonymize(payload: UploadFile = File(...),auth= Depends(auth)):
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    log.info("Entered create into readDicom routing method" )
    try:
        start_time = time.time()
        log.debug("Entered into readDicom function")
        response =DICOMPrivacy.read_dicom(payload)
        log.debug("Returned from readDicom function")
        end_time = time.time()
        total_time = end_time - start_time
        log.info(TOTAL_TIME_LOG + str(total_time))
        if(response==None):
            raise NoAccountException
        if(response==404):
            raise NoAdminConnException  

     
        
        log.info("exit create from readDicom routing method")
        log.debug("tel_Flag==="+str(tel_Falg))
        if(tel_Falg == True):
            log.debug(INSIDE_TELEMETRY_FLAG)
            log.info(TELEMETRY_COMPLETED_LOG)
        return response
        
    except PrivacyException as cie:
        log.error("Exception for readDicom")
        log.error(cie.__dict__)
        er=[{"tenetName":"Privacy","errorCode":"DICOMAnonimyzeRouter","errorMessage":str(cie)+LINE_NO_PREFIX+str(cie.__traceback__.tb_lineno),"apiEndPoint":"/privacy/dicom/anonymize", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id] 
        log.error(cie, exc_info=True)
        log.info("exit create from readDicom routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail=PORTFOLIO_ACCOUNT_INCORRECT,
            headers={"X-Error": ERROR_HEADER_MESSAGE},
        )
    except NoAdminConnException:
        raise HTTPException(
            status_code=435,
            detail=NO_ADMIN_CONNECTION,
            headers={"X-Error": ADMIN_CONNECTION_ERROR},
        )
    except Exception as e:
        log.error(str(e))
        er=[{"tenetName":"Privacy","errorCode":"DICOMAnonimyzeRouter","errorMessage":str(e)+LINE_NO_PREFIX+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/dicom/anonymize", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id] 
        raise HTTPException(
            status_code=500,
            detail=ADMIN_ERROR_MESSAGE,
            headers=ADMIN_ERROR_HEADER)

 
## PAYLOAD CHANGED TO ACCEPT TEXT IN A STRUCTURED FORMAT AND GET RESPONSE FOR THE SAME
from starlette.responses import PlainTextResponse
@router.post('/privacy/code/anonymize',response_class=PlainTextResponse)
async def code_redaction(payload_text: str = Body(..., media_type="text/plain", description="The code to be anonymized"),
                        account_name: str = Query("None", description="account name"),
                        portfolio_name: str = Query("None", description="portfolio name"),
                         portauth= Depends(auth)):
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    log.info("Entered create into textner routing method")
    try:
        log.debug("payload==" + str(payload_text))
        
        start_time = time.time()
        log.debug("Entered into textner function")
        response = CodeNer.code_text(payload_text,model, tokenizer)
        log.debug("Returned from textner function")

        end_time = time.time()
        total_time = end_time - start_time
        log.info(TOTAL_TIME_LOG + str(total_time))
        log.debug("response" + str(response))
        
        if response is None:
            raise NoAccountException
        
        log.info("exit create from textner routing method")
        log.debug(TELEMETRY_FLAG_LOG + str(tel_Falg))
        if(tel_Falg == True):
            telemetry_payload = {
                "uniqueid": request_id,
                "tenant": "privacy",
                "apiname": "CodeText Annonymize",           
                "user": "None",
                "date":now.isoformat(),
                "lotNumber": "None",
                "request": {
                "portfolio_name": portfolio_name,
                "account_name": account_name,
                "exclusion_list": [
                  "None"
                ],
                "input_text": payload_text
              },
                "response": [
                {
                  "type": "None",
                  "beginOffset": 0,
                  "endOffset": 0,
                  "score": 0,
                  "responseText": response
                }
              ]
            }
            # Trigger the API call asynchronously using a separate thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, telemetry_payload)
            log.info(TELEMETRY_COMPLETED_LOG)
        # Return the response as plain text, maintaining the format
        return PlainTextResponse(content=response)
    except PrivacyException as cie:
        log.error("Exception for code anonymize")
        log.error(str(cie))
        er=[{"tenetName":"Privacy","errorCode":"CodeAnnonymizeRouter","errorMessage":str(cie)+LINE_NO_PREFIX+str(cie.__traceback__.tb_lineno),"apiEndPoint":"/privacy/code/anonymize", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id]
        raise cie

from io import BytesIO

@router.post('/privacy/codefile/anonymize')
async def code_anonymize(code_file: UploadFile = File(...),
                         account_name: str = Body("None", description="Enter account name"),
                         portfolio_name: str = Body("None", description="Enter portfolio name")):
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    log.info("Entered create into filener routing method")
    try:
        # Read the file content from the UploadFile object
        code_content = await code_file.read()
        # Perform code redaction
        start_time = time.time()
        log.debug("Entered into filener function")
        redacted_content, output_code_file = CodeNer.code_file(code_content, code_file.filename, model, tokenizer)
        log.debug("Returned from filener function")
        if isinstance(redacted_content, str):
            redacted_content = redacted_content.encode('utf-8')

        end_time = time.time()
        total_time = end_time - start_time
        log.info(TOTAL_TIME_LOG + str(total_time))
        headers = {
            "Content-Disposition": f"attachment; filename={output_code_file}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }

        # Delete the uploaded file
        await code_file.close()
        output_code_file = os.path.splitext(code_file.filename)[0] + "_redacted" + os.path.splitext(code_file.filename)[1]
        os.remove(output_code_file)
        log.debug(TELEMETRY_FLAG_LOG + str(tel_Falg))
        if tel_Falg:
            telemetry_payload = {
                "uniqueid": request_id,
                "tenant": "privacy",
                "apiname": "CodeFile Annonymize",
                "user": "None",
                "date": datetime.now().isoformat(),
                "lotNumber": "None",
                "request": {
                    "portfolio_name": portfolio_name,
                    "account_name": account_name,
                    "exclusion_list": ["None"],
                    "input_text": code_content.decode('utf-8') if isinstance(code_content, bytes) else code_content
                },
                "response": [{
                    "type": "None",
                    "beginOffset": 0,
                    "endOffset": 0,
                    "score": 0,
                    "responseText": redacted_content.decode('utf-8') if isinstance(redacted_content, bytes) else redacted_content
                }]
            }
            # Convert telemetry_payload to JSON and print it
            log.debug("telemetry_payload=" + json.dumps(telemetry_payload, indent=4))

            # Trigger the API call asynchronously using a separate thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, telemetry_payload)
            log.info(TELEMETRY_COMPLETED_LOG)

        # Return the redacted code content as a response with the correct filename
        return StreamingResponse(BytesIO(redacted_content), media_type="application/octet-stream", headers=headers)
    except PrivacyException as cie:
        log.error("Exception for filener")
        log.error(cie, exc_info=True)
        er = [{"tenetName": "Privacy", "errorCode": "codeFileAnonimyzeRouter", "errorMessage": str(cie) + LINE_NO_PREFIX + str(cie.__traceback__.tb_lineno), "apiEndPoint": "/privacy/codefile/anonymize", "errorRequestMethod": "POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid": request_id, "error": er}

        if len(er) != 0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj, request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id]
        raise cie
    except Exception as e:
        log.error(str(e))
        er = [{"tenetName": "Privacy", "errorCode": "codeFileAnonimyzeRouter", "errorMessage": str(e) + LINE_NO_PREFIX + str(e.__traceback__.tb_lineno), "apiEndPoint": "/privacy/codefile/anonymize", "errorRequestMethod": "POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid": request_id, "error": er}

        if len(er) != 0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj, request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id]
        raise HTTPException(
            status_code=500,
            detail=ADMIN_ERROR_MESSAGE,
            headers=ADMIN_ERROR_HEADER
        )

from privacy.service.diffrentialPrivacy import DiffPrivacy
@router.post('/privacy/DifferentialPrivacy/file')
def diff_privacy_file(dataset: UploadFile = File(...),auth= Depends(auth)):
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    log.info("Entered create into uploadFIle routing method" )
    try:
        # payload={"excel":excel}
        start_time = time.time()
        log.debug("Entered into upload_file function")
        response = DiffPrivacy.upload_file(dataset)
        log.debug("Returned from upload_file function")
        end_time = time.time()
        total_time = end_time - start_time
        log.info(TOTAL_TIME_LOG + str(total_time))
        if(response==None):
            raise NoAccountException
        
        log.info("exit create from uploadFIle routing method")
        return response
    except PrivacyException as cie:
        log.error("Exception for uploadFIle")
        log.error(cie.__dict__)
        er = [{"tenetName": "Privacy", "errorCode": "diffPrivacyFileRouter", "errorMessage": str(cie) + LINE_NO_PREFIX + str(cie.__traceback__.tb_lineno), "apiEndPoint": "/privacy/DifferentialPrivacy/file", "errorRequestMethod": "POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id] 
        log.error(cie, exc_info=True)
        log.info("exit create from uploadFIle routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail=PORTFOLIO_ACCOUNT_INCORRECT,
            headers={"X-Error": ERROR_HEADER_MESSAGE},
        )
    except Exception as e:
        log.error(str(e))
        er = [{"tenetName": "Privacy", "errorCode": "diffPrivacyFileRouter", "errorMessage": str(e) + LINE_NO_PREFIX + str(e.__traceback__.tb_lineno), "apiEndPoint": "/privacy/DifferentialPrivacy/file", "errorRequestMethod": "POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id] 
        raise HTTPException(
            status_code=500,
            detail=ADMIN_ERROR_MESSAGE,
            headers=ADMIN_ERROR_HEADER)
    
from privacy.service.diffrentialPrivacy import DiffPrivacy
@router.post('/privacy/DifferentialPrivacy/anonymize')
def diff_privacy_anonymize(suppression:Optional[str]=Form(""),noiselist:Optional[str]=Form(""),binarylist:Optional[str]=Form(""),range_list:Optional[str]=Form(""),auth= Depends(auth)):
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    log.info("Entered create into diffPrivacy routing method" )
    try:
        payload={"suppression":suppression,"noiselist":noiselist,"binarylist":binarylist,"range_list":range_list}
        start_time = time.time()
        log.debug("Entered into diff_privacy function")
        response = DiffPrivacy.diff_privacy(payload)
        log.debug("Returned from diffPrivacy function")
        end_time = time.time()
        total_time = end_time - start_time
        log.info(TOTAL_TIME_LOG + str(total_time))
        if(response==None):
            raise NoAccountException
        
        log.info("exit create from diffPrivacy routing method")
        log.debug("res===="+str(response))
        headers = {"Content-Disposition": "attachment; filename=x.csv"}
        return StreamingResponse(response, media_type="text/csv", headers=headers)
    except PrivacyException as cie:
        log.error("Exception for diffPrivacy")
        log.error(cie.__dict__)
        er = [{"tenetName": "Privacy", "errorCode": "diffPrivacyAnonimyzeRouter", "errorMessage": str(cie) + LINE_NO_PREFIX + str(cie.__traceback__.tb_lineno), "apiEndPoint": DIFF_PRIVACY_ANONYMIZE_ENDPOINT, "errorRequestMethod": "POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id] 
        log.error(cie, exc_info=True)
        log.info(EXIT_USECASE_METHOD)
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail=PORTFOLIO_ACCOUNT_INCORRECT,
            headers={"X-Error": ERROR_HEADER_MESSAGE},
        )
    except Exception as e:
        log.error(str(e))
        er = [{"tenetName": "Privacy", "errorCode": "diffPrivacyAnonimyzeRouter", "errorMessage": str(e) + LINE_NO_PREFIX + str(e.__traceback__.tb_lineno), "apiEndPoint": DIFF_PRIVACY_ANONYMIZE_ENDPOINT, "errorRequestMethod": "POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            
            if request_id_var.get() in error_dict:
                del error_dict[request_id] 
        raise HTTPException(
            status_code=500,
            detail=ADMIN_ERROR_MESSAGE,
            headers=ADMIN_ERROR_HEADER
        )
@fileRouter.post('/privacy/loadRecognizer')
def load_recognizer_file_post(payload:UploadFile = File(...)):
    
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    log.info(ENTERED_ANALYZE_METHOD )

    try:
        log.debug(REQUEST_PAYLOAD_LOG+ str(payload))
        payload = {"file":payload}
        response = LoadRecognizer.set_recognizer(payload)
        return response
    except Exception as e:
        log.error(str(e))
        raise HTTPException(
            status_code=500,
            detail=ADMIN_ERROR_MESSAGE,
            headers=ADMIN_ERROR_HEADER
        )

@fileRouter.get('/privacy/getRecognizer')
def load_recognizer_file_get():
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    try:
        response = LoadRecognizer.load_recognizer()
        return response
    except Exception as e:
        log.error(str(e))
        raise HTTPException(
            status_code=500,
            detail=ADMIN_ERROR_MESSAGE,
            headers=ADMIN_ERROR_HEADER
        )

@fileRouter.post('/privacy-files/video/anonymize')
async def video_privacy(ocr: str = Query('Tesseract', enum=['Tesseract',"EasyOcr","ComputerVision"]),magnification:str=Form(...),rotation_flag:str=Form(...),video: UploadFile = File(...),nlp:str=Form(default=None,example=DEFAULT_NLP_EXAMPLE),portfolio:Optional[str]=Form(None),account:Optional[str]=Form(None),exclusion_list:Optional[str]=Form(None),pii_entities_to_be_redacted:Optional[str]=Form(None),score_threshold:Optional[float] = Form(default=float(0.4)),auth= Depends(auth)):
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    log.info("Entered create into image_anonymize routing method" )
    try:
        payload={"easyocr":ocr,"mag_ratio":magMap[magnification],"rotation_flag":magMap[rotation_flag],"video":video,"nlp":nlp if nlp!="" else None,"portfolio":portfolio,"account":account,"exclusion":exclusion_list,"pii_entities_to_be_redacted":pii_entities_to_be_redacted,"score_threshold":score_threshold}
        start_time = time.time()
        video_service = VideoService()
        response = await video_service.video_privacy(payload)
        end_time = time.time()
        total_time = end_time - start_time
        log.info(TOTAL_TIME_LOG + str(total_time))
        if(response==None):
            raise NoAccountException


        log.info(EXIT_IMAGE_ANONYMIZE_METHOD)
        return response
        
    except PrivacyException as cie:
        log.error("Exception for video_privacy")
        log.error(cie.__dict__)
        er = [{"tenetName": "Privacy", "errorCode": "video_privacyRouter", "errorMessage": str(cie) + LINE_NO_PREFIX + str(cie.__traceback__.tb_lineno), "apiEndPoint": "/privacy-files/video/anonymize", "errorRequestMethod": "POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":request_id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,request_id))
            thread.start()
            
            if request_id_var.get() in error_dict:
                del error_dict[request_id]
        log.error(cie, exc_info=True)
        log.info(EXIT_USECASE_METHOD)
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail=PORTFOLIO_ACCOUNT_INCORRECT,
            headers={"X-Error": ERROR_HEADER_MESSAGE},
        )
    except Exception as e:
        log.error(str(e))
        er = [{"tenetName": "Privacy", "errorCode": "video_privacyRouter", "errorMessage": str(e) + LINE_NO_PREFIX + str(e.__traceback__.tb_lineno), "apiEndPoint": "/privacy-files/video/anonymize", "errorRequestMethod": "POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid": request_id, "error": er}
        
        if len(er) != 0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj, request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id]
                
        raise HTTPException(
            status_code=500,
            detail=ADMIN_ERROR_MESSAGE,
            headers=ADMIN_ERROR_HEADER
        )

# from privacy.service.pdf_service import PDFService
# @fileRouter.post('/privacy-files/PDF/anonymize')
# async def PDF(pdf:UploadFile=File(...),nlp:str=Form(default=None,example=DEFAULT_NLP_EXAMPLE),ocr: str = Query('Tesseract', enum=['Tesseract',"EasyOcr","ComputerVision"]),portfolio:Optional[str]=Form(None),account:Optional[str]=Form(None),exclusion_list:Optional[str]=Form(None),pii_entities_to_be_redacted:Optional[str]=Form(None),score_threshold:Optional[float] = Form(default=float(0.4)),auth= Depends(auth)):
#     # payload = {"video": video, "easyocr": ocr}
#     id = uuid.uuid4().hex
#     request_id_var.set(id)
#     log.info("Entered create into image_anonymize routing method" )
#     try:
#         start_time = datetime.now()
#         log.info(f"start_time: {start_time}")
#         log.info("Before invoking create usecase service ")

#         payload={"easyocr":ocr,"mag_ratio":False,"rotation_flag":False,"file": pdf,"nlp":nlp if nlp!="" else None,"portfolio":portfolio,"account":account,"exclusion":exclusion_list,"pii_entities_to_be_redacted":pii_entities_to_be_redacted,"score_threshold":score_threshold}
      
#         log.debug("Request payload: "+ str(payload))
#         response = PDFService.mask_pdf(AttributeDict(payload))
#         if(response==None):
#             raise NoAccountException
#         log.info("After invoking create usecase service ")
#         log.debug("Response : "+ str(response))
#         log.info("Exit create usecase routing method")
#         end_time = datetime.now()
#         log.info(f"end_time: {end_time}")
#         total_time = end_time - start_time
#         log.info(f"total_time: {total_time}")
#         response = Response(content=response.read(), media_type="application/pdf")
#         response.headers["Content-Disposition"] = "attachment; filename="+pdf.filename

#         return response
        
#     except PrivacyException as cie:
#         log.error(EXCEPTION_ENCRYPT)
#         log.error(cie.__dict__)
#         er=[{"UUID":id,"function":"textEncryptRouter","msg":cie.__dict__,"description":cie.__dict__}]
#         er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
#         logobj = {"uniqueid":id,"error":er}
#         # 
#         if len(er)!=0:
#             thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
#             thread.start()
#             if request_id_var.get() in error_dict:
#                 del error_dict[id] 
#         log.error(cie, exc_info=True)
#         log.info("exit create from encrypt routing method")
#         raise HTTPException(**cie.__dict__)
#     except NoAccountException:
#         raise HTTPException(
#             status_code=430,
#             detail=PORTFOLIO_ACCOUNT_INCORRECT,
#             headers={"X-Error": ERROR_HEADER_MESSAGE},
#         )
#     except Exception as e:
#         log.error(str(e))
#         # ExceptionDb.create({"UUID":request_id_var.get(),"function":"textAnonimyzeRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
#         er=[{"UUID":request_id_var.get(),"function":"textAnonimyzeRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)}]
#         er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
#         logobj = {"uniqueid":id,"error":er}
#         if len(er)!=0:
#             thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
#             thread.start()
#             if request_id_var.get() in error_dict:
#                 del error_dict[id] 
#         raise HTTPException(
#             status_code=500,
#             detail="Please check with administration!!",
#             headers={"X-Error": "Please check with administration!!"})   

from privacy.service.ppt_service import PPTService  
@fileRouter.post('/privacy-files/PPT/anonymize')
async def PPT(ppt: UploadFile = File(...),nlp:str=Form(default=None,example=DEFAULT_NLP_EXAMPLE), ocr: str = Query('Tesseract', enum=['Tesseract', "EasyOcr", "ComputerVision"]), portfolio: Optional[str] = Form(None), account: Optional[str] = Form(None), exclusion_list: Optional[str] = Form(None),pii_entities_to_be_redacted:Optional[str]=Form(None), score_threshold:Optional[float] = Form(default=float(0.4)),auth=Depends(auth)):
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    log.info("Entered create into image_anonymize routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("Before invoking create usecase service")

        payload = {"easyocr": ocr, "mag_ratio": False, "rotation_flag": False, "file": ppt,"nlp":nlp if nlp!="" else None, "portfolio": portfolio, "account": account, "exclusion": exclusion_list,"pii_entities_to_be_redacted":pii_entities_to_be_redacted,"score_threshold":score_threshold}

        log.debug(REQUEST_PAYLOAD_LOG + str(payload))
        response = PPTService.mask_ppt(AttributeDict(payload))
        if response is None:
            raise NoAccountException
        log.info("After invoking create usecase service")
        log.debug("Response : " + str(response))
        log.info(EXIT_USECASE_METHOD)
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")
        response = Response(content=response.read(), media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")
        response.headers["Content-Disposition"] = "attachment; filename=" + ppt.filename

        return response

    except PrivacyException as cie:
        log.error(EXCEPTION_ENCRYPT)
        log.error(cie.__dict__)
        er = [{"UUID": request_id, "function": "textEncryptRouter", "msg": cie.__dict__, "description": cie.__dict__}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid": request_id, "error": er}
        if len(er) != 0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj, request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id]
        log.error(cie, exc_info=True)
        log.info(EXIT_ENCRYPT_METHOD)
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail=PORTFOLIO_ACCOUNT_INCORRECT,
            headers={"X-Error": ERROR_HEADER_MESSAGE},
        )
    except Exception as e:
        log.error(str(e))
        er = [{"UUID": request_id_var.get(), "function": "textAnonimyzeRouter", "msg": str(e), "description": str(e) + LINE_NO_PREFIX + str(e.__traceback__.tb_lineno)}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid": request_id, "error": er}
        if len(er) != 0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj, request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id]
        raise HTTPException(
            status_code=500,
            detail=ADMIN_ERROR_MESSAGE,
            headers=ADMIN_ERROR_HEADER
        )

from privacy.service.docs_service import DOCService
@fileRouter.post('/privacy-files/DOCX/anonymize')
async def DOCX(docx: UploadFile = File(...), nlp:str=Form(default=None,example=DEFAULT_NLP_EXAMPLE),ocr: str = Query('Tesseract', enum=['Tesseract', "EasyOcr", "ComputerVision"]), portfolio: Optional[str] = Form(None), account: Optional[str] = Form(None), exclusion_list: Optional[str] = Form(None), pii_entities_to_be_redacted:Optional[str]=Form(None),score_threshold:Optional[float]=Form(default=float(0.4)), auth=Depends(auth)):
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    log.info("Entered create into image_anonymize routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("Before invoking create usecase service")

        payload = {"easyocr": ocr, "mag_ratio": False, "rotation_flag": False, "file": docx,"nlp":nlp if nlp!="" else None, "portfolio": portfolio, "account": account, "exclusion": exclusion_list,"pii_entities_to_be_redacted":pii_entities_to_be_redacted, "score_threshold":score_threshold}

        log.debug(REQUEST_PAYLOAD_LOG + str(payload))
        response = DOCService.mask_doc(AttributeDict(payload))
        if response is None:
            raise NoAccountException
        log.info("After invoking create usecase service")
        log.debug("Response : " + str(response))
        log.info(EXIT_USECASE_METHOD)
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")
        response = Response(content=response.read(), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        response.headers["Content-Disposition"] = "attachment; filename=" + docx.filename

        return response

    except PrivacyException as cie:
        log.error(EXCEPTION_ENCRYPT)
        log.error(cie.__dict__)
        er = [{"UUID": request_id, "function": "textEncryptRouter", "msg": cie.__dict__, "description": cie.__dict__}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid": request_id, "error": er}
        if len(er) != 0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj, request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id]
        log.error(cie, exc_info=True)
        log.info(EXIT_ENCRYPT_METHOD)
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail=PORTFOLIO_ACCOUNT_INCORRECT,
            headers={"X-Error": ERROR_HEADER_MESSAGE},
        )
    except Exception as e:
        log.error(str(e))
        er = [{"UUID": request_id_var.get(), "function": "textAnonimyzeRouter", "msg": str(e), "description": str(e) + LINE_NO_PREFIX + str(e.__traceback__.tb_lineno)}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid": request_id, "error": er}
        if len(er) != 0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj, request_id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[request_id]
        raise HTTPException(
            status_code=500,
            detail=ADMIN_ERROR_MESSAGE,
            headers=ADMIN_ERROR_HEADER
        )

@fileRouter.post('/privacy-files/csv/anonymize')
def csv_anonymize(file: UploadFile = File(...), keys_to_skip: Union[str, None] = Form(None), nlp: str = Form(default=None, example=DEFAULT_NLP_EXAMPLE), ocr: str = Query('Tesseract', enum=['Tesseract', "EasyOcr", "ComputerVision"]), portfolio: Optional[str] = Form(None), account: Optional[str] = Form(None), exclusion_list: Optional[str] = Form(None),pii_entities_to_be_redacted:Optional[str]=Form(None),score_threshold:Optional[float]=Form(default=float(0.4)),fakeData: Optional[bool] = Form(False),auth=Depends(auth)):
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    log.info("Entered csv_anonymize routing method")
    try:
        payload = {
            "file": file,
            "keys_to_skip": keys_to_skip.split(',') if keys_to_skip else None,
            "nlp":nlp if nlp!="" else "basic",
            "portfolio": portfolio, 
            "account": account, 
            "exclusion": exclusion_list,
            "pii_entities_to_be_redacted":pii_entities_to_be_redacted,
            "fakeData": fakeData,
            "score_threshold":score_threshold,

        }
        log.debug("Payload: " + str(payload))
        start_time = time.time()
        output = CSVService.csv_anonymize(payload)
        end_time = time.time()
        total_time = end_time - start_time
        log.info(TOTAL_TIME_LOG + str(total_time))
        log.info("Exiting csv_anonymize routing method")
        return Response(output.getvalue(), media_type='text/csv', headers={'Content-Disposition': 'attachment; filename=anonymized.csv'})
    except Exception as e:
        log.error(str(e))
        raise e



@fileRouter.post('/privacy-files/json/anonymize')
def anonymize_json(file: UploadFile = File(...), keys_to_skip: Union[str, None] = Form(None),  nlp: str = Form(default=None, example=DEFAULT_NLP_EXAMPLE), ocr: str = Query('Tesseract', enum=['Tesseract', "EasyOcr", "ComputerVision"]), portfolio: Optional[str] = Form(None), account: Optional[str] = Form(None), exclusion_list: Optional[str] = Form(None),pii_entities_to_be_redacted:Optional[str]=Form(None),score_threshold:Optional[float]=Form(default=float(0.4)),auth=Depends(auth)):
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    log.info("Entered anonymize_json routing method")
    try:
        payload = {
            "file": file,
            "keys_to_skip": keys_to_skip.split(',') if keys_to_skip else None,
            "nlp": nlp if nlp != "" else "basic",
            "easyocr": ocr,
            "portfolio": portfolio,
            "account": account,
            "exclusion": exclusion_list,
            "pii_entities_to_be_redacted":pii_entities_to_be_redacted,
            "score_threshold":score_threshold,
        }
        log.debug("Payload: " + str(payload))
        start_time = time.time()
        anonymized_json = JSONService.anonymize_json(payload)
        end_time = time.time()
        total_time = end_time - start_time
        log.info(TOTAL_TIME_LOG + str(total_time))
        log.info("Exiting anonymize_json routing method")
        return Response(anonymized_json, media_type='application/json', headers={'Content-Disposition': 'attachment; filename=anonymized.json'})
    except Exception as e:
        log.error(str(e))
        raise e

from privacy.service.files_service import FileService

def get_file_extension(filename: str) -> str:
    return filename.split('.')[-1].lower()

@fileRouter.post('/privacy-files/anonymize')
def anonymize_file(file: UploadFile = File(...), nlp: str = Form(default=None, example=DEFAULT_NLP_EXAMPLE), ocr: str = Query('Tesseract', enum=['Tesseract', "EasyOcr", "ComputerVision"]), portfolio: Optional[str] = Form(None), account: Optional[str] = Form(None), exclusion_list: Optional[str] = Form(None), keys_to_skip: Union[str, None] = Form(None),pii_entities_to_be_redacted:Optional[str]=Form(None), score_threshold:Optional[float]=Form(default=float(0.4)),auth=Depends(auth)):
    request_id = uuid.uuid4().hex
    request_id_var.set(request_id)
    log.info("Entered anonymize_file routing method")
    try:
        file_extension = get_file_extension(file.filename)
        payload = {
            "file": file,
            "nlp": nlp if nlp != "" else "basic",
            "easyocr": ocr,
            "portfolio": portfolio,
            "account": account,
            "mag_ratio": False,
            "rotation_flag":False,
            "exclusion": exclusion_list,
            "pii_entities_to_be_redacted":pii_entities_to_be_redacted,
            "keys_to_skip": keys_to_skip.split(',') if keys_to_skip else None,
            "score_threshold":score_threshold,
        }
        log.debug("Payload: " + str(payload))
        start_time = time.time()
        response_file = FileService.anonymize_file(payload, file_extension)
        end_time = time.time()
        total_time = end_time - start_time
        log.info(TOTAL_TIME_LOG + str(total_time))
        log.info("Exiting anonymize_file routing method")
        
        media_type = 'application/octet-stream'
        if file_extension == 'csv':
            media_type = 'text/csv'
        elif file_extension == 'json':
            media_type = 'application/json'
        # elif file_extension == 'pdf':
        #     media_type = 'application/pdf'
        elif file_extension == 'ppt':
            media_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        elif file_extension == 'docx':
            media_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

        return StreamingResponse(response_file, media_type=media_type, headers={"Content-Disposition": f"attachment; filename=anonymized.{file_extension}"})
    except Exception as e:
        log.error(str(e))
        raise HTTPException(status_code=500, detail="An error occurred during file anonymization.")
@router.post("/privacy/recognizer/add_or_update")
def add_or_update_custom_recognizer(req: AddRecognizerRequest):
    try:
        # Normalize recog_name and supported_entity to uppercase
        recog_name = req.recog_name.strip().upper()
        supported_entity = recog_name

        #  Normalize recog_type to "Pattern" or "Data", case-insensitive
        recog_type_input = req.recog_type.strip().lower()
        if recog_type_input == "pattern":
            recog_type_norm = "Pattern"
        elif recog_type_input == "data":
            recog_type_norm = "Data"
        else:
            raise HTTPException(status_code=400, detail="Invalid recog_type; must be 'Pattern' or 'Data'")

        # Load existing recogList.json
        if os.path.exists(RECOG_JSON_PATH):
            with open(RECOG_JSON_PATH, "r", encoding="utf-8") as f:
                recognizers_data = json.load(f)
        else:
            recognizers_data = []

        # Check if recognizer exists (case-insensitive by original name)
        existing = next((r for r in recognizers_data if r["RecogName"].upper() == recog_name.upper()), None)

        # Normalize entity_values to lowercase
        entity_values_norm = [value.lower() for value in req.entity_values] if req.entity_values else []

        if existing:
            # Update existing recognizer's fields
            existing["supported_entity"] = supported_entity
            existing["RecogType"] = recog_type_norm
            existing["Score"] = req.score

            # Merge context lists without duplicates
            existing_context_set = set(existing.get("Context", []))
            new_context_set = set(req.context or [])
            existing["Context"] = list(existing_context_set.union(new_context_set))

            # Merge EntityValue lists without duplicates
            old_values = set(existing.get("EntityValue", []))
            new_values = set(entity_values_norm)
            existing["EntityValue"] = list(old_values.union(new_values))

            message = f"Recognizer '{recog_name}' updated successfully."
        else:
            new_recog = {
                "RecogName": recog_name,
                "supported_entity": supported_entity,
                "RecogType": recog_type_norm,
                "Score": req.score,
                "Context": req.context,
                "isEditable": "Yes",
                "isPreDefined": "No",
                "isActive": "Y",
                "isCreated": "Not Started",
                "EntityValue": entity_values_norm
            }
            recognizers_data.append(new_recog)
            message = f"Recognizer '{recog_name}' added successfully."

        # Save back to recogList.json
        with open(RECOG_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(recognizers_data, f, indent=4)

        # Register updated/new recognizer immediately
        recog_to_register = existing if existing else new_recog
        payload = {
            "contents_bytes": json.dumps([recog_to_register]).encode("utf-8")
        }
        LoadRecognizer.set_recognizer(payload)

        log.info(message)
        return {
            "message": message,
            "available_recognizers": registry.get_supported_entities()
        }

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error while adding/updating recognizer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))