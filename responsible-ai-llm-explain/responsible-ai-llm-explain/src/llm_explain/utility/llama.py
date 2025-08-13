'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from llm_explain.config.logger import CustomLogger
import requests
import os

log = CustomLogger()


class Llamacompletion:
    def __init__(self):
        self.url = os.environ.get("LLAMA_ENDPOINT")

    def textCompletion(self, text, technique):

        if technique == "THOT":

            messages =f"""[INST]<<SYS>>You should be a responsible Assistant and should not generate harmful or 
            misleading content! Please answer the following user query in a responsible way. 
            Walk me through this context in manageable parts step by step, summarising and analysing as we go.
            Engage in a step-by-step thought process to explain how the answer was derived. 
            Additionally, associate the source with the answer using the format:
                    Result: "answer"
                    Explanation: "step-by-step reasoning"
                    Always give response in a textual format dont give in json or any code format.<</SYS>>
                    User Query: {text} [/INST]"""
            
        elif technique == "Reread THOT":
        
            messages = f"""[INST]<<SYS>>You should be a responsible Assistant and should not generate harmful or 
                misleading content! Please answer the following user query in a responsible way. 
                Walk me through this context in manageable parts step by step, summarising and analysing as we go.
                Engage in a step-by-step thought process to explain how the answer was derived. 
                Additionally, associate the source with the answer using the format:
                        Result: "answer"
                        Explanation: "step-by-step reasoning"
                        Always give response in a textual format dont give in json or any code format.<</SYS>>
                        User Query: {text} Read the question again {text} [/INST]"""
            
        elif technique == "COT":
            messages = f"""[INST]<<SYS>>You should be a responsible Assistant and should not generate harmful or 
            misleading content! Please answer the following user query in a responsible way. 
            Let's think the answer step by step and explain step by step how you got the answer. 
            Please provide website link as references if you are refering from internet to get the answer.
            Always give response in a textual format dont give in json or any code format.<</SYS>>
            User Query : {text} [/INST]"""

        
        input = {
            "inputs": messages,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.1,
                "num_return_sequences": 1,
                "do_sample": True
            }
            }
        log.info(f"inside Llama completions function")
        response = requests.post(self.url, json=input, verify=False)
        response.raise_for_status()
        generated_text = response.json()[0]["generated_text"]
        output_text = generated_text.split("[/INST]")[1]
        return output_text, 0, "","0"
