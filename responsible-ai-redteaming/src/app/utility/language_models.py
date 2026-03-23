'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''



import traceback
import openai
import anthropic
import os
import time
import torch
import threading
import concurrent.futures
import time as _time
import gc
import requests
import logging,json
from typing import List, Dict
from dotenv import load_dotenv
from typing import Dict, List
from langchain_groq import ChatGroq

try:
    import google.generativeai as genai  # Official google-generativeai client
except ImportError:  # Fallback stub so rest of module can still load
    genai = None
    logging.warning("google-generativeai package not installed; GeminiModel will be unavailable.")
from copy import deepcopy
import urllib3
from app.config.logger  import CustomLogger
from app.utility.ssl_utils import get_ssl_verify

import boto3
from datetime import datetime,timedelta
from typing import List
from langchain_aws import ChatBedrock  # Ensure this is installed
# from app.service.language_models import LanguageModel  # Adjust if needed
# from app.utils.utils import is_time_difference_12_hours  # Ensure this utility is defined
# from app.utils.config import sslv, verify_ssl  # Adjust path if needed

verify_ssl = get_ssl_verify()  
import logging
load_dotenv(override=True)
log = CustomLogger()
import logging
log_file = "run.log"
logging.basicConfig(filename=log_file, level=logging.INFO)
log = logging.getLogger(__name__)
class LanguageModel():
    def __init__(self, model_name):
        self.model_name = model_name
        log.info(f"LanguageModel.__init__ - model_name: {model_name}")
        log.info("-" * 50)
    
    def batched_generate(self, prompts_list: List, max_n_tokens: int, temperature: float):
        """
        Generates responses for a batch of prompts using a language model.
        """
        raise NotImplementedError
class EndpointModel_Tap():
    def __init__(self,target_endpoint_url: str, target_endpoint_headers: dict, target_endpoint_payload: dict, target_endpoint_prompt_variable: str, max_retries: int = 5):
        self.max_retries = max_retries,
        self.target_endpoint_url = target_endpoint_url
        self.target_endpoint_headers = target_endpoint_headers
        self.target_endpoint_payload = target_endpoint_payload
        self.target_endpoint_prompt_variable = target_endpoint_prompt_variable
        log.info(f"Initialized EndpointModel with  endpoint_url: {target_endpoint_url},  headers: {self.target_endpoint_headers}, payload: {self.target_endpoint_payload}, prompt_variable: {self.target_endpoint_prompt_variable}")
    def extract_text_with_gpt(self, result: dict) -> str:
        gpt = GPT("gpt-3")  # Initialize GPT with the appropriate model
        conv = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Extract the relevant text from the following JSON response and provide only the text, nothing else:\n\n{result}\n\nOnly provide the text, nothing else."}
        ]
        extracted_text = gpt.generate(conv, max_n_tokens=1500, temperature=0.0, top_p=1.0)
        extracted_text = extracted_text.replace("Here is the relevant text from the JSON response:", "").strip()
        return extracted_text.strip()
    def generate(self, prompt: str,target_endpoint_url,target_endpoint_headers,target_endpoint_payload,target_endpoint_prompt_variable) -> str:
        headers = {key: value for key, value in target_endpoint_headers.items()}
        data: Dict[str, object] = {}
        for key, value in target_endpoint_payload.items():
            if isinstance(value, str):
                try:
                    data[key] = json.loads(value)
                except json.JSONDecodeError:
                    data[key] = value
            else:
                data[key] = value
        data[target_endpoint_prompt_variable] = prompt
        attempts = int(self.max_retries[0])
        for attempt in range(attempts):
            try:
                log.info(f"EndpointModel_Tap.generate - POST {target_endpoint_url} attempt {attempt+1}/{attempts}")
                response = requests.post(
                    self.target_endpoint_url,
                    headers=headers,
                    json=data,
                    verify=verify_ssl,
                    timeout=30
                )
            except requests.RequestException as net_exc:
                log.error(f"EndpointModel_Tap.generate - network error: {net_exc}")
                time.sleep(min(2 ** attempt, 8))
                continue

            if response.status_code != 200:
                log.error(f"EndpointModel_Tap.generate - HTTP {response.status_code}: {response.text[:200]}")
                time.sleep(min(2 ** attempt, 8))
                continue
            try:
                result = response.json()
            except ValueError:
                log.error("EndpointModel_Tap.generate - non-JSON response body")
                return "$ERROR$"
            text = self.extract_text_with_gpt(result)
            if text:
                return text
            log.warning("EndpointModel_Tap.generate - empty text, retrying")
        log.error("EndpointModel_Tap.generate - exhausted retries")
        return "$ERROR$"

    def batched_generate(self, prompts_list: List[str],target_endpoint_url,target_endpoint_headers,target_endpoint_payload,target_endpoint_prompt_variable) -> List[str]:
        log.info(f"Batched generate called with prompts_list: {prompts_list}")
        return [self.generate(prompt,target_endpoint_url,target_endpoint_headers,target_endpoint_payload,target_endpoint_prompt_variable) for prompt in prompts_list]

    def get_response(self, prompts_list,payload) -> List[str]:
        log.info("reached in Endpoint model ")
        target_endpoint_url=payload["target_endpoint_url"]
        target_endpoint_headers=payload["target_endpoint_headers"]
        target_endpoint_payload=payload["target_endpoint_payload"]
        target_endpoint_prompt_variable=payload["target_endpoint_prompt_variable"]
        log.info(f"EndpointModel.get_response - batchsize: {len(prompts_list)}")
        log.info("-" * 50)
        log.info(f"EndpointModel.get_response - prompts_list: {prompts_list}")
        log.info("-" * 50)
        log.info(f"EndpointModel.get_response - target_endpoint_url: {target_endpoint_url}")
        log.info(f"EndpointModel.get_response - target_endpoint_headers: {target_endpoint_headers}")
        log.info(f"EndpointModel.get_response - target_endpoint_payload: {target_endpoint_payload}")
        log.info(f"EndpointModel.get_response - target_endpoint_prompt_variable: {target_endpoint_prompt_variable}")
        batchsize = len(prompts_list)
        log.info(f"EndpointModel.get_response - prompts_list: {prompts_list}")
        log.info("-" * 50)
        
        full_prompts = []
        for prompt in prompts_list:
            full_prompts.append("Question: "+prompt+". Response: Sure,")
            log.info(f"EndpointModel.get_response - full_prompts: {full_prompts}")
            log.info("-" * 50)

        outputs_list = self.batched_generate(full_prompts,target_endpoint_url,target_endpoint_headers,target_endpoint_payload,target_endpoint_prompt_variable)
        log.info(f"EndpointModel.get_response - outputs_list: {outputs_list}")
        log.info("-" * 50)
        return outputs_list

class EndpointModel_Pair():
    def __init__(self,target_endpoint_url: str, target_endpoint_headers: dict, target_endpoint_payload: dict, target_endpoint_prompt_variable: str, max_retries: int = 5):
        self.max_retries = max_retries,
        self.target_endpoint_url = target_endpoint_url
        self.target_endpoint_headers = target_endpoint_headers
        self.target_endpoint_payload = target_endpoint_payload
        self.target_endpoint_prompt_variable = target_endpoint_prompt_variable
        log.info(f"Initialized EndpointModel with  endpoint_url: {target_endpoint_url},  headers: {self.target_endpoint_headers}, payload: {self.target_endpoint_payload}, prompt_variable: {self.target_endpoint_prompt_variable}")
    def extract_text_with_gpt(self, result: dict) -> str:
        """Use GPT model to extract text from the result."""
        gpt = GPT("gpt-3")  # Initialize GPT with the appropriate model
        conv = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Extract the relevant text from the following JSON response and provide only the text, nothing else:\n\n{result}\n\nOnly provide the text, nothing else."}
        ]
        extracted_text = gpt.generate(conv, max_n_tokens=1500, temperature=0.0, top_p=1.0)
        extracted_text = extracted_text.replace("Here is the relevant text from the JSON response:", "").strip()
        return extracted_text.strip()
    def generate(self, prompt: str,target_endpoint_url,target_endpoint_headers,target_endpoint_payload,target_endpoint_prompt_variable) -> str:
        headers = {key: value for key, value in target_endpoint_headers.items()}
        data: Dict[str, object] = {}
        for key, value in target_endpoint_payload.items():
            if isinstance(value, str):
                try:
                    data[key] = json.loads(value)
                except json.JSONDecodeError:
                    data[key] = value
            else:
                data[key] = value
        data[target_endpoint_prompt_variable] = f"Question: {prompt} Answer: "
        attempts = int(self.max_retries[0])
        for attempt in range(attempts):
            try:
                log.info(f"EndpointModel_Pair.generate - POST {target_endpoint_url} attempt {attempt+1}/{attempts}")
                response = requests.post(
                    self.target_endpoint_url,
                    headers=headers,
                    json=data,
                    verify=verify_ssl,
                    timeout=30
                )
            except requests.RequestException as net_exc:
                log.error(f"EndpointModel_Pair.generate - network error: {net_exc}")
                time.sleep(min(2 ** attempt, 8))
                continue

            if response.status_code != 200:
                log.error(f"EndpointModel_Pair.generate - HTTP {response.status_code}: {response.text[:200]}")
                time.sleep(min(2 ** attempt, 8))
                continue
            try:
                result = response.json()
            except ValueError:
                log.error("EndpointModel_Pair.generate - non-JSON response body")
                return "$ERROR$"
            text = self.extract_text_with_gpt(result)
            if text:
                return text
            log.warning("EndpointModel_Pair.generate - empty text, retrying")
        log.error("EndpointModel_Pair.generate - exhausted retries")
        return "$ERROR$"

    def batched_generate(self, prompts_list: List[str],target_endpoint_url,target_endpoint_headers,target_endpoint_payload,target_endpoint_prompt_variable) -> List[str]:
        log.info(f"Batched generate called with prompts_list: {prompts_list}")
        return [self.generate(prompt,target_endpoint_url,target_endpoint_headers,target_endpoint_payload,target_endpoint_prompt_variable) for prompt in prompts_list]

    def get_response(self, prompts_list: List[str],target_endpoint_url,target_endpoint_headers,target_endpoint_payload,target_endpoint_prompt_variable) -> List[str]:
        log.info(f"EndpointModel.get_response - batchsize: {len(prompts_list)}")
        log.info("-" * 50)
        log.info(f"EndpointModel.get_response - prompts_list: {prompts_list}")
        log.info("-" * 50)
        log.info(f"EndpointModel.get_response - target_endpoint_url: {target_endpoint_url}")
        log.info(f"EndpointModel.get_response - target_endpoint_headers: {target_endpoint_headers}")
        log.info(f"EndpointModel.get_response - target_endpoint_payload: {target_endpoint_payload}")
        log.info(f"EndpointModel.get_response - target_endpoint_prompt_variable: {target_endpoint_prompt_variable}")
        batchsize = len(prompts_list)
        log.info(f"EndpointModel.get_response - prompts_list: {prompts_list}")
        log.info("-" * 50)
        
        full_prompts = []
        for prompt in prompts_list:
            full_prompts.append(prompt)
            log.info(f"EndpointModel.get_response - full_prompts: {full_prompts}")
            log.info("-" * 50)

        outputs_list = self.batched_generate(full_prompts,target_endpoint_url,target_endpoint_headers,target_endpoint_payload,target_endpoint_prompt_variable)
        log.info(f"EndpointModel.get_response - outputs_list: {outputs_list}")
        log.info("-" * 50)
        return outputs_list
    
###############################################
# Inference Safety Limits and Concurrency Guard
###############################################
MAX_PROMPT_CHARS = 8000                 # Hard cap on incoming prompt length
MAX_NEW_TOKENS = 512                    # Prevent runaway generation / OOM
GENERATION_TIMEOUT_SECONDS = 60         # Wall-clock cap for one batch generation
_GEN_SEMAPHORE = threading.Semaphore(2) # Limit concurrent GPU generations

def _truncate_prompts(seq):
    truncated = []
    for p in seq:
        if isinstance(p, str):
            truncated.append(p[:MAX_PROMPT_CHARS])
        else:
            truncated.append(str(p)[:MAX_PROMPT_CHARS])
    return truncated

class HuggingFace(LanguageModel):
    def __init__(self, model_name, model, tokenizer):
        super().__init__(model_name)
        self.model = model 
        self.tokenizer = tokenizer
        self.eos_token_ids = [self.tokenizer.eos_token_id]
        log.info(f"HuggingFace.__init__ - model_name: {model_name}")
        log.info(f"HuggingFace.__init__ - model: {model}")
        log.info(f"HuggingFace.__init__ - tokenizer: {tokenizer}")
        log.info(f"HuggingFace.__init__ - eos_token_ids: {self.eos_token_ids}")
        log.info("-" * 50)

    def batched_generate(self,
                         full_prompts_list,
                         max_n_tokens: int,
                         temperature: float,
                         top_p: float = 1.0):
        """Safely generate a batch with concurrency, length, token, and timeout limits."""
        log.info(f"HuggingFace.batched_generate - full_prompts_list: {full_prompts_list}")
        log.info(f"HuggingFace.batched_generate - max_n_tokens: {max_n_tokens}")
        log.info(f"HuggingFace.batched_generate - temperature: {temperature}")
        log.info(f"HuggingFace.batched_generate - top_p: {top_p}")
        log.info("-" * 50)

        # Enforce safety caps
        safe_tokens = min(max_n_tokens, MAX_NEW_TOKENS)
        full_prompts_list = _truncate_prompts(full_prompts_list)

        acquired = _GEN_SEMAPHORE.acquire(timeout=120)
        if not acquired:
            log.error("HuggingFace.batched_generate - semaphore acquisition timeout")
            return ["$ERROR-CONCURRENCY$"] * len(full_prompts_list)

        inputs = {}
        output_ids = None
        try:
            with torch.inference_mode():
                inputs = self.tokenizer(full_prompts_list, return_tensors='pt', padding=True, truncation=True)
            inputs = {k: v.to(self.model.device.index) for k, v in inputs.items()}
            log.info("HuggingFace.batched_generate - inputs prepared")

            def _do_generate():
                with torch.inference_mode():
                    if temperature > 0:
                        return self.model.generate(
                            **inputs,
                            max_new_tokens=safe_tokens,
                            do_sample=True,
                            temperature=temperature,
                            eos_token_id=self.eos_token_ids,
                            top_p=top_p,
                        )
                    else:
                        return self.model.generate(
                            **inputs,
                            max_new_tokens=safe_tokens,
                            do_sample=False,
                            eos_token_id=self.eos_token_ids,
                            top_p=1,
                            temperature=1,
                        )

            start_ts = _time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(_do_generate)
                try:
                    output_ids = fut.result(timeout=GENERATION_TIMEOUT_SECONDS)
                except concurrent.futures.TimeoutError:
                    log.error("HuggingFace.batched_generate - generation timeout after %ss", GENERATION_TIMEOUT_SECONDS)
                    return ["$ERROR-TIMEOUT$"] * len(full_prompts_list)
            log.info("HuggingFace.batched_generate - generation finished in %.2fs", _time.time() - start_ts)

            if not self.model.config.is_encoder_decoder:
                output_ids = output_ids[:, inputs["input_ids"].shape[1]:]

            outputs_list = self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        except RuntimeError:
            log.exception("HuggingFace.batched_generate - runtime error during generation")
            return ["$ERROR-RUNTIME$"] * len(full_prompts_list)
        finally:
            if inputs:
                try:
                    for key in list(inputs.keys()):
                        inputs[key] = inputs[key].to('cpu')
                except Exception:
                    pass
            if output_ids is not None:
                try:
                    output_ids = output_ids.to('cpu')  # type: ignore[assignment]
                except Exception:
                    pass
            gc.collect()
            if torch.cuda.is_available():
                try:
                    torch.cuda.empty_cache()
                except Exception:
                    pass
            _GEN_SEMAPHORE.release()

        log.info(f"HuggingFace.batched_generate - outputs_list length: {len(outputs_list)}")
        log.info("-" * 50)
        return outputs_list
    
    # (Removed misplaced APIModel logic that was accidentally nested here)

class APIModel(LanguageModel):
    API_RETRY_SLEEP = 5
    API_ERROR_OUTPUT = "$ERROR$"
    API_QUERY_SLEEP = 1
    API_MAX_RETRY = 2
    API_TIMEOUT = 20
    API_HOST_LINK = ''

    MODEL_API_KEY = os.getenv("MODEL_API_KEY")

    def generate(self, conv: List[Dict], 
                 max_n_tokens: int,
                 temperature: float,
                 top_p: float):
        log.info("APIModel.generate max_n_tokens=%d temperature=%f top_p=%f", max_n_tokens, temperature, top_p)
        output = self.API_ERROR_OUTPUT
        for _ in range(self.API_MAX_RETRY):
            try:
                if temperature > 0:
                    payload = {
                        "top_p": top_p,
                        "num_beams": 1,
                        "temperature": temperature,
                        "do_sample": True,
                        "prompt": '',
                        "max_new_tokens": max_n_tokens,
                        "system_prompt": conv,
                    }
                else:
                    payload = {
                        "top_p": 1,
                        "num_beams": 1,
                        "temperature": 1,
                        "do_sample": False,
                        "prompt": '',
                        "max_new_tokens": max_n_tokens,
                        "system_prompt": conv,
                    }
                    if 'llama' in self.model_name:
                        payload['extra_eos_tokens'] = 0
                if 'llama' in self.model_name:
                    assert payload['prompt'] == ''
                    payload['prompt'] = deepcopy(payload['system_prompt'])
                    del payload['system_prompt']

                resp = urllib3.request(
                    "POST",
                    self.API_HOST_LINK,
                    headers={"Authorization": f"Api-Key {self.MODEL_API_KEY}"},
                    timeout=urllib3.Timeout(self.API_TIMEOUT),
                    json=payload,
                )
                resp_json = resp.json()
                if 'vicuna' in self.model_name:
                    if 'error' in resp_json:
                        log.error("APIModel.generate remote error: %s", resp_json.get('error'))
                    output = resp_json.get('output', self.API_ERROR_OUTPUT)
                else:
                    output = resp_json
                if isinstance(output, list) and output:
                    output = output[0]
                break
            except Exception as e:
                log.error("APIModel.generate exception: %s", e)
                time.sleep(self.API_RETRY_SLEEP)
            time.sleep(self.API_QUERY_SLEEP)
        return output

    def batched_generate(self,
                          convs_list: List[List[Dict]],
                          max_n_tokens: int,
                          temperature: float,
                          top_p: float = 1.0):
        return [self.generate(conv, max_n_tokens, temperature, top_p) for conv in convs_list]

class APIModelLlama7B(APIModel): 
    API_HOST_LINK = "LLAMA_API_LINK"
    MODEL_API_KEY = os.getenv("LLAMA_API_KEY")

class APIModelVicuna13B(APIModel): 
    API_HOST_LINK = "VICUNA_API_LINK" 
    MODEL_API_KEY = os.getenv("VICUNA_API_KEY")

class GPT(LanguageModel):
    API_RETRY_SLEEP = 5
    API_ERROR_OUTPUT = "$ERROR$"
    API_QUERY_SLEEP = 1
    API_MAX_RETRY = 2
    API_TIMEOUT = 20

    # Azure GPT-4 Configuration
    apibase_gpt4 = os.getenv("AZURE_GPT4_API_BASE")
    apiversion_gpt4 = os.getenv("AZURE_GPT4_API_VERSION")
    openaimodel_gpt4 = os.getenv("AZURE_GPT4_MODEL_NAME") 
    apikey_gpt4 = os.getenv("AZURE_GPT4_API_KEY")
    # Azure GPT-3 Configuration
    apibase_gpt3 = os.getenv("AZURE_GPT3_API_BASE")
    apiversion_gpt3 = os.getenv("AZURE_GPT3_API_VERSION")
    openaimodel_gpt3 = os.getenv("AZURE_GPT3_MODEL_NAME")  # Deployment name for GPT-3
    apikey_gpt3 = os.getenv("AZURE_GPT3_API_KEY")

    def set_api_configuration(self, model: str):
        log.info(f"GPT.set_api_configuration - model: {model}")
        if model in ["gpt-4", "gpt-4o-eastus2-rai", "gpt-4o-mini-eastus2-rai", "gpt-4o-westus"]:
            openai.api_key = self.apikey_gpt4
            openai.api_base = self.apibase_gpt4
            openai.api_version = self.apiversion_gpt4
            self.model_name = self.openaimodel_gpt4
        else:
            openai.api_key = self.apikey_gpt3
            openai.api_base = self.apibase_gpt3
            openai.api_version = self.apiversion_gpt3
            self.model_name = self.openaimodel_gpt3
        openai.api_type = 'azure'
        log.info(f"GPT.set_api_configuration - openai.api_key: {openai.api_key}")
        log.info(f"GPT.set_api_configuration - openai.api_base: {openai.api_base}")
        log.info(f"GPT.set_api_configuration - openai.api_version: {openai.api_version}")
        log.info(f"GPT.set_api_configuration - self.model_name: {self.model_name}")
        log.info("-" * 50)

    def generate(self, conv: List[Dict], 
                max_n_tokens: int, 
                temperature: float,
                top_p: float):
        '''
        Args:
            conv: List of dictionaries, OpenAI API format
            max_n_tokens: int, max number of tokens to generate
            temperature: float, temperature for sampling
            top_p: float, top p for sampling
        Returns:
            str: generated response
        '''
        # log.info(f"GPT.generate - conv: {conv}")
        log.info(f"GPT.generate - max_n_tokens: {max_n_tokens}")
        log.info(f"GPT.generate - temperature: {temperature}")
        log.info(f"GPT.generate - top_p: {top_p}")
        log.info("-" * 50)
        
        output = self.API_ERROR_OUTPUT
        model = self.model_name
        log.info(model)
        self.set_api_configuration(model)
        for attempt in range(self.API_MAX_RETRY):
            try:
                log.info(f"GPT.generate - Attempt: {attempt + 1}")
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                log.info(f"GPT.generate - conv: {conv}")
                log.info(f"GPT.generate - max_n_tokens: {max_n_tokens}")
                response = openai.ChatCompletion.create(
                            engine=self.model_name,
                            messages=conv,
                            max_tokens=max_n_tokens,
                            temperature=temperature,
                            top_p=top_p,
                            request_timeout=self.API_TIMEOUT,
                            )
                output = response["choices"][0]["message"].get("content", "")
                if output:
                    log.info(f"GPT.generate - output: {output}")
                    log.info("-" * 50)
                    break
                else:
                    log.warning("GPT.generate - Received empty content. Retrying...")
            # except openai.error.OpenAIError as e:
            #     log.info(f"GPT.generate - Exception: {type(e)}, {e}")
            except Exception as e: 
                log.error("language_models.py - GPT.generate exception: %s", e)
                time.sleep(self.API_RETRY_SLEEP)
        
            time.sleep(self.API_QUERY_SLEEP)
        if not output:
            log.error("GPT.generate - Max retries reached. Returning error output.")
        return output 
    
    def batched_generate(self, 
                        convs_list: List[List[Dict]],
                        max_n_tokens: int, 
                        temperature: float,
                        top_p: float = 1.0):
        # log.info(f"GPT.batched_generate - convs_list: {convs_list}")
        log.info(f"GPT.batched_generate - max_n_tokens: {max_n_tokens}")
        log.info(f"GPT.batched_generate - temperature: {temperature}")
        log.info(f"GPT.batched_generate - top_p: {top_p}")
        log.info("-" * 50)
        
        return [self.generate(conv, max_n_tokens, temperature, top_p) for conv in convs_list]

class Claude():
    API_RETRY_SLEEP = 10
    API_ERROR_OUTPUT = "$ERROR$"
    API_QUERY_SLEEP = 1
    API_MAX_RETRY = 5
    API_TIMEOUT = 20
    API_KEY = ""
   
    def __init__(self, model_name) -> None:
        self.model_name = model_name
        self.model = anthropic.Anthropic(
            api_key=self.API_KEY,
        )
        log.info(f"Claude.__init__ - model_name: {model_name}")
        log.info(f"Claude.__init__ - model: {self.model}")
        log.info("-" * 50)

    def generate(self, conv: List, 
                max_n_tokens: int, 
                temperature: float,
                top_p: float):
        '''
        Args:
            conv: List of conversations 
            max_n_tokens: int, max number of tokens to generate
            temperature: float, temperature for sampling
            top_p: float, top p for sampling
        Returns:
            str: generated response
        '''
        log.info(f"Claude.generate - conv: {conv}")
        log.info(f"Claude.generate - max_n_tokens: {max_n_tokens}")
        log.info(f"Claude.generate - temperature: {temperature}")
        log.info(f"Claude.generate - top_p: {top_p}")
        log.info("-" * 50)
        
        output = self.API_ERROR_OUTPUT
        for _ in range(self.API_MAX_RETRY):
            try:
                log.info(f"Claude.generate - Attempt: {_ + 1}")
                completion = self.model.completions.create(
                    model=self.model_name,
                    max_tokens_to_sample=max_n_tokens,
                    prompt=conv,
                    temperature=temperature,
                    top_p=top_p
                )
                output = completion.completion
                log.info(f"Claude.generate - output: {output}")
                log.info("-" * 50)
                break
            except anthropic.APIError as e:
                log.info(f"Claude.generate - Exception: {type(e)}, {e}")
                time.sleep(self.API_RETRY_SLEEP)
        
            time.sleep(self.API_QUERY_SLEEP)
        return output
    
    def batched_generate(self, 
                        convs_list: List[List[Dict]],
                        max_n_tokens: int, 
                        temperature: float,
                        top_p: float = 1.0):
        log.info(f"Claude.batched_generate - convs_list: {convs_list}")
        log.info(f"Claude.batched_generate - max_n_tokens: {max_n_tokens}")
        return [self.generate(conv, max_n_tokens, temperature, top_p) for conv in convs_list]   

class ChatGroqq():
    API_RETRY_SLEEP = 10
    API_ERROR_OUTPUT = "$ERROR$"
    API_QUERY_SLEEP = 0.5
    API_MAX_RETRY = 20
    API_TIMEOUT = 20
    API_KEY = os.getenv("GROQCLOUD_API_KEY")

    def __init__(self, model_name) -> None:
        self.model_name = model_name
        self.model= ChatGroq(
            groq_api_key=self.API_KEY,
            model_name="mixtral-8x7b-32768"
            )
        log.info(f"ChatGroqq.__init__ - model_name: {model_name}")
        log.info(f"ChatGroqq.__init__ - API_KEY: {self.API_KEY}")
        log.info(f"ChatGroqq.__init__ - model: {self.model}")
        log.info("-" * 50)


    def generate(self, conv: List[Dict], 
                max_n_tokens: int, 
                temperature: float,
                top_p: float):
        '''
        Args:
            conv: List of dictionaries, OpenAI API format
            max_n_tokens: int, max number of tokens to generate
            temperature: float, temperature for sampling
            top_p: float, top p for sampling
        Returns:
            str: generated response
        '''
        output = self.API_ERROR_OUTPUT
        log.info(f"ChatGroqq.generate - conv: {conv}")
        log.info(f"ChatGroqq.generate - max_n_tokens: {max_n_tokens}")
        log.info(f"ChatGroqq.generate - temperature: {temperature}")
        log.info(f"ChatGroqq.generate - top_p: {top_p}")
        log.info("-" * 50)

        for _ in range(self.API_MAX_RETRY):
            log.info(f"ChatGroqq.generate - Attempt")
            try: 
                
                response = self.model.invoke(conv)
                output = response.content
                if output:
                    log.info("language_models.py - ChatGroqq.generate - output: %s", output)
                    break
                else:
                    log.warning("language_models.py - ChatGroqq.generate - Received empty content. Retrying...")
            except Exception as e: 
                log.error("language_models.py - ChatGroqq.generate exception: %s", e)
                time.sleep(self.API_RETRY_SLEEP)
        
            time.sleep(self.API_QUERY_SLEEP)
        if not output:
            log.error("language_models.py - ChatGroqq.generate - Max retries reached. Returning error output.")
        return output  
    
    def batched_generate(self, 
                        convs_list: List[List[Dict]],
                        max_n_tokens: int, 
                        temperature: float,
                        top_p: float = 1.0):
        log.info(f"ChatGroqq.batched_generate - convs_list: {convs_list}")
        log.info(f"ChatGroqq.batched_generate - max_n_tokens: {max_n_tokens}")
        log.info(f"ChatGroqq.batched_generate - temperature: {temperature}")
        log.info(f"ChatGroqq.batched_generate - top_p: {top_p}")
        log.info("-" * 50)
        outputs = [self.generate(conv, max_n_tokens, temperature, top_p) for conv in convs_list]
        log.info(f"ChatGroqq.batched_generate - outputs: {outputs}")
        log.info("-" * 50)
        return outputs
        # return [self.generate(conv, max_n_tokens, temperature, top_p) for conv in convs_list]
        
   
class PaLM():
    API_RETRY_SLEEP = 10
    API_ERROR_OUTPUT = "$ERROR$"
    API_QUERY_SLEEP = 1
    API_MAX_RETRY = 5
    API_TIMEOUT = 20
    default_output = "I'm sorry, but I cannot assist with that request."
    API_KEY = os.getenv("PALM_API_KEY")

    def __init__(self, model_name) -> None:
        log.info("language_models.py - Initializing PaLM with model_name: %s", model_name)
        self.model_name = model_name
        genai.configure(api_key=self.API_KEY) 

    def generate(self, conv: List, 
                max_n_tokens: int, 
                temperature: float,
                top_p: float):
        '''
        Args:
            conv: List of dictionaries, 
            max_n_tokens: int, max number of tokens to generate
            temperature: float, temperature for sampling
            top_p: float, top p for sampling
        Returns:
            str: generated response
        '''
        log.info("language_models.py - PaLM.generate called with max_n_tokens: %d, temperature: %f, top_p: %f", max_n_tokens, temperature, top_p)
        output = self.API_ERROR_OUTPUT
        for _ in range(self.API_MAX_RETRY):            
            try:
                completion = genai.chat(
                    messages=conv,
                    temperature=temperature,
                    top_p=top_p
                )
                output = completion.last
                if output is None:
                    output = self.default_output
                else:
                    output = output[:(max_n_tokens*4)] 
                if output:
                    log.info("language_models.py - PaLM.generate - output: %s", output)
                    break
                else:
                    log.warning("language_models.py - PaLM.generate - Received empty content. Retrying...")
            except Exception as e:
                log.error("language_models.py - PaLM.generate exception: %s", e)
                time.sleep(self.API_RETRY_SLEEP)
        
            time.sleep(self.API_QUERY_SLEEP)
        if not output:
            log.error("language_models.py - PaLM.generate - Max retries reached. Returning error output.")
        return output
    
    def batched_generate(self, 
                        convs_list: List[List[Dict]],
                        max_n_tokens: int, 
                        temperature: float,
                        top_p: float = 1.0):
        log.info("language_models.py - PaLM.batched_generate called with max_n_tokens: %d, temperature: %f, top_p: %f", max_n_tokens, temperature, top_p)
        outputs = [self.generate(conv, max_n_tokens, temperature, top_p) for conv in convs_list]
        log.info("language_models.py - PaLM.batched_generate outputs: %s", outputs)
        return outputs

class GeminiPro():
    API_RETRY_SLEEP = 10
    API_ERROR_OUTPUT = "$ERROR$"
    API_QUERY_SLEEP = 1
    API_MAX_RETRY = 5
    API_TIMEOUT = 20
    default_output = "I'm sorry, but I cannot assist with that request."
    API_KEY = os.getenv("PALM_API_KEY")

    def __init__(self, model_name) -> None:
        log.info("language_models.py - Initializing GeminiPro with model_name: %s", model_name)
        self.model_name = model_name
        genai.configure(api_key=self.API_KEY) 
    def extract_text(self,response, default_output):

        try:
            candidate = response.candidates[0]
            if hasattr(candidate.content, "parts"):
                for part in candidate.content.parts:
                    if hasattr(part, "text"):
                        return part.text
            return default_output
        except Exception as e:
            return f"$ERROR$: {str(e)}"
    
    def generate(self, conv: List, 
                max_n_tokens: int, 
                temperature: float,
                top_p: float):
        '''
        Args:
            conv: List of dictionaries, 
            max_n_tokens: int, max number of tokens to generate
            temperature: float, temperature for sampling
            top_p: float, top p for sampling
        Returns:
            str: generated response
        '''
        log.info("language_models.py - GeminiPro.generate called with max_n_tokens: %d, temperature: %f, top_p: %f", max_n_tokens, temperature, top_p)
        output = self.API_ERROR_OUTPUT
        for _ in range(self.API_MAX_RETRY):            
            try:
                model = genai.GenerativeModel(self.model_name)

                response = model.generate_content(
                    contents=conv,
                    generation_config=genai.GenerationConfig(
                    candidate_count=1,
                    temperature=temperature,
                    top_p=top_p,
                    max_output_tokens=max_n_tokens,
                    )
                )



                output = self.extract_text(response, self.default_output)


                if output:
                    log.info("language_models.py - GeminiPro.generate - output: %s", output)
                    break
                else:
                    log.warning("language_models.py - GeminiPro.generate - Received empty content. Retrying...")
            except Exception as e:
                log.error("language_models.py - GeminiPro.generate exception: %s", e)
                time.sleep(self.API_RETRY_SLEEP)
        
            time.sleep(self.API_QUERY_SLEEP)
        if not output:
            log.error("language_models.py - GeminiPro.generate - Max retries reached. Returning error output.")
        return output
    
    def batched_generate(self, 
                        convs_list: List[List[Dict]],
                        max_n_tokens: int, 
                        temperature: float,
                        top_p: float = 1.0):
        log.info("language_models.py - GeminiPro.batched_generate called with max_n_tokens: %d, temperature: %f, top_p: %f", max_n_tokens, temperature, top_p)
        outputs = [self.generate(conv, max_n_tokens, temperature, top_p) for conv in convs_list]
        log.info("language_models.py - GeminiPro.batched_generate outputs: %s", outputs)
        return outputs
    
class GeminiModel(LanguageModel):    
    API_RETRY_SLEEP = 10
    API_ERROR_OUTPUT = "$ERROR$"
    API_QUERY_SLEEP = 1
    API_MAX_RETRY = 5
    API_TIMEOUT = 20
    default_output = "I'm sorry, but I cannot assist with that request."
    API_KEY = os.getenv("GOOGLE_API_KEY")
    def __init__(self, model_name) -> None:
        super().__init__(model_name)
        log.info("language_models.py - Initializing GeminiModel with model_name: %s", model_name)
        # genai.configure(api_key=self.API_KEY)
    
    def extract_text(self,response, default_output):

        try:
            candidate = response.candidates[0]
            if hasattr(candidate.content, "parts"):
                for part in candidate.content.parts:
                    if hasattr(part, "text"):
                        return part.text
            return default_output
        except Exception as e:
            return f"$ERROR$: {str(e)}"

    def generate(self, prompt: str, max_n_tokens: int, temperature: float, top_p: float):
        log.info("language_models.py - GeminiModel.generate called with max_n_tokens: %d, temperature: %f, top_p: %f", max_n_tokens, temperature, top_p)
        output = self.API_ERROR_OUTPUT
        for _ in range(self.API_MAX_RETRY):            
            try:
                # model = genai.GenerativeModel(self.model_name)
                # response = model.generate_content(
                #     contents=prompt,
                #     # contents=[{"role": "user", "parts": [prompt]}],
                #     generation_config=genai.GenerationConfig(
                #         candidate_count=1,
                #         temperature=temperature,
                #         top_p=top_p,
                #         max_output_tokens=max_n_tokens,
                #     )
                # )
                client = genai.Client(api_key=self.API_KEY)

                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )

                log.info(prompt)
                log.info(type(prompt))
                log.info("****************GEMINIMODEL****************")
                log.info("language_models.py - GeminiModel.generate - response: %s", response)
                output = self.extract_text(response, self.default_output)
               
                if output:
                    log.info("language_models.py - GeminiModel.generate - output: %s", output)
                    break
                else:
                    log.warning("language_models.py - GeminiModel.generate - Received empty content. Retrying...")
            except Exception as e:
                log.error("language_models.py - GeminiModel.generate exception: %s", e)
                time.sleep(self.API_RETRY_SLEEP)
        
            time.sleep(self.API_QUERY_SLEEP)
        if not output:
            log.error("language_models.py - GeminiModel.generate - Max retries reached. Returning error output.")
        return output
    
    def batched_generate(self, prompts_list: List[str], max_n_tokens: int, temperature: float, top_p: float = 1.0):
        log.info("language_models.py - GeminiModel.batched_generate called with max_n_tokens: %d, temperature: %f, top_p: %f", max_n_tokens, temperature, top_p)
        outputs = [self.generate(prompt, max_n_tokens, temperature, top_p) for prompt in prompts_list]
        log.info("language_models.py - GeminiModel.batched_generate outputs: %s", outputs)
        return outputs




class LlamaModel(LanguageModel):
    API_RETRY_SLEEP = 10
    API_ERROR_OUTPUT = "$ERROR$"
    API_QUERY_SLEEP = 1
    API_MAX_RETRY = 5
    API_TIMEOUT = 20
    default_output = "I'm sorry, but I cannot assist with that request."

    API_URL = os.getenv("LLAMA_API_URL")  
    API_KEY = os.getenv("LLAMA_API_KEY")  

    def __init__(self, model_name) -> None:
        super().__init__(model_name)
        log.info("language_models.py - Initializing LlamaModel with model_name: %s", model_name)

    def extract_text(self, response, default_output):
        try:
            return response['choices'][0]['message']['content']
        except Exception as e:
            return f"$ERROR$: {str(e)}"

    def generate(self, prompt: str, max_n_tokens: int, temperature: float, top_p: float):
        log.info("language_models.py - LlamaModel.generate called with max_n_tokens: %d, temperature: %f, top_p: %f", max_n_tokens, temperature, top_p)
        output = self.API_ERROR_OUTPUT

        for _ in range(self.API_MAX_RETRY):
            try:
                payload = {
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "top_p": top_p,
                    "frequency_penalty": 0,
                    "presence_penalty": 0,
                    "max_tokens": max_n_tokens
                }

                headers = {
                    "Authorization": self.API_KEY,
                    "Accept": "*/*",
                    "X-Cluster": "H100",  
                    "Content-Type": "application/json"
                }

                response = requests.post(
                    self.API_URL,
                    headers=headers,
                    json=payload,
                    timeout=self.API_TIMEOUT
                )
                response.raise_for_status()

                response_json = response.json()
                log.info("language_models.py - LlamaModel.generate - response: %s", response_json)
                output = self.extract_text(response_json, self.default_output)

                if output:
                    log.info("language_models.py - LlamaModel.generate - output: %s", output)
                    break
                else:
                    log.warning("language_models.py - LlamaModel.generate - Empty output received. Retrying...")

            except Exception as e:
                log.error("language_models.py - LlamaModel.generate exception: %s", e)
                time.sleep(self.API_RETRY_SLEEP)

            time.sleep(self.API_QUERY_SLEEP)

        if not output:
            log.error("language_models.py - LlamaModel.generate - Max retries reached. Returning error output.")

        return output

    def batched_generate(self, prompts_list: List[str], max_n_tokens: int, temperature: float, top_p: float = 1.0):
        log.info("language_models.py - LlamaModel.batched_generate called with max_n_tokens: %d, temperature: %f, top_p: %f", max_n_tokens, temperature, top_p)
        outputs = [self.generate(prompt, max_n_tokens, temperature, top_p) for prompt in prompts_list]
        log.info("language_models.py - LlamaModel.batched_generate outputs: %s", outputs)
        return outputs

# class BedrockModel(LanguageModel):
#     API_RETRY_SLEEP = 10
#     API_ERROR_OUTPUT = "$ERROR$"
#     API_QUERY_SLEEP = 1
#     API_MAX_RETRY = 5
#     default_output = "I'm sorry, but I cannot assist with that request."

#     def __init__(self, model_name) -> None:
#         super().__init__(model_name)
#         self.llm = None
#         self._setup_bedrock_client()

#     def _setup_bedrock_client(self):
#         try:
#             url = os.getenv("AWS_KEY_ADMIN_PATH")
#             response_admin = requests.get(url, verify=sslv[verify_ssl])
#             if response_admin.status_code == 200:
#                 data = response_admin.json()
#                 expiration_time = int(data['expirationTime'].split("hrs")[0])
#                 creation_time = datetime.strptime(data['creationTime'], "%Y-%m-%dT%H:%M:%S.%f")

#                 if self.is_time_difference_12_hours(creation_time, expiration_time):
#                     aws_access_key_id = data['awsAccessKeyId']
#                     aws_secret_access_key = data['awsSecretAccessKey']
#                     aws_session_token = data['awsSessionToken']

#                     bedrock_client = boto3.client(
#                         service_name=os.getenv("AWS_SERVICE_NAME"),
#                         region_name=os.getenv("REGION_NAME"),
#                         aws_access_key_id=aws_access_key_id,
#                         aws_secret_access_key=aws_secret_access_key,
#                         aws_session_token=aws_session_token,
#                         verify=sslv[verify_ssl]
#                     )

#                     self.llm = ChatBedrock(
#                         model_id=os.getenv("AWS_MODEL_ID"),
#                         model_kwargs={"max_tokens": 512, "temperature": 0.1},
#                         client=bedrock_client
#                     )

#                     log.info("BedrockModel - AWS token retrieved and client initialized.")
#                 else:
#                     log.error("BedrockModel - AWS session expired. Re-authentication required.")
#             else:
#                 log.error(f"BedrockModel - Error retrieving credentials: {response_admin.status_code}")
#         except Exception as e:
#             log.error(f"BedrockModel - Exception during setup: {str(e)}")

#     def generate(self, prompt: str, max_n_tokens: int, temperature: float, top_p: float):
#         output = self.API_ERROR_OUTPUT
#         for _ in range(self.API_MAX_RETRY):
#             try:
#                 if self.llm is None:
#                     log.warning("BedrockModel - LLM client not initialized.")
#                     return self.default_output

#                 log.info("BedrockModel.generate - Sending prompt.")
#                 response = self.llm.invoke(prompt)
#                 output = response.content if response and response.content else self.default_output
#                 break
#             except Exception as e:
#                 log.error(f"BedrockModel.generate - Error: {e}")
#                 time.sleep(self.API_RETRY_SLEEP)
#             time.sleep(self.API_QUERY_SLEEP)

#         return output or self.default_output

#     def batched_generate(self, prompts_list: List[str], max_n_tokens: int, temperature: float, top_p: float = 1.0):
#         outputs = [self.generate(prompt, max_n_tokens, temperature, top_p) for prompt in prompts_list]
#         return outputs
    
#     @staticmethod
#     def is_time_difference_12_hours(creation_time: datetime, expiration_hours: int) -> bool:
#         """
#         Returns True if the difference between now and creation_time is less than expiration_hours.
#         """
#         now = datetime.utcnow()
#         expiration_time = creation_time + timedelta(hours=expiration_hours)
#         return now < expiration_time
    


class BedrockModel(LanguageModel):
    API_RETRY_SLEEP = 10
    API_ERROR_OUTPUT = "$ERROR$"
    API_QUERY_SLEEP = 1
    API_MAX_RETRY = 5
    default_output = "I'm sorry, but I cannot assist with that request."

    def __init__(self, model_name) -> None:
        super().__init__(model_name)
        self.llm = None
        self._setup_bedrock_client()

    def _setup_bedrock_client(self):

        try:
            url = os.getenv("AWS_KEY_ADMIN_PATH")
            if not url:
                log.error("AWS_KEY_ADMIN_PATH environment variable not set.")
                return

            # verify_ssl = os.getenv("sslVerify")
            verify_ssl_env = os.getenv("sslVerify", "False")  # get the string from env
            verify_ssl = {"False": False, "True": True, "None": True}.get(verify_ssl_env, False)
            log.info(f"SSL verification: {verify_ssl} -> verify={verify_ssl}")

            log.info(f"Fetching AWS credentials from: {url}")
            response_admin = requests.get(url, verify=verify_ssl)

            if response_admin.status_code != 200:
                log.error(f"Failed to fetch credentials. HTTP {response_admin.status_code}")
                return

            data = response_admin.json()
            log.debug(f"Received credentials JSON: {data}")

        # Check if all required keys exist
            required_keys = ["awsAccessKeyId", "awsSecretAccessKey", "awsSessionToken", "creationTime", "expirationTime"]
            if not all(k in data for k in required_keys):
                log.error("Missing one or more required keys in the credentials JSON.")
                return

            expiration_hours = int(data['expirationTime'].split("hrs")[0])
            creation_time = datetime.strptime(data['creationTime'], "%Y-%m-%dT%H:%M:%S.%f")

            # if not self.is_time_difference_12_hours(creation_time, expiration_hours):
            #     log.warning("AWS credentials are expired. Skipping client initialization.")
            #     return  # or re-trigger a new fetch if your API supports that

            # aws_access_key_id = data['awsAccessKeyId']
            # aws_secret_access_key = data['awsSecretAccessKey']
            # aws_session_token = data['awsSessionToken']
            aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID", data['awsAccessKeyId'])
            aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", data['awsSecretAccessKey'])
            aws_session_token = os.getenv("AWS_SESSION_TOKEN", data['awsSessionToken'])

            region_name = os.getenv("REGION_NAME", "us-east-1")
            service_name = os.getenv("AWS_SERVICE_NAME", "bedrock-runtime")
            model_id = os.getenv("AWS_MODEL_ID")

            if not model_id:
                log.error("AWS_MODEL_ID is not set. Cannot initialize Bedrock client.")
                return

            log.info(f"Using AWS_MODEL_ID: {model_id}")

            bedrock_client = boto3.client(
                service_name=service_name,
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
                verify=verify_ssl
            )

            self.llm = ChatBedrock(
                model_id=model_id,
                model_kwargs={"max_tokens": 512, "temperature": 0.1},
                client=bedrock_client
            )

            log.info("Bedrock client initialized successfully with fresh credentials.")

        except Exception as e:
            log.error(f"BedrockModel - Exception during setup: {e}")
            log.error(traceback.format_exc())

    # LEGACY (disabled) _setup_bedrock_client implementation below used verify=False.
    # It is intentionally retained only for reference and MUST NOT be re-enabled.
    # If resurrecting, always use: response_admin = requests.get(url, verify=verify_ssl, timeout=30)
    # def _setup_bedrock_client(self):
    #     try:
    #         url = os.getenv("AWS_KEY_ADMIN_PATH")
    #         log.info(f"Fetching AWS credentials from: {url}")
    #         log.info(f"SSL verification set to: {verify_ssl}")
    #         response_admin = requests.get(url, verify=verify_ssl, timeout=30)
    #         log.info(f"Received response with status code: {response_admin.status_code}")

    #         if response_admin.status_code == 200:
    #             data = response_admin.json()
    #             log.debug(f"Credential data: {data}")

    #             expiration_time = int(data['expirationTime'].split("hrs")[0])
    #             creation_time = datetime.strptime(data['creationTime'], "%Y-%m-%dT%H:%M:%S.%f")

    #             if self.is_time_difference_12_hours(creation_time, expiration_time):
    #                 log.info("AWS session is valid, initializing Bedrock client...")

    #                 aws_access_key_id = data['awsAccessKeyId']
    #                 aws_secret_access_key = data['awsSecretAccessKey']
    #                 aws_session_token = data['awsSessionToken']

    #                 bedrock_client = boto3.client(
    #                     service_name=os.getenv("awsservicename", "bedrock-runtime"),
    #                     region_name=os.getenv("region_name", "us-east-1"),
    #                     aws_access_key_id=aws_access_key_id,
    #                     aws_secret_access_key=aws_secret_access_key,
    #                     aws_session_token=aws_session_token,
    #                     verify=verify_ssl
    #                 )

    #                 model_id = os.getenv("awsmodelid")
    #                 log.info(f"Using AWS_MODEL_ID: {model_id}")

    #                 self.llm = ChatBedrock(
    #                     model_id=model_id,
    #                     model_kwargs={"max_tokens": 512, "temperature": 0.1},
    #                     client=bedrock_client
    #                 )

    #                 log.info("BedrockModel - AWS token retrieved and client initialized.")
    #             else:
    #                 log.error("BedrockModel - AWS session expired. Re-authentication required.")
    #         else:
    #             log.error(f"BedrockModel - Error retrieving credentials: HTTP {response_admin.status_code}")

    #     except Exception as e:
    #         log.error(f"BedrockModel - Exception during setup: {e}")
    #         log.error(traceback.format_exc())

    def generate(self, prompt: str, max_n_tokens: int, temperature: float, top_p: float):
        output = self.API_ERROR_OUTPUT
        for attempt in range(self.API_MAX_RETRY):
            try:
                if self.llm is None:
                    log.warning("BedrockModel - LLM client not initialized.")
                    return self.default_output

                log.info(f"BedrockModel.generate - Sending prompt (Attempt {attempt + 1})")
                response = self.llm.invoke(prompt)
                output = response.content if response and response.content else self.default_output
                log.debug(f"BedrockModel.generate - Response: {output}")
                break
            except Exception as e:
                log.error(f"BedrockModel.generate - Error: {e}")
                log.error(traceback.format_exc())
                time.sleep(self.API_RETRY_SLEEP)
            time.sleep(self.API_QUERY_SLEEP)

        return output or self.default_output

    def batched_generate(self, prompts_list: List[str], max_n_tokens: int, temperature: float, top_p: float = 1.0):
        log.info(f"BedrockModel.batched_generate - Generating for batch of {len(prompts_list)} prompts.")
        outputs = [self.generate(prompt, max_n_tokens, temperature, top_p) for prompt in prompts_list]
        return outputs

    @staticmethod
    def is_time_difference_12_hours(creation_time: datetime, expiration_hours: int) -> bool:
        """
        Returns True if the current time is within the expiration window from the creation time.
        """
        from datetime import timezone
        # Ensure creation_time is timezone-aware (assume UTC if naive)
        if creation_time.tzinfo is None or creation_time.tzinfo.utcoffset(creation_time) is None:
            creation_time = creation_time.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        expiration_time = creation_time + timedelta(hours=expiration_hours)
        return now < expiration_time
