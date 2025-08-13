"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Union, List,Tuple

class AccountSafetyRequest(BaseModel):
    portfolio:str=Field(example="INFOSYS")
    account:str=Field(example="IMPACT")
    drawings:float = Field(example="0.5")
    hentai:float = Field(example="0.5")
    neutral:float = Field(example="0.5")
    porn:float = Field(example="0.5")
    sexy:float = Field(example="0.5")
    

class AccSafetyParameter(BaseModel):
    accMasterId:float=Field(example=1689056116.3704095)
    drawings:float = Field(example="0.5")
    hentai:float = Field(example="0.5")
    neutral:float = Field(example="0.5")
    porn:float = Field(example="0.5")
    sexy:float = Field(example="0.5")

class AccSafetyParameterResponse(BaseModel):
    safetyParameter: List[AccSafetyParameter]

    class Config:
        orm_mode = True
class AccountSafetyResponse(BaseModel):
    status:str=Field(example="success")
    class Config:
        orm_mode = True



class AccSafetyRequestUpdate(BaseModel):
    accMasterId:float=Field(example=1689056116.3704095)
    parameters : str=Field(example="drawings")
    value : float=Field(example="0.5")

