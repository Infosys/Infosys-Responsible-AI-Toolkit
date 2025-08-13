"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from fairness.dao.bias_model import Bias, TrainingDataset, PredictionDataset
from fairness.dao.mitigation_model import Mitigation, TrainingDataset
from infosys_responsible_ai_fairness.responsible_ai_fairness import BiasResult, DataList, MitigationResult, PRETRAIN, utils, StandardDataset
from infosys_responsible_ai_fairness.responsible_ai_fairness import metricsEntity as me
import numpy as np
from bson import ObjectId
from fairness.dao.individual_fairness import Individual_Fairness
from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
from fairness.dao.llm_analysis import LlmAnalysis
from fairness.dao.model_mitigation_mapper import MitigationModel
from fairness.dao.databaseconnection import DataBase
from io import StringIO, BytesIO
from fastapi.responses import FileResponse
from sklearn.metrics import accuracy_score
from fastapi.responses import StreamingResponse
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
from fairness.service.preprocessing import FairnessUIservicePreproc
from fairness.dao.WorkBench.FileStoreDb import FileStoreReportDb
from fairness.dao.WorkBench.databaseconnection import DataBase_WB
from fairness.mappers.mappers import BiasAnalyzeResponse, BiasAnalyzeRequest, BiasPretrainMitigationResponse, BiasResults, IndividualFairnessRequest, \
    metricsEntity, MitigateBiasRequest, MitigationAnalyzeResponse, PreprocessingMitigationAnalyzeResponse, PreprocessingMitigateBiasRequest, BatchId
from fairness.dao.WorkBench.Tenet import Tenet
from fairness.dao.WorkBench.Batch import Batch
from fairness.dao.WorkBench.report import Report
from fairness.dao.WorkBench.Data import Dataset, DataAttributes, DataAttributeValues
from fairness.constants.local_constants import *
from fairness.service.service_utils import Utils
from fairness.service.service_monitoring import FairnessAudit
from fairness.service.service_success_rates import SuccessRateService
from fairness.service.inprocessing import InprocessingService
from fairness.service.preprocessing import FairnessUIservicePreproc
import io
from fastapi import HTTPException
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
DATASET_CONTAINER_NAME = os.getenv('Dt_containerName')
MODEL_CONTAINER_NAME = os.getenv('Model_containerName')
PDF_CONTAINER_NAME=os.getenv("PDF_CONTAINER_NAME")
CSV_CONTAINER_NAME=os.getenv("CSV_CONTAINER_NAME")
ZIP_CONTAINER_NAME=os.getenv("ZIP_CONTAINER_NAME")
class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class FairnessWorkbench:
    MITIGATED_LOCAL_FILE_PATH="../output/MitigatedData/"
    MITIGATED_UPLOAD_PATH="responsible-ai//responsible-ai-fairness//MitigatedData"
    LOCAL_FILE_PATH="../output/datasets/"

    def __init__(self, db=None):
        if db is not None:
            self.db = db
            self.fileStore = FileStoreReportDb(self.db)
            self.batch =  Batch(self.db)
            self.tenet =  Tenet(self.db)
            self.report = Report(self.db)
            self.dataset = Dataset(self.db)
            self.dataAttributes = DataAttributes(self.db)
            self.dataAttributeValues = DataAttributeValues(self.db)
            log.info("Mockdb is executed")

        else:
            self.db = DataBase().db
            self.fileStore = FileStoreReportDb()
            self.batch =  Batch()
            self.tenet =  Tenet()
            self.report = Report()
            self.dataset = Dataset()
            self.dataAttributes = DataAttributes()
            self.dataAttributeValues = DataAttributeValues()
        self.utils = Utils()
        self.bias_collection = self.db['bias']
        self.mitigation_collection = self.db['mitigation']
        self.fairness_collection = self.db['fs.files']
    
    def wapper_trigger(self, payload: dict):
        log.info("payload"+str(payload))
        if payload.Batch_id is None or '': 
            log.error("Batch Id id missing")
        batchId = payload.Batch_id
        self.batch.update(batch_id=batchId, value={"Status": "In-progress"})
        tenet_id = self.tenet.find(tenet_name='Fairness')
        batch_details = self.batch.find(batch_id=batchId, tenet_id=tenet_id)
        datasetId = batch_details['DataId']     
        dataset_details = self.dataset.find(Dataset_Id=datasetId)
        dataset_attribute_ids = self.dataAttributes.find(dataset_attributes=['mitigationTechnique','mitigationType','methodType'])
        log.info("Dataset Attribute Ids:"+ str(dataset_attribute_ids))
        dataset_attribute_values = self.dataAttributeValues.find(
            dataset_id=datasetId, dataset_attribute_ids=dataset_attribute_ids, batch_id=batchId)
        
        log.info("Dataset Attribute Values:"+str(dataset_attribute_values))

        mitigationTechnique = dataset_attribute_values[0]
        mitigationType = dataset_attribute_values[1]
        log.info("mitigationTechnique"+mitigationTechnique)
        payload = {"Batch_id": batchId}
        
        if mitigationType=="AUDIT":
            methodType = dataset_attribute_values[2]
            if methodType=="Generic":
                audit=FairnessAudit()
                response=audit.workbench_audit(payload)  
                return response   
            elif methodType=="Decisive":
                success_rates=SuccessRateService()
                response=success_rates.workbench_analyze(payload)
                return response
        if mitigationType=="INPROCESSING":
            inprocessingService=InprocessingService()
            response=inprocessingService.inprocessing_exponentiated_gradient_reduction(payload)
            return response
        
        if mitigationTechnique == "":
            obj = FairnessUIservicePreproc()
            payload=BatchId(**payload)
            response = obj.return_protected_attrib_analyseDB(payload)
            return response
        else: 
            obj=FairnessUIservicePreproc()
            payload=BatchId(**payload)
            response= obj.return_pretrainMitigation_protected_attrib(payload)
        return response


    def wrapper_download(self, payload: dict):
        batchId = payload.Batch_id
        report_id = self.report.find(batch_id=batchId)
        print(report_id)
        reportId = report_id['ReportFileId']
        reportName=report_id['ReportName']
        #check extension of the file
        print(reportName)
        container_name=""
        if reportName.endswith('.pdf'):
            container_name=PDF_CONTAINER_NAME
        elif reportName.endswith('zip'):
            container_name=ZIP_CONTAINER_NAME
        elif reportName.endswith('.joblib'):
            container_name=MODEL_CONTAINER_NAME
        else:
            container_name=DATASET_CONTAINER_NAME
            
        if container_name==MODEL_CONTAINER_NAME:
            content = self.fileStore.read_chunked_file(reportId,container_name)
            response = StreamingResponse(io.BytesIO(content['data']), media_type=content['contentType'])
            response.headers["Content-Disposition"] = 'attachment; filename='+reportName
            return response
        content = self.fileStore.read_file(reportId,container_name)
        response = StreamingResponse(io.BytesIO(content['data']), media_type=content['contentType'])
        response.headers["Content-Disposition"] = 'attachment; filename='+reportName
        return response