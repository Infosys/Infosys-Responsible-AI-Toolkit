"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Union, List
# from SafetyMapper import AccSafetyRequest
class AccSafetyRequest(BaseModel):
    portfolio:str=Field(example="Infosys")
    account:str=Field(example="IMPACT")
    drawings:float = Field(example="0.5")
    hentai:float = Field(example="0.5")
    neutral:float = Field(example="0.5")
    porn:float = Field(example="0.5")
    sexy:float = Field(example="0.5")
    
class AccMasterRequest(BaseModel):
    portfolio:str=Field(example="Infosys")
    account:str=Field(example="IMPACT")
    # ptrnList:list=["1689056135.081849","1689056135.4666474"]  adding
    # ThresholdScore:float=Field(example=1.1)
    # dataGrpList:list=["1689072254.362946"]
    # safetyRequest:list[AccSafetyRequest] 

class PrivacyParameterRequest(BaseModel):
    portfolio:str=Field(example="Infosys")
    account:str=Field(example="IMPACT")
    # ptrnList:list=["1689056135.081849","1689056135.4666474"]  adding
    # ThresholdScore:float=Field(example=1.1)
    dataGrpList:list=["1689072254.362946"]
    # safetyRequest:list[AccSafetyRequest] 

class AccMasterUpdate(BaseModel):
    ptrnRecId:float=Field(example=1689056116.3704095)
    ptrnName:str=Field(example="AADHAAR NUMBWR")
    ptrn:str=Field(example=r"[2-9]{1}[0-9]{3}\s{1}[0-9]{4}\s{1}[0-9]{4}")
    ptrnEntity:str=Field(example="AADHAAR_NUMBER")

class AccMasterDelete(BaseModel):
    accMasterId:float=Field(example=1689056116.3704095)
    
class AccDataDelete(BaseModel):
    RecogId:float=Field(example=134.234)
    accMasterId:float=Field(example=1689056116.3704095)
    #Acc Data Delete Bugfix
    
class AccMasterStatus(BaseModel):
    status:str=Field(example="success")
    class Config:
        orm_mode = True
    
class AccData(BaseModel):
    accMasterId:float=Field(example=120.1234)
    portfolio:str=Field(example="INFOSYS")
    account:str=Field(example="IMPACT")
    isActive:str=Field(example="Yes")
    ThresholdScore:float=Field(example=0.85)
    isCreated:str=Field(example="Not Started")
    CreatedDateTime:datetime=Field(example='2023-06-07T10:56:15.657+00:00')
    LastUpdatedDateTime:datetime=Field(example='2023-06-07T10:56:15.657+00:00')
    
class AccMasterResponse(BaseModel):
    accList: List[AccData]

    class Config:
        orm_mode = True
        
class AccPtrnDataRequest(BaseModel):
    accMasterId:float=Field(example=120.1234)
    
# class PtrnEntity(BaseModel):
#     ptrnRecId:float=Field(example=120.1234)
#     ptrnName:str=Field(example="AADHAAR NUmber")
#     dataPtrn:str=Field(example="[2-9]{1}[0-9]{3}\s{1}[0-9]{4}\s{1}[0-9]{4}")
#     supported_entity:str=Field(example="AADHAAR_NUMBER")
#     isActive:str=Field(example="Yes")
#     isCreated:str=Field(example="Not Started")
#     CreatedDateTime:datetime=Field(example='2023-06-07T10:56:15.657+00:00')
#     LastUpdatedDateTime:datetime=Field(example='2023-06-07T10:56:15.657+00:00')
    
# class AccPtrnResponse(BaseModel):
#     accMasterId:float=Field(example=123.1234)
#     PtrnList:List[PtrnEntity]
#     class Config:
#         orm_mode = True
    
class DataAdd(BaseModel):
    dataGrpList:list=[1689072254.362946]
    accMasterId:float=Field(example=120.1234)

class DataGrpEntity(BaseModel):
    RecogId:float=Field(example=120.1234)
    RecogName:str=Field(example="AADHAAR NUmber")
    supported_entity:str=Field(example="AADHAAR_NUMBER")
    RecogType:str=Field(example="Data")
    isActive:str=Field(example="Yes")
    isHashify:bool=Field(example=False)
    isCreated:str=Field(example="Not Started")
    CreatedDateTime:datetime=Field(example='2023-06-07T10:56:15.657+00:00')
    LastUpdatedDateTime:datetime=Field(example='2023-06-07T10:56:15.657+00:00')
    
class AccDataResponse(BaseModel):
    accMasterId:float=Field(example=123.1234)
    dataList:List[DataGrpEntity]
    class Config:
        orm_mode = True
        
class AccSafetyResponse(BaseModel):
    accMasterId:float=Field(example=123.1234)
    dataList:List[AccSafetyRequest]


class AccEncryptionRequest(BaseModel):
    accMasterId:float=Field(example=123.1234)
    dataRecogGrpId:float=Field(example=123.1234)
    isHashify:bool=Field(example=True)


class AccThresholdScoreRequest(BaseModel):
    accMasterId:float=Field(example=123.1234)
    thresholdScore:float = Field(example=0.85)


class AccThresholdScoreResponse(BaseModel):
    status:str=Field(example="success")
    class Config:
        orm_mode = True


class ConfigApi(BaseModel):
    ApiName:str=Field(example="Privacy")
    ApiIp:str=Field(example="http://0.0.0.0")
    ApiPort:Optional[str]=Field(example="12")
    
class ConfigApiUpdate(BaseModel):
    ApiName:str=Field(example="Privacy")
    ApiIp:Optional[str]=Field(example="http://0.0.0.0")
    ApiPort:Optional[str]=Field(example="12")

class ConfigApiDelete(BaseModel):
    ApiName:str=Field(example="Privacy")
    # ApiIp:str=Field(example="http://0.0.0.0")
    # ApiPort:Optional[str]=Field(example="12")
    
    
class ConfigApiResponse(BaseModel):
    result:dict={}
    class Config:
        orm_mode = True


class OpenAIRequest(BaseModel):
    isOpenAI:bool=Field(example="true")
    role:str=Field(example="User")

class ReminderRequest(BaseModel):
    role:str=Field(example="User")
    selfReminder:bool=Field(example="true")

class GoalPriority(BaseModel):
    role:str=Field(example="User")
    goalPriority:bool=Field(example="true")



class OpenAIResponse(BaseModel):
    # status:str=Field(example="success")
    isOpenAI:str=Field(example="true")
    selfReminder:str=Field(example="true")
    goalPriority:str=Field(example="true")
    role:str=Field(example="User")
    class Config:
        orm_mode = True




class OpenAIStatus(BaseModel):
    result:list=[]
    class Config:
        orm_mode = True


class Authority(BaseModel):
    name:str=Field(example="role_admin")

class AuthorityResponse(BaseModel):
    result:List[Authority]

    class Config:
        orm_mode = True


class OpenAiRoleRequest(BaseModel):
    role:str=Field(example="ROLE_ADMIN")

class OpenAIRoleResponse(BaseModel):
    isOpenAI:str=Field(example="true")
    selfReminder:str=Field(example="true")
    goalPriority:str=Field(example="true")
    class Config:
        orm_mode = True




    
    
        
# http://10.79.233.142:8080/api/v1/privacy/pii/admin/ptrnRecognise
# http://10.79.233.142:8080/api/v1/privacy/pii/admin/ptrnRecogniselist