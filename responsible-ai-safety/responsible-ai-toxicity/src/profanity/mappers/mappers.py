'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""
fileName: mappers.py
description: A Pydantic model object for usecase entity model
             which maps the data model to the usecase entity schema
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Union, List

"""
description: profinityEntity
params:
"""


class profanity(BaseModel):
    profaneWord: str = Field(example="dummy")
    beginOffset: int = Field(example=9)
    endOffset: int = Field(example=14)

    class Config:
        orm_mode = True

class profanityScoreList(BaseModel):
    metricName: str = Field(example="toxicity")
    metricScore: float = Field(example=0.78326)

    class Config:
        orm_mode = True

class ProfanityAnalyzeRequest(BaseModel):
    inputText: str = Field(example="You are a dummy")
    user: Optional[str] = Field(None)
    lotNumber: Optional[str] = Field(None)

class MaliciousURLAnalyzeRequest(BaseModel):
    inputText: str = Field(example="You are a dummy")
    maliciousThreshold : float = Field(example=0.5)
    user: Optional[str] = Field(None)
    lotNumber: Optional[str] = Field(None)


class ProfanityAnalyzeResponse(BaseModel):
    profanity: List[profanity]
    profanityScoreList: List[profanityScoreList]

    class Config:
        orm_mode = True


class ProfanitycensorRequest(BaseModel):
    inputText: str = Field(example="You are a dummy")
    user: Optional[str] = Field(None)
    lotNumber: Optional[str] = Field(None)

class ProfanitycensorResponse(BaseModel):
    outputText: str = Field(example="You are a ****")

    class Config:
        orm_mode = True
