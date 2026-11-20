'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


import io, base64
from PIL import Image,ImageDraw
from privacy.service.easy import EasyOCR
from privacy.service.azureComputerVision import ComputerVision
from privacy.mappers.mappers import (PIIAnalyzeRequest,PIIAnalyzeResponse,PIIImageAnalyze,PIIImageAnalyzeRequest,PIIImageAnonymizeResponse)
from privacy.util.encrypt import EncryptImage
from typing import List
from privacy.constants.local_constants import (DELTED_SUCCESS_MESSAGE)
from privacy.config.logger import CustomLogger
from zipfile import ZipFile,is_zipfile
from dotenv import load_dotenv
from privacy.config.logger import request_id_var
load_dotenv()
import numpy as np
import cv2
log = CustomLogger()
import time
import pytesseract
from scipy import ndimage
from PIL import Image as im 
from privacy.util.special_recognizers.DataListRecognizer import DataListRecognizer
from privacy.service.__init__ import *
from privacy.service.api_req import ApiCall
from privacy.service.textPrivacy import TextPrivacy
import re


def _open_image_detached(file_obj):
    with Image.open(file_obj) as opened_image:
        return opened_image.copy()


def _open_image_from_bytes(image_bytes):
    with io.BytesIO(image_bytes) as image_stream:
        with Image.open(image_stream) as opened_image:
            return opened_image.copy()

class ImageRotation:
    @staticmethod
    def float_convertor(x):
        if x.isdigit():
            out= float(x)
        else:
            out= x
        return out 
    @staticmethod
    def get_angle(image):
        k = pytesseract.image_to_osd(image)
        out = {i.split(":")[0]: ImageRotation.float_convertor(i.split(":")[-1].strip()) for i in k.rstrip().split("\n")}
        return out["Rotate"]
    @staticmethod
    def rotate_image(image,pre_angle=0):
        angle=0
        if(pre_angle==0):
            angle=ImageRotation.get_angle(image)
        if(pre_angle==angle):
            return (image,angle)
        img_rotated = ndimage.rotate(image, pre_angle-angle)
        image = im.fromarray(img_rotated)
        return (image,angle)

class ImagePrivacy:
    @staticmethod
    def image_analyze(payload):  
        error_dict[request_id_var.get()]=[]
        try:
            log.debug("Entering in image_analyze function")        
            payload=AttributeDict(payload)
            image = _open_image_detached(payload.image.file)
            if(payload.rotation_flag):
                image,angle=ImageRotation.rotate_image(image)
            global imageAnalyzerEngine
            analyzer,imageAnalyzerEngine,imageRedactorEngine,imagePiiVerifyEngine,encryptImageEngin=select_nlp(payload.nlp)
            
            ocr=None
            if(payload.easyocr=="Tesseract"):
                log.debug("TESSERACT SELECTED")
                imageAnalyzerEngine = ImageAnalyzerEngine(analyzer_engine=analyzer) 
            if(payload.easyocr=="EasyOcr"):
                ocr=EasyOCR()
                EasyOCR.setMag(payload.mag_ratio)
                imageAnalyzerEngine = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)  
            if(payload.easyocr=="ComputerVision"):
                ocr=ComputerVision()

                imageAnalyzerEngine = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)  
            
            log.debug("payload="+str(payload))  
            if(payload.pii_entities_to_be_redacted == None):
                pii_entities_to_be_redacted=None
            else:
                pii_entities_to_be_redacted = payload.pii_entities_to_be_redacted.split(',')
            
            
            sp_recog=None
            if(payload.nlp=="roberta"):
                sp_recog=[roberta_recog]
            if(payload.nlp=="ranha"):
                if(pii_entities_to_be_redacted==None and  payload.account==None):
                    pii_entities_to_be_redacted=list(set(ranha_recog.supported_entities+registry.get_supported_entities()))
                sp_recog=[ranha_recog]
            if(payload.exclusion == None):
                exclusion_list=[]
            else:
                exclusion_list=payload.exclusion.split(",") 
            if payload.nlp == "llama":
                if ocr:
                    ocr_text = ocr.extract_text(image)
                else:
                    ocr_text = pytesseract.image_to_string(image)

                privacyobj=TextPrivacy()
                results = privacyobj.llama_analyze( input_text=ocr_text,
                    exclusion=exclusion_list,
                    pii_entities_to_be_redacted=pii_entities_to_be_redacted,)
                pii_entity_list = []
                for result in results:
                    pii_entity_obj = PIIImageAnalyze(
                        type=result.entity_type,
                        start=result.start,
                        end=result.end,
                        score=result.score
                    )
                    pii_entity_list.append(pii_entity_obj)

                objPIIAnalyzeResponse = PIIAnalyzeResponse
                objPIIAnalyzeResponse.PIIEntities = pii_entity_list

                log.debug("Returning from image_analyze function (LLaMA)")
                return objPIIAnalyzeResponse
            if(payload.portfolio== None):
                if(pii_entities_to_be_redacted == None):
                    results = imageAnalyzerEngine.analyze(image, allow_list=exclusion_list,score_threshold=payload.score_threshold,ad_hoc_recognizers=sp_recog)
                else:
                    try:
                        results = imageAnalyzerEngine.analyze(image,entities=pii_entities_to_be_redacted, allow_list=exclusion_list,score_threshold=payload.score_threshold,ad_hoc_recognizers=sp_recog)
                    except Exception as e:
                        return 482
            else:
                result=[]
                pre_entity=[]
                response_value=ApiCall.request(payload)
                if(response_value==None):
                    return None
                if(response_value==404):
                    return response_value
                entity_type,datalist,pre_entity=response_value
                for d in range(len(datalist)):
                    record=ApiCall.getRecord(entity_type[d])
                    record=AttributeDict(record)
    
                    if(record.RecogType=="Data"):
                            data_recog=(DataListRecognizer(terms=datalist[d],entitie=[entity_type[d]]))
                            registry.add_recognizer(data_recog)
                    elif(record.RecogType=="Pattern" and record.isPreDefined=="No"):
                        context_obj=record.Context.split(',')
                        pattern="|".join(datalist[d])
                        log.debug("pattern="+str(pattern))
                        pattern_obj = Pattern(name=entity_type[d],
                                                       regex=pattern,
                                                       score=record.Score)
                        pattern_recog = PatternRecognizer(supported_entity=entity_type[d],
                                                                   patterns=[pattern_obj],context=context_obj)
                        registry.add_recognizer(pattern_recog)
                results = imageAnalyzerEngine.analyze(image,entities=entity_type+pre_entity, allow_list=exclusion_list,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"],ad_hoc_recognizers=sp_recog)
                result.extend(results)
                results=result                               

            unique_entities = set()
            entity_max_end_map = {}
            pii_entity_list = []
            for result in results:
                log.debug(f"result: {result}")
               
                entity_key = (result.entity_type, result.start)

                
                if entity_key in entity_max_end_map:
                    if result.end > entity_max_end_map[entity_key].end:
                        log.debug(f"Updating max end for {entity_key}: {entity_max_end_map[entity_key].end} -> {result.end}")
                        entity_max_end_map[entity_key] = result
                else:
                    entity_max_end_map[entity_key] = result

            for result in entity_max_end_map.values():
               entity_detected = (result.entity_type, result.start, result.end)
               if entity_detected not in unique_entities:
                unique_entities.add(entity_detected)
                pii_entity_obj = PIIImageAnalyze(
                                    type=result.entity_type,
                                    start=result.start,
                                    end=result.end,
                                    score=result.score)
      
                log.debug(f"pii_entity_obj: {pii_entity_obj}")
                pii_entity_list.append(pii_entity_obj)
                del pii_entity_obj


            log.debug(f"pii_entity_list: {pii_entity_list}")
            objPIIAnalyzeResponse = PIIAnalyzeResponse
            objPIIAnalyzeResponse.PIIEntities = pii_entity_list

            log.debug("Returning from image_analyze function")
            return objPIIAnalyzeResponse
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"imageAnalyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise RuntimeError


    
    def temp(payload):          
        engine = ImageAnalyzerEngine()
        
        image = _open_image_detached(payload.file)
        results = engine.analyze(image)
        pii_entity_list = []
        for result in results:
            log.debug(f"result: {result}")
            pii_entity_list.append(result.entity_type)
            
            

        
        return pii_entity_list

   

    def image_anonymize(payload): 
        log.debug("Entering in image_anonymize function")
        error_dict[request_id_var.get()]=[]
        try: 
            payload=AttributeDict(payload)
            image = _open_image_detached(payload.image.file)
            if(payload.pii_entities_to_be_redacted == None):
                pii_entities_to_be_redacted=None
            else:
                pii_entities_to_be_redacted = payload.pii_entities_to_be_redacted.split(',')
            if(payload.exclusion == None):
                exclusion_list=[]
            else:
                exclusion_list=payload.exclusion.split(",")
            
            
            angle=0
            if(payload.rotation_flag):
                image,angle=ImageRotation.rotate_image(image)
            if payload.nlp == "llama":
                log.debug("Using LLaMA model — skipping select_nlp")

                
                if payload.easyocr == "Tesseract":
                    ocr_text = pytesseract.image_to_string(image)
                    ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                elif payload.easyocr == "EasyOcr":
                    ocr = EasyOCR()
                    EasyOCR.setMag(payload.mag_ratio)
                    ocr_text = ocr.extract_text(image)
                    ocr_data = ocr.extract_data(image)
                elif payload.easyocr == "ComputerVision":
                    ocr = ComputerVision()
                    ocr_text = ocr.extract_text(image)
                    ocr_data = ocr.extract_data(image)

               
                privacyobj = TextPrivacy()
                llama_results = privacyobj.llama_analyze(input_text=ocr_text,
                exclusion=exclusion_list,
                pii_entities_to_be_redacted=pii_entities_to_be_redacted)

                draw = ImageDraw.Draw(image)
                for idx, word in enumerate(ocr_data["text"]):
                    for pii in llama_results:
                        if word and word.strip() and re.search(re.escape(word.strip()), ocr_text[pii.start:pii.end]):
                            x = ocr_data["left"][idx]
                            y = ocr_data["top"][idx]
                            w = ocr_data["width"][idx]
                            h = ocr_data["height"][idx]
                            draw.rectangle([x, y, x + w, y + h], fill=(255, 192, 203))

                if angle != 0 and payload.rotation_flag:
                    image, _ = ImageRotation.rotate_image(image, angle)

                processed_image_stream = io.BytesIO()
                image.save(processed_image_stream, format='PNG')
                processed_image_bytes = processed_image_stream.getvalue()
                base64_encoded_image = base64.b64encode(processed_image_bytes)
                SaveImage.save_img(base64_encoded_image)
                log.debug("Returning from image_anonymize function (LLaMA)")
                return base64_encoded_image
            global imageRedactorEngine
            analyzer,imageAnalyzerEngine,imageRedactorEngine,imagePiiVerifyEngine,encryptImageEngin=select_nlp(payload.nlp)
            
            ocr=None
            if(payload.easyocr=="Tesseract"):
                log.debug("TESSERACT SELECTED")
                imageAnalyzerEngine = ImageAnalyzerEngine(analyzer_engine=analyzer) 
                imageRedactorEngine = ImageRedactorEngine(image_analyzer_engine=imageAnalyzerEngine)
            if(payload.easyocr=="EasyOcr"):
                ocr=EasyOCR()
                EasyOCR.setMag(payload.mag_ratio)

                imageAnalyzerEngine = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)  
                imageRedactorEngine = ImageRedactorEngine(image_analyzer_engine=imageAnalyzerEngine)
            if(payload.easyocr=="ComputerVision"):
                ocr=ComputerVision()

                imageAnalyzerEngine = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)  
                imageRedactorEngine = ImageRedactorEngine(image_analyzer_engine=imageAnalyzerEngine)
            payload=AttributeDict(payload)   
            sp_recog=None
            if(payload.nlp=="roberta"):
                sp_recog=[roberta_recog]
            if(payload.nlp=="ranha"):
                if(pii_entities_to_be_redacted==None and  payload.account==None):
                    pii_entities_to_be_redacted=list(set(ranha_recog.supported_entities+registry.get_supported_entities()))
                sp_recog=[ranha_recog]
 
            
                
                
            if(payload.portfolio== None):
                if(pii_entities_to_be_redacted == None):
                    redacted_image = imageRedactorEngine.redact(image, (255, 192, 203), allow_list=exclusion_list,score_threshold=payload.score_threshold,ad_hoc_recognizers=sp_recog)
                else:
                    try:
                        redacted_image = imageRedactorEngine.redact(image, (255, 192, 203),entities=pii_entities_to_be_redacted, allow_list=exclusion_list,score_threshold=payload.score_threshold,ad_hoc_recognizers=sp_recog)
                    
                    except Exception as e:
                      
                        return 482
              
                processed_image_stream = io.BytesIO()
                redacted_image.save(processed_image_stream, format='PNG')
            else:
                result=[]
                pre_entity=[]
                response_value=ApiCall.request(payload)
                if(response_value==None):
                    return None
                if(response_value==404):
                    return response_value
                entity_type,datalist,pre_entity=response_value
                for d in range(len(datalist)):
                    record=ApiCall.getRecord(entity_type[d])
                    record=AttributeDict(record)
                    
                    if(record.RecogType=="Data"):
                            data_recog=(DataListRecognizer(terms=datalist[d],entitie=[entity_type[d]]))
                            registry.add_recognizer(data_recog)
                    elif(record.RecogType=="Pattern" and record.isPreDefined=="No"):
                        context_obj=record.Context.split(',')
                        pattern="|".join(datalist[d])
                        log.debug("pattern="+str(pattern))
                        pattern_obj = Pattern(name=entity_type[d],
                                                       regex=pattern,
                                                       score=record.Score)
                        pattern_recog = PatternRecognizer(supported_entity=entity_type[d],
                                                                   patterns=[pattern_obj],context=context_obj)
                        registry.add_recognizer(pattern_recog)

                redacted_image = imageRedactorEngine.redact(image, (255, 192, 203),entities=entity_type+pre_entity, allow_list=exclusion_list,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"],ad_hoc_recognizers=sp_recog)
                processed_image_stream = io.BytesIO()
                redacted_image.save(processed_image_stream, format='PNG')
                image=redacted_image
                   
            if(angle!=0 and payload.rotation_flag==True):
                redacted_image,angle=ImageRotation.rotate_image(redacted_image,angle)
                processed_image_stream = io.BytesIO()
                redacted_image.save(processed_image_stream, format='PNG')
            processed_image_bytes = processed_image_stream.getvalue()
            base64_encoded_image=base64.b64encode(processed_image_bytes)
            SaveImage.save_img(base64_encoded_image)
            log.debug("Returning from image_anonymize function")
            return base64_encoded_image
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"imageAnonimyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise RuntimeError(e)

    async def image_masking(self,main_image,template_image):
        template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
        _, _= cv2.threshold(template_gray, 1, 255, cv2.THRESH_BINARY)

        result = cv2.matchTemplate(main_image, template_image, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(result)

        template_height, template_width = template_image.shape[:2]

        mask = np.zeros(main_image.shape[:2], dtype=np.uint8)

        mask[max_loc[1]:max_loc[1] + template_height, max_loc[0]:max_loc[0] + template_width] = 255

        result_with_mask = cv2.bitwise_and(main_image, main_image, mask=cv2.bitwise_not(mask))

        return result_with_mask
    @staticmethod
    def zip_image_anonymize(payload):                                            #$$$$$$$$$$$$
        result=[]
        in_memory_file=io.BytesIO(payload.file.read())

        engine = ImageRedactorEngine()
        log.debug("=="+str(is_zipfile(payload.file)))
                                           
        with ZipFile(in_memory_file, 'r') as zObject:
            for file_name in zObject.namelist():
                
                log.debug(zObject.namelist())
                log.debug("=="+str(type(zObject)))
                file_data=zObject.read(file_name)
                image = _open_image_from_bytes(file_data)
                redacted_image = engine.redact(image, (255, 192, 203))
                processed_image_stream = io.BytesIO()
                redacted_image.save(processed_image_stream, format='PNG')
                processed_image_bytes = processed_image_stream.getvalue()
                base64_encoded_image=base64.b64encode(processed_image_bytes)
                result.append(base64_encoded_image)
        return result
    @staticmethod
    def image_verify(payload):  
           error_dict[request_id_var.get()]=[]
           log.debug("Entering in image_verify function")
           try:
                global imagePiiVerifyEngine
                analyzer,imageAnalyzerEngine,imageRedactorEngine,imagePiiVerifyEngine,encryptImageEngin=select_nlp(payload.nlp)
            
                payload=AttributeDict(payload)
                image = _open_image_detached(payload.image.file)
                if(payload.exclusion == None):
                    exclusion_list=[]
                else:
                    exclusion_list=payload.exclusion.split(",")

                if(payload.portfolio== None):
                    verify_image = imagePiiVerifyEngine.verify(image, allow_list=exclusion_list)
                    processed_image_stream = io.BytesIO()
                    verify_image.save(processed_image_stream, format='PNG')

                else:
                    pre_entity=[]
                    response_value=ApiCall.request(payload)
                    if(response_value==None):
                        return None
                    if(response_value==404):
                        return response_value
                    entity_type,datalist,pre_entity=response_value

                    for d in range(len(datalist)):
                        record=ApiCall.getRecord(entity_type[d])
                        record=AttributeDict(record)

                        if(record.RecogType=="Data"):
                                data_recog=(DataListRecognizer(terms=datalist[d],entitie=[entity_type[d]]))
                                registry.add_recognizer(data_recog)
                        elif(record.RecogType=="Pattern" and record.isPreDefined=="No"):
                            context_obj=record.Context.split(',')
                            pattern="|".join(datalist[d])
                            log.debug("pattern="+str(pattern))
                            pattern_obj = Pattern(name=entity_type[d],
                                                           regex=pattern,
                                                           score=record.Score)
                            pattern_recog = PatternRecognizer(supported_entity=entity_type[d],
                                                                       patterns=[pattern_obj],context=context_obj)
                            registry.add_recognizer(pattern_recog)
                    verify_image = imagePiiVerifyEngine.verify(image,entities=entity_type+pre_entity, allow_list=exclusion_list,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"])
                    processed_image_stream = io.BytesIO()
                    verify_image.save(processed_image_stream, format='PNG')
                    image=verify_image
                        
                processed_image_bytes = processed_image_stream.getvalue()
                base64_encoded_image=base64.b64encode(processed_image_bytes)
                SaveImage.save_img(base64_encoded_image)
                log.debug("Returning from image_verify function")
                return base64_encoded_image
           except Exception as e:
                log.error(str(e))
                log.error("Line No:"+str(e.__traceback__.tb_lineno))
                log.error(str(e.__traceback__.tb_frame))
                error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"imageVeryFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                raise RuntimeError(e)
    @staticmethod   
    def image_encryption(payload):
            error_dict[request_id_var.get()]=[]
            log.debug("Entering in image_encryption function")
            try:
                payload=AttributeDict(payload)
                EncryptImage.entity.clear()

                ocr=None
                global encryptImageEngin
                analyzer,imageAnalyzerEngine,imageRedactorEngine,imagePiiVerifyEngine,encryptImageEngin=select_nlp(payload.nlp)
            
                if(payload.easyocr=="Tesseract"):
                    log.debug("TESSERACT SELECTED")
                    imageAnalyzerEngine = ImageAnalyzerEngine(analyzer_engine=analyzer)
                    encryptImageEngin=EncryptImage(image_analyzer_engine=imageAnalyzerEngine) #
                if(payload.easyocr=="EasyOcr"):
                    ocr=EasyOCR()
                    EasyOCR.setMag(payload.mag_ratio)
                    imageAnalyzerEngine = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)
                    encryptImageEngin=EncryptImage(image_analyzer_engine=imageAnalyzerEngine) #
                if(payload.easyocr=="ComputerVision"):
                    ocr=ComputerVision()

                    imageAnalyzerEngine = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)  
                    encryptImageEngin=EncryptImage(image_analyzer_engine=imageAnalyzerEngine)
               
                payload=AttributeDict(payload)
                image = _open_image_detached(payload.image.file)
                angle=0
                if(payload.rotation_flag):
                    image,angle=ImageRotation.rotate_image(image)
               
                encrypt_mapper=[]
                if(payload.exclusion == None):
                    exclusion_list=[]
                else:
                    exclusion_list=payload.exclusion.split(",")
                encryptImageEngin.get_text(image)
                
                if(payload.pii_entities_to_be_hashified== None):
                    hash_list=None
                else:
                    hash_list = payload.pii_entities_to_be_hashified.split(',')
                    
                sp_recog=None
                if(payload.nlp=="roberta"):
                    sp_recog=[roberta_recog]
                if(payload.nlp=="ranha"):
                    if(hash_list==None and  payload.account==None):
                        hash_list=list(set(ranha_recog.supported_entities+registry.get_supported_entities()))
                    sp_recog=[ranha_recog]
                if(payload.portfolio== None):
                    
                    if(hash_list==None):
                        redacted_image = encryptImageEngin.image_anonymize(image, (255, 192, 203), allow_list=exclusion_list,score_threshold=payload.score_threshold,ad_hoc_recognizers=sp_recog)
                        processed_image_stream = io.BytesIO()
                        redacted_image.save(processed_image_stream, format='PNG')
                    else:
                        redacted_image = encryptImageEngin.image_anonymize(image, (255, 192, 203), allow_list=exclusion_list,entities=hash_list,encryption_list=hash_list,score_threshold=payload.score_threshold,ad_hoc_recognizers=sp_recog)
                        processed_image_stream = io.BytesIO()
                        redacted_image.save(processed_image_stream, format='PNG')
                        res=encryptImageEngin.encrypt(redacted_image,encryption_list=hash_list)
                        redacted_image=res[0]
                        encrypt_mapper=res[1]
                        processed_image_stream = io.BytesIO()
                        redacted_image.save(processed_image_stream, format='PNG')
                else:
                    pre_entity=[]
                    response_value=ApiCall.request(payload)
                    if(response_value==None):
                        return None
                    if(response_value==404):
                        return response_value
                    encryptionList=admin_par[request_id_var.get()]["encryptionList"]
                    entity_type,datalist,pre_entity=response_value
                    for d in range(len(datalist)):
                        record=ApiCall.getRecord(entity_type[d])
                        record=AttributeDict(record)                     
                        if(record.RecogType=="Data"):
                                data_recog=(DataListRecognizer(terms=datalist[d],entitie=[entity_type[d]]))
                                registry.add_recognizer(data_recog)
                        elif(record.RecogType=="Pattern" and record.isPreDefined=="No"):
                            context_obj=record.Context.split(',')
                            pattern="|".join(datalist[d])
                            log.debug("pattern="+str(pattern))
                            pattern_obj = Pattern(name=entity_type[d],
                                                           regex=pattern,
                                                           score=record.Score)
                            pattern_recog = PatternRecognizer(supported_entity=entity_type[d],
                                                                       patterns=[pattern_obj],context=context_obj)
                            registry.add_recognizer(pattern_recog)
                    redacted_image = encryptImageEngin.image_anonymize(image, (255, 192, 203),encryption_list=encryptionList,entities=entity_type+pre_entity, allow_list=exclusion_list,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"],ad_hoc_recognizers=sp_recog)
                    processed_image_stream = io.BytesIO()
                    redacted_image.save(processed_image_stream, format='PNG')
                    image=redacted_image
                    EncryptImage.dis()
                    res=encryptImageEngin.encrypt(redacted_image,encryption_list=encryptionList)
                    redacted_image=res[0]
                    encrypt_mapper=res[1]
                    processed_image_stream = io.BytesIO()
                    redacted_image.save(processed_image_stream, format='PNG')
                    
                if(angle!=0 and payload.rotation_flag==True):
                    redacted_image,angle=ImageRotation.rotate_image(redacted_image,angle)
                    processed_image_stream = io.BytesIO()
                    redacted_image.save(processed_image_stream, format='PNG')
                processed_image_bytes = processed_image_stream.getvalue()
                base64_encoded_image=base64.b64encode(processed_image_bytes)
                SaveImage.save_img(base64_encoded_image)
                obj={"map":encrypt_mapper,"img":base64_encoded_image}
                log.debug("Returning from image_encryption function")
                return obj
            except Exception as e:
                log.error(str(e))
                log.error("Line No:"+str(e.__traceback__.tb_lineno))
                log.error(str(e.__traceback__.tb_frame))
                error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"imageHashifyFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                raise RuntimeError(e)
class SaveImage:
    @staticmethod
    def save_img(img_data):
        log.debug("Image processed (in-memory, no disk persistence)")
        return img_data
