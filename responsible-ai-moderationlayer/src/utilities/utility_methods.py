'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import os
from dotenv import load_dotenv
from config.logger import CustomLogger
from datetime import datetime
import sys
import json
import requests
import time

load_dotenv()
prompt_template = {}
log = CustomLogger()

##########################################################################################################

# To get Templates from DB based on Detection Type
def get_templates(detection_type,userId):
    template = {}
    found = False
    data = prompt_template[userId]
    for d in data:
        if d['templateName'] == detection_type:
            found=True
            for s in d['subTemplates']:
                template[s['template']] = s['templateData']
            break 

    if not found:
        log.error(f"Invalid Detection type : {detection_type}")
        raise Exception("Invalid Detection Type")
    return template


def get_templates_from_file(detection_type):
    template = {}
    found = False
    EXE_CREATION = os.getenv("EXE_CREATION")
    if(EXE_CREATION == "True"):
        # Get the base path (this will be the path to the executable when running the bundled app)
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(base_path, 'data/template_data.json')
    with open(template_path, "r") as file:
        json_data = file.read()
        data = json.loads(json_data)
        templates = data['templates']
    
    for t in templates:
        if t['templateName'] == detection_type:
            found=True
            for s in t['subTemplates']:
                template[s['template']] = s['templateData']
            break 

    if not found:
        log.error(f"Invalid Detection type : {detection_type}")
        raise Exception("Invalid Detection Type")
    return template



# To get GPT Configurations from env file
def config(modelName):
    API_TYPE=os.getenv("OPENAI_API_TYPE")
    if modelName == "gpt3":
        MODEL_NAME = os.getenv("OPENAI_MODEL_GPT3")
        API_BASE = os.getenv("OPENAI_API_BASE_GPT3")
        API_KEY = os.getenv("OPENAI_API_KEY_GPT3")
        API_VERSION = os.getenv("OPENAI_API_VERSION_GPT3")
    elif modelName == "gpt4O":
        MODEL_NAME = os.getenv("OPENAI_MODEL_GPT4_O")
        API_BASE =  os.getenv('OPENAI_API_BASE_GPT4_O') 
        API_KEY = os.getenv('OPENAI_API_KEY_GPT4_O')           
        API_VERSION = os.getenv('OPENAI_API_VERSION_GPT4_O')
    else: # gpt4
        MODEL_NAME = os.getenv("OPENAI_MODEL_GPT4")
        API_BASE = os.getenv("OPENAI_API_BASE_GPT4")
        API_KEY = os.getenv("OPENAI_API_KEY_GPT4")
        API_VERSION = os.getenv("OPENAI_API_VERSION_GPT4")
    return MODEL_NAME,API_BASE,API_KEY,API_VERSION,API_TYPE

def is_time_difference_12_hours(creation_time, expiration_time):
        """
        Checks if the time difference between current time and creation time is 12 hours.

        Args:
            creation_time (datetime.datetime): The time the item was created.
            expiration_time (int): The expiration time in hours.

        Returns:
            bool: True if the time difference is 12 hours, False otherwise.
        """
        time_difference = datetime.now() - creation_time
        log.info(f"time diff : {time_difference}")
        log.info(f"time diff total hours : {time_difference.total_seconds() / 3600}")

        # Check if difference is exactly 12 hours, accounting for minutes and seconds
        return (time_difference.total_seconds() / 3600) < expiration_time

def aicloud_auth_token_generate(aicloud_access_token, token_expiration):
    aicloud_model_auth=os.getenv("AICLOUD_MODEL_AUTH")
    response=requests.get(aicloud_model_auth)
    aicloud_access_token=None
    token_expiration=0
    if response.status_code==200:
        aicloud_access_token=response.json()["access_token"]
        token_expiration = time.time() + 3600
        log.info(".....generating aicloud access token.....")
    else:
        raise Exception("Failed to fetch aicloud access token")
    return((aicloud_access_token,token_expiration))
