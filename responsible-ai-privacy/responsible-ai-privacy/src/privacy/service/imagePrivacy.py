'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


import io, base64
from PIL import Image
from privacy.service.easy import EasyOCR
from privacy.service.azureComputerVision import ComputerVision
# from privacy.dao.TelemetryFlagDb import TelemetryFlag
from privacy.mappers.mappers import *
from privacy.util.encrypt import EncryptImage
from typing import List
from privacy.constants.local_constants import (DELTED_SUCCESS_MESSAGE)
from privacy.config.logger import CustomLogger
#import zipfile
from zipfile import ZipFile,is_zipfile
from dotenv import load_dotenv
from privacy.config.logger import request_id_var
load_dotenv()
import numpy as np
import cv2
# from privacy.util.flair_recognizer import FlairRecognizer 
log = CustomLogger()
import time
import pytesseract
from scipy import ndimage
from PIL import Image as im 
from privacy.util.special_recognizers.DataListRecognizer import DataListRecognizer
# global error_dict
from privacy.service.__init__ import *
from privacy.service.api_req import ApiCall

class ImageRotation:
    def float_convertor(x):
        if x.isdigit():
            out= float(x)
        else:
            out= x
        return out 
    def getAngle(image):
        k = pytesseract.image_to_osd(image)
        out = {i.split(":")[0]: ImageRotation.float_convertor(i.split(":")[-1].strip()) for i in k.rstrip().split("\n")}
        return out["Rotate"]
    def rotateImage(image,preAngle=0):
        angle=0
        # t=time.time()
        if(preAngle==0):
            angle=ImageRotation.getAngle(image)
        # print("angle:",time.time()-t)
        if(preAngle==angle):
            return (image,angle)
        img_rotated = ndimage.rotate(image, preAngle-angle)
        image = im.fromarray(img_rotated)
        return (image,angle)

class ImagePrivacy:
    def image_analyze(payload):  
        error_dict[request_id_var.get()]=[]
        try:
            log.debug("Entering in image_analyze function")        
            payload=AttributeDict(payload)
            image = Image.open(payload.image.file)
           
            # analyzer,registry=ConfModle.getAnalyzerEngin("en_core_web_lg")
            angle=0
            if(payload.rotationFlag):
                image,angle=ImageRotation.rotateImage(image)
            global imageAnalyzerEngine
            analyzer,imageAnalyzerEngine,imageRedactorEngine,imagePiiVerifyEngine,encryptImageEngin=selectNlp(payload.nlp)
            
            ocr=None
            if(payload.easyocr=="Tesseract"):
                # ocr = TesseractOCR()
                log.debug("TESSERACT SELECTED")
                imageAnalyzerEngine = ImageAnalyzerEngine(analyzer_engine=analyzer) 
                # imageRedactorEngine = ImageRedactorEngine(image_analyzer_engine=imageAnalyzerEngine)
            if(payload.easyocr=="EasyOcr"):
                ocr=EasyOCR()
                EasyOCR.setMag(payload.mag_ratio)
                tt=time.time()
                imageAnalyzerEngine = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)  
                # print(time.time()-tt)
            if(payload.easyocr=="ComputerVision"):
                ocr=ComputerVision()
                # EasyOCR.setMag(payload.mag_ratio)

                imageAnalyzerEngine = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)  
                # imageRedactorEngine = ImageRedactorEngine(image_analyzer_engine=imageAnalyzerEngine)
            
            log.debug("payload="+str(payload))  
            if(payload.piiEntitiesToBeRedacted == None):
                piiEntitiesToBeRedacted=None
            else:
                piiEntitiesToBeRedacted = payload.piiEntitiesToBeRedacted.split(',')
            #print("piipiiEntitiesToBeRedacted===",piiEntitiesToBeRedacted)
            
            
            spRecog=None
            if(payload.nlp=="roberta"):
                spRecog=[roberta_recog]
            if(payload.nlp=="ranha"):
                # registry.add_recognizer(ranha_recog)
                if(piiEntitiesToBeRedacted==None and  payload.account==None):
                    piiEntitiesToBeRedacted=list(set(ranha_recog.supported_entities+registry.get_supported_entities()))
                spRecog=[ranha_recog]
            # print("spRecog===",spRecog)
            if(payload.exclusion == None):
                exclusionList=[]
            else:
                exclusionList=payload.exclusion.split(",")  
            if(payload.portfolio== None):
                # entities=["PERSON","LOCATION"],
                #print("payload103===",payload )
                #print("payload.piiEntitiesToBeRedacted103==",payload.piiEntitiesToBeRedacted)
                if(piiEntitiesToBeRedacted == None):
                    results = imageAnalyzerEngine.analyze(image, allow_list=exclusionList,ad_hoc_recognizers=spRecog)
                else:
                    try:
                        results = imageAnalyzerEngine.analyze(image,entities=piiEntitiesToBeRedacted, allow_list=exclusionList,ad_hoc_recognizers=spRecog)
                        #print("result------",results)
                    except Exception as e:
                        #print("error 103===",e)
                        return 482
                #print("results:",results)
            else:
                result=[]
                preEntity=[]
                response_value=ApiCall.request(payload)
                if(response_value==None):
                    return None
                if(response_value==404):
                    # print( response_value)
                    return response_value
                entityType,datalist,preEntity=response_value
                # entityType,datalist,preEntity=ApiCall.request(payload)
                # preEntity=["PERSON"]
                for d in range(len(datalist)):
                    record=ApiCall.getRecord(entityType[d])
                    record=AttributeDict(record)
                    # log.debug("Record ======"+str(record))
    
                    if(record.RecogType=="Data"):
                            dataRecog=(DataListRecognizer(terms=datalist[d],entitie=[entityType[d]]))
                            registry.add_recognizer(dataRecog)
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
                results = imageAnalyzerEngine.analyze(image,entities=entityType+preEntity, allow_list=exclusionList,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"],ad_hoc_recognizers=spRecog)
                result.extend(results)
                    # results = PrivacyService.__analyze(text=payload.inputText,accName=accMasterid.accMasterId)
                # if(len(preEntity)>0):               
                #         results = imageAnalyzerEngine.analyze(image,entities=preEntity, allow_list=exclusionList,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"])
                #         preEntity.clear()
                #         result.extend(results)
                results=result                               

            #log.debug(f"results: {results}")

            list_PIIEntity = []
            for result in results:
                log.debug(f"result: {result}")
                obj_PIIEntity = PIIImageAnalyze(type=result.entity_type,
                                          start=result.start,
                                          end=result.end,
                                          score=result.score)
                log.debug(f"obj_PIIEntity: {obj_PIIEntity}")
                list_PIIEntity.append(obj_PIIEntity)
                del obj_PIIEntity

            log.debug(f"list_PIIEntity: {list_PIIEntity}")
            objPIIAnalyzeResponse = PIIAnalyzeResponse
            objPIIAnalyzeResponse.PIIEntities = list_PIIEntity

            log.debug("Returning from image_analyze function")
            # ApiCall.encryptionList.clear()
            return objPIIAnalyzeResponse
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"imageAnalyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
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
        error_dict[request_id_var.get()]=[]
        try: 
            payload=AttributeDict(payload)
            global imageRedactorEngine
            analyzer,imageAnalyzerEngine,imageRedactorEngine,imagePiiVerifyEngine,encryptImageEngin=selectNlp(payload.nlp)
            
            # analyzer,registry=ConfModle.getAnalyzerEngin("en_core_web_lg")
            ocr=None
            if(payload.easyocr=="Tesseract"):
                # ocr = TesseractOCR()
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
                # EasyOCR.setMag(payload.mag_ratio)

                imageAnalyzerEngine = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)  
                imageRedactorEngine = ImageRedactorEngine(image_analyzer_engine=imageAnalyzerEngine)
            # engine = ImageRedactorEngine()
            payload=AttributeDict(payload)
            image = Image.open(payload.image.file)
            
            
            angle=0
            if(payload.rotationFlag):
                image,angle=ImageRotation.rotateImage(image)
         
            # registry.load_predefined_recognizers()
            # log.debug("payload.image.file====="+str(payload.image.file))
            if(payload.piiEntitiesToBeRedacted == None):
                piiEntitiesToBeRedacted=None
            else:
                piiEntitiesToBeRedacted = payload.piiEntitiesToBeRedacted.split(',')
            #print("piipiiEntitiesToBeRedacted===",piiEntitiesToBeRedacted)
            if(payload.exclusion == None):
                exclusionList=[]
            else:
                exclusionList=payload.exclusion.split(",")
                
            spRecog=None
            if(payload.nlp=="roberta"):
                spRecog=[roberta_recog]
            if(payload.nlp=="ranha"):
                # registry.add_recognizer(ranha_recog)
                if(piiEntitiesToBeRedacted==None and  payload.account==None):
                    piiEntitiesToBeRedacted=list(set(ranha_recog.supported_entities+registry.get_supported_entities()))
                spRecog=[ranha_recog]
            # print("spRecog===",spRecog)
                
                
            if(payload.portfolio== None):
                if(piiEntitiesToBeRedacted == None):
                    redacted_image = imageRedactorEngine.redact(image, (255, 192, 203), allow_list=exclusionList,ad_hoc_recognizers=spRecog)
                else:
                    try:
                        redacted_image = imageRedactorEngine.redact(image, (255, 192, 203),entities=piiEntitiesToBeRedacted, allow_list=exclusionList,ad_hoc_recognizers=spRecog)
                    #print("result------",redacted_image)
                    except Exception as e:
                        #print("error 103===",e)
                        return 482
                #print("results:",redacted_image)
                processed_image_stream = io.BytesIO()
                redacted_image.save(processed_image_stream, format='PNG')
            else:
                result=[]
                preEntity=[]
                response_value=ApiCall.request(payload)
                if(response_value==None):
                    return None
                if(response_value==404):
                    # print( response_value)
                    return response_value
                entityType,datalist,preEntity=response_value
                # entityType,datalist,preEntity=ApiCall.request(payload)
                for d in range(len(datalist)):
                    record=ApiCall.getRecord(entityType[d])
                    record=AttributeDict(record)
                    # log.debug("Record=="+str(record))
                    
                    if(record.RecogType=="Data"):
                            dataRecog=(DataListRecognizer(terms=datalist[d],entitie=[entityType[d]]))
                            registry.add_recognizer(dataRecog)
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
                redacted_image = imageRedactorEngine.redact(image, (255, 192, 203),entities=entityType+preEntity, allow_list=exclusionList,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"],ad_hoc_recognizers=spRecog)
                        # log.debug("redacted_image=="+str(redacted_image))
                processed_image_stream = io.BytesIO()
                redacted_image.save(processed_image_stream, format='PNG')
                    # log.debug("redacted_image="+str(redacted_image))  
                image=redacted_image
                    # results = PrivacyService.__analyze(text=payload.inputText,accName=accMasterid.accMasterId)
                # if(len(preEntity)>0):
                #         redacted_image = imageRedactorEngine.redact(image, (255, 192, 203),entities=preEntity, allow_list=exclusionList,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"])
                #         processed_image_stream = io.BytesIO()
                #         redacted_image.save(processed_image_stream, format='PNG')
                #         preEntity.clear()
            if(angle!=0 and payload.rotationFlag==True):
                redacted_image,angle=ImageRotation.rotateImage(redacted_image,angle)
                processed_image_stream = io.BytesIO()
                redacted_image.save(processed_image_stream, format='PNG')
            # redacted_image.show()
            # redacted_image = engine.redact(image, (255, 192, 203),entities=preEntity)
            # processed_image_stream = io.BytesIO()
            # redacted_image.save(processed_image_stream, format='PNG')
            processed_image_bytes = processed_image_stream.getvalue()
            base64_encoded_image=base64.b64encode(processed_image_bytes)
            # saveImage.saveImg(base64_encoded_image)
            saveImage.saveImg(base64_encoded_image)
            log.debug("Returning from image_anonymize function")
            # ApiCall.encryptionList.clear()
            return base64_encoded_image
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"imageAnonimyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)

    async def image_masking(main_image,template_image):
        template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
        # Threshold the template image to create a binary mask
        _, template_mask = cv2.threshold(template_gray, 1, 255, cv2.THRESH_BINARY)

        # Perform template matching
        result = cv2.matchTemplate(main_image, template_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        # Get the dimensions of the template image
        template_height, template_width = template_image.shape[:2]

        # Create a mask with the same size as the main image
        mask = np.zeros(main_image.shape[:2], dtype=np.uint8)

        # Set the region of interest (ROI) in the mask based on the template location
        mask[max_loc[1]:max_loc[1] + template_height, max_loc[0]:max_loc[0] + template_width] = 255

        # Apply the mask to the main image
        result_with_mask = cv2.bitwise_and(main_image, main_image, mask=cv2.bitwise_not(mask))

        return result_with_mask
    
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
           error_dict[request_id_var.get()]=[]
           log.debug("Entering in image_verify function")
           try:
                # analyzer,registry=ConfModle.getAnalyzerEngin("en_core_web_lg")
                # engine1 = ImageAnalyzerEngine(analyzer_engine=analyzer)
                # imagePiiVerifyEngine = ImagePiiVerifyEngine(image_analyzer_engine=imageAnalyzerEngine)
                # enginex=EncryptImage(image_analyzer_engine=engine1)
                global imagePiiVerifyEngine
                analyzer,imageAnalyzerEngine,imageRedactorEngine,imagePiiVerifyEngine,encryptImageEngin=selectNlp(payload.nlp)
            
                payload=AttributeDict(payload)
                image = Image.open(payload.image.file)
                # registry.load_predefined_recognizers()
                if(payload.exclusion == None):
                    exclusionList=[]
                else:
                    exclusionList=payload.exclusion.split(",")

                if(payload.portfolio== None):
                    verify_image = imagePiiVerifyEngine.verify(image, allow_list=exclusionList)
                    processed_image_stream = io.BytesIO()
                    verify_image.save(processed_image_stream, format='PNG')

                else:
                    result=[]
                    preEntity=[]
                    response_value=ApiCall.request(payload)
                    if(response_value==None):
                        return None
                    if(response_value==404):
                    # print( response_value)
                        return response_value
                    entityType,datalist,preEntity=response_value

                    # Al=ApiCall.encryptionList
                    for d in range(len(datalist)):
                        record=ApiCall.getRecord(entityType[d])
                        record=AttributeDict(record)

                        if(record.RecogType=="Data"):
                                dataRecog=(DataListRecognizer(terms=datalist[d],entitie=[entityType[d]]))
                                registry.add_recognizer(dataRecog)
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
                    verify_image = imagePiiVerifyEngine.verify(image,entities=entityType+preEntity, allow_list=exclusionList,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"])
                     #   verify_image = enginex.encrypt(image,encryptionList=Al,entities=[entityType[d]], allow_list=exclusionList)
                    processed_image_stream = io.BytesIO()
                    verify_image.save(processed_image_stream, format='PNG')
                    # log.debug("redacted_image="+str(redacted_image))  
                    image=verify_image
                        # results = PrivacyService.__analyze(text=payload.inputText,accName=accMasterid.accMasterId)
                    # if(len(preEntity)>0):
                    
                    #         verify_image = imagePiiVerifyEngine.verify(image,entities=preEntity, allow_list=exclusionList,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"])
                    #      #    verify_image = enginex.encrypt(image,encryptionList=Al,entities=preEntity, allow_list=exclusionList)


                    #         processed_image_stream = io.BytesIO()
                    #         verify_image.save(processed_image_stream, format='PNG')
                    #         preEntity.clear()

                processed_image_bytes = processed_image_stream.getvalue()
                base64_encoded_image=base64.b64encode(processed_image_bytes)
                saveImage.saveImg(base64_encoded_image)
                log.debug("Returning from image_verify function")
                # ApiCall.encryptionList.clear()
                return base64_encoded_image
           except Exception as e:
                log.error(str(e))
                log.error("Line No:"+str(e.__traceback__.tb_lineno))
                log.error(str(e.__traceback__.tb_frame))
                error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"imageVeryFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                raise Exception(e)
       
    def imageEncryption(payload):
            error_dict[request_id_var.get()]=[]
            log.debug("Entering in imageEncryption function")
            try:
                payload=AttributeDict(payload)
                EncryptImage.entity.clear()
                # analyzer,registry=ConfModle.getAnalyzerEngin("en_core_web_lg")

                ocr=None
                global encryptImageEngin
                analyzer,imageAnalyzerEngine,imageRedactorEngine,imagePiiVerifyEngine,encryptImageEngin=selectNlp(payload.nlp)
            
                if(payload.easyocr=="Tesseract"):
                    # ocr = TesseractOCR()
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
                    # EasyOCR.setMag(payload.mag_ratio)

                    imageAnalyzerEngine = ImageAnalyzerEngine(analyzer_engine=analyzer,ocr=ocr)  
                    encryptImageEngin=EncryptImage(image_analyzer_engine=imageAnalyzerEngine)
                # engine = ImageRedactorEngine(image_analyzer_engine=engine1)
                # engine = ImageRedactorEngine()
                payload=AttributeDict(payload)
                image = Image.open(payload.image.file)
                angle=0
                if(payload.rotationFlag):
                    image,angle=ImageRotation.rotateImage(image)
                # registry.load_predefined_recognizers()
                # log.debug("payload.image.file====="+str(payload.image.file))
                encryptMapper=[]
                if(payload.exclusion == None):
                    exclusionList=[]
                else:
                    exclusionList=payload.exclusion.split(",")
                encryptImageEngin.getText(image)
                
                if(payload.piiEntitiesToBeHashified== None):
                    hashList=None
                else:
                    hashList = payload.piiEntitiesToBeHashified.split(',')
                    
                spRecog=None
                if(payload.nlp=="roberta"):
                    spRecog=[roberta_recog]
                if(payload.nlp=="ranha"):
                    # registry.add_recognizer(ranha_recog)
                    if(hashList==None and  payload.account==None):
                        hashList=list(set(ranha_recog.supported_entities+registry.get_supported_entities()))
                    spRecog=[ranha_recog]
                # print("spRecog===",spRecog)
                if(payload.portfolio== None):
                    
                    if(hashList==None):
                    # redacted_image = engine.redact(image, (255, 192, 203), allow_list=exclusionList)
                        redacted_image = encryptImageEngin.imageAnonimyze(image, (255, 192, 203), allow_list=exclusionList,ad_hoc_recognizers=spRecog)
                        processed_image_stream = io.BytesIO()
                        redacted_image.save(processed_image_stream, format='PNG')
                    else:
                        redacted_image = encryptImageEngin.imageAnonimyze(image, (255, 192, 203), allow_list=exclusionList,entities=hashList,encryptionList=hashList,ad_hoc_recognizers=spRecog)
                        processed_image_stream = io.BytesIO()
                        redacted_image.save(processed_image_stream, format='PNG')
                        res=encryptImageEngin.encrypt(redacted_image,encryptionList=hashList)
                        redacted_image=res[0]
                        encryptMapper=res[1]
                        processed_image_stream = io.BytesIO()
                        redacted_image.save(processed_image_stream, format='PNG')
                else:
                    result=[]
                    preEntity=[]
                    response_value=ApiCall.request(payload)
                    # encryptionList=ApiCall.encryptionList
                    if(response_value==None):
                        return None
                    if(response_value==404):
                        # print( response_value)
                        return response_value
                    encryptionList=admin_par[request_id_var.get()]["encryptionList"]
                    entityType,datalist,preEntity=response_value
                    # entityType,datalist,preEntity=ApiCall.request(payload)
                    for d in range(len(datalist)):
                        record=ApiCall.getRecord(entityType[d])
                        record=AttributeDict(record)
                        # log.debug("Record=="+str(record))
                     
                        if(record.RecogType=="Data"):
                                dataRecog=(DataListRecognizer(terms=datalist[d],entitie=[entityType[d]]))
                                registry.add_recognizer(dataRecog)
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
                    redacted_image = encryptImageEngin.imageAnonimyze(image, (255, 192, 203),encryptionList=encryptionList,entities=entityType+preEntity, allow_list=exclusionList,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"],ad_hoc_recognizers=spRecog)
                        # log.debug("redacted_image=="+str(redacted_image))
                    processed_image_stream = io.BytesIO()
                    redacted_image.save(processed_image_stream, format='PNG')
                    # log.debug("redacted_image="+str(redacted_image))  
                    image=redacted_image
                        # results = PrivacyService.__analyze(text=payload.inputText,accName=accMasterid.accMasterId)
                    # if(len(preEntity)>0):
                    #         redacted_image = encryptImageEngin.imageAnonimyze(image, (255, 192, 203),encryptionList=encryptionList,entities=preEntity, allow_list=exclusionList,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"])
                    #         processed_image_stream = io.BytesIO()
                    #         redacted_image.save(processed_image_stream, format='PNG')
                    #         preEntity.clear()
                    
                    EncryptImage.dis()
                    res=encryptImageEngin.encrypt(redacted_image,encryptionList=encryptionList)
                    redacted_image=res[0]
                    encryptMapper=res[1]
                    processed_image_stream = io.BytesIO()
                    redacted_image.save(processed_image_stream, format='PNG')
                    
                if(angle!=0 and payload.rotationFlag==True):
                    redacted_image,angle=ImageRotation.rotateImage(redacted_image,angle)
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
                # ApiCall.encryptionList.clear()
                return obj
            except Exception as e:
                log.error(str(e))
                log.error("Line No:"+str(e.__traceback__.tb_lineno))
                log.error(str(e.__traceback__.tb_frame))
                error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"imageHashifyFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                raise Exception(e)
class saveImage:
    def saveImg(img_data):
        
    
        with open("imageToSave.png", "wb") as fh:
            fh.write(base64.decodebytes(img_data))