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
# Constants for commonly used example strings
EXAMPLE_SSN_TEXT = "Ray William's SSN is 012884567"
EXAMPLE_NLP_OPTIONS = "basic/good/roberta/ranha"
EXAMPLE_NLP_DESCRIPTION = "basic,good,better"

"""
description: piiEntity
params:
"""


class PIIEntity(BaseModel):
    type: Optional[str] = Field(example="USA_SSN")
    beginOffset: Optional[int] = Field(example=19)
    endOffset: Optional[int] = Field(example=28)
    score:Optional[float]=Field(example=1)  
    responseText:Optional[str]=Field(example="012884567")

    class Config:
        orm_mode = True

class PIIItems(BaseModel):
    start: Optional[int] = Field(example=19)
    end: Optional[int] = Field(example=28)
    entity_type: Optional[str] = Field(example="USA_SSN") 
    text:Optional[str]=Field(example=EXAMPLE_SSN_TEXT)
    operator:Optional[str]= Field(example="encrypt") 

    class Config:
        orm_mode = True
class PIIEntityImages(BaseModel):
    type: Optional[str] = Field(example="USA_SSN")
    beginOffset: Optional[int] = Field(example=19)
    endOffset: Optional[int] = Field(example=28)
    score:Optional[float]=Field(example=1)  

    class Config:
        orm_mode = True

class PIIImageEntity(BaseModel):
    type: str = Field(example="USA_SSN")

    class Config:
        orm_mode = True

class PIIAnalyzeRequest(BaseModel):
    input_text: str = Field(example=EXAMPLE_SSN_TEXT)
    nlp: Optional[str] = Field(default=None,example=EXAMPLE_NLP_OPTIONS,description=EXAMPLE_NLP_DESCRIPTION)
    portfolio:Optional[str] = Field(default=None)
    account:Optional[str] = Field(default=None)
    pii_entities_to_be_redacted: Optional[list] = Field(default=None)
    exclusion_list:Optional[str] = Field(default=None)
    user: Optional[str] = Field(default=None)
    lotNumber:Optional[str] =Field(default=None)
    score_threshold:Optional[float] = Field(default=float(0.7))
    
class PIIEncryptResponse(BaseModel):
    text: str = Field(example=EXAMPLE_SSN_TEXT)
    items: List[PIIItems]

    class Config:
        orm_mode = True

class PIIDecryptRequest(BaseModel):
    text: str = Field(example=EXAMPLE_SSN_TEXT)
    items: List[PIIItems]

class PIIAnalyzeResponse(BaseModel):
    PIIEntities: List[PIIEntity]

    class Config:
        orm_mode = True


class PIIAnonymizeRequest(BaseModel):
    input_text: str = Field(example=EXAMPLE_SSN_TEXT)
    nlp: Optional[str] = Field(default=None,example=EXAMPLE_NLP_OPTIONS,description=EXAMPLE_NLP_DESCRIPTION)
    portfolio:Optional[str] =Field(default=None)
    account:Optional[str] =Field(default=None)
    exclusion_list:Optional[str] = Field(default=None)
    pii_entities_to_be_redacted: Optional[list] = Field(default=None)
    redactionType: Optional[str] = Field(default=None)
    user: Optional[str] = Field(default=None)
    lotNumber:Optional[str] = Field(default=None)
    fakeData: Optional[bool] = Field(default= False)
    score_threshold:Optional[float] = Field(default=float(0.7))



class PIIAnonymizeResponse(BaseModel):
    anonymizedText: str = Field(example="Ray William's SSN is <USA_SSN>")

    class Config:
        orm_mode = True
        
class PIIDecryptResponse(BaseModel):
    decryptedText: str = Field(example="Ray William's SSN is <USA_SSN>")

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
    type: str = Field(example="USA_SSN")
    start:int = Field(example=19)
    end: int = Field(example=28)
    score: float=Field(example=1)

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
    input_text: str = Field(example=EXAMPLE_SSN_TEXT)
    # entity_type: Optional[str] = Field(example="COMPANY_NAME")
    portfolio:Optional[str] =Field(default=None)
    account:Optional[str] =Field(default=None)

    



class PrivacyShield(BaseModel):
    entitiesRecognised:list = Field(example=["USA_SSN"])
    entitiesConfigured :list = Field(example=["USA_SSN"])
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
    input_text: str = Field(example=EXAMPLE_SSN_TEXT)
