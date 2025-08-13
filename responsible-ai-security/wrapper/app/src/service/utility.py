'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''



import io
import os
import numpy as np
import pickle
#from keras.models import load_model
import tempfile
import datetime,time
import pytz
import pandas as pd
import json
import os
import zipfile
import shutil
import pdfkit
import requests
import csv
import re

import matplotlib.pyplot as plt
import seaborn as sns
import base64

from sklearn.metrics import accuracy_score, confusion_matrix

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyPDF2 import PdfWriter, PdfReader

from src.config.urls import UrlLinks as UL
from sklearn.svm import SVC
from src.dao.Batch import Batch
from src.dao.ModelDb import Model
from src.dao.ModelAttributesDb import ModelAttributes
from src.dao.ModelAttributesValuesDb import ModelAttributesValues
from src.dao.DataDb import Data
from src.dao.DataAttributesDb import DataAttributes
from src.dao.DataAttributesValuesDb import DataAttributesValues
from src.dao.SaveFileDB import FileStoreDb

from src.dao.Security.SecReportDb import SecReport

#from tensorflow.keras.preprocessing import image
from art.estimators.classification import SklearnClassifier
from art.attacks.poisoning.poisoning_attack_svm import PoisoningAttackSVM
from art.estimators.classification.scikitlearn import SklearnAPIClassifier
import concurrent.futures as con
from src.config.logger import CustomLogger

log =CustomLogger()


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

fetch_file = os.getenv("AZURE_GET_API")
upload_file = os.getenv("AZURE_UPLOAD_API")
dataset_container = os.getenv("DATA_CONTAINER_NAME")
model_container = os.getenv("MODEL_CONTAINER_NAME")
zip_container = os.getenv("ZIP_CONTAINER_NAME")
telemetry_flg =os.getenv("TELEMETRY_FLAG")

apiEndPoint ='/v1/security/model'
errorRequestMethod = 'GET'

class Utility:

    AttackTypes = {
        'Art':{
            'Evasion':[
                    "ProjectedGradientDescentTabular","ZerothOrderOptimization","QueryEfficient", 
                    "Deepfool", "Wasserstein", "Boundary", 'CarliniL2Method', 'Pixel', 
                    'UniversalPerturbation', 'FastGradientMethod', 'SpatialTransformation', 'Square', 
                    'ProjectGradientDescentImage', 'BasicIterativeMethod', 'SaliencyMapMethod',
                    'DecisionTree', 'IterativeFrameSaliency','SimBA', 'NewtonFool',
                    'ElasticNet','Poisoning','HopSkipJumpTabular',"HopSkipJumpImage", 
                    "QueryEfficientGradientAttackEndPoint", 'BoundaryAttackEndPoint',
                    'HopSkipJumpAttackEndPoint','VirtualAdversarialMethod', 'GeometricDecisionBasedAttack',
                    'Threshold'
                ],
            'Inference':[ 
                        'MembershipInferenceRule', 'AttributeInference',
                        'InferenceLabelOnlyGap', 'AttributeInferenceWhiteBoxDecisionTree',
                        'AttributeInferenceWhiteBoxLifestyleDecisionTree',
                        'LabelOnlyDecisionBoundary','MembershipInferenceBlackBox',
                        'LabelOnlyGapAttackEndPoint',
                        'MembershipInferenceBlackBoxRuleBasedAttackEndPoint',
                        'LabelOnlyDecisionBoundaryAttackEndPoint',
                        'MembershipInferenceBlackBoxAttackEndPoint'
                    ]
            },
        'Augly':{
            'Augmentation':['Augly']
            }
    }

    
    def find_duplicates(x_train):

        """
        Returns an array of booleans that is true if that element was previously in the array
        :param x_train: training data
        :type x_train: `np.ndarray`
        :return: duplicates array
        :rtype: `np.ndarray`
        """
        
        try:
            dup = np.zeros(x_train.shape[0])
            for idx, x in enumerate(x_train):
                dup[idx] = np.isin(x_train[:idx], x).all(axis=1).any()
            return dup 
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "find_duplicates", e, apiEndPoint, errorRequestMethod)
 

    def get_adversarial_examples(x_train, y_train, attack_idx, x_val, y_val, kernel):
        try:
            # Create ART classifier for scikit-learn SVC
            art_classifier = SklearnClassifier(model=SVC(kernel=kernel), clip_values=(0, 10))
            art_classifier.fit(x_train, y_train)
            init_attack = np.copy(x_train[attack_idx])
            y_attack = np.array([1, 1]) - np.copy(y_train[attack_idx])
            attack = PoisoningAttackSVM(art_classifier, 0.0001, 1.0, x_train, y_train, x_val, y_val, max_iter=50)
            final_attack, _ = attack.poison(np.array([init_attack]), y=np.array([y_attack]))
            
            del init_attack,y_attack,attack
            return final_attack, art_classifier 
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "get_adversarial_examples", e, apiEndPoint, errorRequestMethod)   


    def calc_precision_recall(predicted, actual, positive_value=1):
        try:
            score = 0  # both predicted and actual are positive
            num_positive_predicted = 0  # predicted positive
            num_positive_actual = 0  # actual positive
            for i in range(len(predicted)):
                if predicted[i] == positive_value:
                    num_positive_predicted += 1
                if actual[i] == positive_value:
                    num_positive_actual += 1
                if predicted[i] == actual[i]:
                    if predicted[i] == positive_value:
                        score += 1

            if num_positive_predicted == 0:
                precision = 1
            else:
                precision = score / num_positive_predicted  # the fraction of predicted “Yes” responses that are correct
            if num_positive_actual == 0:
                recall = 1
            else:
                recall = score / num_positive_actual  # the fraction of “Yes” responses that are predicted correctly

            del score,num_positive_predicted,num_positive_actual
            return precision, recall
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "calc_precision_recall", e, apiEndPoint, errorRequestMethod)
    

    def safe_load_from_file(file_path):
        try:
            with open(file_path, 'rb') as f:
                data = f.read()

            file_like_object = io.BytesIO(data)

            original_globals = globals().copy()
            restricted_globals = {'__builtins__': __builtins__,}
            globals().update(restricted_globals)

            unpickler = pickle.Unpickler(file_like_object)
            return unpickler.load()

        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "safe_load_from_file", e, apiEndPoint, errorRequestMethod)    

        finally:
            globals().clear()
            globals().update(original_globals)       


    def readModelFile(payload):
        
        try:
            root_path = os.getcwd()
            root_path = Utility.getcurrentDirectory() + "/database"
            dirList = ["cacheMemory","data","model","payload","report"]
            for dir in dirList:
                dirs = root_path + "/" + dir
                if not os.path.exists(dirs):
                    os.mkdir(dirs)

            # Reading modelId from Batch Table
            batchList = Batch.findall({'BatchId':payload})[0]
            modelList = Model.findall({'ModelId':batchList['ModelId']})[0]
            modelName = modelList['ModelName']
            
            #  Reading ModelAttribute file content from MongoDB and stroing in Payload Folder.
            attributesData = {}
            attributeValues = ModelAttributesValues.findall({"ModelId":modelList['ModelId']})
            for value in attributeValues:
                attributes = ModelAttributes.findall({"ModelAttributeId":value.ModelAttributeId})[0]
                attributesData[attributes["ModelAttributeName"]] = value.ModelAttributeValues
            modelFramework = attributesData['modelFramework']
            
            if attributesData['useModelApi'] == 'No':
                
                #  Reading model file content from MongoDB and stroing in Database Folder.
                if(os.getenv("DB_TYPE") == "mongo"):
                    modelDataId = modelList['ModelData']
                    modelFile = FileStoreDb.fs.get(modelDataId)
                    modelF = modelFile.read()
                    modelFileType = modelFile.filename.split('.')[-1]
                else:
                    modelFile =requests.get(url =fetch_file, params ={"container_name":model_container,"blob_name":modelList['ModelData']})
                    binary_data = modelFile.content
                    temp = io.BytesIO(binary_data)
                    modelF = temp.read()

                    content_disposition = modelFile.headers.get('content-disposition')
                    modelFileType = content_disposition.split(';')[1].split('=')[1].split('.')[-1]

                model_path = root_path + "/model"
                # model_path = os.path.join(model_path,modelName+'.'+modelFileType)
                # model_path = os.path.join(model_path,modelFile.filename)
                model_path = os.path.join(model_path,modelName+'.'+modelFileType)
                if os.path.exists(model_path):
                    os.remove(model_path)
                with open(model_path, 'wb') as f:
                    f.write(modelF)
                
                model_data:any
                if modelFileType == 'h5':
                    model_data = load_model(model_path) 
                else:
                    # model_data = pickle.load(open(model_path, "rb"))
                    model_data = Utility.safe_load_from_file(model_path)     

                del batchList,modelList,attributesData,attributeValues,modelF
                return model_data, model_path, modelName, modelFramework
            else:
                return modelName
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "readModelFile", e, apiEndPoint, errorRequestMethod)
    

    def extractCSVFromZip(cache_path, data_path):

        try:
            with zipfile.ZipFile(cache_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                
                csv_files = [f for f in file_list if f.endswith('.csv')]
                if len(csv_files) == 1:
                    csv_file_path = csv_files[0]
                    data_path = os.path.join(data_path, csv_file_path)
                    with zip_file.open(csv_file_path) as csv_file:
                        # os.makedirs(os.path.dirname(os.path.join(data_path, csv_file_path)), exist_ok=True)
                        with open(data_path, 'wb') as output_file:
                            output_file.write(csv_file.read())

            del file_list,csv_files
            return data_path
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "extractCSVFromZip", e, apiEndPoint, errorRequestMethod)
    
    
    def extractIMAGEFromZip(cache_path, data_path):

        try:
            with zipfile.ZipFile(cache_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                
                image_files = [f for f in file_list if any(f.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif'])]
                data_path = os.path.join(data_path, os.path.basename(cache_path).split('.')[0])
                for image_file in image_files:

                    output_file_path = os.path.join(data_path, os.path.basename(image_file))
                    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                    with zip_file.open(image_file, 'r') as zip_data, open(output_file_path, 'wb') as output_file:
                        shutil.copyfileobj(zip_data, output_file)

                    # OR
                    
                    # with zip_file.open(image_file, 'r') as image_data:
                    #     image = Image.open(io.BytesIO(image_data.read()))
                    #     output_file_path = os.path.join(data_path, os.path.basename(image_file))
                    #     os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                    #     image.save(output_file_path)

            del file_list,image_files      
            return data_path
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "extractIMAGEFromZip", e, apiEndPoint, errorRequestMethod)   
    
    
    def readDataFile(payload):

        try:
            root_path = os.getcwd()
            root_path = Utility.getcurrentDirectory() + "/database"
            dirList = ["cacheMemory","data","model","payload","report"]
            for dir in dirList:
                dirs = root_path + "/" + dir
                if not os.path.exists(dirs):
                    os.mkdir(dirs)

            # Reading modelId from Batch Table
            batchList = Batch.findall({'BatchId':payload['BatchId']})[0]
            dataList = Data.findall({'DataId':batchList['DataId']})[0]
            modelList = Model.findall({'ModelId':batchList['ModelId']})[0]
            datasetName = modelList['ModelName'] 

            datasetName = Utility.sanitize_filenameorfoldername(datasetName)
            
            #  Reading Data file content from MongoDB and stroing in Database Folder.
            sampleDataId = dataList['SampleData']
            if(os.getenv("DB_TYPE") == "mongo"):
                dataFile = FileStoreDb.fs.get(sampleDataId)
                # dataContent = FileStoreDb.findOne(dataList['SampleData'])
                dataF = dataFile.read()
                dataFileType = dataFile.filename.split('.')[-1]
            else: 
                dataFile =requests.get(url =fetch_file, params ={"container_name":dataset_container,"blob_name":dataList['SampleData']})
                binary_data = dataFile.content
                temp = io.BytesIO(binary_data)
                dataF = temp.read()

                content_disposition = dataFile.headers.get('content-disposition')
                dataFileType = content_disposition.split(';')[1].split('=')[1].split('.')[-1]             
            
            data_path = root_path + "/data"
            # data_path = os.path.join(data_path,datasetName + '.' + dataFileType)
            cache_path = root_path + "/cacheMemory"
            # cache_path = os.path.join(cache_path, dataContent["fileName"]) 
            cache_path = os.path.join(cache_path,datasetName + '.' + dataFileType)
            # print('run1',data_path)
            # print('run1',cache_path)

            # if os.path.exists(data_path):    
            #     os.remove(data_path)                                       
            # with open(data_path, 'wb') as f:
            #     f.write(dataF)
            if os.path.exists(cache_path):    
                os.remove(cache_path)                                       
            with open(cache_path, 'wb') as f:
                # f.write(dataContent["data"])
                f.write(dataF)

            if cache_path.endswith('.zip'):
                with zipfile.ZipFile(cache_path, 'r') as zip_file:
                    file_list = zip_file.namelist()
                    csv_files = [f for f in file_list if f.endswith('.csv')]
                    image_files = [f for f in file_list if any(f.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif'])]
                if len(csv_files) == 1 and not image_files:
                    data_path = Utility.extractCSVFromZip(cache_path, data_path)
                elif not csv_files and image_files:
                    data_path = Utility.extractIMAGEFromZip(cache_path, data_path)
            
            elif cache_path.endswith('.csv'):
                # data_path = os.path.join(data_path, dataContent["fileName"]) 
                data_path = os.path.join(data_path, datasetName + '.' + dataFileType) 
                with open(cache_path, 'r') as source_file:
                    reader = csv.reader(source_file)
                    with open(data_path, 'w', newline='') as output_file:
                        writer = csv.writer(output_file)
                        for row in reader:
                            writer.writerow(row)  

            elif any(cache_path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):                   
                # data_path = os.path.join(data_path, dataContent["fileName"])  
                data_path = os.path.join(data_path, datasetName + '.' + dataFileType)            
                with open(cache_path, 'rb') as source_file, open(data_path, 'wb') as dest_file:
                    shutil.copyfileobj(source_file, dest_file)
            # print('run2',data_path)
            # print('run2',cache_path)
            Utility.databaseDelete(cache_path)
            
            # raw_data:any
            # if dataFileType != 'csv':
            #     raw_data = image.load_img(data_path, target_size=(299, 299))
            # else:
            #     raw_data = pd.read_csv(data_path)
            
            # del dataF
            # return raw_data, data_path

            raw_data:any
            if os.path.isdir(data_path):
                raw_data = {}
                for item in os.listdir(data_path):
                    item_path = os.path.join(data_path, item)
                    if os.path.isfile(item_path):
                        if payload['modelFramework'] == 'Keras':
                            input_shape = payload['model'].input_shape
                            raw_data[item] = image.load_img(item_path, target_size=input_shape[1:-1])
                        else:
                            raw_data[item] = image.load_img(item_path, target_size=(299, 299))
                    elif os.path.isdir(item_path):
                        pass
            elif zipfile.is_zipfile(data_path):
                pass
            elif data_path.endswith('.csv'):
                raw_data = pd.read_csv(data_path)
            elif any(data_path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                raw_data = {}
                if payload['modelFramework'] == 'Keras':
                    input_shape = payload['model'].input_shape
                    raw_data[os.path.basename(data_path)] = image.load_img(data_path, target_size=input_shape[1:-1])
                else:
                    raw_data[os.path.basename(data_path)] = image.load_img(data_path, target_size=(299, 299))
            
            del batchList,dataList,modelList,dataF
            return raw_data, data_path
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "readDataFile", e, apiEndPoint, errorRequestMethod)
        

    def updateGroundTruthLabelId(dataid,groundtruthID,groundtruthlabel):
        try:
            groundtruthLabelattributesid = DataAttributes.findall({'DataAttributeName':'groundTruthClassLabel'})[0]['DataAttributeId']
            groundtruthIdattributesid = DataAttributes.findall({'DataAttributeName':'groundTruthClassNames'})[0]['DataAttributeId']

            attributesValueDict = DataAttributesValues.findall({'DataId':dataid})
            for d in attributesValueDict:
                if d['DataAttributeId'] == groundtruthLabelattributesid:
                    groundtruthLabel_id = d['_id']
                if d['DataAttributeId'] == groundtruthIdattributesid:
                    groundtruthId_id = d['_id']

            k1=DataAttributesValues.update(groundtruthLabel_id,{'DataAttributeValues':groundtruthlabel})   
            k2=DataAttributesValues.update(groundtruthId_id,{'DataAttributeValues':groundtruthID}) 
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "updateGroundTruthLabelId", e, apiEndPoint, errorRequestMethod)    


    def readPayloadFile(payload):
        try:
            root_path = os.getcwd()
            root_path = Utility.getcurrentDirectory() + "/database"
            dirList = ["cacheMemory","data","model","payload","report"]
            for dir in dirList:
                dirs = root_path + "/" + dir
                if not os.path.exists(dirs):
                    os.mkdir(dirs)
            
            # Reading modelId,dataId from Batch Table
            batchList = Batch.findall({'BatchId':payload})[0]
            modelList = Model.findall({'ModelId':batchList['ModelId']})[0]
            dataList = Data.findall({'DataId':batchList['DataId']})[0]
            payloadName = modelList['ModelName'] 

            groundtruthFlagValue = dataList['GroundTruthImageFileId']
            if groundtruthFlagValue!="NA":
                groundtruthlabelId = dataList['GroundTruthImageFileId']
                if(os.getenv("DB_TYPE") == "mongo"):
                    groundtruthFile = FileStoreDb.fs.get(groundtruthlabelId)
                    groundF = groundtruthFile.read()
                    groundtruthFileType = groundtruthFile.filename.split('.')[-1]
                else: 
                    groundtruthFile =requests.get(url =fetch_file, params ={"container_name":dataset_container,"blob_name":groundtruthlabelId})
                    binary_data = groundtruthFile.content
                    temp = io.BytesIO(binary_data)
                    groundF = temp.read()

                    content_disposition = groundtruthFile.headers.get('content-disposition')
                    groundtruthFileType = content_disposition.split(';')[1].split('=')[1].split('.')[-1]  

                groundTruth_path = root_path + "/payload"
                groundTruth_path = os.path.join(groundTruth_path,payloadName + '.' + groundtruthFileType)
            
                if os.path.exists(groundTruth_path):    
                    os.remove(groundTruth_path)                                       
                with open(groundTruth_path, 'wb') as f:
                    f.write(groundF)

                if groundtruthFileType=='csv':
                    raw_data = pd.read_csv(groundTruth_path)
                    for column_index in range(len(raw_data.columns)):
                        column_values = raw_data.iloc[:, column_index]
                        if column_index == 0:
                            groundtruthID = column_values.tolist()
                        elif column_index == 1:
                            groundtruthlabel = column_values.tolist()
                    d1=dict(zip(groundtruthID,groundtruthlabel))
                    Utility.updateGroundTruthLabelId(dataList['DataId'],groundtruthID,groundtruthlabel)
                    Utility.databaseDelete(groundTruth_path)

                elif groundtruthFileType=='xlsx':
                    raw_data = pd.read_excel(groundTruth_path)
                    for column_index in range(len(raw_data.columns)):
                        column_values = raw_data.iloc[:, column_index]
                        if column_index == 0:
                            groundtruthID = column_values.tolist()
                        elif column_index == 1:
                            groundtruthlabel = column_values.tolist()
                    d1=dict(zip(groundtruthID,groundtruthlabel))
                    Utility.updateGroundTruthLabelId(dataList['DataId'],groundtruthID,groundtruthlabel)
                    Utility.databaseDelete(groundTruth_path)

                elif groundtruthFileType=='json':
                    with open(groundTruth_path, 'r') as file:
                        raw_data = json.load(file) 
                    for k,i in zip(raw_data.values(),range(len(raw_data))):
                        if i == 0:
                            groundtruthID = k
                        elif i == 1:
                            groundtruthlabel = k
                    d1=dict(zip(groundtruthID,groundtruthlabel))
                    Utility.updateGroundTruthLabelId(dataList['DataId'],groundtruthID,groundtruthlabel)
                    Utility.databaseDelete(groundTruth_path)
            
            #  Reading ModelAttribute content and stroing in attributesData.
            attributesData = {}
            attributeValues = ModelAttributesValues.findall({"ModelId":modelList['ModelId']})
            for value in attributeValues:
                attributes = ModelAttributes.findall({"ModelAttributeId":value.ModelAttributeId})[0]
                attributesData[attributes["ModelAttributeName"]] = value.ModelAttributeValues

            #  Reading DataAttribute content and stroing in attributesData1.
            attributesData1 = {}
            attributeValues = DataAttributesValues.findall({"DataId":dataList['DataId']})
            for value in attributeValues:
                attributes = DataAttributes.findall({"DataAttributeId":value.DataAttributeId})[0]
                attributesData1[attributes["DataAttributeName"]] = value.DataAttributeValues

            # combine attributesData1 and attributesData2 into one attributesData
            for k in attributesData1:
                if k not in attributesData:
                    attributesData[k] = attributesData1[k]

            modelEndPoint = modelList['ModelEndPoint'] 
            attributesData['modelEndPoint'] = modelEndPoint   
            
            payload_path = root_path + "/payload"
            payload_path = os.path.join(payload_path,payloadName+".txt") 
            if os.path.exists(payload_path):                          
                os.remove(payload_path)                                       
            with open(payload_path, 'w') as f:
                f.write(json.dumps(attributesData))
            
            del batchList,dataList,modelList,attributesData,attributeValues,attributesData1
            return payload_path
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "readPayloadFile", e, apiEndPoint, errorRequestMethod)
        
    
    def databaseDelete(payload):
        try:
            if os.path.isfile(payload):
                os.remove(payload)
            elif os.path.isdir(payload):    
                shutil.rmtree(payload)
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "databaseDelete", e, apiEndPoint, errorRequestMethod)
        
    
    def updateCurrentID():
        try:
            root_path = os.getcwd()
            directories = root_path.split(os.path.sep)
            testFlag = False
            for i in range(len(directories)-1, -1, -1):
                if directories[i] == 'test':
                    testFlag = True
                    break
            if testFlag == True:
                src_index = directories.index("test")
                new_path = os.path.sep.join(directories[:src_index])
            else:
                new_path = os.getcwd()
            path = new_path + '/app/config/urls.py'
    
            with open(path, 'r', encoding="utf8") as f:
                data = f.readlines()
    
            UL.Current_ID += 2  # Increment the Current_ID by 2
            Current_Report_ID = UL.Current_ID
            data[20] = f"    Current_ID = {Current_Report_ID}\n"
    
            # with open(path, 'w', encoding="utf8") as f1:
            #     f1.writelines(data)
    
            # Persist the updated UL.Current_ID value
            with open(path, 'r', encoding="utf8") as f2:
                updated_data = f2.read()
            with open(path, 'w', encoding="utf8") as f3:
                f3.write(updated_data.replace(f"    Current_ID = {Current_Report_ID - 2}", f"    Current_ID = {Current_Report_ID}"))
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "updateCurrentID", e, apiEndPoint, errorRequestMethod)    
    

    def updateReportsList(payload):
        try:
            # Taking latest report among reports
            latestDict = {}
            for d in payload['reportList']:
                name = d['ReportName'].split('.')[0]
                if name in payload['attackList']:
                    if d['ReportName'] == payload['modelName']+".zip":
                        continue 
                    else:
                        if name in latestDict:
                            if d['CreatedDateTime'] > latestDict[name]['CreatedDateTime']:
                                latestDict[name] = d
                        else:
                            latestDict[name] = d
            latestReportList = list(latestDict.values())
            
            # Sorting reports base on attack-type
            # reportList_dict = {item['ReportName']: item for item in reportList}
            # reportList = [reportList_dict[item] for item in payload['attackList'] if item in reportList_dict]
            # reportList = [next(item for item in latestReportList if item['ReportName'].split('.')[0] == attackName) for attackName in payload['attackList']]
            reportList = [report for attack in payload['attackList'] for report in latestReportList if attack == report['ReportName'].split('.')[0]]
            # reportList = []
            # for attackName in payload['attackList']:
            #     for report in latestReportList:
            #         if attackName == report['ReportName'].split('.')[0]:
            #             reportList.append(report)
            #             break
            #         else:
            #             continue

            del latestDict,latestReportList
            return reportList
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "updateReportsList", e, apiEndPoint, errorRequestMethod)

    
    def sortReportsList(payload):

        # sort_reports = sorted(payload, key=
        #         lambda x:datetime.datetime.strptime(
        #             x['CreatedDateTime'].strftime("%Y-%m-%dT%H:%M:%S.%f"), "%Y-%m-%dT%H:%M:%S.%f"
        #         ), reverse=True)

        # OR
        try:
            sort_reports = sorted(payload, key=lambda x:x['CreatedDateTime'], reverse=True)

            return sort_reports
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "sortReportsList", e, apiEndPoint, errorRequestMethod)
    

    def dateTimeFormat(payload):

        try:
            # ------------------------------------------------------------------------------------
            # # payload = "2023-12-27T18:22:10.015+00:00"
            # # parsed_date = time.mktime(time.strptime(payload[:-6], "%Y-%m-%dT%H:%M:%S.%f"))
            # # format_date = time.strftime("%d-%m-%Y %I:%M:%S %p", time.localtime(parsed_date))
            # # print(format_date)

            # # payload = datetime.datetime.now()
            # format_date = payload.strftime("%d-%m-%Y %I:%M:%S %p")
            # formatted_date = datetime.datetime.strptime(format_date, "%d-%m-%Y %I:%M:%S %p")

            # # print('Parsed_Date', payload, type(payload))
            # # print('Format_Date', format_date, type(format_date))
            # # print('Formatted_Date', formatted_date, type(formatted_date))

            # return format_date 
            # ------------------------------------------------------------------------------------

            # ------------------------------------------------------------------------------------
            # reportTime:any
            # d1_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M %p")
            # # d2_time = datetime.datetime.now(pytz.utc).strftime("%d-%m-%Y %H:%M")

            # # if d1_time[:-3] == d2_time:
            #     # print('d2_time', f"{d2_time} UTC(-5:30)") 
            #     # reportTime = f"{d1_time} UTC"  # UTC: Coordinated Universal Time
            # # else:
            # #     print('d1_time', f"{d1_time} IST(+5:30)") 
            # #     reportTime = f"{d1_time} IST(+5:30)"  # IST: Indian Standard Time
            # reportTime = f"{d1_time} UTC"

            # return reportTime
            # ------------------------------------------------------------------------------------

            # ------------------------------------------------------------------------------------
            # print(payload)
            dateTime:any
            if payload is None:
                dateTime = f"{(datetime.datetime.now()).strftime('%d-%m-%Y %I:%M:%S %p')} UTC"
            else:
                dateTime = f"{payload.strftime('%d-%m-%Y %I:%M:%S %p')}"

            return dateTime
            # ------------------------------------------------------------------------------------

        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "dateTimeFormat", e, apiEndPoint, errorRequestMethod)
    

    def combineList(payload):
        
        try:
            a = payload['attack_data'].tolist()
            b = payload['target_data'].tolist()
            c = [x + y for x,y in zip(a,b)]
            d = payload['prediction_data'].tolist()
            e = [x + [y] for x,y in zip(c,d)]
            f = []
            if payload['type'] == 'Evasion':
                for i in range(len(e)):
                    if e[i][-1] != e[i][-2]:
                        f.append([(i+2),e[i][-2],e[i][-1],'True'])
                        e[i].append('True')
                    else:
                        e[i].append('False')

                del a,b,c,d
                return e,f
            elif payload['type'] == 'Inference':
                for i in range(len(e)):
                    if e[i][-1] == e[i][-2]:
                        f.append([(i+2),e[i][-2],e[i][-1],'True'])
                        e[i].append('True')
                    else:
                        e[i].append('False')
                del a,b,c,d
                return e,f
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "combineList", e, apiEndPoint, errorRequestMethod)
    

    def checkList(payload):
        try:
            model = payload['model']
            x = payload['original_data']
            adversial_data = payload['adversial_data']
            prediction_list = []

            for i in range(x.shape[0]):
                l=[]
                l.append(x[i])
                l=np.array(l)
                pred=model.predict(l)
                label_benign = np.argmax(pred, axis=1)[0]

                m=[]
                m.append(adversial_data[i])
                m=np.array(m)
                pred=model.predict(m)
                label_adv = np.argmax(pred, axis=1)[0]

                if label_benign == label_adv:
                    continue
                else:
                    prediction_list.append([i, label_benign, label_adv, 'True'])

            del model,x,adversial_data
            return prediction_list
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "checkList", e, apiEndPoint, errorRequestMethod)
    

    def combineReportFile(payload):

        try:
            root_path = os.getcwd()
            root_path = Utility.getcurrentDirectory() + "/database"
            dirList = ["data","model","payload","report"]
            for dir in dirList:
                dirs = root_path + "/" + dir
                if not os.path.exists(dirs):
                    os.mkdir(dirs)
        
            reportList = SecReport.findall({"BatchId":payload['batchid']})
            reportList = Utility.updateReportsList({'reportList':reportList, 'modelName':payload['modelName'],'attackList':payload['attackList']})

            count = 0
            for i in range(len(reportList)):
                count = count + 1
                if(os.getenv("DB_TYPE") == "mongo"):
                    dataContent = FileStoreDb.findOne(reportList[i]["SecReportId"])
                    data = dataContent["data"]
                    attackname = dataContent['fileName'].split('.')[0]
                    fileName = dataContent["fileName"]
                else:
                    dataFile = requests.get(url = fetch_file, params ={"container_name":zip_container,"blob_name":reportList[i]["SecReportId"]})
                    binary_data = dataFile.content
                    temp = io.BytesIO(binary_data)
                    data = temp.read()
                    attackname = reportList[i]["SecReportId"].split('_')[0]
                    content_disposition = dataFile.headers.get('content-disposition')
                    fileName = content_disposition.split(';')[1].split('=')[1].split('.')[0]
                
                attackname = Utility.sanitize_filenameorfoldername(attackname)

                data_path = root_path + "/data"
                data_path = os.path.join(data_path,fileName) 
                if os.path.exists(data_path):                          
                    os.remove(data_path)                                       
                with open(data_path, 'wb') as f:
                    f.write(data)
                
                with zipfile.ZipFile(data_path, 'r') as zip_file:
                    for file_info in zip_file.infolist():
                        if file_info.filename.endswith('.html'):
                            with zip_file.open(file_info.filename) as data_file:
                                data = data_file.read().decode('utf-8')
                                # removing <style-tag> from .html file
                                start_style_tag = data.find('<style>')
                                end_style_tag = data.find('</style>') + len('</style>')
                                if start_style_tag != -1 and end_style_tag != -1:
                                    data_without_style = data[:start_style_tag] + data[end_style_tag:]
                                else:
                                    data_without_style = data
                            with open(os.path.join(payload['report_path'],f"report.html"), 'a', encoding='utf-8') as f:
                                # f.writelines(f"<h2 style='text-align:center; background-color:#8626C3; color:white'>{attackname}_Attack</h2>")
                                f.writelines(data_without_style)
                                # f.writelines('<br><br><br><br><br><br><br>')
                        elif file_info.filename.endswith('.csv'): 
                            with zip_file.open(file_info.filename, 'r') as csv_file:
                                with open(os.path.join(payload['report_path'],f"{attackname}.csv"), 'wb') as f:
                                    shutil.copyfileobj(csv_file, f)   
                        # elif file_info.filename.endswith('.png'): 
                        elif any(file_info.filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']): 
                            # print(file_info.filename)
                            with zip_file.open(file_info.filename, 'r') as image_file:
                                # with open(os.path.join(payload['report_path'],f"{attackname}.png"), 'wb') as f:
                                with open(os.path.join(payload['report_path'],file_info.filename), 'wb') as f:
                                    shutil.copyfileobj(image_file, f)         
                os.remove(data_path)

            del reportList,data
            return count
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "combineReportFile", e, apiEndPoint, errorRequestMethod)
            raise Exception


    def attackDesc(payload):
        try:
            desc = {

                "Poisoning":"""
                            Close implementation of poisoning attack on Support Vector Machines (SVM) by 
                            Biggio et al. 
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1206.6389">Click here</a>
                            </p>
                        """,

                "MembershipInferenceRule":"""
                            A MembershipInferenceRule attack is a type of inference attack that aims 
                            to determine whether a specific data point was used to train a machine 
                            learning model. This attack exploits the differences in the model's 
                            behavior when dealing with data points that are part of the training set 
                            versus those that are not.
                        """,

                "MembershipInferenceBlackBox":"""
                            A MembershipInferenceBlackBox attack is a type of inference attack that 
                            aims to determine whether a specific data point was used to train a 
                            machine learning model, without having access to the model's internal 
                            workings or training data. This attack is considered "black-box" because 
                            the attacker only has access to the model's input-output behavior.
                        """,

                "LabelOnlyDecisionBoundary":"""
                            A LabelOnlyDecisionBoundary attack is a type of membership inference 
                            attack that aims to determine whether a specific data point was used to 
                            train a machine learning model, by analyzing the model's decision boundary 
                            and predicted labels.

                            <p class='content'>
                                Paper-1 link: <a href="https://arxiv.org/abs/2007.14321">Click here</a> (Choquette-Choo et al.)
                            </p>
                            <p class='content'>
                                Paper-2 link: <a href="https://arxiv.org/abs/2007.15528">Click here</a> (Li and Zhang)
                            </p>
                        """,

                "AttributeInferenceWhiteBoxLifestyleDecisionTree":"""
                            An AttributeInferenceWhiteBoxLifestyleDecisionTree attack is a type of 
                            attribute inference attack that aims to infer sensitive attributes of a 
                            target individual from a machine learning model, specifically a decision 
                            tree-based model.

                            Implementation of Fredrikson et al. white box inference attack for decision 
                            trees. Assumes that the attacked feature is discrete or categorical, with 
                            limited number of possible values. For example: a boolean feature. 
                            <p class='content'>
                                Paper link: <a href="https://dl.acm.org/doi/10.1145/2810103.2813677">Click here</a>
                            </p>
                        """,

                "AttributeInferenceWhiteBoxDecisionTree":"""
                            An AttributeInferenceWhiteBoxDecisionTree attack is a type of attribute 
                            inference attack that aims to infer sensitive attributes of a target 
                            individual from a decision tree-based machine learning model.

                            A variation of the method proposed by of Fredrikson et al. in: 
                            <a href="https://dl.acm.org/doi/10.1145/2810103.2813677">Here</a>

                            Assumes the availability of the attacked model's predictions for the samples 
                            under attack, in addition to access to the model itself and the rest of the 
                            feature values. If this is not available, the true class label of the samples 
                            may be used as a proxy. Also assumes that the attacked feature is discrete or 
                            categorical, with limited number of possible values. For example: a boolean 
                            feature. 
                            <p class='content'>
                                Paper link: <a href="https://dl.acm.org/doi/10.1145/2810103.2813677">Click here</a>
                            </p>
                        """,

                "InferenceLabelOnlyGap":"""
                            An InferenceLabelOnlyGap attack is a type of membership inference attack 
                            that aims to infer whether a target individual's data is present in a 
                            machine learning model's training dataset, based on the model's 
                            predictions and the gap between the predicted probabilities of the target 
                            label and the next most likely label.

                            <p class='content'>
                                Paper-1 link: <a href="https://arxiv.org/abs/2007.14321">Click here</a> (Choquette-Choo et al.)
                            </p>
                            <p class='content'>
                                Paper-2 link: <a href="https://arxiv.org/abs/2007.15528">Click here</a> (Li and Zhang)
                            </p>
                        """,

                "AttributeInference":"""
                            An AttributeInference attack is a type of privacy attack that aims to 
                            infer sensitive attributes or information about an individual from a 
                            machine learning model's predictions or outputs.

                            Implementation of a simple black-box attribute inference attack. The idea is 
                            to train a simple neural network to learn the attacked feature from the rest 
                            of the features and the model's predictions. Assumes the availability of the 
                            attacked model's predictions for the samples under attack, in addition to the 
                            rest of the feature values. If this is not available, the true class label of 
                            the samples may be used as a proxy.
                        """,
                
                "CarliniL2Method":"""
                            The CarliniL2Method attack is a type of adversarial attack designed to craft 
                            adversarial examples for machine learning models, particularly those used in
                            image classification. 

                            The goal of this attack is to find a small perturbation to
                            input data causes the model to misclassify the perturbation input while keeping
                            the perturbation within a specified L2 norm constraint.

                            The L_2 optimized attack of Carlini and Wagner (2016). This attack is among 
                            the most effective and should be used among the primary attacks to evaluate 
                            potential defences. A major difference wrt to the original implementation 
                            (<a href="https://github.com/carlini/nn_robust_attacks">Here</a>) is that we use 
                            line search in the optimization of the attack objective. 

                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1608.04644">Click here</a>
                            </p>
                        """,

                "Deepfool":"""
                            A DeepFool attack is a type of adversarial attack that aims to misclassify 
                            a machine learning model's predictions by adding perturbations to the input 
                            data. It is an iterative attack that finds the minimal perturbation 
                            required to change the model's prediction.

                            Implementation of the attack from Moosavi-Dezfooli et al. (2015). 
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1511.04599">Click here</a>
                            </p>
                        """,

                "Boundary":"""
                            In the context of Adversarial Robustness Toolbox(ART), a boundary attack is a
                            type of attack strategy used to find adversarial examples. Adversarial examples
                            are inputs to a machine learning model that are intentionally designed to mis-
                            lead the model, causing it to make incorrect predictions.

                            The goal of a boundary attack is to find a data point close to the decision
                            boundary of the model, where a small perturbation can lead to a different class-
                            ification. This is achieved by iteratively moving the input towards the decision
                            boundary while keeping the perturbation small. The attack aims to find the minimal
                            perturbation needed to change the model's prediction.

                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1712.04248">Click here</a>
                            </p>
                        """,

                "UniversalPerturbation":"""
                            A Universal-Perturbation attack refers to the creation of a single perturbation
                            that, when added to different inputs, causes a model to misclassify them. This
                            perturbation is crafted to be universal in the sense that it can be applied to
                            various inputs, leading to consistent misclassifications.

                            Universal perturbation are partically concerning as they can generalize across
                            a wide range of input samples, making the model vulnerable to misclassifying
                            diverse data points. 
 
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1610.08401">Click here</a> 
                            </p>
                        """,

                "FastGradientMethod":"""
                            In the field of adversarial machine learning, gradient-based attacks are a class
                            of techniques that leverage the gradients of a neural network's loss function with
                            respect to its inputs. The Fast Gradient Method is a well-known example of a gradient
                            based attack. It involves perturbing input data by a small amount in the direction that
                            maximizes the loss, leading to misclassification by the model.

                            This attack was originally implemented by Goodfellow et al. (2015) with the 
                            infinity norm (and is known as the “Fast Gradient Sign Method”). This 
                            implementation extends the attack to other norms, and is therefore called the 
                            Fast Gradient Method. 
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1412.6572">Click here</a>  
                            </p>
                        """,

                "SpatialTransformation":"""
                            A Spatial Transformation Attack is a type of adversarial attack that 
                            targets image classification models by applying spatial transformations 
                            to the input image. The goal is to misclassify the image by exploiting 
                            the model's vulnerability to geometric transformations.

                            Implementation of the spatial transformation attack using translation and 
                            rotation of inputs. The attack conducts black-box queries to the target model 
                            in a grid search over possible translations and rotations to find optimal attack 
                            parameters. 
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1712.02779">Click here</a> 
                            </p>
                        """,

                "Pixel":"""
                            A Pixel Attack is a type of adversarial attack that targets image 
                            classification models by modifying a limited number of pixels in the 
                            input image. The goal is to misclassify the image by exploiting the 
                            model's vulnerability to small, local perturbations.

                            This attack was originally implemented by Vargas et al. (2019). It is 
                            generalisation of One Pixel Attack originally implemented by Su et al. (2019).
                            One Pixel Attack Paper link: <a href="https://arxiv.org/abs/1710.08864"></a> 
                            Pixel Attack 
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1906.06026">Click here</a> 
                            </p>                        
                        """,

                "Wasserstein":"""
                            A Wasserstein Attack is a type of adversarial attack that targets image 
                            classification models by generating perturbations that maximize the 
                            Wasserstein distance between the original and perturbed images. The goal 
                            is to misclassify the image by exploiting the model's vulnerability to 
                            perturbations that affect the image's underlying distribution.

                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1902.07906">Click here</a>
                            </p>
                        """,

                "Square":"""
                            A Square Attack is a type of adversarial attack that targets image 
                            classification models by adding a series of small, square-shaped 
                            perturbations to the input image. The goal is to misclassify the image 
                            by exploiting the model's vulnerability to localized, high-frequency 
                            perturbations.
                
                            This class implements the SquareAttack attack. 
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1912.00049">Click here</a>
                            </p>
                        """,

                "ProjectGradientDescentImage":"""
                            A ProjectGradientDescentImage Attack is a type of adversarial attack that 
                            targets image classification models by generating perturbations that 
                            maximize the model's prediction error while staying within a specified 
                            perturbation budget. The attack uses a projected gradient descent approach 
                            to iteratively update the perturbations, ensuring they remain within the 
                            allowed bounds.

                            The Projected Gradient Descent attack is an iterative method in which, after 
                            each iteration, the perturbation is projected on an lp-ball of specified radius 
                            (in addition to clipping the values of the adversarial sample so that it lies 
                            in the permitted data range). This is the attack proposed by Madry et al. for 
                            adversarial training. 
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1706.06083">Click here</a>
                            </p>
                        """,

                "BasicIterativeMethod":"""
                            A Basic Iterative Method Attack is a type of adversarial attack that 
                            targets image classification models by iteratively applying small 
                            perturbations to the input image. The goal is to misclassify the image 
                            by maximizing the model's prediction error while staying within a 
                            specified perturbation budget.

                            The Basic Iterative Method is the iterative version of FGM and FGSM. 
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1607.02533">Click here</a>
                            </p>
                        """,

                "SaliencyMapMethod":"""
                            A Saliency Map Method Attack is a type of adversarial attack that 
                            targets image classification models by generating perturbations based on 
                            the model's saliency map. The goal is to misclassify the image by 
                            modifying the most salient features that contribute to the model's 
                            prediction.

                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1511.07528">Click here</a>
                            </p>
                        """,

                "IterativeFrameSaliency":"""
                            An Iterative Frame Saliency Attack is a type of adversarial attack 
                            that targets video classification models by iteratively applying 
                            perturbations to the most salient frames. The goal is to misclassify the 
                            video by modifying the frames that contribute most to the model's 
                            prediction.

                            Prioritizes the frame of a sequential input to be adversarially perturbed based 
                            on the saliency score of each frame. 
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1811.11875">Click here</a>
                            </p>
                        """,

                "SimBA":"""
                            SimBA is a query-efficient black-box attack that targets image 
                            classification models by generating adversarial examples using a simple 
                            and efficient algorithm. The goal is to misclassify the image by adding 
                            perturbations that are imperceptible to humans.

                            This class implements the black-box attack SimBA. 
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1905.07121">Click here</a>
                            </p>
                        """,

                "NewtonFool":"""
                            NewtonFool is a powerful and efficient adversarial attack that targets 
                            image classification models by approximating the model's Hessian matrix 
                            using a Newton-like method. The goal is to generate adversarial examples 
                            that are highly effective at misclassifying images.

                            <p class='content'>
                                Paper link: <a href="http://doi.acm.org/10.1145/3134600.3134635">Click here</a>
                            </p>
                        """,

                "ElasticNet":"""
                            ElasticNet is a powerful and efficient adversarial attack that targets 
                            image classification models by leveraging the ElasticNet regularization 
                            technique. The goal is to generate adversarial examples that are highly 
                            effective at misclassifying images while minimizing the perturbation 
                            magnitude.

                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1709.04114">Click here</a>
                            </p>
                        """,

                "QueryEfficient":"""
                            The Query-Efficient attack is a novel adversarial attack designed 
                            specifically for tabular data, such as datasets with categorical and 
                            numerical features. This attack targets machine learning models by 
                            minimizing the number of queries required to generate effective 
                            adversarial examples.

                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1712.07113">Click here</a>
                            </p>
                        """,

                "ProjectedGradientDescentTabular":"""
                            The Projected Gradient Descent (PGD) Tabular Attack is a powerful attack 
                            that targets machine learning models trained on tabular data. It generates 
                            adversarial examples by iteratively applying perturbations to the input 
                            data, maximizing the model's loss while staying within a specified 
                            perturbation budget.

                            The Projected Gradient Descent attack is an iterative method in which, after 
                            each iteration, the perturbation is projected on an lp-ball of specified radius 
                            (in addition to clipping the values of the adversarial sample so that it lies 
                            in the permitted data range). This is the attack proposed by Madry et al. for 
                            adversarial training. 
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1706.06083">Click here</a>
                            </p>
                        """,

                "DecisionTree":"""
                            The DecisionTree Attack is a targeted attack that exploits the decision 
                            boundaries of tree-based models, such as decision trees and random 
                            forests, to generate adversarial examples. It manipulates the input 
                            features to move the data point across the decision boundary, causing the 
                            model to misclassify.

                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1605.07277">Click here</a>
                            </p>
                        """,

                "HopSkipJumpTabular":"""
                            The HopSkipJumpTabular Attack is a query-efficient adversarial attack 
                            designed for tabular data. It leverages a combination of gradient-based 
                            and decision-based methods to generate adversarial examples that mislead 
                            machine learning models.

                            Implementation of the HopSkipJump attack from Jianbo et al. (2019). This is a 
                            powerful black-box attack that only requires final class prediction, and is an 
                            advanced version of the boundary attack. 
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1904.02144">Click here</a>
                            </p>
                        """,

                "ZerothOrderOptimization":"""
                            The Zeroth-Order Optimization Attack is a black-box adversarial attack 
                            that generates perturbations to mislead machine learning models without 
                            accessing their gradients or internal workings. It uses a zeroth-order 
                            optimization method to iteratively update the perturbations, making it a 
                            powerful and query-efficient attack.

                            The black-box zeroth-order optimization attack from Pin-Yu Chen et al. (2018). 
                            This attack is a variant of the C&W attack which uses ADAM coordinate descent 
                            to perform numerical estimation of gradients. 
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1708.03999">Click here</a>
                            </p>
                        """,

                "HopSkipJumpImage":"""
                            The HopSkipJumpImage Attack is a query-efficient adversarial attack 
                            designed to generate perturbed images that mislead image classification 
                            models. It leverages a combination of gradient-based and decision-based 
                            methods to efficiently find adversarial examples.

                            Implementation of the HopSkipJump attack from Jianbo et al. (2019). This is a 
                            powerful black-box attack that only requires final class prediction, and is an 
                            advanced version of the boundary attack. 
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1904.02144">Click here</a>
                            </p>
                        """,

                "QueryEfficientGradientAttackEndPoint":"""
                            The Query-Efficient attack is a novel adversarial attack designed 
                            specifically for tabular data, such as datasets with categorical and 
                            numerical features. This attack targets machine learning models by 
                            minimizing the number of queries required to generate effective 
                            adversarial examples.

                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1712.07113">Click here</a>
                            </p>
                        """,

                "BoundaryAttackEndPoint":"""
                            In the context of Adversarial Robustness Toolbox(ART), a boundary attack is a
                            type of attack strategy used to find adversarial examples. Adversarial examples
                            are inputs to a machine learning model that are intentionally designed to mis-
                            lead the model, causing it to make incorrect predictions.

                            The goal of a boundary attack is to find a data point close to the decision
                            boundary of the model, where a small perturbation can lead to a different class-
                            ification. This is achieved by iteratively moving the input towards the decision
                            boundary while keeping the perturbation small. The attack aims to find the minimal
                            perturbation needed to change the model's prediction.
 
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1712.04248">Click here</a>
                            </p>
                        """,

                "HopSkipJumpAttackEndPoint":"""
                            The HopSkipJumpTabular Attack is a query-efficient adversarial attack 
                            designed for tabular data. It leverages a combination of gradient-based 
                            and decision-based methods to generate adversarial examples that mislead 
                            machine learning models.

                            Implementation of the HopSkipJump attack from Jianbo et al. (2019). This is a 
                            powerful black-box attack that only requires final class prediction, and is an 
                            advanced version of the boundary attack. 
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1904.02144">Click here</a>
                            </p>
                        """,

                "LabelOnlyGapAttackEndPoint":"""
                            An InferenceLabelOnlyGap attack is a type of membership inference attack 
                            that aims to infer whether a target individual's data is present in a 
                            machine learning model's training dataset, based on the model's 
                            predictions and the gap between the predicted probabilities of the target 
                            label and the next most likely label.

                            <p class='content'>
                                Paper-1 link: <a href="https://arxiv.org/abs/2007.14321">Click here</a> (Choquette-Choo et al.)
                            </p>
                            <p class='content'>
                                Paper-2 link: <a href="https://arxiv.org/abs/2007.15528">Click here</a> (Li and Zhang)
                            </p>
                        """,

                "MembershipInferenceBlackBoxRuleBasedAttackEndPoint":"""
                            A MembershipInferenceRule attack is a type of inference attack that aims 
                            to determine whether a specific data point was used to train a machine 
                            learning model. This attack exploits the differences in the model's 
                            behavior when dealing with data points that are part of the training set 
                            versus those that are not.
                        """,

                "LabelOnlyDecisionBoundaryAttackEndPoint":"""
                            A LabelOnlyDecisionBoundary attack is a type of membership inference 
                            attack that aims to determine whether a specific data point was used to 
                            train a machine learning model, by analyzing the model's decision boundary 
                            and predicted labels.

                            <p class='content'>
                                Paper-1 link: <a href="https://arxiv.org/abs/2007.14321">Click here</a> (Choquette-Choo et al.)
                            </p>
                            <p class='content'>
                                Paper-2 link: <a href="https://arxiv.org/abs/2007.15528">Click here</a> (Li and Zhang)
                            </p>
                        """,

                "MembershipInferenceBlackBoxAttackEndPoint":"""
                            A MembershipInferenceBlackBox attack is a type of inference attack that 
                            aims to determine whether a specific data point was used to train a 
                            machine learning model, without having access to the model's internal 
                            workings or training data. This attack is considered "black-box" because 
                            the attacker only has access to the model's input-output behavior.
                        """,

                "VirtualAdversarialMethod":"""
                            The Virtual Adversarial Method is a regularization technique 
                            designed to improve the robustness of machine learning models against 
                            adversarial attacks. It generates virtual adversarial examples during 
                            training, which helps the model to learn robust features and improve its 
                            resistance to attacks.

                            Implementation of a VirtualAdversarialMethod evasion attack. VirtualAdversarialMethod
                            resembles adversarial training, but distinguishes itself in that it determines the 
                            adversarial direction from the model distribution alone without using the label 
                            information, making it applicable to semi-supervised learning.
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1507.00677">Click here</a>
                            </p>
                        """,

                "GeometricDecisionBasedAttack":"""
                            The Geometric Decision-Based Attack is a novel adversarial attack 
                            that exploits the geometric properties of machine learning models to 
                            generate perturbations. It leverages the decision boundary of the model 
                            to craft adversarial examples that are likely to be misclassified.

                            Implementation of a Geometric Decision-Based evasion attack. It is a black-box attack
                            that uses the decision boundary of the model to craft adversarial examples. It is also
                            a query-optimised attack, meaning it uses the minimum number of queries to the model to
                            generate perturbations.
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/2003.06468">Click here</a>
                            </p>                    
                        """,

                "Threshold":"""
                            The Threshold Attack is a type of adversarial attack that generates 
                            perturbations by manipulating the threshold values of machine learning 
                            models. It targets the decision boundary of the model, aiming to 
                            misclassify inputs by pushing them across the threshold.

                            Implementation of a Threshold evasion attack. Threshold
                            validate the dual quality assessment on state-of-the-art neural networks (WideResNet,
                            ResNet, AllConv, DenseNet, NIN, LeNet and CapsNet) as well as adversarial defences for 
                            image classification problem.
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1906.06026">Click here</a>
                            </p>
                        """,

                "Augly":"""
                            This class implements the black-box attack SimBA. 
                            <p class='content'>
                                Paper link: <a href="https://arxiv.org/abs/1905.07121">Click here</a>
                            </p>
                        """
            }

            if payload in desc:
                return desc[payload]
            
            else:
                return ''
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "attackDesc", e, apiEndPoint, errorRequestMethod)

               
    def htmlCssContent(payload):

        try:

            if payload['model_metaData']['dataType'] == 'Tabular':
                
                # .full-page-table {
                #             width: 90%;
                #             height: 50vh;
                #         }
                
                html_data = """
                    <style>
                        body {
                            /* padding: 10px; */
                            font-family: roboto, Arial, sans-serif !important;
                        }

                        .heading-color {
                            /* color: #8626C3; */
                            color: #963596;
                        }

                        .heading-font {
                            /* font-family: math; */
                        }

                        .text-color {
                            color: darkgray;
                        }

                        .heading-margin {
                            padding: 10px;
                            margin: 0px;
                        }

                        .report-container {
                            display: block;
                            /* font-family: Arial, sans-serif; */
                        }

                        .navbar {
                            /* background-color: #8626C3; */
                            background-color: #963596;
                            color: #fff;
                            padding: 12px;
                            text-align: left;
                            font-size: 22px;
                            width: 98%;
                            border-radius: 10px;
                        }

                        .datetime-container {
                            position: fixed;
                            top: 10px;
                            right: 10px;
                            font-size: 14px;
                            padding: 5px 10px;
                        }

                        .report-header {
                            display: block;
                            overflow: hidden;
                            padding: 10px;
                        }

                        .report-header h1 {
                            font-weight: bold;
                            position: relative;
                            font-size: 17px;
                        }

                        .report-header h1::after {
                            content: "";
                            position: absolute;
                            left: 0;
                            bottom: 0;
                            width: 7%;
                            height: 3px;
                            background-color: rgb(28, 160, 242);
                        }

                        .report-body {
                            display: block;
                        }

                        .report-section {
                            display: inline-block;
                            width: 49%;
                            box-sizing: border-box;
                            padding: 10px;
                            vertical-align: top;
                        }

                        .report-section-model {
                            display: inline-block;
                            width: 48%;
                            box-sizing: border-box;
                            margin-top: 0px;
                            vertical-align: top;
                        }

                        .remove-margin {
                            margin: 0px;
                        }

                        .bold-line {
                            border-top: 2px solid rgb(234, 228, 228);
                            font-weight: bold;
                            margin-top: 20px;
                            padding-top: 10px;
                        }

                        .attack-summary {
                            margin-top: 20px;
                            border-collapse: collapse;
                            width: max-content;
                            display: block;
                            overflow-x: auto;
                            white-space: nowrap;
                            margin-bottom: 30px;
                        }

                        .attack-summary th,
                        .attack-summary td {
                            padding: 8px;
                            text-align: left;
                            border-bottom: 1px solid #ddd;
                            min-width: 180px; 
                        }

                        .attack-summary th {
                            /* background-color: #f2f2f2; */
                        }

                        .attack-summary td {
                            color: rgb(124 116 116);
                        }

                        .attack-summary td:nth-child(3),
                        .attack-summary td:nth-child(4),
                        .attack-summary td:nth-child(5) {
                            /* text-align: center; */
                        }

                        .selected-attack {
                            font-weight: bold;
                            color: rgb(100, 232, 100);
                        }

                        .attack-accuracy,
                        .detection-accuracy {
                            display: inline-flex;
                            flex-direction: column;
                            align-items: center;
                            width: 100px;
                            margin-top: 5px;
                        }

                        .attack-accuracy-value,
                        .detection-accuracy-value {
                            font-size: 12px;
                            margin-bottom: 2px;
                        }

                        .attack-accuracy-bar,
                        .detection-accuracy-bar {
                            width: 100%;
                            height: 5px;
                            background-color: #e0e0e0;
                            position: relative;
                        }

                        .attack-accuracy-bar-fill,
                        .detection-accuracy-bar-fill {
                            position: absolute;
                            left: 0;
                            top: 0;
                            height: 100%;
                            background-color: rgb(127, 187, 224);
                        }

                        .attack-header {
                            display: block;
                            overflow: hidden;
                            padding: 10px;
                        }

                        .attack-header h2 {
                            font-weight: bold;
                            position: relative;
                        }

                        .attack-header h2::after {
                            content: "";
                            position: absolute;
                            left: 0;
                            bottom: 0;
                            width: 5%;
                            height: 3px;
                            background-color: rgb(102, 175, 220);
                        }

                        .attack-data-table {
                            margin-top: 20px;
                            border-collapse: collapse;
                            width: max-content;
                            display: block;
                            overflow-x: auto;
                            white-space: nowrap;
                        }

                        .attack-data-table th,
                        .attack-data-table td {
                            padding: 5px;
                            /* text-align: left; */
                            border-bottom: 1px solid #ddd;
                            min-width: 130px;
                        }

                        .attack-data-table th {
                            /* background-color: #f2f2f2; */
                        }

                        .attack-data-table td {
                            color: rgb(124 116 116);
                            /* font-size: 12px; */
                        }

                        .attack-data-table td:nth-child(3),
                        .attack-data-table td:nth-child(4),
                        .attack-data-table td:nth-child(5) {
                            /* text-align: center; */
                        }

                        .attack-data-table-column {
                            /* display: inline-flex;
                            flex-direction: column;
                            align-items: center;
                            width: 100px; */
                            margin-top: 5px;
                        }

                        .attack-data-table-column-value {
                            font-size: 12px;
                            text-align: center;
                            /* margin-bottom: 2px; */
                        }

                        .attack-data {
                            margin-top: 20px;
                            border-collapse: collapse;
                            width: max-content;
                            display: block;
                            overflow-x: auto;
                            white-space: nowrap;
                        }

                        .attack-data th,
                        .attack-data td {
                            padding: 5px;
                            /* text-align: left; */
                            border-bottom: 1px solid #ddd;
                            min-width: 180px; 
                        }

                        .attack-data th {
                            /* background-color: #f2f2f2; */
                        }

                        .attack-data td {
                            color: rgb(124 116 116);
                            text-align: center;
                            /* font-size: 12px; */
                        }

                        .attack-data td:nth-child(3),
                        .attack-data td:nth-child(4),
                        .attack-data td:nth-child(5) {
                            /* text-align: center; */
                        }

                        .graph-container {
                            width: 100%; 
                            height: 560px; 
                        }

                        .graph-container-attack {
                            width: 100%;
                            height: 220px;
                        }

                        .graph-image {
                            max-width: 100%; 
                            max-height: 100%; 
                        }

                        .graph-image-csv {
                            max-width: 100%;
                            max-height: 110%;
                            /* margin: -22px -41px; */
                            margin: -22px -20px;
                        }
                    </style>
                """

                return html_data
            
            elif payload['model_metaData']['dataType'] == 'Image':
            
                html_data = """
                    <style>
                        body{
                            /* padding: 10px; */
                            font-family: roboto, Arial, sans-serif !important;
                        }
                    
                        .heading-color {
                            /* color: #8626C3; */
                            color: #963596;
                        }

                        .heading-font {
                            /* font-family: math; */
                        }

                        .text-color {
                            color: darkgray;
                        }

                        .heading-margin {
                            padding: 10px;
                            margin: 0px;
                        }

                        .report-container {
                            display: block;
                            /* font-family: Arial, sans-serif; */
                        }

                        .navbar {
                            /* background-color: #8626C3; */
                            background-color: #963596;
                            color: #fff;
                            padding: 12px;
                            text-align: left;
                            font-size: 22px;
                            width: 98%;
                            border-radius: 10px;
                        }

                        .datetime-container {
                            position: fixed;
                            top: 10px;
                            right: 10px;
                            font-size: 14px;
                            padding: 5px 10px;
                        }

                        .report-header {
                            display: block;
                            overflow: hidden;
                            padding: 10px;
                        }

                        .report-header h1 {
                            font-weight: bold;
                            position: relative;
                            font-size: 17px;
                        }

                        .report-header h1::after {
                            content: "";
                            position: absolute;
                            left: 0;
                            bottom: 0;
                            width: 7%;
                            height: 3px;
                            background-color: rgb(28, 160, 242);
                        }

                        .report-body {
                            display: block;
                        }

                        .report-section {
                            display: inline-block;
                            width: 49%;
                            box-sizing: border-box;
                            padding: 10px;
                            vertical-align: top;
                        }

                        .report-section-model {
                            display: inline-block;
                            width: 48%;
                            box-sizing: border-box;
                            margin-top: 0px;
                            vertical-align: top;
                        }

                        .remove-margin {
                            margin: 0px;
                        }

                        .bold-line {
                            border-top: 2px solid rgb(234, 228, 228);
                            font-weight: bold;
                            margin-top: 20px;
                            padding-top: 10px;
                        }

                        .attack-summary {
                            margin-top: 20px;
                            border-collapse: collapse;
                            width: max-content;
                            display: block;
                            overflow-x: auto;
                            white-space: nowrap;
                            margin-bottom: 30px;
                        }

                        .attack-summary th,
                        .attack-summary td {
                            padding: 8px;
                            text-align: left;
                            border-bottom: 1px solid #ddd;
                            min-width: 180px; 
                        }

                        .attack-summary th {
                            /* background-color: #f2f2f2; */
                        }

                        .attack-summary td {
                            color: rgb(124 116 116);
                        }

                        .attack-summary td:nth-child(3),
                        .attack-summary td:nth-child(4),
                        .attack-summary td:nth-child(5) {
                            /* text-align: center; */
                        }

                        .selected-attack {
                            font-weight: bold;
                            color: rgb(100, 232, 100);
                        }

                        .attack-accuracy {
                            display: inline-flex;
                            flex-direction: column;
                            align-items: center;
                            width: 100px;
                            margin-top: 5px;
                        }

                        .attack-accuracy-value {
                            font-size: 12px;
                            margin-bottom: 2px;
                        }

                        .attack-accuracy-bar {
                            width: 100%;
                            height: 5px;
                            background-color: #e0e0e0;
                            position: relative;
                        }

                        .attack-accuracy-bar-fill {
                            position: absolute;
                            left: 0;
                            top: 0;
                            height: 100%;
                            background-color: rgb(127, 187, 224);
                        }

                        .attack-header {
                            display: block;
                            overflow: hidden;
                            padding: 10px;
                            margin-bottom: -20px;
                        }

                        .attack-header h2 {
                            font-weight: bold;
                            position: relative;
                        }

                        .attack-header h2::after {
                            content: "";
                            position: absolute;
                            left: 0;
                            bottom: 0;
                            width: 5%;
                            height: 3px;
                            background-color: rgb(102, 175, 220);
                        }

                        .attack-data-table-img {
                            margin-top: 20px;
                            border-collapse: collapse;
                            width: max-content;
                            display: block;
                            overflow-x: auto;
                            white-space: nowrap;
                        }

                        .attack-data-table-img th,
                        .attack-data-table-img td {
                            padding: 5px;
                            /* text-align: left; */
                            border-bottom: 1px solid #ddd;
                            min-width: 250px;
                        }

                        .attack-data-table-img th {
                            /* background-color: #f2f2f2; */
                        }

                        .attack-data-table-img td {
                            color: rgb(124 116 116);
                            /* font-size: 12px; */
                        }

                        .attack-data-table-img td:nth-child(3),
                        .attack-data-table-img td:nth-child(4),
                        .attack-data-table-img td:nth-child(5) {
                            /* text-align: center; */
                        }

                        .attack-data-table-img-column {
                            /* display: inline-flex;
                            flex-direction: column;
                            align-items: center;
                            width: 100px; */
                            margin-top: 5px;
                        }

                        .attack-data-table-img-column-value {
                            font-size: 12px;
                            text-align: center;
                            /* margin-bottom: 2px; */
                        }

                        .attack-data-img {
                            margin-top: 20px;
                            border-collapse: collapse;
                            width: max-content;
                            display: block;
                            overflow-x: auto;
                            white-space: nowrap;
                        }

                        .attack-data-img th,
                        .attack-data-img td {
                            padding: 5px;
                            /* text-align: left; */
                            border-bottom: 1px solid #ddd;
                            min-width: 150px; 
                        }

                        .attack-data-img th {
                            /* background-color: #f2f2f2; */
                        }

                        .attack-data-img td {
                            color: rgb(124 116 116);
                            text-align: center;
                            /* font-size: 12px; */
                            word-break: break-all;
                        }

                        .attack-data-img td:nth-child(3),
                        .attack-data-img td:nth-child(4),
                        .attack-data-img td:nth-child(5) {
                            /* text-align: center; */
                        }

                        .graph-container {
                            width: 100%; 
                            height: 560px; 
                        }

                        .graph-container-attack {
                            width: 100%;
                            height: 220px;
                        }

                        .graph-image {
                            max-width: 100%; 
                            max-height: 100%; 
                        }

                        .graph-image-csv {
                            max-width: 100%;
                            max-height: 110%;
                            margin: -22px -41px;
                        }

                        .graph-image-img {
                            max-width: 130%;
                            max-height: 100%;
                            margin: -9px -25px;
                        }

                        .image-grid {
                            display: flex;
                            flex-wrap: wrap;
                            justify-content: center;
                            gap: 25px;
                        }

                        .image-grid img {
                            width: 440px;
                            height: 240px;
                            object-fit: cover;
                        }

                        a {
                            cursor: pointer;
                            text-decoration: none;
                        }
                    </style>
                """

                return html_data
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "htmlCssContent", e, apiEndPoint, errorRequestMethod)

    
    def htmlContent(payload):

        try:

            if payload['model_metaData']['dataType'] == 'Tabular':

                #706a6a
                # <h3 class="heading-color heading-margin">ATTACK SUMMARY</h3>
                # <table class="full-page-table">

                # <p class="text-color">{Utility.dateTimeFormat(payload['reportTime'])}</p>

                html_data = f"""
                    <body>
                        <div class="report-container">
                            <div class="navbar">
                                <b>INFOSYS RESPONSIBLE AI</b>
                            </div>
                            <div class="datetime-container">
                                <span id="datetime">
                                    <p class="text-color">{payload['reportTime']}</p>
                                </span>
                            </div>
                            <div class="report-header">
                                <h1 class="heading-color">MODEL ROBUSTNESS ASSESSMENT REPORT</h1>
                            </div>
                            <div>
                                <h2 class="heading-color heading-margin">OBJECTIVE</h2>
                            </div>
                            <div class="report-body">
                                <div class="report-section">
                                    <p class="text-color">The report explores various models and their vulnerability to adversarial attacks.
                                        It delves into the methodologies of applying adversarial attacks on these models and provides insightful results
                                        regarding the effectiveness of such attacks. The findings shed light on the models' robustness or
                                        susceptibility, contributing valuable insights to the broader understanding of security in machine
                                        learning applications.</p>
                                </div>
                                <div class="report-section">
                                    <div>
                                        <h3 class="heading-color">MODEL INFORMATION</h3>
                                    </div>
                                    <div class="report-body">
                                        <div class="report-section-model">
                                            <p class="remove-margin">Usecase Name:</p>
                                            <p class="remove-margin">Target DataType:</p>
                                            <p class="remove-margin">Model Api:</p>
                                            <p class="remove-margin">Model End Point:</p>
                                            <p class="remove-margin">Target Output Classes:</p>
                                            <p class="remove-margin">Target Classifier:</p>
                                            <p class="remove-margin">Target ColumnNames:</p>
                                        </div>
                                        <div class="report-section-model">
                                            <p class="remove-margin text-color">{payload['modelName']}</p>
                                            <p class="remove-margin text-color">{payload['model_metaData']['dataType']}</p>
                                            <p class="remove-margin text-color">{payload['model_metaData']['useModelApi']}</p>
                                            <p class="remove-margin text-color">{payload['model_metaData']['modelEndPoint']}</p>
                                            <p class="remove-margin text-color">{payload['model_metaData']['groundTruthClassNames']}</p>
                                            <p class="remove-margin text-color">{payload['model_metaData']['targetClassifier']}</p>
                                            <p class="remove-margin text-color">{payload['model_metaData']['groundTruthClassLabel']}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="bold-line"></div>

                            <div class="attack-summary">
                                <h3 class="heading-color heading-margin">ATTACK SUMMARY</h3>
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Attack Type</th>
                                            <th>Attack Name</th>
                                            <th>Selected Attack</th>
                                            <th>Attack Success</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {payload['rows']}
                                    </tbody>
                                </table>
                            </div>

                        </div>
                    </body>
                """

                if 'graph' in payload:
                    
                    html_data = html_data + f"<body><div class='graph-container'><img src='data:image/png;base64,{payload['graph']}' alt='Attack Graph' class='graph-image'></div></body>"
                    
                    return html_data   
                else:
                    return html_data
                    
            elif payload['model_metaData']['dataType'] == 'Image':

                # <p class="remove-margin">Target Output Classes:</p>
                # <p class="remove-margin text-color">{payload['model_metaData']['targetOutputClasses']}</p>
                # <p class="remove-margin">Target ColumnNames:</p>
                # <p class="remove-margin text-color">{payload['model_metaData']['targetColumnNames']}</p>

                # <p class="text-color">{Utility.dateTimeFormat(payload['reportTime'])}</p>
                
                html_data = f"""
                    <body>
                        <div class="report-container">
                            <div class="navbar">
                                <b>INFOSYS RESPONSIBLE AI</b>
                            </div>
                            <div class="datetime-container">
                                <span id="datetime">
                                    <p class="text-color">{payload['reportTime']}</p>
                                </span>
                            </div>
                            <div class="report-header">
                                <h1 class="heading-color">MODEL ROBUSTNESS ASSESSMENT REPORT</h1>
                            </div>
                            <div>
                                <h2 class="heading-color heading-margin">OBJECTIVE</h2>
                            </div>
                            <div class="report-body">
                                <div class="report-section">
                                    <p class="text-color">The report explores various models and their vulnerability to adversarial attacks.
                                        It delves into the methodologies of applying adversarial attacks on these models and provides insightful results
                                        regarding the effectiveness of such attacks. The findings shed light on the models' robustness or
                                        susceptibility, contributing valuable insights to the broader understanding of security in machine
                                        learning applications.</p>
                                </div>
                                <div class="report-section">
                                    <div>
                                        <h3 class="heading-color">MODEL INFORMATION</h3>
                                    </div>
                                    <div class="report-body">
                                        <div class="report-section-model">
                                            <p class="remove-margin">Usecase Name:</p>
                                            <p class="remove-margin">Target DataType:</p>
                                            <p class="remove-margin">Model Api:</p>
                                            <p class="remove-margin">Model End Point:</p>
                                            
                                            <p class="remove-margin">Target Classifier:</p>
                                            
                                        </div>
                                        <div class="report-section-model">
                                            <p class="remove-margin text-color">{payload['modelName']}</p>
                                            <p class="remove-margin text-color">{payload['model_metaData']['targetDataType']}</p>
                                            <p class="remove-margin text-color">{payload['model_metaData']['useModelApi']}</p>
                                            <p class="remove-margin text-color">{payload['model_metaData']['modelEndPoint']}</p>
                                            
                                            <p class="remove-margin text-color">{payload['model_metaData']['targetClassifier']}</p>
                                            
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="bold-line"></div>

                            <div class="attack-summary">
                                <h3 class="heading-color heading-margin">ATTACK SUMMARY</h3>
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Attack Type</th>
                                            <th>Attack Name</th>
                                            <th>Selected Attack</th>
                                            <th>Attack Success</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {payload['rows']}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </body>
                """

                if 'graph' in payload:
                    
                    html_data = html_data + f"<body><div class='graph-container'><img src='data:image/png;base64,{payload['graph']}' alt='Attack Graph' class='graph-image'></div></body>"
                    return html_data   
                else:
                    return html_data
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "htmlContent", e, apiEndPoint, errorRequestMethod)
       
    
    def htmlMitigationContent(payload):

        try:
            if payload['model_metaData']['dataType'] == 'Tabular':
                
                # <h3 class="heading-color heading-margin">MITIGATION SUMMARY</h3>
                # <table class="full-page-table">
                
                html_data = f"""
                    <body>
                        <div class="attack-summary">
                            <h3 class="heading-color heading-margin">MITIGATION SUMMARY</h3>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Attack Type</th>
                                        <th>Attack Name</th>
                                        <th>Detection Accuracy (LogisticRegression Model)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {payload['mitigation_row']}
                                </tbody>
                            </table>
                        </div>
                        <h3 class="heading-color heading-margin">CONFUSION MATRIX AND CLASSIFICATION REPORT</h3>
                    </body>
                """
                
                return html_data
            
                # html_data = f"""
                #     <div class="attack-summary">
                #         <h3 class="heading-color heading-margin">MITIGATION SUMMARY</h3>
                #         <table class="full-page-table">
                #             <thead>
                #                 <tr>
                #                     <th>Attack Type</th>
                #                     <th>Attack Name</th>
                #                     <th>Detection Accuracy (XGB Model)</th>
                #                 </tr>
                #             </thead>
                #             <tbody>
                #                 {payload['mitigation_row']}
                #             </tbody>
                #         </table>
                #     </div>

                #     <div class="attack-summary">
                #         <h3 class="heading-color heading-margin">DEFENCE MODEL CONFUSION MATRIX</h3>
                #         <table class='full-page-table'>
                #             <tr>
                #                 <th> </th>
                #                 <th>Attack</th>
                #                 <th>Not Attack</th>
                #             </tr>
                #             <tr>
                #                 <th>Attack</th>
                #                 <td>{payload['confusion_matrix'][0][0]}</td>
                #                 <td>{payload['confusion_matrix'][0][1]}</td>
                #             </tr>
                #             <tr>
                #                 <th>Not Attack</th>
                #                 <td>{payload['confusion_matrix'][1][0]}</td>
                #                 <td>{payload['confusion_matrix'][1][1]}</td>
                #             </tr>
                #         </table>
                #     </div>
                # """
                # return html_data
            
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "htmlMitigationContent", e, apiEndPoint, errorRequestMethod)

    
    def htmlAppendixContent(payload):

        try:
            if payload['model_metaData']['dataType'] == 'Tabular':

                html_data = f"""
                        <body>
                            <div class="attack-summary">
                                <h3 class="heading-color heading-margin">APPENDIX</h3>
                                <!-- <h2>Appendix A: Classifier Description and Metrics</h2> -->
                                <!-- <h3>Classifier Overview</h3> -->
                                <!-- <p>The classifier used in this study is a [insert type of classifier, e.g. neural network, decision tree, etc.]. The classifier is designed to [insert brief description of classifier's purpose].</p> -->
                                <h4 class="heading-margin">Classifier Characteristics</h4>
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Term</th>
                                            <th>Definition</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>Classifier</td>
                                            <!-- <td>Definition: A machine learning model that predicts a class label or category for a given input.</td> -->
                                            <!-- <td>Example: A spam classifier that predicts whether an email is spam or not spam.</td> -->
                                            <!-- <td>Types: Binary classifier (e.g., spam vs. not spam), multi-class classifier (e.g., handwritten digit recognition), and multi-label classifier (e.g., text classification with multiple labels).</td> -->
                                            <td>A machine learning model that predicts a class label or category for a given input.</td>
                                        </tr>
                                        <tr>
                                            <td>Evasion</td>
                                            <!-- <td>Definition: A type of attack where an adversary modifies the input data to avoid being detected by a classifier.</td> -->
                                            <!-- <td>Example: An attacker modifies a malware to evade detection by an anti-virus software.</td> -->
                                            <!-- <td>Goal: To create a malicious input that is misclassified as benign by the classifier.</td> -->
                                            <!-- <td>The ability of an attacker to manipulate the input data in order to evade detection by the classifier.</td> -->
                                            <td>A type of attack where an adversary modifies the input data to avoid being detected by a classifier.</td>
                                        </tr>
                                        <tr>
                                            <td>Inference</td>
                                            <!-- <td>Definition: The process of drawing conclusions or making predictions based on input data and a trained model.</td> -->
                                            <!-- <td>Example: Using a trained image classifier to infer the object in an image.</td> -->
                                            <!-- <td>Types: Model inference (e.g., predicting a class label) and model interpretation (e.g., understanding why a model made a prediction).</td> -->
                                            <!-- <td>The process of making predictions or drawing conclusions based on the output of the classifier.</td> -->
                                            <td>The process of making predictions or drawing conclusions based on the output of the classifier.</td>
                                        </tr>
                                        <tr>
                                            <td>Benign</td>
                                            <!-- <td>Definition: A term used to describe input data or instances that are normal, legitimate, or non-malicious.</td> -->
                                            <!-- <td>Example: A benign email that is not spam.</td> -->
                                            <!-- <td>Context: Benign data is often used to train and evaluate machine learning models, and to contrast with malicious or adversarial data.</td> -->
                                            <td>A type of data that is not malicious or threatening.</td>
                                        </tr>
                                        <tr>
                                            <td>Adversarial</td>
                                            <!-- <td>Definition: A term used to describe input data or instances that are malicious, manipulated, or intentionally crafted to deceive or mislead a machine learning model.</td> -->
                                            <!-- <td>Example: An adversarial image that is specifically designed to be misclassified by an image classifier.</td> -->
                                            <!-- <td>Types: Adversarial attacks (e.g., evasion, poisoning), adversarial examples (e.g., manipulated images), and adversarial training (e.g., training a model on adversarial examples).</td> -->
                                            <td>A type of data that is specifically designed to evade or manipulate the classifier.</td>
                                        </tr>
                                    </tbody>
                                </table><br>
                                <h4 class="heading-margin">Performance Metrics</h4>
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Metric</th>
                                            <th>Description</th>
                                            <th>Formula</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>Detection Accuracy</td>
                                            <!-- <td>The proportion of correctly classified instances.</td> -->
                                            <td>The proportion of correctly classified instances among all instances, including both positive and negative classes.</td>
                                            <!-- <td>Interpretation: A high detection accuracy indicates that the classifier is good at distinguishing between positive and negative instances.</td> -->
                                            <td>(TP + TN) / (TP + TN + FP + FN)</td>
                                        </tr>
                                        <tr>
                                            <td>Mean Difference/Mean Absolute Value</td>
                                            <!-- <td>The average difference between the predicted and actual values.</td> -->
                                            <td>The average difference between the predicted values and the actual values.</td>
                                            <!-- <td>Interpretation: A low mean difference indicates that the predicted values are close to the actual values, suggesting a good fit of the model.</td> -->
                                            <!-- <td>(Σ(y_pred - y_true)) / n</td> -->
                                            <td>(1/n) * ∑(Predicted - Actual)</td>
                                        </tr>
                                        <tr>
                                            <td>Precision</td>
                                            <!-- <td>The proportion of true positives among all positive predictions.</td> -->
                                            <td>Proportion of true positives among all positive predictions</td>
                                            <!-- <td>Interpretation: A high precision means that most of the positive predictions made by the classifier are correct.</td> -->
                                            <td>TP / (TP + FP)</td>
                                        </tr>
                                        <tr>
                                            <td>Recall</td>
                                            <!-- <td>The proportion of true positives among all actual positive instances.</td> -->
                                            <td>Proportion of true positives among all actual positive instances</td>
                                            <!-- <td>Interpretation: A high recall means that the classifier is able to detect most of the actual positive instances.</td> -->
                                            <td>TP / (TP + FN)</td>
                                        </tr>
                                        <tr>
                                            <td>F1 Score</td>
                                            <!-- <td>The harmonic mean of precision and recall.</td> -->
                                            <td>Harmonic mean of precision and recall</td>
                                            <!-- <td>Interpretation: The F1 score provides a balanced measure of both precision and recall. A high F1 score means that the classifier has a good balance between precision and recall.</td> -->
                                            <td>2 * (Precision * Recall) / (Precision + Recall)</td>
                                        </tr>
                                        <tr>
                                            <td>Specificity</td>
                                            <td>Proportion of true negatives among all actual negative instances</td>
                                            <!-- <td>Interpretation: A high specificity means that the classifier is able to correctly classify most of the actual negative instances.</td> -->
                                            <td>TN / (TN + FP)</td>
                                        </tr>
                                        <tr>
                                            <td>Balanced Accuracy</td>
                                            <td>Average of recall and specificity</td>
                                            <!-- <td>Interpretation: The balanced accuracy provides a more nuanced measure of the classifier's performance, especially when the classes are imbalanced.</td> -->
                                            <td>(Specificity + Recall) / 2</td>
                                        </tr>
                                        <tr>
                                            <td>False Positive Rate(FPR)</td>
                                            <td>The proportion of true positives among all actual positive instances.</td>
                                            <!-- <td>Interpretation: A low FPR indicates that the classifier is good at avoiding false alarms or false detections.</td> -->
                                            <td>FP / (FP + TN)</td>
                                        </tr>
                                        <tr>
                                            <td>Support</td>
                                            <td>Number of actual instances for each class</td>
                                            <!-- <td>Interpretation: The support provides an idea of the number of instances in each class, which can be useful for understanding the classifier's performance.</td> -->
                                            <td>TP + FN</td>
                                        </tr>
                                        <tr>
                                            <td>Macro Average</td>
                                            <!-- <td>Definition: A method of calculating the average of a metric (e.g., precision, recall, F1-score) across multiple classes, where each class is treated equally.</td> -->
                                            <!-- <td>Formula: Macro Average = (Sum of metric values for each class) / Number of classes</td> -->
                                            <!-- <td>Example: If we have a classification problem with 3 classes (A, B, and C), and we want to calculate the macro F1-score, we would calculate the F1-score for each class separately and then take the average of the three F1-scores.</td> -->
                                            <!-- <td>Macro average is useful when:
                                                All classes are equally important
                                                We want to give equal weight to each class, regardless of the number of instances in each class
                                                We want to evaluate the model's performance on each class individually
                                            </td> -->
                                            <td>A method of calculating the average of a metric (e.g., precision, recall, F1-score) across multiple classes, where each class is treated equally.</td>
                                            <td>(Sum of metric values for each class) / Number of classes</td>
                                        </tr>
                                        <tr>
                                            <td>Weighted Average</td>
                                            <!-- <td>Definition: A method of calculating the average of a metric (e.g., precision, recall, F1-score) across multiple classes, where each class is weighted according to its importance or frequency.</td> -->
                                            <!-- <td>Formula: Weighted Average = (Sum of (metric value for each class * weight for each class)) / Sum of weights</td> -->
                                            <!-- <td>Example: If we have a classification problem with 3 classes (A, B, and C), and we want to calculate the weighted F1-score, we would assign weights to each class based on their importance or frequency (e.g., class A: 0.4, class B: 0.3, class C: 0.3) and then calculate the weighted average of the F1-scores.</td> -->
                                            <!-- <td>Weighted average is useful when:
                                                Some classes are more important than others
                                                We want to give more weight to classes with more instances or higher importance
                                                We want to evaluate the model's performance on a specific class or group of classes
                                            </td> -->
                                            <td>A method of calculating the average of a metric (e.g., precision, recall, F1-score) across multiple classes, where each class is weighted according to its importance or frequency.</td>
                                            <td>(Sum of (metric value for each class * weight for each class)) / Sum of weights</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </body>
                    """
                
                return html_data
            
            elif payload['model_metaData']['dataType'] == 'Image':

                html_data = f"""
                        <body>
                            <div class="attack-summary">
                                <h3 class="heading-color heading-margin">APPENDIX</h3>
                                <!-- <h2>Appendix A: Classifier Description and Metrics</h2> -->
                                <!-- <h3>Classifier Overview</h3> -->
                                <!-- <p>The classifier used in this study is a [insert type of classifier, e.g. neural network, decision tree, etc.]. The classifier is designed to [insert brief description of classifier's purpose].</p> -->
                                <h4 class="heading-margin">Classifier Characteristics</h4>
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Term</th>
                                            <th>Definition</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>Classifier</td>
                                            <!-- <td>Definition: A machine learning model that predicts a class label or category for a given input.</td> -->
                                            <!-- <td>Example: A spam classifier that predicts whether an email is spam or not spam.</td> -->
                                            <!-- <td>Types: Binary classifier (e.g., spam vs. not spam), multi-class classifier (e.g., handwritten digit recognition), and multi-label classifier (e.g., text classification with multiple labels).</td> -->
                                            <td>A machine learning model that predicts a class label or category for a given input.</td>
                                        </tr>
                                        <tr>
                                            <td>Evasion</td>
                                            <!-- <td>Definition: A type of attack where an adversary modifies the input data to avoid being detected by a classifier.</td> -->
                                            <!-- <td>Example: An attacker modifies a malware to evade detection by an anti-virus software.</td> -->
                                            <!-- <td>Goal: To create a malicious input that is misclassified as benign by the classifier.</td> -->
                                            <!-- <td>The ability of an attacker to manipulate the input data in order to evade detection by the classifier.</td> -->
                                            <td>A type of attack where an adversary modifies the input data to avoid being detected by a classifier.</td>
                                        </tr>
                                        <tr>
                                            <td>Inference</td>
                                            <!-- <td>Definition: The process of drawing conclusions or making predictions based on input data and a trained model.</td> -->
                                            <!-- <td>Example: Using a trained image classifier to infer the object in an image.</td> -->
                                            <!-- <td>Types: Model inference (e.g., predicting a class label) and model interpretation (e.g., understanding why a model made a prediction).</td> -->
                                            <!-- <td>The process of making predictions or drawing conclusions based on the output of the classifier.</td> -->
                                            <td>The process of making predictions or drawing conclusions based on the output of the classifier.</td>
                                        </tr>
                                        <tr>
                                            <td>Benign</td>
                                            <!-- <td>Definition: A term used to describe input data or instances that are normal, legitimate, or non-malicious.</td> -->
                                            <!-- <td>Example: A benign email that is not spam.</td> -->
                                            <!-- <td>Context: Benign data is often used to train and evaluate machine learning models, and to contrast with malicious or adversarial data.</td> -->
                                            <td>A type of data that is not malicious or threatening.</td>
                                        </tr>
                                        <tr>
                                            <td>Adversarial</td>
                                            <!-- <td>Definition: A term used to describe input data or instances that are malicious, manipulated, or intentionally crafted to deceive or mislead a machine learning model.</td> -->
                                            <!-- <td>Example: An adversarial image that is specifically designed to be misclassified by an image classifier.</td> -->
                                            <!-- <td>Types: Adversarial attacks (e.g., evasion, poisoning), adversarial examples (e.g., manipulated images), and adversarial training (e.g., training a model on adversarial examples).</td> -->
                                            <td>A type of data that is specifically designed to evade or manipulate the classifier.</td>
                                        </tr>
                                    </tbody>
                                </table><br>
                            </div>
                        </body>
                    """
                
                return html_data
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "htmlAppendixContent", e, apiEndPoint, errorRequestMethod)
    
    
    def htmlCssContentReport(payload):

        try:

            if payload['type'] == 'Tabular':

                # color: rgb(28, 160, 242);
                # .full-page-table {
                #         width: 90%;
                #         height: 50vh;
                #     }
                
                html_data = """
                <style>
                    body{
                        /* padding: 10px; */
                        font-family: roboto, Arial, sans-serif !important;
                    }

                    .heading-color {
                        color: #8626C3;
                    }

                    .heading-font {
                        /* font-family: math; */
                    }

                    .text-color {
                        color: darkgray;
                    }

                    .heading-margin {
                        padding: 10px;
                        margin: 0px;
                    }

                    .report-container {
                        display: block;
                        /* font-family: Arial, sans-serif; */
                    }

                    .datetime-container {
                        position: fixed;
                        top: 10px;
                        right: 10px;
                        font-size: 14px;
                        padding: 5px 10px;
                    }

                    .report-header {
                        display: block;
                        overflow: hidden;
                        padding: 10px;
                    }

                    .report-header h1 {
                        font-weight: bold;
                        position: relative;
                        font-size: 17px;
                    }

                    .report-header h1::after {
                        content: "";
                        position: absolute;
                        left: 0;
                        bottom: 0;
                        width: 7%;
                        height: 3px;
                        background-color: rgb(28, 160, 242);
                    }

                    .report-body {
                        display: block;
                    }

                    .report-section {
                        display: inline-block;
                        width: 49%;
                        box-sizing: border-box;
                        padding: 10px;
                        vertical-align: top;
                    }

                    .report-section-model {
                        display: inline-block;
                        width: 48%;
                        box-sizing: border-box;
                        margin-top: 0px;
                        vertical-align: top;
                    }

                    .remove-margin {
                        margin: 0px;
                    }

                    .bold-line {
                        border-top: 2px solid rgb(234, 228, 228);
                        font-weight: bold;
                        margin-top: 20px;
                        padding-top: 10px;
                    }

                    .attack-summary {
                        margin-top: 20px;
                        border-collapse: collapse;
                        width: max-content;
                        display: block;
                        overflow-x: auto;
                        white-space: nowrap;
                        margin-bottom: 30px;
                    }

                    .attack-summary th,
                    .attack-summary td {
                        padding: 8px;
                        text-align: left;
                        border-bottom: 1px solid #ddd;
                        min-width: 180px; 
                    }

                    .attack-summary th {
                        /* background-color: #f2f2f2; */
                    }

                    .attack-summary td {
                        color: rgb(124 116 116);
                    }

                    .attack-summary td:nth-child(3),
                    .attack-summary td:nth-child(4),
                    .attack-summary td:nth-child(5) {
                        /* text-align: center; */
                    }

                    .selected-attack {
                        font-weight: bold;
                        color: rgb(100, 232, 100);
                    }

                    .attack-accuracy,
                    .detection-accuracy {
                        display: inline-flex;
                        flex-direction: column;
                        align-items: center;
                        width: 100px;
                        margin-top: 5px;
                    }

                    .attack-accuracy-value,
                    .detection-accuracy-value {
                        font-size: 12px;
                        margin-bottom: 2px;
                    }

                    .attack-accuracy-bar,
                    .detection-accuracy-bar {
                        width: 100%;
                        height: 5px;
                        background-color: #e0e0e0;
                        position: relative;
                    }

                    .attack-accuracy-bar-fill,
                    .detection-accuracy-bar-fill {
                        position: absolute;
                        left: 0;
                        top: 0;
                        height: 100%;
                        background-color: rgb(127, 187, 224);
                    }

                    .attack-header {
                        display: block;
                        overflow: hidden;
                        padding: 10px;
                    }

                    .attack-header h2 {
                        font-weight: bold;
                        position: relative;
                    }

                    .attack-header h2::after {
                        content: "";
                        position: absolute;
                        left: 0;
                        bottom: 0;
                        width: 5%;
                        height: 3px;
                        background-color: rgb(102, 175, 220);
                    }

                    .attack-data-table {
                        margin-top: 20px;
                        border-collapse: collapse;
                        width: max-content;
                        display: block;
                        overflow-x: auto;
                        white-space: nowrap;
                    }

                    .attack-data-table th,
                    .attack-data-table td {
                        padding: 5px;
                        /* text-align: left; */
                        border-bottom: 1px solid #ddd;
                        min-width: 130px;
                    }

                    .attack-data-table th {
                        /* background-color: #f2f2f2; */
                    }

                    .attack-data-table td {
                        color: rgb(124 116 116);
                        /* font-size: 12px; */
                    }

                    .attack-data-table td:nth-child(3),
                    .attack-data-table td:nth-child(4),
                    .attack-data-table td:nth-child(5) {
                        /* text-align: center; */
                    }

                    .attack-data-table-column {
                        /* display: inline-flex;
                        flex-direction: column;
                        align-items: center;
                        width: 100px; */
                        margin-top: 5px;
                    }

                    .attack-data-table-column-value {
                        font-size: 12px;
                        text-align: center;
                        /* margin-bottom: 2px; */
                    }

                    .attack-data {
                        margin-top: 20px;
                        border-collapse: collapse;
                        width: max-content;
                        display: block;
                        overflow-x: auto;
                        white-space: nowrap;
                    }

                    .attack-data th,
                    .attack-data td {
                        padding: 5px;
                        /* text-align: left; */
                        border-bottom: 1px solid #ddd;
                        min-width: 180px; 
                    }

                    .attack-data th {
                        /* background-color: #f2f2f2; */
                    }

                    .attack-data td {
                        color: rgb(124 116 116);
                        text-align: center;
                        /* font-size: 12px; */
                    }

                    .attack-data td:nth-child(3),
                    .attack-data td:nth-child(4),
                    .attack-data td:nth-child(5) {
                        /* text-align: center; */
                    }

                    .graph-container {
                        width: 100%; 
                        height: 560px; 
                    }

                    .graph-container-attack {
                        width: 100%;
                        height: 220px;
                    }

                    .graph-image {
                        max-width: 100%; 
                        max-height: 100%; 
                    }

                    .graph-image-csv {
                        max-width: 100%;
                        max-height: 110%;
                        /* margin: -22px -41px; */
                        margin: -22px -20px;
                    }
                </style>
            """

                return html_data
            
            elif payload['type'] == 'Image':
                
                html_data = """
                <style>
                    body{
                        /* padding: 10px; */
                        font-family: roboto, Arial, sans-serif !important;
                    }

                    .heading-color {
                        color: #8626C3;
                    }

                    .heading-font {
                        /* font-family: math; */
                    }

                    .text-color {
                        color: darkgray;
                    }

                    .heading-margin {
                        padding: 10px;
                        margin: 0px;
                    }

                    .report-container {
                        display: block;
                        /* font-family: Arial, sans-serif; */
                    }

                    .datetime-container {
                        position: fixed;
                        top: 10px;
                        right: 10px;
                        font-size: 14px;
                        padding: 5px 10px;
                    }

                    .report-header {
                        display: block;
                        overflow: hidden;
                        padding: 10px;
                    }

                    .report-header h1 {
                        font-weight: bold;
                        position: relative;
                        font-size: 17px;
                    }

                    .report-header h1::after {
                        content: "";
                        position: absolute;
                        left: 0;
                        bottom: 0;
                        width: 7%;
                        height: 3px;
                        background-color: rgb(28, 160, 242);
                    }

                    .report-body {
                        display: block;
                    }

                    .report-section {
                        display: inline-block;
                        width: 49%;
                        box-sizing: border-box;
                        padding: 10px;
                        vertical-align: top;
                    }

                    .report-section-model {
                        display: inline-block;
                        width: 48%;
                        box-sizing: border-box;
                        margin-top: 0px;
                        vertical-align: top;
                    }

                    .remove-margin {
                        margin: 0px;
                    }

                    .bold-line {
                        border-top: 2px solid rgb(234, 228, 228);
                        font-weight: bold;
                        margin-top: 20px;
                        padding-top: 10px;
                    }

                    .attack-summary {
                        margin-top: 20px;
                        border-collapse: collapse;
                        width: max-content;
                        display: block;
                        overflow-x: auto;
                        white-space: nowrap;
                        margin-bottom: 30px;
                    }

                    .attack-summary th,
                    .attack-summary td {
                        padding: 8px;
                        text-align: left;
                        border-bottom: 1px solid #ddd;
                        min-width: 180px; 
                    }

                    .attack-summary th {
                        /* background-color: #f2f2f2; */
                    }

                    .attack-summary td {
                        color: rgb(124 116 116);
                    }

                    .attack-summary td:nth-child(3),
                    .attack-summary td:nth-child(4),
                    .attack-summary td:nth-child(5) {
                        /* text-align: center; */
                    }

                    .selected-attack {
                        font-weight: bold;
                        color: rgb(100, 232, 100);
                    }

                    .attack-accuracy {
                        display: inline-flex;
                        flex-direction: column;
                        align-items: center;
                        width: 100px;
                        margin-top: 5px;
                    }

                    .attack-accuracy-value {
                        font-size: 12px;
                        margin-bottom: 2px;
                    }

                    .attack-accuracy-bar {
                        width: 100%;
                        height: 5px;
                        background-color: #e0e0e0;
                        position: relative;
                    }

                    .attack-accuracy-bar-fill {
                        position: absolute;
                        left: 0;
                        top: 0;
                        height: 100%;
                        background-color: rgb(127, 187, 224);
                    }

                    .attack-header {
                        display: block;
                        overflow: hidden;
                        padding: 10px;
                        margin-bottom: -20px;
                    }

                    .attack-header h2 {
                        font-weight: bold;
                        position: relative;
                    }

                    .attack-header h2::after {
                        content: "";
                        position: absolute;
                        left: 0;
                        bottom: 0;
                        width: 5%;
                        height: 3px;
                        background-color: rgb(102, 175, 220);
                    }

                    .attack-data-table-img {
                        margin-top: 20px;
                        border-collapse: collapse;
                        width: max-content;
                        display: block;
                        overflow-x: auto;
                        white-space: nowrap;
                    }

                    .attack-data-table-img th,
                    .attack-data-table-img td {
                        padding: 5px;
                        /* text-align: left; */
                        border-bottom: 1px solid #ddd;
                        min-width: 250px;
                    }

                    .attack-data-table-img th {
                        /* background-color: #f2f2f2; */
                    }

                    .attack-data-table-img td {
                        color: rgb(124 116 116);
                        /* font-size: 12px; */
                    }

                    .attack-data-table-img td:nth-child(3),
                    .attack-data-table-img td:nth-child(4),
                    .attack-data-table-img td:nth-child(5) {
                        /* text-align: center; */
                    }

                    .attack-data-table-img-column {
                        /* display: inline-flex;
                        flex-direction: column;
                        align-items: center;
                        width: 100px; */
                        margin-top: 5px;
                    }

                    .attack-data-table-img-column-value {
                        font-size: 12px;
                        text-align: center;
                        /* margin-bottom: 2px; */
                    }

                    .attack-data-img {
                        margin-top: 20px;
                        border-collapse: collapse;
                        width: max-content;
                        display: block;
                        overflow-x: auto;
                        white-space: nowrap;
                    }

                    .attack-data-img th,
                    .attack-data-img td {
                        padding: 5px;
                        /* text-align: left; */
                        border-bottom: 1px solid #ddd;
                        min-width: 150px; 
                    }

                    .attack-data-img th {
                        /* background-color: #f2f2f2; */
                    }

                    .attack-data-img td {
                        color: rgb(124 116 116);
                        text-align: center;
                        /* font-size: 12px; */
                        word-break: break-all;
                    }

                    .attack-data-img td:nth-child(3),
                    .attack-data-img td:nth-child(4),
                    .attack-data-img td:nth-child(5) {
                        /* text-align: center; */
                    }

                    .graph-container {
                        width: 100%; 
                        height: 560px; 
                    }

                    .graph-container-attack {
                        width: 100%;
                        height: 220px;
                    }

                    .graph-image {
                        max-width: 100%; 
                        max-height: 100%; 
                    }

                    .graph-image-csv {
                        max-width: 100%;
                        max-height: 110%;
                        margin: -22px -41px;
                    }

                    .graph-image-img {
                        max-width: 130%;
                        max-height: 100%;
                        margin: -9px -25px;
                    }

                    .image-grid {
                        display: flex;
                        flex-wrap: wrap;
                        justify-content: center;
                        gap: 25px;
                    }

                    .image-grid img {
                        width: 440px;
                        height: 240px;
                        object-fit: cover;
                    }

                    a {
                        cursor: pointer;
                        text-decoration: none;
                    }
                </style>
            """

                return html_data
            
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "htmlCssContentReport", e, apiEndPoint, errorRequestMethod)
    
    
    def htmlContentReport(payload):
        
        try:

            if payload['type'] == 'Tabular':

                # <div class="attack-data">
                #     <h3 class="heading-color heading-margin">Adversial input used for attack and Adversial output generated</h3>
                #     <table>
                #         <thead>
                #             <tr>
                #                 <th>Sample Index</th>
                #                 <th>Expected Value</th>
                #                 <th>Predicated Value</th>
                #                 <th>Success</th>
                #             </tr>
                #         </thead>
                #         <tbody>
                #             {payload['attack_ipop_row']}
                #         </tbody>
                #     </table>
                # </div>

                if payload['column_graph_data']:
                
                    html_data = f"""
                        <body>
                            <div class="report-container">

                                <div class="attack-header">
                                    <h2 class="heading-color">{payload['attackName']}_Attack</h2>
                                </div>

                                <div class="report-body">
                                    <div class="report-section">
                                        <h3 class="heading-color">Description</h3>
                                        <p class="text-color">{Utility.attackDesc(payload['attackName'])}</p>
                                    </div>
                                    <div class="report-section">
                                        <h3 class="heading-color">Visualization for Prediction Data</h3>
                                        {payload['graph_html']}
                                    </div>
                                </div>
                            </div>
                            <div class="attack-data-table">
                                <h3 class="heading-color heading-margin">Attack Status</h3>
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Attack ID</th>
                                            <th>Model Name</th>
                                            <th>Attack Name</th>
                                            <th>Status</th>
                                            <th>Mean Difference</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {payload['attack_status_row']}
                                    </tbody>
                                </table>
                            </div>
                            <div class="attack-data">
                                <h3 class="heading-color heading-margin">Attacked Columns</h3>
                                {payload['column_graph_data']}
                            </div>
                        </body>
                    """
                    
                    return html_data
                
                else:

                    html_data = f"""
                        <body>
                            <div class="report-container">

                                <div class="attack-header">
                                    <h2 class="heading-color">{payload['attackName']}_Attack</h2>
                                </div>

                                <div class="report-body">
                                    <div class="report-section">
                                        <h3 class="heading-color">Description</h3>
                                        <p class="text-color">{Utility.attackDesc(payload['attackName'])}</p>
                                    </div>
                                    <div class="report-section">
                                        <h3 class="heading-color">Visualization for Prediction Data</h3>
                                        {payload['graph_html']}
                                    </div>
                                </div>
                            </div>
                            <div class="attack-data-table">
                                <h3 class="heading-color heading-margin">Attack Status</h3>
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Attack ID</th>
                                            <th>Model Name</th>
                                            <th>Attack Name</th>
                                            <th>Status</th>
                                            <th>Mean Difference</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {payload['attack_status_row']}
                                    </tbody>
                                </table>
                            </div>                           
                        </body>
                    """
                    
                    return html_data
            
            elif payload['type'] == 'Image':
                
                if payload['graph_html']:
                    
                    # <h3 class="heading-color heading-margin">Adversial input used for attack and Adversial output generated</h3>
                    html_data = f"""
                        <body>
                            <div class="report-container">

                                <div class="attack-header">
                                    <h2 class="heading-color">{payload['attackName']}_Attack</h2>
                                </div>

                                <div class="report-body">
                                    <div class="heading-margin">
                                        <h3 class="heading-color">Description</h3>
                                        <p class="text-color">{Utility.attackDesc(payload['attackName'])}</p>
                                    </div>                 
                                </div>

                                <div class="report-body">
                                    <h3 class="heading-color heading-margin">Attack Visualization</h3>
                                    <div class="image-grid">
                                        {payload['graph_html']}
                                    </div>                 
                                </div>

                            </div>

                            <div class="attack-data-img">
                                <h3 class="heading-color heading-margin">Attack Analysis</h3>
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Image Path</th>
                                            <th>Expected Value</th>
                                            <th>Predicated Value</th>
                                            <th>Confidence Score</th>
                                            <th>Success</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {payload['attack_ipop_row']}
                                    </tbody>
                                </table>
                            </div>
                        </body>
                    """  

                    # <div class="attack-data-table-img">
                    # <h3 class="heading-color heading-margin">Attack Status</h3>
                    #     <table>
                    #         <thead>
                    #             <tr>
                    #                 <th>Base Model Name</th>
                    #                 <th>Actual Labels</th>
                    #                 <th>Confidence Score</th>
                    #             </tr>
                    #         </thead>
                    #         <tbody>
                    #             {payload['attack_status_row']}
                    #         </tbody>
                    #     </table>
                    # </div>       
                    
                    return html_data
                
                else:

                    # <h3 class="heading-color heading-margin">Adversial input used for attack and Adversial output generated</h3> 
                    html_data = f"""
                        <body>
                            <div class="report-container">

                                <div class="attack-header">
                                    <h2 class="heading-color">{payload['attackName']}_Attack</h2>
                                </div>

                                <div class="report-body">
                                    <div class="heading-margin">
                                        <h3 class="heading-color">Description</h3>
                                        <p class="text-color">{Utility.attackDesc(payload['attackName'])}</p>
                                    </div>                 
                                </div>

                            </div>

                            <div class="attack-data-img">
                                <h3 class="heading-color heading-margin">Attack Analysis</h3>
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Image Path</th>
                                            <th>Expected Value</th>
                                            <th>Predicated Value</th>
                                            <th>Confidence Score</th>
                                            <th>Success</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {payload['attack_ipop_row']}
                                    </tbody>
                                </table>
                            </div>
                        </body>
                    """  
    
                    return html_data
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "htmlContentReport", e, apiEndPoint, errorRequestMethod)
    
    
    def htmlToPdfWithWatermark(payload):
        try:
            # convert html file into pdf file
            html_path = os.path.join(payload['folder_path'],"report.html")
            pdf_path = os.path.join(payload['folder_path'],"report.pdf")
            option = {
                'page-size':'A4',
                'orientation':'Portrait',
                # 'margin-top':'0.75in',
                # 'margin-right':'0.75in',
                # 'margin-bottom':'0.75in',
                # 'margin-left':'0.75in',
                'encoding':'UTF-8',
                'no-outline':None,
                'footer-center':'Page [page] of [toPage]',
            }
            pdfkit.from_file(html_path, output_path=pdf_path, options=option)

            # create watermark.pdf file
            watermark_path = os.path.join(payload['folder_path'], 'watermark.pdf')
            # txt = 'Infosys'
            txt = ''
            c = canvas.Canvas(watermark_path, pagesize=letter)
            c.setFont('Helvetica', 50)
            c.setFillColorRGB(0.53,0.15,0.76)
            c.setFillAlpha(0.13)
            c.rotate(45)
            c.drawString(400, 8, txt)
            c.save()

            # adding watermark in each page of report.pdf file
            combine_pdf = os.path.join(payload['folder_path'], 'report.pdf')
            modify_pdf = os.path.join(payload['folder_path'], 'report.pdf')

            with open(combine_pdf, 'rb') as pdf_file, open(watermark_path, 'rb') as watermark_file:
                pdf_reader = PdfReader(pdf_file)
                watermark_reader = PdfReader(watermark_file)
                watermark_page = watermark_reader.pages[0]
                pdf_writer = PdfWriter()

                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page.merge_page(watermark_page)
                    pdf_writer.add_page(page)

                with open(modify_pdf, 'wb') as out_file:
                    pdf_writer.write(out_file)
            os.remove(watermark_path)

            return 
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "htmlToPdfWithWatermark", e, apiEndPoint, errorRequestMethod)
    

    def generateDefenceAccuracy(payload):

        try:
            payload_folder_path = Utility.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,payload["modelName"] + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            for filename in os.listdir(payload['folder_path']):
                if filename.endswith('.pkl'):
                    # load model file
                    model_file = os.path.join(payload['folder_path'], filename)
                    with open(model_file, 'rb') as file:
                        # load_model = pickle.load(file)
                        load_model = Utility.safe_load_from_file(file)

                    # reading attack dataset 
                    df = pd.read_csv(payload['csv_path'])
                    df = df[df[df.columns[-1]] == True]
                    df.drop(Output_column,axis=1,inplace=True)
                    df.drop(columns=df.columns[-2:], axis=1, inplace=True)
                    df.insert(df.shape[1],"Attack",[1 for i in range(df.shape[0])])
                    # calculate model accuarcy base on current dataset
                    X = df.loc[:,df.columns!="Attack"]
                    Y = df["Attack"]
                    y_pred = load_model.predict(X)
                    model_accuracy = accuracy_score(Y, y_pred)
                    # print('model_accuracy',model_accuracy)

                    del df,X,Y,y_pred
                    return model_accuracy
        except Exception as exc:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "generateDefenceAccuracy", exc, apiEndPoint, errorRequestMethod)
            raise Exception
        

    def confusionMatrix(payload):

        try:
            payload_folder_path = Utility.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,payload["modelName"] + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            for filename in os.listdir(payload['folder_path']):
                if filename.endswith('.pkl'):
                    # load model file
                    model_file = os.path.join(payload['folder_path'], filename)
                    with open(model_file, 'rb') as file:
                        # load_model = pickle.load(file)
                        load_model = Utility.safe_load_from_file(file)

            y_pred_combined_list = []
            Y_actual_combined_list = []
            for filename in os.listdir(payload['folder_path']):
                if filename.endswith('.csv'):
                    csv_path = os.path.join(payload['folder_path'], filename)
                    df = pd.read_csv(csv_path)
                    # df = df[df[df.columns[-1]] == True]
                    # print(filename,':-',df.shape)
                    Y = df[Output_column].values
                    df.drop(columns=df.columns[-3:], axis=1, inplace=True)
                    X = df.iloc[:, :]
                    y_pred_combined_list.append(load_model.predict(X))
                    Y_actual_combined_list.append(Y)

            y_pred_combined = np.concatenate([np.array(sublist) for sublist in y_pred_combined_list], axis=0)  
            Y_actual_combined = np.concatenate([np.array(sublist) for sublist in Y_actual_combined_list], axis=0)  

            tn, fp, fn, tp = confusion_matrix(Y_actual_combined, y_pred_combined).ravel()   
            # print('true negative',tn)
            # print('true positive',tp)
            # print('false negative',fn)
            # print('false positive',fp)   

            del y_pred_combined_list,Y_actual_combined_list,y_pred_combined,Y_actual_combined
            return [tn, fp, fn, tp]   
        except Exception as exc:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "confusionMatrix", exc, apiEndPoint, errorRequestMethod)
            raise Exception  
    
    
    def checkAttackListStatus(payload):

        try:
            if payload['meta_data']['dataType'] == 'Tabular':

                statusList = []
                defenceList = []

                for filename in os.listdir(payload['folder_path']):
                    if filename.endswith('.csv'):
                        csv_path = os.path.join(payload['folder_path'], filename)
                        df = pd.read_csv(csv_path)
                        col = df[df[df.columns[-1]] == True][df.columns[-1]].value_counts().tolist()
                        if len(col) > 0:
                            value = (col[0] / df.shape[0]) * 100
                            # score = Utility.generateDefenceAccuracy({'modelName':payload['modelName'], 'csv_path':csv_path, 'folder_path':payload['folder_path']})
                            score = payload['attack_accuracy_dict'][filename]
                            statusList.append({filename.split('.')[0]:value})
                            defenceList.append({filename.split('.')[0]:(score*100)})
                        else:
                            statusList.append({filename.split('.')[0]:0.0})
                            defenceList.append({filename.split('.')[0]:0.0})
                    else:
                        if filename.endswith('.pdf') or filename.endswith('.html') or filename.endswith('.pkl'):
                            continue

                del df,col
                return statusList,defenceList

            elif payload['meta_data']['dataType'] == 'Image':

                statusList = []

                # print('attackList:---', payload['attackList'])
                for attackName in payload['attackList']:
                    count = 0
                    equal = 0
                    unequal = 0
                    for filename in os.listdir(payload['folder_path']):
                        if any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                            if attackName == filename.split('.')[0].split('^')[1][:-1]:
                                count += 1
                                if filename.split('.')[0].split('^')[1][-1] == 'T':
                                    equal += 1
                                elif filename.split('.')[0].split('^')[1][-1] == 'F':
                                    unequal += 1
                    # print(attackName,equal, count)
                    statusList.append({attackName:(equal/count)*100})
                    # defenceList.append({attackName:0.0})

                # print('statusList:---', statusList)
                # print('defenceList:---', defenceList)
                # return statusList,defenceList
                del count,equal,unequal
                return statusList
            
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "checkAttackListStatus", e, apiEndPoint, errorRequestMethod)
        
    
    def makeAttackListRow(payload):

        try:
            if payload['meta_data']['dataType'] == 'Tabular':

                # get status message of all selected attackList
                keys_list = [key for dictionary in payload['statusList'] for key in dictionary.keys()]

                # all applicable attack arrange in list of dictionary
                attack_list_dict = []
                for i in range(len(payload['total_attacks'])):
                    d = {}
                    if (payload['total_attacks'][i] in payload['attackList']) and (payload['total_attacks'][i] in keys_list):
                        attack_type = ''
                        if payload['total_attacks'][i] in Utility.AttackTypes['Art']['Evasion']:
                            attack_type = 'Evasion'
                        elif payload['total_attacks'][i] in Utility.AttackTypes['Art']['Inference']:
                            attack_type = 'Inference'

                        val1 = ''
                        for k in payload['statusList']:
                            if payload['total_attacks'][i] == next(iter(k.keys())):
                                val1 = k[payload['total_attacks'][i]]
                                break
                        
                        val2 = ''
                        for k in payload['defenceList']:
                            if payload['total_attacks'][i] == next(iter(k.keys())):
                                val2 = k[payload['total_attacks'][i]]
                                break

                        d['name'] = payload['total_attacks'][i]
                        d['selectedAttack'] = '<i class="pass-icon">✔</i>'
                        d['status'] = val1
                        d['accuracy'] = val2
                        d['type'] = attack_type
                        attack_list_dict.append(d)
                    # else:
                    #     d['name'] = payload['total_attacks'][i]
                    #     d['selectedAttack'] = '<i class="fail-icon">X</i>'
                    #     d['status'] = "-"
                    #     attack_list_dict.append(d)

                # sort this list base on Attack Type key
                attack_list_dict = sorted(attack_list_dict, key=lambda x: x['type'])

                # take all these attacks base on sorting with type key
                # attack_list = []
                # for k in attack_list_dict:
                #     attack_list.append(k['name'])
                attack_list = [{k:v for k,v in d.items() if k in ['name', 'type']} for d in attack_list_dict]

                # now all the rows write in html format
                rows = ""
                mitigation_row = ""
                for attack in attack_list_dict:

                    row = f"""
                        <tr>
                            <td>{attack['type']}</td>
                            <td>{attack['name']}</td>
                            <td><span class="selected-attack">✔</span></td>
                            <td>
                                <div class="attack-accuracy">
                                    <div class="attack-accuracy-value">{attack['status']:.2f}%</div>
                                    <div class="attack-accuracy-bar">
                                        <div class="attack-accuracy-bar-fill" style="width: {attack['status']}%;"></div>
                                    </div>
                                </div>
                            </td>
                            
                        </tr>
                    """

                    m_row = f"""
                        <tr>
                            <td>{attack['type']}</td>
                            <td>{attack['name']}</td>
                            <td>
                                <div class="detection-accuracy">
                                    <div class="detection-accuracy-value">{attack['accuracy']:.2f}%</div>
                                    <div class="detection-accuracy-bar">
                                        <div class="detection-accuracy-bar-fill" style="width: {attack['accuracy']}%;"></div>
                                    </div>
                                </div>
                            </td>
                        </tr>
                    """

                    rows += row
                    mitigation_row += m_row

                del keys_list,attack_list_dict
                return rows, mitigation_row, attack_list
            
            elif payload['meta_data']['dataType'] == 'Image':

                # get status message of all selected attackList
                keys_list = [key for dictionary in payload['statusList'] for key in dictionary.keys()]
                # print('keys_list',keys_list)

                # all applicable attack arrange in list of dictionary
                attack_list_dict = []
                for i in range(len(payload['total_attacks'])):
                    d = {}
                    if (payload['total_attacks'][i] in payload['attackList']) and (payload['total_attacks'][i] in keys_list):
                        attack_type = ''
                        if payload['total_attacks'][i] in Utility.AttackTypes['Art']['Evasion']:
                            attack_type = 'Evasion'
                        elif payload['total_attacks'][i] in Utility.AttackTypes['Art']['Inference']:
                            attack_type = 'Inference'
                        elif payload['total_attacks'][i] in Utility.AttackTypes['Augly']['Augmentation']:
                            attack_type = 'Augmentation'

                        val1 = ''
                        for k in payload['statusList']:
                            if payload['total_attacks'][i] == next(iter(k.keys())):
                                val1 = k[payload['total_attacks'][i]]
                                break

                        d['name'] = payload['total_attacks'][i]
                        d['selectedAttack'] = '<i class="pass-icon">✔</i>'
                        d['status'] = val1
                        d['type'] = attack_type
                        attack_list_dict.append(d)
                    # else:
                    #     d['name'] = payload['total_attacks'][i]
                    #     d['selectedAttack'] = '<i class="fail-icon">X</i>'
                    #     d['status'] = "-"
                    #     attack_list_dict.append(d)

                # sort this list base on Attack Type key
                attack_list_dict = sorted(attack_list_dict, key=lambda x: x['type'])
                # print('attack_list_dict',attack_list_dict)

                # take all these attacks base on sorting with type key
                # attack_list = []
                # for k in attack_list_dict:
                #     attack_list.append(k['name'])
                attack_list = [{k:v for k,v in d.items() if k in ['name', 'type']} for d in attack_list_dict]

                # now all the rows write in html format
                rows = ""
                for attack in attack_list_dict:
                    row = f"""
                        <tr>
                            <td>{attack['type']}</td>
                            <td>{attack['name']}</td>
                            <td><span class="selected-attack">✔</span></td>
                            <td>
                                <div class="attack-accuracy">
                                    <div class="attack-accuracy-value">{attack['status']:.2f}%</div>
                                    <div class="attack-accuracy-bar">
                                        <div class="attack-accuracy-bar-fill" style="width: {attack['status']}%;"></div>
                                    </div>
                                </div>
                            </td>
                        </tr>
                    """
                    rows += row

                del keys_list,attack_list_dict
                return rows, attack_list
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "checkAttackListStatus", e, apiEndPoint, errorRequestMethod)
    

    def sanitize_filenameorfoldername(filename):
        try:
            # Allow only alphanumeric characters, underscores, and hyphens
            if not re.match(r'^[\w\-.]+$', filename):
                raise ValueError("Invalid filename: only alphanumeric characters, underscores, and hyphens are allowed.")
            return filename
        except Exception as exc:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "sanitize_filenameorfoldername", exc, apiEndPoint, errorRequestMethod) 

    def createAttackFolder(payload):
        
        try:
            origional_evasion_path:any
            origional_inference_path:any
            folders = list(set(d['type'] for d in payload['attack_list']))
            # print(payload['attack_list'])
            # print(folders)
            for folder in folders:
                if folder == 'Evasion':
                    evasion_path = os.path.join(payload['report_path'],'Art',folder)
                    # print('origional_evasion_path',evasion_path)
                    # if not os.path.exists(evasion_path):
                    #     os.mkdir(evasion_path)
                    if not os.path.exists(evasion_path):
                        os.makedirs(evasion_path, exist_ok=True)
                    origional_evasion_path = evasion_path
                elif folder == 'Inference':
                    inference_path = os.path.join(payload['report_path'],'Art',folder)
                    # print('origional_inference_path',inference_path)
                    # if not os.path.exists(inference_path):
                    #     os.mkdir(inference_path)
                    if not os.path.exists(inference_path):
                        os.makedirs(inference_path, exist_ok=True)
                    origional_inference_path = inference_path
                elif folder == 'Augmentation':
                    augly_path = os.path.join(payload['report_path'],'Augly',folder)
                    # print('origional_augly_path',augly_path)
                    # if not os.path.exists(inference_path):
                    #     os.mkdir(inference_path)
                    if not os.path.exists(augly_path):
                        os.makedirs(augly_path, exist_ok=True)
                    origional_augly_path = augly_path

            # folders = list(set(d['name'] for d in payload['attack_list']))
            # for folder in folders:
            #     if folder in Utility.ArtAttackTypes['Evasion']:
            #         evasion_path = os.path.join(evasion_path,folder)
            #         if not os.path.exists(evasion_path):
            #             os.mkdir(evasion_path)
            #     elif folder in Utility.ArtAttackTypes['Inference']:
            #         inference_path = os.path.join(inference_path,folder)
            #         if not os.path.exists(inference_path):
            #             os.mkdir(inference_path)

            # if evasion_path:
            #     origional_evasion_path = evasion_path
            # else:
            #     evasion_path = ''

            # if inference_path:
            #     origional_inference_path = inference_path
            # else:
            #     inference_path = ''
            
            for filename in os.listdir(payload['report_path']):
                filename = Utility.sanitize_filenameorfoldername(filename)
                if filename.endswith('.csv'):
                    csv_file_path = os.path.join(payload['report_path'], filename)
                    if filename.split('.')[0] in Utility.AttackTypes['Art']['Evasion']:
                        new_folder = os.path.join(evasion_path,filename.split('.')[0])
                        if not os.path.exists(new_folder):
                            os.mkdir(new_folder)
                        with open(csv_file_path, 'r') as csv_file:
                            with open(os.path.join(new_folder, filename), 'w') as f:
                                shutil.copyfileobj(csv_file, f) 
                        evasion_path = origional_evasion_path
                    elif filename.split('.')[0] in Utility.AttackTypes['Art']['Inference']:
                        new_folder = os.path.join(inference_path,filename.split('.')[0])
                        if not os.path.exists(new_folder):
                            os.mkdir(new_folder)
                        with open(csv_file_path, 'r') as csv_file:
                            with open(os.path.join(new_folder, filename), 'w') as f:
                                shutil.copyfileobj(csv_file, f)
                        inference_path = origional_inference_path
                    Utility.databaseDelete(csv_file_path)
                elif any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                    png_file_path = os.path.join(payload['report_path'], filename)
                    # print(filename.split('.')[0].split('^')[1][:-1])
                    if filename.split('.')[0].split('^')[1] in Utility.AttackTypes['Art']['Evasion']:
                        new_folder = os.path.join(evasion_path,filename.split('.')[0].split('^')[1])
                        if not os.path.exists(new_folder):
                            os.mkdir(new_folder)
                        with open(png_file_path, 'rb') as png_file:
                            # content = png_file.read()
                            # with open(os.path.join(new_folder, filename), 'wb') as f:
                            with open(os.path.join(new_folder, f"{filename.split('.')[0].split('^')[0]}.{filename.split('.')[1]}"), 'wb') as f:
                                shutil.copyfileobj(png_file, f)
                                # f.write(content) 
                        evasion_path = origional_evasion_path
                    elif filename.split('.')[0].split('^')[1] in Utility.AttackTypes['Art']['Inference']:
                        new_folder = os.path.join(inference_path,filename.split('.')[0].split('^')[1])
                        if not os.path.exists(new_folder):
                            os.mkdir(new_folder)
                        with open(png_file_path, 'rb') as png_file:
                            # content = png_file.read()
                            # with open(os.path.join(new_folder, filename), 'wb') as f:
                            with open(os.path.join(new_folder, f"{filename.split('.')[0].split('^')[0]}.{filename.split('.')[1]}"), 'wb') as f:
                                shutil.copyfileobj(png_file, f)
                                # f.write(content) 
                        inference_path = origional_inference_path
                    elif filename.split('.')[0].split('^')[1] in Utility.AttackTypes['Augly']['Augmentation']:
                        new_folder = os.path.join(augly_path,filename.split('.')[0].split('^')[1])
                        if not os.path.exists(new_folder):
                            os.mkdir(new_folder)
                        with open(png_file_path, 'rb') as png_file:
                            # content = png_file.read()
                            # with open(os.path.join(new_folder, filename), 'wb') as f:
                            with open(os.path.join(new_folder, f"{filename.split('.')[0].split('^')[0]}.{filename.split('.')[1]}"), 'wb') as f:
                                shutil.copyfileobj(png_file, f)
                                # f.write(content) 
                        augly_path = origional_augly_path
                    Utility.databaseDelete(png_file_path)
                # elif filename.endswith('.png'):
                #     png_file_path = os.path.join(payload['report_path'], filename)
                #     if filename.split('.')[0] in Utility.ArtAttackTypes['Evasion']:
                #         with open(png_file_path, 'r', encoding='utf-8', errors='replace') as png_file:
                #             # content = png_file.read()
                #             with open(os.path.join(evasion_path, filename), 'w', encoding='utf-8') as f:
                #                 shutil.copyfileobj(png_file, f)
                #                 # f.write(content) 
                #     elif filename.split('.')[0] in Utility.ArtAttackTypes['Inference']:
                #         with open(png_file_path, 'r', encoding='utf-8', errors='replace') as png_file:
                #             # content = png_file.read()
                #             with open(os.path.join(inference_path, filename), 'w', encoding='utf-8') as f:
                #                 shutil.copyfileobj(png_file, f)
                #                 # f.write(content) 
                #     Utility.databaseDelete(png_file_path)
                # elif filename.endswith('.png'):
                #     png_file_path = os.path.join(payload['report_path'], filename)
                #     with open(png_file_path, 'r') as png_file:
                #         result = chardet.detect(png_file.read())
                #         encoding = result['encoding']
                #     if filename.split('.')[0] in Utility.ArtAttackTypes['Evasion']:
                #         with codecs.open(png_file_path, 'r', encoding=encoding, errors='ignore') as png_file:
                #             with codecs.open(os.path.join(evasion_path, filename), 'w', encoding='utf-8') as f:
                #                 shutil.copyfileobj(png_file, f)
                #     elif filename.split('.')[0] in Utility.ArtAttackTypes['Inference']:
                #         with codecs.open(png_file_path, 'r', encoding=encoding, errors='ignore') as png_file:
                #             with codecs.open(os.path.join(inference_path, filename), 'w', encoding='utf-8') as f:
                #                 shutil.copyfileobj(png_file, f)
                #     Utility.databaseDelete(png_file_path)
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "createAttackFolder", e, apiEndPoint, errorRequestMethod)
    
    
    def graphForMitigation(payload):

        try:
            if payload['model_metaData']['dataType'] == 'Tabular':

                report_df = pd.DataFrame(payload['classification_reports']).T.rename(index={'0': 'benign', '1': 'adversarial'})
                tn, fp, fn, tp = payload['confusion_matrix'].ravel()
                specificity_not_attack = tp / (tp + fn)
                specificity_attack = tn / (tn + fp)
                accuracy_specificity = report_df.loc['accuracy']['support']
                macro_avg_specificity = (specificity_not_attack + specificity_attack) / 2
                support_not_attack = report_df.loc['benign']['support']
                support_attack = report_df.loc['adversarial']['support']
                weighted_avg_specificity = (specificity_not_attack * support_not_attack + specificity_attack * support_attack) / (support_not_attack + support_attack)
                report_df.loc['benign','specificity'] = specificity_not_attack
                report_df.loc['adversarial','specificity'] = specificity_attack
                report_df.loc['accuracy','specificity'] = accuracy_specificity
                report_df.loc['macro avg','specificity'] = macro_avg_specificity
                report_df.loc['weighted avg','specificity'] = weighted_avg_specificity

                balance_accuracy_not_attack = (report_df.loc['benign']['recall'] + specificity_not_attack) / 2
                balance_accuracy_attack = (report_df.loc['adversarial']['recall'] + specificity_attack) / 2
                macro_avg_balance_accuracy = (balance_accuracy_not_attack + balance_accuracy_attack) / 2
                weighted_avg_balance_accuracy = (balance_accuracy_not_attack * support_not_attack + balance_accuracy_attack * support_attack) / (support_not_attack + support_attack)
                report_df.loc['benign','balance accuracy'] = balance_accuracy_not_attack
                report_df.loc['adversarial','balance accuracy'] = balance_accuracy_attack
                report_df.loc['accuracy','balance accuracy'] = accuracy_specificity
                report_df.loc['macro avg','balance accuracy'] = macro_avg_balance_accuracy
                report_df.loc['weighted avg','balance accuracy'] = weighted_avg_balance_accuracy

                false_positive_rate_not_attack = fn / (fn + tp)
                false_positive_rate_attack = fp / (fp + tn)
                macro_avg_false_positive_rate = (false_positive_rate_not_attack + false_positive_rate_attack) / 2
                weighted_avg_false_positive_rate = (false_positive_rate_not_attack * support_not_attack + false_positive_rate_attack * support_attack) / (support_not_attack + support_attack)
                report_df.loc['benign','FPR'] = false_positive_rate_not_attack
                report_df.loc['adversarial','FPR'] = false_positive_rate_attack
                report_df.loc['accuracy','FPR'] = accuracy_specificity
                report_df.loc['macro avg','FPR'] = macro_avg_false_positive_rate
                report_df.loc['weighted avg','FPR'] = weighted_avg_false_positive_rate

                report_df = report_df[['precision','recall','f1-score','specificity','balance accuracy','FPR','support']]
                return report_df

        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "graphForMitigation", e, apiEndPoint, errorRequestMethod)
    
    
    def graphForAttack(payload):

        try:
            if payload['type'] == 'Tabular':
                
                csv_path = os.path.join(payload['folder_path'],'Attack_Samples.csv')
                graph_path = os.path.join(payload['folder_path'], 'graph.png')

                # taking counts of False and True and then generate pie chart and save graph in png
                df = pd.read_csv(csv_path)
                if payload["attackName"] in Utility.AttackTypes['Art']['Evasion']:
                    comparasion_counts = df[[payload['target'],'prediction']].apply(
                                            lambda x: 'Successful' if x[payload['target']] != x['prediction'] 
                                                else 'Unsuccessful', axis=1).value_counts().to_dict()
                elif payload["attackName"] in Utility.AttackTypes['Art']['Inference']:
                    comparasion_counts = df[[payload['target'],'prediction']].apply(
                                            lambda x: 'Successful' if x[payload['target']] == x['prediction'] 
                                                else 'Unsuccessful', axis=1).value_counts().to_dict()
                plt.figure(figsize=(8,6))
                if len(comparasion_counts) > 1:
                    comparasion_counts = {'Successful': comparasion_counts['Successful'], 
                                        'Unsuccessful':comparasion_counts['Unsuccessful']}
                    # # plt.pie(list(comparasion_counts.values()), labels=list(comparasion_counts.keys()), 
                    # #         colors=['#bf1029','#056517'], explode=(0.1,0), autopct='%1.1f%%', startangle=90)
                    # plt.pie(list(comparasion_counts.values()), labels=list(comparasion_counts.keys()), 
                    #         colors=['#1ca0f2','#05050F'], explode=(0.1,0), autopct='%1.1f%%', startangle=90)
                    plt.pie(list(comparasion_counts.values()), labels=list(comparasion_counts.keys()), 
                            colors=['#1ca0f2','#05050F'], explode=(0.1,0), startangle=90, autopct=lambda pct: "{:1.1f}%".format(pct), 
                            textprops={'color': '#FFFFFF','size': '20'})
                else:
                    if 'Unsuccessful' in comparasion_counts and 'Successful' not in comparasion_counts:
                        # # plt.pie(list(comparasion_counts.values()), labels=list(comparasion_counts.keys()), 
                        # #     colors=['#056517'], startangle=90)
                        # plt.pie(list(comparasion_counts.values()), labels=list(comparasion_counts.keys()), 
                        #     colors=['#05050F'], startangle=90)
                        plt.pie(list(comparasion_counts.values()), labels=list(comparasion_counts.keys()), 
                            colors=['#05050F'], startangle=90, autopct=lambda pct: "{:1.1f}%".format(pct), 
                            textprops={'color': '#FFFFFF','size': '20'})
                    elif 'Successful' in comparasion_counts and 'Unsuccessful' not in comparasion_counts:
                        # # plt.pie(list(comparasion_counts.values()), labels=list(comparasion_counts.keys()), 
                        # #     colors=['#bf1029'], startangle=90)
                        # plt.pie(list(comparasion_counts.values()), labels=list(comparasion_counts.keys()), 
                        #     colors=['#1ca0f2'], startangle=90)
                        plt.pie(list(comparasion_counts.values()), labels=list(comparasion_counts.keys()), 
                            colors=['#1ca0f2'], startangle=90, autopct=lambda pct: "{:1.1f}%".format(pct), 
                            textprops={'color': '#FFFFFF','size': '20'})
                # cols = comparasion_counts.index.to_list()
                # plt.figure(figsize=(8,6))
                # # plt.bar(comparasion_counts.index, comparasion_counts.values, label=['True','False'])
                # if len(cols) > 1:
                #     plt.pie(comparasion_counts.values, labels=['Unsuccessfull Data','Successfull Data'], colors=['#056517','#bf1029'], explode=(0.1,0), autopct='%1.1f%%', startangle=90)
                # else:
                #     if cols[0] == 'Successfull Data':
                #         plt.pie(comparasion_counts.values, labels=['Successfull Data'], colors=['#bf1029'], autopct='%1.1f%%', startangle=90)
                #     else:
                #         plt.pie(comparasion_counts.values, labels=['Unsuccessfull Data'], colors=['#056517'], autopct='%1.1f%%', startangle=90)
                plt.legend(loc='center right', bbox_to_anchor=(1.2, 0.9), prop={'size': 16}, markerscale=0)
                plt.grid(True)
                plt.savefig(graph_path)
                plt.close()

                # saved graph.png convert into html
                with open(graph_path, 'rb') as img_file:
                    img_data = img_file.read()
                    base64_img = base64.b64encode(img_data).decode('utf-8')

                graph_html = f"""<div class='graph-container-attack'><img src='data:image/png;base64,{base64_img}' alt='Attack Graph' class='graph-image-csv'></div>"""
                os.remove(graph_path)
                del df
                return graph_html
            
            elif payload['type'] == 'Image':
                
                c = 0
                graph_html = ''
                for keys in payload['top_keys']:
                    c += 1
                    if keys in payload['attackDataList']:

                        graph_path = os.path.join(payload['folder_path'], 'graph.png')

                        # if payload['basePrediction_class'] == payload['adversialPrediction_class']:
                        #     plt.pie([100], labels=['UnSuccessfull Data'], colors=['#05050F'], startangle=90, 
                        #             autopct=lambda pct: "{:1.1f}%".format(pct), textprops={'color': '#FFFFFF'})
                        # else:
                        #     plt.pie([100], labels=['Successfull Data'], colors=['#1ca0f2'], startangle=90, 
                        #             autopct=lambda pct: "{:1.1f}%".format(pct), textprops={'color': '#FFFFFF'})    
                        # plt.legend(loc='center right', bbox_to_anchor=(1.2, 0.9))
                        # plt.grid(True)
                        # plt.savefig(graph_path)
                        # plt.close()



                        #---------------------------------------------------------------------

                        # # def break_word(word, max_length=15):
                        # #     lines = []
                        # #     while len(word) > max_length:
                        # #         lines.append(word[:max_length])
                        # #         word = word[max_length:]
                        # #     if word:
                        # #         lines.append(word)
                        # #     return '\n'.join(lines)

                        # def break_word(word):
                        #     max_length=len(word)
                        #     parts = word.split('-')
                        #     lines = []
                        #     for part in parts:
                        #         while len(part) > max_length:
                        #             lines.append(part[:max_length])
                        #             part = part[max_length:]
                        #         if part:
                        #             lines.append(part)
                        #     return '\n'.join(lines)
                        
                        # composite_image = np.concatenate((payload['attackDataList'][keys][1][0], np.ones((payload['attackDataList'][keys][1].shape[1], 10, 3)), payload['attackDataList'][keys][2][0]), axis=1)
                        # # fig, ax = plt.subplots(figsize=(14, 6))
                        # fig, ax = plt.subplots(figsize=(80, 50))
                        # ax.imshow(composite_image)
                        # ax.axis('off')
                        # # ax.text(0.25, -0.1, f"{keys.split('.')[0]}-{payload['attackDataList'][keys][3]}", transform=ax.transAxes, ha='center', fontsize=32, weight='bold')
                        # # ax.text(0.75, -0.1, f"{keys.split('.')[0]}-{payload['attackDataList'][keys][4]}", transform=ax.transAxes, ha='center', fontsize=32, weight='bold')
                        # ax.text(0.25, -0.2, break_word(f"{keys.split('.')[0]}-{payload['attackDataList'][keys][3]}"), transform=ax.transAxes, ha='center', fontsize=150, weight='bold')
                        # ax.text(0.75, -0.2, break_word(f"{keys.split('.')[0]}-{payload['attackDataList'][keys][4]}"), transform=ax.transAxes, ha='center', fontsize=150, weight='bold')
                        # ax.text(0.25, -0.28, "(Expected Value)", transform=ax.transAxes, ha='center', fontsize=130, weight='bold')
                        # ax.text(0.75, -0.28, "(Predicted Value)", transform=ax.transAxes, ha='center', fontsize=130, weight='bold')
                        # ax.set_title('     Original Image                  Adversarial Image', loc='center', fontsize=150, weight='bold')
                        # plt.savefig(graph_path)
                        # plt.close()

                        #---------------------------------------------------------------------

                        #---------------------------------------------------------------------

                        def break_word(word):
                            max_length = len(word)
                            lines = []
                            while len(word) > max_length:
                                lines.append(word[:max_length])
                                word = word[max_length:]
                            if word:
                                lines.append(word)
                            return '\n'.join(lines)
                        
                        composite_image = np.concatenate((payload['attackDataList'][keys][1][0], np.ones((payload['attackDataList'][keys][1].shape[1], 10, 3)), payload['attackDataList'][keys][2][0]), axis=1)
                        # fig, ax = plt.subplots(figsize=(14, 6))
                        fig, ax = plt.subplots(figsize=(80, 50))
                        ax.imshow(composite_image)
                        ax.axis('off')
                        # # ax.text(0.25, -0.1, f"{keys.split('.')[0]}-{payload['attackDataList'][keys][3]}", transform=ax.transAxes, ha='center', fontsize=32, weight='bold')
                        # # ax.text(0.75, -0.1, f"{keys.split('.')[0]}-{payload['attackDataList'][keys][4]}", transform=ax.transAxes, ha='center', fontsize=32, weight='bold')
                        # ax.text(0.25, -0.1, break_word(f"{payload['attackDataList'][keys][3]}"), transform=ax.transAxes, ha='center', fontsize=180, weight='bold')
                        # ax.text(0.75, -0.1, break_word(f"{payload['attackDataList'][keys][4]}"), transform=ax.transAxes, ha='center', fontsize=180, weight='bold')
                        # ax.text(0.25, -0.19, "(Predicted Value)", transform=ax.transAxes, ha='center', fontsize=160, weight='bold') # -0.18
                        # ax.text(0.75, -0.19, "(Predicted Value)", transform=ax.transAxes, ha='center', fontsize=160, weight='bold') # -0.18
                        # ax.text(0.25, -0.26, "(Original Image)", transform=ax.transAxes, ha='center', fontsize=140, weight='bold') # -0.25
                        # ax.text(0.75, -0.26, "(Adversarial Image)", transform=ax.transAxes, ha='center', fontsize=140, weight='bold') # -0.25
                        # # ax.text(0.25, -0.25, "(Original Prediction)", transform=ax.transAxes, ha='center', fontsize=140, weight='bold')
                        # # ax.text(0.75, -0.25, "(Adversarial Prediction)", transform=ax.transAxes, ha='center', fontsize=140, weight='bold')
                        ax.text(0.25, -0.07, "Original Image", transform=ax.transAxes, ha='center', fontsize=140, weight='bold') # -0.25
                        ax.text(0.75, -0.07, "Adversarial Image", transform=ax.transAxes, ha='center', fontsize=140, weight='bold') # -0.25
                        ax.text(0.25, -0.20, break_word(f"{payload['attackDataList'][keys][3]}"), transform=ax.transAxes, ha='center', fontsize=180, weight='bold')
                        ax.text(0.75, -0.20, break_word(f"{payload['attackDataList'][keys][4]}"), transform=ax.transAxes, ha='center', fontsize=180, weight='bold')
                        ax.text(0.25, -0.28, "(Predicted Value)", transform=ax.transAxes, ha='center', fontsize=150, weight='bold') # -0.18
                        ax.text(0.75, -0.28, "(Predicted Value)", transform=ax.transAxes, ha='center', fontsize=150, weight='bold') # -0.18
                        
                        ax.set_title(break_word(f"{keys.split('.')[0]}"), loc='center', fontsize=200, weight='bold')
                        plt.savefig(graph_path)
                        plt.close()

                        #---------------------------------------------------------------------



                        # saved graph.png convert into html
                        with open(graph_path, 'rb') as img_file:
                            img_data = img_file.read()
                            base64_img = base64.b64encode(img_data).decode('utf-8')

                        graph_html += f"""<img src='data:image/png;base64,{base64_img}' alt='Attack Graph'>"""
                        os.remove(graph_path)

                        if c == 4:
                            break
                        
                return graph_html
            
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "graphForAttack", e, apiEndPoint, errorRequestMethod)
        

    def graphForAttackColumn(payload):

        try:
            if payload['type'] == 'Tabular':

                graph_path = os.path.join(payload['report_path'], 'graph.png')
                adversarial_df = pd.read_csv(payload['adversarial_data_path'])
                original_df = pd.read_csv(payload['original_data_path'])

                if payload['attackName'] in Utility.AttackTypes['Art']['Inference']:
                    return None

                elif payload['attackName'] in Utility.AttackTypes['Art']['Evasion']:
                    original_df = original_df.iloc[:, :-1]
                    adversarial_df = adversarial_df.iloc[:, :-3]

                    # bar graph for most attack column 
                    # exact_val = np.sqrt(np.mean((original_df - adversarial_df) ** 2, axis=0)) # RMSE
                    exact_val = np.mean(np.abs(original_df - adversarial_df), axis=0) # MAE
                    top_cols_indices = np.argsort(exact_val)[::-1][:5]
                    top_cols = adversarial_df.columns[top_cols_indices]

                    if np.any(exact_val[top_cols_indices] == 0):
                        print(f"Skipping {payload['attackName']} because it has zero exact_values")
                        return None

                    else:
                        
                        plt.figure(figsize=(8, 6))
                        plt.bar(original_df.columns[top_cols_indices], exact_val[top_cols], color=['#1ca0f2'])

                        for i, value in enumerate(exact_val[top_cols]):
                            plt.text(i, value, f"{value:.2g}", ha='center', va='bottom') # f"{value:.2g}", f"{value:.2f}"

                        plt.xlabel('Column Name')
                        # plt.ylabel('Root Mean Square Error (RMSE)')
                        plt.ylabel('Mean Absolute Value (Benign and Adversarial)')
                        plt.title('Top 5 Attacked Columns')
                        plt.xticks(rotation=45, ha='right')
                        plt.tight_layout()
                        # plt.show()
                        plt.savefig(graph_path)
                        plt.close()
                    
                        # saved graph.png convert into html
                        with open(graph_path, 'rb') as img_file:
                            img_data = img_file.read()
                            base64_img = base64.b64encode(img_data).decode('utf-8')
                        graph_data = f"<body><div class='graph-container'><img src='data:image/png;base64,{base64_img}' alt='Attack Graph' class='graph-image'></div></body>"
                        os.remove(graph_path)

                        del adversarial_df,original_df
                        return graph_data
            
            elif payload['type'] == 'Image':
                
                pass

        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "graphForAttackColumn", e, apiEndPoint, errorRequestMethod)
    

    def graphForCombineAttack(payload):
        
        try:
            # taking counts of False and True and then generate stack bar chart and save graph in png
            html_path = os.path.join(payload['folder_path'], 'report.html')
            graph_html:any
            if payload['model_metaData']['dataType'] == 'Image':
                attackList = [x['name'] for x in payload['attack_list']] 
                graph_path = os.path.join(payload['folder_path'], 'graph.png')
                df_size = []
                data = []
                for attackName in attackList:
                    count = 0
                    equal = 0
                    unequal = 0
                    for filename in os.listdir(payload['folder_path']):
                        if any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                            if attackName == filename.split('.')[0].split('^')[1][:-1]:
                                count += 1
                                if filename.split('.')[0].split('^')[1][-1] == 'T':
                                    equal += 1
                                elif filename.split('.')[0].split('^')[1][-1] == 'F':
                                    unequal += 1
                            
                    df_size.append(count)
                    data.append((attackName,unequal,equal))
                # print('dataList:---', data)
                result_df = pd.DataFrame(data, columns=['','Unsuccessful','Successful'])
                result_df.set_index('')[['Unsuccessful','Successful']].plot(kind='bar', 
                                        stacked=True, figsize=(12,8), color=['#05050F','#1ca0f2']) # ['#05050F','#1ca0f2'] | ['#056517','#bf1029']
                
                # plt.title('Evasion Attack Robustness', color='white', bbox=dict(facecolor='darkorchid'))
                plt.ylabel('Adversial Sample Size')
                plt.xlabel('Attack Name')
                plt.legend(title='Status', bbox_to_anchor=(1.05,1), loc='upper left')
                plt.xticks(rotation=45, ha='right')
                plt.yticks(np.arange(0, max(result_df['Unsuccessful'] + result_df['Successful'])+1, 1))
                plt.tight_layout()
        
                for index, row in result_df.iterrows():
                    plt.text(index, row['Unsuccessful']/2, f"{((row['Unsuccessful']/df_size[index])*100):.1f}%", ha='center', va='center', color='white')
                    plt.text(index, row['Unsuccessful']+row['Successful']/2, f"{((row['Successful']/df_size[index])*100):.1f}%", ha='center', va='center', color='white')
                plt.savefig(graph_path)
                plt.close()
                
                # saved graph.png convert into html
                with open(graph_path, 'rb') as img_file:
                    img_data = img_file.read()
                    base64_img = base64.b64encode(img_data).decode('utf-8')

                graph_html = Utility.htmlContent({'modelName':payload['modelName'], 'model_metaData':payload['model_metaData'], 'reportTime':payload['reportTime'], 'success_skipped':payload['success_skipped'], 'rows':payload['rows'], 'graph':base64_img})
                # graph_html = Utility.htmlContent({'modelName':payload['modelName'], 'model_metaData':payload['model_metaData'], 'reportTime':payload['reportTime'], 'success_skipped':payload['success_skipped'], 'rows':payload['rows'], 'graph':base64_img})
                os.remove(graph_path)

                # add appendix part in html
                appendix_html = Utility.htmlAppendixContent({'model_metaData':payload['model_metaData']})

                # read content of combined html and add graph html content at begining
                with open(html_path, 'r') as old_html_file:
                    old_html_content = old_html_file.read()
                new_html_content = graph_html + old_html_content + appendix_html

                # now after adding graph+combined html content then again write into same previous combined.html
                with open(html_path, 'w', encoding='utf-8') as combine_html_file:
                    combine_html_file.writelines(new_html_content)
                    combine_html_file.writelines(Utility.htmlCssContent({'model_metaData':payload['model_metaData']}))
            
                del attackList,result_df,graph_html,old_html_content,appendix_html,new_html_content
                return
                
            elif payload['model_metaData']['dataType'] == 'Tabular':
                
                attackList = [x['name'] for x in payload['attack_list']] 
                graph_path = os.path.join(payload['folder_path'], 'graph.png')
                df_size = []
                data = []
                for attackName in attackList:
                    for filename in os.listdir(payload['folder_path']):
                        if attackName == filename.split('.')[0]:
                            if filename.endswith('.csv'):
                                csv_path = os.path.join(payload['folder_path'], filename)
                                df = pd.read_csv(csv_path)
                                df_size.append(df.shape[0])
                                equal = len(df[df[payload['target']] == df['prediction']])
                                unequal = len(df[df[payload['target']] != df['prediction']])
                                if filename.split('.')[0] in Utility.AttackTypes['Art']['Evasion']:
                                    data.append((filename.split('.')[0],equal,unequal))
                                elif filename.split('.')[0] in Utility.AttackTypes['Art']['Inference']:
                                    data.append((filename.split('.')[0],unequal,equal))
                
                result_df = pd.DataFrame(data, columns=['','Unsuccessful','Successful'])
                # result_df.set_index('')[['Unsuccessful','Successful']].plot(kind='bar', 
                #                                     stacked=True, figsize=(12,8), color=['#056517','#bf1029'])
                result_df.set_index('')[['Unsuccessful','Successful']].plot(kind='bar', 
                                                    stacked=True, figsize=(12,8), color=['#05050F','#1ca0f2'])
                # plt.title('Evasion Attack Robustness', color='white', bbox=dict(facecolor='darkorchid'))
                plt.ylabel('Adversial Sample Size')
                plt.xlabel('Attack Name')
                plt.legend(title='Status', bbox_to_anchor=(1.05,1), loc='upper left')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()

                for index, row in result_df.iterrows():
                    plt.text(index, row['Unsuccessful']/2, f"{((row['Unsuccessful']/df_size[index])*100):.1f}%", ha='center', va='center', color='white')
                    plt.text(index, row['Unsuccessful']+row['Successful']/2, f"{((row['Successful']/df_size[index])*100):.1f}%", ha='center', va='center', color='white')
                plt.savefig(graph_path)
                plt.close()

                # saved graph.png convert into html
                with open(graph_path, 'rb') as img_file:
                    img_data = img_file.read()
                    base64_img = base64.b64encode(img_data).decode('utf-8')
                
                graph_html = Utility.htmlContent({'modelName':payload['modelName'], 'model_metaData':payload['model_metaData'], 'reportTime':payload['reportTime'], 'success_skipped':payload['success_skipped'], 'rows':payload['rows'], 'graph':base64_img, 'confusion_matrix':payload['confusion_matrix']})

                # add mitigation part in html
                mitifation_html_content = Utility.htmlMitigationContent({'modelName':payload['modelName'], 'model_metaData':payload['model_metaData'], 'reportTime':payload['reportTime'], 'success_skipped':payload['success_skipped'], 'rows':payload['rows'], 'graph':base64_img, 'confusion_matrix':payload['confusion_matrix'], 'mitigation_row':payload['mitigation_row']})

                # add graph for confusion and classificatio_report
                report_df = Utility.graphForMitigation({'confusion_matrix':payload['confusion_matrix'], 'classification_reports':payload['classification_reports'], 'model_metaData':payload['model_metaData']})
                report_df.columns = [col.replace(' ', '\n') for col in report_df.columns]

                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))  
                # graph for confusion matrix
                sns.heatmap(pd.DataFrame(payload['confusion_matrix']), annot=True, fmt='g', cmap='Blues', ax=ax1, xticklabels=['Benign','Adversarial'],
                            yticklabels=['Benign','Adversarial'])
                ax1.set_ylabel('Actual', fontsize=13)
                ax1.set_title('Confusion Matrix', fontsize=14, pad=20) # fontweight='bold'
                ax1.xaxis.set_label_position('top') 
                ax1.set_xlabel('Prediction', fontsize=13)
                ax1.xaxis.tick_top()
                
                # graph for classification report
                sns.heatmap(report_df.iloc[:,:], annot=True, fmt='.2f', cmap='Blues', ax=ax2, 
                            xticklabels=report_df.columns, yticklabels=report_df.index[:], 
                            )
                # ax2.set_ylabel('Label', fontsize=13)
                ax2.set_title('Classification Report', fontsize=14, pad=20) # fontweight='bold'
                ax2.xaxis.set_label_position('top') 
                ax2.set_xlabel('Metric', fontsize=13)
                ax2.xaxis.tick_top()
                plt.subplots_adjust(hspace=50000.5)
                plt.tight_layout()
                plt.savefig(graph_path)
                plt.close()

                # saved graph.png convert into html
                with open(graph_path, 'rb') as img_file:
                    img_data = img_file.read()
                    base64_img = base64.b64encode(img_data).decode('utf-8')
                graph_data = f"<body><div class='graph-container'><img src='data:image/png;base64,{base64_img}' alt='Attack Graph' class='graph-image'></div></body>"
                os.remove(graph_path)

                # add appendix part in html
                appendix_html = Utility.htmlAppendixContent({'model_metaData':payload['model_metaData']})

                # add combined html, add graph html, add mitigation html, graph_data, appendix content 
                with open(html_path, 'r') as old_html_file:
                    old_html_content = old_html_file.read()
                new_html_content = graph_html + old_html_content + mitifation_html_content + graph_data + appendix_html

                # now after adding graph+combined html content then again write into same previous combined.html
                with open(html_path, 'w', encoding='utf-8') as combine_html_file:
                    combine_html_file.writelines(new_html_content)
                    combine_html_file.writelines(Utility.htmlCssContent({'model_metaData':payload['model_metaData']}))
            
                del attackList,result_df,graph_html,old_html_content,mitifation_html_content,graph_data,appendix_html,new_html_content
                return
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "graphForCombineAttack", e, apiEndPoint, errorRequestMethod)
    
    
    def graphForCombineAttack1(payload):

        try:
            html_path = os.path.join(payload['folder_path'], 'report.html')
            graph_html:any
            if payload['model_metaData']['dataType'] == 'Image':
                attackList = [x['name'] for x in payload['attack_list']]
                graph_path = os.path.join(payload['folder_path'], 'graph.png')

                num_attacks = len(attackList)
                max_attacks = 8
                if num_attacks > max_attacks:
                    num_subplots = -(-num_attacks // max_attacks)  
                else:
                    num_subplots = 1
                fig, axs = plt.subplots(num_subplots, 1)
                if num_attacks < max_attacks:
                    axs = [axs]

                for i in range(num_subplots):
                    if num_attacks > max_attacks:
                        chunk_attackList = attackList[i*max_attacks:(i+1)*max_attacks]
                    else:
                        chunk_attackList = attackList
                    df_size = []
                    data = []
                    for attackName in chunk_attackList:
                        count = 0
                        equal = 0
                        unequal = 0
                        for filename in os.listdir(payload['folder_path']):
                            if any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                                if attackName == filename.split('.')[0].split('^')[1][:-1]:
                                    count += 1
                                    if filename.split('.')[0].split('^')[1][-1] == 'T':
                                        equal += 1
                                    elif filename.split('.')[0].split('^')[1][-1] == 'F':
                                        unequal += 1
                        df_size.append(count)
                        data.append((attackName, unequal, equal))
                    
                    result_df = pd.DataFrame(data, columns=['', 'Unsuccessful', 'Successful'])
                    result_df.set_index('')[['Unsuccessful', 'Successful']].plot(kind='bar', ax=axs[i], stacked=True, figsize=(12,8), color=['#05050F','#1ca0f2'])
                    # Set title and labels for each subplot
                    if num_attacks > max_attacks:
                        axs[i].set_title(f'Attacks {i*max_attacks+1} to {(i+1)*max_attacks}' if i < num_subplots - 1 else f'Attacks {i*max_attacks+1} to {num_attacks}')
                    else:
                        axs[i].set_title('Attacks')
                    axs[i].set_ylabel('Adversial Sample Size')
                    axs[i].set_xlabel('Attack Name')
                    axs[i].legend(title='Status', bbox_to_anchor=(1.05,1), loc='upper left')
                    axs[i].set_xticklabels(chunk_attackList, rotation=45, ha='right')
                    axs[i].set_yticks(np.arange(0, max(result_df['Unsuccessful'] + result_df['Successful'])+1, 1))
                    
                    # Add percentage labels to each bar
                    for index, row in result_df.iterrows():
                        axs[i].text(index, row['Unsuccessful']/2, f"{((row['Unsuccessful']/df_size[index])*100):.1f}%", ha='center', va='center', color='white') # , fontsize=8
                        axs[i].text(index, row['Unsuccessful']+row['Successful']/2, f"{((row['Successful']/df_size[index])*100):.1f}%", ha='center', va='center', color='white') # , fontsize=8            
                fig.tight_layout()
                fig.savefig(graph_path)
                plt.close(fig)
                
                # saved graph.png convert into html
                with open(graph_path, 'rb') as img_file:
                    img_data = img_file.read()
                    base64_img = base64.b64encode(img_data).decode('utf-8')

                graph_html = Utility.htmlContent({'modelName':payload['modelName'], 'model_metaData':payload['model_metaData'], 'reportTime':payload['reportTime'], 'success_skipped':payload['success_skipped'], 'rows':payload['rows'], 'graph':base64_img})
                # graph_html = Utility.htmlContent({'modelName':payload['modelName'], 'model_metaData':payload['model_metaData'], 'reportTime':payload['reportTime'], 'success_skipped':payload['success_skipped'], 'rows':payload['rows'], 'graph':base64_img})
                os.remove(graph_path)

                # add appendix part in html
                appendix_html = Utility.htmlAppendixContent({'model_metaData':payload['model_metaData']})

                # read content of combined html and add graph html content at begining
                with open(html_path, 'r') as old_html_file:
                    old_html_content = old_html_file.read()
                new_html_content = graph_html + old_html_content + appendix_html

                # now after adding graph+combined html content then again write into same previous combined.html
                with open(html_path, 'w', encoding='utf-8') as combine_html_file:
                    combine_html_file.writelines(new_html_content)
                    combine_html_file.writelines(Utility.htmlCssContent({'model_metaData':payload['model_metaData']}))
            
                del attackList,num_attacks,num_subplots,chunk_attackList,result_df,graph_html,old_html_content,appendix_html,new_html_content
                return

            elif payload['model_metaData']['dataType'] == 'Tabular':
                attackList = [x['name'] for x in payload['attack_list']]
                graph_path = os.path.join(payload['folder_path'], 'graph.png')

                num_attacks = len(attackList)
                max_attacks = 8
                if num_attacks > max_attacks:
                    num_subplots = -(-num_attacks // max_attacks)  # calculate the number of subplots needed
                else:
                    num_subplots = 1
                fig, axs = plt.subplots(num_subplots, 1)
                if num_attacks < max_attacks:
                    axs = [axs]

                for i in range(num_subplots):
                    if num_attacks > max_attacks:
                        chunk_attackList = attackList[i*max_attacks:(i+1)*max_attacks]
                    else:
                        chunk_attackList = attackList
                    df_size = []
                    data = []
                    for attackName in chunk_attackList:
                        for filename in os.listdir(payload['folder_path']):
                            if attackName == filename.split('.')[0]:
                                if filename.endswith('.csv'):
                                    csv_path = os.path.join(payload['folder_path'], filename)
                                    df = pd.read_csv(csv_path)
                                    df_size.append(df.shape[0])
                                    equal = len(df[df[payload['target']] == df['prediction']])
                                    unequal = len(df[df[payload['target']] != df['prediction']])
                                    if filename.split('.')[0] in Utility.AttackTypes['Art']['Evasion']:
                                        data.append((filename.split('.')[0],equal,unequal))
                                    elif filename.split('.')[0] in Utility.AttackTypes['Art']['Inference']:
                                        data.append((filename.split('.')[0],unequal,equal))
                    
                    result_df = pd.DataFrame(data, columns=['', 'Unsuccessful', 'Successful'])
                    result_df.set_index('')[['Unsuccessful', 'Successful']].plot(kind='bar', ax=axs[i], stacked=True, figsize=(12,8), color=['#05050F','#1ca0f2'])
                    # Set title and labels for each subplot
                    if num_attacks > max_attacks:
                        axs[i].set_title(f'Attacks {i*max_attacks+1} to {(i+1)*max_attacks}' if i < num_subplots - 1 else f'Attacks {i*max_attacks+1} to {num_attacks}')
                    else:
                        axs[i].set_title('Attacks')
                    axs[i].set_ylabel('Adversial Sample Size')
                    axs[i].set_xlabel('Attack Name')
                    axs[i].legend(title='Status', bbox_to_anchor=(1.05,1), loc='upper left')
                    axs[i].set_xticklabels(chunk_attackList, rotation=45, ha='right')
                    # Add percentage labels to each bar
                    for index, row in result_df.iterrows():
                        axs[i].text(index, row['Unsuccessful']/2, f"{((row['Unsuccessful']/df_size[index])*100):.1f}%", ha='center', va='center', color='white') # , fontsize=8
                        axs[i].text(index, row['Unsuccessful']+row['Successful']/2, f"{((row['Successful']/df_size[index])*100):.1f}%", ha='center', va='center', color='white') # , fontsize=8
                fig.tight_layout()
                fig.savefig(graph_path)
                plt.close(fig)    
                   
                # saved graph.png convert into html
                with open(graph_path, 'rb') as img_file:
                    img_data = img_file.read()
                    base64_img = base64.b64encode(img_data).decode('utf-8')  

                graph_html = Utility.htmlContent({'modelName':payload['modelName'], 'model_metaData':payload['model_metaData'], 'reportTime':payload['reportTime'], 'success_skipped':payload['success_skipped'], 'rows':payload['rows'], 'graph':base64_img, 'confusion_matrix':payload['confusion_matrix']})   

                # add mitigation part in html
                mitifation_html_content = Utility.htmlMitigationContent({'modelName':payload['modelName'], 'model_metaData':payload['model_metaData'], 'reportTime':payload['reportTime'], 'success_skipped':payload['success_skipped'], 'rows':payload['rows'], 'graph':base64_img, 'confusion_matrix':payload['confusion_matrix'], 'mitigation_row':payload['mitigation_row']})

                # add graph for confusion and classificatio_report
                report_df = Utility.graphForMitigation({'confusion_matrix':payload['confusion_matrix'], 'classification_reports':payload['classification_reports'], 'model_metaData':payload['model_metaData']})
                report_df.columns = [col.replace(' ', '\n') for col in report_df.columns]

                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))  
                # graph for confusion matrix
                sns.heatmap(pd.DataFrame(payload['confusion_matrix']), annot=True, fmt='g', cmap='Blues', ax=ax1, xticklabels=['Benign','Adversarial'],
                            yticklabels=['Benign','Adversarial'])
                ax1.set_ylabel('Actual', fontsize=13)
                ax1.set_title('Confusion Matrix', fontsize=14, pad=20) # fontweight='bold'
                ax1.xaxis.set_label_position('top') 
                ax1.set_xlabel('Prediction', fontsize=13)
                ax1.xaxis.tick_top()

                # graph for classification report
                sns.heatmap(report_df.iloc[:,:], annot=True, fmt='.2f', cmap='Blues', ax=ax2, 
                            xticklabels=report_df.columns, yticklabels=report_df.index[:], 
                            )
                # ax2.set_ylabel('Label', fontsize=13)
                ax2.set_title('Classification Report', fontsize=14, pad=20) # fontweight='bold'
                ax2.xaxis.set_label_position('top') 
                ax2.set_xlabel('Metric', fontsize=13)
                ax2.xaxis.tick_top()
                plt.subplots_adjust(hspace=50000.5)
                plt.tight_layout()
                plt.savefig(graph_path)
                plt.close()

                # saved graph.png convert into html
                with open(graph_path, 'rb') as img_file:
                    img_data = img_file.read()
                    base64_img = base64.b64encode(img_data).decode('utf-8')
                graph_data = f"<body><div class='graph-container'><img src='data:image/png;base64,{base64_img}' alt='Attack Graph' class='graph-image'></div></body>"
                os.remove(graph_path)

                # add appendix part in html
                appendix_html = Utility.htmlAppendixContent({'model_metaData':payload['model_metaData']})

                # add combined html, add graph html, add mitigation html, graph_data, appendix content 
                with open(html_path, 'r') as old_html_file:
                    old_html_content = old_html_file.read()
                new_html_content = graph_html + old_html_content + mitifation_html_content + graph_data + appendix_html

                # now after adding graph+combined html content then again write into same previous combined.html
                with open(html_path, 'w', encoding='utf-8') as combine_html_file:
                    combine_html_file.writelines(new_html_content)
                    combine_html_file.writelines(Utility.htmlCssContent({'model_metaData':payload['model_metaData']}))
            
                del attackList,num_attacks,num_subplots,chunk_attackList,result_df,graph_html,old_html_content,mitifation_html_content,graph_data,appendix_html,new_html_content
                return

        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "graphForCombineAttack1", e, apiEndPoint, errorRequestMethod)
    
    
    def getPredictionsFromEndpoint(payload):

        try:
            
            api_data_variable = payload['data']
            api_response_variable = payload['prediction']

            if payload['batch']:
                # Send a post request to the end point with multiple data points
                headers ={'Content-Type': 'application/json'}
                request_data =json.dumps({api_data_variable: payload['train_data'].tolist()})
                log.info('Trying connection to model endpoint...')
                response = requests.post(payload['api'], request_data, headers=headers)
            else:
                # Send a post request to the end point with single data point
                headers ={'Content-Type': 'application/json'}
                request_data =json.dumps({api_data_variable: payload['train_data'].reshape(1, -1).tolist()})
                log.info('Trying connection to model endpoint...')
                response = requests.post(payload['api'], request_data, headers=headers)
                
            # Get the prediction from the response
            prediction = json.loads(response.text)[api_response_variable]

        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "getPredictionsFromEndpoint", e, apiEndPoint, errorRequestMethod)

        return prediction
    

    def createArtEstimator(payload):
        try:
            sklearn_api_estimator = SklearnAPIClassifier(api=payload['modelEndPoint'],
                                    nb_classes = payload['nb_classes'],
                                    input_shape = payload['input_shape'],
                                    api_data_variable = payload['api_data_variable'],
                                    api_response_variable = payload['api_response_variable']
                                )
            
            # return 'sklearn_api_estimator'
            return sklearn_api_estimator
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "createArtEstimator", e, apiEndPoint, errorRequestMethod)

    
    def generateImage(payload):

        try:
            # Create a composite image with the original and adversarial images
            composite_image = np.concatenate((payload['base_sample'][0], np.ones((payload['base_sample'].shape[1], 10, 3)), payload['adversial_sample'][0]), axis=1)

            # Set the figure size and create a subplot
            fig, ax = plt.subplots(figsize=(10, 4))

            # Display the composite image
            ax.imshow(composite_image)
            ax.axis('off')

            # Set the titles for the original and adversarial images
            ax.text(0.25, -0.1, 'Original Image', transform=ax.transAxes, ha='center')
            ax.text(0.75, -0.1, 'Adversarial Image', transform=ax.transAxes, ha='center')

            # Save the composite image to a file
            img_path = os.path.join(payload['report_path'], f"{payload['attackName']}.png")
            plt.savefig(img_path)

            # Show the plot
            # plt.show()
            plt.close()

            del composite_image
            return 
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "generateImage", e, apiEndPoint, errorRequestMethod)
    

    def getcurrentDirectory():
        try:
            root_path = os.getcwd()
            directories = root_path.split(os.path.sep)
            srcFlag = False

            for i in range(len(directories)-1, -1, -1):
                if directories[i] == 'app':
                    srcFlag = True
                    break
            if srcFlag == True:
                src_index = directories.index("app")
                new_path = os.path.sep.join(directories[:src_index])
            else:
                new_path = os.getcwd()

            return new_path
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "getcurrentDirectory", e, apiEndPoint, errorRequestMethod)


    def isContentSafe(payload):
        try:
            for key, value in payload.items():
                if(type(value) != str):
                    return False
                for char in value:
                    if(char!='-' and char!='_' and char!=' ' and (char.isalnum()==False)):
                        return False
            return True
        except Exception as e:
            log.info(e)
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "isContentSafe", e, apiEndPoint, errorRequestMethod)
    