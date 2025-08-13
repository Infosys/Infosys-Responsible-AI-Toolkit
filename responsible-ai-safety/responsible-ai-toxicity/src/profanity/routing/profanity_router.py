'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import json
import os
import uuid
from pydantic import BaseModel, Field, Json
from fastapi import Body, Depends, Form,Request,APIRouter, HTTPException
from typing import List, Optional, Union
import requests
from profanity.mappers.mappers import profanity, profanityScoreList, ProfanityAnalyzeRequest, ProfanityAnalyzeResponse,ProfanitycensorRequest, ProfanitycensorResponse,MaliciousURLAnalyzeRequest
from profanity.service.service import  AddProfaneWordService, CsvSafetyService, ProfanityService as service
from profanity.service.malicious_url_service import MaliciousUrlService
from profanity.exception.exception import ProfanityException
from profanity.config.logger import CustomLogger
from datetime import datetime
import concurrent.futures
from fastapi import FastAPI, UploadFile,File
from fastapi import Response
from fastapi.responses import FileResponse

now = datetime.now()
router = APIRouter()
log=CustomLogger()
sslv={"False":False,"True":True,"None":True}
profanitytelemetryurl = os.getenv("PROFANITY_TELEMETRY_URL")

class NoAccountException(Exception):
    pass
class NoAdminConnException(Exception):
    pass

def send_telemetry_request(privacy_telemetry_request):
        log.info(profanitytelemetryurl)
        response = requests.post(profanitytelemetryurl, json=privacy_telemetry_request,verify=sslv[os.getenv("VERIFY_SSL","None")])
        log.info(response)
        response.raise_for_status()
        log.info("after raise status")       
        response_data = response.json()
        log.info(response_data)
        


@router.post('/safety/profanity/addProfaneWords')
def analyze(payload:UploadFile = File(...)):
    log.info("Entered create usecase routing method")
    payload = {"file":payload}
    id = uuid.uuid4().hex
    log.info("UUID: " + id)
    try:
        log.info("before invoking create usecase service ")
        log.debug("request payload: "+ str(payload))
        response = AddProfaneWordService.addProneWord(payload)
        log.info("after invoking create usecase service ")
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except ProfanityException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)





@router.post('/safety/profanity/analyze', response_model= ProfanityAnalyzeResponse)
def analyze(payload: ProfanityAnalyzeRequest):
    log.info("Entered create usecase routing method")
    id = uuid.uuid4().hex
    log.info("UUID: " + id)
    try:
        log.info("before invoking create usecase service ")
        log.debug("request payload: "+ str(payload))
        response = service.analyze(payload)
        log.info("after invoking create usecase service ")
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        log.info('Before telemetry')
        tel_flag = os.getenv('TELEMETRY_FLAG')
        # tel_flag = json.loads(telFlagData)
        log.debug("TelFlag="+ str(tel_flag))
        
        if(tel_flag == "True"):
            profanityScoreList = [dict(obj) for obj in response.profanityScoreList]
            responseObject = {
                "profanity": response.profanity,
                "profanityScoreList": profanityScoreList,
                "outputText": "None"
            }

            telemetryPayload = {
                    "uniqueid": id,
                    "tenant": "profanity",      
                    "apiname": "analyze",   
                    "user": payload.user if payload.user is not None else "None",
                    "date":now.isoformat(),
                    "lotNumber": payload.lotNumber if payload.lotNumber is not None else "None",
                    "request": {
                        "inputText": payload.inputText,
                    },
                    "response": responseObject
                }
            print("INSIDE TELEMETRY IF CONDITION")         
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, telemetryPayload)
            log.info('After telemetry')
        return response
    except ProfanityException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)



@router.post('/safety/profanity/censor', response_model= ProfanitycensorResponse)
def censor(payload: ProfanitycensorRequest):
    log.info("Entered create usecase routing method")
    id = uuid.uuid4().hex
    log.info("UUID: " + id)
    try:
        log.info("before invoking create usecase service ")
        log.debug("request payload: "+ str(payload))
        response = service.censor(payload)
        log.info("after invoking create usecase service ")
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        log.info('Before telemetry')
        tel_flag = os.getenv('TELEMETRY_FLAG')
        # tel_flag = json.loads(telFlagData)
        log.debug("TelFlag==="+ str(tel_flag))

        if(tel_flag == "True"):
            profObj = {
                "profaneWord": "None",
                "beginOffset": 0,
                "endOffset": 0
            }
            profScoreObj ={
                "metricName":"None",
                "metricScore":0
            }
            
            responseObject = {
                "profanity": [profObj],
                "profanityScoreList": [profScoreObj],
                "outputText": response.outputText
            }
            telemetryPayload = {
                    "uniqueid": id,
                    "tenant": "profanity",  
                    "apiname": "censor",       
                    "user": payload.user if payload.user is not None else "None",
                    "date":now.isoformat(),
                    "lotNumber": payload.lotNumber if payload.lotNumber is not None else "None",
                    "request": {
                        "inputText": payload.inputText,
                    },
                    "response": responseObject
                }
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, telemetryPayload)
            log.info('After telemetry')
        return response
    except ProfanityException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)



# @router.post('/safety/profanity/imageanalyze')
# def imageAnalyze(config:Optional[str]=Body(default='{"drawings":0.5,"hentai":0.5,"neutral":0.5,"porn":0.5,"sexy":0.5}'),image: UploadFile = File(...)):
#     # print("===========================",config,type(config))
#     config='{"drawings":0.5,"hentai":0.5,"neutral":0.5,"porn":0.5,"sexy":0.5}' if config==None or config=="" else config
#     config=json.loads(config)
#     log.info("Entered create usecase routing method")
#     id = uuid.uuid4().hex
#     try:
#         log.debug("before invoking create usecase service ")
#         log.debug("request payload: "+ str(image))
#         response = service.imageAnalyze(image,config)
#         log.debug("after invoking create usecase service ")
#         # log.debug("response : "+ str(response))
#         log.debug("exit create usecase routing method")
      
       
#         return response
#     except ProfanityException as cie:
#         log.error(cie.__dict__)
#         log.info("exit create usecase routing method")
#         raise HTTPException(**cie.__dict__)




@router.post('/safety/profanity/imageanalyze')
def imageAnalyze(
    portfolio: Optional[str] = Form(None),
    account: Optional[str] = Form(None),
    image: UploadFile = File(...),
    accuracy: Optional[str] = Form("high")  # New parameter for accuracy
):
    payload = {
        "image": image,
        "portfolio": portfolio,
        "account": account,
        "accuracy": accuracy  # Include the new parameter in the payload
    }
    log.info("Entered create usecase routing method")
    id = uuid.uuid4().hex
    log.info("UUID: " + id)
    try:
        log.debug("before invoking create usecase service ")
        log.debug("request payload: " + str(payload))
        response = service.imageAnalyze(payload)
        log.debug("after invoking create usecase service ")
        log.debug("exit create usecase routing method")
        if response is None:
            print("Inside Raise Exception")
            raise NoAccountException
        if response == 404:
            raise NoAdminConnException
        return response
    except ProfanityException as cie:
        log.error(cie.__dict__)
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
            detail="Accounts and Portfolio not available with the Subscription!!",
            headers={"X-Error": "Admin Connection is not established,"},
        )

@router.post('/safety/profanity/imageGenerate')
def imageAnalyze(portfolio:Optional[str]=Form(None),account:Optional[str]=Form(None),prompt:str=Form(...)):
    log.info("Entered create usecase routing method")
    # config='{"drawings":0.5,"hentai":0.25,"neutral":0.5,"porn":0.25,"sexy":0.25}' if config==None or config=="" else config
    # config=json.loads(config)
    payload={"prompt":prompt,"portfolio":portfolio,"account":account}
    id = uuid.uuid4().hex
    log.info("UUID: " + id)
    try:
        log.debug("before invoking create usecase service ")
        # log.debug("request payload: "+ str(image))
        response = service.imageGenerate(payload)
        if(response==None):
            print("Inside Raise Exception")
            # return "Portfolio/Account Is Incorrect"
            raise NoAccountException
        if(response==404):
            raise NoAdminConnException
        log.debug("after invoking create usecase service ")
        log.debug("response : "+ str(response))
        log.debug("exit create usecase routing method")

        
        return response
    except ProfanityException as cie:
        log.error(cie.__dict__)
        log.debug("exit create usecase routing method")
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

## NSFW VIDEO

@router.post('/safety/profanity/videosafety')
def videoAnalyze(video: UploadFile = File(...)):
    log.info("Entered create usecase routing method")
    # config='{"drawings":0.5,"hentai":0.25,"neutral":0.5,"porn":0.25,"sexy":0.25}' if config==None or config=="" else config
    # config=json.loads(config)
    payload={"video":video}
    print(payload,"Payload from Router")
    id = uuid.uuid4().hex
    log.info("UUID: " + id)
    try:
        log.debug("before invoking create usecase service ")
        # log.debug("request payload: "+ str(image))
        response = service.videoCensor(payload)
        # print(response,"Response after API")
        if(response==None):
            print("Inside Raise Exception")
            # return "Portfolio/Account Is Incorrect"
            raise NoAccountException
        if(response==404):
            raise NoAdminConnException
        log.debug("after invoking create usecase service ")
        # log.debug("response : "+ str(response))
        log.debug("exit create usecase routing method")

        
        return response
    except ProfanityException as cie:
        log.error(cie.__dict__)
        log.debug("exit create usecase routing method")
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

## NUDITY IMAGES

@router.post('/safety/profanity/nudanalyze')
def nudAnalyze(portfolio:Optional[str]=Form(None),account:Optional[str]=Form(None),image: UploadFile = File(...)):
    # print("===========================",config,type(config))
    payload={"image":image,"portfolio":portfolio,"account":account}
    # config='{"drawings":0.5,"hentai":0.5,"neutral":0.5,"porn":0.5,"sexy":0.5}' if config==None or config=="" else config
    # config=json.loads(config)
    log.info("Entered create usecase routing method")
    id = uuid.uuid4().hex
    log.info("UUID: " + id)
    try:
        log.debug("before invoking create usecase service ")
        log.debug("request payload: "+ str(payload))
        response = service.nudCensor(payload)
        log.debug("after invoking create usecase service ")
        # log.debug("response : "+ str(response))
        log.debug("exit create usecase routing method")
        if(response==None):
            print("Inside Raise Exception")
            # return "Portfolio/Account Is Incorrect"
            raise NoAccountException
        if(response==404):
            raise NoAdminConnException
       
        return response
    except ProfanityException as cie:
        log.error(cie.__dict__)
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
        
## Nudity Video
@router.post('/safety/profanity/nudvideosafety')
def videoAnalyzeNud(video: UploadFile = File(...)):
    log.info("Entered create usecase routing method")
    
    payload={"video":video}
    print(payload,"Payload from Router")
    id = uuid.uuid4().hex
    log.info("UUID: " + id)
    try:
        log.debug("before invoking create usecase service ")
        # log.debug("request payload: "+ str(image))
        response = service.nudVideoCensor(payload)
        # print(response,"Response after API")
        if(response==None):
            print("Inside Raise Exception")
            # return "Portfolio/Account Is Incorrect"
            raise NoAccountException
        if(response==404):
            raise NoAdminConnException
        log.debug("after invoking create usecase service ")
        # log.debug("response : "+ str(response))
        log.debug("exit create usecase routing method")

        
        return response
    except ProfanityException as cie:
        log.error(cie.__dict__)
        log.debug("exit create usecase routing method")
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


## Malicious URL Detection
@router.post('/safety/profanity/maliciousUrl')
def maliciousUrl(payload: MaliciousURLAnalyzeRequest):
    log.info("Entered create usecase routing method")
    id = uuid.uuid4().hex
    log.info("UUID: " + id)
    try:
        log.info("before invoking create usecase service ")
        log.debug("request payload: "+ str(payload))
        m= MaliciousUrlService()
        response = m.scan(payload)
        log.info("after invoking create usecase service ")
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        log.info('Before telemetry')
        tel_flag = os.getenv('TELEMETRY_FLAG')
        log.debug("TelFlag="+ str(tel_flag))
        
        if(tel_flag == "True"):
            log.info("INSIDE TELEMETRY IF CONDITION")    
            responseObject = {
                "profanityScoreList": response['result'],
                "outputText": "None"
            }

            telemetryPayload = {
                    "uniqueid": id,
                    "tenant": "malicious-url-detection",      
                    "apiname": "detect",   
                    "user": payload.user if payload.user is not None else "None",
                    "date": now.isoformat(),
                    "lotNumber": payload.lotNumber if payload.lotNumber is not None else "None",
                    "request": {
                        "inputText": payload.inputText,
                    },
                    "response": responseObject
                }
                 
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(send_telemetry_request, telemetryPayload)
            log.info('After telemetry')
        return response
    except ProfanityException as cie:
        log.error(cie.__dict__)
        log.debug("exit create usecase routing method")
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
        
@router.post('/safety/profanity/csvSafety')
def bulkAnalyze(file: UploadFile = File(...)):
    log.info("Entered create usecase routing method")
    payload={"file":file}
    id = uuid.uuid4().hex
    log.info("UUID: " + id)
    try:
        log.info("before invoking create usecase service ")
        log.debug("request payload: "+ str(payload))
        # response = service.analyze(payload)
        response = CsvSafetyService.csvSafetyCheck(payload)
        log.info("after invoking create usecase service ")
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        log.info('Before telemetry')
        tel_flag = os.getenv('TELEMETRY_FLAG')
        # tel_flag = json.loads(telFlagData)
        log.debug("TelFlag="+ str(tel_flag))
        
        
        return Response(response.getvalue(), media_type='text/csv', headers={'Content-Disposition': 'attachment; filename=safety.csv'})
        
    except ProfanityException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)


