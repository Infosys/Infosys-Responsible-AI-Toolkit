'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os
import pymongo
import datetime
from config.logger import CustomLogger, request_id_var
import json
import requests
import hvac
import urllib.parse
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
import traceback
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
import time
from contextlib import contextmanager
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
import threading
from urllib.parse import quote_plus

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

log = CustomLogger()

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

request_id_var.set("Startup")

@dataclass
class DatabaseConfig:
    """Database configuration class"""
    db_type: str
    host: str
    username: str
    password: str
    database: str
    port: Optional[str] = None
    
    def validate(self):
        """Validate database configuration"""
        required_fields = ['db_type', 'host', 'database']
        for field in required_fields:
            if not getattr(self, field):
                raise ValueError(f"Missing required database configuration: {field}")
        
        if self.db_type == "cosmos" and os.getenv("COSMOS_PATH"):
            return
        
        if self.db_type == "mongo" and not self.username and not self.password:
            log.info("Local MongoDB connection without authentication")
            return
        
        if not self.username or not self.password:
            raise ValueError(f"Missing required database configuration: username or password")

class VaultManager(ABC):
    """Abstract base class for vault managers"""
    
    @abstractmethod
    def get_credentials(self) -> Dict[str, str]:
        pass

class HashiCorpVaultManager(VaultManager):
    """HashiCorp Vault manager"""
    
    def __init__(self):
        self.vault_url = os.getenv("APP_VAULT_URL")
        self.role_id = os.getenv("APP_VAULT_ROLE_ID")
        self.secret_id = os.getenv("APP_VAULT_SECRET_ID")
        self.vault_path = os.getenv("APP_VAULT_PATH")
        self.vault_backend = os.getenv("APP_VAULT_BACKEND")
        self.username_key = os.getenv("APP_VAULT_KEY_MONGOUSER")
        self.password_key = os.getenv("APP_VAULT_KEY_MONGOPASS")
        
    def get_credentials(self) -> Dict[str, str]:
        try:
            payload = {'role_id': self.role_id, 'secret_id': self.secret_id}
            response = requests.post(
                f"{self.vault_url}/v1/auth/approle/login",
                data=json.dumps(payload),
                timeout=10
            )
            response.raise_for_status()
            
            token = response.json()["auth"]["client_token"]
            log.info("Vault token generated successfully")
            
            client = hvac.Client(url=self.vault_url, token=token)
            secret = client.secrets.kv.v2.read_secret_version(
                path=self.vault_path,
                mount_point=self.vault_backend,
            )["data"]["data"]

            return {
                'username': secret[self.username_key],
                'password': secret[self.password_key]
            }
        except Exception as e:
            log.error(f"Error retrieving credentials from HashiCorp Vault: {e}")
            raise

class AzureVaultManager(VaultManager):
    """Azure Key Vault manager"""
    
    def __init__(self):
        self.tenant_id = os.getenv("AZURE_VAULT_TENANT_ID")
        self.client_id = os.getenv("AZURE_VAULT_CLIENT_ID")
        self.client_secret = os.getenv("VAULT_SECRET")
        self.vault_url = os.getenv("KEYVAULTURL")
        self.username_key = os.getenv("APP_VAULT_KEY_MONGOUSER")
        self.password_key = os.getenv("APP_VAULT_KEY_MONGOPASS")
        
    def get_credentials(self) -> Dict[str, str]:
        try:
            credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            sc = SecretClient(vault_url=self.vault_url, credential=credential)
            
            username = sc.get_secret(self.username_key).value
            password = sc.get_secret(self.password_key).value
            
            log.info("Retrieved credentials from Azure Key Vault")
            return {'username': username, 'password': password}
            
        except Exception as e:
            log.error(f"Error retrieving credentials from Azure Key Vault: {e}")
            raise

class DatabaseConnection(ABC):
    """Abstract base class for database connections"""
    
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def close(self):
        pass
    
    @abstractmethod
    def get_connection(self):
        pass

class MongoDBConnection(DatabaseConnection):
    """MongoDB connection manager"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.client = None
        self.database = None
        self._lock = threading.Lock()

    def connect(self):
        with self._lock:
            if self.client is None:
                try:
                    connection_string = self._build_mongo_connection_string()
                    
                    self.client = pymongo.MongoClient(connection_string)
                    self.database = self.client[self.config.database]
                    
                    log.info("MongoDB client connection established")
                    log.info(f"dbname : {self.config.database}")
                    
                    self.client.admin.command('ping')
                    log.info(f"MongoDB connection established to {self.config.host}")
                    
                except Exception as e:
                    log.error(f"Error connecting to MongoDB: {e}")
                    raise
    
    def _build_mongo_connection_string(self) -> str:
        """Build MongoDB connection string securely"""
        if self.config.db_type == "cosmos" and os.getenv("COSMOS_PATH"):
            return os.getenv("COSMOS_PATH")
        
        # Check if we have valid credentials (not empty or placeholder values)
        has_valid_credentials = (
            self.config.username and self.config.password and 
            len(self.config.username.strip()) > 0 and 
            len(self.config.password.strip()) > 0 and
            not self.config.username.startswith("default") and
            not self.config.password.startswith("default")
        )
        
        if has_valid_credentials:
            
            self._validate_mongo_params()
            
            encoded_auth_token = quote_plus(self.config.password)
            encoded_username = quote_plus(self.config.username)
            sanitized_host = self._sanitize_mongo_host(self.config.host)
            sanitized_database = quote_plus(self.config.database)
            
            if self.config.db_type == "mongo":
                return (
                    f"mongodb://{encoded_username}:{encoded_auth_token}@{sanitized_host}/"
                    f"?authMechanism=SCRAM-SHA-256&authSource={sanitized_database}"
                    "&connectTimeoutMS=10000&serverSelectionTimeoutMS=10000"
                )
            else:
                return (
                    f"mongodb://{encoded_username}:{encoded_auth_token}@{sanitized_host}/"
                    f"?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000"
                    f"&appName=@{encoded_username}&connectTimeoutMS=10000&serverSelectionTimeoutMS=10000"
                )
        else:
            host = self.config.host if self.config.host else "localhost:27017"
            return f"mongodb://{self._sanitize_mongo_host(host)}/"

    def _validate_mongo_params(self):
        """Validate MongoDB connection parameters"""
        import re
        if not re.match(r'^[a-zA-Z0-9_.-]+$', self.config.username):
            raise ValueError(f"Invalid MongoDB username: {self.config.username}")
        if not re.match(r'^[a-zA-Z0-9_.-]+$', self.config.database):
            raise ValueError(f"Invalid MongoDB database name: {self.config.database}")

    def _sanitize_mongo_host(self, host: str) -> str:
        """Sanitize MongoDB host parameter"""
        import re
        if not re.match(r'^[a-zA-Z0-9.-]+:[0-9]+$', host) and not re.match(r'^[a-zA-Z0-9.-]+$', host):
            raise ValueError(f"Invalid MongoDB host format: {host}")
        return host   
    
    def close(self):
        with self._lock:
            if self.client:
                self.client.close()
                self.client = None
                self.database = None
                log.info("MongoDB connection closed")
    
    def get_connection(self):
        if self.database is None:
            self.connect()
        return self.database

class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL connection manager using SQLAlchemy"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = None
        self._lock = threading.Lock()
        
    def connect(self):
        with self._lock:
            if self.engine is None:
                try:
                    if not self._validate_connection_params():
                        raise ValueError("Invalid connection parameters")
                    
                    encoded_auth_token = quote_plus(self.config.password)
                    encoded_username = quote_plus(self.config.username)
                    encoded_database = quote_plus(self.config.database)
                    
                    host_parts = self.config.host.split(":")
                    host = self._sanitize_host(host_parts[0])
                    port = self._sanitize_port(host_parts[1] if len(host_parts) > 1 else "5432")
                    
                    connection_string = (
                        f"postgresql://{encoded_username}:{encoded_auth_token}@{host}:{port}/{encoded_database}"
                        "?connect_timeout=10"
                    )
                    
                    self.engine = create_engine(
                        connection_string,
                        poolclass=QueuePool,
                        pool_size=5,
                        max_overflow=10,
                        pool_pre_ping=True,
                        pool_recycle=3600
                    )
                    
                    with self.engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
                        self._create_tables(conn)
                        conn.commit()
                    
                    log.info(f"PostgreSQL connection established to {host}:{port}")
                    
                except Exception as e:
                    log.error(f"Error connecting to PostgreSQL: {e}")
                    raise
    
    def _validate_connection_params(self) -> bool:
        """Validate connection parameters to prevent injection"""
        import re
        
        if not re.match(r'^[a-zA-Z0-9_.-]+$', self.config.username):
            log.error(f"Invalid username format: {self.config.username}")
            return False
        
        if not re.match(r'^[a-zA-Z0-9_.-]+$', self.config.database):
            log.error(f"Invalid database name format: {self.config.database}")
            return False
        
        return True
    
    def _sanitize_host(self, host: str) -> str:
        """Sanitize host parameter"""
        import re
        if not re.match(r'^[a-zA-Z0-9.-]+$', host):
            raise ValueError(f"Invalid host format: {host}")
        return host

    def _sanitize_port(self, port: str) -> str:
        """Sanitize port parameter"""
        try:
            port_int = int(port)
            if not (1 <= port_int <= 65535):
                raise ValueError(f"Invalid port range: {port}")
            return str(port_int)
        except ValueError:
            raise ValueError(f"Invalid port format: {port}")
    
    def _create_tables(self, conn):
        """Create required tables if they don't exist"""
        create_moderation_table = '''
            CREATE TABLE IF NOT EXISTS ModerationResult (
                id VARCHAR(50) PRIMARY KEY,
                payload JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
        
        create_log_table = '''
            CREATE TABLE IF NOT EXISTS log_db (
                id VARCHAR(50) PRIMARY KEY,
                error JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
        
        conn.execute(text(create_moderation_table))
        conn.execute(text(create_log_table))
    
    def close(self):
        with self._lock:
            if self.engine:
                self.engine.dispose()
                self.engine = None
                log.info("PostgreSQL connection closed")
    
    def get_connection(self):
        if self.engine is None:
            self.connect()
        return self.engine

class DatabaseManager:
    """Centralized database manager"""
    
    def __init__(self):
        self.connection = None
        self.config = None
        self._lock = threading.Lock()
        
    def initialize(self):
        """Initialize database connection based on configuration"""
        try:
            self.config = self._get_database_config()
            self.config.validate()
            
            if self.config.db_type in ["mongo", "cosmos"]:
                self.connection = MongoDBConnection(self.config)
            elif self.config.db_type == "psql":
                self.connection = PostgreSQLConnection(self.config)
            else:
                raise ValueError(f"Unsupported database type: {self.config.db_type}")
            
            self.connection.connect()
            log.info(f"Database manager initialized for {self.config.db_type}")
            
        except Exception as e:
            log.error(f"Error initializing database manager: {e}")
            raise
    
    def _get_database_config(self) -> DatabaseConfig:
        """Get database configuration from environment and vault"""
        db_type = os.getenv("DBTYPE", "False")
        
        if db_type == "False":
            raise ValueError("Database is disabled")
        
        log.info(f"Database type: {db_type}")
        log.info(f"Vault enabled: {os.getenv('ISVAULT')}")
        log.info(f"Has COSMOS_PATH: {bool(os.getenv('COSMOS_PATH'))}")
        
        dbname = os.getenv("APP_MONGO_DBNAME", "")
        host = os.getenv("APP_MONGO_HOST", "")
        
        vault_enabled = os.getenv("ISVAULT") == "True"
        
        if vault_enabled:
            vault_name = os.getenv("VAULTNAME")
            log.info(f"Using vault: {vault_name}")
            
            if not vault_name:
                raise ValueError("VAULTNAME environment variable is required when ISVAULT=True. Set to 'HASHICORP' or 'AZURE'")
            
            if vault_name == "HASHICORP":
                vault_manager = HashiCorpVaultManager()
            elif vault_name == "AZURE":
                vault_manager = AzureVaultManager()
            else:
                raise ValueError(f"Unsupported vault type: {vault_name}. Supported types: HASHICORP, AZURE")
            
            credentials = vault_manager.get_credentials()
            username = credentials['username']
            password = credentials['password']
        else:
            username = os.getenv("DB_USERNAME", "")
            password = os.getenv("DB_PWD", "")
            
            log.info(f"Username provided: {bool(username)}")
            log.info(f"Password provided: {bool(password)}")
            
            if db_type == "cosmos" and os.getenv("COSMOS_PATH"):
                log.info("Using Cosmos DB with connection string")
                return DatabaseConfig(
                    db_type=db_type,
                    host=host or "cosmos.documents.azure.com",  
                    username="",  # Empty - credentials are in COSMOS_PATH connection string
                    password="",  # Empty - credentials are in COSMOS_PATH connection string
                    database=dbname or "defaultdb"
                )

            if db_type == "mongo" and not username and not password:
                log.info("Using local MongoDB without authentication")

            return DatabaseConfig(
                db_type=db_type,
                host=host or "localhost:27017", 
                username=username,
                password=password,
                database=dbname or "defaultdb"
            )
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager"""
        if self.connection is None:
            self.initialize()
        
        conn = self.connection.get_connection()
        try:
            yield conn
        except Exception as e:
            log.error(f"Database operation error: {e}")
            raise
        finally:
            pass
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

db_manager = DatabaseManager()

class DatabaseOperations:
    """Base class for database operations"""
    
    def __init__(self):
        pass
    
    def is_database_available(self) -> bool:
        """Check if database is available"""
        try:
            return (db_manager.connection is not None and 
                   db_manager.config is not None)
        except Exception:
            return False
    
    def _execute_mongo_operation(self, collection_name: str, operation: str, *args, **kwargs):
        """Execute MongoDB operation"""
        if not self.is_database_available():
            raise RuntimeError("Database not available")
            
        try:
            with db_manager.get_connection() as db:
                collection = db[collection_name]
                method = getattr(collection, operation)
                return method(*args, **kwargs)
        except Exception as e:
            log.error(f"MongoDB operation error in {collection_name}.{operation}: {e}")
            raise
    
    def _execute_postgres_operation(self, query: str, params: Dict[str, Any] = None):
        """Execute PostgreSQL operation"""
        if not self.is_database_available():
            raise RuntimeError("Database not available")
            
        try:
            with db_manager.get_connection() as engine:
                with engine.connect() as conn:
                    result = conn.execute(text(query), params or {})
                    conn.commit()
                    return result
        except Exception as e:
            log.error(f"PostgreSQL operation error: {e}")
            raise
        
class ProfaneWords(DatabaseOperations):
    """ProfaneWords database operations"""
    
    def findOne(self, id: str):
        try:
            if not self.is_database_available():
                log.warning("Database not available, skipping ProfaneWords.findOne operation")
                return None
                
            if db_manager.config.db_type == "psql":
                raise NotImplementedError("ProfaneWords not implemented for PostgreSQL")
            else:
                result = self._execute_mongo_operation("ProfaneWords", "find_one", {"_id": id})
                return AttributeDict(result) if result else None
        except Exception as e:
            log.error(f"Error in ProfaneWords.findOne: {e}")
            return None

class FeedbackDb(DatabaseOperations):
    """Feedback database operations"""
    
    def create(self, value: Dict[str, Any]):
        try:
            if not self.is_database_available():
                log.warning("Database not available, skipping FeedbackDb.create operation")
                return "Database not available"
                
            if db_manager.config.db_type == "psql":
                raise NotImplementedError("Feedback not implemented for PostgreSQL")
            else:
                result = self._execute_mongo_operation("feedback", "insert_one", value)
                return result.acknowledged
        except Exception as e:
            log.error(f"Error in FeedbackDb.create: {e}")
            return "Error creating feedback"

class Results(DatabaseOperations):
    """Results database operations"""
    
    def __init__(self):
        super().__init__()
    
    def findOne(self, id: str):
        try:
            if not self.is_database_available():
                log.warning("Database not available, skipping findOne operation")
                return None
                
            if db_manager.config.db_type == "psql":
                query = "SELECT payload FROM ModerationResult WHERE id = :id"
                result = self._execute_postgres_operation(query, {"id": id})
                row = result.fetchone()
                return AttributeDict(row[0]) if row else None
            else:
                result = self._execute_mongo_operation("Results", "find_one", {"_id": id})
                return AttributeDict(result) if result else None
        except Exception as e:
            log.error(f"Error in Results.findOne: {e}")
            return None
    
    def findall(self, query: Dict[str, Any]):
        try:
            if not self.is_database_available():
                log.warning("Database not available, skipping findall operation")
                return []
                
            if db_manager.config.db_type == "psql":
                sql_query = "SELECT payload FROM ModerationResult"
                result = self._execute_postgres_operation(sql_query)
                return [AttributeDict(row[0]) for row in result.fetchall()]
            else:
                results = self._execute_mongo_operation("Results", "find", query)
                return [AttributeDict(doc) for doc in results]
        except Exception as e:
            log.error(f"Error in Results.findall: {e}")
            return []
    
    def create(self, value, id: str, portfolio: str, accountname: str, user: str = None, lotnumber: str = None):
        if hasattr(request_id_var, 'set'):
            request_id_var.set(id)
        
        try:
            if not self.is_database_available():
                log.warning("Database not available, skipping create operation")
                return "Database not available"
            
            processed_value = None
            
            if isinstance(value, str):
                try:
                    processed_value = json.loads(value)
                except json.JSONDecodeError:
                    log.error(f"Invalid JSON string in create: {value}")
                    return "Invalid JSON"
            elif hasattr(value, 'json') and callable(getattr(value, 'json')):
                try:
                    processed_value = json.loads(value.json())
                except Exception as e:
                    log.error(f"Error calling json() method: {e}")
                    return "Error processing value"
            elif isinstance(value, dict):
                processed_value = value
            else:
                try:
                    processed_value = dict(value)
                except Exception as e:
                    log.error(f"Error converting value to dict: {e}")
                    return "Error converting value"
            
            if processed_value is None:
                log.error("Failed to process value in create method")
                return "Error processing value"
            
            doc_id = processed_value.get("uniqueid", id)
            mydoc = {
                "_id" if db_manager.config.db_type != "psql" else "id": doc_id,
                "created": processed_value.get("created", datetime.datetime.now().isoformat()),
                "portfolio": portfolio,
                "accountname": accountname,
                "lotnumber": lotnumber,
                "Moderations": processed_value.get("moderationResults", {})
            }
            
            if user:
                mydoc["user"] = user
            
            if db_manager.config.db_type == "psql":
                query = "INSERT INTO ModerationResult(id, payload) VALUES (:id, :payload)"
                self._execute_postgres_operation(query, {"id": doc_id, "payload": json.dumps(mydoc)})
                return "PtrnRecogCreatedData"
            else:
                result = self._execute_mongo_operation("Results", "insert_one", mydoc)
                return result.acknowledged
                
        except Exception as e:
            log.error(f"Error in Results.create: {e}")
            return "Error creating record"
    
    def createRequestPayload(self, endpoint: str, value, id: str, portfolio: str, accountname: str, user: str = None, lotnumber: str = None):
        if hasattr(request_id_var, 'set'):
            request_id_var.set(id)
            
        try:
            if not self.is_database_available():
                log.warning("Database not available, skipping createRequestPayload operation")
                return "Database not available"
                
            mydoc = {
                "id": id,
                "created": datetime.datetime.now(),
                "portfolio": portfolio,
                "accountname": accountname,
                "lotnumber": lotnumber,
                "Request Payload": value,
                "API": endpoint
            }
            
            if user:
                mydoc["user"] = user
            
            if db_manager.config.db_type == "psql":
                query = "INSERT INTO ModerationResult(id, payload) VALUES (:id, :payload)"
                self._execute_postgres_operation(query, {"id": id, "payload": json.dumps(mydoc)})
                return "PtrnRecogCreatedData"
            else:
                result = self._execute_mongo_operation("Results", "insert_one", mydoc)
                return result.acknowledged
                
        except Exception as e:
            log.error(f"Error in Results.createRequestPayload: {e}")
            return "Error creating request payload"
    
    def createlog(self, value: Dict[str, Any]):
        try:
            if not self.is_database_available():
                log.warning("Database not available, skipping createlog operation")
                return "Database not available"
                
            value["created"] = time.time()
            
            if db_manager.config.db_type == "psql":
                query = "INSERT INTO log_db(id, error) VALUES (:id, :error)"
                self._execute_postgres_operation(query, {"id": value["_id"], "error": json.dumps(value)})
                return "PtrnRecogCreatedData"
            else:
                result = self._execute_mongo_operation("Logdb", "insert_one", value)
                return result.acknowledged
                
        except Exception as e:
            log.error(f"Error in Results.createlog: {e}")
            return "Error creating log"
    
    def createwithfeedback(self, value: Dict[str, Any]):
        try:
            if not self.is_database_available():
                log.warning("Database not available, skipping createwithfeedback operation")
                return "Database not available"
                
            if db_manager.config.db_type == "psql":
                raise NotImplementedError("createwithfeedback not implemented for PostgreSQL")
            else:
                result = self._execute_mongo_operation("Results", "insert_one", value)
                return result.acknowledged
        except Exception as e:
            log.error(f"Error in Results.createwithfeedback: {e}")
            return "Error creating feedback"
    
    def update(self, query: Dict[str, Any], value: Dict[str, Any]):
        try:
            if not self.is_database_available():
                log.warning("Database not available, skipping update operation")
                return "Database not available"
                
            if db_manager.config.db_type == "psql":
                raise NotImplementedError("update not implemented for PostgreSQL")
            else:
                newvalues = {"$set": value}
                result = self._execute_mongo_operation("Results", "update_one", query, newvalues)
                return result.acknowledged
        except Exception as e:
            log.error(f"Error in Results.update: {e}")
            return "Error updating record"
    
    def delete(self, id: str):
        try:
            if not self.is_database_available():
                log.warning("Database not available, skipping delete operation")
                return "Database not available"
                
            if db_manager.config.db_type == "psql":
                query = "DELETE FROM ModerationResult WHERE id = :id"
                return self._execute_postgres_operation(query, {"id": id})
            else:
                return self._execute_mongo_operation("Results", "delete_one", {"_id": id})
        except Exception as e:
            log.error(f"Error in Results.delete: {e}")
            return "Error deleting record"
    
    def deleteMany(self, query: Dict[str, Any]):
        try:
            if not self.is_database_available():
                log.warning("Database not available, skipping deleteMany operation")
                return "Database not available"
                
            if db_manager.config.db_type == "psql":
                raise NotImplementedError("deleteMany not implemented for PostgreSQL")
            else:
                result = self._execute_mongo_operation("Results", "delete_many", query)
                return result.acknowledged
        except Exception as e:
            log.error(f"Error in Results.deleteMany: {e}")
            return "Error deleting records"
        
try:
    db_type = os.getenv("DBTYPE", "False")
    if db_type != "False":
        has_vault = os.getenv("ISVAULT") == "True"
        has_cosmos_path = bool(os.getenv("COSMOS_PATH"))
        has_credentials = bool(os.getenv("DB_USERNAME")) and bool(os.getenv("DB_PWD"))
        
        is_local_mongo = (db_type == "mongo" and 
                 (not os.getenv("DB_USERNAME") and not os.getenv("DB_PWD")) and
                 (not os.getenv("APP_MONGO_HOST") or 
                  os.getenv("APP_MONGO_HOST", "").startswith("localhost")))
        
        if has_vault or has_cosmos_path or has_credentials or db_type == "cosmos" or is_local_mongo:
            db_manager.initialize()
            log.info("Database manager initialized successfully")
        else:
            log.warning("Database configuration incomplete, skipping initialization")
            log.warning("Set ISVAULT=True with vault config, or provide DB_USERNAME/DB_PWD, or set COSMOS_PATH for Cosmos DB")
    else:
        log.info("Database disabled (DBTYPE=False)")
except Exception as e:
    log.error(f"Failed to initialize database manager: {e}")
    log.warning("Application will continue without database connectivity")

def get_results_instance():
    """Get a Results instance for the current thread"""
    return Results()

def get_profane_words_instance():
    """Get a ProfaneWords instance for the current thread"""
    return ProfaneWords()

def get_feedback_db_instance():
    """Get a FeedbackDb instance for the current thread"""
    return FeedbackDb()

profane_words = ProfaneWords()
feedbackdb = FeedbackDb()
results = Results()

def safe_create_request_payload(endpoint: str, value, id: str, portfolio: str, accountname: str, user: str = None, lotnumber: str = None):
    """Thread-safe wrapper for createRequestPayload"""
    try:
        results_instance = Results()
        return results_instance.createRequestPayload(endpoint, value, id, portfolio, accountname, user, lotnumber)
    except Exception as e:
        log.error(f"Error in safe_create_request_payload: {e}")
        return "Error creating request payload"

def safe_create_result(value, id: str, portfolio: str, accountname: str, user: str = None, lotnumber: str = None):
    """Thread-safe wrapper for create"""
    try:
        results_instance = Results()
        return results_instance.create(value, id, portfolio, accountname, user, lotnumber)
    except Exception as e:
        log.error(f"Error in safe_create_result: {e}")
        return "Error creating result"
