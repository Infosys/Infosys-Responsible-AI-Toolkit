"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from fairness.config.logger import CustomLogger
from fairness.dao.WorkBench.databaseconnection import DataBase_WB
from gridfs.errors import NoFile, FileExists
from gridfs import GridFS
import shutil
import os
from dotenv import load_dotenv
load_dotenv()
from fairness.config.logger import CustomLogger
from fairness.dao.databaseconnection import DataBase
import datetime
import time

log = CustomLogger()



class FileStore:
    
    #fs = GridFS(devraidb)
    # Create a MongoDB database instance
    ModelWorkBench = DataBase_WB()
    fs = GridFS(ModelWorkBench.db)

    def getfilename(self,unique_id: str):
            try:
                # Find the file in the database
                file_metadata = FileStoreReportDb.fs.find_one({"_id": unique_id})
                if file_metadata:

                    filename = file_metadata.filename
                return filename
            except NoFile:
                raise FileNotFoundError(f"No file found with unique ID {unique_id}")


    @staticmethod
    def read_file(unique_id: str):

            try:
                # file_metadata = FileStoreReportDb().fs.find_one({"_id": unique_id, "contentType": file_type})
                file_metadata = FileStoreReportDb().fs.find_one({"_id": unique_id})
                # Check if the file was found
                if file_metadata is None:
                    raise FileNotFoundError(f"No file found with unique ID {unique_id} and type {file_type}")
                
                # Get the file from the database
                file_content = FileStoreReportDb().fs.get(file_metadata._id)
                
                return {"data": file_content, "name":file_metadata.filename, "extension": file_metadata.filename.split('.')[-1],"contentType":file_metadata.content_type}
            except NoFile:
                raise FileNotFoundError(f"No file found with unique ID {unique_id} and type {file_type}")


    def save_local_file(self,filePath,fileType):
            
            if os.path.exists(filePath):
                if os.path.getsize(filePath)<=0:
                    raise ValueError("File content cannot be None")
            else:
                raise FileNotFoundError("No file found with the name "+filePath.split("/")[-1]+" locally")
            with open(filePath,'rb') as f:
                file_id=FileStore.fs.put(f,filename=filePath.split('/')[-1],content_type=fileType)
            return file_id

