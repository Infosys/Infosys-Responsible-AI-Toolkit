'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import asyncio
import http
from io import BytesIO
from tempfile import NamedTemporaryFile
import time
import uuid
import httpx
import requests
from privacy.util.code_detect.ner.pii_inference.netcustom import code_detect_ner
from privacy.dao.TelemetryFlagDb import TelemetryFlag
from fastapi import Depends, Query,Request,APIRouter, HTTPException, WebSocket,websockets,FastAPI,Cookie
from typing import List, Union

from privacy.service.privacytelemetryservice import PrivacyTelemetryRequest
from privacy.service.Video_service import *
from fastapi.params import Form
from privacy.mappers.mappers import *
#from privacy.mappers.mappers import PIIEntity, PIIAnalyzeRequest, PIIAnonymizeResponse, PIIAnonymizeRequest,PIIAnalyzeResponse,PIIImageAnonymizeResponse,PIIImageAnalyzeResponse,PIIImageAnalyzeRequest
from privacy.service.service import PrivacyService as service, TelemetryFlagData
# from privacy.service.logo_service import Logo 
from privacy.service.code_detect_service import *
from privacy.service.excel_service import Excel
from privacy.service.service import DICOM
from privacy.exception.exception import PrivacyException
from privacy.config.logger import CustomLogger

from fastapi import FastAPI, UploadFile,File
from fastapi.responses import FileResponse, JSONResponse
from datetime import date
import concurrent.futures
from fastapi import Request
from fastapi.responses import StreamingResponse
from privacy.util.code_detect.ner.pii_inference.netcustom import *
# from privacy.util.face_detect.mask_detect_video import mask_video
import logging
# from privacy.code_generator.codegeneration import create_new_recognizer_file,modify_recognizer_registry,modify_init_py,run_wheel_creation_commands, copy_wheel_file,test
from privacy.dao.privacy.PrivacyException import ExceptionDb
from privacy.dao.privacy.TelemetryDb import TelemetryDb
router = APIRouter()
# user_id=1234
log=CustomLogger()
app = FastAPI()
# logger = UserLogger()

import tracemalloc

#@router.post('/privacy/text/analyze', response_model= PIIAnalyzeResponse)
today = date.today()
from datetime import datetime
import asyncio
from dotenv import load_dotenv
load_dotenv()
# import gc
import os
from uuid import UUID, uuid4
# from fastapi_sessions.backends.implementations import InMemoryBackend
# from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
# from request_id_store import request_ids
from privacy.config.logger import request_id_var
# from fastapi.se

# from fastapi_session import get_session
# returns current date and time
now = datetime.now()
# from memory_profiler import profile
# telFlagData = TelemetryFlag.findall({})[0]
# tel_Falg = telFlagData["TelemetryFlag"]
telFlagData = TelemetryFlag.findall({"Module":"Privacy"})
print("Teldata==",telFlagData)
if(len(telFlagData) == 0):
    telData = TelemetryFlag.create({"module":"Privacy"})
    print("telData===",telData)
privacytelemetryurl = os.getenv("PRIVACY_TELEMETRY_URL")

# print("tel_falg===",tel_Falg)


class NoAccountException(Exception):
    pass





## FUNCTION FOR FAIL_SAFE TELEMETRY
def send_telemetry_request(privacy_telemetry_request):
    try:
        response = requests.post(privacytelemetryurl, json=privacy_telemetry_request)
        response.raise_for_status()
        response_data = response.json()
        print(response_data)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"send_telemetry_requestFunction","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

@router.post('/privacy/text/analyze', response_model= PIIAnalyzeResponse)
# @profile
def analyze(payload: PIIAnalyzeRequest):

    # gc.collect()
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered into analyze routing method" )

    try:
        log.debug("request payload: "+ str(payload))
        startTime = time.time()
        log.debug("Entered into analyze function")
        tracemalloc.start()
        response = service.analyze(payload)
       
        tracemalloc.stop()
        log.debug("Returned from analyze function")
        endTime = time.time()
        totalTime = endTime - startTime
        
        log.info("Total Time taken "+str(totalTime))
        if(response==None):
            print("Inside Raise Exception")
            # return "Portfolio/Account Is Incorrect"
            raise NoAccountException
        #     raise HTTPException(
        #     status_code=430,
        #     detail="Portfolio/Account Is Incorrect",
        #     headers={"X-Error": "There goes my error"},

        # )
    
        log.debug("response : "+ str(response))
        log.info("exit create from analyze routing method")
        telFlagData = TelemetryFlag.findall({"Module":"Privacy"})[0]
        tel_Falg = telFlagData["TelemetryFlag"]
        log.debug("TelFlag==="+ str(tel_Falg))
        # TelemetryDb.create({"UUID":id,"tenant":"privacy","apiName":analyze.__name__,"portfolio":payload.portfolio,"accountName":payload.account,"exclusion_list":payload.exclusionList,"entityrecognised":"Text"})
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
                "UUID": id,
                "tenant": "privacy",
                "apiname": analyze.__name__,           
                "user": payload.user,
                "date":now.isoformat(),
                # "exclusionList": payload.exclusionList,
                "request": requestObj,
                "response": responseList
            }
            TelemetryDb.create(telemetryPayload)
            send_telemetry_request(telemetryPayload)
            # privacy_telemetry_request = PrivacyTelemetryRequest(
            #         tenant='privacy',
            #         user = payload.user,
            #         apiname=analyze.__name__,
            #         #counts= '1',
            #         date=now.isoformat(),
            #         request = requestObj,
            #         response = responseList
            # )
            # Trigger the API call asynchronously using a separate thread
                # with concurrent.futures.ThreadPoolExecutor() as executor:
                #     executor.submit(send_telemetry_request, telemetryPayload)
            log.info("******TELEMETRY REQUEST COMPLETED********")
        # responseprivacytelemetry = requests.post(privacytelemetryurl, json=privacy_telemetry_request.__dict__)
        # gc.collect()
        return response
    except PrivacyException as cie:
        log.debug("Exception for analyze")
        log.error(cie.__dict__)
        ExceptionDb.create({"UUID":id,"function":"textAnalyzeRouter","msg":cie.__dict__,"description":cie.__dict__})
        # print(cie)
        # print(cie.__dict__)
        log.error(cie, exc_info=True)
        log.info("exit create from analyze routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"textAnalyzeRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    
@router.post('/privacy/text/anonymize', response_model= PIIAnonymizeResponse)
def anonymize(payload: PIIAnonymizeRequest):
    
    id = uuid.uuid4().hex
    request_id_var.set(id)
    
    log.info("Entered create into anonymize routing method")
    try:
        # log.info("Entered create usecase routing method" )
        log.debug("request payload: "+ str(payload))
        startTime = time.time()
        log.debug("Entered into anonymize function")
        response = service.anonymize(payload)
        log.debug("Returned from anonymize function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        if(response==None):
            raise NoAccountException
        #     raise HTTPException(
        #     status_code=430,
        #     detail="Portfolio/Account Is Incorrect",
        #     headers={"X-Error": "There goes my error"},
        # )
        # log.info("after invoking create usecase service ")
        log.debug("response : "+ str(response))
        log.info("exit create from anonymize routing method")
        telFlagData = TelemetryFlag.findall({"Module":"Privacy"})[0]
        tel_Falg = telFlagData["TelemetryFlag"]
        # log.debug("Tel Flag==="+ str(tel_Falg))
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
                "UUID": id,
                "tenant": "privacy",
                "apiname": anonymize.__name__,
                "user": payload.user,
                "date":now.isoformat(),
                # "exclusionList": payload.exclusionList,
                "request": requestObj,
                "response": [responseObj]
            }
            TelemetryDb.create(telemetryPayload)
            send_telemetry_request(telemetryPayload)
            # privacy_telemetry_request = PrivacyTelemetryRequest(
            #     tenant='privacy',
            #     user = payload.user,
            #     apiname=anonymize.__name__,
            #     #counts= '1',
            #     date=now.isoformat(),
            #     portfolio=payload.portfolio,
            #     accountname=payload.account,
            #     exclusion_list=payload.exclusionList,
            #     entityrecognised='Text'
            # )
            # Trigger the API call asynchronously using a separate thread
           
            # with concurrent.futures.ThreadPoolExecutor() as executor:
            #     executor.submit(send_telemetry_request, telemetryPayload)
            log.info("******TELEMETRY REQUEST COMPLETED********")
        return response
    except PrivacyException as cie:
        log.error("Exception for anonymize")
        log.error(cie.__dict__)
        ExceptionDb.create({"UUID":id,"function":"textAnonimyzeRouter","msg":cie.__dict__,"description":cie.__dict__})
        
        log.error(cie, exc_info=True)
        log.info("exit create from anonymize routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"textAnonimyzeRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

@router.post('/privacy/image/analyze', response_model= PIIImageAnalyzeResponse)
def image_analyze(ocr: str = Query('Tesseract', enum=['Tesseract',"EasyOcr"]),magnification:str=Form(...),image: UploadFile = File(...),portfolio:Optional[str]=Form(None),account:Optional[str]=Form(None),exclusionList:Optional[str]=Form(None)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into image_analyze routing method")
    try:
       
        payload={"easyocr":ocr,"mag_ratio":bool(magnification),"image":image,"portfolio":portfolio,"account":account,"exclusion":exclusionList}
        log.debug("Requested payload" + str(payload))
        startTime = time.time()
        log.debug("Entered into image_analyze function")
        response = service.image_analyze(payload)
        log.debug("Returned from image_analyze function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        if(response==None):
            raise NoAccountException
        #     raise HTTPException(
        #     status_code=430,
        #     detail="Portfolio/Account Is Incorrect",
        #     headers={"X-Error": "There goes my error"},
        # )
        
        log.info("exit create from image_analyze routing method")
        telFlagData = TelemetryFlag.findall({"Module":"Privacy"})[0]
        tel_Falg = telFlagData["TelemetryFlag"]
        log.debug("tel_Flag==="+str(tel_Falg))
        # responseList = list(map(lambda obj: obj.__dict__, response.PIIEntities))
        # requestList = payload.__dict__
        if(tel_Falg == True):
            log.debug("Inside Telemetry Flag")
            # telemetryPayload = {
            #     "UUID": id,
            #     "tenant": "privacy",
            #     "apiName": image_analyze.__name__,
            #     # "portfolio": portfolio,
            #     # "accountName": account,
            #     # "exclusion_list": exclusionList,
            #     "request": requestList,
            #     "response": responseList
            # }
            # TelemetryDb.create(telemetryPayload)
            privacy_telemetry_request = PrivacyTelemetryRequest(
                tenant='privacy',
                apiname=image_analyze.__name__,
                #counts= '1',
                date=now.isoformat(),
                portfolio=portfolio,
                accountname=account,
                exclusion_list=exclusionList,
                entityrecognised='Image'
            )
            # Trigger the API call asynchronously using a separate thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, privacy_telemetry_request)
            log.info("******TELEMETRY REQUEST COMPLETED********")
        return response
        
    except PrivacyException as cie:
        log.error("Exception for image_analyze")
        log.error(cie.__dict__)
        ExceptionDb.create({"UUID":id,"function":"imageAnalyzeRouter","msg":cie.__dict__,"description":cie.__dict__})
       
        log.error(cie, exc_info=True)
        log.info("exit create from image_analyze routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"imageAnalyzeRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

@router.post('/privacy/image/anonymize')
def image_anonymize(ocr: str = Query('Tesseract', enum=['Tesseract',"EasyOcr"]),magnification:str=Form(...),image: UploadFile = File(...),portfolio:Optional[str]=Form(None),account:Optional[str]=Form(None),exclusionList:Optional[str]=Form(None)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into image_anonymize routing method" )
    try:
        
        payload={"easyocr":ocr,"mag_ratio":bool(magnification),"image":image,"portfolio":portfolio,"account":account,"exclusion":exclusionList}
        log.debug("Payload:"+str(payload))
        startTime = time.time()
        log.debug("Entered into image_anonymize function")
        response = service.image_anonymize(payload)
        log.debug("Returned from image_anonymize function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        if(response==None):
            raise NoAccountException
        #     raise HTTPException(
        #     status_code=430,
        #     detail="Portfolio/Account Is Incorrect",
        #     headers={"X-Error": "There goes my error"},
        # )
        
        
        log.info("exit create from image_anonymize routing method")
        telFlagData = TelemetryFlag.findall({"Module":"Privacy"})[0]
        tel_Falg = telFlagData["TelemetryFlag"]
        log.debug("tel_Flag==="+str(tel_Falg))
        # responseList = list(map(lambda obj: obj.__dict__, response.PIIEntities))
        # requestList = payload.__dict__
        if(tel_Falg == True):
            log.debug("Inside Telemetry Flag")
            # telemetryPayload = {
            #     "UUID": id,
            #     "tenant": "privacy",
            #     "apiName": image_anonymize.__name__,
            #     # "portfolio": portfolio,
            #     # "accountName": account,
            #     # "exclusion_list": exclusionList,
            #     "request": requestList,
            #     "response": responseList
            # }
            # TelemetryDb.create(telemetryPayload)
            privacy_telemetry_request = PrivacyTelemetryRequest(
                tenant='privacy',
                apiname=image_anonymize.__name__,
                #counts= '1',
                date=now.isoformat(),
                portfolio=portfolio,
                accountname=account,
                exclusion_list=exclusionList,
                entityrecognised='Image'
            )
            # Trigger the API call asynchronously using a separate thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, privacy_telemetry_request)
            log.info("******TELEMETRY REQUEST COMPLETED********")
        return response
        
    except PrivacyException as cie:
        log.error("Exception for image_anonymize")
        log.error(cie.__dict__)
        ExceptionDb.create({"UUID":id,"function":"imageAnonimyzeRouter","msg":cie.__dict__,"description":cie.__dict__})
       
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
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"imageAnonimyzeRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
# @router.post('/privacy/pii/image/anonymize/zip')                                   #########@#@@#@#$@
# def image_anonymize(payload: UploadFile):
#     try:
#         log.info("Entered create usecase routing method" )
#         response = service.zipimage_anonymize(payload)
#         if(response==None):
#             raise HTTPException(
#             status_code=430,
#             detail="Portfolio/Account Is Incorrect",
#             headers={"X-Error": "There goes my error"},
#         )
#         log.info("after invoking create usecase service ")
        
#         log.info("exit create usecase routing method")
#         return response
        
#     except PrivacyException as cie:
#         log.error(cie.__dict__)
#         log.info("exit create usecase routing method")
#         raise HTTPException(**cie.__dict__)


# @router.post('/privacy/pii/image/anonymize/multiple')
# def image_anonymize(payload: List[UploadFile] = File(...)):
#     try:
#         log.info("Entered create usecase routing method" )
#         response=[]
#         for image in payload:
#             response.append(service.image_anonymize(image))
            
#         log.info("after invoking create usecase service ")
        
#         log.info("exit create usecase routing method")
#         return response
        
#     except PrivacyException as cie:
#         log.error(cie.__dict__)
#         log.info("exit create usecase routing method")
#         raise HTTPException(**cie.__dict__)

# @router.post('/privacy/pii/image/analyze/multiple')#,response_model=PIIMultipleImageAnalyzeResponse)
# def image_analyze(payload: List[UploadFile] = File(...)):
#     try:
#         log.info("Entered create usecase routing method" )
#         response=[]
#         for image in payload:
#             response.append(service.temp(image))
        
#         log.info("after invoking create usecase service ")
        
#         log.info("exit create usecase routing method")
#         return response
        
#     except PrivacyException as cie:
#         log.error(cie.__dict__)
#         log.info("exit create usecase routing method")
#         raise HTTPException(**cie.__dict__)


@router.post('/privacy/image/verify')
def image_verify(image: UploadFile = File(...),portfolio:Optional[str]=Form(None),account:Optional[str]=Form(None),exclusionList:Optional[str]=Form(None)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into image_verify routing method" )
    try:
        payload={"image":image,"portfolio":portfolio,"account":account,"exclusion":exclusionList}
        log.debug("request payload: "+str(payload))
        startTime = time.time()
        log.debug("Entered into image_verify function")
        response = service.image_verify(payload)
        log.debug("Returned from image_verify function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        if(response==None):
            raise NoAccountException
        #     raise HTTPException(
        #     status_code=430,
        #     detail="Portfolio/Account Is Incorrect",
        #     headers={"X-Error": "There goes my error"},
        # )
      
        
        log.info("exit create from image_verify routing method")
        telFlagData = TelemetryFlag.findall({"Module":"Privacy"})[0]
        tel_Falg = telFlagData["TelemetryFlag"]
        log.debug("tel_Flag==="+ str(tel_Falg))
        # responseList = list(map(lambda obj: obj.__dict__, response.PIIEntities))
        if(tel_Falg == True):
            log.debug("Inside Telemetry Flag")
            # telemetryPayload = {
            #     "UUID": id,
            #     "tenant": "privacy",
            #     "apiName": image_verify.__name__,
            #     # "portfolio": portfolio,
            #     # "accountName": account,
            #     # "exclusion_list": exclusionList,
            #     "request": payload,
            #     "response": response
            # }
            # TelemetryDb.create(telemetryPayload)
            privacy_telemetry_request = PrivacyTelemetryRequest(
                tenant='privacy',
                apiname=image_verify.__name__,
                #counts= '1',
                date=now.isoformat(),
                portfolio=portfolio,
                accountname=account,
                exclusion_list=exclusionList,
                entityrecognised='Image'
            )
            # Trigger the API call asynchronously using a separate thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, privacy_telemetry_request)
            log.info("******TELEMETRY REQUEST COMPLETED********")
        return response
        
    except PrivacyException as cie:
        log.error("Exception for image_verify")
        log.error(cie.__dict__)
        ExceptionDb.create({"UUID":id,"function":"imageVerifyRouter","msg":cie.__dict__,"description":cie.__dict__})
       
        log.error(cie, exc_info=True)
        log.info("exit create from image_verify routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"imageVerifyRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    
@router.post('/privacy/image/hashify')
def image_hashify(ocr: str = Query('Tesseract', enum=['Tesseract',"EasyOcr"]),magnification:str=Form(...),image: UploadFile = File(...),portfolio:Optional[str]=Form(None),account:Optional[str]=Form(None),exclusionList:Optional[str]=Form(None)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into imageEncryption routing method" )
    try:
        payload={"easyocr":ocr,"mag_ratio":bool(magnification),"image":image,"portfolio":portfolio,"account":account,"exclusion":exclusionList}
        log.debug("request payload: "+str(payload))
        startTime = time.time()
        log.debug("Entered into imageEncryption function")
        response = service.imageEncryption(payload)
        log.debug("Returned from imageEncryption function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        if(response==None):
            raise NoAccountException
        #     raise HTTPException(
        #     status_code=430,
        #     detail="Portfolio/Account Is Incorrect",
        #     headers={"X-Error": "There goes my error"},
        # )
        log.info("exit create from into imageEncryption routing method")
        telFlagData = TelemetryFlag.findall({"Module":"Privacy"})[0]
        tel_Falg = telFlagData["TelemetryFlag"]
        log.debug("tel_Flag==="+str(tel_Falg))
        # requestList = payload.__dict__
        if(tel_Falg == True):
            log.debug("Inside Telemetry Flag")
            # telemetryPayload = {
            #     "UUID": id,
            #     "tenant": "privacy",
            #     "apiName": image_verify.__name__,
            #     # "portfolio": portfolio,
            #     # "accountName": account,
            #     # "exclusion_list": exclusionList,
            #     "request": requestList,
            #     "response": response
            # }
            # TelemetryDb.create(telemetryPayload)
            privacy_telemetry_request = PrivacyTelemetryRequest(
                tenant='privacy',
                apiname=image_verify.__name__,
                #counts= '1',
                date=now.isoformat(),
                portfolio=portfolio,
                accountname=account,
                exclusion_list=exclusionList,
                entityrecognised='Image'
            )
            # Trigger the API call asynchronously using a separate thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, privacy_telemetry_request)
            log.info("******TELEMETRY REQUEST COMPLETED********")
        return response
        
    except PrivacyException as cie:
        log.error("Exception for imageEncryption")
        log.error(cie.__dict__)
        ExceptionDb.create({"UUID":id,"function":"imageHashifyRouter","msg":cie.__dict__,"description":cie.__dict__})
       
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
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"imageHashifyRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    


@router.post('/privacy/privacyShield', response_model= PIIPrivacyShieldResponse)
def privacy_shield(payload: PIIPrivacyShieldRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into privacyShield routing method")
    try:
        # log.info("Entered create usecase routing method" )
        log.debug("request payload: "+ str(payload))
        startTime = time.time()
        log.debug("Entered into privacyShield function")
        response = service.privacyShield(payload)
        log.debug("Returned from privacyShield function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        if(response==None):
            raise NoAccountException
        #     raise HTTPException(
        #     status_code=430,
        #     detail="Portfolio/Account Is Incorrect",
        #     headers={"X-Error": "There goes my error"},
        # )
        # log.info("after invoking create usecase service ")
        log.debug("response : "+ str(response))
        log.info("exit create from privacyShield routing method")
        telFlagData = TelemetryFlag.findall({"Module":"Privacy"})[0]
        tel_Falg = telFlagData["TelemetryFlag"]
        log.debug("tel_Flag==="+str(tel_Falg))
        # responseList = response.privacyCheck
        # requestList = payload.__dict__
        if(tel_Falg == True):
            log.debug("Inside Telemetry Flag")
            # telemetryPayload = {
            #     "UUID": id,
            #     "tenant": "privacy",
            #     "apiName": "privacyshield",
            #     # "portfolio": payload.portfolio,
            #     # "accountName": payload.account,
            #     # "exclusion_list": "None",
            #     "request": requestList,
            #     "response": responseList
            # }
            # TelemetryDb.create(telemetryPayload)
            privacy_telemetry_request = PrivacyTelemetryRequest(
                tenant='privacy',
                apiname="privacyshield",
                #counts= '1',
                date=now.isoformat(),
                portfolio=payload.portfolio,
                accountname=payload.account,
                exclusion_list="None",
                entityrecognised='Text'
            )
            # Trigger the API call asynchronously using a separate thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, privacy_telemetry_request)
            log.info("******TELEMETRY REQUEST COMPLETED********")
        return response
    except PrivacyException as cie:
        log.error("Exception for privacyShield")
        log.error(cie.__dict__)
        ExceptionDb.create({"UUID":id,"function":"privacyShield","msg":cie.__dict__,"description":cie.__dict__})
       
        log.error(cie, exc_info=True)
        log.info("exit create from privacyShield routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"privacyShield","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

# from privacy.service.dicom_service import DICOM
# @router.get('/privacy/pii/dicom/anonymize')
# def image_anonymize():
#     try:
#         log.info("Entered create usecase routing method" )
#         # payload={"image":image,"portfolio":portfolio,"account":account,"exclusion":exclusionList}
#         # log.info(str(payload))
#         # response = service.image_anonymize(payload)
#         response=DICOM.dicomReader()
#         # print(response)
        
#         # if(response==None):
#         #     raise HTTPException(
#         #     status_code=430,
#         #     detail="Portfolio/Account Is Incorrect",
#         #     headers={"X-Error": "There goes my error"},
#         # )
#         log.info("after invoking create usecase service ")
        
#         log.info("exit create usecase routing method")
#         return response
        
#     except PrivacyException as cie:
#         log.error(cie.__dict__)
#         log.info("exit create usecase routing method")
#         raise HTTPException(**cie.__dict__)
 
   
@router.post('/privacy/dicom/anonymize')
def dicom_anonymize(payload: UploadFile = File(...)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into readDicom routing method" )
    try:
        # payload={"image":image,"portfolio":portfolio,"account":account,"exclusion":exclusionList}
        startTime = time.time()
        log.debug("Entered into readDicom function")
        response =DICOM.readDicom(payload)
        log.debug("Returned from readDicom function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        if(response==None):
            raise NoAccountException
        #     raise HTTPException(
        #     status_code=430,
        #     detail="Portfolio/Account Is Incorrect",
        #     headers={"X-Error": "There goes my error"},
        # )
     
        
        log.info("exit create from readDicom routing method")
        telFlagData = TelemetryFlag.findall({"Module":"Privacy"})[0]
        tel_Falg = telFlagData["TelemetryFlag"]
        log.debug("tel_Flag==="+str(tel_Falg))
        # responseList = list(map(lambda obj: obj.__dict__, response.PIIEntities))
        # requestList = payload.__dict__
        if(tel_Falg == True):
            log.debug("Inside Telemetry Flag")
            # telemetryPayload = {
            #     "UUID": id,
            #     "tenant": "privacy",
            #     "apiName": "DICOMIMAGE",
            #     # "portfolio": "None",
            #     # "accountName": "None",
            #     # "exclusion_list": "None",
            #     "request": requestList,
            #     "response": responseList
            # }
            # TelemetryDb.create(telemetryPayload)
            privacy_telemetry_request = PrivacyTelemetryRequest(
                tenant='privacy',
                apiname='DICOMIMAGE',
                #counts= '1',
                date=now.isoformat(),
                # portfolio= 
                # accountname=payload.account,
                # exclusion_list="None",
                entityrecognised='DICOM'
            )
            # Trigger the API call asynchronously using a separate thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, privacy_telemetry_request)
            log.info("******TELEMETRY REQUEST COMPLETED********")
        return response
        
    except PrivacyException as cie:
        log.error("Exception for readDicom")
        log.error(cie.__dict__)
        ExceptionDb.create({"UUID":id,"function":"DICOMAnonimyzeRouter","msg":cie.__dict__,"description":cie.__dict__})
       
        log.error(cie, exc_info=True)
        log.info("exit create from readDicom routing method")
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
            status_code=430,
            detail="Portfolio/Account Is Incorrect",
            headers={"X-Error": "There goes my error"},
        )
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"DICOMAnonimyzeRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})








# @router.post('/privacy/pii/video/anonymize',response_model= LogoHidingResponse)
   
# @router.post('/privacy/video/anonymize')
# async def image_analyze(payload: UploadFile = File(...),name:Optional[str]=Form(None)):
#     try:
#         log.info("Entered create usecase routing method" )
#         print("payload====",payload)
#         payload={"payload":payload,"filename":name}
#         print("payload====",payload)
#         # payload={"image":image,"portfolio":portfolio,"account":account,"exclusion":exclusionList}
#         response =VideoAnalyzer.anonymize(payload)
#         # for i in response:
#         #     print(i)``
            
#         # print(response)
#         # if(response==None):
#         #     raise HTTPException(
#         #     status_code=430,
#         #     detail="Portfolio/Account Is Incorrect",
#         #     headers={"X-Error": "There goes my error"},
#         # )
#         # log.info("after invoking create usecase service ")
        
#         # log.info("exit create usecase routing method")
#         print(response)
#         # return StreamingResponse(response,media_type="multipart/x-mixed-replace; boundary=frame")

#         # return response
#         telFlagData = TelemetryFlag.findall({"Module":"Privacy"})[0]
#         tel_Falg = telFlagData["TelemetryFlag"]
#         print("tel_Flag===",tel_Falg)
#         if(tel_Falg == True):
#             print("Inside Telemetry Flag")
#             privacy_telemetry_request = PrivacyTelemetryRequest(
#                 tenant='privacy',
#                 apiname="Video_Anonymize",
#                 #counts= '1',
#                 date=now.isoformat(),
#                 # portfolio= 
#                 # accountname=payload.account,
#                 # exclusion_list="None",
#                 entityrecognised='Video'
#             )
#             # Trigger the API call asynchronously using a separate thread
#             with concurrent.futures.ThreadPoolExecutor() as executor:
#                 executor.submit(send_telemetry_request, privacy_telemetry_request)
#         return FileResponse(response,media_type="video/mp4")
#         # return FileResponse(response)
        
#     except PrivacyException as cie:
#         log.error(cie.__dict__)
#         log.info("exit create usecase routing method")
#         raise HTTPException(**cie.__dict__)
    
# @router.post('/privacy/video/anonymize')
# # async def video_anonymize(payload: UploadFile = File(...), name: Optional[str] = Form(None)):
#     id = uuid.uuid4().hex
#     request_id_var.set(id)
#     try:
#         # Save the uploaded video to a temporary file
#         temp_video_path = NamedTemporaryFile(delete=False, suffix=".mp4").name
#         with open(temp_video_path, "wb") as temp_video:
#             temp_video.write(payload.file.read())

#         # # Define paths for face detector and mask detector model
#         # face_detector_path = "face_detector"
#         # mask_detector_model_path = "mask_detector.model"

#         # Call the video processing function
#         output_video_path = NamedTemporaryFile(delete=False, suffix=".mp4").name
#         startTime = time.time()
#         log.info("Entered into mask_video function")
#         mask_video(temp_video_path, output_path=output_video_path)
#         log.info("Returned from mask_video function")
#         endTime = time.time()
#         totalTime = endTime - startTime
#         log.info("Total Time taken "+str(totalTime))

#         # Remove the temporary uploaded video file
#         os.remove(temp_video_path)
#         telFlagData = TelemetryFlag.findall({"Module":"Privacy"})[0]
#         tel_Falg = telFlagData["TelemetryFlag"]
#         log.debug("tel_Flag==="+str(tel_Falg))
#         # responseList = list(map(lambda obj: obj.__dict__, response.PIIEntities))
#         # requestList = payload.__dict__
#         if(tel_Falg == True):
#             log.info("Inside Telemetry Flag")
#             # telemetryPayload = {
#             #     "UUID": id,
#             #     "tenant": "privacy",
#             #     "apiName": "Video_Anonymize",
#             #     # "portfolio": "None",
#             #     # "accountName": "None",
#             #     # "exclusion_list": "None",
#             #     "request": requestList,
#             #     "response": responseList
#             # }
#             # TelemetryDb.create(telemetryPayload)
#             privacy_telemetry_request = PrivacyTelemetryRequest(
#                 tenant='privacy',
#                 apiname="Video_Anonymize",
#                 #counts= '1',
#                 date=now.isoformat(),
#                 # portfolio= 
#                 # accountname=payload.account,
#                 # exclusion_list="None",
#                 entityrecognised='Video'
#             )
#             # Trigger the API call asynchronously using a separate thread
#             with concurrent.futures.ThreadPoolExecutor() as executor:
#                 executor.submit(send_telemetry_request, privacy_telemetry_request)
#             log.info("******TELEMETRY REQUEST COMPLETED********")

#         # Return the processed video as a FileResponse
#         return FileResponse(output_video_path, media_type="video/mp4", filename=name or "output.mp4")

#     except Exception as cie:
#         # Handle exceptions as needed
#         log.error(cie.__dict__)
#         ExceptionDb.create({"UUID":id,"function":"videoAnonimyzeRouter","msg":cie.__dict__,"description":cie.__dict__})
       
#         log.info("Exception for mask_video")
#         log.error(cie, exc_info=True)
#         raise HTTPException(detail=str(cie), status_code=500)


    
@router.post('/privacy/excel/anonymize')
def logo_anonymize(excel: UploadFile = File(...)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into excelanonymize routing method" )
    try:
        payload={"excel":excel}
        print("payload==",payload)
        # print("type==",excel.file.content_type)
        startTime = time.time()
        log.debug("Entered into excelanonymize function")
        response = Excel.excelanonymize(payload)
        log.debug("Returned from excelanonymize function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        if(response==None):
            raise NoAccountException
        #     raise HTTPException(
        #     status_code=430,
        #     detail="Portfolio/Account Is Incorrect",
        #     headers={"X-Error": "There goes my error"},
        # )
       
        log.info("exit create from excelanonymize routing method")
        log.debug("response===="+str(response))
        telFlagData = TelemetryFlag.findall({"Module":"Privacy"})[0]
        tel_Falg = telFlagData["TelemetryFlag"]
        log.debug("tel_Flag==="+str(tel_Falg))
        # responseList = list(map(lambda obj: obj.__dict__, response.PIIEntities))
        # requestList = payload.__dict__
        if(tel_Falg == True):
            log.debug("Inside Telemetry Flag")
            # telemetryPayload = {
            #     "UUID": id,
            #     "tenant": "privacy",
            #     "apiName": "Excel_Anonymize",
            #     # "portfolio": "None",
            #     # "accountName": "None",
            #     # "exclusion_list": "None",
            #     "request": requestList,
            #     "response": responseList
            # }
            # TelemetryDb.create(telemetryPayload)
            privacy_telemetry_request = PrivacyTelemetryRequest(
                tenant='privacy',
                apiname="Excel_Anonymize",
                #counts= '1',
                date=now.isoformat(),
                # portfolio= 
                # accountname=payload.account,
                # exclusion_list="None",
                entityrecognised='Excel'
            )
            # Trigger the API call asynchronously using a separate thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, privacy_telemetry_request)
            log.info("******TELEMETRY REQUEST COMPLETED********")
        return FileResponse(response,media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        # return response
        
    except PrivacyException as cie:
        log.error("Exception for excelanonymize")
        log.error(cie.__dict__)
        ExceptionDb.create({"UUID":id,"function":"excelAnonimyzeRouter","msg":cie.__dict__,"description":cie.__dict__})
       
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
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"excelAnonimyzeRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})


@router.get('/privacy/telemetryFlag', response_model= TelemetryResponse)
def telemetry_flag():
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into getTelFlagData routing method")
    try:
        # log.info("Entered create usecase routing method" )
        # log.debug()
        startTime = time.time()
        log.debug("Entered into getTelFlagData function")
        response = TelemetryFlagData.getTelFlagData()
        log.debug("Returned from getTelFlagData function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        # log.info("after invoking create usecase service ")
        log.debug("response : "+ str(response))
        
        log.info("exit create from getTelFlagData routing method")
        return response
    except PrivacyException as cie:
        log.error("Exception for getTelFlagData")
        log.error(cie.__dict__)
        log.error(cie, exc_info=True)
        log.info("exit create from getTelFlagData routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"telemetryFlagRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
# @router.post('/privacy/code/anonymize')
# def code_redaction(payload: PIICodeDetectRequest):
#     try:
#         log.info("Entered create usecase routing method" )
#         print("payload==",payload)
#         # response = CodeDetect.codeDetectRegex(payload)
#         response = code_detect_ner.textner(payload.inputText)
#         # payload_json = json.dumps(payload)
#         # response = CodeDetect.codeDetectNerText(payload_json)
#         print("response",response)
#         if(response==None):
#             raise HTTPException(
#             status_code=430,
#             detail="Enter the code to redact",
#             headers={"X-Error": "There goes my error"},
#         )
#         log.info("after invoking create usecase service ")
        
#         log.info("exit create usecase routing method")
#         telFlagData = TelemetryFlag.findall({"Module":"Privacy"})[0]
#         tel_Falg = telFlagData["TelemetryFlag"]
#         print("tel_Flag===",tel_Falg)
#         if(tel_Falg == True):
#             print("Inside Telemetry Flag")
#             privacy_telemetry_request = PrivacyTelemetryRequest(
#                 tenant='privacy',
#                 apiname=code_redaction.__name__,
#                 #counts= '1',
#                 date=now.isoformat(),
#                 # portfolio= 
#                 # accountname=payload.account,
#                 # exclusion_list="None",
#                 entityrecognised='Code'
#             )
#             # Trigger the API call asynchronously using a separate thread
#             with concurrent.futures.ThreadPoolExecutor() as executor:
#                 executor.submit(send_telemetry_request, privacy_telemetry_request)
#         #result = response.inputText
#         return response
        
#     except PrivacyException as cie:
#         log.error(cie.__dict__)
#         log.info("exit create usecase routing method")
#         raise HTTPException(**cie.__dict__)
    
from starlette.responses import PlainTextResponse
@router.post('/privacy/code/anonymize',response_class=PlainTextResponse)
async def code_redaction(text: str=Form(...)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into textner routing method" )
    try:
        # payload = text  # Extract the text from the request body
        payload_text = text  # Decode the payload bytes to text
        log.debug("payload=="+str(payload_text))
        startTime = time.time()
        log.debug("Entered into textner function")
        response = code_detect_ner.textner(payload_text)
        log.debug("Returned from textner function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        log.debug("response"+  str(response))
        if response is None:
            raise NoAccountException
            # raise HTTPException(
            #     status_code=430,
            #     detail="Enter the code to redact",
            #     headers={"X-Error": "There goes my error"},
            # )
        
        # log.info("after invoking create usecase service ")
        log.info("exit create from textner routing method")
        telFlagData = TelemetryFlag.findall({"Module":"Privacy"})[0]
        tel_Falg = telFlagData["TelemetryFlag"]
        log.debug("tel_Flag==="+str(tel_Falg))
        # responseList = list(map(lambda obj: obj.__dict__, response.PIIEntities))
        # requestList = payload.__dict__
        if(tel_Falg == True):
            log.debug("Inside Telemetry Flag")
            # telemetryPayload = {
            #     "UUID": id,
            #     "tenant": "privacy",
            #     "apiName": code_redaction.__name__,
            #     # "portfolio": "None",
            #     # "accountName": "None",
            #     # "exclusion_list": "None",
            #     "request": requestList,
            #     "response": responseList
            # }
            # TelemetryDb.create(telemetryPayload)
            privacy_telemetry_request = PrivacyTelemetryRequest(
                tenant='privacy',
                apiname=code_redaction.__name__,
                #counts= '1',
                date=now.isoformat(),
                # portfolio= 
                # accountname=payload.account,
                # exclusion_list="None",
                entityrecognised='Code'
            )
            # Trigger the API call asynchronously using a separate thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, privacy_telemetry_request)
            log.info("******TELEMETRY REQUEST COMPLETED********")
        return response
    except PrivacyException as cie:
        log.error("Exception for code anonymize")
        log.error(cie, exc_info=True)
        # Handle any other exceptions
        log.error(cie.__dict__)
        ExceptionDb.create({"UUID":id,"function":"codeAnonimyzeRouter","msg":cie.__dict__,"description":cie.__dict__})
        raise HTTPException(**cie.__dict__)
    except NoAccountException:
        raise HTTPException(
                status_code=430,
                detail="Enter the code to redact",
                headers={"X-Error": "There goes my error"},
            )
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"codeAnonimyzeRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})  
        # ...
        # print(e)
        

# @router.post('/privacy/codefile/anonymize')
# async def code_anonymize(code_file: UploadFile = File(...)):
#     try:
#         log.info("Before invoking code redaction service")
        
#         # Save the uploaded code file to a temporary location
#         input_code_file = f"privacy/util/code_detect/ner/pii_inference/temp/{code_file.filename}"
#         with open(input_code_file, "wb") as file:
#             file.write(code_file.file.read())
#         # Perform code redaction
#         output_code_file = code_detect_ner.filener(input_code_file)
#         log.info("After invoking code redaction service")
#         # Return the redacted code file as a response
#         return FileResponse(output_code_file, media_type="text/plain")
#     except Exception as e:
#         log.exception("An error occurred during code redaction")
#         raise

from io import BytesIO

# @router.post('/privacy/codefile/anonymize')
# async def code_anonymize(code_file: UploadFile = File(...)):
#     try:
#         # Read the file content from the UploadFile object
#         code_content = await code_file.read()

#         # Perform code redaction
#         redacted_content, output_code_file = code_detect_ner.filener(code_content, code_file.filename)
#         headers = {
#             "Content-Disposition": f"attachment; filename={output_code_file}",
#             "Access-Control-Expose-Headers": "Content-Disposition"
#         }
#         # Return the redacted code content as a response with the correct filename
#         # headers = {"Content-Disposition": f"attachment; filename={output_code_file}"}
#         return StreamingResponse(BytesIO(redacted_content), media_type="application/octet-stream", headers=headers)
#     except Exception as e:
#         raise e
@router.post('/privacy/codefile/anonymize')
async def code_anonymize(code_file: UploadFile = File(...)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into filener routing method" )
    try:
        # Read the file content from the UploadFile object
        code_content = await code_file.read()

        # Perform code redaction
        startTime = time.time()
        log.debug("Entered into filener function")
        redacted_content, output_code_file = code_detect_ner.filener(code_content, code_file.filename)
        log.debug("Returned from filener function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        headers = {
            "Content-Disposition": f"attachment; filename={output_code_file}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }

        # Delete the uploaded file
        await code_file.close()
        # filepath = os.path.join('', code_file.filename)
        output_code_file = os.path.splitext(code_file.filename)[0] + "_redacted" + os.path.splitext(code_file.filename)[1]
        os.remove(output_code_file)
        telFlagData = TelemetryFlag.findall({"Module":"Privacy"})[0]
        tel_Falg = telFlagData["TelemetryFlag"]
        # responseList = list(map(lambda obj: obj.__dict__, response.PIIEntities))
        # requestList = payload.__dict__
        if(tel_Falg == True):
            log.debug("Inside Telemetry Flag")
            # telemetryPayload = {
            #     "UUID": id,
            #     "tenant": "privacy",
            #     "apiName": code_anonymize.__name__,
            #     # "portfolio": "None",
            #     # "accountName": "None",
            #     # "exclusion_list": "None",
            #     "request": requestList,
            #     "response": responseList
            # }
            # TelemetryDb.create(telemetryPayload)
            privacy_telemetry_request = PrivacyTelemetryRequest(
                tenant='privacy',
                apiname=code_anonymize.__name__,
                #counts= '1',
                date=now.isoformat(),
                # portfolio= 
                # accountname=payload.account,
                # exclusion_list="None",
                entityrecognised='Code'
            )
            # Trigger the API call asynchronously using a separate thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, privacy_telemetry_request)
            log.info("******TELEMETRY REQUEST COMPLETED********")

        # Return the redacted code content as a response with the correct filename
        return StreamingResponse(BytesIO(redacted_content), media_type="application/octet-stream", headers=headers)
    except PrivacyException as cie:
        log.error("Exception for filener")
        log.error(cie, exc_info=True)
        ExceptionDb.create({"UUID":id,"function":"codeFileAnonimyzeRouter","msg":cie.__dict__,"description":cie.__dict__})
        raise cie
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"codeFileAnonimyzeRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})




# # from privacy.service.test import Test
# @router.get('/privacy/pii/video/anonymizea')
# async def image_analyze():
#     try:
#         log.info("Entered create usecase routing method" )
#         # payload={"image":image,"portfolio":portfolio,"account":account,"exclusion":exclusionList}
#         # response =VideoAnalyzer.anonymize(payload)
#         # print(response)
#         # if(response==None):
#         #     raise HTTPException(
#         #     status_code=430,
#         #     detail="Portfolio/Account Is Incorrect",
#         #     headers={"X-Error": "There goes my error"},
#         # )
#         # log.info("after invoking create usecase service ")
#         # x=[]
#         x=Test.work()
#         # for i in x:
#         #     print(i)
#         # log.info("exit create usecase routing method")
#         return StreamingResponse(x,media_type="plain/text")
        
        
#     except PrivacyException as cie:
#         log.error(cie.__dict__)
#         log.info("exit create usecase routing method")
#         raise HTTPException(**cie.__dict__)
# app=FastAPI()
# cc=set()
# @app.websocket("/ws")
# async def check(websocket:WebSocket):
#     await websocket.accept()
#     cc.add(websocket)
#     try:
#         while True:
#             m="asdasdasdasdasd"
#             await websocket.send_text(m)
#             await asyncio.sleep(1)
#     except:
#         cc.remove(websocket)



from privacy.service.diffrentialPrivacy import DiffPrivacy
@router.post('/privacy/DifferentialPrivacy/file')
def diff_privacy_file(dataset: UploadFile = File(...)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into uploadFIle routing method" )
    try:
        # payload={"excel":excel}
        # print("payload==",payload)
        # print("type==",excel.file.content_type)
        startTime = time.time()
        log.debug("Entered into uploadFIle function")
        response = DiffPrivacy.uploadFIle(dataset)
        log.debug("Returned from uploadFIle function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        if(response==None):
            raise NoAccountException
        #     raise HTTPException(
        #     status_code=430,
        #     detail="Portfolio/Account Is Incorrect",
        #     headers={"X-Error": "There goes my error"},
        # )
        # log.info("after invoking create usecase service ")
        
        log.info("exit create from uploadFIle routing method")
        # telFlagData = TelemetryFlag.findall({"Module":"Privacy"})[0]
        # tel_Falg = telFlagData["TelemetryFlag"]
        # print("tel_Flag===",tel_Falg)
        # if(tel_Falg == True):
        #     print("Inside Telemetry Flag")
        #     privacy_telemetry_request = PrivacyTelemetryRequest(
        #         tenant='privacy',
        #         apiname="Excel_Anonymize",
        #         #counts= '1',
        #         date=now.isoformat(),
        #         # portfolio= 
        #         # accountname=payload.account,
        #         # exclusion_list="None",
        #         entityrecognised='Excel'
        #     )
        #     # Trigger the API call asynchronously using a separate thread
        #     with concurrent.futures.ThreadPoolExecutor() as executor:
            #    executor.submit(send_telemetry_request, privacy_telemetry_request)
        return response
    except PrivacyException as cie:
        log.error("Exception for uploadFIle")
        log.error(cie.__dict__)
        ExceptionDb.create({"UUID":id,"function":"diffPrivacyFileRouter","msg":cie.__dict__,"description":cie.__dict__})

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
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"diffPrivacyFileRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
from privacy.service.diffrentialPrivacy import DiffPrivacy
@router.post('/privacy/DifferentialPrivacy/anonymize')
def diff_privacy_anonymize(suppression:Optional[str]=Form(""),noiselist:Optional[str]=Form(""),binarylist:Optional[str]=Form(""),rangeList:Optional[str]=Form("")):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create into diffPrivacy routing method" )
    try:
        # log.info("Entered create usecase routing method" )
        # payload={"excel":excel}
        # print("payload==",payload)
        payload={"suppression":suppression,"noiselist":noiselist,"binarylist":binarylist,"rangelist":rangeList}
        # print("type==",excel.file.content_type)
        startTime = time.time()
        log.debug("Entered into diffPrivacy function")
        response = DiffPrivacy.diffPrivacy(payload)
        log.debug("Returned from diffPrivacy function")
        endTime = time.time()
        totalTime = endTime - startTime
        log.info("Total Time taken "+str(totalTime))
        if(response==None):
            raise NoAccountException
        #     raise HTTPException(
        #     status_code=430,
        #     detail="Portfolio/Account Is Incorrect",
        #     headers={"X-Error": "There goes my error"},
        # )
        # log.info("after invoking create usecase service ")
        
        log.info("exit create from diffPrivacy routing method")
        log.debug("res===="+str(response))
        # telFlagData = TelemetryFlag.findall({"Module":"Privacy"})[0]
        # tel_Falg = telFlagData["TelemetryFlag"]
        # print("tel_Flag===",tel_Falg)
        # if(tel_Falg == True):
        #     print("Inside Telemetry Flag")
        #     privacy_telemetry_request = PrivacyTelemetryRequest(
        #         tenant='privacy',
        #         apiname="Excel_Anonymize",
        #         #counts= '1',
        #         date=now.isoformat(),
        #         # portfolio= 
        #         # accountname=payload.account,
        #         # exclusion_list="None",
        #         entityrecognised='Excel'
        #     )
        #     # Trigger the API call asynchronously using a separate thread
        #     with concurrent.futures.ThreadPoolExecutor() as executor:
            #    executor.submit(send_telemetry_request, privacy_telemetry_request)
        # return response
        headers = {"Content-Disposition": f"attachment; filename=x.csv"}
        return StreamingResponse(response, media_type="text/csv", headers=headers)
    except PrivacyException as cie:
        log.error("Exception for diffPrivacy")
        log.error(cie.__dict__)
        ExceptionDb.create({"UUID":id,"function":"diffPrivacyAnonimyzeRouter","msg":cie.__dict__,"description":cie.__dict__})

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
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"diffPrivacyAnonimyzeRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})