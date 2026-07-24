"""
Pytest configuration files for image explainability tests
Provides fixtures and auto-mocking for heavy dependencies

This module MUST set up mocks at import time to prevent
import-time errors from heavy libraries like CLIP and torch
"""

import sys
import os
from unittest.mock import MagicMock, patch

# ============================================================================
# CRITICAL: Setup mocks at module import time BEFORE pytest discovers tests
# ============================================================================

def _setup_critical_mocks():
    """
    Mock heavy dependencies that fail at import time.
    This is called immediately when conftest.py is imported.
    """
    
    # Create mock CLIP that returns proper tuple from load()
    clip_mock = MagicMock()
    model_mock = MagicMock()
    preprocess_mock = MagicMock(side_effect=lambda x: x)  # passthrough preprocessor
    
    # CRITICAL: load() must return a tuple of (model, preprocess)
    clip_mock.load = MagicMock(return_value=(model_mock, preprocess_mock))
    
    # Mock torch
    torch_mock = MagicMock()
    torch_mock.no_grad = MagicMock(
        return_value=MagicMock(
            __enter__=MagicMock(return_value=None),
            __exit__=MagicMock(return_value=None)
        )
    )
    torch_mock.cuda = MagicMock()
    torch_mock.device = MagicMock()
    torch_mock.Tensor = MagicMock()
    torch_mock.tensor = MagicMock(return_value=MagicMock())
    torch_mock.mm = MagicMock(return_value=MagicMock())
    torch_mock.nn.Module = object  # For class inheritance
    
    # Pre-install all mocks into sys.modules
    sys.modules['clip'] = clip_mock
    sys.modules['torch'] = torch_mock
    sys.modules['torch.nn'] = MagicMock()
    sys.modules['torch.nn.functional'] = MagicMock()
    sys.modules['torch.optim'] = MagicMock()
    sys.modules['torch.utils'] = MagicMock()
    sys.modules['torch.utils.data'] = MagicMock()
    
    # Mock other heavy dependencies
    sys.modules['transformers'] = MagicMock()
    sys.modules['cv2'] = MagicMock()
    sys.modules['PIL'] = MagicMock()
    sys.modules['PIL.Image'] = MagicMock()
    sys.modules['google'] = MagicMock()
    sys.modules['google.generativeai'] = MagicMock()
    sys.modules['ollama'] = MagicMock()

# Execute mocks immediately on conftest import
_setup_critical_mocks()

import pytest
import io
from fastapi.testclient import TestClient


@pytest.fixture
def mock_image_data():
    """Fixture providing mock image data"""
    return b'\xff\xd8\xff\xe0\x00\x10JFIF...'


@pytest.fixture
def mock_base64_image():
    """Fixture providing base64 encoded image"""
    return 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='


@pytest.fixture
def mock_file_path():
    """Fixture providing mock file path"""
    return '/tmp/test_image.jpg'


@pytest.fixture
def mock_mime_type():
    """Fixture providing mime type"""
    return 'image/jpeg'


@pytest.fixture
def mock_upload_file():
    """Fixture providing FastAPI UploadFile mock"""
    file_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
    upload_file = MagicMock()
    upload_file.filename = "test_image.jpg"
    upload_file.content_type = "image/jpeg"
    upload_file.file = io.BytesIO(file_content)
    upload_file.read = MagicMock(return_value=file_content)
    return upload_file


@pytest.fixture
def mock_png_bytes():
    """Fixture providing PNG image bytes"""
    # Minimal valid PNG (1x1 transparent pixel)
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'


@pytest.fixture
def mock_jpeg_bytes():
    """Fixture providing JPEG image bytes"""
    return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9'


@pytest.fixture
def mock_image_service():
    """Fixture providing mocked ImageService"""
    from unittest.mock import MagicMock
    mock_service = MagicMock()
    mock_service.analyze_image = MagicMock(return_value={
        "image_description": "Test description",
        "aesthetic_score": 85,
        "alignment_score": 90,
        "uncertainty_score": 15,
        "bias": {"Analysis": "No bias", "Bias type(s)": "None"}
    })
    mock_service.object_detection_img = MagicMock(return_value={
        "detected_objects": ["person", "car"],
        "bounding_boxes": [[10, 20, 100, 200]]
    })
    return mock_service


@pytest.fixture
def mock_logger():
    """Fixture providing mocked CustomLogger"""
    from unittest.mock import MagicMock
    mock_log = MagicMock()
    mock_log.info = MagicMock()
    mock_log.debug = MagicMock()
    mock_log.error = MagicMock()
    mock_log.warning = MagicMock()
    return mock_log


@pytest.fixture
def sample_analyze_response():
    """Fixture providing sample AnalyzeResponse data"""
    return {
        "image_description": "A beautiful landscape with mountains",
        "aesthetic_score": 85.5,
        "alignment_score": 90.2,
        "uncertainty_score": 12.3,
        "certainty_score": 87.7,
        "creativity_score": 75.0,
        "coherence_score": 88.0,
        "bias": {
            "Analysis": "No significant bias detected",
            "Bias type(s)": "None"
        }
    }


@pytest.fixture
def sample_object_detection_response():
    """Fixture providing sample ObjectDetectionResponse data"""
    return {
        "detected_objects": ["person", "car", "tree"],
        "bounding_boxes": [[50, 100, 200, 300], [300, 150, 450, 400]],
        "confidence_scores": [0.95, 0.88, 0.92]
    }
