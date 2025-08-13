"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from typing import List
from pydantic import BaseModel, Field
from datetime import datetime

class NewUserRequest(BaseModel):
    email:str = Field(example="abc@infosys.com")
    login:str=Field(example="abc")
    cred:str=Field(example="Abc@123")
    langKey:str=Field(example="en")

class NewAuthRequest(BaseModel):
    username:str=Field(example="abc@infosys.com")
    cred:str=Field(example="Abc@123")
    rememberMe:bool=Field(example=True)

class UpdateUserRequest(BaseModel):
    activated:bool=Field(example=True)
    authorities:list=Field(example=["ROLE_ML"])
    id:int= Field(example=3)
   

class UserData(BaseModel):
    activated:bool=Field(example=True)
    authorities:List=Field(example=["ROLE_ML"])
    createdBy:str=Field(example="system")
    createdDate:datetime=Field(example='2023-06-07T10:56:15.657+00:00')
    firstName:str=Field(example="abc@infosys.com")
    id:int= Field(example=3)
    lastModifiedBy:str=Field(example="system")
    lastModifiedDate:datetime=Field(example='2023-06-07T10:56:15.657+00:00')
    login:str=Field(example="abc")

class UserDataResponse(BaseModel):
    userList: List[UserData]
    class Config:
        orm_mode = True

class flagCreation(BaseModel):
    Module:str = Field(example="RaiBackend")
    TelemetryFlag:bool = Field(example=False)

class getData(BaseModel):
    Module:str = Field(example="RaiBackend")
    TelemetryFlag:bool = Field(example=False)
    CreatedDateTime:datetime=Field(example='2023-06-07T10:56:15.657+00:00')
    LastUpdatedDateTime:datetime=Field(example='2023-06-07T10:56:15.657+00:00')

    
class CreationStatus(BaseModel):
    status:str=Field(example="success")
    class Config:
        orm_mode = True
class AllDataResponse(BaseModel):
    DataList: List[getData]
    class Config:
        orm_mode = True
class flagUpdate(BaseModel):
    Module:str = Field(example="RaiBackend")
    TelemetryFlag:bool = Field(example=False)

class newRoleUpdRqst(BaseModel):
    loginName: str = Field(example="abc")
    role: list = Field(example = ["ROLE_ADMIN","ROLE_USER"])

class newRoleCreate(BaseModel):
    role:str = Field(example="ROLE_ML")

class UserConsentCreate(BaseModel):
    userId: str = Field(example="abc")
    userConsentStatus: bool