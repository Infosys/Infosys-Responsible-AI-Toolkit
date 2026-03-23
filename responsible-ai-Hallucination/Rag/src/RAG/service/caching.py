"""
SPDX-License-Identifier: MIT

Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from langchain.document_loaders import PyPDFLoader,DirectoryLoader, TextLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.chat_models import AzureChatOpenAI
import os
import shutil
import time
import uuid
from RAG.config.logger import CustomLogger,request_id_var
import traceback
import requests
import io
from RAG.service.service import cache,MAX_CACHE_SIZE,select_embeddingmodel
from RAG.dao.AdminDb import mydb, collection, fs, defaultfs
import pickle

log=CustomLogger()
request_id_var.set("Startup")

# llm = AzureChatOpenAI(deployment_name=os.getenv("OPENAI_MODEL"), temperature=1)
VECTORSTORE_BASE_DIR = "../data/vectorstores/"
dbtypename=os.getenv("DB_TYPE")

def caching(vectorestoreid,llmtype):
    """
    Caches the vectorstore for the given blob names.
    """
    try:
        if llmtype=="openai":
            if dbtypename=="mongo":
                vectorstore = pickle.loads(fs.get_last_version(_id=vectorestoreid+"vectorstore",filename="vectorstore.pkl").read())
            else:
                #########################
                # Define the filter to retrieve the document
                filter = {"id": vectorestoreid + "vectorstore"}
                document = collection.find_one(filter)
                if document:
                    vectorstore_binary = document["data"]
                    vectorstore = pickle.loads(vectorstore_binary)
                    print("Vectorstore retrieved successfully!")
                else:
                    print("Document not found!")
        else:
            vectorstore_path = f"{VECTORSTORE_BASE_DIR}{vectorestoreid}/"
            embedding_function = select_embeddingmodel(llmtype)
        
            # Load vectorstore using FAISS native method
            vectorstore = FAISS.load_local(
                vectorstore_path, 
                embedding_function, 
                allow_dangerous_deserialization=True
            )
            
            print(f"Vectorstore loaded successfully from: {vectorstore_path}")
        vs= vectorstore
        vectorindex=0
        if len(cache) == MAX_CACHE_SIZE:
            vectorindex=cache.popitem()[0]
        cache[id(vs)] = vs
        return id(vs),vectorindex
    
    except Exception as e:
        log.error("Failed at Vectorestore Caching")
        log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

def removeCache(id):
    """
    Removes the vectorstore from the cache.
    """
    try:
        if id in cache:
            cache.__delitem__(id)
            return id
        else:
            return -1
    except Exception as e:
        log.error("Failed at Remove caching")
        log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
