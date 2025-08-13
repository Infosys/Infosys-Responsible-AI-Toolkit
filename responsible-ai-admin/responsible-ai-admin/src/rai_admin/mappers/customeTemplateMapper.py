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

class subTemplate(BaseModel):
        subtemplate:str=Field(example="evaluation")
        templateData:str=Field(example="TemplateData1")
class CustomeTemplateReq(BaseModel):
        userId:str=Field(example="123")
        mode:str=Field(example="Master_Template/Private_Template")
        category:str=Field(example="SingleModel/MultiModel")
        # templateType:str=Field(example="request")
        templateName:str=Field(example="Template1")
        description:str=Field(example="Template1")
        # masterTemplateList:List[str]
        subTemplates:List[subTemplate]

class CustomeTemplate(BaseModel):
        templateId:float=Field(example="123")
        userId:str=Field(example="123")
        mode:str=Field(example="private")
        category:str=Field(example="SingleModel")
        uniqueId:str=Field(example="123")
        # templateType:str=Field(example="request")
        templateName:str=Field(example="Template1")
        description:str=Field(example="Template1")
        # masterTemplateList:List[dict]
        subTemplates:List[dict]

class GetTemplate(BaseModel):
        userId:str=Field(example="123")
        templateName:str=Field(example="Template1")
        class Config:
                orm_mode = True
# class AccSafetyParameter(BaseModel):
#     accMasterId:float=Field(example=1689056116.3704095)
#     drawings:float = Field(example="0.5")
#     hentai:float = Field(example="0.5")
#     neutral:float = Field(example="0.5")
#     porn:float = Field(example="0.5")
#     sexy:float = Field(example="0.5")

# class AccSafetyResponse(BaseModel):
#     safetyParameter: List[AccSafetyParameter]

#     class Config:
#         orm_mode = True
class CustomeTemplateStatus(BaseModel):
    status:str=Field(example="success")
    class Config:
        orm_mode = True


class CustomeTemplateRes(BaseModel):
    templates: List[CustomeTemplate]
    class Config:
        orm_mode = True



# class AccSafetyRequestUpdate(BaseModel):
#     accMasterId:float=Field(example=1689056116.3704095)
#     parameters : str=Field(example="drawings")
#     value : float=Field(example="0.5")

class AccTempMapReq(BaseModel):
        userId:str=Field(example="123")
        portfolio:str=Field(example="Infosys")
        account:str=Field(example="IMPACT")
        category:str
        subcategory:str
        requestTemplate:List[str]
        responseTemplate:List[str]
        comparisonTemplate:List[str]

class AccModMapsReq(BaseModel):
        userId:str=Field(example="123")
        portfolio:str=Field(example="Infosys")
        account:str=Field(example="IMPACT")

class ModMapReq(BaseModel):
        category:str=Field(example="SingleModel")
        portfolio:str=Field(example="Infosys")
        account:str=Field(example="IMPACT")
        
class ModConfigReq(BaseModel):
        category:str=Field(example="SingleModel")
        subcategory:str=Field(example="Template")
        portfolio:str=Field(example="Infosys")
        account:str=Field(example="IMPACT")
        
class AccTempMapv(BaseModel):
        mapId:float=Field(example="123"),
        # "userId":value.userId,
        accMasterId:float=Field(example="123"),
        # "requestTemplate":value.requestTemplate,  
        # "responseTemplate":value.responseTemplate,
       
        userId:str=Field(example="123")
        
        portfolio:str=Field(example="Infosys")
        account:str=Field(example="IMPACT")
        category:str=Field(example="SingleModel")
        subcategory:str=Field(example="Template")
        requestTemplate:List[str]
        responseTemplate:List[str]
        comparisonTemplate:List[str]
class AccTempMap(BaseModel):
        accList: List[AccTempMapv]
        class Config:
                orm_mode = True
        
        
class TempMapDelete(BaseModel):
        userId:str=Field(example="123")
        portfolio:str=Field(example="Infosys")
        account:str=Field(example="IMPACT")
     
class AddTempMap(BaseModel):
        # mapId:str=Field(example="123")
        userId:str=Field(example="123")
        portfolio:str=Field(example="Infosys")
        account:str=Field(example="IMPACT")
        category:str=Field(example="SingleModel")
        subcategory:str=Field(example="Template")
        requestTemplate:List[str]
        responseTemplate:List[str]
        comparisonTemplate:List[str]
        class Config:
                orm_mode = True
class RemoveTempMap(BaseModel):
        # mapId:str=Field(example="123")
        userId:str=Field(example="123")
        portfolio:str=Field(example="Infosys")
        account:str=Field(example="IMPACT")
        category:str=Field(example="SingleModel")
        subcategory:str=Field(example="Template")
        tempType:str=Field(example="request")
        templateName:str=Field(example="template1")
        class Config:
                orm_mode = True