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

class AICanvasResp(BaseModel):
    BusinessProblem:str = Field(example = "About Business Problem")
    BusinessValue:str = Field(example = "About Business Value")   
    EndUserValue:str = Field(example = "About End User Value")
    DataStrategy:str = Field(example = "About Data Strategy")
    ModellingApproach:str = Field(example = "About Modelling Approach")
    ModelTraining:str = Field(example = "About Model Training")
    ObjectiveFunction:str = Field(example = "About Objective Function")
    AICloudEngineeringServices:str = Field(example = "About AI Cloud and Engineering Services")
    ResponsibleAIApproach:str = Field(example = "About Responsible AI Approach")



class AICanvasRequest(BaseModel):
    UserId:str = Field(example = "UserId")
    UseCaseName:str = Field(example = "UseCaseName")
    AICanvasResponse : Union[AICanvasResp,None] = None

class AICanvas(BaseModel):
    AICanvasResponse : Union[AICanvasResp,None] = None

class AICanvasDataResponse(BaseModel):    
     dataResponseList: List[AICanvas]
     class Config:
        orm_mode = True
