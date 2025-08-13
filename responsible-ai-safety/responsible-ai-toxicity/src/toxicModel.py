import os
import math
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
# from sentence_transformers import SentenceTransformer,util
# from mapper import profanity, profanityScoreList, ProfanityAnalyzeRequest, ProfanityAnalyzeResponse,ProfanitycensorRequest, ProfanitycensorResponse
from detoxify import Detoxify




check_point = 'toxic_debiased-c7548aa0.ckpt'
toxicityModel = Detoxify(checkpoint='../models/detoxify/'+ check_point,
                            device="cpu",
                            huggingface_config_path='../models/detoxify')
# #tokenizer = AutoTokenizer.from_pretrained("models/detoxify")
tokenizer = toxicityModel.tokenizer
# check_point = 'toxic_debiased-c7548aa0.ckpt'
# toxicityModel = Detoxify(checkpoint='../models/detoxify/'+ check_point,
#                             device="cuda",
#                             huggingface_config_path='../models/detoxify')
# tokenizer = AutoTokenizer.from_pretrained("../models/detoxify",ignore_mismatched_sizes=True)


class Toxic:
    def analyze (text):
        
       
        text = text
        if not text or not isinstance(text, str):
            raise ValueError("The input text must be a non-empty string.")

 #       inputs = tokenizer(text, truncation=True, padding=True, max_length=512, return_tensors="pt")
        inputs = tokenizer(text, truncation=True, padding=True, max_length=512, return_tensors="pt")
        #print("inputs======",inputs)
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
                #with torch.no_grad():
                output = toxicityModel.predict(text)
                
        else:
           
            output = toxicityModel.predict(text)
        toxic_score = output['toxicity']
       
        # print("output=====",output)
        return output
        