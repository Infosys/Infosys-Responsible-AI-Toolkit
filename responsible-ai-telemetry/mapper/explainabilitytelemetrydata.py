'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Explanation(BaseModel):
    predictedTarget: str
    anchor: List[str]

class Response(BaseModel):
    explainerID: int
    explanation: List[Explanation]

class Request(BaseModel):
    portfolio_name: Optional[str]= Field(example="Infy")
    account_name: Optional[str]= Field(example="RAI")
    inputText: str
    explainerID: int

class TelemetryData(BaseModel):
    uniqueid: str
    tenant: str
    apiname: str
    user: Optional[str]= Field(example="admin")
    date: datetime
    lotNumber: Optional[str] = Field(example="P1")
    request: Request
    response: Response

class ResponseItem(BaseModel):
    InputPrompt: Optional[str] = None
    Response: Optional[str] = None
    Chain_of_Thought: Optional[str] = None
    Token_Cost: Optional[int] = None

    class Config:
        extra = "allow"  # Allows additional fields not explicitly defined in the model.

class ExplainBulkProcessTelemetryData(BaseModel):
    uniqueId: Optional[str] = None
    tenetName: Optional[str] = None
    apiName: Optional[str] = None
    userId: Optional[str] = None
    date: Optional[datetime] = None
    response: Optional[List[ResponseItem]] = None