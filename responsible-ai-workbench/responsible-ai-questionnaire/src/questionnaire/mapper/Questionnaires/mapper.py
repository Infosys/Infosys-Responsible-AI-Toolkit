'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Union, List




class SubmissionRequest(BaseModel):
    QuestionId:str = Field(example = "D1.1.1")
    UserId:str = Field(example = "UserId")
    UseCaseName:str = Field(example = "UseCaseName")
    QuestionOptionId:float=Field(example=2323.2323)
    ResponseDesc:str = Field(example = "Response Description.....")
    # Q_Weightage:float = Field(example=2.0)
    # RAI_Risk_Index:float = Field(example=2.0)
  


class Submission(BaseModel):
    QuestionId:str = Field(example = "D1.1.1")
    UserId:str = Field(example = "UserId")
    QuestionOptionId:float=Field(example=2323.2323)
    ResponseDesc:str = Field(example = "Response Description.....")
    # Q_Weightage:float = Field(example=2.0)
    # RAI_Risk_Index:float = Field(example=2.0)
    CreatedDateTime:datetime=Field(example='2023-06-07T10:56:15.657+00:00')
    LastUpdatedDateTime:datetime=Field(example='2023-06-07T10:56:15.657+00:00')



class SubmissionResponse(BaseModel):
    result:List[Submission]
    
    class Config:
        orm_mode = True


class UseCaseNameRequest(BaseModel):
    UserId:str = Field(example = "UserId")
    UseCaseName:str = Field(example = "UseCaseName")
    
    
class ImpactRequest(BaseModel):
    Dimension:str=Field(example="Dimension")
    Impact:str=Field(example="Impact")
    MinScore:float=Field(example=2.0)
    MaxScore:float=Field(example=2.0)




        


