"""
Integration Test Setup Verification Script

Run this script to verify your environment is ready for integration tests.
"""

import os
import sys

def check_pymongo():
    """Check if pymongo is installed and get version."""
    try:
        import pymongo
        print(f"✓ pymongo {pymongo.__version__} is installed")
        return True
    except ImportError:
        print("✗ pymongo is NOT installed")
        print("  Install: pip install pymongo")
        return False

def check_mongodb_connection():
    """Check if MongoDB is accessible."""
    try:
        import pymongo
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print("✓ MongoDB is RUNNING and accessible at localhost:27017")
        client.close()
        return True
    except Exception as e:
        print(f"✗ MongoDB is NOT accessible: {str(e)}")
        print("  Start MongoDB:")
        print("    Windows: net start MongoDB")
        print("    Docker:  docker run -d -p 27017:27017 --name mongodb-test mongo:latest")
        return False

def check_mongomock():
    """Check if mongomock is installed (optional)."""
    try:
        import mongomock
        print(f"✓ mongomock {mongomock.__version__} is installed (optional)")
        return True
    except ImportError:
        print("- mongomock is not installed (optional, for fallback testing)")
        return True  # Not critical

def check_required_packages():
    """Check if required packages are installed."""
    required = {
        'pytest': 'Testing framework',
        'pytest-cov': 'Coverage measurement',
        'numpy': 'Numerical computing',
        'pandas': 'Data manipulation',
        'sklearn': 'ML models (scikit-learn)',
        'art': 'Adversarial Robustness Toolbox'
    }
    
    all_present = True
    for package, description in required.items():
        try:
            if package == 'sklearn':
                import sklearn
                print(f"✓ scikit-learn {sklearn.__version__} - {description}")
            elif package == 'art':
                import art
                print(f"✓ adversarial-robustness-toolbox - {description}")
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                print(f"✓ {package} {version} - {description}")
        except ImportError:
            print(f"✗ {package} is NOT installed - {description}")
            all_present = False
    
    return all_present

def check_env_variables():
    """Check if required environment variables are set."""
    print("\nEnvironment Variables:")
    
    env_vars = {
        'DB_NAME': 'Database name',
        'TEST_DB': 'Test database (should be empty or different from DB_NAME)',
        'DB_TYPE': 'Database type (should be "mongo")',
        'MONGO_PATH': 'MongoDB connection string',
        'TELEMETRY_FLAG': 'Telemetry flag (should be "False" for tests)'
    }
    
    for var, description in env_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'PATH' in var or 'PWD' in var:
                display_value = value[:20] + '...' if len(value) > 20 else value
            else:
                display_value = value
            print(f"✓ {var} = {display_value} ({description})")
        else:
            if var == 'TEST_DB':
                print(f"- {var} is not set (OK for integration tests - will use real DB)")
            else:
                print(f"⚠ {var} is not set - {description}")
                print(f"  Set in .env file or environment")

def check_directory_structure():
    """Verify integration test directory exists."""
    integration_dir = 'app/test/integration'
    if os.path.exists(integration_dir):
        print(f"\n✓ Integration test directory exists: {integration_dir}")
        
        test_files = [
            'conftest.py',
            'test_utility_integration.py',
            'test_art_integration.py',
            'test_service_defence_integration.py'
        ]
        
        for test_file in test_files:
            file_path = os.path.join(integration_dir, test_file)
            if os.path.exists(file_path):
                print(f"  ✓ {test_file}")
            else:
                print(f"  ✗ {test_file} is missing")
        return True
    else:
        print(f"\n✗ Integration test directory NOT found: {integration_dir}")
        return False

def create_sample_env():
    """Create a sample .env file for integration tests."""
    env_content = """# Integration Test Environment Configuration

# Database Configuration
DB_NAME="test_security_integration_db"
TEST_DB=""  # Leave empty to use real DB (not mock)
DB_TYPE="mongo"
MONGO_PATH="mongodb://localhost:27017/"

# Optional: Azure Blob Storage (if testing blob features)
MODEL_CONTAINER_NAME="test-models"
DATA_CONTAINER_NAME="test-data"
ZIP_CONTAINER_NAME="test-zips"
PREPROCESSOR_CONTAINER_NAME="test-preprocessor"

# Disable telemetry for testing
TELEMETRY_FLAG="False"

# Authentication (use none for tests)
AUTH_TYPE="none"

# Placeholder values (not needed for integration tests)
AZURE_CLIENT_ID="placeholder"
AZURE_TENANT_ID="placeholder"
AZURE_AD_JWKS_URL="placeholder"
AZURE_CLIENT_SECRET="placeholder"
ALLOW_ORIGINS="*"
ERRORLOGAPI="placeholder"
SECURITYPDFGENERATIONIP="localhost"
"""
    
    env_file = '.env.integration.example'
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"\n✓ Created sample environment file: {env_file}")
    print("  Copy this to .env and update values as needed")

def main():
    """Run all checks."""
    print("=" * 60)
    print("Integration Test Environment Check")
    print("=" * 60)
    
    print("\nChecking Python Packages:")
    print("-" * 40)
    mongo_ok = check_pymongo()
    packages_ok = check_required_packages()
    mongomock_ok = check_mongomock()
    
    print("\nChecking MongoDB Connection:")
    print("-" * 40)
    mongodb_ok = check_mongodb_connection()
    
    print("\nChecking Environment:")
    print("-" * 40)
    check_env_variables()
    
    print("\nChecking Directory Structure:")
    print("-" * 40)
    dir_ok = check_directory_structure()
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    if mongo_ok and packages_ok and mongodb_ok and dir_ok:
        print("✓ Your environment is READY for integration tests!")
        print("\nRun integration tests:")
        print("  pytest app/test/integration/ -v")
        print("\nWith coverage:")
        print("  pytest app/test/integration/ --cov=app/src --cov-report=term -v")
        return 0
    else:
        print("⚠ Your environment needs some setup")
        if not mongo_ok or not packages_ok:
            print("\nInstall missing packages:")
            print("  pip install -r requirements/requirement.txt")
        if not mongodb_ok:
            print("\nStart MongoDB:")
            print("  Windows: net start MongoDB")
            print("  Docker:  docker run -d -p 27017:27017 --name mongodb-test mongo:latest")
        
        print("\nGenerate sample .env file:")
        create_sample_env()
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
