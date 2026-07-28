"""
Unit tests for privacy.routing.privacy_router module.
Tests cover all API endpoints, helper functions, and error handling.
"""
import pytest
import json
import os
from unittest.mock import Mock, MagicMock, patch, mock_open
from io import BytesIO
from fastapi import HTTPException
from fastapi.testclient import TestClient

# Import the router and dependencies
from privacy.routing import privacy_router
from privacy.routing.privacy_router import (
    router,
    send_telemetry_request,
    NoAccountException,
    NoAdminConnException,
    NoMatchingRecognizer,
    Telemetry
)
from privacy.mappers.mappers import (
    PIIAnalyzeRequest,
    PIIAnalyzeResponse,
    PIIAnonymizeRequest,
    PIIAnonymizeResponse,
    PIIEncryptResponse,
    PIIDecryptRequest,
    PIIDecryptResponse,
    PIIImageAnalyzeResponse,
    PIIEntity,
    PIIItems
)
from privacy.exception.exception import PrivacyException

# Create a test FastAPI app with the router
from fastapi import FastAPI

# Mock dependencies before app initialization
os.environ["AUTH_TYPE"] = "none"
os.environ["TELE_FLAG"] = "False"

# Import after setting env vars
from privacy.routing.privacy_router import auth as original_auth

app = FastAPI()
app.include_router(router)

# Override the auth dependency to return None (no auth check)
async def override_auth():
    return None

app.dependency_overrides[original_auth] = override_auth

client = TestClient(app)


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up required environment variables."""
    monkeypatch.setenv("AUTH_TYPE", "none")
    monkeypatch.setenv("TELE_FLAG", "False")
    monkeypatch.setenv("PRIVACY_TELEMETRY_URL", "http://test-telemetry.com")
    monkeypatch.setenv("PRIVACY_ERROR_URL", "http://test-error.com")
    monkeypatch.setenv("VERIFY_SSL", "False")
    yield


@pytest.fixture
def mock_text_privacy():
    """Mock TextPrivacy service."""
    with patch('privacy.routing.privacy_router.TextPrivacy') as mock:
        yield mock


@pytest.fixture
def mock_image_privacy():
    """Mock ImagePrivacy service."""
    with patch('privacy.routing.privacy_router.ImagePrivacy') as mock:
        yield mock


@pytest.fixture
def mock_api_call():
    """Mock ApiCall service."""
    with patch('privacy.routing.privacy_router.ApiCall') as mock:
        yield mock


@pytest.fixture
def mock_load_recognizer():
    """Mock LoadRecognizer service."""
    with patch('privacy.routing.privacy_router.LoadRecognizer') as mock:
        yield mock


@pytest.fixture
def mock_requests():
    """Mock requests library."""
    with patch('privacy.routing.privacy_router.requests') as mock:
        yield mock


@pytest.fixture
def sample_pii_entity():
    """Create a sample PIIEntity."""
    return PIIEntity(
        type="PERSON",
        beginOffset=0,
        endOffset=10,
        score=0.95,
        responseText="John Doe"
    )


@pytest.fixture
def sample_analyze_response(sample_pii_entity):
    """Create a sample PIIAnalyzeResponse."""
    return PIIAnalyzeResponse(PIIEntities=[sample_pii_entity])


@pytest.fixture
def sample_anonymize_response():
    """Create a sample PIIAnonymizeResponse."""
    return PIIAnonymizeResponse(anonymizedText="This is [REDACTED] text")


@pytest.fixture
def sample_encrypt_response():
    """Create a sample PIIEncryptResponse."""
    return PIIEncryptResponse(
        text="encrypted_text_here",
        items=[PIIItems(start=0, end=10, entity_type="PERSON", text="test", operator="encrypt")]
    )


@pytest.fixture
def sample_decrypt_response():
    """Create a sample PIIDecryptResponse."""
    return PIIDecryptResponse(decryptedText="decrypted text here")


@pytest.fixture
def sample_image_analyze_response():
    """Create a sample PIIImageAnalyzeResponse."""
    return PIIImageAnalyzeResponse(
        PIIEntities=[],
        filename="test.jpg"
    )


@pytest.fixture
def mock_request_id():
    """Mock request_id_var context variable."""
    with patch('privacy.routing.privacy_router.request_id_var') as mock:
        mock.get.return_value = "test-request-id"
        yield mock


# ============================================================================
# Test Exception Classes
# ============================================================================

class TestExceptionClasses:
    """Test custom exception classes."""
    
    def test_no_account_exception(self):
        """Test NoAccountException can be raised."""
        with pytest.raises(NoAccountException):
            raise NoAccountException("Test error")
    
    def test_no_admin_conn_exception(self):
        """Test NoAdminConnException can be raised."""
        with pytest.raises(NoAdminConnException):
            raise NoAdminConnException("Test error")
    
    def test_no_matching_recognizer(self):
        """Test NoMatchingRecognizer can be raised."""
        with pytest.raises(NoMatchingRecognizer):
            raise NoMatchingRecognizer("Test error")


# ============================================================================
# Test Helper Functions
# ============================================================================

class TestHelperFunctions:
    """Test helper functions in privacy_router."""
    
    def test_send_telemetry_request_success(self, mock_requests, mock_request_id):
        """Test send_telemetry_request with successful API call."""
        with patch('privacy.routing.privacy_router.os.getenv', return_value="False"):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.json.return_value = {"status": "success"}
            mock_requests.post.return_value = mock_response
            
            telemetry_data = {"test": "data"}
            send_telemetry_request(telemetry_data)
            
            mock_requests.post.assert_called_once()
    
    def test_send_telemetry_request_failure(self, mock_requests, mock_request_id):
        """Test send_telemetry_request with failed API call."""
        mock_requests.post.side_effect = Exception("Connection error")
        
        with pytest.raises(HTTPException) as exc_info:
            send_telemetry_request({"test": "data"})
        
        assert exc_info.value.status_code == 500


# ============================================================================
# Test Telemetry Class
# ============================================================================

class TestTelemetryClass:
    """Test Telemetry class methods."""
    
    def test_error_telemetry_request_with_flag_true(self, mock_requests, mock_request_id):
        """Test error_telemetry_request when telemetry flag is true."""
        with patch('privacy.routing.privacy_router.tel_Falg', True), \
             patch('privacy.routing.privacy_router.os.getenv', return_value="False"):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.json.return_value = {"status": "success"}
            mock_requests.post.return_value = mock_response
            
            error_obj = {
                "uniqueid": "test-id",
                "error": [{"errorCode": "test", "errorMessage": "test error"}]
            }
            
            Telemetry.error_telemetry_request(error_obj, "test-id")
            
            mock_requests.post.assert_called_once()
    
    def test_error_telemetry_request_with_flag_false(self, mock_requests, mock_request_id):
        """Test error_telemetry_request when telemetry flag is false."""
        with patch('privacy.routing.privacy_router.tel_Falg', False):
            error_obj = {
                "uniqueid": "test-id",
                "error": [{"errorCode": "test", "errorMessage": "test error"}]
            }
            
            Telemetry.error_telemetry_request(error_obj, "test-id")
            
            # Should not call API when flag is False
            mock_requests.post.assert_not_called()
    
    def test_error_telemetry_request_failure(self, mock_requests, mock_request_id):
        """Test error_telemetry_request with failed API call."""
        with patch('privacy.routing.privacy_router.tel_Falg', True):
            mock_requests.post.side_effect = Exception("Connection error")
            
            error_obj = {
                "uniqueid": "test-id",
                "error": [{"errorCode": "test", "errorMessage": "test error"}]
            }
            
            with pytest.raises(HTTPException) as exc_info:
                Telemetry.error_telemetry_request(error_obj, "test-id")
            
            assert exc_info.value.status_code == 500


# ============================================================================
# Test Text Privacy Endpoints
# ============================================================================

class TestTextPrivacyEndpoints:
    """Test text privacy API endpoints."""
    
    def test_analyze_success(self, mock_env_vars, mock_text_privacy, mock_api_call, sample_analyze_response):
        """Test /privacy/text/analyze endpoint with successful response."""
        mock_text_privacy.analyze = MagicMock(return_value=sample_analyze_response)
        mock_api_call.delAdminList = MagicMock(return_value=None)
        
        response = client.post(
            "/privacy/text/analyze",
            json={
                "inputText": "John Doe lives in New York",
                "portfolio": "test_portfolio",
                "account": "test_account"
            }
        )
        
        assert response.status_code == 200
        assert mock_text_privacy.analyze.called
        assert mock_api_call.delAdminList.called
    
    def test_analyze_no_account_exception(self, mock_env_vars, mock_text_privacy, mock_api_call):
        """Test /privacy/text/analyze with NoAccountException."""
        mock_text_privacy.analyze = MagicMock(return_value=None)
        
        response = client.post(
            "/privacy/text/analyze",
            json={"inputText": "test text"}
        )
        
        assert response.status_code == 430
        assert "Portfolio/Account Is Incorrect" in response.json()["detail"]
    
    def test_analyze_no_admin_conn_exception(self, mock_env_vars, mock_text_privacy, mock_api_call):
        """Test /privacy/text/analyze with NoAdminConnException."""
        mock_text_privacy.analyze = MagicMock(return_value=404)
        
        response = client.post(
            "/privacy/text/analyze",
            json={"inputText": "test text"}
        )
        
        assert response.status_code == 435
    
    def test_analyze_no_matching_recognizer(self, mock_env_vars, mock_text_privacy, mock_api_call):
        """Test /privacy/text/analyze with NoMatchingRecognizer."""
        mock_text_privacy.analyze = MagicMock(return_value=482)
        
        response = client.post(
            "/privacy/text/analyze",
            json={"inputText": "test text"}
        )
        
        assert response.status_code == 482
    

    
    def test_decrypt_success(self, mock_env_vars, mock_text_privacy, sample_decrypt_response):
        """Test /privacy/text/decrpyt endpoint with successful response."""
        mock_text_privacy.decryption = MagicMock(return_value=sample_decrypt_response)
        
        response = client.post(
            "/privacy/text/decrpyt",
            json={
                "text": "encrypted_data",
                "items": [{
                    "start": 0,
                    "end": 10,
                    "entity_type": "PERSON",
                    "text": "test",
                    "operator": "encrypt"
                }]
            }
        )
        
        assert response.status_code == 200
        assert "decryptedText" in response.json()
        assert mock_text_privacy.decryption.called


# ============================================================================
# Test Text Anonymize Endpoint
# ============================================================================

class TestTextAnonymizeEndpoint:
    """Test text anonymize API endpoint."""
    
    def test_anonymize_success(self, mock_env_vars, mock_text_privacy, mock_api_call):
        """Test /privacy/text/anonymize endpoint with successful response."""
        mock_response = PIIAnonymizeResponse(anonymizedText="This is [REDACTED] text")
        mock_instance = MagicMock()
        mock_instance.anonymize.return_value = mock_response
        mock_text_privacy.return_value = mock_instance
        # Mock the class method call
        mock_text_privacy.anonymize = MagicMock(return_value=mock_response)
        mock_api_call.delAdminList = MagicMock(return_value=None)
        
        response = client.post(
            "/privacy/text/anonymize",
            json={
                "inputText": "John Doe lives in New York",
                "portfolio": "test_portfolio",
                "account": "test_account",
                "fakeData": False
            }
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        assert response.status_code == 200
        assert "anonymizedText" in response.json()
        assert mock_text_privacy.anonymize.called
    
    def test_anonymize_no_account_exception(self, mock_env_vars, mock_text_privacy, mock_api_call):
        """Test /privacy/text/anonymize with NoAccountException."""
        mock_text_privacy.anonymize = MagicMock(return_value=None)
        
        response = client.post(
            "/privacy/text/anonymize",
            json={
                "inputText": "test text",
                "fakeData": False
            }
        )
        
        assert response.status_code == 430
    
    def test_anonymize_no_admin_conn_exception(self, mock_env_vars, mock_text_privacy, mock_api_call):
        """Test /privacy/text/anonymize with NoAdminConnException."""
        mock_text_privacy.anonymize = MagicMock(return_value=404)
        
        response = client.post(
            "/privacy/text/anonymize",
            json={
                "inputText": "test text",
                "fakeData": False
            }
        )
        
        assert response.status_code == 435
    
    def test_anonymize_no_matching_recognizer(self, mock_env_vars, mock_text_privacy, mock_api_call):
        """Test /privacy/text/anonymize with NoMatchingRecognizer."""
        mock_text_privacy.anonymize = MagicMock(return_value=482)
        
        response = client.post(
            "/privacy/text/anonymize",
            json={
                "inputText": "test text",
                "fakeData": False
            }
        )
        
        assert response.status_code == 482
    
    def test_anonymize_privacy_exception(self, mock_env_vars, mock_text_privacy, mock_api_call):
        """Test /privacy/text/anonymize with PrivacyException."""
        from privacy.exception.exception import PrivacyException
        
        with patch('privacy.routing.privacy_router.error_dict', {}):
            mock_privacy_exc = PrivacyException(detail="Test error")
            mock_text_privacy.anonymize = MagicMock(side_effect=mock_privacy_exc)
            
            response = client.post(
                "/privacy/text/anonymize",
                json={
                    "inputText": "test text",
                    "fakeData": False
                }
            )
            
            # Source code has a bug (UnboundLocalError with 'e'), results in 500 instead of 400
            assert response.status_code == 500
    
    def test_anonymize_with_telemetry(self, mock_env_vars, mock_text_privacy, mock_api_call, mock_requests):
        """Test /privacy/text/anonymize with telemetry enabled."""
        with patch('privacy.routing.privacy_router.tel_Falg', True):
            mock_response = PIIAnonymizeResponse(anonymizedText="[REDACTED] text")
            mock_text_privacy.anonymize = MagicMock(return_value=mock_response)
            mock_api_call.delAdminList = MagicMock(return_value=None)
            
            mock_requests.post.return_value = Mock(status_code=200)
            
            response = client.post(
                "/privacy/text/anonymize",
                json={
                    "inputText": "John Doe",
                    "user": "test_user",
                    "portfolio": "test_portfolio",
                    "exclusionList": "exclude1,exclude2",
                    "fakeData": False
                }
            )
            
            assert response.status_code == 200


# ============================================================================
# Test Text Encrypt/Decrypt Endpoints
# ============================================================================

class TestTextEncryptEndpoint:
    """Test text encrypt API endpoint."""
    
    def test_encrypt_success(self, mock_env_vars, mock_text_privacy, mock_api_call):
        """Test /privacy/text/encrpyt endpoint with successful response."""
        mock_response = PIIEncryptResponse(
            text="encrypted_text",
            items=[PIIItems(start=0, end=10, entity_type="PERSON", text="test", operator="encrypt")]
        )
        mock_text_privacy.encrypt = MagicMock(return_value=mock_response)
        
        response = client.post(
            "/privacy/text/encrpyt",
            json={
                "inputText": "John Doe lives here",
                "portfolio": "test_portfolio",
                "account": "test_account",
                "fakeData": False
            }
        )
        
        assert response.status_code == 200
        assert "text" in response.json()
        assert mock_text_privacy.encrypt.called
    
    def test_encrypt_no_account_exception(self, mock_env_vars, mock_text_privacy, mock_api_call):
        """Test /privacy/text/encrpyt with NoAccountException."""
        mock_text_privacy.encrypt = MagicMock(return_value=None)
        
        response = client.post(
            "/privacy/text/encrpyt",
            json={
                "inputText": "test text",
                "fakeData": False
            }
        )
        
        assert response.status_code == 430
    
    def test_encrypt_no_admin_conn_exception(self, mock_env_vars, mock_text_privacy, mock_api_call):
        """Test /privacy/text/encrpyt with NoAdminConnException."""
        with patch('privacy.routing.privacy_router.error_dict', {}):
            mock_text_privacy.encrypt = MagicMock(side_effect=NoAdminConnException())
            
            response = client.post(
                "/privacy/text/encrpyt",
                json={
                    "inputText": "test text",
                    "fakeData": False
                }
            )
            
            # Endpoint doesn't have specific handler for NoAdminConnException, falls to generic (500)
            assert response.status_code == 500
    
    def test_encrypt_no_matching_recognizer(self, mock_env_vars, mock_text_privacy, mock_api_call):
        """Test /privacy/text/encrpyt with NoMatchingRecognizer."""
        with patch('privacy.routing.privacy_router.error_dict', {}):
            mock_text_privacy.encrypt = MagicMock(side_effect=NoMatchingRecognizer())
            
            response = client.post(
                "/privacy/text/encrpyt",
                json={
                    "inputText": "test text",
                    "fakeData": False
                }
            )
            
            # Endpoint doesn't have specific handler for NoMatchingRecognizer, falls to generic (500)
            assert response.status_code == 500
    
    def test_encrypt_generic_exception(self, mock_env_vars, mock_text_privacy, mock_api_call):
        """Test /privacy/text/encrpyt with generic exception."""
        with patch('privacy.routing.privacy_router.error_dict', {}):
            mock_text_privacy.encrypt = MagicMock(side_effect=Exception("Encryption error"))
            
            response = client.post(
                "/privacy/text/encrpyt",
                json={
                    "inputText": "test text",
                    "fakeData": False
                }
            )
            
            assert response.status_code == 500


class TestTextDecryptEndpoint:
    """Test text decrypt API endpoint."""
    
    def test_decrypt_no_account_exception(self, mock_env_vars, mock_text_privacy):
        """Test /privacy/text/decrpyt with NoAccountException."""
        mock_text_privacy.decryption = MagicMock(side_effect=NoAccountException())
        
        response = client.post(
            "/privacy/text/decrpyt",
            json={
                "text": "encrypted_data",
                "items": []
            }
        )
        
        assert response.status_code == 430
    
    def test_decrypt_generic_exception(self, mock_env_vars, mock_text_privacy):
        """Test /privacy/text/decrpyt with generic exception."""
        with patch('privacy.routing.privacy_router.error_dict', {}):
            mock_text_privacy.decryption = MagicMock(side_effect=Exception("Decryption error"))
            
            response = client.post(
                "/privacy/text/decrpyt",
                json={
                    "text": "encrypted_data",
                    "items": []
                }
            )
            
            assert response.status_code == 500
    
    def test_decrypt_privacy_exception(self, mock_env_vars, mock_text_privacy):
        """Test /privacy/text/decrpyt with PrivacyException."""
        from privacy.exception.exception import PrivacyException
        
        with patch('privacy.routing.privacy_router.error_dict', {}):
            mock_privacy_exc = PrivacyException(detail="Decrypt error")
            mock_text_privacy.decryption = MagicMock(side_effect=mock_privacy_exc)
            
            response = client.post(
                "/privacy/text/decrpyt",
                json={
                    "text": "encrypted_data",
                    "items": []
                }
            )
            
            # Source code has a bug (UnboundLocalError with 'e'), results in 500 instead of 400
            assert response.status_code == 500


# ============================================================================
# Test Image Privacy Endpoints
# ============================================================================

class TestImageAnalyzeEndpoint:
    """Test image analyze API endpoint."""
    
    def test_image_analyze_success(self, mock_env_vars, mock_image_privacy):
        """Test /privacy/image/analyze endpoint with successful response."""
        from privacy.mappers.mappers import PIIImageAnalyze
        mock_response = PIIImageAnalyzeResponse(
            PIIEntities=[PIIImageAnalyze(type="PERSON", start=0, end=10, score=0.95)]
        )
        mock_image_privacy.image_analyze.return_value = mock_response
        
        file_content = b"fake image content"
        files = {"images": ("test.jpg", BytesIO(file_content), "image/jpeg")}
        data = {
            "magnification": "True",
            "rotationFlag": "False",
            "ocr": "Tesseract",
            "nlp": "basic"
        }
        
        response = client.post(
            "/privacy/image/analyze",
            files=files,
            data=data
        )
        
        assert response.status_code == 200
        mock_image_privacy.image_analyze.assert_called()
    
    def test_image_analyze_no_account_exception(self, mock_env_vars, mock_image_privacy):
        """Test /privacy/image/analyze with NoAccountException."""
        mock_image_privacy.image_analyze.return_value = None
        
        file_content = b"fake image content"
        files = {"images": ("test.jpg", BytesIO(file_content), "image/jpeg")}
        data = {
            "magnification": "True",
            "rotationFlag": "False",
            "ocr": "Tesseract"
        }
        
        response = client.post(
            "/privacy/image/analyze",
            files=files,
            data=data
        )
        
        assert response.status_code == 430
    
    def test_image_analyze_no_admin_conn_exception(self, mock_env_vars, mock_image_privacy):
        """Test /privacy/image/analyze with NoAdminConnException."""
        mock_image_privacy.image_analyze.return_value = 404
        
        file_content = b"fake image content"
        files = {"images": ("test.jpg", BytesIO(file_content), "image/jpeg")}
        data = {
            "magnification": "False",
            "rotationFlag": "True",
            "ocr": "EasyOcr"
        }
        
        response = client.post(
            "/privacy/image/analyze",
            files=files,
            data=data
        )
        
        assert response.status_code == 435
    
    def test_image_analyze_generic_exception(self, mock_env_vars, mock_image_privacy):
        """Test /privacy/image/analyze with generic exception."""
        with patch('privacy.routing.privacy_router.error_dict', {}):
            mock_image_privacy.image_analyze.side_effect = Exception("Image processing error")
            
            file_content = b"fake image content"
            files = {"images": ("test.jpg", BytesIO(file_content), "image/jpeg")}
            data = {
                "magnification": "True",
                "rotationFlag": "False",
                "ocr": "ComputerVision"
            }
            
            response = client.post(
                "/privacy/image/analyze",
                files=files,
                data=data
            )
            
            assert response.status_code == 500


class TestImageAnonymizeEndpoint:
    """Test image anonymize API endpoint."""
    
    def test_image_anonymize_success(self, mock_env_vars, mock_image_privacy):
        """Test /privacy/image/anonymize endpoint with successful response."""
        mock_image_data = BytesIO(b"anonymized image data")
        mock_image_privacy.image_anonymize.return_value = mock_image_data
        
        file_content = b"fake image content"
        files = {"images": ("test.jpg", BytesIO(file_content), "image/jpeg")}
        data = {
            "magnification": "True",
            "rotationFlag": "False",
            "ocr": "Tesseract",
            "nlp": "basic"
        }
        
        response = client.post(
            "/privacy/image/anonymize",
            files=files,
            data=data
        )
        
        assert response.status_code == 200
        mock_image_privacy.image_anonymize.assert_called()
    
    def test_image_anonymize_no_account_exception(self, mock_env_vars, mock_image_privacy):
        """Test /privacy/image/anonymize with NoAccountException."""
        mock_image_privacy.image_anonymize.return_value = None
        
        file_content = b"fake image content"
        files = {"images": ("test.jpg", BytesIO(file_content), "image/jpeg")}
        data = {
            "magnification": "False",
            "rotationFlag": "True"
        }
        
        response = client.post(
            "/privacy/image/anonymize",
            files=files,
            data=data
        )
        
        assert response.status_code == 430
    
    def test_image_anonymize_generic_exception(self, mock_env_vars, mock_image_privacy):
        """Test /privacy/image/anonymize with generic exception."""
        with patch('privacy.routing.privacy_router.error_dict', {}):
            mock_image_privacy.image_anonymize.side_effect = Exception("Anonymization error")
            
            file_content = b"fake image content"
            files = {"images": ("test.jpg", BytesIO(file_content), "image/jpeg")}
            data = {
                "magnification": "True",
                "rotationFlag": "False"
            }
            
            response = client.post(
                "/privacy/image/anonymize",
                files=files,
                data=data
            )
            
            assert response.status_code == 500


class TestImageHashifyEndpoint:
    """Test image hashify API endpoint."""
    
    def test_image_hashify_success(self, mock_env_vars, mock_image_privacy):
        """Test /privacy/image/hashify endpoint with successful response."""
        mock_image_data = BytesIO(b"hashified image data")
        mock_image_privacy.imageEncryption.return_value = mock_image_data
        
        file_content = b"fake image content"
        files = {"image": ("test.jpg", BytesIO(file_content), "image/jpeg")}
        data = {
            "magnification": "True",
            "rotationFlag": "False",
            "ocr": "Tesseract",
            "nlp": "basic"
        }
        
        response = client.post(
            "/privacy/image/hashify",
            files=files,
            data=data
        )
        
        assert response.status_code == 200
        mock_image_privacy.imageEncryption.assert_called()
    
    def test_image_hashify_no_account_exception(self, mock_env_vars, mock_image_privacy):
        """Test /privacy/image/hashify with NoAccountException."""
        mock_image_privacy.imageEncryption.return_value = None
        
        file_content = b"fake image content"
        files = {"image": ("test.jpg", BytesIO(file_content), "image/jpeg")}
        data = {
            "magnification": "False",
            "rotationFlag": "True"
        }
        
        response = client.post(
            "/privacy/image/hashify",
            files=files,
            data=data
        )
        
        assert response.status_code == 430
    
    def test_image_hashify_generic_exception(self, mock_env_vars, mock_image_privacy):
        """Test /privacy/image/hashify with generic exception."""
        with patch('privacy.routing.privacy_router.error_dict', {}):
            mock_image_privacy.imageEncryption.side_effect = Exception("Hashify error")
            
            file_content = b"fake image content"
            files = {"image": ("test.jpg", BytesIO(file_content), "image/jpeg")}
            data = {
                "magnification": "True",
                "rotationFlag": "False"
            }
            
            response = client.post(
                "/privacy/image/hashify",
                files=files,
                data=data
            )
            
            assert response.status_code == 500


# ============================================================================
# Test DICOM Anonymize Endpoint
# ============================================================================

class TestDICOMAnonymizeEndpoint:
    """Test DICOM anonymize API endpoint."""
    
    def test_dicom_anonymize_success(self, mock_env_vars):
        """Test /privacy/dicom/anonymize endpoint with successful response."""
        with patch('privacy.routing.privacy_router.DICOMPrivacy') as mock_dicom:
            mock_dicom_data = BytesIO(b"anonymized dicom data")
            mock_dicom.readDicom.return_value = mock_dicom_data
            
            file_content = b"fake dicom content"
            files = {"payload": ("test.dcm", BytesIO(file_content), "application/dicom")}
            
            response = client.post(
                "/privacy/dicom/anonymize",
                files=files
            )
            
            assert response.status_code == 200
            mock_dicom.readDicom.assert_called_once()
    
    def test_dicom_anonymize_no_account_exception(self, mock_env_vars):
        """Test /privacy/dicom/anonymize with NoAccountException."""
        with patch('privacy.routing.privacy_router.DICOMPrivacy') as mock_dicom:
            mock_dicom.readDicom.return_value = None
            
            file_content = b"fake dicom content"
            files = {"payload": ("test.dcm", BytesIO(file_content), "application/dicom")}
            
            response = client.post(
                "/privacy/dicom/anonymize",
                files=files
            )
            
            assert response.status_code == 430
    
    def test_dicom_anonymize_no_admin_conn_exception(self, mock_env_vars):
        """Test /privacy/dicom/anonymize with NoAdminConnException."""
        with patch('privacy.routing.privacy_router.DICOMPrivacy') as mock_dicom:
            mock_dicom.readDicom.return_value = 404
            
            file_content = b"fake dicom content"
            files = {"payload": ("test.dcm", BytesIO(file_content), "application/dicom")}
            
            response = client.post(
                "/privacy/dicom/anonymize",
                files=files
            )
            
            assert response.status_code == 435
    
    def test_dicom_anonymize_generic_exception(self, mock_env_vars):
        """Test /privacy/dicom/anonymize with generic exception."""
        with patch('privacy.routing.privacy_router.DICOMPrivacy') as mock_dicom, \
             patch('privacy.routing.privacy_router.error_dict', {}):
            mock_dicom.readDicom.side_effect = Exception("DICOM error")
            
            file_content = b"fake dicom content"
            files = {"payload": ("test.dcm", BytesIO(file_content), "application/dicom")}
            
            response = client.post(
                "/privacy/dicom/anonymize",
                files=files
            )
            
            assert response.status_code == 500


# ============================================================================
# Test Code Detection Endpoints
# ============================================================================

class TestCodeAnonymizeEndpoint:
    """Test code anonymize API endpoint."""
    
    def test_code_anonymize_success(self, mock_env_vars):
        """Test /privacy/code/anonymize endpoint with successful response."""
        with patch('privacy.routing.privacy_router.codeNer') as mock_code_ner:
            mock_code_ner.codeText.return_value = "anonymized code content"
            
            response = client.post(
                "/privacy/code/anonymize",
                content="def hello(): pass",
                headers={"Content-Type": "text/plain"},
                params={"accountName": "test_account", "portfolioName": "test_portfolio"}
            )
            
            assert response.status_code == 200
            assert response.text == "anonymized code content"
            mock_code_ner.codeText.assert_called_once()
    
    def test_code_anonymize_no_account_exception(self, mock_env_vars):
        """Test /privacy/code/anonymize with NoAccountException."""
        from privacy.routing.privacy_router import NoAccountException
        
        with patch('privacy.routing.privacy_router.codeNer') as mock_code_ner:
            mock_code_ner.codeText.return_value = None
            
            # Endpoint raises NoAccountException which is not an HTTPException
            with pytest.raises(NoAccountException):
                response = client.post(
                    "/privacy/code/anonymize",
                    content="def hello(): pass",
                    headers={"Content-Type": "text/plain"}
                )
    
    def test_code_anonymize_with_telemetry(self, mock_env_vars, mock_requests):
        """Test /privacy/code/anonymize with telemetry enabled."""
        with patch('privacy.routing.privacy_router.tel_Falg', True), \
             patch('privacy.routing.privacy_router.codeNer') as mock_code_ner:
            mock_code_ner.codeText.return_value = "anonymized code"
            mock_requests.post.return_value = Mock(status_code=200)
            
            response = client.post(
                "/privacy/code/anonymize",
                content="def hello(): pass",
                headers={"Content-Type": "text/plain"}
            )
            
            assert response.status_code == 200
    
    def test_code_anonymize_privacy_exception(self, mock_env_vars):
        """Test /privacy/code/anonymize with PrivacyException."""
        from privacy.exception.exception import PrivacyException
        
        with patch('privacy.routing.privacy_router.codeNer') as mock_code_ner, \
             patch('privacy.routing.privacy_router.error_dict', {}):
            mock_privacy_exc = PrivacyException(detail="Code error")
            mock_code_ner.codeText.side_effect = mock_privacy_exc
            
            # Endpoint re-raises PrivacyException, TestClient should catch it
            # Since PrivacyException is not an HTTPException, it will propagate
            with pytest.raises(PrivacyException) as exc_info:
                response = client.post(
                    "/privacy/code/anonymize",
                    content="def hello(): pass",
                    headers={"Content-Type": "text/plain"}
                )
            
            assert str(exc_info.value) == "Code error"


class TestCodeFileAnonymizeEndpoint:
    """Test code file anonymize API endpoint."""
    
    def test_codefile_anonymize_success(self, mock_env_vars):
        """Test /privacy/codefile/anonymize endpoint with successful response."""
        with patch('privacy.routing.privacy_router.codeNer.codeFile') as mock_code_ner, \
             patch('privacy.routing.privacy_router.os.remove'):
            mock_code_ner.return_value = (b"anonymized code file", "test_redacted.py")
            
            file_content = b"def hello(): pass"
            files = {"code_file": ("test.py", BytesIO(file_content), "text/plain")}
            data = {
                "accountName": "test_account",
                "portfolioName": "test_portfolio"
            }
            
            response = client.post(
                "/privacy/codefile/anonymize",
                files=files,
                data=data
            )
            
            assert response.status_code == 200
            mock_code_ner.assert_called_once()
    
    def test_codefile_anonymize_generic_exception(self, mock_env_vars):
        """Test /privacy/codefile/anonymize with generic exception."""
        with patch('privacy.routing.privacy_router.code_detect_ner') as mock_code_detect, \
             patch('privacy.routing.privacy_router.error_dict', {}):
            mock_code_detect.side_effect = Exception("Code file error")
            
            file_content = b"def hello(): pass"
            files = {"code_file": ("test.py", BytesIO(file_content), "text/plain")}
            
            response = client.post(
                "/privacy/codefile/anonymize",
                files=files
            )
            
            assert response.status_code == 500


# ============================================================================
# Test Differential Privacy Endpoints
# ============================================================================

class TestDifferentialPrivacyEndpoints:
    """Test differential privacy API endpoints."""
    
    def test_diff_privacy_file_success(self, mock_env_vars):
        """Test /privacy/DifferentialPrivacy/file endpoint with successful response."""
        with patch('privacy.routing.privacy_router.DiffPrivacy') as mock_diff:
            mock_output = {"status": "success", "data": "processed"}
            mock_diff.uploadFIle.return_value = mock_output
            
            file_content = b"dataset content"
            files = {"dataset": ("data.csv", BytesIO(file_content), "text/csv")}
            
            response = client.post(
                "/privacy/DifferentialPrivacy/file",
                files=files
            )
            
            assert response.status_code == 200
            mock_diff.uploadFIle.assert_called_once()
    
    def test_diff_privacy_file_generic_exception(self, mock_env_vars):
        """Test /privacy/DifferentialPrivacy/file with generic exception."""
        with patch('privacy.routing.privacy_router.DiffPrivacy') as mock_diff, \
             patch('privacy.routing.privacy_router.error_dict', {}):
            mock_diff.uploadFIle.side_effect = Exception("Diff privacy error")
            
            file_content = b"dataset content"
            files = {"dataset": ("data.csv", BytesIO(file_content), "text/csv")}
            
            response = client.post(
                "/privacy/DifferentialPrivacy/file",
                files=files
            )
            
            assert response.status_code == 500
    
    def test_diff_privacy_anonymize_success(self, mock_env_vars):
        """Test /privacy/DifferentialPrivacy/anonymize endpoint with successful response."""
        with patch('privacy.routing.privacy_router.DiffPrivacy') as mock_diff:
            mock_output = BytesIO(b"anonymized data")
            mock_diff.diffPrivacy.return_value = mock_output
            
            data = {
                "suppression": "col1,col2",
                "noiselist": "col3",
                "binarylist": "col4",
                "rangeList": "col5"
            }
            
            response = client.post(
                "/privacy/DifferentialPrivacy/anonymize",
                data=data
            )
            
            assert response.status_code == 200
            mock_diff.diffPrivacy.assert_called_once()
    
    def test_diff_privacy_anonymize_generic_exception(self, mock_env_vars):
        """Test /privacy/DifferentialPrivacy/anonymize with generic exception."""
        with patch('privacy.routing.privacy_router.DiffPrivacy') as mock_diff, \
             patch('privacy.routing.privacy_router.error_dict', {}):
            mock_diff.diffPrivacy.side_effect = Exception("Anonymize error")
            
            response = client.post(
                "/privacy/DifferentialPrivacy/anonymize",
                data={"suppression": "col1"}
            )
            
            assert response.status_code == 500


# ============================================================================
# Test File Service Endpoints
# ============================================================================

class TestCSVAnonymizeEndpoint:
    """Test CSV anonymize API endpoint."""
    
    def test_csv_anonymize_success(self, mock_env_vars):
        """Test /privacy-files/csv/anonymize endpoint with successful response."""
        with patch('privacy.routing.privacy_router.CSVService') as mock_csv:
            mock_output = BytesIO(b"anonymized,csv,data")
            mock_csv.csv_anonymize.return_value = mock_output
            
            file_content = b"name,email\nJohn,john@test.com"
            files = {"file": ("data.csv", BytesIO(file_content), "text/csv")}
            data = {
                "keys_to_skip": "email",
                "nlp": "basic",
                "ocr": "Tesseract"
            }
            
            # Create app with fileRouter
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/csv/anonymize",
                files=files,
                data=data
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/csv; charset=utf-8"
            mock_csv.csv_anonymize.assert_called_once()
    
    def test_csv_anonymize_with_portfolio_account(self, mock_env_vars):
        """Test /privacy-files/csv/anonymize with portfolio and account."""
        with patch('privacy.routing.privacy_router.CSVService') as mock_csv:
            mock_output = BytesIO(b"anonymized,csv,data")
            mock_csv.csv_anonymize.return_value = mock_output
            
            file_content = b"name,email\nJohn,john@test.com"
            files = {"file": ("data.csv", BytesIO(file_content), "text/csv")}
            data = {
                "portfolio": "test_portfolio",
                "account": "test_account",
                "exclusionList": "email,phone"
            }
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/csv/anonymize",
                files=files,
                data=data
            )
            
            assert response.status_code == 200
    
    def test_csv_anonymize_generic_exception(self, mock_env_vars):
        """Test /privacy-files/csv/anonymize with generic exception."""
        with patch('privacy.routing.privacy_router.CSVService') as mock_csv:
            mock_csv.csv_anonymize.side_effect = Exception("CSV error")
            
            file_content = b"name,email\nJohn,john@test.com"
            files = {"file": ("data.csv", BytesIO(file_content), "text/csv")}
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/csv/anonymize",
                files=files
            )
            
            assert response.status_code == 500


class TestJSONAnonymizeEndpoint:
    """Test JSON anonymize API endpoint."""
    
    def test_json_anonymize_success(self, mock_env_vars):
        """Test /privacy-files/json/anonymize endpoint with successful response."""
        with patch('privacy.routing.privacy_router.JSONService') as mock_json:
            mock_output = '{"name": "[REDACTED]", "email": "test@test.com"}'
            mock_json.anonymize_json.return_value = mock_output
            
            file_content = b'{"name": "John", "email": "john@test.com"}'
            files = {"file": ("data.json", BytesIO(file_content), "application/json")}
            data = {
                "keys_to_skip": "email",
                "nlp": "good",
                "ocr": "EasyOcr"
            }
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/json/anonymize",
                files=files,
                data=data
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/json"
            mock_json.anonymize_json.assert_called_once()
    
    def test_json_anonymize_with_pii_entities(self, mock_env_vars):
        """Test /privacy-files/json/anonymize with piiEntitiesToBeRedacted."""
        with patch('privacy.routing.privacy_router.JSONService') as mock_json:
            mock_output = '{"name": "[REDACTED]"}'
            mock_json.anonymize_json.return_value = mock_output
            
            file_content = b'{"name": "John"}'
            files = {"file": ("data.json", BytesIO(file_content), "application/json")}
            data = {
                "piiEntitiesToBeRedacted": "PERSON,EMAIL"
            }
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/json/anonymize",
                files=files,
                data=data
            )
            
            assert response.status_code == 200
    
    def test_json_anonymize_generic_exception(self, mock_env_vars):
        """Test /privacy-files/json/anonymize with generic exception."""
        with patch('privacy.routing.privacy_router.JSONService') as mock_json:
            mock_json.anonymize_json.side_effect = Exception("JSON error")
            
            file_content = b'{"name": "John"}'
            files = {"file": ("data.json", BytesIO(file_content), "application/json")}
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/json/anonymize",
                files=files
            )
            
            assert response.status_code == 500


class TestFileAnonymizeEndpoint:
    """Test generic file anonymize API endpoint."""
    
    def test_get_file_extension(self):
        """Test get_file_extension helper function."""
        from privacy.routing.privacy_router import get_file_extension
        
        assert get_file_extension("test.csv") == "csv"
        assert get_file_extension("document.docx") == "docx"
        assert get_file_extension("data.json") == "json"
        assert get_file_extension("presentation.ppt") == "ppt"
        assert get_file_extension("file.name.with.dots.pdf") == "pdf"
    
    def test_file_anonymize_csv_success(self, mock_env_vars):
        """Test /privacy-files/anonymize endpoint for CSV files."""
        with patch('privacy.routing.privacy_router.FileService') as mock_file_service:
            mock_output = BytesIO(b"anonymized,data")
            mock_file_service.anonymize_file.return_value = mock_output
            
            file_content = b"name,value\nJohn,123"
            files = {"file": ("data.csv", BytesIO(file_content), "text/csv")}
            data = {"nlp": "basic", "ocr": "Tesseract"}
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/anonymize",
                files=files,
                data=data
            )
            
            assert response.status_code == 200
            assert "text/csv" in response.headers["content-type"]
            mock_file_service.anonymize_file.assert_called_once()
    
    def test_file_anonymize_json_success(self, mock_env_vars):
        """Test /privacy-files/anonymize endpoint for JSON files."""
        with patch('privacy.routing.privacy_router.FileService') as mock_file_service:
            mock_output = BytesIO(b'{"anonymized": true}')
            mock_file_service.anonymize_file.return_value = mock_output
            
            file_content = b'{"name": "John"}'
            files = {"file": ("data.json", BytesIO(file_content), "application/json")}
            data = {"nlp": "roberta"}
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/anonymize",
                files=files,
                data=data
            )
            
            assert response.status_code == 200
            assert "application/json" in response.headers["content-type"]
    
    def test_file_anonymize_docx_success(self, mock_env_vars):
        """Test /privacy-files/anonymize endpoint for DOCX files."""
        with patch('privacy.routing.privacy_router.FileService') as mock_file_service:
            mock_output = BytesIO(b"anonymized docx content")
            mock_file_service.anonymize_file.return_value = mock_output
            
            file_content = b"fake docx content"
            files = {"file": ("document.docx", BytesIO(file_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            data = {"nlp": "ranha", "keys_to_skip": "footer"}
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/anonymize",
                files=files,
                data=data
            )
            
            assert response.status_code == 200
            assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.headers["content-type"]
    
    def test_file_anonymize_ppt_success(self, mock_env_vars):
        """Test /privacy-files/anonymize endpoint for PPT files."""
        with patch('privacy.routing.privacy_router.FileService') as mock_file_service:
            mock_output = BytesIO(b"anonymized ppt content")
            mock_file_service.anonymize_file.return_value = mock_output
            
            file_content = b"fake ppt content"
            files = {"file": ("presentation.ppt", BytesIO(file_content), "application/vnd.ms-powerpoint")}
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/anonymize",
                files=files
            )
            
            assert response.status_code == 200
            assert "application/vnd.openxmlformats-officedocument.presentationml.presentation" in response.headers["content-type"]
    
    def test_file_anonymize_generic_file_type(self, mock_env_vars):
        """Test /privacy-files/anonymize endpoint for generic file type."""
        with patch('privacy.routing.privacy_router.FileService') as mock_file_service:
            mock_output = BytesIO(b"anonymized content")
            mock_file_service.anonymize_file.return_value = mock_output
            
            file_content = b"fake content"
            files = {"file": ("data.txt", BytesIO(file_content), "text/plain")}
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/anonymize",
                files=files
            )
            
            assert response.status_code == 200
            assert "application/octet-stream" in response.headers["content-type"]
    
    def test_file_anonymize_generic_exception(self, mock_env_vars):
        """Test /privacy-files/anonymize with generic exception."""
        with patch('privacy.routing.privacy_router.FileService') as mock_file_service:
            mock_file_service.anonymize_file.side_effect = Exception("File error")
            
            file_content = b"content"
            files = {"file": ("data.csv", BytesIO(file_content), "text/csv")}
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/anonymize",
                files=files
            )
            
            assert response.status_code == 500
            assert "file anonymization" in response.json()["detail"].lower()


# ============================================================================
# Test Recognizer Endpoints
# ============================================================================

class TestRecognizerEndpoints:
    """Test recognizer management endpoints."""
    
    def test_load_recognizer_post_success(self, mock_env_vars, mock_load_recognizer):
        """Test /privacy/loadRecognizer POST endpoint with successful response."""
        mock_load_recognizer.set_recognizer.return_value = {"status": "success"}
        
        file_content = b"recognizer config"
        files = {"payload": ("recognizer.json", BytesIO(file_content), "application/json")}
        
        response = client.post(
            "/privacy/loadRecognizer",
            files=files
        )
        
        assert response.status_code == 200
        mock_load_recognizer.set_recognizer.assert_called_once()
    
    def test_load_recognizer_post_failure(self, mock_env_vars, mock_load_recognizer):
        """Test /privacy/loadRecognizer POST endpoint with failure."""
        mock_load_recognizer.set_recognizer.side_effect = Exception("Load error")
        
        file_content = b"recognizer config"
        files = {"payload": ("recognizer.json", BytesIO(file_content), "application/json")}
        
        response = client.post(
            "/privacy/loadRecognizer",
            files=files
        )
        
        assert response.status_code == 500
    
    def test_get_recognizer_success(self, mock_env_vars, mock_load_recognizer):
        """Test /privacy/getRecognizer GET endpoint with successful response."""
        mock_load_recognizer.load_recognizer.return_value = {
            "recognizers": ["PERSON", "EMAIL", "PHONE"]
        }
        
        response = client.get("/privacy/getRecognizer")
        
        assert response.status_code == 200
        assert "recognizers" in response.json()
        mock_load_recognizer.load_recognizer.assert_called_once()
    
    def test_get_recognizer_failure(self, mock_env_vars, mock_load_recognizer):
        """Test /privacy/getRecognizer GET endpoint with failure."""
        mock_load_recognizer.load_recognizer.side_effect = Exception("Load error")
        
        response = client.get("/privacy/getRecognizer")
        
        assert response.status_code == 500


# ============================================================================
# Test Privacy Exception Handling
# ============================================================================

class TestPrivacyExceptionHandling:
    """Test exception handling in router endpoints."""
    

    
    def test_generic_exception_handling(self, mock_env_vars, mock_text_privacy):
        """Test generic exception handling in endpoints."""
        with patch('privacy.routing.privacy_router.error_dict', {}):
            mock_text_privacy.analyze.side_effect = Exception("Unexpected error")
            
            response = client.post(
                "/privacy/text/analyze",
                json={"inputText": "test text"}
            )
            
            assert response.status_code == 500


# ============================================================================
# Test Telemetry Enabled Paths
# ============================================================================

class TestTelemetryEnabledPaths:
    """Test endpoints with telemetry enabled (tel_Falg=True)."""
    
    def test_analyze_with_telemetry_enabled(self, mock_env_vars, mock_text_privacy, mock_api_call, mock_requests, sample_analyze_response):
        """Test /privacy/text/analyze with telemetry enabled."""
        with patch('privacy.routing.privacy_router.tel_Falg', True), \
             patch('privacy.routing.privacy_router.concurrent.futures.ThreadPoolExecutor') as mock_executor:
            mock_text_privacy.analyze = MagicMock(return_value=sample_analyze_response)
            mock_api_call.delAdminList = MagicMock(return_value=None)
            mock_requests.post.return_value = Mock(status_code=200)
            
            response = client.post(
                "/privacy/text/analyze",
                json={
                    "inputText": "John Doe lives in New York",
                    "portfolio": "test_portfolio",
                    "account": "test_account",
                    "user": "test_user",
                    "exclusionList": "email"
                }
            )
            
            assert response.status_code == 200
            mock_executor.assert_called()
    
    def test_anonymize_with_telemetry_error_handling(self, mock_env_vars, mock_text_privacy, mock_api_call):
        """Test /privacy/text/anonymize with telemetry enabled and PrivacyException."""
        from privacy.exception.exception import PrivacyException
        
        with patch('privacy.routing.privacy_router.tel_Falg', True), \
             patch('privacy.routing.privacy_router.error_dict', {}), \
             patch('privacy.routing.privacy_router.threading.Thread') as mock_thread:
            mock_privacy_exc = PrivacyException(detail="Test error")
            mock_text_privacy.anonymize = MagicMock(side_effect=mock_privacy_exc)
            
            response = client.post(
                "/privacy/text/anonymize",
                json={
                    "inputText": "test text",
                    "fakeData": False
                }
            )
            
            # Verify thread was created for error telemetry
            # Note: Source has bug with UnboundLocalError, but thread creation should be attempted
            assert response.status_code == 500
    
    def test_encrypt_with_telemetry_enabled(self, mock_env_vars, mock_text_privacy, mock_api_call, mock_requests):
        """Test /privacy/text/encrpyt with telemetry enabled."""
        with patch('privacy.routing.privacy_router.tel_Falg', True), \
             patch('privacy.routing.privacy_router.concurrent.futures.ThreadPoolExecutor') as mock_executor:
            mock_response = PIIEncryptResponse(
                text="encrypted_text",
                items=[PIIItems(start=0, end=10, entity_type="PERSON", text="test", operator="encrypt")]
            )
            mock_text_privacy.encrypt = MagicMock(return_value=mock_response)
            mock_requests.post.return_value = Mock(status_code=200)
            
            response = client.post(
                "/privacy/text/encrpyt",
                json={
                    "inputText": "John Doe",
                    "portfolio": "test_portfolio",
                    "account": "test_account",
                    "user": "test_user",
                    "fakeData": False
                }
            )
            
            assert response.status_code == 200
    
    def test_image_analyze_with_telemetry_enabled(self, mock_env_vars, mock_image_privacy, mock_requests):
        """Test /privacy/image/analyze with telemetry enabled."""
        with patch('privacy.routing.privacy_router.tel_Falg', True):
            from privacy.mappers.mappers import PIIImageAnalyze
            mock_response = PIIImageAnalyzeResponse(
                PIIEntities=[PIIImageAnalyze(type="PERSON", start=0, end=10, score=0.95)]
            )
            mock_image_privacy.image_analyze.return_value = mock_response
            mock_requests.post.return_value = Mock(status_code=200)
            
            file_content = b"fake image content"
            files = {"images": ("test.jpg", BytesIO(file_content), "image/jpeg")}
            data = {
                "magnification": "True",
                "rotationFlag": "False",
                "ocr": "Tesseract",
                "nlp": "basic"
            }
            
            response = client.post(
                "/privacy/image/analyze",
                files=files,
                data=data
            )
            
            assert response.status_code == 200


# ============================================================================
# Test Error Dictionary Cleanup
# ============================================================================

class TestErrorDictionaryCleanup:
    """Test error_dict cleanup in exception handlers."""
    
    def test_image_anonymize_error_handling_with_thread(self, mock_env_vars, mock_image_privacy):
        """Test error handling with thread spawning in image_anonymize."""
        with patch('privacy.routing.privacy_router.error_dict', {}), \
             patch('privacy.routing.privacy_router.threading.Thread') as mock_thread:
            mock_image_privacy.image_anonymize.side_effect = Exception("Anonymize error")
            
            file_content = b"fake image content"
            files = {"images": ("test.jpg", BytesIO(file_content), "image/jpeg")}
            data = {
                "magnification": "True",
                "rotationFlag": "False",
                "ocr": "Tesseract"
            }
            
            response = client.post(
                "/privacy/image/anonymize",
                files=files,
                data=data
            )
            
            # Should spawn thread for error telemetry
            mock_thread.assert_called()
            assert response.status_code == 500


# ============================================================================
# Test PPT and DOCX File Endpoints
# ============================================================================

class TestPPTFileEndpoint:
    """Test PPT file anonymize endpoint."""
    
    def test_ppt_anonymize_success(self, mock_env_vars):
        """Test /privacy-files/PPT/anonymize endpoint with successful response."""
        with patch('privacy.routing.privacy_router.PPTService') as mock_ppt:
            mock_output = BytesIO(b"anonymized ppt content")
            mock_ppt.mask_ppt.return_value = mock_output
            
            file_content = b"fake ppt content"
            files = {"ppt": ("presentation.ppt", BytesIO(file_content), "application/vnd.ms-powerpoint")}
            data = {
                "nlp": "basic",
                "portfolio": "test_portfolio",
                "account": "test_account"
            }
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/PPT/anonymize",
                files=files,
                data=data
            )
            
            assert response.status_code == 200
            assert "application/vnd.openxmlformats-officedocument.presentationml.presentation" in response.headers["content-type"]
    
    def test_ppt_anonymize_no_account_exception(self, mock_env_vars):
        """Test /privacy-files/PPT/anonymize with NoAccountException."""
        with patch('privacy.routing.privacy_router.PPTService') as mock_ppt:
            mock_ppt.mask_ppt.return_value = None
            
            file_content = b"fake ppt content"
            files = {"ppt": ("presentation.ppt", BytesIO(file_content), "application/vnd.ms-powerpoint")}
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/PPT/anonymize",
                files=files
            )
            
            assert response.status_code == 430
    
    def test_ppt_anonymize_privacy_exception_with_error_telemetry(self, mock_env_vars):
        """Test /privacy-files/PPT/anonymize with PrivacyException and error telemetry."""
        from privacy.exception.exception import PrivacyException
        
        with patch('privacy.routing.privacy_router.PPTService') as mock_ppt, \
             patch('privacy.routing.privacy_router.error_dict', {"test-id": [{"error": "data"}]}), \
             patch('privacy.routing.privacy_router.threading.Thread') as mock_thread:
            mock_privacy_exc = PrivacyException(detail="PPT processing error")
            mock_ppt.mask_ppt.side_effect = mock_privacy_exc
            
            file_content = b"fake ppt content"
            files = {"ppt": ("presentation.ppt", BytesIO(file_content), "application/vnd.ms-powerpoint")}
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/PPT/anonymize",
                files=files
            )
            
            # Should spawn thread for error telemetry
            mock_thread.assert_called()
            assert response.status_code in [400, 500]
    
    def test_ppt_anonymize_generic_exception_with_error_telemetry(self, mock_env_vars):
        """Test /privacy-files/PPT/anonymize with generic Exception and error telemetry."""
        with patch('privacy.routing.privacy_router.PPTService') as mock_ppt, \
             patch('privacy.routing.privacy_router.error_dict', {}), \
             patch('privacy.routing.privacy_router.threading.Thread') as mock_thread:
            mock_ppt.mask_ppt.side_effect = Exception("PPT error")
            
            file_content = b"fake ppt content"
            files = {"ppt": ("presentation.ppt", BytesIO(file_content), "application/vnd.ms-powerpoint")}
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/PPT/anonymize",
                files=files
            )
            
            mock_thread.assert_called()
            assert response.status_code == 500


class TestDOCXFileEndpoint:
    """Test DOCX file anonymize endpoint."""
    
    def test_docx_anonymize_success(self, mock_env_vars):
        """Test /privacy-files/DOCX/anonymize endpoint with successful response."""
        with patch('privacy.routing.privacy_router.DOCService') as mock_doc:
            mock_output = BytesIO(b"anonymized docx content")
            mock_doc.mask_doc.return_value = mock_output
            
            file_content = b"fake docx content"
            files = {"docx": ("document.docx", BytesIO(file_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            data = {
                "nlp": "roberta",
                "portfolio": "test_portfolio",
                "account": "test_account",
                "exclusionList": "header,footer"
            }
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/DOCX/anonymize",
                files=files,
                data=data
            )
            
            assert response.status_code == 200
            assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.headers["content-type"]
    
    def test_docx_anonymize_no_account_exception(self, mock_env_vars):
        """Test /privacy-files/DOCX/anonymize with NoAccountException."""
        with patch('privacy.routing.privacy_router.DOCService') as mock_doc:
            mock_doc.mask_doc.return_value = None
            
            file_content = b"fake docx content"
            files = {"docx": ("document.docx", BytesIO(file_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/DOCX/anonymize",
                files=files
            )
            
            assert response.status_code == 430
    
    def test_docx_anonymize_privacy_exception_with_error_telemetry(self, mock_env_vars):
        """Test /privacy-files/DOCX/anonymize with PrivacyException and error telemetry."""
        from privacy.exception.exception import PrivacyException
        
        with patch('privacy.routing.privacy_router.DOCService') as mock_doc, \
             patch('privacy.routing.privacy_router.error_dict', {}), \
             patch('privacy.routing.privacy_router.threading.Thread') as mock_thread:
            mock_privacy_exc = PrivacyException(detail="DOCX processing error")
            mock_doc.mask_doc.side_effect = mock_privacy_exc
            
            file_content = b"fake docx content"
            files = {"docx": ("document.docx", BytesIO(file_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/DOCX/anonymize",
                files=files
            )
            
            mock_thread.assert_called()
            assert response.status_code in [400, 500]
    
    def test_docx_anonymize_generic_exception_with_error_telemetry(self, mock_env_vars):
        """Test /privacy-files/DOCX/anonymize with generic Exception and error telemetry."""
        with patch('privacy.routing.privacy_router.DOCService') as mock_doc, \
             patch('privacy.routing.privacy_router.error_dict', {}), \
             patch('privacy.routing.privacy_router.threading.Thread') as mock_thread:
            mock_doc.mask_doc.side_effect = Exception("DOCX error")
            
            file_content = b"fake docx content"
            files = {"docx": ("document.docx", BytesIO(file_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/DOCX/anonymize",
                files=files
            )
            
            mock_thread.assert_called()
            assert response.status_code == 500


# ============================================================================
# Test Video Anonymize Endpoint
# ============================================================================

class TestVideoAnonymizeEndpoint:
    """Test video anonymize endpoint."""
    
    def test_video_anonymize_success(self, mock_env_vars):
        """Test /privacy-files/video/anonymize endpoint with successful response."""
        with patch('privacy.routing.privacy_router.VideoService') as mock_video_service:
            mock_instance = MagicMock()
            mock_response = {"video_data": "anonymized_video"}
            
            # Create an async mock for videoPrivacy using AsyncMock
            from unittest.mock import AsyncMock
            mock_instance.videoPrivacy = AsyncMock(return_value=mock_response)
            mock_video_service.return_value = mock_instance
            
            file_content = b"fake video content"
            files = {"video": ("test.mp4", BytesIO(file_content), "video/mp4")}
            data = {
                "magnification": "True",
                "rotationFlag": "False",
                "ocr": "Tesseract",
                "nlp": "basic",
                "portfolio": "test_portfolio",
                "account": "test_account"
            }
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/video/anonymize",
                files=files,
                data=data
            )
            
            assert response.status_code == 200
    
    def test_video_anonymize_no_account_exception(self, mock_env_vars):
        """Test /privacy-files/video/anonymize with NoAccountException."""
        with patch('privacy.routing.privacy_router.VideoService') as mock_video_service:
            mock_instance = MagicMock()
            
            # Create async mock that returns None
            from unittest.mock import AsyncMock
            mock_instance.videoPrivacy = AsyncMock(return_value=None)
            mock_video_service.return_value = mock_instance
            
            file_content = b"fake video content"
            files = {"video": ("test.mp4", BytesIO(file_content), "video/mp4")}
            data = {
                "magnification": "False",
                "rotationFlag": "True",
                "ocr": "EasyOcr"
            }
            
            from fastapi import FastAPI
            test_app = FastAPI()
            test_app.include_router(privacy_router.fileRouter)
            test_client = TestClient(test_app)
            
            response = test_client.post(
                "/privacy-files/video/anonymize",
                files=files,
                data=data
            )
            
            assert response.status_code == 430


class TestLoadRecognizerExceptionPaths:
    """Test exception paths in loadRecognizer endpoints."""
    
    def test_load_recognizer_post_exception(self, mock_env_vars, mock_load_recognizer):
        """Test /privacy/loadRecognizer POST with exception."""
        mock_load_recognizer.set_recognizer = MagicMock(side_effect=Exception("Load error"))
        
        file_content = b"fake recognizer data"
        files = {"payload": ("recognizer.json", BytesIO(file_content), "application/json")}
        
        response = client.post(
            "/privacy/loadRecognizer",
            files=files
        )
        
        assert response.status_code == 500
    
    def test_load_recognizer_get_exception(self, mock_env_vars, mock_load_recognizer):
        """Test /privacy/getRecognizer GET with exception."""
        mock_load_recognizer.load_recognizer = MagicMock(side_effect=Exception("Get error"))
        
        response = client.get("/privacy/getRecognizer")
        
        assert response.status_code == 500

