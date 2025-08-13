"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from PIL import Image
import google.generativeai as genai
import google.ai.generativelanguage as glm
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json
import datetime
import time
import os
#import pdfkit
import ast
import matplotlib.pyplot as plt
import base64
from mimetypes import guess_type
from io import BytesIO
import requests
from sklearn.neighbors import NearestNeighbors

from fairness.dao.WorkBench.FileStoreDb import FileStoreReportDb
from fairness.dao.WorkBench.databaseconnection import DataBase_WB
from fairness.dao.WorkBench.Tenet import Tenet
from fairness.dao.WorkBench.Batch import Batch
from fairness.dao.WorkBench.html import Html
from fairness.dao.WorkBench.Data import Dataset,DataAttributes,DataAttributeValues
from fairness.constants.local_constants import *
from fairness.config.logger import CustomLogger
import pandas
import io
from fastapi import HTTPException
import tempfile  
log = CustomLogger()

import joblib
import pickle

from fairlearn.postprocessing import ThresholdOptimizer

from fairlearn.metrics import demographic_parity_difference, equalized_odds_difference, true_positive_rate, true_negative_rate, false_positive_rate, false_negative_rate
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier

from io import StringIO, BytesIO
from fairness.dao.databaseconnection import DataBase

from aif360.datasets import BinaryLabelDataset
from aif360.algorithms.inprocessing import ExponentiatedGradientReduction

from bson import ObjectId
import numpy as np
import openai
from pathlib import Path

from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from fairness.dao.WorkBench.report import Report
load_dotenv()
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class InprocessingService:
    def __init__(self, MockDB=None):
        if MockDB is not None:
            self.db = MockDB.db
            self.fileStore = FileStoreReportDb(self.db)
            self.batch =  Batch(self.db)
            self.tenet =  Tenet(self.db)
            self.dataset = Dataset(self.db)
            self.dataAttributes = DataAttributes(self.db)
            self.dataAttributeValues = DataAttributeValues(self.db)
            log.info("Mockdb is executed")
            self.bias_collection = self.db['bias']
            self.mitigation_collection = self.db['mitigation']
            self.mitigation_model_collection = self.db['mitigation_model']
            self.metrics_collection = self.db['metrics']
            self.llm_analysis_collection = self.db['llm_analysis']
            self.llm_connection_credentials_collection = self.db['llm_connection_credentails']

        else:
            self.db = DataBase().db
            self.fileStore = FileStoreReportDb()
            self.batch =  Batch()
            self.tenet =  Tenet()
            self.dataset = Dataset()
            self.dataAttributes = DataAttributes()
            self.dataAttributeValues = DataAttributeValues()
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

    AWARE_MODEL_LOCAL_PATH='../output/aware_model/'
    AWARE_MODEL_UPLOAD_PATH='responsible-ai//responsible-ai-fairness//aware-model'


    def mitigation_model_analyze(y_true, y_pred, df_sensitive_features):
        return {
            'demographic_parity_difference': demographic_parity_difference(y_true, y_pred, sensitive_features=df_sensitive_features),
            'equalized_odds_difference': equalized_odds_difference(y_true, y_pred, sensitive_features=df_sensitive_features),
            'true_positive_rate': true_positive_rate(y_true, y_pred),
            'true_negative_rate': true_negative_rate(y_true, y_pred),
            'false_positive_rate': false_positive_rate(y_true, y_pred),
            'false_negative_rate': false_negative_rate(y_true, y_pred),
            'accuracy_score': accuracy_score(y_true, y_pred)
        }


    def upload_inprocess(self, payload: dict):
        fileId = payload['fileId']
        traindata = self.fileStore.read_file(fileId)
        df_train = pandas.read_csv(BytesIO(traindata['data']))
        feature_list = list(df_train.columns)
        response = {
            'feature_list': feature_list
        }

        return response


    def inprocessing_exponentiated_gradient_reduction(self, payload: dict):
        if payload['Batch_id'] is None or '':
            log.error("Batch Id id missing")
        batchId = payload['Batch_id']
        self.batch.update(batch_id=batchId, value={"Status": "In-progress"})
        tenet_id = self.tenet.find(tenet_name='Fairness')
        batch_details = self.batch.find(batch_id=batchId, tenet_id=tenet_id)
        datasetId = batch_details['DataId']
        dataset_details = self.dataset.find(Dataset_Id=datasetId)
        dataset_attribute_ids = self.dataAttributes.find(dataset_attributes=[
                                                    'sensitiveFeatures', 'favourableLabel', 'label'])
        log.info("Dataset Attribute Ids: {dataset_attribute_ids}")
        dataset_attribute_values = self.dataAttributeValues.find(
            dataset_id=datasetId, dataset_attribute_ids=dataset_attribute_ids, batch_id=batchId)

        log.info("Dataset Attribute Values: {dataset_attribute_values}")
        fileId = dataset_details["SampleData"]

        sensitiveFeatures = dataset_attribute_values[0]
        log.info(f"sensitiveFeatures: {sensitiveFeatures}")
        favourableLabel = dataset_attribute_values[1]
        log.info(f"favourableLabel {favourableLabel}")
        label = dataset_attribute_values[2]
        content=self.fileStore.read_file(fileId)
        if content is None:
            raise HTTPException(status_code=500, detail="No content received from the POST request")

        df_train = pandas.read_csv(BytesIO(content['data']))
        train, test = train_test_split(df_train, test_size=0.3)

        favourable_label=int(favourableLabel)
        unfavourable_label=0 if favourable_label==1 else 1

        dataset_train=BinaryLabelDataset(
            df=train,
            label_names=[label],
            favorable_label=favourable_label,
            unfavorable_label=unfavourable_label,
            protected_attribute_names=sensitiveFeatures
        )

        dataset_test=BinaryLabelDataset(
            df=test,
            label_names=[label],
            favorable_label=favourable_label,
            unfavorable_label=unfavourable_label,
            protected_attribute_names=sensitiveFeatures
        )

        exponentiated_gradient_reduction=ExponentiatedGradientReduction(estimator=RandomForestClassifier(), constraints='EqualizedOdds')

        exponentiated_gradient_reduction.fit(dataset=dataset_train)

        model_unique_name='model_'+'.joblib'

        container_name = os.getenv('Model_CONTAINER_NAME')

        bytes_buffer = io.BytesIO()
        joblib.dump(exponentiated_gradient_reduction, bytes_buffer)
        bytes_data = bytes_buffer.getvalue()
        fileId = self.fileStore.save_file(file=bytes_data, filename=model_unique_name, contentType="joblib", tenet='Fairness', container_name=container_name)
        dataset_pred=exponentiated_gradient_reduction.predict(dataset=dataset_test)

        y_test=dataset_test.labels
        y_pred=dataset_pred.labels

        df_test_sensitive_features=test[sensitiveFeatures]

        metrics=InprocessingService.mitigation_model_analyze(y_test, y_pred, df_test_sensitive_features)

        model_file_name=model_unique_name+'.joblib'
    
        response={
            "modelfileId": fileId,
            "metrics": metrics
        }
        report_document={"ReportId":time.time(),"BatchId":batchId,"ReportFileId":fileId,"TenetId":tenet_id,"ReportName":model_unique_name,"ContentType":"joblib","CreatedDateTime":datetime.datetime.now()}
        self.batch.update(batch_id=batchId, value={"Status": "Completed"})
        Report.create(report_document)
        if response is None:
            self.batch.update(batch_id=batchId, value={"Status": "Failed"})
            raise HTTPException(status_code=500, detail="No response received from the POST request")
        return response
    