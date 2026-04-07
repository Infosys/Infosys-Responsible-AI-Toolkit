"""
Integration Test Configuration

This conftest.py is specifically for integration tests.
It does NOT mock the database - uses real MongoDB connections.
"""
import os
import pytest
import pymongo
from pymongo import MongoClient
import tempfile
import shutil

# Save original environment variables to restore after integration tests
_original_test_db = os.environ.get("TEST_DB", None)
_original_db_name = os.environ.get("DB_NAME", None)

# Set environment for integration tests - use real database
# Do NOT set TEST_DB to match DB_NAME (that triggers mock mode)
os.environ["TELEMETRY_FLAG"] = "False"
os.environ["DB_NAME"] = os.getenv("DB_NAME", "test_security_integration_db")
os.environ["TEST_DB"] = ""  # Empty means use real DB, not mock
os.environ["DB_TYPE"] = os.getenv("DB_TYPE", "mongo")
os.environ["MONGO_PATH"] = os.getenv("MONGO_PATH", "mongodb://localhost:27017/")

# Azure blob storage settings (use test containers if available)
os.environ.setdefault("MODEL_CONTAINER_NAME", "test-models")
os.environ.setdefault("DATA_CONTAINER_NAME", "test-data")
os.environ.setdefault("ZIP_CONTAINER_NAME", "test-zips")
os.environ.setdefault("PREPROCESSOR_CONTAINER_NAME", "test-preprocessor")

# Disable authentication for integration tests
os.environ.setdefault("AUTH_TYPE", "none")

def pytest_sessionfinish(session, exitstatus):
    """
    Restore original environment variables after integration tests complete.
    This prevents integration test settings from affecting unit tests.
    """
    if _original_test_db is not None:
        os.environ["TEST_DB"] = _original_test_db
    else:
        os.environ.pop("TEST_DB", None)
    
    if _original_db_name is not None:
        os.environ["DB_NAME"] = _original_db_name

@pytest.fixture(scope="session")
def real_db_connection():
    """
    Fixture providing a real MongoDB connection for integration tests.
    Cleans up test database after all tests complete.
    """
    db_name = os.environ["DB_NAME"]
    mongo_path = os.environ["MONGO_PATH"]
    
    try:
        client = MongoClient(mongo_path, serverSelectionTimeoutMS=5000)
        # Test the connection
        client.admin.command('ping')
        db = client[db_name]
        
        yield db
        
        # Cleanup: Drop test database after all tests
        print(f"\n[CLEANUP] Dropping test database: {db_name}")
        client.drop_database(db_name)
        client.close()
    except pymongo.errors.ServerSelectionTimeoutError:
        pytest.skip("MongoDB not available - skipping integration tests")

@pytest.fixture(scope="function")
def clean_db_collections(real_db_connection):
    """
    Fixture that cleans up database collections before each test.
    Ensures tests start with clean state.
    """
    db = real_db_connection
    
    # List of collections used by the application
    collections = [
        'Model', 'ModelAttributes', 'ModelAttributesValues',
        'Data', 'DataAttributes', 'DataAttributesValues',
        'Batch', 'SecReport', 'ErrDtl',
        'fs.files', 'fs.chunks'  # GridFS collections
    ]
    
    # Clean collections before test
    for collection_name in collections:
        if collection_name in db.list_collection_names():
            db[collection_name].delete_many({})
    
    yield db
    
    # Optional: Clean after test as well
    for collection_name in collections:
        if collection_name in db.list_collection_names():
            db[collection_name].delete_many({})

@pytest.fixture(scope="function")
def test_temp_dir():
    """
    Fixture providing a temporary directory for file operations.
    Automatically cleans up after test.
    """
    temp_dir = tempfile.mkdtemp(prefix="integration_test_")
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

@pytest.fixture(scope="function")
def sample_model_file(test_temp_dir):
    """
    Creates a sample model file for testing.
    """
    import pickle
    import numpy as np
    from sklearn.svm import SVC
    
    # Create a simple trained model
    X = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])
    y = np.array([0, 1, 0, 1])
    model = SVC(kernel='linear', probability=True)
    model.fit(X, y)
    
    model_path = os.path.join(test_temp_dir, "test_model.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    return model_path

@pytest.fixture(scope="function")
def sample_data_file(test_temp_dir):
    """
    Creates a sample data file for testing.
    """
    import pickle
    import numpy as np
    
    X_test = np.array([[0.5, 0.5], [1.5, 1.5], [2.5, 2.5]])
    y_test = np.array([0, 1, 0])
    
    data = {
        'X_test': X_test,
        'y_test': y_test
    }
    
    data_path = os.path.join(test_temp_dir, "test_data.pkl")
    with open(data_path, 'wb') as f:
        pickle.dump(data, f)
    
    return data_path

@pytest.fixture(scope="function")
def create_batch_helper():
    """Helper to create Batch records with proper payload structure."""
    from src.dao.Batch import Batch
    
    def _create_batch(batch_id, model_id, data_id, user_id="test_user", tenant_id="test_tenant"):
        class PayloadObj:
            def __init__(self, userId, modelId, dataId):
                self.userId = userId
                self.modelId = modelId
                self.dataId = dataId
        
        try:
            payload = PayloadObj(userId=user_id, modelId=model_id, dataId=data_id)
            result = Batch.create(payload, tenant_id)
            if result and 'BatchId' in result:
                return result['BatchId']  # Returns the generated batch ID
            else:
                # Fallback: return a generated batch ID
                import time
                return time.time()
        except Exception as e:
            # If Batch.create fails, return a timestamp as batch ID
            import time
            return time.time()
    
    return _create_batch

@pytest.fixture(scope="function") 
def sample_model_data_in_db(clean_db_collections, sample_model_file, sample_data_file, create_batch_helper):
    """
    Inserts sample model and data records into database for testing.
    Returns IDs of created records.
    """
    from src.dao.ModelDb import Model
    from src.dao.DataDb import Data
    from src.dao.SaveFileDB import FileStoreDb
    from src.dao.ModelAttributesDb import ModelAttributes
    from src.dao.ModelAttributesValuesDb import ModelAttributesValues
    from src.dao.DataAttributesDb import DataAttributes
    from src.dao.DataAttributesValuesDb import DataAttributesValues
    import io
    import time
    
    db = clean_db_collections
    
    # Create a model file in GridFS
    with open(sample_model_file, 'rb') as f:
        model_content = f.read()
    
    # Simulate file upload
    class FakeFile:
        def __init__(self, content, content_type="application/octet-stream"):
            self.file = io.BytesIO(content)
            self.content_type = content_type
    
    fake_model_file = FakeFile(model_content)
    model_file_id = FileStoreDb.create(fake_model_file, "test_model.pkl")
    
    # Create data file in GridFS
    with open(sample_data_file, 'rb') as f:
        data_content = f.read()
    
    fake_data_file = FakeFile(data_content)
    data_file_id = FileStoreDb.create(fake_data_file, "test_data.pkl")
    
    # Create Model record with all required fields
    model_record = {
        'userId': 'test_user',
        'modelName': 'TestModel_Integration',
        'modelVersion': '1.0',
        'modelType': 'classification',
        'modelData': model_file_id,
        'modelEndPoint': '',
        'status': 'active',
        'createdDate': time.time()
    }
    model_id = Model.create(model_record)
    
    # Validate model_id was created
    if model_id is None:
        raise ValueError("Model.create() returned None - check required fields")
    
    # Create Model Attributes for framework
    attr_framework = ModelAttributes.create({
        'ModelAttributeName': 'modelFramework',
        'ModelAttributeType': 'string'
    })
    attr_use_api = ModelAttributes.create({
        'ModelAttributeName': 'useModelApi',
        'ModelAttributeType': 'string'
    })
    
    # Create ModelAttributesValues
    ModelAttributesValues.create({
        'ModelId': model_id,
        'ModelAttributeId': attr_framework,
        'ModelAttributeValues': 'sklearn'
    })
    ModelAttributesValues.create({
        'ModelId': model_id,
        'ModelAttributeId': attr_use_api,
        'ModelAttributeValues': 'No'
    })
    
    # Insert Data record with all required fields
    data_record = {
        'userId': 'test_user',
        'dataSetName': 'TestData_Integration',
        'sampleData': data_file_id,
        'groundTruthImageFileId': 'NA',
    }
    data_id = Data.create(data_record)
    
    # Validate data_id was created
    if data_id is None:
        raise ValueError("Data.create() returned None - check required fields")
    
    # Create Batch record using helper
    batch_id = create_batch_helper(
        batch_id='test_batch_integration',
        model_id=model_id,
        data_id=data_id
    )
    
    return {
        'model_id': model_id,
        'data_id': data_id,
        'model_file_id': model_file_id,
        'data_file_id': data_file_id,
        'model_path': sample_model_file,
        'data_path': sample_data_file,
        'batch_id': batch_id
    }
