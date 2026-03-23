'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import zipfile
from explain.service.responsible_ai_explain import ResponsibleAIExplain
from explain.config.logger import CustomLogger, request_id_var
from explain.dao.workbench.FileStoreDb import fileStoreDb
from explain.dao.workbench.Model import Model, ModelAttributes, ModelAttributeValues
from explain.dao.workbench.Dataset import Dataset, DatasetAttributes, DatasetAttributeValues
from explain.dao.workbench.Tenet import Tenet
from explain.dao.workbench.Html import Html
from explain.dao.workbench.Batch import Batch
from explain.dao.workbench.Preprocessor import Preprocessor
from explain.dao.explainability.TblException import Tbl_Exception
from explain.dao.explainability.TblExplanationMethods import Tbl_Explanation_Methods
from explain.utils.report import Report
from explain.utils.create_csv import CreateCSV
from explain.mappers.mappers import GetExplanationMethodsResponse, GetExplanationResponse, GetReportResponse, ExplainabilityTabular_New
from io import  BytesIO
from datetime import datetime
import pandas as pd
import joblib
import keras
import time
import json
import os
import requests
import time

log = CustomLogger()

class Payload:
    def __init__(self, **entries):
        self.__dict__.update(entries)

class ExplainService:

    def save_as_json_file(fileName:str,content):
        with open(fileName, "w") as outfile:
            json.dump(content,outfile,indent=2)

    def save_as_file(filename:str, content):
        with open(filename,"wb") as outfile:
            outfile.write(content)
    
    def save_html_to_file(html_string, filename):
        with open(filename, 'w') as f:
            f.write(html_string)
    
    def get_explanation_methods(payload: dict):
        # Check if payload is not None and it contains 'modelId' and 'datasetId'
        if payload.modelId is None or '' or payload.datasetId is None or '':
            log.error("modelId and/or datasetId are missing")
            return GetExplanationMethodsResponse(status='FAILURE', 
                                                 message='modelId and/or datasetId are missing', 
                                                 dataType='',
                                                 methods=[])

        try:
            # Extract modelId and datasetId from the payload
            modelId = payload.modelId
            datasetId = payload.datasetId

            model_attribute_ids = ModelAttributes.find(model_attributes=['useModelApi'])
            model_attribute_values = ModelAttributeValues.find(batch_id=None, model_id=modelId, model_attribute_ids=model_attribute_ids)
            
            use_model_end_point = model_attribute_values[0]
            if use_model_end_point.lower() == 'yes':
                model_attribute_names = ['modelFramework','taskType']
                model_attribute_ids = ModelAttributes.find(model_attributes=model_attribute_names)
                model_attribute_values = ModelAttributeValues.find(batch_id=None, model_id=modelId, model_attribute_ids=model_attribute_ids)

                model_details = {'modelFramework': model_attribute_values[0],
                                 'taskType': model_attribute_values[1]}
            else:
                model_attribute_names = ['modelFramework', 'algorithm', 'taskType']
                model_attribute_ids = ModelAttributes.find(model_attributes=model_attribute_names)
                model_attribute_values = ModelAttributeValues.find(batch_id=None, model_id=modelId, model_attribute_ids=model_attribute_ids)

                model_details = {'modelFramework': model_attribute_values[0],
                                'algorithm': model_attribute_values[1],
                                'taskType': model_attribute_values[2]}
            
            dataset_attribute_ids = DatasetAttributes.find(dataset_attributes=['dataType'])
            dataType = DatasetAttributeValues.find(dataset_id=datasetId, dataset_attribute_ids=dataset_attribute_ids)
            
            dataset_details = {'dataType': dataType[0]}
            
            # Get the explanation methods for the given modelType, taskType, and dataType
            cursor = Tbl_Explanation_Methods.find_methods(model_framework=model_details['modelFramework'], 
                                                         task_type=model_details['taskType'], 
                                                         data_type=dataset_details['dataType'])
        
            # Check if the cursor is not None
            if not cursor:
                log.error("No explanation methods found")
                return GetExplanationMethodsResponse(status='FAILURE', message='No explanation methods found',dataType='', methods=[])
            
            method_list = []
            if payload.scope is not None:
                scope = payload.scope
                if use_model_end_point.lower() == 'yes':
                    for document in cursor:
                        # Check the scope
                        if document['scope'] == scope:
                            method_list.append(document['methods'])
                else:
                    # Create a list of explanation methods for the given scope
                    for document in cursor:
                        # Check if the modelType is not in the unsupportedModelTypes list for the given explanation method
                        if document['scope'] == scope and model_details['algorithm'].split('(')[0] not in document['unsupportedModels']:
                            method_list.append(document['methods'])
            else:
                if use_model_end_point.lower() == 'yes':
                    for document in cursor:
                        if document['methods'] not in method_list:
                                method_list.append(document['methods'])
                else:
                    # Create a list of explanation methods for LOCAL and GLOBAL scopes
                    for document in cursor:
                        # Check if the modelType is not in the unsupportedModelTypes list for the given explanation method
                        if model_details['algorithm'].split('(')[0] not in document['unsupportedModels']:
                            if document['methods'] not in method_list:
                                method_list.append(document['methods'])
            
            # check if method_list is empty or not, if empty raise exception
            if not method_list:
                raise ValueError("No explanation methods found for the given modelType, taskType, and dataType")
            
            # Create a GetExplanationMethodsResponse object with the scope and methods and return it
            obj = GetExplanationMethodsResponse(status='SUCCESS', 
                                                message='Identification of explanation methods successful',
                                                dataType=dataset_details['dataType'],
                                                methods=method_list
                                                )
            return obj

        except Exception as e:
            # Log the error and return an empty GetExplanationMethodsResponse object
            log.error(f"UUID: {request_id_var.get()}, Error: {e}", exc_info=True)
            Tbl_Exception.create({"UUID":request_id_var.get(),"function":"get_explanation_methodsServiceFunction","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise
    
    def data_to_dataframe(data, column_name='Value'):
        """
        Convert a single string or a dictionary to a pandas DataFrame.
        
        For a single string, create a single-column DataFrame.
        For a dictionary, create a single-row DataFrame with each key-value pair as a column-value pair.
        
        Parameters:
        data (str or dict): The data to be converted into a DataFrame.
        column_name (str): The name of the DataFrame column if the data is a string. Default is 'Value'.
        
        Returns:
        pd.DataFrame: The resulting DataFrame with the data.
        """
        if isinstance(data, str):
            # Create a single-column DataFrame for a single string
            df = pd.DataFrame([data], columns=[column_name])
        elif isinstance(data, dict):
            # Create a single-row DataFrame with each key-value pair as a column-value pair for a dictionary
            df = pd.DataFrame([data])
        else:
            raise ValueError("The input data must be either a single string or a dictionary")

        return df
    
    def generate_explanation(payload: dict):
        try:
            db_type = os.getenv('DB_TYPE').lower()

            # Extract modelId and datasetId from the payload
            modelId = payload.modelId
            datasetId = payload.datasetId
            scope = payload.scope
            method = payload.method 
            if hasattr(payload, 'inputText'):
                inputText = payload.inputText
            else:
                inputText = None

            if hasattr(payload, 'inputRow'):
                inputRow = payload.inputRow
            else:
                inputRow = None
            preprocessorId = payload.preprocessorId

            model_attribute_ids = ModelAttributes.find(model_attributes=['useModelApi'])
            model_attribute_values = ModelAttributeValues.find(batch_id=None, model_id=modelId, model_attribute_ids=model_attribute_ids)
            use_model_end_point = model_attribute_values[0]

            model_details = Model.find(model_id=modelId)

            if use_model_end_point.lower() == 'yes':
                model_attribute_names = ['modelFramework','taskType','data','prediction','targetDataType']
                model_attribute_ids = ModelAttributes.find(model_attributes=model_attribute_names)
                model_attribute_values = ModelAttributeValues.find(batch_id=None, model_id=modelId, model_attribute_ids=model_attribute_ids)
               
                model_details['modelFramework'] = model_attribute_values[0]
                model_details['taskType'] = model_attribute_values[1]
                model_details['data'] = model_attribute_values[2]
                model_details['prediction'] = model_attribute_values[3]
                model_details['targetDataType'] = model_attribute_values[4]
                model_details['algorithm'] = None

            else:
                # Get the model details
                model_attribute_ids = ModelAttributes.find(model_attributes=['modelFramework', 'algorithm', 'taskType','targetDataType'])
                model_attribute_values = ModelAttributeValues.find(batch_id=None, model_id=modelId, model_attribute_ids=model_attribute_ids)
                model_details['modelFramework'] = model_attribute_values[0]
                model_details['algorithm'] = model_attribute_values[1]
                model_details['taskType'] = model_attribute_values[2]
                model_details['targetDataType'] = model_attribute_values[3]
                model_details['data'] = None
                model_details['prediction'] = None
                model_details['ModelEndPoint'] = None
            
            # Load the model based on its Access/Framework type
            if model_details['modelFramework'] == 'API':
                model = model_details['ModelEndPoint']
            else:
                container_name = None if db_type == 'mongo' else os.getenv('MODEL_CONTAINER_NAME')
                modelObject = fileStoreDb.read_file_exp(unique_id=model_details['ModelData'], container_name=container_name)

                if model_details['modelFramework'] in ('Scikit-learn', 'Statsmodels'):
                    model = joblib.load(BytesIO(modelObject['data'].read()) if db_type == 'mongo' else BytesIO(modelObject['data']))
                elif model_details['modelFramework'] == 'Keras':
                    with open('model.h5', 'wb') as f:
                        f.write(modelObject['data'].read() if db_type == 'mongo' else modelObject['data'])
                        model = keras.models.load_model('model.h5')
                    os.remove('model.h5')
                else:
                    log.error("Unsupported model file type. Supported file types are pkl/h5")
                    return GetExplanationResponse(status='FAILURE', message='Unsupported model file type. Supported file types are pkl/h5', explanation=[])

            # Get the dataset details 
            if model_details['taskType'] == 'CLASSIFICATION' or model_details['taskType'] == 'CLUSTERING':
                dataset_attributes = ['groundTruthClassLabel', 'dataType', 'fileName', 'groundTruthClassNames']
            else:
                dataset_attributes = ['groundTruthClassLabel', 'dataType', 'fileName']
            dataset_details = Dataset.find(dataset_id=datasetId)
            dataset_attribute_ids = DatasetAttributes.find(dataset_attributes=dataset_attributes)
            dataset_attribute_values = DatasetAttributeValues.find(dataset_id=datasetId, dataset_attribute_ids=dataset_attribute_ids)

            dataset_details['targetClassLabel'] = dataset_attribute_values[0]
            dataset_details['dataType'] = dataset_attribute_values[1]
            dataset_details['fileName'] = dataset_attribute_values[2]
            dataset_details['datasetFileType'] = dataset_attribute_values[2].split('.')[-1]
            try:
                dataset_details['targetClassNames'] = dataset_attribute_values[3]
            except IndexError:
                dataset_details['targetClassNames'] = None
            
            # Load the dataset based on its file type
            container_name = None if db_type == 'mongo' else os.getenv('DATASET_CONTAINER_NAME')
            datasetObject = fileStoreDb.read_file_exp(unique_id = dataset_details['SampleData'], container_name = container_name)
            data = BytesIO(datasetObject['data'].read()) if db_type == 'mongo' else BytesIO(datasetObject['data'])
            if dataset_details['datasetFileType'] == 'csv':
                try:
                    dataset = pd.read_csv(data)
                except UnicodeDecodeError:
                    data.seek(0)  # Reset the read position of the BytesIO object
                    try:
                        dataset = pd.read_csv(data, encoding='ISO-8859-1')
                    except UnicodeDecodeError:
                        dataset = pd.read_csv(data, encoding='cp1252')
            elif dataset_details['datasetFileType'] == 'parquet':
                dataset = pd.read_parquet(data)
            else:
                log.error("Unsupported dataset file type")
                return GetExplanationResponse(status='FAILURE', message='Unsupported dataset file type. Supported file types are csv/parquet.', explanation=[])

            if inputRow is not None:
                lineDataset_as_is = ExplainService.data_to_dataframe(inputRow)
                
                # Get the common columns between datasetA and datasetB
                common_columns = [col for col in dataset.columns if col in lineDataset_as_is.columns]

                # Reorder columns in datasetB to match the order in datasetA
                lineDataset = lineDataset_as_is[common_columns]
                
            elif inputText is not None:
                lineDataset = ExplainService.data_to_dataframe(inputText)
            else:
                lineDataset = None
            
            if preprocessorId is not None and preprocessorId != 0:
                preprocessor_details = Preprocessor.find(preprocessor_id= preprocessorId)

                container_name = None if db_type == 'mongo' else os.getenv('PREPROCESSOR_CONTAINER_NAME')
                preprocessorObject = fileStoreDb.read_file_exp(unique_id=preprocessor_details['PreprocessorFileId'], container_name=container_name)
                preprocessor = joblib.load(BytesIO(preprocessorObject['data'].read()) if db_type == 'mongo' else BytesIO(preprocessorObject['data']))
                if hasattr(preprocessor, 'tokenizer') and preprocessor.tokenizer:
                    preprocessor.tokenizer = None
                if hasattr(preprocessor, 'stop_words') and preprocessor.stop_words is None:
                    preprocessor.stop_words = 'english'
            else:
                preprocessor = None
            
            inputIndex = 0
            # Generate the explanation based on the method
            obj_explain = ResponsibleAIExplain.get_explanation(model=model,
                                                                taskType=model_details['taskType'],
                                                                modelType=model_details['modelFramework'],
                                                                dataset=dataset,
                                                                preprocessor=preprocessor,
                                                                targetClassLabel=dataset_details['targetClassLabel'],
                                                                targetClassNames=dataset_details['targetClassNames'],
                                                                method=method,
                                                                scope=scope,
                                                                lineDataset=lineDataset,
                                                                inputIndex=inputIndex,
                                                                api_input_request= model_details['data'],
                                                                api_output_response= model_details['prediction']
                                                                )
    
            List_explain_tabular = []
            model_dict={"Model Name":model_details['ModelName'],"Algorithm":model_details['algorithm'],"ModelEndpoint": model_details['ModelEndPoint'],"Task Type": model_details['taskType'][0] + model_details['taskType'][1:].lower()}
            dataset_dict={"Dataset Name":dataset_details['DataSetName'], "dataType": dataset_details['dataType'], "GroundTruth Class Label":dataset_details['targetClassLabel'],"GroundTruth Class Names": dataset_details['targetClassNames']}
            for item in obj_explain: 
                if item.get('anchor'):
                    objexplainabilitylocalabular = ExplainabilityTabular_New(modelName = model_dict['Model Name'],
                                                                            algorithm = model_dict['Algorithm'],
                                                                            endpoint = model_dict['ModelEndpoint'],
                                                                            taskType = model_dict['Task Type'],
                                                                            datasetName = dataset_dict['Dataset Name'],
                                                                            dataType = dataset_dict['dataType'],
                                                                            groundTruthLabel = dataset_dict['GroundTruth Class Label'], 
                                                                            groundTruthClassNames = dataset_dict['GroundTruth Class Names'],
                                                                            featureNames = None,
                                                                            methodName = 'ANCHOR',
                                                                            methodDescription = item['description'],
                                                                            anchor=item['anchor'],
                                                                            attributionsText =None,
                                                                            shapImportanceText = None,
                                                                            featureImportance = None,
                                                                            timeSeriesForecast=None,
                                                                            shapValues=None,
                                                                            explanationDesc=None
                                                                                )
                elif item.get('attributionsText'):
                    objexplainabilitylocalabular = ExplainabilityTabular_New(modelName = model_dict['Model Name'],
                                                                                algorithm = model_dict['Algorithm'],
                                                                                endpoint = model_dict['ModelEndpoint'],
                                                                                taskType = model_dict['Task Type'],
                                                                                datasetName = dataset_dict['Dataset Name'],
                                                                                dataType = dataset_dict['dataType'],
                                                                                groundTruthLabel = dataset_dict['GroundTruth Class Label'], 
                                                                                groundTruthClassNames = dataset_dict['GroundTruth Class Names'],
                                                                                featureNames = item['featureNames'],
                                                                                methodName = 'INTEGRATED GRADIENTS',
                                                                                methodDescription = item['description'],
                                                                                anchor = None,
                                                                                attributionsText = item['attributionsText'],
                                                                                shapImportanceText = None,
                                                                                featureImportance = None,
                                                                                timeSeriesForecast = None,
                                                                                shapValues = None,
                                                                                explanationDesc = None
                                                                                )
                elif item.get('shapImportanceText'):
                    method_mapping = {
                        'TEXT-SHAP-EXPLAINER': 'SHAP EXPLAINER'
                    }
                    method_name = method_mapping.get(method)
                    objexplainabilitylocalabular = ExplainabilityTabular_New(modelName = model_dict['Model Name'],
                                                                                algorithm = model_dict['Algorithm'],
                                                                                endpoint = model_dict['ModelEndpoint'],
                                                                                taskType = model_dict['Task Type'],
                                                                                datasetName = dataset_dict['Dataset Name'],
                                                                                dataType = dataset_dict['dataType'],
                                                                                groundTruthLabel = dataset_dict['GroundTruth Class Label'], 
                                                                                groundTruthClassNames = dataset_dict['GroundTruth Class Names'],
                                                                                featureNames = item['featureNames'],
                                                                                methodName = method_name,
                                                                                methodDescription = item['description'],
                                                                                anchor = None,
                                                                                attributionsText = None,
                                                                                shapImportanceText = item['shapImportanceText'],
                                                                                featureImportance = None,
                                                                                timeSeriesForecast = None,
                                                                                shapValues = None,
                                                                                explanationDesc = None
                                                                                )
                elif item.get('importantFeatures'):
                    method_mapping = {
                        'KERNEL-EXPLAINER': 'KERNEL EXPLAINER',
                        'LIME-TABULAR': 'LIME TABULAR',
                        'TEXT-SHAP-EXPLAINER': 'SHAP EXPLAINER'
                    }
                    method_name = method_mapping.get(method)
                    objexplainabilitylocalabular = ExplainabilityTabular_New(modelName = model_dict['Model Name'],
                                                                            algorithm = model_dict['Algorithm'],
                                                                            endpoint = model_dict['ModelEndpoint'],
                                                                            taskType = model_dict['Task Type'],
                                                                            datasetName = dataset_dict['Dataset Name'],
                                                                            dataType = dataset_dict['dataType'],
                                                                            groundTruthLabel = dataset_dict['GroundTruth Class Label'], 
                                                                            groundTruthClassNames = dataset_dict['GroundTruth Class Names'],
                                                                            featureNames = item['featureNames'],
                                                                            methodName = method_name,
                                                                            methodDescription = item['description'],
                                                                            anchor=None,
                                                                            attributionsText =None,
                                                                            shapImportanceText = None,
                                                                            featureImportance = item['importantFeatures'],
                                                                            timeSeriesForecast=None,
                                                                            shapValues=None,
                                                                            explanationDesc=None)
                elif item.get('timeSeries'):
                    method_mapping = {
                        'TS-KERNEL-EXPLAINER': 'KERNEL EXPLAINER',
                        'TS-LIME-TABULAR': 'LIME TABULAR'
                    }
                    method_name = method_mapping.get(method)
                    objexplainabilitylocalabular = ExplainabilityTabular_New(modelName = model_dict['Model Name'],
                                                                            algorithm = model_dict['Algorithm'],
                                                                            endpoint = model_dict['ModelEndpoint'],
                                                                            taskType = model_dict['Task Type'],
                                                                            datasetName = dataset_dict['Dataset Name'],
                                                                            dataType = dataset_dict['dataType'],
                                                                            groundTruthLabel = dataset_dict['GroundTruth Class Label'], 
                                                                            groundTruthClassNames = dataset_dict['GroundTruth Class Names'],
                                                                            featureNames = item['featureNames'],
                                                                            methodName = method_name,
                                                                            methodDescription = item['description'],
                                                                            anchor = None,
                                                                            attributionsText = None,
                                                                            shapImportanceText = None,
                                                                            featureImportance = None,
                                                                            timeSeriesForecast = item['timeSeries'],
                                                                            shapValues = None,
                                                                            explanationDesc = None)
                else:
                    objexplainabilitylocalabular = ExplainabilityTabular_New(predictedTarget=item['predictedTarget'],inputRow=[])
                    
                List_explain_tabular.append(objexplainabilitylocalabular.dict())
                
            return GetExplanationResponse(status='SUCCESS',
                                                message='Explanation generated successfully',
                                                explanation=List_explain_tabular)
            
        except Exception as e:
            log.error(f"UUID: {request_id_var.get()}, Error: {e}", exc_info=True)
            Tbl_Exception.create({"UUID":request_id_var.get(),"function":"generate_explanationServiceFunction","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise
    
    def generate_report(payload: dict):
        # Check if payload is not None and it contains 'modelId' and 'datasetId'
        if payload.batchId is None or '':
            log.error("Batch Id id missing")
            return GetReportResponse(status='FAILURE', 
                                     message='Batch Id missing')
        try:
            tenet_id = Tenet.find(tenet_name='Explainability')
            batch_id = payload.batchId
            batch_details = Batch.find(batch_id=batch_id, tenet_id=tenet_id)
            modelId = batch_details['ModelId']
            datasetId = batch_details['DataId']
            preprocessorId = batch_details['PreprocessorId']
            title =  batch_details['Title']

            model_attribute_ids = ModelAttributes.find(model_attributes=['taskType','targetDataType'])
            model_attribute_values = ModelAttributeValues.find(batch_id=None, model_id=modelId, model_attribute_ids=model_attribute_ids)                
            task_type = model_attribute_values[0]
            target_data_type = model_attribute_values[1]

            if task_type != 'TIMESERIESFORECAST' and target_data_type != 'Text': 
                updated_methods = {"GLOBAL":["KERNEL-EXPLAINER"], "LOCAL": ["LIME-TABULAR"]}
            elif task_type == 'TIMESERIESFORECAST':
                updated_methods = {"GLOBAL": ["TS-KERNEL-EXPLAINER"],"LOCAL": ["TS-LIME-TABULAR"]}
            else:
                model_attribute_ids = ModelAttributes.find(model_attributes=['appExplanationMethods'])
                model_attribute_values = ModelAttributeValues.find(batch_id=batch_id, model_id=modelId, model_attribute_ids=model_attribute_ids)    
                methods = model_attribute_values[0]
                updated_methods = {"LOCAL": methods}

            # Update the batch status to "Started"
            Batch.update(batch_id=batch_id, value={'Status': "Started"})
            
            final_response=[]
            
            for scope, values in updated_methods.items():
                for method in values:
                    response={}
                    
                    # Create a Payload object
                    payload_obj = Payload(modelId=modelId, datasetId=datasetId, preprocessorId=preprocessorId, 
                                          scope=scope, method=method)
                   
                    # Generate explanation for the given payload
                    obj_explain = ExplainService.generate_explanation(payload_obj)
                    
                    response["title"] = title
                    response["algorithm"] = obj_explain.explanation[0].algorithm
                    response["endpoint"] = obj_explain.explanation[0].endpoint
                    response["taskType"] = obj_explain.explanation[0].taskType
                    response["datasetName"] = obj_explain.explanation[0].datasetName
                    response["dataType"] = obj_explain.explanation[0].dataType
                    response["groundTruthLabel"] = obj_explain.explanation[0].groundTruthLabel
                    response["groundTruthClassNames"] = obj_explain.explanation[0].groundTruthClassNames
                    response["methodName"] = obj_explain.explanation[0].methodName
                    response["methodDescription"] = obj_explain.explanation[0].methodDescription
                    response["scope"] = scope
                    response["featureNames"] = obj_explain.explanation[0].featureNames
                   
                    # Check if 'anchor' is in obj_explain
                    if obj_explain.explanation[0].anchor is not None:
                        response["anchors"] = obj_explain.explanation[0].anchor
                    # Check if 'attributionsText' is in obj_explain
                    elif obj_explain.explanation[0].attributionsText is not None:
                        response["attributionsText"] = obj_explain.explanation[0].attributionsText
                    # Check if 'featureImportance' is in obj_explain
                    elif obj_explain.explanation[0].featureImportance is not None:
                        response["featureImportance"]=obj_explain.explanation[0].featureImportance
                    # Check if 'limeTimeSeries' is in obj_explain
                    elif obj_explain.explanation[0].timeSeriesForecast is not None:
                        response["timeSeriesForecast"] = obj_explain.explanation[0].timeSeriesForecast
                    # Check if 'shapValues' is in obj_explain
                    elif obj_explain.explanation[0].shapImportanceText is not None:
                        response["shapImportanceText"] = obj_explain.explanation[0].shapImportanceText
                    # If none of the above, set 'anchors', 'featureImportance', 'attributionsText', and 'limeTimeSeries' to None
                    else:
                        response["anchors"] = None
                        response["attributionsText"] = None
                        response["featureImportance"]=None
                        response["limeTimeSeries"]=None
                        response["shapImportanceText"] = None

                    final_response.append(response)
            
            # Generate HTML content from the final_response
            html_content = Report.generate_html_content(final_response)
            
            # Save the HTML content to a local file
            local_file_path = "../output/explanationreport.html"
            ExplainService.save_html_to_file(html_content, local_file_path)

            # Create csv file
            CreateCSV.json_to_csv(final_response)

            # Define the directory containing the files to be zipped and the zip file path
            output_dir = '../output'
            zip_file_path = os.path.join(output_dir, 'report.zip')

            # Ensure the output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Create a zip file and add all .csv and .html files in the output directory to it
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        if file.endswith('.csv') or file.endswith('.html'):
                            file_path = os.path.join(root, file)
                            # Adjust the path in the zip file to maintain the directory structure under 'output/'
                            arcname = os.path.relpath(file_path, os.path.dirname(output_dir))
                            zipf.write(file_path, arcname)

            # Now you can save the zip file to the database
            # Assuming fileStoreDb.save_file() takes a file-like object, you can open the zip file in binary mode
            with open('../output/report.zip', 'rb') as zipf:
                FileId = fileStoreDb.save_file(file = zipf, filename = 'explanation_report.zip', contentType = 'application/zip', tenet = 'Explainability')
                report_name = 'explanation_report.zip'

            HtmlId = time.time()
            doc = {
                    'HtmlId': HtmlId,
                    'BatchId': batch_id,
                    'TenetId': tenet_id,
                    'ReportName': report_name,
                    'HtmlFileId': FileId,
                    'CreatedDateTime': datetime.now()
                }
            Html.create(doc)

            url = os.getenv("REPORT_URL")
            payload = {"batchId": batch_id}
            verify_ssl = os.getenv('VERIFY_SSL', 'false').lower() in ('true', '1', 't', 'yes')
            response = requests.request("POST", url, data=payload, verify= verify_ssl).json()

            # Directory path of the output folder
            output_dir = '../output'
            # Delete all files in the directory
            for filename in os.listdir(output_dir):
                file_path = os.path.join(output_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            if response['status']=='SUCCESS':
                # Update the batch status to "Completed"
                Batch.update(batch_id=batch_id, value={'Status': "Completed"})
                return GetReportResponse(status='SUCCESS',
                                        message='Report generated successfully')
            else:
                # Update the batch status to "Failed"
                Batch.update(batch_id=batch_id, value={'Status': "Failed"})
                return GetReportResponse(status='FAILURE',
                                        message=f"Error in generating report due to: {response['message']}")
            
        except Exception as e:
            Batch.update(batch_id=batch_id, value={'Status': "Failed"})
            log.error(f"UUID: {request_id_var.get()}, Error: {e}", exc_info=True)
            Tbl_Exception.create({"UUID":request_id_var.get(),"function":"generate_reportServiceFunction","msg":str(e),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise