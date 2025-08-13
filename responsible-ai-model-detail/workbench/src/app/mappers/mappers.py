'''
MIT license https://opensource.org/licenses/MIT Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from typing import Union,List, Optional
from pydantic import BaseModel,Field,model_validator
from fastapi import UploadFile
import json
from pydantic.class_validators import root_validator

class TenetDataRequest(BaseModel):
    tenetName : str = "RAI"
    tenetId : float = "0.0"

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    class Config:
        from_attributes = True

class GetModelPayloadRequest(BaseModel):
    modelName : str = "Cartoonclassification_Model"
    targetDataType : Optional[str] = Field(example="Tabular or Image or Text")
    # remove target -> targetDataType : str = "Tabular or Image or Text"
    taskType: str = "classification or regression or timeseries forecast"
    imageClassificationTypes: Optional[str] =Field(example="binary classification or multi classification")
    targetClassifier : Optional[str] = Field(example="SklearnClassifier")
    useModelApi : str = "Yes/No"
    modelEndPoint : Optional[str] = Field(example="Na")
    data: Optional[str] = Field(example="data")
    prediction : Optional[str] = Field(example="prediction")

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    class Config:
        from_attributes = True



    

class GetModelRequest(BaseModel):
    # ModelFile: Union[UploadFile, None] = None
    ModelFile: Optional[UploadFile] = None


class UpdateModelPayloadRequest(BaseModel):
    targetDataType : str = "Tabular or Image or Text"
    taskType: str = "classification or regression or timeseries forecast"
    targetClassifier : str = "SklearnClassifier"
    useModelApi : str = "Yes/No"
    modelEndPoint : Optional[str] = Field(example="Na")
    data: Optional[str] = Field(example="data")
    prediction : Optional[str] = Field(example="prediction")

    
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    class Config:
        from_attributes = True


class GetDataPayloadRequest(BaseModel):
    dataFileName : str = "Cartoonclassification"
    dataType : str = "Tabular or Image or Text"
    groundTruthClassNames : Optional[list] = Field(example=[0,1])
    groundTruthClassLabel : Optional[Union[str, list]] = Field(example="target") 
    

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    class Config:
        from_attributes = True
    

class GetDataRequest(BaseModel):
    DataFile: Union[UploadFile] = None

# class GetGroundtruthFileRequest(BaseModel):
#     GroundTruthFile: Optional[Union[UploadFile]] = None


class UpdateDataPayloadRequest(BaseModel):
    dataType : str = "Tabular or Image or Text"
    groundTruthClassNames : list = [0,1]
    groundTruthClassLabel: Optional[str] = Field(example="target")

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    class Config:
        from_attributes = True

## FOR BATCH GENERATION MAPPER

class GetBatchPayloadRequest(BaseModel):
    userId:Optional[str] = Field(example="admin")
    title:Optional[str] = Field(example="Preprocessor1")
    modelId:Optional[float] = Field(default=None, example=1.1)
    dataId:Optional[float] = Field(example="2.1")
    tenetName: Optional[List[str]]
    appAttacks: Optional[List[str]] = None
    appExplanationMethods: Optional[List[str]] = None
    biasType: Optional[str] = None
    methodType: Optional[str] = None
    taskType: Optional[str] = None
    label: Optional[str] = None
    favorableOutcome: Optional[str] = None
    protectedAttribute: Optional[List[str]] = None
    privilegedGroup: Optional[List[List[str]]] = None
    preProcessorId: Optional[float] = None
    mitigationType: Optional[str] = None
    mitigationTechnique : Optional[str] = None
    sensitiveFeatures: Optional[List[str]] = None
    predLabel : Optional[str] = None
    knn : Optional[int] = 5
    favourableLabel: Optional[str] = None
    
## FOR BATCH STATUS

class GetBatchStatusPayloadRequest(BaseModel):
    batchId:Optional[float] = Field(example="1.1")
    

## FOR Preprocessor
class GetPreprocessorPayloadRequest(BaseModel):
    userId:Optional[str] = Field(example="admin")
    preprocessorName:Optional[str] = Field(example="preprocessor")
    preprocessorFileId:Optional[float] = Field(example="4.1")

class GetPreprocessorRequest(BaseModel):
    PreprocessorFile: Union[UploadFile] = None

class UpdatePreprocessorPayloadRequest(BaseModel):
    preprocessorName:Optional[str] = Field(example="preprocessor")
