"""
SPDX-License-Identifier: MIT

Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from pydantic import BaseModel, Field,Extra
from typing import Optional, Union, List
from enum import Enum
from fastapi import Depends,Request,APIRouter, HTTPException,Form,UploadFile,File

class RetrievalRequest(BaseModel):
    text: str = Field(example="Total area of India")
    id: str= Field(example="dhf8327y8r8732gr87")

class gevalRequest(BaseModel):
    text: str = Field(example="How many moons do earth have?")
    response: str = Field(example="Earth have only one moon")
    sourcetext: str= Field(example="source")
    llmtype: str = Field(example="openai")

class defaultRetrievalRequest(BaseModel):
    fileupload:bool = Field(example=True)
    text: str = Field(example="Total area of India")
    llmtype: str = Field(example="openai")
    vectorestoreid :Optional[str] = Field(example="764r876634874")
    
class covRequest(BaseModel):
    fileupload:bool = Field(example=True)
    text: str = Field(example="Total area of India")
    vectorestoreid :Optional[str] = Field(example="764r876634874")
    complexity : str = Field(enum=["simple", "medium", "complex"])
    llmtype: str = Field(example="openai")   
    
class cachingRequest(BaseModel):
    vectorestoreid: str = Field(example="764r876634874")
    llmtype: str = Field(example="openai")

class removecachingRequest(BaseModel):
    id: int = Field(example="34545645645645")
    
class Show_score(BaseModel):
    prompt: str = Field(example="Total area of India")
    response: str = Field(example="Response to the input question")
    sourcearr: List[str] = Field(example=["source 1", "source 2"])

class qachatbotRequest(BaseModel):
    text: str = Field(example="How RAG process takes place?")    