'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from pydantic import BaseModel,Field,Extra
from datetime import date
from typing import List
from datetime import datetime
from enum import Enum
from typing import Optional, Union, List

class Choice(BaseModel):
    text:str= Field(example="Russia is the biggest country by area.")
    index:int=Field(example=0)
    finishReason:str=Field(example="length")


class Result(str, Enum):
    PASSED = 'PASSED'
    FAILED = 'FAILED'
    UNMODERATED  = 'UNMODERATED'


class MODCHECKS(str, Enum):
    PromptInjection = 'PromptInjection'
    JailBreak = 'JailBreak'
    Toxicity  = 'Toxicity'
    Piidetct  = 'Piidetct'
    Refusal  = 'Refusal'
    Profanity  = 'Profanity'
    RestrictTopic  = 'RestrictTopic'
    TextQuality  = 'TextQuality'
    CustomizedTheme = "CustomizedTheme"


class PIICHECKS(str, Enum):
    PERSON = 'PERSON'
    LOCATION = 'LOCATION'
    DATE  = 'DATE'
    AU_ABN  = 'AU_ABN'
    AU_ACN  = 'AU_ACN'
    AADHAR_NUMBER  = 'AADHAR_NUMBER'
    AU_MEDICARE  = 'AU_MEDICARE'
    AU_TFN  = 'AU_TFN'
    CREDIT_CARD = 'CREDIT_CARD'
    CRYPTO = 'CRYPTO'
    DATE_TIME  = 'DATE_TIME'
    EMAIL_ADDRESS  = 'EMAIL_ADDRESS'
    ES_NIF  = 'ES_NIF'
    IBAN_CODE  = 'IBAN_CODE'
    IP_ADDRESS  = 'IP_ADDRESS'
    IT_DRIVER_LICENSE  = 'IT_DRIVER_LICENSE'
    IT_FISCAL_CODE = 'IT_FISCAL_CODE'
    IT_IDENTITY_CARD = 'IT_IDENTITY_CARD'
    IT_PASSPORT  = 'IT_PASSPORT'
    IT_VAT_CODE  = 'IT_VAT_CODE'
    MEDICAL_LICENSE  = 'MEDICAL_LICENSE'
    PAN_Number  = 'PAN_Number'
    PHONE_NUMBER  = 'PHONE_NUMBER'
    SG_NRIC_FIN  = 'SG_NRIC_FIN'
    UK_NHS  = 'UK_NHS'
    URL  = 'URL'
    PASSPORT  = 'PASSPORT'
    US_ITIN  = 'US_ITIN'
    US_PASSPORT  = 'US_PASSPORT'
    US_SSN  = 'US_SSN'


class promptInjectionCheck(BaseModel):
    injectionConfidenceScore:str = Field(example="0.98")
    injectionThreshold:str = Field(example="0.70")
    result:Result=Field(example="PASSED")


class jailbreakCheck(BaseModel):
    jailbreakSimilarityScore:str =Field(example="0.82")
    jailbreakThreshold:str =Field(example="0.6")
    result:Result =Field(example="PASSED")


class refusalCheck(BaseModel):
    refusalSimilarityScore:str =Field(example="0.82")
    RefusalThreshold:str =Field(example="0.6")
    result:Result =Field(example="PASSED")

        
class textRelevanceCheck(BaseModel):
    PromptResponseSimilarityScore:str =Field(example="0.82")

class privacyCheck(BaseModel):
    entitiesRecognised:List = Field(example=['PERSON'])
    entitiesConfiguredToBlock:List = Field(example=['ADHAR_NUMBER'])
    result:Result =Field(example="PASSED")


class toxicityCheck(BaseModel):
    toxicityScore:List = Field(example=[{'toxicity': '0.85'}])
    toxicitythreshold: str = Field(example="0.55")
    result:Result =Field(example="PASSED")


class profanityCheck(BaseModel):
    profaneWordsIdentified:List = Field(['bullshit'])
    profaneWordsthreshold: str = Field(example="2")
    result:Result =Field(example="PASSED")
    

class summary(BaseModel):
    status: str = Field(example="REJECTED")
    reason:List =Field(example=["PROMPT-INJECTION", "PRIVACY"])

class restrictedtopic(BaseModel):
    topicScores: List = Field(example=[{'Explosives': '0.85'}])
    topicThreshold: str = Field(example="0.65")
    result: Result =Field(example="PASSED")


class textQuality(BaseModel):
    readabilityScore : str=Field(example="80")
    textGrade : str=Field(example="Grade 12-13")


class customThemeCheck(BaseModel):
    customSimilarityScore:str =Field(example="0.82")
    themeThreshold:str =Field(example="0.6")
    result:Result =Field(example="PASSED")


class RequestModeration(BaseModel):
    text :str = Field(example="Which is the biggest country in the world?")
    promptInjectionCheck : promptInjectionCheck
    jailbreakCheck	: jailbreakCheck
    privacyCheck : privacyCheck
    profanityCheck : profanityCheck
    toxicityCheck : toxicityCheck
    restrictedtopic : restrictedtopic
    textQuality : textQuality
    refusalCheck : refusalCheck
    customThemeCheck : customThemeCheck
    summary : summary

class TimeForCheck(BaseModel):
    Privacy_Check: Optional[str] = Field(None, alias="Privacy Check")
    Text_Quality_Check: Optional[str] = Field(None, alias="Text Quality Check")
    Toxicity_Check: Optional[str] = Field(None, alias="Toxicity Check")
    Profanity_Check: Optional[str] = Field(None, alias="Profanity Check")
    Prompt_Injection_Check: Optional[str] = Field(None, alias="Prompt Injection Check")
    Restricted_Topic_Check: Optional[str] = Field(None, alias="Restricted Topic Check")
    Jailbreak_Check: Optional[str] = Field(None, alias="Jailbreak Check")
    Refusal_Check: Optional[str] = Field(None, alias="Refusal Check")
    Custom_Theme_Check: Optional[str] = Field(None, alias="Custom Theme Check")

class TimeTakenByModel(BaseModel):
    Privacy_Check: Optional[str] = Field(None, alias="Privacy Check")
    Toxicity_Check: Optional[str] = Field(None, alias="Toxicity Check")
    Prompt_Injection_Check: Optional[str] = Field(None, alias="Prompt Injection Check")
    Restricted_Topic_Check: Optional[str] = Field(None, alias="Restricted Topic Check")
    Jailbreak_Check: Optional[str] = Field(None, alias="Jailbreak Check")
    Custom_Theme_Check: Optional[str] = Field(None, alias="Custom Theme Check")

class TimeTakenByAPI(BaseModel):
    Toxicity_Check: Optional[float] = Field(None, alias="Toxicity Check")
    Profanity_Check: Optional[float] = Field(None, alias="Profanity Check")
    Prompt_Injection_Check: Optional[float] = Field(None, alias="Prompt Injection Check")
    Restricted_Topic_Check: Optional[float] = Field(None, alias="Restricted Topic Check")
    Jailbreak_Check: Optional[float] = Field(None, alias="Jailbreak Check")
    Refusal_Check: Optional[float] = Field(None, alias="Refusal Check")
    Custom_Theme_Check: Optional[float] = Field(None, alias="Custom Theme Check")

class ModerationLayerTime(BaseModel):
    Time_for_each_individual_check: Optional[TimeForCheck] = Field(None, alias="Time for each individual check")
    Time_taken_by_each_model: Optional[TimeTakenByModel] = Field(None, alias="Time taken by each model")
    Time_taken_By_API: Optional[TimeTakenByAPI] = Field(None, alias="Time taken By API")
    Total_time_for_moderation_Check: Optional[str] = Field(None, alias="Total time for moderation Check")
    Time_By_Model: Optional[float] = Field(None, alias="Time By Model")
    Latency_By_API: Optional[float] = Field(None, alias="Latency By API")
    Time_By_Validation: Optional[float] = Field(None, alias="Time By Validation")
    Time_Difference_model_and_validity: Optional[float] = Field(None, alias="Time Difference mdoel and validity")
    Time_Difference_between_ML_and_MM: Optional[float] = Field(None, alias="Time Diffrence btwn ML and MM")
class ModerationResults(BaseModel):
    uniqueid:str = Field(example= "123e4567-e89b-12d3-a456-426614174000")
    moderationResults : RequestModeration
    Moderation_layer_time: Optional[ModerationLayerTime] = Field(None, alias="Moderation layer time")
    portfolioName: str
    created: datetime
    accountName: str
    userid: Optional[str]=Field(None)
    lotNumber: Optional[str] = Field(None)


class TOXTHRESHOLDS(BaseModel):
    ToxicityThreshold: float = Field(example=0.60)
    SevereToxicityThreshold: float = Field(example=0.60)
    ObsceneThreshold: float = Field(example=0.60)
    ThreatThreshold: float = Field(example=0.60)
    InsultThreshold: float = Field(example=0.60)
    IdentityAttackThreshold: float = Field(example=0.60)
    SexualExplicitThreshold: float = Field(example=0.60)


class RTTHRESHOLDS(BaseModel):
    RestrictedtopicThreshold: float = Field(example=0.70)
    Restrictedtopics: List = Field(["Terrorism", "Explosives"])


class CustomThemeTexts(BaseModel):
    Themename: str
    Themethresold: float = Field(example=0.60)
    ThemeTexts: List =Field(example=["Text1","Text2","Text3"])


class MODTHRESHOLDS(BaseModel):
    PromptinjectionThreshold: float = Field(example=0.70)
    JailbreakThreshold: float = Field(example=0.70)
    PiientitiesConfiguredToDetect:List[PIICHECKS] = Field(example=['PERSON','LOCATION','DATE','AU_ABN','AU_ACN','AADHAR_NUMBER','AU_MEDICARE','AU_TFN','CREDIT_CARD','CRYPTO','DATE_TIME','EMAIL_ADDRESS','ES_NIF','IBAN_CODE','IP_ADDRESS','IT_DRIVER_LICENSE','IT_FISCAL_CODE','IT_IDENTITY_CARD','IT_PASSPORT','IT_VAT_CODE','MEDICAL_LICENSE','PAN_Number','PHONE_NUMBER','SG_NRIC_FIN','UK_NHS','URL','PASSPORT','US_ITIN','US_PASSPORT','US_SSN'])
    PiientitiesConfiguredToBlock:List[PIICHECKS] = Field(example=["AADHAR_NUMBER","PAN_Number"])
    RefusalThreshold: float = Field(example=0.70)
    ToxicityThresholds: TOXTHRESHOLDS
    ProfanityCountThreshold: int = Field(example=1)
    RestrictedtopicDetails: RTTHRESHOLDS
    CustomTheme: CustomThemeTexts

class completionRequest(BaseModel):
    Prompt: str = Field(example= "Which is the biggest country in the world?")
    ModerationChecks : List[MODCHECKS] = Field(example=['PromptInjection','JailBreak','Toxicity','Piidetct','Refusal','Profanity','RestrictTopic',"TextQuality","CustomizedTheme"])
    ModerationCheckThresholds: MODTHRESHOLDS


    