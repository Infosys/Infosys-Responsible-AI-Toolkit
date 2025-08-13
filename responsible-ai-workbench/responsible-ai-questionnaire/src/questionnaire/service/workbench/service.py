'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


from questionnaire.mapper.Questionnaires.mapper import UseCaseNameRequest
from questionnaire.config.logger import request_id_var
from questionnaire.dao.ExceptionDb import ExceptionDb
from dotenv import load_dotenv

from questionnaire.dao.UserLotAllocationDb import *
import pandas as pd
import requests
load_dotenv()
sslv={"False":False,"True":True,"None":True}
import os
class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class WorkBench:
    tenantList={"Privacy":{"url":os.getenv("PRIVACY_API")},
                "Safety":{"url":os.getenv("PROFANITY_API")},
                "FM-Moderation":{"url":os.getenv("FM_MODERATION_API")},
                "Explainability":{"url":os.getenv("EXPLAINABILITY_API")}}
    

    def getLotNumber(user):
        try:
            userLength = UserLotAllocationDb.findall({'user':user})
            new_lot=0
            if(len(userLength) > 0):
                # old_lot = len(userLength)
                # print(old_lot)
                new_lot = os.getenv("SERVERTYPE")+str(len(userLength) + 1) 

            else:
                new_lot =  os.getenv("SERVERTYPE")+str(new_lot+1)
                # privacyTeleUrl = (f"{privacyTeleUrl1}"f"&_a=(query:(language:kuery,query:'user:%22{value.user}%22%20and%20lotNumber%20:{new_lot}'))"  )
            return new_lot
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            ExceptionDb.create({"UUID":request_id_var.get(),"function":"getLotNumberFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)
        
    def setLotNumber(new_lot,fileName,user,tenant):
        try:
            # print(new_lot)    
            # print(tenant)
            privacyTeleUrl1 =  TelemetryUrlStore.findOne(tenant) 

            log.debug("privacyTeleUrl1:"+str(privacyTeleUrl1))
            if(tenant == "FM-Moderation"):
                privacyTeleUrl = (f"{privacyTeleUrl1}"f"&_a=(query:(language:kuery,query:'userid:%22{user}%22%20and%20lotNumber%20:{new_lot}'))"  )
            else:
                privacyTeleUrl = (f"{privacyTeleUrl1}"f"&_a=(query:(language:kuery,query:'user:%22{user}%22%20and%20lotNumber%20:{new_lot}'))"  )
            log.debug("privacyTeleUrl:"+str(privacyTeleUrl))
            lotDetail=UserLotAllocationDb.findall({"user":user,"lotNumber":new_lot})
            if(len(lotDetail) > 0):
                lotDataCreated = UserLotAllocationDb.mycol.update_one({"user":user,"lotNumber": new_lot},{'$push':{"TelemetryLinks":{"tenant":tenant,"TelemetryLink": privacyTeleUrl}}})
            else:
                lotDataCreated = UserLotAllocationDb.create({"user":user,"lotNumber": new_lot,"fileName":fileName,"status":"created","TelemetryLinks":{"tenant":tenant,"TelemetryLink": privacyTeleUrl}})
            # lotDataCreated = UserLotAllocationDb.create({"tenant":tenant,"user":user,"lotNumber": new_lot,"TelemetryLink":privacyTeleUrl})
            log.debug("lot data=="+str(lotDataCreated))
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            ExceptionDb.create({"UUID":request_id_var.get(),"function":"setLotFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)
       
        
                    

    def apiCall(url, payload):
        payload=AttributeDict(payload)
        try:
            log.debug("url:"+str(url))
            log.debug("payload:"+str(payload))
            response = requests.post(url, json=payload,verify=sslv[os.getenv("VERIFY_SSL","None")])
            return response.json()
        except Exception as e:
                log.error(str(e))
                log.error("Line No:"+str(e.__traceback__.tb_lineno))
                log.error(str(e.__traceback__.tb_frame))
                ExceptionDb.create({"UUID":request_id_var.get(),"function":"apiCallFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                raise Exception(e)
    
    def tenant(i,lotNum,fileName,userid,tenant,text,n):
                    try:
                        if(i==0):
                            # print("=====",tenant,lotNum)
                            WorkBench.setLotNumber(lotNum,fileName,userid,tenant)
                            # WorkBench.tenantList[tenant]["lotnum"]=lotNum``
                        # log.debug("tenantlist"+str(WorkBench.tenantList))
                        log.debug("Tenant:"+str(tenant))
                        log.debug("lotNum:"+str(lotNum))
                        # url = "http://10.66.155.13:30002/v1/privacy/text/analyze"
                        reqPayload ={"Privacy": {
                                      "inputText": text,
                                      "user": userid,
                                      "lotNumber": lotNum
                                    },"Safety":{
                                      "inputText": text,
                                      "user": userid,
                                      "lotNumber": lotNum
                                     }, 
                                    "FM-Moderation":{
  "AccountName": "None",
  "userid": userid,
  "PortfolioName": "None",
  "lotNumber": lotNum,
  "Prompt": text,
  "ModerationChecks": [
    "PromptInjection",
    "JailBreak",
    "Toxicity",
    "Piidetct",
    "Refusal",
    "Profanity",
    "RestrictTopic",
    "TextQuality",
    "CustomizedTheme"
  ],
  "ModerationCheckThresholds": {
    "PromptinjectionThreshold": 0.7,
    "JailbreakThreshold": 0.7,
    "PiientitiesConfiguredToDetect": [
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
    ],
    "PiientitiesConfiguredToBlock": [
      "AADHAR_NUMBER",
      "PAN_Number"
    ],
    "RefusalThreshold": 0.7,
    "ToxicityThresholds": {
      "ToxicityThreshold": 0.6,
      "SevereToxicityThreshold": 0.6,
      "ObsceneThreshold": 0.6,
      "ThreatThreshold": 0.6,
      "InsultThreshold": 0.6,
      "IdentityAttackThreshold": 0.6,
      "SexualExplicitThreshold": 0.6
    },
    "ProfanityCountThreshold": 1,
    "RestrictedtopicDetails": {
      "RestrictedtopicThreshold": 0.7,
      "Restrictedtopics": [
        "Terrorism",
        "Explosives"
      ]
    },
    "CustomTheme": {
      "Themename": "string",
      "Themethresold": 0.6,
      "ThemeTexts": [
        "Text1",
        "Text2",
        "Text3"
      ]
    }
  }
},
                                    "Explainability":{
                                              "inputText": text,
                                              "explainerID": 1,
                                              "user": userid,
                                              "lotNumber": lotNum
                                            }
                                    
                                        }
                        # lo(reqPayload)
                        res=WorkBench.apiCall(WorkBench.tenantList[tenant]["url"],reqPayload[tenant])
                        log.debug(str(res))  
                        # if(i==0):
                        #     UserLotAllocationDb.update({"user":userid,"lotNumber":lotNum},{"status":"Processing"})
                        # if(i==n):
                        #     UserLotAllocationDb.update({"user":userid,"lotNumber":lotNum},{"status":"Completed"})
                        # # if(i==df[0].count()-1):
                    except Exception as e:
                        log.error(str(e))
                        log.error("Line No:"+str(e.__traceback__.tb_lineno))
                        log.error(str(e.__traceback__.tb_frame))
                        ExceptionDb.create({"UUID":request_id_var.get(),"function":"tenantFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                        raise Exception(e)
    
    def uploadFile(payload):
        payload=AttributeDict(payload)
        tenantList=payload.tenant
        userid=payload.userId
        
        try:
            df = pd.read_csv(payload.file.file,header=None)
            fileName=payload.file.filename
            i=0
            lotNum=WorkBench.getLotNumber(userid)
            for text in df[0]:
                log.debug("text:"+str(text))
                for tenant in tenantList:
                    WorkBench.tenant(i,lotNum,fileName,userid,tenant,text,df[0].count()-1)
                UserLotAllocationDb.update({"user":userid,"lotNumber":lotNum},{"status":"Processing"})
                        
                # # if("Privacy" in tenant):
                #     try:
                #         if(i==0):
                #             lotNum=WorkBench.getLotNumber(userid,"Privacy")
                #             WorkBench.setLotNumber(lotNum,userid,"Privacy")
                #             WorkBench.tenantList["Privacy"]["lotnum"]=lotNum
                #         print("Privacy")
                #         print(WorkBench.tenantList["Privacy"]["lotnum"])
                #         url = "http://10.66.155.13:30002/v1/privacy/text/analyze"
                #         reqPayload = {
                #                       "inputText": text,
                #                       "user": userid,
                #                       "lotNumber": WorkBench.tenantList["Privacy"]["lotnum"]
                #                     }
                #         print(reqPayload)
                #         res=WorkBench.apiCall(url,reqPayload)
                #         if(i==0):
                #             UserLotAllocationDb.update({"user":userid,"tenant":"Privacy","lotNumber":WorkBench.tenantList["Privacy"]["lotnum"]},{"status":"Processing"})
                #         if(i==df[0].count()-1):
                #             UserLotAllocationDb.update({"user":userid,"tenant":"Privacy","lotNumber":WorkBench.tenantList["Privacy"]["lotnum"]},{"status":"Completed"})
                #         print(res)  
                #         # if(i==df[0].count()-1):
                #     except Exception as e:
                #         # raise Exception(e)
                #         print(e)
                    
                # # if("Profanity" in tenant):
                #     try:    
                #         if(i==0):
                #             lotNum=WorkBench.getLotNumber(userid,"Profanity")
                #             WorkBench.setLotNumber(lotNum,userid,"Profanity")
                #             WorkBench.tenantList["Profanity"]["lotnum"]=lotNum
                #         # lotNum=WorkBench.getLotNumber(userid,tenant)
                # # fo    r text in df[0]:
                #         url = "http://10.66.155.13:30003/api/v1/safety/profanity/analyze"
                #         reqPayload = {
                #                       "inputText": text,
                #                       "user": userid,
                #                       "lotNumber": lotNum
                #                     }
                #         WorkBench.apiCall(url,reqPayload)
                #         if(i==0):
                #             UserLotAllocationDb.update({"user":userid,"tenant":"Profanity","lotNumber":WorkBench.tenantList["Profanity"]["lotnum"]},{"status":"Processing"})
                #         if(i==df[0].count()-1):
                #             UserLotAllocationDb.update({"user":userid,"tenant":"Profanity","lotNumber":WorkBench.tenantList["Profanity"]["lotnum"]},{"status":"Completed"})
                        
                #         # if(i==df[0].count()-1):
                #             # WorkBench.setLotNumber(lotNum,userid,"Profanity")
                #     except Exception as e:
                #         # raise Exception(e)
                #         print(e)
                    
                # # if("FM-Moderat`ion" in tenant):
                    # try:
                    #     if(i==0):
                    #         lotNum=WorkBench.getLotNumber(userid,"FM-Moderation")
                    #         WorkBench.setLotNumber(lotNum,userid,"FM-Moderation")
                    #         WorkBench.tenantList["FM-Moderation"]["lotnum"]=lotNum
                        
                        
                        
                        # lotNum=WorkBench.getLotNumber(userid,"FM-Moderation")
                # fo    r text in df[0]:
                
#                         url = "http://10.68.47.121:8000/rai/v1/moderations"
#                         reqPayload = {
#   "AccountName": "None",
#   "PortfolioName": "None",
#    "User": userid,
#   "lotNumber": str(lotNum),
#   "Prompt":text,
#   "ModerationChecks": [
#     "PromptInjection",
#     "JailBreak",
#     "Toxicity",
#     "Piidetct",
#     "Refusal",
#     "Profanity",
#     "RestrictTopic",
#     "TextQuality",
#     "CustomizedTheme"
#   ],
#   "ModerationCheckThresholds": {
#     "PromptinjectionThreshold": 0.7,
#     "JailbreakThreshold": 0.7,
#     "PiientitiesConfiguredToDetect": [
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
#     ],
#     "PiientitiesConfiguredToBlock": [
#       "AADHAR_NUMBER",
#       "PAN_Number"
#     ],
#     "RefusalThreshold": 0.7,
#     "ToxicityThresholds": {
#       "ToxicityThreshold": 0.6,
#       "SevereToxicityThreshold": 0.6,
#       "ObsceneThreshold": 0.6,
#       "ThreatThreshold": 0.6,
#       "InsultThreshold": 0.6,
#       "IdentityAttackThreshold": 0.6,
#       "SexualExplicitThreshold": 0.6
#     },
#     "ProfanityCountThreshold": 1,
#     "RestrictedtopicDetails": {
#       "RestrictedtopicThreshold": 0.7,
#       "Restrictedtopics": [
#         "Terrorism",
#         "Explosives"
#       ]
#     },
#     "CustomTheme": {
#       "Themename": "string",
#       "Themethresold": 0.6,
#       "ThemeTexts": [
#         "Text1",
#         "Text2",
#         "Text3"
#       ]
#     }
#   }
# }
#                         WorkBench.apiCall(url,reqPayload)
#                         # if(i==df[0].count()-1):
#                             # WorkBench.setLotNumber(lotNum,userid,"FM-Moderation")
#                     except Exception as e:
#                         # raise Exception(e)
#                         print(e)
                i=i+1
            # return df
            UserLotAllocationDb.update({"user":userid,"lotNumber":lotNum},{"status":"Completed"})
                       
        except Exception as e:
                log.error(str(e))
                log.error("Line No:"+str(e.__traceback__.tb_lineno))
                log.error(str(e.__traceback__.tb_frame))
                ExceptionDb.create({"UUID":request_id_var.get(),"function":"uploadFileFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                raise Exception(e)
