"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
SERVICE_UPLOAD_FILE_METADATA = {
                "tenetName": "Fairness",
                "errorCode": "Upload_file-500",
                "errorMessage": "CustomValueError",
                "apiEndPoint": "/fairness/bias/getDataset",
                "errorRequestMethod": "POST"
            }

SERVICE_UPD_GETATTRIBUTE_METADATA = {
                "tenetName": "Fairness",
                "errorCode": "return_protected_attrib-500",
                "errorMessage": "CustomValueError",
                "apiEndPoint": "/fairness/bias/getAttributes",
                "errorRequestMethod": "POST"
            }

SERVICE_attributes_Data_METADATA = {
                "tenetName": "Fairness",
                "errorCode": "attributes_Data-500",
                "errorMessage": "CustomValueError",
                "apiEndPoint": "/fairness/bias/Workbench/fileid",
                "errorRequestMethod": "POST"
            }

SERVICE_return_protected_attrib_DB_METADATA = {
                "tenetName": "Fairness",
                "errorCode": "return_protected_attrib_DB-500",
                "errorMessage": "CustomValueError",
                "apiEndPoint": "/fairness/bias/UIworkbench/batchId/Attributes",
                "errorRequestMethod": "POST"
            }

SERVICE_getLabels_METADATA = {
                "tenetName": "Fairness",
                "errorCode": "getLabels-500",
                "errorMessage": "CustomValueError",
                "apiEndPoint": "fairness/individual/bias/getlabels",
                "errorRequestMethod": "POST"
            }

SERVICE_getScore_METADATA = {
                "tenetName": "Fairness",
                "errorCode": "getScore-500",
                "errorMessage": "CustomValueError",
                "apiEndPoint": "/fairness/individual/bias/getscore",
                "errorRequestMethod": "POST"
            }

SERVICE_upload_file_Premitigation_METADATA = {
                "tenetName": "Fairness",
                "errorCode": "upload_file_Premitigation-500",
                "errorMessage": "CustomValueError",
                "apiEndPoint": "/fairness/pretrain/mitigation/getDataset",
                "errorRequestMethod": "POST"
            }

SERVICE_return_pretrainMitigation_protected_attrib_METADATA = {
                "tenetName": "Fairness",
                "errorCode": "return_pretrainMitigation_protected_attrib-500",
                "errorMessage": "CustomValueError",
                "apiEndPoint": "/fairness/pretrain/mitigation/getAttributes",
                "errorRequestMethod": "POST"
            }

SERVICE_upload_file_singleendpoint_METADATA = {
                "tenetName": "Fairness",
                "errorCode": "upload_file_singleendpoint-500",
                "errorMessage": "CustomValueError",
                "apiEndPoint": "/fairness/Analyse",
                "errorRequestMethod": "POST"
            }

SERVICE_upload_file_Premitigation_METADATA = {
                "tenetName": "Fairness",
                "errorCode": "upload_file_Premitigation-500",
                "errorMessage": "CustomValueError",
                "apiEndPoint": "/fairness/pretrainMitigate",
                "errorRequestMethod": "POST"
            }

SERVICE_getLabels_Individual_METADATA = {
                "tenetName": "Fairness",
                "errorCode": "getLabels_Individual-500",
                "errorMessage": "CustomValueError",
                "apiEndPoint": "/fairness/IndividualMetrics",
                "errorRequestMethod": "POST"
            }

SERVICE_Internal_METADATA = {
                "tenetName": "Fairness",
                "errorCode": "internalserver-500",
                "errorMessage": "Internal server error occured",
                "apiEndPoint": "Check the API endpoint",
                "errorRequestMethod": "POST"
            }

workbench_preprocess_labels = {
                "tenetName": "Fairness",
                "errorCode": "workbench_preprocess_labels-500",
                "errorMessage": "Internal server error occured",
                "apiEndPoint": "/fairness/preprocessing/mitigation/get_data",
                "errorRequestMethod": "POST"
            }

workbench_preprocess_get_batchId = {
                "tenetName": "Fairness",
                "errorCode": "workbench_preprocess_get_batchId-500",
                "errorMessage": "Internal server error occured",
                "apiEndPoint": "/fairness/bias/workbench/analyze/batchId/Attributes",
                "errorRequestMethod": "POST"
            }

workbenchAnalyse_get_data = {
                "tenetName": "Fairness",
                "errorCode": "workbenchAnalyse_get_data-500",
                "errorMessage": "Internal server error occured",
                "apiEndPoint": "/fairness/bias/Workbench/analyse/uploadfile",
                "errorRequestMethod": "POST"
            }

workbench_Analyse = {
                "tenetName": "Fairness",
                "errorCode": "internalserver-500",
                "errorMessage": "Internal server error occured",
                "apiEndPoint": "/fairness/bias/workbench/analyze/batchId/Attributes",
                "errorRequestMethod": "POST"
            }

inprocess_uploadfile = {
                "tenetName": "Fairness",
                "errorCode": "inprocess_get_data-500",
                "errorMessage": "Internal server error occured",
                "apiEndPoint": "/fairness/Workbench/inprocessing_uploadfile",
                "errorRequestMethod": "POST"
}

inprocess_get_data = {
                "tenetName": "Fairness",
                "errorCode": "inprocess_get_data-500",
                "errorMessage": "Internal server error occured",
                "apiEndPoint": "/fairness/Workbench/inprocessing",
                "errorRequestMethod": "POST"
}

text_openai_keys = {
                "tenetName": "Fairness",
                "errorCode": "openai-500",
                "errorMessage": "OPEN_AI key was not found",
                "apiEndPoint": "/fairness/analysis/llm",
                "errorRequestMethod": "POST"
}

image_openai_keys = {
                "tenetName": "Fairness",
                "errorCode": "openai-500",
                "errorMessage": "OPEN_AI key was not found",
                "apiEndPoint": "/fairness/analysis/image",
                "errorRequestMethod": "POST"
}

wraper_batch = {
                "tenetName": "Fairness",
                "errorCode": "openai-500",
                "errorMessage": "OPEN_AI key was not found",
                "apiEndPoint": "/fairness/wrapper/batchId",
                "errorRequestMethod": "POST"
}

Wrapper_download = {
                "tenetName": "Fairness",
                "errorCode": "openai-500",
                "errorMessage": "OPEN_AI key was not found",
                "apiEndPoint": "/fairness/wrapper/download",
                "errorRequestMethod": "POST"
}