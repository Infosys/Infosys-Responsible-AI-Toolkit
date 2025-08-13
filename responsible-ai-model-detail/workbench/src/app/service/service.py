'''
MIT license https://opensource.org/licenses/MIT Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from ast import If
from io import BytesIO
import os
from urllib import response

from app.config.logger import CustomLogger
from app.mappers.mappers import GetBatchStatusPayloadRequest, GetModelRequest,GetModelPayloadRequest,UpdateModelPayloadRequest,GetDataRequest,GetDataPayloadRequest,UpdateDataPayloadRequest      

from app.dao.SaveFileDB import FileStoreDb
from app.dao.ModelDb import Model
from app.dao.ModelAttributesDb import ModelAttributes
from app.dao.ModelAttributesValuesDb import ModelAttributesValues
from app.dao.DataDb import Data
from app.dao.DataAttributesDb import DataAttributes
from app.dao.DataAttributesValuesDb import DataAttributesValues
from app.dao.Tenet import Tenet
from app.dao.DatabaseConnection import DB
from app.dao.Batch import Batch
from app.dao.Html import Html
from app.dao.Report import Report
from datetime import datetime
import multiprocessing
import requests
import keras
import joblib
import concurrent.futures
from app.dao.PreprocessorDb import Preprocessor
log = CustomLogger()
explainabilitygeneration = os.getenv("EXPLAINABILITYGENERATION")
fairnessgeneration = os.getenv("FAIRNESSGENERATION")
securitygeneration = os.getenv("SECURITYGENERATION")
sslVerify = os.getenv("sslVerify")
sslv={"False":False,"True":True,"None":True}

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

db_type = os.getenv('DB_TYPE').lower()
class InfosysRAI:

    # ------------------------------------------------------------------------------------

    def getTenetsList():
        try:
            response = Tenet.findall({"ProjectName" : "RAI"})
            tenent_details =[]
            if response:
                
                for tenent in response:
                    payload_data = {}
                    payload_data['Id'] = tenent['Id']
                    payload_data['TenetName'] = tenent['TenetName']
                    payload_data['ProjectName'] = tenent['ProjectName']
                    payload_data['CreatedDateTime'] = tenent['CreatedDateTime']
                    payload_data['LastUpdatedDateTime'] = tenent['LastUpdatedDateTime']
                    tenent_details.append(payload_data)
            return tenent_details
        except Exception as exc:
            return "Something Went Wrong" 
    

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


    def deletetenet(payload):
        try:
            Tenet.delete(payload)
            return f"Successfully Deleted {payload['TenetName']} Tenet Entries."
        except Exception as exc:
            return f"TENET deletion failed due to {exc}"

    # ------------------------------------------------------------------------------------

    def getData(payload):

        DataList = Data.findall({"UserId":payload['userid'],"IsActive":'Y'})

        DataAttributesList = DataAttributes.findall({"IsActive":'Y'})
        AttributesMapping = {}
        for Attribute in DataAttributesList:
                AttributesMapping[Attribute['DataAttributeId']] = Attribute['DataAttributeName']

        DataattributesList = []
        try:
            if DataList:
                for Datas in DataList:
                    payload_data = {}
                    payload_data['dataId'] = Datas['DataId']
                    payload_data['dataSetName'] = Datas['DataSetName']
                    payload_data['sampleData'] = Datas['SampleData']

                    attributeList = DataAttributesValues.findall({'DataId':Datas['DataId'],"IsActive":'Y'})
                    for d in attributeList:
                        if d['DataAttributeId'] in AttributesMapping:
                            attributeName = AttributesMapping[d['DataAttributeId']]
                            payload_data[attributeName] = d['DataAttributeValues']
                            
                    DataattributesList.append(payload_data)
                DataattributesList.reverse()

                return DataattributesList
            
            else:
                return "No Data Added Yet"
        except Exception as exc:
            return f"Model retrieval failed due to {exc}"
    
    
    
    def addData(userId,Payload1:GetDataPayloadRequest,Payload2:GetDataRequest):    #Payload3:GetGroundtruthFileRequest

        try:
            Payload1 = AttributeDict(Payload1)
            keys = Payload1.keys()
            # this will checking dataFile present in Database or not
            data_extension = os.path.splitext(Payload2.DataFile.filename)
            data_file = FileStoreDb.fs.find_one({'filename':Payload1.dataFileName+data_extension[1]})
            data_extensionModified = Payload2.DataFile.filename
            # this will storing all metadata in DataDb, DataAttributesDb, DataAttributesValuesDb
            Payload1["fileName"] = data_extensionModified
            if db_type == 'mongo':
                if data_file:
                    return "DataFile Already Added"
                else:
                    commonTenetId = Tenet.findOne("Common")
                    dataFileId = FileStoreDb.create(Payload2.DataFile,Payload1.dataFileName+data_extension[1])
                    # if Payload3.GroundTruthFile is not None:
                    #     groundTruthFile_Extension = os.path.splitext(Payload3.GroundTruthFile.filename)
                    #     groundTruthFileName = Payload1.dataFileName+'_groundtruthFile'+groundTruthFile_Extension[1]
                    #     groundTruthFileId = FileStoreDb.create(Payload3.GroundTruthFile,groundTruthFileName)
                    #     dataId = Data.create({"dataSetName":Payload1.dataFileName,"sampleData":dataFileId,"userId":userId,'groundTruthImageFileId':groundTruthFileId})
                    # else:
                    #     dataId = Data.create({"dataSetName":Payload1.dataFileName,"sampleData":dataFileId,"userId":userId,'groundTruthImageFileId':'NA'}) 
                    dataId = Data.create({"dataSetName":Payload1.dataFileName,"sampleData":dataFileId,"userId":userId,'groundTruthImageFileId':'NA'})       
                    # dataFileId = str(dataFileId)
                    for key in keys:
                        if key == "dataFileName":
                            pass
                        else:
                            dataAttributesId = DataAttributes.findall({"DataAttributeName":key,"TenetId":commonTenetId})
                            # dataAttributesId = DataAttributes.create({"dataAttributeName":key,"tenetId":commonTenetId})
                            if(len(dataAttributesId) > 1 or len(dataAttributesId) == 0):
                                return f"No Entry or Multiple entries are present for {key} "
                            else:
                                dataAttributesId = dataAttributesId[0]["DataAttributeId"]
                            dataAttributesValuesId = DataAttributesValues.create({"dataAttributeId":dataAttributesId,"dataId":dataId,"dataAttributeValues":Payload1[key]})
                    
                    return "Data Added Sucessfully"
            if db_type == 'cosmos':
                print(type(Payload2.DataFile),"DATA FILE TYPE")
                if data_file:
                    return "DataFile Already Added"
                else:
                    commonTenetId = Tenet.findOne("Common")
                    container_name = os.getenv('DATA_CONTAINER_NAME')
                    upload_file_api = os.getenv('AZURE_UPLOAD_API') 
                    Payload2.DataFile.file.seek(0)
                    response =requests.post(url =upload_file_api, files ={"file":(Payload2.DataFile.filename,Payload2.DataFile.file)}, data ={"container_name":container_name}, verify = sslv[sslVerify]).json()
                    # dataFileId = FileStoreDb.create(Payload2.DataFile,Payload1.dataFileName+data_extension[1])
                    blob_name =response["blob_name"]
                    print(blob_name,"blob_name")
                    # if Payload3.GroundTruthFile is not None:
                    #     Payload3.GroundTruthFile.file.seek(0)
                    #     groundTruthFile_Extension = os.path.splitext(Payload3.GroundTruthFile.filename)
                    #     groundTruthFileName = Payload1.dataFileName+'_groundtruthFile'+groundTruthFile_Extension[1]
                    #     response =requests.post(url =upload_file_api, files ={"file":(groundTruthFileName,Payload3.GroundTruthFile.file)}, data ={"container_name":container_name}, verify = sslv[sslVerify]).json()
                    #     groundTruthFileId_blob_name =response["blob_name"]
                    #     dataId = Data.create({"dataSetName":Payload1.dataFileName,"sampleData":blob_name,"userId":userId,'groundTruthImageFileId':groundTruthFileId_blob_name})
                    # else:
                    #     dataId = Data.create({"dataSetName":Payload1.dataFileName,"sampleData":blob_name,"userId":userId,'groundTruthImageFileId':'NA'}) 
                    dataId = Data.create({"dataSetName":Payload1.dataFileName,"sampleData":blob_name,"userId":userId,'groundTruthImageFileId':'NA'}) 
                    for key in keys:
                        if key == "dataFileName":
                            pass
                        else:
                            dataAttributesId = DataAttributes.findall({"DataAttributeName":key,"TenetId":commonTenetId})
                            # dataAttributesId = DataAttributes.create({"dataAttributeName":key,"tenetId":commonTenetId})
                            if(len(dataAttributesId) > 1 or len(dataAttributesId) == 0):
                                return f"No Entry or Multiple entries are present for {key} "
                            else:
                                dataAttributesId = dataAttributesId[0]["DataAttributeId"]
                            dataAttributesValuesId = DataAttributesValues.create({"dataAttributeId":dataAttributesId,"dataId":dataId,"dataAttributeValues":Payload1[key]})
                    
                    return "Data Added Sucessfully"
                # return "Data Added Sucessfully"
        
        except Exception as exc:
            return f"DataFile Addition Failed! Please Try Again{exc}"
    
    

    def updateData(payload,Payload1:UpdateDataPayloadRequest,Payload2:GetDataRequest):
        print(payload,"payload")
        dataList = Data.findall({"UserId":payload['userid'],'DataId':payload['dataid']})
        print(dataList,"dataList")
        if(len(dataList)):
            dataList = dataList[0]
        else:
            return "No Data Exists With This Id."
        
        try:
            if dataList:
                Payload1 = AttributeDict(Payload1)
                keys = Payload1.keys()

                # Reading metadata of DataDb Table and Updating new metadata values
                attributesData = {}
                attributeValues = DataAttributesValues.findall({"DataId":payload['dataid']})
                print(attributeValues,"attributeValues")
                for value in attributeValues:
                    attributes = DataAttributes.findall({"DataAttributeId":value.DataAttributeId})
                    if attributes:
                        attributesData[attributes[0]['DataAttributeName']] = value.DataAttributeValues
                    # attributes = DataAttributes.findall({"DataAttributeId":value.DataAttributeId})
                    #print( attributes,"attributes")
                    #print(attributesData,"attributesData")
                    
                    # attributesData[attributes['DataAttributeName']] = value.DataAttributeValues
                
                Payload1['fileName'] = Payload2.DataFile.filename
                print(Payload1.keys(),"Payload1.keys()")
                # Update DataAttributesValuesDb and DataAttributesValuesDb
                for key in keys:
                    if attributesData[key] == Payload1[key]:
                        continue
                    else:
                        #print( attributeValues,"attributes")
                        attributeValues = DataAttributesValues.findall({"DataId":payload['dataid']})
                        #print( attributeValues,"AFTERattributes")
                        for value in attributeValues:
                            dataAttributeList = DataAttributes.findall({"DataAttributeId":value.DataAttributeId})[0]
                            if key == dataAttributeList['DataAttributeName']:
                                DataAttributesValues.update(value.DataAttributeValuesId, {'DataAttributeValues':Payload1[key]})

                # this will checking dataFile present in Database or not and Update SaveFileDB
                if db_type == 'mongo':
                    if Payload2.DataFile:
                        data_file_id = FileStoreDb.fs.find_one({'_id':dataList['SampleData']})
                        FileStoreDb.delete(dataList['SampleData'])
                        # FileStoreDb.delete(data_file_id)
                        data_extension = os.path.splitext(Payload2.DataFile.filename)
                        dataFileId = FileStoreDb.create(Payload2.DataFile,Payload2.DataFile.filename)
                        Data.update(dataList['_id'], {'SampleData':dataFileId})
                        print(dataFileId,"dataFileId")
                        print(Payload2.DataFile.filename,"filename")
                        
                if db_type == 'cosmos':
                    if Payload2.DataFile:
                        data_file_blob_name = dataList['SampleData']
                        container_name = os.getenv('DATA_CONTAINER_NAME')
                        upload_file_api = os.getenv('AZURE_UPLOAD_API')
                        Payload2.DataFile.file.seek(0)
                        responseUpdate =requests.post(url =upload_file_api, files ={"file":(Payload2.DataFile.filename,Payload2.DataFile.file)}, data ={"container_name":container_name}, verify = sslv[sslVerify]).json()
                        print(responseUpdate,"responseUpdate")
                        blob_name = responseUpdate["blob_name"]
                        print(blob_name,"blob_name UPDATED")
                        Data.update(dataList['_id'], {'SampleData':blob_name})
                return 'Data Updated Successfully.'
            
        except Exception as exc:
            return f"DataFile Updating Failed! Please Try Again{exc}"


    
    def deleteData(payload):
        Payload = AttributeDict(payload)
        dataList = Data.findall({"UserId":payload['userid'], 'DataId':payload['dataid'],'IsActive':'Y'})
        Data_AttributesValues = DataAttributesValues.findall({"DataId":Payload.dataid,'IsActive':'Y'})

        try:
            if len(dataList):
                for Datas in Data_AttributesValues:
                    DataAttributesValues.update(Datas['_id'], {'IsActive':'N'})

                    DataAttributes_list = DataAttributes.findall({"DataAttributeId":Datas["DataAttributeId"]})
                    for DataAttribute in DataAttributes_list:
                        DataAttributes.update(DataAttribute['_id'], {'IsActive':'N'})

                for Datas in dataList:
                    Data.update(Datas['_id'], {'IsActive':'N'})
                    
                return "Data Deleted Sucessfully"
            else:
                return 'No Data Available to Delete'
        except Exception as exc:
            return f"DataFile deletion Failed! Please Try Again{exc}"

    # ------------------------------------------------------------------------------------

    def getModel(payload):

        ModelList = Model.findall({"UserId":payload['userid'],"IsActive":'Y'})

        ModelAttributesList = ModelAttributes.findall({"IsActive":'Y'})
        AttributesMapping = {}
        for Attribute in ModelAttributesList:
                AttributesMapping[Attribute['ModelAttributeId']] = Attribute['ModelAttributeName']

        ModelattributesList = []
        try:
            if ModelList:
                for Models in ModelList:
                    print(Models)
                    payload_data = {}
                    payload_data['modelId'] = Models['ModelId']
                    payload_data['modelName'] = Models['ModelName']
                    payload_data['modelEndPoint'] = Models['ModelEndPoint']
                    payload_data['modelFileId'] = Models['ModelData']
                    attributeList = ModelAttributesValues.findall({'ModelId':Models['ModelId']})
                    for d in attributeList:
                        if d['ModelAttributeId'] in AttributesMapping:
                            attributeName = AttributesMapping[d['ModelAttributeId']]
                            payload_data[attributeName] = d['ModelAttributeValues']
                    ModelattributesList.append(payload_data)
                ModelattributesList.reverse()

                return ModelattributesList
            
            else:
                return "No Model Added Yet"
        except Exception as exc:
            return f"Model loading Failed! Please Try Again{exc}"



    def addModel(userId,Payload1:GetModelPayloadRequest,Payload2:GetModelRequest):

        try:
            if db_type == 'mongo':
                Payload1 = AttributeDict(Payload1)
                keys = Payload1.keys()
                x = Model.findall({"UserId":userId,"ModelName":Payload1.modelName,"IsActive":'Y'})
                v = 0
                if(len(x) > 0 ):
                    v  = x[-1].ModelVersion + 1
                # data_extension = os.path.splitext(Payload2.ModelFile.filename)
                # data_extensionModified = Payload2.ModelFile.filename
                # print("data_extensionModified===>",data_extensionModified)
                # Payload1["fileName"] = data_extensionModified
                # this will checking modelFile present in Database or not
                model_Name,model_file = None,None
                if Payload1.useModelApi.lower() == "yes":
                    model_Name = Model.findall({"UserId":userId,"ModelName":Payload1.modelName,"IsActive":'Y'})
                    print(model_Name,"model_Name") 
                else:
                    data_extension = os.path.splitext(Payload2.ModelFile.filename)
                    data_extensionModified = Payload2.ModelFile.filename
                    print("data_extensionModified===>",data_extensionModified)
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
                        # modelId = str(modelFileId)
                        model_file = FileStoreDb.fs.get(modelFileId)
                        if Payload1["fileName"].split('.')[-1] == "pkl":
                            model = joblib.load(BytesIO(model_file.read()))
                            algorithm = type(model).__name__
                            if algorithm =='Pipeline':
                                algorithm = str(model.steps[-1][1])
                            modelFramework = "Scikit-learn"
                            if 'arima' in algorithm.lower():
                                modelFramework = "Statsmodels"
                        elif Payload1["fileName"].split('.')[-1] == "zip":
                            algorithm = "LLM" # need to be updated later
                            modelFramework = "Transformers"
                        elif Payload1["fileName"].split('.')[-1] == "h5":
                            # Write the data to a file
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
                        modelAttributesValuesId = ModelAttributesValues.create({"modelAttributeId":modelAttributesId,"modelId":modelId,"modelAttributeValues":Payload1[key]})
                
                return "Model Added Sucessfully"
            if db_type == 'cosmos':
                Payload1 = AttributeDict(Payload1)
                keys = Payload1.keys()
                x = Model.findall({"UserId":userId,"ModelName":Payload1.modelName,"IsActive":'Y'})
                v = 0
                if(len(x) > 0 ):
                    v  = x[-1].ModelVersion + 1
                # data_extension = os.path.splitext(Payload2.ModelFile.filename)
                # data_extensionModified = Payload2.ModelFile.filename
                # print("data_extensionModified===>",data_extensionModified)
                # Payload1["fileName"] = data_extensionModified
                # this will checking modelFile present in Database or not
                model_Name,model_file = None,None
                if Payload1.useModelApi.lower() == "yes":
                    model_Name = Model.findall({"UserId":userId,"ModelName":Payload1.modelName,"IsActive":'Y'})
                    print(model_Name,"model_Name") 
                else:
                    data_extension = os.path.splitext(Payload2.ModelFile.filename)
                    data_extensionModified = Payload2.ModelFile.filename
                    print("data_extensionModified===>",data_extensionModified)
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
                        commonTenetId = Tenet.findOne("Common")
                        container_name = os.getenv('MODEL_CONTAINER_NAME')
                        upload_file_api = os.getenv('AZURE_UPLOAD_API')
                        get_file_api = os.getenv('AZURE_GET_API')
                        Payload2.ModelFile.file.seek(0)
                        response =requests.post(url =upload_file_api, files ={"file":(Payload2.ModelFile.filename,Payload2.ModelFile.file)}, data ={"container_name":container_name},verify = sslv[sslVerify]).json()
                        blob_name =response["blob_name"]
                        modelId = Model.create({"userId":userId,"modelName":Payload1.modelName,"modelVersion":v,"modelData":blob_name,"modelEndPoint":"NA"}) 
                        # responseGet = requests.get(url=get_file_api, data={"container_name": container_name, "blob_name": blob_name})
                        responseGet = requests.get(
                            url=get_file_api, 
                            params={"container_name": container_name, "blob_name": blob_name}, verify = sslv[sslVerify]
                        )
                        print(type(responseGet.content),"MODEL BLOB TYPE")
                        # dataFileId = FileStoreDb
                        if Payload1["fileName"].split('.')[-1] == "pkl":
                            modelFileObj = responseGet.content
                            model = joblib.load(BytesIO(modelFileObj))
                            algorithm = type(model).__name__
                            if algorithm =='Pipeline':
                                algorithm = str(model.steps[-1][1])
                            modelFramework = "Scikit-learn"
                            if 'arima' in algorithm.lower():
                                modelFramework = "Statsmodels"
                        elif Payload1["fileName"].split('.')[-1] == "zip":
                            algorithm = "LLM" # need to be updated later
                            modelFramework = "Transformers"
                        elif Payload1["fileName"].split('.')[-1] == "h5":
                            modelFileObj = responseGet.content
                            print(" IN MODEL H5")
                            # Write the data to a file
                            with open('model.h5', 'wb') as f:
                                f.write(modelFileObj)
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
                        modelAttributesValuesId = ModelAttributesValues.create({"modelAttributeId":modelAttributesId,"modelId":modelId,"modelAttributeValues":Payload1[key]})
                return "Model Added Sucessfully"
        except Exception as exc:
            return f"MODEL Addition Failed! Please Try Again{exc}"



    def updateModel(payload,Payload1:UpdateModelPayloadRequest,Payload2:GetModelRequest):
        print(payload,"payload=====>")
        Models = Model.findall({"UserId":payload["userid"],'ModelId':payload['modelid'],"IsActive":'Y'})
        print(Models,"Models====>")
        if(len(Models)):
            Models = Models[0]
        else:
            return "No Data Exists With This Id."
        try:
            if Models:
                Payload1 = AttributeDict(Payload1)
                keys = Payload1.keys()

                # Reading metadata of ModelDB Table and Updating new metadata values
                attributesData = {}
                attributeValues = ModelAttributesValues.findall({"ModelId":payload['modelid'],"IsActive":'Y'})
                for value in attributeValues:
                    attributes = ModelAttributes.findall({"ModelAttributeId":value.ModelAttributeId,"IsActive":'Y'})[0]
                    attributesData[attributes['ModelAttributeName']] = value.ModelAttributeValues
                Payload1['fileName'] = Payload2.ModelFile.filename
                print(Payload1.keys(),"Payload1.keys()")
                # Update ModelAttributesDb and ModelAttributesValuesDb
                for key in keys:
                    if key not in attributesData:
                        continue
                    else:
                        attributeValues = ModelAttributesValues.findall({"ModelId":payload['modelid'],"IsActive":'Y'})
                        for value in attributeValues:
                            modelAttributeList = ModelAttributes.findall({"ModelAttributeId":value.ModelAttributeId,"IsActive":'Y'})[0]
                            if key == modelAttributeList['ModelAttributeName']:
                                ModelAttributesValues.update(value.ModelAttributeValuesId, {'ModelAttributeValues':Payload1[key]})
                print(keys,"keys")
                if db_type == 'mongo':
                    # this will checking dataFile present in Database or not and Update SaveFileDB
                    if Payload2.ModelFile:
                        model_file_id = FileStoreDb.fs.find_one({'_id':Models['ModelData']})
                        FileStoreDb.delete(Models['ModelData'])
                        model_extension = os.path.splitext(Payload2.ModelFile.filename)
                        modelFileId = FileStoreDb.create(Payload2.ModelFile,Payload2.ModelFile.filename)
                        Model.update(Models['_id'], {'ModelData':modelFileId})
                        print(Payload2.ModelFile.filename,"filename")
                if db_type == 'cosmos':
                    # this will checking dataFile present in Database or not and Update SaveFileDB
                    if Payload2.ModelFile:
                        model_file_blob_name = Models['ModelData']
                        container_name = os.getenv('MODEL_CONTAINER_NAME')
                        upload_file_api = os.getenv('AZURE_UPLOAD_API')
                        Payload2.ModelFile.file.seek(0)
                        responseUpdate =requests.post(url =upload_file_api, files ={"file":(Payload2.ModelFile.filename,Payload2.ModelFile.file)}, data ={"container_name":container_name}, verify = sslv[sslVerify]).json()
                        print(responseUpdate,"responseUpdate")
                        blob_name = responseUpdate["blob_name"]
                        print(blob_name,"blob_name UPDATED")
                        Model.update(Models['_id'], {'ModelData':blob_name})
                    
                return 'Model Updated Successfully'
            else:
                return "No Model Exists With This Id"
        except Exception as exc:
            return f"MODEL updating Failed! Please Try Again{exc}"



    def deleteModel(payload):
        Payload = AttributeDict(payload)
        Modelslist = Model.findall({"UserId":Payload["userid"],"ModelId":Payload["modelid"],'IsActive':'Y'})
        Model_AttributesValues = ModelAttributesValues.findall({"ModelId":Payload["modelid"],'IsActive':'Y'})

        try:
            if len(Modelslist):
                for Models in Model_AttributesValues:
                    ModelAttributesValues.update(Models['_id'], {'IsActive':'N'})

                    # ModelAttributes_list = ModelAttributes.findall({"ModelAttributeId":Models["ModelAttributeId"]})
                    # for ModelAttribute in ModelAttributes_list:
                    #     ModelAttributes.update(ModelAttribute['_id'], {'IsActive':'N'})

                for Models in Modelslist:
                    Model.update(Models['_id'], {'IsActive':'N'})

                return "Model Deleted Sucessfully"
            else:
                return 'No Model Available to Delete'
        except Exception as exc:
            return f"MODEL deletion Failed! Please Try Again{exc}"
    
    # ------------------------------------------------------------------------------------
    
    ## FOR PREPROCESSOR
    def getPreprocessor(payload):
        PreprocessorList = []
        try:
            response = Preprocessor.findall({"UserId":payload['userid'],"IsActive":'Y'})
            if response:
                for Preprocessors in response:
                    payload_data = {}
                    payload_data['preprocessorId'] = Preprocessors['PreprocessorId']
                    payload_data['preprocessorName'] = Preprocessors['PreprocessorName']
                    payload_data['preprocessorFileId'] = Preprocessors['PreprocessorFileId']
                    PreprocessorList.append(payload_data)
                PreprocessorList.reverse()
            else:
                return {"message": "This user doesn't have preprocessor values"}
            return PreprocessorList
        except Exception as exc:
            return f"Preprocessor retrieval failed due to {exc}"


    def addPreprocessor(userId,Payload1, Payload2):
        try:
            Payload1 = AttributeDict(Payload1)
            keys = Payload1.keys()
            x = Preprocessor.findall({"UserId":userId,"PreprocessorName":Payload1.preprocessorName,"IsActive":'Y'})
            if(len(x) > 0 ):
                return 'Preprocessor Already Exist With the Same Name.'
            else:
                if db_type == 'mongo':
                    preprocessorFileId = FileStoreDb.create(Payload2.PreprocessorFile,Payload1.preprocessorName)
                    preprocessorFileId = str(preprocessorFileId)
                    preprocessorId = Preprocessor.create({"userId":userId,"preprocessorName":Payload1.preprocessorName,"preprocessorFileId":preprocessorFileId})
                    return "Preprocessor Added Sucessfully"
                if db_type == 'cosmos': 
                    container_name = os.getenv('PREPROCESSOR_CONTAINER_NAME')
                    upload_file_api = os.getenv('AZURE_UPLOAD_API')
                    Payload2.PreprocessorFile.file.seek(0)
                    response =requests.post(url =upload_file_api, files ={"file":(Payload2.PreprocessorFile.filename,Payload2.PreprocessorFile.file)}, data ={"container_name":container_name}, verify = sslv[sslVerify]).json()
                    blob_name =response["blob_name"]
                    print(blob_name,"blob_name")
                    preprocessorId = Preprocessor.create({"userId":userId,"preprocessorName":Payload1.preprocessorName,"preprocessorFileId":blob_name})
                    return "Preprocessor Added Sucessfully"
        except Exception as exc:
            return f"Preprocessor Addition Failed! Please Try Again{exc}"

    def updatePreprocessor(payload,Payload1,Payload2):
        Preprocessors = Preprocessor.findall({"UserId":payload["userid"],'PreprocessorId':payload['preprocessorid'],"IsActive":'Y'})
        if(len(Preprocessors)):
            Preprocessors = Preprocessors[0]
        else:
            return "No Preprocessor Exists With This Id."
        try:
            if Preprocessors:
                Payload1 = AttributeDict(Payload1)
                keys = Payload1.keys()
                print(Payload1,"Payload1")
                print(Payload2,"Payload2")
                # Update PreprocessorDb
                for key in keys:
                    print(key,"key")
                    Preprocessor.update(Preprocessors['_id'], {key:Payload1[key]})
                if db_type == 'mongo':
                    # this will checking dataFile present in Database or not and Update SaveFileDB
                    if Payload2.PreprocessorFile:
                        preprocessor_file_id = FileStoreDb.fs.find_one({'_id':Preprocessors['PreprocessorFileId']})
                        print(preprocessor_file_id,"preprocessor_file_id")
                        FileStoreDb.delete(Preprocessors['PreprocessorFileId'])
                        preprocessorFileId = FileStoreDb.create(Payload2.PreprocessorFile,Payload2.PreprocessorFile.filename)
                        Preprocessor.update(Preprocessors['_id'], {'PreprocessorFileId':preprocessorFileId})
                    return 'Preprocessor Updated Successfully'
                if db_type == 'cosmos':
                    # this will checking dataFile present in Database or not and Update SaveFileDB
                    if Payload2.PreprocessorFile:
                        preprocessor_file_blob_name = Preprocessors['PreprocessorFileId']
                        container_name = os.getenv('PREPROCESSOR_CONTAINER_NAME')
                        upload_file_api = os.getenv('AZURE_UPLOAD_API')
                        Payload2.PreprocessorFile.file.seek(0)
                        responseUpdate =requests.post(url =upload_file_api, files ={"file":(Payload2.PreprocessorFile.filename,Payload2.PreprocessorFile.file)}, data ={"container_name":container_name}, verify = sslv[sslVerify]).json()
                        print(responseUpdate,"responseUpdate")
                        blob_name = responseUpdate["blob_name"]
                        print(blob_name,"blob_name UPDATED")
                        Preprocessor.update(Preprocessors['_id'], {'PreprocessorFileId':blob_name})
                    return 'Preprocessor Updated Successfully'
            else:
                return "No Preprocessor Exists With This Id"
        except Exception as exc:
            return f"Preprocessor updating Failed! Please Try Again{exc}"

    def deletePreprocessor(payload):
        Payload = AttributeDict(payload)
        Preprocessorlist = Preprocessor.findall({"UserId":Payload["userid"],"PreprocessorId":Payload["preprocessorid"],'IsActive':'Y'})
        try:
            if len(Preprocessorlist):
                for Preprocessors in Preprocessorlist:
                    Preprocessor.update(Preprocessors['_id'], {'IsActive':'N'})
                return "Preprocessor Deleted Sucessfully"
            else:
                return 'No Preprocessor Available to Delete'
        except Exception as exc:
            return f"Preprocessor deletion Failed! Please Try Again{exc}"
    
    
    
    ## FOR COMMON BATCH TABLE
    
    def getBatchList(payload):
        try:
            payloadInDictionary = AttributeDict(payload)
            print("PAYLOAD IN DICT AFTER DELETE===",payloadInDictionary)
            batchedTenetIds = []
            fairnessBatchIdValidation = [] ## FOR FAIRNESS ONLY
            uniqueBatchIds = set()
            for tenetName in payloadInDictionary.tenetName:
                tenantId = Tenet.findOne(tenetName)
                ## DATA CREATION FROM BATCH FOR FAIRNESS
                if(tenetName=="Fairness"):
                    def send_fairnress_request(batch_id):
                        print(batch_id,"Fairness batch_id")
                        response = requests.post(fairnessgeneration, batch_id, verify = sslv[sslVerify])
                        print("Fairness Response", response)
                    fairnessTenetId = Tenet.findOne("Fairness")
                    data_attribute_names = ["biasType", "methodType", "taskType", "label", "favorableOutcome", "protectedAttribute", "privilegedGroup","mitigationType","mitigationTechnique", "predLabel", "knn","sensitiveFeatures","favourableLabel"]
                    batchedTenetId = Batch.create(payload,tenantId)
                    fairnessBatchIdValidation = batchedTenetId
                    # getBatchId = batchedTenetId[0]
                    for name in data_attribute_names:
                        fairnessDataAttribute = DataAttributes.findDAVId({"DataAttributeName": name}, {"tenetId": fairnessTenetId})
                        # print("fairnessDataAttribute==",fairnessDataAttribute)
                        if fairnessDataAttribute is not None and payloadInDictionary[name] is not None:
                            payloadInDictionary['DataAttributeId'] = fairnessDataAttribute  
                            payloadInDictionary['DataAttributevalues'] = payloadInDictionary[name]
                            payloadInDictionary['BatchId'] = batchedTenetId['BatchId']
                            #print("PAYLOAD IN DICT in IF LOOP===",payloadInDictionary)
                            fairnessDataAdd = DataAttributesValues.createForBatchData(payloadInDictionary)
                            del payloadInDictionary['DataAttributeId']
                            del payloadInDictionary['DataAttributevalues']
                            del payloadInDictionary['BatchId']
                            print("DATA INSERTED IN DATA ATTRIBUTE VALUES FOR FAIRNESS")
                    # Trigger the API call asynchronously using a separate thread
                    print(fairnessDataAdd, "Fairness generated ID")
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.submit(send_fairnress_request, batchedTenetId['BatchId'])
                    print("Fairness batch completed")
                    batchedTenetIds.append({"BatchId": batchedTenetId["BatchId"], "TenetId": tenantId})
                    uniqueBatchIds.add(batchedTenetId['BatchId'])
                    # print("batchedTenetIdsFair===",batchedTenetIds)
                ## MODEL CREATION DATA FROM BATCH FOR SECURITY
                if(tenetName=="Security"):
                    def send_seurity_request(batch_id):
                        print(batch_id,"Security batch_id")
                        data = {
                            'batchId':batch_id
                        }
                        response = requests.post(securitygeneration, data=data,verify = sslv[sslVerify])
                        print("Security Response", response)
                    securityTenetId = tenantId
                    data_attribute_names = ["appAttacks"]
                    batchedTenetId = Batch.create(payload,tenantId)
                    for name in data_attribute_names:
                        securityDataAttribute = ModelAttributes.findMAVId({"ModelAttributeName": name}, {"tenetId": securityTenetId})
                        # print("securityDataAttribute==",securityDataAttribute)
                        if securityDataAttribute is not None and payloadInDictionary[name] is not None:
                            payloadInDictionary['ModelAttributeId'] = securityDataAttribute  
                            payloadInDictionary['ModelAttributevalues'] = payloadInDictionary[name]
                            payloadInDictionary['BatchId'] = batchedTenetId['BatchId']
                            #print("PAYLOAD IN DICT IN IF LOOP===",payloadInDictionary)
                            securityDataAdd = ModelAttributesValues.createForBatchData(payloadInDictionary)
                            del payloadInDictionary['ModelAttributeId']
                            del payloadInDictionary['ModelAttributevalues']
                            del payloadInDictionary['BatchId']
                            print("DATA INSERTED IN MODEL ATTRIBUTE VALUES FOR SECURITY")
                        
                    # Trigger the API call asynchronously using a separate thread
                    p1 = multiprocessing.Process(target = send_seurity_request, args=(batchedTenetId['BatchId'], )) 
                    print("Security batch completed")
                    batchedTenetIds.append({"BatchId": batchedTenetId["BatchId"], "TenetId": tenantId})  # Add the new entry to the list
                    uniqueBatchIds.add(batchedTenetId['BatchId'])
                ## MODEL CREATION DATA FROM BATCH FOR FAIRNESS
                if(tenetName=="Fairness"):
                    def send_fairnress_request(batch_id):
                        print(batch_id,"Fairness batch_id")
                        response = requests.post(fairnessgeneration, batch_id, verify = sslv[sslVerify])
                        print("Fairness Response", response)
                    fairnessTenetId = Tenet.findOne("Fairness")
                    data_attribute_names = ["label"]
                    batchedTenetId = fairnessBatchIdValidation
                    for name in data_attribute_names:
                        fairnessModelAttribute = ModelAttributes.findMAVId({"ModelAttributeName": name}, {"tenetId": fairnessTenetId})
                        print("fairnessModelAttribute==",fairnessModelAttribute)
                        if fairnessModelAttribute is not None and payloadInDictionary[name] is not None:
                            payloadInDictionary['ModelAttributeId'] = fairnessModelAttribute  
                            payloadInDictionary['ModelAttributevalues'] = payloadInDictionary[name]
                            payloadInDictionary['BatchId'] = batchedTenetId['BatchId']
                            #print("PAYLOAD IN DICT in IF LOOP===",payloadInDictionary)
                            fairnessDataAdd = ModelAttributesValues.createForBatchData(payloadInDictionary)
                            del payloadInDictionary['ModelAttributeId']
                            del payloadInDictionary['ModelAttributevalues']
                            del payloadInDictionary['BatchId']
                            print("DATA INSERTED IN DATA ATTRIBUTE VALUES FOR FAIRNESS")
                    # Trigger the API call asynchronously using a separate thread
                    print(fairnessDataAdd, "Fairness generated ID")
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.submit(send_fairnress_request, batchedTenetId['BatchId'])
                    print("Fairness batch completed")
                    if batchedTenetId["BatchId"] not in uniqueBatchIds:
                        # Add the BatchId to the set
                        uniqueBatchIds.add(batchedTenetId["BatchId"])

                        # Append the BatchId and TenetId to the list
                        batchedTenetIds.append({"BatchId": batchedTenetId["BatchId"], "TenetId": tenantId})
                    # batchedTenetIds.append({"BatchId": batchedTenetId["BatchId"], "TenetId": tenantId})
                    
                    print("batchedTenetIdsFair===",batchedTenetIds)
                    print("uniqueBatchIds===",uniqueBatchIds)
                
                ## MODEL CREATION DATA FROM BATCH FOR EXPLAINABILITY
                if(tenetName=="Explainability"):
                    def send_explainability_request(batch_id):
                        print(batch_id,"batch_id")
                        response = requests.post(explainabilitygeneration, batch_id, verify = sslv[sslVerify])
                        print("Explainability Response", response)
                    explainabilityTenetId = Tenet.findOne("Explainability")
                    data_attribute_names = ["appExplanationMethods"]
                    batchedTenetId = Batch.create(payload,tenantId)
                    for name in data_attribute_names:
                        explainabilityDataAttribute = ModelAttributes.findMAVId({"ModelAttributeName": name}, {"tenetId": explainabilityTenetId})
                        if explainabilityDataAttribute is not None and payloadInDictionary[name] is not None:
                            payloadInDictionary['ModelAttributeId'] = explainabilityDataAttribute  
                            payloadInDictionary['ModelAttributevalues'] = payloadInDictionary[name]
                            payloadInDictionary['BatchId'] = batchedTenetId['BatchId']
                            explainabilityDataAdd = ModelAttributesValues.createForBatchData(payloadInDictionary)
                            del payloadInDictionary['ModelAttributeId']
                            del payloadInDictionary['ModelAttributevalues']
                            del payloadInDictionary['BatchId']
                            print("DATA INSERTED IN MODEL ATTRIBUTE VALUES FOR EXPLAINABILITY")
                    # Trigger the API call asynchronously using a separate thread
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.submit(send_explainability_request, batchedTenetId['BatchId'])
                    print("Explainability batch completed")
                    batchedTenetIds.append({"BatchId": batchedTenetId["BatchId"], "TenetId": tenantId})  # Add the new entry to the list
                    uniqueBatchIds.add(batchedTenetId['BatchId'])
                    # print("batchedTenetIdsExplain===",batchedTenetIds)
            return batchedTenetIds
        except Exception as exc:
            return f"Batch Creation Failed {exc}"
    
    ## FOR BATCH STATUS
    
    def getBatchStatusList(payload):
        status = Batch.findStatus(payload)
        return status
    
    ## GET BATCHES LIST
    
    def getBatchTable(payload):
        try:
            batches = Batch.findBatchTable(payload['userid'])

            TenetDataList = InfosysRAI.getTenetsList()
            ModelList = Model.findall({"UserId":payload['userid'],"IsActive":'Y'})
            DataList = Data.findall({"UserId":payload['userid'],"IsActive":'Y'})
            TenetMapping = {}
            ModelMapping = {}
            DataMapping = {}
            for Tenets in TenetDataList:
                TenetMapping[Tenets['Id']] = Tenets['TenetName']
            for Models in ModelList:
                ModelMapping[Models['ModelId']] = Models['ModelName']
            for Datas in DataList:
                DataMapping[Datas['DataId']] = Datas['DataSetName']

            for batch in batches:
                if batch['TenetId'] in TenetMapping:
                    batch['TenetName'] = TenetMapping[batch['TenetId']] 
                if batch['ModelId'] in ModelMapping:
                    batch['ModelName'] = ModelMapping[batch['ModelId']]
                if batch['DataId'] in DataMapping:
                    batch['DataSetName'] = DataMapping[batch['DataId']] 
            batches.reverse()
            del TenetDataList, ModelList, DataList
            del TenetMapping, ModelMapping, DataMapping
            return batches
        
        except Exception as exc:
            return f"Batch deletion Failed! As{exc}"
    

    def deleteBatch(payload):
        Payload = AttributeDict(payload)

        try:
            Batchslist = Batch.findall({"UserId":Payload["userid"],"BatchId":Payload["batchid"]})
            HtmlReportlist = Html.findall({"BatchId":Payload["batchid"]})
            PdfReportlist = Report.findall({"BatchId":Payload["batchid"]})

            if len(Batchslist):

                for HtmlReportDict in HtmlReportlist:
                    if 'HtmlFileId' in HtmlReportDict:
                        FileStoreDb.delete(HtmlReportDict['HtmlFileId'])
                Html.delete({"BatchId": Payload["batchid"]})   

                for PdfReportDict in PdfReportlist:
                    if 'ReportFileId' in PdfReportDict:
                        FileStoreDb.delete(PdfReportDict['ReportFileId'])
                Report.delete({"BatchId":Payload["batchid"]})   
                
                Batch.delete({"UserId":Payload["userid"],"BatchId":Payload["batchid"]}) 
                del Batchslist, HtmlReportlist, PdfReportlist

                return "Batch Deleted Sucessfully"
            else:
                return "Please Provide Correct BatchId!"
            
        except Exception as exc:
            return f"Batch deletion Failed! As{exc}"
        