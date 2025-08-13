"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pathlib
from PIL import Image
import google.generativeai as genai
import google.ai.generativelanguage as glm
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json
import datetime
import time
import os

# import pdfkit
import ast
import matplotlib.pyplot as plt
import base64
from mimetypes import guess_type
from io import BytesIO
import requests
import io
from sklearn.neighbors import NearestNeighbors
from fastapi.responses import StreamingResponse

from fairness.dao.WorkBench.FileStoreDb import FileStoreReportDb
from fairness.dao.WorkBench.databaseconnection import DataBase_WB
from fairness.mappers.mappers import (
    BiasAnalyzeResponse,
    BiasAnalyzeRequest,
    BiasPretrainMitigationResponse,
    BiasResults,
    IndividualFairnessRequest,
    metricsEntity,
    MitigateBiasRequest,
    MitigationAnalyzeResponse,
    PreprocessingMitigationAnalyzeResponse,
    PreprocessingMitigateBiasRequest,
    BatchId,
)
from fairness.exception.exception import (
    FairnessException,
    FairnessUIParameterNotFoundError,
)
from aif360.datasets import StandardDataset
from aif360.metrics import BinaryLabelDatasetMetric
from fairness.dao.WorkBench.Tenet import Tenet
from fairness.dao.WorkBench.Batch import Batch
from fairness.dao.WorkBench.html import Html
from fairness.dao.WorkBench.Data import Dataset, DataAttributes, DataAttributeValues
from fairness.constants.local_constants import *
from fairness.constants.llm_constants import (
    GEMINI_IMAGE_PROMPT_TEMPLATE,
    GEMINI_PROMPT_TEMPLATE,
    MIXTRAL_PROMPT_TEMPLATE,
    OPENAI,
    GPT_4,
    GPT_4O,
    GPT_4O_TEXT,
    GPT_4O_IMAGE,
    GEMINI,
    GEMINI_PRO_VISION,
    INTERNAL,
    MIXTRAL,
    GPT_4O_IMAGE_PROMPT_TEMPLATE,
    GPT_4O_TEXT_PROMPT_TEMPLATE,
    LLAMA_TEXT_TEMPLATE,AWS_IMAGE_TEMPLATE, AWS_TEXT_TEMPLATE
)
from fairness.config.logger import CustomLogger
import pandas
from fastapi import HTTPException
from fairness.exception.custom_exception import CustomHTTPException
import tempfile
import re

log = CustomLogger()

import joblib

from fairlearn.postprocessing import ThresholdOptimizer

from fairlearn.metrics import (
    demographic_parity_difference,
    equalized_odds_difference,
    true_positive_rate,
    true_negative_rate,
    false_positive_rate,
    false_negative_rate,
)
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier

from fastapi.responses import FileResponse

from infosys_responsible_ai_fairness.responsible_ai_fairness import (
    BiasResult,
    DataList,
    MitigationResult,
    PRETRAIN,
    utils,
    StandardDataset,
    metricsEntity,
)

from io import StringIO, BytesIO
from fairness.dao.databaseconnection import DataBase
from fairness.dao.bias_model import Bias, TrainingDataset, PredictionDataset
from fairness.dao.mitigation_model import Mitigation, TrainingDataset
from fairness.dao.model_mitigation_mapper import MitigationModel

from aif360.datasets import BinaryLabelDataset
from aif360.algorithms.inprocessing import ExponentiatedGradientReduction
from fairness.dao.llm_analysis import LlmAnalysis
from fairness.dao.llm_connection_credentials import LlmConnectionCredentials
from fairness.dao.individual_fairness import Individual_Fairness
from fairness.Telemetry.Telemetry_call import SERVICE_UPLOAD_FILE_METADATA
from fairness.Telemetry.Telemetry_call import SERVICE_UPD_GETATTRIBUTE_METADATA
from fairness.Telemetry.Telemetry_call import SERVICE_attributes_Data_METADATA
from fairness.Telemetry.Telemetry_call import (
    SERVICE_return_protected_attrib_DB_METADATA,
)
from fairness.Telemetry.Telemetry_call import SERVICE_getLabels_METADATA
from fairness.Telemetry.Telemetry_call import SERVICE_getScore_METADATA
from fairness.Telemetry.Telemetry_call import SERVICE_upload_file_Premitigation_METADATA
from fairness.Telemetry.Telemetry_call import (
    SERVICE_return_pretrainMitigation_protected_attrib_METADATA,
)
from bson import ObjectId
import numpy as np

from fairness.dao.LlmConnection import create_llm_connection, Azureopenai, GeminiFlash, GeminiPro, AWS

from dotenv import load_dotenv

fairnesstelemetryurl = os.getenv("FAIRNESS_TELEMETRY_URL")
telemetry_flag = os.getenv("tel_Falg")
load_dotenv()


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class FairnessService:
    MITIGATED_LOCAL_FILE_PATH = "../output/MitigatedData/"
    MITIGATED_UPLOAD_PATH = "responsible-ai//responsible-ai-fairness//MitigatedData"
    DATASET_LOCAL_FILE_PATH = "../output/UItoNutanixStorage/"
    DATASET_UPLOAD_FILE_PATH = "responsible-ai//responsible-ai-fairness//Fairness_ui"
    DATASET_WB_LOCAL_FILE_PATH = "../output/"
    LOCAL_FILE_PATH = "../output/datasets/"
    MODEL_LOCAL_PATH = "../output/model/"
    MITIGATED_MODEL_LOCAL_PATH = "../output/mitigated_model/"
    AWARE_MODEL_LOCAL_PATH = "../output/aware_model/"
    MODEL_UPLOAD_PATH = "responsible-ai//responsible-ai-fairness//model"
    MITIGATED_MODEL_UPLOAD_PATH = (
        "responsible-ai//responsible-ai-fairness//mitigated-model"
    )
    AWARE_MODEL_UPLOAD_PATH = "responsible-ai//responsible-ai-fairness//aware-model"

    def __init__(self, db=None):
        if db is not None:
            self.db = db
            self.fileStore = FileStoreReportDb(self.db)
            self.batch = Batch(self.db)
            self.tenet = Tenet(self.db)
            self.dataset = Dataset(self.db)
            self.dataAttributes = DataAttributes(self.db)
            self.dataAttributeValues = DataAttributeValues(self.db)
            log.info("Mockdb is executed")

        else:
            self.db = DataBase().db
            self.fileStore = FileStoreReportDb()
            self.batch = Batch()
            self.tenet = Tenet()
            self.dataset = Dataset()
            self.dataAttributes = DataAttributes()
            self.dataAttributeValues = DataAttributeValues()
            log.info("database")
        self.bias_collection = self.db["bias"]
        self.mitigation_collection = self.db["mitigation"]
        self.fairness_collection = self.db["fs.files"]

    def save_as_json_file(fileName: str, content):
        with open(fileName, "w") as outfile:
            json.dump(content, outfile, indent=2)

    def save_as_file(filename: str, content):
        with open(filename, "wb") as outfile:
            outfile.write(content)

    def read_html_file(filename: str):
        with open(filename, "r") as file:
            html_content = file.read()
        return html_content

    def json_to_html(json_obj):
        df = pandas.read_json(json.dumps(json_obj))

        # Extract metric names and values
        data = df.iloc[0]
        metrics = data["metrics"]

        # Generate HTML content
        html_content = "<body><h2>FAIRNESS REPORT</h2>"
        html_content = f"<h2 style='text-align:center; color:white; background-color:darkorchid; font-size:35px; font-family: sans-serif;'>Fairness Report</h2>"
        html_content = (
            html_content
            + f"<h3 style='font-weight:normal; font-family: sans-serif; font-size:17px;'>{F_Desc}</h3>"
        )
        html_content = (
            html_content
            + f"<h3 style='font-weight:normal; font-family: sans-serif; font-size:17px;'>{D_Desc}</h3>"
        )
        html_content += f"<body><h3 style='color:darkorchid; text-align:left; font-size:23px'>METRICS</h3></body>"

        # Iterate over metrics and create plots
        for metric in metrics:
            metric_name = metric["name"]
            metric_value = float(metric["value"])
            metric_desc = metric["description"]

            # Create a new plot for each metric
            # plt.figure(figsize =(12,6))
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(metric_name, metric_value, color="darkorchid")

            ax.set_xlabel("Metric")
            ax.set_ylabel("Value")
            ax.set_title(f"{metric_name}")
            ax.set_ylim(-1, 1)

            # Save the plot as a PNG file
            path = "../output/"  # Replace with the desired path
            filename = os.path.join(path, f"{metric_name.replace(' ', '_')}.png")
            plt.savefig(filename)

            # Convert the PNG file to base64
            with open(filename, "rb") as imagefile:
                encoded_image = base64.b64encode(imagefile.read()).decode()

            # Embed the base64 image in the HTML content
            # html_content = f"<h2 style='text-align:center; color:white; background-color:darkorchid; font-size:35px; font-family: sans-serif;'>Fairness Report</h2>"

            html_content += f"<body><h3 style='color:darkorchid; text-align:left; font-size:21px'>{metric_name}</h3></body>"
            html_content += f"<h3 style='font-weight:normal; font-family: sans-serif; font-size:17px;'>Description - {metric_desc}</h3>"
            html_content += f"<h3 style='font-weight:normal; font-family: sans-serif; font-size:17px;'>Measured Value = {metric_value}</h3>"
            html_content += f"<img src='data:image/png;base64,{encoded_image}' alt='{metric_name} Plot'>"

        html_content += "</body>"
        local_file_path = "../output/fairnessreport.html"

        return html_content

    def save_html_to_file(html_string, filename):
        with open(filename, "w") as f:
            f.write(html_string)

    def parse_nutanix_bucket_object(fullpath: str):
        split_path = fullpath.split("//")
        return {"bucket_name": split_path[0], "object_key": "/".join(split_path[1:])}

    def get_data_frame(extension: str, tpath: str, sep: str, usecols: list):
        if extension == "csv":
            return pandas.read_csv(tpath, sep=",", usecols=usecols)
        elif extension == "parquet":
            return pandas.read_parquet(tpath, sep=",", usecols=usecols)
        elif extension == "feather":
            return pandas.read_feather(tpath, sep=",", usecols=usecols)
        elif extension == "json":
            return pandas.read_json(tpath, sep=",", usecols=usecols)

    # def uploadfile_to_db(uploadPath, filePath):
    #     # to upload file in Nutanix
    #     buck_dict = FairnessService.parse_nutanix_bucket_object(uploadPath)
    #     bucket_ = buck_dict["bucket_name"]
    #     key_ = buck_dict["object_key"]
    #     strt_time = time.time()
    #     log.info(f"Start time{strt_time}")
    #     fileName = os.path.basename(filePath)
    #     NutanixObjectStorage.upload_with_high_threshold(
    #         filePath, bucket_, key_ + "/" + fileName, 10
    #     )
    #     end_time = time.time()
    #     log.info(f"End time{end_time}")
    #     log.info(f"Total Time:{end_time - strt_time}")

    def uploadfile_to_mongodb(uploadPath, filePath, fileType):
        # to upload file in Mongodb
        strt_time = time.time()
        log.info(f"Start time{strt_time}")
        fileId = FileStoreReportDb.save_local_file(filePath=filePath, fileType=fileType)
        log.info(fileId)
        end_time = time.time()
        log.info(f"End time{end_time}")
        log.info(f"Total Time:{end_time - strt_time}")
        return fileId

    def pretrainedAnalyse(
        traindata,
        labelmap,
        label,
        protectedAttributes,
        favourableOutcome,
        CategoricalAttributes,
        features,
        biastype,
        methods,
        flag,
    ):
        ds = DataList()
        datalist = ds.getDataList(
            traindata,
            labelmap,
            label,
            protectedAttributes,
            favourableOutcome,
            CategoricalAttributes,
            features,
            biastype,
            flag,
        )
        biasResult = BiasResult()
        list_bias_results = biasResult.analyzeResult(
            biastype, methods, protectedAttributes, datalist
        )
        return list_bias_results

    def preprocessingmitigateandtransform(
        traindata,
        labelmap,
        label,
        protectedAttributes,
        favourableOutcome,
        CategoricalAttributes,
        features,
        biastype,
        methods,
        mitigationTechnique,
        flag,
    ):
        ds = DataList()
        datalist = ds.getDataList(
            traindata,
            labelmap,
            label,
            protectedAttributes,
            favourableOutcome,
            CategoricalAttributes,
            features,
            biastype,
            flag,
        )
        biasResult = BiasResult()
        list_bias_results = biasResult.analyzeResult(
            biastype, methods, protectedAttributes, datalist
        )
        mitigated_df = biasResult.mitigateAndTransform(
            datalist, protectedAttributes, mitigationTechnique
        )
        log.info(list_bias_results)
        return list_bias_results, mitigated_df

    def posttrainedAnalyse(
        testdata, label, labelmap, protectedAttributes, taskType, methods, flag
    ):
        ds = DataList()
        group_unpriv_ts, group_priv_ts, df_preprocessed, df_orig = ds.preprocessDataset(
            testdata, label, labelmap, protectedAttributes, taskType, flag
        )
        predicted_y = df_preprocessed["labels_pred"]
        actual_y = df_preprocessed["label"]
        biasResult = BiasResult()
        list_bias_results = biasResult.analyseHoilisticAIBiasResult(
            taskType,
            methods,
            group_unpriv_ts,
            group_priv_ts,
            predicted_y,
            actual_y,
            protectedAttributes,
        )
        log.info(f"list_bias_results: {list_bias_results}")

        return list_bias_results

    def analyzeTenet(self, payload: dict) -> BiasAnalyzeResponse:
        log.info("***************Entering Analyse*************")
        log.debug(f"payload: {payload}")
        methods = payload.method
        biastype = payload.biasType
        trainingDataset = AttributeDict(payload.trainingDataset)
        tpath = AttributeDict(trainingDataset.path).uri
        label = trainingDataset.label
        extension = trainingDataset.extension
        predictionDataset = AttributeDict(payload.predictionDataset)
        ppath = AttributeDict(predictionDataset.path).uri
        predlabel = predictionDataset.predlabel
        features = payload.features.split(",")
        protectedAttributes = payload.facet
        CategoricalAttributes = payload.categoricalAttributes
        if CategoricalAttributes == " ":
            CategoricalAttributes = []
        else:
            CategoricalAttributes = CategoricalAttributes.split(",")
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
            attr["unprivileged"] += [i.unprivileged]

        protectedAttributes = AttributeDict(attr)
        taskType = payload.taskType
        train_df = pandas.read_csv(tpath, sep=",", usecols=features)
        log.info(f"Getting df{train_df}")
        pred_features = features
        if biastype == "POSTTRAIN":
            pred_features = features.append("labels_pred")
        df = pandas.read_csv(ppath, sep=",", usecols=pred_features)
        log.info(f"Getting df{df}")
        # bucket_dict = FairnessService.parse_nutanix_bucket_object(tpath)
        # bucket = bucket_dict['bucket_name']
        # key = bucket_dict['object_key']
        # traindata = NutanixObjectStorage.get_file_content(bucket, key)
        # s = str(traindata, 'utf-8')
        # traindata = StringIO(s)

        # traindata = NutanixObjectStorage.get_file_content(bucket, key)

        # s = str(traindata, 'utf-8')
        # traindata = StringIO(s)

        # bucket_dict = FairnessService.parse_nutanix_bucket_object(ppath)
        # bucket = bucket_dict['bucket_name']
        # key = bucket_dict['object_key']

        # testdata = NutanixObjectStorage.get_file_content(bucket, key)
        # s = str(testdata, 'utf-8')
        # testdata = StringIO(s)

        list_bias_results = None
        if biastype == "PRETRAIN":
            list_bias_results = FairnessService.pretrainedAnalyse(
                train_df,
                labelmap,
                label,
                protectedAttributes,
                favourableOutcome,
                CategoricalAttributes,
                features,
                biastype,
                methods,
                True,
            )
        elif biastype == "POSTTRAIN":
            list_bias_results = FairnessService.posttrainedAnalyse(
                df, label, labelmap, protectedAttributes, taskType, methods, True
            )

        objbias_pretrainanalyzeResponse = BiasAnalyzeResponse(
            biasResults=list_bias_results
        )
        json_object = objbias_pretrainanalyzeResponse.json()
        log.info(f"json_object:{json_object}")
        return objbias_pretrainanalyzeResponse

    def analyzedemo(self, payload: dict, batchId=None) -> BiasAnalyzeResponse:
        log.info(payload)
        log.info("***************Entering Analyse*************")
        log.info(f"BatchId:{batchId}")

        log.debug(f"payload: {payload}")
        methods = payload.method
        biastype = payload.biasType
        fileId = payload.fileid
        if fileId is None:

            raise HTTPException("fileId is missing in the payload")
        # file_type ="text/csv"
        retrivedata = self.fileStore.read_file(fileId)
        df = pandas.read_csv(BytesIO(retrivedata["data"]))
        if df is None or df.empty:
            raise ValueError("Dataframe is empty or None")
        # trainingDataset = AttributeDict(payload.trainingDataset)
        # tpath = AttributeDict(trainingDataset.path).uri
        label = payload.label
        # predictionDataset = AttributeDict(payload.predictionDataset)
        # ppath = AttributeDict(predictionDataset.path).uri
        # predlabel = PredictionDataset.predlabel
        features = payload.features.split(",")
        protectedAttributes = payload.facet
        CategoricalAttributes = payload.categoricalAttributes
        if CategoricalAttributes == " ":
            CategoricalAttributes = []
        else:
            CategoricalAttributes = CategoricalAttributes.split(",")
        favourableOutcome = [str(i) for i in payload.favourableOutcome]
        outputPath = AttributeDict(payload.outputPath).uri
        labelmap = payload.labelmaps
        if biastype == "POSTTRAIN":
            label = payload.label

        attr = {"name": [], "privileged": [], "unprivileged": []}
        for i in protectedAttributes:
            i = AttributeDict(i)
            log.info("=", i)
            attr["name"] += [i.name]
            attr["privileged"] += [i.privileged]
            attr["unprivileged"] += [i.unprivileged]

        protectedAttributes = AttributeDict(attr)
        taskType = payload.taskType
        # bucket_dict = FairnessService.parse_nutanix_bucket_object(tpath)
        # bucket = bucket_dict['bucket_name']
        # key = bucket_dict['object_key']

        list_bias_results = None
        if biastype == "PRETRAIN":
            list_bias_results = FairnessService.pretrainedAnalyse(
                df,
                labelmap,
                label,
                protectedAttributes,
                favourableOutcome,
                CategoricalAttributes,
                features,
                biastype,
                methods,
                True,
            )
        elif biastype == "POSTTRAIN":
            list_bias_results = FairnessService.posttrainedAnalyse(
                df, label, labelmap, protectedAttributes, taskType, methods, True
            )

        objbias_pretrainanalyzeResponse = BiasAnalyzeResponse(
            biasResults=list_bias_results
        )
        json_object = objbias_pretrainanalyzeResponse.json()
        # if Condition returns metric results, else will work with batchid and return the response
        if batchId == None:
            return objbias_pretrainanalyzeResponse
        else:

            local_file_path = "../output/" + "sample.json"
            FairnessService.save_as_json_file(local_file_path, list_bias_results)
            html = FairnessService.json_to_html(list_bias_results)
            local_file_path = "../output/fairness_report.html"
            FairnessService.save_html_to_file(html, local_file_path)
            # reportId= FileStoreReportDb.save_file(file=html)
            tenet_id = (self.tenet.find(tenet_name="Fairness"),)
            html_containerName = os.getenv("HTML_CONTAINER_NAME")
            htmlFileId = self.fileStore.save_file(
                file=BytesIO(html.encode("utf-8")),
                filename="fairness_report.html",
                contentType="text/html",
                tenet="Fairness",
                container_name=html_containerName,
            )

            HtmlId = time.time()
            doc = {
                "HtmlId": HtmlId,
                "BatchId": batchId,
                "TenetId": tenet_id,
                "ReportName": "fairness_report.html",
                "HtmlFileId": htmlFileId,
                "CreatedDateTime": datetime.datetime.now(),
            }
            Html.create(doc)

            url = os.getenv("REPORT_URL")
            payload = {"batchId": batchId}
            response = requests.request("POST", url, data=payload, verify=False).json()
            log.info(response)
            if response is None:
                raise HTTPException(
                    status_code=500, detail="Error in generating PDF report"
                )

            return objbias_pretrainanalyzeResponse

    # def analyze(self, payload: dict) -> BiasAnalyzeResponse:

    #     log.info("***************Entering Analyse*************")
    #     log.debug(f"payload: {payload}")
    #     methods = payload.method
    #     biastype = payload.biasType
    #     trainingDataset = AttributeDict(payload.trainingDataset)
    #     tpath = AttributeDict(trainingDataset.path).uri
    #     label = trainingDataset.label

    #     predictionDataset = AttributeDict(payload.predictionDataset)
    #     ppath = AttributeDict(predictionDataset.path).uri
    #     predlabel = predictionDataset.predlabel
    #     features = payload.features.split(",")
    #     protectedAttributes = payload.facet
    #     CategoricalAttributes = payload.categoricalAttributes
    #     if CategoricalAttributes == " ":
    #         CategoricalAttributes = []
    #     else:
    #         CategoricalAttributes = CategoricalAttributes.split(",")
    #     favourableOutcome = [str(i) for i in payload.favourableOutcome]
    #     outputPath = AttributeDict(payload.outputPath).uri
    #     labelmap = payload.labelmaps
    #     if biastype == "POSTTRAIN":
    #         label = predictionDataset.label

    #     attr = {"name": [], "privileged": [], "unprivileged": []}
    #     for i in protectedAttributes:
    #         i = AttributeDict(i)
    #         log.info("=", i)
    #         attr["name"] += [i.name]
    #         attr["privileged"] += [i.privileged]
    #         attr["unprivileged"] += [i.unprivileged]

    #     protectedAttributes = AttributeDict(attr)

    #     taskType = payload.taskType
    #     bucket_dict = FairnessService.parse_nutanix_bucket_object(tpath)
    #     bucket = bucket_dict["bucket_name"]
    #     key = bucket_dict["object_key"]

    #     traindata = NutanixObjectStorage.get_file_content(bucket, key)

    #     s = str(traindata, "utf-8")
    #     traindata = StringIO(s)

    #     bucket_dict = FairnessService.parse_nutanix_bucket_object(ppath)
    #     bucket = bucket_dict["bucket_name"]
    #     key = bucket_dict["object_key"]

    #     testdata = NutanixObjectStorage.get_file_content(bucket, key)
    #     s = str(testdata, "utf-8")
    #     testdata = StringIO(s)

    #     list_bias_results = None
    #     if biastype == "PRETRAIN":
    #         list_bias_results = FairnessService.pretrainedAnalyse(
    #             traindata,
    #             labelmap,
    #             label,
    #             protectedAttributes,
    #             favourableOutcome,
    #             CategoricalAttributes,
    #             features,
    #             biastype,
    #             methods,
    #             False,
    #         )
    #     elif biastype == "POSTTRAIN":
    #         list_bias_results = FairnessService.posttrainedAnalyse(
    #             testdata, label, labelmap, protectedAttributes, taskType, methods, False
    #         )

    #     objbias_pretrainanalyzeResponse = BiasAnalyzeResponse(
    #         biasResults=list_bias_results
    #     )
    #     json_object = objbias_pretrainanalyzeResponse.json()
    #     log.info(f"json_object:{json_object}")

    #     # json_name = '../output/' + "output.json"
    #     # with open(json_name, "w") as outfile:
    #     #     outfile.write(json_object)
    #     #
    #     # buck_dict = FairnessService.parse_nutanix_bucket_object(outputPath)
    #     # bucket_ = buck_dict['bucket_name']
    #     # key_ = buck_dict['object_key']

    #     # NutanixObjectStorage.upload_with_high_threshold(json_name, bucket_, key_, 10)

    #     return objbias_pretrainanalyzeResponse

    def trainMitigate(
        traindata,
        testdata,
        methods,
        label,
        labelmap,
        protectedAttributes,
        taskType,
        mitigationType,
        mitigationTechnique,
        biasType,
        trainingDataset,
        predictionDataset,
    ):
        ds = DataList()
        group_unpriv_tr, group_priv_tr, df_preprocessedTrain, train_orig = (
            ds.preprocessDataset(
                traindata, label, labelmap, protectedAttributes, taskType, False
            )
        )
        group_unpriv_ts, group_priv_ts, df_preprocessedTest, test_orig = (
            ds.preprocessDataset(
                testdata, label, labelmap, protectedAttributes, taskType, False
            )
        )

        y_pred = df_preprocessedTest["labels_pred"]
        true_y = df_preprocessedTest["label"]
        biasResult = BiasResult()
        list_bias_results = biasResult.analyseHoilisticAIBiasResult(
            taskType,
            methods,
            group_unpriv_ts,
            group_priv_ts,
            y_pred,
            true_y,
            protectedAttributes,
        )

        bias_before_mitigation = list_bias_results[0]["biasDetected"]
        original_metric = list_bias_results[0]["metrics"]
        if mitigationType == "PREPROCESSING":
            fileName = trainingDataset.name
            dataset = train_orig
            column_names = df_preprocessedTrain.iloc[:, :-1].columns.values.tolist()
        else:
            fileName = predictionDataset.name
            dataset = test_orig
            column_names = df_preprocessedTest.iloc[:, :-1].columns.values.tolist()
            column_names.remove("label")
        X_train, y_train = ds.target_column_return(df_preprocessedTrain)
        X_test, y_test = ds.target_column_return(df_preprocessedTest, True)
        train_data = X_train, y_train, group_unpriv_tr, group_priv_tr
        test_data = X_test, y_test, group_unpriv_ts, group_priv_ts
        mitigation_object = MitigationResult()
        (
            group_unprivileged,
            group_privileged,
            predicted_y,
            actual_y,
            mitigated_data_df,
        ) = mitigation_object.mitigationResult(
            train_data,
            test_data,
            mitigationType,
            mitigationTechnique,
            dataset,
            column_names,
        )
        list_bias_results_afterMitigation = biasResult.analyseHoilisticAIBiasResult(
            taskType,
            methods,
            group_unprivileged,
            group_privileged,
            predicted_y,
            actual_y,
            protectedAttributes,
        )
        bias = list_bias_results_afterMitigation[0]["biasDetected"]
        metrics = list_bias_results_afterMitigation[0]["metrics"]
        uniqueNm = (
            "Mitigated_"
            + fileName
            + "_"
            + datetime.datetime.now().strftime("%m%d%Y%H%M%S")
            + ".csv"
        )
        mitigation_result_list = mitigation_object.mitigationResultList(
            bias_before_mitigation,
            bias,
            original_metric,
            metrics,
            biasType,
            mitigationType,
            mitigationTechnique,
            uniqueNm,
        )
        # upload mitigated data to nutanix
        filePath = FairnessService.MITIGATED_LOCAL_FILE_PATH + uniqueNm
        uploadPath = FairnessService.MITIGATED_UPLOAD_PATH
        mitigated_data_csv = mitigated_data_df.to_csv(filePath)
        FairnessService.uploadfile_to_db(uploadPath, filePath)
        return mitigation_result_list

    # def mitigate(self, payload: dict) -> MitigationAnalyzeResponse:
    #     log.info("************Entering Mitigation************")
    #     log.debug(f"payload: {payload}")
    #     methods = payload.method
    #     biastype = payload.biasType
    #     mitigationType = payload.mitigationType
    #     mitigationTechnique = payload.mitigationTechnique
    #     taskType = payload.taskType
    #     trainingDataset = AttributeDict(payload.trainingDataset)
    #     trainingDatasetpath = AttributeDict(trainingDataset.path).uri
    #     label = trainingDataset.label

    #     predictionDataset = AttributeDict(payload.predictionDataset)
    #     predictionDatasetpath = AttributeDict(predictionDataset.path).uri
    #     predictionlabel = predictionDataset.predlabel
    #     features = payload.features.split(",")
    #     protectedAttributes = payload.facet
    #     CategoricalAttributes = payload.categoricalAttributes
    #     if CategoricalAttributes == " ":
    #         CategoricalAttributes = []
    #     else:
    #         CategoricalAttributes = CategoricalAttributes.split(",")
    #     favourableOutcome = [str(i) for i in payload.favourableOutcome]
    #     outputPath = AttributeDict(payload.outputPath).uri
    #     labelmap = payload.labelmaps
    #     if biastype == "POSTTRAIN":
    #         label = predictionDataset.label

    #     attr = {"name": [], "privileged": [], "unprivileged": []}
    #     for i in protectedAttributes:
    #         i = AttributeDict(i)
    #         log.info("=", i)
    #         attr["name"] += [i.name]
    #         attr["privileged"] += [i.privileged]
    #         attr["unprivileged"] += [i.unprivileged]

    #     protectedAttributes = AttributeDict(attr)
    #     bucket_dict = FairnessService.parse_nutanix_bucket_object(trainingDatasetpath)
    #     bucket = bucket_dict["bucket_name"]
    #     key = bucket_dict["object_key"]

    #     traindata = NutanixObjectStorage.get_file_content(bucket, key)
    #     s = str(traindata, "utf-8")
    #     traindata = StringIO(s)

    #     bucket_dict = FairnessService.parse_nutanix_bucket_object(predictionDatasetpath)
    #     bucket = bucket_dict["bucket_name"]
    #     key = bucket_dict["object_key"]

    #     testdata = NutanixObjectStorage.get_file_content(bucket, key)
    #     s = str(testdata, "utf-8")
    #     testdata = StringIO(s)
    #     mitigation_result_list = FairnessService.trainMitigate(
    #         traindata,
    #         testdata,
    #         methods,
    #         label,
    #         labelmap,
    #         protectedAttributes,
    #         taskType,
    #         mitigationType,
    #         mitigationTechnique,
    #         biastype,
    #         trainingDataset,
    #         predictionDataset,
    #     )

    #     objbias_pretrainanalyzeResponse = MitigationAnalyzeResponse(
    #         mitigationResults=mitigation_result_list
    #     )

    #     json_object = objbias_pretrainanalyzeResponse.json()
    #     log.info(f"json_object: {json_object}")

        # json_name = '../output/' + "output.json"
        # with open(json_name, "w") as outfile:
        #     outfile.write(json_object)
        #
        # buck_dict = FairnessService.parse_nutanix_bucket_object(outputPath)
        # bucket_ = buck_dict['bucket_name']
        # key_ = buck_dict['object_key']
        #
        # NutanixObjectStorage.upload_with_high_threshold(json_name, bucket_, key_, 10)

        return objbias_pretrainanalyzeResponse

    def preprocessingmitigate(self, payload: dict) -> BiasPretrainMitigationResponse:
        log.info("************Entering preprocessingMitigation************")
        log.debug(f"payload: {payload}")
        methods = payload.method
        biastype = payload.biasType
        mitigationType = payload.mitigationType
        mitigationTechnique = payload.mitigationTechnique
        taskType = payload.taskType
        trainingDataset = AttributeDict(payload.trainingDataset)
        extension = trainingDataset.extension
        fileType = trainingDataset.fileType
        trainingDatasetpath = AttributeDict(trainingDataset.path).uri
        label = trainingDataset.label
        features = payload.features.split(",")
        protectedAttributes = payload.facet
        CategoricalAttributes = payload.categoricalAttributes
        if CategoricalAttributes == " ":
            CategoricalAttributes = []
        else:
            CategoricalAttributes = CategoricalAttributes.split(",")
        favourableOutcome = [str(i) for i in payload.favourableOutcome]
        outputPath = AttributeDict(payload.outputPath).uri
        labelmap = payload.labelmaps

        attr = {"name": [], "privileged": [], "unprivileged": []}
        for i in protectedAttributes:
            i = AttributeDict(i)
            log.info("=", i)
            attr["name"] += [i.name]
            attr["privileged"] += [i.privileged]
            attr["unprivileged"] += [i.unprivileged]

        # get data from csv and convert to dataframe
        df = pandas.read_csv(trainingDatasetpath, sep=",", usecols=features)
        log.info(f"Getting df{df}")

        protectedAttributes = AttributeDict(attr)

        # bucket_dict = FairnessService.parse_nutanix_bucket_object(trainingDatasetpath)
        # bucket = bucket_dict['bucket_name']
        # key = bucket_dict['object_key']
        # traindata = NutanixObjectStorage.get_file_content(bucket, key)
        # s = str(traindata, 'utf-8')
        # traindata = StringIO(s)

        list_bias_results = None
        if mitigationType == "PREPROCESSING":
            Preprocessing_mitigation_result_list, mitigated_df = (
                FairnessService.preprocessingmitigateandtransform(
                    df,
                    labelmap,
                    label,
                    protectedAttributes,
                    favourableOutcome,
                    CategoricalAttributes,
                    features,
                    biastype,
                    methods,
                    mitigationTechnique,
                    True,
                )
            )

        # upload data to MongoDB
        fileName = trainingDataset.name
        uniqueNm = (
            "PMitigated_"
            + fileName
            + "_"
            + datetime.datetime.now().strftime("%m%d%Y%H%M%S")
            + extension
        )
        filePath = FairnessService.MITIGATED_LOCAL_FILE_PATH + uniqueNm
        log.info(f"filepath {filePath}")
        uploadPath = FairnessService.MITIGATED_UPLOAD_PATH
        log.info(f"UploadPath {uploadPath}")
        # mitigated_data_csv=mitigated_df.to_csv(filePath)
        FairnessUIservice.pretrain_save_file(mitigated_df, extension, filePath)
        # encoded_df = pandas.get_dummies(mitigated_df)
        mitigate_data = mitigated_df.to_csv(index=False)
        dt_containerName = os.getenv("Dt_containerName")
        fileId = self.fileStore.save_file(
            file=mitigate_data.encode("utf-8"),
            filename=uniqueNm,
            contentType=fileType,
            tenet="Fairness",
            container_name=dt_containerName,
        )
        # FairnessService.uploadfile_to_mongodb(uploadPath,filePath,fileType)
        objbias_pretrainanalyzeResponse = BiasPretrainMitigationResponse(
            biasResults=Preprocessing_mitigation_result_list, fileName=uniqueNm
        )
        json_object = objbias_pretrainanalyzeResponse.json()
        # log.info('json_object:', json_object)
        return objbias_pretrainanalyzeResponse, fileId

    # Get mitigated data using MONGO DB
    def get_mitigated_data(self, fileName):
        content = self.fileStore.read_file(fileName)
        response = StreamingResponse(
            io.BytesIO(content["data"]), media_type=content["contentType"]
        )
        response.headers["Content-Disposition"] = (
            "attachment; filename=" + content["name"]
        )
        return response

    # def get_mitigated_data(self, fileName):
    #     log.info("Started returning data to user.")
    #     local_csv_file_path=os.path.join(FairnessService.MITIGATED_LOCAL_FILE_PATH,fileName)
    #     #check if the asked file is present locally else download from nutanix and store
    #     if os.path.exists(local_csv_file_path):
    #         return local_csv_file_path
    #     else:
    #        filePath=FairnessService.MITIGATED_UPLOAD_PATH+"//"+fileName
    #        bucket_dict = FairnessService.parse_nutanix_bucket_object(filePath)
    #        bucket = bucket_dict['bucket_name']
    #        key = bucket_dict['object_key']
    #        traindata = NutanixObjectStorage.get_file_content(bucket, key)
    #        if traindata:
    #            with open(local_csv_file_path,'wb') as f:
    #                f.write(traindata)
    #     return local_csv_file_path


class FairnessUIservice:
    def __init__(self, MockDB=None):
        self.api_token=None
        if MockDB is not None:
            self.db = MockDB.db
            self.fileStore = FileStoreReportDb(self.db)
            self.batch = Batch(self.db)
            self.tenet = Tenet(self.db)
            self.dataset = Dataset(self.db)
            self.dataAttributes = DataAttributes(self.db)
            self.dataAttributeValues = DataAttributeValues(self.db)
            self.bias_collection = self.db["bias"]
            self.mitigation_collection = self.db["mitigation"]
            self.mitigation_model_collection = self.db["mitigation_model"]
            self.metrics_collection = self.db["metrics"]
        else:
            self.db = DataBase().db
            self.fileStore = FileStoreReportDb()
            self.batch = Batch()
            self.tenet = Tenet()
            self.dataset = Dataset()
            self.dataAttributes = DataAttributes()
            self.dataAttributeValues = DataAttributeValues()
            self.bias_collection = self.db["bias"]
            self.mitigation_collection = self.db["mitigation"]
            self.mitigation_model_collection = self.db["mitigation_model"]
            self.metrics_collection = self.db["metrics"]
            self.llm_analysis_collection = self.db["llm_analysis"]
            self.llm_connection_credentials_collection = self.db[
                "llm_connection_credentials"
            ]

    request_payload = ""
    mitigation_payload = ""
    pretrainMitigation_payload = ""
    ca_dict = {}

    def pretrain_save_file(df: pandas.DataFrame, extension: str, file_path: str):
        log.info(df, "dataframe")
        log.info(extension, "extension")
        log.info(file_path, "file_path")
        if extension == "csv":
            df.to_csv(file_path, index=False)
        elif extension == "parquet":
            df.to_parquet(file_path, index=False)
        elif extension == "json":
            df.to_json(file_path, index=False, orient="records")
        elif extension == "feather":
            df.to_feather(file_path)

    def get_extension(fileName: str):
        if fileName.endswith(".csv"):
            return "csv"
        elif fileName.endswith(".feather"):
            return "feather"
        elif fileName.endswith(".parquet"):
            return "parquet"
        elif fileName.endswith(".json"):
            return "json"

    def get_data_frame(extension: str, fileName: str):
        # if extension == "csv":
        return pandas.read_csv(os.path.join(FairnessService.LOCAL_FILE_PATH, fileName))
        # elif extension=="parquet":
        #     return pandas.read_parquet(os.path.join(FairnessService.LOCAL_FILE_PATH, fileName))
        # elif extension == "feather":
        #     return pandas.read_feather(os.path.join(FairnessService.LOCAL_FILE_PATH, fileName))
        # elif extension == "json":
        #     return pandas.read_json(os.path.join(FairnessService.LOCAL_FILE_PATH, fileName))

    def store_file_locally(extension, file_content, file_path, file_name):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Create temporary file
            temp_file_name = temp_file.name
            # Write binary data to the temporary file
            file_content = file_content
            temp_file.write(file_content)
            # Reset the file pointer to the beginning for reading
            temp_file.seek(0)

            df = pandas.DataFrame()
            if extension == "csv":
                df = pandas.read_csv(temp_file)
            elif extension == "parquet":
                df = pandas.read_parquet(temp_file)
            elif extension == "feather":
                df = pandas.read_feather(temp_file)
            elif extension == "json":
                df = pandas.read_json(temp_file)
            df.to_csv(os.path.join(file_path, file_name), index=False)
            # Close the temporary file before deletion
            temp_file.close()
        os.remove(temp_file_name)
        # with open(os.path.join(file_path, file_name), 'wb') as f:
        #     f.write(file_content.read())

    # def store_file_locally2(extension,file_content,file_path,file_name):
    #     with tempfile.NamedTemporaryFile(delete=False) as temp_file:
    #         # Create temporary file
    #         temp_file_name = temp_file.name
    #         # Write binary data to the temporary file
    #         # file_content = file_content.read()
    #         temp_file.write(file_content.readall())
    #         # Reset the file pointer to the beginning for reading
    #         temp_file.seek(0)

    #         df = pandas.DataFrame()
    #         if extension == "csv":
    #               df=pandas.read_csv(temp_file)
    #         elif extension=="parquet":
    #               df=pandas.read_parquet(temp_file)
    #         elif extension == "feather":
    #             df=pandas.read_feather(temp_file)
    #         elif extension == "json":
    #             df=pandas.read_json(temp_file)
    #         df.to_csv(os.path.join(file_path, file_name),index=False)
    #         # Close the temporary file before deletion
    #         temp_file.close()
    #     os.remove(temp_file_name)
    #     # with open(os.path.join(file_path, file_name), 'wb') as f:
    #     #     f.write(file_content.read())

    def upload_file(self, payload: dict):
        ca_dict = {}
        enter_time = time.time()
        log.info(f"Entering Upload:{enter_time}")
        biasType = payload["biasType"]
        methodType = payload["methodType"]
        taskType = payload["taskType"]
        fileId = payload["fileId"]
        # FileID = float(fileId)
        content = self.fileStore.read_file(fileId)
        if content is None:
            raise HTTPException(
                status_code=500, detail="No content received from the POST request"
            )
        dataFile = content["data"]
        name_of_dataset = content["name"].split(".")[0]
        # fileName = FileStoreReportDb.getfilename(FileID)
        fileContentType = content["contentType"]
        extension = content["extension"]
        uniqueNm = (
            name_of_dataset
            + "_"
            + datetime.datetime.now().strftime("%m%d%Y%H%M%S")
            + "."
            + extension
        )

        FairnessUIservice.store_file_locally(
            extension, dataFile, FairnessService.LOCAL_FILE_PATH, uniqueNm
        )

        read_file = FairnessUIservice.get_data_frame(extension, uniqueNm)

        feature_list = list(read_file.columns)

        tDataset = TrainingDataset()
        tDataset.id = 32
        tDataset.name = name_of_dataset
        tDataset.fileType = fileContentType
        tDataset.label = ""
        tDataset.extension = extension
        tDataset.path = {
            "storage": "INFY_AICLD_NUTANIX",
            "uri": os.path.join(FairnessService.LOCAL_FILE_PATH, uniqueNm),
        }

        pDataset = PredictionDataset()
        pDataset.id = 32
        pDataset.name = name_of_dataset
        pDataset.fileType = fileContentType
        pDataset.label = ""
        pDataset.extension = extension
        pDataset.predlabel = ""
        pDataset.path = {
            "storage": "INFY_AICLD_NUTANIX",
            "uri": os.path.join(FairnessService.LOCAL_FILE_PATH, uniqueNm),
        }

        request_payload = Bias()
        request_payload.biasType = biasType
        request_payload.method = methodType
        request_payload.taskType = taskType
        request_payload.features = ",".join(feature_list)
        request_payload.trainingDataset = tDataset
        request_payload.predictionDataset = pDataset

        # to create dictionary of CA present in dataset
        st_ti = time.time()
        log.info(f"Entering CA Dict:{st_ti}")
        updated_df = read_file.select_dtypes(exclude="number")
        for each in list(updated_df.columns):
            updated_df.drop(updated_df[(updated_df[each] == "?")].index, inplace=True)
            updated_df[each] = updated_df[each].str.replace(".", "")
            ca_dict[each] = list(updated_df[each].unique())
        log.info(
            f"list of columns remaining in dataset after exclusion :  {updated_df.columns}"
        )
        request_payload.ca_dict = ca_dict
        ex_ti = time.time()
        log.info(f"Exit CA Dict:{ex_ti - st_ti}")
        categorical_attribute = ",".join(list(updated_df.columns))
        request_payload.categoricalAttributes = categorical_attribute
        log.info(f"JSON OBJECT IN UPLOAD: {request_payload}")
        res = self.bias_collection.insert_one(request_payload.model_dump())
        response = {
            "biasType": biasType,
            "methodname": methodType,
            "FileName": name_of_dataset,
            "UploadedFileType": fileContentType,
            "AttributesInTheDataset": {
                "FeatureList ": feature_list,
                "CategoricalAttributesList": list(updated_df.columns),
            },
            "CategoricalAttributesUniqueValues": request_payload.ca_dict,
            "recordId": str(res.inserted_id),
        }
        if response is None:
            raise HTTPException(
                status_code=500, detail="No response received from the POST request"
            )

        exit_time = time.time()
        log.info(f"Exiting Upload:{exit_time - enter_time}")
        return response

    def return_protected_attrib(self, payload: dict):
        fairnessServiceObj = FairnessService()
        record = self.bias_collection.find_one({"_id": ObjectId(payload["recordId"])})
        request_payload = Bias(**record)
        label = payload["label"]
        favourableOutcome = payload["FavourableOutcome"]
        protectedAttribute = payload["ProtectedAttribute"]
        priv = payload["priviledged"]
        labelmap = {}
        for value in request_payload.ca_dict[label]:
            if value == favourableOutcome:
                labelmap[value] = "1"
            else:
                labelmap[value] = "0"

        request_payload.labelmaps = labelmap
        request_payload.trainingDataset.label = label
        request_payload.predictionDataset.label = label
        request_payload.predictionDataset.predlabel = "labels_pred"
        request_payload.favourableOutcome.append(favourableOutcome)
        outcomeList = request_payload.ca_dict[label].copy()
        outcomeList.remove(favourableOutcome)
        unfavourableOutcome = "".join(outcomeList)

        protectedAttribute = protectedAttribute.replace("[", "")
        protectedAttribute = protectedAttribute.replace("]", "")
        protectedAttribute = protectedAttribute.replace('"', "")
        protectedAttribute = protectedAttribute.split(",")

        priv = priv.replace("[", "")
        priv = priv.replace("]", "")
        priv = priv.replace('"', "")
        priv = priv.split(",")

        ca_list = list(request_payload.ca_dict.keys()).copy()
        ca_list.remove(label)

        protected_attribute_list = []

        for pa in protectedAttribute:
            attribute_values = request_payload.ca_dict[pa].copy()
            ca_list.remove(pa)
            for privledged in priv:
                if privledged in attribute_values:
                    request = {}
                    request["name"] = pa
                    request["privileged"] = [privledged]
                    attribute_values.remove(privledged)
                    request["unprivileged"] = attribute_values
                    log.info("Request after each turn:", request)
                    protected_attribute_list.append(request)

        log.info(f"Facets:{protected_attribute_list}")

        request_payload.facet = protected_attribute_list

        request_payload_json = request_payload.model_dump_json()
        self.bias_collection.update_one(
            {"_id": ObjectId(payload["recordId"])},
            {"$set": request_payload.model_dump()},
        )

        request_payload_json = AttributeDict(**json.loads(request_payload_json))
        request_payload_json["categoricalAttributes"] = ",".join(ca_list)
        if FairnessUIservice.validate_json_request(request_payload_json):
            response = fairnessServiceObj.analyzeTenet(request_payload_json)
            if response is None:
                raise HTTPException(
                    status_code=500, detail="No response received from the POST request"
                )
        else:
            response = "Please Input Correct Parameters."
        return response

    def attributes_Data(self, payload: dict):
        enter_time = time.time()
        log.info(f"Entering Upload:{enter_time}")
        FairnessUIservice.ca_dict.clear()
        # datasetID
        fileId = payload["fileId"]
        file_type = "text/csv"
        # reading File from DB
        retrivedata = self.fileStore.read_file(fileId)
        if retrivedata is None:
            raise HTTPException(
                status_code=500, detail="No content received from the POST request"
            )
        dataset = pandas.read_csv(BytesIO(retrivedata["data"]))
        name_of_dataset = retrivedata["name"].split(".")[0]
        # uniqueNm = "sampledata" + datetime.datetime.now().strftime("%m%d%Y%H%M%S")
        # local_path=FairnessService.DATASET_WB_LOCAL_FILE_PATH+ uniqueNm + '.csv'
        # file_name = os.path.basename(local_path)
        # dataset.to_csv(local_path, index=False)
        # log.info(file_name)
        biasType = payload["biasType"]
        methodType = payload["methodType"]
        taskType = payload["taskType"]
        FairnessUIservice.request_payload = open(
            "../output/UIanalyseRequestPayload.txt"
        ).read()
        FairnessUIservice.request_payload = FairnessUIservice.request_payload.replace(
            "{biasType}", biasType
        )

        FairnessUIservice.request_payload = FairnessUIservice.request_payload.replace(
            "{method}", methodType
        )

        FairnessUIservice.request_payload = FairnessUIservice.request_payload.replace(
            "{taskType}", taskType
        )

        FairnessUIservice.request_payload = FairnessUIservice.request_payload.replace(
            "{fileName}", name_of_dataset
        )
        # x = filename.rfind(".")
        # name_of_dataset = filename[:x]
        FairnessUIservice.request_payload = FairnessUIservice.request_payload.replace(
            "{name}", name_of_dataset
        )
        fileContentType = "text/csv"
        # read_file = pandas.read_csv(local_path)
        # # uniqueNm = "output" + datetime.datetime.now().strftime("%m%d%Y%H%M%S")
        # # local_path=FairnessService.DATASET_LOCAL_FILE_PATH+ uniqueNm + '.csv'
        # save_file = read_file.to_csv(local_path, index=False)
        # # FairnessService.uploadfile_to_db(FairnessService.DATASET_UPLOAD_FILE_PATH,local_path)
        # trainingDatasetURL = FairnessService.DATASET_WB_LOCAL_FILE_PATH+  "//" + file_name
        # log.info("Training Dataset URL:", trainingDatasetURL)
        # predictionDatasetURL = trainingDatasetURL
        FairnessUIservice.request_payload = FairnessUIservice.request_payload.replace(
            "{fileid}", fileId
        )
        #
        # FairnessUIservice.request_payload = FairnessUIservice.request_payload.replace('{predictionDatasetURL}',
        #                                                                               predictionDatasetURL)
        feature_list = list(dataset.columns)
        FairnessUIservice.request_payload = FairnessUIservice.request_payload.replace(
            "{features}", ",".join(feature_list)
        )

        # to create dictionary of CA present in dataset
        st_ti = time.time()
        log.info(f"Entering CA Dict:{st_ti}")
        updated_df = dataset.select_dtypes(exclude="number")
        for each in list(updated_df.columns):
            updated_df.drop(updated_df[(updated_df[each] == "?")].index, inplace=True)
            updated_df[each] = updated_df[each].str.replace(".", "")
            FairnessUIservice.ca_dict[each] = list(updated_df[each].unique())
        log.info(
            f"list of columns remaining in dataset after exclusion : {updated_df.columns}"
        )
        ex_ti = time.time()
        log.info(f"Exit CA Dict:{ex_ti - st_ti}")
        categorical_attribute = ",".join(list(updated_df.columns))
        FairnessUIservice.request_payload = FairnessUIservice.request_payload.replace(
            "{categoricalAttributes}", categorical_attribute
        )
        log.info(f"JSON OBJECT IN UPLOAD: {FairnessUIservice.request_payload}")
        response = {
            "biasType": biasType,
            "methodname": methodType,
            "FileName": name_of_dataset,
            "UploadedFileType": fileContentType,
            "AttributesInTheDataset": {
                "FeatureList ": feature_list,
                "CategoricalAttributesList": list(updated_df.columns),
            },
            "CategoricalAttributesUniqueValues": FairnessUIservice.ca_dict,
        }
        if response is None:
            # raise CustomValueError(SERVICE_attributes_Data_METADATA,"No response received from the POST request")
            raise HTTPException(
                status_code=500, detail="No response received from the POST request"
            )

        exit_time = time.time()
        log.info(f"Exiting Upload:{exit_time - enter_time}")

        return response

    def return_protected_attrib_DB(self, payload: dict):

        if payload.Batch_id is None or "":
            log.error("Batch Id id missing")
        enter_time = time.time()
        log.info(f"Entering Upload:{enter_time}")
        batchId = payload.Batch_id
        self.batch.update(batch_id=batchId, value={"Status": "In-progress"})
        # tenet id
        tenet_id = self.tenet.find(tenet_name="Fairness")
        # batch id
        batch_details = self.batch.find(batch_id=batchId, tenet_id=tenet_id)
        log.info(f"Batch Details:{batch_details}")
        # datasetId
        datasetId = batch_details["DataId"]
        # sample data
        dataset_details = self.dataset.find(Dataset_Id=datasetId)

        dataset_attribute_ids = self.dataAttributes.find(
            dataset_attributes=[
                "biasType",
                "methodType",
                "taskType",
                "label",
                "favorableOutcome",
                "protectedAttribute",
                "privilegedGroup",
            ]
        )
        log.info(f"Dataset Attribute Ids:{dataset_attribute_ids}")
        dataset_attribute_values = self.dataAttributeValues.find(
            dataset_id=datasetId,
            dataset_attribute_ids=dataset_attribute_ids,
            batch_id=batchId,
        )
        # dataset_attribute_values = DataAttributeValues.find(dataset_id=datasetId, dataset_attribute_ids=dataset_attribute_ids, IsActive= 'Y')
        dataset_details["biasType"] = dataset_attribute_values[0]
        dataset_details["methodType"] = dataset_attribute_values[1]
        dataset_details["taskType"] = dataset_attribute_values[2]
        dataset_details["label"] = dataset_attribute_values[3]
        dataset_details["favorableOutcome"] = dataset_attribute_values[4]
        dataset_details["protectedAttribute"] = dataset_attribute_values[5]
        dataset_details["privilegedGroup"] = dataset_attribute_values[6]

        biastype = dataset_details["biasType"]
        log.info(f"{biastype}biastype in return_protected_attrib_DB")
        methodtype = dataset_details["methodType"]
        log.info(f"{methodtype}methodtype in return_protected_attrib_DB")
        tasktype = dataset_details["taskType"]
        log.info(f"{tasktype}tasktype in return_protected_attrib_DB")
        label = dataset_details["label"]
        log.info(f"{label}label in return_protected_attrib_DB")
        favourableOutcome = dataset_details["favorableOutcome"]
        log.info(f"{favourableOutcome}favourableOutcome in return_protected_attrib_DB")
        protectedAttribute = dataset_details["protectedAttribute"]
        log.info(
            f"{protectedAttribute}protectedAttribute in return_protected_attrib_DB"
        )
        priv = dataset_details["privilegedGroup"]
        log.info(f"{priv}priv in return_protected_attrib_DB")

        FairnessUIservice.request_payload = FairnessUIservice.request_payload.replace(
            "{label}", label
        )
        FairnessUIservice.request_payload = FairnessUIservice.request_payload.replace(
            "{favourableOutcome}", favourableOutcome
        )
        outcomeList = FairnessUIservice.ca_dict[label]
        outcomeList.remove(favourableOutcome)
        unfavourableOutcome = "".join(outcomeList)
        FairnessUIservice.request_payload = FairnessUIservice.request_payload.replace(
            "{unfavourableOutcome}", unfavourableOutcome
        )

        request_payload_json = json.loads(FairnessUIservice.request_payload)

        protectedAttribute = protectedAttribute.replace("[", "")
        protectedAttribute = protectedAttribute.replace("]", "")
        protectedAttribute = protectedAttribute.replace('"', "")
        protectedAttribute = protectedAttribute.split(",")

        priv = priv.replace("[", "")
        priv = priv.replace("]", "")
        priv = priv.replace('"', "")
        priv = priv.split(",")

        ca_list = list(FairnessUIservice.ca_dict.keys())
        ca_list.remove(label)

        protected_attribute_list = []

        for pa in protectedAttribute:
            attribute_values = FairnessUIservice.ca_dict[pa]
            ca_list.remove(pa)
            for privledged in priv:
                if privledged in attribute_values:
                    request = {}
                    request["name"] = pa
                    request["privileged"] = [privledged]
                    attribute_values.remove(privledged)
                    request["unprivileged"] = attribute_values
                    log.info("Request after each turn:", request)
                    protected_attribute_list.append(request)

        log.info(f"Facets:{protected_attribute_list}")
        request_payload_json["biasType"] = dataset_details["biasType"]
        request_payload_json["method"] = dataset_details["methodType"]
        request_payload_json["taskType"] = dataset_details["taskType"]

        request_payload_json["facet"] = protected_attribute_list
        request_payload_json["categoricalAttributes"] = ",".join(ca_list)
        log.info(f"JSON OBJECT IN get attributes: {request_payload_json}")

        request_payload_json = AttributeDict(request_payload_json)
        if FairnessUIservice.validate_json_request(request_payload_json):
            response = FairnessService.analyzedemo(self, request_payload_json, batchId)
            if response is None:
                # raise CustomHTTPException(SERVICE_return_protected_attrib_DB_METADATA,"no response received from the POST request")
                raise HTTPException(
                    status_code=500, detail="No response received from the POST request"
                )
            self.batch.update(batch_id=batchId, value={"Status": "Completed"})
            # DataAttributeValues.update(dataset_id=datasetId, value={"IsActive": "N"})
        else:
            response = "Please Input Correct Parameters."

        FairnessUIservice.ca_dict.clear()

        return response

    # Individual fairness metrics API
    def getLabels(self, payload: dict):
        fileId = payload["fileId"]
        content = self.fileStore.read_file(fileId)
        dataFile = content["data"]

        name_of_dataset = content["name"].split(".")[0]
        # fileName = FileStoreReportDb.getfilename(fileId)
        fileContentType = content["contentType"]
        extension = content["extension"]
        uniqueNm = (
            name_of_dataset
            + datetime.datetime.now().strftime("%m%d%Y%H%M%S")
            + "."
            + extension
        )

        FairnessUIservice.store_file_locally(
            extension, dataFile, FairnessService.LOCAL_FILE_PATH, uniqueNm
        )
        # convert to dataframe
        read_file = FairnessUIservice.get_data_frame(extension, uniqueNm)

        feature_list = list(read_file.columns)

        features_dict = {}
        # to create dictionary of CA present in dataset
        st_ti = time.time()
        log.info(f"Entering CA Dict:{st_ti}")
        updated_df = read_file
        # for each in list(updated_df.columns):
        #     log.info(each)
        #     log.info(type(updated_df[each]))
        #     if type(updated_df[each])==int:
        #         features_dict[each] = list(updated_df[each].astype(int).unique())
        #     else:
        #         features_dict[each] = list(updated_df[each].unique())

        # need optimization here
        # for features in features_dict:
        #     log.info(type(features_dict[features][0]))
        #     if isinstance(features_dict[features][0], np.int64):
        #         log.info("Inside")
        #         features_dict[features] = [int(i) for i in features_dict[features]]
        log.info(
            f"list of columns remaining in dataset after exclusion : {updated_df.columns}"
        )
        # save in db
        obj = Individual_Fairness()
        obj.local_file_name = uniqueNm
        obj.features_dict = features_dict
        log.info(features_dict)
        ex_ti = time.time()
        res = self.metrics_collection.insert_one(obj.model_dump())
        response = {
            "FileName": name_of_dataset,
            "UploadedFileType": fileContentType,
            "AttributesInTheDataset": {"FeatureList ": feature_list},
            # "AttributesUniqueValues": obj.features_dict,
            "recordId": str(res.inserted_id),
        }
        if response is None:
            raise HTTPException(
                status_code=500, detail="No response received from the POST request"
            )

        return response

    def getScore(self, payload: IndividualFairnessRequest):
        labels = payload.labels
        log.info(labels)
        record = self.metrics_collection.find_one({"_id": ObjectId(payload.recordId)})
        request_payload = Individual_Fairness(**record)
        local_file_name = request_payload.local_file_name
        _, extension = os.path.splitext(local_file_name)
        read_file = FairnessUIservice.get_data_frame(
            extension.lstrip("."), local_file_name
        )
        dataset_list = []
        categorical_features = read_file.select_dtypes(
            include="object"
        ).columns.tolist()
        # remove labels from categorical attributes
        for label in labels:
            if label in categorical_features:
                categorical_features.remove(label)

        for label in labels:
            df = read_file.copy()
            # drop labels other than the current label, so that it will not be considered for fairness
            for label_2 in labels:
                if label != label_2:
                    df = df.drop(label_2, axis=1)

            # customize StandardDataset just for Individual fairness, as we are not considering protected attributes
            dataset_orig = StandardDataset(
                df=df,
                label_name=label,
                favorable_classes=[df[label][0]],
                protected_attribute_names=[],
                privileged_classes=[np.array([])],
                categorical_features=categorical_features,
                features_to_keep=[],
                features_to_drop=[],
                na_values=[],
                custom_preprocessing=None,
                metadata={},
            )
            dataset_list.append(dataset_orig)

        response = []
        scores = []
        util = utils()
        for dataset in dataset_list:
            score_dict = {}
            score = np.round(util.consistency(dataset), 2)
            scores.append(score)
            obj_metric_cs = metricsEntity(
                name="CONSISTENCY",
                description="Individual fairness metric that measures how similar the labels are for similar instances. Score ranges from [0,1], where 1 indicates consistent labels for similar instances.",
                value=float(score[0]),
            )

            score_dict[dataset.label_names[0]] = obj_metric_cs.metricsEntity
            response.append(score_dict)
            if response is None:
                # raise CustomValueError(SERVICE_getScore_METADATA,"No response received from the POST request")
                raise HTTPException(
                    status_code=500, detail="No response received from the POST request"
                )
        return response

    def upload_file_pretrainMitigation(self, payload: dict):
        enter_time = time.time()
        log.info("Entering Upload:", enter_time)
        ca_dict = {}
        pretrainMitigation_payload = Mitigation()
        taskType = payload["taskType"]
        mitigationType = payload["mitigationType"]
        mitigationTechnique = payload["mitigationTechnique"]
        fileId = payload["fileId"]
        # get content from mongodb
        content = self.fileStore.read_file(fileId)
        file_content = content["data"]
        # file_name=FileStoreReportDb.getfilename(fileId)
        name_of_dataset = content["name"].split(".")[0]
        extension = content["extension"]
        uniquenm = name_of_dataset + datetime.datetime.now().strftime("%m%d%Y%H%M%S")
        contentType = content["contentType"]
        FairnessUIservice.store_file_locally(
            extension, file_content, FairnessService.LOCAL_FILE_PATH, uniquenm
        )
        # convert to dataframe
        read_file = pandas.read_csv(
            os.path.join(FairnessService.LOCAL_FILE_PATH, uniquenm)
        )

        tDataset = TrainingDataset()
        tDataset.id = 32
        tDataset.extension = extension
        tDataset.name = name_of_dataset
        tDataset.fileType = contentType
        tDataset.label = ""
        tDataset.path = {
            "storage": "INFY_AICLD_NUTANIX",
            "uri": os.path.join(FairnessService.LOCAL_FILE_PATH, uniquenm),
        }

        pretrainMitigation_payload.taskType = taskType
        pretrainMitigation_payload.mitigationType = mitigationType
        pretrainMitigation_payload.mitigationTechnique = mitigationTechnique
        pretrainMitigation_payload.trainingDataset = tDataset
        pretrainMitigation_payload.biasType = "PRETRAIN"
        pretrainMitigation_payload.method = "ALL"

        feature_list = list(read_file.columns)
        pretrainMitigation_payload.features = ",".join(feature_list)

        # to create dictionary of CA present in dataset
        st_ti = time.time()
        log.info(f"Entering CA Dict:{st_ti}")
        updated_df = read_file.select_dtypes(exclude="number")
        for each in list(updated_df.columns):
            updated_df.drop(updated_df[(updated_df[each] == "?")].index, inplace=True)
            updated_df[each] = updated_df[each].str.replace(".", "")
            ca_dict[each] = list(updated_df[each].unique())

        log.info(
            f"list of columns remaining in dataset after exclusion : {updated_df.columns}"
        )
        ex_ti = time.time()
        log.info(f"Exit CA Dict: {ex_ti - st_ti}")
        categorical_attribute = ",".join(list(updated_df.columns))
        pretrainMitigation_payload.ca_dict = ca_dict
        pretrainMitigation_payload.categoricalAttributes = categorical_attribute
        log.info(f"JSON OBJECT IN UPLOAD: {pretrainMitigation_payload}")
        res = self.mitigation_collection.insert_one(
            pretrainMitigation_payload.model_dump()
        )
        response = {
            "mitigationType": mitigationType,
            "mitigationTechnique": mitigationTechnique,
            "trainFileName": name_of_dataset,
            "UploadedFileType": contentType,
            "AttributesInTheDataset": {
                "FeatureList ": feature_list,
                "CategoricalAttributesList": list(updated_df.columns),
            },
            "CategoricalAttributesUniqueValues": ca_dict,
            "recordId": str(res.inserted_id),
        }
        if response is None:
            # raise CustomValueError(SERVICE_upload_file_Premitigation_METADATA,"No response received from the POST request")
            raise HTTPException(
                status_code=500, detail="No response received from the POST request"
            )
        exit_time = time.time()
        log.info(f"Exiting Upload: {exit_time - enter_time}")
        return response

    def return_pretrainMitigation_protected_attrib(self, payload: dict):
        fairnessServiceObj = FairnessService()
        record = self.mitigation_collection.find_one(
            {"_id": ObjectId(payload["recordId"])}
        )
        log.info(f"Record: {record}")
        pretrainMitigation_payload = Mitigation(**record)
        label = payload["label"]
        favourableOutcome = payload["FavourableOutcome"]
        protectedAttribute = payload["ProtectedAttribute"]
        priv = payload["priviledged"]
        labelmap = {}
        for value in pretrainMitigation_payload.ca_dict[label]:
            if value == favourableOutcome:
                labelmap[value] = "1"
            else:
                labelmap[value] = "0"

        pretrainMitigation_payload.trainingDataset.label = label
        pretrainMitigation_payload.labelmaps = labelmap
        pretrainMitigation_payload.favourableOutcome.append(favourableOutcome)
        outcomeList = pretrainMitigation_payload.ca_dict[label].copy()
        outcomeList.remove(favourableOutcome)
        unfavourableOutcome = "".join(outcomeList)

        # request_payload_json = json.loads(pretrainMitigation_payload)

        protectedAttribute = protectedAttribute.replace("[", "")
        protectedAttribute = protectedAttribute.replace("]", "")
        protectedAttribute = protectedAttribute.replace('"', "")
        protectedAttribute = protectedAttribute.split(",")

        priv = priv.replace("[", "")
        priv = priv.replace("]", "")
        priv = priv.replace('"', "")
        priv = priv.split(",")

        ca_list = list(pretrainMitigation_payload.ca_dict.keys()).copy()
        ca_list.remove(label)

        protected_attribute_list = []

        for pa in protectedAttribute:
            attribute_values = pretrainMitigation_payload.ca_dict[pa].copy()
            ca_list.remove(pa)
            for privledged in priv:
                if privledged in attribute_values:
                    request = {}
                    request["name"] = pa
                    request["privileged"] = [privledged]
                    attribute_values.remove(privledged)
                    request["unprivileged"] = attribute_values
                    log.info("Request after each turn:", request)
                    protected_attribute_list.append(request)

        log.info(f"Facets: {protected_attribute_list}")

        pretrainMitigation_payload.facet = protected_attribute_list
        self.mitigation_collection.update_one(
            {"_id": ObjectId(payload["recordId"])},
            {"$set": pretrainMitigation_payload.model_dump()},
        )
        request_payload_json = pretrainMitigation_payload.model_dump_json()

        request_payload_json = AttributeDict(**json.loads(request_payload_json))
        request_payload_json["categoricalAttributes"] = ",".join(ca_list)
        log.info(f"Final payload in get attributes: {request_payload_json}")
        # request_payload_json = AttributeDict(request_payload_json)
        if FairnessUIservice.validate_pretrain_json_request(request_payload_json):
            response = fairnessServiceObj.preprocessingmitigate(request_payload_json)
            if response is None:
                # raise CustomHTTPException(SERVICE_return_pretrainMitigation_protected_attrib_METADATA,"no response received from the POST request")
                raise HTTPException(
                    status_code=500, detail="No response received from the POST request"
                )
        else:
            response = "Please Input Correct Parameters."

        return response

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

    def validate_mitigate_df(
        filename, protected_attribute, privledged, unprivledged, label, labelmap
    ):
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
                    attr_dict[col_orig_name].append(each[prev_index + 1 :])
                else:
                    attr_dict[col_orig_name] = [each[prev_index + 1 :]]
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
                                transformed_df[key].insert(i, each[prev_index + 1 :])

        transformed_df[label] = transformed_df[label].replace(
            [1, 0], [fav_outcome, unfav_outcome]
        )

        df = pandas.DataFrame.from_dict(transformed_df)
        unique_nm = datetime.datetime.now().strftime("%m%d%Y%H%M%S")
        mitigated_df_filename = (
            "../output/transformedDataset/output/mitigateDF" + unique_nm + ".csv"
        )
        df.to_csv(mitigated_df_filename, index=False)
        return mitigated_df_filename

    # def mitigate(payload: dict):
    #     log.debug(f"payload: {payload}")
    #     biastype = payload.biasType
    #     mitigationType = payload.mitigationType
    #     mitigationTechnique = payload.mitigationTechnique
    #     trainingDataset = AttributeDict(payload.trainingDataset)
    #     trainingDatasetpath = AttributeDict(trainingDataset.path).uri
    #     label = trainingDataset.label

    #     predictionDataset = AttributeDict(payload.predictionDataset)
    #     predictionDatasetpath = AttributeDict(predictionDataset.path).uri
    #     predictionlabel = predictionDataset.predlabel
    #     features = payload.features.split(",")
    #     protectedAttributes = payload.facet
    #     CategoricalAttributes = payload.categoricalAttributes
    #     if CategoricalAttributes == " ":
    #         CategoricalAttributes = []
    #     else:
    #         CategoricalAttributes = CategoricalAttributes.split(",")
    #     favourableOutcome = [str(i) for i in payload.favourableOutcome]
    #     outputPath = AttributeDict(payload.outputPath).uri
    #     labelmap = payload.labelmaps
    #     if biastype == "POSTTRAIN":
    #         label = predictionDataset.label

    #     attr = {"name": [], "privileged": [], "unprivileged": []}
    #     for i in protectedAttributes:
    #         i = AttributeDict(i)
    #         attr["name"] += [i.name]
    #         attr["privileged"] += [i.privileged]
    #         attr["unprivileged"] += [i.unprivileged]

    #     protectedAttributes = AttributeDict(attr)

    #     bucket_dict = FairnessService.parse_nutanix_bucket_object(trainingDatasetpath)
    #     bucket = bucket_dict["bucket_name"]
    #     key = bucket_dict["object_key"]

    #     traindata = NutanixObjectStorage.get_file_content(bucket, key)
    #     s = str(traindata, "utf-8")
    #     traindata = StringIO(s)

    #     bucket_dict = FairnessService.parse_nutanix_bucket_object(predictionDatasetpath)
    #     bucket = bucket_dict["bucket_name"]
    #     key = bucket_dict["object_key"]

    #     testdata = NutanixObjectStorage.get_file_content(bucket, key)
    #     s = str(testdata, "utf-8")
    #     testdata = StringIO(s)

    #     ds = DataList()
    #     datalist = ds.getDataList(
    #         traindata,
    #         testdata,
    #         labelmap,
    #         label,
    #         protectedAttributes,
    #         favourableOutcome,
    #         CategoricalAttributes,
    #         features,
    #         predictionlabel,
    #         biastype,
    #     )
    #     mitigation_res = MitigationResult()
    #     mitigation_result_list = mitigation_res.mitigateResult(
    #         mitigationType, mitigationTechnique, datalist
    #     )
    #     fileNm = "../output/transformedDataset/transformed_df.csv"
    #     mitigated_file_path = FairnessUIservice.validate_mitigate_df(
    #         filename=fileNm,
    #         protected_attribute=attr["name"],
    #         privledged=attr["privileged"],
    #         unprivledged=attr["unprivileged"],
    #         label=label,
    #         labelmap=labelmap,
    #     )
    #     response = MitigationAnalyzeResponse(mitigationResults=mitigation_result_list)
    #     objbias_pretrainanalyzeResponse = {
    #         "response": response,
    #         "file_path": mitigated_file_path,
    #     }
    #     return objbias_pretrainanalyzeResponse

    # def mitigation_model_get_mitigated_model_name_analyze(self, payload: dict):
    #     record_id = payload["recordId"]
    #     label = payload["label"]

    #     sensitive_features_str = payload["sensitiveFeatures"]

    #     sensitive_features_str = sensitive_features_str.replace("[", "")
    #     sensitive_features_str = sensitive_features_str.replace("]", "")

    #     sensitive_features = [str.strip() for str in sensitive_features_str.split(",")]

    #     record = self.mitigation_model_collection.find_one({"_id": ObjectId(record_id)})

    #     mitigation_model_payload = MitigationModel(**record)

    #     model_url = mitigation_model_payload.modelURL
    #     training_dataset_url = mitigation_model_payload.trainingDatasetURL
    #     testing_dataset_url = mitigation_model_payload.testingDatasetURL

    #     bucket_dict_model = FairnessService.parse_nutanix_bucket_object(model_url)
    #     bucket_dict_training_dataset = FairnessService.parse_nutanix_bucket_object(
    #         training_dataset_url
    #     )
    #     bucket_dict_testing_dataset = FairnessService.parse_nutanix_bucket_object(
    #         testing_dataset_url
    #     )

    #     bucket_model = bucket_dict_model["bucket_name"]
    #     key_model = bucket_dict_model["object_key"]

    #     bucket_training_dataset = bucket_dict_training_dataset["bucket_name"]
    #     key_training_dataset = bucket_dict_training_dataset["object_key"]

    #     bucket_testing_dataset = bucket_dict_testing_dataset["bucket_name"]
    #     key_testing_datset = bucket_dict_testing_dataset["object_key"]

    #     model = NutanixObjectStorage.get_file_content(bucket_model, key_model)
    #     training_dataset = NutanixObjectStorage.get_file_content(
    #         bucket_training_dataset, key_training_dataset
    #     )
    #     testing_dataset = NutanixObjectStorage.get_file_content(
    #         bucket_testing_dataset, key_testing_datset
    #     )

    #     model = BytesIO(model)
    #     training_dataset = BytesIO(training_dataset)
    #     testing_dataset = BytesIO(testing_dataset)

    #     model = joblib.load(model)
    #     df_train = pandas.read_csv(training_dataset)
    #     df_test = pandas.read_csv(testing_dataset)

    #     x_train = df_train.drop(label, axis=1)
    #     y_train = df_train[label]

    #     x_test = df_test.drop(label, axis=1)
    #     y_test = df_test[label]

    #     df_train_sensitive_features = df_train[sensitive_features]
    #     df_test_sensitive_features = df_test[sensitive_features]

    #     metrics_before_optimization = {}
    #     metrics_after_optimization = {}

    #     y_pred = model.predict(x_test)

    #     metrics_before_optimization = FairnessUIservice.mitigation_model_analyze(
    #         y_test, y_pred, df_test_sensitive_features
    #     )

    #     optimal_optimizer = None
    #     optimal_equalized_odds_difference_value = None
    #     optimal_y_pred = None

    #     iteration_count = 12

    #     for iteration in range(iteration_count):
    #         optimizer = ThresholdOptimizer(
    #             estimator=model,
    #             constraints="equalized_odds",
    #             objective="balanced_accuracy_score",
    #             predict_method="auto",
    #             prefit=True,
    #         )

    #         optimizer.fit(
    #             x_train, y_train, sensitive_features=df_train_sensitive_features
    #         )

    #         y_pred = optimizer.predict(
    #             x_test, sensitive_features=df_test_sensitive_features
    #         )

    #         current_equalized_odds_difference_value = equalized_odds_difference(
    #             y_test, y_pred, sensitive_features=df_test_sensitive_features
    #         )

    #         if (
    #             optimal_optimizer == None
    #             or current_equalized_odds_difference_value
    #             < optimal_equalized_odds_difference_value
    #         ):
    #             optimal_optimizer = optimizer
    #             optimal_equalized_odds_difference_value = (
    #                 current_equalized_odds_difference_value
    #             )
    #             optimal_y_pred = y_pred

    #         if (
    #             optimal_equalized_odds_difference_value
    #             < metrics_before_optimization["equalized_odds_difference"]
    #         ):

    #             break

    #     metrics_after_optimization = FairnessUIservice.mitigation_model_analyze(
    #         y_test, optimal_y_pred, df_test_sensitive_features
    #     )

    #     model_unique_name = "mitigated_model_" + datetime.datetime.now().strftime(
    #         "%m%d%Y%H%M%S"
    #     )
    #     local_path_model = (
    #         FairnessService.MITIGATED_MODEL_LOCAL_PATH + model_unique_name + ".joblib"
    #     )

    #     joblib.dump(optimal_optimizer, local_path_model)

    #     FairnessService.uploadfile_to_db(
    #         FairnessService.MITIGATED_MODEL_UPLOAD_PATH, local_path_model
    #     )

    #     able_to_optimize = (
    #         metrics_after_optimization["equalized_odds_difference"]
    #         <= metrics_before_optimization["equalized_odds_difference"]
    #     )

    #     response = {
    #         "mitigated_model_file_name": model_unique_name + ".joblib",
    #         "able_to_optimize": able_to_optimize,
    #     }

    #     if able_to_optimize:
    #         response["metrics_before_optimization"] = metrics_before_optimization
    #         response["metrics_after_optimization"] = metrics_after_optimization

    #     return response

    # def get_mitigated_model(self, filename: str):
    #     upload_model_path = (
    #         FairnessService.MITIGATED_MODEL_UPLOAD_PATH + "//" + filename
    #     )

    #     bucket_dict = FairnessService.parse_nutanix_bucket_object(upload_model_path)

    #     bucket = bucket_dict["bucket_name"]
    #     key = bucket_dict["object_key"]

    #     model = NutanixObjectStorage.get_file_content(bucket, key)

    #     model = BytesIO(model)
    #     model = joblib.load(model)

    #     local_path = FairnessService.MITIGATED_MODEL_LOCAL_PATH + filename

    #     joblib.dump(model, local_path)

    #     return local_path

    # def chat_interaction_image(self,prompt_template, data_url):
    #     engine_name = os.getenv("OPENAI_ENGINE_NAME")
    #     engine_name = engine_name.strip()
    #     if engine_name == "" or engine_name is None:
    #         raise HTTPException(status_code=500, detail="OpenAI Engine Name not found")
    #     try:
    #         completion = self.client.chat.completions.create(
    #             model=engine_name,
    #             messages=[
    #                 {"role": "system", "content": "You are a helpful assistant."},
    #                 {
    #                     "role": "user",
    #                     "content": [
    #                         {"type": "text", "text": prompt_template},
    #                         {"type": "image_url", "image_url": {"url": data_url}},
    #                     ],
    #                 },
    #             ],
    #             temperature=0.3,
    #             max_tokens=800,
    #             top_p=0.95,
    #             frequency_penalty=0,
    #             presence_penalty=0,
    #         )

    #         response = completion.choices[0].message.content
    #     except Exception as e:
    #         raise e

    #     return response

    def image_to_data_url(image_name, image_content):
        mime_type, _ = guess_type(image_name)

        if mime_type is None:
            mime_type = "application/octet-stream"

        image_buffer = ""

        with BytesIO() as image_buffer:
            image_content.save(image_buffer, format=image_content.format)
            base64_encoded_data = base64.b64encode(image_buffer.getvalue()).decode(
                "utf-8"
            )

        return f"data:{mime_type};base64,{base64_encoded_data}"

    def get_analysis_image(self, payload: dict):
        prompt = payload["prompt"]

        image = payload["image"]

        image_name = image.filename
        image_file = image.file
        image_content = Image.open(image_file)

        evaluator = payload["evaluator"]

        if evaluator is None or evaluator=="":
             # Create LLM connection using the factory method
            llm_connection = create_llm_connection()

            # Get the active LLM name and instance
            active_llm_name = llm_connection.get_active_llm()
            llm_instance = llm_connection.llm_instance  # Access the actual LLM instance

            # Your existing prompt template logic
            if isinstance(llm_instance, Azureopenai):
                prompt_template = GPT_4O_IMAGE_PROMPT_TEMPLATE
                data_url=FairnessUIservice.image_to_data_url(image_name, image_content)
                # Use the LLM connection
                result = llm_connection.get_image_completion(prompt_template, data_url)

            elif isinstance(llm_instance, GeminiFlash) or isinstance(llm_instance, GeminiPro):
                prompt_template = GEMINI_IMAGE_PROMPT_TEMPLATE
                # Use the LLM connection
                result = llm_connection.get_image_completion(
                    prompt_template.format(input_placeholder=prompt) if hasattr(prompt_template, 'format') else prompt_template, image_content)
            
            elif isinstance(llm_instance, AWS):
                prompt_template = AWS_IMAGE_TEMPLATE
                data_url=FairnessUIservice.image_to_data_url(image_name, image_content)
                # Use the LLM connection
                result = llm_connection.get_image_completion(prompt_template, data_url)
                # Handle AWS response parsing
                if '{{' in result:
                    start_idx = result.find('{{') + 1
                    end_idx = result.rfind('}}')
                    json_str = result[start_idx:end_idx+1]
                else:
                    start_idx = result.find('{')
                    end_idx = result.rfind('}')
                    json_str = result[start_idx:end_idx+1]

                result = json.loads(json_str)

                return result  # Return the dictionary directly
            else:
                    return {"error": "Unsupported LLM type for image analysis"}

            return json.loads(result[result.find('{'): result.find('}')+1])

        else:

            evaluator = evaluator.upper()

            if(evaluator==GPT_4O):
                openai_instance = Azureopenai()
                prompt_template=GPT_4O_IMAGE_PROMPT_TEMPLATE

                data_url=FairnessUIservice.image_to_data_url(image_name, image_content)
                # Use the instance of Azureopenai to get image completion
                result = openai_instance.get_image_completion(prompt_template, data_url)
                result = json.loads(result[result.find('{'): result.find('}')+1])

            elif(evaluator=="GEMINI_2.5_FLASH"):
                gemini_instance = GeminiFlash()
                prompt_template = GEMINI_IMAGE_PROMPT_TEMPLATE
                # Use the instance of Gemini to get image completion
                result = gemini_instance.get_image_completion(
                    prompt_template.format(input_placeholder=prompt) if hasattr(prompt_template, 'format') else prompt_template,
                    image_content
                    )
                result = json.loads(result[result.find('{'): result.find('}')+1])
            
            elif(evaluator=="GEMINI_2.5_PRO"):
                gemini_instance = GeminiPro()
                prompt_template = GEMINI_IMAGE_PROMPT_TEMPLATE
                # Use the instance of Gemini to get image completion
                result = gemini_instance.get_image_completion(
                    prompt_template.format(input_placeholder=prompt) if hasattr(prompt_template, 'format') else prompt_template,
                    image_content
                    )
                result = json.loads(result[result.find('{'): result.find('}')+1])
            
            elif(evaluator=='AWS_CLAUDE_V3_5'):
                aws_instance = AWS()
                prompt_template = AWS_IMAGE_TEMPLATE
                data_url=FairnessUIservice.image_to_data_url(image_name, image_content)
                # Use the LLM connection
                result = aws_instance.get_image_completion(prompt_template, data_url)
                # Handle AWS response parsing
                if '{{' in result:
                    start_idx = result.find('{{') + 1
                    end_idx = result.rfind('}}')
                    json_str = result[start_idx:end_idx+1]
                else:
                    start_idx = result.find('{')
                    end_idx = result.rfind('}')
                    json_str = result[start_idx:end_idx+1]

                result = json.loads(json_str)

            else:
                result="Please select a valid evaluator"

            return result

    # def chat_interaction_text(self,prompt_template, text):
    #     try:
    #         engine_name = os.getenv("OPENAI_ENGINE_NAME")
    #         engine_name = engine_name.strip()
    #         if engine_name == "" or engine_name is None:
    #             raise HTTPException(
    #                 status_code=500, detail="OpenAI Engine Name not found"
    #             )
    #         prompt = prompt_template.format(input_placeholder=text)

    #         message_text = [
    #             {"role": "system", "content": prompt},
    #             {"role": "user", "content": text},
    #         ]

    #         completion = self.client.chat.completions.create(
    #             model=engine_name,
    #             messages=message_text,
    #             temperature=0.3,
    #             max_tokens=800,
    #             top_p=0.95,
    #             frequency_penalty=0,
    #             presence_penalty=0,
    #             stop=None,
    #         )

    #         output = completion.choices[0].message.content

    #     except Exception as e:
    #         raise e

    #     return output
    
    def get_new_token(self):
        url = os.getenv("API_TOKEN_URL")
        headers = {
            "Content-Type": "application/json"
        }
        ssl_verify=os.getenv("VERIFY_SSL").strip()
        verify = False if ssl_verify == "False" else True
        response = requests.request("GET",url,  headers=headers, verify=verify)
        if response.status_code == 200:
            token = response.json().get("access_token")
            self.api_token=token #storing the token
            return token
        else:
            raise Exception("Failed to fetch new token. Status Code: {}".format(response.status_code))
    
    def call_api(self,prompt,recur_count=0):
        """Call the API, refreshing the token if it's expired."""
        # If there's no token, get a new one
        if not self.api_token:
            log.info("No valid token found. Getting a new one...")
            self.api_token = self.get_new_token()
        
        url = os.getenv("LLAMA_API_URL")
        payload = json.dumps({
        "model": os.getenv("LLAMA_AI_CLOUD_MODEL"),
        "messages": [
            {
            "role": "user",
            "content": prompt
            }
        ],
        "temperature": os.getenv("LLAMA_AI_CLOUD_TEMPRATURE"),
        "top_p": os.getenv("LLAMA_AI_CLOUD_TOP_P"),
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "max_tokens": 800,
        "stop": None
        })
        headers = {
        'Content-Type': 'application/json',
        'Accept': '*',
        'X-Cluster': 'H100',
        'Authorization': f'Bearer {self.api_token}'
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)
        # if the token is expired, get a new one
        if response.status_code==401:
            if recur_count>3:
                log.info("Unable to generate token")
                raise HTTPException(500,"Internal Server error")
            
            log.info("Token expired. Getting a new one...")
            self.api_token = self.get_new_token()
            return self.call_api(prompt,recur_count+1)
    
        
        recur_count=0
    
        response=json.loads(response.content)
        print(f"response {response}")
        return response
    
    # Function to extract JSON from response
    def extract_json(self,response_text):
        try:
            extraction_methods = [
                lambda x: json.loads(re.search(r'```json(.*?)```', x, re.DOTALL).group(1).strip()) if re.search(r'```json(.*?)```', x, re.DOTALL) else None,
                lambda x: json.loads(re.search(r'\{.*\}', x, re.DOTALL).group(0)) if re.search(r'\{.*\}', x, re.DOTALL) else None,
                lambda x: json.loads(re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', x)[-1]) if re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', x) else None
            ]
            for method in extraction_methods:
                try:
                    extracted_json = method(response_text)
                    if extracted_json:
                        return extracted_json
                except Exception as e:
                    continue
            return None
        except Exception as e:
            return None

    def mixtral(self, prompt):
        try:
            url = os.getenv("MIXTRAL_URL")

            payload = {
                "inputs": [prompt],
                "parameters": {"max_new_tokens": 200, "temperature": 0.3},
            }

            json_payload = json.dumps(payload)

            headers = {
                "access-token": os.getenv("MIXTRAL_ACCESS_TOKEN"),
                "Content-Type": "application/json",
            }

            response = requests.post(
                url, data=json_payload, headers=headers, verify=False
            )
            if response.status_code == 200:
                predictions = response.json()
            elif response.status_code == 401:
                raise HTTPException(
                    status_code=500,
                    detail="Unauthorized request. Please check the access token.",
                )
            else:
                log.info("Please check the URL or try again later.", response.text)
                raise Exception(
                    status_code=500, detail="Please check the URL or try again later."
                )
        except Exception as e:
            raise e
        json_data = ast.literal_eval(predictions["content"])
        log.info("Json_data", json_data)
        return json_data["generated_text"]

    def get_token_value(self, category, name):
        record = self.llm_analysis_collection.find_one(
            {"$and": [{"category": category}, {"name": name}, {"active": True}]}
        )

        llm_analysis_payload = LlmAnalysis(**record)

        response = llm_analysis_payload.value

        return response

    def get_analysis_llm(self, payload: dict):
        response = payload["response"]
        evaluator = payload["evaluator"]

        if evaluator is None or evaluator == '':
        # Create LLM connection using the factory method
            llm_connection = create_llm_connection()
            # Get the active LLM name and instance
            active_llm_name = llm_connection.get_active_llm()
            llm_instance = llm_connection.llm_instance  # Access the actual LLM instance

            # Your existing prompt template logic
            if isinstance(llm_instance, Azureopenai):
                prompt_template = GPT_4O_TEXT_PROMPT_TEMPLATE
            elif isinstance(llm_instance, GeminiFlash) or isinstance(llm_instance, GeminiPro):
                prompt_template = GEMINI_PROMPT_TEMPLATE
            elif isinstance(llm_instance, AWS):
                prompt_template = AWS_TEXT_TEMPLATE
            prompt = prompt_template.format(input_placeholder=response)

            # # Choose prompt template based on LLM name
            # if active_llm_name == 'openai':
            #     prompt_template = GPT_4O_TEXT_TEMPLATE
            # # elif active_llm_name == 'gemini':
            # #     prompt_template = GEMINI_TEXT_TEMPLATE

            # Use the LLM connection
            result = llm_connection.get_chat_completion(prompt, response)

            return json.loads(result[result.find('{'): result.find('}')+1])

        else:
            evaluator = evaluator.upper()
            result = {}

            if(evaluator==GPT_4O or evaluator==GPT_4) :
                openai_instance = Azureopenai()
                prompt_template=GPT_4O_TEXT_PROMPT_TEMPLATE
                prompt = prompt_template.format(input_placeholder=response)
                 # Use the instance of Azureopenai to get chat completion
                result = openai_instance.get_chat_completion(prompt, response)
                return json.loads(result[result.find('{'): result.find('}')+1])

            elif(evaluator=="GEMINI_2.5_FLASH"):
                gemini_instance = GeminiFlash()
                prompt_template=GEMINI_PROMPT_TEMPLATE
                prompt = prompt_template.format(input_placeholder=response)
                # Use the instance of Gemini to get chat completion
                result = gemini_instance.get_chat_completion(prompt, response)
                return json.loads(result[result.find('{'): result.find('}')+1])
            
            elif(evaluator=="GEMINI_2.5_PRO"):
                gemini_instance = GeminiPro()
                prompt_template=GEMINI_PROMPT_TEMPLATE
                prompt = prompt_template.format(input_placeholder=response)
                # Use the instance of Gemini to get chat completion
                result = gemini_instance.get_chat_completion(prompt, response)
                return json.loads(result[result.find('{'): result.find('}')+1])
            
            elif evaluator == 'AWS_CLAUDE_V3_5':
                aws_instance = AWS()
                prompt_template=AWS_TEXT_TEMPLATE
                prompt_template= prompt_template.format(input_placeholder=response)
                # Use the instance of AWS to get chat completion
                result = aws_instance.get_chat_completion(prompt_template, response)
                return json.loads(result[result.find('{'): result.find('}')+1])

            elif evaluator == 'LLAMA':
 
                prompt_template=LLAMA_TEXT_TEMPLATE
                prompt=prompt_template.format(
                    input_placeholder=response
                )
                
                llama_response=self.call_api(prompt)
                llama_response = llama_response['choices'][0]['message']['content']
                # Extract and process the JSON from Llama response
                result = self.extract_json(llama_response)
            elif evaluator == MIXTRAL:
                prompt_template = MIXTRAL_PROMPT_TEMPLATE

                result = FairnessUIservice().mixtral(
                    prompt_template.format(input_placeholder=response)
                )
                result = json.loads(result[result.find("{") : result.find("}") + 1])
            else:
                result = "Please select a valid evaluator"

        return result

