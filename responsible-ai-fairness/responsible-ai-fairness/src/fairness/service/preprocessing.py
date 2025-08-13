"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import io
from fairness.dao.bias_model import Bias, TrainingDataset, PredictionDataset
from fairness.dao.mitigation_model import Mitigation, TrainingDataset
from infosys_responsible_ai_fairness.responsible_ai_fairness import BiasResult, DataList, MitigationResult, PRETRAIN, utils, StandardDataset
from infosys_responsible_ai_fairness.responsible_ai_fairness import metricsEntity as me
import openai
import numpy as np
from bson import ObjectId
from fairness.dao.individual_fairness import Individual_Fairness
from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
from fairness.dao.llm_analysis import LlmAnalysis
from fairness.dao.model_mitigation_mapper import MitigationModel
from fairness.dao.databaseconnection import DataBase
from io import StringIO, BytesIO
from fastapi.responses import FileResponse, StreamingResponse
from sklearn.metrics import accuracy_score
from fairlearn.metrics import demographic_parity_difference, equalized_odds_difference, true_positive_rate, true_negative_rate, false_positive_rate, false_negative_rate
from fairlearn.postprocessing import ThresholdOptimizer
import joblib
import json
import datetime
import time
import os
# import pdfkit
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import requests
from sklearn.neighbors import NearestNeighbors

from fairness.dao.WorkBench.FileStoreDb import FileStoreReportDb
from fairness.dao.WorkBench.databaseconnection import DataBase_WB
from fairness.mappers.mappers import BiasAnalyzeResponse, BiasAnalyzeRequest, BiasPretrainMitigationResponse, BiasResults, IndividualFairnessRequest, \
    metricsEntity, MitigateBiasRequest, MitigationAnalyzeResponse, PreprocessingMitigationAnalyzeResponse, PreprocessingMitigateBiasRequest, BatchId, BiasAnalyzeMetrics, BiasAnalyzeIndividualMetric
from fairness.exception.exception import FairnessException, FairnessUIParameterNotFoundError
from aif360.datasets import StandardDataset
from aif360.metrics import BinaryLabelDatasetMetric
from fairness.dao.WorkBench.Tenet import Tenet
from fairness.dao.WorkBench.Batch import Batch
from fairness.dao.WorkBench.html import Html
from fairness.dao.WorkBench.report import Report
from fairness.dao.WorkBench.Data import Dataset, DataAttributes, DataAttributeValues
from fairness.constants.local_constants import *
from fairness.constants.llm_constants import OPENAI, GPT_4
from fairness.config.logger import CustomLogger
from fairness.service.service_utils import Utils
import pandas
from fastapi import HTTPException

log = CustomLogger()


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class FairnessServicePreproc:
    MITIGATED_LOCAL_FILE_PATH="../output/MitigatedData/"
    MITIGATED_UPLOAD_PATH="responsible-ai//responsible-ai-fairness//MitigatedData"
    LOCAL_FILE_PATH="../output/datasets/"

    def __init__(self, db=None):
        if db is not None:
            self.db = db
            self.fileStore = FileStoreReportDb(self.db)
            self.batch =  Batch(self.db)
            self.tenet =  Tenet(self.db)
            self.dataset = Dataset(self.db)
            self.dataAttributes = DataAttributes(self.db)
            self.dataAttributeValues = DataAttributeValues(self.db)
        else:
            self.db = DataBase().db
            self.fileStore = FileStoreReportDb()
            self.batch =  Batch()
            self.tenet =  Tenet()
            self.dataset = Dataset()
            self.dataAttributes = DataAttributes()
            self.dataAttributeValues = DataAttributeValues()
        self.utils = Utils()
        self.bias_collection = self.db['bias']
        self.mitigation_collection = self.db['mitigation']
        self.fairness_collection = self.db['fs.files']


    def pretrained_Analyse(traindata, labelmap, label, protectedAttributes, favourableOutcome,
                          CategoricalAttributes, features, biastype, methods, flag):
        ds = DataList()
        datalist = ds.getDataList(traindata, labelmap, label, protectedAttributes, favourableOutcome,
                                  CategoricalAttributes, features, biastype, flag)
        biasResult = BiasResult()
        list_bias_results = biasResult.analyzeResult(
            biastype, methods, protectedAttributes, datalist)
        return list_bias_results

    
    def posttrained_Analyse(testdata, label, labelmap, protectedAttributes, taskType, methods, flag,predLabel="labels_pred"):
        ds = DataList()
        group_unpriv_ts, group_priv_ts, df_preprocessed, df_orig = ds.preprocessDataset(testdata, label, labelmap,
                                                                                        protectedAttributes, taskType, flag,predLabel)
        predicted_y = df_preprocessed[predLabel]
        actual_y = df_preprocessed["label"]
        biasResult = BiasResult()
        list_bias_results = biasResult.analyseHoilisticAIBiasResult(taskType, methods, group_unpriv_ts,
                                                                    group_priv_ts, predicted_y, actual_y,
                                                                    protectedAttributes)
        log.info(f"list_bias_results: {list_bias_results}")

        return list_bias_results
    
    def preprocessingmitigateandtransform(traindata, labelmap, label, protectedAttributes, favourableOutcome,
                                          CategoricalAttributes, features, biastype, methods, mitigationTechnique, flag):

        log.info("****************************preprocessingmitigateandtransform**********")
        ds = DataList()
        datalist = ds.getDataList(traindata, labelmap, label, protectedAttributes, favourableOutcome,
                                  CategoricalAttributes, features, biastype, flag)
        
        biasResult = BiasResult()

        list_bias_results = biasResult.analyzeResult(
            biastype, methods, protectedAttributes, datalist)
        mitigated_df = biasResult.mitigateAndTransform(
            datalist, protectedAttributes, mitigationTechnique)
        return list_bias_results, mitigated_df
    


    def analyze_Fn(self, payload: dict, batchId, individual_fairness= None, dataset=None) -> (BiasAnalyzeResponse,BiasAnalyzeMetrics,BiasAnalyzeIndividualMetric):
        log.info(payload)
        log.info("***************Entering Analyse*************")

        log.debug(f"payload: {payload}")
        methods = payload.method
        biastype = payload.biasType
        fileId = payload.fileid
        file_type = "text/csv"
        df = dataset
        label = payload.label
        predLabel=payload.predictionDataset['predlabel']
        features = payload.features.split(",")
        protectedAttributes = payload.facet
        CategoricalAttributes = payload.categoricalAttributes
        if CategoricalAttributes == ' ':
            CategoricalAttributes = []
        else:
            CategoricalAttributes = CategoricalAttributes.split(',')
        favourableOutcome = [str(i) for i in payload.favourableOutcome]
        # outputPath = AttributeDict(payload.outputPath).uri
        labelmap = payload.labelmaps
        if biastype == "POSTTRAIN":
            label = payload.label

        attr = {"name": [], "privileged": [], "unprivileged": []}
        for i in protectedAttributes:
            i = AttributeDict(i)
            log.info(f"{i}")
            attr["name"] += [i.name]
            attr["privileged"] += [i.privileged]
            attr['unprivileged'] += [i.unprivileged]
        unprivileged = attr['unprivileged']

        protectedAttributes = AttributeDict(attr)
        taskType = payload.taskType
        tenet_id = self.tenet.find(tenet_name='Fairness')
        batch_details = self.batch.find(batch_id=batchId, tenet_id=tenet_id)
        datasetId = batch_details['DataId']
        dataset_attribute_ids = self.dataAttributes.find(dataset_attributes=[
                                                    'biasType', 'methodType', 'taskType', 'protectedAttribute', 'privilegedGroup'])
        log.info(f"Dataset Attribute Ids:{dataset_attribute_ids}")
        dataset_attribute_values = self.dataAttributeValues.find(
            dataset_id=datasetId, dataset_attribute_ids=dataset_attribute_ids, batch_id=batchId)
        log.info(f"Dataset Attribute Values: {dataset_attribute_values}")

        list_bias_results = None
        if biastype == "PRETRAIN" and methods != "CONSISTENCY" and methods == "ALL":
            list_bias_results = FairnessServicePreproc.pretrained_Analyse(df, labelmap, label,
                                                                  protectedAttributes, favourableOutcome,
                                                                  CategoricalAttributes, features, biastype,
                                                                  methods, True)
            individual_data = None
            #get the results of individual_fairness
            if methods == "ALL" :
                #get the results of individual_fairness
                individual_fairness=individual_fairness.result()
                individual_data = [item['income-per-year'] for item in individual_fairness if 'income-per-year' in item]
            objbias_pretrainanalyzeResponse = BiasAnalyzeMetrics(
                biasResults=list_bias_results, individualMetrics=individual_data)
        elif biastype == "PRETRAIN" and methods != "ALL" and methods != "CONSISTENCY":
            list_bias_results = FairnessServicePreproc.pretrained_Analyse(df, labelmap, label,
                                                                  protectedAttributes, favourableOutcome,
                                                                  CategoricalAttributes, features, biastype,
                                                                  methods, True)
            objbias_pretrainanalyzeResponse = BiasAnalyzeResponse(
                biasResults=list_bias_results)

        elif biastype == "PRETRAIN" and methods == "CONSISTENCY":
            individual_fairness=individual_fairness.result()
            individual_data = [item['income-per-year'] for item in individual_fairness if 'income-per-year' in item]
            objbias_pretrainanalyzeResponse = BiasAnalyzeIndividualMetric(individualMetrics=individual_data)

        elif biastype == "POSTTRAIN":
            list_bias_results = FairnessServicePreproc.posttrained_Analyse(df, label, labelmap,
                                                                   protectedAttributes, taskType, methods, True,predLabel)

            objbias_pretrainanalyzeResponse = BiasAnalyzeResponse(
                biasResults=list_bias_results)
        json_object = objbias_pretrainanalyzeResponse.json(exclude_none=True)
        # if Condition returns metric results, else will work with batchid and return the response
        if batchId == None:
            return objbias_pretrainanalyzeResponse
        else:
            local_file_path = '../output/' + "sample.json"
            # self.utils.save_as_json_file(
            #     local_file_path, list_bias_results,individual_fairness)
            if biastype == "PRETRAIN" and methods != "CONSISTENCY" and methods == "ALL":
                self.utils.save_as_json_file(
                local_file_path, list_bias_results,individual_fairness)
                html = self.utils.json_to_html(list_bias_results,individual_fairness,label,dataset_attribute_values,unprivileged)
            elif biastype == "PRETRAIN" and methods != "ALL" and methods != "CONSISTENCY":
                self.utils.save_as_json_file(
                local_file_path, list_bias_results,None)
                html = self.utils.json_to_html(list_bias_results,None,label,dataset_attribute_values,unprivileged)
            elif biastype == "PRETRAIN" and methods == "CONSISTENCY":
                self.utils.save_as_json_file_obj(
                local_file_path,individual_fairness)
                html = self.utils.json_to_html_individualMetric(individual_fairness,label,dataset_attribute_values,unprivileged)
            else:
                self.utils.save_as_json_file(
                local_file_path, list_bias_results,None)
                html=self.utils.json_to_html(list_bias_results,None,predLabel,dataset_attribute_values,unprivileged)
            local_file_path = "../output/fairness_report.html"
            self.utils.save_html_to_file(html, local_file_path)
            # reportId= self.fileStore.save_file(file=html)
            tenet_id = self.tenet.find(tenet_name='Fairness')
            html_containerName = os.getenv('HTML_CONTAINER_NAME')
            htmlFileId = self.fileStore.save_file(file=BytesIO(html.encode(
                'utf-8')), filename='fairness_report.html', contentType='text/html', tenet='Fairness', container_name=html_containerName)
            HtmlId = time.time()
            doc = {
                'HtmlId': HtmlId,
                'BatchId': batchId,
                'TenetId': tenet_id,
                'ReportName': 'fairness_report.html',
                'HtmlFileId': htmlFileId,
                'CreatedDateTime': datetime.datetime.now(),
            }
            Html.create(doc)

            url = os.getenv("REPORT_URL")
            payload = {"batchId": batchId}
            response = requests.request(
                "POST", url, data=payload, verify=False).json()
            return objbias_pretrainanalyzeResponse



    def preprocessingmitigate(self, payload: dict,batchId=None,dataset=None, extension = None) -> BiasPretrainMitigationResponse:
        log.info("************Entering preprocessingMitigation************")
        log.debug(f"payload: {payload}")
        methods = payload.method
        biastype = payload.biasType
        mitigationType = payload.mitigationType
        mitigationTechnique = payload.mitigationTechnique
        taskType = payload.taskType
        label = payload.label
        df = dataset
        extensions = extension
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
            log.info("= {i}")
            attr["name"] += [i.name]
            attr["privileged"] += [i.privileged]
            attr['unprivileged'] += [i.unprivileged]



        protectedAttributes = AttributeDict(attr)
    
        if mitigationType == "PREPROCESSING":
            Preprocessing_mitigation_result_list,mitigated_df = FairnessServicePreproc.preprocessingmitigateandtransform(df, labelmap, label,
                                                                                                                   protectedAttributes, favourableOutcome,
                                                                                                                   CategoricalAttributes, features,
                                                                                                                   biastype, methods, mitigationTechnique, True)
        log.info(f"{mitigated_df}mitigated df ")
        log.info(f"{Preprocessing_mitigation_result_list}Preprocessing_mitigation_result_list")                                                                                                                                                                                                 

        # upload data to MongoDB
        fileName = payload.filename
        uniqueNm = "mitigated_data"+"."+ extensions
        mitigate_data = mitigated_df.to_csv(index=False)
        dt_containerName = os.getenv('Dt_containerName')
        fileId=self.fileStore.save_file(file=mitigate_data.encode('utf-8'),filename=uniqueNm, contentType = extensions, tenet='Fairness',container_name=dt_containerName)
        ReportId = time.time()
        tenet_id = 2.2
        doc = {
                'ReportId': ReportId,
                'BatchId': batchId,
                'TenetId': tenet_id,
                'ReportName': uniqueNm,
                'ReportFileId': fileId,
                'ContentType': 'csv',
                'CreatedDateTime': datetime.datetime.now()
            }
        Report.create(doc)
        # FairnessService.uploadfile_to_mongodb(uploadPath,filePath,fileType)
        objbias_pretrainanalyzeResponse = BiasPretrainMitigationResponse(biasResults=Preprocessing_mitigation_result_list,fileName=uniqueNm)
        json_object = objbias_pretrainanalyzeResponse.json()
        # log.info('json_object:', json_object)
        return objbias_pretrainanalyzeResponse, fileId

    

    # Get mitigated data using MONGO DB
    def get_mitigated_data(self, fileName):
        log.info("fileName:", fileName)
        content = self.fileStore.read_file(fileName)
        response = StreamingResponse(io.BytesIO(file['data']), media_type="text/csv")

        return response

class FairnessUIservicePreproc:
    def __init__(self, MockDB=None):
        if MockDB is not None:
            self.db = MockDB.db
            self.fileStore = FileStoreReportDb(self.db)
            self.batch =  Batch(self.db)
            self.tenet =  Tenet(self.db)
            self.dataset = Dataset(self.db)
            self.dataAttributes = DataAttributes(self.db)
            self.dataAttributeValues = DataAttributeValues(self.db)

        else:
            self.db = DataBase().db
            self.fileStore = FileStoreReportDb()
            self.batch =  Batch()
            self.tenet =  Tenet()
            self.dataset = Dataset()
            self.dataAttributes = DataAttributes()
            self.dataAttributeValues = DataAttributeValues()
            log.info("database")
                    
        self.utils = Utils()
        self.bias_collection = self.db['bias']
        self.mitigation_collection = self.db['mitigation']
        self.mitigation_model_collection = self.db['mitigation_model']
        self.metrics_collection = self.db['metrics']
        self.llm_analysis_collection = self.db['llm_analysis']
        self.llm_connection_credentials_collection = self.db['llm_connection_credentails']

    request_payload = ""
    mitigation_payload = ""
    pretrainMitigation_payload = ""
    ca_dict = {}

    def analyse_UploadFile(self, payload: dict):
        fileId = payload["fileId"]
        file_type = "text/csv"
        log.debug("Reading file from database..........")
        enter_time = time.time()
        retrivedata = self.fileStore.read_file(fileId)
        if retrivedata is None:
            raise HTTPException(status_code=500, detail="No content received from the POST request")
        name_of_dataset = retrivedata["name"].split('.')[0]
        exit_time = time.time()
        log.info(f"Reading file completed in:{exit_time - enter_time}")
        # filename = self.fileStore.getfilename(fileId)

        dataset = pandas.read_csv(BytesIO(retrivedata['data']))

        biasType = payload["biasType"]
        methodType = payload["methodType"]
        taskType = payload["taskType"]
        # x = filename.rfind(".")
        # name_of_dataset = filename[:x]
        fileContentType = "text/csv"
        feature_list = list(dataset.columns)
        # to create dictionary of CA present in dataset
        updated_df = dataset.select_dtypes(exclude='number')
        udf_columns = list(updated_df.columns)
        categorical_values = {}
        for each in udf_columns:
            updated_df.drop(
                updated_df[(updated_df[each] == '?')].index, inplace=True)
            updated_df[each] = updated_df[each].str.replace('.', '')
            categorical_values[each] = list(updated_df[each].unique())
        log.info(f"list of columns remaining in dataset after exclusion :{updated_df.columns}")
        categorical_attribute = ','.join(list(updated_df.columns))
        log.info(f"JSON OBJECT IN UPLOAD: {FairnessUIservicePreproc.request_payload}")
        response = {
            "biasType": biasType,
            "methodname": methodType,
            "FileName": name_of_dataset,
            "UploadedFileType": fileContentType,
            "AttributesInTheDataset": {"FeatureList ": feature_list,
                                       "CategoricalAttributesList": udf_columns},
            "CategoricalAttributesUniqueValues": categorical_values
        }
        if response is None:
            raise HTTPException(status_code=500, detail="No response received from the POST request")

        return response


    def get_Pretrain_Analyze(self,payload:dict,dataset):
        
        fileId = payload["sampleData"]
        biasType = payload["biasType"]
        methodType = payload["methodType"]
        taskType = payload['taskType']
        label = payload['label']
        favourableOutcome = payload["favorableOutcome"]
        protectedAttribute = payload["protectedAttribute"]
        priv = payload['privilegedGroup']
        predLabel=payload["predLabel"]
        k=payload["knn"]
        log.info(f"biasType:, {biasType}, methodType:, {methodType}, taskType:, {taskType}, label:, {label}, favourableOutcome:, {favourableOutcome}, protectedAttribute:, {protectedAttribute}, priv:, {priv},predLabel:,{predLabel}")            
        retrivedata = self.fileStore.read_file(fileId)
        if retrivedata is None:
            raise HTTPException(status_code=500, detail="No content received from the POST request")

        name_of_dataset = retrivedata["name"].split('.')[0]
        priv_list = priv
        if len(priv_list) != len(protectedAttribute):
            raise HTTPException(
                status_code=400, detail="Priviledged attribute count should be equal to protected attribute count")
        log.info(f"Priv_list{priv_list}")


        feature_list = list(dataset.columns)
        # to create dictionary of CA present in dataset
        categorical_values = {}
        st_ti = time.time()
        log.info(f"Entering CA Dict:{st_ti}")
        updated_df = dataset.select_dtypes(exclude='number')
        for each in list(updated_df.columns):
            updated_df.drop(
                updated_df[(updated_df[each] == '?')].index, inplace=True)
            updated_df[each] = updated_df[each].str.replace('.', '')
            categorical_values[each] = list(updated_df[each].unique())

        outcomeList = categorical_values[label]
        outcomeList.remove(favourableOutcome)
        unfavourableOutcome = ''.join(outcomeList)

        ca_list = list(categorical_values.keys())
        ca_list.remove(label)

        protected_attribute_list = []

        for pa in protectedAttribute:
            attribute_values = categorical_values[pa]
            ca_list.remove(pa)
            request = {}
            request["name"] = pa
            priv_each_list = []
            for priv_list_ in priv_list:
                for each in priv_list_:
                    if each in attribute_values:
                        priv_each_list.append(each)
                        attribute_values.remove(each)
                        log.info(f"Request after each turn: {request}")
            request["privileged"] = priv_each_list
            request["unprivileged"] = attribute_values
            protected_attribute_list.append(request)

        log.info(f"Facets:{protected_attribute_list}")
        categorical_attribute = ','.join(list(updated_df.columns))
        facet = protected_attribute_list
        categoricalAttributes = ','.join(ca_list)
        # ...................................................................................................

        request_payload = ""
        request_payload = open(
            "../output/UIanalyseRequestPayload.txt").read()
        request_payload = request_payload.replace(
            '{name}', name_of_dataset)
        request_payload = request_payload.replace(
            '{fileid}', fileId)
        request_payload = request_payload.replace(
            '{biasType}', biasType)

        request_payload = request_payload.replace(
            '{method}', methodType)

        request_payload = request_payload.replace(
            '{taskType}', taskType)

        request_payload = request_payload.replace(
            '{fileName}', name_of_dataset)
        request_payload = request_payload.replace('{features}',
                                                  ','.join(feature_list))
        request_payload = request_payload.replace(
            "{label}", label)
        request_payload = request_payload.replace("{predLabel}", predLabel)
        request_payload = request_payload.replace("{favourableOutcome}",
                                                  favourableOutcome)
        request_payload = request_payload.replace("{unfavourableOutcome}",
                                                  unfavourableOutcome)
        log.info(request_payload)
        request_payload_json = json.loads(request_payload)
     

        request_payload_json["facet"] = facet
        request_payload_json["categoricalAttributes"] = categoricalAttributes
        request_payload_json = AttributeDict(request_payload_json)
        return request_payload_json
        
        
    def get_Individual_Fairness(self, payload,operation_type):
        if payload["biasType"]=="PRETRAIN":
            label=payload["label"]
        else:
            label=payload["predLabel"]
        fileId=payload["sampleData"]
        k=payload["knn"]
        if label=="" or label==None:
            raise Exception("Label can not be null")
        retrivedata = self.fileStore.read_file(fileId)
        if retrivedata is None:
            raise HTTPException(status_code=500, detail="No content received from the POST request")

        dataset = pandas.read_csv(BytesIO(retrivedata['data']))
        dataset_list = []
        categorical_features = dataset.select_dtypes(
            include='object').columns.tolist()
        # remove labels from categorical attributes
        if label in categorical_features:
            categorical_features.remove(label)

        df = dataset.copy()
        # drop labels other than the current label, so that it will not be considered for fairness
        if operation_type=="PREPROCESSING" and "labels_pred" in df.columns:
            df = df.drop("pred_label", axis=1)
        if operation_type=="POSTPROCESSING" and label in df.columns:
            df=df.drop(label,axix=1)
            # customize StandardDataset just for Individual fairness, as we are not considering protected attributes
        dataset_orig = StandardDataset(df=df, label_name=label, favorable_classes=[df[label][0]],
                                           protected_attribute_names=[],
                                           privileged_classes=[np.array([])],
                                           categorical_features=categorical_features,
                                           features_to_keep=[], features_to_drop=[],
                                           na_values=[], custom_preprocessing=None,
                                           metadata={})
        dataset_list.append(dataset_orig)

        response = []
        scores = []
        util = utils()
        for dataset in dataset_list:
            score_dict = {}
            score = np.round(util.consistency(dataset,k), 2)
            scores.append(score)
            obj_metric_cs = me(name='CONSISTENCY',
                               description='Individual fairness metric that measures how similar the labels are for similar instances. Score ranges from [0,1], where 1 indicates consistent labels for similar instances.',
                               value=float(score[0]))

            score_dict[dataset.label_names[0]] = obj_metric_cs.metricsEntity
            response.append(score_dict)
        log.info(response)
        if response is None:
            raise HTTPException(status_code=500, detail="No response received from the POST request")
        return response

        
        
    def return_protected_attrib_analyseDB(self, payload: dict):
        import concurrent.futures
        if payload.Batch_id is None or '':
            log.error("Batch Id id missing")
            
        #get all the required data for analyze and individual fairness
        payload_details={}
        batchId = payload.Batch_id
        self.batch.update(batch_id=batchId, value={"Status": "In-progress"})
        tenet_id = self.tenet.find(tenet_name='Fairness')
        batch_details = self.batch.find(batch_id=batchId, tenet_id= tenet_id)
        datasetId = batch_details['DataId']
        payload_details["dataset_details"] = self.dataset.find(Dataset_Id= datasetId)
        attributes_list=['biasType', 'methodType', 'taskType', 'label', 'favorableOutcome', 'protectedAttribute', 'privilegedGroup']
        payload_details["dataset_attribute_ids"] = self.dataAttributes.find(dataset_attributes=attributes_list)
        payload_details_list = self.dataAttributeValues.find(
            dataset_id=datasetId, dataset_attribute_ids=payload_details["dataset_attribute_ids"], batch_id=batchId)
        #store all the attributes in this dict and del all other variable
        payload_details_dict={} 
        payload_details_dict["sampleData"]=payload_details["dataset_details"]["SampleData"]
        for i in range(0,len(payload_details["dataset_attribute_ids"])):
            payload_details_dict[attributes_list[i]]=payload_details_list[i]
        
        log.info(f"payload_details_dict--->{payload_details_dict}")
        payload_details_dict["predLabel"]="labels_pred"        #Default predLabel
        if payload_details_dict["biasType"] =="POSTTRAIN":   #Add predLabel if biasType is POSTTRAIN
            predLabel = self.dataAttributes.find(dataset_attributes=["predLabel"])
            if self.dataAttributeValues.checkValue(dataset_id=datasetId, dataset_attribute_ids=predLabel, batch_id=batchId):
                predLabel_value = self.dataAttributeValues.find(
                dataset_id=datasetId, dataset_attribute_ids=predLabel, batch_id=batchId)
                payload_details_dict["predLabel"]=predLabel_value[0]
                log.info(f"posttrain predLabel--->{predLabel_value}")

            
        log.info(f"payload_details_dict--->{payload_details_dict}")

        payload_details_dict["knn"]=5
        #Add knn if methodType is ALL
        if payload_details_dict["methodType"] =="ALL" or "CONSISTENCY":
            knn = self.dataAttributes.find(dataset_attributes=["knn"])
            if self.dataAttributeValues.checkValue(dataset_id=datasetId, dataset_attribute_ids=knn, batch_id=batchId):
                knn_value = self.dataAttributeValues.find(
                dataset_id=datasetId, dataset_attribute_ids=knn, batch_id=batchId)
                payload_details_dict["knn"]=knn_value[0]         
        log.info(f"payload_detailsdataset_details{payload_details_dict}")
        # get csv
        enter_time = time.time()
        log.info(f"Reading file from db: {enter_time}")
        retrivedata = self.fileStore.read_file(payload_details_dict['sampleData'])
        dataset = pandas.read_csv(BytesIO(retrivedata['data']))
        exit_time=time.time()
        log.info(f"Reading file completed in:{exit_time-enter_time}")
        
        fairnessService = FairnessServicePreproc()
        individual_fairness = None
        #call both analyze and individual fairness concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            pretrain_analyze=executor.submit(self.get_Pretrain_Analyze,payload_details_dict,dataset)
            if payload_details_dict["methodType"] =="CONSISTENCY" or 'ALL':
                individual_fairness=executor.submit(self.get_Individual_Fairness,payload_details_dict,"PREPROCESSING")
                log.info(f"individual_fairness--->{individual_fairness}")
            request_payload_json=pretrain_analyze.result()
            
            
        if FairnessUIservicePreproc.validate_json_request(request_payload_json):
            try:
                log.info(f"{payload_details}payload_details")
                response = FairnessServicePreproc.analyze_Fn(self,
                    request_payload_json, batchId, individual_fairness, dataset=dataset)
                self.batch.update(batch_id=batchId, value={"Status": "Completed"})
                # DataAttributeValues.update(dataset_id=datasetId, value={"IsActive": "N"})
            except FairnessUIParameterNotFoundError as cie:
                self.batch.update(batch_id=batchId, value={'Status': "Failed"})
                log.error(cie.__dict__)
                log.info("exit JSON ANALYSE method of Fairness Service")
                raise HTTPException(**cie.__dict__)

        else:
            response = "Please Input Correct Parameters."
        return response


    def upload_file_pretrainMitigation(self, payload: dict):
        fileId = payload["fileId"]
        log.debug("Reading file from database..........")
        enter_time = time.time()
        log.info(f"Entering Upload:{enter_time}")
        taskType = payload["taskType"]
        mitigationType = payload["MitigationType"]
        mitigationTechnique = payload["MitigationTechnique"]
        fileId = payload["fileId"]
        file_type = "text/csv"
        # get content from mongodb
        retrivedata = self.fileStore.read_file(fileId)
        if retrivedata is None:
            raise HTTPException(status_code=500, detail="No content received from the POST request")
        file_content=retrivedata["data"]
        name_of_dataset = retrivedata["name"].split('.')[0]
        # file_name=self.fileStore.getfilename(fileId)
        extension=retrivedata["extension"]
        uniquenm= name_of_dataset + datetime.datetime.now().strftime("%m%d%Y%H%M%S")
        contentType = retrivedata["contentType"]
        self.utils.store_file_locally_DB(extension,file_content,FairnessServicePreproc.LOCAL_FILE_PATH,uniquenm)

        read_file=pandas.read_csv(os.path.join(FairnessServicePreproc.LOCAL_FILE_PATH,uniquenm))

        # filename = self.fileStore.getfilename(fileId)
        
        feature_list = list(read_file.columns)

        updated_df = read_file.select_dtypes(exclude='number')
        udf_columns = list(updated_df.columns)
        categorical_values = {}
        for each in udf_columns:
            updated_df.drop(
                updated_df[(updated_df[each] == '?')].index, inplace=True)
            updated_df[each] = updated_df[each].str.replace('.', '')
            categorical_values[each] = list(updated_df[each].unique())

        log.info(f"list of columns remaining in dataset after exclusion : {updated_df.columns}")
        ex_ti = time.time()
        categorical_attribute = ','.join(list(updated_df.columns))
        response = {
            "mitigationType": mitigationType,
            "mitigationTechnique": mitigationTechnique,
            "trainFileName": name_of_dataset,
            "UploadedFileType": file_type,
            "AttributesInTheDataset": {"FeatureList ": feature_list,
                                       "CategoricalAttributesList": list(updated_df.columns)},
            "CategoricalAttributesUniqueValues": categorical_values
        }
        exit_time = time.time()
        log.info(f"Exiting Upload:{exit_time - enter_time}")
        if response is None:
            raise HTTPException(status_code=500, detail="No response received from the POST request")
        return response


    def return_pretrainMitigation_protected_attrib(self, payload: dict):
        log.info(payload)
        fairnessServicePreproc= FairnessServicePreproc()
        if payload.Batch_id is None or '':
            log.error("Batch Id id missing")
        batchId = payload.Batch_id
        self.batch.update(batch_id=batchId, value={"Status": "In-progress"})
        tenet_id = self.tenet.find(tenet_name='Fairness')
        batch_details = self.batch.find(batch_id=batchId, tenet_id=tenet_id)
        datasetId = batch_details['DataId']
        dataset_details = self.dataset.find(Dataset_Id=datasetId)
        dataset_attribute_ids = self.dataAttributes.find(dataset_attributes=[
                                                    'mitigationType', 'mitigationTechnique', 'methodType', 'taskType', 'label', 'favorableOutcome', 'protectedAttribute', 'privilegedGroup'])
        log.info(f"Dataset Attribute Ids:{dataset_attribute_ids}")
        dataset_attribute_values = self.dataAttributeValues.find(
            dataset_id=datasetId, dataset_attribute_ids=dataset_attribute_ids, batch_id=batchId)

        log.info(f"Dataset Attribute Values:{dataset_attribute_values}")
        fileId = dataset_details["SampleData"]
        # file_name = self.fileStore.getfilename(fileId)

        # log.info("File Name:", fileName)
        # get csv
        enter_time = time.time()
        log.info(f"Reading file from db:{enter_time}")
        # retrivedata = self.fileStore.read_file(fileId)

        content=self.fileStore.read_file(fileId)
        file_content=content["data"]
        extension=content["extension"]
        name_of_dataset = content["name"].split('.')[0]
        uniquenm= name_of_dataset + datetime.datetime.now().strftime("%m%d%Y%H%M%S")
        contentType = content["contentType"]
        self.utils.store_file_locally_DB(extension,file_content,FairnessServicePreproc.LOCAL_FILE_PATH,uniquenm)    
        #convert to dataframe   
        read_file=pandas.read_csv(os.path.join(FairnessServicePreproc.LOCAL_FILE_PATH,uniquenm))
        # dataset = pandas.read_csv(BytesIO(retrivedata['data'].read()))
        exit_time=time.time()
        log.info("Reading file completed in:", exit_time-enter_time)
        
        mitigationType = dataset_attribute_values[0]
        log.info("Mitigation Type:", mitigationType)
        mitigationTechnique = dataset_attribute_values[1]
        log.info("mitigationTechnique",mitigationTechnique)
        methodType = dataset_attribute_values[2]
        log.info("methodType",methodType)
        taskType = dataset_attribute_values[3]
        log.info("taskType",taskType)
        label = dataset_attribute_values[4]
        log.info("label",label)
        favourableOutcome = dataset_attribute_values[5]
        log.info("favourableOutcome",favourableOutcome)
        protectedAttribute = dataset_attribute_values[6]
        log.info("protectedAttribute",protectedAttribute)
        priv = dataset_attribute_values[7]
        log.info("priv",priv)

        feature_list = list(read_file.columns)

        labelmap = {}
        categorical_values = {}
        updated_df = read_file.select_dtypes(exclude='number')
        udf_columns = list(updated_df.columns)
        for each in udf_columns:
            updated_df.drop(
                updated_df[(updated_df[each] == '?')].index, inplace=True)
            updated_df[each] = updated_df[each].str.replace('.', '')
            categorical_values[each] = list(updated_df[each].unique())

        for value in categorical_values[label]:
            if value == favourableOutcome:
                labelmap[value] = '1'
            else:
                labelmap[value] = '0'

        outcomeList = categorical_values[label].copy()
        log.info(f"OutcomeList:{outcomeList}")
        log.info(f"FavourableOutcome:{favourableOutcome}")
        outcomeList.remove(favourableOutcome)
        unfavourableOutcome = ''.join(outcomeList)
        priv_list = priv
        if len(priv_list) != len(protectedAttribute):
            raise HTTPException(
                status_code=400, detail="Priviledged attribute count should be equal to protected attribute count")
        log.info("Priv_list", priv_list)

        ca_list = list(categorical_values.keys()).copy()
        ca_list.remove(label)

        protected_attribute_list = []

        for pa in protectedAttribute:
            attribute_values = categorical_values[pa]
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

        log.info(f"Facets:{protected_attribute_list}")

        facet = protected_attribute_list
        categoricalAttributes = ','.join(ca_list)

        request_payload = ""
        request_payload = open(
            "../output/UIPretrainMitigationPayload.txt").read()
        request_payload = request_payload.replace(
            '{name}', name_of_dataset)
        request_payload = request_payload.replace(
            '{fileid}', fileId)
        request_payload = request_payload.replace(
            '{mitigationType}', mitigationType)

        request_payload = request_payload.replace(
            '{mitigationTechnique}', mitigationTechnique)

        request_payload = request_payload.replace(
            '{taskType}', taskType)

        request_payload = request_payload.replace(
            '{filename}', name_of_dataset)
        request_payload = request_payload.replace('{features}',
                                                  ','.join(feature_list))
        request_payload = request_payload.replace(
            "{label}", label)
        request_payload = request_payload.replace("{favourableOutcome}",
                                                  favourableOutcome)
        request_payload = request_payload.replace("{unfavourableOutcome}",
                                                  unfavourableOutcome)
        log.info(request_payload)
        # FairnessUIservice.request_payload=  FairnessUIservice.request_payload.replace("{protectedAttribute}",protectedAttribute)
        request_payload_json = json.loads(request_payload)
        # .....................................................................................................

        request_payload_json["facet"] = facet
        request_payload_json["categoricalAttributes"] = categoricalAttributes
        request_payload_json = AttributeDict(request_payload_json)
        log.info(f"Request_payload_json------>{request_payload_json}")

        if FairnessUIservicePreproc.validate_pretrain_json_request(request_payload_json):
            try:
                response = fairnessServicePreproc.preprocessingmitigate(
                    request_payload_json,batchId,dataset=read_file, extension=extension)
                self.batch.update(batch_id=batchId, value={"Status": "Completed"})
            except FairnessUIParameterNotFoundError as cie:
                self.batch.update(batch_id=batchId, value={'Status': "Failed"})
                log.error(cie.__dict__)
                log.info("exit JSON PretrainMitigation method of Fairness Service")
                raise HTTPException(**cie.__dict__)
        else:
            response = "Please Input Correct Parameters."

        return response

    

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

    

    def validate_mitigate_df(filename, protected_attribute, privledged, unprivledged, label, labelmap):
        fav_outcome_index = list(labelmap.values()).index(1)
        unfav_outcome_index = list(labelmap.values()).index(0)
        fav_outcome = list(labelmap.keys())[fav_outcome_index]
        unfav_outcome = list(labelmap.keys())[unfav_outcome_index]
        df = pandas.read_csv(filename)
        columns = list(df.columns)
        attr_dict = {}
        col_set_without_encoding = set()
        transformed_df = {}
        for each in columns:
            if "=" in each:
                prev_index = each.index("=")
                col_orig_name = each[:prev_index]
                if col_orig_name in (attr_dict.keys()):
                    attr_dict[col_orig_name].append(each[prev_index + 1:])
                else:
                    attr_dict[col_orig_name] = [each[prev_index + 1:]]
            else:
                col_set_without_encoding.add(each)
                transformed_df[each] = df[each]

        complete_col_lst = list(attr_dict.keys())
        complete_col_lst.extend(col_set_without_encoding)

        for key in attr_dict.keys():
            transformed_df[key] = []
            for each in columns:
                if "=" in each:
                    prev_index = each.index("=")
                    col_orig_name = each[:prev_index]
                    if col_orig_name == key:
                        for i in range(len(df[each])):
                            if df[each][i] != 0:
                                transformed_df[key].insert(
                                    i, each[prev_index + 1:])

        transformed_df[label] = transformed_df[label].replace(
            [1, 0], [fav_outcome, unfav_outcome])

        df = pandas.DataFrame.from_dict(transformed_df)
        unique_nm = datetime.datetime.now().strftime("%m%d%Y%H%M%S")
        mitigated_df_filename = "../output/transformedDataset/output/mitigateDF" + \
            unique_nm + ".csv"
        df.to_csv(mitigated_df_filename, index=False)
        return mitigated_df_filename