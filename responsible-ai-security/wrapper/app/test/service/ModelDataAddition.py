'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from pydantic import BaseModel,Field
from src.dao.SaveFileDB import FileStoreDb
from src.dao.ModelDb import Model
from src.dao.ModelAttributesDb import ModelAttributes
from src.dao.ModelAttributesValuesDb import ModelAttributesValues
from src.dao.DataDb import Data
from src.dao.DataAttributesDb import DataAttributes
from src.dao.DataAttributesValuesDb import DataAttributesValues
from src.dao.Tenet import Tenet
from src.dao.Batch import Batch
from src.dao.Html import Html
from datetime import datetime
from typing import Union,List, Optional
from fastapi import UploadFile
import os
import joblib
from io import BytesIO
from src.dao.DatabaseConnection import DB
import json
try:
    import keras
except ImportError:
    import unittest.mock as mock
    keras = mock.Mock()
from src.service.service import Infosys
class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class GetModelPayloadRequest(BaseModel):
    modelName : str = "Cartoonclassification_Model"
    targetDataType : Optional[str] = Field(example="Tabular or Image or Text")
    taskType: str = "classification or regression or timeseries forecast"
    targetClassifier : Optional[str] = Field(example="SklearnClassifier")
    useModelApi : str = "Yes/No"
    modelEndPoint : Optional[str] = Field(example="Na")
    data: Optional[str] = Field(example="data")
    prediction : Optional[str] = Field(example="prediction")

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

class GetModelRequest(BaseModel):
    ModelFile: Optional[UploadFile] = None

class GetDataPayloadRequest(BaseModel):
    dataFileName : str = "Cartoonclassification"
    dataType : str = "Tabular or Image or Text"
    groundTruthClassNames : list = [0,1]
    groundTruthClassLabel : Union[list, str] = "target" #str = "target" 
    

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    

class GetDataRequest(BaseModel):
    DataFile: Union[UploadFile] = None  

class GetBatchPayloadRequest(BaseModel):
    userId:Optional[str] = Field(default=None, description="admin")
    title:Optional[str] = Field(default=None, description="Preprocessor1")
    modelId:Optional[float] = Field(default=None, description="1.1")
    dataId:Optional[float] = Field(default=None, description="2.1")
    tenetName: Optional[List[str]] = None
    appAttacks: Optional[List[str]] = None
    appExplanationMethods: Optional[List[str]] = None
    biasType: Optional[str] = None
    methodType: Optional[str] = None
    taskType: Optional[str] = None
    label: Optional[str] = None
    favorableOutcome: Optional[str] = None
    protectedAttribute: Optional[str] = None
    privilegedGroup: Optional[str] = None
    preProcessorId: Optional[float] = None

class TenetDataRequest(BaseModel):
    tenetName : str = "RAI"
    tenetId : float = "0.0"

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

class AddModelData:

    mydb=DB.connect()

    def addData(userId,Payload1:GetDataPayloadRequest,Payload2:GetDataRequest):
        try:
            Payload1 = AttributeDict(Payload1)
            keys = Payload1.keys()
            data_extension = os.path.splitext(Payload2.DataFile.filename)
            data_file = FileStoreDb.fs.find_one({'filename':Payload1.dataFileName+data_extension[1]})
            data_extensionModified = Payload2.DataFile.filename
            Payload1["fileName"] = data_extensionModified
            if data_file:
                try:
                    existing_data = Data.findall({"DataSetName":Payload1.dataFileName})
                    if not existing_data:
                        FileStoreDb.fs.delete(data_file._id)
                        data_file = None
                except Exception as e:
                    print(f"Error checking existing data: {e}")

            if data_file:
                return "DataFile Already Added"
            else:
                print('d1')
                commonTenetId = Tenet.findOne("Common")
                dataFileId = FileStoreDb.create(Payload2.DataFile,Payload1.dataFileName+data_extension[1])
                print('dataFileId',dataFileId)
                dataId = Data.create({"dataSetName":Payload1.dataFileName,"sampleData":dataFileId,"userId":userId,"groundTruthImageFileId":"NA"})
                print('dataId',dataId)
                for key in keys:
                    if key == "dataFileName":
                        print('d2')
                        pass
                    else:
                        print('d3')
                        dataAttributesId = DataAttributes.findall({"DataAttributeName":key,"TenetId":commonTenetId})
                        if(len(dataAttributesId) > 1 or len(dataAttributesId) == 0):
                            print(f'd4: Failed for key={key}, count={len(dataAttributesId)}')
                            return f"No Entry or Multiple entries are present for {key} "
                        else:
                            print('d5')
                            dataAttributesId = dataAttributesId[0]["DataAttributeId"]
                        dataAttributesValuesId = DataAttributesValues.create({"dataAttributeId":dataAttributesId,"dataId":dataId,"dataAttributeValues":Payload1[key]})
                
                return "Data Added Sucessfully"
        
        except Exception as exc:
            print(f"EXCEPTION IN AddData: {exc}")
            return f"DataFile Addition Failed! Please Try Again{exc}"    


    def addModel(userId,Payload1:GetModelPayloadRequest,Payload2:GetModelRequest):

        try:
            Payload1 = AttributeDict(Payload1)
            keys = Payload1.keys()
            x = Model.findall({"UserId":userId,"ModelName":Payload1.modelName,"IsActive":'Y'})
            v = 0
            if(len(x) > 0 ):
                v  = x[-1].ModelVersion + 1
            model_Name,model_file = None,None
            if Payload1.useModelApi.lower() == "yes":
                model_Name = Model.findall({"UserId":userId,"ModelName":Payload1.modelName,"IsActive":'Y'})
                print(model_Name,"model_Name") 
            else:
                data_extension = os.path.splitext(Payload2.ModelFile.filename)
                data_extensionModified = Payload2.ModelFile.filename
                Payload1["fileName"] = data_extensionModified
                model_extension = os.path.splitext(Payload2.ModelFile.filename)
                model_file = FileStoreDb.fs.find_one({'filename':Payload1.modelName+model_extension[1]})
            
            
            # this will storing all metadata in ModelDb, ModelAttributesDb, ModelAttributesValuesDb
            if Payload1.useModelApi.lower() == "yes":
                if model_Name :
                    return 'Model Already Exist With the Same Name.'
                else:
                    modelId = Model.create({"userId":userId,"modelName":Payload1.modelName,"modelVersion":v,"modelData":0.0,"modelEndPoint":Payload1.modelEndPoint})
                    Payload1["modelFramework"] = "API"
            else:
                if model_file:
                    return 'Model Already Exist With the Same Name.'
                else:
                    modelFileId = FileStoreDb.create(Payload2.ModelFile,Payload1.modelName+model_extension[1])
                    modelId = Model.create({"userId":userId,"modelName":Payload1.modelName,"modelVersion":v,"modelData":modelFileId,"modelEndPoint":"NA"}) 
                    model_file = FileStoreDb.fs.get(modelFileId)
                    if Payload1["fileName"].split('.')[-1] == "pkl":
                        model = joblib.load(BytesIO(model_file.read()))
                        algorithm = type(model).__name__
                        modelFramework = "Scikit-learn"
                    elif Payload1["fileName"].split('.')[-1] == "zip":
                        algorithm = "LLM" # need to be updated later
                        modelFramework = "Transformers"
                    elif Payload1["fileName"].split('.')[-1] == "h5":
                        with open('model.h5', 'wb') as f:
                            f.write(model_file.read())
                        model = keras.models.load_model('model.h5')
                        os.remove('model.h5')
                        algorithm = type(model).__name__
                        modelFramework = "Keras"
                    
                    Payload1["modelFramework"] = modelFramework
                    Payload1["algorithm"] = algorithm
            commonTenetId = Tenet.findOne("Common")
            
            for key in keys:
                print(key,"keys")
                if key in ["modelName","modelEndPoint"]:
                    pass
                else:
                    modelAttributesId = ModelAttributes.findall({"ModelAttributeName":key,"TenetId":commonTenetId})
                    if(len(modelAttributesId) > 1 or len(modelAttributesId) == 0):
                        return f"No Entry or Multiple entries are present for {key} "
                    else:
                        modelAttributesId = modelAttributesId[0]["ModelAttributeId"]
                        print('modelAttributesId',modelAttributesId)
                    modelAttributesValuesId = ModelAttributesValues.create({"modelAttributeId":modelAttributesId,"modelId":modelId,"modelAttributeValues":Payload1[key]})
                    print('modelAttributesValuesId',modelAttributesValuesId)
            
            return "Model Added Sucessfully"
        except Exception as exc:
            return f"MODEL Addition Failed! Please Try Again{exc}"


    def getBatchList(payload:GetBatchPayloadRequest):
        try:
            payloadInDictionary = AttributeDict(payload)
            print("PAYLOAD IN DICT AFTER DELETE===",payloadInDictionary)
            batchedTenetIds = []
            for tenetName in payloadInDictionary.tenetName:
                tenantId = Tenet.findOne(tenetName)
                if(tenetName=="Security"):
                    securityTenetId = tenantId
                    data_attribute_names = ["appAttacks"]
                    batchedTenetId = Batch.create(payload,tenantId)
                    for name in data_attribute_names:
                        securityDataAttribute = ModelAttributes.findMAVId({"ModelAttributeName": name}, {"tenetId": securityTenetId})
                        if securityDataAttribute is not None and payloadInDictionary[name] is not None:
                            payloadInDictionary['ModelAttributeId'] = securityDataAttribute  
                            payloadInDictionary['ModelAttributevalues'] = payloadInDictionary[name]
                            payloadInDictionary['BatchId'] = batchedTenetId['BatchId']
                            securityDataAdd = ModelAttributesValues.createForBatchData(payloadInDictionary)
                            del payloadInDictionary['ModelAttributeId']
                            del payloadInDictionary['ModelAttributevalues']
                            del payloadInDictionary['BatchId']
                            print("DATA INSERTED IN MODEL ATTRIBUTE VALUES FOR SECURITY")
                    batchedTenetIds.append({"BatchId": batchedTenetId["BatchId"], "TenetId": tenantId})  # Add the new entry to the list
            return batchedTenetIds
        except Exception as exc:
            return f"Batch Creation Failed {exc}"   

    def addTenet(payload):
        try:
            Payload = AttributeDict(payload)
            if 'ProjectName' not in list(Payload.keys()):
                Payload["ProjectName"] = "RAI"
            Payload =  {k.lower(): v for k, v in Payload.items()}

            if len(Tenet.findall({'TenetName': Payload['tenetname']}))>=1:
                return f"{Payload['tenetname']} Tenet Already Exists."
            else:
                response = Tenet.create(Payload)
                return f"Successfully added {Payload['tenetname']} Tenet."
            
        except Exception as exc:
            return f"Tenet Addition Failed Due To {exc}"    

    def loadtenets():
        try:
            collist = AddModelData.mydb.list_collection_names()
            root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            tenant_jsonPath = root_path +'/service/tenet.json'
            f=open(tenant_jsonPath,'r')
            tenetList = json.loads(f.read())
            if 'Tenet' not in collist:
                print("TenetList---",tenetList)
                for tenet in tenetList:
                    tenet = AttributeDict(tenet)
                    X = AddModelData.addTenet(tenet)
            
            return "Success"
        except Exception as exc:
            return "Something Went Wrong"   

    def loadmodelattributes():
        try:
            collist = AddModelData.mydb.list_collection_names()
            root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            modelattributes_jsonPath = root_path +'/service/modelattributes.json'
            f=open(modelattributes_jsonPath,'r')
            modelAttributesList = json.loads(f.read())
            if 'ModelAttributes' not in collist:
                print("ModelAttributesList---",modelAttributesList)
                for modelAttributes in modelAttributesList:
                    modelAttributes = AttributeDict(modelAttributes)
                    id = ModelAttributes.create({"modelAttributeName":modelAttributes["ModelAttributeName"],"tenetId":modelAttributes["TenetId"]})
                    if id:
                        print(f"ModelAttributeName {modelAttributes.ModelAttributeName} got initalised Successfully")
            
            return "Success"
        except Exception as exc:
            return "Something Went Wrong"      

    def loaddataattributes():
        try:
            collist = AddModelData.mydb.list_collection_names()
            root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            datasetattributes_jsonPath = root_path +'/service/datasetattributes.json'
            f=open(datasetattributes_jsonPath,'r')
            dataAttributesList = json.loads(f.read())
            if 'DataAttributes' not in collist:
                print("datasetAttributesList---",dataAttributesList)
                for dataAttributes in dataAttributesList:
                    dataAttributes = AttributeDict(dataAttributes)
                    id = DataAttributes.create({"dataAttributeName":dataAttributes["DataAttributeName"],"tenetId":dataAttributes["TenetId"]})
                    print(id)
                    if id:
                        print(f"DataAttributeName {dataAttributes.DataAttributeName} got initalised Successfully")
            
            return "Success"
        except Exception as exc:
            return "Something Went Wrong"    


    def loadApi():
        # root_path = os.getcwd()
        # directories = root_path.split(os.path.sep)
        # src_index = directories.index("test")
        # new_path = os.path.sep.join(directories[:src_index])
        
        # Robust path finding
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        json_path = os.path.join(base_dir, 'src', 'config', 'attack.json')
        
        # json_path = new_path + '/app/config/attack.json'
        collist = AddModelData.mydb.list_collection_names()
        f=open(json_path,'r')
        attackList=json.loads(f.read())
        if 'Attack' not in collist:
            for attack in attackList:
                X = Infosys.addAttack(attack)
        return               

