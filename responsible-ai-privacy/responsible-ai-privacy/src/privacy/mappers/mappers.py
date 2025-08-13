'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""
fileName: mappers.py
description: A Pydantic model object for usecase entity model
             which maps the data model to the usecase entity schema
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional,Union, List

"""
description: piiEntity
params:
"""


class PIIEntity(BaseModel):
    type: Optional[str] = Field(example="US_SSN")
    beginOffset: Optional[int] = Field(example=19)
    endOffset: Optional[int] = Field(example=28)
    score:Optional[float]=Field(example=1.1)  
    responseText:Optional[str]=Field(example="012884567")

    class Config:
        orm_mode = True

class PIIItems(BaseModel):
    start: Optional[int] = Field(example=19)
    end: Optional[int] = Field(example=28)
    entity_type: Optional[str] = Field(example="US_SSN") 
    text:Optional[str]=Field(example="John Smith's SSN is 012884567")
    operator:Optional[str]= Field(example="encrypt") 

    class Config:
        orm_mode = True

class PIIImageEntity(BaseModel):
    type: str = Field(example="US_SSN")

    class Config:
        orm_mode = True

class PIIAnalyzeRequest(BaseModel):
    inputText: str = Field(example="John Smith's SSN is 012884567")
    nlp: Optional[str] = Field(default=None,example="basic/good/roberta/ranha",description="basic,good,better")
    # entity_type: Optional[str] = Field(example="COMPANY_NAME")
    # portfolio:Optional[str] = Field(example="string")
    # account:Optional[str] = Field(example="string")
    # piiEntitiesToBeRedacted: Optional[list] = Field(example=["US_SSN"])
    # exclusionList:Optional[str] = Field(example="Karan,Infosys")
    # user: Optional[str] = Field(None)
    # lotNumber:Optional[str] = Field(None)
    portfolio:Optional[str] = Field(default=None)
    account:Optional[str] = Field(default=None)
    piiEntitiesToBeRedacted: Optional[list] = Field(default=None)
    exclusionList:Optional[str] = Field(default=None)
    user: Optional[str] = Field(default=None)
    lotNumber:Optional[str] =Field(default=None)
    
class PIIEncryptResponse(BaseModel):
    text: str = Field(example="John Smith's SSN is 012884567")
    items: List[PIIItems]

    class Config:
        orm_mode = True

class PIIDecryptRequest(BaseModel):
    text: str = Field(example="John Smith's SSN is 012884567")
    items: List[PIIItems]

class PIIAnalyzeResponse(BaseModel):
    PIIEntities: List[PIIEntity]

    class Config:
        orm_mode = True


class PIIAnonymizeRequest(BaseModel):
    inputText: str = Field(example="John Smith's SSN is 012884567")
    nlp: Optional[str] = Field(default=None,example="basic/good/roberta/ranha",description="basic,good,better")
    portfolio:Optional[str] =Field(default=None)
    account:Optional[str] =Field(default=None)
    exclusionList:Optional[str] = Field(default=None)
    piiEntitiesToBeRedacted: Optional[list] = Field(default=None)
    redactionType: Optional[str] = Field(default=None)
    user: Optional[str] = Field(default=None)
    lotNumber:Optional[str] = Field(default=None)
    fakeData: Optional[bool] = Field(example = False)



class PIIAnonymizeResponse(BaseModel):
    anonymizedText: str = Field(example="John Smith's SSN is <US_SSN>")

    class Config:
        orm_mode = True
        
class PIIDecryptResponse(BaseModel):
    decryptedText: str = Field(example="John Smith's SSN is <US_SSN>")

    class Config:
        orm_mode = True   
    
#class Image
class PIIImageAnalyzeRequest(BaseModel):
    class Config:
        orm_mode = True

class PIIImageAnonymizeResponse(BaseModel):
    base64text: str=Field(example="kshdbfbfwbedhbaskjbakbsakjnalhbsfsfvslkjdnlkjdsnkdsbflkjsbdsklakbkdb")

    class Config:
        orm_mode = True

class PIIImageAnalyze(BaseModel):
    type: str = Field(example="US_SSN")
    start:int = Field(example=19)
    end: int = Field(example=28)
    score: float=Field(example=1.1)

    class Config:
        orm_mode = True

class PIIImageAnalyzeResponse(BaseModel):
    PIIEntities: List[PIIImageAnalyze]

    class Config:
        orm_mode = True

class PIIMultipleImageAnalyzeResponse(BaseModel):
    PIIEntities: List[List[PIIImageEntity]]

    class Config:
        orm_mode = True



class PIIPrivacyShieldRequest(BaseModel):
    inputText: str = Field(example="John Smith's SSN is 012884567")
    # entity_type: Optional[str] = Field(example="COMPANY_NAME")
    portfolio:Optional[str] =Field(default=None)
    account:Optional[str] =Field(default=None)

    



class PrivacyShield(BaseModel):
    entitiesRecognised:list = Field(example=["US_SSN"])
    entitiesConfigured :list = Field(example=["US_SSN"])
    result:str =""

class PIIPrivacyShieldResponse(BaseModel):
    privacyCheck: List[PrivacyShield]

    class Config:
        orm_mode = True



class LogoHidingResponse(BaseModel):
    base64text: str=Field(example="kshdbfbfwbedhbaskjbakbsakjnalhbsfsfvslkjdnlkjdsnkdsbflkjsbdsklakbkdb")

    class Config:
        orm_mode = True

class Telemetry(BaseModel):
    Module:str= Field(example = "Privacy")
    TelemetryFlagValue : bool = Field(example=True) 
  

class TelemetryResponse(BaseModel):
    result : List[Telemetry]

    class Config:
        orm_mode = True
    
class PIICodeDetectRequest(BaseModel):
    inputText: str = Field(example="John Smith's SSN is 012884567")
