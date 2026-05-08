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
            gibberish_labels=payload['labels']
            score_threshold = payload.get('gibberish_threshold', 0.7)

            nlp = pipeline(task="text-classification", model=gibberishModel, tokenizer=gibberishTokenizer, device=device,
                        model_kwargs=pipeline_kwargs)

            tokens = gibberishTokenizer.tokenize(text)
            num_tokens = len(tokens)

            match_type = MatchType.FULL

            if num_tokens > 500:
                match_type = MatchType.SENTENCE

            results_all = nlp(match_type.get_inputs(text))
            log.debug(f"Gibberish detection finished :{results_all}")

            hierarchy = {"noise": 0, "word salad": 1, "mild gibberish": 2, "clean": 3}
            final_label = "clean"
            final_score = 0.0
            
            highest_score_label = "clean"
            highest_score = 0.0

            for result in results_all:
                label = result["label"]
                score = round(result["score"], 2)

                if label in gibberish_labels:
                    if score > highest_score:
                        highest_score = score
                        highest_score_label = label
                        
                    if score >= score_threshold and hierarchy[label] < hierarchy[final_label]:
                        final_label = label
                        final_score = score

            if final_label == "clean" and highest_score > 0:
                final_label = highest_score_label
                final_score = highest_score

            output = {}
            output['gibberish_label'] = final_label
            output['gibberish_score'] = final_score

            del nlp
            er=log_dict[request_id_var.get()]
            logobj = {"_id":id,"error":er}
            if len(er)!=0:
                log.debug(str(logobj))
            del log_dict[id]
            return {"result": [output], "time_taken": str(round(time.time() - st, 3)) + "s"}

        except Exception as e:   
            log.error("Error occurred in gibberish_check")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                    "Error Module":"Failed at gibberish_check call"})
            raise InternalServerError()
