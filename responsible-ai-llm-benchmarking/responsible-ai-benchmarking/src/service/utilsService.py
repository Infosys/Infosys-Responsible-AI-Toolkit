"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from trustllm.task import fairness
from trustllm.utils import file_process
from trustllm import config
from trustllm.generation import generation
from trustllm.task.pipeline import run_fairness
import os
import json
from trustllm.dataset_download import download_dataset
from config.logger import CustomLogger
import logging
import zipfile
import tqdm

# log=CustomLogger()
# logging.basicConfig(
#     level=logging.DEBUG,  # Set the desired logging level
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Specify the file name for the log file
#       #     Set the file mode to 'w' for overwriting or 'a' for appending
# )
# Create a logger instance
# log = logging.getLogger()
class Utils:
    def __init__(self):
        pass
    def countRes(json_object):
        count=0
        for cell in json_object:
            if "res" in cell:
                count+=1
        return count
        
    @staticmethod
    def getStatus(dataset_name):
        #get count of all the generated res from json i.e. count of all the "res" key
        base_dir=os.path.join("generation_results/datasets",os.path.join(dataset_name,"fairness"))
        if not os.path.exists(base_dir):
            return "dataset does not exists"
        #get all the json file path
        count=0
        #convert json file path into json object and get count of res
        for file in file_list:
            f = open(os.path.join(base_dir,file),) 
            json_object=json.load(f)
            count+=Utils.countRes(json_object)
        print(count)
        return count
    
    @staticmethod
    def getLogs():
        return "huggingface_evaluator.log"
    
    @staticmethod
    def getDataset(dataset_name):
        base_dir=os.path.join("generation_results/datasets",dataset_name)
        zip_path=os.path.join("output","file.zip")
        with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    zipf.write(os.path.join(root,file),os.path.relpath(os.path.join(root,file),os.path.join(base_dir,'..')))
        return zip_path
    
    @staticmethod
    def removeNullValues(dataset_path,test_type):
        #remove the null values if any in the datasets and write it back to the file.
        with open(os.path.join(dataset_path,test_type), 'r',encoding='utf-8') as f:
            json_file=json.load(f)
        for i in tqdm(range(0, len(json_file), 1), desc=f"Removing null objects from {test_type}", leave=False):
            if any(value is None for value in json_file[i].values()):
                json_file.remove(json_file[i])
        with open(os.path.join(dataset_path,test_type), 'w',encoding='utf-8') as f:
            json.dump(json_file, f) 

        
    
