"""
Unit tests for InfosysRAI service layer.
"""

import pytest
import os
import sys
from unittest.mock import Mock, MagicMock, patch, mock_open
from io import BytesIO

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app.service.service import InfosysRAI, AttributeDict


class TestAttributeDict:
    """Tests for AttributeDict class."""
    def test_attribute_dict_getattr(self):
        ad = AttributeDict({'test_attr': 'value'})
        assert ad.test_attr == 'value'
    
    def test_attribute_dict_setitem(self):
        ad = AttributeDict()
        ad['test_attr'] = 'value'
        assert ad['test_attr'] == 'value'
    
    def test_attribute_dict_setattr(self):
        ad = AttributeDict()
        ad.test_attr = 'value'
        assert ad.test_attr == 'value'


class TestGetTenetsList:
    """Tests for getTenetsList method."""
    
    @patch('app.service.service.Tenet')
    def test_get_tenets_list_success(self, mock_tenet):
        mock_tenet.findall.return_value = [
            {
                'Id': 1,
                'TenetName': 'Fairness',
                'ProjectName': 'RAI',
                'CreatedDateTime': '2025-01-01',
                'LastUpdatedDateTime': '2025-01-02'
            }
        ]
        
        result = InfosysRAI.getTenetsList()
        
        assert len(result) == 1
        assert result[0]['TenetName'] == 'Fairness'
        mock_tenet.findall.assert_called_once_with({"ProjectName": "RAI"})
    
    @patch('app.service.service.Tenet')
    def test_get_tenets_list_empty(self, mock_tenet):
        mock_tenet.findall.return_value = []
        
        result = InfosysRAI.getTenetsList()
        
        assert result == []
    
    @patch('app.service.service.Tenet')
    def test_get_tenets_list_exception(self, mock_tenet):
        mock_tenet.findall.side_effect = Exception("Database error")
        
        result = InfosysRAI.getTenetsList()
        
        assert result == "Something Went Wrong"


class TestAddTenet:
    """Tests for addTenet method."""
    
    @patch('app.service.service.Tenet')
    def test_add_tenet_success(self, mock_tenet):
        mock_tenet.findall.return_value = []
        mock_tenet.create.return_value = True
        
        payload = {'TenetName': 'NewTenet'}
        result = InfosysRAI.addTenet(payload)
        
        assert "Successfully added" in result
        mock_tenet.create.assert_called_once()
    
    @patch('app.service.service.Tenet')
    def test_add_tenet_already_exists(self, mock_tenet):
        mock_tenet.findall.return_value = [{'TenetName': 'ExistingTenet'}]
        
        payload = {'TenetName': 'ExistingTenet'}
        result = InfosysRAI.addTenet(payload)
        
        assert "Already Exists" in result
    
    @patch('app.service.service.Tenet')
    def test_add_tenet_exception(self, mock_tenet):
        mock_tenet.findall.side_effect = Exception("Database error")
        
        payload = {'TenetName': 'NewTenet'}
        result = InfosysRAI.addTenet(payload)
        
        assert "Failed Due To" in result


class TestDeleteTenet:
    """Tests for deletetenet method."""
    
    @patch('app.service.service.Tenet')
    def test_delete_tenet_success(self, mock_tenet):
        mock_tenet.delete.return_value = True
        
        payload = {'TenetName': 'TestTenet'}
        result = InfosysRAI.deletetenet(payload)
        
        assert "Successfully Deleted" in result
        mock_tenet.delete.assert_called_once_with(payload)
    
    @patch('app.service.service.Tenet')
    def test_delete_tenet_exception(self, mock_tenet):
        mock_tenet.delete.side_effect = Exception("Delete error")
        
        payload = {'TenetName': 'TestTenet'}
        result = InfosysRAI.deletetenet(payload)
        
        assert "deletion failed" in result


class TestGetData:
    """Tests for getData method."""
    
    @patch('app.service.service.DataAttributesValues')
    @patch('app.service.service.DataAttributes')
    @patch('app.service.service.Data')
    def test_get_data_success(self, mock_data, mock_data_attrs, mock_data_attr_vals):
        mock_data.findall.return_value = [
            {'DataId': 1, 'DataSetName': 'TestData', 'SampleData': 'sample.csv'}
        ]
        mock_data_attrs.findall.return_value = [
            {'DataAttributeId': 101, 'DataAttributeName': 'testAttr'}
        ]
        mock_data_attr_vals.findall.return_value = [
            {'DataAttributeId': 101, 'DataAttributeValues': 'testValue'}
        ]
        
        payload = {'userid': 'user123'}
        result = InfosysRAI.getData(payload)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['dataSetName'] == 'TestData'


class TestAddData:
    """Tests for addData method."""
    
    @patch.dict(os.environ, {'DB_TYPE': 'mongo'})
    @patch('app.service.service.DataAttributesValues')
    @patch('app.service.service.DataAttributes')
    @patch('app.service.service.Data')
    @patch('app.service.service.FileStoreDb')
    @patch('app.service.service.Tenet')
    def test_add_data_mongo_success(self, mock_tenet, mock_filestore, mock_data, 
                                     mock_data_attrs, mock_data_attr_vals):
        mock_filestore.fs.find_one.return_value = None
        mock_tenet.findOne.return_value = 'common_id'
        mock_filestore.create.return_value = 'file_id'
        mock_data.create.return_value = 'data_id'
        mock_data_attrs.findall.return_value = [{'DataAttributeId': 101}]
        mock_data_attr_vals.create.return_value = 'attr_val_id'
        
        payload1 = {'dataFileName': 'test_data', 'attr1': 'value1'}
        payload2 = Mock()
        payload2.DataFile.filename = 'test.csv'
        
        result = InfosysRAI.addData('user123', payload1, payload2)
        
        assert result == "Data Added Sucessfully"
    
    @patch.dict(os.environ, {'DB_TYPE': 'mongo'})
    @patch('app.service.service.FileStoreDb')
    def test_add_data_already_exists(self, mock_filestore):
        mock_filestore.fs.find_one.return_value = {'filename': 'test.csv'}
        
        payload1 = {'dataFileName': 'test_data'}
        payload2 = Mock()
        payload2.DataFile.filename = 'test.csv'
        
        result = InfosysRAI.addData('user123', payload1, payload2)
        
        assert result == "DataFile Already Added"


class TestUpdateData:
    """Tests for updateData method."""
    
    @patch('app.service.service.Data')
    def test_update_data_not_exists(self, mock_data):
        mock_data.findall.return_value = []
        
        payload = {'userid': 'user123', 'dataid': '123'}
        payload1 = {}
        payload2 = Mock()
        
        result = InfosysRAI.updateData(payload, payload1, payload2)
        
        assert result == "No Data Exists With This Id."


class TestDeleteData:
    """Tests for deleteData method."""
    
    @patch('app.service.service.DataAttributes')
    @patch('app.service.service.DataAttributesValues')
    @patch('app.service.service.Data')
    def test_delete_data_success(self, mock_data, mock_data_attr_vals, mock_data_attrs):
        mock_data.findall.return_value = [{'_id': '1', 'DataId': '123'}]
        mock_data_attr_vals.findall.return_value = [
            {'_id': 'val1', 'DataAttributeId': 'attr1'}
        ]
        mock_data_attrs.findall.return_value = [{'_id': 'attr1'}]
        
        payload = {'userid': 'user123', 'dataid': '123'}
        result = InfosysRAI.deleteData(payload)
        
        assert result == "Data Deleted Sucessfully"
    
    @patch('app.service.service.Data')
    def test_delete_data_no_data(self, mock_data):
        mock_data.findall.return_value = []
        
        payload = {'userid': 'user123', 'dataid': '123'}
        result = InfosysRAI.deleteData(payload)
        
        assert result == 'No Data Available to Delete'


class TestGetModel:
    """Tests for getModel method."""
    
    @patch('app.service.service.ModelAttributesValues')
    @patch('app.service.service.ModelAttributes')
    @patch('app.service.service.Model')
    def test_get_model_success(self, mock_model, mock_model_attrs, mock_model_attr_vals):
        mock_model.findall.return_value = [
            {'ModelId': 1, 'ModelName': 'TestModel', 'ModelEndPoint': 'NA', 'ModelData': 'file_id'}
        ]
        mock_model_attrs.findall.return_value = [
            {'ModelAttributeId': 201, 'ModelAttributeName': 'framework'}
        ]
        mock_model_attr_vals.findall.return_value = [
            {'ModelAttributeId': 201, 'ModelAttributeValues': 'TensorFlow'}
        ]
        
        payload = {'userid': 'user123'}
        result = InfosysRAI.getModel(payload)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['modelName'] == 'TestModel'


class TestDeleteModel:
    """Tests for deleteModel method."""
    
    @patch('app.service.service.ModelAttributesValues')
    @patch('app.service.service.Model')
    def test_delete_model_success(self, mock_model, mock_model_attr_vals):
        mock_model.findall.return_value = [{'_id': '1', 'ModelId': '456'}]
        mock_model_attr_vals.findall.return_value = [{'_id': 'val1'}]
        
        payload = {'userid': 'user123', 'modelid': '456'}
        result = InfosysRAI.deleteModel(payload)
        
        assert result == "Model Deleted Sucessfully"


class TestGetPreprocessor:
    """Tests for getPreprocessor method."""
    
    @patch('app.service.service.Preprocessor')
    def test_get_preprocessor_success(self, mock_preprocessor):
        mock_preprocessor.findall.return_value = [
            {'PreprocessorId': 1, 'PreprocessorName': 'TestPreprocessor', 
             'PreprocessorFileId': 'file_id'}
        ]
        
        payload = {'userid': 'user123'}
        result = InfosysRAI.getPreprocessor(payload)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['preprocessorName'] == 'TestPreprocessor'
    
    @patch('app.service.service.Preprocessor')
    def test_get_preprocessor_no_data(self, mock_preprocessor):
        mock_preprocessor.findall.return_value = []
        
        payload = {'userid': 'user123'}
        result = InfosysRAI.getPreprocessor(payload)
        
        assert result == {"message": "This user doesn't have preprocessor values"}


class TestDeletePreprocessor:
    """Tests for deletePreprocessor method."""
    
    @patch('app.service.service.Preprocessor')
    def test_delete_preprocessor_success(self, mock_preprocessor):
        mock_preprocessor.findall.return_value = [{'_id': '1'}]
        
        payload = {'userid': 'user123', 'preprocessorid': '789'}
        result = InfosysRAI.deletePreprocessor(payload)
        
        assert result == "Preprocessor Deleted Sucessfully"
    
    @patch('app.service.service.Preprocessor')
    def test_delete_preprocessor_no_data(self, mock_preprocessor):
        mock_preprocessor.findall.return_value = []
        
        payload = {'userid': 'user123', 'preprocessorid': '789'}
        result = InfosysRAI.deletePreprocessor(payload)
        
        assert result == 'No Preprocessor Available to Delete'


class TestGetBatchStatusList:
    """Tests for getBatchStatusList method."""
    
    @patch('app.service.service.Batch')
    def test_get_batch_status_list(self, mock_batch):
        mock_batch.findStatus.return_value = {'status': 'completed'}
        
        payload = {'batchid': 'batch123'}
        result = InfosysRAI.getBatchStatusList(payload)
        
        assert result == {'status': 'completed'}
        mock_batch.findStatus.assert_called_once_with(payload)


class TestGetBatchTable:
    """Tests for getBatchTable method."""
    
    @patch('app.service.service.Data')
    @patch('app.service.service.Model')
    @patch('app.service.service.InfosysRAI.getTenetsList')
    @patch('app.service.service.Batch')
    def test_get_batch_table_success(self, mock_batch, mock_get_tenets, 
                                      mock_model, mock_data):
        mock_batch.findBatchTable.return_value = [
            {'TenetId': 1, 'ModelId': 2, 'DataId': 3}
        ]
        mock_get_tenets.return_value = [{'Id': 1, 'TenetName': 'Fairness'}]
        mock_model.findall.return_value = [{'ModelId': 2, 'ModelName': 'TestModel'}]
        mock_data.findall.return_value = [{'DataId': 3, 'DataSetName': 'TestData'}]
        
        payload = {'userid': 'user123'}
        result = InfosysRAI.getBatchTable(payload)
        
        assert isinstance(result, list)
        assert len(result) == 1


class TestDeleteBatch:
    """Tests for deleteBatch method."""
    
    @patch('app.service.service.Report')
    @patch('app.service.service.Html')
    @patch('app.service.service.Batch')
    @patch('app.service.service.FileStoreDb')
    def test_delete_batch_success(self, mock_filestore, mock_batch, 
                                   mock_html, mock_report):
        mock_batch.findall.return_value = [{'BatchId': 'batch123'}]
        mock_html.findall.return_value = [{'HtmlFileId': 'html_id'}]
        mock_report.findall.return_value = [{'ReportFileId': 'report_id'}]
        
        payload = {'userid': 'user123', 'batchid': 'batch123'}
        result = InfosysRAI.deleteBatch(payload)
        
        assert result == "Batch Deleted Sucessfully"
        mock_batch.delete.assert_called_once()
    
    @patch('app.service.service.Report')
    @patch('app.service.service.Html')
    @patch('app.service.service.Batch')
    @patch('app.service.service.FileStoreDb')
    def test_delete_batch_multiple_reports(self, mock_filestore, mock_batch, mock_html, mock_report):
        """Test deletion of batch with multiple HTML and report files."""
        mock_batch.findall.return_value = [{'BatchId': 'batch123'}]
        mock_html.findall.return_value = [
            {'HtmlFileId': 'html_id1'},
            {'HtmlFileId': 'html_id2'}
        ]
        mock_report.findall.return_value = [
            {'ReportFileId': 'report_id1'},
            {'ReportFileId': 'report_id2'}
        ]
        
        payload = {'userid': 'user123', 'batchid': 'batch123'}
        result = InfosysRAI.deleteBatch(payload)
        
        assert result == "Batch Deleted Sucessfully"


class TestGetDataMultipleRecords:
    """Tests for getData with multiple records."""
    
    @patch('app.service.service.DataAttributesValues')
    @patch('app.service.service.DataAttributes')
    @patch('app.service.service.Data')
    def test_get_data_multiple_records(self, mock_data, mock_data_attrs, mock_data_attr_vals):
        mock_data.findall.return_value = [
            {'DataId': 1, 'DataSetName': 'Data1', 'SampleData': 'sample1.csv'},
            {'DataId': 2, 'DataSetName': 'Data2', 'SampleData': 'sample2.csv'},
            {'DataId': 3, 'DataSetName': 'Data3', 'SampleData': 'sample3.csv'}
        ]
        mock_data_attrs.findall.return_value = [
            {'DataAttributeId': 101, 'DataAttributeName': 'testAttr'}
        ]
        mock_data_attr_vals.findall.return_value = [
            {'DataAttributeId': 101, 'DataAttributeValues': 'testValue'}
        ]
        
        payload = {'userid': 'user123'}
        result = InfosysRAI.getData(payload)
        
        assert isinstance(result, list)
        assert len(result) == 3


class TestGetModelMultipleRecords:
    """Tests for getModel with multiple records."""
    
    @patch('app.service.service.ModelAttributesValues')
    @patch('app.service.service.ModelAttributes')
    @patch('app.service.service.Model')
    def test_get_model_multiple_records(self, mock_model, mock_model_attrs, mock_model_attr_vals):
        mock_model.findall.return_value = [
            {'ModelId': 1, 'ModelName': 'Model1', 'ModelEndPoint': 'NA', 'ModelData': 'file_id1'},
            {'ModelId': 2, 'ModelName': 'Model2', 'ModelEndPoint': 'http://api.com', 'ModelData': 'file_id2'}
        ]
        mock_model_attrs.findall.return_value = [
            {'ModelAttributeId': 201, 'ModelAttributeName': 'framework'}
        ]
        mock_model_attr_vals.findall.return_value = [
            {'ModelAttributeId': 201, 'ModelAttributeValues': 'TensorFlow'}
        ]
        
        payload = {'userid': 'user123'}
        result = InfosysRAI.getModel(payload)
        
        assert isinstance(result, list)
        assert len(result) == 2


class TestGetPreprocessorMultipleRecords:
    """Tests for getPreprocessor with multiple records."""
    
    @patch('app.service.service.Preprocessor')
    def test_get_preprocessor_multiple_records(self, mock_preprocessor):
        mock_preprocessor.findall.return_value = [
            {'PreprocessorId': 1, 'PreprocessorName': 'Preprocessor1', 'PreprocessorFileId': 'file_id1'},
            {'PreprocessorId': 2, 'PreprocessorName': 'Preprocessor2', 'PreprocessorFileId': 'file_id2'}
        ]
        
        payload = {'userid': 'user123'}
        result = InfosysRAI.getPreprocessor(payload)
        
        assert isinstance(result, list)
        assert len(result) == 2


class TestDeleteWithMultipleAttributes:
    """Tests for delete operations with multiple attributes."""
    
    @patch('app.service.service.DataAttributes')
    @patch('app.service.service.DataAttributesValues')
    @patch('app.service.service.Data')
    def test_delete_data_multiple_attributes(self, mock_data, mock_data_attr_vals, mock_data_attrs):
        mock_data.findall.return_value = [{'_id': '1', 'DataId': '123'}]
        mock_data_attr_vals.findall.return_value = [
            {'_id': 'val1', 'DataAttributeId': 'attr1'},
            {'_id': 'val2', 'DataAttributeId': 'attr2'},
            {'_id': 'val3', 'DataAttributeId': 'attr3'}
        ]
        mock_data_attrs.findall.return_value = [
            {'_id': 'attr1'},
            {'_id': 'attr2'},
            {'_id': 'attr3'}
        ]
        
        payload = {'userid': 'user123', 'dataid': '123'}
        result = InfosysRAI.deleteData(payload)
        
        assert result == "Data Deleted Sucessfully"
    
    @patch('app.service.service.ModelAttributes')
    @patch('app.service.service.ModelAttributesValues')
    @patch('app.service.service.Model')
    def test_delete_model_multiple_attributes(self, mock_model, mock_model_attr_vals, mock_model_attrs):
        mock_model.findall.return_value = [{'_id': '1', 'ModelId': '456'}]
        mock_model_attr_vals.findall.return_value = [
            {'_id': 'val1', 'ModelAttributeId': 'attr1'},
            {'_id': 'val2', 'ModelAttributeId': 'attr2'}
        ]
        mock_model_attrs.findall.return_value = [
            {'_id': 'attr1'},
            {'_id': 'attr2'}
        ]
        
        payload = {'userid': 'user123', 'modelid': '456'}
        result = InfosysRAI.deleteModel(payload)
        
        assert result == "Model Deleted Sucessfully"

class TestGetBatchOperations:
    """Tests for batch operations."""
    
    @patch('app.service.service.Batch')
    def test_get_batch_status_list(self, mock_batch):
        mock_batch.findStatus.return_value = 'Completed'
        
        result = InfosysRAI.getBatchStatusList('batch_123')
        
        assert result == 'Completed'
    
    @patch('app.service.service.Data')
    @patch('app.service.service.Model')
    @patch('app.service.service.Batch')
    @patch('app.service.service.InfosysRAI.getTenetsList')
    def test_get_batch_table_success(self, mock_get_tenets, mock_batch, mock_model, mock_data):
        mock_batch.findBatchTable.return_value = [
            {
                'BatchId': 'batch1',
                'TenetId': 1,
                'ModelId': 'model1',
                'DataId': 'data1',
                'Status': 'Completed'
            }
        ]
        mock_get_tenets.return_value = [{'Id': 1, 'TenetName': 'Fairness', 'ProjectName': 'RAI'}]
        mock_model.findall.return_value = [{'ModelId': 'model1', 'ModelName': 'TestModel'}]
        mock_data.findall.return_value = [{'DataId': 'data1', 'DataSetName': 'TestData'}]
        
        result = InfosysRAI.getBatchTable({'userid': 'user123'})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['TenetName'] == 'Fairness'
        assert result[0]['ModelName'] == 'TestModel'
        assert result[0]['DataSetName'] == 'TestData'
    
    @patch('app.service.service.Batch')
    def test_get_batch_table_exception(self, mock_batch):
        mock_batch.findBatchTable.side_effect = Exception("Database error")
        
        result = InfosysRAI.getBatchTable({'userid': 'user123'})
        
        assert "Batch deletion Failed" in result


class TestDeleteBatchOperations:
    """Tests for deleteBatch operations."""
    
    @patch('app.service.service.Report')
    @patch('app.service.service.Html')
    @patch('app.service.service.Batch')
    @patch('app.service.service.FileStoreDb')
    def test_delete_batch_with_reports(self, mock_filestore, mock_batch, mock_html, mock_report):
        mock_batch.findall.return_value = [{'BatchId': 'batch123'}]
        mock_html.findall.return_value = [
            {'HtmlFileId': 'html1'},
            {'HtmlFileId': 'html2'}
        ]
        mock_report.findall.return_value = [
            {'ReportFileId': 'report1'},
            {'ReportFileId': 'report2'}
        ]
        
        payload = {'userid': 'user123', 'batchid': 'batch123'}
        result = InfosysRAI.deleteBatch(payload)
        
        assert result == "Batch Deleted Sucessfully"
        assert mock_filestore.delete.call_count == 4  # 2 HTML + 2 PDF
    
    @patch('app.service.service.Batch')
    def test_delete_batch_exception(self, mock_batch):
        mock_batch.findall.side_effect = Exception("Database error")
        
        payload = {'userid': 'user123', 'batchid': 'batch123'}
        result = InfosysRAI.deleteBatch(payload)
        
        assert "Batch deletion Failed" in result


class TestGetBatchListExplainability:
    """Tests for getBatchList with various tenets."""
    
    @patch('app.service.service.ModelAttributesValues')
    @patch('app.service.service.ModelAttributes')
    @patch('app.service.service.Batch')
    @patch('app.service.service.Tenet')
    @patch('app.service.service.requests')
    @patch('app.service.service.concurrent.futures.ThreadPoolExecutor')
    @patch('builtins.print')
    def test_get_batch_list_explainability(self, mock_print, mock_executor, mock_requests, 
                                           mock_tenet, mock_batch, mock_model_attrs, 
                                           mock_model_attr_vals):
        mock_tenet.findOne.return_value = 'T_EXPLAIN'
        mock_batch.create.return_value = {'BatchId': 'batch456', 'TenetId': 'T_EXPLAIN'}
        mock_model_attrs.findMAVId.return_value = 'attr_id_456'
        mock_model_attr_vals.createForBatchData.return_value = 'val_id_456'
        
        payload = {
            'tenetName': ['Explainability'],
            'userId': 'user123',
            'title': 'Explainability Test',
            'modelId': 'model1',
            'dataId': 'data1',
            'preProcessorId': 'prep1',
            'appExplanationMethods': 'SHAP'
        }
        
        with patch.dict(os.environ, {'sslVerify': 'False'}):
            result = InfosysRAI.getBatchList(payload)
        
        assert isinstance(result, list)
    
    @patch('app.service.service.ModelAttributesValues')
    @patch('app.service.service.ModelAttributes')
    @patch('app.service.service.Batch')
    @patch('app.service.service.Tenet')
    @patch('app.service.service.requests')
    @patch('app.service.service.multiprocessing.Process')
    @patch('builtins.print')
    def test_get_batch_list_security(self, mock_print, mock_process, mock_requests, 
                                     mock_tenet, mock_batch, mock_model_attrs, 
                                     mock_model_attr_vals):
        mock_tenet.findOne.return_value = 'T_SEC'
        mock_batch.create.return_value = {'BatchId': 'batch789', 'TenetId': 'T_SEC'}
        mock_model_attrs.findMAVId.return_value = 'attr_id_789'
        mock_model_attr_vals.createForBatchData.return_value = 'val_id_789'
        
        payload = {
            'tenetName': ['Security'],
            'userId': 'user123',
            'title': 'Security Test',
            'modelId': 'model1',
            'dataId': 'data1',
            'preProcessorId': 'prep1',
            'appAttacks': 'FGSM'
        }
        
        with patch.dict(os.environ, {'sslVerify': 'False'}):
            result = InfosysRAI.getBatchList(payload)
        
        assert isinstance(result, list)
    
    @patch('app.service.service.Batch')
    def test_get_batch_list_exception(self, mock_batch):
        mock_batch.create.side_effect = Exception("Batch creation failed")
        
        payload = {
            'tenetName': ['Fairness'],
            'userId': 'user123',
            'title': 'Test',
            'modelId': 'model1',
            'dataId': 'data1',
            'preProcessorId': 'prep1'
        }
        
        result = InfosysRAI.getBatchList(payload)
        
        assert "Batch Creation Failed" in result


class TestAddModelWithPipeline:
    """Tests for addModel with Pipeline model."""
    
    @patch('app.service.service.db_type', 'mongo')
    @patch('app.service.service.ModelAttributesValues')
    @patch('app.service.service.ModelAttributes')
    @patch('app.service.service.Tenet')
    @patch('app.service.service.Model')
    @patch('app.service.service.FileStoreDb')
    @patch('app.service.service.joblib')
    def test_add_model_with_pipeline(self, mock_joblib, mock_filestore, mock_model, 
                                     mock_tenet, mock_model_attrs, mock_model_attr_vals):
        mock_model.findall.return_value = []
        mock_filestore.fs.find_one.return_value = None
        mock_tenet.findOne.return_value = 'T001'
        mock_model_attrs.findall.return_value = [{'ModelAttributeId': 'attr1'}]
        mock_model.create.return_value = 'model_id_123'
        
        # Mock GridFS
        mock_file = Mock()
        mock_file.read.return_value = b'pipeline_model'
        mock_filestore.fs.get.return_value = mock_file
        mock_filestore.create.return_value = 'file_id_123'
        
        # Mock Pipeline model
        mock_pipeline = Mock()
        mock_pipeline.__class__.__name__ = 'Pipeline'
        mock_pipeline.steps = [('scaler', Mock()), ('estimator', Mock(__class__=type('RandomForest', (), {})))]
        mock_joblib.load.return_value = mock_pipeline
        
        payload1 = {
            'modelName': 'PipelineModel',
            'useModelApi': 'no',
            'problemType': 'classification'
        }
        payload2 = Mock()
        payload2.ModelFile.filename = 'model.pkl'
        payload2.ModelFile.file = Mock()
        
        result = InfosysRAI.addModel('user123', payload1, payload2)
        
        assert result == "Model Added Sucessfully"
    
    @patch('app.service.service.db_type', 'mongo')
    @patch('app.service.service.ModelAttributesValues')
    @patch('app.service.service.ModelAttributes')
    @patch('app.service.service.Tenet')
    @patch('app.service.service.Model')
    @patch('app.service.service.FileStoreDb')
    @patch('app.service.service.joblib')
    def test_add_model_with_arima(self, mock_joblib, mock_filestore, mock_model, 
                                  mock_tenet, mock_model_attrs, mock_model_attr_vals):
        mock_model.findall.return_value = []
        mock_filestore.fs.find_one.return_value = None
        mock_tenet.findOne.return_value = 'T001'
        mock_model_attrs.findall.return_value = [{'ModelAttributeId': 'attr1'}]
        mock_model.create.return_value = 'model_id_123'
        
        # Mock GridFS
        mock_file = Mock()
        mock_file.read.return_value = b'arima_model'
        mock_filestore.fs.get.return_value = mock_file
        mock_filestore.create.return_value = 'file_id_123'
        
        # Mock ARIMA model
        mock_arima = Mock()
        mock_arima.__class__.__name__ = 'ARIMA'
        mock_joblib.load.return_value = mock_arima
        
        payload1 = {
            'modelName': 'ARIMAModel',
            'useModelApi': 'no',
            'problemType': 'forecasting'
        }
        payload2 = Mock()
        payload2.ModelFile.filename = 'model.pkl'
        payload2.ModelFile.file = Mock()
        
        result = InfosysRAI.addModel('user123', payload1, payload2)
        
        assert result == "Model Added Sucessfully"


class TestEdgeCases:
    """Tests for edge cases and error conditions."""
    
    @patch('app.service.service.ModelAttributes')
    @patch('app.service.service.Tenet')
    @patch('app.service.service.Model')
    @patch('app.service.service.FileStoreDb')
    def test_add_model_multiple_attribute_entries(self, mock_filestore, mock_model, 
                                                  mock_tenet, mock_model_attrs):
        mock_model.findall.return_value = []
        mock_filestore.fs.find_one.return_value = None
        mock_tenet.findOne.return_value = 'T001'
        # Return multiple entries for same attribute
        mock_model_attrs.findall.return_value = [
            {'ModelAttributeId': 'attr1'},
            {'ModelAttributeId': 'attr2'}
        ]
        
        payload1 = {
            'modelName': 'TestModel',
            'useModelApi': 'yes',
            'modelEndPoint': 'http://api.example.com',
            'problemType': 'classification'
        }
        payload2 = Mock()
        
        result = InfosysRAI.addModel('user123', payload1, payload2)
        
        assert "No Entry or Multiple entries are present" in result
    
    @patch('app.service.service.DataAttributes')
    @patch('app.service.service.Tenet')
    @patch('app.service.service.Data')
    @patch('app.service.service.FileStoreDb')
    def test_add_data_no_attribute_entry(self, mock_filestore, mock_data, 
                                        mock_tenet, mock_data_attrs):
        mock_filestore.fs.find_one.return_value = None
        mock_tenet.findOne.return_value = 'T001'
        # Return no entries for attribute
        mock_data_attrs.findall.return_value = []
        mock_data.create.return_value = 'data_id_123'
        mock_filestore.create.return_value = 'file_id_123'
        
        payload1 = {
            'dataFileName': 'TestData',
            'dataType': 'tabular'
        }
        payload2 = Mock()
        payload2.DataFile.filename = 'data.csv'
        payload2.DataFile.file = Mock()
        
        with patch.dict(os.environ, {'DB_TYPE': 'mongo'}):
            result = InfosysRAI.addData('user123', payload1, payload2)
        
        assert "No Entry or Multiple entries are present" in result
    
    @patch('app.service.service.Preprocessor')
    def test_update_preprocessor_not_exists(self, mock_preprocessor):
        mock_preprocessor.findall.return_value = []
        
        payload = {'userid': 'user123', 'preprocessorid': 'nonexistent'}
        payload1 = {'preprocessorName': 'Updated'}
        payload2 = Mock()
        
        result = InfosysRAI.updatePreprocessor(payload, payload1, payload2)
        
        assert result == "No Preprocessor Exists With This Id."
    
    @patch('app.service.service.Model')
    def test_update_model_not_exists(self, mock_model):
        mock_model.findall.return_value = []
        
        payload = {'userid': 'user123', 'modelid': 'nonexistent'}
        payload1 = {'modelName': 'Updated'}
        payload2 = Mock()
        
        result = InfosysRAI.updateModel(payload, payload1, payload2)
        
        assert result == "No Data Exists With This Id."
    
    @patch('app.service.service.Preprocessor')
    @patch('app.service.service.FileStoreDb')
    @patch('builtins.print')
    def test_update_preprocessor_mongo_success(self, mock_print, mock_filestore, mock_preprocessor):
        mock_preprocessor.findall.return_value = [
            {'_id': '1', 'PreprocessorFileId': 'old_file'}
        ]
        mock_filestore.fs.find_one.return_value = {'_id': 'old_file'}
        mock_filestore.create.return_value = 'new_file_id'
        
        payload = {'userid': 'user123', 'preprocessorid': '123'}
        payload1 = {'preprocessorName': 'UpdatedPrep'}
        payload2 = Mock()
        payload2.PreprocessorFile = Mock()
        payload2.PreprocessorFile.filename = 'new_prep.pkl'
        
        with patch.dict(os.environ, {'DB_TYPE': 'mongo'}):
            result = InfosysRAI.updatePreprocessor(payload, payload1, payload2)
        
        assert result == 'Preprocessor Updated Successfully'


class TestGetDataAdditional:
    """Additional tests for getData method."""
    
    @patch('app.service.service.DataAttributesValues')
    @patch('app.service.service.DataAttributes')
    @patch('app.service.service.Data')
    def test_get_data_no_data(self, mock_data, mock_data_attrs, mock_data_attr_vals):
        mock_data.findall.return_value = []
        
        payload = {'userid': 'user123'}
        result = InfosysRAI.getData(payload)
        
        assert result == "No Data Added Yet"
    
    @patch('app.service.service.DataAttributesValues')
    @patch('app.service.service.DataAttributes')
    @patch('app.service.service.Data')
    def test_get_data_exception(self, mock_data, mock_data_attrs, mock_data_attr_vals):
        mock_data.findall.side_effect = Exception("Database error")
        
        payload = {'userid': 'user123'}
        with pytest.raises(Exception, match="Database error"):
            InfosysRAI.getData(payload)


class TestAddDataMongo:
    """Tests for addData method with MongoDB."""
    
    @patch('app.service.service.db_type', 'mongo')
    @patch('app.service.service.DataAttributesValues')
    @patch('app.service.service.DataAttributes')
    @patch('app.service.service.Tenet')
    @patch('app.service.service.Data')
    @patch('app.service.service.FileStoreDb')
    def test_add_data_mongo_success(self, mock_filestore, mock_data, mock_tenet, 
                                    mock_data_attrs, mock_data_attr_vals):
        mock_filestore.fs.find_one.return_value = None
        mock_tenet.findOne.return_value = 'T001'
        mock_data_attrs.findall.return_value = [{'DataAttributeId': 'attr1'}]
        mock_data.create.return_value = 'data_id_123'
        mock_filestore.create.return_value = 'file_id_123'
        
        payload1 = {
            'dataFileName': 'TestData',
            'dataType': 'tabular'
        }
        payload2 = Mock()
        payload2.DataFile.filename = 'data.csv'
        payload2.DataFile.file = Mock()
        
        result = InfosysRAI.addData('user123', payload1, payload2)
        
        assert result == "Data Added Sucessfully"
    
    @patch('app.service.service.db_type', 'mongo')
    @patch('app.service.service.FileStoreDb')
    def test_add_data_already_exists(self, mock_filestore):
        mock_filestore.fs.find_one.return_value = {'_id': 'existing_file'}
        
        payload1 = {'dataFileName': 'ExistingData'}
        payload2 = Mock()
        payload2.DataFile.filename = 'data.csv'
        
        result = InfosysRAI.addData('user123', payload1, payload2)
        
        assert result == "DataFile Already Added"


class TestUpdateDataMongo:
    """Tests for updateData method with MongoDB."""
    
    @patch('app.service.service.db_type', 'mongo')
    @patch('app.service.service.FileStoreDb')
    @patch('app.service.service.Data')
    @patch('app.service.service.DataAttributes')
    @patch('app.service.service.DataAttributesValues')
    @patch('builtins.print')
    def test_update_data_mongo_success(self, mock_print, mock_data_attr_vals, mock_data_attrs, 
                                       mock_data, mock_filestore):
        mock_data.findall.return_value = [{
            '_id': 'data1',
            'DataId': 'data1',
            'SampleData': 'old_file'
        }]
        mock_data_attr_vals.findall.return_value = [
            AttributeDict({'DataAttributeId': 'attr1', 'DataAttributeValues': 'oldval', 'DataAttributeValuesId': 'val1'})
        ]
        mock_data_attrs.findall.return_value = [{'DataAttributeName': 'fileName', 'DataAttributeId': 'attr1'}]
        mock_filestore.fs.find_one.return_value = {'_id': 'old_file'}
        mock_filestore.create.return_value = 'new_file_id'
        
        payload = {'userid': 'user123', 'dataid': 'data1'}
        payload1 = {'fileName': 'newfile.csv'}
        payload2 = Mock()
        payload2.DataFile = Mock()
        payload2.DataFile.filename = 'newfile.csv'
        
        result = InfosysRAI.updateData(payload, payload1, payload2)
        
        assert result == 'Data Updated Successfully.'
    
    @patch('app.service.service.Data')
    def test_update_data_not_exists(self, mock_data):
        mock_data.findall.return_value = []
        
        payload = {'userid': 'user123', 'dataid': 'nonexistent'}
        payload1 = {}
        payload2 = Mock()
        
        result = InfosysRAI.updateData(payload, payload1, payload2)
        
        assert result == "No Data Exists With This Id."


class TestDeleteData:
    """Tests for deleteData method."""
    
    @patch('app.service.service.DataAttributes')
    @patch('app.service.service.DataAttributesValues')
    @patch('app.service.service.Data')
    def test_delete_data_success(self, mock_data, mock_data_attr_vals, mock_data_attrs):
        mock_data.findall.return_value = [{'_id': '1', 'DataId': 'data1'}]
        mock_data_attr_vals.findall.return_value = [
            {'_id': 'val1', 'DataAttributeId': 'attr1'}
        ]
        mock_data_attrs.findall.return_value = [{'_id': 'attr1'}]
        
        payload = {'userid': 'user123', 'dataid': 'data1'}
        result = InfosysRAI.deleteData(payload)
        
        assert result == "Data Deleted Sucessfully"
    
    @patch('app.service.service.Data')
    def test_delete_data_not_available(self, mock_data):
        mock_data.findall.return_value = []
        
        payload = {'userid': 'user123', 'dataid': 'nonexistent'}
        result = InfosysRAI.deleteData(payload)
        
        assert result == 'No Data Available to Delete'


class TestGetModel:
    """Additional tests for getModel method."""
    
    @patch('app.service.service.ModelAttributesValues')
    @patch('app.service.service.ModelAttributes')
    @patch('app.service.service.Model')
    @patch('builtins.print')
    def test_get_model_success(self, mock_print, mock_model, mock_model_attrs, mock_model_attr_vals):
        mock_model.findall.return_value = [
            {
                'ModelId': 1,
                'ModelName': 'TestModel',
                'ModelEndPoint': 'http://api.example.com',
                'ModelData': 'file_id'
            }
        ]
        mock_model_attrs.findall.return_value = [
            {'ModelAttributeId': 101, 'ModelAttributeName': 'problemType'}
        ]
        mock_model_attr_vals.findall.return_value = [
            {'ModelAttributeId': 101, 'ModelAttributeValues': 'classification'}
        ]
        
        payload = {'userid': 'user123'}
        result = InfosysRAI.getModel(payload)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['modelName'] == 'TestModel'


class TestAddModelZipFile:
    """Tests for addModel with zip file."""
    
    @patch('app.service.service.db_type', 'mongo')
    @patch('app.service.service.ModelAttributesValues')
    @patch('app.service.service.ModelAttributes')
    @patch('app.service.service.Tenet')
    @patch('app.service.service.Model')
    @patch('app.service.service.FileStoreDb')
    def test_add_model_zip_file(self, mock_filestore, mock_model, mock_tenet, 
                               mock_model_attrs, mock_model_attr_vals):
        mock_model.findall.return_value = []
        mock_filestore.fs.find_one.return_value = None
        mock_tenet.findOne.return_value = 'T001'
        mock_model_attrs.findall.return_value = [{'ModelAttributeId': 'attr1'}]
        mock_model.create.return_value = 'model_id_123'
        mock_filestore.create.return_value = 'file_id_123'
        
        mock_file = Mock()
        mock_file.read.return_value = b'zip_content'
        mock_filestore.fs.get.return_value = mock_file
        
        payload1 = {
            'modelName': 'LLMModel',
            'useModelApi': 'no',
            'problemType': 'llm'
        }
        payload2 = Mock()
        payload2.ModelFile.filename = 'model.zip'
        payload2.ModelFile.file = Mock()
        
        result = InfosysRAI.addModel('user123', payload1, payload2)
        
        assert result == "Model Added Sucessfully"


class TestUpdateModelMongo:
    """Tests for updateModel method with MongoDB."""
    
    @patch('app.service.service.db_type', 'mongo')
    @patch('app.service.service.FileStoreDb')
    @patch('app.service.service.Model')
    @patch('app.service.service.ModelAttributes')
    @patch('app.service.service.ModelAttributesValues')
    @patch('builtins.print')
    def test_update_model_mongo_success(self, mock_print, mock_model_attr_vals, mock_model_attrs, 
                                        mock_model, mock_filestore):
        mock_model.findall.return_value = [{
            '_id': 'model1',
            'ModelId': 'model1',
            'ModelData': 'old_file'
        }]
        mock_model_attr_vals.findall.return_value = [
            AttributeDict({
                'ModelAttributeId': 'attr1',
                'ModelAttributeValues': 'oldval',
                'ModelAttributeValuesId': 'val1'
            })
        ]
        mock_model_attrs.findall.return_value = [
            {'ModelAttributeName': 'fileName', 'ModelAttributeId': 'attr1'}
        ]
        mock_filestore.fs.find_one.return_value = {'_id': 'old_file'}
        mock_filestore.create.return_value = 'new_file_id'
        
        payload = {'userid': 'user123', 'modelid': 'model1'}
        payload1 = {'fileName': 'newmodel.pkl'}
        payload2 = Mock()
        payload2.ModelFile = Mock()
        payload2.ModelFile.filename = 'newmodel.pkl'
        
        result = InfosysRAI.updateModel(payload, payload1, payload2)
        
        assert result == 'Model Updated Successfully'


class TestDeleteModel:
    """Tests for deleteModel method."""
    
    @patch('app.service.service.ModelAttributesValues')
    @patch('app.service.service.Model')
    def test_delete_model_success(self, mock_model, mock_model_attr_vals):
        mock_model.findall.return_value = [{'_id': '1', 'ModelId': 'model1'}]
        mock_model_attr_vals.findall.return_value = [
            {'_id': 'val1', 'ModelAttributeId': 'attr1'}
        ]
        
        payload = {'userid': 'user123', 'modelid': 'model1'}
        result = InfosysRAI.deleteModel(payload)
        
        assert result == "Model Deleted Sucessfully"


class TestPreprocessorMethods:
    """Tests for preprocessor methods."""
    
    @patch('app.service.service.Preprocessor')
    def test_get_preprocessor_success(self, mock_preprocessor):
        mock_preprocessor.findall.return_value = [
            {
                'PreprocessorId': '123',
                'PreprocessorName': 'TestPrep',
                'PreprocessorFileId': 'file_id'
            }
        ]
        
        payload = {'userid': 'user123'}
        result = InfosysRAI.getPreprocessor(payload)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['preprocessorName'] == 'TestPrep'
    
    @patch('app.service.service.Preprocessor')
    def test_get_preprocessor_no_data(self, mock_preprocessor):
        mock_preprocessor.findall.return_value = []
        
        payload = {'userid': 'user123'}
        result = InfosysRAI.getPreprocessor(payload)
        
        assert result == {"message": "This user doesn't have preprocessor values"}
    
    @patch('app.service.service.db_type', 'mongo')
    @patch('app.service.service.Preprocessor')
    @patch('app.service.service.FileStoreDb')
    def test_add_preprocessor_mongo_success(self, mock_filestore, mock_preprocessor):
        mock_preprocessor.findall.return_value = []
        mock_filestore.create.return_value = 'file_id_123'
        mock_preprocessor.create.return_value = 'prep_id_123'
        
        payload1 = {'preprocessorName': 'NewPrep'}
        payload2 = Mock()
        payload2.PreprocessorFile = Mock()
        payload2.PreprocessorFile.filename = 'prep.pkl'
        
        result = InfosysRAI.addPreprocessor('user123', payload1, payload2)
        
        assert result == "Preprocessor Added Sucessfully"
    
    @patch('app.service.service.Preprocessor')
    def test_add_preprocessor_already_exists(self, mock_preprocessor):
        mock_preprocessor.findall.return_value = [{'PreprocessorName': 'ExistingPrep'}]
        
        payload1 = {'preprocessorName': 'ExistingPrep'}
        payload2 = Mock()
        
        result = InfosysRAI.addPreprocessor('user123', payload1, payload2)
        
        assert result == 'Preprocessor Already Exist With the Same Name.'
    
    @patch('app.service.service.Preprocessor')
    def test_delete_preprocessor_success(self, mock_preprocessor):
        mock_preprocessor.findall.return_value = [
            {'_id': '1', 'PreprocessorId': 'prep1'}
        ]
        
        payload = {'userid': 'user123', 'preprocessorid': 'prep1'}
        result = InfosysRAI.deletePreprocessor(payload)
        
        assert result == "Preprocessor Deleted Sucessfully"
    
    @patch('app.service.service.Preprocessor')
    def test_delete_preprocessor_not_available(self, mock_preprocessor):
        mock_preprocessor.findall.return_value = []
        
        payload = {'userid': 'user123', 'preprocessorid': 'nonexistent'}
        result = InfosysRAI.deletePreprocessor(payload)
        
        assert result == 'No Preprocessor Available to Delete'


class TestBatchMethods:
    """Tests for batch methods."""
    
    @patch('app.service.service.Batch')
    def test_get_batch_status_list(self, mock_batch):
        mock_batch.findStatus.return_value = [
            {'BatchId': 'batch1', 'Status': 'COMPLETED'}
        ]
        
        payload = {'batchid': 'batch1'}
        result = InfosysRAI.getBatchStatusList(payload)
        
        assert len(result) == 1
        assert result[0]['Status'] == 'COMPLETED'
    
    @patch('app.service.service.Data')
    @patch('app.service.service.Model')
    @patch('app.service.service.Batch')
    def test_get_batch_table_success(self, mock_batch, mock_model, mock_data):
        mock_batch.findBatchTable.return_value = [
            {'BatchId': 'batch1', 'TenetId': 'T1', 'ModelId': 'M1', 'DataId': 'D1'}
        ]
        mock_model.findall.return_value = [{'ModelId': 'M1', 'ModelName': 'TestModel'}]
        mock_data.findall.return_value = [{'DataId': 'D1', 'DataSetName': 'TestData'}]
        
        with patch.object(InfosysRAI, 'getTenetsList', return_value=[
            {'Id': 'T1', 'TenetName': 'Fairness'}
        ]):
            payload = {'userid': 'user123'}
            result = InfosysRAI.getBatchTable(payload)
        
        assert isinstance(result, list)
    
    @patch('app.service.service.Report')
    @patch('app.service.service.Html')
    @patch('app.service.service.Batch')
    @patch('app.service.service.FileStoreDb')
    def test_delete_batch_success(self, mock_filestore, mock_batch, mock_html, mock_report):
        mock_batch.findall.return_value = [{'_id': '1', 'BatchId': 'batch1'}]
        mock_html.findall.return_value = [{'HtmlFileId': 'html_file'}]
        mock_report.findall.return_value = [{'ReportFileId': 'report_file'}]
        
        payload = {'userid': 'user123', 'batchid': 'batch1'}
        result = InfosysRAI.deleteBatch(payload)
        
        assert result == "Batch Deleted Sucessfully"


class TestAdditionalServiceCoverage:
    """Additional tests to increase service.py coverage."""
    
    @patch('app.service.service.Tenet')
    def test_add_tenet_with_project_name(self, mock_tenet):
        """Test addTenet when ProjectName is provided in payload."""
        mock_tenet.findall.return_value = []
        mock_tenet.create.return_value = True
        
        payload = {'TenetName': 'NewTenet', 'ProjectName': 'CustomProject'}
        result = InfosysRAI.addTenet(payload)
        
        assert "Successfully added" in result
    
    @patch('app.service.service.Tenet')
    def test_add_tenet_exception_handling(self, mock_tenet):
        """Test addTenet exception handling."""
        mock_tenet.findall.side_effect = Exception("Database error")
        
        payload = {'TenetName': 'ErrorTenet'}
        result = InfosysRAI.addTenet(payload)
        
        assert "Failed Due To" in result
    
    @patch('app.service.service.ModelAttributesValues')
    @patch('app.service.service.Model')
    def test_delete_model_exception_handling(self, mock_model, mock_model_attr_vals):
        """Test deleteModel exception handling."""
        mock_model.findall.side_effect = Exception("Delete error")
        
        payload = {'userid': 'user123', 'modelid': 'model1'}
        with pytest.raises(Exception, match="Delete error"):
            InfosysRAI.deleteModel(payload)
    
    @patch('app.service.service.DataAttributesValues')
    @patch('app.service.service.DataAttributes')
    @patch('app.service.service.Data')
    def test_delete_data_exception_handling(self, mock_data, mock_data_attrs, mock_data_attr_vals):
        """Test deleteData exception handling."""
        mock_data.findall.side_effect = Exception("Delete error")
        
        payload = {'userid': 'user123', 'dataid': 'data1'}
        with pytest.raises(Exception, match="Delete error"):
            InfosysRAI.deleteData(payload)
    
    @patch('app.service.service.Preprocessor')
    def test_get_preprocessor_exception_handling(self, mock_preprocessor):
        """Test getPreprocessor exception handling."""
        mock_preprocessor.findall.side_effect = Exception("Retrieval error")
        
        payload = {'userid': 'user123'}
        result = InfosysRAI.getPreprocessor(payload)
        
        assert "retrieval failed" in result
    
    @patch('app.service.service.Preprocessor')
    def test_delete_preprocessor_exception_handling(self, mock_preprocessor):
        """Test deletePreprocessor exception handling."""
        mock_preprocessor.findall.side_effect = Exception("Delete error")
        
        payload = {'userid': 'user123', 'preprocessorid': 'prep1'}
        with pytest.raises(Exception, match="Delete error"):
            InfosysRAI.deletePreprocessor(payload)
    
    @patch('app.service.service.Report')
    @patch('app.service.service.Html')
    @patch('app.service.service.Batch')
    def test_delete_batch_exception_handling(self, mock_batch, mock_html, mock_report):
        """Test deleteBatch exception handling."""
        mock_batch.findall.side_effect = Exception("Delete error")
        
        payload = {'userid': 'user123', 'batchid': 'batch1'}
        result = InfosysRAI.deleteBatch(payload)
        
        assert "deletion Failed" in result
    
    @patch('app.service.service.Data')
    @patch('app.service.service.Model')
    @patch('app.service.service.Batch')
    def test_get_batch_table_exception_handling(self, mock_batch, mock_model, mock_data):
        """Test getBatchTable exception handling."""
        mock_batch.findBatchTable.side_effect = Exception("Retrieval error")
        
        payload = {'userid': 'user123'}
        result = InfosysRAI.getBatchTable(payload)
        
        assert "deletion Failed" in result
    
    @patch('app.service.service.db_type', 'mongo')
    @patch('app.service.service.Preprocessor')
    @patch('app.service.service.FileStoreDb')
    def test_add_preprocessor_exception_handling(self, mock_filestore, mock_preprocessor):
        """Test addPreprocessor exception handling."""
        mock_preprocessor.findall.side_effect = Exception("Addition error")
        
        payload1 = {'preprocessorName': 'TestPrep'}
        payload2 = Mock()
        
        result = InfosysRAI.addPreprocessor('user123', payload1, payload2)
        
        assert "Addition Failed" in result
    
    @patch('app.service.service.db_type', 'mongo')
    @patch('app.service.service.Preprocessor')
    @patch('app.service.service.FileStoreDb')
    @patch('builtins.print')
    def test_update_preprocessor_exception_handling(self, mock_print, mock_filestore, mock_preprocessor):
        """Test updatePreprocessor exception handling."""
        mock_preprocessor.findall.return_value = [{'_id': '1', 'PreprocessorFileId': 'file1'}]
        mock_preprocessor.update.side_effect = Exception("Update error")
        
        payload = {'userid': 'user123', 'preprocessorid': 'prep1'}
        payload1 = {'preprocessorName': 'UpdatedPrep'}
        payload2 = Mock()
        payload2.PreprocessorFile = None
        
        result = InfosysRAI.updatePreprocessor(payload, payload1, payload2)
        
        assert "updating Failed" in result
    
    @patch('app.service.service.db_type', 'mongo')
    @patch('app.service.service.DataAttributesValues')
    @patch('app.service.service.DataAttributes')
    @patch('app.service.service.Tenet')
    @patch('app.service.service.Data')
    @patch('app.service.service.FileStoreDb')
    def test_add_data_exception_handling(self, mock_filestore, mock_data, mock_tenet,
                                         mock_data_attrs, mock_data_attr_vals):
        """Test addData exception handling."""
        mock_filestore.fs.find_one.side_effect = Exception("File error")
        
        payload1 = {'dataFileName': 'TestData'}
        payload2 = Mock()
        payload2.DataFile.filename = 'data.csv'
        
        result = InfosysRAI.addData('user123', payload1, payload2)
        
        assert "Addition Failed" in result
    
    @patch('app.service.service.db_type', 'mongo')
    @patch('app.service.service.ModelAttributesValues')
    @patch('app.service.service.ModelAttributes')
    @patch('app.service.service.Tenet')
    @patch('app.service.service.Model')
    @patch('app.service.service.FileStoreDb')
    def test_add_model_exception_handling(self, mock_filestore, mock_model, mock_tenet,
                                          mock_model_attrs, mock_model_attr_vals):
        """Test addModel exception handling."""
        mock_model.findall.side_effect = Exception("Model error")
        
        payload1 = {'modelName': 'TestModel', 'useModelApi': 'no'}
        payload2 = Mock()
        
        result = InfosysRAI.addModel('user123', payload1, payload2)
        
        assert "Addition Failed" in result
    
    @patch('app.service.service.Data')
    @patch('app.service.service.DataAttributes')
    @patch('app.service.service.DataAttributesValues')
    @patch('app.service.service.FileStoreDb')
    @patch('builtins.print')
    def test_update_data_exception_handling(self, mock_print, mock_filestore,
                                            mock_data_attr_vals, mock_data_attrs, mock_data):
        """Test updateData exception handling."""
        mock_data.findall.side_effect = Exception("Update error")
        
        payload = {'userid': 'user123', 'dataid': 'data1'}
        payload1 = {}
        payload2 = Mock()
        
        with pytest.raises(Exception, match="Update error"):
            InfosysRAI.updateData(payload, payload1, payload2)
    
    @patch('app.service.service.Model')
    @patch('app.service.service.ModelAttributes')
    @patch('app.service.service.ModelAttributesValues')
    @patch('app.service.service.FileStoreDb')
    @patch('builtins.print')
    def test_update_model_exception_handling(self, mock_print, mock_filestore,
                                             mock_model_attr_vals, mock_model_attrs, mock_model):
        """Test updateModel exception handling."""
        mock_model.findall.side_effect = Exception("Update error")
        
        payload = {'userid': 'user123', 'modelid': 'model1'}
        payload1 = {}
        payload2 = Mock()
        
        with pytest.raises(Exception, match="Update error"):
            InfosysRAI.updateModel(payload, payload1, payload2)


class TestComprehensiveServiceCoverage:
    """Comprehensive tests to achieve 86% code coverage."""
    
    @patch('app.service.service.Tenet')
    def test_get_tenets_list_empty(self, mock_tenet):
        """Test getTenetsList with empty result."""
        mock_tenet.findall.return_value = []
        result = InfosysRAI.getTenetsList()
        assert result == []
    
    @patch('app.service.service.Tenet')
    def test_get_tenets_list_exception(self, mock_tenet):
        """Test getTenetsList exception handling."""
        mock_tenet.findall.side_effect = Exception("Database error")
        result = InfosysRAI.getTenetsList()
        assert result == "Something Went Wrong"
    
    @patch('app.service.service.Tenet')
    def test_add_tenet_already_exists(self, mock_tenet):
        """Test addTenet when tenet already exists."""
        mock_tenet.findall.return_value = [{'TenetName': 'Fairness'}]
        payload = {'TenetName': 'Fairness'}
        result = InfosysRAI.addTenet(payload)
        assert "Already Exists" in result
    
    @patch('app.service.service.Tenet')
    def test_delete_tenet_success(self, mock_tenet):
        """Test deletetenet success."""
        mock_tenet.delete.return_value = True
        payload = {'TenetName': 'Fairness'}
        result = InfosysRAI.deletetenet(payload)
        assert "Successfully Deleted" in result
    
    @patch('app.service.service.Tenet')
    def test_delete_tenet_exception(self, mock_tenet):
        """Test deletetenet exception handling."""
        mock_tenet.delete.side_effect = Exception("Delete error")
        payload = {'TenetName': 'Fairness'}
        result = InfosysRAI.deletetenet(payload)
        assert "deletion failed" in result
    
    @patch('app.service.service.db_type', 'mongo')
    @patch('app.service.service.DataAttributesValues')
    @patch('app.service.service.DataAttributes')
    @patch('app.service.service.Tenet')
    @patch('app.service.service.Data')
    @patch('app.service.service.FileStoreDb')
    def test_add_data_file_already_exists(self, mock_filestore, mock_data, mock_tenet,
                                          mock_data_attrs, mock_data_attr_vals):
        """Test addData when file already exists."""
        mock_filestore.fs.find_one.return_value = {'filename': 'existing.csv'}
        
        payload1 = {'dataFileName': 'ExistingData', 'dataType': 'Tabular'}
        payload2 = Mock()
        payload2.DataFile.filename = 'existing.csv'
        
        result = InfosysRAI.addData('user123', payload1, payload2)
        assert result == "DataFile Already Added"
    
    @patch('app.service.service.DataAttributesValues')
    @patch('app.service.service.DataAttributes')
    @patch('app.service.service.Data')
    def test_delete_data_not_found(self, mock_data, mock_data_attrs, mock_data_attr_vals):
        """Test deleteData when data not found."""
        mock_data.findall.return_value = []
        
        payload = {'userid': 'user123', 'dataid': 'nonexistent'}
        result = InfosysRAI.deleteData(payload)
        assert result == "No Data Available to Delete"
    
    @patch('app.service.service.Preprocessor')
    def test_delete_preprocessor_not_found(self, mock_preprocessor):
        """Test deletePreprocessor when not found."""
        mock_preprocessor.findall.return_value = []
        
        payload = {'userid': 'user123', 'preprocessorid': 'nonexistent'}
        result = InfosysRAI.deletePreprocessor(payload)
        assert result == "No Preprocessor Available to Delete"
    
    @patch('app.service.service.Report')
    @patch('app.service.service.Html')
    @patch('app.service.service.Batch')
    def test_delete_batch_with_reports(self, mock_batch, mock_html, mock_report):
        """Test deleteBatch when batch has associated reports."""
        mock_batch.findall.return_value = [{'BatchId': 'batch1'}]
        mock_html.findall.return_value = [{'HtmlId': 'html1'}]
        mock_report.findall.return_value = [{'ReportId': 'report1'}]
        mock_html.delete.return_value = True
        mock_report.delete.return_value = True
        mock_batch.delete.return_value = True
        
        payload = {'userid': 'user123', 'batchid': 'batch1'}
        result = InfosysRAI.deleteBatch(payload)
        assert result == "Batch Deleted Sucessfully"
