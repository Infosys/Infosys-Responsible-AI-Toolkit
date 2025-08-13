'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
########################################### IMPORT LIBRARIES ############################################

from service.textTemplate_service import *
from PIL import Image
import base64
from io import BytesIO
from utilities.utility_methods import *

###############################   Template based Guardrails (LLM Evaluation) #######################

multimodal_log_dict = {}

BASELINE_PROMPT_FOR_MULTIMODAL = """You are a detail-oriented and highly analytical LLM to detect {detection_type} in the provided prompt(if provided) and image(if provided).
        {evaluation_criteria}
        {prompting_instructions}
        {few_shot}
        Given the below User Query , generate an output with following fields separated by comma as shown below:
        {output_format}
"""


def get_multimodal_response(template_name,modelName,messages):
    MODEL_NAME,API_BASE,API_KEY,API_VERSION,API_TYPE = config(modelName)
    try:
        client = AzureOpenAI(
                        azure_endpoint=API_BASE,
                        api_key=API_KEY,
                        api_version=API_VERSION
                    )

        response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    max_tokens=500)
        
        log.info(f"response from gpt4o : {response}")
        content = response.choices[0].message.content
        content = content.replace("{{","{").replace("}}","}").replace("```","").replace("json","").replace("\n","")
        content = content if content.startswith("{") else "{\n" + content + "\n}"
        content=re.sub(r'(?<!")None(?!")','"None"',content)
        log.info(f"content : {content}")
        response_dict = json.loads(content)
        
        response_dict['threshold']=0.6

        if template_name == "Image Toxicity Check":
            response_dict["result"] = "PASSED"
            for s in response_dict["score"]:
                if s["metricScore"] > response_dict['threshold']:
                    response_dict["result"] = "FAILED"
                    break
        else:
            response_dict['result']="FAILED" if response_dict['score'] > response_dict['threshold'] else "PASSED"

        return response_dict
                
    except Exception as e:
        line_number = traceback.extract_tb(e.__traceback__)[0].lineno
        log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at Multimodal call"})
        log.error(f"Error occured : {line_number,e}")




class ImageTemplateService:
    '''Encodes image using Base64 encoding'''
    def encode_image(self,images):
        try:
            encoded_images=[]
            for image in images:
                im = Image.open(image)
                buffered = BytesIO()
                if im.format in ["JPEG","jpg","jpeg"]:
                    format="JPEG"
                elif im.format in ["PNG","png"]:
                    format="PNG"
                elif im.format in ["GIF","gif"]:
                    format="GIF"
                elif im.format in ["BMP","bmp"]:
                    format="BMP"
                im.save(buffered,format=format)
                buffered.seek(0) 
                encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
                encoded_images.append(encoded_image)

            return encoded_images
        except IOError as e:
            line_number = traceback.extract_tb(e.__traceback__)[0].lineno
            multimodal_log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                    "Error Module":"Failed in Multimodal check"})
            log.error(f"Error opening image file: {line_number,e}")
        


    def generate_response(self,req,headers):
        try:
            id = uuid.uuid4().hex
            request_id_var.set(id)
            headers['id']=id
            multimodal_log_dict[request_id_var.get()]=[]
            userid = req['userid']
            base64_images=self.encode_image(req['Image'])
            vars = get_templates(req['TemplateName'],userid)
            args ={"detection_type":req['TemplateName'],
                    "evaluation_criteria":vars["evaluation_criteria"],
                    "few_shot":vars["few_shot_examples"],
                    "output_format":get_output_format(req['TemplateName'])}
            
            messages = [{"role": "user","content":[]}]
            for image in base64_images:
                messages[0]["content"].append({"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{image}"}})
            
            if req['Prompt'] != "":
                messages[0]["content"].append({"type": "text", "text": req['Prompt']})
                
            st = time.time()
            if req['TemplateName'] == "Image Restricted Topic Check":
                args["prompting_instructions"] = vars["prompting_instructions"] + "Get the topics from {topics} to be restricted.".replace("{topics}",req['Restrictedtopics'])
                messages[0]["content"].append({"type": "text", "text": BASELINE_PROMPT_FOR_MULTIMODAL.format(**args)})
                response = get_multimodal_response(req['TemplateName'],req['ModelName'],messages)
            else:
                args["prompting_instructions"]=vars["prompting_instructions"]
                messages[0]["content"].append({"type": "text", "text": BASELINE_PROMPT_FOR_MULTIMODAL.format(**args)})
                response = get_multimodal_response(req['TemplateName'],req['ModelName'],messages)
            
            final_response = {'uniqueid':id,'userid':userid, 
                              'lotNumber': str(req['lotNumber']), 
                              'created': str(datetime.now()),
                              'model': req['ModelName'],
                              'moderationResults':response,
                              'evaluation_check':req['TemplateName'],
                              'timeTaken':str(round(time.time() - st, 3))+"s"}
            
            if req['userid'] !="None":
                    for d in prompt_template[req['userid']]:
                        if d["templateName"]==req['TemplateName']:
                            final_response['description'] = d["description"]
            
            return final_response

        except Exception as e:
            line_number = traceback.extract_tb(e.__traceback__)[0].lineno
            multimodal_log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                    "Error Module":"Failed at Multimodal model call"})
            log.error(f"Error occured : {line_number,e}")


