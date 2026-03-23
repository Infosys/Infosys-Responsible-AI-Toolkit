'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''



import pymongo
import datetime,time
from dotenv import load_dotenv
from app.config.logger import CustomLogger
from app.dao.DatabaseConnection import DB
from gridfs import GridFS
import shutil
import os
import requests
from app.utility.ssl_utils import get_ssl_verify
from gridfs.errors import NoFile

load_dotenv()
log = CustomLogger()

mydb = DB.connect()
if mydb is None:
    raise RuntimeError("Database connection failed for FileStoreDb")

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class FileStoreDb:

    fs = GridFS(mydb)
    db_type = (os.getenv('DB_TYPE') or 'mongo').lower()
    
    @classmethod
    def _generate_file_id(cls) -> str:
        """Generate a unique increasing-ish id (isolated to cut duplication)."""
        file_id = str(time.time())
        time.sleep(0.001)  
        return file_id

    @classmethod
    def read_file(cls, unique_id, container_name):
        """
        Dispatcher to backend-specific implementations (Mongo/GridFS vs Blob).
        """
        if cls.db_type == 'mongo':
            return cls._read_file_mongo(unique_id)
        return cls._read_file_blob(unique_id, container_name)

    @staticmethod
    def _read_file_mongo(unique_id):
        try:
            meta = FileStoreDb.fs.find_one({"_id": unique_id})
            if meta is None:
                raise FileNotFoundError(f"No file found with unique ID {unique_id}")
            return {"data": meta.read()}
        except NoFile:
            raise FileNotFoundError(f"No file found with unique ID {unique_id}")

    @staticmethod
    def _read_file_blob(unique_id, container_name):
        """Retrieve a blob from remote storage with TLS verification.

        Raises:
            ValueError: Missing required identifiers.
            RuntimeError: Remote server responded with non-200 or network failure.
        """
        download_file_api = os.getenv('AZURE_GET_API')
        if not download_file_api:
            raise ValueError("Environment variable AZURE_GET_API is not set")
        if not container_name or not unique_id:
            raise ValueError("container_name and unique_id must not be empty")

        try:
            response = requests.get(
                url=download_file_api,
                params={"container_name": container_name, "blob_name": unique_id},
                timeout=30,
                verify=get_ssl_verify()
            )
        except requests.RequestException as exc:
            raise RuntimeError(f"Blob download request failed: {exc}") from exc

        if response.status_code != 200:
            raise RuntimeError(
                f"Blob download failed: {download_file_api} returned {response.status_code}"
            )
        return {'data': response.content}

    @classmethod
    def findOne(cls, file_id):
        """Backward-compatible alias; prefer get_file."""
        return cls.get_file(file_id)

    @classmethod
    def get_file(cls, file_id):
        """Return single file (metadata + content) or None."""
        file = cls.fs.find_one({"_id": file_id})
        if not file:
            return None
        return {
            "fileName": file.filename,
            "data": file.read(),
            "type": file.content_type
        }

    @classmethod
    def _store_new_file(cls, file_id, file_obj):
        """Internal helper to create GridFS file."""
        with cls.fs.new_file(
            _id=file_id,
            filename=file_obj.filename,
            content_type=getattr(file_obj, "content_type", None)
        ) as f:
            file_obj.file.seek(0)
            shutil.copyfileobj(file_obj.file, f)
            return f._id

    @classmethod
    def create(cls, file_obj):
        """Create a new stored file; returns generated id."""
        file_id = cls._generate_file_id()
        return cls._store_new_file(file_id, file_obj)

    @classmethod
    def update(cls, file_id, file_obj):
        """Replace an existing file (delete + recreate)."""
        cls.delete(file_id)
        return cls._store_new_file(file_id, file_obj)

    @classmethod
    def delete(cls, file_id):
        """Delete a stored file (idempotent)."""
        if mydb is None:
            log.error("Delete called but database connection is None (file_id=%s)", file_id)
            return
        try:
            mydb['fs.files'].delete_many({'_id': file_id})
            mydb['fs.chunks'].delete_many({'files_id': file_id})
        except Exception as exc:
            log.error("Failed to delete file_id=%s from GridFS: %s", file_id, exc)
