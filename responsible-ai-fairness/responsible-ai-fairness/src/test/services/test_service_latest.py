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
# from fastapi import UploadFile, Headers
# from starlette.datastructures import Headers
import os
from io import BytesIO
# from ..conftest import DummyCollection
# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fairness.service.service_latest import FairnessServiceUpload
from fairness.service.service_latest import FairnessUIserviceUpload
from test.conftest import *
ServiceUpload =  FairnessServiceUpload()
UIserviceUpload = FairnessUIserviceUpload()
load_dotenv()
from fastapi import UploadFile
from starlette.datastructures import Headers
import os
from io import BytesIO


def create_upload_file():
    # File path
    file_path = "test/test_files/adult.csv"

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

def test_uploadfile_analyse():
    create_upload_file_=create_upload_file()
    payload = {
        'methodType': 'ALL',
        'biasType': 'PRETRAIN',
        'taskType': 'CLASSIFICATION',
        'file': create_upload_file_,
        'label': 'income-per-year',
        'FavourableOutcome': '>50K',
        'ProtectedAttribute': 'race',
        'priviledged': 'White'
    }
    
    result = UIserviceUpload.upload_file(payload)
    assert result.biasResults is not None

def test_uploadfile_methodNone():
    create_upload_file_=create_upload_file()
    payload = {
        'methodType': None,
        'biasType': 'PRETRAIN',
        'taskType': 'CLASSIFICATION',
        'file': create_upload_file_,
        'label': 'income-per-year',
        'FavourableOutcome': '>50K',
        'ProtectedAttribute': 'race',
        'priviledged': 'White'
    }
    with pytest.raises(TypeError):
    
        result = UIserviceUpload.upload_file(payload)

def test_uploadfile_biasTypeNone():
    create_upload_file_=create_upload_file()
    payload = {
        'methodType': 'ALL',
        'biasType': None,
        'taskType': 'CLASSIFICATION',
        'file': create_upload_file_,
        'label': 'income-per-year',
        'FavourableOutcome': '>50K',
        'ProtectedAttribute': 'race',
        'priviledged': 'White'
    }
    with pytest.raises(TypeError):
    
        result = UIserviceUpload.upload_file(payload)

def test_uploadfile_taskTypeNone():
    create_upload_file_=create_upload_file()
    payload = {
        'methodType': 'ALL',
        'biasType': 'PRETRAIN',
        'taskType': None,
        'file': create_upload_file_,
        'label': 'income-per-year',
        'FavourableOutcome': '>50K',
        'ProtectedAttribute': 'race',
        'priviledged': 'White'
    }
    with pytest.raises(TypeError):
    
        result = UIserviceUpload.upload_file(payload)

def test_uploadfile_LabelNone():
    create_upload_file_=create_upload_file()
    payload = {
        'methodType': 'ALL',
        'biasType': 'PRETRAIN',
        'taskType': 'CLASSIFICATION',
        'file': create_upload_file_,
        'label': None,
        'FavourableOutcome': '>50K',
        'ProtectedAttribute': 'race',
        'priviledged': 'White'
    }
    with pytest.raises(TypeError):
    
        result = UIserviceUpload.upload_file(payload)

def test_uploadfile_favourNone():
    create_upload_file_=create_upload_file()
    payload = {
        'methodType': 'ALL',
        'biasType': 'PRETRAIN',
        'taskType': 'CLASSIFICATION',
        'file': create_upload_file_,
        'label': 'income-per-year',
        'FavourableOutcome': None,
        'ProtectedAttribute': 'race',
        'priviledged': 'White'
    }
    with pytest.raises(TypeError):
    
        result = UIserviceUpload.upload_file(payload)

def test_uploadfile_protectedNone():
    create_upload_file_=create_upload_file()
    payload = {
        'methodType': 'ALL',
        'biasType': 'PRETRAIN',
        'taskType': 'CLASSIFICATION',
        'file': create_upload_file_,
        'label': 'income-per-year',
        'FavourableOutcome': '>50K',
        'ProtectedAttribute': None,
        'priviledged': 'White'
    }
    with pytest.raises(AttributeError):
    
        result = UIserviceUpload.upload_file(payload)

def test_uploadfile_privlNone():
    create_upload_file_=create_upload_file()
    payload = {
        'methodType': 'ALL',
        'biasType': 'PRETRAIN',
        'taskType': 'CLASSIFICATION',
        'file': create_upload_file_,
        'label': 'income-per-year',
        'FavourableOutcome': '>50K',
        'ProtectedAttribute': 'race',
        'priviledged': None
    }
    with pytest.raises(AttributeError):
    
        result = UIserviceUpload.upload_file(payload)


def test_uploadfile_pretrain():
    create_upload_file_=create_upload_file()
    payload = {
        'MitigationType': 'PREPROCESSING',
        'MitigationTechnique': 'REWEIGHING',
        'taskType': 'CLASSIFICATION',
        'file': create_upload_file_,
        'label': 'income-per-year',
        'FavourableOutcome': '>50K',
        'ProtectedAttribute': 'race',
        'priviledged': 'White'
    }
    result = UIserviceUpload.upload_file_Premitigation(payload)
    assert result.biasResults is not None



def test_pretrainuploadfile_mitigateTypeNone():
    create_upload_file_=create_upload_file()
    payload = {
        'MitigationType': None,
        'MitigationTechnique': 'REWEIGHING',
        'taskType': 'CLASSIFICATION',
        'file': create_upload_file_,
        'label': 'income-per-year',
        'FavourableOutcome': '>50K',
        'ProtectedAttribute': 'race',
        'priviledged': 'White'
    }
    with pytest.raises(TypeError):
        UIserviceUpload.upload_file_Premitigation(payload)

def test_pretrainuploadfile_mitigateTechNone():
    create_upload_file_=create_upload_file()
    payload = {
        'MitigationType': 'PREPROCESSING',
        'MitigationTechnique': None,
        'taskType': 'CLASSIFICATION',
        'file': create_upload_file_,
        'label': 'income-per-year',
        'FavourableOutcome': '>50K',
        'ProtectedAttribute': 'race',
        'priviledged': 'White'
    }
    with pytest.raises(TypeError):
        UIserviceUpload.upload_file_Premitigation(payload)

def test_pretrainuploadfile_taskType_None():
    create_upload_file_=create_upload_file()
    payload = {
        'MitigationType': 'PREPROCESSING',
        'MitigationTechnique': 'REWEIGHING',
        'taskType': None,
        'file': create_upload_file_,
        'label': 'income-per-year',
        'FavourableOutcome': '>50K',
        'ProtectedAttribute': 'race',
        'priviledged': 'White'
    }
    with pytest.raises(TypeError):
        UIserviceUpload.upload_file_Premitigation(payload)

def test_pretrainuploadfile_label_None():
    create_upload_file_=create_upload_file()
    payload = {
        'MitigationType': 'PREPROCESSING',
        'MitigationTechnique': 'REWEIGHING',
        'taskType': 'CLASSIFICATION',
        'file': create_upload_file_,
        'label': None,
        'FavourableOutcome': '>50K',
        'ProtectedAttribute': 'race',
        'priviledged': 'White'
    }
    with pytest.raises(TypeError):
        UIserviceUpload.upload_file_Premitigation(payload)

def test_pretrainuploadfile_favour_None():
    create_upload_file_=create_upload_file()
    payload = {
        'MitigationType': 'PREPROCESSING',
        'MitigationTechnique': 'REWEIGHING',
        'taskType': 'CLASSIFICATION',
        'file': create_upload_file_,
        'label': 'income-per-year',
        'FavourableOutcome': None,
        'ProtectedAttribute': 'race',
        'priviledged': 'White'
    }
    with pytest.raises(TypeError):
        UIserviceUpload.upload_file_Premitigation(payload)

def test_pretrainuploadfile_protected_None():
    create_upload_file_=create_upload_file()
    payload = {
        'MitigationType': 'PREPROCESSING',
        'MitigationTechnique': 'REWEIGHING',
        'taskType': 'CLASSIFICATION',
        'file': create_upload_file_,
        'label': 'income-per-year',
        'FavourableOutcome': '>50K',
        'ProtectedAttribute': None,
        'priviledged': 'White'
    }
    with pytest.raises(AttributeError):
        UIserviceUpload.upload_file_Premitigation(payload)

def test_pretrainuploadfile_Priv_None():
    create_upload_file_=create_upload_file()
    payload = {
        'MitigationType': 'PREPROCESSING',
        'MitigationTechnique': 'REWEIGHING',
        'taskType': 'CLASSIFICATION',
        'file': create_upload_file_,
        'label': 'income-per-year',
        'FavourableOutcome': '>50K',
        'ProtectedAttribute': 'race',
        'priviledged': None
    }
    with pytest.raises(AttributeError):
        UIserviceUpload.upload_file_Premitigation(payload)

def test_individual_uploadfile():
    create_upload_file_=create_upload_file()
    payload = {
        'file': create_upload_file_,
        'label': 'income-per-year'
    }
    payload['label'] = [payload['label']]
    
    result = UIserviceUpload.getLabels_Individual(payload)
    assert result is not None

