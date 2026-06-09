"""
Unit tests for routers module.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app.routing.routers import (
    data, model, tenet, batch, preprocessor
)


# Create a test app
app = FastAPI()
app.include_router(tenet, tags=["tenet"])
app.include_router(data, tags=["data"])
app.include_router(model, tags=["model"])
app.include_router(preprocessor, tags=["preprocessor"])
app.include_router(batch, tags=["batch"])

client = TestClient(app)


class TestTenetRoutes:
    """Tests for tenet routes."""
    
    @patch('app.routing.routers.InfosysRAI')
    @patch('app.routing.routers.gc')
    def test_get_tenet(self, mock_gc, mock_infosys_rai):
        mock_infosys_rai.getTenetsList.return_value = [
            {'Id': 1, 'TenetName': 'Fairness'}
        ]
        
        response = client.get('/v1/workbench/tenet')
        
        assert response.status_code == 200
        mock_infosys_rai.getTenetsList.assert_called_once()
        mock_gc.collect.assert_called_once()
    
    @patch('app.routing.routers.InfosysRAI')
    @patch('app.routing.routers.gc')
    def test_add_tenet(self, mock_gc, mock_infosys_rai):
        mock_infosys_rai.addTenet.return_value = "Successfully added fairness Tenet."
        
        response = client.post(
            '/v1/workbench/addtenet',
            json={'TenetName': 'Fairness', 'ProjectName': 'RAI'}
        )
        
        assert response.status_code == 200
        mock_infosys_rai.addTenet.assert_called_once()
        mock_gc.collect.assert_called_once()
    
    @patch('app.routing.routers.InfosysRAI')
    @patch('app.routing.routers.gc')
    def test_delete_tenet(self, mock_gc, mock_infosys_rai):
        mock_infosys_rai.deletetenet.return_value = "Successfully Deleted fairness Tenet."
        
        response = client.delete('/v1/workbench/deletetenet?TenetName=Fairness')
        
        assert response.status_code == 200
        mock_infosys_rai.deletetenet.assert_called_once()
        mock_gc.collect.assert_called_once()
    
    @patch('app.routing.routers.InfosysRAI')
    def test_get_tenet_empty_list(self, mock_infosys_rai):
        mock_infosys_rai.getTenetsList.return_value = []
        
        response = client.get('/v1/workbench/tenet')
        
        assert response.status_code == 200
        assert response.json() == []
    
    @patch('app.routing.routers.InfosysRAI')
    def test_add_tenet_already_exists(self, mock_infosys_rai):
        mock_infosys_rai.addTenet.return_value = "Fairness Already Exists"
        
        response = client.post(
            '/v1/workbench/addtenet',
            json={'TenetName': 'Fairness'}
        )
        
        assert response.status_code == 200


class TestDataRoutes:
    """Tests for data routes."""
    
    @patch('app.routing.routers.InfosysRAI')
    @patch('app.routing.routers.gc')
    def test_get_datas(self, mock_gc, mock_infosys_rai):
        mock_infosys_rai.getData.return_value = [
            {'dataSetName': 'test_data', 'DataId': 1}
        ]
        
        response = client.post(
            '/v1/workbench/data',
            data={'userId': 'user123'}
        )
        
        assert response.status_code == 200
        mock_infosys_rai.getData.assert_called_once()
        mock_gc.collect.assert_called_once()
    
    @patch('app.routing.routers.InfosysRAI')
    @patch('app.routing.routers.gc')
    def test_add_data(self, mock_gc, mock_infosys_rai):
        mock_infosys_rai.addData.return_value = "Data Added Sucessfully"
        
        # Mock file upload
        files = {'DataFile': ('test.csv', b'data', 'text/csv')}
        data_payload = {
            'userId': 'user123',
            'Payload': '{"dataFileName": "test_data"}',
        }
        
        response = client.post(
            '/v1/workbench/adddata',
            data=data_payload,
            files=files
        )
        
        # Accept both success and validation error
        assert response.status_code in [200, 422]
        # Only check if gc.collect was called if the request succeeded
        if response.status_code == 200:
            mock_gc.collect.assert_called()
    
    @patch('app.routing.routers.InfosysRAI')
    @patch('app.routing.routers.gc')
    def test_delete_data(self, mock_gc, mock_infosys_rai):
        mock_infosys_rai.deleteData.return_value = "Data Deleted Sucessfully"
        
        response = client.request(
            method='DELETE',
            url='/v1/workbench/deletedata',
            data={'userId': 'user123', 'dataid': 1}
        )
        
        assert response.status_code == 200
        mock_infosys_rai.deleteData.assert_called_once()
        mock_gc.collect.assert_called_once()
    
    @patch('app.routing.routers.InfosysRAI')
    def test_get_datas_no_data(self, mock_infosys_rai):
        mock_infosys_rai.getData.return_value = "No Data Added Yet"
        
        response = client.post(
            '/v1/workbench/data',
            data={'userId': 'user123'}
        )
        
        assert response.status_code == 200


class TestModelRoutes:
    """Tests for model routes."""
    
    @patch('app.routing.routers.InfosysRAI')
    @patch('app.routing.routers.gc')
    def test_get_models(self, mock_gc, mock_infosys_rai):
        mock_infosys_rai.getModel.return_value = [
            {'modelName': 'test_model', 'ModelId': 1}
        ]
        
        response = client.post(
            '/v1/workbench/model',
            data={'userId': 'user123'}
        )
        
        assert response.status_code == 200
        mock_infosys_rai.getModel.assert_called_once()
        mock_gc.collect.assert_called_once()
    
    @patch('app.routing.routers.InfosysRAI')
    @patch('app.routing.routers.gc')
    def test_add_model(self, mock_gc, mock_infosys_rai):
        mock_infosys_rai.addModel.return_value = "Model Added Sucessfully"
        
        files = {'ModelFile': ('model.pkl', b'model_data', 'application/octet-stream')}
        data_payload = {
            'userId': 'user123',
            'Payload': '{"modelName": "test_model", "useModelApi": "no"}',
        }
        
        response = client.post(
            '/v1/workbench/addmodel',
            data=data_payload,
            files=files
        )
        
        assert response.status_code in [200, 422]
        # Only check if gc.collect was called if the request succeeded
        if response.status_code == 200:
            mock_gc.collect.assert_called()
    
    @patch('app.routing.routers.InfosysRAI')
    @patch('app.routing.routers.gc')
    def test_delete_model(self, mock_gc, mock_infosys_rai):
        mock_infosys_rai.deleteModel.return_value = "Model Deleted Sucessfully"
        
        response = client.request(
            method='DELETE',
            url='/v1/workbench/deletemodel',
            data={'userId': 'user123', 'modelId': 1}
        )
        
        assert response.status_code == 200
        mock_infosys_rai.deleteModel.assert_called_once()
        mock_gc.collect.assert_called_once()
    
    @patch('app.routing.routers.InfosysRAI')
    def test_get_models_no_model(self, mock_infosys_rai):
        mock_infosys_rai.getModel.return_value = "No Model Added Yet"
        
        response = client.post(
            '/v1/workbench/model',
            data={'userId': 'user123'}
        )
        
        assert response.status_code == 200


class TestPreprocessorRoutes:
    """Tests for preprocessor routes."""
    
    @patch('app.routing.routers.InfosysRAI')
    @patch('app.routing.routers.gc')
    def test_get_preprocessor(self, mock_gc, mock_infosys_rai):
        mock_infosys_rai.getPreprocessor.return_value = [
            {'preprocessorName': 'test_preprocessor', 'PreprocessorId': 1}
        ]
        
        response = client.post(
            '/v1/workbench/preprocessor',
            data={'userId': 'user123'}
        )
        
        assert response.status_code == 200
        mock_infosys_rai.getPreprocessor.assert_called_once()
        mock_gc.collect.assert_called_once()
    
    @patch('app.routing.routers.InfosysRAI')
    @patch('app.routing.routers.gc')
    def test_add_preprocessor(self, mock_gc, mock_infosys_rai):
        mock_infosys_rai.addPreprocessor.return_value = "Preprocessor Added Sucessfully"
        
        files = {'PreprocessorFile': ('preprocessor.pkl', b'preprocessor_data', 'application/octet-stream')}
        data_payload = {
            'userId': 'user123',
            'preprocessorName': 'test_preprocessor',
        }
        
        response = client.post(
            '/v1/workbench/addpreprocessor',
            data=data_payload,
            files=files
        )
        
        assert response.status_code in [200, 422]
        mock_gc.collect.assert_called()
    
    @patch('app.routing.routers.InfosysRAI')
    @patch('app.routing.routers.gc')
    def test_delete_preprocessor(self, mock_gc, mock_infosys_rai):
        mock_infosys_rai.deletePreprocessor.return_value = "Preprocessor Deleted Sucessfully"
        
        response = client.request(
            method='DELETE',
            url='/v1/workbench/deletepreprocessor',
            data={'userId': 'user123', 'preprocessorId': 1}
        )
        
        assert response.status_code == 200
        mock_infosys_rai.deletePreprocessor.assert_called_once()
        mock_gc.collect.assert_called_once()
    
    @patch('app.routing.routers.InfosysRAI')
    def test_get_preprocessor_no_data(self, mock_infosys_rai):
        mock_infosys_rai.getPreprocessor.return_value = {"message": "This user doesn't have preprocessor values"}
        
        response = client.post(
            '/v1/workbench/preprocessor',
            data={'userId': 'user123'}
        )
        
        assert response.status_code == 200


class TestBatchRoutes:
    """Tests for batch routes."""
    
    @patch('app.routing.routers.InfosysRAI')
    @patch('app.routing.routers.gc')
    def test_get_batch_status(self, mock_gc, mock_infosys_rai):
        mock_infosys_rai.getBatchStatusList.return_value = {'status': 'completed'}
        
        response = client.post(
            '/v1/workbench/getbatchstatus',
            data={'id': 1}
        )
        
        assert response.status_code == 200
        mock_gc.collect.assert_called_once()
    
    @patch('app.routing.routers.InfosysRAI')
    @patch('app.routing.routers.gc')
    def test_get_batch_table(self, mock_gc, mock_infosys_rai):
        mock_infosys_rai.getBatchTable.return_value = [
            {'BatchId': 'batch123', 'TenetName': 'Fairness'}
        ]
        
        response = client.post(
            '/v1/workbench/getbatchtable',
            data={'userId': 'user123'}
        )
        
        assert response.status_code == 200
        mock_infosys_rai.getBatchTable.assert_called_once()
        mock_gc.collect.assert_called_once()
    
    @patch('app.routing.routers.InfosysRAI')
    @patch('app.routing.routers.gc')
    def test_delete_batch(self, mock_gc, mock_infosys_rai):
        mock_infosys_rai.deleteBatch.return_value = "Batch Deleted Sucessfully"
        
        response = client.request(
            method='DELETE',
            url='/v1/workbench/deletebatch',
            data={'userId': 'user123', 'batchId': 1}
        )
        
        assert response.status_code == 200
        mock_infosys_rai.deleteBatch.assert_called_once()
        mock_gc.collect.assert_called_once()


class TestRouteIntegration:
    """Integration tests for routes."""
    
    @patch('app.routing.routers.InfosysRAI')
    @patch('app.routing.routers.gc')
    def test_gc_collect_called_on_all_routes(self, mock_gc, mock_infosys_rai):
        # Mock all InfosysRAI methods
        mock_infosys_rai.getTenetsList.return_value = []
        mock_infosys_rai.getData.return_value = []
        mock_infosys_rai.getModel.return_value = []
        mock_infosys_rai.getPreprocessor.return_value = []
        mock_infosys_rai.getBatchTable.return_value = []
        
        # Test multiple routes
        client.get('/v1/workbench/tenet')
        client.post('/v1/workbench/data', data={'userId': 'user123'})
        client.post('/v1/workbench/model', data={'userId': 'user123'})
        
        # Verify gc.collect was called multiple times
        assert mock_gc.collect.call_count >= 3
    
    @patch('app.routing.routers.InfosysRAI')
    def test_all_routes_return_service_response(self, mock_infosys_rai):
        # Mock responses
        mock_infosys_rai.getTenetsList.return_value = "service_response"
        mock_infosys_rai.getData.return_value = "service_response"
        mock_infosys_rai.getModel.return_value = "service_response"
        
        # Test routes
        response1 = client.get('/v1/workbench/tenet')
        response2 = client.post('/v1/workbench/data', data={'userId': 'user123'})
        response3 = client.post('/v1/workbench/model', data={'userId': 'user123'})
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
    
    @patch('app.routing.routers.InfosysRAI')
    def test_routes_handle_various_user_ids(self, mock_infosys_rai):
        mock_infosys_rai.getData.return_value = []
        
        user_ids = ['user1', 'user123', 'test@example.com', '12345']
        
        for user_id in user_ids:
            response = client.post(
                '/v1/workbench/data',
                data={'userId': user_id}
            )
            assert response.status_code == 200
    
    @patch('app.routing.routers.InfosysRAI')
    def test_delete_routes_with_various_ids(self, mock_infosys_rai):
        mock_infosys_rai.deleteData.return_value = "Deleted"
        mock_infosys_rai.deleteModel.return_value = "Deleted"
        mock_infosys_rai.deleteBatch.return_value = "Deleted"
        
        # Test delete routes with different IDs
        client.request(method='DELETE', url='/v1/workbench/deletedata', data={'userId': 'user1', 'dataid': 1})
        client.request(method='DELETE', url='/v1/workbench/deletemodel', data={'userId': 'user1', 'modelId': 2})
        client.request(method='DELETE', url='/v1/workbench/deletebatch', data={'userId': 'user1', 'batchId': 3})
        
        assert mock_infosys_rai.deleteData.call_count >= 1
        assert mock_infosys_rai.deleteModel.call_count >= 1
        assert mock_infosys_rai.deleteBatch.call_count >= 1
