"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
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
from .MockDB import Database_MockDB
import pytest
from pytest_mock import mocker
from mongomock import MongoClient
from dotenv import load_dotenv
import requests
from unittest.mock import Mock, patch, MagicMock
import pandas
# from fastapi import UploadFile, Headers
# from starlette.datastructures import Headers
import os
from io import BytesIO
# from ..conftest import DummyCollection
# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fairness.service.service_latest import FairnessServiceUpload
from fairness.service.service_latest import FairnessUIserviceUpload
from fairness.service.service_latest import AttributeDict
from tests.conftest import *
ServiceUpload =  FairnessServiceUpload()
UIserviceUpload = FairnessUIserviceUpload()
load_dotenv()
from fastapi import UploadFile
from starlette.datastructures import Headers
import os
from io import BytesIO
from pathlib import Path

def create_upload_file():
    # File path
    file_path = "tests/test_files/adult.csv"

    # Open the file in binary mode
    with open(Path(file_path), 'rb') as f:
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
        'predLabel': 'predicted',
        'FavourableOutcome': '>50K',
        'ProtectedAttribute': ['race'],
        'priviledged': [['White']]
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
        'predLabel': 'predicted',
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
        'predLabel': 'predicted',
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
        'predLabel': 'predicted',
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
        'predLabel': 'predicted',
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
        'predLabel': 'predicted',
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
        'predLabel': 'predicted',
        'FavourableOutcome': '>50K',
        'ProtectedAttribute': None,
        'priviledged': [['White']]
    }
    with pytest.raises(TypeError):
    
        result = UIserviceUpload.upload_file(payload)

def test_uploadfile_privlNone():
    create_upload_file_=create_upload_file()
    payload = {
        'methodType': 'ALL',
        'biasType': 'PRETRAIN',
        'taskType': 'CLASSIFICATION',
        'file': create_upload_file_,
        'label': 'income-per-year',
        'predLabel': 'predicted',
        'FavourableOutcome': '>50K',
        'ProtectedAttribute': ['race'],
        'priviledged': None
    }
    with pytest.raises(TypeError):
    
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
        'ProtectedAttribute': ['race'],
        'priviledged': [['White']]
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
        'priviledged': [['White']]
    }
    with pytest.raises(TypeError):
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
        'ProtectedAttribute': ['race'],
        'priviledged': None
    }
    with pytest.raises(TypeError):
        UIserviceUpload.upload_file_Premitigation(payload)

def test_individual_uploadfile():
    create_upload_file_=create_upload_file()
    payload = {
        'file': create_upload_file_,
        'label': 'income-per-year',
        'k': 5
    }
    payload['label'] = [payload['label']]
    
    result = UIserviceUpload.getLabels_Individual(payload)
    assert result is not None


# ==================== COMPREHENSIVE TEST CASES FOR FULL COVERAGE ====================

class TestAttributeDict:
    """Test AttributeDict utility class"""
    
    def test_attribute_dict_getattr(self):
        """Test __getattr__ functionality"""
        attr_dict = AttributeDict({'key1': 'value1', 'key2': 'value2'})
        assert attr_dict.key1 == 'value1'
        assert attr_dict.key2 == 'value2'
    
    def test_attribute_dict_setattr(self):
        """Test __setattr__ functionality"""
        attr_dict = AttributeDict()
        attr_dict.new_key = 'new_value'
        assert attr_dict['new_key'] == 'new_value'
    
    def test_attribute_dict_delattr(self):
        """Test __delattr__ functionality"""
        attr_dict = AttributeDict({'key1': 'value1'})
        del attr_dict.key1
        assert 'key1' not in attr_dict
    
    def test_attribute_dict_inheritance(self):
        """Test that AttributeDict inherits from dict"""
        attr_dict = AttributeDict({'key': 'value'})
        assert isinstance(attr_dict, dict)
        assert attr_dict['key'] == 'value'


class TestFairnessServiceUploadInit:
    """Test FairnessServiceUpload initialization"""
    
    def test_init_creates_utils(self):
        """Test that __init__ creates Utils instance"""
        service = FairnessServiceUpload()
        assert hasattr(service, 'utils')
        assert isinstance(service.utils, Utils)
    
    def test_class_constants(self):
        """Test class constants are defined"""
        assert FairnessServiceUpload.MITIGATED_LOCAL_FILE_PATH.endswith(os.path.join('MitigatedData', ''))
        assert FairnessServiceUpload.LOCAL_FILE_PATH.endswith(os.path.join('datasets', ''))
        assert FairnessServiceUpload.MODEL_LOCAL_PATH.endswith(os.path.join('model', ''))


class TestFairnessUIserviceUploadInit:
    """Test FairnessUIserviceUpload initialization"""
    
    def test_init_with_mockdb(self):
        """Test initialization with MockDB"""
        service = FairnessUIserviceUpload(MockDB=None)
        assert hasattr(service, 'utils')
        assert isinstance(service.utils, Utils)
    
    def test_init_without_mockdb(self):
        """Test initialization without MockDB"""
        service = FairnessUIserviceUpload()
        assert hasattr(service, 'utils')


class TestPretrainedAnalyseStatic:
    """Test the pretrainedAnalyse static method"""
    
    def test_pretrained_analyse_with_mock(self):
        """Test pretrainedAnalyse with mocked dependencies"""
        from unittest.mock import Mock, patch
        import pandas as pd
        
        sample_data = {
            'age': [25, 35, 45],
            'race': [0, 1, 0],
            'income-per-year': [0, 1, 0]
        }
        df = pd.DataFrame(sample_data)
        
        with patch('fairness.service.service_latest.DataList') as mock_datalist, \
             patch('fairness.service.service_latest.BiasResult') as mock_bias_result:
            
            mock_ds = Mock()
            mock_ds.getDataList.return_value = Mock()
            mock_datalist.return_value = mock_ds
            
            mock_br = Mock()
            mock_br.analyzeResult.return_value = [{'metric': 'value'}]
            mock_bias_result.return_value = mock_br
            
            result = FairnessServiceUpload.pretrainedAnalyse(
                traindata=df,
                labelmap={'1': 1, '0': 0},
                label='income-per-year',
                protectedAttributes=['race'],
                favourableOutcome=['1'],
                CategoricalAttributes=['race'],
                features=['age', 'race', 'income-per-year'],
                biastype='PRETRAIN',
                methods='ALL',
                flag=True
            )
            
            assert result is not None
            assert isinstance(result, list)
            mock_ds.getDataList.assert_called_once()
            mock_br.analyzeResult.assert_called_once()


class TestPosttrainedAnalyseStatic:
    """Test the posttrainedAnalyse static method"""
    
    def test_posttrained_analyse_with_mock(self):
        """Test posttrainedAnalyse with mocked dependencies"""
        from unittest.mock import Mock, patch
        import pandas as pd
        
        sample_data = {
            'age': [25, 35, 45],
            'race': [0, 1, 0],
            'income-per-year': [0, 1, 0],
            'pred_income': [0, 1, 1]
        }
        df = pd.DataFrame(sample_data)
        
        # Create preprocessed dataframe
        preprocessed_df = df.copy()
        preprocessed_df['label'] = preprocessed_df['income-per-year']
        
        with patch('fairness.service.service_latest.DataList') as mock_datalist, \
             patch('fairness.service.service_latest.BiasResult') as mock_bias_result:
            
            mock_ds = Mock()
            mock_ds.preprocessDataset.return_value = (Mock(), Mock(), preprocessed_df, df)
            mock_datalist.return_value = mock_ds
            
            mock_br = Mock()
            mock_br.analyseHoilisticAIBiasResult.return_value = [{'metric': 'value'}]
            mock_bias_result.return_value = mock_br
            
            result = FairnessServiceUpload.posttrainedAnalyse(
                testdata=df,
                label='income-per-year',
                predLabel='pred_income',
                labelmap={'1': 1, '0': 0},
                protectedAttributes=['race'],
                taskType='CLASSIFICATION',
                methods='ALL',
                flag=True
            )
            
            assert result is not None
            assert isinstance(result, list)
            mock_ds.preprocessDataset.assert_called_once()
            mock_br.analyseHoilisticAIBiasResult.assert_called_once()


class TestPreprocessingMitigateAndTransform:
    """Test preprocessingmitigateandtransform static method"""
    
    def test_preprocessing_mitigate_transform_with_mock(self):
        """Test preprocessingmitigateandtransform with mocked dependencies"""
        from unittest.mock import Mock, patch
        import pandas as pd
        
        sample_data = {
            'age': [25, 35, 45],
            'race': [0, 1, 0],
            'income-per-year': [0, 1, 0]
        }
        df = pd.DataFrame(sample_data)
        
        with patch('fairness.service.service_latest.DataList') as mock_datalist, \
             patch('fairness.service.service_latest.BiasResult') as mock_bias_result:
            
            mock_ds = Mock()
            mock_ds.getDataList.return_value = Mock()
            mock_datalist.return_value = mock_ds
            
            mock_br = Mock()
            mock_br.analyzeResult.return_value = [{'metric': 'value'}]
            mock_br.mitigateAndTransform.return_value = df
            mock_bias_result.return_value = mock_br
            
            result = FairnessServiceUpload.preprocessingmitigateandtransform(
                traindata=df,
                labelmap={'1': 1, '0': 0},
                label='income-per-year',
                protectedAttributes=['race'],
                favourableOutcome=['1'],
                CategoricalAttributes=['race'],
                features=['age', 'race', 'income-per-year'],
                biastype='PRETRAIN',
                methods='ALL',
                mitigationTechnique='REWEIGHING',
                flag=True
            )
            
            assert result is not None
            assert len(result) == 2  # Returns tuple of (list_bias_results, mitigated_df)
            mock_ds.getDataList.assert_called_once()
            mock_br.analyzeResult.assert_called_once()
            mock_br.mitigateAndTransform.assert_called_once()


class TestGetDataFrame:
    """Test get_data_frame static method"""
    
    def test_get_data_frame_csv(self, tmp_path):
        """Test get_data_frame with CSV file"""
        from unittest.mock import patch
        import pandas as pd
        
        mock_df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        
        with patch('pandas.read_csv', return_value=mock_df):
            result = FairnessUIserviceUpload.get_data_frame('csv', 'test.csv')
            assert result is not None
            assert isinstance(result, pd.DataFrame)


class TestPretrainSaveFile:
    """Test pretrain_save_file static method"""
    
    def test_pretrain_save_file_csv(self, tmp_path):
        """Test saving DataFrame as CSV"""
        import pandas as pd
        
        df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        file_path = tmp_path / "test.csv"
        
        FairnessUIserviceUpload.pretrain_save_file(df, 'csv', str(file_path))
        
        assert file_path.exists()
        loaded_df = pd.read_csv(file_path)
        assert len(loaded_df) == 2
    
    def test_pretrain_save_file_json(self, tmp_path):
        """Test saving DataFrame as JSON"""
        import pandas as pd
        
        df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        file_path = tmp_path / "test.json"
        
        FairnessUIserviceUpload.pretrain_save_file(df, 'json', str(file_path))
        
        assert file_path.exists()
    
    def test_pretrain_save_file_parquet(self, tmp_path):
        """Test saving DataFrame as Parquet"""
        import pandas as pd
        
        df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        file_path = tmp_path / "test.parquet"
        
        FairnessUIserviceUpload.pretrain_save_file(df, 'parquet', str(file_path))
        
        assert file_path.exists()


class TestGetMitigatedData:
    """Test get_mitigated_data method"""
    
    def test_get_mitigated_data_success(self):
        """Test get_mitigated_data raises HTTPException when file not found"""
        from fastapi import HTTPException
        
        service = FairnessUIserviceUpload()
        
        with pytest.raises(HTTPException) as exc_info:
            result = service.get_mitigated_data('test.csv')
        
        assert exc_info.value.status_code == 404


class TestValidateJsonRequest:
    """Test validate_json_request static method"""
    
    def test_validate_json_request_valid(self):
        """Test validate_json_request with valid payload"""
        payload = AttributeDict({
            'method': 'ALL',
            'biasType': 'PRETRAIN',
            'taskType': 'CLASSIFICATION',
            'trainingDataset': {'path': {'uri': '/path/to/train.csv'}, 'label': 'income'},
            'predictionDataset': {'path': {'uri': '/path/to/pred.csv'}, 'predlabel': 'pred_income'},
            'features': 'age,race,income',
            'facet': [{'name': 'race'}],
            'categoricalAttributes': 'race',
            'favourableOutcome': ['>50K'],
            'outputPath': {'uri': '/output'},
            'labelmaps': {'>50K': '1'}
        })
        
        result = FairnessUIserviceUpload.validate_json_request(payload)
        assert result is True


class TestValidatePretrainJsonRequest:
    """Test validate_pretrain_json_request static method"""
    
    def test_validate_pretrain_json_request_valid(self):
        """Test validate_pretrain_json_request with valid payload"""
        payload = AttributeDict({
            'method': 'ALL',
            'biasType': 'PRETRAIN',
            'taskType': 'CLASSIFICATION',
            'trainingDataset': {'path': {'uri': '/path/to/train.csv'}, 'label': 'income'},
            'features': 'age,race,income',
            'facet': [{'name': 'race'}],
            'categoricalAttributes': 'race',
            'favourableOutcome': ['>50K'],
            'outputPath': {'uri': '/output'},
            'labelmaps': {'>50K': '1'}
        })
        
        result = FairnessUIserviceUpload.validate_pretrain_json_request(payload)
        assert result is True


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_attribute_dict_with_empty_dict(self):
        """Test AttributeDict with empty dictionary"""
        attr_dict = AttributeDict({})
        assert len(attr_dict) == 0
    
    def test_pretrain_save_file_with_empty_df(self, tmp_path):
        """Test pretrain_save_file with empty DataFrame"""
        import pandas as pd
        
        df = pd.DataFrame()
        file_path = tmp_path / "empty.csv"
        
        FairnessUIserviceUpload.pretrain_save_file(df, 'csv', str(file_path))
        assert file_path.exists()


class TestResourceManagement:
    """Test resource management and cleanup"""
    
    def test_service_initialization_multiple_times(self):
        """Test that service can be initialized multiple times"""
        service1 = FairnessServiceUpload()
        service2 = FairnessServiceUpload()
        
        assert service1.utils is not None
        assert service2.utils is not None
        assert service1.utils is not service2.utils


# Run with: pytest test_service_latest.py -v --cov=fairness.service.service_latest --cov-report=term-missing

