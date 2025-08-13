'''
Copyright 2024-2025 Infosys Ltd.

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

from llm.service.azure_open_ai_img_gen import Azure
from llm.mapper.mapper import ImageGenerationResponse
from llm.config.logger import CustomLogger, request_id_var
request_id_var.set("startup")

from dotenv import load_dotenv
load_dotenv()

log = CustomLogger()

class LLMService:

    def generate_image(payload) -> ImageGenerationResponse:
        if payload.prompt is None or payload.prompt == "":
            raise Exception("Prompt is required to generate an image.")
        if payload.model is None or payload.model == "":
            raise Exception("Model is required to generate an image.")
        
        try:
            prompt = payload.prompt
            model = payload.model

            uuid_value = request_id_var.get()

            base64_image = Azure().generate_image(prompt, model)

            return ImageGenerationResponse(image=base64_image)
        except Exception as e:
            log.error(f"UUID: {uuid_value}, Request error: {e}", exc_info=True)
            raise

