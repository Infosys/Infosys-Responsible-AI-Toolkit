import torch
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import os
import re
import time
import sys
from profanity.config.logger import CustomLogger
from profanity.mappers.mappers import MaliciousURLAnalyzeRequest
from random import uniform

try:
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
    log=CustomLogger()
    log.info(f"application_path : {application_path}")
    log.info("before loading model")
    device = "cuda"
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    log.info(f"device : {device}")
    gpu=0 if torch.cuda.is_available() else -1
    
    # Loading model and tokenizer
    pipeline_kwargs={
            "top_k": None,
            "return_token_type_ids": False,
            "max_length": 128,
            "truncation": True,
        }
    model = AutoModelForSequenceClassification.from_pretrained(os.path.join(application_path,"../models/codebert-base-Malicious_URLs")).to(device)
    tokenizer = AutoTokenizer.from_pretrained(os.path.join(application_path,"../models/codebert-base-Malicious_URLs"))
    nlp = pipeline(task="text-classification",model=model,tokenizer=tokenizer,**pipeline_kwargs,)
    log.info("model loaded")

except Exception as e:
    log.error(str(e))
    raise Exception("Process Failed , Check with admin")





class MaliciousUrlService:
    def scan(self, payload: MaliciousURLAnalyzeRequest):
        try:
            st=time.time()
            prompt = payload.inputText
            threshold = payload.maliciousThreshold
            url_pattern = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
            urls = url_pattern.findall(prompt)
            _malicious_labels = [
                "defacement",
                "phishing",
                "malware",
            ]
            if len(urls) == 0:
                return {"prompt":prompt,"scoreList":[],"result":"UNMODERATED","threshold":threshold,"time":str(round(time.time()-st,3))+"s"}
            
            results = nlp(urls)
            log.info(f"results : {results}")

            final_result={}
            final_result['url_with_scores']=[]
            final_result['result']="PASSED"
            for i in range(0,len(urls)):
                for r in results[i]:
                    if r['label'] in _malicious_labels and r['score'] > threshold:
                        final_result['url_with_scores'].append({"url":urls[i],"scores":{r['label']:r['score']}})
                        final_result['result']="FAILED"
                        break

            return {"prompt":prompt,"scoreList":final_result['url_with_scores'],"result":final_result['result'],"threshold":threshold,"time":str(round(time.time()-st,3))+"s"}
        except Exception as e:
            log.error(f"Exception: {e}")
            raise Exception("Process Failed , Check with admin")
