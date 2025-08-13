'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from http.client import HTTPException
import json
import os
import threading
import time
import jwt
from dotenv import load_dotenv
from config.logger import CustomLogger, request_id_var
from exception.exception import completionException, InvalidTokenException, EmptyModerationChecksListException
from flask import request,jsonify
import traceback
import uuid
from mapper.mapper import *
from flask import Blueprint 
from service.service import *
from cov import Cov
from auth import Auth
from cov_llama_deepseek import COV
from cov_aws import CovAWS
from cov_gemini import CovGemini
from geval import gEval
from telemetry import telemetry
import requests
from translate import Translate
from service.textTemplate_service import *
from service.imageTemplate_service import *
from service.recommend_service import *
from datetime import datetime
from utilities.lruCaching import *
import secrets
import sys

if os.getenv("DBTYPE") != "False":
    from dao.AdminDb import Results
    

app =  Blueprint('app', __name__)
log=CustomLogger()
load_dotenv()
logcheck=os.getenv("LOGCHECK")


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def handle_object(obj):
    return vars(obj) 

@app.route("/health",methods=[ 'GET'])
def health():
    if(logcheck=="true"):
        log.info("Entered health routing method")
        log.info("Health check Success")
    return json.dumps({"status":"Health check Success"})

@app.route("/rai/v1/moderations",methods=[ 'POST'])
def generate_text():
    log.info("Entered create usecase routing method")
    log.info("Moderation API STARTED")
    st=time.time()
    try:
        log.info("before invoking create usecase service")
        authorization = request.headers.get('authorization')
        response = None
        token_info = None
        payload=AttributeDict(request.get_json())
        headers = {'Authorization': authorization}
        token_env = payload.token_env if "token_env" in payload else "others"

        #any env other than edgeverve
        if token_env=='others':
            if authorization != None: 
                log.info("got auth from headers")
                decoded_token = jwt.decode(authorization.split(" ")[1], algorithms=["HS256"], options={"verify_signature": False})
                X_Correlation_ID = request.headers.get('X-Correlation-ID')
                X_Span_ID = request.headers.get('X-Span-ID')
                if 'unique_name' in decoded_token:
                    token_info = {"unique_name":decoded_token['unique_name'],"X-Correlation-ID":X_Correlation_ID,"X-Span-ID":X_Span_ID,"appid":decoded_token["appid"]}
                else:
                    token_info = {"unique_name":str(uuid.uuid4()),
                        "X-Correlation-ID":X_Correlation_ID,"X-Span-ID":X_Span_ID,"appid":decoded_token["appid"]}
            elif not Auth.is_env_vars_present() is None:
                log.info("got token using auth url")
                tok = Auth.get_valid_bearer_token()
                headers = {'Authorization': f'Bearer {tok}'}
            
            #Going without token for aicloud
            elif os.getenv("TELEMETRY_ENVIRONMENT")=='AZURE' and (os.getenv('TARGETENVIRONMENT')=='azure' or os.getenv('TARGETENVIRONMENT')=='aicloud' or os.getenv('TARGETENVIRONMENT')=='aicloud-raitest'):
                log.info("Going without auth token for aicloud")
            
            else:
                raise InvalidTokenException("Invalid token, enter correct token in headers or provide authurl")
            
        elif token_env=='edgeverve':
            if authorization != None:
                log.info("Got auth from headers")
                tok=authorization.split(" ")[1]
                headers={'Authorization':f'Bearer {tok}'}
            else:
                raise InvalidTokenException("Invalid token, enter correct token in headers")

        if len(payload.ModerationChecks)==0:
            raise EmptyModerationChecksListException("Input moderation checks list is empty",310)

        if token_info is not None:
            response = getModerationResult(payload=payload,headers=headers,telemetryFlag=True,token_info=token_info)
        else:
            response = getModerationResult(payload=payload,headers=headers,telemetryFlag=True)

        if response == "Prompt is Empty":
            raise completionException("400- Prompt is Empty")
        
        response = json.loads(json.dumps(response, default=handle_object))
        log.info("after invoking create usecase service ")
        log.info("exit create usecase routing method")
        log.info(f"Total time taken=======> {time.time()-st}")
        return response
    except InvalidTokenException as e:
        log.error(str(traceback.extract_tb(e.__traceback__)[0].lineno))
        log.info(str(e))
    except EmptyModerationChecksListException as e:
        log.error(str(traceback.extract_tb(e.__traceback__)[0].lineno))
        log.info(str(e))
        return jsonify({'error_code': 310, 'message': str(e)}), 310
 
    except Exception as e:     
        log.error(str(traceback.extract_tb(e.__traceback__)[0].lineno))
        log.info(e)


@app.route("/rai/v1/moderations/coupledmoderations",methods=[ 'POST'])
def generate_text2():
    log.info("Entered create usecase routing method")
    log.info("Couple Moderation API STARTED")
    st=time.time()
    try:
        log.info("before invoking create usecase service ")
        authorization = request.headers.get('authorization')
        if authorization !=None:
            headers = {'Authorization': authorization}
        else:
            tok = Auth.get_valid_bearer_token()
            if tok:
                headers = {'Authorization': f'Bearer {tok}'}
            else:
                log.info("No valid token available.")
        
        payload=AttributeDict(request.get_json())

        if payload.Prompt == "":
            raise completionException("400- Prompt is Empty")
        
        if len(payload.InputModerationChecks)==0:
            raise EmptyModerationChecksListException("Input moderation checks list is empty",310)
        
        response = getCoupledModerationResult(payload=payload,headers=headers)
        response = json.loads(json.dumps(response, default=handle_object))
        log.info("after invoking create usecase service ")
        log.info("exit create usecase routing method")
        log.info(f"Total time taken=======> {time.time()-st}")
        return response
    
    except completionException as cie:
        log.error(str(cie.__dict__))
        log.info("exit create usecase routing method")
        raise HTTPException(cie)
    
    except EmptyModerationChecksListException as e:
        log.error(str(traceback.extract_tb(e.__traceback__)[0].lineno))
        log.info(str(e))
        return jsonify({'error_code': 310, 'message': str(e)}), 310


    
# To access admin url to retrieve Prompt Templates
@app.route("/rai/v1/moderations/getTemplates/<userId>",methods=[ 'GET'])
def get_templates(userId):
    log.info("Entered get_templates() routing method")
    try:
        log.info("before invoking create usecase service")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        url = os.getenv("ADMINTEMPLATEPATH")+userId+"?category=AllModel"
        response = requests.get(url,verify=sslv[verify_ssl])
        template_names=[]
        if response.status_code == 200:
            prompt_template[userId]=response.json()['templates']
            for i in prompt_template[userId]:
                if  i.get('mode')=='Master_Template' or i.get('userId') == userId:
                    template_names.append(i.get('templateName'))
            log.info("Templates stored successfully")
        else:
           log.info("Error getting data: ",{response.status_code})
           
        log.info("after invoking create usecase service ")
        return {"templates retrieved":template_names}
    except Exception as e:
        log.error(e.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**e.__dict__)
    

# To clear the cache
@app.route("/rai/v1/moderations/clearCache",methods=[ 'GET'])
def clear_Cache():
    log.info("Entered clearCache() routing method")
    try:
        log.info("before invoking create usecase service")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        lru.resetCache()
        log.info(f"cache length : {len(lru.getCache())}")
        log.info("after invoking create usecase service ")
        return "Cache cleared"
    except Exception as e:
        log.error(e.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**e.__dict__)

    

@app.route("/rai/v1/moderations/translate",methods=[ 'POST'])
def translate():
    log.info("Entered create usecase routing method")
    try:
        log.info("before invoking create usecase service ")
        st=time.time()
        id = uuid.uuid4().hex
        request_id_var.set(id)
        payload = request.get_json()
        payload=AttributeDict(payload)

        if payload.choice == "google":
            print("Inside Google Translate")
            text,language = Translate.translate(payload.Prompt)
        elif payload.choice == "azure":
            print("Inside Azure Translate")
            text,language = Translate.azure_translate(payload.Prompt)
        responseObj={"text":text,"language" :language,"timetaken":round(time.time()-st,3)}
        log.info("after invoking create usecase service")
        log.info("exit create usecase routing method")
        return responseObj
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)


@app.route("/rai/v1/moderations/evalLLM",methods=[ 'POST'])
def templateBasedEvaluation():
    log.info("Entered evalllm check routing method")
    log.info("Eval LLM API STARTED")
    st=time.time()
    try:
        log.info("before invoking create usecase service ")
        authorization = request.headers.get('authorization')
        req = AttributeDict(request.get_json())
        headers = {'Authorization': authorization}
        if req.Prompt == "":
            log.error("Prompt is Empty, Please enter a valid prompt !!!")
            raise completionException("400- Prompt is Empty, Please enter a valid prompt !!!")
        
        ts = TextTemplateService()
        response = ts.generate_response(req,headers,telemetryFlag=True)
        log.info("after invoking create usecase service")
        log.info("exit create usecase routing method")          
        log.info(f"Total time taken=======> {time.time()-st}s")
        return response
    except Exception as e:
        log.error(str(e.__dict__),"dictionary")
        log.info("Evalllm routing method exception")
        raise HTTPException(**e.__dict__)
    


@app.route("/rai/v1/moderations/multimodal",methods=[ 'POST'])
def generate_image_explainability():
    log.info("Entered multimodal check routing method")
    log.info("MultiModal API STARTED")
    try:
        log.info("before invoking create usecase service ")
        st=time.time()
        authorization = request.headers.get('authorization')
        headers = {'Authorization': authorization}
        image_files = request.files.getlist('Image')
        image_streams = [file.stream for file in image_files]
        log.info(f"files: {image_files}")

        request_payload = {"Prompt":request.form['Prompt'],
                           "Image":image_streams,
                           "ModelName":request.form["model_name"],
                           "TemplateName":request.form["TemplateName"],
                           "Restrictedtopics":request.form["Restrictedtopics"],
                           "lotNumber":request.form["lotNumber"],
                           "userid":request.form["userid"],
                           "AccountName":request.form["AccountName"],
                           "PortfolioName":request.form["PortfolioName"]}
        
        m = ImageTemplateService()
        response = m.generate_response(request_payload,headers)
        log.info("exit create usecase routing method")
        log.info(f"Total time taken=======> {time.time()-st}s")
        return response
        
    except Exception as e:
        log.error(e.__dict__)
        log.info("Multimodal routing method exception")
        raise HTTPException(**e.__dict__)

# To recommend prompts
@app.route("/rai/v1/moderations/recommend",methods=[ 'POST'])
def recommend():
    log.info("Entered recommend routing method")
    log.info("recommend API STARTED")
    try:
        log.info("before invoking create usecase service ")
        st=time.time()
        response = get_cached_prompts(seed=secrets.randbelow(sys.maxsize))
        log.info(f"response : {response}")
        log.info("exit create usecase routing method")
        log.info(f"Total time taken=======> {time.time()-st}s")
        return response
    except Exception as e:
        log.error(e.__dict__)
        log.info("Recommend routing method exception")
        raise HTTPException(**e.__dict__)


@app.route("/rai/v1/moderations/openai",methods=[ 'POST'])
def generate_text3():
    log.info("Entered create usecase routing method")
    try:
        log.info("before invoking create usecase service ")
        st=time.time()
        id = uuid.uuid4().hex
        request_id_var.set(id)
        payload = request.get_json()
        payload=AttributeDict(payload)
        if payload.model_name == "AWS_CLAUDE_V3_5":
            log.info("Inside AWS_CLAUDE_V3_5 model")
            interact=AWScompletions()
        elif payload.model_name == "DeepSeek":
            log.info("Inside DeepSeek model")
            interact=LlamaDeepSeekcompletion()
        elif payload.model_name == "Llama3-70b":
            log.info("Inside llama3 model")
            interact=Llama3completions()
        elif payload.model_name == "Gemini-Pro" or payload.model_name == "Gemini-Flash":
            log.info("Inside Gemini model")
            interact = Geminicompletions(payload.model_name)
        else:
            interact=Openaicompletions()
        output_text,index,finish_reason,hallucinationScore = interact.textCompletion(payload.Prompt,float(payload.temperature),PromptTemplate="GoalPriority",deployment_name=payload.model_name)
        if index == -1:
            return output_text
        # output_text,index,finish_reason = interact.textCompletion(payload.Prompt,float(payload.temperature),SelfReminder=False,GoalPriority=False)
        # respoonseObj=Choice(text=output_text,index=index,finishReason = finish_reason)
        respoonseObj={"text":output_text,"index":index,"finishReason" :finish_reason,"timetaken":round(time.time()-st,3)}

        log.info("after invoking create usecase service")
        log.info("exit create usecase routing method")
        return respoonseObj
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    
@app.route("/rai/v1/moderations/openaiCOT",methods=[ 'POST'])
def generate_text4():
    log.info("Entered create openaiCOT usecase routing method")
    try:
        st=time.time()
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        payload = request.get_json()
        payload=AttributeDict(payload)
        if payload.model_name in ["Llama","DeepSeek"]:
            log.info("Inside Llama or DeepSeek")
            interact = LlamaDeepSeekcompletion()
        elif payload.model_name == "AWS_CLAUDE_V3_5":
            log.info("Inside AWS_CLAUDE_V3_5 model")
            interact=AWScompletions()
        elif payload.model_name == "Llama3-70b":
            log.info("Inside llama3 model")
            interact=Llama3completions()
        elif payload.model_name == "Gemini-Pro" or payload.model_name == "Gemini-Flash":
            log.info("Inside Gemini model")
            interact=Geminicompletions(payload.model_name)
        else:
            interact=Openaicompletions()
        output_text,index,finish_reason,hallucinationScore = interact.textCompletion(payload.Prompt,float(payload.temperature),PromptTemplate="GoalPriority",deployment_name=payload.model_name,Moderation_flag=False,COT=True)
        if index == -1:
            return output_text
        # output_text,index,finish_reason = interact.textCompletion(payload.Prompt,float(payload.temperature),SelfReminder=False,GoalPriority=False,Moderation_flag=False,COT=True)
        # responseObj=Choice(text=output_text,index=index,finishReason = finish_reason)
        respoonseObj={"text":output_text,"index":index,"finishReason" :finish_reason,"timetaken":round(time.time()-st,3)}
        log.info("after invoking create usecase service ")
        log.info("exit create usecase routing method")
        return respoonseObj
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)


@app.route("/rai/v1/moderations/healthcareopenaiCOT",methods=[ 'POST'])
def generate_text4_healthcare():
    log.info("Entered create usecase routing method")
    try:
        st=time.time()
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        payload = request.get_json()
        payload=AttributeDict(payload)
        payload.Prompt = payload.Prompt.replace('Provide justification for your answer.', 'Please consider the given question and reference then let us know in simple terms how the answer is derived.')
        payload.Prompt = payload.Prompt + ' ' + payload.PromptResponse
        if payload.model_name in ["Llama","DeepSeek"]:
            log.info("Inside Llama or DeepSeek")
            interact = LlamaDeepSeekcompletion()
        elif payload.model_name == "AWS_CLAUDE_V3_5":
            log.info("Inside AWS_CLAUDE_V3_5 model")
            interact=AWScompletions()
        elif payload.model_name == "Llama3-70b":
            log.info("Inside llama3 model")
            interact=Llama3completions()
        else:
            interact=Openaicompletions()
        output_text,index,finish_reason,hallucinationScore = interact.textCompletion(payload.Prompt,float(payload.temperature),PromptTemplate="GoalPriority",deployment_name=payload.model_name,Moderation_flag=False,COT=True)
        if index == -1:
            return output_text
        # output_text,index,finish_reason = interact.textCompletion(payload.Prompt,float(payload.temperature),SelfReminder=False,GoalPriority=False,Moderation_flag=False,COT=True)
        # responseObj=Choice(text=output_text,index=index,finishReason = finish_reason)
        respoonseObj={"text":output_text,"index":index,"finishReason" :finish_reason,"timetaken":round(time.time()-st,3)}
        log.info("after invoking create usecase service ")
        log.info("exit create usecase routing method")
        return respoonseObj
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)



@app.route("/rai/v1/moderations/openaiTHOT",methods=[ 'POST'])
def generate_Thot():
    log.info("Entered create usecase routing method")
    try:
        st=time.time()
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        payload = request.get_json()
        payload=AttributeDict(payload)
        if payload.model_name in ["Llama","DeepSeek"]:
            log.info("Inside Llama or DeepSeek")
            interact = LlamaDeepSeekcompletion()
        elif payload.model_name == "AWS_CLAUDE_V3_5":
            log.info("Inside AWS_CLAUDE_V3_5 model")
            interact=AWScompletions()
        elif payload.model_name == "Llama3-70b":
            log.info("Inside llama3 model")
            interact=Llama3completions()
        elif payload.model_name == "Gemini-Pro" or payload.model_name == "Gemini-Flash":
            log.info("Inside Gemini model")
            interact=Geminicompletions(payload.model_name)
        else:
            interact=Openaicompletions()
        output_text,index,finish_reason,hallucinationScore = interact.textCompletion(payload.Prompt,float(payload.temperature),PromptTemplate="GoalPriority",deployment_name=payload.model_name,Moderation_flag=False,THOT=True)
        if index == -1:
            return output_text
        # output_text,index,finish_reason = interact.textCompletion(payload.Prompt,float(payload.temperature),SelfReminder=False,GoalPriority=False,Moderation_flag=False,COT=True)
        # responseObj=Choice(text=output_text,index=index,finishReason = finish_reason)
        respoonseObj={"text":output_text,"index":index,"finishReason" :finish_reason,"timetaken":round(time.time()-st,3)}
        log.info("after invoking create usecase service ")
        log.info("exit create usecase routing method")
        return respoonseObj
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)


# @router.get("/ModerationTime")
# def generate_text(authenticated: bool = Depends(authenticate_token)):
#     log.info("Entered create usecase routing method")
#     try:
#         log.info("before invoking create usecase service")
#         obj=moderationTime()
#         log.info("after invoking create usecase service ")
#         #log.debug("response : " + str(response))
#         log.info("exit create usecase routing method")
#         return obj
#     except completionException as cie:
#         log.error(cie.__dict__)
#         log.info("exit create usecase routing method")
#         raise HTTPException(**cie.__dict__)
    
@app.route("/rai/v1/moderations/ModerationTime",methods=[ 'GET'])
def generate_text5():
    log.info("Entered create usecase routing method")
    try:
        log.info("before invoking create usecase service")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        obj=moderationTime()
        log.info("after invoking create usecase service ")
        #log.debug("response : " + str(response))
        log.info("exit create usecase routing method")
        return obj
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)

@app.route("/rai/v1/moderations/setTelemetry",methods=[ 'POST'])
def settelemetry():
    log.info("Entered create usecase routing method ")   
    st=time.time()
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        payload = request.data
        # print("checkpoint in telemetary func 1 -> ",payload)
        payload=AttributeDict(payload)
        telemetry.tel_flag=payload
        response = "Success"
        log.info("after invoking create usecase service ")
        # log.debug("response : " + str(response))
        log.info("exit create usecase routing method")
        log.info(f"Total time taken=======> {time.time()-st}")
        return response
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    
@app.route("/rai/v1/moderations/ToxicityPopup",methods=[ 'POST'])
async def generate_text6():
    log.info("Entered create usecase routing method")
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        authorization = request.headers.get('authorization')
        payload = request.get_json()
        payload=AttributeDict(payload)
        obj= await toxicity_popup(payload,authorization)
        log.info("after invoking create usecase service ")
        #log.debug("response : " + str(response))
        log.info("exit create usecase routing method")
        return obj
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)

@app.route("/rai/v1/moderations/ProfanityPopup",methods=[ 'POST'])
def generate_text7():
    log.info("Entered create usecase routing method")
    authorization = request.headers.get('authorization')
    payload = request.get_json()
    payload=AttributeDict(payload)
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        obj=profanity_popup(payload.text,authorization)
        log.info("after invoking create usecase service ")
        #log.debug("response : " + str(response))
        log.info("exit create usecase routing method")
        return obj
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    
@app.route("/rai/v1/moderations/PrivacyPopup",methods=[ 'POST'])
def generate_text8():
    log.info("Entered create usecase routing method")
    payload = request.get_json()
    payload=AttributeDict(payload)
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        obj=privacy_popup(payload)
        log.info("after invoking create usecase service ")
        #log.debug("response : " + str(response))
        log.info("exit create usecase routing method")
        json_string = json.dumps(obj, default=handle_object)
        obj = json.loads(json_string)
        return obj
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    
@app.route("/rai/v1/moderations/COV",methods=[ 'POST'])
def generate_text9():
    log.info("Entered create usecase routing method for cov")
    st=time.time()
    payload = request.get_json()
    payload=AttributeDict(payload)
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        if payload.model_name in ["Llama","DeepSeek"]:
            log.info("Inside Llama or DeepSeek COV")
            response = COV.cov(payload.text, payload.complexity,payload.model_name)
        elif payload.model_name == "AWS_CLAUDE_V3_5":
            log.info("Inside AWS_CLAUDE_V3_5 model")
            response = CovAWS.cov(payload.text, payload.complexity)
        elif payload.model_name == "Llama3-70b":
            log.info("Inside llama3 model")
            response=COV.cov(payload.text, payload.complexity,payload.model_name)
        elif payload.model_name == "Gemini-Pro" or payload.model_name == "Gemini-Flash":
            log.info("Inside Gemini model")
            response=CovGemini.cov(payload.text, payload.complexity,payload.model_name)
        else:
            response = Cov.cov(payload.text, payload.complexity, payload.model_name)
            promptTriggering = "The response was filtered due to the prompt triggering Azure OpenAI's content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766"
            if (promptTriggering not in response) and (response != "Rate Limit Error"):
                response['original_question'] = response['original_question'].pop()
        #Send Translated Final Answer Also 
        log.info("after invoking create usecase service ")
        log.info("exit create usecase routing method")
        log.info(f"Total time taken=======> {time.time()-st}")
        if payload.translate == "google":
           
            translated_final_answer,language = Translate.translate(response['final_answer'])
            response['translated_final_answer'] = translated_final_answer
        elif payload.translate == "azure":
            
            translated_final_answer,language = Translate.azure_translate(response['final_answer'])
            response['translated_final_answer'] = translated_final_answer

        final_respose =json.dumps(response)
        return final_respose
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)

@app.route("/rai/v1/moderations/OrgPolicy",methods=[ 'POST'])
def org_policy():
    log.info("Entered create usecase routing method")
    st=time.time()
    authorization = request.headers.get('authorization')
    payload = request.get_json()
    payload=AttributeDict(payload)
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        response = organization_policy(payload,authorization)
        log.info("after invoking create usecase service ")
        # log.debug("response : " + str(response))
        log.info("exit create usecase routing method")
        log.info(f"Total time taken=======> {time.time()-st}")
        return response
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    
@app.route("/rai/v1/moderations/gEval",methods=[ 'POST'])
def Faithfullness():
    log.info("Entered create usecase routing method")
    st=time.time()
    authorization = request.headers.get('authorization')
    payload = request.get_json()
    payload=AttributeDict(payload)
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        response = gEval(payload,authorization)
        log.info("after invoking create usecase service ")
        # log.debug("response : " + str(response))
        log.info("exit create usecase routing method")
        log.info(f"Total time taken=======> {time.time()-st}")
        return response
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)

@app.route("/rai/v1/moderations/Hallucination_Check",methods=[ 'POST'])
def hallucination_check():
    log.info("Entered create usecase routing method")
    st=time.time()

    authorization = request.headers.get('authorization')
    payload = request.get_json()
    payload=AttributeDict(payload)
    try:
        log.info("before invoking create usecase service ")        
        request_id_var.set("similarity")   # id -> similaritycheck
        output_score = show_score(payload.prompt, payload.response, payload.sourcearr, authorization)
        log.info("after invoking create usecase service ")
        log.info("exit create usecase routing method")
        log.info(f"Total time taken=======> {time.time()-st}")
        return output_score
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)

