'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from werkzeug.exceptions import InternalServerError
from fastapi.encoders import jsonable_encoder
import traceback
from mapper.mapper import *
import time
import contextvars
from config.logger import CustomLogger,request_id_var
import nltk
from nltk.tokenize import sent_tokenize
import numpy as np
import sys
import os

log = CustomLogger()

try:
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
    
    log.info("Before loading prompt injection model")
    
    nltk.data.path.append(os.path.join(application_path, 'data', 'nltk_data'))

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    PROMPT_INJECTION_MODEL_PATH = os.path.join(application_path, "models/fine_tuned_promptInjection_model")
    
    injection_model = AutoModelForSequenceClassification.from_pretrained(PROMPT_INJECTION_MODEL_PATH).to(device)
    injection_tokenizer = AutoTokenizer.from_pretrained(PROMPT_INJECTION_MODEL_PATH)
    injection_pipeline = pipeline("text-classification", model=injection_model, tokenizer=injection_tokenizer, device=device)
    
    label_mapping = {
        0: "SAFE",
        1: "INJECTION"
    }

    request_id_var.set("Startup")
    log_dict={}
    log.info("Prompt injection model loaded successfully")

except Exception as e:
    log.error(f"Failed to load the prompt injection model. Exception: {e}")
    log.error(f"Traceback: {traceback.format_exc()}")
    raise

def promptInjection_check(text, id):
    log.info("Inside promptInjection_check function")
    request_id_var.set(id)
    start_time = time.time()
    
    try:
        input_ids = injection_tokenizer.encode(text, add_special_tokens=False)
        token_limit = 512
        
        if len(input_ids) > token_limit:
            log.info(f"Text length ({len(input_ids)} tokens) exceeds the limit. Processing with token-based chunks.")
            
            chunk_size = 500
            overlap = 100
            result_scores = []
            
            for i in range(0, len(input_ids), chunk_size - overlap):
                chunk_ids = input_ids[i : i + chunk_size]
                
                chunk_text = injection_tokenizer.decode(chunk_ids, skip_special_tokens=True)
                
                result = injection_pipeline(chunk_text)
                predicted_score = result[0]["score"]

                if predicted_score > 0.85:
                    time_taken = f"{round(time.time() - start_time, 3)}s"
                    log.info(f"Immediate INJECTION detected. Score: {predicted_score}")
                    return "INJECTION", predicted_score, {'time_taken': time_taken}

                result_scores.append(predicted_score)
            
            max_score = np.max(result_scores) if result_scores else 0
            final_label = "INJECTION" if max_score > 0.6 else "SAFE"
            
            time_taken = f"{round(time.time() - start_time, 3)}s"
            log.info(f"No immediate injection detected. Returning maximum score. Label: {final_label}, Max Score: {max_score}")
            return final_label, max_score, {'time_taken': time_taken}

        else:
            log.info(f"Text length ({len(input_ids)} tokens) is within the limit. Processing as a single input.")
            result = injection_pipeline(text)
            
            predicted_label_id = result[0]["label"]
            predicted_score = result[0]["score"]
            
            end_time = time.time()
            time_taken = f"{round(end_time - start_time, 3)}s"
            
            final_label = "INJECTION" if predicted_label_id == 1 else "SAFE"
            
            log.info(f"Prompt injection result: Label='{final_label}', Score={predicted_score}, Time='{time_taken}'")
            
            return final_label, predicted_score, {'time_taken': time_taken}
            
    except Exception as e:
        log.error("Error occurred in promptInjection_check", exc_info=True)
        error_details = {
            "request_id": request_id_var.get(),
            "error": str(e),
            "error_module": "Failed at promptInjection_check call"
        }
        log.error(error_details)
        raise InternalServerError()