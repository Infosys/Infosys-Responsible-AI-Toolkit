'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from pydantic import BaseModel, Field,Extra
from typing import Optional, Union, List
from enum import Enum

class PiiEntitiesforPopup(BaseModel):
    EntityType: str = Field(example="US_SSN")
    beginOffset: int = Field(example=19)
    endOffset: int = Field(example=28)
    value: str =Field(example = "Karan")

class PrivacyPopup(BaseModel):
    entitiesToDetect:list = Field(example=["US_SSN"])
    entitiesToBlock :list = Field(example=["US_SSN"])
    entitiesRecognized :list[PiiEntitiesforPopup]
    result:str =Field(example="Passsed")

class PrivacyPopupResponse(BaseModel):
    privacyCheck: List[PrivacyPopup]

    class Config:
        orm_mode = True


class completionRequest(BaseModel):
    prompt: str = Field(example="Which is the biggest country in the world?")
    temperature: str = Field(example="0")
    LLMinteraction: str = Field(example="yes")
    #LLMmodel:str = Field(example="Llama or Openai or Bloom")
    SelfReminder :bool =Field(example=True)

    class Config:
        orm_mode = True
class toxicityPopupRequest(BaseModel):
    text: str = Field(example="Which is the biggest country in the world?")

class Choice(BaseModel):
    text:str= Field(example="Russia is the biggest country by area.")
    index:int=Field(example=0)
    finishReason:str=Field(example="length")

    class Config:
        orm_mode = True

class Result(str, Enum):
    PASSED = 'PASSED'
    FAILED = 'FAILED'
    UNMODERATED  = 'UNMODERATED'

    class Config:
        orm_mode = True

class promptInjectionCheck(BaseModel):
    injectionConfidenceScore:str = Field(example="0.98")
    injectionThreshold:str = Field(example="0.70")
    result:Result=Field(example="PASSED")

    class Config:
        orm_mode = True

class jailbreakCheck(BaseModel):
    jailbreakSimilarityScore:str =Field(example="0.82")
    jailbreakThreshold:str =Field(example="0.6")
    result:Result =Field(example="PASSED")

    class Config:
        orm_mode = True

class refusalCheck(BaseModel):
    refusalSimilarityScore:str =Field(example="0.82")
    RefusalThreshold:str =Field(example="0.6")
    result:Result =Field(example="PASSED")

    class Config:
        orm_mode = True
        
class textRelevanceCheck(BaseModel):
    PromptResponseSimilarityScore:str =Field(example="0.82")

class privacyCheck(BaseModel):
    entitiesRecognised:List = Field(example=['LOCATION'])
    entitiesConfiguredToBlock:List = Field(example=['ADHAR_NUMBER'])
    result:Result =Field(example="PASSED")

    class Config:
        orm_mode = True

class metricScore(BaseModel):
    metricName:str =Field(example="toxicity")
    metricScore:float =Field(example=0.0006679997895844281)

class ToxicScore(BaseModel):
    toxicScore:List[metricScore] = Field(example=[{
                                "metricName": "toxicity",
                                "metricScore": 0.0006679997895844281
                            },
                            {
                                "metricName": "severe_toxicity",
                                "metricScore": 1.3805756680085324e-06
                            },
                            {
                                "metricName": "obscene",
                                "metricScore": 3.030665720871184e-05
                            },
                            {
                                "metricName": "threat",
                                "metricScore": 2.1546358766499907e-05
                            },
                            {
                                "metricName": "insult",
                                "metricScore": 0.00013677669630851597
                            },
                            {
                                "metricName": "identity_attack",
                                "metricScore": 0.00017613476666156203
                            },
                            {
                                "metricName": "sexual_explicit",
                                "metricScore": 1.4234438822313678e-05
                            }])
class toxicityCheck(BaseModel):
    toxicityScore: List[ToxicScore]
    toxicitythreshold: str = Field(example="0.55")
    result: Result = Field(example="PASSED")
    toxicityTypesConfiguredToBlock: Optional[List[str]] = Field(
        default=None,
        example=[
            "toxicity",
            "severe_toxicity",
            "obscene",
            "threat",
            "insult",
            "identity_attack",
            "sexual_explicit"
        ]
    )
    toxicityTypesRecognised: Optional[List[str]] = Field(default_factory=list)  # Default to empty list if not provided
    

    class Config:
        orm_mode = True

class profanityCheck(BaseModel):
    profaneWordsIdentified:List = Field(['bullshit'])
    profaneWordsthreshold: str = Field(example="2")
    result:Result =Field(example="PASSED")
    
    class Config:
        orm_mode = True

class summary(BaseModel):
    status: str = Field(example="PASSED")
    reason:List =Field(example=[])
    
    class Config:
        orm_mode = True

class restrictedtopic(BaseModel):
    topicScores: List = Field(example=[{'Explosives': '0.85'}])
    topicThreshold: str = Field(example="0.65")
    result: Result =Field(example="PASSED")
    topicTypesConfiguredToBlock: Optional[List[str]] = Field(example=["Terrorism", "Explosives"])
    topicTypesRecognised: Optional[List[str]] = Field(example=[])

    class Config:
        orm_mode = True
class textQuality(BaseModel):
    readabilityScore : str=Field(example="80")
    textGrade : str=Field(example="Grade 12-13")

class customThemeCheck(BaseModel):
    customSimilarityScore:str =Field(example="0.82")
    themeThreshold:str =Field(example="0.6")
    result:Result =Field(example="PASSED")

class randomNoiseCheck(BaseModel):
    smoothLlmScore:str =Field(example="0.82")
    smoothLlmThreshold:str =Field(example="0.6")
    result:Result =Field(example="PASSED")

class advancedJailbreakCheck(BaseModel):
    text:str =Field(example="NON ADVERSARIAL")
    result:Result =Field(example="PASSED")

class RequestModeration(BaseModel):
    text :str=Field(example="Which is the biggest country in the world?")
    promptInjectionCheck : promptInjectionCheck
    jailbreakCheck  : jailbreakCheck
    privacyCheck : privacyCheck
    profanityCheck : profanityCheck
    toxicityCheck : toxicityCheck
    restrictedtopic : restrictedtopic
    textQuality : textQuality
    refusalCheck : refusalCheck
    customThemeCheck : customThemeCheck
    randomNoiseCheck : randomNoiseCheck
    advancedJailbreakCheck : advancedJailbreakCheck
    summary : summary

    class Config:
        orm_mode = True

class ResponseModeration(BaseModel):
    generatedText:str=Field(example="Russia is the biggest country by area.")
    privacyCheck: privacyCheck
    profanityCheck:profanityCheck
    toxicityCheck : toxicityCheck
    restrictedtopic : restrictedtopic
    textQuality : textQuality
    textRelevanceCheck : textRelevanceCheck
    refusalCheck : refusalCheck
    summary : summary

    class Config:
        orm_mode = True


class ModerationResults(BaseModel):
    requestModeration : RequestModeration
    responseModeration : ResponseModeration

    class Config:
        orm_mode = True
        
# class TimeForCheck(BaseModel):
#     toxicityCheck: str
#     privacyCheck: str
#     promptInjectionCheck: str
#     customthemeCheck: str
#     restrictedtopic: str
#     jailbreakCheck: str

# class TimeTakenByModel(BaseModel):
#     toxicityCheck: str
#     privacyCheck: str
#     promptInjectionCheck: str
#     customthemeCheck: str
#     restrictedtopic: str
#     jailbreakCheck: str


class RequestModerationTime(BaseModel):
    promptInjectionCheck: Optional[str] = None
    jailbreakCheck: Optional[str] = None
    toxicityCheck: Optional[str] = None
    privacyCheck: Optional[str] = None
    profanityCheck: Optional[str] = None
    refusalCheck: Optional[str] = None
    restrictedtopic: Optional[str] = None
    textqualityCheck: Optional[str] = None
    customthemeCheck: Optional[str] = None
    smoothLlmCheck: Optional[str] = None
    bergeronCheck: Optional[str] = None
    
class ResponseModerationTime(BaseModel):
    promptInjectionCheck: Optional[str] = None
    jailbreakCheck: Optional[str] = None
    toxicityCheck: Optional[str] = None
    privacyCheck: Optional[str] = None
    profanityCheck: Optional[str] = None
    refusalCheck: Optional[str] = None
    restrictedtopic: Optional[str] = None
    textqualityCheck: Optional[str] = None
    customthemeCheck: Optional[str] = None
    smoothLlmCheck: Optional[str] = None
    bergeronCheck: Optional[str] = None
    textrelevanceCheck: Optional[str] = None

class ModelTime(BaseModel):
    toxicityCheck: Optional[str] = None
    privacyCheck: Optional[str] = None
    jailbreakCheck: Optional[str] = None
    promptInjectionCheck: Optional[str] = None
    customthemeCheck: Optional[str] = None
    restrictedtopic: Optional[str] = None


class ModerationLayerTime(BaseModel):
    requestModeration: Optional[RequestModerationTime] = None
    responseModeration: Optional[ResponseModerationTime] = None
    OpenAIInteractionTime: Optional[str] = None
    translate: Optional[str] = None
    Time_taken_by_each_model_in_requestModeration: Optional[ModelTime] = None
    Total_time_for_moderation_Check: Optional[str] = None
    Time_taken_by_each_model_in_responseModeration: Optional[ModelTime] = None
    # Time_for_each_individual_check: TimeForCheck = Field(..., alias="Time for each individual check")
    # Time_taken_by_each_model: TimeTakenByModel = Field(..., alias="Time taken by each model")
    # Total_time_for_moderation_Check: str = Field(..., alias="Total time for moderation Check")

class completionResponse(BaseModel):
    uniqueid:str=Field(example= "123e4567-e89b-12d3-a456-426614174000")
    object:str =Field(example="text_completion")
    userid: Optional[str] = Field(example="admin")
    lotNumber: Optional[str] = Field(example="1")
    created:str =Field(example='1646932609')
    model:str= Field(example="openai")
    choices:List[Choice]
    moderationResults: ModerationResults
    portfolioName: str
    accountName: str
    Moderation_layer_time: Optional[ModerationLayerTime] = Field(None, alias="Moderation layer time")

    class Config:
        orm_mode = True