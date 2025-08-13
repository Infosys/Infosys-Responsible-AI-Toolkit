"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
import os
import sys
from io import BytesIO
from gridfs import GridFS, GridOut
from mongomock import gridfs
from fairness.service.service import FairnessUIservice
from fairness.service.service_utils import Utils
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from fairness.dao.WorkBench.FileStoreDb import FileStoreReportDb
from fairness.mappers.mappers import BiasAnalyzeRequest, BiasAnalyzeResponse, GetMitigationRequest, IndividualFairnessRequest, MitigateBiasRequest, GetBiasResponse, \
    GetBiasRequest, MitigationAnalyzeResponse, PreprocessingMitigationAnalyzeResponse, PreprocessingMitigateBiasRequest,BatchId
from gridfs.errors import NoFile, FileExists
from test.MockDB import Database_MockDB
import pytest
from pytest_mock import mocker
from mongomock import MongoClient
from dotenv import load_dotenv
import requests
# from ..conftest import DummyCollection
# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fairness.service.preprocessing import FairnessServicePreproc
from fairness.service.preprocessing import FairnessUIservicePreproc
service = FairnessServicePreproc()
UIservice = FairnessUIservicePreproc()
load_dotenv()


class TestUpload_file_pretrain:
    @classmethod
    def setup_class(cls):
        cls.fileId = 1714378168.1872904
        cls.mitigationType = 'PREPROCESSING'
        cls.mitigationTechnique = 'REWEIGHING'
        cls.taskType = 'CLASSIFICATION'
        
        cls.payload = {
            'mitigationType': cls.mitigationType,
            'mitigationTechnique': cls.mitigationTechnique,
            'taskType': cls.taskType,
            'fileId': cls.fileId
        }
        cls.uiservice = FairnessUIservicePreproc()
    
    def test_mitigationType_None(self):
        self.payload['mitigationType'] = None
        with pytest.raises(Exception):
            self.uiservice.upload_file_pretrainMitigation(self.payload)
    
    def test_assert_mitigationTechnique_None(self):
        self.payload['mitigationTechnique'] = None
        with pytest.raises(Exception):
            self.uiservice.upload_file_pretrainMitigation(self.payload)
    
    
    def test_assert_classification_none(self):
        self.payload['taskType'] = None
        with pytest.raises(Exception):
            self.uiservice.upload_file_pretrainMitigation(self.payload)
    
    def test_assert_fileId_none(self):
        self.payload['fileId'] = None
        with pytest.raises(Exception):
            self.uiservice.upload_file_pretrainMitigation(self.payload)
    
    def test_successfulGetUpload_file_pretrain(self,setup_database):
        fairnessUiService=FairnessUIservicePreproc(setup_database[0])
        params = {
            'fileId': setup_database[1],
            'MitigationType': 'PREPROCESSING',
            'MitigationTechnique': 'REWEIGHING',
            'taskType': 'CLASSIFICATION'

        } 
        get_result = fairnessUiService.upload_file_pretrainMitigation(params)
        assert all(get_result.get(key) is not None for key in ['mitigationType','mitigationTechnique','trainFileName','UploadedFileType','AttributesInTheDataset'])

class TestReturnProtectedAttribDB:
    def test_assert_batchid_return(self,setup_database):
        fairnessUiServicebatch=FairnessUIservicePreproc(setup_database[0])
        BatchId_=setup_database[2]
        batchId=BatchId(Batch_id=BatchId_)
        getLabel_result = fairnessUiServicebatch.return_pretrainMitigation_protected_attrib(batchId)

    def test_assert_batchid_returnNone(self,setup_database):
        fairnessUiServicebatch=FairnessUIservicePreproc(setup_database[0])
        BatchId_=setup_database[2]
        batchId=None
        with pytest.raises(AttributeError): 
            getLabel_result = fairnessUiServicebatch.return_pretrainMitigation_protected_attrib(batchId)


class Test_analyse:
    def test_successfulGetUpload_file_analyse(self,setup_database):
        fairnessUiService=FairnessUIservicePreproc(setup_database[0])
        params = {
            'fileId': setup_database[1],
            'biasType': 'PRETRAIN',
            'methodType':'ALL',
            'taskType': 'CLASSIFICATION'

        } 
        get_result = fairnessUiService.analyse_UploadFile(params)
        assert all(get_result.get(key) is not None for key in ['biasType','methodname','FileName','UploadedFileType','AttributesInTheDataset'])

class Test_analyze_results:
    def test_analyze_batchid_return(self,setup_database):
        fairnessUiServicebatch=FairnessUIservicePreproc(setup_database[0])
        BatchId_=setup_database[2]
        batchId=BatchId(Batch_id=BatchId_)
        getLabel_result = fairnessUiServicebatch.return_protected_attrib_analyseDB(batchId)
        assert getLabel_result is not None
    
    def test_analyze_batchid_return(self,setup_database):
        fairnessUiServicebatch=FairnessUIservicePreproc(setup_database[0])
        BatchId_=setup_database[2]
        batchId=None
        with pytest.raises(AttributeError):
            getLabel_result = fairnessUiServicebatch.return_protected_attrib_analyseDB(batchId)