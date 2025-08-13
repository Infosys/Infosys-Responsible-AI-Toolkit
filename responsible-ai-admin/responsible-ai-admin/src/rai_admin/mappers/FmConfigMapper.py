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


class FMConfigEntry(BaseModel):
    status:str= Field(example= "success")
    class Config:
        orm_mode = True

class ToxicityThreshold(BaseModel):
    ToxicityThreshold:float=Field(example=0.6)
    SevereToxicityThreshold:float=Field(example=0.6)
    ObsceneThreshold:float=Field(example=0.6)
    ThreatThreshold:float=Field(example=0.6)
    InsultThreshold:float=Field(example=0.6)
    IdentityAttackThreshold:float=Field(example=0.6)
    SexualExplicitThreshold:float=Field(example=0.6)

class RestrictedtopicDetail(BaseModel):
    RestrictedtopicThreshold:float = Field(example=0.7)
    Restrictedtopics:List = [
        "Terrorism",
        "Explosives"
      ]
class CustomThemeDetail(BaseModel):
    Themename:str = Field(example="String")
    Themethresold:float = Field(example=0.6)
    ThemeTexts:List = [
        "Text1",
        "Text2",
        "Text3"
      ]

class InvisibleTextCountDetail(BaseModel):
    InvisibleTextCountThreshold: int = Field(example=1)
    BannedCategories: List[str] = [
        "Cf",
        "Co",
        "Cn",
        "So",
        "Sc"
    ]

class GibberishDetail(BaseModel):
    GibberishThreshold: float = Field(example=0.7)
    GibberishLabels: List[str] = [
        "word salad",
        "noise",
        "mild gibberish",
        "clean"
    ]


class ModerationCheckThreshold(BaseModel):
    PromptinjectionThreshold:float=Field(example=0.7)
    JailbreakThreshold:float=Field(example=0.7)
    PiientitiesConfiguredToDetect: List =  [
      "PERSON",
      "LOCATION",
      "DATE",
      "AU_ABN",
      "AU_ACN",
      "AADHAR_NUMBER",
      "AU_MEDICARE",
      "AU_TFN",
      "CREDIT_CARD",
      "CRYPTO",
      "DATE_TIME",
      "EMAIL_ADDRESS",
      "ES_NIF",
      "IBAN_CODE",
      "IP_ADDRESS",
      "IT_DRIVER_LICENSE",
      "IT_FISCAL_CODE",
      "IT_IDENTITY_CARD",
      "IT_PASSPORT",
      "IT_VAT_CODE",
      "MEDICAL_LICENSE",
      "PAN_Number",
      "PHONE_NUMBER",
      "SG_NRIC_FIN",
      "UK_NHS",
      "URL",
      "PASSPORT",
      "US_ITIN",
      "US_PASSPORT",
      "US_SSN"
    ]
    PiientitiesConfiguredToBlock:List = [
      "AADHAR_NUMBER",
      "PAN_Number"
    ]
    RefusalThreshold:float= Field(example=0.7)
    ToxicityThresholds: Union[ToxicityThreshold,None] = None
    ProfanityCountThreshold:float= Field(example=1)
    RestrictedtopicDetails: Union[RestrictedtopicDetail,None] = None
    CustomTheme: Union[CustomThemeDetail,None] = None
    SentimentThreshold: float = Field(example=-0.01)
    InvisibleTextCountDetails: Union[InvisibleTextCountDetail, None] = None
    GibberishDetails: Union[GibberishDetail, None] = None
    BanCodeThreshold: float = Field(example=0.7)


class FMConfigRequest(BaseModel):
    AccountName:str=Field(example="Infosys")
    PortfolioName:str=Field(example="IMPACT")
    ModerationChecks:List=["PromptInjection","JailBreak","Piidetct","Refusal","Profanity","RestrictTopic","TextQuality","CustomizedTheme",        "Sentiment",
        "InvisibleText",
        "Gibberish",
        "BanCode"]
    ModerationCheckThresholds: Union[ModerationCheckThreshold,None] = None
    
class fmAccountData(BaseModel):
    accMasterId:float=Field(example=120.1234)
    PortfolioName:str=Field(example="INFOSYS")
    AccountName:str=Field(example="IMPACT")

class FmConfigResponse(BaseModel):
    fmList: List[fmAccountData]
    class Config:
        orm_mode = True
class FMGrpData(BaseModel):
    accMasterId:float=Field(example=123.1234)
    ModerationChecks:List=["PromptInjection","JailBreak","Piidetct","Refusal","Profanity","RestrictTopic","TextQuality","CustomizedTheme",        "Sentiment",
        "InvisibleText",
        "Gibberish",
        "BanCode"]
    ModerationCheckThresholds: Union[ModerationCheckThreshold,None] = None



class FmAccDataResponse(BaseModel):
    
    dataList:List[FMGrpData]
    class Config:
        orm_mode = True

class FmConfigUpdateStatus(BaseModel):
    status:str=Field(example="success")
    class Config:
        orm_mode = True
from datetime import datetime
from typing import Optional, Union, List


class FMConfigEntry(BaseModel):
    status:str= Field(example= "success")
    class Config:
        orm_mode = True

class ToxicityThreshold(BaseModel):
    ToxicityThreshold:float=Field(example=0.6)
    SevereToxicityThreshold:float=Field(example=0.6)
    ObsceneThreshold:float=Field(example=0.6)
    ThreatThreshold:float=Field(example=0.6)
    InsultThreshold:float=Field(example=0.6)
    IdentityAttackThreshold:float=Field(example=0.6)
    SexualExplicitThreshold:float=Field(example=0.6)

class RestrictedtopicDetail(BaseModel):
    RestrictedtopicThreshold:float = Field(example=0.7)
    Restrictedtopics:List = [
        "terrorism",
        "explosives"
      ]
class CustomThemeDetail(BaseModel):
    Themename:str = Field(example="String")
    Themethresold:float = Field(example=0.6)
    ThemeTexts:List = [
        "Text1",
        "Text2",
        "Text3"
      ]


# class ModerationCheckThreshold(BaseModel):
#     PromptinjectionThreshold:float=Field(example=0.7)
#     JailbreakThreshold:float=Field(example=0.7)
#     PiientitiesConfiguredToDetect: List =  [
#       "PERSON",
#       "LOCATION",
#       "DATE",
#       "AU_ABN",
#       "AU_ACN",
#       "AADHAR_NUMBER",
#       "AU_MEDICARE",
#       "AU_TFN",
#       "CREDIT_CARD",
#       "CRYPTO",
#       "DATE_TIME",
#       "EMAIL_ADDRESS",
#       "ES_NIF",
#       "IBAN_CODE",
#       "IP_ADDRESS",
#       "IT_DRIVER_LICENSE",
#       "IT_FISCAL_CODE",
#       "IT_IDENTITY_CARD",
#       "IT_PASSPORT",
#       "IT_VAT_CODE",
#       "MEDICAL_LICENSE",
#       "PAN_Number",
#       "PHONE_NUMBER",
#       "SG_NRIC_FIN",
#       "UK_NHS",
#       "URL",
#       "PASSPORT",
#       "US_ITIN",
#       "US_PASSPORT",
#       "US_SSN"
#     ]
#     PiientitiesConfiguredToBlock:List = [
#       "AADHAR_NUMBER",
#       "PAN_Number"
#     ]
#     RefusalThreshold:float= Field(example=0.7)
#     ToxicityThresholds: Union[ToxicityThreshold,None] = None
#     ProfanityCountThreshold:float= Field(example=1)
#     RestrictedtopicDetails: Union[RestrictedtopicDetail,None] = None
#     CustomTheme: Union[CustomThemeDetail,None] = None
#     SentimentThreshold: float = Field(example=-0.01)
#     InvisibleTextCountDetails: Union[InvisibleTextCountDetail, None] = None
#     GibberishDetails: Union[GibberishDetail, None] = None
#     BanCodeThreshold: float = Field(example=0.7)


class FMConfigRequest(BaseModel):
    AccountName:str=Field(example="IMPACT")
    PortfolioName:str=Field(example="Infosys")
    ModerationChecks:list=["PromptInjection","JailBreak"]
    OutputModerationChecks:list=["Toxicity","Piidetct","Refusal"]
    ModerationCheckThresholds: Union[ModerationCheckThreshold,None] = None
    
class fmAccountData(BaseModel):
    accMasterId:float=Field(example=120.1234)
    portfolio:str=Field(example="INFOSYS")
    account:str=Field(example="IMPACT")

class FmConfigResponse(BaseModel):
    fmList: List[fmAccountData]
    class Config:
        orm_mode = True

class FMGrpData(BaseModel):
    accMasterId:float=Field(example=1703579888.137873)
    ModerationChecks:list= ["PromptInjection","JailBreak","Piidetct"]
    OutputModerationChecks:list=["Toxicity","Piidetct","Refusal"]
    ModerationCheckThresholds: Union[ModerationCheckThreshold,None] = None
    



class FmAccDataResponse(BaseModel):    
     dataList: List[FMGrpData]
     class Config:
        orm_mode = True

class FmConfigUpdateStatus(BaseModel):
    status:str=Field(example="success")
    class Config:
        orm_mode = True
class FmConfigDelete(BaseModel):
    accMasterId:float=Field(example=1689056116.3704095)


class ModerationCheckResponse(BaseModel):    
    dataList: List[str]
    
class AccPortRequest(BaseModel):
    AccountName:str=Field(example="IMPACT")
    PortfolioName:str=Field(example="Infosys")


