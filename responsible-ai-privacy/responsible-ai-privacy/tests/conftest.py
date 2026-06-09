'''
MIT License https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

pytest configuration file
Contains common fixtures and test setup for the entire test suite
'''

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# Set required environment variables BEFORE any module imports
# This prevents KeyError during privacy_router module import
os.environ.setdefault("AUTH_TYPE", "none")
os.environ.setdefault("TELE_FLAG", "False")
os.environ.setdefault("PRIVACY_TELEMETRY_URL", "http://test-telemetry.com")
os.environ.setdefault("PRIVACY_ERROR_URL", "http://test-error.com")
os.environ.setdefault("VERIFY_SSL", "False")
os.environ.setdefault("MONGO_PATH", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "test_db")

# Mock pymongo BEFORE any imports to prevent database connection
mock_pymongo = MagicMock()
mock_mongo_client = MagicMock()
mock_db = MagicMock()
mock_mongo_client.__getitem__.return_value = mock_db
mock_pymongo.MongoClient = MagicMock(return_value=mock_mongo_client)
sys.modules['pymongo'] = mock_pymongo
sys.modules['pymongo.synchronous'] = MagicMock()
sys.modules['pymongo.synchronous.mongo_client'] = MagicMock()
sys.modules['pymongo.synchronous.database'] = MagicMock()

# Mock heavy dependencies BEFORE any imports to prevent model loading
# This prevents transformer models from being loaded during test collection

# Create sophisticated torch mock with proper module structure
mock_torch = MagicMock()
mock_torch.__spec__ = MagicMock()
mock_torch.__spec__.origin = 'torch'
mock_torch.nn = MagicMock()
mock_torch.nn.Module = MagicMock()
mock_torch.nn.functional = MagicMock()
mock_torch.cuda = MagicMock()
mock_torch.cuda.is_available = MagicMock(return_value=False)
mock_torch.device = MagicMock(return_value='cpu')
mock_torch.backends = MagicMock()
mock_torch.backends.cudnn = MagicMock()
mock_torch.hub = MagicMock()
mock_torch.hub._get_torch_home = MagicMock(return_value='/tmp/torch_home')
mock_torch.utils = MagicMock()
mock_torch.utils.data = MagicMock()
mock_torch.utils.data.DataLoader = MagicMock()
mock_torch.utils.data.IterableDataset = MagicMock()
mock_torch.version = MagicMock()
mock_torch.version.cuda = '11.0'
mock_torch.autograd = MagicMock()
mock_torch.autograd.Variable = MagicMock()
sys.modules['torch'] = mock_torch
sys.modules['torch.nn'] = mock_torch.nn
sys.modules['torch.nn.functional'] = mock_torch.nn.functional
sys.modules['torch.cuda'] = mock_torch.cuda
sys.modules['torch.backends'] = mock_torch.backends
sys.modules['torch.backends.cudnn'] = mock_torch.backends.cudnn
sys.modules['torch.hub'] = mock_torch.hub
sys.modules['torch.utils'] = mock_torch.utils
sys.modules['torch.utils.data'] = mock_torch.utils.data
sys.modules['torch.version'] = mock_torch.version
sys.modules['torch.autograd'] = mock_torch.autograd

# Mock torchvision
mock_torchvision = MagicMock()
mock_torchvision.transforms = MagicMock()
mock_torchvision.ops = MagicMock()
mock_torchvision.ops.torchvision = MagicMock()
mock_torchvision.ops.torchvision._cuda_version = MagicMock(return_value='11000')
sys.modules['torchvision'] = mock_torchvision
sys.modules['torchvision.transforms'] = mock_torchvision.transforms
sys.modules['torchvision.ops'] = mock_torchvision.ops

# Mock easyocr to prevent initialization at import time
mock_easyocr = MagicMock()
mock_easyocr.Reader = MagicMock()
sys.modules['easyocr'] = mock_easyocr
sys.modules['easyocr.easyocr'] = MagicMock()
sys.modules['easyocr.recognition'] = MagicMock()
sys.modules['easyocr.detection'] = MagicMock()

# Mock transformers and related modules
# Create proper mock classes for base classes used in dataclasses
class MockModelOutput:
    """Mock ModelOutput class that can be used as a base class in dataclasses"""
    pass

class MockDataCollatorForTokenClassification:
    """Mock DataCollatorForTokenClassification that can be used as a base class in dataclasses"""
    pass

mock_transformers = MagicMock()
mock_transformers.utils = MagicMock()
mock_transformers.utils.ModelOutput = MockModelOutput
mock_transformers.models = MagicMock()
mock_transformers.models.auto = MagicMock()
mock_transformers.models.auto.auto_factory = MagicMock()
mock_transformers.trainer_utils = MagicMock()
mock_transformers.DataCollatorForTokenClassification = MockDataCollatorForTokenClassification
sys.modules['transformers'] = mock_transformers
sys.modules['transformers.utils'] = mock_transformers.utils
sys.modules['transformers.models'] = mock_transformers.models
sys.modules['transformers.models.auto'] = mock_transformers.models.auto
sys.modules['transformers.models.auto.auto_factory'] = mock_transformers.models.auto.auto_factory
sys.modules['transformers.trainer_utils'] = mock_transformers.trainer_utils

# Mock spacy to prevent model loading
mock_spacy = MagicMock()
mock_spacy.load = MagicMock(return_value=MagicMock())
mock_spacy.tokens = MagicMock()
mock_spacy.tokens.Doc = MagicMock()
mock_spacy.tokens.Span = MagicMock()
mock_spacy.matcher = MagicMock()
mock_spacy.matcher.PhraseMatcher = MagicMock()
sys.modules['spacy'] = mock_spacy
sys.modules['spacy.util'] = MagicMock()
sys.modules['spacy.language'] = MagicMock()
sys.modules['spacy.tokens'] = mock_spacy.tokens
sys.modules['spacy.matcher'] = mock_spacy.matcher

# Mock curated_transformers
sys.modules['curated_transformers'] = MagicMock()
sys.modules['curated_transformers.models'] = MagicMock()
sys.modules['curated_transformers.models.activations'] = MagicMock()
sys.modules['curated_transformers.models.albert'] = MagicMock()

# Mock spacy_curated_transformers
sys.modules['spacy_curated_transformers'] = MagicMock()
sys.modules['spacy_curated_transformers.pipeline'] = MagicMock()
sys.modules['spacy_curated_transformers.models'] = MagicMock()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

# Set up global mock variables in privacy.service.test_service namespace
# These need to be injected after test_service module is imported
def setup_test_service_globals():
    """Setup mock global variables for test_service module"""
    # Import the test_service module directly
    from privacy.service import test_service
    
    # Create mock analyzer and anonymizer
    mock_analyzer = MagicMock()
    mock_analyzer.analyze = MagicMock(return_value=[])
    
    mock_anonymizer = MagicMock()
    mock_anonymizer.anonymize = MagicMock(return_value=MagicMock(text="", items=[]))
    
    # Create mock Data class
    mock_data_class = type('Data', (), {})
    mock_data_class.encrypted_text = []
    
    # Inject directly into test_service module namespace
    test_service.analyzer = mock_analyzer
    test_service.anonymizer = mock_anonymizer
    test_service.Data = mock_data_class
    test_service.imageAnalyzerEngine = MagicMock()
    test_service.imageRedactorEngine = MagicMock()
    test_service.imagePiiVerifyEngine = MagicMock()
    test_service.encryptImageEngin = MagicMock()
    test_service.deanonymizer = MagicMock()
    test_service.registry = MagicMock()

# Call setup immediately
setup_test_service_globals()

# Additional mocking for privacy_router dependencies
# Mock datasets library to prevent import errors
sys.modules['datasets'] = MagicMock()
sys.modules['datasets.arrow_dataset'] = MagicMock()

# Mock numpy properly for dataclass compatibility
mock_numpy = MagicMock()
mock_numpy.dtype = type  # Make dtype a real type for dataclass compatibility
mock_numpy.ndarray = MagicMock
sys.modules['numpy'] = mock_numpy

# Mock scipy
sys.modules['scipy'] = MagicMock()
sys.modules['scipy.stats'] = MagicMock()
sys.modules['scipy.spatial'] = MagicMock()

# Mock cv2
sys.modules['cv2'] = MagicMock()

# Mock PIL
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()

# Mock sklearn
mock_sklearn = MagicMock()
mock_sklearn.metrics = MagicMock()
mock_sklearn.utils = MagicMock()
mock_sklearn.exceptions = MagicMock()
sys.modules['sklearn'] = mock_sklearn
sys.modules['sklearn.metrics'] = mock_sklearn.metrics
sys.modules['sklearn.utils'] = mock_sklearn.utils
sys.modules['sklearn.exceptions'] = mock_sklearn.exceptions

# Mock seqeval
sys.modules['seqeval'] = MagicMock()
sys.modules['seqeval.metrics'] = MagicMock()
sys.modules['seqeval.metrics.sequence_labeling'] = MagicMock()

# Mock onnxruntime
sys.modules['onnxruntime'] = MagicMock()

# Mock diffprivlib
sys.modules['diffprivlib'] = MagicMock()
sys.modules['diffprivlib.mechanisms'] = MagicMock()
sys.modules['diffprivlib.mechanisms.binary'] = MagicMock()

# Mock pydicom
sys.modules['pydicom'] = MagicMock()

# Mock AutoModelForTokenClassification and AutoTokenizer to prevent HuggingFace model loading
mock_model_instance = MagicMock()
mock_tokenizer_instance = MagicMock()
mock_tokenizer_instance.model_max_length = 512

# Override the from_pretrained methods to return mock instances
mock_transformers.AutoModelForTokenClassification.from_pretrained = MagicMock(return_value=mock_model_instance)
mock_transformers.AutoTokenizer.from_pretrained = MagicMock(return_value=mock_tokenizer_instance)


@pytest.fixture(scope='session')
def project_root():
    """Return the project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope='session')
def src_dir(project_root):
    """Return the src directory"""
    return project_root / 'src'


@pytest.fixture(scope='session')
def test_data_dir():
    """Return the test data directory"""
    test_dir = Path(__file__).parent
    data_dir = test_dir / 'test_data'
    data_dir.mkdir(exist_ok=True)
    return data_dir


@pytest.fixture(autouse=True)
def initialize_request_context():
    """Initialize request_id_var for logger in all tests"""
    from privacy.config import logger
    # Set a default request ID for tests
    logger.request_id_var.set("test-request-id")
    yield
    # Cleanup after test
    try:
        token = logger.request_id_var.set("test-request-id")
    except:
        pass


@pytest.fixture
def mock_logger():
    """Mock CustomLogger for tests"""
    mock_log = Mock()
    mock_log.debug = Mock()
    mock_log.info = Mock()
    mock_log.warning = Mock()
    mock_log.error = Mock()
    mock_log.critical = Mock()
    return mock_log


@pytest.fixture
def mock_request_id():
    """Mock request ID variable"""
    mock_var = Mock()
    mock_var.get.return_value = 'test-request-id-123'
    return mock_var


@pytest.fixture
def sample_text_with_pii():
    """Sample text containing PII for testing"""
    return "John Smith lives at 123 Main St. His email is john.smith@example.com and SSN is 123-45-6789."


@pytest.fixture
def sample_text_without_pii():
    """Sample text without PII for testing"""
    return "This is a clean text without any personal information."


@pytest.fixture
def mock_analyzer_result():
    """Mock analyzer result for PII detection"""
    mock_result = Mock()
    mock_result.entity_type = 'PERSON'
    mock_result.start = 0
    mock_result.end = 10
    mock_result.score = 0.95
    return mock_result


@pytest.fixture
def mock_pii_analyze_request():
    """Mock PIIAnalyzeRequest object"""
    from privacy.mappers.mappers import PIIAnalyzeRequest
    
    return PIIAnalyzeRequest(
        inputText="Test text with PII",
        piiEntitiesToBeRedacted=['PERSON', 'EMAIL'],
        exclusionList=None,
        portfolio=None,
        nlp='basic'
    )


@pytest.fixture
def mock_pii_anonymize_request():
    """Mock PIIAnonymizeRequest object"""
    from privacy.mappers.mappers import PIIAnonymizeRequest
    
    return PIIAnonymizeRequest(
        inputText="Test text with PII",
        piiEntitiesToBeRedacted=['PERSON', 'EMAIL'],
        exclusionList=None,
        portfolio=None,
        nlp='basic',
        fakeData=False
    )


@pytest.fixture
def mock_database_connection():
    """Mock database connection"""
    mock_conn = Mock()
    mock_conn.cursor.return_value = Mock()
    mock_conn.commit = Mock()
    mock_conn.close = Mock()
    return mock_conn


@pytest.fixture
def mock_presidio_analyzer():
    """Mock Presidio AnalyzerEngine"""
    mock_analyzer = Mock()
    mock_analyzer.analyze.return_value = []
    return mock_analyzer


@pytest.fixture
def mock_presidio_anonymizer():
    """Mock Presidio AnonymizerEngine"""
    mock_anonymizer = Mock()
    mock_anon_result = Mock()
    mock_anon_result.text = "Anonymized text"
    mock_anon_result.items = []
    mock_anonymizer.anonymize.return_value = mock_anon_result
    return mock_anonymizer


@pytest.fixture
def mock_image_analyzer_engine():
    """Mock ImageAnalyzerEngine for image processing"""
    mock_engine = Mock()
    mock_engine.analyze.return_value = []
    mock_engine._parse_ocr_kwargs.return_value = ({}, None)
    
    # Mock OCR
    mock_ocr = Mock()
    mock_ocr.perform_ocr.return_value = {'text': 'Sample text'}
    mock_ocr.get_text_from_ocr_dict.return_value = 'Sample text'
    mock_engine.ocr = mock_ocr
    
    return mock_engine


@pytest.fixture
def sample_pil_image():
    """Create a sample PIL Image for testing"""
    from PIL import Image
    return Image.new('RGB', (100, 100), color='white')


@pytest.fixture
def sample_numpy_image():
    """Create a sample numpy array image for testing"""
    import numpy as np
    return np.zeros((100, 100, 3), dtype=np.uint8)


@pytest.fixture
def mock_api_call():
    """Mock ApiCall service"""
    with pytest.mock.patch('privacy.service.api_req.ApiCall') as mock_api:
        mock_api.request.return_value = (
            ['ENTITY1', 'ENTITY2'],  # entityType
            [['data1'], ['data2']],  # datalist
            ['PRE_ENTITY']  # preEntity
        )
        mock_api.getRecord.return_value = {
            'RecogType': 'Data',
            'RecogName': 'ENTITY1',
            'isPreDefined': 'No',
            'Score': 0.8
        }
        yield mock_api


@pytest.fixture
def mock_error_dict():
    """Mock global error_dict"""
    return {'test-request-id': []}


@pytest.fixture
def mock_admin_par():
    """Mock admin_par configuration dictionary"""
    return {
        'test-request-id': {
            'scoreTreshold': 0.5,
            'encryptionList': ['EMAIL', 'CREDIT_CARD'],
            'records': [
                {
                    'RecogName': 'EMAIL',
                    'RecogType': 'Pattern',
                    'isPreDefined': 'Yes',
                    'Score': 0.9
                },
                {
                    'RecogName': 'PERSON',
                    'RecogType': 'Pattern',
                    'isPreDefined': 'Yes',
                    'Score': 0.85
                }
            ]
        }
    }


@pytest.fixture
def temp_test_file(tmp_path):
    """Create a temporary test file"""
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("Test content")
    return test_file


@pytest.fixture
def temp_test_directory(tmp_path):
    """Create a temporary test directory"""
    test_dir = tmp_path / "test_directory"
    test_dir.mkdir()
    return test_dir


@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all mocks before each test"""
    yield
    # Cleanup code can go here if needed


@pytest.fixture
def mock_fastapi_request():
    """Mock FastAPI Request object"""
    mock_request = Mock()
    mock_request.headers = {'content-type': 'application/json'}
    mock_request.client = Mock()
    mock_request.client.host = '127.0.0.1'
    return mock_request


@pytest.fixture
def mock_fastapi_response():
    """Mock FastAPI Response object"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {}
    return mock_response


@pytest.fixture
def mock_recognizer_registry():
    """Mock RecognizerRegistry"""
    mock_registry = Mock()
    mock_registry.get_supported_entities.return_value = ['PERSON', 'EMAIL', 'PHONE_NUMBER']
    mock_registry.add_recognizer = Mock()
    return mock_registry


# Test markers configuration
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_model: mark test as requiring ML model"
    )
    config.addinivalue_line(
        "markers", "requires_db: mark test as requiring database"
    )


# Custom assertion helpers
class CustomAssertions:
    """Custom assertion helpers for tests"""
    
    @staticmethod
    def assert_valid_pii_entity(entity):
        """Assert that a PII entity has valid structure"""
        assert hasattr(entity, 'type')
        assert hasattr(entity, 'beginOffset')
        assert hasattr(entity, 'endOffset')
        assert entity.beginOffset >= 0
        assert entity.endOffset > entity.beginOffset
    
    @staticmethod
    def assert_valid_json_response(response):
        """Assert that response is valid JSON response"""
        assert response is not None
        assert hasattr(response, 'status_code')
        assert 200 <= response.status_code < 600


@pytest.fixture
def custom_assertions():
    """Provide custom assertion helpers"""
    return CustomAssertions()


# Pytest hooks for better test output
def pytest_runtest_makereport(item, call):
    """Hook to customize test reporting"""
    if call.when == "call":
        if call.excinfo is not None:
            # Test failed
            pass
        else:
            # Test passed
            pass


# Coverage configuration
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add unit marker to tests in unit directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to tests in integration directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add slow marker to tests with "slow" in name
        if "slow" in item.nodeid.lower():
            item.add_marker(pytest.mark.slow)
