# '''
# License textMIT Licensehttps://mit-license.org/Copyright © 2025 Infosys Ltd.

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# '''
# #from privacy.mappers.mappers import PIIEntity, PIIAnalyzeRequest, PIIAnalyzeResponse,PIIAnonymizeRequest,PIIAnonymizeResponse,PIIImageAnonymizeResponse,PIIImageAnalyzeResponse,PIIImageAnalyzeRequest
# #from privacy.mappers.mappers import PIIEntity, PIIAnalyzeRequest, PIIAnalyzeResponse,PIIAnonymizeRequest,PIIAnonymizeResponse,PIIImageAnonymizeResponse,PIIImageAnalyzeResponse,PIIImageAnalyzeRequest
# import json
# import io, base64
# import random
# from PIL import Image
# import requests
# import pandas as pd
# from privacy.service.easy import EasyOCR
# from privacy.service.azureComputerVision import ComputerVision
# from privacy.mappers.mappers import PIIEntity,PIIAnalyzeRequest,PIIAnalyzeResponse,PIIAnonymizeRequest,PIIAnonymizeResponse,PIIImageAnonymizeResponse,PIIImageAnalyzeResponse,PIIImageAnalyzeRequest, PIIPrivacyShieldResponse
# import os
# import httpx
# from privacy.util.encrypt import EncryptImage

# from typing import List
# from privacy.constants.local_constants import (DELTED_SUCCESS_MESSAGE)
# from privacy.exception.exception import PrivacyNameNotEmptyError, PrivacyException, PrivacyNotFoundError
# from presidio_analyzer import Pattern, pattern_recognizer, AnalyzerEngine, RecognizerRegistry,predefined_recognizers
# from presidio_anonymizer import AnonymizerEngine, DeanonymizeEngine
# from presidio_anonymizer.entities import (RecognizerResult,
#     OperatorResult,
#     OperatorConfig)
# from privacy.config.logger import CustomLogger
# from presidio_image_redactor import ImageRedactorEngine,ImageAnalyzerEngine,ImagePiiVerifyEngine       
# from fastapi import FastAPI, UploadFile
# from fastapi.responses import FileResponse
# from PIL import Image
# import base64
# import io
# import os
# from zipfile import ZipFile,is_zipfile
# from dotenv import load_dotenv
# import tempfile
# import glob
# from pathlib import Path
# import matplotlib.pyplot as plt
# import pydicom
# from presidio_image_redactor import DicomImageRedactorEngine
# from presidio_analyzer.nlp_engine import NlpEngineProvider
# from privacy.util.conf.conf import ConfModle
# from privacy.config.logger import request_id_var
# load_dotenv()
# import numpy as np
# import cv2
# import re
# from faker import Faker
# fake = Faker()

# from privacy.util.fakerEntities import FakeData

# log = CustomLogger()
# import time

# import cv2
# import pytesseract
# from scipy import ndimage
# from PIL import Image as im 
# from privacy.util.special_recognizers.DataListRecognizer import DataListRecognizer
# from privacy.service.__init__ import AttributeDict, registry, admin_par, update_session_dict, error_dict
# from privacy.service.api_req import ApiCall

# from xeger import Xeger
# x = Xeger()

# import contextvars


# class ImageRotation:
#     @staticmethod
#     def float_convertor(val):
#         if val.isdigit():
#             out= float(val)
#         else:
#             out= val
#         return out
#     @staticmethod
#     def get_angle(image):
#         k = pytesseract.image_to_osd(image)
#         out = {i.split(":")[0]: ImageRotation.float_convertor(i.split(":")[-1].strip()) for i in k.rstrip().split("\n")}
#         return out["Rotate"]
#     @staticmethod
#     def rotate_image(image, pre_angle=0):
#         angle=0
#         if(pre_angle==0):
#             angle=ImageRotation.get_angle(image)
#         if(pre_angle==angle):
#             return (image,angle)
#         img_rotated = ndimage.rotate(image, pre_angle-angle)
#         image = im.fromarray(img_rotated)
#         return (image,angle)

        
# class PrivacyService:
    

#     def analyze(self,payload: PIIAnalyzeRequest) -> PIIAnalyzeResponse:
#         error_dict[request_id_var.get()]=[]
#         log.debug("Entering in analyze function")
       
#         log.debug(f"payload: {payload}")
#         try:
#             if payload.exclusion_list is None:
#                 exclusion_list=[]
#             else:
#                 exclusion_list=payload.exclusion_list

#             if payload.portfolio is None:
#                 results = PrivacyService.__analyze(text=payload.input_text,exclusion=exclusion_list)
#             else:
#                 results = PrivacyService.__analyze(text=payload.input_text,acc_name=payload,exclusion=exclusion_list)
#             if results is None:
#                 return PIIAnalyzeResponse()
#             if results== 404:
#                 return results
#             pii_entity_list = []
#             results=sorted(results, key=lambda i: i.start)
            
#             for result in results:
#                 log.debug(f"result: {result}")
#                 pii_entity = PIIEntity(type=result.entity_type,
#                                           beginOffset=result.start,
#                                           endOffset=result.end,
#                                           score=result.score,
#                                           responseText=payload.input_text[result.start:result.end])
#                 log.debug(f"pii_entity: {pii_entity}")
#                 pii_entity_list.append(pii_entity)
#                 del pii_entity

#             log.debug(f"pii_entity_list: {pii_entity_list}")
#             obj_pii_analyze_response = PIIAnalyzeResponse
#             obj_pii_analyze_response.PIIEntities = pii_entity_list
          
#             log.debug("Returning from analyze function")
#             return obj_pii_analyze_response
#         except Exception as e:
#             log.error(str(e))
#             log.error("Line No:"+str(e.__traceback__.tb_lineno))
#             log.error(str(e.__traceback__.tb_frame))
#             error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"textAnalyzeMainFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
#             raise RuntimeError(e)
  
#     @staticmethod
#     def __analyze(text: str,acc_name:any=None,exclusion:any=None):
#         result=[]
        
        
#         try:
#             if acc_name is None:
               
#                 result = analyzer.analyze(text=text,language="en",allow_list=exclusion,return_decision_process = True)
              

#             else:
#                 pre_entity=[]
               
#                 data_list_ent = []
                
#                 response_value=ApiCall.request(acc_name)

#                 if(response_value==None):
#                     return None
#                 if(response_value==404):
                   
#                     return response_value
                
#                 entity_type,datalist,pre_entity=response_value
              
#                 for d in range(len(datalist)):
#                     record=ApiCall.getRecord(entity_type[d])
#                     record=AttributeDict(record)
#                     log.debug("Record====="+str(record))

                   
#                     if(record.RecogType=="Data"):
                            
#                             data_recog=(DataListRecognizer(terms=datalist[d],entitie=[entity_type[d]]))
#                             registry.add_recognizer(data_recog)
#                             update_session_dict(entity_type[d], datalist[d])
#                             data = {entity_type[d]: datalist[d]}
#                             data_list_ent.append(data)
                 
#                     elif(record.RecogType=="Pattern" and record.isPreDefined=="No"):
#                         context_obj=record.Context.split(',')
#                         pattern="|".join(datalist[d])
                        
#                         log.debug("pattern="+str(pattern))
#                         pattern_obj = Pattern(name=entity_type[d],
#                                                        regex=pattern,
#                                                        score=record.Score)
#                         pattern_recog = pattern_recognizer(supported_entity=entity_type[d],
#                                                                    patterns=[pattern_obj],context=context_obj)
#                         registry.add_recognizer(pattern_recog)

                 
#                 results = analyzer.analyze(text=text, language="en",entities=entity_type+pre_entity,allow_list=exclusion,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"])
                     
#                 result.extend(results)
                    

#                 log.debug(f"results: {results}")
#                 log.debug(f"type results: {type(results)}")
                
#             log.debug("result="+str(result))

#             return result
#         except Exception as e:
#             log.error(str(e))
          
#             log.error("Line No:"+str(e.__traceback__.tb_lineno))
#             log.error(str(e.__traceback__.tb_frame))
#             error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"textAnalyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
#             raise RuntimeError(e)
  
#     def anonymize(self,payload: PIIAnonymizeRequest):
#         error_dict[request_id_var.get()]=[]
#         log.debug("Entering in anonymize function")
#         try:
#             Data.encrypted_text.clear()  
           
#             if payload.exclusion_list is None:
#                 exclusion_list=[]
#             else:
#                 exclusion_list=payload.exclusion_list
#             if payload.portfolio is None:
#                 results = PrivacyService.__analyze(text=payload.input_text,exclusion=exclusion_list)
#             else: 
#                 results = PrivacyService.__analyze(text=payload.input_text,acc_name=payload,exclusion=exclusion_list)
                
#             if results is None:
#                 return None

#             if results == 404:

#                 return results
#             dict_operators = {} 
#             if payload.fakeData is True:            
#                 fake_dict_operator = FakeDataGenerate.fake_data_generation(results,payload.input_text)
#                 dict_operators.update(fake_dict_operator)
        

#             encryptionList=[]
#             if payload.portfolio is not None :

#                 encryptionList=admin_par[request_id_var.get()]["encryptionList"]
#             if encryptionList is not None and len(encryptionList) >0 :
#                 for entity in encryptionList:
#                     print("---------------------------")
#                     dict_operators.update({entity: OperatorConfig("hash", {"hash-type": 'md5'})})
#             anonymize_text = anonymizer.anonymize(text=payload.input_text,
#                                                   operators=dict_operators,
#                                                   analyzer_results=results)


#             log.debug(f"anonymize_text: {anonymize_text}")
#             log.debug(f"anonymize_text_item"+ str(anonymize_text.items))

#             obj_PIIAnonymizeResponse = PIIAnonymizeResponse
#             obj_PIIAnonymizeResponse.anonymizedText = anonymize_text.text
#             log.debug("Returning from anonymize function")

#             return obj_PIIAnonymizeResponse
#         except Exception as e:
#             log.error(str(e))
#             log.error("Line No:"+str(e.__traceback__.tb_lineno))
#             log.error(str(e.__traceback__.tb_frame))
#             error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"textAnonimyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
#             raise RuntimeError(e)

#     def encrypt(self,payload: PIIAnonymizeRequest):
#         log.debug("Entering in encrypt function")
        
#         try:
#             Data.encrypted_text.clear()  

#             if payload.exclusion_list is None:
#                 exclusion_list=[]
#             else:
#                 exclusion_list=payload.exclusion_list
#             if payload.portfolio is None:
#                 results = PrivacyService.__analyze(text=payload.input_text,exclusion=exclusion_list)
#             else: 
#                 results = PrivacyService.__analyze(text=payload.input_text,acc_name=payload,exclusion=exclusion_list)

#             if results is None:
#                 return None
#             dict_operators = {} 
            
#             data = "WmZq4t7w!z%C&F)J"
                
#             for i in results:
#                 dict_operators.update({i.entity_type : OperatorConfig("encrypt", {"key": data})})
            
#             anonymize_text = anonymizer.anonymize(text=payload.input_text,
#                                                   operators=dict_operators,
#                                                   analyzer_results=results)
            
#             log.debug("anonymize_text: %s", anonymize_text)
#             log.debug("anonymize_text_item: %s", anonymize_text.items)
            
#             obj_PIIEncryptResponse = PIIEncryptResponse
#             obj_PIIEncryptResponse.text = anonymize_text.text
#             obj_PIIEncryptResponse.items= anonymize_text.items
#             log.debug("Returning from encrypt function")
            
#             return obj_PIIEncryptResponse
        
        
#         except Exception as e:
#             log.error(str(e))
#             log.error("Line No:"+str(e.__traceback__.tb_lineno))
#             log.error(str(e.__traceback__.tb_frame))
#             error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"textAnonimyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
#             raise RuntimeError(e)

#     def decryption(self,payload: PIIDecryptRequest):
#         log.debug("Entering in decrypt function")
       
#         print("payload=====",payload)
#         try:
#             anonymized_text = payload.text
#             anonymized_entities = payload.items
            
#             data = "WmZq4t7w!z%C&F)J"
#             list_ent= []
#             for item in anonymized_entities:
#                 list_ent.append(OperatorResult(start=item.start,
#                                     end=item.end ,
#                                     entity_type= item.entity_type,
#                                     text= item.text,
#                                     operator= item.operator,))
#             anonymized_entities=list_ent    
            
#             deanonymized_result = deanonymizer.deanonymize(text=anonymized_text,
#                                             entities=anonymized_entities,
#                                     operators={"DEFAULT": OperatorConfig("decrypt", {"key": data})},)
            
#             obj_PIIDecryptResponse = PIIDecryptResponse
#             obj_PIIDecryptResponse.decryptedText = deanonymized_result.text
#             log.debug("Returning from anonymize function")

#             return obj_PIIDecryptResponse
            
            
#         except Exception as e:
#             log.error(str(e))
#             log.error("Line No:"+str(e.__traceback__.tb_lineno))
#             log.error(str(e.__traceback__.tb_frame))
#             error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"textAnonimyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
#             raise RuntimeError(e)


#     def image_analyze(self,payload):  
#         error_dict[request_id_var.get()]=[]
#         try:
#             log.debug("Entering in image_analyze function")        
#             payload=AttributeDict(payload)
#             image = Image.open(payload.image.file)
           
            
#             if(payload.rotation_flag):
#                 image,_=ImageRotation.rotateImage(image)
            
#             ocr=None
#             global image_analyzer_engine
#             if(payload.easyocr=="EasyOcr"):
#                 ocr=EasyOCR()
#                 EasyOCR.setMag(payload.mag_ratio)
#                 image_analyzer_engine = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)  

#             if(payload.easyocr=="ComputerVision"):
#                 ocr=ComputerVision()

#                 image_analyzer_engine = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)

#             log.debug("payload="+str(payload))  
#             if(payload.exclusion == None):
#                 exclusion_list=[]
#             else:
#                 exclusion_list=payload.exclusion.split(",")  
#             if(payload.portfolio== None):
#                 results = image_analyzer_engine.analyze(image, allow_list=exclusion_list)
#             else:
#                 result=[]
#                 pre_entity=[]
#                 response_value=ApiCall.request(payload)
#                 if(response_value==None):
#                     return None
#                 if(response_value==404):
#                     return response_value
#                 entity_type,datalist,pre_entity=response_value
               
#                 for d in range(len(datalist)):
#                     record=ApiCall.getRecord(entity_type[d])
#                     record=AttributeDict(record)
                   
    
#                     if(record.RecogType=="Data"):
#                             data_recog=(DataListRecognizer(terms=datalist[d],entitie=[entity_type[d]]))
#                             registry.add_recognizer(data_recog)
                            
#                     elif(record.RecogType=="Pattern" and record.isPreDefined=="No"):
#                         context_obj=record.Context.split(',')
#                         pattern="|".join(datalist[d])
#                         log.debug("pattern="+str(pattern))
#                         pattern_obj = Pattern(name=entity_type[d],
#                                                        regex=pattern,
#                                                        score=record.Score)
#                         pattern_recog = pattern_recognizer(supported_entity=entity_type[d],
#                                                                    patterns=[pattern_obj],context=context_obj)
#                         registry.add_recognizer(pattern_recog)

#                 results = image_analyzer_engine.analyze(image,entities=entity_type+pre_entity, allow_list=exclusion_list,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"])
#                 result.extend(results)
                    
#                 results=result                               

           

#             pii_entity_list = []
#             for result in results:
#                 log.debug(f"result: {result}")
#                 pii_entity = PIIEntity(type=result.entity_type,
#                                           beginOffset=result.start,
#                                           endOffset=result.end,
#                                           score=result.score)
#                 log.debug(f"pii_entity: {pii_entity}")
#                 pii_entity_list.append(pii_entity)
#                 del pii_entity

#             log.debug(f"pii_entity_list: {pii_entity_list}")
#             objPIIAnalyzeResponse = PIIAnalyzeResponse
#             objPIIAnalyzeResponse.PIIEntities = pii_entity_list

#             log.debug("Returning from image_analyze function")
          
#             return objPIIAnalyzeResponse
#         except Exception as e:
#             log.error(str(e))
#             log.error("Line No:"+str(e.__traceback__.tb_lineno))
#             log.error(str(e.__traceback__.tb_frame))
#             error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"imageAnalyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
#             raise RuntimeError(e)


    
#     def temp(payload):          
#         engine = ImageAnalyzerEngine()
        
#         image = Image.open(payload.file)                              
#         results = engine.analyze(image)
        
#         pii_entity_list = []
#         for result in results:
#             log.debug(f"result: {result}")
#             pii_entity_list.append(result.entity_type)
            
            

        
#         return pii_entity_list

   

#     def image_anonymize(self,payload): 
#         log.debug("Entering in image_anonymize function")
#         error_dict[request_id_var.get()]=[]
#         try: 
#             payload=AttributeDict(payload)
           
#             ocr=None
#             global imageRedactorEngine
#             if(payload.easyocr=="EasyOcr"):
#                 ocr=EasyOCR()
#                 EasyOCR.setMag(payload.mag_ratio)

#                 image_analyzer_engine = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)  
#                 imageRedactorEngine = ImageRedactorEngine(image_analyzer_engine=image_analyzer_engine)
#             if(payload.easyocr=="ComputerVision"):
#                 ocr=ComputerVision()
                

#                 image_analyzer_engine = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)  
#                 imageRedactorEngine = ImageRedactorEngine(image_analyzer_engine=image_analyzer_engine)

#             payload=AttributeDict(payload)
#             image = Image.open(payload.image.file)
          
            
#             angle=0
#             if(payload.rotation_flag):
#                 image,angle=ImageRotation.rotateImage(image)
         
           
#             if(payload.exclusion == None):
#                 exclusion_list=[]
#             else:
#                 exclusion_list=payload.exclusion.split(",")
#             if(payload.portfolio== None):
#                 redacted_image = imageRedactorEngine.redact(image, (255, 192, 203), allow_list=exclusion_list)
#                 processed_image_stream = io.BytesIO()
#                 redacted_image.save(processed_image_stream, format='PNG')
#             else:
#                 result=[]
#                 pre_entity=[]
#                 response_value=ApiCall.request(payload)
#                 if(response_value==None):
#                     return None
#                 if(response_value==404):
#                     return response_value
#                 entity_type,datalist,pre_entity=response_value
#                 for d in range(len(datalist)):
#                     record=ApiCall.getRecord(entity_type[d])
#                     record=AttributeDict(record)
                    
#                     if(record.RecogType=="Data"):
#                             data_recog=(DataListRecognizer(terms=datalist[d],entitie=[entity_type[d]]))
#                             registry.add_recognizer(data_recog)
#                     elif(record.RecogType=="Pattern" and record.isPreDefined=="No"):
#                         context_obj=record.Context.split(',')
#                         pattern="|".join(datalist[d])
#                         log.debug("pattern="+str(pattern))
#                         pattern_obj = Pattern(name=entity_type[d],
#                                                        regex=pattern,
#                                                        score=record.Score)
#                         pattern_recog = pattern_recognizer(supported_entity=entity_type[d],
#                                                                    patterns=[pattern_obj],context=context_obj)
#                         registry.add_recognizer(pattern_recog)
                       
#                 redacted_image = imageRedactorEngine.redact(image, (255, 192, 203),entities=entity_type+pre_entity, allow_list=exclusion_list,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"])
                    
#                 processed_image_stream = io.BytesIO()
#                 redacted_image.save(processed_image_stream, format='PNG')
                   
#                 image=redacted_image
                   
#             if(angle!=0 and payload.rotation_flag==True):
#                 redacted_image,angle=ImageRotation.rotateImage(redacted_image,angle)
#                 processed_image_stream = io.BytesIO()
#                 redacted_image.save(processed_image_stream, format='PNG')
          
#             processed_image_bytes = processed_image_stream.getvalue()
#             base64_encoded_image=base64.b64encode(processed_image_bytes)
            
#             SaveImage.save_img(base64_encoded_image)
#             log.debug("Returning from image_anonymize function")
           
#             return base64_encoded_image
#         except Exception as e:
#             log.error(str(e))
#             log.error("Line No:"+str(e.__traceback__.tb_lineno))
#             log.error(str(e.__traceback__.tb_frame))
#             error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"imageAnonimyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
#             raise Exception(e)

#     async def image_masking(main_image,template_image):
#         template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
       
#         _, template_mask = cv2.threshold(template_gray, 1, 255, cv2.THRESH_BINARY)

       
#         result = cv2.matchTemplate(main_image, template_image, cv2.TM_CCOEFF_NORMED)
#         _, max_val, _, max_loc = cv2.minMaxLoc(result)

  
#         template_height, template_width = template_image.shape[:2]

     
#         mask = np.zeros(main_image.shape[:2], dtype=np.uint8)

#         mask[max_loc[1]:max_loc[1] + template_height, max_loc[0]:max_loc[0] + template_width] = 255

       
#         result_with_mask = cv2.bitwise_and(main_image, main_image, mask=cv2.bitwise_not(mask))

#         return result_with_mask

#     def zipimage_anonymize(self,payload):                                            #$$$$$$$$$$$$
#         result=[]
#         in_memory_file=io.BytesIO(payload.file.read())

#         engine = ImageRedactorEngine()
#         log.debug("=="+str(is_zipfile(payload.file)))
                                           
#         with ZipFile(in_memory_file, 'r') as zObject:
#             for file_name in zObject.namelist():
                
#                 log.debug(zObject.namelist())
#                 log.debug("=="+str(type(zObject)))
#                 file_data=zObject.read(file_name)
#                 image=Image.open(io.BytesIO(file_data))
#                 redacted_image = engine.redact(image, (255, 192, 203))
#                 processed_image_stream = io.BytesIO()
#                 redacted_image.save(processed_image_stream, format='PNG')
#                 processed_image_bytes = processed_image_stream.getvalue()
#                 base64_encoded_image=base64.b64encode(processed_image_bytes)
#                 result.append(base64_encoded_image)
#         return result
    
#     def image_verify(self,payload):  
#            error_dict[request_id_var.get()]=[]
#            log.debug("Entering in image_verify function")
#            try:
               
#                 global imagePiiVerifyEngine
#                 payload=AttributeDict(payload)
#                 image = Image.open(payload.image.file)
         
#                 if(payload.exclusion == None):
#                     exclusion_list=[]
#                 else:
#                     exclusion_list=payload.exclusion.split(",")

#                 if(payload.portfolio== None):
#                     verify_image = imagePiiVerifyEngine.verify(image, allow_list=exclusion_list)
#                     processed_image_stream = io.BytesIO()
#                     verify_image.save(processed_image_stream, format='PNG')

#                 else:
#                     pre_entity=[]
#                     response_value=ApiCall.request(payload)
#                     if(response_value==None):
#                         return None
#                     if(response_value==404):
                 
#                         return response_value
#                     entity_type,datalist,pre_entity=response_value

                  
#                     for d in range(len(datalist)):
#                         record=ApiCall.getRecord(entity_type[d])
#                         record=AttributeDict(record)

#                         if(record.RecogType=="Data"):
#                                 data_recog=(DataListRecognizer(terms=datalist[d],entitie=[entity_type[d]]))
#                                 registry.add_recognizer(data_recog)
#                         elif(record.RecogType=="Pattern" and record.isPreDefined=="No"):
#                             context_obj=record.Context.split(',')
#                             pattern="|".join(datalist[d])
#                             log.debug("pattern="+str(pattern))
#                             pattern_obj = Pattern(name=entity_type[d],
#                                                            regex=pattern,
#                                                            score=record.Score)
#                             pattern_recog = pattern_recognizer(supported_entity=entity_type[d],
#                                                                        patterns=[pattern_obj],context=context_obj)
#                             registry.add_recognizer(pattern_recog)
#                     verify_image = imagePiiVerifyEngine.verify(image,entities=entity_type+pre_entity, allow_list=exclusion_list,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"])
                    
#                     processed_image_stream = io.BytesIO()
#                     verify_image.save(processed_image_stream, format='PNG')
                    
#                     image=verify_image
                      

#                 processed_image_bytes = processed_image_stream.getvalue()
#                 base64_encoded_image=base64.b64encode(processed_image_bytes)
#                 SaveImage.save_img(base64_encoded_image)
#                 log.debug("Returning from image_verify function")
         
#                 return base64_encoded_image
#            except Exception as e:
#                 log.error(str(e))
#                 log.error("Line No:"+str(e.__traceback__.tb_lineno))
#                 log.error(str(e.__traceback__.tb_frame))
#                 error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"imageVeryFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
#                 raise Exception(e)
       
#     def image_encryption(self,payload):
#             error_dict[request_id_var.get()]=[]
#             log.debug("Entering in image_encryption function")
#             try:
#                 payload=AttributeDict(payload)
#                 EncryptImage.entity.clear()

#                 ocr=None
#                 global encryptImageEngin
#                 if(payload.easyocr=="EasyOcr"):
#                     ocr=EasyOCR()
#                     EasyOCR.setMag(payload.mag_ratio)
#                     image_analyzer_engine = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)
#                     encryptImageEngin=EncryptImage(image_analyzer_engine=image_analyzer_engine) #
#                 if(payload.easyocr=="ComputerVision"):
#                     ocr=ComputerVision()

#                     image_analyzer_engine = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)  
#                     encryptImageEngin=EncryptImage(image_analyzer_engine=image_analyzer_engine)

#                 payload=AttributeDict(payload)
#                 image = Image.open(payload.image.file)
#                 angle=0
#                 if(payload.rotation_flag):
#                     image,angle=ImageRotation.rotateImage(image)
               
#                 encrypt_mapper=[]
#                 if(payload.exclusion == None):
#                     exclusion_list=[]
#                 else:
#                     exclusion_list=payload.exclusion.split(",")
#                 encryptImageEngin.getText(image)
#                 if(payload.portfolio== None):
#                     redacted_image = encryptImageEngin.imageAnonimyze(image, (255, 192, 203), allow_list=exclusion_list)
#                     processed_image_stream = io.BytesIO()
#                     redacted_image.save(processed_image_stream, format='PNG')
#                 else:
#                     result=[]
#                     pre_entity=[]
#                     response_value=ApiCall.request(payload)
#                     if(response_value==None):
#                         return None
#                     if(response_value==404):
#                         return response_value
#                     encryptionList=admin_par[request_id_var.get()]["encryptionList"]
#                     entity_type,datalist,pre_entity=response_value
#                     for d in range(len(datalist)):
#                         record=ApiCall.getRecord(entity_type[d])
#                         record=AttributeDict(record)
                     
#                         if(record.RecogType=="Data"):
#                                 data_recog=(DataListRecognizer(terms=datalist[d],entitie=[entity_type[d]]))
#                                 registry.add_recognizer(data_recog)
                               
#                         elif(record.RecogType=="Pattern" and record.isPreDefined=="No"):
#                             context_obj=record.Context.split(',')
#                             pattern="|".join(datalist[d])
#                             log.debug("pattern="+str(pattern))
#                             pattern_obj = Pattern(name=entity_type[d],
#                                                            regex=pattern,
#                                                            score=record.Score)
#                             pattern_recog = pattern_recognizer(supported_entity=entity_type[d],
#                                                                        patterns=[pattern_obj],context=context_obj)
#                             registry.add_recognizer(pattern_recog)
                           
#                     redacted_image = encryptImageEngin.imageAnonimyze(image, (255, 192, 203),encryptionList=encryptionList,entities=entity_type+pre_entity, allow_list=exclusion_list,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"])
#                     processed_image_stream = io.BytesIO()
#                     redacted_image.save(processed_image_stream, format='PNG')
#                     image=redacted_image
                       
                    
#                     EncryptImage.dis()
#                     res=encryptImageEngin.encrypt(redacted_image,encryptionList=encryptionList)
#                     redacted_image=res[0]
#                     encrypt_mapper=res[1]
#                     processed_image_stream = io.BytesIO()
#                     redacted_image.save(processed_image_stream, format='PNG')
                    
#                 if(angle!=0 and payload.rotation_flag==True):
#                     redacted_image,angle=ImageRotation.rotateImage(redacted_image,angle)
#                     processed_image_stream = io.BytesIO()
#                     redacted_image.save(processed_image_stream, format='PNG')
               
#                 processed_image_bytes = processed_image_stream.getvalue()
#                 base64_encoded_image=base64.b64encode(processed_image_bytes)

#                 SaveImage.save_img(base64_encoded_image)
#                 obj={"map":encrypt_mapper,"img":base64_encoded_image}
#                 log.debug("Returning from image_encryption function")
               
#                 return obj
#             except Exception as e:
#                 log.error(str(e))
#                 log.error("Line No:"+str(e.__traceback__.tb_lineno))
#                 log.error(str(e.__traceback__.tb_frame))
#                 error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"imageHashifyFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
#                 raise RuntimeError(e)


    
    
    
    
#     def privacy_shield(self,payload: PIIPrivacyShieldRequest) -> PIIPrivacyShieldResponse:
#         log.debug("Entering in privacy_shield function")
#         log.debug(f"payload: {payload}")

#         res = []
#         tot_ent=[]
#         enres=[]
       
#         log.debug("response="+str(res))
#         if payload.portfolio is None:
#             response_value=ApiCall.request(payload)
#             if response_value is None:
#                 obj_response = PIIPrivacyShieldResponse()
#                 obj_response.privacyCheck = []
#                 return obj_response
#             if response_value == 404:
#                 return response_value
#             entity_type, _, pre_entity = response_value

#             results = PrivacyService.__analyze(text=payload.input_text)
          
#             record=[ele for ele in admin_par[request_id_var.get()]["records"] if ele["isPreDefined"]=="Yes"]
            
#             for i in record:
#                 i=AttributeDict(i)
#                 tot_ent.append(i.RecogName)
#         else:
#             response_value = ApiCall.request(payload)
#             if response_value is None:
#                 obj_response = PIIPrivacyShieldResponse()
#                 obj_response.privacyCheck = []
#                 return obj_response
#             if response_value == 404:
#                 return response_value
#             entity_type, _, pre_entity = response_value

#             entity_type.extend(pre_entity)

#             tot_ent = entity_type

#             results = PrivacyService.__analyze(text=payload.input_text, acc_name=payload)

#         value = payload.input_text
#         pii_entity_list = []
#         results = sorted(results, key=lambda i: i.start)
#         for result in results:
#             log.debug(f"result: {result}")
#             enres.append({"type": result.entity_type, "start": result.start, "end": result.end, "value": value[result.start:result.end]})
           
#             log.debug(f"pii_entity: {enres}")
            

#         if(len(enres)==0):
#             temp= "Passed"
#         else:
#             temp = "Failed"

#         objent = PrivacyShield(
#              entitiesRecognised=enres,
#              entitiesConfigured= tot_ent,
#              result=temp
#         )
#         pii_entity_list.append(objent)
#         log.debug(f"pii_entity_list: {pii_entity_list}")
        
#         objPIIAnalyzeResponse = PIIPrivacyShieldResponse()
#         objPIIAnalyzeResponse.privacyCheck = pii_entity_list


#         log.debug("objPIIAnalyzeResponse="+str(objPIIAnalyzeResponse.privacyCheck))
#         log.debug("Returning from privacyShield function")
#         return objPIIAnalyzeResponse
      

# class FakeDataGenerate:
#     def fake_data_generation(self,results,input_text):
#         fake_data_dict = {}
#         for i in results:
#             method_name = i.entity_type.lower()
#             if hasattr(FakeData, method_name):
#                 ent = getattr(FakeData, method_name)
#                 fake_data_dict.update({i.entity_type: OperatorConfig("replace", {"new_value": ent()})})
#             elif i.entity_type in get_session_dict():
#                 ent_value =get_session_dict()[i.entity_type]
                       
#                 log.debug("Value of ent_value 342========"+str(ent_value))
#                 text = str(input_text[i.start:i.end])
#                 print("text===",text)
#                 random_data=""
#                 while True:
#                     if text in ent_value:
#                         random_data = random.choice(ent_value)
#                         print("RNDAOM dATA 348===",random_data)
#                         if random_data.lower() != str(input_text[i.start:i.end]).lower()  :
#                             fake_data_dict.update({i.entity_type: OperatorConfig("replace", {"new_value": random_data})})
#                             ent_value.remove(random_data)
#                             break
#                     else:
#                         print("Value of ent_value 344========",text)
#                         break
                        
                      
#                 fake_data_dict.update({i.entity_type: OperatorConfig("replace", {"new_value": random_data})})
                    
#             else:
               
#                 decision_process = i.analysis_explanation
               
#                 if(decision_process==None):        
#                     continue
#                 pattern = decision_process.pattern        
               
#                 t=x.xeger(pattern)
#                 p=r'[\x00-\x1F\x7F-\xFF]'  
                      
#                 t1=re.sub(p, ' ', t)
                      
#                 fake_data_dict.update({i.entity_type: OperatorConfig("replace", {"new_value": t1})})
                       
                
                
#         return fake_data_dict

# class DICOM:
#     @staticmethod
#     def dcm_to_png(dcm_obj):
#         plt.clf()
#         plt.imshow(dcm_obj.pixel_array,cmap=plt.cm.bone)
#         plt.axis('off')
#         buffer=io.BytesIO()
#         plt.savefig(buffer,format='png', bbox_inches='tight', pad_inches=0)
#         buffer.seek(0)
#         return base64.b64encode(buffer.getvalue())
        
    
   
    
#     def read_dicom(self,payload):
#         error_dict[request_id_var.get()]=[]
#         log.debug("Entering in readDicom function")
#         try:
          
#             EncryptImage.entity.clear()
           
#             dicom_engine = DicomImageRedactorEngine()
#             dicom_instance = pydicom.dcmread(payload.file)
            
#             redacted_dicom_instance = dicom_engine.redact(dicom_instance, fill="contrast") 
#             original=DICOM.dcm_to_png(dicom_instance)
#             redacted=DICOM.dcm_to_png(redacted_dicom_instance)

#             obj={"original":original,"anonymize":redacted}
#             log.debug("Returning from readDicom function")
#             return obj
  
#         except Exception as e:
#             log.error(str(e))
#             log.error("Line No:"+str(e.__traceback__.tb_lineno))
#             log.error(str(e.__traceback__.tb_frame))
#             error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"readDICOMFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
#             raise RuntimeError(e)
  
    




# class SaveImage:
#     @staticmethod
#     def save_img(img_data):
        
    
#         with open("imageToSave.png", "wb") as fh:
#             fh.write(base64.decodebytes(img_data))




        

        
