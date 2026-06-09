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


log = CustomLogger()

import sys
import os

global_sigmoid_fn = torch.nn.Sigmoid()

try:
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
        
    log=CustomLogger()
    log.info("before loading topic model")
    request_id_var = contextvars.ContextVar("request_id_var")

    device = "cuda" 
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print("device",device)
    gpu=0 if torch.cuda.is_available() else -1

    FINE_TUNED_MODEL_PATH = os.path.join(application_path, "models/fine_tuned_restrictedTopic_model")

    tokenizer = AutoTokenizer.from_pretrained(FINE_TUNED_MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(FINE_TUNED_MODEL_PATH).to(device)
    model.eval()
    
    topictokenizer_dberta = AutoTokenizer.from_pretrained(os.path.join(application_path,"models/restricted-deberta-base-zeroshot-v2"))
    topicmodel_dberta = AutoModelForSequenceClassification.from_pretrained(os.path.join(application_path,"models/restricted-deberta-base-zeroshot-v2")).to(device)
    nlp = pipeline('zero-shot-classification', model=topicmodel_dberta, tokenizer=topictokenizer_dberta, device=gpu)
 
    request_id_var.set("Startup")
    log_dict={}
    log.info("topic model loaded")

except Exception as e:
    log.error(f"Exception: {e}")
    log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
    

def classify_with_bert_multi_label(text, device):

    encoding = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    encoding = {k: v.to(device) for k, v in encoding.items()}

    with torch.no_grad():
        outputs = model(**encoding)
        logits = outputs.logits
        probs = global_sigmoid_fn(logits.squeeze().cpu())
        
    if not hasattr(model.config, 'id2label'):
        log.error("fine-tuned distilbert model config does not have 'id2label'. Cannot map scores to labels.")
        raise ValueError("Model configuration missing 'id2label' mapping for multi-label classification.")
    
    id2label = model.config.id2label
    scores = probs.tolist()

    results = [
        {"label": id2label.get(i, f"label_{i}"), "score": round(score, 4)}
        for i, score in enumerate(scores)
    ]

    return results

def restricttopic_check(payload, id):
    log.info("inside restricttopic_check")
    
    try:
        st = time.time()
        text = payload['text']
        model_name = payload.get('model', "deberta")
        
        output = {}

        if model_name == "fine-tuned distilbert":
        
            allowed_labels = payload.get('labels', [])
            allowed_labels_lower = [label.lower() for label in allowed_labels]
            
            # Get all classification results first
            results = classify_with_bert_multi_label(text, device)
            
            filtered_results = [
                item for item in results
                if item['label'] in allowed_labels_lower
            ]

            # Sort the final filtered list
            filtered_results.sort(key=lambda x: x['score'], reverse=True)
            
            output = {
                "sequence": text,
                "labels": [item['label'] for item in filtered_results],
                "scores": [item['score'] for item in filtered_results]
            }

        elif model_name == "deberta":
            labels = payload['labels']
            hypothesis_template = "This text falls under and is strictly related to topic {}"
            with torch.no_grad():
                output = nlp(text, labels, hypothesis_template=hypothesis_template, multi_label=True)
            for i in range(len(output["scores"])):
                output["scores"][i] = round(output["scores"][i], 4)
        else:
            raise ValueError(f"Unknown model specified: {model_name}")

        et = time.time()
        rt = et - st
        output['time_taken'] = str(round(rt, 3)) + "s"
        return output
    
    except Exception as e:
        log.error("Error occurred in restricttopic_check")
        log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno), e}")
        
        if not hasattr(restricttopic_check, 'log_dict'):
            restricttopic_check.log_dict = {}
        if request_id_var.get() not in restricttopic_check.log_dict:
            restricttopic_check.log_dict[request_id_var.get()] = []
        restricttopic_check.log_dict[request_id_var.get()].append({
            "Line number": str(traceback.extract_tb(e.__traceback__)[0].lineno),
            "Error": str(e),
            "Error Module": "Failed at restricttopic_check call"
        })
        raise InternalServerError()