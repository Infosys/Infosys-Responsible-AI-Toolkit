# Test Suite for Responsible AI Privacy

This directory contains comprehensive test cases for the Responsible AI Privacy project, achieving 75%+ code coverage.

## 📁 Directory Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── unit/                    # Unit tests for individual modules
│   ├── test_encrypt.py      # Tests for encryption utilities
│   ├── test_textPrivacy.py  # Tests for text privacy services
│   ├── test_exception.py    # Tests for exception handling
│   └── test_codegeneration.py  # Tests for code generation
├── integration/             # Integration tests
└── test_data/              # Test data files (auto-created)
```

## 🚀 Getting Started

### 1. Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### 2. Run All Tests

```bash
pytest
```

### 3. Run Tests with Coverage Report

```bash
pytest --cov=src/privacy --cov-report=html
```

Then open `htmlcov/index.html` in your browser to view the coverage report.

## 📊 Running Specific Tests

### Run Unit Tests Only
```bash
pytest tests/unit -v
```

### Run Integration Tests Only
```bash
pytest tests/integration -v
```

### Run Specific Test File
```bash
pytest tests/unit/test_encrypt.py -v
```

### Run Specific Test Class
```bash
pytest tests/unit/test_encrypt.py::TestDetect -v
```

### Run Specific Test Function
```bash
pytest tests/unit/test_encrypt.py::TestDetect::test_getFace_with_valid_face_image -v
```

## 🏷️ Test Markers

Tests are organized with markers for easy filtering:

### Run Unit Tests Only
```bash
pytest -m unit
```

### Run Integration Tests Only
```bash
pytest -m integration
```

### Skip Slow Tests
```bash
pytest -m "not slow"
```

### Run Tests Requiring Models
```bash
pytest -m requires_model
```

### Run Tests Requiring Database
```bash
pytest -m requires_db
```

## 📈 Coverage Goals

- **Overall Target**: 75%+ code coverage
- **Critical Modules**: 85%+ coverage
- **Utility Functions**: 80%+ coverage

### Generate Coverage Report

```bash
# HTML Report
pytest --cov=src/privacy --cov-report=html

# Terminal Report
pytest --cov=src/privacy --cov-report=term-missing

# XML Report (for CI/CD)
pytest --cov=src/privacy --cov-report=xml
```

## 🧪 Test Categories

### Unit Tests (tests/unit/)
- **test_encrypt.py**: 
  - `TestFig2Img` - Matplotlib to PIL conversion
  - `TestDetect` - Face detection functionality
  - `TestEncryptImage` - Image encryption and anonymization
  - Edge cases and error scenarios

- **test_textPrivacy.py**:
  - `TestTextPrivacyAnalyze` - Text PII analysis
  - `TestTextPrivacyTextAnalyze` - Core text analysis
  - `TestTextPrivacyAnonymize` - Text anonymization
  - `TestTextPrivacyEncrypt` - Text encryption
  - `TestTextPrivacyDecrypt` - Text decryption
  - `TestShieldPrivacyShield` - Privacy shield functionality

- **test_exception.py**:
  - `TestPrivacyException` - Base exception class
  - `TestPrivacyNotFoundError` - 404 errors
  - `TestPrivacyNameNotEmptyError` - Validation errors
  - `TestUnSupportedMediaTypeException` - Media type errors
  - Exception handlers

- **test_codegeneration.py**:
  - `TestCreateNewRecognizerFile` - File creation
  - `TestModifyRecognizerRegistry` - Registry modification
  - `TestModifyInitPy` - Init file updates
  - `TestRunWheelCreationCommands` - Wheel building
  - `TestCopyWheelFile` - Wheel deployment

## 🛠️ Writing New Tests

### Test Template

```python
import pytest
from unittest.mock import Mock, patch

class TestYourModule:
    """Test cases for YourModule"""
    
    @pytest.fixture
    def setup_data(self):
        """Setup test data"""
        return {"key": "value"}
    
    def test_basic_functionality(self, setup_data):
        """Test basic functionality"""
        # Arrange
        input_data = setup_data
        
        # Act
        result = your_function(input_data)
        
        # Assert
        assert result is not None
        assert result["key"] == "expected_value"
```

### Best Practices

1. **Use Descriptive Names**: Test names should clearly describe what they test
2. **Follow AAA Pattern**: Arrange, Act, Assert
3. **Mock External Dependencies**: Use `@patch` for external services
4. **Test Edge Cases**: Include tests for error conditions
5. **Keep Tests Independent**: Each test should run independently
6. **Use Fixtures**: Reuse common setup code with fixtures

## 🔧 Continuous Integration

### Running Tests in CI/CD

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    pip install -r requirements-test.txt
    pytest --cov=src/privacy --cov-report=xml --cov-fail-under=75
```

## 📝 Test Coverage Report

After running tests with coverage, you'll get:

1. **Terminal Output**: Quick summary with missing lines
2. **HTML Report**: Detailed, browsable coverage at `htmlcov/index.html`
3. **XML Report**: For CI/CD integration at `coverage.xml`

## 🐛 Debugging Tests

### Run Tests with Print Statements
```bash
pytest -s tests/unit/test_encrypt.py
```

### Run Tests with Debugging
```bash
pytest --pdb tests/unit/test_encrypt.py
```

### Run Tests with Increased Verbosity
```bash
pytest -vv tests/unit/test_encrypt.py
```

### Show Local Variables on Failure
```bash
pytest -l tests/unit/test_encrypt.py
```

## ⚡ Performance Testing

### Run Tests in Parallel
```bash
pytest -n auto
```

### Run with Timeout
```bash
pytest --timeout=300
```

### Benchmark Tests
```bash
pytest --benchmark-only
```

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Python Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

## 🤝 Contributing

When adding new tests:
1. Place unit tests in `tests/unit/`
2. Place integration tests in `tests/integration/`
3. Use appropriate markers (`@pytest.mark.unit`, etc.)
4. Ensure tests pass locally before committing
5. Maintain or improve code coverage

## ⚠️ Known Issues

- Some tests require ML models to be downloaded
- Database tests require PostgreSQL to be running
- Image processing tests require OpenCV

## 📧 Support

For questions about tests, please contact the development team or open an issue in the project repository.
