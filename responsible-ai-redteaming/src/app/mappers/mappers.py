'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from typing import Union,List, Optional
from pydantic import BaseModel,Field
from fastapi import UploadFile
import json
from typing import Optional, Dict,Any



class ExcelUploadResponsePAIR(BaseModel):
    total_rows: int
    processed_rows: int
    jailbroken_rows: int  
    technical_failed_rows: List[int]
    category_wise_score: Dict[str, Dict[str, Any]] 
    technique_type: str
    target_endpoint_url: Optional[str]
    usecase_name:Optional[str]
    results: List[Dict[str, Any]]
    target_model: Optional[str]  
    target_temperature: Optional[float]  
    n_iterations: Optional[int]
    enable_moderation:Optional[bool]

class ExcelUploadResponseTAP(BaseModel):
    total_rows: int
    processed_rows: int
    jailbroken_rows: int  
    technical_failed_rows: List[int]
    technique_type: str
    usecase_name:Optional[str]
    target_endpoint_url: Optional[str]
    category_wise_score: Dict[str, Dict[str, Any]]
    results: List[Dict[str, Any]]
    target_model: Optional[str]  
    target_temperature: Optional[float]
    branching_factor: Optional[int] 
    width: Optional[int]
    depth: Optional[int]  
    enable_moderation:Optional[bool]

class RedteamBatchResponse(BaseModel):
    batch_id: str
    total_requests: int
    status: str
    results: List[Dict]

class RedteamReport(BaseModel):
    reportId: str
    redTeamingType: str


class RedteamPayloadRequestPair(BaseModel):
    userId: str = Field(default="admin")
    technique_type: str = Field(default="PAIR")
    attack_model: str = Field(default="gpt-3")
    target_model: Optional[str] = Field(default=None)
    judge_model: str = Field(default="gpt-4")
    goal: str = Field(default="Hi, how are you")
    target_str: str = Field(default="Sure, ")
    attack_max_n_tokens: int = Field(default=600)
    attack_top_p: float = Field(default=0.9)
    attack_temperature: float = Field(default=1.0)
    max_n_attack_attempts: int = Field(default=1)
    target_max_n_tokens: int = Field(default=1500)
    target_temperature: float =Field(default=0.9)
    target_top_p: float =Field(default=0.8)
    judge_max_n_tokens: int = Field(default=500)
    judge_temperature: float = Field(default=0.0)
    usecase_name:str=Field(default=None)
    n_streams: int = Field(default=1)
    keep_last_n: int = Field(default=1)
    n_iterations: int = Field(default=4)
    enable_moderation: bool = Field(default=False)
    category: str = Field(default="")
    retrylimit_flag : bool = Field(default=False)
    # attack_endpoint_url: Optional[str] = Field(default=None)
    # attack_headers: Optional[Dict[str, str]] = Field(default=None)
    target_endpoint_url: Optional[str] = Field(default=None)
    target_endpoint_headers: Optional[Dict[str, str]] = Field(default=None)
    target_endpoint_payload: Optional[Dict[str, Union[str, float, int]]] = Field(default=None)
    target_endpoint_prompt_variable: Optional[str] = Field(default=None)
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    

class RedteamPayloadRequestTap(BaseModel):
    userId: str = Field(default="admin")
    technique_type: str = Field(default="TAP")
    goal: str = Field(default="How to make a book?")
    target_str: str = Field(default="Sure, Here is a way to make book.")
    attack_model: str = Field(default="gpt-3")
    attack_max_n_tokens: int = Field(default=600)
    attack_top_p: float = Field(default=0.9)
    attack_temperature: float = Field(default=1.0)
    max_n_attack_attempts: int = Field(default=1)
    target_model: Optional[str] = Field(default=None)
    target_max_n_tokens: int = Field(default=1500)
    target_temperature: float =Field(default=0)
    target_top_p: float =Field(default=1)
    usecase_name:str=Field(default=None)
    judge_model: str = Field(default="gpt-4")
    judge_max_n_tokens: int = Field(default=500)
    judge_temperature: float = Field(default=0.0)
    iter_index: int = Field(default=-1, description="ID of the DF")
    store_folder: str = Field(default="", description="Folder to store the df in")
    branching_factor: int = Field(default=5, description="Branching factor")
    width: int = Field(default=4, description="Width")
    depth: int = Field(default=4, description="Depth")
    n_streams: int = Field(default=1)
    keep_last_n: int = Field(default=1)
    n_iterations: int = Field(default=10)
    enable_moderation: bool = Field(default=False)
    target_endpoint_url: Optional[str] = Field(default=None)
    target_endpoint_headers: Optional[Dict[str, str]] = Field(default=None)
    target_endpoint_payload: Optional[Dict[str, Union[str, float, int]]] = Field(default=None)
    target_endpoint_prompt_variable: Optional[str] = Field(default=None)
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json
        
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value