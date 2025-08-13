'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from io import BytesIO
from tempfile import NamedTemporaryFile
import threading
import time
import uuid

import requests
from privacy.util.code_detect.ner.pii_inference.netcustom import code_detect_ner
from privacy.util.code_detect.ner.CodePIINER import codeNer
from fastapi import Depends, Query,Request,APIRouter, HTTPException, Response, WebSocket,websockets,FastAPI,Cookie,Body
from typing import List, Union

from privacy.service.privacytelemetryservice import PrivacyTelemetryRequest
from privacy.service.Video_service import *
from privacy.service.csv_service import *
from privacy.service.json_service import *
from fastapi.params import Form
from privacy.mappers.mappers import *


from privacy.service.Video_service import VideoService
from privacy.service.code_detect_service import *
from privacy.service.excel_service import Excel

from privacy.exception.exception import PrivacyException
from privacy.config.logger import CustomLogger

from fastapi import FastAPI, UploadFile,File
from fastapi.responses import FileResponse
from datetime import date
import concurrent.futures
from fastapi import Request
from fastapi.responses import StreamingResponse
from privacy.util.code_detect.ner.pii_inference.netcustom import *
import logging
from privacy.service.api_req import *
from privacy.service.__init__ import *
from privacy.service.textPrivacy import TextPrivacy,Shield
from privacy.service.imagePrivacy import ImagePrivacy
from privacy.service.dicomPrivacy import DICOMPrivacy
from privacy.service.loadRecognizer import LoadRecognizer
import cv2
import numpy as np
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



class NoAccountException(Exception):
    pass

class NoAdminConnException(Exception):
    pass

class NoMatchingRecognizer(Exception):
    pass



## FUNCTION FOR FAIL_SAFE TELEMETRY
def send_telemetry_request(privacy_telemetry_request):
    id = uuid.uuid4().hex
    request_id_var.set("telemetry")

    try:

        log.debug("teleReq=" + json.dumps(privacy_telemetry_request, indent=4))
        
        response = requests.post(privacytelemetryurl, json=privacy_telemetry_request)
 
        response.raise_for_status()
        response_data = response.json()
        log.debug("tele data response: "+ str(response))
 
    except Exception as e:
        log.error(str(e))
        raise HTTPException(
            status_code=500,    
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
        
        
class Telemetry:
    def error_telemetry_request(errobj,id):
        request_id_var.set(id)

        try:
 
            log.debug("teleReq="+str(errobj))
            log.debug("teleReq="+str(errobj['error']))  # Convert list to string before concatenating
            errorRequest = errobj['error'][0]
 
            if(tel_Falg):
                response = requests.post(privacyerrorteleurl, json=errorRequest)
 
                response.raise_for_status()
                response_data = response.json()
                log.debug("tele error response: "+ str(response))
 
        except Exception as e:
            log.error(str(e))
            raise HTTPException(
                status_code=500,    
                detail="Please check with administration!!",
                headers={"X-Error": "Please check with administration!!"})
        


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
def loadRecognizer(payload:UploadFile = File(...)):
    
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered into analyze routing method" )

    try:
        log.debug("request payload: "+ str(payload))
        payload = {"file":payload}
        response = LoadRecognizer.set_recognizer(payload)
        return response
    except Exception as e:
        log.error(str(e))
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

@router.get('/privacy/getRecognizer')
def loadRecognizer():
    id = uuid.uuid4().hex
    request_id_var.set(id)
    try:
        response = LoadRecognizer.load_recognizer()
        return response
    except Exception as e:
        log.error(str(e))
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

@router.post('/privacy/text/analyze', response_model= PIIAnalyzeResponse)
def analyze(payload: PIIAnalyzeRequest,auth= Depends(auth)):

    
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered into analyze routing method" )

    try:
        log.debug("request payload: "+ str(payload))
        startTime = time.time()
        log.debug("Entered into analyze function")
        tracemalloc.start()
        response = TextPrivacy.analyze(payload)
        ApiCall.delAdminList()
        tracemalloc.stop()
        log.debug("Returned from analyze function")
        endTime = time.time()
        totalTime = endTime - startTime
          
        log.info("Total Time taken "+str(totalTime))
        if(response==482):
            raise NoMatchingRecognizer
        if(response==None):
            raise NoAccountException
 
        if(response==404):
            raise NoAdminConnException
        
    
        log.debug("response : "+ str(response))
        log.info("exit create from analyze routing method")
        log.debug("TelFlag==="+ str(tel_Falg))
        if(tel_Falg == True):
            responseList = list(map(lambda obj: obj.__dict__, response.PIIEntities))
            requestList = payload.__dict__
            requestObj = {
                "portfolio_name": payload.portfolio if payload.portfolio is not None else "None",
                "account_name": payload.account if payload.account is not None else "None",
                "inputText": requestList["inputText"],
                "exclusion_list": requestList["exclusionList"].split(',') if requestList["exclusionList"] is not None else [],
            }
            
            telemetryPayload = {
                "uniqueid": id,
                "tenant": "privacy",
                "apiname": analyze.__name__,           
                "user": payload.user if payload.user is not None else "None",
                "date":now.isoformat(),
                "lotNumber": payload.lotNumber if payload.lotNumber is not None else "None",
                "request": requestObj,
                "response": responseList
            }
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, telemetryPayload)
            log.info("******TELEMETRY REQUEST COMPLETED********")

        
        return response
    except PrivacyException as cie:
        log.debug("Exception for analyze")
        log.error(cie.__dict__)

        er=[{"tenetName":"Privacy","errorCode":"textAnalyzeRouter","errorMessage":str(e)+"Line No:"+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/text/analyze", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 


        log.error(cie, exc_info=True)
        log.info("exit create from analyze routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except NoAdminConnException:
        raise HTTPException(
            status_code=435,
            detail=" Accounts and Portfolio not available with the Subscription!!",
            headers={"X-Error": "Admin Connection is not established,"},
        )
    except NoMatchingRecognizer:
        raise HTTPException(
            status_code=482,
            detail=" No matching recognizers were found to serve the request.",
            headers={"X-Error": "Check Recognizer"},
        )
    except Exception as e:
        log.error(str(e))
 
        er=[{"tenetName":"Privacy","errorCode":"textAnalyzeRouter","errorMessage":str(e)+"Line No:"+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/text/analyze", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
@router.post('/privacy/text/anonymize', response_model= PIIAnonymizeResponse)
def anonymize(payload: PIIAnonymizeRequest,auth= Depends(auth)):
    
    id = uuid.uuid4().hex
    request_id_var.set(id)
    
    log.info("Entered create into anonymize routing method")
    try:
        log.debug("request payload: "+ str(payload))
        startTime = time.time()
        log.debug("Entered into anonymize function")
        response = TextPrivacy.anonymize(payload)
 
        ApiCall.delAdminList()
        log.debug("Returned from anonymize function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        if(response==482):
            raise NoMatchingRecognizer
        if(response==None):
            raise NoAccountException
        if(response==404):
            raise NoAdminConnException
        log.debug("response : "+ str(response))
        log.info("exit create from anonymize routing method")
        if(tel_Falg == True):
            log.debug("Inside Telemetry Flag")
            requestList = payload.__dict__
            requestObj = {
               "portfolio_name": payload.portfolio if payload.portfolio is not None else "None",
                "account_name": payload.account if payload.account is not None else "None",
                "inputText": requestList["inputText"],
                "exclusion_list": requestList["exclusionList"].split(',') if requestList["exclusionList"] is not None else [],
            }
            responseObj = {
                "type": "None",
                "beginOffset": 0,
                "endOffset": 0,
                "score": 0,
                "responseText": response.anonymizedText
            }
            telemetryPayload = {
                "uniqueid": id,
                "tenant": "privacy",
                "apiname": anonymize.__name__,
                "user": payload.user if payload.user is not None else "None",
                "date":now.isoformat(),
                "lotNumber": payload.lotNumber if payload.lotNumber is not None else "None",
                "request": requestObj,
                "response": [responseObj]
            }
           
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, telemetryPayload)
            log.info("******TELEMETRY REQUEST COMPLETED********")
        return response
    except PrivacyException as cie:
        log.error("Exception for anonymize")
        log.error(cie.__dict__)
        er=[{"tenetName":"Privacy","errorCode":"textAnonimyzeRouter","errorMessage":str(e)+"Line No:"+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/text/annonymize", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        log.error(cie, exc_info=True)
        log.info("exit create from anonymize routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except NoAdminConnException:
        raise HTTPException(
            status_code=435,
            detail=" Accounts and Portfolio not available with the Subscription!!",
            headers={"X-Error": "Admin Connection is not established,"},
        )
    except NoMatchingRecognizer:
        raise HTTPException(
            status_code=482,
            detail=" No matching recognizers were found to serve the request.",
            headers={"X-Error": "Check Recognizer"},
        )
    except Exception as e:
        log.error(str(e))
        er=[{"tenetName":"Privacy","errorCode":"textAnonimyzeRouter","errorMessage":str(e)+"Line No:"+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/text/annonymize", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
            
@router.post('/privacy/text/encrpyt',response_model=PIIEncryptResponse)
def encrypt(payload: PIIAnonymizeRequest,auth= Depends(auth)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    
    log.info("Entered create into encrypt routing method")
    try:
        log.debug("request payload: "+ str(payload))
        startTime = time.time()
        log.debug("Entered into encrypt function")
        response = TextPrivacy.encrypt(payload)
        log.debug("Returned from encrypt function")
        endTime = time.time()
        totalTime = endTime - startTime
 
        log.info("Total Time taken "+str(totalTime))
        
        if(response==None):
            raise NoAccountException
        log.info("exit create from encrypt routing method")
        if(tel_Falg == True):
            log.debug("Inside Telemetry Flag")
            requestList = payload.__dict__
            requestObj = {
               "portfolio_name": payload.portfolio if payload.portfolio is not None else "None",
                "account_name": payload.account if payload.account is not None else "None",
                "inputText": requestList["inputText"],
                "exclusion_list": requestList["exclusionList"].split(',') if requestList["exclusionList"] is not None else [],
            }
            responseObj = {
                "type": "None",
                "beginOffset": 0,
                "endOffset": 0,
                "score": 0,
                "responseText": response.text
            }
            telemetryPayload = {
                "uniqueid": id,
                "tenant": "privacy",
                "apiname": anonymize.__name__,
                "user": payload.user if payload.user is not None else "None",
                "date":now.isoformat(),
                "lotNumber": payload.lotNumber if payload.lotNumber is not None else "None",
                "request": requestObj,
                "response": [responseObj]
            }
           
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, telemetryPayload)
            log.info("******TELEMETRY REQUEST COMPLETED********")
        return response
       
    except PrivacyException as cie:
        log.error("Exception for encrypt")
        log.error(cie.__dict__)
        er=[{"tenetName":"Privacy","errorCode":"textEncryptRouter","errorMessage":str(e)+"Line No:"+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/text/encrpyt", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        log.error(cie, exc_info=True)
        log.info("exit create from encrypt routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except Exception as e:
        log.error(str(e))
        er=[{"tenetName":"Privacy","errorCode":"textEncryptRouter","errorMessage":str(e)+"Line No:"+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/text/encrpyt", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
        
@router.post('/privacy/text/decrpyt',response_model= PIIDecryptResponse)  
def decrypt(payload: PIIDecryptRequest,auth= Depends(auth)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into decrypt routing method")
    try:
        log.debug("request payload: "+ str(payload))
        startTime = time.time()
        log.debug("Entered into decrypt function")
        response = TextPrivacy.decryption(payload)
        log.debug("Returned from decrypt function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        return response
    except PrivacyException as cie:
        log.error("Exception for decrypt")
        log.error(cie.__dict__)
        er=[{"tenetName":"Privacy","errorCode":"textDecryptRouter","errorMessage":str(e)+"Line No:"+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/text/decrpyt", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        log.error(cie, exc_info=True)
        log.info("exit create from decrypt routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except Exception as e:
        log.error(str(e))
        er=[{"tenetName":"Privacy","errorCode":"textDecryptRouter","errorMessage":str(e)+"Line No:"+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/text/decrpyt", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id]
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

@router.post('/privacy/image/analyze', response_model=List[PIIImageAnalyzeResponse])
def image_analyze(
    ocr: str = Query('Tesseract', enum=['Tesseract', "EasyOcr", "ComputerVision"]),
    magnification: str = Form(...),
    rotationFlag: str = Form(...),
    images: List[UploadFile] = File(...),
    nlp: str = Form(default=None, example="basic/good/roberta/ranha"),
    portfolio: Optional[str] = Form(None),
    account: Optional[str] = Form(None),
    exclusionList: Optional[str] = Form(None),
    piiEntitiesToBeRedacted: Optional[str] = Form(None),
    auth=Depends(auth)
):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into image_analyze routing method")
    try:
        payloads = []
        for image in images:
            payload = {
                "easyocr": ocr,
                "mag_ratio": magMap[magnification],
                "rotationFlag": magMap[rotationFlag],
                "image": image,
                "nlp": nlp if nlp != "" else None,
                "portfolio": portfolio if portfolio != "" else None,
                "account": account if account != "" else None,
                "piiEntitiesToBeRedacted": piiEntitiesToBeRedacted if piiEntitiesToBeRedacted != "" else None,
                "exclusion": exclusionList if exclusionList != "" else None
            }
            payloads.append(payload)
        
        log.debug("Requested payloads: " + str(payloads))
        startTime = time.time()
        log.debug("Entered into image_analyze function")
        
        responses = []
        for payload in payloads:
            response = ImagePrivacy.image_analyze(payload)
            responses.append(response)
        
        ApiCall.delAdminList()
        log.debug("Returned from image_analyze function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken " + str(totalTime))
        
        for response in responses:
            if response == 482:
                raise NoMatchingRecognizer
            if response is None:
                raise NoAccountException
            if response == 404:
                raise NoAdminConnException        
        log.info("exit create from image_analyze routing method")
        log.debug("tel_Flag==="+str(tel_Falg))
        if(tel_Falg == True):
            log.debug("Inside Telemetry Flag")
            log.info("******TELEMETRY REQUEST COMPLETED********")
        return responses
        
    except PrivacyException as cie:
        log.error("Exception for image_analyze")
        log.error(cie.__dict__)
        er=[{"tenetName":"Privacy","errorCode":"imageAnalyzeRouter","errorMessage":str(e)+"Line No:"+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/image/analyze", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        log.error(cie, exc_info=True)
        log.info("exit create from image_analyze routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except NoAdminConnException:
        raise HTTPException(
            status_code=435,
            detail=" Accounts and Portfolio not available with the Subscription!!",
            headers={"X-Error": "Admin Connection is not established,"},
        )
    except NoMatchingRecognizer:
        raise HTTPException(
            status_code=482,
            detail=" No matching recognizers were found to serve the request.",
            headers={"X-Error": "Check Recognizer"},
        )
    except Exception as e:
        log.error(str(e))
        er=[{"tenetName":"Privacy","errorCode":"imageAnalyzeRouter","errorMessage":str(e)+"Line No:"+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/image/analyze", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

@router.post('/privacy/image/anonymize')
def image_anonymize(
    ocr: str = Query('Tesseract', enum=['Tesseract', "EasyOcr", "ComputerVision"]),
    magnification: str = Form(...),
    rotationFlag: str = Form(...),
    images: List[UploadFile] = File(...),
    nlp: str = Form(default=None, example="basic/good/roberta/ranha"),
    portfolio: Union[str, None] = Form(None),
    account: Union[str, None] = Form(None),
    exclusionList: Union[str, None] = Form(None),
    piiEntitiesToBeRedacted: Union[str, None] = Form(None),
    auth=Depends(auth)
):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into image_anonymize routing method")
    try:
        payloads = []
        for image in images:
            payload = {
                "easyocr": ocr,
                "mag_ratio": magMap[magnification],
                "rotationFlag": magMap[rotationFlag],
                "image": image,
                "nlp": nlp if nlp != "" else None,
                "portfolio": portfolio if portfolio != "" else None,
                "account": account if account != "" else None,
                "piiEntitiesToBeRedacted": piiEntitiesToBeRedacted if piiEntitiesToBeRedacted != "" else None,
                "exclusion": exclusionList if exclusionList != "" else None
            }
            payloads.append(payload)
        
        log.debug("Payloads: " + str(payloads))
        startTime = time.time()
        log.debug("Entered into image_anonymize function")
        responses = []
        for payload in payloads:
            response = ImagePrivacy.image_anonymize(payload)
            responses.append(response)
        ApiCall.delAdminList()
        log.debug("Returned from image_anonymize function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken " + str(totalTime))
        for response in responses:
            if response == 482:
                raise NoMatchingRecognizer
            if response is None:
                raise NoAccountException
            if response == 404:
                raise NoAdminConnException
        
        log.info("exit create from image_anonymize routing method")
        log.debug("tel_Flag==="+str(tel_Falg))
        if(tel_Falg == True):
            log.debug("Inside Telemetry Flag")
            log.info("******TELEMETRY REQUEST COMPLETED********")
        return responses
        
    except PrivacyException as cie:
        log.error("Exception for image_anonymize")
        log.error(cie.__dict__)
        er=[{"tenetName":"Privacy","errorCode":"imageAnonimyzeRouter","errorMessage":str(e)+"Line No:"+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/image/anonymize", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        log.error(cie, exc_info=True)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except NoAdminConnException:
        raise HTTPException(
            status_code=435,
            detail=" Accounts and Portfolio not available with the Subscription!!",
            headers={"X-Error": "Admin Connection is not established,"},
        )
    except NoMatchingRecognizer:
        raise HTTPException(
            status_code=482,
            detail=" No matching recognizers were found to serve the request.",
            headers={"X-Error": "Check Recognizer"},
        )
    except Exception as e:
        log.error(str(e))
        er=[{"tenetName":"Privacy","errorCode":"imageAnonimyzeRouter","errorMessage":str(e)+"Line No:"+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/image/anonymize", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
        
@router.post('/privacy/image/hashify')
def image_hashify(ocr: str = Query('Tesseract', enum=['Tesseract',"EasyOcr","ComputerVision"]),magnification:str=Form(...),rotationFlag:str=Form(...),image: UploadFile = File(...),nlp:str=Form(default=None,example="basic/good/roberta/ranha"),piiEntitiesToBeHashified:Union[str|None]=Form(None),portfolio:Optional[str]=Form(None),account:Optional[str]=Form(None),exclusionList:Optional[str]=Form(None),auth= Depends(auth)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into imageEncryption routing method" )
    try:
        payload={"easyocr":ocr,"mag_ratio":magMap[magnification],"rotationFlag":magMap[rotationFlag],"image":image,"nlp":nlp if nlp!="" else None,"piiEntitiesToBeHashified":piiEntitiesToBeHashified if piiEntitiesToBeHashified !="" else None,"portfolio":portfolio,"account":account,"exclusion":exclusionList}
        log.debug("request payload: "+str(payload))
        startTime = time.time()
        log.debug("Entered into imageEncryption function")
        response = ImagePrivacy.imageEncryption(payload)
        ApiCall.delAdminList()
        log.debug("Returned from imageEncryption function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        if(response==None):
            raise NoAccountException
        if(response==404):
            raise NoAdminConnException        
        
        log.info("exit create from into imageEncryption routing method")
        log.debug("tel_Flag==="+str(tel_Falg))
        if(tel_Falg == True):
            log.debug("Inside Telemetry Flag")
            log.info("******TELEMETRY REQUEST COMPLETED********")
        return response
        
    except PrivacyException as cie:
        log.error("Exception for imageEncryption")
        log.error(cie.__dict__)
        er=[{"tenetName":"Privacy","errorCode":"imageVerifyRouter","errorMessage":str(e)+"Line No:"+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/image/verify", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        log.error(cie, exc_info=True)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except NoAdminConnException:
        raise HTTPException(
            status_code=435,
            detail=" Accounts and Portfolio not available with the Subscription!!",
            headers={"X-Error": "Admin Connection is not established,"},
        )
    except Exception as e:
        log.error(str(e))
        er=[{"tenetName":"Privacy","errorCode":"imageVerifyRouter","errorMessage":str(e)+"Line No:"+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/image/verify", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
     
   
@router.post('/privacy/dicom/anonymize')
def dicom_anonymize(payload: UploadFile = File(...),auth= Depends(auth)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into readDicom routing method" )
    try:
        startTime = time.time()
        log.debug("Entered into readDicom function")
        response =DICOMPrivacy.readDicom(payload)
        log.debug("Returned from readDicom function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        if(response==None):
            raise NoAccountException
        if(response==404):
            raise NoAdminConnException  

     
        
        log.info("exit create from readDicom routing method")
        log.debug("tel_Flag==="+str(tel_Falg))
        if(tel_Falg == True):
            log.debug("Inside Telemetry Flag")
            log.info("******TELEMETRY REQUEST COMPLETED********")
        return response
        
    except PrivacyException as cie:
        log.error("Exception for readDicom")
        log.error(cie.__dict__)
        er=[{"tenetName":"Privacy","errorCode":"DICOMAnonimyzeRouter","errorMessage":str(e)+"Line No:"+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/dicom/anonymize", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        log.error(cie, exc_info=True)
        log.info("exit create from readDicom routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except NoAdminConnException:
        raise HTTPException(
            status_code=435,
            detail=" Accounts and Portfolio not available with the Subscription!!",
            headers={"X-Error": "Admin Connection is not established,"},
        )
    except Exception as e:
        log.error(str(e))
        er=[{"tenetName":"Privacy","errorCode":"DICOMAnonimyzeRouter","errorMessage":str(e)+"Line No:"+str(e.__traceback__.tb_lineno),"apiEndPoint":"/privacy/dicom/anonymize", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

 
## PAYLOAD CHANGED TO ACCEPT TEXT IN A STRUCTURED FORMAT AND GET RESPONSE FOR THE SAME
from starlette.responses import PlainTextResponse
@router.post('/privacy/code/anonymize',response_class=PlainTextResponse)
async def code_redaction(payload_text: str = Body(..., media_type="text/plain", description="The code to be anonymized"),
                        accountName: str = Query("None", description="account name"),
                        portfolioName: str = Query("None", description="portfolio name"),
                         portauth= Depends(auth)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into textner routing method")
    try:
        log.debug("payload==" + str(payload_text))
        
        startTime = time.time()
        log.debug("Entered into textner function")
        response = codeNer.codeText(payload_text,model, tokenizer)
        log.debug("Returned from textner function")
        
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken " + str(totalTime))
        log.debug("response" + str(response))
        
        if response is None:
            raise NoAccountException
        
        log.info("exit create from textner routing method")
        log.debug("TelFlag==="+ str(tel_Falg))
        if(tel_Falg == True):
            telemetryPayload = {
                "uniqueid": id,
                "tenant": "privacy",
                "apiname": "CodeText Annonymize",           
                "user": "None",
                "date":now.isoformat(),
                "lotNumber": "None",
                "request": {
                "portfolio_name": portfolioName,
                "account_name": accountName,
                "exclusion_list": [
                  "None"
                ],
                "inputText": payload_text
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
                executor.submit(send_telemetry_request, telemetryPayload)
            log.info("******TELEMETRY REQUEST COMPLETED********")
        # Return the response as plain text, maintaining the format
        return PlainTextResponse(content=response)
    except PrivacyException as cie:
        log.error("Exception for code anonymize")
        log.error(str(cie))
        er=[{"tenetName":"Privacy","errorCode":"CodeAnnonymizeRouter","errorMessage":str(cie)+"Line No:"+str(cie.__traceback__.tb_lineno),"apiEndPoint":"/privacy/code/anonymize", "errorRequestMethod":"POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id]
        raise cie

from io import BytesIO

@router.post('/privacy/codefile/anonymize')
async def code_anonymize(code_file: UploadFile = File(...),
                         accountName: str = Body("None", description="Enter account name"),
                         portfolioName: str = Body("None", description="Enter portfolio name")):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into filener routing method")
    try:
        # Read the file content from the UploadFile object
        code_content = await code_file.read()
        # Perform code redaction
        startTime = time.time()
        log.debug("Entered into filener function")
        redacted_content, output_code_file = codeNer.codeFile(code_content, code_file.filename, model, tokenizer)
        log.debug("Returned from filener function")
        if isinstance(redacted_content, str):
            redacted_content = redacted_content.encode('utf-8')

        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken " + str(totalTime))
        headers = {
            "Content-Disposition": f"attachment; filename={output_code_file}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }

        # Delete the uploaded file
        await code_file.close()
        output_code_file = os.path.splitext(code_file.filename)[0] + "_redacted" + os.path.splitext(code_file.filename)[1]
        os.remove(output_code_file)
        log.debug("TelFlag===" + str(tel_Falg))
        if tel_Falg:
            telemetryPayload = {
                "uniqueid": id,
                "tenant": "privacy",
                "apiname": "CodeFile Annonymize",
                "user": "None",
                "date": datetime.now().isoformat(),
                "lotNumber": "None",
                "request": {
                    "portfolio_name": portfolioName,
                    "account_name": accountName,
                    "exclusion_list": ["None"],
                    "inputText": code_content.decode('utf-8') if isinstance(code_content, bytes) else code_content
                },
                "response": [{
                    "type": "None",
                    "beginOffset": 0,
                    "endOffset": 0,
                    "score": 0,
                    "responseText": redacted_content.decode('utf-8') if isinstance(redacted_content, bytes) else redacted_content
                }]
            }
            # Convert telemetryPayload to JSON and print it
            log.debug("telemetryPayload=" + json.dumps(telemetryPayload, indent=4))

            # Trigger the API call asynchronously using a separate thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, telemetryPayload)
            log.info("******TELEMETRY REQUEST COMPLETED********")

        # Return the redacted code content as a response with the correct filename
        return StreamingResponse(BytesIO(redacted_content), media_type="application/octet-stream", headers=headers)
    except PrivacyException as cie:
        log.error("Exception for filener")
        log.error(cie, exc_info=True)
        er = [{"tenetName": "Privacy", "errorCode": "codeFileAnonimyzeRouter", "errorMessage": str(cie) + "Line No:" + str(cie.__traceback__.tb_lineno), "apiEndPoint": "/privacy/codefile/anonymize", "errorRequestMethod": "POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid": id, "error": er}

        if len(er) != 0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj, id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id]
        raise cie
    except Exception as e:
        log.error(str(e))
        er = [{"tenetName": "Privacy", "errorCode": "codeFileAnonimyzeRouter", "errorMessage": str(e) + "Line No:" + str(e.__traceback__.tb_lineno), "apiEndPoint": "/privacy/codefile/anonymize", "errorRequestMethod": "POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid": id, "error": er}

        if len(er) != 0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj, id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id]
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

from privacy.service.diffrentialPrivacy import DiffPrivacy
@router.post('/privacy/DifferentialPrivacy/file')
def diff_privacy_file(dataset: UploadFile = File(...),auth= Depends(auth)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into uploadFIle routing method" )
    try:
        # payload={"excel":excel}
        startTime = time.time()
        log.debug("Entered into uploadFIle function")
        response = DiffPrivacy.uploadFIle(dataset)
        log.debug("Returned from uploadFIle function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        if(response==None):
            raise NoAccountException
        
        log.info("exit create from uploadFIle routing method")
        return response
    except PrivacyException as cie:
        log.error("Exception for uploadFIle")
        log.error(cie.__dict__)
        er = [{"tenetName": "Privacy", "errorCode": "diffPrivacyFileRouter", "errorMessage": str(cie) + "Line No:" + str(cie.__traceback__.tb_lineno), "apiEndPoint": "/privacy/DifferentialPrivacy/file", "errorRequestMethod": "POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        log.error(cie, exc_info=True)
        log.info("exit create from uploadFIle routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except Exception as e:
        log.error(str(e))
        er = [{"tenetName": "Privacy", "errorCode": "diffPrivacyFileRouter", "errorMessage": str(e) + "Line No:" + str(e.__traceback__.tb_lineno), "apiEndPoint": "/privacy/DifferentialPrivacy/file", "errorRequestMethod": "POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
from privacy.service.diffrentialPrivacy import DiffPrivacy
@router.post('/privacy/DifferentialPrivacy/anonymize')
def diff_privacy_anonymize(suppression:Optional[str]=Form(""),noiselist:Optional[str]=Form(""),binarylist:Optional[str]=Form(""),rangeList:Optional[str]=Form(""),auth= Depends(auth)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into diffPrivacy routing method" )
    try:
        payload={"suppression":suppression,"noiselist":noiselist,"binarylist":binarylist,"rangelist":rangeList}
        startTime = time.time()
        log.debug("Entered into diffPrivacy function")
        response = DiffPrivacy.diffPrivacy(payload)
        log.debug("Returned from diffPrivacy function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        if(response==None):
            raise NoAccountException
        
        log.info("exit create from diffPrivacy routing method")
        log.debug("res===="+str(response))
        headers = {"Content-Disposition": f"attachment; filename=x.csv"}
        return StreamingResponse(response, media_type="text/csv", headers=headers)
    except PrivacyException as cie:
        log.error("Exception for diffPrivacy")
        log.error(cie.__dict__)
        er = [{"tenetName": "Privacy", "errorCode": "diffPrivacyAnonimyzeRouter", "errorMessage": str(cie) + "Line No:" + str(cie.__traceback__.tb_lineno), "apiEndPoint": "/privacy/DifferentialPrivacy/anonymize", "errorRequestMethod": "POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        log.error(cie, exc_info=True)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except Exception as e:
        log.error(str(e))
        er = [{"tenetName": "Privacy", "errorCode": "diffPrivacyAnonimyzeRouter", "errorMessage": str(e) + "Line No:" + str(e.__traceback__.tb_lineno), "apiEndPoint": "/privacy/DifferentialPrivacy/anonymize", "errorRequestMethod": "POST"}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
@fileRouter.post('/privacy/loadRecognizer')
def loadRecognizer(payload:UploadFile = File(...)):
    
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered into analyze routing method" )

    try:
        log.debug("request payload: "+ str(payload))
        payload = {"file":payload}
        response = LoadRecognizer.set_recognizer(payload)
        return response
    except Exception as e:
        log.error(str(e))
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

@fileRouter.get('/privacy/getRecognizer')
def loadRecognizer():
    id = uuid.uuid4().hex
    request_id_var.set(id)
    try:
        response = LoadRecognizer.load_recognizer()
        return response
    except Exception as e:
        log.error(str(e))
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
   

@fileRouter.post('/privacy-files/video/anonymize')
async def videoPrivacy(ocr: str = Query('Tesseract', enum=['Tesseract',"EasyOcr","ComputerVision"]),magnification:str=Form(...),rotationFlag:str=Form(...),video: UploadFile = File(...),nlp:str=Form(default=None,example="basic/good/roberta/ranha"),portfolio:Optional[str]=Form(None),account:Optional[str]=Form(None),exclusionList:Optional[str]=Form(None),piiEntitiesToBeRedacted:Optional[str]=Form(None),scoreThreshold:Optional[float] = Form(default=float(0.4)),auth= Depends(auth)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into image_anonymize routing method" )
    try:
        payload={"easyocr":ocr,"mag_ratio":magMap[magnification],"rotationFlag":magMap[rotationFlag],"video":video,"nlp":nlp if nlp!="" else None,"portfolio":portfolio,"account":account,"exclusion":exclusionList,"piiEntitiesToBeRedacted":piiEntitiesToBeRedacted,"scoreThreshold":scoreThreshold}
        startTime = time.time()
        video_service = VideoService()
        response = await video_service.videoPrivacy(payload)
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        if(response==None):
            raise NoAccountException
        
        
        log.info("exit create from image_anonymize routing method")
        return response
        
    except PrivacyException as cie:
        log.error("Exception for video_privacy")
        log.error(cie.__dict__)
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            
            if request_id_var.get() in error_dict:
                del error_dict[id]
        log.error(cie, exc_info=True)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except Exception as e:
        log.error(str(e))
        er = [{"tenetName": "Privacy", "errorCode": "diffPrivacyAnonimyzeRouter", "errorMessage": str(e) + "Line No:" + str(e.__traceback__.tb_lineno), "apiEndPoint": "/privacy/DifferentialPrivacy/anonymize", "errorRequestMethod": "POST"}]
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
        
    except PrivacyException as cie:
        log.error("Exception for video_privacy")
        log.error(cie.__dict__)
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            
            if request_id_var.get() in error_dict:
                del error_dict[id]
        log.error(cie, exc_info=True)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except Exception as e:
        log.error(str(e))
        er = [{"tenetName": "Privacy", "errorCode": "diffPrivacyAnonimyzeRouter", "errorMessage": str(e) + "Line No:" + str(e.__traceback__.tb_lineno), "apiEndPoint": "/privacy/DifferentialPrivacy/anonymize", "errorRequestMethod": "POST"}]
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

from privacy.service.pdf_service import PDFService
@fileRouter.post('/privacy-files/PDF/anonymize')
async def PDF(pdf:UploadFile=File(...),nlp:str=Form(default=None,example="basic/good/roberta/ranha"),ocr: str = Query('Tesseract', enum=['Tesseract',"EasyOcr","ComputerVision"]),portfolio:Optional[str]=Form(None),account:Optional[str]=Form(None),exclusionList:Optional[str]=Form(None),piiEntitiesToBeRedacted:Optional[str]=Form(None),scoreThreshold:Optional[float] = Form(default=float(0.4)),auth= Depends(auth)):
    # payload = {"video": video, "easyocr": ocr}
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into image_anonymize routing method" )
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("Before invoking create usecase service ")

        payload={"easyocr":ocr,"mag_ratio":False,"rotationFlag":False,"file": pdf,"nlp":nlp if nlp!="" else None,"portfolio":portfolio,"account":account,"exclusion":exclusionList,"piiEntitiesToBeRedacted":piiEntitiesToBeRedacted,"scoreThreshold":scoreThreshold}
      
        log.debug("Request payload: "+ str(payload))
        response = PDFService.mask_pdf(AttributeDict(payload))
        if(response==None):
            raise NoAccountException
        log.info("After invoking create usecase service ")
        log.debug("Response : "+ str(response))
        log.info("Exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")
        response = Response(content=response.read(), media_type="application/pdf")
        response.headers["Content-Disposition"] = "attachment; filename="+pdf.filename

        return response
        
    except PrivacyException as cie:
        log.error("Exception for encrypt")
        log.error(cie.__dict__)
        er=[{"UUID":id,"function":"textEncryptRouter","msg":cie.__dict__,"description":cie.__dict__}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        # 
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        log.error(cie, exc_info=True)
        log.info("exit create from encrypt routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except Exception as e:
        log.error(str(e))
        # ExceptionDb.create({"UUID":request_id_var.get(),"function":"textAnonimyzeRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        er=[{"UUID":request_id_var.get(),"function":"textAnonimyzeRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid":id,"error":er}
        if len(er)!=0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj,id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id] 
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})   

from privacy.service.ppt_service import PPTService  
@fileRouter.post('/privacy-files/PPT/anonymize')
async def PPT(ppt: UploadFile = File(...),nlp:str=Form(default=None,example="basic/good/roberta/ranha"), ocr: str = Query('Tesseract', enum=['Tesseract', "EasyOcr", "ComputerVision"]), portfolio: Optional[str] = Form(None), account: Optional[str] = Form(None), exclusionList: Optional[str] = Form(None),piiEntitiesToBeRedacted:Optional[str]=Form(None), auth=Depends(auth)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into image_anonymize routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("Before invoking create usecase service")

        payload = {"easyocr": ocr, "mag_ratio": False, "rotationFlag": False, "file": ppt,"nlp":nlp if nlp!="" else None, "portfolio": portfolio, "account": account, "exclusion": exclusionList,"piiEntitiesToBeRedacted":piiEntitiesToBeRedacted}

        log.debug("Request payload: " + str(payload))
        response = PPTService.mask_ppt(AttributeDict(payload))
        if response is None:
            raise NoAccountException
        log.info("After invoking create usecase service")
        log.debug("Response : " + str(response))
        log.info("Exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")
        response = Response(content=response.read(), media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")
        response.headers["Content-Disposition"] = "attachment; filename=" + ppt.filename

        return response

    except PrivacyException as cie:
        log.error("Exception for encrypt")
        log.error(cie.__dict__)
        er = [{"UUID": id, "function": "textEncryptRouter", "msg": cie.__dict__, "description": cie.__dict__}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid": id, "error": er}
        if len(er) != 0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj, id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id]
        log.error(cie, exc_info=True)
        log.info("exit create from encrypt routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except Exception as e:
        log.error(str(e))
        er = [{"UUID": request_id_var.get(), "function": "textAnonimyzeRouter", "msg": str(e), "description": str(e) + "Line No:" + str(e.__traceback__.tb_lineno)}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid": id, "error": er}
        if len(er) != 0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj, id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id]
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"}
        )

from privacy.service.docs_service import DOCService
@fileRouter.post('/privacy-files/DOCX/anonymize')
async def DOCX(docx: UploadFile = File(...), nlp:str=Form(default=None,example="basic/good/roberta/ranha"),ocr: str = Query('Tesseract', enum=['Tesseract', "EasyOcr", "ComputerVision"]), portfolio: Optional[str] = Form(None), account: Optional[str] = Form(None), exclusionList: Optional[str] = Form(None), piiEntitiesToBeRedacted:Optional[str]=Form(None),auth=Depends(auth)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into image_anonymize routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("Before invoking create usecase service")

        payload = {"easyocr": ocr, "mag_ratio": False, "rotationFlag": False, "file": docx,"nlp":nlp if nlp!="" else None, "portfolio": portfolio, "account": account, "exclusion": exclusionList,"piiEntitiesToBeRedacted":piiEntitiesToBeRedacted}

        log.debug("Request payload: " + str(payload))
        response = DOCService.mask_doc(AttributeDict(payload))
        if response is None:
            raise NoAccountException
        log.info("After invoking create usecase service")
        log.debug("Response : " + str(response))
        log.info("Exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")
        response = Response(content=response.read(), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        response.headers["Content-Disposition"] = "attachment; filename=" + docx.filename

        return response

    except PrivacyException as cie:
        log.error("Exception for encrypt")
        log.error(cie.__dict__)
        er = [{"UUID": id, "function": "textEncryptRouter", "msg": cie.__dict__, "description": cie.__dict__}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid": id, "error": er}
        if len(er) != 0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj, id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id]
        log.error(cie, exc_info=True)
        log.info("exit create from encrypt routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except Exception as e:
        log.error(str(e))
        er = [{"UUID": request_id_var.get(), "function": "textAnonimyzeRouter", "msg": str(e), "description": str(e) + "Line No:" + str(e.__traceback__.tb_lineno)}]
        er.extend(error_dict[request_id_var.get()] if request_id_var.get() in error_dict else [])
        logobj = {"uniqueid": id, "error": er}
        if len(er) != 0:
            thread = threading.Thread(target=Telemetry.error_telemetry_request, args=(logobj, id))
            thread.start()
            if request_id_var.get() in error_dict:
                del error_dict[id]
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"}
        )

@fileRouter.post('/privacy-files/csv/anonymize')
def csv_anonymize(file: UploadFile = File(...), keys_to_skip: Union[str, None] = Form(None), nlp: str = Form(default=None, example="basic/good/roberta/ranha"), ocr: str = Query('Tesseract', enum=['Tesseract', "EasyOcr", "ComputerVision"]), portfolio: Optional[str] = Form(None), account: Optional[str] = Form(None), exclusionList: Optional[str] = Form(None),piiEntitiesToBeRedacted:Optional[str]=Form(None),auth=Depends(auth)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered csv_anonymize routing method")
    try:
        payload = {
            "file": file,
            "keys_to_skip": keys_to_skip.split(',') if keys_to_skip else None,
            "nlp":nlp if nlp!="" else "basic",
            "portfolio": portfolio, 
            "account": account, 
            "exclusion": exclusionList,
            "piiEntitiesToBeRedacted":piiEntitiesToBeRedacted

        }
        log.debug("Payload: " + str(payload))
        start_time = time.time()
        output = CSVService.csv_anonymize(payload)
        end_time = time.time()
        total_time = end_time - start_time
        log.info("Total Time taken " + str(total_time))
        log.info("Exiting csv_anonymize routing method")
        return Response(output.getvalue(), media_type='text/csv', headers={'Content-Disposition': 'attachment; filename=anonymized.csv'})
    except Exception as e:
        log.error(str(e))
        raise e



@fileRouter.post('/privacy-files/json/anonymize')
def anonymize_json(file: UploadFile = File(...), keys_to_skip: Union[str, None] = Form(None),  nlp: str = Form(default=None, example="basic/good/roberta/ranha"), ocr: str = Query('Tesseract', enum=['Tesseract', "EasyOcr", "ComputerVision"]), portfolio: Optional[str] = Form(None), account: Optional[str] = Form(None), exclusionList: Optional[str] = Form(None),piiEntitiesToBeRedacted:Optional[str]=Form(None),auth=Depends(auth)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered anonymize_json routing method")
    try:
        payload = {
            "file": file,
            "keys_to_skip": keys_to_skip.split(',') if keys_to_skip else None,
            "nlp": nlp if nlp != "" else "basic",
            "easyocr": ocr,
            "portfolio": portfolio,
            "account": account,
            "exclusion": exclusionList,
            "piiEntitiesToBeRedacted":piiEntitiesToBeRedacted,
        }
        log.debug("Payload: " + str(payload))
        start_time = time.time()
        anonymized_json = JSONService.anonymize_json(payload)
        end_time = time.time()
        total_time = end_time - start_time
        log.info("Total Time taken " + str(total_time))
        log.info("Exiting anonymize_json routing method")
        return Response(anonymized_json, media_type='application/json', headers={'Content-Disposition': 'attachment; filename=anonymized.json'})
    except Exception as e:
        log.error(str(e))
        raise e

from privacy.service.files_service import *

def get_file_extension(filename: str) -> str:
    return filename.split('.')[-1].lower()

@fileRouter.post('/privacy-files/anonymize')
def anonymize_file(file: UploadFile = File(...), nlp: str = Form(default=None, example="basic/good/roberta/ranha"), ocr: str = Query('Tesseract', enum=['Tesseract', "EasyOcr", "ComputerVision"]), portfolio: Optional[str] = Form(None), account: Optional[str] = Form(None), exclusionList: Optional[str] = Form(None), keys_to_skip: Union[str, None] = Form(None),piiEntitiesToBeRedacted:Optional[str]=Form(None), auth=Depends(auth)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
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
            "rotationFlag":False,
            "exclusion": exclusionList,
            "piiEntitiesToBeRedacted":piiEntitiesToBeRedacted,
            "keys_to_skip": keys_to_skip.split(',') if keys_to_skip else None
        }
        log.debug("Payload: " + str(payload))
        start_time = time.time()
        response_file = FileService.anonymize_file(payload, file_extension)
        end_time = time.time()
        total_time = end_time - start_time
        log.info("Total Time taken " + str(total_time))
        log.info("Exiting anonymize_file routing method")
        
        media_type = 'application/octet-stream'
        if file_extension == 'csv':
            media_type = 'text/csv'
        elif file_extension == 'json':
            media_type = 'application/json'
        elif file_extension == 'pdf':
            media_type = 'application/pdf'
        elif file_extension == 'ppt':
            media_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        elif file_extension == 'docx':
            media_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

        return StreamingResponse(response_file, media_type=media_type, headers={"Content-Disposition": f"attachment; filename=anonymized.{file_extension}"})
    except Exception as e:
        log.error(str(e))
        raise HTTPException(status_code=500, detail="An error occurred during file anonymization.")