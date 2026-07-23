'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""
Constants for the Responsible AI Moderation Layer

This module contains all constants used throughout the application to avoid
magic numbers and improve maintainability.
"""

class ProcessingConstants:
    """Constants for text processing operations."""
    
    # Text chunking configuration
    MAX_TOKENS_PER_CHUNK = 400
    DEFAULT_CHUNK_OVERLAP = 50
    
    # API timeout configurations
    DEFAULT_TIMEOUT = 30  # seconds
    EXTENDED_TIMEOUT = 60  # seconds for heavy operations
    
    # Retry configurations
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    EXPONENTIAL_BACKOFF_BASE = 2
    
    # Score thresholds
    DEFAULT_PII_THRESHOLD = 0.4
    TOXICITY_THRESHOLD = 0.6
    SIMILARITY_THRESHOLD = 0.8
    
    # Cache configurations
    DEFAULT_CACHE_TTL = 3600  # 1 hour in seconds
    DEFAULT_CACHE_SIZE = 1000  # maximum number of items
    
    # File size limits
    MAX_FILE_SIZE_MB = 50
    MAX_TEXT_LENGTH = 100000  # characters
    
    # Database configurations
    CONNECTION_POOL_SIZE = 10
    CONNECTION_TIMEOUT = 30
    QUERY_TIMEOUT = 60

class HttpConstants:
    """HTTP-related constants."""
    
    # Status codes
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    
    # Headers
    CONTENT_TYPE_JSON = "application/json"
    CONTENT_TYPE_FORM = "application/x-www-form-urlencoded"
    AUTHORIZATION_HEADER = "Authorization"
    BEARER_PREFIX = "Bearer "

class SecurityConstants:
    """Security-related constants."""
    
    # Token expiration
    TOKEN_EXPIRATION_BUFFER = 60  # seconds
    DEFAULT_TOKEN_EXPIRY = 3600  # 1 hour
    
    # Encryption
    DEFAULT_HASH_ROUNDS = 12
    
    # Rate limiting
    DEFAULT_RATE_LIMIT = 100  # requests per hour
    BURST_LIMIT = 20  # requests per minute

class LoggingConstants:
    """Logging-related constants."""
    
    # Log levels
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    
    # Log formats
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
    REQUEST_ID_PREFIX = "REQ_"

class DatabaseConstants:
    """Database-related constants."""
    
    # Collection/Table names
    MODERATION_RESULTS_COLLECTION = "ModerationResult"
    LOG_COLLECTION = "log_db"
    PROFANE_WORDS_COLLECTION = "ProfaneWords"
    
    # Database types
    MONGODB = "mongo"
    POSTGRESQL = "psql" 
    COSMOSDB = "cosmos"

class ModelConstants:
    """Model-related constants."""
    
    # Environment targets
    AZURE_ENV = "azure"
    AICLOUD_ENV = "aicloud"
    
    # Model names
    GPT4 = "gpt4"
    GPT3 = "gpt3"
    LLAMA3 = "Llama3-70b"
    GEMINI_FLASH = "Gemini-Flash"
    GEMINI_PRO = "Gemini-Pro"
    AWS_CLAUDE = "AWS_CLAUDE_V3_5"

class ValidationConstants:
    """Input validation constants."""
    
    # String length limits
    MAX_USERNAME_LENGTH = 50
    MAX_EMAIL_LENGTH = 254
    MIN_PASSWORD_LENGTH = 8
    MAX_DESCRIPTION_LENGTH = 500
    
    # List size limits
    MAX_MODERATION_CHECKS = 50
    MAX_ENTITY_LIST_SIZE = 100
    
    # Regex patterns (basic examples - should be more comprehensive in production)
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    UUID_PATTERN = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
