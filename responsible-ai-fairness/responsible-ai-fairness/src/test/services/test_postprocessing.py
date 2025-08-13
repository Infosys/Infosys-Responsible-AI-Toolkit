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
from fairness.service.postprocessing import ModelMitigation
modelmitigate = ModelMitigation()

load_dotenv()


class Test_model:

    def test_model_uploadfiles(self,setup_database):
        expect_output = {'feature_list': ['age', 'fnlwgt', 'education-num', 'capital-gain', 'capital-loss', 'hours-per-week', 'workclass', 'education', 'marital-status', 'occupation', 'relationship', 'native-country', 'income-per-year', 'race', 'sex']} 
        modelmitigate = ModelMitigation(setup_database[0])
        dataset = setup_database[3]
        model = setup_database[4]
        # Prepare the parameters
        payload = {
            'trainingDatasetID': dataset,
            'modelID': model

        }
        
            
        result = modelmitigate.mitigation_modelUpload_Fs(payload)
        assert expect_output == result

    def test_assert_batchid_return(self,setup_database):
        modelmitigate=ModelMitigation(setup_database[0])
        BatchId_=setup_database[5]
        batchId=BatchId(Batch_id=BatchId_)
        result = modelmitigate.mitigation_getmitigated_modelname_analyze(batchId)

    def test_assert_batchid_returnNone(self,setup_database):
        modelmitigate=ModelMitigation(setup_database[0])
        BatchId_=setup_database[5]
        batchId=None
        with pytest.raises(AttributeError):
            result = modelmitigate.mitigation_getmitigated_modelname_analyze(batchId)