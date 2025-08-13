# MIT license https://opensource.org/licenses/MIT
# Copyright 2024 Infosys Ltd
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import base64
import io
from typing import Tuple
import cv2
from PIL import Image
from privacy.service.imagePrivacy import AttributeDict, ImagePrivacy
from privacy.service.api_req import ApiCall
from privacy.service.textPrivacy import TextPrivacy
from privacy.service.__init__ import *
import numpy as np
from privacy.config.logger import request_id_var
from privacy.config.logger import CustomLogger
import os
import shutil
import threading
import time
import uuid
import fitz 
import io 
from PIL import Image 
from unidecode import unidecode
log = CustomLogger()
error_dict={}

def pdfToImage():
    pass
    
class PDFService:
    def processImages(pdf_file,page,imgs,pgno,payload,uid):
        try:
            request_id_var.set(uid)
            img=pdf_file.extract_image(imgs[0])

            if  len(img["image"])<700:
                return None
            bb=page.get_image_bbox(imgs)

            imgd=io.BytesIO(img["image"])
            # payload={"easyocr":None,"mag_ratio":False,"rotationFlag":False,"image":AttributeDict({"file":imgd}),"portfolio":None,"account":None,"exclusion":None}
            payload["image"]=AttributeDict({"file":imgd})
            # payload["piiEntitiesToBeRedacted"]=None
            resImage=ImagePrivacy.image_anonymize(AttributeDict(payload))
            resImg =base64.b64decode(resImage)

            page.insert_image(fitz.Rect(bb[0],bb[1],bb[2],bb[3]),stream=resImg)
        except Exception as e:
                log.error(str(e))
                log.error("Line No:"+str(e.__traceback__.tb_lineno))
                log.error(str(e.__traceback__.tb_frame))
                error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"PDFMASKMainFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                # ExceptionDb.create({"UUID":request_id_var.get(),"function":"textAnalyzeMainFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                raise Exception(e)
    def editText(text,i,page):
        request_id_var.set("editText")
        log.debug(unidecode(str(text[i.start:i.end]))+":"+str(i.entity_type))
        x=page.search_for(text[i.start:i.end])

        for inst in x:
            # Create a redaction annotation to replace the text

            page.add_redact_annot(inst, "<"+i.entity_type+">",fontname="helv", fontsize=15) 
            # page.insert_text((inst[0],inst[1]), i.entity_type,fontname="helv", fontsize=5) 
            # page.write_text((inst[0],inst[1]), (i.entity_type),overlay=True)
    def processText(page,payload,uid):
        try:
            request_id_var.set(uid)
            text=page.get_text()
             
            accDetails=None
            if(payload.portfolio!=None):
                accDetails=AttributeDict({"portfolio":payload.portfolio,"account":payload.account})             
            
            res=TextPrivacy.textAnalyze(text=text,accName=accDetails,exclusion=payload.exclusion.split(',') if payload.exclusion != None else [],piiEntitiesToBeRedacted=payload.piiEntitiesToBeRedacted.split(',') if payload.piiEntitiesToBeRedacted != None else [],nlp=payload.nlp)

            res=anonymizer._remove_conflicts_and_get_text_manipulation_data(res,(
                ConflictResolutionStrategy.MERGE_SIMILAR_OR_CONTAINED
            ))

            res=anonymizer._merge_entities_with_whitespace_between(text,res)

            resThreds=[]
            for i in res:

                    thread = threading.Thread(target=PDFService.editText, args=(text,i,page))
                    thread.start()
                    resThreds.append(thread)
            for thread in resThreds:
                    thread.join()  
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

 
        except Exception as e:
                log.error(str(e))
                log.error("Line No:"+str(e.__traceback__.tb_lineno))
                log.error(str(e.__traceback__.tb_frame))
                error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"PDFMASKMainFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                # ExceptionDb.create({"UUID":request_id_var.get(),"function":"textAnalyzeMainFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                raise Exception(e)
    def mask_pdf(payload):
        try:
            log.debug("payload:-"+str(payload))
            id = uuid.uuid4().hex
            request_id_var.set(id)
            payload = AttributeDict(payload)
           
            if(payload.portfolio!=None or payload.account!=None):
                response_value=ApiCall.request(AttributeDict({"portfolio":payload.portfolio,"account":payload.account}))
                if(response_value==None):
                        return None
            fitz.TOOLS.set_small_glyph_heights(True)
            pdf_file=fitz.open(stream=payload.file.file.read(), filetype="pdf")

            # new_pdf = fitz.open(filetype="pdf")
      
            for page_index in range(len(pdf_file)): 
                    page = pdf_file[page_index] 

                    threads=[]
                    thread = threading.Thread(target=PDFService.processText, args=(page,payload,id))
                    thread.start()
                    # thread.join()
                    threads.append(thread)
                    page_image_list = page.get_images(full=True)
                                #   new_page = new_pdf.new_page()              # for imgs in page_image_list:
                    for imgs in page_image_list:
                        thread = threading.Thread(target=PDFService.processImages, args=(pdf_file,page,imgs,page_index,payload,id))
                        thread.start()
                        threads.append(thread)
                    for thread in threads:
                          thread.join()
 
            # new_pdf.save("masked.pdf")  
              
            # pdf_file.save("masked.pdf")
            pdf_bytes = io.BytesIO()
            pdf_file.save(pdf_bytes)
            pdf_bytes.seek(0)

    # Create FastAPI response
            
            return pdf_bytes         
            # return new_pdf
                #   page.insert_image(page_image_list[0][0],s)
               
        except Exception as e:
                log.error(str(e))
                log.error("Line No:"+str(e.__traceback__.tb_lineno))
                log.error(str(e.__traceback__.tb_frame))
                error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"PDFMASKMainFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                # ExceptionDb.create({"UUID":request_id_var.get(),"function":"textAnalyzeMainFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                raise Exception(e)
