from __future__ import annotations

import re
from enum import Enum
import time
import traceback
import uuid
from werkzeug.exceptions import InternalServerError
from config.logger import CustomLogger,request_id_var
import torch
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import os
import sys
import nltk
from nltk.tokenize.punkt import PunktSentenceTokenizer



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
    pipeline_kwargs={"max_length": 128, "truncation": True, "return_token_type_ids": True}
    bancodeModel = AutoModelForSequenceClassification.from_pretrained(os.path.join(application_path, "models/bancode")).to(device)
    bancodeTokenizer = AutoTokenizer.from_pretrained(os.path.join(application_path, "models/bancode"))
    
    request_id_var.set("Startup")
    log_dict={}
    log.info("model loaded")

except Exception as e:
    log.error(f"Exception: {e}")
    log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

def remove_markdown(text):
    # Patterns to remove Markdown elements but keep text inside ** and *
    patterns = [
        r"\*\*([^\*]+)\*\*",  # Bold, preserves text inside
        r"\*([^\*]+)\*",  # Italic, preserves text inside
        r"\!\[[^\]]+\]\([^\)]+\)",  # Images
        r"\[[^\]]+\]\([^\)]+\)",  # Links
        r"\#{1,6}\s",  # Headers
        r"\>+",  # Blockquotes
        r"`{1,3}[^`]+`{1,3}",  # Inline code and code blocks
        r"\n{2,}",  # Multiple newlines
    ]

    clean_text = text
    for pattern in patterns:
        # Use substitution to preserve the text inside ** and *
        if "([^\*]+)" in pattern:
            clean_text = re.sub(pattern, r"\1", clean_text)
        else:
            clean_text = re.sub(pattern, "", clean_text)

    # Extra cleanup for simpler elements
    clean_text = re.sub(r"\*|\_|\`", "", clean_text)

    return clean_text.strip()


class BanCode:
    """
    A scanner that detects if input is code and blocks it.
    """
    def scan(self, payload):
        log.info("inside bancode_check")
        id=uuid.uuid4().hex
        request_id_var.set(id)
        log_dict[request_id_var.get()]=[]
        
        try:
            st = time.time()
            prompt=payload['text']
            nlp = pipeline(task="text-classification",model=bancodeModel,tokenizer=bancodeTokenizer,**pipeline_kwargs)

            # Hack: Improve accuracy
            new_prompt = remove_markdown(prompt)  # Remove markdown
            new_prompt = re.sub(r"\d+\.\s+|[-*•]\s+", "", new_prompt)  # Remove list markers
            new_prompt = re.sub(r"\d+", "", new_prompt)  # Remove numbers
            new_prompt = re.sub(r'\.(?!\d)(?=[\s\'"“”‘’)\]}]|$)', "", new_prompt)  # Remove periods

            result =nlp(new_prompt)[0]
            log.debug(f"Ban code finished :{result}")
            del nlp
            er=log_dict[request_id_var.get()]
            logobj = {"_id":id,"error":er}
            if len(er)!=0:
                log.debug(str(logobj))
            del log_dict[id]
            return {"result":result,"time_taken":str(round(time.time()-st,3))+"s"}
        except Exception as e:   
            log.error("Error occured in bancode_check")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                    "Error Module":"Failed at bancode_check call"})
            raise InternalServerError()