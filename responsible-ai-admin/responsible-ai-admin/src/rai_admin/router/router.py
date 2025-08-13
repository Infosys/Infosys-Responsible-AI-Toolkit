"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from ast import Dict
from fastapi import Body, Depends, Form,Request,APIRouter, HTTPException
from typing import List, Union
from rai_admin.mappers.PtrnRecogMapper import PtrnRecogResponse,PtrnRecogRequest, PtrnRecogStatus
from rai_admin.mappers.RecognizerMapper import *

from rai_admin.mappers.AccMasterMapper import *
from rai_admin.mappers.PrivacyMapper import *
from rai_admin.mappers.FmConfigMapper import *


#from rai_admin.mappers.mappers import PIIEntity, PIIAnalyzeRequest, PIIAnonymizeResponse, PIIAnonymizeRequest,PIIAnalyzeResponse,PIIImageAnonymizeResponse,PIIImageAnalyzeResponse,PIIImageAnalyzeRequest
# from rai_admin.service.service import rai_adminService as service
from rai_admin.service.recognizer_service import *
from rai_admin.exception.exception import RaiAdminException
from rai_admin.config.logger import CustomLogger
from fastapi import FastAPI, UploadFile,File
from fastapi.responses import FileResponse
import uuid
from rai_admin.config.logger import request_id_var
from rai_admin.dao.AdminException import ExceptionDb
from rai_admin.mappers.SafetyMapper import AccSafetyRequestUpdate, AccountSafetyResponse
from rai_admin.mappers.customeTemplateMapper import AccTempMap, AccTempMapReq, AddTempMap, CustomeTemplateReq,CustomeTemplateRes, CustomeTemplateStatus, RemoveTempMap, TempMapDelete
from rai_admin.service.moderation_service import ModerationService, TempMap
from rai_admin.service.aws_service import AWSService
from rai_admin.mappers.AWSMapper import *
router = APIRouter()
modRouter=APIRouter()
log=CustomLogger()
class NoAccountException(Exception):
    pass


# @router.post('/rai/admin/ptrnRecognise', response_model= PtrnRecogStatus)
# def analyze(payload: PtrnRecogRequest):
#     log.info("Entered create usecase routing method")
#     try:
#         
#         log.debug("request payload: "+ str(payload))
#         response = PrtnRecog.ptrnEntry(payload)
#         
#         log.debug("response : "+ str(response))
#         log.info("exit create usecase routing method")
#         return response
#     except RaiAdminException as cie:
#         log.error(cie.__dict__)
#         log.info("exit create usecase routing method")
#         raise HTTPException(**cie.__dict__)
    
# @router.get('/rai/admin/ptrnRecogniselist', response_model= PtrnRecogResponse)
# def analyze():
#     log.info("Entered create usecase routing method")
#     try:
#         
#         response = PrtnRecog.getPtrnEntry()
#         
#         log.debug("response : "+ str(response))
#         log.info("exit create usecase routing method")
#         return response
#     except RaiAdminException as cie:
#         log.error(cie.__dict__)
#         log.info("exit create usecase routing method")
#         raise HTTPException(**cie.__dict__)
    
# @router.patch('/rai/admin/ptrnRecogniseUpdate', response_model= PtrnRecogStatus)
# def analyze(payload: PtrnRecogUpdate):
#     log.info("Entered create usecase routing method") 
# id = uuid.uuid4().hex
#     try:
#         
#         log.debug("request payload: "+ str(payload))
#         response = PrtnRecog.ptrnUpdate(payload)
#         
#         log.debug("response : "+ str(response))
#         log.info("exit create usecase routing method")
#         return response
#     except RaiAdminException as cie:
#         log.error(cie.__dict__)
#         log.info("exit create usecase routing method")
#         raise HTTPException(**cie.__dict__)
    

# @router.delete('/rai/admin/ptrnRecogniseDelete', response_model= PtrnRecogStatus)
# def analyze(payload: PtrnRecogDelete):
#     log.info("Entered create usecase routing method")
#     try:
#         
#         log.debug("request payload: "+ str(payload))
#         response = PrtnRecog.ptrnDelete(payload)
#         
#         log.debug("response : "+ str(response))
#         log.info("exit create usecase routing method")
#         return response
#     except RaiAdminException as cie:
#         log.error(cie.__dict__)
#         log.info("exit create usecase routing method")
#         raise HTTPException(**cie.__dict__)

    
    
@router.get('/rai/admin/getRecognizer')
def analyze():
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        response = response = PrivacyData.getEntitiesList()
        # response = DataRecogGrp.getDataEntry()
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"DataRecogGrplistRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    



@router.get('/rai/admin/getAccount')
def analyze():
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        response = AccMaster.getAccountDtl()
        # response = DataRecogGrp.getDataEntry()
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"DataRecogGrplistRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    

    

@router.post('/rai/admin/DataRecogGrp', response_model=RecogStatus)
async def analyze(name: str= Form(...),filecpy:Optional[UploadFile] = File(None),ptrn:Optional[str]=Form(None),entity: str= Form(...),rtype:str=Form(),score:Optional[str]=Form(None) , context:Optional[str]=Form(None)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        payload={"name":name,"entity":entity,"file":filecpy,"ptrn":ptrn,"type":rtype,"score":float(score),"context":context}
        
        log.debug("request payload: "+ str(payload))
        response = DataRecogGrp.dataEntry(payload)
        # response=PtrnRecogStatus
        # response.status="true"
        # response = "yes"
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"DataRecogGrpRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    
    
@router.get('/rai/admin/DataRecogGrplist', response_model= RecogResponse)
def analyze():
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = DataRecogGrp.getDataEntry()
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"DataRecogGrplistRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    
@router.post('/rai/admin/DataRecogGrpEntites', response_model= DataEntitiesResponse)
def analyze(payload:DataEntitiesRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = DataRecogGrp.getEntityDetails(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"DataRecogGrpEntitesRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    

@router.patch('/rai/admin/DataEntitesUpdate', response_model= RecogStatus)
def analyze(payload:DataEntity):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = DataRecogGrp.EntityUpdate(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"DataEntitesUpdateRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
        
## FOR SAFETY

@router.patch('/rai/admin/SafetyUpdate', response_model= AccMasterStatus)
def analyze(payload:AccSafetyRequestUpdate):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = AccMaster.SafetyUpdate(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"SafetyEntitesUpdateRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    

@router.patch('/rai/admin/DataGrpUpdate', response_model= RecogStatus)
def analyze(payload:DataGrpUpdate):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = DataRecogGrp.DataGrpUpdate(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"DataGrpUpdateRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    
@router.patch('/rai/admin/DataEntityAdd', response_model= RecogStatus)
def analyze(payload:DataEntityAdd):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = DataRecogGrp.EntityAdd(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"DataEntityAddRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    

@router.delete('/rai/admin/DataRecogGrpDelete', response_model= AccMasterStatus)
def analyze(payload: DataGrpDelete):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        log.debug("request payload: "+ str(payload))
        response = DataRecogGrp.DataGrpDelete(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"DataRecogGrpDeleteRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    


    
@router.delete('/rai/admin/DataRecogEntityDelete', response_model= RecogStatus)
def analyze(payload: DataEntityDelete):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        log.debug("request payload: "+ str(payload))
        response = DataRecogGrp.DataEntityDelete(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"DataRecogEntityDeleteRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    

@router.post('/rai/admin/PrivacyParameter', response_model=AccMasterStatus)
async def analyze(payload:PrivacyParameterRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
    
        
        log.debug("request payload: "+ str(payload))
       
        response = AccMaster.addPrivacyParameter(payload)
        # response=PtrnRecogStatus
        # response.status="true"
        # response = "yes"
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
        


@router.post('/rai/admin/SafetyParameter', response_model=AccountSafetyResponse)
async def analyze(payload:AccountSafetyRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
    
        
        log.debug("request payload: "+ str(payload))
        # if payload.safetyRequest is None:
        #     payload.safetyRequest={
        #      "drawings":0.5,
        #      "hentai":0.5,
        #      "neutral":0.5,
        #      "porn":0.5,
        #      "sexy":0.5
        #     }
        response = SafetyParameter.addSafetyParameter(payload)
        # response = AccMaster.accEntry(payload)
        # response=PtrnRecogStatus
        # response.status="true"
        # response = "yes"
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    

@router.post('/rai/admin/AccMasterEntry', response_model=AccMasterStatus)
async def analyze(payload:AccMasterRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
    
        
        log.debug("request payload: "+ str(payload))
        
        response = AccMaster.accEntry(payload)
        # response=PtrnRecogStatus
        # response.status="true"
        # response = "yes"
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    
@router.get('/rai/admin/AccMasterList', response_model= AccMasterResponse)
def analyze():
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = AccMaster.getAccEntry()
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterListRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    



# @router.post('/rai/admin/AccPtrnList', response_model= AccPtrnResponse)
# def analyze(payload:AccPtrnDataRequest):
#     log.info("Entered create usecase routing method")
#     try:
#         
#         response = AccMaster.getAccPtrn(payload)
#         
#         log.debug("response : "+ str(response))
#         log.info("exit create usecase routing method")
#         return response
#     except RaiAdminException as cie:
#         log.error(cie.__dict__)
#         log.info("exit create usecase routing method")
#         raise HTTPException(**cie.__dict__)

@router.post('/rai/admin/AccDataList', response_model=Union[AccDataResponse,None])
def analyze(payload:AccPtrnDataRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = AccMaster.getAccData(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccDataListRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

@router.post('/rai/admin/AccSafetyListAccountWise')
def analyze(payload:AccPtrnDataRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        print(payload)
        #response = AccMaster.getAccData(payload)
        response = AccMaster.getAccSafetyData(payload)
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccSafetyListRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    


@router.post('/rai/admin/PrivacyDataList', response_model= AccPrivacyResponse)
def analyze(payload:AccPrivacyRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = PrivacyData.getDataList(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"PrivacyDataListRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    


@router.post('/rai/admin/SafetyDataList', response_model= Union[AccSafetyParameterResponse,None])
def analyze(payload:AccPrivacyRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = SafetyData.getDataList(payload)
        
        
        log.debug("response : "+ str(response))
        print("Response=====",response)
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"PrivacyDataListRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
   
    
@router.delete('/rai/admin/AccMasterDelete', response_model= AccMasterStatus)
def analyze(payload: AccMasterDelete):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        log.debug("request payload: "+ str(payload))
        response = AccMaster.AccDelete(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterDeleteRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    


    
@router.delete('/rai/admin/AccDataDelete', response_model= AccMasterStatus)
def analyze(payload: AccDataDelete):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        log.debug("request payload: "+ str(payload))
        print(str(payload))
        response = AccMaster.DataEntityDelete(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)  
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccDataDeleteRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
      
    

@router.get('/rai/admin/LoadRecognizers', response_model= AccMasterStatus)
def analyze():
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = DataLOader.loader()
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"LoadRecognizersRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    

@router.patch('/rai/admin/AccEntityAdd', response_model= AccMasterStatus)
def analyze(payload:DataAdd):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = AccMaster.DataEntityAdd(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccEntityAddRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    



@router.post('/rai/admin/PrivacyEncrypt', response_model= AccMasterStatus)
def analyze(payload:AccEncryptionRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = AccMaster.setEncryption(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"PrivacyEncryptRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    

@router.patch('/rai/admin/ThresholdUpdate', response_model= AccThresholdScoreResponse)
def analyze(payload:AccThresholdScoreRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = AccMaster.ThresholdScoreUpdate(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"ThresholdUpdateRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    

@router.get('/rai/admin/ConfigApi', response_model= ConfigApiResponse)
def analyze():
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = DataLOader.loadApi()
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"ConfigApiRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    



@router.post('/rai/admin/ApiPost', response_model= AccMasterStatus)
def analyze(payload:ConfigApi):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = DataLOader.fillApi(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"ApiPostRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
  
  
# Update endpoint
@router.patch('/rai/admin/ApiUpdate', response_model=AccMasterStatus)
def update_api(payload: ConfigApiUpdate):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered update API routing method")
    try:
        response = DataLOader.updateApi(payload)
        log.debug("response : "+ str(response))
        log.info("exit update API routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit update API routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"ApiUpdateRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

# Delete endpoint
@router.delete('/rai/admin/ApiDelete', response_model=AccMasterStatus)
def delete_api(payload: ConfigApiDelete):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered delete API routing method")
    try:
        response = DataLOader.deleteApi(payload)
        log.debug("response : "+ str(response))
        log.info("exit delete API routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit delete API routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"ApiDeleteRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})  





@router.patch('/rai/admin/UpdateOpenAI', response_model= OpenAIResponse)
def analyze(payload:OpenAIRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = OpenAI.setOpenAI(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"UpdateOpenAIRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    

@router.patch('/rai/admin/UpdateReminder', response_model= OpenAIResponse)
def analyze(payload:ReminderRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = OpenAI.setReminder(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"UpdateReminderRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    


@router.patch('/rai/admin/UpdateGoalPriority', response_model= OpenAIResponse)
def analyze(payload:GoalPriority):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = OpenAI.setGoalPriority(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"UpdateGoalPriorityRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    

@router.get('/rai/admin/getOpenAI', response_model= OpenAIStatus)
def analyze():
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = OpenAI.getOpenAI()
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"getOpenAIRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    

@router.post('/rai/admin/userRole', response_model= OpenAIRoleResponse)
def analyze(payload:OpenAiRoleRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = OpenAI.CheckRole(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"userRoleRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    





@router.get('/rai/admin/getRole', response_model= AuthorityResponse)
def analyze():
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = Role.getRole()
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"getRoleRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    
@router.post('/rai/admin/FMConfigEntry', response_model= FMConfigEntry)
def analyze(payload: FMConfigRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create fm config method")
    try:
        log.debug("request payload: "+ str(payload))
        response = FMConfig.fmEntry(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method in try ")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"FMConfigEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
@router.get('/rai/admin/FMConfigEntryList', response_model= FmConfigResponse)
def analyze():
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = FMConfig.fmAccEntry()
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"FMConfigEntryListRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    

@router.post('/rai/admin/FmGrpDataList', response_model=Union[FmAccDataResponse,None])
def analyze(payload:AccPtrnDataRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = FMConfig.getFmGrpData(payload)
        # if(response == Null):

        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"FmGrpDataListRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
@router.patch('/rai/admin/FmGrpDataUpdate', response_model= FmConfigUpdateStatus)
def analyze(payload:FMGrpData):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = FMConfig.FmGrpUpdate(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"FmGrpDataUpdateRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    

@router.post('/rai/admin/getAttributes',response_model=FmAccDataResponse)
def analyze(payload:AccPortRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        log.debug("request payload: "+ str(payload))

        response = FMConfig.getByAccPort(payload)
        # print(response.dataList)
        if(response.dataList==[]):
            raise NoAccountException

        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
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
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"getAttributesRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    

@router.delete('/rai/admin/FmConfigDelete', response_model= FmConfigUpdateStatus)
def analyze(payload: FmConfigDelete):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        log.debug("request payload: "+ str(payload))
        response = FMConfig.FmConfigDelete(payload)
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"FmConfigDeleteRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    
@router.get('/rai/admin/ModerationCheckLists', response_model= ModerationCheckResponse)
def analyze():
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = FMConfig.getModerationChecks()
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"ModerationCheckListsRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    
@router.get('/rai/admin/RestrictedTopicsLists', response_model= ModerationCheckResponse)
def analyze():
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = FMConfig.getRestrictedTopics()
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"RestrictedTopicsListsRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
@router.get('/rai/admin/OutputModerationCheckLists', response_model= ModerationCheckResponse)
def analyze():
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        
        response = FMConfig.getOutputModerationChecks()
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"OutputModerationCheckListsRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    

# @router.get('/rai/admin/ThemeTextsLists', response_model= ModerationCheckResponse)
# def analyze():
#     log.info("Entered create usecase routing method")
#     try:
#         
#         response = FMConfig.getThemeTexts()
#         
#         log.debug("response : "+ str(response))
#         log.info("exit create usecase routing method")
#         return response
#     except RaiAdminException as cie:
#         log.error(cie.__dict__)
#         log.info("exit create usecase routing method")
#         raise HTTPException(**cie.__dict__)

    
    
    
@router.post('/rai/admin/uploadFile')
def pdfFile_anonymize(file: List[UploadFile] = File(...),userId:str=Form(...))->List:
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")

    try:
        # re = payload.file._file
        # b = io.BytesIO()
        # print(b.read)
        # print("ressssss",re)
        payload={"file":file,"userId":userId}
        
        log.debug(str(payload))
        
        response=RAG.storeFile(payload)
        log.debug(str(response))
        
        log.info("exit create usecase routing method")
        # print("res----",response)
        return response
        
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"uploadFileRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    
@router.post('/rai/admin/getFiles')
async def pdfFile_anonymize(userId:str=Form(...))->list:
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")

    try:
        # re = payload.file._file
        # b = io.BytesIO()
        # print(b.read)
        # print("ressssss",re)
        payload={"userId":userId}
        
        log.debug(str(payload))
        
        response=RAG.getFiles(payload)
        log.debug(str(response))
        
        
        log.info("exit create usecase routing method")
        # print("res----",response)
        return response
        
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"getFilesRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
    
@router.post('/rai/admin/setCache')
def pdfFile_anonymize(embName:str=Form(...),userId:str=Form(...),docid:List[str]=Form(...)):
# def pdfFile_anonymize(items:dict[str,str]):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")

    try:
        # re = payload.file._file
        # b = io.BytesIO()
        # print(b.read)
        # print("ressssss",re)
        # payload=items
        # print(docid)
        payload={"docid":[i for i in docid[0].split(",")],"uid":userId,"ename":embName}
        
        log.debug(str(payload))
        
        response=RAG.setCache(payload)
        log.debug(str(response))
        
        log.info("exit create usecase routing method")
        # print("res----",response)
        return response
        
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"setCacheRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    
@router.post('/rai/admin/getEmbedings')
async def pdfFile_anonymize(userId:str=Form(...))->list:
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")

    try:
        # re = payload.file._file
        # b = io.BytesIO()
        # print(b.read)
        # print("ressssss",re)
        payload={"userId":userId}
        
        log.debug(str(payload))
        
        response=RAG.getEmbedings(payload)
        log.debug(str(response))
        
        
        log.info("exit create usecase routing method")
        # print("res----",response)
        return response
        
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"getEmbedingsRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    

@router.delete('/rai/admin/clearEmbedings')
async def pdfFile_anonymize(embId:str=Form(...))->list:
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")

    try:
        # re = payload.file._file
        # b = io.BytesIO()
        # print(b.read)
        # print("ressssss",re)
        
        payload={"eid":float(embId)}
        
        log.debug(str(payload))
        
        response=RAG.delEmbedings(payload)
        log.debug(str(response))
        
        
        log.info("exit create usecase routing method")
        # print("res----",response)
        return response
        
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"clearEmbedingsRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})


@router.delete('/rai/admin/deleteFile')
async def pdfFile_anonymize(docid:str=Form(...),userid:str=Form()):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")

    try:
        # re = payload.file._file
        # b = io.BytesIO()
        # print(b.read)
        # print("ressssss",re)
        
        payload={"docid":float(docid),"userId":userid}
        
        log.debug(str(payload))
        
        response=RAG.delFiles(payload)
        log.debug(str(response))
        
        
        log.info("exit create usecase routing method")
        # print("res----",response)
        return response
        
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"clearDocsRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    


@modRouter.post('/rai/admin/createCustomeTemplate', response_model=CustomeTemplateStatus)
# async def analyze(payload:CustomeTemplateReq):
async def analyze(payload:CustomeTemplateReq):
# async def analyze(templateName:str=Form(),templateData:UploadFile=File(...)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        # payload=AttributeDict({"templateName":templateName,"templateData":templateData})
        
        log.debug("request payload: "+ str(payload))
        
        response = ModerationService.createTemplate(payload)
        # response=PtrnRecogStatus
        # response.status="true"
        # response = "yes"
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})


@modRouter.get('/rai/admin/getCustomeTemplate/{userId}', response_model=CustomeTemplateRes)
async def analyze(userId,category):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
    
        
        # log.debug("request payload: "+ str(payload))
        payload=AttributeDict({"userId":userId,"category":category})
        print("payload",payload)
        response = ModerationService.getTemplate(payload)
        # response=PtrnRecogStatus
        # response.status="true"
        # response = "yes"
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

@modRouter.post('/rai/admin/getTemplate', response_model=CustomeTemplateRes)
# async def analyze(payload:CustomeTemplateReq):
async def analyze(templateId:str=Form()):
# async def analyze(templateName:str=Form(),templateData:UploadFile=File(...)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        payload=AttributeDict({"templateId":templateId})
        
        log.debug("request payload: "+ str(payload))
        
        response = ModerationService.getTempData(payload)
        # response=PtrnRecogStatus
        # response.status="true"
        # response = "yes"
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

# @modRouter.get('/rai/admin/getTemplateFile/{userId}')
# async def analyze(userId):
#     id = uuid.uuid4().hex
#     request_id_var.set(id)
#     log.info("Entered create usecase routing method")
#     try:
    
        
#         # log.debug("request payload: "+ str(payload))
        
#         response = ModerationService.getTemplateFile(userId)
#         # response=PtrnRecogStatus
#         # response.status="true"
#         # response = "yes"
        
#         log.debug("response : "+ str(response))
#         log.info("exit create usecase routing method")
#         return FileResponse(response)
#     except RaiAdminException as cie:
#         log.error(cie.__dict__)
#         log.info("exit create usecase routing method")
#         raise HTTPException(**cie.__dict__)
#     except Exception as e:
#         log.error(str(e))
#         ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
#         raise HTTPException(
#             status_code=500,
#             detail="Please check with administration!!",
#             headers={"X-Error": "Please check with administration!!"})


@modRouter.patch('/rai/admin/updateCustomeTemplate', response_model=CustomeTemplateStatus)
# async def analyze(payload:CustomeTemplateReq):
async def analyze(payload:CustomeTemplateReq):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
    
        
        log.debug("request payload: "+ str(payload))
        
        response = ModerationService.updateTemplate(payload)
        # response=PtrnRecogStatus
        # response.status="true"
        # response = "yes"
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

@modRouter.delete('/rai/admin/deleteCustomeTemplate', response_model=CustomeTemplateStatus)
# async def analyze(payload:CustomeTemplateReq):
async def analyze(templateId:str=Form(...)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
    
        payload=AttributeDict({"templateId":templateId})
        log.debug("request payload: "+ str(payload))
        
        response = ModerationService.deleteTemplate(payload)
        # response=PtrnRecogStatus
        # response.status="true"
        # response = "yes"
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

@modRouter.delete('/rai/admin/deleteSubTemplate', response_model=CustomeTemplateStatus)
# async def analyze(payload:CustomeTemplateReq):
async def analyze(subTemplateId:str=Form(...)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
    
        payload=AttributeDict({"subTemplateId":subTemplateId})
        log.debug("request payload: "+ str(payload))
        
        response = ModerationService.deleteSubTemplate(payload)
        # response=PtrnRecogStatus
        # response.status="true"
        # response = "yes"
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

@modRouter.post('/rai/admin/AccTemplateMap', response_model=CustomeTemplateStatus)
# async def analyze(payload:CustomeTemplateReq):
async def analyze(payload:AccTempMapReq):
# async def analyze(templateName:str=Form(),templateData:UploadFile=File(...)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        # payload=AttributeDict({"templateName":templateName,"templateData":templateData})
        
        log.debug("request payload: "+ str(payload))
        
        response = TempMap.AccTempMap(payload)
        # response=PtrnRecogStatus
        # response.status="true"
        # response = "yes"
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

@modRouter.get('/rai/admin/getModMaps')
async def analyze(userid,portfolio,account):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        payload=AttributeDict({"userid":userid,"portfolio": portfolio,"account": account})
        response = TempMap.getAccModMap(payload)
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

@modRouter.get('/rai/admin/getModMap')
async def analyze(category,portfolio,account):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        payload=AttributeDict({"category":category,"portfolio": portfolio,"account": account})
        response = TempMap.getModMap(payload)
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

@modRouter.get('/rai/admin/getModConfig')
async def analyze(category,subcategory,portfolio,account):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        payload=AttributeDict({"category":category,"subcategory":subcategory,"portfolio": portfolio,"account": account})
        response = TempMap.getModConfig(payload)
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

@modRouter.get('/rai/admin/getAccTemplate/{userId}')
async def analyze(userId):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
    
        
        # log.debug("request payload: "+ str(payload))
        payload=AttributeDict({"userId":userId})
        response = TempMap.getAccTempMap(payload)
        # response=PtrnRecogStatus
        # response.status="true"
        # response = "yes"
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})


@modRouter.post('/rai/admin/getTempMap', response_model=list)
# async def analyze(payload:CustomeTemplateReq):
async def analyze(accMasterId:str=Form(...)):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
    
        payload=AttributeDict({"accMasterId":accMasterId})
        log.debug("request payload: "+ str(payload))
        
        response = TempMap.getTempMap(payload)
        # response=PtrnRecogStatus
        # response.status="true"
        # response = "yes"
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})


@modRouter.delete('/rai/admin/deleteTempMap', response_model=CustomeTemplateStatus)
# async def analyze(payload:CustomeTemplateReq):
async def analyze(payload:TempMapDelete):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
    
        # payload=AttributeDict({"subTemplateId":subTemplateId})
        log.debug("request payload: "+ str(payload))
        
        response = TempMap.deleteTempMap(payload)
        # response=PtrnRecogStatus
        # response.status="true"
        # response = "yes"
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})



@modRouter.patch('/rai/admin/addTempMap', response_model=CustomeTemplateStatus)
# async def analyze(payload:CustomeTemplateReq):
async def analyze(payload:AddTempMap):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
    
        # payload=AttributeDict({"subTemplateId":subTemplateId})
        log.debug("request payload: "+ str(payload))
        
        response = TempMap.addTempMap(payload)
        # response=PtrnRecogStatus
        # response.status="true"
        # response = "yes"
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
@modRouter.delete('/rai/admin/removeTempMap', response_model=CustomeTemplateStatus)
# async def analyze(payload:CustomeTemplateReq):
async def analyze(payload:RemoveTempMap):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
    
        # payload=AttributeDict({"subTemplateId":subTemplateId})
        log.debug("request payload: "+ str(payload))
        
        response = TempMap.removeTempMap(payload)
        # response=PtrnRecogStatus
        # response.status="true"
        # response = "yes"
        
        log.debug("response : "+ str(response))
        log.info("exit create usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"AccMasterEntryRouter","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

############################################# For storing AWS Creds ####################################################

# For getting AWS Credentials
@router.get('/rai/admin/getAWSCreds')
def getAWSCreds(credName):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered getAWSCreds usecase routing method")
    try:
        response = AWSService.getAWSCreds({"credName":credName})
        log.debug("response : "+ str(response))
        log.info("exit getAWSCreds usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit getAWSCreds usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"getAWSCreds","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})

# For Storing AWS Creds
@router.post('/rai/admin/addAWSCreds', response_model=AWSStatus)
def addAWSCreds(payload:AWSReq):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered addAWSCreds usecase routing method")
    try:
        response = AWSService.createCreds(payload)
        log.debug("response : "+ str(response))
        log.info("exit addAWSCreds usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit addAWSCreds usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"addAWSCreds","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    

@router.patch('/rai/admin/updateAWSCreds', response_model= AWSStatus)
def updateAWSCreds(payload:CredUpdate):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered updateAWSCreds usecase routing method")
    try:
        response = AWSService.updateCreds(payload)
        log.debug("response : "+ str(response))
        log.info("exit updateAWSCreds usecase routing method")
        return response
    except RaiAdminException as cie:
        log.error(cie.__dict__)
        log.info("exit updateAWSCreds usecase routing method")
        raise HTTPException(**cie.__dict__)
    except Exception as e:
        log.error(str(e))
        ExceptionDb.create({"UUID":request_id_var.get(),"function":"updateAWSCreds","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
        raise HTTPException(
            status_code=500,
            detail="Please check with administration!!",
            headers={"X-Error": "Please check with administration!!"})
    

###############################################################################################
