"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

"""
fileName: mappers.py
description: A Pydantic model object for usecase entity model
             which maps the data model to the usecase entity schema
"""

import json
from fastapi import UploadFile
from pydantic import BaseModel, Field, model_validator, validator, root_validator
from datetime import datetime
from enum import Enum
from typing import Optional, Union, List, Dict
import pandas as pd
import os

from fastapi.responses import FileResponse

"""
description: Fairness
params: 
"""
class IndividualFairnessRequest(BaseModel):
    labels: List[str] = Field(example=["income-per-year"])
    recordId: str = Field(example="6014sla28j123h")

class ProtetedAttribute(BaseModel):
    name: str = Field("race")
    privileged: list = ["White"]
    unprivileged: list = ["Black"
        , "Amer-Indian-Eskimo"
        , "Asian-Pac-Islander"
        , "Other"]

    class Config:
        orm_mode = True


class TrainingDatasetPath(BaseModel):
    storage: str = Field(example="INFY_AICLD_NUTANIX")
    uri: str = Field(example="responsible-ai//responsible-ai-fairness//adult.csv")

    class Config:
        orm_mode = True

class PredictionDatasetPath(BaseModel):
    storage: str = Field(example="INFY_AICLD_NUTANIX")
    uri: str = Field(example="responsible-ai//responsible-ai-fairness//TestFairData.csv")

    class Config:
        orm_mode = True


class OutputPath(BaseModel):
    storage: str = Field(example="INFY_AICLD_NUTANIX")
    uri: str = Field(example="responsible-ai//responsible-ai-fairness//OUTPUT.json")

    class Config:
        orm_mode = True


class PreDataset(BaseModel):
    id: int = Field(example=32)
    name: str = Field(example="Adult")
    fileType: str = Field(example="text/csv")
    path: TrainingDatasetPath
    label: str = Field(example="income-per-year")

    class Config:
        orm_mode = True


class PostDataset(BaseModel):
    id: int = Field(example=32)
    name: str = Field(example="Adult")
    fileType: str = Field(example="text/csv")
    path: PredictionDatasetPath
    label: str = Field(example="income-per-year")
    predlabel: str = Field(example="labels_pred")

    class Config:
        orm_mode = True


class BiasAnalyzeRequest(BaseModel):
    method: str = Field(example="STATISTICAL-PARITY-DIFFERENCE")
    biasType: str = Field(example="PRETRAIN")
    taskType: str = Field(example="CLASSIFICATION")

    trainingDataset: PreDataset
    predictionDataset: PostDataset

    features: str = Field(
        example="age,workclass,hours-per-week,education,native-country,race,sex,income-per-year")  # age,education-num,capital-gain,capital-loss,hours-per-week,sex
    categoricalAttributes: str = Field(example="education,native-country,workclass,sex")

    favourableOutcome: List = Field(example=['>50K'])
    labelmaps: dict = {">50K": 1, "<=50K": 0}
    facet: List[ProtetedAttribute]
    outputPath: OutputPath


    class Config:
        orm_mode = True

class metricsEntity(BaseModel):
    name: str = Field(example="STATISTICAL-PARITY-DIFFERENCE")
    description: str = Field(
        example="Computed as the difference of the rate of favorable outcomes received by the unprivileged group to the privileged group.The ideal value of this metric is 0. Fairness for this metric is between -0.1 and 0.1")
    value: str = Field(example=0.25)

    class Config:
        orm_mode = True


class BiasResults(BaseModel):
    biasDetected: bool = Field(example=True)
    protectedAttribute: List[ProtetedAttribute]
    metrics: List[metricsEntity]

    class Config:
        orm_mode = True


class BiasAnalyzeResponse(BaseModel):
    biasResults: List[BiasResults]

    class Config:
        orm_mode = True

class BiasAnalyzeMetrics(BaseModel):
    biasResults: List[BiasResults]
    individualMetrics: Optional[List] = None

    class Config:
        orm_mode = True

class BiasAnalyzeIndividualMetric(BaseModel):
    individualMetrics: Optional[List]

    class Config:
        orm_mode = True
        
class BiasPretrainMitigationResponse(BaseModel):
    biasResults: List[BiasResults]
    fileName:str
    class Config:
        orm_mode = True
        
class BiasPretrainMitigationResponseUseCase(BaseModel):
    biasResults: List[BiasResults]
    fileName:List[str]
    class Config:
        orm_mode = True


class MitigationType(str, Enum):
    PreProcessing = 'PREPROCESSING'
    InProcessing = 'INPROCESSING'
    PostProcessing = 'POSTPROCESSING'


class MitigationTechnique(str, Enum):
    REWEIGHING = 'REWEIGHING'
    DISPARATE_IMPACT_REMOVER = 'DISPARATE IMPACT REMOVER'
    CORRELATION_REMOVER = 'CORRELATION REMOVER'
    LEARNING_FAIR_REPRESENTATION = 'LEARNING FAIR REPRESENTATION'
    ML_DEBIASER = 'ML DEBIASER'
    REJECT_OPTION_CLASSIFICATION = 'REJECT OPTION CLASSIFICATION'
    LP_DEBIASER = 'LP DEBIASER'
    EQUALIZED_ODDS = 'EQUALIZED ODDS'
    CALIBRATED_EQUALIZED_ODDS = 'CALIBRATED EQUALIZED ODDS'


class MitigateBiasRequest(BaseModel):
    biasType: str = Field(example="PRETRAIN")
    mitigationType: MitigationType = Field(example="PREPROCESSING")
    mitigationTechnique: MitigationTechnique = Field(example="REWEIGHING")
    method: str = Field(example="ALL")
    taskType: str = Field(example="CLASSIFICATION")
    trainingDataset: PreDataset
    predictionDataset: PostDataset
    features: str = Field(
        example="age,workclass,hours-per-week,education,native-country,race,sex,income-per-year")  # age,education-num,capital-gain,capital-loss,hours-per-week,sex
    categoricalAttributes: str = Field(example="education,native-country,workclass,sex")

    favourableOutcome: List = Field(example=['>50K'])
    labelmaps: dict = {">50K": 1, "<=50K": 0}
    facet: List[ProtetedAttribute]
    outputPath: OutputPath

    class Config:
        orm_mode = True


class PreprocessingMitigateBiasRequest(BaseModel):
    method: str = Field(example="ALL")
    biasType: str = Field(example="PRETRAIN")
    taskType: str = Field(example="CLASSIFICATION")
    mitigationType: MitigationType = Field(example="PREPROCESSING")
    mitigationTechnique: MitigationTechnique = Field(example="REWEIGHING")
    trainingDataset: PreDataset
    features: str = Field(
        example="age,workclass,hours-per-week,education,native-country,race,sex,income-per-year")  # age,education-num,capital-gain,capital-loss,hours-per-week,sex
    categoricalAttributes: str = Field(example="education,native-country,workclass,sex")

    favourableOutcome: List = Field(example=['>50K'])
    labelmaps: dict = {">50K": 1, "<=50K": 0}
    facet: List[ProtetedAttribute]
    outputPath: OutputPath

    class Config:
        orm_mode = True


class MitigationResults(BaseModel):
    biasType: str = Field(example="PRETRAIN")
    mitigationType: MitigationType = Field(example="PREPROCESSING")
    mitigationTechnique: MitigationTechnique = Field(example="REWEIGHING")
    metricsBeforeMitigation: List[metricsEntity]
    biasDetectedOriginally: bool = Field(example=True)
    metricsAfterMitigation: List[metricsEntity]
    biasDetectedAfterMitigation: bool = Field(example=False)
    mitigatedFileName:str

    class Config:
        orm_mode = True

class PreprocessingMitigationResults(BaseModel):
    biasType: str = Field(example="PRETRAIN")
    mitigationType: MitigationType = Field(example="PREPROCESSING")
    mitigationTechnique: MitigationTechnique = Field(example="REWEIGHING")
    mitigatedFileName:str

    class Config:
        orm_mode = True


class MitigationAnalyzeResponse(BaseModel):
    mitigationResults: List[MitigationResults]

    class Config:
        orm_mode = True

class PreprocessingMitigationAnalyzeResponse(BaseModel):
    mitigationResults: List[PreprocessingMitigationResults]

    class Config:
        orm_mode = True


class GetBiasRequest(BaseModel):
    mlModelId: int = Field(example=23)

    class Config:
        orm_mode = True


class GetBiasResponse(BaseModel):
    biasResults: List[BiasResults]

    class Config:
        orm_mode = True

class GetMitigationRequest(BaseModel):
    fileName: str = Field(example="Mitigated_Adult_1231213213.csv")

    class Config:
        orm_mode = True

class BatchId(BaseModel):
    Batch_id: float = Field(example=123.12)

    class Config:
        orm_mode = True
        
        
class FairnessAnalysisRequest(BaseModel):
    biasType: str = Field(example="PRETRAIN")
    taskType: str = Field(example="CLASSIFICATION")
    methodType: str = Field(example="ALL")
    label: str = Field(example="income-per-year")
    predLabel: str = Field(example="labels_pred")
    favourableOutcome: str = Field(example=">50K")
    protectedAttribute: List[str]=["race","sex"]
    priviledgedGroups: List[List[str]]=[["White","Black"],["Male"]]
   
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    class Config:
        orm_mode = True
        
        
class MitigationRequest(BaseModel):
    mitigationType: str = Field(example="PREPROCESSING")
    mitigationTechnique: str = Field(example="REWEIGHING")
    taskType: str = Field(example="ALL")
    label: str = Field(example="income-per-year")
    favourableOutcome: str = Field(example=">50K")
    protectedAttribute: List[str]=["race","sex"]
    priviledgedGroups: List[List[str]]=[["White","Black"],["Male"]]
   
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    class Config:
        orm_mode = True
        
        
class IndividualRequest(BaseModel):
    label: list[str] = Field(example=["income-per-year"])
    k: int = Field(example=5)
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    class Config:
        orm_mode = True
    
class AnalysisRequest(BaseModel):
    label: str = Field(example="labels_pred")
    favourableOutcome: Union[str,int] = Field(example=1)
    categorical_attrbutes: List[str] = Field(example=["race","sex"])
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    class Config:
        orm_mode = True
        
class GetDataRequest(BaseModel):
    # ModelFile: Union[UploadFile, None] = None
    file: Union[UploadFile] = None
    
    
class AuditRequest(BaseModel):
    label: str = Field(example="labels_pred")
    favourableOutcome: Union[str,int] = Field(example=1)
    categorical_attrbutes: List[str] = Field(example=["race","sex"])
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    class Config:
        orm_mode = True
    
class MonitoringRequest(BaseModel):
    label: str = Field(example="Prompt")
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    class Config:
        orm_mode = True


