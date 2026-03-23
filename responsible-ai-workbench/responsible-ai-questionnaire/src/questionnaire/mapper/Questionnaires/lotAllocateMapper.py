'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional,Union, List



class lotAssignRequest(BaseModel):
    tenant: str = Field(example="Privacy")
    user: str = Field(example = "admin") 

class lotAssignStatus(BaseModel):
    status:str=Field(example="success")
    class Config:
        orm_mode = True

class linkRequest(BaseModel):
    tenant: str = Field(example="Privacy")
    telemetryLink: str= Field(example="http://vimptblt1117:5601/app/dashboards#/view/c24f5380-69c0-11ee-a575-8b621e49e8c9?_g=(refreshInterval:(pause:!t,value:60000),time:(from:now-7d%2Fd,to:now))")


# class lotAssignResponse(BaseModel):
#     lotList: List[lotAssignResponseData]
#     class Config:
#         orm_mode = True
# class lotUserRequest(BaseModel):
#     user: str = Field(example = "admin") 