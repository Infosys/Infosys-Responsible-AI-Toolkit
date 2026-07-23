# Responsible AI Steganography Detection

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Detection Techniques](#detection-techniques)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Integration](#integration)
- [Security Considerations](#security-considerations)
- [License](#license)
- [Contact](#contact)

## Introduction

The **Responsible AI Steganography Detection** module is a comprehensive text-based steganography detection service that identifies hidden messages and covert communication attempts in textual inputs. This module is part of the Infosys Responsible AI Toolkit and provides advanced detection capabilities for various steganographic techniques.

Steganography in text involves hiding information within seemingly normal text content using techniques such as zero-width characters, whitespace manipulation, linguistic patterns, and Unicode exploitation. This module helps identify and prevent such covert communication channels in AI systems.

## Features

### 🔍 Multi-Technique Detection
- **Zero-Width Character Detection**: Identifies invisible Unicode characters used for data hiding
- **Whitespace Pattern Analysis**: Detects suspicious spacing and trailing whitespace patterns
- **Linguistic Steganography**: Analyzes text patterns for systematic encoding schemes
- **Character Frequency Analysis**: Identifies anomalous character distributions
- **Unicode Exploitation Detection**: Detects homograph attacks and suspicious Unicode usage

### 🚀 High-Performance API
- RESTful API with comprehensive Swagger documentation
- Single text and batch processing capabilities
- Real-time detection with millisecond response times
- Configurable sensitivity thresholds
- Detailed analysis results and security recommendations

### 🛡️ Enterprise-Ready
- Comprehensive test coverage (unit and integration tests)
- Configurable security settings
- Rate limiting and input validation
- Error handling and logging
- Compatible with existing Responsible AI Toolkit architecture

## Detection Techniques

### 1. Zero-Width Character Detection

Identifies hidden messages encoded using invisible Unicode characters:

- Zero Width Space (U+200B)
- Zero Width Non-Joiner (U+200C)
- Zero Width Joiner (U+200D)
- Word Joiner (U+2060)
- Other invisible Unicode characters

**Example Detection:**
```python
# Text with hidden zero-width characters
text = "Normal text\u200Bwith\u200Bhidden\u200Bmessage"
# Detection confidence: 60-100% depending on pattern complexity
```

### 2. Whitespace Pattern Analysis

Detects suspicious whitespace usage patterns:

- Excessive trailing spaces on lines
- Unusual spacing patterns between words
- Systematic whitespace encoding schemes

### 3. Linguistic Steganography

Analyzes linguistic patterns for hidden encoding:

- First letter frequency analysis
- Capitalization pattern detection
- Word choice entropy analysis
- Systematic linguistic encoding

### 4. Character Frequency Analysis

Identifies anomalous character frequency distributions:

- Space frequency deviation from normal English
- Vowel frequency analysis
- Detection of non-printable characters
- Statistical anomaly detection

### 5. Unicode Exploitation Detection

Detects malicious Unicode usage:

- Homograph attacks (look-alike characters)
- Suspicious Unicode ranges
- Character substitution attacks
- Mixed script detection

## Prerequisites

1. **Python 3.11+** installed and configured
2. **pip** package manager
3. **Virtual environment** (recommended)
4. **Flask** and related dependencies (see requirements.txt)

## Installation

### Step 1: Clone the Repository
```bash
cd responsible-ai-steganography
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
cd requirements
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
cd ../src
cp .env .env.local  # Copy and customize environment settings
```

## Configuration

### Environment Variables

Configure the following variables in your `.env` file:

```bash
# Application Configuration
DEBUG=False
SECRET_KEY=your-secret-key-here
HOST=0.0.0.0
PORT=5001

# CORS Configuration
CORS_ORIGINS=*

# Detection Sensitivity (0-100)
ZERO_WIDTH_SENSITIVITY=20
WHITESPACE_SENSITIVITY=30
LINGUISTIC_SENSITIVITY=25
FREQUENCY_SENSITIVITY=15
UNICODE_SENSITIVITY=30

# Performance Settings
MAX_TEXT_LENGTH=100000
MAX_BATCH_SIZE=100
PROCESSING_TIMEOUT_SECONDS=30
```

### Sensitivity Configuration

Each detection technique has configurable sensitivity thresholds:

- **Lower values** (10-30): More sensitive, may produce false positives
- **Medium values** (30-50): Balanced detection
- **Higher values** (50-80): Less sensitive, fewer false positives

## Running the Application

### Development Mode
```bash
cd src
python main.py
```

### Production Mode
```bash
# Set production environment
export DEBUG=False
export SECRET_KEY=your-production-secret-key

# Run with Gunicorn (recommended)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 main:app
```

### Docker Deployment
```bash
# Build Docker image
docker build -t responsible-ai-steganography .

# Run container
docker run -p 5001:5001 responsible-ai-steganography
```

The service will be available at:
- **API Base URL**: `http://localhost:5001/rai/v1/steganography/`
- **Swagger Documentation**: `http://localhost:5001/rai/v1/steganography/`
- **Health Check**: `http://localhost:5001/health`

## API Documentation

### Single Text Detection

**Endpoint**: `POST /rai/v1/steganography/detect`

**Request**:
```json
{
  "text": "Text to analyze for steganography",
  "user_id": "optional_user_identifier",
  "metadata": {
    "source": "optional_metadata"
  }
}
```

**Response**:
```json
{
  "success": true,
  "result": {
    "is_suspicious": true,
    "confidence_score": 75,
    "detected_techniques": ["zero_width", "unicode"],
    "details": {
      "zero_width": {
        "is_suspicious": true,
        "confidence": 60,
        "found_characters": [...],
        "binary_pattern": "01010101"
      },
      "unicode": {
        "is_suspicious": true,
        "confidence": 30,
        "exploits": [...]
      }
    },
    "recommendations": [
      "Remove or validate zero-width Unicode characters in input text",
      "Implement Unicode normalization before processing"
    ]
  },
  "processing_time_ms": 12.5,
  "timestamp": "2025-01-15 14:30:25 UTC"
}
```

### Batch Detection

**Endpoint**: `POST /rai/v1/steganography/detect/batch`

**Request**:
```json
{
  "texts": [
    {
      "text": "First text to analyze",
      "id": "text_1",
      "metadata": {}
    },
    {
      "text": "Second text to analyze",
      "id": "text_2"
    }
  ],
  "user_id": "batch_user"
}
```

### Supported Techniques

**Endpoint**: `GET /rai/v1/steganography/techniques`

Returns information about all supported detection techniques.

### Health Check

**Endpoint**: `GET /rai/v1/steganography/health`

Returns service health status and version information.

## Testing

### Run Unit Tests
```bash
cd tests
pytest test_steganography_detection.py -v
```

### Run API Tests
```bash
pytest test_steganography_api.py -v
```

### Run All Tests with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Test Examples

```python
# Test zero-width character detection
def test_zero_width_detection():
    service = SteganographyDetectionService()
    text = "Hidden\u200Bmessage\u200Bhere"
    result = service.detect_steganography(text)
    assert result['is_suspicious'] == True
    assert 'zero_width' in result['detected_techniques']
```

## Integration

### Integration with Moderation Layer

The steganography detection module can be integrated with the existing moderation layer:

```python
# Add to moderation pipeline
from app.services.steganography_service import SteganographyDetectionService

stego_service = SteganographyDetectionService()

def enhanced_moderation_check(text):
    # Existing moderation checks
    moderation_result = existing_moderation(text)
    
    # Add steganography detection
    stego_result = stego_service.detect_steganography(text)
    
    if stego_result['is_suspicious']:
        moderation_result['steganography_detected'] = True
        moderation_result['steganography_confidence'] = stego_result['confidence_score']
        moderation_result['steganography_techniques'] = stego_result['detected_techniques']
    
    return moderation_result
```

### Integration with Admin Module

Configure detection thresholds via the admin interface:

```json
{
  "steganography_settings": {
    "zero_width_sensitivity": 25,
    "whitespace_sensitivity": 30,
    "enable_binary_extraction": true,
    "max_processing_time": 30
  }
}
```

## Security Considerations

### Input Validation
- Maximum text length limits (default: 100,000 characters)
- Batch size restrictions (default: 100 items)
- Content-Type validation
- Request timeout enforcement

### Rate Limiting
- Configurable rate limits per IP/user
- Burst protection
- Resource usage monitoring

### Privacy Protection
- No sensitive data logging
- Configurable data retention
- User consent compliance

### False Positive Management
- Adjustable sensitivity thresholds
- Whitelist capabilities for known safe patterns
- Context-aware detection

## Performance

### Benchmarks
- **Single text detection**: < 50ms for texts up to 10,000 characters
- **Batch processing**: < 5ms per item average
- **Memory usage**: < 100MB for typical workloads
- **Throughput**: > 1000 requests per minute

### Optimization Tips
- Use batch processing for multiple texts
- Adjust sensitivity thresholds based on use case
- Enable caching for repeated analysis
- Use appropriate hardware sizing

## Contributing

1. Follow the existing code structure and patterns
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure compatibility with the Responsible AI Toolkit
5. Follow security best practices

### Development Setup
```bash
# Install development dependencies
pip install -r requirements/requirements.txt

# Run linting
flake8 src/
black src/

# Run type checking
mypy src/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## Contact

For questions, support, or contributions:

- **Email**: Infosysraitoolkit@infosys.com
- **Documentation**: [Infosys Responsible AI Toolkit](https://infosys.github.io/Infosys-Responsible-AI-Toolkit/)
- **Issues**: Create issues in the main repository

---

**Note**: This module is designed to detect steganographic techniques and should be used as part of a comprehensive security strategy. Regular updates and threshold tuning may be required based on evolving attack vectors.
