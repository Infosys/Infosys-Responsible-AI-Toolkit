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
from fairness.service.service import FairnessService
from fairness.service.service import FairnessUIservice
from fastapi import UploadFile
from starlette.datastructures import Headers
import os
from io import BytesIO
service = FairnessService()
UIservice = FairnessUIservice()
load_dotenv()

global_recordId = None
recordId = None
global_recordId_Pretrain = None
global_recordId_model = None

class TestUploadFile:
    def test_assert_fileId_type_uploadfile(self,setup_database):
        global global_recordId
        obj=setup_database[0]
        file_id = setup_database[1]
        fairnessUiService=FairnessUIservice(obj)
        params = {
            'methodType': 'ALL',
            'biasType': 'PRETRAIN',
            'taskType': 'CLASSIFICATION',
            'fileId': file_id
        }
        
        getLabel_result = fairnessUiService.upload_file(params)
        assert all(getLabel_result.get(key) is not None for key in ['biasType','methodname','FileName','UploadedFileType','AttributesInTheDataset'])
        global_recordId = getLabel_result.get('recordId')


class Test_return_protected_attrib:

    def test_assert_fileId_type_attr(self,setup_database):
        global global_recordId
        obj=setup_database[0]
        file_id = setup_database[1]
        fairnessUiService=FairnessUIservice(obj)
        params = {
            'label': 'income-per-year',
            'FavourableOutcome':'>50K',
            'ProtectedAttribute':'race',
            'priviledged':'White',
            'recordId': global_recordId  
        }
        
        getLabel_result = fairnessUiService.return_protected_attrib(params)
        assert getLabel_result.biasResults is not None

class Test_attributes_Data:
    def test_return_Result(self,setup_database):
        obj=setup_database[0]
        file_id = setup_database[1]
        fairnessUiService=FairnessUIservice(obj)
        params = {
            'methodType': 'ALL',
            'biasType': 'PRETRAIN',
            'taskType': 'CLASSIFICATION',
            'fileId': file_id
        }
        
        getLabel_result = fairnessUiService.attributes_Data(params)
        assert all(getLabel_result.get(key) is not None for key in ['biasType','methodname','FileName','UploadedFileType','AttributesInTheDataset'])

class Test_return_protected_attrib_DB:
    def test_assert_batchid_return(self,setup_database):
        fairnessUiServicebatch=FairnessUIservice(setup_database[0])
        BatchId_=setup_database[2]
        batchId=BatchId(Batch_id=BatchId_)
        getLabel_result = fairnessUiServicebatch.return_protected_attrib_DB(batchId)
        assert getLabel_result.biasResult is not None
    
    def test_assert_batchid_return(self,setup_database):
        fairnessUiServicebatch=FairnessUIservice(setup_database[0])
        BatchId_=setup_database[2]
        batchId=None
        with pytest.raises(AttributeError):
            getLabel_result = fairnessUiServicebatch.return_protected_attrib_DB(batchId)


class Test_getLabels:
    def test_getlabel_result(self,setup_database):
        global recordId
        obj=setup_database[0]
        file_id = setup_database[1]
        fairnessUiService=FairnessUIservice(obj)
        params = {
            'fileId': file_id
        }
        
        getLabel_result = fairnessUiService.getLabels(params)
        recordId = getLabel_result.get('recordId')
        assert getLabel_result is not None

class Test_getScore:
    def test_getscore_result(self,setup_database):
        global recordId
        obj=setup_database[0]
        file_id = setup_database[1]
        fairnessUiService=FairnessUIservice(obj)
        BatchId_=setup_database[2]
        individual_fr =IndividualFairnessRequest(labels=["income-per-year"],recordId=recordId)    
        getLabel_result = fairnessUiService.getScore(individual_fr)
        assert getLabel_result is not None

class Test_upload_file_pretrainMitigation:
    def test_assert_pretrain_results(self,setup_database):
        global global_recordId_Pretrain
        obj=setup_database[0]
        file_id = setup_database[1]
        fairnessUiService=FairnessUIservice(obj)
        params = {
            'mitigationType': 'PREPROCESSING',
            'mitigationTechnique': 'REWEIGHING',
            'taskType': 'CLASSIFICATION',
            'fileId': file_id
        }
        
        getLabel_result = fairnessUiService.upload_file_pretrainMitigation(params)
        assert all(getLabel_result.get(key) is not None for key in ['mitigationType','mitigationTechnique','trainFileName','UploadedFileType','AttributesInTheDataset'])
        global_recordId_Pretrain = getLabel_result.get('recordId')

class Test_return_pretrainMitigation_protected_attrib:
    def test_assert_pretrain_attr(self,setup_database):
        global global_recordId_Pretrain
        obj=setup_database[0]
        file_id = setup_database[1]
        fairnessUiService=FairnessUIservice(obj)
        params = {
            'label': 'income-per-year',
            'FavourableOutcome':'>50K',
            'ProtectedAttribute':'race',
            'priviledged':'White',
            'recordId': global_recordId_Pretrain 
        }
        
        getLabel_result = fairnessUiService.return_pretrainMitigation_protected_attrib(params)
        assert getLabel_result is not None

class Test_return_pretrainMitigation_protected_attrib_DB:
    def create_upload_file():

        # File path
        file_path = "test/test_files/df_train"

        # Open the file in binary mode
        with open(file_path, 'rb') as f:
            contents = f.read()

        # Create an UploadFile instance
        upload_file = UploadFile(
            filename=os.path.basename(file_path),
            file=BytesIO(contents),
            headers=Headers({
                'content-disposition': f'form-data; name="file"; filename="{os.path.basename(file_path)}"',
                'content-type': 'text/csv'
            })
        )

        # Set the size attribute
        upload_file.size = os.path.getsize(file_path)
        return upload_file

    def create_second_file():
        # File path
        file_path = "test/test_files/df_test"

        # Open the file in binary mode
        with open(file_path, 'rb') as f:
            contents = f.read()

        # Create an UploadFile instance
        upload_file = UploadFile(
            filename=os.path.basename(file_path),
            file=BytesIO(contents),
            headers=Headers({
                'content-disposition': f'form-data; name="file"; filename="{os.path.basename(file_path)}"',
                'content-type': 'text/csv'
            })
        )

        # Set the size attribute
        upload_file.size = os.path.getsize(file_path)
        return upload_file

    def create_upload_model():
        # File path
        file_path = "test/test_files/model.joblib"

        # Open the file in binary mode
        with open(file_path, 'rb') as f:
            contents = f.read()

        # Create an UploadFile instance
        upload_file = UploadFile(
            filename=os.path.basename(file_path),
            file=BytesIO(contents),
            headers=Headers({
                'content-disposition': f'form-data; name="file"; filename="{os.path.basename(file_path)}"',
                'content-type': 'text/csv'
            })
        )

        # Set the size attribute
        upload_file.size = os.path.getsize(file_path)
        return upload_file

    def test_uploadfile_model(self):
        global global_recordId_model
        UIservice = FairnessUIservice()
        create_upload_file_ = Test_return_pretrainMitigation_protected_attrib_DB.create_upload_file()
        create_second_file_ = Test_return_pretrainMitigation_protected_attrib_DB.create_second_file()
        create_upload_model_ = Test_return_pretrainMitigation_protected_attrib_DB.create_upload_model()
        payload = {
            'model': create_upload_model_,
            'trainingDataset': create_upload_file_,
            'testingDataset': create_second_file_
        }
        result = UIservice.mitigation_model_upload_files(payload)
        assert result is not None
        global_recordId_model = result.get('record_id')

    def test_model_result(self):
        global global_recordId_model
        UIservice = FairnessUIservice()
        payload = {
            'recordId': global_recordId_model,
            'label': 'income-per-year',
            'sensitiveFeatures': 'race'
        }
        result = UIservice.mitigation_model_get_mitigated_model_name_analyze(payload)
        
    