'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
#from privacy.mappers.mappers import PIIEntity, PIIAnalyzeRequest, PIIAnalyzeResponse,PIIAnonymizeRequest,PIIAnonymizeResponse,PIIImageAnonymizeResponse,PIIImageAnalyzeResponse,PIIImageAnalyzeRequest
#from privacy.mappers.mappers import PIIEntity, PIIAnalyzeRequest, PIIAnalyzeResponse,PIIAnonymizeRequest,PIIAnonymizeResponse,PIIImageAnonymizeResponse,PIIImageAnalyzeResponse,PIIImageAnalyzeRequest
import json
import io, base64
from PIL import Image
import requests
import pandas as pd
from privacy.service.easy import EasyOCR
from privacy.dao.TelemetryFlagDb import TelemetryFlag
from privacy.mappers.mappers import *
import os
from privacy.dao.privacy.PrivacyException import ExceptionDb
import httpx
# from privacy.util.nltk_recog import CustomNltkNlpEngine

from privacy.util.encrypt import EncryptImage

from typing import List
from privacy.constants.local_constants import (DELTED_SUCCESS_MESSAGE)
from privacy.exception.exception import PrivacyNameNotEmptyError, PrivacyException, PrivacyNotFoundError
from presidio_analyzer import Pattern, PatternRecognizer, AnalyzerEngine, RecognizerRegistry,predefined_recognizers
from presidio_anonymizer import AnonymizerEngine, DeanonymizeEngine
from presidio_anonymizer.entities import (RecognizerResult,
    OperatorResult,
    OperatorConfig)
from privacy.config.logger import CustomLogger
from presidio_image_redactor import ImageRedactorEngine,ImageAnalyzerEngine,ImagePiiVerifyEngine       
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from PIL import Image
import base64
import io
import os
#import zipfile
from zipfile import ZipFile,is_zipfile
from dotenv import load_dotenv
import tempfile
import glob
from pathlib import Path
import matplotlib.pyplot as plt
import pydicom
from presidio_image_redactor import DicomImageRedactorEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from privacy.util.conf.conf import ConfModle
from privacy.dao.AccDataGrpMappingDb import AccDataGrpDb
from privacy.dao.DataRecogdb import RecogDb
from privacy.dao.EntityDb import EntityDb
from privacy.dao.AccMasterDb import AccMasterDb
from privacy.dao.privacy.PrivacyException import ExceptionDb
from privacy.config.logger import request_id_var
load_dotenv()
import numpy as np

log = CustomLogger()
import time
# import gc
# importing the library
# from memory_profiler import profile

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
class Data:
    encrypted_text=[]
# log.info("============2")
registry = RecognizerRegistry()
# log.info("============2a")
analyzer = AnalyzerEngine(registry=registry)
# log.debug("============2b")
registry.load_predefined_recognizers()
        
class PrivacyService:
    # @profile

    def analyze(payload: PIIAnalyzeRequest) -> PIIAnalyzeResponse:
        log.debug("Entering in analyze function")
        # gc.collect()
        log.debug(f"payload: {payload}")
        try:
            if(payload.exclusionList == None):
                exclusionList=[]
            else:
                exclusionList=payload.exclusionList

            if(payload.portfolio== None):
                results = PrivacyService.__analyze(text=payload.inputText,exclusion=exclusionList)
            else:
                results = PrivacyService.__analyze(text=payload.inputText,accName=payload,exclusion=exclusionList)
            if results == None:
                return None
            list_PIIEntity = []
            results=sorted(results, key=lambda i: i.start)
            
            for result in results:
                log.debug(f"result: {result}")
                obj_PIIEntity = PIIEntity(type=result.entity_type,
                                          beginOffset=result.start,
                                          endOffset=result.end,
                                          score=result.score)
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
            ExceptionDb.create({"UUID":request_id_var.get(),"function":"textAnalyzeMainFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)
    # @profile
    
    def __analyze(text: str,accName:any=None,exclusion:any=None):
        result=[]
#         configuration = {
#     "nlp_engine_name": "spacy",
#     "models": [
#         # {"lang_code": "en", "model_name": "en_core_web_lg"},
#         {"lang_code": "en", "model_name": "en_core_web_lg"},
# ]}
#         provider = NlpEngineProvider(nlp_configuration=configuration)
#         nlp_engine = provider.create_engine()
#         registry = RecognizerRegistry()
#         analyzer = AnalyzerEngine(registry=registry,nlp_engine=nlp_engine)
#         # analyzer = AnalyzerEngine()
        
        # analyzer.(CustomNltkNlpEngine())
        # analyzer,registry=ConfModle.getAnalyzerEngin("en_core_web_lg")
        # registry.load_predefined_recognizers()
        # log.debug("============2")
        # registry = RecognizerRegistry()
        # log.debug("============2a")
        # analyzer = AnalyzerEngine(registry=registry)
        # log.debug("============2b")
        # registry.load_predefined_recognizers()
        
        
        try:
            if(accName==None):
                result = analyzer.analyze(text=text, language="en",allow_list=exclusion)
                #score_threshold reference
                # gc.collect()

            else:
                preEntity=[]
                # entityType,datalist,preEntity=ApiCall.request(accName)
                response_value=ApiCall.request(accName)
                if(response_value==None):
                    return None
                entityType,datalist,preEntity=response_value
                for d in range(len(datalist)):
                    record=ApiCall.getRecord(entityType[d])
                    record=AttributeDict(record)
                    # log.debug("Record====="+str(record))

                    predefined_recognizers.data_recognizer.DataList.entity.clear()
                    predefined_recognizers.data_recognizer.DataList.resetData()
                    if(record.RecogType=="Data"):
                            predefined_recognizers.data_recognizer.DataList.entity.append(entityType[d])
                            predefined_recognizers.data_recognizer.DataList.setData(datalist[d])
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
                    results = analyzer.analyze(text=text, language="en",entities=entityType,allow_list=exclusion,score_threshold=ApiCall.scoreTreshold)
                        # entityType.remove(preEntity)
                    result.extend(results)
                    # preEntity.clear()
                if len(preEntity) > 0:
                    results = analyzer.analyze(text=text, language="en",entities=preEntity,allow_list=exclusion,score_threshold=ApiCall.scoreTreshold)
                    preEntity.clear()
                    result.extend(results)
                predefined_recognizers.data_recognizer.DataList.entity.clear()
                predefined_recognizers.data_recognizer.DataList.resetData()

                log.debug(f"results: {results}")
                log.debug(f"type results: {type(results)}")
                # result.extend(results)
            # gc.collect()
            # del analyzer
            # del registry
            log.debug("result="+str(result))

            return result
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            ExceptionDb.create({"UUID":request_id_var.get(),"function":"textAnalyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)

    def anonymize(payload: PIIAnonymizeRequest):
        log.debug("Entering in anonymize function")
        try:
            Data.encrypted_text.clear()
            # print("payload====",payload)
            anonymizer = AnonymizerEngine()
            if(payload.exclusionList == None):
                exclusionList=[]
            else:
                exclusionList=payload.exclusionList
            if(payload.portfolio== None):
                results = PrivacyService.__analyze(text=payload.inputText,exclusion=exclusionList)
            else:

                results = PrivacyService.__analyze(text=payload.inputText,accName=payload,exclusion=exclusionList)
            if results == None:
                return None
            dict_operators = {}
            if(payload.portfolio!= None ):
                res=ApiCall.request(payload)
                print("Res279=======",res)
            else:
                pass
            # res=ApiCall.request(payload)
            encryptionList=ApiCall.encryptionList
            print(len(encryptionList),encryptionList)
            if encryptionList is not None and len(encryptionList) >0 :
                for entity in encryptionList:
                    dict_operators.update({entity: OperatorConfig("hash", {"hash-type": 'md5'})})
            else:
                dict_operators = None


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
            ExceptionDb.create({"UUID":request_id_var.get(),"function":"textAnonimyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)
    

  

    def image_analyze(payload):  
        try:
            log.debug("Entering in image_analyze function")        
            payload=AttributeDict(payload)
            image = Image.open(payload.image.file)
            analyzer,registry=ConfModle.getAnalyzerEngin("en_core_web_lg")


            ocr=None
            if(payload.easyocr=="EasyOcr"):
                ocr=EasyOCR()
                EasyOCR.setMag(payload.mag_ratio)
            engine = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)  
            registry.load_predefined_recognizers()
            log.debug("payload="+str(payload))  
            if(payload.exclusion == None):
                exclusionList=[]
            else:
                exclusionList=payload.exclusion.split(",")  
            if(payload.portfolio== None):
                results = engine.analyze(image, allow_list=exclusionList)
            else:
                result=[]
                preEntity=[]
                response_value=ApiCall.request(payload)
                if(response_value==None):
                    return None
                entityType,datalist,preEntity=response_value
                # entityType,datalist,preEntity=ApiCall.request(payload)
                # preEntity=["PERSON"]
                for d in range(len(datalist)):
                    record=ApiCall.getRecord(entityType[d])
                    record=AttributeDict(record)
                    # log.debug("Record ======"+str(record))
                    predefined_recognizers.data_recognizer.DataList.entity.clear()
                    predefined_recognizers.data_recognizer.DataList.resetData()
                    if(record.RecogType=="Data"):
                            predefined_recognizers.data_recognizer.DataList.entity.append(entityType[d])
                            predefined_recognizers.data_recognizer.DataList.setData(datalist[d])
                            # log.debug("++++++"+str(entityType[d]))
                            # results = engine.analyze(image,entities=[entityType[d]])
                            # result.extend(results)
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
                        # log.debug("==========="+str(entityType[d]))                   
                        # results = engine.analyze(image,entities=[entityType[d]])
                        # result.extend(results)
                    results = engine.analyze(image,entities=[entityType[d]], allow_list=exclusionList,score_threshold=ApiCall.scoreTreshold)
                    result.extend(results)
                    # results = PrivacyService.__analyze(text=payload.inputText,accName=accMasterid.accMasterId)
                if(len(preEntity)>0):               
                        results = engine.analyze(image,entities=preEntity, allow_list=exclusionList,score_threshold=ApiCall.scoreTreshold)
                        preEntity.clear()
                        result.extend(results)
                results=result                               

            #log.debug(f"results: {results}")

            list_PIIEntity = []
            for result in results:
                log.debug(f"result: {result}")
                obj_PIIEntity = PIIEntity(type=result.entity_type,
                                          beginOffset=result.start,
                                          endOffset=result.end,
                                          score=result.score)
                log.debug(f"obj_PIIEntity: {obj_PIIEntity}")
                list_PIIEntity.append(obj_PIIEntity)
                del obj_PIIEntity

            log.debug(f"list_PIIEntity: {list_PIIEntity}")
            objPIIAnalyzeResponse = PIIAnalyzeResponse
            objPIIAnalyzeResponse.PIIEntities = list_PIIEntity

            log.debug("Returning from image_analyze function")

            return objPIIAnalyzeResponse
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            ExceptionDb.create({"UUID":request_id_var.get(),"function":"imageAnalyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)


    
    def temp(payload):          
        engine = ImageAnalyzerEngine()
        
        image = Image.open(payload.file)                              
        results = engine.analyze(image)
        #log.debug(f"results: {results}")
        list_PIIEntity = []
        for result in results:
            log.debug(f"result: {result}")
            list_PIIEntity.append(result.entity_type)
            
            

        
        return list_PIIEntity

   

    def image_anonymize(payload): 
        log.debug("Entering in image_anonymize function")
        try: 
            payload=AttributeDict(payload)
            analyzer,registry=ConfModle.getAnalyzerEngin("en_core_web_lg")
            ocr=None
            if(payload.easyocr=="EasyOcr"):
                ocr=EasyOCR()
                # EasyOCR.setMag(payload.mag_ratio)

            engine1 = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)  
            engine = ImageRedactorEngine(image_analyzer_engine=engine1)
            # engine = ImageRedactorEngine()
            payload=AttributeDict(payload)
            image = Image.open(payload.image.file)
            registry.load_predefined_recognizers()
            # log.debug("payload.image.file====="+str(payload.image.file))
            if(payload.exclusion == None):
                exclusionList=[]
            else:
                exclusionList=payload.exclusion.split(",")
            if(payload.portfolio== None):
                redacted_image = engine.redact(image, (255, 192, 203), allow_list=exclusionList)
                processed_image_stream = io.BytesIO()
                redacted_image.save(processed_image_stream, format='PNG')
            else:
                result=[]
                preEntity=[]
                response_value=ApiCall.request(payload)
                if(response_value==None):
                    return None
                entityType,datalist,preEntity=response_value
                # entityType,datalist,preEntity=ApiCall.request(payload)
                for d in range(len(datalist)):
                    record=ApiCall.getRecord(entityType[d])
                    record=AttributeDict(record)
                    # log.debug("Record=="+str(record))
                    predefined_recognizers.data_recognizer.DataList.entity.clear()
                    predefined_recognizers.data_recognizer.DataList.resetData()
                    if(record.RecogType=="Data"):
                            predefined_recognizers.data_recognizer.DataList.entity.append(entityType[d])
                            predefined_recognizers.data_recognizer.DataList.setData(datalist[d])
                            # log.debug("++++++"+str(entityType[d]))
                            # results = engine.analyze(image,entities=[entityType[d]])
                            # redacted_image = engine.redact(image, (255, 192, 203),entities=[entityType[d]])
                            # processed_image_stream = io.BytesIO()
                            # redacted_image.save(processed_image_stream, format='PNG')
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
                        # log.debug("=="+str(entityType[d]))
                        # results = engine.analyze(image,entities=[entityType[d]])
                    redacted_image = engine.redact(image, (255, 192, 203),entities=[entityType[d]], allow_list=exclusionList,score_threshold=ApiCall.scoreTreshold)
                        # log.debug("redacted_image=="+str(redacted_image))
                    processed_image_stream = io.BytesIO()
                    redacted_image.save(processed_image_stream, format='PNG')
                    # log.debug("redacted_image="+str(redacted_image))  
                    image=redacted_image
                    # results = PrivacyService.__analyze(text=payload.inputText,accName=accMasterid.accMasterId)
                if(len(preEntity)>0):
                        redacted_image = engine.redact(image, (255, 192, 203),entities=preEntity, allow_list=exclusionList,score_threshold=ApiCall.scoreTreshold)
                        processed_image_stream = io.BytesIO()
                        redacted_image.save(processed_image_stream, format='PNG')
                        preEntity.clear()

            # redacted_image = engine.redact(image, (255, 192, 203),entities=preEntity)
            # processed_image_stream = io.BytesIO()
            # redacted_image.save(processed_image_stream, format='PNG')
            processed_image_bytes = processed_image_stream.getvalue()
            base64_encoded_image=base64.b64encode(processed_image_bytes)
            # saveImage.saveImg(base64_encoded_image)
            saveImage.saveImg(base64_encoded_image)
            log.debug("Returning from image_anonymize function")
            return base64_encoded_image
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            ExceptionDb.create({"UUID":request_id_var.get(),"function":"imageAnonimyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)

    def zipimage_anonymize(payload):                                            #$$$$$$$$$$$$
        result=[]
        in_memory_file=io.BytesIO(payload.file.read())

        engine = ImageRedactorEngine()
        log.debug("=="+str(is_zipfile(payload.file)))
                                           
        with ZipFile(in_memory_file, 'r') as zObject:
            for file_name in zObject.namelist():
                
                log.debug(zObject.namelist())
                log.debug("=="+str(type(zObject)))
                file_data=zObject.read(file_name)
                image=Image.open(io.BytesIO(file_data))
                redacted_image = engine.redact(image, (255, 192, 203))
                processed_image_stream = io.BytesIO()
                redacted_image.save(processed_image_stream, format='PNG')
                processed_image_bytes = processed_image_stream.getvalue()
                base64_encoded_image=base64.b64encode(processed_image_bytes)
                result.append(base64_encoded_image)
        return result
    
    def image_verify(payload):  
           log.debug("Entering in image_verify function")
           try:
                analyzer,registry=ConfModle.getAnalyzerEngin("en_core_web_lg")
                engine1 = ImageAnalyzerEngine(analyzer_engine=analyzer)
                engine = ImagePiiVerifyEngine(image_analyzer_engine=engine1)
                enginex=EncryptImage(image_analyzer_engine=engine1)
                payload=AttributeDict(payload)
                image = Image.open(payload.image.file)
                registry.load_predefined_recognizers()
                if(payload.exclusion == None):
                    exclusionList=[]
                else:
                    exclusionList=payload.exclusion.split(",")

                if(payload.portfolio== None):
                    verify_image = engine.verify(image, allow_list=exclusionList)
                    processed_image_stream = io.BytesIO()
                    verify_image.save(processed_image_stream, format='PNG')

                else:
                    result=[]
                    preEntity=[]
                    response_value=ApiCall.request(payload)
                    if(response_value==None):
                        return None
                    entityType,datalist,preEntity=response_value

                    # Al=ApiCall.encryptionList
                    for d in range(len(datalist)):
                        record=ApiCall.getRecord(entityType[d])
                        record=AttributeDict(record)

                        predefined_recognizers.data_recognizer.DataList.entity.clear()
                        predefined_recognizers.data_recognizer.DataList.resetData()
                        if(record.RecogType=="Data"):
                                predefined_recognizers.data_recognizer.DataList.entity.append(entityType[d])
                                predefined_recognizers.data_recognizer.DataList.setData(datalist[d])
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
                        verify_image = engine.verify(image,entities=[entityType[d]], allow_list=exclusionList,score_threshold=ApiCall.scoreTreshold)
                     #    verify_image = enginex.encrypt(image,encryptionList=Al,entities=[entityType[d]], allow_list=exclusionList)
                        processed_image_stream = io.BytesIO()
                        verify_image.save(processed_image_stream, format='PNG')
                        # log.debug("redacted_image="+str(redacted_image))  
                        image=verify_image
                        # results = PrivacyService.__analyze(text=payload.inputText,accName=accMasterid.accMasterId)
                    if(len(preEntity)>0):
                    
                            verify_image = engine.verify(image,entities=preEntity, allow_list=exclusionList,score_threshold=ApiCall.scoreTreshold)
                         #    verify_image = enginex.encrypt(image,encryptionList=Al,entities=preEntity, allow_list=exclusionList)


                            processed_image_stream = io.BytesIO()
                            verify_image.save(processed_image_stream, format='PNG')
                            preEntity.clear()

                processed_image_bytes = processed_image_stream.getvalue()
                base64_encoded_image=base64.b64encode(processed_image_bytes)
                saveImage.saveImg(base64_encoded_image)
                log.debug("Returning from image_verify function")
                return base64_encoded_image
           except Exception as e:
                log.error(str(e))
                log.error("Line No:"+str(e.__traceback__.tb_lineno))
                log.error(str(e.__traceback__.tb_frame))
                ExceptionDb.create({"UUID":request_id_var.get(),"function":"imageVeryFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                raise Exception(e)
       
    def imageEncryption(payload):
            log.debug("Entering in imageEncryption function")
            try:
                payload=AttributeDict(payload)
                EncryptImage.entity.clear()
                analyzer,registry=ConfModle.getAnalyzerEngin("en_core_web_lg")

                ocr=None
                if(payload.easyocr=="EasyOcr"):
                    ocr=EasyOCR()
                    EasyOCR.setMag(payload.mag_ratio)
                engine1 = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)
                # engine = ImageRedactorEngine(image_analyzer_engine=engine1)
                engine2=EncryptImage(image_analyzer_engine=engine1) #
                # engine = ImageRedactorEngine()
                payload=AttributeDict(payload)
                image = Image.open(payload.image.file)
                registry.load_predefined_recognizers()
                # log.debug("payload.image.file====="+str(payload.image.file))
                encryptMapper=[]
                if(payload.exclusion == None):
                    exclusionList=[]
                else:
                    exclusionList=payload.exclusion.split(",")
                engine2.getText(image)
                if(payload.portfolio== None):
                    # redacted_image = engine.redact(image, (255, 192, 203), allow_list=exclusionList)
                    redacted_image = engine2.imageAnonimyze(image, (255, 192, 203), allow_list=exclusionList)
                    processed_image_stream = io.BytesIO()
                    redacted_image.save(processed_image_stream, format='PNG')
                else:
                    result=[]
                    preEntity=[]
                    response_value=ApiCall.request(payload)
                    encryptionList=ApiCall.encryptionList
                    if(response_value==None):
                        return None
                    entityType,datalist,preEntity=response_value
                    # entityType,datalist,preEntity=ApiCall.request(payload)
                    for d in range(len(datalist)):
                        record=ApiCall.getRecord(entityType[d])
                        record=AttributeDict(record)
                        # log.debug("Record=="+str(record))
                        predefined_recognizers.data_recognizer.DataList.entity.clear()
                        predefined_recognizers.data_recognizer.DataList.resetData()
                        if(record.RecogType=="Data"):
                                predefined_recognizers.data_recognizer.DataList.entity.append(entityType[d])
                                predefined_recognizers.data_recognizer.DataList.setData(datalist[d])
                                # log.debug("++++++"+str(entityType[d]))
                                # results = engine.analyze(image,entities=[entityType[d]])
                                # redacted_image = engine.redact(image, (255, 192, 203),entities=[entityType[d]])
                                # processed_image_stream = io.BytesIO()
                                # redacted_image.save(processed_image_stream, format='PNG')
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
                            # log.debug("=="+str(entityType[d]))    
                            # results = engine.analyze(image,entities=[entityType[d]])
                        redacted_image = engine2.imageAnonimyze(image, (255, 192, 203),encryptionList=encryptionList,entities=[entityType[d]], allow_list=exclusionList,score_threshold=ApiCall.scoreTreshold)
                            # log.debug("redacted_image=="+str(redacted_image))
                        processed_image_stream = io.BytesIO()
                        redacted_image.save(processed_image_stream, format='PNG')
                        # log.debug("redacted_image="+str(redacted_image))  
                        image=redacted_image
                        # results = PrivacyService.__analyze(text=payload.inputText,accName=accMasterid.accMasterId)
                    if(len(preEntity)>0):
                            redacted_image = engine2.imageAnonimyze(image, (255, 192, 203),encryptionList=encryptionList,entities=preEntity, allow_list=exclusionList,score_threshold=ApiCall.scoreTreshold)
                            processed_image_stream = io.BytesIO()
                            redacted_image.save(processed_image_stream, format='PNG')
                            preEntity.clear()
                    EncryptImage.dis()
                    res=engine2.encrypt(redacted_image,encryptionList=encryptionList)
                    redacted_image=res[0]
                    encryptMapper=res[1]
                    processed_image_stream = io.BytesIO()
                    redacted_image.save(processed_image_stream, format='PNG')

                # redacted_image = engine.redact(image, (255, 192, 203),entities=preEntity)
                # processed_image_stream = io.BytesIO()
                # redacted_image.save(processed_image_stream, format='PNG')
                processed_image_bytes = processed_image_stream.getvalue()
                base64_encoded_image=base64.b64encode(processed_image_bytes)
                # saveImage.saveImg(base64_encoded_image)
                saveImage.saveImg(base64_encoded_image)
                obj={"map":encryptMapper,"img":base64_encoded_image}
                log.debug("Returning from imageEncryption function")
                return obj
            except Exception as e:
                log.error(str(e))
                log.error("Line No:"+str(e.__traceback__.tb_lineno))
                log.error(str(e.__traceback__.tb_frame))
                ExceptionDb.create({"UUID":request_id_var.get(),"function":"imageHashifyFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                raise Exception(e)


    
    
    
    
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
            entityType,datalist,preEntity=response_value
            # entityType,datalist,preEntity=ApiCall.request(payload) 
            results = PrivacyService.__analyze(text=payload.inputText)
            # entity=RecogDb.findall({})
            record=[ele for ele in ApiCall.records if ele["isPreDefined"]=="Yes"]
            
            for i in record:
                i=AttributeDict(i)
                totEnt.append(i.RecogName)
            pass
        else:
            # entityType,datalist,preEntity=ApiCall.request(payload) 
            response_value=ApiCall.request(payload)
            if(response_value==None):
                return None
            entityType,datalist,preEntity=response_value
           
            to=[]
            # log.debug("entityTyope="+str(entityType))
            # log.debug("preEntity="+str(preEntity))
            entityType.extend(preEntity)
            # log.debug("entity="+str(entityType))
            totEnt=entityType
                
            results = PrivacyService.__analyze(text=payload.inputText,accName=payload)
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
        # return res


class DICOM:
    def dcmToPng(dcmObj):
        plt.clf()
        plt.imshow(dcmObj.pixel_array,cmap=plt.cm.bone)
        plt.axis('off')
        buffer=io.BytesIO()
        plt.savefig(buffer,format='png', bbox_inches='tight', pad_inches=0)
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue())
        
    # def dicomReader():    
    #     engine = DicomImageRedactorEngine()
    #     op=r"C:\WORK\GIT\responsible-ai-privacy\responsible-ai-privacy\src\privacy\temp\0_ORIGINAL.dcm"
    #     dicom_instance = pydicom.dcmread(op)
    #     print(type(dicom_instance))
    #     redacted_dicom_instance = engine.redact(dicom_instance, fill="contrast")
    #     # compare_dicom_images(dicom_instance, redacted_dicom_instance)
    #     # print(type(redacted_dicom_instance))
    #     # plt.imshow(redacted_dicom_instance.pixel_array, cmap=plt.cm.bone)  # set the color map to bone
    #     # plt.show()
    #     # dd=BytesIO()
    #     # redacted_dicom_instance.save_as(dd)
    #     image = redacted_dicom_instance.pixel_array
    #     # x=Image.fromarray(image)
    #     p=r"C:\WORK\GIT\responsible-ai-privacy\responsible-ai-privacy\src\dicomResult.png"
    #     o=r"C:\WORK\GIT\responsible-ai-privacy\responsible-ai-privacy\src\dicomInput.png"
        
    #     # plt.imsave(p,image,cmap=plt.cm.bone)
    #     # plt.imsave(o,dicom_instance.pixel_array,cmap=plt.cm.bone)
    #     plt.imshow(dicom_instance.pixel_array,cmap=plt.cm.bone)
    #     b=BytesIO()
    #     plt.savefig(b,format='png')
    #     b.seek(0)
    #     # image=Image.open(b)
    #     # image.show()
    #     print(image)
    #     # d=redacted_dicom_instance.tobytes()
    #     # f=open(p,'rb')
    #     # of=open(o,'rb')
    #     print(b.getvalue())
    #     redicated=base64.b64encode(b.getvalue())
    #     # original=base64.b64encode(of.read())
    #     saveImage.saveImg(redicated)
    #     obj=image
    #     # obj={"original":original,"anonymize":redicated}
    #     return redicated
    
    def readDicom(payload):
        log.debug("Entering in readDicom function")
        try:
            # print(type(payload))
            print(payload.file)
            EncryptImage.entity.clear()
            predefined_recognizers.data_recognizer.DataList.entity.clear()
            predefined_recognizers.data_recognizer.DataList.resetData()
            DicomEngine = DicomImageRedactorEngine()
            dicom_instance = pydicom.dcmread(payload.file)
            print(type(dicom_instance))
            redacted_dicom_instance = DicomEngine.redact(dicom_instance, fill="contrast") 
            original=DICOM.dcmToPng(dicom_instance)
            redacted=DICOM.dcmToPng(redacted_dicom_instance)

            obj={"original":original,"anonymize":redacted}
            log.debug("Returning from readDicom function")
            return obj
  
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            ExceptionDb.create({"UUID":request_id_var.get(),"function":"readDICOMFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)
  
    




class saveImage:
    def saveImg(img_data):
        
    
        with open("imageToSave.png", "wb") as fh:
            fh.write(base64.decodebytes(img_data))
        
        
        
        
class PrivacyData:
    def getDataList(payload)->dict:
        try:
            accName=None
            if(payload.portfolio!=None):
                payload=AttributeDict(payload)
                # query={"portfolio":payload.portfolio,"account":payload.account}
                query=payload
                accMasterid=AccMasterDb.findall(query)
                if(len(accMasterid)==0):
                    obj=([],[],[],[],[],[])
                    return obj
                # print(accMasterid)

                accName=accMasterid[0].accMasterId  
                thresholdScore=  accMasterid[0].ThresholdScore     

            datalsit=[]
            newEntityType=[]
            preEntity=[]
            recogList=[]
            encrList=[]

            # score=[]
            if(accName!=None):
                # print("=====",accName)
                # accMasterid=AccMasterDb.findall({"accMasterName":accName})[0]
                accdata=AccDataGrpDb.findall({"accMasterId":accName})
                # print(accdata)
                for i in accdata:
                    # print("===",i.dataRecogGrpId)
                    record=RecogDb.findOne(i.dataRecogGrpId)
                    # print(record)
                    record=AttributeDict(record)

                    recogList.append(record)
                    # print(recogList)
                    if(i.isHashify==True):
                        encrList.append(record.RecogName)
                    if(record.isPreDefined=="No"):
                        newEntityType.append(record.RecogName)
                        datalsit.append(EntityDb.mycol.distinct("EntityName",{"RecogId":i.dataRecogGrpId}))
                    else:
                        preEntity.append(record.RecogName)
                # entityType=
            else:
                recogList=RecogDb.findall({})
            # print(newEntityType)
            # print(preEntity)         
            # print(datalsit)
            # print(recogList)

            obj=(newEntityType,datalsit,preEntity,recogList,encrList,[thresholdScore])
            return obj
        except Exception as e:

            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            ExceptionDb.create({"UUID":request_id_var.get(),"function":"getDataListFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)    
    


class TelemetryFlagData:
    def getTelFlagData():
        log.debug("Entering in getTelFlagData function")
        try:
            res =[]
            telFlagData = TelemetryFlag.findall({})[0]
            log.debug("telFlagData===="+str(telFlagData))

            object = Telemetry(
                Module=telFlagData["Module"],
                TelemetryFlagValue = telFlagData["TelemetryFlag"]
            )
            res.append(object)

            obj = TelemetryResponse
            obj.result=res
            # obj.Module = telFlagData["Module"]
            # obj.TelemetryFlagValue = telFlagData["TelemetryFlag"]
            log.debug("Returning from getTelFlagData function")
            return obj
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            ExceptionDb.create({"UUID":request_id_var.get(),"function":"getTelFlagDataFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)

class ApiCall:
    records=[]
    encryptionList=[]
    scoreTreshold=0.0
    def request(data):
        try:
            ApiCall.records.clear()
            ApiCall.encryptionList.clear()
            payload=AttributeDict({"portfolio":data.portfolio,"account":data.account})
            
            # payload={"accName":"Infosys","subAccName":"Impact"}
            # api_url = os.getenv("PRIVADMIN_API")
            
            # print(api_url)
            # aurl=api_url+"/api/v1/rai/admin/PrivacyDataList"
            # log.debug(aurl)
            # log.debug(str(type(aurl)))
            log.debug("Calling Admin Api  ======")
            log.debug("api payload:"+str(payload))
            # print(payload)
            # response1 = requests.post(
            #     url=aurl
            #     , headers={'Content-Type': "application/json",
            #                'accept': "application/json"}
            #     , verify=False
            #     , json=payload
            #     )
            # response1=httpx.post(aurl, json=payload)
            # response1=httpx.post('http://10.66.155.13:30016/api/v1/rai/admin/PrivacyDataList', json=payload)
            # log.debug("response="+str(response1))
            # log.debug("response11="+str(response1.text))
            response1=PrivacyData.getDataList(payload)
            entityType,datalist,preEntity,records,encryptionList,scoreTreshold=response1
            
            log.debug("data fetched")
            if(len(records)==0):
                return None
            log.debug("entityType="+str(entityType))
            ApiCall.encryptionList.extend(encryptionList)
            ApiCall.records.extend(records)
            ApiCall.scoreTreshold=scoreTreshold[0]
            return(entityType,datalist,preEntity)
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            ExceptionDb.create({"UUID":request_id_var.get(),"function":"ApiRequestFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)

  
        # record=[ele for ele in records if ele.RecogName=="PASSPORT"][0]  
    def getRecord(name):
        log.debug("name="+str(name))
        log.debug("ApiCall.records="+str(ApiCall.records))
        record=[ele for ele in ApiCall.records if ele["RecogName"]==name][0]
        return record
   
          
    
# class CheckData:
#     def check(text,values,key="11111111"):
#         # print("PrivacyService.encrypted_text",Data.encrypted_text)
#         # text=Data.encrypted_text[0]
#         print("=========",text)
#         result=[]
#         for v in values:
#             value=Encrypt.encryptData(key,v)
#             if(value in text):
#                 x=True
#             else:
#                 x=False
#             result.append({"value":v,"isPresent":x})
#         print(result)
#         return result




        

        
