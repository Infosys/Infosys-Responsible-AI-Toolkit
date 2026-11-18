'''
License textMIT Licensehttps://mit-license.org/Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

import secrets
import json
import io, base64
import random
from privacy.config.logger import request_id_var
import pandas as pd
from privacy.service.easy import EasyOCR
from privacy.mappers.mappers import PIICodeDetectRequest
from diffprivlib.mechanisms import binary
from privacy.util.encrypt import EncryptImage

from typing import List
from privacy.constants.local_constants import (DELTED_SUCCESS_MESSAGE)
from privacy.config.logger import CustomLogger
from dotenv import load_dotenv
from privacy.service.__init__ import error_dict
from diffprivlib.mechanisms import snapping
from diffprivlib.mechanisms import laplace
from diffprivlib.mechanisms import gaussian
load_dotenv()
import numpy as np
import math
log = CustomLogger()
LINE_NO_LABEL = "Line No:"

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class DiffPrivacy:
    headder=["a","b"]
    df=pd.DataFrame()

    @staticmethod
    def noise_add(df,col):
        log.info("noise_add Function called........")
        epsilon = 1.0  
        sensitivity = 1  
        scale = sensitivity / epsilon
        rng = np.random.default_rng(seed=42)
        laplace_noise = rng.laplace(loc=0, scale=scale, size=len(df))
        if(df[col].dtypes=='int64'):
            df[col] += laplace_noise
            df[col]=df[col].astype(int)
        else:
            df[col] += laplace_noise
    @staticmethod        
    def binary_check(df,col):
        log.info("BinaryCheck Function")
        data=list(df[col].unique())
        mechanism = binary.Binary(epsilon=1.0,value0=data[0],value1=data[1])
        for d in range(len(df[col])):
            temp=df.loc[d,col]
            res=mechanism.randomise(temp)
            df.loc[d,col]=res
        
        
    @staticmethod        
    def range_add(df,col):
        log.info("range Adding Function")
        import math
        minv=df[col].min()
        maxv=df[col].max()

        base=10
        maxrange=math.ceil(maxv / base) * base
        minrange=round(minv/base)*base
        
        range_magnitude = abs(maxrange - minrange)
        num_ranges = max(range_magnitude // 10, 1)  

        interval = range_magnitude / num_ranges
        binlist=set()
        lablelist=[]

        for i in range(num_ranges):
            start = minrange + i * interval
            end = minrange + (i + 1) * interval
            if(i==num_ranges-1):
                end=maxrange
            binlist.add(start)
            binlist.add(end)
            lablelist.append(f"{start}-{end}")
        binlist=sorted(list(binlist))
        df[col]=pd.cut(df[col], bins=binlist, labels=lablelist)

    @staticmethod
    def gaussian_func(df,col):
        log.info("gaussian Function......")
        gaussian_val=gaussian.GaussianAnalytic(epsilon=1,delta=1,sensitivity=2)
        for d in range(len(df[col])):
            temp=df.loc[d,col]
            res=gaussian_val.randomise(temp)
            if(df[col].dtypes=='int64'):
                df.loc[d,col]=int(res)
            else:    
                df.loc[d,col]=res
        
    @staticmethod   
    def laplace_func(df,col):
        log.info("Laplace Function......")
        minv=df[col].min()-5
        maxv=df[col].max()+5
        laplace_var=laplace.LaplaceTruncated(epsilon=1,delta=0,sensitivity=1,lower=minv,upper=maxv)
        for d in range(len(df[col])):
            temp=df.loc[d,col]
            res=laplace_var.randomise(temp)
            if(df[col].dtypes=='int64'):
                df.loc[d,col]=int(res)
            else:    
                df.loc[d,col]=res
    @staticmethod
    def snapping_func(df,col):
        log.info("Snapping Function......")
        minv=df[col].min()-5
        maxv=df[col].max()+5
        snapping_var=snapping.Snapping(epsilon=1,sensitivity=1,lower=minv,upper=maxv)
        for d in range(len(df[col])):
            temp=df.loc[d,col]
            res=snapping_var.randomise(temp)
            if(df[col].dtypes=='int64'):
                df.loc[d,col]=int(res)
            else:    
                df.loc[d,col]=res

    @staticmethod
    def upload_file(file):
        error_dict[request_id_var.get()]=[]
        log.info("Entering in upload_file function")
        try:
            df=pd.read_csv(file.file)
            DiffPrivacy.df=df
            headders=df.columns
            print(headders)
            numaric_headder=df.select_dtypes(include = ['int64',"float64"])
            print(numaric_headder)
            DiffPrivacy.headder.extend(headders)
            binary_list=[]
            for c in df.columns:
               if(len(df[c].unique())==2):
                    binary_list.append(c)
            log.info("Returning from upload_file function")

            return {"allHeadders":list(headders),"numaricHeadder":list(numaric_headder.columns),"binaryHeadder":list(binary_list)}
        except Exception as e:
            log.error(str(e))
            log.error(LINE_NO_LABEL + str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"textAnalyzeMainFunction","msg":str(e.__class__.__name__),"description":str(e)+LINE_NO_LABEL+str(e.__traceback__.tb_lineno)})
            raise RuntimeError(e)
    @staticmethod
    def list_parser(list_data):
        if(list_data[0]==""):
            
            return []
        return list_data
    @staticmethod
    def diff_privacy(payload):
        error_dict[request_id_var.get()]=[]
        log.info("Entering in diff_privacy function")
        try:
            log.debug(payload)
            log.debug(payload["suppression"])
            df=DiffPrivacy.df

            suppress_header=DiffPrivacy.list_parser(payload["suppression"].split(","))

            noise_header=DiffPrivacy.list_parser(payload["noiselist"].split(","))
            binary_header=DiffPrivacy.list_parser(payload["binarylist"].split(","))
            range_header=DiffPrivacy.list_parser(payload["range_list"].split(","))
            log.debug(df)
            log.debug(suppress_header)
            noise_list=["laplace_func","noise_add","gaussian_func","snapping_func"]

            noise_var = getattr(DiffPrivacy, secrets.choice(noise_list))
            if(suppress_header != []):
                df = df.drop(suppress_header, axis=1)
            for noise in noise_header:
                noise_var(df,noise)

            for bcol in binary_header:
                DiffPrivacy.binary_check(df,bcol)

            for rcol in range_header:
                DiffPrivacy.range_add(df,rcol)
            log.debug(df)


            buffer = io.BytesIO()

            df.to_csv(buffer,index=False)
            buffer.seek(0)

            log.info("Returning from diffPrivacy function")
            return buffer
        except Exception as e:
            log.error(str(e))
            log.error(LINE_NO_LABEL+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"textAnalyzeMainFunction","msg":str(e.__class__.__name__),"description":str(e)+LINE_NO_LABEL+str(e.__traceback__.tb_lineno)})
            raise RuntimeError(e)
