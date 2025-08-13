"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import json
import datetime
import time
import os
#import pdfkit
import matplotlib.pyplot as plt
from fairness.mappers.mappers import BiasAnalyzeResponse, BiasPretrainMitigationResponse, BiasPretrainMitigationResponseUseCase,BiasResults, IndividualFairnessRequest, \
    metricsEntity
from aif360.datasets import StandardDataset
from fairness.constants.local_constants import *
from fairness.config.logger import CustomLogger
import pandas
from fastapi import HTTPException  
log = CustomLogger()
from infosys_responsible_ai_fairness.responsible_ai_fairness import BiasResult, DataList, MitigationResult, PRETRAIN, utils,StandardDataset, metricsEntity
from fairness.service.service_utils import Utils
from fairness.Telemetry.Telemetry_call import SERVICE_getLabels_Individual_METADATA 
import numpy as np


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class FairnessServiceUpload:
    MITIGATED_LOCAL_FILE_PATH="../output/MitigatedData/"
    MITIGATED_UPLOAD_PATH="responsible-ai//responsible-ai-fairness//MitigatedData"
    DATASET_LOCAL_FILE_PATH="../output/UItoNutanixStorage/"
    DATASET_UPLOAD_FILE_PATH="responsible-ai//responsible-ai-fairness//Fairness_ui"
    DATASET_WB_LOCAL_FILE_PATH="../output/"
    LOCAL_FILE_PATH="../output/datasets/"
    MODEL_LOCAL_PATH='../output/model/'
    MITIGATED_MODEL_LOCAL_PATH='../output/mitigated_model/'
    AWARE_MODEL_LOCAL_PATH='../output/aware_model/'
    MODEL_UPLOAD_PATH='responsible-ai//responsible-ai-fairness//model'
    MITIGATED_MODEL_UPLOAD_PATH='responsible-ai//responsible-ai-fairness//mitigated-model'
    AWARE_MODEL_UPLOAD_PATH='responsible-ai//responsible-ai-fairness//aware-model'

    def __init__(self):
        self.utils = Utils()
    
    def pretrainedAnalyse(traindata, labelmap, label, protectedAttributes, favourableOutcome,
                          CategoricalAttributes, features, biastype, methods,flag):
        
        ds = DataList()
        datalist = ds.getDataList(traindata, labelmap, label, protectedAttributes, favourableOutcome,
                                  CategoricalAttributes, features, biastype,flag)
        biasResult = BiasResult()
        list_bias_results = biasResult.analyzeResult(biastype, methods, protectedAttributes, datalist)
        return list_bias_results
    
    def posttrainedAnalyse(testdata, label,predLabel, labelmap, protectedAttributes, taskType, methods,flag):
        ds = DataList()
        group_unpriv_ts, group_priv_ts, df_preprocessed,df_orig = ds.preprocessDataset(testdata, label, labelmap,
                                                                               protectedAttributes, taskType,flag,predLabel)
        predicted_y = df_preprocessed[predLabel]
        actual_y = df_preprocessed["label"]
        biasResult = BiasResult()
        list_bias_results = biasResult.analyseHoilisticAIBiasResult(taskType, methods, group_unpriv_ts,
                                                                    group_priv_ts, predicted_y, actual_y,
                                                                    protectedAttributes)
        log.info(f"list_bias_results: {list_bias_results}")

        return list_bias_results
    
    def preprocessingmitigateandtransform(traindata, labelmap, label, protectedAttributes, favourableOutcome,
                          CategoricalAttributes, features, biastype, methods, mitigationTechnique,flag):
        ds = DataList()
        datalist = ds.getDataList(traindata, labelmap, label, protectedAttributes, favourableOutcome,
                                  CategoricalAttributes, features, biastype,flag)
        biasResult = BiasResult()
        list_bias_results = biasResult.analyzeResult(biastype, methods, protectedAttributes, datalist)
        mitigated_df = biasResult.mitigateAndTransform(datalist,protectedAttributes,mitigationTechnique)
        log.info(list_bias_results)
        return list_bias_results,mitigated_df



    
    def analyze(payload: dict) -> BiasAnalyzeResponse:
        log.info("***************Entering Analyse*************")
        log.debug(f"payload: {payload}")
        methods = payload.method
        biastype = payload.biasType
        trainingDataset = AttributeDict(payload.trainingDataset)
        tpath = AttributeDict(trainingDataset.path).uri
        label = trainingDataset.label
        predLabel=payload.predictionDataset['predlabel']
        predictionDataset = AttributeDict(payload.predictionDataset)
        ppath = AttributeDict(predictionDataset.path).uri
        features = payload.features.split(",")
        protectedAttributes = payload.facet
        CategoricalAttributes = payload.categoricalAttributes
        if CategoricalAttributes == ' ':
            CategoricalAttributes = []
        else:
            CategoricalAttributes = CategoricalAttributes.split(',')
        favourableOutcome = [str(i) for i in payload.favourableOutcome]
        outputPath = AttributeDict(payload.outputPath).uri
        labelmap = payload.labelmaps
        if biastype == "POSTTRAIN":
            label = predictionDataset.label
        attr = {"name": [], "privileged": [], "unprivileged": []}
        for i in protectedAttributes:
            i = AttributeDict(i)
            log.info("=", i)
            attr["name"] += [i.name]
            attr["privileged"] += [i.privileged]
            attr['unprivileged'] += [i.unprivileged]
        protectedAttributes = AttributeDict(attr)
        taskType = payload.taskType
        train_df=pandas.read_csv(tpath,sep=",", usecols=features)
        pred_features = features
        if biastype=="POSTTRAIN":
            pred_features=features.append("labels_pred")
        df=pandas.read_csv(ppath,sep=",", usecols=pred_features)

        list_bias_results = None
        if biastype == "PRETRAIN":
            list_bias_results = FairnessServiceUpload.pretrainedAnalyse(train_df, labelmap, label,
                                                                  protectedAttributes, favourableOutcome,
                                                                  CategoricalAttributes, features, biastype,
                                                                  methods, True)
        elif biastype == "POSTTRAIN":
            list_bias_results = FairnessServiceUpload.posttrainedAnalyse(df, label,predLabel,labelmap,
                                                                   protectedAttributes, taskType, methods, True)

        objbias_pretrainanalyzeResponse = BiasAnalyzeResponse(biasResults=list_bias_results)
        json_object = objbias_pretrainanalyzeResponse.json()
        log.info(f'json_object:{json_object}')
        return objbias_pretrainanalyzeResponse

    
    def preprocessingmitigate(payload: dict) -> BiasPretrainMitigationResponse:
        log.info("************Entering preprocessingMitigation************")
        methods = payload.method
        biastype = payload.biasType
        mitigationType = payload.mitigationType
        mitigationTechnique = payload.mitigationTechnique
        taskType = payload.taskType
        fileName = payload.filename
        extension = os.path.splitext(fileName)[1][1:]
        trainingDataset = AttributeDict(payload.trainingDataset)
        fileType = trainingDataset.fileType
        trainingDatasetpath = AttributeDict(trainingDataset.path).uri
        label = trainingDataset.label
        features = payload.features.split(",")
        protectedAttributes = payload.facet
        CategoricalAttributes = payload.categoricalAttributes
        if CategoricalAttributes == ' ':
            CategoricalAttributes = []
        else:
            CategoricalAttributes = CategoricalAttributes.split(',')
        favourableOutcome = [str(i) for i in payload.favourableOutcome]
        outputPath = AttributeDict(payload.outputPath).uri
        labelmap = payload.labelmaps
        attr = {"name": [], "privileged": [], "unprivileged": []}
        for i in protectedAttributes:
            i = AttributeDict(i)
            log.info("=", i)
            attr["name"] += [i.name]
            attr["privileged"] += [i.privileged]
            attr['unprivileged'] += [i.unprivileged]
        df=pandas.read_csv(trainingDatasetpath,sep=",", usecols=features)
        protectedAttributes = AttributeDict(attr)
        list_bias_results = None
        if mitigationType == "PREPROCESSING":

            Preprocessing_mitigation_result_list,mitigated_df = FairnessServiceUpload.preprocessingmitigateandtransform(df, labelmap, label,
                                                              protectedAttributes, favourableOutcome,
                                                              CategoricalAttributes, features,
                                                              biastype, methods, mitigationTechnique,True)
        
        utils=Utils()
        mitigated_df_cat=mitigated_df.copy()
        mitigated_df_cat=utils.modifyDf(mitigated_df_cat,protectedAttributes,labelmap,label)
        fileName=payload.filename
        uniqueNm_orig = "mitigated"+str(fileName).split('.')[0] + "_" + \
            datetime.datetime.now().strftime("%m%d%Y%H%M%S")+"."+extension
        uniqueNm_modify = "mitigated_modify_"+str(fileName).split('.')[0] + "_" + \
            datetime.datetime.now().strftime("%m%d%Y%H%M%S")+"."+extension
        filePath_orig=FairnessServiceUpload.MITIGATED_LOCAL_FILE_PATH+uniqueNm_orig
        filePath_modify=FairnessServiceUpload.MITIGATED_LOCAL_FILE_PATH+uniqueNm_modify
        FairnessUIserviceUpload.pretrain_save_file(mitigated_df,extension,filePath_orig)
        FairnessUIserviceUpload.pretrain_save_file(mitigated_df_cat,extension,filePath_modify)
        objbias_pretrainanalyzeResponse = BiasPretrainMitigationResponseUseCase(biasResults=Preprocessing_mitigation_result_list,fileName=[uniqueNm_orig,uniqueNm_modify])
        json_object = objbias_pretrainanalyzeResponse.json()
        log.info(f'json_object: {json_object}')
        return objbias_pretrainanalyzeResponse



class FairnessUIserviceUpload:
    def __init__(self, MockDB=None):
        self.utils = Utils() 
    
    def get_data_frame(extension: str,fileName: str):
        # if extension == "csv":
        return  pandas.read_csv(os.path.join(FairnessServiceUpload.LOCAL_FILE_PATH, fileName))
    
    def pretrain_save_file(df: pandas.DataFrame, extension:str,file_path: str):
        if extension == "csv":
            df.to_csv(file_path, index=False)
        elif extension == "parquet":
             df.to_parquet(file_path, index=False)
        elif extension == "json":
             df.to_json(file_path, index=False,orient= 'records')
        elif extension == "feather":
             df.to_feather(file_path)
              
    def upload_file(self,payload:dict):
        log.info(payload,"payload*************")
        enter_time = time.time()
        log.info("Entering Upload:", enter_time)
        ca_dict = {}
        ca_dict.clear()
        biasType = payload["biasType"]
        request_payload = ""
        request_payload = open("../output/UIanalyseRequestPayloadUpload.txt").read()
        request_payload = request_payload.replace('{biasType}', biasType)
        methodType = payload["methodType"]
        request_payload = request_payload.replace('{method}', methodType)
        taskType = payload["taskType"]
        request_payload = request_payload.replace('{taskType}', taskType)
        file = payload["file"]
        label = payload["label"]
        predLabel=payload["predLabel"]
        favourableOutcome = payload["FavourableOutcome"]
        protectedAttribute = payload["ProtectedAttribute"]
        priv = payload["priviledged"]
        fileName = file.filename
        log.info("File Name:", fileName)
        extension = os.path.splitext(fileName)[1][1:]
        log.info("Extension:", extension)
        request_payload = request_payload.replace('{fileName}', fileName)
        x = fileName.rfind(".")
        name_of_dataset = fileName[:x]
        request_payload = request_payload.replace('{name}', name_of_dataset)
        fileContentType = file.content_type
        dataFile = file.file
        uniqueNm = name_of_dataset+"_" + datetime.datetime.now().strftime("%m%d%Y%H%M%S")+"."+extension
        self.utils.store_file_locally(extension,dataFile,FairnessServiceUpload.LOCAL_FILE_PATH,uniqueNm)  
        read_file=pandas.read_csv(os.path.join(FairnessServiceUpload.LOCAL_FILE_PATH,uniqueNm))
        trainingDatasetURL = os.path.join(FairnessServiceUpload.LOCAL_FILE_PATH,uniqueNm)
        predictionDatasetURL = trainingDatasetURL
        request_payload = request_payload.replace('{trainingDatasetURL}',trainingDatasetURL)
        request_payload = request_payload.replace('{predictionDatasetURL}',predictionDatasetURL)
        feature_list = list(read_file.columns)
        request_payload = request_payload.replace('{features}',','.join(feature_list))
        st_ti = time.time()
        log.info("Entering CA Dict:", st_ti)
        updated_df = read_file.select_dtypes(exclude='number')
        for each in list(updated_df.columns):
            updated_df.drop(updated_df[(updated_df[each] == '?')].index, inplace=True)
            updated_df[each] = updated_df[each].str.replace('.', '')
            ca_dict[each] = list(updated_df[each].unique())
        log.info("list of columns remaining in dataset after exclusion : ", updated_df.columns)
        ex_ti = time.time()
        log.info("Exit CA Dict:", ex_ti - st_ti)
        categorical_attribute = ','.join(list(updated_df.columns))
        request_payload = request_payload.replace('{categoricalAttributes}',categorical_attribute)
        request_payload = request_payload.replace("{label}", label)
        request_payload = request_payload.replace("{predlabel}", predLabel)
        request_payload = request_payload.replace("{favourableOutcome}",favourableOutcome)
        log.info(ca_dict, "ca_dict")
        log.info(label,"label")
        outcomeList = ca_dict[label]
        log.info(outcomeList,"outcomeList")
        outcomeList.remove(favourableOutcome)
        unfavourableOutcome = ''.join(outcomeList)
        request_payload = request_payload.replace("{unfavourableOutcome}",unfavourableOutcome)
        log.info("Request Payload:", request_payload)
        request_payload_json = json.loads(request_payload)
        priv_list = priv
        if len(priv_list) != len(protectedAttribute):
            raise HTTPException(
                status_code=400, detail="Priviledged attribute count should be equal to protected attribute count")
        log.info("Priv_list", priv_list)
        ca_list = list(ca_dict.keys())
        ca_list.remove(label)

        protected_attribute_list = []

        for pa in protectedAttribute:
            attribute_values = ca_dict[pa]
            log.info("attributed_values:", attribute_values)
            ca_list.remove(pa)
            request = {}
            request["name"] = pa
            priv_each_list = []
            for priv_list_ in priv_list:
                for each in priv_list_:
                    if each in attribute_values:
                        priv_each_list.append(each)
                        attribute_values.remove(each)
                        log.info("Request after each turn:", request)
            request["privileged"] = priv_each_list
            request["unprivileged"] = attribute_values
            protected_attribute_list.append(request)

        log.info("Facets:"+str(protected_attribute_list))

        request_payload_json["facet"] = protected_attribute_list
        request_payload_json["categoricalAttributes"] = ','.join(ca_list)
        log.info("JSON OBJECT IN get attributes: "+str(request_payload_json))

        request_payload_json = AttributeDict(request_payload_json)
        if FairnessUIserviceUpload.validate_json_request(request_payload_json):
            response = FairnessServiceUpload.analyze(request_payload_json)
            if response is None:
                # raise CustomHTTPException(SERVICE_upload_file_singleendpoint_METADATA,"Response is not received from POST request")
                raise HTTPException(status_code=500, detail="Response is not received from POST request")
        else:
            response = "Please Input Correct Parameters."
        ca_dict.clear()
        return response

    def upload_file_Premitigation(self,payload: dict):
        log.info(f"{payload}payload")
        enter_time = time.time()
        log.info(f"Entering Upload:{enter_time}")
        ca_dict={}
        pretrain_payload = ""
        pretrain_payload = open("../output/UIPretrainMitigationPayloadUpload.txt").read() 
        mitigationType= payload["MitigationType"]
        pretrain_payload = pretrain_payload.replace('{mitigationType}', mitigationType)
        mitigationTechnique=payload["MitigationTechnique"]
        pretrain_payload = pretrain_payload.replace('{mitigationTechnique}', mitigationTechnique)
        taskType = payload["taskType"]

        pretrain_payload = pretrain_payload.replace('{taskType}', taskType)
        file = payload["file"]
        fileName = file.filename
        log.info(f"File Name:{fileName}")
        extension = os.path.splitext(fileName)[1][1:]
        log.info(f"Extension:{extension}")
        pretrain_payload = pretrain_payload.replace('{filename}', fileName)
        x = fileName.rfind(".")
        name_of_dataset = fileName[:x]
        pretrain_payload = pretrain_payload.replace('{name}', name_of_dataset)
        fileContentType = file.content_type
        dataFile = file.file
        uniqueNm= name_of_dataset+ datetime.datetime.now().strftime("%m%d%Y%H%M%S")
        
        self.utils.store_file_locally(extension,dataFile,FairnessServiceUpload.LOCAL_FILE_PATH,uniqueNm) 
        read_file=pandas.read_csv(os.path.join(FairnessServiceUpload.LOCAL_FILE_PATH,uniqueNm))
        #convert to dataframe   
        trainingDatasetURL = os.path.join(FairnessServiceUpload.LOCAL_FILE_PATH,uniqueNm)
        predictionDatasetURL = trainingDatasetURL
        pretrain_payload = pretrain_payload.replace('{trainingDatasetURL}',trainingDatasetURL)
        pretrain_payload = pretrain_payload.replace('{predictionDatasetURL}',predictionDatasetURL)

        feature_list = list(read_file.columns)
        pretrain_payload = pretrain_payload.replace('{features}',','.join(feature_list))
       
        # to create dictionary of CA present in dataset
        st_ti = time.time()
        log.info(f"Entering CA Dict:{st_ti}")
        updated_df = read_file.select_dtypes(exclude='number')
        for each in list(updated_df.columns):
            updated_df.drop(updated_df[(updated_df[each] == '?')].index, inplace=True)
            updated_df[each] = updated_df[each].str.replace('.', '')
            ca_dict[each] = list(updated_df[each].unique())
        
        log.info(f"list of columns remaining in dataset after exclusion : {updated_df.columns}")
        ex_ti = time.time()
        log.info(f"Exit CA Dict:{ex_ti - st_ti}")
        categorical_attribute = ','.join(list(updated_df.columns))
        pretrain_payload = pretrain_payload.replace('{categoricalAttributes}',categorical_attribute)
        label = payload["label"]
        favourableOutcome = payload["FavourableOutcome"]
        protectedAttribute = payload["ProtectedAttribute"]
        priv = payload["priviledged"]
        pretrain_payload = pretrain_payload.replace("{label}", label)
        pretrain_payload = pretrain_payload.replace("{favourableOutcome}",favourableOutcome)
        outcomeList = ca_dict[label]
        outcomeList.remove(favourableOutcome)
        unfavourableOutcome = ''.join(outcomeList)
        pretrain_payload = pretrain_payload.replace("{unfavourableOutcome}",unfavourableOutcome)
        log.info(f"Request Payload:{pretrain_payload}")
        # Convert request_payload to a dictionary
        pretrain_payload_json = json.loads(pretrain_payload)
        labelmap = {}
        for value in ca_dict[label]:
            if (value == favourableOutcome):
                labelmap[value]= '1'
            else:
                labelmap[value] = '0'  

        # request_payload_json = json.loads(pretrainMitigation_payload)
        priv_list = priv

        ca_list = list(ca_dict.keys())
        ca_list.remove(label)

        protected_attribute_list = []

        for pa in protectedAttribute:
            attribute_values = ca_dict[pa]
            log.info(f"attributed_values:{attribute_values}")
            ca_list.remove(pa)
            request = {}
            request["name"] = pa
            priv_each_list = []
            for priv_list_ in priv_list:
                for each in priv_list_:
                    if each in attribute_values:
                        priv_each_list.append(each)
                        attribute_values.remove(each)
                        log.info(f"Request after each turn:{request}")
            request["privileged"] = priv_each_list
            request["unprivileged"] = attribute_values
            protected_attribute_list.append(request)


        log.info(f"Facets: {protected_attribute_list}")

        pretrain_payload_json["facet"] = protected_attribute_list
        pretrain_payload_json["categoricalAttributes"] = ','.join(ca_list)
        log.info(f"JSON OBJECT IN get attributes: {pretrain_payload_json}")

        pretrain_payload_json = AttributeDict(pretrain_payload_json)
        log.info(f"pretrain_payload_json{pretrain_payload_json}")
        # request_payload_json = AttributeDict(request_payload_json)
        if FairnessUIserviceUpload.validate_pretrain_json_request(pretrain_payload_json):
            response = FairnessServiceUpload.preprocessingmitigate(pretrain_payload_json)
            if response is None:
                # raise CustomHTTPException(SERVICE_upload_file_Premitigation_METADATA,"Response is not received from POST request")
                raise HTTPException(status_code=500, detail="Response is not received from POST request")

        else:
            response = "Please Input Correct Parameters."

        return response        
    

    def getLabels_Individual(self,payload:dict):
        log.info(f"{payload}payload")
        file= payload["file"]
        k=payload["k"]
        log.info(f"{file}file")
        labels = payload["label"]
        log.info(f"{labels}label")
        fileName = file.filename
        log.info(f"File Name:{fileName}")

        extension = os.path.splitext(fileName)[1][1:]

        x = fileName.rfind(".")
        name_of_dataset = fileName[:x]
        log.info(f"name_of_dataset{name_of_dataset}")
        fileContentType = file.content_type
        dataFile = file.file
        uniqueNm = name_of_dataset + datetime.datetime.now().strftime("%m%d%Y%H%M%S")+"."+extension
   
        self.utils.store_file_locally(extension,dataFile,FairnessServiceUpload.LOCAL_FILE_PATH,uniqueNm)    
        #convert to dataframe   
        read_file = FairnessUIserviceUpload.get_data_frame(extension,uniqueNm)
        # local_path=FairnessServiceUpload.LOCAL_FILE_PATH+ uniqueNm
        # save_file = read_file.to_csv(local_path, index=False)
        # local_file_name=uniqueNm
        
        feature_list = list(read_file.columns)
        features_dict={}
         # to create dictionary of CA present in dataset
        st_ti = time.time()
        log.info(f"Entering CA Dict:{st_ti}")
        updated_df = read_file
        log.info(f"list of columns remaining in dataset after exclusion :  {updated_df.columns}")
        # save in db
        log.info(features_dict)
        local_file_name=uniqueNm
        _, extension = os.path.splitext(local_file_name)
        read_file = FairnessUIserviceUpload.get_data_frame(extension.lstrip('.'),local_file_name)
        dataset_list=[]
        categorical_features = read_file.select_dtypes(include='object').columns.tolist()
        #remove labels from categorical attributes
        for label in labels:
            if label in categorical_features:
                categorical_features.remove(label)
        
        for label in labels:
            df=read_file.copy()
            #drop labels other than the current label, so that it will not be considered for fairness
            for label_2 in labels:
                if label!=label_2:
                    df=df.drop(label_2,axis=1)
            log.info(f"{df}df")
            log.info(f"{label}label")
            #customize StandardDataset just for Individual fairness, as we are not considering protected attributes
            dataset_orig=StandardDataset(df=df, label_name=label, favorable_classes=[df[label][0]],
                                       protected_attribute_names=[],
                                       privileged_classes=[np.array([])],
                                       categorical_features=categorical_features,
                                       features_to_keep=[], features_to_drop=[],
                                       na_values=[], custom_preprocessing=None,
                                       metadata={})
            dataset_list.append(dataset_orig)
       
        response=[]
        scores=[]
        util=utils()
        for dataset in dataset_list:
            score_dict={}
            score = np.round(util.consistency(dataset,k), 2)
            scores.append(score)
            obj_metric_cs = metricsEntity(name='CONSISTENCY',
                                          description='Individual fairness metric that measures how similar the labels are for similar instances. Score ranges from [0,1], where 1 indicates consistent labels for similar instances.',
                                          value=float(score[0]))
            
            score_dict[dataset.label_names[0]]=obj_metric_cs.metricsEntity
            response.append(score_dict)
        log.info(f"Response: {response}")
        # return json.dumps(response)
        if response is None:
            raise HTTPException(SERVICE_getLabels_Individual_METADATA,"Response is not received from POST request")

        return response
    
    def get_mitigated_data(self,fileName):
        local_file_path = os.path.join(FairnessServiceUpload.MITIGATED_LOCAL_FILE_PATH, fileName)
        if os.path.exists(local_file_path):
            return local_file_path
        else:
            raise HTTPException(status_code=404, detail="File not found")


    def validate_json_request(payload):
        log.info(f"Payload:test{payload}")
        chk_lst = []
        methods = payload.method
        chk_lst.append(methods)
        biastype = payload.biasType
        chk_lst.append(biastype)
        taskType = payload.taskType
        chk_lst.append(taskType)
        trainingDataset = AttributeDict(payload.trainingDataset)
        chk_lst.append(trainingDataset)
        tpath = AttributeDict(trainingDataset.path).uri
        chk_lst.append(tpath)
        label = trainingDataset.label
        chk_lst.append(label)

        predictionDataset = AttributeDict(payload.predictionDataset)
        chk_lst.append(predictionDataset)
        ppath = AttributeDict(predictionDataset.path).uri
        chk_lst.append(ppath)
        predlabel = predictionDataset.predlabel
        chk_lst.append(predlabel)
        features = payload.features.split(",")
        chk_lst.append(features)
        protectedAttributes = payload.facet
        chk_lst.append(protectedAttributes)
        CategoricalAttributes = payload.categoricalAttributes
        chk_lst.append(CategoricalAttributes)
        favourableOutcome = [str(i) for i in payload.favourableOutcome]
        chk_lst.append(favourableOutcome)
        outputPath = AttributeDict(payload.outputPath).uri
        chk_lst.append(outputPath)
        labelmap = payload.labelmaps
        chk_lst.append(labelmap)

        for each in chk_lst:
            if len(each) != 0:
                JSON_CREATED = True
            else:
                JSON_CREATED = False

        return JSON_CREATED

    
    def validate_pretrain_json_request(payload):
        chk_lst = []
        methods = payload.method
        chk_lst.append(methods)
        biastype = payload.biasType
        chk_lst.append(biastype)
        taskType = payload.taskType
        chk_lst.append(taskType)
        trainingDataset = AttributeDict(payload.trainingDataset)
        chk_lst.append(trainingDataset)
        tpath = AttributeDict(trainingDataset.path).uri
        chk_lst.append(tpath)
        label = trainingDataset.label
        chk_lst.append(label)

        features = payload.features.split(",")
        chk_lst.append(features)
        protectedAttributes = payload.facet
        chk_lst.append(protectedAttributes)
        CategoricalAttributes = payload.categoricalAttributes
        chk_lst.append(CategoricalAttributes)
        favourableOutcome = [str(i) for i in payload.favourableOutcome]
        chk_lst.append(favourableOutcome)
        outputPath = AttributeDict(payload.outputPath).uri
        chk_lst.append(outputPath)
        labelmap = payload.labelmaps
        chk_lst.append(labelmap)

        for each in chk_lst:
            if len(each) != 0:
                JSON_CREATED = True
            else:
                JSON_CREATED = False

        return JSON_CREATED
    