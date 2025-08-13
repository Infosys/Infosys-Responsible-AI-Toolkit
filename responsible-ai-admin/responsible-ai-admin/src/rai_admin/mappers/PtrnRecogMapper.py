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

class PtrnRecogRequest(BaseModel):
    ptrnName:str=Field(example="AADHAAR NUmber")
    ptrn:str=Field(example="[2-9]{1}[0-9]{3}\s{1}[0-9]{4}\s{1}[0-9]{4}")
    ptrnEntity:str=Field(example="AADHAAR_NUMBER")
    

class PtrnRecogUpdate(BaseModel):
    ptrnRecId:float=Field(example=1689056116.3704095)
    ptrnName:str=Field(example="AADHAAR NUMBWR")
    ptrn:str=Field(example="[2-9]{1}[0-9]{3}\s{1}[0-9]{4}\s{1}[0-9]{4}")
    ptrnEntity:str=Field(example="AADHAAR_NUMBER")

class PtrnRecogDelete(BaseModel):
    ptrnRecId:float=Field(example=1689056116.3704095)
    

    
class PtrnRecogStatus(BaseModel):
    status:str=Field(example="success")
    class Config:
        orm_mode = True
    
class PtrnEntity(BaseModel):
    ptrnRecId:float=Field(example=120.1234)
    ptrnName:str=Field(example="AADHAAR NUmber")
    dataPtrn:str=Field(example="[2-9]{1}[0-9]{3}\s{1}[0-9]{4}\s{1}[0-9]{4}")
    supported_entity:str=Field(example="AADHAAR_NUMBER")
    isActive:str=Field(example="Yes")
    isCreated:str=Field(example="Not Started")
    CreatedDateTime:datetime=Field(example='2023-06-07T10:56:15.657+00:00')
    LastUpdatedDateTime:datetime=Field(example='2023-06-07T10:56:15.657+00:00')
    
class PtrnRecogResponse(BaseModel):
    PtrnList: List[PtrnEntity]

    class Config:
        orm_mode = True
        
# http://10.79.233.142:8080/api/v1/privacy/pii/admin/ptrnRecognise
# http://10.79.233.142:8080/api/v1/privacy/pii/admin/ptrnRecogniselist