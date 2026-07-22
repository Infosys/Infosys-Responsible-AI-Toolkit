"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Unit tests for RecognizerMapper.py
"""

import pytest
from datetime import datetime
from pydantic import ValidationError


@pytest.mark.unit
class TestRecognizerMappers:
    """Test cases for Recognizer mapper models"""

    def test_recog_request_valid(self):
        """Test RecogRequest with valid data"""
        from rai_admin.mappers.RecognizerMapper import RecogRequest
        
        data = {
            "RecogName": "Email Recognizer",
            "Entity": "EMAIL"
        }
        
        recog_request = RecogRequest(**data)
        
        assert recog_request.RecogName == "Email Recognizer"
        assert recog_request.Entity == "EMAIL"

    def test_data_grp_update_valid(self):
        """Test DataGrpUpdate with valid data"""
        from rai_admin.mappers.RecognizerMapper import DataGrpUpdate
        
        data = {
            "RecogId": 120.1234,
            "RecogName": "Updated Recognizer",
            "supported_entity": "PHONE"
        }
        
        update_model = DataGrpUpdate(**data)
        
        assert update_model.RecogId == 120.1234
        assert update_model.RecogName == "Updated Recognizer"
        assert update_model.supported_entity == "PHONE"

    def test_data_grp_delete_valid(self):
        """Test DataGrpDelete with valid data"""
        from rai_admin.mappers.RecognizerMapper import DataGrpDelete
        
        delete_model = DataGrpDelete(RecogId=120.1234)
        
        assert delete_model.RecogId == 120.1234

    def test_data_entity_delete_valid(self):
        """Test DataEntityDelete with valid data"""
        from rai_admin.mappers.RecognizerMapper import DataEntityDelete
        
        delete_model = DataEntityDelete(EntityId=134.234)
        
        assert delete_model.EntityId == 134.234

    def test_recog_status_valid(self):
        """Test RecogStatus with valid data"""
        from rai_admin.mappers.RecognizerMapper import RecogStatus
        
        status_model = RecogStatus(status="success")
        
        assert status_model.status == "success"

    def test_data_entity_add_valid(self):
        """Test DataEntityAdd with valid data"""
        from rai_admin.mappers.RecognizerMapper import DataEntityAdd
        
        data = {
            "EntityNames": ["Entity1", "Entity2"],
            "RecogId": 120.1234
        }
        
        add_model = DataEntityAdd(**data)
        
        assert add_model.EntityNames == ["Entity1", "Entity2"]
        assert add_model.RecogId == 120.1234

    def test_data_entity_valid(self):
        """Test DataEntity with valid data"""
        from rai_admin.mappers.RecognizerMapper import DataEntity
        
        data = {
            "EntityId": 134.234,
            "EntityName": "Test Entity",
            "RecogId": 234.234
        }
        
        entity_model = DataEntity(**data)
        
        assert entity_model.EntityId == 134.234
        assert entity_model.EntityName == "Test Entity"
        assert entity_model.RecogId == 234.234

    def test_data_entities_request_valid(self):
        """Test DataEntitiesRequest with valid data"""
        from rai_admin.mappers.RecognizerMapper import DataEntitiesRequest
        
        request_model = DataEntitiesRequest(RecogId=124.123)
        
        assert request_model.RecogId == 124.123

    def test_data_entities_response_valid(self):
        """Test DataEntitiesResponse with valid data"""
        from rai_admin.mappers.RecognizerMapper import DataEntitiesResponse, DataEntity
        
        entities = [
            DataEntity(EntityId=1.1, EntityName="Entity1", RecogId=100.1),
            DataEntity(EntityId=2.2, EntityName="Entity2", RecogId=100.1)
        ]
        
        response_model = DataEntitiesResponse(DataEntities=entities)
        
        assert len(response_model.DataEntities) == 2
        assert response_model.DataEntities[0].EntityName == "Entity1"

    def test_recog_response_valid(self):
        """Test RecogResponse with valid data"""
        from rai_admin.mappers.RecognizerMapper import RecogResponse, DataGrpEntity
        
        entities = [
            DataGrpEntity(
                RecogId=120.1234,
                RecogName="Test Recognizer",
                supported_entity="EMAIL",
                RecogType="Data",
                Score=1.1,
                Context="Test Context",
                isEditable="Yes",
                isPreDefined="Yes",
                isActive="Yes",
                isCreated="Not Started",
                CreatedDateTime=datetime.now(),
                LastUpdatedDateTime=datetime.now()
            )
        ]
        
        response_model = RecogResponse(RecogList=entities)
        
        assert len(response_model.RecogList) == 1
        assert response_model.RecogList[0].RecogName == "Test Recognizer"
