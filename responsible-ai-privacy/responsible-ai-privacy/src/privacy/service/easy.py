'''
License textMIT Licensehttps://mit-license.org/Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

import json
import io, base64
from PIL import Image
import requests
import pandas as pd
import os
import httpx
from presidio_image_redactor.entities import ImageRecognizerResult


from typing import List
from presidio_analyzer import Pattern, PatternRecognizer, AnalyzerEngine, RecognizerRegistry,predefined_recognizers
from presidio_anonymizer import AnonymizerEngine, DeanonymizeEngine
from presidio_anonymizer.entities import (RecognizerResult,
    OperatorResult,
    OperatorConfig)
from presidio_image_redactor import ImageRedactorEngine,ImageAnalyzerEngine,ImagePiiVerifyEngine,OCR
     
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from PIL import Image
import base64
import io
import os
import re
from zipfile import ZipFile,is_zipfile
from dotenv import load_dotenv
import tempfile
import easyocr
import numpy as np
from difflib import SequenceMatcher
from privacy.config.logger import CustomLogger
import pytesseract
import time
load_dotenv()


log = CustomLogger()

output_type = easyocr.Reader(['en'],model_storage_directory=r"privacy/util/model",download_enabled=False)
        
class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
class Data:
    encrypted_text=[]
class EasyOCR(OCR):
    mag_ratio=1
    def process(self):
        return self
    @classmethod
    def setMag(cls,ratio):
        if ratio:
            cls.mag_ratio=10
        else:
            cls.mag_ratio=1
            
        
        
    def perform_ocr(self, image: object, **kwargs) -> dict:
        s=time.time()
        image=np.array(image)
        log.warn("==========================="+str(EasyOCR.mag_ratio))
        res=output_type.readtext(image,mag_ratio=EasyOCR.mag_ratio,width_ths=0.2,batch_size=10)
        print(res)
        df = pd.DataFrame(res,columns=['coordinates','text','conf'])
        res_dict=df.to_dict(orient='records')
        textmap={"text":[],"left":[],"top":[],"width":[],"height":[],"conf":[]}
        
        for val in res_dict:
            textmap["text"].append(val["text"])
            textmap["left"].append(min(val['coordinates'][0][0],val["coordinates"][3][0]))
            textmap["top"].append(min(val['coordinates'][0][1],val["coordinates"][1][1]))
            textmap["width"].append(abs(val['coordinates'][1][0]-val["coordinates"][0][0]))
            textmap["height"].append(abs(val['coordinates'][3][1]-val["coordinates"][0][1]))
            textmap["conf"].append(val["conf"])
        log.warn("time======="+str(time.time()-s))
        return textmap
            
