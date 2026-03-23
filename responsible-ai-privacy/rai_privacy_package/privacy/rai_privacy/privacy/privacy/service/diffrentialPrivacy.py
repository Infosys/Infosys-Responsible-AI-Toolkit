'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import secrets
import json
import io, base64
import random
from PIL import Image
import requests
import pandas as pd
from privacy.service.easy import EasyOCR
from privacy.dao.TelemetryFlagDb import TelemetryFlag
from privacy.mappers.mappers import *
import os
import httpx
# from privacy.util.nltk_recog import CustomNltkNlpEngine
from diffprivlib.mechanisms import binary
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
from diffprivlib.mechanisms import snapping
from diffprivlib.mechanisms import laplace
from diffprivlib.mechanisms import gaussian
load_dotenv()
import numpy as np
import math
log = CustomLogger()

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class DiffPrivacy:
    headder=["a","b"]
    df=pd.DataFrame()

    
    def noiseAdd(df,col):
        log.info("noiseAdd Function called........")
        epsilon = 1.0  # Privacy parameter for differential privacy
        sensitivity = 1  # Sensitivity of the age values
        scale = sensitivity / epsilon
        laplace_noise = np.random.laplace(loc=0, scale=scale, size=len(df))
        # print(laplace_noise)
        # keyList=[]
        if(df[col].dtypes=='int64'):
            df[col] += laplace_noise
            df[col]=df[col].astype(int)
            # keyList.append(math.ceil(laplace_noise))
        else:
            # keyList.append(laplace_noise)
            df[col] += laplace_noise
        # DiffPrivacy.key[col]={"value":False,"key":keyList}
            
    def binaryCheck(df,col):
        log.info("BinaryCheck Function")
        data=list(df[col].unique())
        # print(data)
        # keyList=[]
        mechanism = binary.Binary(epsilon=1.0,value0=data[0],value1=data[1])
        for d in range(len(df[col])):
            temp=df.loc[d,col]
            # print("==/",temp)
            res=mechanism.randomise(temp)
            # keyList.append(int(temp==res))
            df.loc[d,col]=res
        # DiffPrivacy.key[col]={"value":data,"key":keyList}
        
        
            
    def rangeAdd(df,col):
        log.info("range Adding Function")
        import math
        minv=df[col].min()
        maxv=df[col].max()

        base=10
        maxrange=math.ceil(maxv / base) * base
        minrange=round(minv/base)*base
        
        range_magnitude = abs(maxrange - minrange)
        # print(range_magnitude)
        # Determine the number of ranges based on the magnitude``
        num_ranges = max(range_magnitude // 10, 1)  # Assuming a minimum range size of 10

        # Calculate the interval
        interval = range_magnitude / num_ranges
        binlist=set()
        lablelist=[]

        for i in range(num_ranges):
            start = minrange + i * interval
            end = minrange + (i + 1) * interval
            if(i==num_ranges-1):
                # print(i)
                end=maxrange
            binlist.add(start)
            binlist.add(end)
            lablelist.append(f"{start}-{end}")
            # ranges.append((start, end))
        binlist=sorted(list(binlist))
        df[col]=pd.cut(df[col], bins=binlist, labels=lablelist)


    def gaussianFunc(df,col):
        log.info("gaussian Function......")
        gaussianVal=gaussian.GaussianAnalytic(epsilon=1,delta=1,sensitivity=2)
        # keyList=[]
        for d in range(len(df[col])):
            temp=df.loc[d,col]
            # print("==/",temp)
            res=gaussianVal.randomise(temp)
            if(df[col].dtypes=='int64'):
                # keyList.append(math.ceil((temp-res)))
                df.loc[d,col]=int(res)
            else:    
                # keyList.append((temp-res))
                df.loc[d,col]=res
        # DiffPrivacy.key[col]={"value":False,"key":keyList}
        
        
    def laplaceFunc(df,col):
        log.info("Laplace Function......")
        minv=df[col].min()-5
        maxv=df[col].max()+5
        # keyList=[]
        laplaceVar=laplace.LaplaceTruncated(epsilon=1,delta=0,sensitivity=1,lower=minv,upper=maxv)
        for d in range(len(df[col])):
            temp=df.loc[d,col]
            # print("==/",temp)
            res=laplaceVar.randomise(temp)
            if(df[col].dtypes=='int64'):
                # keyList.append(math.ceil((temp-res)))
                df.loc[d,col]=int(res)
            else:    
                # keyList.append((temp-res))
                df.loc[d,col]=res
        # DiffPrivacy.key[col]={"value":False,"key":keyList}
    
    def snappingFunc(df,col):
        log.info("Snapping Function......")
        # print(df)
        # print(col)
        # print(df[col])
        # print(df[col].min())
        
        minv=df[col].min()-5
        maxv=df[col].max()+5
        # keyList=[]
        snappingVar=snapping.Snapping(epsilon=1,sensitivity=1,lower=minv,upper=maxv)
        for d in range(len(df[col])):
            temp=df.loc[d,col]
            # print("==/",temp)
            res=snappingVar.randomise(temp)
            if(df[col].dtypes=='int64'):
                # keyList.append(math.ceil((temp-res)))
                df.loc[d,col]=int(res)
            else:    
                # keyList.append((temp-res))
                df.loc[d,col]=res
        # DiffPrivacy.key[col]={"value":False,"key":keyList}
        
        
            
    
        
    def uploadFIle(file):
        log.info("Entering in uploadFIle function")
        # print(file.file.read())
        df=pd.read_csv(file.file)
        # df=pd.read_csv(file)
        DiffPrivacy.df=df
        headders=df.columns
        print(headders)
        numaricHeadder=df.select_dtypes(include = ['int64',"float64"])
        print(numaricHeadder)
        DiffPrivacy.headder.extend(headders)
        binaryList=[]
        for c in df.columns:
    # print(s)
           if(len(df[c].unique())==2):
                binaryList.append(c)
        log.info("Returning from uploadFIle function")
                
        return {"allHeadders":list(headders),"numaricHeadder":list(numaricHeadder.columns),"binaryHeadder":list(binaryList)}
        
    def listParser(listdata):
        if(listdata[0]==""):
            
            return []
        return listdata
    def diffPrivacy(payload):
        log.info("Entering in diffPrivacy function")
        log.debug(payload)
        log.debug(payload["suppression"])
        df=DiffPrivacy.df
        
        suppressHedder=DiffPrivacy.listParser(payload["suppression"].split(","))
        # if(suppressHedder[0]==""):
        #     suppressHedder=[]
            
        noiseHeadder=DiffPrivacy.listParser(payload["noiselist"].split(","))
        binaryHeadder=DiffPrivacy.listParser(payload["binarylist"].split(","))
        rangeHeadder=DiffPrivacy.listParser(payload["rangelist"].split(","))
        log.debug(df)
        log.debug(suppressHedder)
        # print(h)
        noiseList=["laplaceFunc","noiseAdd","gaussianFunc","snappingFunc"]
        
        noiseVar = getattr(DiffPrivacy, secrets.choice(noiseList))
        if(suppressHedder is not []):
            df = df.drop(suppressHedder, axis=1)
        for noise in noiseHeadder:
            # DiffPrivacy.noiseAdd(df,noise)
            noiseVar(df,noise)
        
        for bcol in binaryHeadder:
            DiffPrivacy.binaryCheck(df,bcol)
        
        for rcol in rangeHeadder:
            DiffPrivacy.rangeAdd(df,rcol)
        log.debug(df)
        
        
        buffer = io.BytesIO()

        df.to_csv(buffer,index=False)
        # csv=csvData.encode()
        buffer.seek(0)
        
        log.info("Returning from diffPrivacy function")
        # return [df,DiffPrivacy.key]
        return buffer
