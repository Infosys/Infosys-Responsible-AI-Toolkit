'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from io import BytesIO
import uuid
from fastapi import Body, Depends, File, Form,Request,APIRouter, HTTPException, UploadFile
from typing import List, Optional, Union
from pydantic import BaseModel


# from questionnaire.mapper.Questionnaires.mapper import DimensionRequest, PrincipalGuidanceRequest, PrincipalGuidanceResponse, QuestionOptionRequest, QuestionOptionResponse, QuestionRequest, QuestionResponse, QusPrincipalMappingRequest, QusPrincipalMappingResponse, SubDimensionRequest, SubDimensionResponse,
from questionnaire.mapper.Questionnaires.mapper import ImpactRequest, SubmissionResponse,SubmissionRequest,UseCaseNameRequest

# from questionnaire.mapper.Questionnaires.mapper import DimensionResponse

from questionnaire.exception.exception import PrivacyException;

from questionnaire.config.logger import CustomLogger
from questionnaire.config.logger import request_id_var

from questionnaire.mapper.Questionnaires.canvasMapper import *

from questionnaire.dao.UserLotAllocationDb import *
from questionnaire.dao.TelemetryUrlStore import *
from questionnaire.mapper.Questionnaires.lotAllocateMapper import *
from questionnaire.dao.ExceptionDb import ExceptionDb

from questionnaire.mapper.Questionnaires.aiCanvasMapper import *


router = APIRouter()
log=CustomLogger()


class LargeDataInput(BaseModel):
    data:list
   
@router.get('/questionnaire/allLotDetails/{userId}')
def getAllSlotAssign(userId):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create getAllSlotAssignRouter routing method")

    try:
        log.debug("before invoking get getAllSlotAssignRouter service")
        response = UserLotAllocationDb.findAllOnUser(userId)
        response=response[::-1]
        # response=[1,2]
        log.debug("after invoking get getAllSlotAssignRouter service")
        log.debug("response: "+ str(response))
        log.info("exit create getAllSlotAssignRouter routing method")
        return response
    except PrivacyException as cie:
        log.error(cie.__dict__)
        log.info("exit create getAllSlotAssignRouter routing method")
        raise HTTPException(**cie.__dict__) 
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"getAllSlotAssignRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
@router.post('/questionnaire/telemetryUrlAdd')
def addTelemetryUrl(payload:linkRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create addTelemetryUrlRouter routing method")

    try:
        log.debug("before invoking get addTelemetryUrlRouter service")
        log.debug("request payload: "+ str(payload))
        response = TelemetryUrlStore.create(payload)
        log.debug("after invoking get addTelemetryUrlRouter service")
        log.debug("response: "+ str(response))
        log.info("exit create addTelemetryUrlRouter routing method")
        return response
    except PrivacyException as cie:
        log.error(cie.__dict__)
        log.info("exit create addTelemetryUrlRouter routing method")
        raise HTTPException(**cie.__dict__) 
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"addTelemetryUrlRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
@router.get('/questionnaire/telemetryUrlGet/{tenant}')
def getAllTelemetryUrl(tenant):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create getAllTelemetryUrlRouter routing method")

    try:
        log.debug("before invoking get getAllTelemetryUrlRouter service")
        response = TelemetryUrlStore.findOne(tenant)
        log.debug("after invoking get getAllTelemetryUrlRouter service")
        log.debug("response: "+ str(response))
        log.info("exit create getAllTelemetryUrlRouter routing method")
        return response
    except PrivacyException as cie:
        log.error(cie.__dict__)
        log.info("exit create getAllTelemetryUrlRouter routing method")
        raise HTTPException(**cie.__dict__) 
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"getAllTelemetryUrlRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
from questionnaire.service.workbench.service import WorkBench

@router.post('/questionnaire/workbench/uploadFile')
def slotAssign(file: UploadFile = File(...), userId: str = Form(...), tenant: List[str] = Form(...)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create slotAssignRouter routing method")

    try:
        payload={"file":file,"userId":userId,"tenant":tenant[0].split(',')}
        log.debug("before invoking create slotAssignRouter service")
        log.debug("request payload: "+ str(payload))
        response =WorkBench.uploadFile(payload)
        log.debug("after invoking create slotAssignRouter service")
        log.debug("response: "+ str(response))
        log.info("exit create slotAssignRouter routing method")
        return response
    except PrivacyException as cie:
        log.error(cie.__dict__)
        log.info("exit create slotAssignRouter routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"lotAssignRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

