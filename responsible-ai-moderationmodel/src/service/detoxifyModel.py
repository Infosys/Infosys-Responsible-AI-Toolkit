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
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from werkzeug.exceptions import InternalServerError
from fastapi.encoders import jsonable_encoder
import traceback
from mapper.mapper import *
import time
import contextvars
from config.logger import CustomLogger,request_id_var


log = CustomLogger()

import sys
import os

try:
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
        
    log=CustomLogger()
    log.info("before loading detoxify model")
    request_id_var = contextvars.ContextVar("request_id_var")
    device = "cuda"
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print("device",device)
    gpu=0 if torch.cuda.is_available() else -1

    FINE_TUNED_MODEL_PATH = os.path.join(application_path, "models/fine_tuned_toxicity_model")
    tokenizer = AutoTokenizer.from_pretrained(FINE_TUNED_MODEL_PATH)
    toxicityModel = AutoModelForSequenceClassification.from_pretrained(FINE_TUNED_MODEL_PATH).to(device)
    toxicityModel.eval()

    request_id_var.set("Startup")
    log_dict={}
    log.info("detoxify model loaded")

except Exception as e:
    log.error(f"Exception: {e}")
    log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")


def toxicity_check(payload, id):
    log.info("Inside toxicity_check function")
    request_id_var.set(id)
    start_time = time.time()

    try:
        text = payload['text']
        
        input_ids = tokenizer.encode(text, add_special_tokens=False)
        token_limit = 500
        
        # This is the label map for your model's output
        label_map = {
            'toxicity': 0,
            'severe_toxicity': 1,
            'obscene': 2,
            'threat': 3,
            'insult': 4,
            'identity_attack': 5,
            'sexual_explicit' : 6
        }

        if len(input_ids) > token_limit:
            log.info(f"Text length ({len(input_ids)} tokens) exceeds the limit. Processing in chunks.")
            
            result_list = []
            
            val = math.ceil(len(input_ids) / token_limit)
            j = 0
            k = token_limit
            
            for i in range(val):
                chunk_text = tokenizer.decode(input_ids[j:k])
                j += token_limit
                k += token_limit
                
                chunk_inputs = tokenizer(
                    chunk_text, 
                    return_tensors="pt", 
                    truncation=True, 
                    padding=True
                ).to(device)

                with torch.no_grad():
                    chunk_outputs = toxicityModel(**chunk_inputs)
                    chunk_predictions = torch.sigmoid(chunk_outputs.logits)
                    result_list.append(chunk_predictions)
            
            all_predictions = torch.cat(result_list, dim=0)
            avg_predictions = torch.mean(all_predictions, dim=0, keepdim=True)

            output_scores = {
                label: float(avg_predictions[0][index]) for label, index in label_map.items()
            }
            
        else:
            log.info(f"Text length ({len(input_ids)} tokens) is within the limit. Processing as a single input.")

            inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(device)
            
            with torch.no_grad():
                outputs = toxicityModel(**inputs)
                predictions = torch.sigmoid(outputs.logits)
            
            output_scores = {
                label: float(predictions[0][index]) for label, index in label_map.items()
            }

        list_profanity_score = [
            profanityScore(metricName=metric, metricScore=score)
            for metric, score in output_scores.items()
        ]

        response = {
            'toxicScore': list_profanity_score,
            'time_taken': f"{round(time.time() - start_time, 3)}s"
        }
        
        return response
    
    except Exception as e:
        log.error("Error occurred in toxicity_check", exc_info=True)
        log_dict[request_id_var.get()].append({
            "Line number": str(traceback.extract_tb(e.__traceback__)[-1].lineno),
            "Error": str(e),
            "Error Module": "Failed at toxicity_check call"
        })
        raise InternalServerError()