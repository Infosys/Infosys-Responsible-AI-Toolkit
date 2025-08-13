import os
'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import multiprocessing
import threading

import math
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from sentence_transformers import SentenceTransformer,util
from detoxify import Detoxify
#from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from werkzeug.exceptions import InternalServerError
from fastapi.encoders import jsonable_encoder
import traceback
from mapper.mapper import *
import time
import contextvars
from config.logger import CustomLogger,request_id_var
from privacy.privacy import Privacy as ps

log = CustomLogger()

import sys
import os

try:
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
        
    log=CustomLogger()
    log.info("before loading model")
    request_id_var = contextvars.ContextVar("request_id_var")
    #pipe = StableDiffusionPipeline.from_pretrained('/model/stablediffusion/fp32/model')
    device = "cuda"
#    registry = RecognizerRegistry()
#    registry.load_predefined_recognizers()
#    analyzer_engine = AnalyzerEngine(registry=registry)

    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print("device",device)
    gpu=0 if torch.cuda.is_available() else -1
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # # for i in os.walk(BASE_DIR)
    # print(BASE_DIR)
    # print(os.listdir(BASE_DIR))
    # print(os.listdir())
    check_point = 'toxic_debiased-c7548aa0.ckpt'
    toxicityModel = Detoxify(checkpoint=os.path.join(application_path, 'models/detoxify/'+ check_point),
                        device=device,
                        huggingface_config_path=os.path.join(application_path, 'models/detoxify'))
    tokenizer = AutoTokenizer.from_pretrained(os.path.join(application_path, "models/detoxify"))


    PromptModel_dberta = AutoModelForSequenceClassification.from_pretrained(os.path.join(application_path, "models/dbertaInjection")).to(device)
    Prompttokens_dberta = AutoTokenizer.from_pretrained(os.path.join(application_path, "models/dbertaInjection"))
    promtModel = pipeline("text-classification", model=PromptModel_dberta, tokenizer=Prompttokens_dberta, device=device)

    #topictokenizer_Facebook = AutoTokenizer.from_pretrained("../models/facebook")
    #topicmodel_Facebook = AutoModelForSequenceClassification.from_pretrained("../models/facebook").to(device)

    topictokenizer_dberta = AutoTokenizer.from_pretrained(os.path.join(application_path,"models/restricted-dberta-base-zeroshot-v2"))
    topicmodel_dberta = AutoModelForSequenceClassification.from_pretrained(os.path.join(application_path,"models/restricted-dberta-base-zeroshot-v2")).to(device)
    nlp = pipeline('zero-shot-classification', model=topicmodel_dberta, tokenizer=topictokenizer_dberta,device=gpu)
    # nlidist = pipeline('zero-shot-classification', model="../models/nli-distilroberta-base",device=gpu)
    # bartlarge = pipeline('zero-shot-classification', model="../models/bart-large-mnli",device=gpu)
    # nildeberta = pipeline('zero-shot-classification', model="../models/nli-deberta-v3-small",device=gpu)
    # debertasmall = pipeline('zero-shot-classification', model="../models/deberta-small-long-nli",device=gpu)
    nlimini = pipeline('zero-shot-classification', model="../models/nli-MiniLM2-L6-H768",device=gpu)
    # nlimini = pipeline('zero-shot-classification', model=r"C:\Users\amitumamaheshwar.h\Downloads\nli-MiniLM2-L6-H768",device=gpu)
    # distilbart = pipeline('zero-shot-classification', model="../models/distilbart-mnli-12-6",device=gpu)
    # classifier = pipeline("zero-shot-classification",model="../../../models/facebook",device=device)
    # classifier2 = pipeline("zero-shot-classification",model="../../../models/restricted-dberta-large-zeroshot",device=device)
    # encoder = SentenceTransformer("../models/multi-qa-mpnet-base-dot-v1").to(device)
    # classifier = pipeline("zero-shot-classification",model="../../models/facebook",device=device)
    # classifier2 = pipeline("zero-shot-classification",model="../../models/restricted-dberta-large-zeroshot",device=device)
    encoder = SentenceTransformer(os.path.join(application_path, "models/multi-qa-mpnet-base-dot-v1")).to(device)

    jailbreakModel = encoder
    similarity_model =encoder
    request_id_var.set("Startup")
    log_dict={}
    log.info("model loaded")

except Exception as e:
    log.error(f"Exception: {e}")
    log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

def privacy(id,text):  
    log.info("inside privacy")
    
    try:
        st = time.time()
        res=ps.textAnalyze({"inputText":text,
                    "account": None,
                    "portfolio":None,
                    "exclusionList": None,
                    "fakeData": "false"})
        et = time.time()
        rt = et-st
        #print("result start",res.PIIEntities,"result end", "time",rt)
        
        # output['PIIresult'] = {"PIIresult":res.PIIEntities,"modelcalltime":round(rt,3)}
        return {"PIIresult":res.PIIEntities,"modelcalltime":round(rt,3)}
    except Exception as e:
             
            log.error("Error occured in privacy")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at privacy call"})
            raise InternalServerError()

def multi_q_net_similarity(id,text1=None,text2=None,emb1=None,emb2=None):
    
    try:
        st = time.time()
        if text1:
            with torch.no_grad():
                emb1 = jailbreakModel.encode(text1, convert_to_tensor=True,device=device)
        if text2:
            with torch.no_grad():
                emb2 = jailbreakModel.encode(text2, convert_to_tensor=True,device=device)
        
        emb = util.pytorch_cos_sim(emb1, emb2).to("cpu").numpy().tolist()
        del emb1
        del emb2
        et = time.time()
        rt =et-st
        return emb,{'time_taken': str(round(rt,3))+"s"}
    except Exception as e:
             
            log.error("Error occured in multi_q_net_similarity")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at multi_q_net_similarity call"})
            raise InternalServerError()
            
def multi_q_net_embedding(id,lst):
    log.info("inside multi_q_net_embedding")
    
    try:
        st = time.time()
        # print("start time JB===========",lst,st)
        
        res = []
        for text in lst:
            with torch.no_grad():
                text_embedding = jailbreakModel.encode(text, convert_to_tensor=True,device=device)
            res.append(text_embedding.to("cpu").numpy().tolist())

        del text_embedding
        et = time.time()
        rt = et-st
        # output['multi_q_net_embedding'] =(res,{'time_taken': str(round(rt,3))+"s"})
        return res,{'time_taken': str(round(rt,3))+"s"}
        # return output
        # return text_embedding.numpy().tolist()
    except Exception as e:
             
            log.error("Error occured in multi_q_net text embedding")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at multi_q_net text embedding call"})
            raise InternalServerError()
            
def restricttopic_check(payload,id): 
    log.info("inside restricttopic_check")
    
    try:
        st = time.time()
        # topicmodel = topicmodel_Facebook
        # topictokenizer = topictokenizer_Facebook

        # nlp = pipeline('zero-shot-classification', model=classifier, tokenizer=topictokenizer)

        text=payload['text']
        if('model' in payload):
            model=payload['model']
        else:
            model="nliMini"
        labels=payload['labels']
        #hypothesis_template = "The topic of this text is {}"
        hypothesis_template="This text falls under and is strictly related to topic {}"
        
    
        if(model=="nliMini"):
            cls=nlimini
        else:
            cls=nlp
        # print(model,cls)
        #commented to use just dberta model
        #model =payload['model'] if hasattr(payload, 'model') else "facebook"
        #if model==None:
        #    model="dberta"
        
        # if model=="facebook":
        #     # nlp = classifier
        #     nlp = pipeline('zero-shot-classification', model=topicmodel_Facebook, tokenizer=topictokenizer_Facebook, device=gpu)
        # elif model=="dberta": 
        #     # nlp = classifier2
        #     nlp = pipeline('zero-shot-classification', model=topicmodel_dberta, tokenizer=topictokenizer_dberta,device=gpu)
        # nlp = pipeline('zero-shot-classification', model=topicmodel_dberta, tokenizer=topictokenizer_dberta,device=gpu)
        with torch.no_grad():    
            output=cls(text, labels,hypothesis_template=hypothesis_template,multi_label=True)
        # print("=================",output)
        for i in range(len(output["scores"])):
            output["scores"][i] = round(output["scores"][i],4)

        # del nlp
        del cls
        et = time.time()
        rt = et-st
        output['time_taken'] = str(round(rt,3))+"s"
        # output1['restricttopic'] = output
        return output
    
    except Exception as e:
             
            log.error("Error occured in restricttopic_check")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at restricttopic_check call"})
            raise InternalServerError()

def toxicity_check(payload,id) :
    log.info("inside toxicity_check")
    
    try:
        st = time.time()
        text = payload['text']

        #to check number of tokens 
        input_ids_val = tokenizer.encode(text)
        input_ids=input_ids_val[1:-1]
        result_list=[]
        #to send max 450 tokens to the model at a time and at end find avg result for each token set
        token_limit=450
        if len(input_ids)>token_limit:
            val=math.ceil(len(input_ids)/token_limit)
            j=0
            k=token_limit
            for i in range(0,val):
                text="".join(tokenizer.decode(input_ids[j:k]))
                j+=token_limit
                k+=token_limit
                with torch.no_grad():
                    result = toxicityModel.predict(text)
                    result_list.append(result)
            output = {
                'toxicity': 0,
                'severe_toxicity': 0,
                'obscene': 0,
                'threat': 0,
                'insult': 0,
                'identity_attack': 0,
                'sexual_explicit': 0
                }
            for j in result_list:
                 output['toxicity']+=j['toxicity']
                 output['severe_toxicity']+=j['severe_toxicity']
                 output['obscene']+=j['obscene']
                 output['identity_attack']+=j['identity_attack']
                 output['insult']+=j['insult']
                 output['threat']+=j['threat']
                 output['sexual_explicit']+=j['sexual_explicit']
            output = {k: v / len(result_list) for k, v in output.items()}
        else:
            with torch.no_grad():
                output = toxicityModel.predict(text)
        List_profanity_score = []
        obj_profanityScore_toxic = profanityScore(metricName='toxicity',
                                        metricScore=output['toxicity'])
        obj_profanityScore_severe_toxic = profanityScore(metricName='severe_toxicity',
                                        metricScore=output['severe_toxicity'])
        obj_profanityScore_obscene = profanityScore(metricName='obscene',
                                        metricScore=output['obscene'])
        obj_profanityScore_threat = profanityScore(metricName='threat',
                                        metricScore=output['threat'])
        obj_profanityScore_insult = profanityScore(metricName='insult',
                                        metricScore=output['insult'])
        obj_profanityScore_identity_attack = profanityScore(metricName='identity_attack',
                                        metricScore=output['identity_attack'])
        obj_profanityScore_sexual_explicit = profanityScore(metricName='sexual_explicit',
                                        metricScore=output['sexual_explicit'])
        
        List_profanity_score.append(obj_profanityScore_toxic)
        List_profanity_score.append(obj_profanityScore_severe_toxic)
        List_profanity_score.append(obj_profanityScore_obscene)
        List_profanity_score.append(obj_profanityScore_threat)
        List_profanity_score.append(obj_profanityScore_insult)
        List_profanity_score.append(obj_profanityScore_identity_attack)
        List_profanity_score.append(obj_profanityScore_sexual_explicit)

        objProfanityAnalyzeResponse = {}
        objProfanityAnalyzeResponse['toxicScore'] = List_profanity_score
        et = time.time()
        rt = et-st
        objProfanityAnalyzeResponse['time_taken'] = str(round(rt,3))+"s"
        # output1['toxicity'] = objProfanityAnalyzeResponse
        return objProfanityAnalyzeResponse
    
    except Exception as e:
             
            log.error("Error occured in toxicity_check")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at toxicity_check call"})
            raise InternalServerError()
              
def promptInjection_check(text,id):
    
    log.info("inside promptInjection_check")
    try:
        st = time.time()
        result = promtModel(text)
        # print("============:",result)
        predicted_label_name = result[0]["label"]
        predicted_probabilities = result[0]["score"]
        # del tokens
        et = time.time()
        rt = et-st
        # output['promptInjection'] = (predicted_label_name,predicted_probabilities, {'time_taken':str(round(rt,3))+"s"})
        
        return predicted_label_name,predicted_probabilities, {'time_taken':str(round(rt,3))+"s"}
    except Exception as e:
            
            log.error("Error occured in promptInjection_check")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at promptInjection_check call"})
            raise InternalServerError()
        
# def checkall(id,payload):
#     try:
#         st = time.time()
#         output = {}
#         x=[]
#         threads = []
#         results = []
#         thread = threading.Thread(target=toxicity_check, args=(payload['text'],id,output))
#         threads.append(thread)
#         thread.start()
#         thread1 = threading.Thread(target=promptInjection_check, args=(payload['text']['text'],id,output))
#         threads.append(thread1)
#         thread1.start()
#         thread2 = threading.Thread(target=restricttopic_check, args=(payload["restric"],id,output))
#         threads.append(thread2)
#         thread2.start()
#         thread3 = threading.Thread(target=multi_q_net_embedding, args=(id,payload['embed']["text"],output))
#         threads.append(thread3)
#         thread3.start()
#         thread4 = threading.Thread(target=privacy, args=(id,payload['text']['text'],output))
#         threads.append(thread4)
#         thread4.start()
#         for thread in threads:
#             thread.join()
#             # print("=======================:",result)
#             # results.append(thread.result)
#         # with multiprocessing.Pool() as pool:
#         #     output['toxicity'] =pool.starmap(toxicity_check, [(payload["text"],id)])
#         #     output['promptInjection'] = pool.starmap(promptInjection_check, [(payload['text'],id)])
#         #     output['restricttopic'] = pool.starmap(restricttopic_check, [(payload["restric"],id)])
#         #     output['multi_q_net_embedding'] = pool.starmap(multi_q_net_embedding, [(id,payload['embed']["text"])])
#         #     output['privacy'] = pool.starmap(privacy, [(id,payload['text'])])
#         # print("output",output)
#         et = time.time()
#         rt = et-st
#         output['time_taken'] = str(round(rt,3))+"s"
#         return output
#     except Exception as e:
            
#             log.error("Error occured in checkall")
#             log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
#             log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
#                                                    "Error Module":"Failed at checkall call"})
#             raise InternalServerError()
