'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''



# from privacy.dao.TelemetryFlagDb import TelemetryFlag
from privacy.mappers.mappers import *

from typing import List
from privacy.constants.local_constants import (DELTED_SUCCESS_MESSAGE)
from privacy.exception.exception import PrivacyNameNotEmptyError, PrivacyException, PrivacyNotFoundError

from privacy.config.logger import CustomLogger
log = CustomLogger()
from dotenv import load_dotenv
from privacy.config.logger import request_id_var
load_dotenv()
from faker import Faker
fake = Faker()

from privacy.util.special_recognizers.DataListRecognizer import DataListRecognizer
# global error_dict
from privacy.service.__init__ import *
from privacy.service.api_req import ApiCall

from privacy.util.special_recognizers.fakeData import FakeDataGenerate
from privacy.service.__init__ import *
from privacy.service.api_req import ApiCall


class TextPrivacy:
    def analyze(payload: PIIAnalyzeRequest) -> PIIAnalyzeResponse:
        error_dict[request_id_var.get()]=[]
        log.debug("Entering in analyze function")
        # gc.collect()
        log.debug(f"payload: {payload}")
        piiEntitiesToBeRedacted = payload.piiEntitiesToBeRedacted
        try:
            if(payload.exclusionList == None):
                exclusionList=[]
            else:
                exclusionList=payload.exclusionList

            if(payload.portfolio== None):
                results = TextPrivacy.textAnalyze(text=payload.inputText,piiEntitiesToBeRedacted=piiEntitiesToBeRedacted,exclusion=exclusionList,nlp=payload.nlp)
            else:
                results = TextPrivacy.textAnalyze(text=payload.inputText,accName=payload,exclusion=exclusionList,nlp=payload.nlp)
            if results == None:
                return None
            if( results== 404):
                return results
            if(results==482):
                return results
            list_PIIEntity = []
            results=sorted(results, key=lambda i: i.start)
            
            for result in results:
                log.debug(f"result: {result}")
                obj_PIIEntity = PIIEntity(type=result.entity_type,
                                          beginOffset=result.start,
                                          endOffset=result.end,
                                          score=result.score,
                                          responseText=payload.inputText[result.start:result.end])
                log.debug(f"obj_PIIEntity: {obj_PIIEntity}")
                list_PIIEntity.append(obj_PIIEntity)
                del obj_PIIEntity

            log.debug(f"list_PIIEntity: {list_PIIEntity}")
            objPIIAnalyzeResponse = PIIAnalyzeResponse
            objPIIAnalyzeResponse.PIIEntities = list_PIIEntity
            # gc.collect()
            log.debug("Returning from analyze function")
            return objPIIAnalyzeResponse
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"textAnalyzeMainFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            # ExceptionDb.create({"UUID":request_id_var.get(),"function":"textAnalyzeMainFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)
    # @profile
    
    def textAnalyze(text: str,accName:any=None,exclusion:any=None,piiEntitiesToBeRedacted:any=None,nlp="basic"):
        result=[]
       
        analyzer,imageAnalyzerEngine,imageRedactorEngine,imagePiiVerifyEngine,encryptImageEngin=selectNlp(nlp)
         
        spRecog=None
        if(nlp=="roberta"):
            spRecog=[roberta_recog]
        if(nlp=="ranha"):
            # registry.add_recognizer(ranha_recog)
            if(piiEntitiesToBeRedacted==None and  accName==None):
                piiEntitiesToBeRedacted=list(set(ranha_recog.supported_entities+registry.get_supported_entities()))
            spRecog=[ranha_recog]
        try:
            if(accName==None):
                 
                # ent_pattern=[]
                if(piiEntitiesToBeRedacted == None):
                    result = analyzer.analyze(text=text,language="en",allow_list=exclusion,return_decision_process = True,score_threshold=0.5,ad_hoc_recognizers=spRecog)
                    
                else:
                    try:
                        result = analyzer.analyze(text=text,language="en",entities=piiEntitiesToBeRedacted,allow_list=exclusion,return_decision_process = True, ad_hoc_recognizers=spRecog)
                         
                    except Exception as e:
                         
                        return 482
                        # raise Exception("An error occurred while analyzing the text", e)

                 
                 

                        
            #     #score_threshold reference
            #     # gc.collect()
             

            else:
                preEntity=[]
                # entityType,datalist,preEntity=admin_par[request_id_var.get()]["scoreTreshold"].request(accName)
                # entityType,datalist,preEntity=ApiCall.request(accName)
                dataistEnt = []
                
                response_value=ApiCall.request(accName)

                if(response_value==None):
                    return None
                if(response_value==404):
                     
                    return response_value
                
                entityType,datalist,preEntity=response_value
                 
                for d in range(len(datalist)):
                    record=ApiCall.getRecord(entityType[d])
                    record=AttributeDict(record)
                    log.debug("Record====="+str(record))

                    # predefined_recognizers.data_recognizer.DataList.entity.clear()
                    # predefined_recognizers.data_recognizer.DataList.resetData()
                    if(record.RecogType=="Data"):
                            
                            dataRecog=(DataListRecognizer(terms=datalist[d],entitie=[entityType[d]]))
                            registry.add_recognizer(dataRecog)
                            # predefined_recognizers.data_recognizer.DataList.entity.append(entityType[d])
                            # predefined_recognizers.data_recognizer.DataList.setData(datalist[d])
                             
                             
                            update_session_dict(entityType[d], datalist[d])
                            data = {entityType[d]: datalist[d]}
                            dataistEnt.append(data)
                 
                    elif(record.RecogType=="Pattern" and record.isPreDefined=="No"):
                        contextObj=record.Context.split(',')
                        pattern="|".join(datalist[d])
                         
                        log.debug("pattern="+str(pattern))
                        patternObj = Pattern(name=entityType[d],
                                                       regex=pattern,
                                                       score=record.Score)
                        patternRecog = PatternRecognizer(supported_entity=entityType[d],
                                                                   patterns=[patternObj],context=contextObj)
                        registry.add_recognizer(patternRecog)

                    # result.clear()
                     
                 
                 
                results = analyzer.analyze(text=text, language="en",entities=entityType+preEntity,allow_list=exclusion,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"],ad_hoc_recognizers=spRecog)
                        # entityType.remove(preEntity)
                result.extend(results)
                    # preEntity.clear()
                # if len(preEntity) > 0:
                #     results = analyzer.analyze(text=text, language="en",entities=preEntity,allow_list=exclusion,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"])
                #     preEntity.clear()
                #     result.extend(results)
                # predefined_recognizers.data_recognizer.DataList.entity.clear()
                # predefined_recognizers.data_recognizer.DataList.resetData()

                log.debug(f"results: {results}")
                log.debug(f"type results: {type(results)}")
                # result.extend(results)
            # gc.collect()
            # del analyzer
            # del registry
            # ApiCall.encryptionList.clear()
            log.debug("result="+str(result))
                
            return result
        except Exception as e:
            log.error(str(e))
            
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            # ExceptionDb.create({"UUID":request_id_var.get(),"function":"textAnalyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"textAnalyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)
  
    def anonymize(payload: PIIAnonymizeRequest):
        error_dict[request_id_var.get()]=[]
        log.debug("Entering in anonymize function")
        try:
            # Data.encrypted_text.clear()  
            
            
            # if(payload.piiEntitiesToBeRedacted != None):
            #     piiEntitiesToBeRedacted = payload.piiEntitiesToBeRedacted
            # else:
            piiEntitiesToBeRedacted = payload.piiEntitiesToBeRedacted 
            if(payload.exclusionList == None):
                exclusionList=[]
            else:
                exclusionList=payload.exclusionList
            if(payload.portfolio== None):
                results = TextPrivacy.textAnalyze(text=payload.inputText,exclusion=exclusionList,piiEntitiesToBeRedacted=piiEntitiesToBeRedacted,nlp=payload.nlp)
                 
                
                # if(len(results)==2):
                 
                #     return results[0]
                
                
                    # obj_PIIAnonymizeResponse = PIIAnonymizeResponse
                     
                    # obj_PIIAnonymizeResponse.anonymizedText = str(results[1])
                    # return obj_PIIAnonymizeResponse
            else: 
                results = TextPrivacy.textAnalyze(text=payload.inputText,accName=payload,exclusion=exclusionList,nlp=payload.nlp)
                
            ent_pattern=[]
            if results == None:
                return None

            if(results==404):
                     
                    return results
                
            if(results==482):
                return results
            dict_operators = {} 
            if payload.fakeData == True:            
                #  fakeDataGeneration() used for generating fakeData for the entities whcih return dict containg the fake data is replaced with entity....
                fake_dict_operator = FakeDataGenerate.fakeDataGeneration(results,payload.inputText)
                dict_operators.update(fake_dict_operator)
        

            encryptionList=[]
            if(payload.portfolio!= None ):

                encryptionList=admin_par[request_id_var.get()]["encryptionList"]
             
            if encryptionList is not None and len(encryptionList) >0 :
                for entity in encryptionList:
                     
                    dict_operators.update({entity: OperatorConfig("hash", {"hash-type": 'md5'})})
            # else:
            #     dict_operators = None

            # ApiCall.encryptionList.clear()
            anonymize_text = anonymizer.anonymize(text=payload.inputText,
                                                  operators=dict_operators,
                                                  analyzer_results=results)


            log.debug(f"anonymize_text: {anonymize_text}")
            log.debug(f"anonymize_text_item"+ str(anonymize_text.items))

            obj_PIIAnonymizeResponse = PIIAnonymizeResponse
            obj_PIIAnonymizeResponse.anonymizedText = anonymize_text.text
            log.debug("Returning from anonymize function")

            return obj_PIIAnonymizeResponse
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"textAnonimyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)

    def encrypt(payload: PIIAnonymizeRequest):
        log.debug("Entering in encrypt function")
        
        try:
            # Data.encrypted_text.clear()  
            
            if(payload.exclusionList == None):
                exclusionList=[]
            else:
                exclusionList=payload.exclusionList
            if(payload.portfolio== None):
                results = TextPrivacy.textAnalyze(text=payload.inputText,exclusion=exclusionList,nlp=payload.nlp)
            else: 
                results = TextPrivacy.textAnalyze(text=payload.inputText,accName=payload,exclusion=exclusionList,nlp=payload.nlp)
                
            if results == None:
                return None
            dict_operators = {} 
            
            data = "WmZq4t7w!z%C&F)J"
                
            for i in results:
                dict_operators.update({i.entity_type : OperatorConfig("encrypt", {"key": data})})
            
            anonymize_text = anonymizer.anonymize(text=payload.inputText,
                                                  operators=dict_operators,
                                                  analyzer_results=results)
            
            log.debug(f"anonymize_text: {anonymize_text}")
            log.debug(f"anonymize_text_item"+ str(anonymize_text.items))
            
            obj_PIIEncryptResponse = PIIEncryptResponse
            obj_PIIEncryptResponse.text = anonymize_text.text
            obj_PIIEncryptResponse.items= anonymize_text.items
            log.debug("Returning from encrypt function")
            
            return obj_PIIEncryptResponse
        
        
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"textAnonimyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)
    
    def decryption(payload: PIIDecryptRequest):
        log.debug("Entering in decrypt function")
        # payload=AttributeDict(payload)
         
        try:
            anonymized_text = payload.text
            anonymized_entities = payload.items
            
            data = "WmZq4t7w!z%C&F)J"
            list_ent= []
            for item in anonymized_entities:
                list_ent.append(OperatorResult(start=item.start,
                                    end=item.end ,
                                    entity_type= item.entity_type,
                                    text= item.text,
                                    operator= item.operator,))
            anonymized_entities=list_ent    
            
            deanonymized_result = deanonymizer.deanonymize(text=anonymized_text,
                                            entities=anonymized_entities,
                                    operators={"DEFAULT": OperatorConfig("decrypt", {"key": data})},)
            
            obj_PIIDecryptResponse = PIIDecryptResponse
            obj_PIIDecryptResponse.decryptedText = deanonymized_result.text
            log.debug("Returning from anonymize function")

            return obj_PIIDecryptResponse
            
            
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"textAnonimyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)
    
class Shield:
    def privacyShield(payload: PIIPrivacyShieldRequest) -> PIIPrivacyShieldResponse:
        log.debug("Entering in privacyShield function")
        log.debug(f"payload: {payload}")

        res = []
        totEnt=[]
        enres=[]
        query={}
       
        log.debug("response="+str(res))
        if(payload.portfolio== None):
            response_value=ApiCall.request(payload)
            if(response_value==None):
                return None
            if(response_value==404):
                     
                    
                    return response_value
            entityType,datalist,preEntity=response_value
            # entityType,datalist,preEntity=ApiCall.request(payload) 
            results = TextPrivacy.textAnalyze(text=payload.inputText)
            # entity=RecogDb.findall({})
            record=[ele for ele in admin_par[request_id_var.get()]["records"] if ele["isPreDefined"]=="Yes"]
            
            for i in record:
                i=AttributeDict(i)
                totEnt.append(i.RecogName)
            pass
        else:
            # entityType,datalist,preEntity=ApiCall.request(payload) 
            response_value=ApiCall.request(payload)
            if(response_value==None):
                return None
            if(response_value==404):
                     
                    return response_value
            entityType,datalist,preEntity=response_value
           
            to=[]
            # log.debug("entityTyope="+str(entityType))
            # log.debug("preEntity="+str(preEntity))
            entityType.extend(preEntity)
            # log.debug("entity="+str(entityType))
            totEnt=entityType
                
            results = TextPrivacy.textAnalyze(text=payload.inputText,accName=payload)
            # log.debug("total recoed="+str(totEnt))
        
        value=payload.inputText
        list_PIIEntity = []
        results=sorted(results, key=lambda i: i.start)
        for result in results:
            log.debug(f"result: {result}")
            enres.append({"type":result.entity_type,"start":result.start,"end":result.end,"value":value[result.start:result.end]})
            # obj_PIIEntity = PIIEntity(type=result.entity_type,
            #                           beginOffset=result.start,
            #                           endOffset=result.end)
            log.debug(f"obj_PIIEntity: {enres}")
            # list_PIIEntity.append(enres)
            # del obj_PIIEntity

        if(len(enres)==0):
            temp= "Passed"
        else:
            temp="Failed"

        objent = PrivacyShield(
             entitiesRecognised=enres,
             entitiesConfigured= totEnt,
             result=temp
        )
        list_PIIEntity.append(objent)
        log.debug(f"list_PIIEntity: {list_PIIEntity}")
        
        objPIIAnalyzeResponse = PIIPrivacyShieldResponse
        objPIIAnalyzeResponse.privacyCheck = list_PIIEntity


        log.debug("objPIIAnalyzeResponse="+str(objPIIAnalyzeResponse.privacyCheck))
        log.debug("Returning from privacyShield function")
        return objPIIAnalyzeResponse
    