'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from pydantic import BaseModel
from datetime import date
from typing import List
from datetime import datetime
from pydantic import BaseModel, Field,Extra
from typing import Optional, Union, List

class ProfanityRequest(BaseModel):
    inputText: str

class profanity(BaseModel):
    profaneWord: str
    beginOffset: int
    endOffset: int 


class profanityScoreList(BaseModel):
    metricName: str 
    metricScore: float 


class ProfanityResponse(BaseModel):
    profanity: List[profanity]
    profanityScoreList: List[profanityScoreList]
    outputText: str


class TelemetryData(BaseModel):
    uniqueid: str
    tenant: str
    apiname: str
    date: datetime
    user: Optional[str]= Field(example="admin")
    lotNumber: Optional[str] = Field(example="1")
    request: ProfanityRequest
    response: ProfanityResponse

