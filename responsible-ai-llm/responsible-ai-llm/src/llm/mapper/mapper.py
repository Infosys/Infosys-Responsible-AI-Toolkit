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

from pydantic import BaseModel, Field
from typing import Optional

class OpenAiRequest(BaseModel):
    messages:str= Field(..., example="""[{"role": "user", "content": "Which is the biggest country in the world?"}]""")
    temperature:float= Field(...,example="0")
    model:str=Field(...,example="gpt4")
    max_tokens:Optional[int]=Field(None,example="800")
    top_p:Optional[float]=Field(None,example="1.0")
    frequency_penalty:Optional[float]=Field(None,example="0")
    presence_penalty:Optional[float]=Field(None,example="0")
    stop:Optional[str] = Field(None,example="None")

    class Config:
        from_attributes = True
        
class Choice(BaseModel):
    text:str= Field(example="Russia is the biggest country by area.")
    index:int=Field(example=0)
    finishReason:str=Field(example="length")

    class Config:
        from_attributes = True

class ImageGenerationRequest(BaseModel):
    prompt: str = Field(example="Generate an image of a doctor with a stethoscope.")
    model: str = Field(example="DALL-E-2")

    class Config:
        from_attributes = True

class ImageGenerationResponse(BaseModel):
    image: str = Field(example="base64 encoded image")

    class Config:
        from_attributes = True