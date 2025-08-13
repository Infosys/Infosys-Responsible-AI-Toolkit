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
    pipeline_kwargs={"return_token_type_ids": False,"max_length": 512,"truncation": True,"batch_size": 1}
    gibberishModel = AutoModelForSequenceClassification.from_pretrained(os.path.join(application_path, "models/gibberish")).to(device)
    gibberishTokenizer = AutoTokenizer.from_pretrained(os.path.join(application_path, "models/gibberish"))
    
    request_id_var.set("Startup")
    log_dict={}
    log.info("model loaded")

except Exception as e:
    log.error(f"Exception: {e}")
    log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")



class MatchType(Enum):
    SENTENCE = "sentence"
    FULL = "full"

    def get_inputs(self, prompt: str) -> list[str]:
        if self == MatchType.SENTENCE:
            pk = PunktSentenceTokenizer()
            return pk.sentences_from_text(text=prompt)
        return [prompt]
    

class Gibberish:

    def scan(self,payload):
        log.info("inside gibberish_check")
        id=uuid.uuid4().hex
        request_id_var.set(id)
        log_dict[request_id_var.get()]=[]
        try:
            st = time.time()
            text=payload['text']
            gibberish_labels = payload['labels']
            nlp = pipeline(task="text-classification", model=gibberishModel, tokenizer=gibberishTokenizer, device=device,model_kwargs=pipeline_kwargs)
            match_type = MatchType(MatchType.FULL)
            results_all = nlp(match_type.get_inputs(text))
            log.debug(f"Gibberish detection finished :{results_all}")
            output={}
            res=[]
            for result in results_all:
                score = round(
                    result["score"] if result["label"] in gibberish_labels else 1 - result["score"],
                    2,
                )
                output['gibberish_label'] =  result["label"]
                output['gibberish_score'] = score

                res.append(output)

            del nlp
            er=log_dict[request_id_var.get()]
            logobj = {"_id":id,"error":er}
            if len(er)!=0:
                log.debug(str(logobj))
            del log_dict[id]
            return {"result":res,"time_taken":str(round(time.time()-st,3))+"s"}
        
        except Exception as e:   
            log.error("Error occured in gibberish_check")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                    "Error Module":"Failed at gibberish_check call"})
            raise InternalServerError()