
import pytest
import json
from pydantic import ValidationError
from src.mappers.mappers import GetAttackDataRequest

class TestMappersAdditional:
    def test_get_attack_data_request_creation(self):
        request = GetAttackDataRequest(attackName='TestAttack', attackDataType='Tabular', algorithmSupported='XGBoost', attackFunc='test_func')
        assert request.attackName == 'TestAttack'
        assert request.attackDataType == 'Tabular'
        
    def test_get_attack_data_request_defaults(self):
        request = GetAttackDataRequest()
        assert request.attackName == 'attackName'
        assert request.attackDataType == 'Tabular or Image or Text'
        
    def test_get_attack_data_request_json_string(self):
        json_str = json.dumps({'attackName': 'JSONAttack', 'attackDataType': 'Image', 'algorithmSupported': 'CNN', 'attackFunc': 'json_func'})
        request = GetAttackDataRequest.validate_to_json(json_str)
        assert request.attackName == 'JSONAttack'
        
    def test_get_attack_data_request_dict(self):
        data_dict = {'attackName': 'DictAttack', 'attackDataType': 'Text', 'algorithmSupported': 'BERT', 'attackFunc': 'dict_func'}
        request = GetAttackDataRequest(**data_dict)
        assert request.attackName == 'DictAttack'
        
    def test_get_attack_data_request_partial(self):
        request = GetAttackDataRequest(attackName='PartialAttack')
        assert request.attackName == 'PartialAttack'
        
    def test_get_attack_data_request_empty_strings(self):
        request = GetAttackDataRequest(attackName='', attackDataType='', algorithmSupported='', attackFunc='')
        assert request.attackName == ''
        
    def test_get_attack_data_request_special_chars(self):
        request = GetAttackDataRequest(attackName='Attack@123', attackDataType='Tabular', algorithmSupported='XGB', attackFunc='func_v1')
        assert request.attackName == 'Attack@123'
        
    def test_get_attack_data_request_long_strings(self):
        long_name = 'A' * 1000
        request = GetAttackDataRequest(attackName=long_name)
        assert len(request.attackName) == 1000
        
    def test_get_attack_data_request_validators(self):
        validators = list(GetAttackDataRequest.__get_validators__())
        assert len(validators) == 1
