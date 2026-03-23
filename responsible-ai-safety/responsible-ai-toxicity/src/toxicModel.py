'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os
import math
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from detoxify import Detoxify




check_point = 'toxic_debiased-c7548aa0.ckpt'
toxicityModel = Detoxify(checkpoint='../models/detoxify/'+ check_point,
                            device="cpu",
                            huggingface_config_path='../models/detoxify')
tokenizer = toxicityModel.tokenizer


class Toxic:
    def analyze (text):
        
       
        text = text
        if not text or not isinstance(text, str):
            raise ValueError("The input text must be a non-empty string.")

        inputs = tokenizer(text, truncation=True, padding=True, max_length=512, return_tensors="pt")
        List_profanity = []
        input_ids_val = tokenizer.encode(text)
        input_ids=input_ids_val[1:-1]
        result_list=[]
        #to send max 510 tokens to the model at a time and at end find avg result for each token set
        if len(input_ids)>510:
            val=math.ceil(len(input_ids)/510)
            j=0
            k=510
            for i in range(0,val):
                text="".join(tokenizer.decode(input_ids[j:k]))
                j+=510
                k+=510
                output = toxicityModel.predict(text)
                
        else:
           
            output = toxicityModel.predict(text)
        toxic_score = output['toxicity']
       
        return output
        