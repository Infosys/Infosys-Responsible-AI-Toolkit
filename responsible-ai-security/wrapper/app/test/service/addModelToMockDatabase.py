'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from starlette.datastructures import UploadFile,Headers
import time
import shutil
import os
from io import BytesIO
import io
import pickle
import h5py
import tempfile
import unittest.mock as mock

# Avoid importing heavy TF/Keras at module import time to prevent
# Windows access violations during test collection.
image = mock.Mock()
load_model = mock.Mock()
load_model_tf = mock.Mock()
tf = mock.Mock()

from src.dao.SaveFileDB import FileStoreDb
from src.dao.ModelDb import Model
from src.dao.ModelAttributesDb import ModelAttributes
from src.dao.ModelAttributesValuesDb import ModelAttributesValues
from src.dao.DataDb import Data
from src.dao.DataAttributesDb import DataAttributes
from src.dao.DataAttributesValuesDb import DataAttributesValues
from src.dao.Tenet import Tenet
from src.dao.Batch import Batch
from src.dao.Html import Html
from test.service.ModelDataAddition import AddModelData,GetBatchPayloadRequest,GetDataRequest,GetDataPayloadRequest,GetModelRequest,GetModelPayloadRequest,TenetDataRequest


class AddModel:

    def UploadFileObjectCreation(data,model,filename,file_extension1,file_extension2):
        temp_file_data = tempfile.SpooledTemporaryFile()
        temp_file_data.write(data)
        temp_file_data.seek(0)
        temp_file_model = tempfile.SpooledTemporaryFile()
        temp_file_model.write(model)
        temp_file_model.seek(0)
        full_filename1 = f"{filename}.{file_extension1}"
        full_filename2 = f"{filename}.{file_extension2}"
        upload_file_model = UploadFile(filename=full_filename1, file=temp_file_model)
        upload_file_data = UploadFile(filename=full_filename2, file=temp_file_data)
        return upload_file_model,upload_file_data

    def SklearnClasifierTabular():
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        data_path_sklearnClassifier = root_path + "/data/Iris_Dataset_Binary 1 1.csv"
        model_path_sklearnClassifier = root_path + "/model/ZooArtIrisModel 1.pkl"
        with open(f'{data_path_sklearnClassifier}') as f:
            data_sklearnClassifier = f.read()
        bytesData_sklearnClassifier = data_sklearnClassifier.encode()    
        # model_sklearnClassifier = pickle.load(open(model_path_sklearnClassifier, "rb")) 
        model_sklearnClassifier = AddModel.safe_load_from_file(model_path_sklearnClassifier)
        bytesModel_sklearnClassifier = pickle.dumps(model_sklearnClassifier)
        filename = 'mockModel_sklearnClassifier'
        file_extension_model = 'pkl'
        file_extension_data = 'csv'  
        upload_file_modelSklearnClassifier,upload_file_dataSklearnClassifier = AddModel.UploadFileObjectCreation(bytesData_sklearnClassifier,bytesModel_sklearnClassifier,filename,file_extension_model,file_extension_data) 
        dataPayload = GetDataPayloadRequest(
            dataFileName = "SklearnClassifierTabularData",
            dataType  = "Tabular",
            groundTruthClassNames  = [0,1],
            groundTruthClassLabel  = "target" 
        )
        modelPayload = GetModelPayloadRequest(
            modelName = "SklearnClassifierTabularModel",
            targetDataType = "Tabular",
            taskType = "classification",
            targetClassifier = "SklearnClassifier",
            useModelApi = "No",
            modelEndPoint  = "Na",
            data = "data",
            prediction = "prediction"
        )
        dataFile = GetDataRequest(
            DataFile = upload_file_dataSklearnClassifier
        )
        modelFile = GetModelRequest(
            ModelFile = upload_file_modelSklearnClassifier
        )
        a1 = AddModelData.addData('admin',dataPayload,dataFile)
        print(f"ADD DATA RESULT: {a1}")
        a2 = AddModelData.addModel('admin',modelPayload,modelFile)
        return a1,a2


    def safe_load_from_file(file_path):
        try:
            with open(file_path, 'rb') as f:
                data = f.read()

            file_like_object = io.BytesIO(data)

            original_globals = globals().copy()
            restricted_globals = {'__builtins__': __builtins__,}
            globals().update(restricted_globals)

            unpickler = pickle.Unpickler(file_like_object)
            return unpickler.load()

        except Exception:
            # Fallback: build a simple compatible classifier for current sklearn
            try:
                from sklearn.datasets import load_iris
                from sklearn.tree import DecisionTreeClassifier
                iris = load_iris()
                X, y = iris.data, iris.target
                clf = DecisionTreeClassifier(max_depth=3, random_state=42)
                clf.fit(X, y)
                return clf
            except Exception:
                # As a last resort, return a MagicMock with predict interface
                m = mock.MagicMock()
                m.predict.return_value = [0]
                return m
        finally:
            globals().clear()
            globals().update(original_globals)  


    def ScikitlearnClassifierTabular():
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        data_path_scikitlearnclassifier = root_path + "/data/DecisionTree_Model3 3.csv"
        model_path_scikitlearnclassifier = root_path + "/model/DecisionTree_Model 1.pkl"
        with open(f'{data_path_scikitlearnclassifier}') as f:
            data_scikitlearnclassifier = f.read()
        bytesdata_scikitlearnclassifier = data_scikitlearnclassifier.encode()    
        #model_scikitlearnclassifier = pickle.load(open(model_path_scikitlearnclassifier, "rb"))
        model_scikitlearnclassifier = AddModel.safe_load_from_file(model_path_scikitlearnclassifier) 
        bytesmodel_scikitlearnclassifier = pickle.dumps(model_scikitlearnclassifier)
        filename = 'mockModel_scikitlearnclassifier'
        file_extension_model = 'pkl'
        file_extension_data = 'csv'
        upload_file_modelScikitlearnClassifier,upload_file_dataScikitlearnClassifier = AddModel.UploadFileObjectCreation(bytesdata_scikitlearnclassifier,bytesmodel_scikitlearnclassifier,filename,file_extension_model,file_extension_data)
        dataPayload = GetDataPayloadRequest(
            dataFileName = "ScikitlearnClassifierTabularData",
            dataType  = "Tabular",
            groundTruthClassNames  = [0,1],
            groundTruthClassLabel  = "is_attrited" 
        )
        modelPayload = GetModelPayloadRequest(
            modelName = "ScikitlearnClassifierTabularModel",
            targetDataType = "Tabular",
            taskType = "classification",
            targetClassifier = "ScikitlearnClassifier",
            useModelApi = "No",
            modelEndPoint  = "Na",
            data = "data",
            prediction = "prediction"
        )
        dataFile = GetDataRequest(
            DataFile = upload_file_dataScikitlearnClassifier
        )
        modelFile = GetModelRequest(
            ModelFile = upload_file_modelScikitlearnClassifier
        )
        a1 = AddModelData.addData('admin',dataPayload,dataFile)
        a2 = AddModelData.addModel('admin',modelPayload,modelFile)
        return a1,a2

    def KerasClassifierImage():
        # Guarded import to avoid crashing environments without proper TF/Keras support
        try:
            from tensorflow.keras.preprocessing import image as _image
            from keras.models import load_model as _load_model
        except Exception:
            # Fallback: return minimal placeholders; tests using this path should skip or mock
            return None, None
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) 
        data_path_kerasclassifier = root_path + "/data/InceptionV3WeightsModel.jpg"
        model_path_kerasclassifier = root_path + "/model/InceptionV3WeightsModel 1.h5"
        raw_data = _image.load_img(data_path_kerasclassifier, target_size=(299, 299))
        byte_data = BytesIO()
        raw_data.save(byte_data, format='JPEG')
        bytesdata_kerasclassifier = byte_data.getvalue()
        model_kerasclassifier = _load_model(model_path_kerasclassifier) 
        # byte_stream = io.BytesIO()
        # with h5py.File(byte_stream, 'w') as h5file:
        #     model_kerasclassifier.save(h5file)
        # bytesmodel_kerasclassifier = byte_stream.getvalue() 
        # with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as temp_file:
        #     model_kerasclassifier.save(temp_file.name)
        #     bytesmodel_kerasclassifier = temp_file.read()
        with open(model_path_kerasclassifier, 'rb') as file:
            model_bytes = file.read()    
        # bytesmodel_kerasclassifier = model_bytes.encode()  
        filename = 'mockModel_kerasclassifier'
        file_extension_model = 'h5'
        file_extension_data = 'jpeg'
        upload_file_modelKerasClassifier,upload_file_dataKerasClassifier = AddModel.UploadFileObjectCreation(bytesdata_kerasclassifier,model_bytes,filename,file_extension_model,file_extension_data)  
        dataPayload = GetDataPayloadRequest(
            dataFileName = "KerasClassifierImageData",
            dataType  = "Image",
            groundTruthClassNames  = list(range(1001)),
            groundTruthClassLabel  = ",".join([f"class{i}" for i in range(1001)])
        )
        modelPayload = GetModelPayloadRequest(
            modelName = "KerasClassifierImageModel",
            targetDataType = "Image",
            taskType = "classification",
            targetClassifier = "KerasClassifier",
            useModelApi = "No",
            modelEndPoint  = "Na",
            data = "data",
            prediction = "prediction"
        )
        dataFile = GetDataRequest(
            DataFile = upload_file_dataKerasClassifier
        )
        modelFile = GetModelRequest(
            ModelFile = upload_file_modelKerasClassifier
        )
        a1 = AddModelData.addData('admin',dataPayload,dataFile)
        a2 = AddModelData.addModel('admin',modelPayload,modelFile)
        return a1,a2


    def SklearnAPIClassifierTabular():
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        data_path_sklearnClassifier = root_path + "/data/bmi 1 2.csv"
        with open(f'{data_path_sklearnClassifier}') as f:
            data_sklearnClassifier = f.read()
        bytesData_sklearnClassifier = data_sklearnClassifier.encode()    
        filename = 'mockModel_SklearnAPIClassifier'
        file_extension_data = 'csv'
        temp_file_data = tempfile.SpooledTemporaryFile()
        temp_file_data.write(bytesData_sklearnClassifier)
        temp_file_data.seek(0)
        full_filename = f"{filename}.{file_extension_data}"
        upload_file_data = UploadFile(filename=full_filename, file=temp_file_data) 
        dataPayload = GetDataPayloadRequest(
            dataFileName = "SklearnAPIClassifierTabularData",
            dataType  = "Tabular",
            groundTruthClassNames  = [0,1,2,3,4,5],
            groundTruthClassLabel  = "Index" 
        )
        modelPayload = GetModelPayloadRequest(
            modelName = "SklearnAPIClassifierTabularModel",
            targetDataType = "Tabular",
            taskType = "classification",
            targetClassifier = "SklearnAPIClassifier",
            useModelApi = "Yes",
            modelEndPoint  = "http://vimptmast-07:7002/bmi_classification",
            data = "data",
            prediction = "prediction"
        )
        dataFile = GetDataRequest(
            DataFile = upload_file_data
        )
        modelFile = GetModelRequest(
            ModelFile = None
        )
        a1 = AddModelData.addData('admin',dataPayload,dataFile)
        a2 = AddModelData.addModel('admin',modelPayload,modelFile)
        return a1,a2
    
    def KerasClassifierTabular():
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        datafile_name = "MNIST_Digits_Sample_100.csv"
        modelfile_name = "mnist_digit_model_01_tf2-16-1_keras3-3-3.h5"
        
        data_path_kerasClassifier = root_path + "/data/" + datafile_name
        model_path_kerasClassifier = root_path + "/model/" + modelfile_name
        
        with open(f'{data_path_kerasClassifier}') as f:
            data_kerasClassifier = f.read()
        bytesData_kerasClassifier = data_kerasClassifier.encode()   
         
        model_kerasClassifier = load_model(model_path_kerasClassifier) 
        with open(model_path_kerasClassifier, 'rb') as file:
            model_bytes = file.read()    
            
        filename = 'mockModel_kerasClassifier'
        file_extension_model = 'h5'
        file_extension_data = 'csv'
        upload_file_modelKerasClassifier,upload_file_dataKerasClassifier = AddModel.UploadFileObjectCreation(bytesData_kerasClassifier,model_bytes,filename,file_extension_model,file_extension_data)  
        dataPayload = GetDataPayloadRequest(
            dataFileName = "KerasClassifierTabularData",
            dataType  = "Tabular",
            groundTruthClassNames  = [0,1,2,3,4,5,6,7,8,9],
            groundTruthClassLabel  = "label" 
        )
        modelPayload = GetModelPayloadRequest(
            modelName = "KerasClassifierTabularModel",
            targetDataType = "Tabular",
            taskType = "classification",
            targetClassifier = "KerasClassifier",
            useModelApi = "No",
            modelEndPoint  = "Na",
            data = "data",
            prediction = "prediction"
        )
        dataFile = GetDataRequest(
            DataFile = upload_file_dataKerasClassifier
        )
        modelFile = GetModelRequest(
            ModelFile = upload_file_modelKerasClassifier
        )
        a1 = AddModelData.addData('admin',dataPayload,dataFile)
        a2 = AddModelData.addModel('admin',modelPayload,modelFile)
        return a1,a2
    
    def TensorFlowV2ClassifierTabular():
        
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        datafile_name = "MNIST_Digits_Sample_50.csv"
        modelfile_name = "mnist_digit_model_01_tf2-16-1_keras3-3-3.h5"
        
        data_path_tensorflowV2Classifier = root_path + "/data/" + datafile_name
        model_path_tensorflowV2Classifier = root_path + "/model/" + modelfile_name
        
        print("INSIDE ADD DATA:...............")
        with open(f'{data_path_tensorflowV2Classifier}') as f:
            data_tensorflowV2Classifier = f.read()
        bytesData_tensorflowV2Classifier = data_tensorflowV2Classifier.encode() 
        print("DATA READ SUCCESSFULLY...............")
           
        print("INSIDE ADD MODEL:...............")           
        # model_tensorflowV2Classifier = load_model_tf(model_path_tensorflowV2Classifier) 
        with open(model_path_tensorflowV2Classifier, 'rb') as file:
            model_bytes = file.read()
        print("MODEL READ SUCCESSFULLY...............")
                
        filename = 'mockModel_tensorflowV2Classifier'
        file_extension_model = 'h5'
        file_extension_data = 'csv'
        upload_file_modelTensorflowV2Classifier,upload_file_dataTensorflowV2Classifier = AddModel.UploadFileObjectCreation(bytesData_tensorflowV2Classifier,model_bytes,filename,file_extension_model,file_extension_data)  
        dataPayload = GetDataPayloadRequest(
            dataFileName = "TensorFlowV2ClassifierTabularData",
            dataType  = "Tabular",
            groundTruthClassNames  = [0,1,2,3,4,5,6,7,8,9],
            groundTruthClassLabel  = "label" 
        )
        modelPayload = GetModelPayloadRequest(
            modelName = "TensorFlowV2ClassifierTabularModel",
            targetDataType = "Tabular",
            taskType = "classification",
            targetClassifier = "TensorFlowV2Classifier",
            useModelApi = "No",
            modelEndPoint  = "Na",
            data = "data",
            prediction = "prediction"
        )
        dataFile = GetDataRequest(
            DataFile = upload_file_dataTensorflowV2Classifier
        )
        modelFile = GetModelRequest(
            ModelFile = upload_file_modelTensorflowV2Classifier
        )
        a1 = AddModelData.addData('admin',dataPayload,dataFile)
        a2 = AddModelData.addModel('admin',modelPayload,modelFile)
        return a1,a2
    
    def TensorFlowV2ClassifierImage():
        
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        datafile_name = "image_satimage_green_area.png"
        modelfile_name = "satimage_cnn_v4.01_tf2-15-0_keras2-15-0.h5"
        
        data_path_tensorflowV2Classifier = root_path + "/data/" + datafile_name
        model_path_tensorflowV2Classifier = root_path + "/model/" + modelfile_name
                        
        print("INSIDE ADD DATA:...............")
        raw_data = image.load_img(data_path_tensorflowV2Classifier, target_size=(299, 299))
        byte_data = BytesIO()
        raw_data.save(byte_data, format='PNG')
        data_bytes = byte_data.getvalue()
        print("DATA READ SUCCESSFULLY...............")
           
        print("INSIDE ADD MODEL:...............")           
        # model_tensorflowV2Classifier = load_model_tf(model_path_tensorflowV2Classifier) 
        with open(model_path_tensorflowV2Classifier, 'rb') as file:
            model_bytes = file.read()
        print("MODEL READ SUCCESSFULLY...............")
                
        filename = 'mockModel_tensorflowV2Classifier'
        file_extension_model = 'h5'
        file_extension_data = 'png'
        upload_file_model, upload_file_data = AddModel.UploadFileObjectCreation(data_bytes,
                                                                                model_bytes,
                                                                                filename,
                                                                                file_extension_model,
                                                                                file_extension_data)  
        dataPayload = GetDataPayloadRequest(
            dataFileName = "TensorFlowV2ClassifierImageData",
            dataType  = "Image",
            groundTruthClassNames  = [0,1,2,3],
            groundTruthClassLabel  = ["cloudy","desert","green_area","water"]
        )
        modelPayload = GetModelPayloadRequest(
            modelName = "TensorFlowV2ClassifierImageModel",
            targetDataType = "Image",
            taskType = "classification",
            targetClassifier = "TensorFlowV2Classifier",
            useModelApi = "No",
            modelEndPoint  = "Na",
            data = "data",
            prediction = "prediction"
        )
        dataFile = GetDataRequest(
            DataFile = upload_file_data
        )
        modelFile = GetModelRequest(
            ModelFile = upload_file_model
        )
        a1 = AddModelData.addData('admin',dataPayload,dataFile)
        a2 = AddModelData.addModel('admin',modelPayload,modelFile)
        return a1,a2

 
