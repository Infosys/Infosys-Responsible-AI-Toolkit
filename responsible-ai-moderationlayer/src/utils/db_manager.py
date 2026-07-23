'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""
Database Connection Manager

This module provides a centralized database connection management system
with proper connection pooling, error handling, and resource cleanup.
"""

import os
import pymongo
import urllib.parse
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from typing import Optional, Dict, Any
import threading
import time

from config.logger import CustomLogger
from config.constants import DatabaseConstants, ProcessingConstants

log = CustomLogger()

class DatabaseConnectionError(Exception):
    """Custom exception for database connection errors."""
    pass

class DatabaseManager:
    """
    Centralized database connection manager with connection pooling
    and proper resource management.
    """
    
    _instance = None
    _lock = threading.Lock()
    _connections = {}
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the database manager."""
        if not self._initialized:
            self._initialized = True
            self.db_type = os.getenv("DBTYPE", "False")
            self.db_name = os.getenv("APP_MONGO_DBNAME")
            self._setup_connections()
    
    def _setup_connections(self):
        """Setup database connections based on configuration."""
        if self.db_type == "False":
            log.info("Database connections disabled")
            return
            
        try:
            if self.db_type == DatabaseConstants.MONGODB:
                self._setup_mongodb()
            elif self.db_type == DatabaseConstants.POSTGRESQL:
                self._setup_postgresql()
            elif self.db_type == DatabaseConstants.COSMOSDB:
                self._setup_cosmosdb()
            else:
                raise DatabaseConnectionError(f"Unsupported database type: {self.db_type}")
                
        except Exception as e:
            log.error(f"Failed to setup database connections: {e}")
            raise DatabaseConnectionError(f"Database setup failed: {e}")
    
    def _setup_mongodb(self):
        """Setup MongoDB connection."""
        try:
            connection_string = self._get_mongodb_connection_string()
            client = pymongo.MongoClient(
                connection_string,
                maxPoolSize=ProcessingConstants.CONNECTION_POOL_SIZE,
                minPoolSize=1,
                maxIdleTimeMS=120000,
                serverSelectionTimeoutMS=ProcessingConstants.CONNECTION_TIMEOUT * 1000,
                socketTimeoutMS=ProcessingConstants.QUERY_TIMEOUT * 1000
            )
            
            # Test the connection
            client.admin.command('ping')
            
            self._connections['mongodb'] = client
            log.info("MongoDB connection established successfully")
            
        except Exception as e:
            log.error(f"MongoDB connection failed: {e}")
            raise DatabaseConnectionError(f"MongoDB connection failed: {e}")
    
    def _setup_postgresql(self):
        """Setup PostgreSQL connection with connection pooling."""
        try:
            connection_string = self._get_postgresql_connection_string()
            
            engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=ProcessingConstants.CONNECTION_POOL_SIZE,
                max_overflow=20,
                pool_timeout=ProcessingConstants.CONNECTION_TIMEOUT,
                pool_recycle=3600,  # 1 hour
                echo=False
            )
            
            # Test the connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                
            # Create tables if they don't exist
            self._create_postgresql_tables(engine)
            
            self._connections['postgresql'] = engine
            log.info("PostgreSQL connection established successfully")
            
        except Exception as e:
            log.error(f"PostgreSQL connection failed: {e}")
            raise DatabaseConnectionError(f"PostgreSQL connection failed: {e}")
    
    def _setup_cosmosdb(self):
        """Setup CosmosDB connection."""
        try:
            connection_string = os.getenv("COSMOS_PATH")
            if not connection_string:
                raise ValueError("COSMOS_PATH environment variable not set")
                
            client = pymongo.MongoClient(
                connection_string,
                maxPoolSize=ProcessingConstants.CONNECTION_POOL_SIZE,
                minPoolSize=1,
                serverSelectionTimeoutMS=ProcessingConstants.CONNECTION_TIMEOUT * 1000,
                socketTimeoutMS=ProcessingConstants.QUERY_TIMEOUT * 1000
            )
            
            # Test the connection
            client.admin.command('ping')
            
            self._connections['cosmosdb'] = client
            log.info("CosmosDB connection established successfully")
            
        except Exception as e:
            log.error(f"CosmosDB connection failed: {e}")
            raise DatabaseConnectionError(f"CosmosDB connection failed: {e}")
    
    def _get_mongodb_connection_string(self) -> str:
        """Generate MongoDB connection string based on vault configuration."""
        vault = os.getenv("ISVAULT", "False")
        
        if vault == "True":
            # Use vault for credentials
            username, password = self._get_vault_credentials()
        else:
            # Use environment variables
            username = os.getenv("DB_USERNAME")
            password = os.getenv("DB_PWD")
        
        if not username or not password:
            raise ValueError("Database credentials not available")
            
        encoded_password = urllib.parse.quote(password, safe='')
        host = os.getenv("APP_MONGO_HOST")
        
        if not host:
            # Fallback to MONGO_PATH for local development
            mongo_path = os.getenv("MONGO_PATH")
            if mongo_path:
                return mongo_path
            raise ValueError("Database host configuration not found")
        
        auth_mechanism = "SCRAM-SHA-256"
        return f"mongodb://{username}:{encoded_password}@{host}/?authMechanism={auth_mechanism}&authSource={self.db_name}"
    
    def _get_postgresql_connection_string(self) -> str:
        """Generate PostgreSQL connection string."""
        vault = os.getenv("ISVAULT", "False")
        
        if vault == "True":
            username, password = self._get_vault_credentials()
        else:
            username = os.getenv("DB_USERNAME")
            password = os.getenv("DB_PWD")
        
        if not username or not password:
            raise ValueError("Database credentials not available")
            
        host_port = os.getenv("APP_MONGO_HOST", "localhost:5432")
        host, port = host_port.split(":") if ":" in host_port else (host_port, "5432")
        
        return f"postgresql://{username}:{password}@{host}:{port}/{self.db_name}"
    
    def _get_vault_credentials(self) -> tuple:
        """Get credentials from vault (placeholder implementation)."""
        # This is a simplified version - in production, implement proper vault integration
        # For now, return environment fallback
        username = os.getenv("DB_USERNAME")
        password = os.getenv("DB_PWD")
        
        if not username or not password:
            raise ValueError("Vault credentials not available and no fallback found")
            
        return username, password
    
    def _create_postgresql_tables(self, engine):
        """Create PostgreSQL tables if they don't exist."""
        create_moderation_table = '''
            CREATE TABLE IF NOT EXISTS ModerationResult (
                id VARCHAR(50) PRIMARY KEY,
                payload JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
        
        create_log_table = '''
            CREATE TABLE IF NOT EXISTS log_db (
                id VARCHAR(50) PRIMARY KEY,
                error JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
        
        with engine.connect() as conn:
            conn.execute(text(create_moderation_table))
            conn.execute(text(create_log_table))
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """
        Get a database connection using context manager for proper cleanup.
        
        Usage:
            with db_manager.get_connection() as conn:
                # Use connection
                pass
        """
        if self.db_type == "False":
            raise DatabaseConnectionError("Database connections are disabled")
        
        connection = None
        try:
            if self.db_type == DatabaseConstants.MONGODB:
                connection = self._connections['mongodb'][self.db_name]
            elif self.db_type == DatabaseConstants.POSTGRESQL:
                connection = self._connections['postgresql'].connect()
            elif self.db_type == DatabaseConstants.COSMOSDB:
                connection = self._connections['cosmosdb'][self.db_name]
            else:
                raise DatabaseConnectionError(f"Unsupported database type: {self.db_type}")
                
            yield connection
            
        except Exception as e:
            log.error(f"Database operation failed: {e}")
            raise
        finally:
            # Clean up connection for PostgreSQL
            if connection and self.db_type == DatabaseConstants.POSTGRESQL:
                connection.close()
    
    def get_database(self):
        """Get database instance for MongoDB/CosmosDB."""
        if self.db_type == "False":
            raise DatabaseConnectionError("Database connections are disabled")
            
        if self.db_type in [DatabaseConstants.MONGODB, DatabaseConstants.COSMOSDB]:
            db_key = 'mongodb' if self.db_type == DatabaseConstants.MONGODB else 'cosmosdb'
            return self._connections[db_key][self.db_name]
        else:
            raise DatabaseConnectionError(f"get_database() not supported for {self.db_type}")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on database connections."""
        health_status = {
            "database_type": self.db_type,
            "status": "unknown",
            "details": {}
        }
        
        if self.db_type == "False":
            health_status["status"] = "disabled"
            return health_status
        
        try:
            start_time = time.time()
            
            if self.db_type == DatabaseConstants.MONGODB:
                client = self._connections['mongodb']
                client.admin.command('ping')
                
            elif self.db_type == DatabaseConstants.POSTGRESQL:
                engine = self._connections['postgresql']
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                    
            elif self.db_type == DatabaseConstants.COSMOSDB:
                client = self._connections['cosmosdb']
                client.admin.command('ping')
            
            response_time = time.time() - start_time
            health_status.update({
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "details": {
                    "connection_active": True,
                    "database_name": self.db_name
                }
            })
            
        except Exception as e:
            health_status.update({
                "status": "unhealthy",
                "error": str(e),
                "details": {
                    "connection_active": False
                }
            })
            
        return health_status
    
    def close_connections(self):
        """Close all database connections."""
        for db_type, connection in self._connections.items():
            try:
                if hasattr(connection, 'close'):
                    connection.close()
                elif hasattr(connection, 'dispose'):  # SQLAlchemy engine
                    connection.dispose()
                log.info(f"Closed {db_type} connection")
            except Exception as e:
                log.error(f"Error closing {db_type} connection: {e}")

# Global database manager instance
db_manager = DatabaseManager()
