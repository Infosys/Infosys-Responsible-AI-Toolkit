'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


import base64
import json
import io, base64
from PIL import Image
import requests
import pandas as pd
from privacy.mappers.mappers import *
import os

from privacy.config.logger import CustomLogger
from privacy.util.code_detect import *
from privacy.util.code_detect.regexdetection import *
import json
from privacy.util.code_detect.ner.pii_inference.netcustom import code_detect_ner
log = CustomLogger()

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class CodeDetect:
    def codeDetectRegex(payload)->PIICodeDetectRequest:
        payload=AttributeDict(payload)
        print("Text===",payload)
        #finalpayload=str(payload)
        #ouputjson=json.loads(payload)
        output_code=code_detect.codeDetectRegex(payload.inputText)
        print("output_code===",output_code)
        return output_code
    
    def codeDetectNerText(payload)->PIICodeDetectRequest:
        payload=AttributeDict(payload)
        print("Text===",payload)
        #finalpayload=str(payload)
        #ouputjson=json.loads(payload)
        output_code=code_detect_ner.textner(payload.inputText)
        print("output_code===",output_code)
        return output_code  
