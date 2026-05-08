"""
Integration Tests Module

This module contains integration tests that use real database and filesystem.
These tests are separate from unit tests and require proper environment setup.

To run integration tests:
1. Ensure MongoDB is running and accessible
2. Set environment variables for test database:
   - DB_NAME="test_security_db"
   - TEST_DB="" (empty to use real DB)
   - DB_TYPE="mongo"
   - MONGO_PATH="mongodb://localhost:27017/" (or your connection string)
3. Run: pytest app/test/integration/ --cov=app/src

Note: Integration tests will create and delete test data in the database.
"""
