"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from io import StringIO, BytesIO
import pytest
from fairness.dao.WorkBench.FileStoreDb import FileStoreReportDb
from gridfs import GridFS, GridOut
from mongomock import gridfs
from test.MockDB import Database_MockDB
import time
import json
from gridfs.errors import NoFile, FileExists
import pandas
from sklearn.datasets import load_iris, fetch_california_housing
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import pickle
from fastapi import UploadFile
from starlette.datastructures import Headers
import os
from io import BytesIO

@pytest.fixture(scope="session", autouse=True)
def llm_connection_credentails():

    llm_connection_credentails = '''[{
        "name": "openai",
        "value": "GPT_4",
        "details": {
            "api_type": "mocked_api_type",
            "api_base": "Mocked Api-base",
            "api_version": "2023-07-01-preview",
            "api_key": "mocked-api_key"
        },
  "active": true
}]'''
    return llm_connection_credentails

@pytest.fixture(scope="session", autouse=True)
def csv_data():

    csv_data={"race":["Black","White","Black","White","White"],
        "sex":["Male","Female","Male","Female","Male"],
        "age":[12,34,123,123,12],
        "education":["Bachelors","Bachelors","Bachelors","Bachelors","Bachelors"],
        "relationship":["Husband","Wife","Husband","Wife","Husband"],
        "occupation":["Machine-op-inspct","Protective-serv","Exec-managerial","Protective-serv","Protective-serv"],"income-per-year":["<=50K","<=50K","<=50K",">50K",">50K"]}
    return csv_data


@pytest.fixture(scope="session", autouse=True)
def csv_data_model():
    csv_data_model={"age":[37,48,21,38,56,63,46,26,28,42,46],
            "fnlwgt":[48779,40666,203076,166062,138593,331527,181363,141824,339897,147510,138107],
            "education-num":[13,7,9,9,12,9,12,10,2,13,14],
            "capital-gain":[0,0,0,0,0,0,0,0,0,0,0],
            "capital-loss":[0,0,0,0,0,0,0,0,0,0,0],
            "hours-per-week":[40,60,35,50,40,14,40,40,43,40,60],
            "workclass":[1,4,4,4,7,0,4,4,4,2,2],
            "education":[9,1,11,11,7,11,7,15,3,9,12],
            "marital-status":[2,2,4,0,0,2,2,0,2,5,2],
            "occupation":[10,6,6,1,10,0,4,4,7,10,4],
            "relationship":[0,0,3,1,1,0,0,1,0,4,0],
            "native-country":[39,39,39,39,39,39,39,39,26,39,39],
            "income-per-year":[0,0,0,0,0,0,1,0,0,0,1],
            "race":[4,4,4,4,4,4,4,4,4,4,4],
            "sex":[1,1,1,0,0,1,1,0,1,1,1],}
    return csv_data_model

# @pytest.fixture(scope="session", autouse=True)
# def model():
#     df={"age":[37,48,21,38,56,63,46,26,28,42,46],
#             "fnlwgt":[48779,40666,203076,166062,138593,331527,181363,141824,339897,147510,138107],
#             "education-num":[13,7,9,9,12,9,12,10,2,13,14],
#             "capital-gain":[0,0,0,0,0,0,0,0,0,0,0],
#             "capital-loss":[0,0,0,0,0,0,0,0,0,0,0],
#             "hours-per-week":[40,60,35,50,40,14,40,40,43,40,60],
#             "workclass":[1,4,4,4,7,0,4,4,4,2,2],
#             "education":[9,1,11,11,7,11,7,15,3,9,12],
#             "marital-status":[2,2,4,0,0,2,2,0,2,5,2],
#             "occupation":[10,6,6,1,10,0,4,4,7,10,4],
#             "relationship":[0,0,3,1,1,0,0,1,0,4,0],
#             "native-country":[39,39,39,39,39,39,39,39,26,39,39],
#             "race":[4,4,4,4,4,4,4,4,4,4,4],
#             "sex":[1,1,1,0,0,1,1,0,1,1,1],}
#     x_train=pandas.DataFrame(x_train)
#     df2 ={"income-per-year":[0,0,0,0,0,0,1,0,0,0,1]}
#     y_train=pandas.DataFrame(y_train)
#     model= RandomForestClassifier()
#     model.fit(x_train,y_train)
#     return model

@pytest.fixture(scope="session", autouse=True)
def batch_data():

    mydoc=[{
        "UserId": "admin",
        "Status": "In-progress",
        "CreatedDateTime": "sdhjk",
        "LastUpdatedDateTime": "jhjkgjk",
        "BatchId": 123.124,
        "DataId": 12.12,
        "ModelId": 543748789476.34674,
        "TenetId": 1
    },
    {
        "UserId": "admin",
        "Status": "In-progress",
        "CreatedDateTime": "sdhjk",
        "LastUpdatedDateTime": "jhjkgjk",
        "BatchId": 123.125,
        "DataId": 12.124,
        "ModelId":13.13 ,
        "TenetId": 1
    }
    ]
    return mydoc

def dataset_data(file_id, file_id_model):

    mydoc=[{
        "UserId": "admin",
        "DataSetName": "adult",
        "isActive": "Y",
        "SampleData":file_id ,
        "CreatedDateTime": "",
        "LastUpdatedDateTime": "",
        "DataId": 12.12
    },
    {
    "UserId": "admin",
    "DataSetName": "adult",
    "isActive": "Y",
    "SampleData":file_id_model ,
    "CreatedDateTime": "",
    "LastUpdatedDateTime": "",
    "DataId": 12.124
    }]
    return mydoc


def model_data(model_Id):
    mydoc = {
    "UserId": "Admin",
    "ModelId": 13.13,
    "ModelName": "Fairness_Model_Test",
    "ModelVersion": 0,
    "IsActive": "Y",
    "ModelData": model_Id,
    "ModelEndPoint": "NA",
    "CreatedDateTime": "",
    "LastUpdatedDateTime": ""
    }
    return mydoc


@pytest.fixture(scope="session", autouse=True)
def Tenet_data():
    log.info("tenet start")
    mydoc={
        "Id": 1,
        "TenetName": "Fairness"
    }
    log.info("tenet excuted")
    return mydoc


@pytest.fixture(scope="session", autouse=True)
def dataattributes_data():  

    mydoc = [
    {
        "DataAttributeId": 1,
        "DataAttributeName": "biasType",
        "isActive": "Y",
        "CreatedDateTime": "",
        "LastUpdatedDateTime": "",
        "TenetId": 0
    },
    {
        "DataAttributeId": 2,
        "DataAttributeName": "methodType",
        "isActive": "Y",
        "CreatedDateTime": "",
        "LastUpdatedDateTime": "",
        "TenetId": 0
    },
    {
        "DataAttributeId": 3,
        "DataAttributeName": "taskType",
        "isActive": "Y",
        "CreatedDateTime": "",
        "LastUpdatedDateTime": "",
        "TenetId": 0
    },
    {
        "DataAttributeId": 4,
        "DataAttributeName": "label",
        "isActive": "Y",
        "CreatedDateTime": "",
        "LastUpdatedDateTime": "",
        "TenetId": 0
    },
    {
        "DataAttributeId": 5,
        "DataAttributeName": "protectedAttribute",
        "isActive": "Y",
        "CreatedDateTime": "",
        "LastUpdatedDateTime": "",
        "TenetId": 0
    },
    {
        "DataAttributeId": 6,
        "DataAttributeName": "favorableOutcome",
        "isActive": "Y",
        "CreatedDateTime": "",
        "LastUpdatedDateTime": "",
        "TenetId": 0
    },
    {
        "DataAttributeId": 7,
        "DataAttributeName": "CategoricalAttributes",
        "isActive": "Y",
        "CreatedDateTime": "",
        "LastUpdatedDateTime": "",
        "TenetId": 0
    },
    {
        "DataAttributeId": 8,
        "DataAttributeName": "features",
        "isActive": "Y",
        "CreatedDateTime": "",
        "LastUpdatedDateTime": "",
        "TenetId": 0
    },
    {
        "DataAttributeId": 9,
        "DataAttributeName": "privilegedGroup",
        "isActive": "Y",
        "CreatedDateTime": "",
        "LastUpdatedDateTime": "",
        "TenetId": 0
    },
    {
        "DataAttributeId": 10,
        "DataAttributeName": "MitigationType",
        "isActive": "Y",
        "CreatedDateTime": "",
        "LastUpdatedDateTime": "",
        "TenetId": 0
    },
    {
        "DataAttributeId": 11,
        "DataAttributeName": "MitigationTechnique",
        "isActive": "Y",
        "CreatedDateTime": "",
        "LastUpdatedDateTime": "",
        "TenetId": 0
    }
    ]
            
    return mydoc

@pytest.fixture(scope="session", autouse=True)
def modelttributes_data():
    mydoc =[{
    "ModelAttributeId": 1,
    "ModelAttributeName": "label",
    "IsActive": "Y",
    "TenetId": 0,
    "CreatedDateTime": "",
    "LastUpdatedDateTime": ""
    },{
    "ModelAttributeId": 2,
    "ModelAttributeName": "sensitiveFeatures",
    "IsActive": "Y",
    "TenetId": 0,
    "CreatedDateTime": "",
    "LastUpdatedDateTime": ""
    }]
    return mydoc

@pytest.fixture(scope="session", autouse=True)
def dataattributesValues_data():
    mydoc = [{
    "DataAttributeValuesId": 1,
    "DataAttributeId": 1,
    "DataAttributeValues": "PRETRAIN",
    "IsActive": "Y",
    "CreatedDateTime": "",
    "LastUpdatedDateTime": "",
    "DataId": 12.12,
    "BatchId": 123.124
    },
    {
    "DataAttributeValuesId": 2,
    "DataAttributeId": 2,
    "DataAttributeValues": "ALL",
    "IsActive": "Y",
    "CreatedDateTime": "",
    "LastUpdatedDateTime": "",
    "DataId": 12.12,
    "BatchId": 123.124
    },
    {
    "DataAttributeValuesId": 4,
    "DataAttributeId": 4,
    "DataAttributeValues": "income-per-year",
    "IsActive": "Y",
    "CreatedDateTime": "",
    "LastUpdatedDateTime": "",
    "DataId": 12.12,
    "BatchId": 123.124
    },
    {
    "DataAttributeValuesId": 6,
    "DataAttributeId": 6,
    "DataAttributeValues": ">50K",
    "IsActive": "Y",
    "CreatedDateTime": "",
    "LastUpdatedDateTime": "",
    "DataId": 12.12,
    "BatchId": 123.124
    },
    {
    "DataAttributeValuesId": 8,
    "DataAttributeId": 8,
    "DataAttributeValues": [
        "age",
        "workclass",
        "hours-per-week",
        "education",
        "native-country",
        "race",
        "sex",
        "income-per-year"
    ],
    "IsActive": "Y",
    "CreatedDateTime": "",
    "LastUpdatedDateTime": "",
    "DataId": 12.12,
    "BatchId": 123.124
    },
    {
    "DataAttributeValuesId": 7,
    "DataAttributeId": 7,
    "DataAttributeValues": [
        "education",
        "native-country",
        "workclass",
        "sex"
    ],
    "CreatedDateTime": "",
    "LastUpdatedDateTime": "",
    "DatasetID": 12.12,
    "BatchId": 123.124
    },
    {
    "DataAttributeValuesId": 3,
    "DataAttributeId": 3,
    "DataAttributeValues": "CLASSIFICATION",
    "IsActive": "Y",
    "CreatedDateTime": "",
    "LastUpdatedDateTime": "",
    "DataId": 12.12,
    "BatchId": 123.124
    },
    {
    "DataAttributeValuesId": 9,
    "DataAttributeId": 9,
    "DataAttributeValues": "White",
    "IsActive": "Y",
    "CreatedDateTime": "",
    "LastUpdatedDateTime": "",
    "DataId": 12.12,
    "BatchId": 123.124
    },
    {
    "DataAttributeValuesId": 5,
    "DataAttributeId": 5,
    "DataAttributeValues": "race",
    "IsActive": "Y",
    "CreatedDateTime": "",
    "LastUpdatedDateTime": "",
    "DataId": 12.12,
    "BatchId": 123.124
    },
    {
    "DataAttributeValuesId": 10,
    "DataAttributeId": 10,
    "DataAttributeValues": "PREPROCESSING",
    "IsActive": "Y",
    "CreatedDateTime": "",
    "LastUpdatedDateTime": "",
    "DataId": 12.12,
    "BatchId": 123.124
    },
    {
    "DataAttributeValuesId": 11,
    "DataAttributeId": 11,
    "DataAttributeValues": "REWEIGHING",
    "IsActive": "Y",
    "CreatedDateTime": "",
    "LastUpdatedDateTime": "",
    "DataId": 12.12,
    "BatchId": 123.124
    }]
    return mydoc

@pytest.fixture(scope="session", autouse=True)
def modelattributesValues_data():
    mydoc = [{
    "ModelAttributeValuesId": 1,
    "ModelAttributeId": 1,
    "ModelId": 13.13,
    "ModelAttributeValues": "income-per-year",
    "IsActive": "Y",
    "CreatedDateTime": "",
    "LastUpdatedDateTime": "",
    "BatchId": 123.125
    },
    {
    "ModelAttributeValuesId": 2,
    "ModelAttributeId": 2,
    "ModelId": 13.13,
    "ModelAttributeValues": [
        "race"
    ],
    "IsActive": "Y",
    "CreatedDateTime": "",
    "LastUpdatedDateTime": "",
    "BatchId": 123.125
    }]
    return mydoc
        

def save_file(obj, file, filename, contentType, tenet):

    # Check if file_content is not None
    if file is None:
        raise ValueError("File content cannot be None")

    # Check if filename, contentType, and tenet are not None
    if filename is None or contentType is None or tenet is None:
        raise ValueError("Filename, contentType, and tenet cannot be None")

    localTime = time.time()
    time.sleep(1/1000)
    try:
        with obj.new_file(_id=str(localTime),
                          filename=filename,
                          contentType=contentType,
                          tenet=tenet,
                          ) as f:
            f.write(file)
    except FileExists:
        raise FileExistsError(
            f"A file with the same ID ({localTime}) already exists")
    except Exception as e:
        raise IOError(f"An error occurred while writing the file: {str(e)}")

    return f._id


@pytest.fixture(scope="session", autouse=True)
def setup_database(llm_connection_credentails,csv_data,csv_data_model,batch_data,Tenet_data,dataattributes_data, dataattributesValues_data, modelttributes_data, modelattributesValues_data):
    #create csv from DF and convert to binary in memeory
   
    df=pandas.DataFrame(csv_data)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_binary = csv_buffer.getvalue().encode()
    csv_buffer.close()
    df2=pandas.DataFrame(csv_data_model)
    csv_buffer_md = StringIO()
    df2.to_csv(csv_buffer_md, index=False)
    csv_binary_model = csv_buffer_md.getvalue().encode()
    csv_buffer_md.close()

    #store this binary into mockDB
    gridfs.enable_gridfs_integration()
    obj = Database_MockDB()
    fs = GridFS(obj.db)
    file_id = save_file(fs, csv_binary, "Consistency_1.csv", "csv", "fairness")
    file_id_model = save_file(fs, csv_binary_model, "modeldataset.csv", "csv", "fairness")
    dataset_data_=dataset_data(file_id,file_id_model)
    model_path = 'test/test_files/model.joblib'

    model_content=joblib.load(model_path)
    model_byte_stream = BytesIO()
    joblib.dump(model_content, model_byte_stream)
    model_byte_stream.seek(0)

    model_Id = save_file(fs, model_byte_stream, "model.joblib", "joblib", "fairness")
    model_data_ = model_data(model_Id)

    json_content=json.loads(llm_connection_credentails)
    #add llm credentials to db
    response = obj.db['llm_connection_credentails'].insert_many(json_content)

    #add batch_data to db
    mydata = obj.db['Batch']
    CreateData= mydata.insert_many(batch_data)
    dataset = obj.db['Dataset'].insert_many(dataset_data_)
    tenet =  obj.db['Tenet']
    create_tenet = tenet.insert_one(Tenet_data)
    dataattributes = obj.db['DataAttributes'].insert_many(dataattributes_data)
    dataattributesValues = obj.db['DataAttributesValues'].insert_many(dataattributesValues_data)
    model = obj.db['Model'].insert_one(model_data_)
    modelattributes = obj.db['ModelAttributes'].insert_many(modelttributes_data)
    modelattributesValues = obj.db['ModelAttributesValues'].insert_many(modelattributesValues_data)
    rec_id= CreateData.inserted_ids[0]
    rec_id_model= CreateData.inserted_ids[1]
    values = mydata.find_one({'_id': rec_id},{"BatchId": 1, "_id": 0})
    value = mydata.find_one({'_id': rec_id_model},{"BatchId": 1, "_id": 0})
    tenet_name = "Fairness"
    tenet_Id = tenet.find_one({"TenetName": tenet_name}) 
    log.info(f"{tenet_Id}tenet_Id")
    batch_id = values['BatchId']
    batch_id_model = value['BatchId']
    log.info(f"file{file_id}")
    log.info(f"{batch_id}batch_id")
    log.info(f"file{file_id_model}")
    yield [obj, file_id,batch_id,file_id_model,model_Id,batch_id_model]


# class AttributeDict(dict):
#     __getattr__ = dict.__getitem__
#     __setattr__ = dict.__setitem__
#     __delattr__ = dict.__delitem__

# class DummyCollection:
    # obj=Database_MockDB()
    # mydata = obj.db['SampleData']

#     def findOne(id):
#         values = DummyCollection.mydata.find_one({'_id': id},{})
#         values = AttributeDict(values)
#         return values
    
#     def create():
#         localTime = time.time()
#         time
#         mydoc={
#             "_id":"123",
#             "batch_id":"1234",
#             "addedData":"dummyData"
#         }
        

      