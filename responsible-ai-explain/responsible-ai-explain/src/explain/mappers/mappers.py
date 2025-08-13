'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""
fileName: mappers.py
description: A Pydantic model object for usecase entity model
             which maps the data model to the usecase entity schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum

"""
description: Explainability
params:
"""

class DatasetType(str, Enum):
    csv = 'text/csv'
    parquet = 'text/parquet'

class TaskType(str, Enum):
    CLASSIFICATION  = 'CLASSIFICATION'
    REGRESSION = 'REGRESSION'
    TIMESERIESFORECAST = 'TIMESERIESFORECAST'

class Scope(str, Enum):
    GLOBAL = "GLOBAL"
    LOCAL = "LOCAL"

class Status(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

class GetExplanationMethodsRequest(BaseModel):
    modelId: float = Field(example=11.0)
    datasetId: float = Field(example=12.0)
    scope: Optional[Scope ]= Field(example="")
    
    class Config:
        from_attributes = True

class GetExplanationMethodsResponse(BaseModel):
    status: Status = Field(examples=['SUCCESS', 'FAILURE'])
    message: str = Field(example="Identification of explanation methods successful")
    dataType: Optional[str] = Field(example="Tabular")  
    methods: List = Field(example=[])
    
    class Config:
        from_attributes = True
        
class GetExplanationRequest(BaseModel):
    modelId: float = Field(example=11.01)
    datasetId: float = Field(example=12.02)
    preprocessorId: Optional[float] = Field(example=13.03)
    scope: str = Field(example="LOCAL")
    method: str = Field(example="ANCHOR-TABULAR")
    inputText: Optional[str] = Field(example="This movie was fantastic! The plot was gripping and the acting was top-notch.")
    inputRow: Optional[Dict] = Field(example={})
    
    class Config:
        from_attributes = True

class ExplainabilityTabular(BaseModel):
    modelPrediction: Optional[str] = Field(example="Class_GOOD")
    # modelConfidence: Optional[float] = Field(example= "0.85")
    anchorText: Optional[List] = Field(example=["awesome"])
    integratedText: Optional[List] = Field(example=["awesome"])
    anchor: Optional[List] = Field(example=["awesome"])
    importantFeatures : Optional[List] # [importantFeatures]
    limeTimeSeries : Optional[str]  = Field(example="base64 explain image")
    shapValues: Optional[List] = Field(example=[])
    inputRow: Optional[List] = Field(example=[{}])
    # inputText: Optional[str] = Field(example="")
    description: Optional[str] = Field(example="")
    modelDetails: Optional[Dict] = Field(example={})
    datasetDetails: Optional[Dict] = Field(example={})
    
    class Config:
        from_attributes = True
        
class ExplainabilityTabular_1(BaseModel):
    inputText: Optional[str] = Field(example="This movie was fantastic! The plot was gripping and the acting was top-notch.")
    inputRow: Optional[List] = Field(example=[])
    modelPrediction: Optional[str] = Field(example="Normal")
    # modelConfidence: Optional[str] = Field(example="0.85")
    explanation: Optional[List] = Field(example=[])
    timeSeries : Optional[str]  = Field(example="base64 explain image")
    
    class Config:
        from_attributes = True
        
class ExplainabilityTabular_New(BaseModel):
    modelName: str = Field(example="BMI Classification Model")
    algorithm: str = Field(example="Random Forest")
    endpoint: Optional[str] = Field(example="https://localhost:5000/bmi/predict")
    taskType: str = Field(example="CLASSIFICATION")
    datasetName: str = Field(example="BMI Dataset")
    dataType: str = Field(example="Tabular")
    groundTruthLabel: Optional[str] = Field(example="Index")
    groundTruthClassNames: Optional[List] = Field(example=["Underweight", "Normal", "Overweight", "Obese"])
    featureNames: Optional[List] = Field(example=["Age", "Weight", "Height"])
    methodName: str = Field(example="ANCHOR-TABULAR")
    methodDescription: str = Field(example="Anchor Explanation Description")
    anchor: Optional[List[ExplainabilityTabular_1]]
    attributionsText: Optional[List[ExplainabilityTabular_1]]
    shapImportanceText: Optional[List[ExplainabilityTabular_1]]
    featureImportance: Optional[List[ExplainabilityTabular_1]]
    timeSeriesForecast : Optional[List[ExplainabilityTabular_1]]
    shapValues: Optional[List[ExplainabilityTabular_1]]
    explanationDesc: Optional[Dict] = Field(example={})
    
    class Config:
        from_attributes = True

class GetExplanationResponse(BaseModel):
    status: Status = Field(examples=['SUCCESS', 'FAILURE'])
    message: str = Field(example="Identification of explanation methods successful")
    explanation: List[ExplainabilityTabular_New]
    
    class Config:
        from_attributes = True

class GetReportRequest(BaseModel):
    batchId: float = Field(example=123.0)
    
    class Config:
        from_attributes = True

class GetReportResponse(BaseModel):
    status: Status = Field(examples=['SUCCESS', 'FAILURE'])
    message: str = Field(example="Report generated successfully")
    
    class Config:
        from_attributes = True

        