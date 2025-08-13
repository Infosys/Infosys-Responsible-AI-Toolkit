'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


import logging
import datetime,time
import requests
from src.mappers.mappers import GetAttackDataRequest
from src.service.art import Art
#from src.service.augly import Augly
from src.service.artendpoint import ArtEndPoint
from src.config.urls import UrlLinks
import shutil
import json
import os
import csv
import re

from src.service.utility import Utility as UT
from src.config.logger import CustomLogger
from src.service.defence import Defence as DF

from src.dao.Batch import Batch
from src.dao.DataDb import Data
from src.dao.DatabaseConnection import DB
from src.dao.ModelDb import Model
from src.dao.ModelAttributesDb import ModelAttributes
from src.dao.ModelAttributesValuesDb import ModelAttributesValues
from src.dao.Html import Html
from src.dao.SaveFileDB import FileStoreDb

from src.dao.Security.AttackDb import Attack
from src.dao.Security.AttackAttributesDb import AttackAttributes
from src.dao.Security.AttackAttributesValuesDb import AttackAttributesValues
from src.dao.Security.SecReportDb import SecReport
import concurrent.futures as con

securitypdfgenerationip = os.getenv("SECURITYPDFGENERATIONIP")
log = CustomLogger()

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

class Infosys:
    
    
    # SelectedModel : str = "Dummy"
    SelectedModel : float = 0.0

    ArtSupportedModel:list = sorted(["ProjectedGradientDescentTabular","ZerothOrderOptimization",
                            "QueryEfficient", "Deepfool", 
                            "Wasserstein", "Boundary", 
                            'CarliniL2Method', 'Pixel', 
                            'UniversalPerturbation', 'FastGradientMethod', 
                            'SpatialTransformation', 'Square', 
                            'MembershipInferenceRule', 'ProjectGradientDescentImage', 
                            'BasicIterativeMethod', 'SaliencyMapMethod',
                            'DecisionTree', 'IterativeFrameSaliency',
                            'SimBA', 'NewtonFool','AttributeInference',
                            'InferenceLabelOnlyGap', 'ElasticNet',
                            'Poisoning', 'AttributeInferenceWhiteBoxDecisionTree',
                            'AttributeInferenceWhiteBoxLifestyleDecisionTree',
                            'LabelOnlyDecisionBoundary','HopSkipJumpTabular',
                            "HopSkipJumpImage", 'MembershipInferenceBlackBox',
                            "QueryEfficientGradientAttackEndPoint", 'BoundaryAttackEndPoint',
                            'HopSkipJumpAttackEndPoint', 'LabelOnlyGapAttackEndPoint',
                            'MembershipInferenceBlackBoxRuleBasedAttackEndPoint',
                            'LabelOnlyDecisionBoundaryAttackEndPoint',
                            'MembershipInferenceBlackBoxAttackEndPoint','VirtualAdversarialMethod', 
                            'GeometricDecisionBasedAttack','Threshold','Augly'])
    
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

    # -------------------------------------------------------------------------------------------------

    def logUI(payload):
        {   
            "level": 5,   
            "additional": [],   
            "message":"Error",   
            "timestamp":"2020-02-02T11:42:40.153Z",   
            "fileName":"main.js",   
            "lineNumber": 87,   
            "columnNumber": 26
        }

        return ''
        
    # -------------------------------------------------------------------------------------------------

    def getavailableAttack():

        try:
            if(UrlLinks.Assessment_Generation==False):
                return sorted(["ProjectedGradientDescentTabular","ZerothOrderOptimization",
                                "QueryEfficient", "Deepfool", 
                                "Wasserstein", "Boundary", 
                                'CarliniL2Method', 'Pixel', 
                                'UniversalPerturbation', 'FastGradientMethod', 
                                'SpatialTransformation', 'Square', 
                                'MembershipInferenceRule', 'ProjectGradientDescentImage', 
                                'BasicIterativeMethod', 'SaliencyMapMethod',
                                'DecisionTree', 'IterativeFrameSaliency',
                                'SimBA', 'NewtonFool','AttributeInference',
                                'InferenceLabelOnlyGap', 'ElasticNet',
                                'Poisoning', 'AttributeInferenceWhiteBoxDecisionTree',
                                'AttributeInferenceWhiteBoxLifestyleDecisionTree',
                                'LabelOnlyDecisionBoundary','HopSkipJumpTabular',
                                "HopSkipJumpImage", 'MembershipInferenceBlackBox',
                                "QueryEfficientGradientAttackEndPoint", 'BoundaryAttackEndPoint',
                                'HopSkipJumpAttackEndPoint', 'LabelOnlyGapAttackEndPoint',
                                'MembershipInferenceBlackBoxRuleBasedAttackEndPoint',
                                'LabelOnlyDecisionBoundaryAttackEndPoint',
                                'MembershipInferenceBlackBoxAttackEndPoint','VirtualAdversarialMethod',
                                'GeometricDecisionBasedAttack','Threshold','Augly'])
            else:
                return ["extraction","evasion"]
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "getavailableAttack", e, apiEndPoint, errorRequestMethod)
    
    # -------------------------------------------------------------------------------------------------

    def getAttackFuncs(payload):
        try:
            # Reading Payload based on modelid then find attack based on datatype and classifier
            attributesData = {
                'targetClassifier':payload['targetClassifier'],
                'targetDataType':payload['targetDataType']
            }

            # Reading AttackName from AttackDb base on above requirements
            classifierList = AttackAttributesValues.findall({'AttackAttributeValues':attributesData["targetClassifier"]})
            dataList = AttackAttributesValues.findall({'AttackAttributeValues':attributesData["targetDataType"]})
            attackid_list = [d.get('AttackId') for d in dataList]
            exact_attackid_list = [d for d in classifierList if d.get('AttackId') in attackid_list]
            attacks_fun = []
            for d in exact_attackid_list:
                valuesList = AttackAttributesValues.findall(
                            {
                                'AttackId':d['AttackId']
                            }
                        )
                for k in valuesList:
                    if k['AttackAttributeValues'] == attributesData["targetClassifier"]:
                        continue
                    if k['AttackAttributeValues'] == attributesData["targetDataType"]:
                        continue
                    else:
                        attacks_fun.append(k['AttackAttributeValues'])

            del classifierList,dataList,attackid_list,exact_attackid_list
            return sorted(attacks_fun)
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "getAttackFuncs", e, apiEndPoint, errorRequestMethod)



    def addAttack(Payload:GetAttackDataRequest):
    
        try:
            Payload = AttributeDict(Payload)
            keys = Payload.keys()
            if(len(Payload.attackName) < 1):
                return "NULL value restricted!"

            # added data in AttackDb, AttackAttributesDb, AttackAttributesValuesDb
            attack_data = Attack.mycol.find_one({"AttackName":Payload.attackName})
            if attack_data:
                return 'Attack Already Exists'
            else:
                attackId = Attack.create({"attackName":Payload.attackName})
                for key in keys:
                    if(key == "attackName"):
                        pass
                    else:
                        attackAttributesId = AttackAttributes.create({"attackAttributeName":key})
                        attackAttributesValuesId = AttackAttributesValues.create({"attackAttributeId":attackAttributesId,"attackId":attackId,"attackAttributeValues":Payload[key]})

                return "Attack Added Sucessfully"
        
        except Exception as exc:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(UT.log_error_to_telemetry, "addAttack", exc, apiEndPoint, errorRequestMethod)
            return "Attack Addition Failed! Please Try Again"
    
    

    def deleteAttack(payload):

        try:
            attackattributesvalues_list = AttackAttributesValues.findall({'AttackAttributeValues':payload['attackName']})
            if len(attackattributesvalues_list) < 1 :
                return "No Attack Available to Delete"
            else:
                # delete from AttackAttributesValuesDb
                attackattributesvalues_list = AttackAttributesValues.findall({'AttackAttributeValues':payload['attackName']})
                attackId = attackattributesvalues_list[0]['AttackId']
                attackattributeId = attackattributesvalues_list[0]['AttackAttributeId']
                attackattributeValueId = attackattributesvalues_list[0]['AttackAttributeValuesId']
                AttackAttributesValues.delete({'AttackAttributeValuesId':attackattributeValueId})
                
                # delete from AttackAttributesDb
                AttackAttributes.delete({'AttackAttributeId':attackattributeId})

                # delete from AttackDb
                Attack.delete({'AttackId':attackId})

                del attackattributesvalues_list
                return "Attack Deleted Sucessfully"
        except Exception as exc:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "deleteAttack", exc, apiEndPoint, errorRequestMethod)
            return "Oops! Unable to Delete Attack, Please Try After Sometime."
    
   # -------------------------------------------------------------------------------------------------
         
    def setAttack(payload):
        
        try:
            if(payload['modelUrl'] in Infosys.ArtSupportedModel):
                
                AttackFunction = payload['modelUrl']

                if(AttackFunction == "ProjectedGradientDescentTabular"):
                    response = Art.ProjectedGradientDescentZoo(payload['batchId'])
                elif(AttackFunction == "ZerothOrderOptimization"):
                    response = Art.ZooAttackVectors(payload['batchId'])
                elif(AttackFunction == "QueryEfficient"):
                    response = Art.QueryEfficient(payload['batchId'])
                elif(AttackFunction == "Deepfool"):
                    response = Art.DeepfoolAttack(payload['batchId'])  
                elif(AttackFunction == "Wasserstein"):
                    response = Art.WassersteinAttack(payload['batchId'])
                elif(AttackFunction == "Boundary"):
                    response = Art.BoundaryAttack(payload['batchId'])
                elif(AttackFunction == "CarliniL2Method"):
                    response = Art.CarliniAttack(payload['batchId'])
                elif(AttackFunction == 'Pixel'):
                    response = Art.PixelAttack(payload['batchId'])
                elif(AttackFunction == 'UniversalPerturbation'):
                    response = Art.UniversalPerturbationAttack(payload['batchId'])
                elif(AttackFunction == 'FastGradientMethod'):
                    response = Art.FastGradientMethodAttack(payload['batchId'])
                elif(AttackFunction == 'SpatialTransformation'):
                    response = Art.SpatialTransformation(payload['batchId'])
                elif(AttackFunction == 'Square'):
                    response = Art.SquareAttack(payload['batchId'])
                elif(AttackFunction == 'AttributeInference'): 
                    response = Art.AttributeInference(payload['batchId'])
                elif(AttackFunction == 'MembershipInferenceBlackBox'):
                    response = Art.MembershipInferenceBlackBox(payload['batchId'])
                elif(AttackFunction == 'MembershipInferenceRule'):
                    response = Art.MembershipInferenceRule(payload['batchId'])
                elif(AttackFunction == 'ProjectGradientDescentImage'):
                    response = Art.ProjectGradientDescentAttack(payload['batchId'])
                elif(AttackFunction == 'BasicIterativeMethod'):
                    response = Art.BasicIterativeMethodAttack(payload['batchId'])
                elif(AttackFunction == 'SaliencyMapMethod'):
                    response = Art.SaliencyMapMethodAttack(payload['batchId'])
                elif(AttackFunction == 'DecisionTree'):
                    response = Art.DecisionTreeAttackVectors(payload['batchId'])
                elif(AttackFunction == 'IterativeFrameSaliency'):
                    response = Art.IterativeFrameSaliencyAttack(payload['batchId'])
                elif(AttackFunction == 'SimBA'):
                    response = Art.SimbaAttack(payload['batchId'])
                elif(AttackFunction == 'NewtonFool'):
                    response = Art.NewtonFoolAttack(payload['batchId'])
                elif(AttackFunction == 'InferenceLabelOnlyGap'):
                    response = Art.InferenceLabelOnlyAttack(payload['batchId'])
                elif(AttackFunction == 'ElasticNet'):
                    response = Art.ElasticNetAttack(payload['batchId'])
                # elif(AttackFunction == "Poisoning"):
                #     response = Art.PoisoningAttackSVM(payload['batchId'])
                elif(AttackFunction == "AttributeInferenceWhiteBoxDecisionTree"):
                    response = Art.AttributeInferenceWhiteBoxDecisionTreeAttack(payload['batchId'])
                elif(AttackFunction == "AttributeInferenceWhiteBoxLifestyleDecisionTree"):
                    response = Art.AttributeInferenceWhiteBoxLifestyleDecisionTreeAttack(payload['batchId'])
                elif(AttackFunction == "LabelOnlyDecisionBoundary"):
                    response = Art.LabelOnlyDecisionBoundaryAttack(payload['batchId'])
                elif(AttackFunction == "HopSkipJumpTabular"):
                    response = Art.HopSkipJumpCSV(payload['batchId'])
                # elif(AttackFunction == "HopSkipJumpImage"):
                #     response = Art.HopSkipJumpImage(payload['batchId'])
                elif(AttackFunction == "QueryEfficientGradientAttackEndPoint"):
                    response = ArtEndPoint.QueryEfficientGradientAttack(payload['batchId'])
                elif(AttackFunction == "BoundaryAttackEndPoint"):
                    response = ArtEndPoint.BoundaryAttack(payload['batchId'])
                elif(AttackFunction == "HopSkipJumpAttackEndPoint"):
                    response = ArtEndPoint.HopSkipJumpAttack(payload['batchId'])
                elif(AttackFunction == "LabelOnlyGapAttackEndPoint"):
                    response = ArtEndPoint.LabelOnlyGapAttack(payload['batchId'])
                elif(AttackFunction == "MembershipInferenceBlackBoxRuleBasedAttackEndPoint"):
                    response = ArtEndPoint.MembershipInferenceBlackBoxRuleBasedAttack(payload['batchId'])
                elif(AttackFunction == "LabelOnlyDecisionBoundaryAttackEndPoint"):
                    response = ArtEndPoint.LabelOnlyDecisionBoundaryAttack(payload['batchId'])
                elif(AttackFunction == "MembershipInferenceBlackBoxAttackEndPoint"):
                    response = ArtEndPoint.MembershipInferenceBlackBoxAttack(payload['batchId'])
                # elif(AttackFunction == 'VirtualAdversarialMethod'):
                #     response = Art.VirtualAdversarialMethod(payload['batchId'])
                # elif(AttackFunction == "GeometricDecisionBasedAttack"):
                #     response = Art.GeometricDecisionAttack(payload['batchId'])
                # elif(AttackFunction == 'Threshold'):
                #     response = Art.Threshold(payload['batchId']) 
                elif(AttackFunction == "Augly"):
                    response = Augly.Augly(payload['batchId'])   
                return response
            
        except Exception as exc:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "setAttack", exc, apiEndPoint, errorRequestMethod)
            return {"Oops! Something is Wrong With Input, Please Retry!"}
            
    # -------------------------------------------------------------------------------------------------

class Bulk:


    def loadApi():

        try:
            mydb=DB.connect()
            collist = mydb.list_collection_names()
    
            f=open(r"src/config/attack.json",'r')
            attackList=json.loads(f.read())
            if 'Attack' not in collist:
                log.info("AttackList---",attackList)
                for attack in attackList:
                    X = Infosys.addAttack(attack)
            
            return
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "loadApi", e, apiEndPoint, errorRequestMethod)
    


    def batchAttack(payload): 

        try:
            root_path = os.getcwd()
            root_path = UT.getcurrentDirectory() + "/database"
            dirList = ["data","model","payload","report"]
            for dir in dirList:
                dirs = root_path + "/" + dir
                if not os.path.exists(dirs):
                    os.mkdir(dirs)
            payload = AttributeDict(payload)
            
            response = Infosys.setAttack({"batchId":payload["batchId"], "modelUrl":payload["modelUrl"]})["Job_Id"]
            response = Bulk.sanitize_filenameorfoldername(response)
            #response is folder name only
            report_path = root_path + "/report"
            report_path = os.path.join(report_path,response+".zip")
            reportid:any
            if(os.getenv("DB_TYPE") == "mongo"):
                file = open(report_path,'rb')
                with FileStoreDb.fs.new_file(_id=str(time.time()),filename=response.split('_')[0]+".zip",contentType="zip") as f:
                    shutil.copyfileobj(file,f)
                    reportid=f._id
                    time.sleep(1)
                file.close()
            else:
                file = open(report_path,'rb')
                responses = requests.post(url =upload_file, files ={"file":(response.split('_')[0]+".zip", file)}, data ={"container_name":zip_container}).json()
                reportid = responses["blob_name"]
                file.close()

            # # Reading BatchId from SecBatchDtlDb and storing in SecReportDb
            secReportId = SecReport.create({'reportId':reportid,'batchId':payload["batchId"],'reportname':response.split('_')[0]})
            
            shutil.rmtree(os.path.join(root_path + "/report",response))
            UT.databaseDelete(report_path)

            del response,file
            return payload["batchId"]
        except Exception as exc:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "batchAttack", exc, apiEndPoint, errorRequestMethod)
            return {"Oops! Something is Wrong With Input, Please Retry!"}

    def sanitize_filenameorfoldername(filename):
        try:
            # Allow only alphanumeric characters, underscores, and hyphens
            if not re.match(r'^[\w\-]+$', filename):
                raise ValueError("Invalid filename: only alphanumeric characters, underscores, and hyphens are allowed.")
            return filename
        except Exception as exc:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "sanitize_filenameorfoldername", exc, apiEndPoint, errorRequestMethod) 

    def combinereport(payload):

        try:
            root_path = UT.getcurrentDirectory() + "/database"
            dirList = ["data","model","payload","report"]
            for dir in dirList:
                dirs = root_path + "/" + dir
                if not os.path.exists(dirs):
                    os.mkdir(dirs)

            # Reading modelId, dataId, tenetId from Batch Table
            batchList = Batch.findall({'BatchId':payload['batchid']})[0]
            modelList = Model.findall({'ModelId':batchList['ModelId']})[0]
            dataList = Data.findall({'DataId':batchList['DataId']})[0]

            modelName = modelList['ModelName']
            modelid = modelList['ModelId']
            modelendPoint = modelList['ModelEndPoint']
            foldername = f'{modelName}'
            foldername = Bulk.sanitize_filenameorfoldername(foldername)
            report_path = root_path + "/report"
            report_path = os.path.join(report_path,foldername)
            if os.path.isdir(report_path):    
                if os.path.isfile(report_path) or os.path.islink(report_path):
                    os.remove(report_path)  # remove the file
                elif os.path.isdir(report_path):
                    shutil.rmtree(report_path)  # remove dir and all contains
            os.mkdir(report_path)

            # reading origional datafile
            model, model_path, modelName, modelFramework = UT.readModelFile(payload['batchid'])
            raw_data, data_path = UT.readDataFile({'BatchId':payload['batchid'], 'model':model ,'modelFramework':modelFramework})

            # fetching targetClassifier after reading payload path from mongodb
            Payload_path = UT.readPayloadFile(batchList['BatchId'])
            payload_folder_path =  UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path, modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            payload_data = json.loads(data)
            payload_data["modelEndPoint"] = modelendPoint

            #  Reading Report file from MongoDB and stroing in Database Folder.
            count = UT.combineReportFile({'batchid':payload['batchid'],'modelName':modelName,'report_path':report_path,'attackList':payload['attackList']})
            
            # get all applicable attack and arrange in list of dictionary
            total_attacks = Infosys.getAttackFuncs({'targetClassifier':payload_data['targetClassifier'],'targetDataType':payload_data['dataType']})
            
            # creating defence model for combining report
            if payload_data['dataType'] == 'Tabular':
                # originaldataContent = FileStoreDb.findOne(Model.findOne(modelid)['SampleDataID'])
                # original_data_path = os.path.join(report_path,originaldataContent["fileName"]) 
                # if os.path.exists(original_data_path):                          
                #     os.remove(original_data_path)                                       
                # with open(original_data_path, 'wb') as f:
                #     f.write(originaldataContent["data"])

                original_data_path = os.path.join(report_path, os.path.basename(data_path))
                with open(data_path, 'r') as source_file:
                    reader = csv.reader(source_file)
                    with open(original_data_path, 'w', newline='') as output_file:
                        writer = csv.writer(output_file)
                        for row in reader:
                            writer.writerow(row)

                
                # DF.generateCombinedDenfenseModel({'payloadData':payload_data, 'report_path':report_path, 'modelName':modelName, 'dataFileName':originaldataContent["fileName"].split('.')[0]})
                # DF.generateCombinedDenfenseModel({'payloadData':payload_data, 'report_path':report_path, 'modelName':modelName, 'dataFileName':os.path.basename(data_path).split('.')[0]})
                confusion_matrix, classification_reports, attack_accuracy_dict = DF.generateCombinedDenfenseModel({'payloadData':payload_data, 'report_path':report_path, 'modelName':modelName, 'dataFileName':os.path.basename(data_path).split('.')[0]})
                UT.databaseDelete(original_data_path)

                # print(list(os.listdir(report_path)))
                # statusList,defenceList = UT.checkAttackListStatus1({'folder_path':report_path, 'modelName':modelName})
                statusList,defenceList = UT.checkAttackListStatus({'folder_path':report_path, 'modelName':modelName, 'attackList':payload['attackList'], 'meta_data':payload_data, 'attack_accuracy_dict':attack_accuracy_dict})
                # print(defenceList)
                # print(statusList)
                rows, mitigation_row, attack_list = UT.makeAttackListRow({'total_attacks':total_attacks,'attackList':payload['attackList'],'statusList':statusList,'defenceList':defenceList, 'meta_data':payload_data})
                # print(attack_list)

            elif payload_data['dataType'] == 'Image':
                # print(list(os.listdir(report_path)))
                # statusList,defenceList = UT.checkAttackListStatus1({'folder_path':report_path, 'modelName':modelName})
                statusList = UT.checkAttackListStatus({'folder_path':report_path, 'modelName':modelName, 'attackList':payload['attackList'], 'meta_data':payload_data})
                # print(statusList)
                rows, attack_list = UT.makeAttackListRow({'total_attacks':total_attacks,'attackList':payload['attackList'],'statusList':statusList, 'meta_data':payload_data})
                # print(attack_list)

            # adding summary content and combine graph in combine html
            success_skipped_list = [len(total_attacks), count, (len(total_attacks)-count)]

            # taking dateTime depend on server
            # report_datetime = UT.dateTimeFormat()

            # generating confusion matrix for tabular
            if payload_data['dataType'] == 'Tabular':
                # confusion_matrix = UT.confusionMatrix({'folder_path':report_path, 'modelName':modelName, 'attackList':payload['attackList'], 'meta_data':payload_data})
            
                #creating combined report file ".html"
                # report_datetime = datetime.datetime.now()
                report_datetime = payload['dateTime']
                UT.graphForCombineAttack({'folder_path':report_path, 'modelName':modelName, 'model_metaData':payload_data, 'reportTime':report_datetime, 'success_skipped':success_skipped_list, 'target':payload_data['groundTruthClassLabel'], 'rows':rows, 'attack_list':attack_list, 'confusion_matrix':confusion_matrix, 'mitigation_row':mitigation_row, 'classification_reports':classification_reports})
            
            elif payload_data['dataType'] == 'Image':
                #creating combined report file ".html"
                # report_datetime = datetime.datetime.now()
                report_datetime = payload['dateTime']
                UT.graphForCombineAttack({'folder_path':report_path, 'modelName':modelName, 'model_metaData':payload_data, 'reportTime':report_datetime, 'success_skipped':success_skipped_list, 'target':payload_data['groundTruthClassLabel'], 'rows':rows, 'attack_list':attack_list})

            # removing all non attack image
            if payload_data['dataType'] == 'Image': 
                for filename in os.listdir(report_path):
                    if any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                        if filename.split('.')[0].split('^')[1][-1] == 'F':
                            img_path = os.path.join(report_path, filename)
                            UT.databaseDelete(img_path)
                        elif filename.split('.')[0].split('^')[1][-1] == 'T':
                            img_old_path = os.path.join(report_path, filename)
                            # print('img_old_path',img_old_path)
                            img_new_path = img_old_path.replace(os.path.basename(img_old_path),f"{os.path.basename(img_old_path).split('.')[0][:-1]}.{os.path.basename(img_old_path).split('.')[-1]}")
                            # print('img_new_path',img_new_path)
                            os.rename(img_old_path, img_new_path)
                            # print(img_new_path)

                            # img_new_path = os.path.join(report_path, f"{filename.split('.')[0][:-1]}.{filename.split('.')[-1]}")
                            # with open(img_old_path, 'rb') as old_file:
                            #     with open(img_new_path, 'wb') as new_file:
                            #         shutil.copyfileobj(old_file, new_file)
                            # print(img_new_path)

                            UT.databaseDelete(img_old_path)

            # Segregating adversial sample base on their type
            UT.createAttackFolder({'report_path':report_path, 'attack_list':attack_list})
            shutil.make_archive(report_path,'zip',report_path)

            report_path = os.path.join(report_path+".zip")
            reportid = time.time()
            if(os.getenv("DB_TYPE") == "mongo"):
                file = open(report_path,'rb')
                with FileStoreDb.fs.new_file(_id=str(reportid),filename=foldername+".zip",contentType="zip") as f:
                    shutil.copyfileobj(file,f)
                    reportid=f._id
                    time.sleep(1)
                file.close()
            else:
                file = open(report_path,'rb')
                responses = requests.post(url =upload_file, files ={"file":(foldername+".zip", file)}, data ={"container_name":zip_container}).json()
                reportid = responses["blob_name"]
                file.close()
            # Storing Report in Html Table
            data = {
                    "HtmlId": time.time(), 
                    "BatchId": batchList['BatchId'],
                    "TenetId": batchList['TenetId'],
                    "ReportName": foldername+'.zip',
                    "HtmlFileId": reportid,
                    "ContentType": "application/zip",
                    "CreatedDateTime": datetime.datetime.now(),
                }
            Html.create(data)

            shutil.rmtree(os.path.join(root_path + "/report",foldername))
            UT.databaseDelete(data_path)
            UT.databaseDelete(model_path)
            UT.databaseDelete(report_path)
            UT.databaseDelete(Payload_path)
            
            del batchList,modelList,dataList,model,modelName,modelFramework,raw_data,total_attacks,success_skipped_list,file,data
            return {'combineReportFileId':reportid}
        
        except Exception as exc:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "combinereport", exc, apiEndPoint, errorRequestMethod)

    
    
    def runAllAttack(payload):
        
        try:  
            api_start_time = time.perf_counter()
            # Reading modelId, dataId, tenetId from Batch Table
            batchList = Batch.findall({'BatchId':payload['batchid']})[0]
            
            #  Reading ModelAttribute content and stroing in attributesData.
            attributesData = {}
            attributeValues = ModelAttributesValues.findall({"ModelId":batchList['ModelId']})
            for value in attributeValues:
                attributes = ModelAttributes.findall({"ModelAttributeId":value.ModelAttributeId})[0]
                attributesData[attributes["ModelAttributeName"]] = value.ModelAttributeValues
            
            # Reading all attacks
            attacks_fun_list = attributesData['appAttacks']

            # Updating metadata Status of Batch Table
            Batch.update(batchList['BatchId'], {'Status':'InProgress...'})

            # Reading AttackName from AttackDb base on above requirements
            attackList = []
            for attack in attacks_fun_list:
                try:
                    d = {}
                    Payload = {"batchId":batchList['BatchId'], "modelUrl":attack}
                    log.info("-"*80)
                    log.info(f"Attack: {attack}")
                    start_time = time.perf_counter()
                    batchid = Bulk.batchAttack(Payload)
                    end_time = time.perf_counter()
                    total_time = end_time - start_time
                    log.info("{:^20} {:^20} {:^20}".format("Start time", "End time", "Total time(sec)"))
                    log.info("{:^20.2f} {:^20.2f} {:^20.2f}".format(start_time, end_time, total_time))
                    log.info("-"*80)
                    if attack in UT.AttackTypes['Art']['Evasion']:
                        d['type'] = 'Evasion'
                        d['name'] = attack
                    elif attack in UT.AttackTypes['Art']['Inference']:
                        d['type'] = 'Inference'
                        d['name'] = attack
                    elif attack in UT.AttackTypes['Augly']['Augmentation']:
                        d['type'] = 'Augmentation'
                        d['name'] = attack
                    attackList.append(d)
                except Exception as e:
                    log.info(e)

            # sorting attacks base on attack-type 
            attackList = sorted(attackList, key=lambda x: x['type'])
            attackList = [x['name'] for x in attackList]

            combineReportId = Bulk.combinereport({'batchid':batchList['BatchId'],'attackList':attackList, 'dateTime':payload['dateTime']})
            
            if combineReportId:
                try:
                    # now Html content  store in Report Table
                    url = securitypdfgenerationip + '/v1/report/converttopdfreport'
                    data = {
                        'batchId':payload['batchid']
                    }
                    log.info('Trying Connection To PDF-Conversion APIs ...')
                    response = requests.post(url, data=data)
                    log.info(f"After PDF-Conversion: {response}")

                    if response.status_code == 200:
                        log.info("Request successfull!")
                        log.info(f"Response--- {response.status_code}")

                        # Updating metadata of LastUpdatedDateTime from SecBatchDtlDb Table
                        Batch.update(batchList['BatchId'], {'LastUpdatedDateTime':datetime.datetime.now()})

                        # Updating metadata Status of Batch Table
                        Batch.update(batchList['BatchId'], {'Status':'Completed'})

                        api_end_time = time.perf_counter()
                        api_total_time = api_end_time - api_start_time
                        log.info("-"*40)
                        log.info("{:^20} {:^20} {:^20}".format("Api Start time", "Api End time", "Api Total time(sec)"))
                        log.info("{:^20.2f} {:^20.2f} {:^20.2f}".format(api_start_time, api_end_time, api_total_time))
                        log.info("-"*40)

                    elif response.status_code == 422:
                        log.info("Unprocessable Entity")
                        log.info(f"{response.json()}")
                    else:
                        log.info(f"Request failed with status code: {response.status_code}")
                        log.info(f"{response.text}")
                    
                    del batchList,attributesData,attributeValues,attacks_fun_list,attackList
                    return payload['batchid']
                except Exception as exe:
                    log.info(exe)
            else:
                return 'Oops! Failed to generate Combined Report...'
        except Exception as exe:
            log.info(exe)
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "runAllAttack", exe, apiEndPoint, errorRequestMethod)
            return {"runAllAttack api failed"}
    
    # -------------------------------------------------------------------------------------------------
