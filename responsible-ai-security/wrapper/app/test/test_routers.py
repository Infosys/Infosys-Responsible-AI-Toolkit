
'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
'''

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from src.routing.routers import attack, bulk
from src.mappers.mappers import GetAttackDataRequest

# Setup minimal app for testing
app = FastAPI()
app.include_router(attack)
app.include_router(bulk)

class TestRouters:

    @patch('src.routing.routers.gc.collect', return_value=0)
    @patch('src.service.service.Infosys.getAttackFuncs')
    def test_get_attacks(self, mock_get, mock_gc):
        mock_get.return_value = {"attack1": "func1"}
        
        # Form data as per routers.py
        payload = {
            'TargetClassifier': 'Sklearn',
            'TargetDataType': 'Tabular'
        }
        
        with TestClient(app) as client:
            response = client.post('/rai/v1/security_workbench/attack', data=payload)
        
        assert response.status_code == 200
        assert response.json() == {"attack1": "func1"}
        mock_get.assert_called_once()
        # Verify call args if needed
        # actual_call = mock_get.call_args[0][0]
        # assert actual_call['targetClassifier'] == 'Sklearn'

    @patch('src.routing.routers.gc.collect', return_value=0)
    @patch('src.service.service.Infosys.addAttack')
    def test_add_attack(self, mock_add, mock_gc):
        mock_add.return_value = {"status": "success"}
        
        json_payload = {
            "attackName": "NewAttack",
            "attackDataType": "Tabular",
            "algorithmSupported": "XGBoost",
            "attackFunc": "fn_attack"
        }
        
        with TestClient(app) as client:
            response = client.post('/rai/v1/security_workbench/addattack', json=json_payload)
        
        assert response.status_code == 200
        assert response.json() == {"status": "success"}
        mock_add.assert_called_once()

    @patch('src.routing.routers.gc.collect', return_value=0)
    @patch('src.service.service.Infosys.deleteAttack')
    def test_delete_attack(self, mock_delete, mock_gc):
        mock_delete.return_value = {"status": "deleted"}
        
        # Query parameter: AttacFunc
        params = {"AttacFunc": "OldAttack"}
        
        with TestClient(app) as client:
            response = client.delete('/rai/v1/security_workbench/deleteattack', params=params)
        
        assert response.status_code == 200
        assert response.json() == {"status": "deleted"}
        mock_delete.assert_called_once()

    @patch('src.routing.routers.gc.collect', return_value=0)
    @patch('src.service.service.Bulk.runAllAttack')
    def test_run_all_attacks(self, mock_run, mock_gc):
        mock_run.return_value = 12345.0
        
        # Form data: batchId, dateTime (optional)
        data = {
            "batchId": 101.0
        }
        
        with TestClient(app) as client:
            response = client.post('/rai/v1/security_workbench/runallattacks', data=data)
        
        assert response.status_code == 200
        assert response.json() == {'BatchId': 12345.0}
        mock_run.assert_called_once()

    @patch('src.routing.routers.gc.collect', return_value=0)
    @patch('src.service.service.Infosys.getAttackFuncs')
    def test_get_attacks_exception(self, mock_get, mock_gc):
        mock_get.side_effect = Exception("DB Error")
        
        payload = {'TargetClassifier': 'Sklearn', 'TargetDataType': 'Tabular'}
        # Check if 500 is handled. The router catches exception and returns HTTPException(500)
        with TestClient(app) as client:
            response = client.post('/rai/v1/security_workbench/attack', data=payload)
        assert response.status_code == 500
        assert "Internal server error" in response.json()['detail']

    @patch('src.routing.routers.gc.collect', return_value=0)
    @patch('src.service.service.Infosys.addAttack')
    def test_add_attack_exception(self, mock_add, mock_gc):
        mock_add.side_effect = Exception("Add failed")
        
        json_payload = {
            "attackName": "NewAttack",
            "attackDataType": "Tabular",
            "algorithmSupported": "XGBoost",
            "attackFunc": "fn_attack"
        }
        
        with TestClient(app) as client:
            response = client.post('/rai/v1/security_workbench/addattack', json=json_payload)
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()['detail']

    @patch('src.routing.routers.gc.collect', return_value=0)
    @patch('src.service.service.Infosys.deleteAttack')
    def test_delete_attack_exception(self, mock_delete, mock_gc):
        mock_delete.side_effect = Exception("Delete failed")
        
        params = {"AttacFunc": "OldAttack"}
        
        with TestClient(app) as client:
            response = client.delete('/rai/v1/security_workbench/deleteattack', params=params)
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()['detail']

    @patch('src.routing.routers.gc.collect', return_value=0)
    @patch('src.service.service.Bulk.runAllAttack')
    def test_run_all_attacks_exception(self, mock_run, mock_gc):
        mock_run.side_effect = Exception("Run failed")
        
        data = {"batchId": 101.0}
        
        with TestClient(app) as client:
            response = client.post('/rai/v1/security_workbench/runallattacks', data=data)
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()['detail']

    @patch('src.routing.routers.UT.dateTimeFormat')
    @patch('src.routing.routers.gc.collect', return_value=0)
    @patch('src.service.service.Bulk.runAllAttack')
    def test_run_all_attacks_with_datetime(self, mock_run, mock_gc, mock_dt_format):
        import datetime
        mock_run.return_value = 12346.0
        mock_dt_format.return_value = "2024-01-01 00:00:00"
        
        dt = datetime.datetime(2024, 1, 1)
        data = {
            "batchId": 102.0,
            "dateTime": dt.isoformat()
        }
        
        with TestClient(app) as client:
            response = client.post('/rai/v1/security_workbench/runallattacks', data=data)
        
        assert response.status_code == 200
        assert response.json() == {'BatchId': 12346.0}
