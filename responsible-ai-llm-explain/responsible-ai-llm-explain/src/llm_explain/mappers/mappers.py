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

"""
module: LLM Explainability
fileName: mappers.py
description: A Pydantic model object for usecase entity model
             which maps the data model to the usecase entity schema
"""

from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict
from enum import Enum
import json

class Methods(str, Enum):
    ALL = "All"
    TOKEN_IMPORTANCE = "Token-Importance"
    EVALUATION_METRICS = "Evalution-Metrics"
    THOT = "ThoT"
    REREAD_THOT = "ReRead-ThoT"
    GOT = "GoT"
    COT = "CoT"
    COV = "CoV"
    LOT = "LoT"
    SAFE_SEARCH = "Safe-Search"
    SENTIMENT_ANALYSIS = "Sentiment-Analysis"

class ResponseTypes(str, Enum):
    JSON = "json"
    EXCEL = "excel"

class EndPointRequest(BaseModel):
    modelEndpointUrl: Optional[str] = Field(example="http://localhost:8002/model/endpoint")
    endpointInputParam: Optional[Dict] = Field(example={"input_parameter": "inputs", "parameters": {}})
    endpointOutputParam: Optional[str] = Field(example="['output']['choices'][0]['text']")

    class Config:
        from_attributes = True

class SentimentAnalysisRequest(BaseModel):
    inputPrompt: str = Field(example="Unfortunately the movie served with bad visuals but the actors performed well")
    modelName: Optional[str] = Field(example="gpt4")

    class Config:
        from_attributes = True

class SentimentAnalysisResponse(BaseModel):
    explanation: List

    class Config:
        from_attributes = True

class UncertainityRequest(BaseModel):
    inputPrompt: str = Field(example="Who are the co-founders of Infosys?")
    response: str = Field(example="Infosys was co-founded by Narayana Murthy along with six other engineers: Nandan Nilekani, S. Gopalakrishnan (Kris), S. D. Shibulal, K. Dinesh, N. S. Raghavan, and Ashok Arora. Established in 1981, Infosys started with a modest capital of $250 and has since grown into one of the largest IT services companies in the world. Narayana Murthy, often regarded as the face of Infosys, played a pivotal role in shaping the company's culture and vision, while the combined efforts of all co-founders contributed to its remarkable growth and success in the global IT industry.")
    context: Optional[str] = None
    modelName: Optional[str] = Field(example="gpt4")
    endpointDetails: Optional[EndPointRequest] = None

    class Config:
        from_attributes = True

class UncertainityResponse(BaseModel):
    uncertainty: Dict = Field(example={"score": 0.5, "explanation": "The response is uncertain as it mentions the co-founders of Infosys without providing specific details.", "recommendation": "Maintain the grammatical correctness and focus on providing additional information."})
    coherence: Dict = Field(example={"score": 0.8, "explanation": "The response is relevant to the prompt as it provides information about the co-founders of Infosys.", "recommendation": "Maintain the grammatical correctness and focus on providing additional information."})
    time_taken: float = Field(example=0.5)
    token_cost: Optional[float] = None
    
    class Config:
        from_attributes = True

class TokenImportanceResponse(BaseModel):
    token_importance_mapping:List
    time_taken: float = Field(example=0.5)
    token_cost: Optional[float] = None
    
    class Config:
        from_attributes = True

class TokenImportanceRequest(BaseModel):
    inputPrompt: str = Field(example="Who are the co-founders of Infosys?")
    modelName: Optional[str] = Field(example="GPT")
    endpointDetails: Optional[EndPointRequest] = None

    class Config:
        from_attributes = True

class GoTRequest(BaseModel):
    inputPrompt: str = Field(example="Who are the co-founders of Infosys?")
    modelName: Optional[str] = Field(example="gpt4")

    class Config:
        from_attributes = True
        
class GoTResponse(BaseModel):
    final_thought: str = Field(example='The co-founders of Infosys are N. R. Narayana Murthy, ...')
    score: float = Field(example=9.5)
    token_cost: float = Field(example=0.5)
    consistency_level: str = Field(example='High Consistent')
    time_taken: float = Field(example=0.5)
    
    class Config:
        from_attributes = True

class SafeSearchRequest(BaseModel):
    inputPrompt: str = Field(example="Who are the co-founders of Infosys?")
    llm_response: str = Field(example="Infosys, a global leader in technology services and consulting, was founded in 1981 by seven visionaries: N.R. Narayana Murthy, Nandan Nilekani, S. Gopalakrishnan, S.D. Shibulal, K. Dinesh, N.S. Raghavan, and Ashok Arora. These co-founders combined their expertise and entrepreneurial spirit to create a company that has since grown into one of the largest and most respected IT services firms in the world. Infosys, headquartered in Bangalore, India, has been instrumental in the global IT revolution, providing innovative solutions and services to clients across various industries. The founders' commitment to excellence and their forward-thinking approach laid a strong foundation for the company's enduring success.")
    modelName: Optional[str] = Field(example="gpt4")

    class Config:
        from_attributes = True

class SafeSearchResponse(BaseModel):
    internetResponse: List = Field(example="The co-founders of Infosys are N. R. Narayana Murthy, ...")
    metrics: List = Field(examples=[])
    time_taken: float = Field(example=0.5)
    token_cost: Optional[float] = None

    class Config:
        from_attributes = True

class rereadRequest(BaseModel):
    inputPrompt: str = Field(example="Who are the co-founders of Infosys?")
    modelName: Optional[str] = Field(example="GPT4")
    endpointDetails: Optional[EndPointRequest] = None

    class Config:
        from_attributes = True

class rereadResponse(BaseModel):
    response: dict = {}
    time_taken: float = Field(example=0.5)
    token_cost: Optional[float] = None

    class Config:
        from_attributes = True

class openAIRequest(BaseModel):
    inputPrompt: str = Field(example= "Which is the biggest country in the world?")
    temperature: Optional[str] = Field(example="0")
    modelName: Optional[str] =Field(example="GPT4")
    endpointDetails: Optional[EndPointRequest] = None

    class Config:
        from_attributes = True

class CoTResponse(BaseModel):
    explanation: str = Field(example="Russia is the largest country in the world by land area, covering approximately 17,098,242 square kilometers.")
    time_taken: float = Field(example=0.5)
    token_cost: Optional[float] = None

    class Config:
        from_attributes = True

class CoVRequest(BaseModel):
    inputPrompt: str = Field(example="Which is the biggest country in the world?")
    complexity : str = Field(enum=["simple", "medium", "complex"])
    modelName: Optional[str] =Field(example="gpt4")
    translate: str = Field(example="no")
    endpointDetails: Optional[EndPointRequest] = None

    class Config:
        from_attributes = True

class CoVResponse(BaseModel):
    original_question: str = Field(example="Which is the biggest country in the world?")
    baseline_response : str = Field(example="Russia is the largest country in the world by land area, covering approximately 17,098,242 square kilometers.")
    verification_questions: str =Field(example="1. What is the largest country in the world by land area? 2. How many square kilometers does Russia cover? 3. What is the approximate land area of Russia? 4. What is the total area of Russia in square kilometers? 5. What is the land area of Russia in square kilometers?")
    verification_answers: str = Field(example="1. Russia is the largest country in the world by land area. 2. Russia covers approximately 17,098,242 square kilometers. 3. The approximate land area of Russia is 17,098,242 square kilometers. 4. The total area of Russia is 17,098,242 square kilometers. 5. The land area of Russia is 17,098,242 square kilometers.")
    final_answer: str = Field(example="Russia is the largest country in the world by land area, covering approximately 17,098,242 square kilometers.")
    time_taken: float = Field(example=0.5)
    token_cost: Optional[float] = None

    class Config:
        from_attributes = True

class FileUploadRequest(BaseModel):
    methods: List[Methods]
    responseFileType: ResponseTypes
    userId: Optional[str] = ""
    
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    
    class Config:
        from_attributes = True

class lotRequest(BaseModel):
    inputPrompt: str = Field(example="Who are the co-founders of Infosys?")
    llmResponse: Optional[str] = Field(example="Infosys was co-founded by Narayana Murthy along with six other engineers: Nandan Nilekani, S. Gopalakrishnan (Kris), S. D. Shibulal, K. Dinesh, N. S. Raghavan, and Ashok Arora. Established in 1981, Infosys started with a modest capital of $250 and has since grown into one of the largest IT services companies in the world. Narayana Murthy, often regarded as the face of Infosys, played a pivotal role in shaping the company's culture and vision, while the combined efforts of all co-founders contributed to its remarkable growth and success in the global IT industry.")
    modelName: Optional[str] = Field(example="GPT4")
    endpointDetails: Optional[EndPointRequest] = None

    class Config:
        from_attributes = True

class lotResponse(BaseModel):
    response: dict = {}
    time_taken: float = Field(example=0.5)
    token_cost: Optional[float] = None

    class Config:
        from_attributes = True