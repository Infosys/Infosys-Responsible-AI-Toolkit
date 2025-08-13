'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from dataclasses import dataclass
from pydantic import BaseModel, Field,Extra
from typing import Optional, Union, List
from enum import Enum

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
    UNDETERMINED = 'UNDETERMINED'

    class Config:
        orm_mode = True

class MODCHECKS(str, Enum):
    PromptInjection = 'PromptInjection'
    JailBreak = 'JailBreak'
    Toxicity  = 'Toxicity'
    Piidetct  = 'Piidetct'
    Refusal  = 'Refusal'
    Profanity  = 'Profanity'
    RestrictTopic  = 'RestrictTopic'
    TextQuality  = 'TextQuality'
    TextRelevance = "TextRelevance"
    CustomizedTheme = "CustomizedTheme"
    Sentiment = "Sentiment"
    InvisibleText = "InvisibleText"
    Gibberish = "Gibberish"
    BanCode = "BanCode"

    class Config:
        orm_mode = True
        
class llm_Based_Checks(str, Enum):
    smoothLlmCheck = 'smoothLlmCheck'
    bergeronCheck = 'bergeronCheck'
    
    class Config:
        orm_mode = True

class TOXICITYTYPES(str, Enum):
    TOXICITY="toxicity"
    SEVERETOXICITY = "severe_toxicity"
    OBSCENE="obscene"
    THREAT = "threat"
    INSULT = "insult"
    IDENTITYATTACK="identity_attack"
    SEXUALEXPLICIT = "sexual_explicit"
    class Config:
        orm_mode = True
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
    IN_PAN = 'IN_PAN'
    IN_AADHAAR = 'IN_AADHAAR'
    PHONE_NUMBER  = 'PHONE_NUMBER'
    SG_NRIC_FIN  = 'SG_NRIC_FIN'
    UK_NHS  = 'UK_NHS'
    URL  = 'URL'
    PASSPORT  = 'PASSPORT'
    US_ITIN  = 'US_ITIN'
    US_PASSPORT  = 'US_PASSPORT'
    US_SSN  = 'US_SSN'

    class Config:
        orm_mode = True


# class PIICHECKSToBlock(str, Enum):
#     PERSON = 'PERSON'
#     LOCATION = 'LOCATION'
#     DATE  = 'DATE'
#     AU_ABN  = 'AU_ABN'
#     AU_ACN  = 'AU_ACN'
#     AADHAR_NUMBER  = 'AADHAR_NUMBER'
#     AU_MEDICARE  = 'AU_MEDICARE'
#     AU_TFN  = 'AU_TFN'
#     CREDIT_CARD = 'CREDIT_CARD'
#     CRYPTO = 'CRYPTO'
#     DATE_TIME  = 'DATE_TIME'
#     EMAIL_ADDRESS  = 'EMAIL_ADDRESS'
#     ES_NIF  = 'ES_NIF'
#     IBAN_CODE  = 'IBAN_CODE'
#     IP_ADDRESS  = 'IP_ADDRESS'
#     IT_DRIVER_LICENSE  = 'IT_DRIVER_LICENSE'
#     IT_FISCAL_CODE = 'IT_FISCAL_CODE'
#     IT_IDENTITY_CARD = 'IT_IDENTITY_CARD'
#     IT_PASSPORT  = 'IT_PASSPORT'
#     IT_VAT_CODE  = 'IT_VAT_CODE'
#     MEDICAL_LICENSE  = 'MEDICAL_LICENSE'
#     PAN_Number  = 'PAN_Number'
#     PHONE_NUMBER  = 'PHONE_NUMBER'
#     SG_NRIC_FIN  = 'SG_NRIC_FIN'
#     UK_NHS  = 'UK_NHS'
#     URL  = 'URL'
#     PASSPORT  = 'PASSPORT'
#     US_ITIN  = 'US_ITIN'
#     US_PASSPORT  = 'US_PASSPORT'
#     US_SSN  = 'US_SSN'

#     class Config:
#         orm_mode = True

class promptInjectionCheck(BaseModel):
    injectionConfidenceScore:str = Field(example="98")
    injectionThreshold:str = Field(example="60")
    result:Result=Field(example="PASSED")

    class Config:
        orm_mode = True

class sentimentCheck(BaseModel):
    score:str = Field(example="0.85")
    threshold:str = Field(example="0.0")
    result:Result=Field(example="PASSED")
    class Config:
        orm_mode = True

class invisibleTextCheck(BaseModel):
    invisibleTextIdentified:List = Field(['bullshit'])
    threshold:str = Field(example="0.0")
    result:Result=Field(example="PASSED")
    class Config:
        orm_mode = True

class gibberishCheck(BaseModel):
    gibberishScore:List = Field(['bullshit'])
    threshold:str = Field(example="0.0")
    result:Result=Field(example="PASSED")
    class Config:
        orm_mode = True

class bancodeCheck(BaseModel):
    label:str="CODE"
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
    entitiesRecognised:List = Field(example=['PERSON'])
    entitiesConfiguredToBlock:List = Field(example=['ADHAR_NUMBER'])
    result:Result =Field(example="PASSED")

    class Config:
        orm_mode = True

class toxicityCheckTypes(BaseModel):
    toxicityTypesRecognised:List[TOXICITYTYPES] = Field(example=['TOXICITY','OBSCENE'])
    toxicityTypesConfiguredToBlock:List[TOXICITYTYPES] = Field(example=['TOXICITY','OBSCENE'])
    toxicityScore:List = Field(example=[{'toxicity': '0.85'}])
    toxicitythreshold: str = Field(example="0.55")
    result:Result =Field(example="PASSED")
    class Config:
        orm_mode = True
class toxicityCheck(BaseModel):
    toxicityScore:List = Field(example=[{'toxicity': '0.85'}])
    toxicitythreshold: str = Field(example="0.55")
    result:Result =Field(example="PASSED")

    class Config:
        orm_mode = True

class smoothLlmCheck(BaseModel):
    smoothLlmScore: str = Field(example="0.0")
    smoothLlmThreshold: str = Field(example="0.6")
    result:Result =Field(example="PASSED")
    
    class Config:
        orm_mode = True
        
class bergeronCheck(BaseModel):
    text:str= Field(example="SAFE")
    result:Result =Field(example="PASSED")
    
    class Config:
        orm_mode = True

class profanityCheck(BaseModel):
    profaneWordsIdentified:List = Field(['bullshit'])
    profaneWordsthreshold: str = Field(example="2")
    result:Result =Field(example="PASSED")
    
    class Config:
        orm_mode = True

class summary(BaseModel):
    status: str = Field(example="REJECTED")
    reason:List =Field(example=["PROMPT-INJECTION", "PRIVACY"])
    
    class Config:
        orm_mode = True

class restrictedtopic(BaseModel):
    topicScores: List = Field(example=[{'Explosives': '0.85'}])
    topicThreshold: str = Field(example="0.65")
    result: Result =Field(example="PASSED")
    class Config:
        orm_mode = True
class restrictedtopicTypes(BaseModel):
    topicTypesConfiguredToBlock:List=Field(example=['Explosives','Terrorism'])
    topicTypesRecognised:List=Field(example=['Explosives'])
    topicScores: List = Field(example=[{'Explosives': '0.85'}])
    topicThreshold: str = Field(example="0.65")
    result: Result =Field(example="PASSED")

    class Config:
        orm_mode = True

class profanityPopupRequest(BaseModel):
    text: str = Field(example="Which is the biggest country in the world?")

class covRequest(BaseModel):
    text: str = Field(example="Which is the biggest country in the world?")
    complexity : str = Field(enum=["simple", "medium", "complex"])
    model_name: Optional[str] =Field(example="gpt4")
    translate: str = Field(example="no")

class privacyPopupRequest(BaseModel):
    text: str = Field(example="Which is the biggest country in the world?")
    # PiientitiesConfiguredToDetect:List[PIICHECKS] = Field(example=['PERSON','LOCATION','DATE','AU_ABN','AU_ACN','AADHAR_NUMBER','AU_MEDICARE','AU_TFN','CREDIT_CARD','CRYPTO','DATE_TIME','EMAIL_ADDRESS','ES_NIF','IBAN_CODE','IP_ADDRESS','IT_DRIVER_LICENSE','IT_FISCAL_CODE','IT_IDENTITY_CARD','IT_PASSPORT','IT_VAT_CODE','MEDICAL_LICENSE','PAN_Number','PHONE_NUMBER','SG_NRIC_FIN','UK_NHS','URL','PASSPORT','US_ITIN','US_PASSPORT','US_SSN'])
    PiientitiesConfiguredToBlock:List[PIICHECKS] = Field(example=["AADHAR_NUMBER","PAN_Number"])

class textQuality(BaseModel):
    readabilityScore : str=Field(example="80")
    textGrade : str=Field(example="Grade 12-13")

    class Config:
        orm_mode = True

class customThemeCheck(BaseModel):
    customSimilarityScore:str =Field(example="0.82")
    themeThreshold:str =Field(example="0.6")
    result:Result =Field(example="PASSED")

    class Config:
        orm_mode = True

class PiiEntitiesforPopup(BaseModel):
    EntityType: str = Field(example="US_SSN")
    beginOffset: int = Field(example=19)
    endOffset: int = Field(example=28)
    value: str =Field(example = "Karan")

# @dataclass
class PrivacyPopup(BaseModel):
    entitiesToDetect:list = Field(example=["US_SSN"])
    entitiesToBlock :list = Field(example=["US_SSN"])
    entitiesRecognized :list[PiiEntitiesforPopup]
    result:str =Field(example="Passsed")

class PrivacyPopupResponse(BaseModel):
    privacyCheck: List[PrivacyPopup]

    class Config:
        orm_mode = True

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
    # textRelevance : textRelevanceCheck
    customThemeCheck : customThemeCheck
    sentimentCheck : sentimentCheck
    invisibleTextCheck : invisibleTextCheck
    gibberishCheck : gibberishCheck
    bancodeCheck : bancodeCheck
    summary : summary

    class Config:
        orm_mode = True

class CoupledRequestModeration(BaseModel):
    text :str = Field(example="Which is the biggest country in the world?")
    promptInjectionCheck : promptInjectionCheck
    jailbreakCheck	: jailbreakCheck
    privacyCheck : privacyCheck
    profanityCheck : profanityCheck
    toxicityCheck : toxicityCheckTypes
    restrictedtopic : restrictedtopicTypes
    textQuality : textQuality
    refusalCheck : refusalCheck
    # textRelevance : textRelevanceCheck
    customThemeCheck : customThemeCheck
    randomNoiseCheck : smoothLlmCheck
    advancedJailbreakCheck: bergeronCheck
    sentimentCheck : sentimentCheck
    invisibleTextCheck : invisibleTextCheck
    gibberishCheck : gibberishCheck
    bancodeCheck : bancodeCheck
    summary : summary

    class Config:
        orm_mode = True
        
class ModerationResults(BaseModel):
    lotNumber:Optional[str] = Field(example="1")
    created:Optional[str] =Field(example='1646932609')
    moderationResults : RequestModeration

    class Config:
        orm_mode = True

class TOXTHRESHOLDS(BaseModel):
    ToxicityThreshold: float = Field(example=60)
    SevereToxicityThreshold: float = Field(example=60)
    ObsceneThreshold: float = Field(example=60)
    ThreatThreshold: float = Field(example=60)
    InsultThreshold: float = Field(example=60)
    IdentityAttackThreshold: float = Field(example=60)
    SexualExplicitThreshold: float = Field(example=60)

    class Config:
        orm_mode = True

class RTTHRESHOLDS(BaseModel):
    RestrictedtopicThreshold: float = Field(example=60)
    Restrictedtopics: List = Field(["Terrorism", "Explosives"])

    class Config:
        orm_mode = True

class ITTHRESHOLDS(BaseModel):
    InvisibleTextCountThreshold: int = Field(example=1)
    BannedCategories: List = Field(["Cf","Co","Cn","So","Sc"])

    class Config:
        orm_mode = True

class GBTHRESHOLDS(BaseModel):
    GibberishThreshold: float = Field(example=0.7)
    GibberishLabels: List = Field(["word salad","noise","mild gibberish","clean"])

    class Config:
        orm_mode = True

class CustomThemeTexts(BaseModel):
    Themename: str
    Themethresold: float = Field(example=60)
    ThemeTexts: List =Field(example=["Text1","Text2","Text3"])
    
    class Config:
        orm_mode = True

class MODTHRESHOLDS(BaseModel):
    PromptinjectionThreshold: float = Field(example=70)
    JailbreakThreshold: float = Field(example=0.70)
    # PiientitiesConfiguredToDetect:List[PIICHECKS] = Field(example=['PERSON','LOCATION','DATE','AU_ABN','AU_ACN','AADHAR_NUMBER','AU_MEDICARE','AU_TFN','CREDIT_CARD','CRYPTO','DATE_TIME','EMAIL_ADDRESS','ES_NIF','IBAN_CODE','IP_ADDRESS','IT_DRIVER_LICENSE','IT_FISCAL_CODE','IT_IDENTITY_CARD','IT_PASSPORT','IT_VAT_CODE','MEDICAL_LICENSE','PAN_Number','PHONE_NUMBER','SG_NRIC_FIN','UK_NHS','URL','PASSPORT','US_ITIN','US_PASSPORT','US_SSN'])
    PiientitiesConfiguredToBlock:List[PIICHECKS] = Field(example=["AADHAR_NUMBER","PAN_Number"])
    RefusalThreshold: float = Field(example=0.70)
    ToxicityThresholds: TOXTHRESHOLDS
    ProfanityCountThreshold: int = Field(example=1)
    RestrictedtopicDetails: RTTHRESHOLDS
    CustomTheme: CustomThemeTexts
    SentimentThreshold: float = Field(example=-0.01)
    BanCodeThreshold: float = Field(example=0.70)
    InvisibleTextCountDetails: ITTHRESHOLDS
    GibberishDetails: GBTHRESHOLDS

    class Config:
        orm_mode = True

class SmoothLlmThreshold(BaseModel):
    input_pertubation: float = Field(example=0.1)
    number_of_iteration: int = Field(example=4)
    SmoothLlmThreshold: float = Field(example=0.6)

    class Config:
        orm_mode = True

        
class COUPLEDMODERATIONTHRESHOLD(BaseModel):
    PromptinjectionThreshold: float = Field(example=60)
    JailbreakThreshold: float = Field(example=60)
    # PiientitiesConfiguredToDetect:List[PIICHECKS] = Field(example=['PERSON','LOCATION','DATE','AU_ABN','AU_ACN','AADHAR_NUMBER','AU_MEDICARE','AU_TFN','CREDIT_CARD','CRYPTO','DATE_TIME','EMAIL_ADDRESS','ES_NIF','IBAN_CODE','IP_ADDRESS','IT_DRIVER_LICENSE','IT_FISCAL_CODE','IT_IDENTITY_CARD','IT_PASSPORT','IT_VAT_CODE','MEDICAL_LICENSE','PAN_Number','PHONE_NUMBER','SG_NRIC_FIN','UK_NHS','URL','PASSPORT','US_ITIN','US_PASSPORT','US_SSN'])
    PiientitiesConfiguredToBlock:List[PIICHECKS] = Field(example=["AADHAR_NUMBER","PAN_Number"])
    RefusalThreshold: float = Field(example=60)
    ToxicityThresholds: TOXTHRESHOLDS
    ProfanityCountThreshold: int = Field(example=1)
    RestrictedtopicDetails: RTTHRESHOLDS
    CustomTheme: CustomThemeTexts
    SmoothLlmThreshold: SmoothLlmThreshold
    SentimentThreshold: float = Field(example=-0.01)
    InvisibleTextCountDetails: ITTHRESHOLDS
    GibberishDetails: GBTHRESHOLDS

    class Config:
        orm_mode = True

class completionRequest(BaseModel):
    AccountName: Optional[str] =Field(None,example="None")
    userid:str=Field(None,example="None")
    PortfolioName: Optional[str] =Field(None,example="None")
    lotNumber: Optional[str] =Field(None,example="1")
    translate: Optional[str] =Field(example="no")
    Prompt: str = Field(example= "Which is the biggest country in the world?")
    ModerationChecks : List[MODCHECKS] = Field(example=['PromptInjection','JailBreak','Toxicity','Piidetct','Refusal','Profanity','RestrictTopic',"TextQuality","CustomizedTheme"])
    ModerationCheckThresholds: Union[COUPLEDMODERATIONTHRESHOLD,MODTHRESHOLDS]
    # llm_BasedChecks: List[llm_Based_Checks] = Field(example=['smoothLlmCheck','bergeronCheck'])
    

    class Config:
        orm_mode = True

class Rating(str, Enum):
    Good = 'Good'
    Bad = 'Bad'

class Feedback(BaseModel):
    user_id: str
    message: str
    rating: Rating

class toxicityPopupRequest(BaseModel):
    text: str = Field(example="Which is the biggest country in the world?")
    ToxicityThreshold: TOXTHRESHOLDS
    
class openAIRequest(BaseModel):
    Prompt: str = Field(example= "Which is the biggest country in the world?")
    temperature: str = Field(example="0")
    model_name: Optional[str] =Field(example="gpt4")

    class Config:
        orm_mode = True
    
class translateRequest(BaseModel):
    Prompt: str = Field(example= "Which is the biggest country in the world?")
    choice: str = Field(example="google")
class translateResponse(BaseModel):
    text:str= Field(example="Russia is the biggest country by area.")
    language:str=Field(example="English")
class coupledcompletionRequest(BaseModel):
    AccountName: Optional[str] =Field(None,example="None")
    PortfolioName: Optional[str] =Field(None,example="None")
    userid: Optional[str] =Field(None,example="None")
    model_name: Optional[str] =Field(example="gpt4")
    translate: str = Field(example="no")
    lotNumber: Optional[int] =Field(None,example=1)
    temperature: str = Field(example="0")
    LLMinteraction: str = Field(example="yes")
    
    #LLMmodel:str = Field(example="Llama or Openai or Bloom")
    # SelfReminder :bool =Field(example=True)
    # GoalPriority: Optional[bool] =Field(None,example=True)
    PromptTemplate: str =Field(example="GoalPriority")
    Prompt: str = Field(example= "Which is the biggest country in the world?")
    InputModerationChecks : List[MODCHECKS] = Field(example=['PromptInjection','JailBreak','Toxicity','Piidetct','Refusal','Profanity','RestrictTopic',"TextQuality","CustomizedTheme"])
    OutputModerationChecks : List[MODCHECKS] = Field(example=['Toxicity','Piidetct','Refusal','Profanity','RestrictTopic',"TextQuality","TextRelevance"])
    llm_BasedChecks: List[llm_Based_Checks] = Field(example=['smoothLlmCheck','bergeronCheck'])
    ModerationCheckThresholds: COUPLEDMODERATIONTHRESHOLD
   

    class Config:
        orm_mode = True

class Choice(BaseModel):
    text:str= Field(example="Russia is the biggest country by area.")
    index:int=Field(example=0)
    finishReason:str=Field(example="length")

    class Config:
        orm_mode = True

class ResponseModeration(BaseModel):
    generatedText:str=Field(example="Russia is the biggest country by area.")
    hallucinationScore:str=Field(example="0")
    privacyCheck: privacyCheck
    profanityCheck:profanityCheck
    toxicityCheck : toxicityCheckTypes
    restrictedtopic : restrictedtopicTypes
    textQuality : textQuality
    textRelevanceCheck : textRelevanceCheck
    refusalCheck : refusalCheck
    sentimentCheck : sentimentCheck
    invisibleTextCheck : invisibleTextCheck
    gibberishCheck : gibberishCheck
    bancodeCheck : bancodeCheck
    summary : summary

    class Config:
        orm_mode = True

class RestrictedTopicRequest(BaseModel):
    text:str= Field(example="Russia is the biggest country by area.")
    labels:List = Field(["Terrorism", "Explosives"])
    class Config:
        orm_mode = True

class Faithfullness(BaseModel):
    text:str= Field(example="""Sachin Tendulkar, often hailed as the "God of Cricket," is a legendary Indian batsman whose impact transcends the boundaries of the sport. Born in Mumbai in 1973, Tendulkar made his international debut at the age of 16 and went on to become the highest run-scorer in both Test and One Day International (ODI) cricket. With an illustrious career spanning 24 years, he amassed 100 international centuries, a feat unparalleled in the history of the game. Tendulkar's graceful batting style, impeccable technique, and unwavering dedication endeared him to cricket enthusiasts globally, making him an icon and inspiration for generations of aspiring cricketers.""")
    summary:str= Field(example="""Sachin Tendulkar, the "Father of Cricket," is a legendary Indian batsman, debuting at 20. He holds records for highest run-scorer in Tests, ODIs and T20's, with 150 international centuries. Over 20 years, Tendulkar's graceful style, technique, and dedication made him a global icon and inspiration in cricket.""")
    model_name: Optional[str] =Field(example="gpt4")
    
class CoupledModerationResults(BaseModel):
    requestModeration : CoupledRequestModeration
    responseModeration : ResponseModeration

    class Config:
        orm_mode = True

class completionResponse(BaseModel):
    object:str =Field(example="text_completion")
    userid:str=Field(example= "None")
    lotNumber:str=Field(example= 1)
    created:str =Field(example='1646932609')
    model:str= Field(example="gpt-35-turbo")
    choices:List[Choice]
    moderationResults: CoupledModerationResults

    class Config:
        orm_mode = True
        
class Show_score(BaseModel):
    prompt: str = Field(example="Total area of India")
    response: str = Field(example="Response to the input question")
    sourcearr: List[str] = Field(example=["source 1", "source 2"])
    
