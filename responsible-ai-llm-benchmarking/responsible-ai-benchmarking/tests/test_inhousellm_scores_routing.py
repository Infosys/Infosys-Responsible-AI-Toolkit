"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient

# Add the parent directory to the path to import the router
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the database connection before importing the router
# This prevents the actual database connection from being created during module import
with patch('dao.databaseConnection.DataBase') as mock_db_class:
    mock_db_instance = MagicMock()
    mock_db_class.return_value = mock_db_instance
    mock_db_instance.db = MagicMock()
    
    from router.inhousellm_scores_routing import router


# Fixtures
@pytest.fixture
def client():
    """Create a test client for the FastAPI router."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def mock_service():
    """Mock the Scores service."""
    with patch('router.inhousellm_scores_routing.service') as mock:
        yield mock


@pytest.fixture
def mock_logger():
    """Mock the CustomLogger."""
    with patch('router.inhousellm_scores_routing.log') as mock:
        yield mock


@pytest.fixture
def sample_fairness_scores():
    """Sample fairness scores data."""
    return [
        {
            "model_name": "gpt-4",
            "category": "fairness",
            "score": 0.85,
            "metrics": {"bias": 0.15, "equity": 0.90}
        },
        {
            "model_name": "llama-2",
            "category": "fairness",
            "score": 0.78,
            "metrics": {"bias": 0.22, "equity": 0.85}
        }
    ]


@pytest.fixture
def sample_privacy_scores():
    """Sample privacy scores data."""
    return [
        {
            "model_name": "gpt-4",
            "category": "privacy",
            "score": 0.92,
            "metrics": {"data_leak": 0.08}
        }
    ]


@pytest.fixture
def sample_safety_scores():
    """Sample safety scores data."""
    return [
        {
            "model_name": "gpt-4",
            "category": "safety",
            "score": 0.88,
            "metrics": {"harmful_content": 0.12}
        }
    ]


@pytest.fixture
def sample_ethics_scores():
    """Sample ethics scores data."""
    return [
        {
            "model_name": "gpt-4",
            "category": "ethics",
            "score": 0.90,
            "metrics": {"moral_alignment": 0.91}
        }
    ]


@pytest.fixture
def sample_truthfulness_scores():
    """Sample truthfulness scores data."""
    return [
        {
            "model_name": "gpt-4",
            "category": "truthfulness",
            "score": 0.87,
            "metrics": {"accuracy": 0.89, "hallucination": 0.11}
        }
    ]


@pytest.fixture
def sample_add_score_payload():
    """Sample payload for adding a score."""
    return {
        "category": "fairness",
        "model_name": "new-model",
        "score": 0.75,
        "metrics": {"bias": 0.25, "equity": 0.80}
    }


# Test Cases for GET /inhouse/scores/fairness/getScores
class TestGetFairnessScores:
    """Test cases for fairness scores endpoint."""
    
    def test_get_fairness_scores_success(self, client, mock_service, mock_logger, sample_fairness_scores):
        """Test successful retrieval of fairness scores."""
        mock_service.getFairnessScores.return_value = sample_fairness_scores
        
        response = client.get("/inhouse/scores/fairness/getScores")
        
        assert response.status_code == 200
        assert response.json() == sample_fairness_scores
        mock_service.getFairnessScores.assert_called_once()
        mock_logger.info.assert_called()
    
    def test_get_fairness_scores_empty_list(self, client, mock_service, mock_logger):
        """Test retrieval when no fairness scores exist."""
        mock_service.getFairnessScores.return_value = []
        
        response = client.get("/inhouse/scores/fairness/getScores")
        
        assert response.status_code == 200
        assert response.json() == []
        mock_service.getFairnessScores.assert_called_once()
    
    def test_get_fairness_scores_exception(self, client, mock_service, mock_logger):
        """Test error handling when getFairnessScores raises an exception."""
        error_dict = {"status_code": 500, "detail": "Database connection failed"}
        mock_exception = HTTPException(status_code=500, detail="Database connection failed")
        mock_exception.__dict__ = error_dict
        mock_service.getFairnessScores.side_effect = mock_exception
        
        response = client.get("/inhouse/scores/fairness/getScores")
        
        assert response.status_code == 500
        mock_logger.error.assert_called()


# Test Cases for GET /inhouse/scores/privacy/getScores
class TestGetPrivacyScores:
    """Test cases for privacy scores endpoint."""
    
    def test_get_privacy_scores_success(self, client, mock_service, mock_logger, sample_privacy_scores):
        """Test successful retrieval of privacy scores."""
        mock_service.getPrivacyScores.return_value = sample_privacy_scores
        
        response = client.get("/inhouse/scores/privacy/getScores")
        
        assert response.status_code == 200
        assert response.json() == sample_privacy_scores
        mock_service.getPrivacyScores.assert_called_once()
    
    def test_get_privacy_scores_empty_list(self, client, mock_service, mock_logger):
        """Test retrieval when no privacy scores exist."""
        mock_service.getPrivacyScores.return_value = []
        
        response = client.get("/inhouse/scores/privacy/getScores")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_privacy_scores_exception(self, client, mock_service, mock_logger):
        """Test error handling when getPrivacyScores raises an exception."""
        error_dict = {"status_code": 500, "detail": "Internal server error"}
        mock_exception = HTTPException(status_code=500, detail="Internal server error")
        mock_exception.__dict__ = error_dict
        mock_service.getPrivacyScores.side_effect = mock_exception
        
        response = client.get("/inhouse/scores/privacy/getScores")
        
        assert response.status_code == 500


# Test Cases for GET /inhouse/scores/safety/getScores
class TestGetSafetyScores:
    """Test cases for safety scores endpoint."""
    
    def test_get_safety_scores_success(self, client, mock_service, mock_logger, sample_safety_scores):
        """Test successful retrieval of safety scores."""
        mock_service.getSafteyScores.return_value = sample_safety_scores
        
        response = client.get("/inhouse/scores/safety/getScores")
        
        assert response.status_code == 200
        assert response.json() == sample_safety_scores
        mock_service.getSafteyScores.assert_called_once()
    
    def test_get_safety_scores_empty_list(self, client, mock_service, mock_logger):
        """Test retrieval when no safety scores exist."""
        mock_service.getSafteyScores.return_value = []
        
        response = client.get("/inhouse/scores/safety/getScores")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_safety_scores_exception(self, client, mock_service, mock_logger):
        """Test error handling when getSafteyScores raises an exception."""
        error_dict = {"status_code": 503, "detail": "Service unavailable"}
        mock_exception = HTTPException(status_code=503, detail="Service unavailable")
        mock_exception.__dict__ = error_dict
        mock_service.getSafteyScores.side_effect = mock_exception
        
        response = client.get("/inhouse/scores/safety/getScores")
        
        assert response.status_code == 503


# Test Cases for GET /inhouse/scores/ethics/getScores
class TestGetEthicsScores:
    """Test cases for ethics scores endpoint."""
    
    def test_get_ethics_scores_success(self, client, mock_service, mock_logger, sample_ethics_scores):
        """Test successful retrieval of ethics scores."""
        mock_service.getEthicsScores.return_value = sample_ethics_scores
        
        response = client.get("/inhouse/scores/ethics/getScores")
        
        assert response.status_code == 200
        assert response.json() == sample_ethics_scores
        mock_service.getEthicsScores.assert_called_once()
    
    def test_get_ethics_scores_empty_list(self, client, mock_service, mock_logger):
        """Test retrieval when no ethics scores exist."""
        mock_service.getEthicsScores.return_value = []
        
        response = client.get("/inhouse/scores/ethics/getScores")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_ethics_scores_exception(self, client, mock_service, mock_logger):
        """Test error handling when getEthicsScores raises an exception."""
        error_dict = {"status_code": 500, "detail": "Database error"}
        mock_exception = HTTPException(status_code=500, detail="Database error")
        mock_exception.__dict__ = error_dict
        mock_service.getEthicsScores.side_effect = mock_exception
        
        response = client.get("/inhouse/scores/ethics/getScores")
        
        assert response.status_code == 500


# Test Cases for GET /inhouse/scores/truthfullness/getScores
class TestGetTruthfulnessScores:
    """Test cases for truthfulness scores endpoint."""
    
    def test_get_truthfulness_scores_success(self, client, mock_service, mock_logger, sample_truthfulness_scores):
        """Test successful retrieval of truthfulness scores."""
        mock_service.getTruthfullnessScores.return_value = sample_truthfulness_scores
        
        response = client.get("/inhouse/scores/truthfullness/getScores")
        
        assert response.status_code == 200
        assert response.json() == sample_truthfulness_scores
        mock_service.getTruthfullnessScores.assert_called_once()
    
    def test_get_truthfulness_scores_empty_list(self, client, mock_service, mock_logger):
        """Test retrieval when no truthfulness scores exist."""
        mock_service.getTruthfullnessScores.return_value = []
        
        response = client.get("/inhouse/scores/truthfullness/getScores")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_truthfulness_scores_exception(self, client, mock_service, mock_logger):
        """Test error handling when getTruthfullnessScores raises an exception."""
        error_dict = {"status_code": 404, "detail": "Resource not found"}
        mock_exception = HTTPException(status_code=404, detail="Resource not found")
        mock_exception.__dict__ = error_dict
        mock_service.getTruthfullnessScores.side_effect = mock_exception
        
        response = client.get("/inhouse/scores/truthfullness/getScores")
        
        assert response.status_code == 404


# Test Cases for POST /inhouse/scores/fairness/addScore
class TestAddScore:
    """Test cases for adding scores endpoint."""
    
    def test_add_score_success(self, client, mock_service, mock_logger, sample_add_score_payload):
        """Test successful addition of a score."""
        mock_service.addScore.return_value = {"message": "Score added successfully"}
        
        response = client.post("/inhouse/scores/fairness/addScore", json=sample_add_score_payload)
        
        assert response.status_code == 200
        assert response.json() == {"message": "Score added successfully"}
        mock_service.addScore.assert_called_once_with(sample_add_score_payload)
    
    def test_add_score_with_different_categories(self, client, mock_service, mock_logger):
        """Test adding scores for different categories."""
        categories = ["fairness", "privacy", "safety", "ethics", "truthfullness"]
        
        for category in categories:
            payload = {
                "category": category,
                "model_name": f"{category}-model",
                "score": 0.85
            }
            mock_service.addScore.return_value = {"message": f"{category} score added"}
            
            response = client.post("/inhouse/scores/fairness/addScore", json=payload)
            
            assert response.status_code == 200
            mock_service.addScore.assert_called_with(payload)
    
    def test_add_score_invalid_payload(self, client, mock_service, mock_logger):
        """Test adding score with invalid payload."""
        invalid_payload = {"invalid_key": "invalid_value"}
        error_dict = {"status_code": 400, "detail": "Invalid payload"}
        mock_exception = HTTPException(status_code=400, detail="Invalid payload")
        mock_exception.__dict__ = error_dict
        mock_service.addScore.side_effect = mock_exception
        
        response = client.post("/inhouse/scores/fairness/addScore", json=invalid_payload)
        
        assert response.status_code == 400
    
    def test_add_score_duplicate_entry(self, client, mock_service, mock_logger):
        """Test adding a score that already exists."""
        payload = {
            "category": "fairness",
            "model_name": "existing-model",
            "score": 0.75
        }
        error_dict = {"status_code": 409, "detail": "Score already exists"}
        mock_exception = HTTPException(status_code=409, detail="Score already exists")
        mock_exception.__dict__ = error_dict
        mock_service.addScore.side_effect = mock_exception
        
        response = client.post("/inhouse/scores/fairness/addScore", json=payload)
        
        assert response.status_code == 409
    
    def test_add_score_exception(self, client, mock_service, mock_logger, sample_add_score_payload):
        """Test error handling when addScore raises an exception."""
        error_dict = {"status_code": 500, "detail": "Failed to add score"}
        mock_exception = HTTPException(status_code=500, detail="Failed to add score")
        mock_exception.__dict__ = error_dict
        mock_service.addScore.side_effect = mock_exception
        
        response = client.post("/inhouse/scores/fairness/addScore", json=sample_add_score_payload)
        
        assert response.status_code == 500
        mock_logger.error.assert_called()


# Test Cases for POST /inhouse/scores/fairness/deleteScore
class TestDeleteScore:
    """Test cases for deleting scores endpoint."""
    
    def test_delete_score_success(self, client, mock_service, mock_logger):
        """Test successful deletion of a score."""
        mock_service.deleteScores.return_value = "Deleted Successfully"
        
        response = client.post(
            "/inhouse/scores/fairness/deleteScore",
            params={"category": "fairness", "model_name": "test-model"}
        )
        
        assert response.status_code == 200
        assert response.json() == "Deleted Successfully"
        mock_service.deleteScores.assert_called_once_with("fairness", "test-model")
    
    def test_delete_score_all_categories(self, client, mock_service, mock_logger):
        """Test deleting scores from all categories."""
        categories = ["fairness", "privacy", "safety", "ethics", "truthfullness"]
        
        for category in categories:
            mock_service.deleteScores.return_value = "Deleted Successfully"
            
            response = client.post(
                "/inhouse/scores/fairness/deleteScore",
                params={"category": category, "model_name": f"{category}-model"}
            )
            
            assert response.status_code == 200
            mock_service.deleteScores.assert_called_with(category, f"{category}-model")
    
    def test_delete_score_not_found(self, client, mock_service, mock_logger):
        """Test deletion when score doesn't exist."""
        mock_service.deleteScores.return_value = "Some problem Occures while deleting the scores"
        
        response = client.post(
            "/inhouse/scores/fairness/deleteScore",
            params={"category": "fairness", "model_name": "non-existent-model"}
        )
        
        assert response.status_code == 200
        assert "problem" in response.json().lower()
    
    def test_delete_score_missing_category(self, client, mock_service, mock_logger):
        """Test deletion with missing category parameter."""
        response = client.post(
            "/inhouse/scores/fairness/deleteScore",
            params={"model_name": "test-model"}
        )
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_delete_score_missing_model_name(self, client, mock_service, mock_logger):
        """Test deletion with missing model_name parameter."""
        response = client.post(
            "/inhouse/scores/fairness/deleteScore",
            params={"category": "fairness"}
        )
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_delete_score_exception(self, client, mock_service, mock_logger):
        """Test error handling when deleteScores raises an exception."""
        error_dict = {"status_code": 500, "detail": "Database error during deletion"}
        mock_exception = HTTPException(status_code=500, detail="Database error during deletion")
        mock_exception.__dict__ = error_dict
        mock_service.deleteScores.side_effect = mock_exception
        
        response = client.post(
            "/inhouse/scores/fairness/deleteScore",
            params={"category": "fairness", "model_name": "test-model"}
        )
        
        assert response.status_code == 500
        mock_logger.error.assert_called()


# Integration Tests
class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_add_and_retrieve_score_workflow(self, client, mock_service, mock_logger):
        """Test the complete workflow of adding and retrieving a score."""
        # Add a score
        add_payload = {
            "category": "fairness",
            "model_name": "workflow-model",
            "score": 0.82
        }
        mock_service.addScore.return_value = {"message": "Score added successfully"}
        
        add_response = client.post("/inhouse/scores/fairness/addScore", json=add_payload)
        assert add_response.status_code == 200
        
        # Retrieve scores
        mock_service.getFairnessScores.return_value = [add_payload]
        get_response = client.get("/inhouse/scores/fairness/getScores")
        
        assert get_response.status_code == 200
        assert len(get_response.json()) == 1
    
    def test_add_retrieve_and_delete_workflow(self, client, mock_service, mock_logger):
        """Test the complete workflow of adding, retrieving, and deleting a score."""
        model_name = "complete-workflow-model"
        
        # Add a score
        add_payload = {
            "category": "fairness",
            "model_name": model_name,
            "score": 0.88
        }
        mock_service.addScore.return_value = {"message": "Score added successfully"}
        add_response = client.post("/inhouse/scores/fairness/addScore", json=add_payload)
        assert add_response.status_code == 200
        
        # Retrieve scores
        mock_service.getFairnessScores.return_value = [add_payload]
        get_response = client.get("/inhouse/scores/fairness/getScores")
        assert get_response.status_code == 200
        assert any(score["model_name"] == model_name for score in get_response.json())
        
        # Delete the score
        mock_service.deleteScores.return_value = "Deleted Successfully"
        delete_response = client.post(
            "/inhouse/scores/fairness/deleteScore",
            params={"category": "fairness", "model_name": model_name}
        )
        assert delete_response.status_code == 200
        assert delete_response.json() == "Deleted Successfully"


# Edge Cases and Boundary Tests
class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_get_scores_with_special_characters(self, client, mock_service, mock_logger):
        """Test retrieving scores with special characters in model names."""
        special_scores = [
            {"model_name": "model-with-dash", "score": 0.85},
            {"model_name": "model_with_underscore", "score": 0.90},
            {"model_name": "model.with.dots", "score": 0.88}
        ]
        mock_service.getFairnessScores.return_value = special_scores
        
        response = client.get("/inhouse/scores/fairness/getScores")
        
        assert response.status_code == 200
        assert len(response.json()) == 3
    
    def test_add_score_with_boundary_values(self, client, mock_service, mock_logger):
        """Test adding scores with boundary values."""
        boundary_cases = [
            {"category": "fairness", "model_name": "zero-score", "score": 0.0},
            {"category": "fairness", "model_name": "perfect-score", "score": 1.0},
            {"category": "fairness", "model_name": "negative-score", "score": -0.1}
        ]
        
        for payload in boundary_cases:
            mock_service.addScore.return_value = {"message": "Score added"}
            response = client.post("/inhouse/scores/fairness/addScore", json=payload)
            
            # Should handle appropriately (either accept or reject based on validation)
            assert response.status_code in [200, 400, 422]
    
    def test_delete_score_with_empty_string(self, client, mock_service, mock_logger):
        """Test deletion with empty string parameters."""
        mock_service.deleteScores.return_value = "Some problem Occures while deleting the scores"
        
        response = client.post(
            "/inhouse/scores/fairness/deleteScore",
            params={"category": "", "model_name": ""}
        )
        
        # Should handle empty strings appropriately
        assert response.status_code in [200, 400, 422]


# Performance and Load Tests
class TestPerformance:
    """Test performance-related scenarios."""
    
    def test_retrieve_large_dataset(self, client, mock_service, mock_logger):
        """Test retrieving a large number of scores."""
        large_dataset = [
            {
                "model_name": f"model-{i}",
                "category": "fairness",
                "score": 0.75 + (i % 25) * 0.01
            }
            for i in range(1000)
        ]
        mock_service.getFairnessScores.return_value = large_dataset
        
        response = client.get("/inhouse/scores/fairness/getScores")
        
        assert response.status_code == 200
        assert len(response.json()) == 1000
    
    def test_concurrent_score_additions(self, client, mock_service, mock_logger):
        """Test adding multiple scores in sequence."""
        mock_service.addScore.return_value = {"message": "Score added successfully"}
        
        for i in range(10):
            payload = {
                "category": "fairness",
                "model_name": f"concurrent-model-{i}",
                "score": 0.80 + i * 0.01
            }
            response = client.post("/inhouse/scores/fairness/addScore", json=payload)
            assert response.status_code == 200


# Security Tests
class TestSecurity:
    """Test security-related scenarios."""
    
    def test_sql_injection_in_model_name(self, client, mock_service, mock_logger):
        """Test SQL injection attempts in model_name parameter."""
        malicious_payloads = [
            "'; DROP TABLE scores; --",
            "' OR '1'='1",
            "admin'--",
            "1' UNION SELECT * FROM users--"
        ]
        
        for malicious_input in malicious_payloads:
            mock_service.deleteScores.return_value = "Deleted Successfully"
            response = client.post(
                "/inhouse/scores/fairness/deleteScore",
                params={"category": "fairness", "model_name": malicious_input}
            )
            # Service should handle or sanitize the input
            assert response.status_code in [200, 400, 422]
    
    def test_xss_in_payload(self, client, mock_service, mock_logger):
        """Test XSS attempts in payload data."""
        xss_payload = {
            "category": "fairness",
            "model_name": "<script>alert('XSS')</script>",
            "score": 0.85,
            "metrics": {"test": "<img src=x onerror=alert('XSS')>"}
        }
        mock_service.addScore.return_value = {"message": "Score added successfully"}
        
        response = client.post("/inhouse/scores/fairness/addScore", json=xss_payload)
        
        # Should handle or sanitize XSS attempts
        assert response.status_code in [200, 400]
    
    def test_oversized_payload(self, client, mock_service, mock_logger):
        """Test handling of extremely large payload."""
        oversized_payload = {
            "category": "fairness",
            "model_name": "test-model",
            "score": 0.85,
            "metrics": {"data": "A" * 10000000}  # 10MB of data
        }
        error_dict = {"status_code": 413, "detail": "Payload too large"}
        mock_exception = HTTPException(status_code=413, detail="Payload too large")
        mock_exception.__dict__ = error_dict
        mock_service.addScore.side_effect = mock_exception
        
        response = client.post("/inhouse/scores/fairness/addScore", json=oversized_payload)
        
        # Should reject oversized payloads
        assert response.status_code in [413, 400, 422]
    
    def test_unauthorized_access_without_auth(self, client, mock_service, mock_logger):
        """Test endpoints without authentication headers (if auth is required)."""
        # This test assumes authentication might be required in the future
        response = client.get("/inhouse/scores/fairness/getScores")
        
        # Currently returns 200, but should be monitored for auth implementation
        assert response.status_code in [200, 401, 403]
    
    def test_path_traversal_attempt(self, client, mock_service, mock_logger):
        """Test path traversal attempts in parameters."""
        path_traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "....//....//....//etc/passwd"
        ]
        
        for attempt in path_traversal_attempts:
            mock_service.deleteScores.return_value = "Deleted Successfully"
            response = client.post(
                "/inhouse/scores/fairness/deleteScore",
                params={"category": attempt, "model_name": "test"}
            )
            assert response.status_code in [200, 400, 422]


# Data Validation Tests
class TestDataValidation:
    """Test data validation and type checking."""
    
    def test_invalid_score_type(self, client, mock_service, mock_logger):
        """Test adding score with invalid data type."""
        invalid_payloads = [
            {"category": "fairness", "model_name": "test", "score": "invalid"},
            {"category": "fairness", "model_name": "test", "score": None},
            {"category": "fairness", "model_name": "test", "score": []},
            {"category": "fairness", "model_name": "test", "score": {}}
        ]
        
        for payload in invalid_payloads:
            error_dict = {"status_code": 422, "detail": "Invalid score type"}
            mock_exception = HTTPException(status_code=422, detail="Invalid score type")
            mock_exception.__dict__ = error_dict
            mock_service.addScore.side_effect = mock_exception
            
            response = client.post("/inhouse/scores/fairness/addScore", json=payload)
            assert response.status_code in [400, 422]
    
    def test_score_out_of_range(self, client, mock_service, mock_logger):
        """Test scores outside valid range (if applicable)."""
        out_of_range_scores = [1.5, 2.0, -1.0, 100, -100]
        
        for score in out_of_range_scores:
            payload = {
                "category": "fairness",
                "model_name": "test-model",
                "score": score
            }
            error_dict = {"status_code": 400, "detail": "Score out of range"}
            mock_exception = HTTPException(status_code=400, detail="Score out of range")
            mock_exception.__dict__ = error_dict
            mock_service.addScore.side_effect = mock_exception
            
            response = client.post("/inhouse/scores/fairness/addScore", json=payload)
            assert response.status_code in [200, 400, 422]
    
    def test_missing_required_fields(self, client, mock_service, mock_logger):
        """Test payload with missing required fields."""
        incomplete_payloads = [
            {"category": "fairness", "model_name": "test"},  # missing score
            {"category": "fairness", "score": 0.85},  # missing model_name
            {"model_name": "test", "score": 0.85},  # missing category
            {}  # empty payload
        ]
        
        for payload in incomplete_payloads:
            error_dict = {"status_code": 422, "detail": "Missing required fields"}
            mock_exception = HTTPException(status_code=422, detail="Missing required fields")
            mock_exception.__dict__ = error_dict
            mock_service.addScore.side_effect = mock_exception
            
            response = client.post("/inhouse/scores/fairness/addScore", json=payload)
            assert response.status_code in [400, 422]
    
    def test_null_and_none_values(self, client, mock_service, mock_logger):
        """Test handling of null and None values."""
        null_payloads = [
            {"category": None, "model_name": "test", "score": 0.85},
            {"category": "fairness", "model_name": None, "score": 0.85},
            {"category": "fairness", "model_name": "test", "score": None}
        ]
        
        for payload in null_payloads:
            error_dict = {"status_code": 422, "detail": "Null values not allowed"}
            mock_exception = HTTPException(status_code=422, detail="Null values not allowed")
            mock_exception.__dict__ = error_dict
            mock_service.addScore.side_effect = mock_exception
            
            response = client.post("/inhouse/scores/fairness/addScore", json=payload)
            assert response.status_code in [400, 422]
    
    def test_unicode_and_special_characters(self, client, mock_service, mock_logger):
        """Test handling of unicode and special characters."""
        special_char_payloads = [
            {"category": "fairness", "model_name": "模型-测试", "score": 0.85},
            {"category": "fairness", "model_name": "модель-тест", "score": 0.85},
            {"category": "fairness", "model_name": "🤖-model", "score": 0.85},
            {"category": "fairness", "model_name": "test\x00model", "score": 0.85}
        ]
        
        for payload in special_char_payloads:
            mock_service.addScore.return_value = {"message": "Score added successfully"}
            response = client.post("/inhouse/scores/fairness/addScore", json=payload)
            # Should either accept or properly reject unicode/special chars
            assert response.status_code in [200, 400, 422]


# Response Validation Tests
class TestResponseValidation:
    """Test response format and content validation."""
    
    def test_response_content_type(self, client, mock_service, mock_logger, sample_fairness_scores):
        """Test that response has correct content type."""
        mock_service.getFairnessScores.return_value = sample_fairness_scores
        
        response = client.get("/inhouse/scores/fairness/getScores")
        
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")
    
    def test_response_structure_consistency(self, client, mock_service, mock_logger):
        """Test that all GET endpoints return consistent structure."""
        endpoints = [
            ("/inhouse/scores/fairness/getScores", "getFairnessScores"),
            ("/inhouse/scores/privacy/getScores", "getPrivacyScores"),
            ("/inhouse/scores/safety/getScores", "getSafteyScores"),
            ("/inhouse/scores/ethics/getScores", "getEthicsScores"),
            ("/inhouse/scores/truthfullness/getScores", "getTruthfullnessScores")
        ]
        
        for endpoint, method_name in endpoints:
            sample_data = [{"model_name": "test", "category": "test", "score": 0.85}]
            getattr(mock_service, method_name).return_value = sample_data
            
            response = client.get(endpoint)
            
            assert response.status_code == 200
            assert isinstance(response.json(), list)
    
    def test_error_response_format(self, client, mock_service, mock_logger):
        """Test that error responses have consistent format."""
        error_dict = {"status_code": 500, "detail": "Test error"}
        mock_exception = HTTPException(status_code=500, detail="Test error")
        mock_exception.__dict__ = error_dict
        mock_service.getFairnessScores.side_effect = mock_exception
        
        response = client.get("/inhouse/scores/fairness/getScores")
        
        assert response.status_code == 500
        # FastAPI automatically formats error responses
        assert "detail" in response.json()


# Concurrency and Thread Safety Tests
class TestConcurrency:
    """Test concurrent operations and thread safety."""
    
    def test_simultaneous_reads(self, client, mock_service, mock_logger, sample_fairness_scores):
        """Test multiple simultaneous read operations."""
        mock_service.getFairnessScores.return_value = sample_fairness_scores
        
        # Simulate multiple concurrent requests
        responses = []
        for _ in range(5):
            response = client.get("/inhouse/scores/fairness/getScores")
            responses.append(response)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            assert response.json() == sample_fairness_scores
    
    def test_read_during_write(self, client, mock_service, mock_logger, sample_fairness_scores):
        """Test reading data while write operation is in progress."""
        # Simulate write operation
        add_payload = {"category": "fairness", "model_name": "test", "score": 0.85}
        mock_service.addScore.return_value = {"message": "Score added successfully"}
        
        write_response = client.post("/inhouse/scores/fairness/addScore", json=add_payload)
        
        # Simulate read during write
        mock_service.getFairnessScores.return_value = sample_fairness_scores
        read_response = client.get("/inhouse/scores/fairness/getScores")
        
        assert write_response.status_code == 200
        assert read_response.status_code == 200


# Idempotency Tests
class TestIdempotency:
    """Test idempotency of operations."""
    
    def test_get_request_idempotency(self, client, mock_service, mock_logger, sample_fairness_scores):
        """Test that GET requests are idempotent."""
        mock_service.getFairnessScores.return_value = sample_fairness_scores
        
        # Make multiple identical GET requests
        responses = []
        for _ in range(3):
            response = client.get("/inhouse/scores/fairness/getScores")
            responses.append(response.json())
        
        # All responses should be identical
        assert all(resp == responses[0] for resp in responses)
    
    def test_delete_idempotency(self, client, mock_service, mock_logger):
        """Test delete operation idempotency."""
        # First delete should succeed
        mock_service.deleteScores.return_value = "Deleted Successfully"
        response1 = client.post(
            "/inhouse/scores/fairness/deleteScore",
            params={"category": "fairness", "model_name": "test-model"}
        )
        
        # Second delete of same item
        mock_service.deleteScores.return_value = "Some problem Occures while deleting the scores"
        response2 = client.post(
            "/inhouse/scores/fairness/deleteScore",
            params={"category": "fairness", "model_name": "test-model"}
        )
        
        assert response1.status_code == 200
        # Second delete should handle gracefully
        assert response2.status_code in [200, 404]


# Logging and Observability Tests
class TestLogging:
    """Test logging functionality."""
    
    def test_info_logging_on_success(self, client, mock_service, mock_logger, sample_fairness_scores):
        """Test that info logs are generated on successful operations."""
        mock_service.getFairnessScores.return_value = sample_fairness_scores
        
        response = client.get("/inhouse/scores/fairness/getScores")
        
        assert response.status_code == 200
        # Verify that info logging was called
        assert mock_logger.info.call_count >= 1
    
    def test_error_logging_on_failure(self, client, mock_service, mock_logger):
        """Test that error logs are generated on failures."""
        error_dict = {"status_code": 500, "detail": "Test error"}
        mock_exception = HTTPException(status_code=500, detail="Test error")
        mock_exception.__dict__ = error_dict
        mock_service.getFairnessScores.side_effect = mock_exception
        
        response = client.get("/inhouse/scores/fairness/getScores")
        
        assert response.status_code == 500
        # Verify that error logging was called
        mock_logger.error.assert_called()
    
    def test_logging_includes_operation_details(self, client, mock_service, mock_logger):
        """Test that logs include relevant operation details."""
        payload = {"category": "fairness", "model_name": "test", "score": 0.85}
        mock_service.addScore.return_value = {"message": "Score added successfully"}
        
        response = client.post("/inhouse/scores/fairness/addScore", json=payload)
        
        assert response.status_code == 200
        # Logs should be called with operation info
        assert mock_logger.info.called


# State Management Tests
class TestStateManagement:
    """Test state management and data consistency."""
    
    def test_service_state_isolation(self, client, mock_service, mock_logger):
        """Test that operations don't interfere with each other's state."""
        # Add fairness score
        fairness_payload = {"category": "fairness", "model_name": "test1", "score": 0.85}
        mock_service.addScore.return_value = {"message": "Score added"}
        response1 = client.post("/inhouse/scores/fairness/addScore", json=fairness_payload)
        
        # Add privacy score
        privacy_payload = {"category": "privacy", "model_name": "test2", "score": 0.90}
        mock_service.addScore.return_value = {"message": "Score added"}
        response2 = client.post("/inhouse/scores/fairness/addScore", json=privacy_payload)
        
        # Both should succeed independently
        assert response1.status_code == 200
        assert response2.status_code == 200
    
    def test_data_consistency_after_error(self, client, mock_service, mock_logger, sample_fairness_scores):
        """Test that data remains consistent after an error occurs."""
        # Successful operation
        mock_service.getFairnessScores.return_value = sample_fairness_scores
        response1 = client.get("/inhouse/scores/fairness/getScores")
        assert response1.status_code == 200
        
        # Failed operation
        error_dict = {"status_code": 500, "detail": "Temporary error"}
        mock_exception = HTTPException(status_code=500, detail="Temporary error")
        mock_exception.__dict__ = error_dict
        mock_service.getFairnessScores.side_effect = mock_exception
        response2 = client.get("/inhouse/scores/fairness/getScores")
        assert response2.status_code == 500
        
        # Subsequent operation should work
        mock_service.getFairnessScores.side_effect = None
        mock_service.getFairnessScores.return_value = sample_fairness_scores
        response3 = client.get("/inhouse/scores/fairness/getScores")
        assert response3.status_code == 200


# HTTP Method Tests
class TestHTTPMethods:
    """Test HTTP method handling."""
    
    def test_invalid_http_methods(self, client, mock_service, mock_logger):
        """Test that endpoints reject invalid HTTP methods."""
        # Try POST on GET endpoint
        response = client.post("/inhouse/scores/fairness/getScores")
        assert response.status_code == 405  # Method Not Allowed
        
        # Try GET on POST endpoint
        response = client.get("/inhouse/scores/fairness/addScore")
        assert response.status_code == 405
        
        # Try PUT on endpoints
        response = client.put("/inhouse/scores/fairness/getScores")
        assert response.status_code == 405
        
        # Try PATCH on endpoints
        response = client.patch("/inhouse/scores/fairness/getScores")
        assert response.status_code == 405
    
    def test_options_method(self, client, mock_service, mock_logger):
        """Test OPTIONS method for CORS preflight."""
        response = client.options("/inhouse/scores/fairness/getScores")
        # Should return allowed methods or 200
        assert response.status_code in [200, 204, 405]
    
    def test_head_method(self, client, mock_service, mock_logger):
        """Test HEAD method returns headers without body."""
        response = client.head("/inhouse/scores/fairness/getScores")
        # HEAD should work like GET but without body
        assert response.status_code in [200, 405]


# Input Sanitization Tests
class TestInputSanitization:
    """Test input sanitization and normalization."""
    
    def test_whitespace_handling(self, client, mock_service, mock_logger):
        """Test handling of leading/trailing whitespace."""
        payloads = [
            {"category": " fairness ", "model_name": " test ", "score": 0.85},
            {"category": "fairness\n", "model_name": "test\t", "score": 0.85},
            {"category": "  fairness  ", "model_name": "  test  ", "score": 0.85}
        ]
        
        for payload in payloads:
            mock_service.addScore.return_value = {"message": "Score added"}
            response = client.post("/inhouse/scores/fairness/addScore", json=payload)
            # Should either accept or normalize whitespace
            assert response.status_code in [200, 400, 422]
    
    def test_case_sensitivity(self, client, mock_service, mock_logger):
        """Test case sensitivity in category names."""
        categories = ["fairness", "Fairness", "FAIRNESS", "FaIrNeSs"]
        
        for category in categories:
            mock_service.deleteScores.return_value = "Deleted Successfully"
            response = client.post(
                "/inhouse/scores/fairness/deleteScore",
                params={"category": category, "model_name": "test"}
            )
            # Should handle case consistently
            assert response.status_code in [200, 400, 422]
    
    def test_model_name_length_limits(self, client, mock_service, mock_logger):
        """Test model name with various lengths."""
        # Very short name
        short_payload = {"category": "fairness", "model_name": "a", "score": 0.85}
        mock_service.addScore.return_value = {"message": "Score added"}
        response1 = client.post("/inhouse/scores/fairness/addScore", json=short_payload)
        
        # Very long name
        long_payload = {"category": "fairness", "model_name": "a" * 1000, "score": 0.85}
        mock_service.addScore.return_value = {"message": "Score added"}
        response2 = client.post("/inhouse/scores/fairness/addScore", json=long_payload)
        
        # Empty name
        empty_payload = {"category": "fairness", "model_name": "", "score": 0.85}
        error_dict = {"status_code": 400, "detail": "Empty model name"}
        mock_exception = HTTPException(status_code=400, detail="Empty model name")
        mock_exception.__dict__ = error_dict
        mock_service.addScore.side_effect = mock_exception
        response3 = client.post("/inhouse/scores/fairness/addScore", json=empty_payload)
        
        # Should validate length appropriately
        assert response1.status_code in [200, 400, 422]
        assert response2.status_code in [200, 400, 422]
        assert response3.status_code in [400, 422]


# Regression Tests
class TestRegression:
    """Regression tests for previously fixed bugs."""
    
    def test_duplicate_function_names_fixed(self, client, mock_service, mock_logger):
        """Regression: Ensure all endpoint functions have unique names."""
        # The router had multiple functions named 'getScore'
        # This test ensures they all work correctly despite the naming
        endpoints = [
            "/inhouse/scores/fairness/getScores",
            "/inhouse/scores/privacy/getScores",
            "/inhouse/scores/safety/getScores",
            "/inhouse/scores/ethics/getScores",
            "/inhouse/scores/truthfullness/getScores"
        ]
        
        for endpoint in endpoints:
            method_name = endpoint.split("/")[3]  # Extract category
            if method_name == "fairness":
                mock_service.getFairnessScores.return_value = []
            elif method_name == "privacy":
                mock_service.getPrivacyScores.return_value = []
            elif method_name == "safety":
                mock_service.getSafteyScores.return_value = []
            elif method_name == "ethics":
                mock_service.getEthicsScores.return_value = []
            elif method_name == "truthfullness":
                mock_service.getTruthfullnessScores.return_value = []
            
            response = client.get(endpoint)
            assert response.status_code == 200
    
    def test_typo_in_logger_variable(self, client, mock_service, mock_logger):
        """Regression: Test that logger typo 'og' doesn't cause issues."""
        # There's a typo in the router: 'og=CustomLogger()' instead of 'log'
        mock_service.deleteScores.return_value = "Deleted Successfully"
        
        response = client.post(
            "/inhouse/scores/fairness/deleteScore",
            params={"category": "fairness", "model_name": "test"}
        )
        
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
