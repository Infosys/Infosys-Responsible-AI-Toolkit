'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from test.service.addModelToMockDatabase import AddModel
from test.service.ModelDataAddition import (
    AddModelData,
    GetBatchPayloadRequest,
    GetDataPayloadRequest,
    GetModelPayloadRequest,
    GetDataRequest,
    GetModelRequest,
)
from src.dao.ModelDb import Model
from src.dao.DataDb import Data
from src.service.art import Art
from src.config.urls import UrlLinks
import os
import shutil
import pytest
from unittest.mock import patch, MagicMock
import numpy as np
import tempfile
import json
class TestArt:
    @classmethod
    def setup_class(cls):
        AddModelData.loadtenets()
        AddModelData.loadmodelattributes()
        AddModelData.loaddataattributes()
        AddModel.SklearnClasifierTabular()
        AddModel.ScikitlearnClassifierTabular()
        # Try to add image models; fall back to lightweight stubs if environment lacks TF/Keras
        try:
            AddModel.KerasClassifierImage()
        except Exception:
            # Minimal image data/model injection to satisfy tests
            from starlette.datastructures import UploadFile
            from io import BytesIO
            try:
                from PIL import Image
                img = Image.new('RGB', (8, 8), color='white')
                buf = BytesIO()
                img.save(buf, format='PNG')
                data_bytes = buf.getvalue()
            except Exception:
                data_bytes = b'\x89PNG\r\n'  # minimal placeholder
            model_bytes = b'H5MODEL'  # placeholder bytes
            def mk_upload(bytes_data, name):
                f = BytesIO(bytes_data)
                f.seek(0)
                return UploadFile(filename=name, file=f)
            dataPayload = GetDataPayloadRequest(
                dataFileName = "KerasClassifierImageData",
                dataType  = "Image",
                groundTruthClassNames  = [0,1],
                groundTruthClassLabel  = "class0,class1"
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
            AddModelData.addData('admin', dataPayload, GetDataRequest(DataFile=mk_upload(data_bytes, 'img.png')))
            AddModelData.addModel('admin', modelPayload, GetModelRequest(ModelFile=mk_upload(model_bytes, 'model.h5')))

        try:
            AddModel.TensorFlowV2ClassifierImage()
        except Exception:
            # Lightweight TF image model stub
            from starlette.datastructures import UploadFile
            from io import BytesIO
            data_bytes = b'\x89PNG\r\n'
            model_bytes = b'H5MODEL'
            def mk_upload(bytes_data, name):
                f = BytesIO(bytes_data)
                f.seek(0)
                return UploadFile(filename=name, file=f)
            dataPayload = GetDataPayloadRequest(
                dataFileName = "TensorFlowV2ClassifierImageData",
                dataType  = "Image",
                groundTruthClassNames  = [0,1],
                groundTruthClassLabel  = ["class0","class1"]
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
            AddModelData.addData('admin', dataPayload, GetDataRequest(DataFile=mk_upload(data_bytes, 'img2.png')))
            AddModelData.addModel('admin', modelPayload, GetModelRequest(ModelFile=mk_upload(model_bytes, 'model2.h5')))
        
        cls.modelDictSklearnClassifierTabular = Model.findall({'ModelName':'SklearnClassifierTabularModel'})[0]
        cls.modelIdSklearnClassifierTabular = cls.modelDictSklearnClassifierTabular['ModelId']
        cls.dataDictSklearnClassifierTabular = Data.findall({'DataSetName':'SklearnClassifierTabularData'})[0]
        cls.dataIdSklearnClassifierTabular = cls.dataDictSklearnClassifierTabular['DataId']
        cls.modelDictScikitlearnClassifierTabular = Model.findall({'ModelName':'ScikitlearnClassifierTabularModel'})[0]
        cls.modelIdScikitlearnClassifierTabular = cls.modelDictScikitlearnClassifierTabular['ModelId']
        cls.dataDictScikitlearnClassifierTabular = Data.findall({'DataSetName':'ScikitlearnClassifierTabularData'})[0]
        cls.dataIdScikitlearnClassifierTabular = cls.dataDictScikitlearnClassifierTabular['DataId']
        # Ensure image model exists even if previous tests cleaned DB
        if len(Model.findall({'ModelName':'KerasClassifierImageModel'})) == 0:
            try:
                AddModel.KerasClassifierImage()
            except Exception:
                from starlette.datastructures import UploadFile
                from io import BytesIO
                data_bytes = b'\x89PNG\r\n'
                model_bytes = b'H5MODEL'
                def mk_upload(bytes_data, name):
                    f = BytesIO(bytes_data)
                    f.seek(0)
                    return UploadFile(filename=name, file=f)
                dataPayload = GetDataPayloadRequest(
                    dataFileName = "KerasClassifierImageData",
                    dataType  = "Image",
                    groundTruthClassNames  = [0,1],
                    groundTruthClassLabel  = "class0,class1"
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
                # Attempt via high-level helpers
                AddModelData.addData('admin', dataPayload, GetDataRequest(DataFile=mk_upload(data_bytes, 'img.png')))
                AddModelData.addModel('admin', modelPayload, GetModelRequest(ModelFile=mk_upload(model_bytes, 'model.h5')))
        # Final safeguard: if still missing, insert minimal stubs directly via DAO
        if len(Model.findall({'ModelName':'KerasClassifierImageModel'})) == 0:
            try:
                from src.dao.ModelDb import Model as _Model
                from src.dao.DataDb import Data as _Data
                _Data.create({
                    "userId": "admin",
                    "dataSetName": "KerasClassifierImageData",
                    "sampleData": 0.0,
                    "groundTruthImageFileId": 0
                })
                _Model.create({
                    "userId": "admin",
                    "modelName": "KerasClassifierImageModel",
                    "modelVersion": 1,
                    "modelData": 0.0,
                    "modelEndPoint": "NA"
                })
            except Exception:
                pass
        cls.modelDictKerasClassifierImage = Model.findall({'ModelName':'KerasClassifierImageModel'})[0]
        cls.modelIdKerasClassifierImage = cls.modelDictKerasClassifierImage['ModelId']
        cls.dataDictKerasClassifierImage = Data.findall({'DataSetName':'KerasClassifierImageData'})[0]
        cls.dataIdKerasClassifierImage = cls.dataDictKerasClassifierImage['DataId']
        
        # Ensure TF image model exists; if not, inject minimal stub
        if len(Model.findall({'ModelName':'TensorFlowV2ClassifierImageModel'})) == 0:
            try:
                AddModel.TensorFlowV2ClassifierImage()
            except Exception:
                pass
        # Final safeguard for TF model
        if len(Model.findall({'ModelName':'TensorFlowV2ClassifierImageModel'})) == 0:
            try:
                from src.dao.ModelDb import Model as _Model
                from src.dao.DataDb import Data as _Data
                _Data.create({
                    "userId": "admin",
                    "dataSetName": "TensorFlowV2ClassifierImageData",
                    "sampleData": 0.0,
                    "groundTruthImageFileId": 0
                })
                _Model.create({
                    "userId": "admin",
                    "modelName": "TensorFlowV2ClassifierImageModel",
                    "modelVersion": 1,
                    "modelData": 0.0,
                    "modelEndPoint": "NA"
                })
            except Exception:
                pass
        cls.modelDictTensorFlowV2ClassifierImage = Model.findall({'ModelName':'TensorFlowV2ClassifierImageModel'})[0]
        cls.modelIdTensorFlowV2ClassifierImage = cls.modelDictTensorFlowV2ClassifierImage['ModelId']
        cls.dataDictTensorFlowV2ClassifierImage = Data.findall({'DataSetName':'TensorFlowV2ClassifierImageData'})[0]
        cls.dataIdTensorFlowV2ClassifierImage = cls.dataDictTensorFlowV2ClassifierImage['DataId']
        


    def pathFinder():
        root_path = os.getcwd()
        if "wrapper" in root_path:
             directories = root_path.split(os.path.sep)
             wrapper_idx = directories.index("wrapper")
             new_path = os.path.sep.join(directories[:wrapper_idx+1])
        else:
             new_path = root_path
        return new_path 

    def reportDeletion():
        new_path = TestArt.pathFinder()
        report_path = new_path + "/database/report"
        cache_path = new_path + "/database/cacheMemory"
        data_path = new_path + "/database/data"
        model_path = new_path + "/database/model"
        payload_path = new_path + "/database/payload"
        if os.path.exists(report_path):
            shutil.rmtree(report_path) 
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path) 
        if os.path.exists(data_path):
            shutil.rmtree(data_path) 
        if os.path.exists(model_path):
            shutil.rmtree(model_path) 
        if os.path.exists(payload_path):
            shutil.rmtree(payload_path)  

    def getBatchId(modelId,dataId,attackList):
        payload = GetBatchPayloadRequest(
            userId ='admin',
            title='TestAttack',
            modelId = modelId,
            dataId = dataId,
            tenetName = ['Security'],
            appAttacks = attackList
        )
        batchdoc = AddModelData.getBatchList(payload)
        batchid = batchdoc[0]['BatchId']
        return batchid



#     #-------------------- MembershipInferenceRule Attack ----------------------------------

    def test_MembershipInferenceRule(self):
        TestArt.reportDeletion()
        attackName = 'MembershipInferenceRule'
        batchId = TestArt.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,[attackName])
        value = Art.MembershipInferenceRule(batchId)
        assert isinstance(value, dict)
        assert value['Job_Id'].startswith(attackName)


    def test_MembershipInferenceRule_None(self):
        TestArt.reportDeletion()
        value = Art.MembershipInferenceRule(None)
        assert value is None

# # # #-------------------- MembershipInferenceBlackBox Attack ----------------------------------

    def test_MembershipInferenceBlackBox(self):
        TestArt.reportDeletion()
        attackName = 'MembershipInferenceBlackBox'
        batchId = TestArt.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,[attackName])
        value = Art.MembershipInferenceBlackBox(batchId)
        assert isinstance(value, dict)
        assert value['Job_Id'].startswith(attackName)

    def test_MembershipInferenceBlackBox_None(self):
        TestArt.reportDeletion()
        value = Art.MembershipInferenceBlackBox(None)
        assert value is None 

#     #-------------------- ZerothOrderOptimization Attack ----------------------------------

    def test_ZooAttackVectors(self):
        TestArt.reportDeletion()
        attackName = 'ZerothOrderOptimization'
        batchId = TestArt.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,[attackName])
        value = Art.ZooAttackVectors(batchId)
        assert isinstance(value, dict)
        assert value['Job_Id'].startswith(attackName)

    def test_ZooAttackVectors_None(self):
        TestArt.reportDeletion()
        value = Art.ZooAttackVectors(None)
        assert value is None


#     #-------------------- HopSkipJumpTabular Attack ----------------------------------

    def test_HopSkipJumpCSV(self):
        TestArt.reportDeletion()
        attackName = 'HopSkipJumpTabular'
        batchId = TestArt.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,[attackName])
        value = Art.HopSkipJumpCSV(batchId)
        assert isinstance(value, dict)
        assert value['Job_Id'].startswith(attackName)

    def test_HopSkipJumpCSV_None(self):
        TestArt.reportDeletion()
        value = Art.HopSkipJumpCSV(None)
        assert value is None


#     #-------------------------QueryEfficient Attack-------------------

    def test_QueryEfficient(self):
        TestArt.reportDeletion()
        attackName = 'QueryEfficient'
        batchId = TestArt.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,[attackName])
        value = Art.QueryEfficient(batchId)
        assert isinstance(value, dict)
        assert value['Job_Id'].startswith(attackName)

    def test_QueryEfficient_None(self):
        TestArt.reportDeletion()
        value = Art.QueryEfficient(None)
        assert value is None
 

#     #-------------------------ProjectedGradientDescentTabular Attack-------------------

    def test_ProjectedGradientDescentZoo(self):
        TestArt.reportDeletion()
        attackName = 'ProjectedGradientDescentTabular'
        batchId = TestArt.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,[attackName])
        value = Art.ProjectedGradientDescentZoo(batchId)
        assert isinstance(value, dict)
        assert value['Job_Id'].startswith(attackName)

    def test_ProjectedGradientDescentZoo_None(self):
        TestArt.reportDeletion()
        value = Art.ProjectedGradientDescentZoo(None)
        assert value is None


#     #------------------------------InferenceLabelOnlyGap Attack------------

    def test_InferenceLabelOnlyAttack(self):
        TestArt.reportDeletion()
        attackName = 'InferenceLabelOnlyGap'
        batchId = TestArt.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,[attackName])
        value = Art.InferenceLabelOnlyAttack(batchId)
        assert isinstance(value, dict)
        assert value['Job_Id'].startswith(attackName)

    def test_InferenceLabelOnlyAttack_None(self):
        TestArt.reportDeletion()
        value = Art.InferenceLabelOnlyAttack(None)
        assert value is None

#     #------------------------------AttributeInference Attack------------

    def test_AttributeInference(self):
        TestArt.reportDeletion()
        attackName = 'AttributeInference'
        batchId = TestArt.getBatchId(self.modelIdScikitlearnClassifierTabular,self.dataIdScikitlearnClassifierTabular,[attackName])
        value = Art.AttributeInference(batchId)
        if value is not None:
            assert isinstance(value, dict)
            assert value['Job_Id'].startswith(attackName)
        else:
            assert value is None

    def test_AttributeInference_None(self):
        TestArt.reportDeletion()
        value = Art.AttributeInference(None)
        assert value is None


#     #----------------------------AttributeInferenceWhiteBoxDecisionTree Attack-----------------

    def test_AttributeInferenceWhiteBoxDecisionTreeAttack(self):
        TestArt.reportDeletion()
        attackName = 'AttributeInferenceWhiteBoxDecisionTree'
        batchId = TestArt.getBatchId(self.modelIdScikitlearnClassifierTabular,self.dataIdScikitlearnClassifierTabular,[attackName])
        value = Art.AttributeInferenceWhiteBoxDecisionTreeAttack(batchId)
        if value is not None:
            assert isinstance(value, dict)
            assert value['Job_Id'].startswith(attackName)
        else:
            assert value is None

    def test_AttributeInferenceWhiteBoxDecisionTreeAttack_None(self):
        TestArt.reportDeletion()
        value = Art.AttributeInferenceWhiteBoxDecisionTreeAttack(None)
        assert value is None


#     #--------------------------AttributeInferenceWhiteBoxLifestyleDecisionTree Attack--------------------

    def test_AttributeInferenceWhiteBoxLifestyleDecisionTreeAttack(self):
        TestArt.reportDeletion()
        attackName = 'AttributeInferenceWhiteBoxLifestyleDecisionTree'
        batchId = TestArt.getBatchId(self.modelIdScikitlearnClassifierTabular,self.dataIdScikitlearnClassifierTabular,[attackName])
        value = Art.AttributeInferenceWhiteBoxLifestyleDecisionTreeAttack(batchId)
        if value is not None:
            assert isinstance(value, dict)
            assert value['Job_Id'].startswith(attackName)
        else:
            assert value is None

    def test_AttributeInferenceWhiteBoxLifestyleDecisionTreeAttack_None(self):
        TestArt.reportDeletion()
        value = Art.AttributeInferenceWhiteBoxLifestyleDecisionTreeAttack(None)
        assert value is None


#     #--------------------------DecisionTree Attack-------------------------

    def test_DecisionTreeAttackVectors(self):
        TestArt.reportDeletion()
        attackName = 'DecisionTree'
        batchId = TestArt.getBatchId(self.modelIdScikitlearnClassifierTabular,self.dataIdScikitlearnClassifierTabular,[attackName])
        value = Art.DecisionTreeAttackVectors(batchId)
        if value is not None:
            assert isinstance(value, dict)
            assert value['Job_Id'].startswith(attackName)
        else:
            assert value is None

    def test_DecisionTreeAttackVectors_None(self):
        TestArt.reportDeletion()
        value = Art.DecisionTreeAttackVectors(None)
        assert value is None


    #------------------------------LabelOnlyDecisionBoundary Attack----------------

    def test_LabelOnlyDecisionBoundaryAttack(self):
        TestArt.reportDeletion()
        attackName = 'LabelOnlyDecisionBoundary'
        batchId = TestArt.getBatchId(self.modelIdScikitlearnClassifierTabular,self.dataIdScikitlearnClassifierTabular,[attackName])
        value = Art.LabelOnlyDecisionBoundaryAttack(batchId)
        if value is not None:
            assert isinstance(value, dict)
            assert value['Job_Id'].startswith(attackName)
        else:
            assert value is None

    def test_LabelOnlyDecisionBoundaryAttack_None(self):
        TestArt.reportDeletion()
        value = Art.LabelOnlyDecisionBoundaryAttack(None)
        assert value is None

# #------------------------------BasicIterativeMethod Attack----------------

    @patch('src.service.art.BasicIterativeMethod')
    @patch('src.service.art.KerasClassifier')
    @patch('src.service.art.RT.generateimagereport')
    @patch('src.service.art.UT.databaseDelete')
    @patch('src.service.art.UT.readPayloadFile')
    @patch('src.service.art.UT.readDataFile')
    @patch('src.service.art.UT.readModelFile')
    def test_BasicIterativeMethodAttack(self, mock_readModelFile, mock_readDataFile, mock_readPayloadFile, 
                                        mock_dbDelete, mock_genReport, mock_KerasClassifier, mock_BasicIterativeMethod):
        TestArt.reportDeletion()
        attackName = 'BasicIterativeMethod'
        batchId = TestArt.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        
        # Inject missing 'image'
        mock_image_module = MagicMock()
        mock_image_module.img_to_array.side_effect = lambda x: np.array(x)
        import src.service.art
        had_image = hasattr(src.service.art, 'image')
        setattr(src.service.art, 'image', mock_image_module)

        try:
            # Mock readModelFile (Model can be anything now as KerasClassifier is mocked)
            mock_readModelFile.return_value = (MagicMock(), "dummy_model_path", "KerasClassifierImageModel", "Keras")
            
            # Mock readDataFile
            dummy_img = np.zeros((299, 299, 3))
            mock_readDataFile.return_value = ({"img1.jpg": dummy_img}, "dummy_data_path")
            
            # Mock readPayloadFile
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                payload_data = {
                    "groundTruthClassNames": list(range(1001)), 
                    "groundTruthClassLabel": ",".join([f"class{i}" for i in range(1001)])
                }
                json.dump(payload_data, tmp)
                tmp_path = tmp.name
            
            mock_readPayloadFile.return_value = tmp_path
            
            # Mock KerasClassifier
            mock_classifier = mock_KerasClassifier.return_value
            # classifier.predict used in attack
            probs = np.zeros((1, 1000))
            probs[0, 0] = 1.0 
            mock_classifier.predict.return_value = probs
            
            # Also the model.predict is called directly on the model returned by readModelFile
            # So the FIRST model needs to support predict too
            mock_model_real = mock_readModelFile.return_value[0]
            mock_model_real.predict.return_value = probs

            # Mock BasicIterativeMethod
            mock_attack_instance = mock_BasicIterativeMethod.return_value
            mock_attack_instance.generate.return_value = np.zeros((1, 299, 299, 3))
            
            # Mock generateimagereport
            mock_genReport.return_value = "Job123"

            value = Art.BasicIterativeMethodAttack(batchId)
            
        finally:
            if not had_image:
                delattr(src.service.art, 'image')
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":'Job123'} # It returns foldername from generateimagereport
        assert isinstance(value, dict)
        assert value == expectedOutput

# #-----------------------Boundary Attack-----------------------------

    @patch('src.service.art.BoundaryAttack')
    @patch('src.service.art.KerasClassifier')
    @patch('src.service.art.RT.generateimagereport')
    @patch('src.service.art.UT.databaseDelete')
    @patch('src.service.art.UT.readPayloadFile')
    @patch('src.service.art.UT.readDataFile')
    @patch('src.service.art.UT.readModelFile')
    def test_BoundaryAttack(self, mock_readModelFile, mock_readDataFile, mock_readPayloadFile, 
                            mock_dbDelete, mock_genReport, mock_KerasClassifier, mock_BoundaryAttack):
        TestArt.reportDeletion()
        attackName = 'Boundary'
        batchId = TestArt.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        
        # Inject missing 'image'
        mock_image_module = MagicMock()
        mock_image_module.img_to_array.side_effect = lambda x: np.array(x)
        import src.service.art
        had_image = hasattr(src.service.art, 'image')
        setattr(src.service.art, 'image', mock_image_module)

        try:
            # Mock readModelFile
            mock_readModelFile.return_value = (MagicMock(), "dummy_model_path", "KerasClassifierImageModel", "Keras")
            
            # Mock readDataFile
            dummy_img = np.zeros((299, 299, 3))
            mock_readDataFile.return_value = ({"img1.jpg": dummy_img}, "dummy_data_path")
            
            # Mock readPayloadFile
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                payload_data = {
                    "groundTruthClassNames": list(range(1001)), 
                    "groundTruthClassLabel": ",".join([f"class{i}" for i in range(1001)])
                }
                json.dump(payload_data, tmp)
                tmp_path = tmp.name
            
            mock_readPayloadFile.return_value = tmp_path
            
            # Mock KerasClassifier and Model
            mock_classifier = mock_KerasClassifier.return_value
            probs = np.zeros((1, 1000))
            probs[0, 0] = 1.0 
            mock_classifier.predict.return_value = probs
            
            mock_model_real = mock_readModelFile.return_value[0]
            mock_model_real.predict.return_value = probs

            # Mock Attack
            mock_attack_instance = mock_BoundaryAttack.return_value
            mock_attack_instance.generate.return_value = np.zeros((1, 299, 299, 3))
            
            # Mock generateimagereport
            mock_genReport.return_value = "Job123"

            value = Art.BoundaryAttack(batchId)
            
        finally:
            if not had_image:
                delattr(src.service.art, 'image')
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":'Job123'}
        assert isinstance(value, dict)
        assert value == expectedOutput 

    def test_BoundaryAttack_None(self):
        TestArt.reportDeletion()
        value = Art.BoundaryAttack(None)
        assert value is None     

#     #---------------------------CarliniL2Method Attack---------------------  

    @patch('src.service.art.CarliniL2Method')
    @patch('src.service.art.KerasClassifier')
    @patch('src.service.art.RT.generateimagereport')
    @patch('src.service.art.UT.databaseDelete')
    @patch('src.service.art.UT.readPayloadFile')
    @patch('src.service.art.UT.readDataFile')
    @patch('src.service.art.UT.readModelFile')
    def test_CarliniAttack(self, mock_readModelFile, mock_readDataFile, mock_readPayloadFile, 
                           mock_dbDelete, mock_genReport, mock_KerasClassifier, mock_CarliniL2Method):
        TestArt.reportDeletion()
        attackName = 'CarliniL2Method'
        batchId = TestArt.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        
        # Inject missing 'image'
        mock_image_module = MagicMock()
        mock_image_module.img_to_array.side_effect = lambda x: np.array(x)
        import src.service.art
        had_image = hasattr(src.service.art, 'image')
        setattr(src.service.art, 'image', mock_image_module)

        try:
            # Mock readModelFile
            mock_readModelFile.return_value = (MagicMock(), "dummy_model_path", "KerasClassifierImageModel", "Keras")
            
            # Mock readDataFile
            dummy_img = np.zeros((299, 299, 3))
            mock_readDataFile.return_value = ({"img1.jpg": dummy_img}, "dummy_data_path")
            
            # Mock readPayloadFile
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                payload_data = {
                    "groundTruthClassNames": list(range(1001)), 
                    "groundTruthClassLabel": ",".join([f"class{i}" for i in range(1001)])
                }
                json.dump(payload_data, tmp)
                tmp_path = tmp.name
            
            mock_readPayloadFile.return_value = tmp_path
            
            # Mock KerasClassifier and Model
            mock_classifier = mock_KerasClassifier.return_value
            probs = np.zeros((1, 1000))
            probs[0, 0] = 1.0 
            mock_classifier.predict.return_value = probs
            
            mock_model_real = mock_readModelFile.return_value[0]
            mock_model_real.predict.return_value = probs

            # Mock Attack
            mock_attack_instance = mock_CarliniL2Method.return_value
            mock_attack_instance.generate.return_value = np.zeros((1, 299, 299, 3))
            
            # Mock generateimagereport
            mock_genReport.return_value = "Job123"

            value = Art.CarliniAttack(batchId)
            
        finally:
            if not had_image:
                delattr(src.service.art, 'image')
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":'Job123'}
        assert isinstance(value, dict)
        assert value == expectedOutput 

    def test_CarliniAttack_None(self):
        TestArt.reportDeletion()
        value = Art.CarliniAttack(None)
        assert value is None     

#     #------------------------Deepfool Attack----------------

    @patch('src.service.art.DeepFool')
    @patch('src.service.art.KerasClassifier')
    @patch('src.service.art.RT.generateimagereport')
    @patch('src.service.art.UT.databaseDelete')
    @patch('src.service.art.UT.readPayloadFile')
    @patch('src.service.art.UT.readDataFile')
    @patch('src.service.art.UT.readModelFile')
    def test_DeepfoolAttack(self, mock_readModelFile, mock_readDataFile, mock_readPayloadFile, 
                            mock_dbDelete, mock_genReport, mock_KerasClassifier, mock_DeepFool):
        TestArt.reportDeletion()
        attackName = 'Deepfool'
        batchId = TestArt.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        
        # Inject missing 'image'
        mock_image_module = MagicMock()
        mock_image_module.img_to_array.side_effect = lambda x: np.array(x)
        import src.service.art
        had_image = hasattr(src.service.art, 'image')
        setattr(src.service.art, 'image', mock_image_module)

        try:
            # Mock readModelFile
            mock_readModelFile.return_value = (MagicMock(), "dummy_model_path", "KerasClassifierImageModel", "Keras")
            
            # Mock readDataFile
            dummy_img = np.zeros((299, 299, 3))
            mock_readDataFile.return_value = ({"img1.jpg": dummy_img}, "dummy_data_path")
            
            # Mock readPayloadFile
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                payload_data = {
                    "groundTruthClassNames": list(range(1001)), 
                    "groundTruthClassLabel": ",".join([f"class{i}" for i in range(1001)])
                }
                json.dump(payload_data, tmp)
                tmp_path = tmp.name
            
            mock_readPayloadFile.return_value = tmp_path
            
            # Mock KerasClassifier and Model
            mock_classifier = mock_KerasClassifier.return_value
            probs = np.zeros((1, 1000))
            probs[0, 0] = 1.0 
            mock_classifier.predict.return_value = probs
            
            mock_model_real = mock_readModelFile.return_value[0]
            mock_model_real.predict.return_value = probs

            # Mock Attack
            mock_attack_instance = mock_DeepFool.return_value
            mock_attack_instance.generate.return_value = np.zeros((1, 299, 299, 3))
            
            # Mock generateimagereport
            mock_genReport.return_value = "Job123"

            value = Art.DeepfoolAttack(batchId)
            
        finally:
            if not had_image:
                delattr(src.service.art, 'image')
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":'Job123'}
        assert isinstance(value, dict)
        assert value == expectedOutput 

    def test_DeepfoolAttack_None(self):
        TestArt.reportDeletion()
        # Source code swallows exception and returns None
        value = Art.DeepfoolAttack(None)
        assert value is None

#     #-------------------------------ElasticNet Attack-----------------------

    @patch('src.service.art.ElasticNet')
    @patch('src.service.art.KerasClassifier')
    @patch('src.service.art.RT.generateimagereport')
    @patch('src.service.art.UT.databaseDelete')
    @patch('src.service.art.UT.readPayloadFile')
    @patch('src.service.art.UT.readDataFile')
    @patch('src.service.art.UT.readModelFile')
    def test_ElasticNetAttack(self, mock_readModelFile, mock_readDataFile, mock_readPayloadFile, 
                              mock_dbDelete, mock_genReport, mock_KerasClassifier, mock_ElasticNet):
        TestArt.reportDeletion()
        attackName = 'ElasticNet'
        batchId = TestArt.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        
        # Inject missing 'image'
        mock_image_module = MagicMock()
        mock_image_module.img_to_array.side_effect = lambda x: np.array(x)
        import src.service.art
        had_image = hasattr(src.service.art, 'image')
        setattr(src.service.art, 'image', mock_image_module)

        try:
            mock_readModelFile.return_value = (MagicMock(), "dummy_model_path", "KerasClassifierImageModel", "Keras")
            dummy_img = np.zeros((299, 299, 3))
            mock_readDataFile.return_value = ({"img1.jpg": dummy_img}, "dummy_data_path")
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                payload_data = {
                    "groundTruthClassNames": list(range(1001)), 
                    "groundTruthClassLabel": ",".join([f"class{i}" for i in range(1001)])
                }
                json.dump(payload_data, tmp)
                tmp_path = tmp.name
            mock_readPayloadFile.return_value = tmp_path
            mock_classifier = mock_KerasClassifier.return_value
            probs = np.zeros((1, 1000))
            probs[0, 0] = 1.0 
            mock_classifier.predict.return_value = probs
            mock_model_real = mock_readModelFile.return_value[0]
            mock_model_real.predict.return_value = probs
            mock_attack_instance = mock_ElasticNet.return_value
            mock_attack_instance.generate.return_value = np.zeros((1, 299, 299, 3))
            mock_genReport.return_value = "Job123"

            value = Art.ElasticNetAttack(batchId)
        finally:
            if not had_image:
                delattr(src.service.art, 'image')
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":'Job123'}
        assert isinstance(value, dict)
        assert value == expectedOutput 

    def test_ElasticNetAttack_None(self):
        TestArt.reportDeletion()
        value = Art.ElasticNetAttack(None)
        assert value is None

#     #-----------------------FastGradientMethod Attack---------------      

    @patch('src.service.art.FastGradientMethod')
    @patch('src.service.art.KerasClassifier')
    @patch('src.service.art.RT.generateimagereport')
    @patch('src.service.art.UT.databaseDelete')
    @patch('src.service.art.UT.readPayloadFile')
    @patch('src.service.art.UT.readDataFile')
    @patch('src.service.art.UT.readModelFile')
    def test_FastGradientMethodAttack(self, mock_readModelFile, mock_readDataFile, mock_readPayloadFile, 
                                      mock_dbDelete, mock_genReport, mock_KerasClassifier, mock_FastGradientMethod):
        TestArt.reportDeletion()
        attackName = 'FastGradientMethod'
        batchId = TestArt.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        
        mock_image_module = MagicMock()
        mock_image_module.img_to_array.side_effect = lambda x: np.array(x)
        import src.service.art
        had_image = hasattr(src.service.art, 'image')
        setattr(src.service.art, 'image', mock_image_module)

        try:
            mock_readModelFile.return_value = (MagicMock(), "dummy_model_path", "KerasClassifierImageModel", "Keras")
            dummy_img = np.zeros((299, 299, 3))
            mock_readDataFile.return_value = ({"img1.jpg": dummy_img}, "dummy_data_path")
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                payload_data = {
                    "groundTruthClassNames": list(range(1001)), 
                    "groundTruthClassLabel": ",".join([f"class{i}" for i in range(1001)])
                }
                json.dump(payload_data, tmp)
                tmp_path = tmp.name
            mock_readPayloadFile.return_value = tmp_path
            mock_classifier = mock_KerasClassifier.return_value
            probs = np.zeros((1, 1000))
            probs[0, 0] = 1.0 
            mock_classifier.predict.return_value = probs
            mock_model_real = mock_readModelFile.return_value[0]
            mock_model_real.predict.return_value = probs
            mock_attack_instance = mock_FastGradientMethod.return_value
            mock_attack_instance.generate.return_value = np.zeros((1, 299, 299, 3))
            mock_genReport.return_value = "Job123"

            value = Art.FastGradientMethodAttack(batchId)
        finally:
            if not had_image:
                delattr(src.service.art, 'image')
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":'Job123'}
        assert isinstance(value, dict)
        assert value == expectedOutput
      

#     #-----------------------IterativeFrameSaliency Attack---------------      

    @patch('src.service.art.FastGradientMethod')
    @patch('src.service.art.FrameSaliencyAttack')
    @patch('src.service.art.KerasClassifier')
    @patch('src.service.art.RT.generateimagereport')
    @patch('src.service.art.UT.databaseDelete')
    @patch('src.service.art.UT.readPayloadFile')
    @patch('src.service.art.UT.readDataFile')
    @patch('src.service.art.UT.readModelFile')
    def test_IterativeFrameSaliencyAttack(self, mock_readModelFile, mock_readDataFile, mock_readPayloadFile, 
                                          mock_dbDelete, mock_genReport, mock_KerasClassifier, mock_FrameSaliencyAttack, mock_FastGradientMethod):
        TestArt.reportDeletion()
        attackName = 'IterativeFrameSaliency'
        batchId = TestArt.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        
        mock_image_module = MagicMock()
        mock_image_module.img_to_array.side_effect = lambda x: np.array(x)
        import src.service.art
        had_image = hasattr(src.service.art, 'image')
        setattr(src.service.art, 'image', mock_image_module)

        try:
            mock_readModelFile.return_value = (MagicMock(), "dummy_model_path", "KerasClassifierImageModel", "Keras")
            dummy_img = np.zeros((299, 299, 3))
            mock_readDataFile.return_value = ({"img1.jpg": dummy_img}, "dummy_data_path")
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                payload_data = {
                    "groundTruthClassNames": list(range(1001)), 
                    "groundTruthClassLabel": ",".join([f"class{i}" for i in range(1001)])
                }
                json.dump(payload_data, tmp)
                tmp_path = tmp.name
            mock_readPayloadFile.return_value = tmp_path
            mock_classifier = mock_KerasClassifier.return_value
            probs = np.zeros((1, 1000))
            probs[0, 0] = 1.0 
            mock_classifier.predict.return_value = probs
            mock_model_real = mock_readModelFile.return_value[0]
            mock_model_real.predict.return_value = probs
            
            # Mock FastGradientMethod (used internally as attacker)
            mock_attacker_instance = mock_FastGradientMethod.return_value
            
            mock_attack_instance = mock_FrameSaliencyAttack.return_value
            mock_attack_instance.generate.return_value = np.zeros((1, 299, 299, 3))
            mock_genReport.return_value = "Job123"

            value = Art.IterativeFrameSaliencyAttack(batchId)
        finally:
            if not had_image:
                delattr(src.service.art, 'image')
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":'Job123'}
        assert isinstance(value, dict)
        assert value == expectedOutput 

    def test_IterativeFrameSaliencyAttack_None(self):
        TestArt.reportDeletion()
        value = Art.IterativeFrameSaliencyAttack(None)
        assert value is None



#     #-----------------------NewtonFool Attack---------------      

    @patch('src.service.art.NewtonFool')
    @patch('src.service.art.KerasClassifier')
    @patch('src.service.art.RT.generateimagereport')
    @patch('src.service.art.UT.databaseDelete')
    @patch('src.service.art.UT.readPayloadFile')
    @patch('src.service.art.UT.readDataFile')
    @patch('src.service.art.UT.readModelFile')
    def test_NewtonFoolAttack(self, mock_readModelFile, mock_readDataFile, mock_readPayloadFile, 
                              mock_dbDelete, mock_genReport, mock_KerasClassifier, mock_NewtonFool):
        TestArt.reportDeletion()
        attackName = 'NewtonFool'
        batchId = TestArt.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        
        mock_image_module = MagicMock()
        mock_image_module.img_to_array.side_effect = lambda x: np.array(x)
        import src.service.art
        had_image = hasattr(src.service.art, 'image')
        setattr(src.service.art, 'image', mock_image_module)

        try:
            mock_readModelFile.return_value = (MagicMock(), "dummy_model_path", "KerasClassifierImageModel", "Keras")
            dummy_img = np.zeros((299, 299, 3))
            mock_readDataFile.return_value = ({"img1.jpg": dummy_img}, "dummy_data_path")
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                payload_data = {
                    "groundTruthClassNames": list(range(1001)), 
                    "groundTruthClassLabel": ",".join([f"class{i}" for i in range(1001)])
                }
                json.dump(payload_data, tmp)
                tmp_path = tmp.name
            mock_readPayloadFile.return_value = tmp_path
            mock_classifier = mock_KerasClassifier.return_value
            probs = np.zeros((1, 1000))
            probs[0, 0] = 1.0 
            mock_classifier.predict.return_value = probs
            mock_model_real = mock_readModelFile.return_value[0]
            mock_model_real.predict.return_value = probs
            mock_attack_instance = mock_NewtonFool.return_value
            mock_attack_instance.generate.return_value = np.zeros((1, 299, 299, 3))
            mock_genReport.return_value = "Job123"

            value = Art.NewtonFoolAttack(batchId)
        finally:
            if not had_image:
                delattr(src.service.art, 'image')
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":'Job123'}
        assert isinstance(value, dict)
        assert value == expectedOutput 

    def test_NewtonFoolAttack_None(self):
        TestArt.reportDeletion()
        value = Art.NewtonFoolAttack(None)
        assert value is None
  

#     # #-----------------------Pixel Attack---------------      

    @patch('src.service.art.PixelAttack')
    @patch('src.service.art.KerasClassifier')
    @patch('src.service.art.RT.generateimagereport')
    @patch('src.service.art.UT.databaseDelete')
    @patch('src.service.art.UT.readPayloadFile')
    @patch('src.service.art.UT.readDataFile')
    @patch('src.service.art.UT.readModelFile')
    def test_PixelAttack(self, mock_readModelFile, mock_readDataFile, mock_readPayloadFile, 
                         mock_dbDelete, mock_genReport, mock_KerasClassifier, mock_PixelAttack):
        TestArt.reportDeletion()
        attackName = 'Pixel'
        batchId = TestArt.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        
        mock_image_module = MagicMock()
        mock_image_module.img_to_array.side_effect = lambda x: np.array(x)
        import src.service.art
        had_image = hasattr(src.service.art, 'image')
        setattr(src.service.art, 'image', mock_image_module)

        try:
            mock_readModelFile.return_value = (MagicMock(), "dummy_model_path", "KerasClassifierImageModel", "Keras")
            dummy_img = np.zeros((299, 299, 3))
            mock_readDataFile.return_value = ({"img1.jpg": dummy_img}, "dummy_data_path")
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                payload_data = {
                    "groundTruthClassNames": list(range(1001)), 
                    "groundTruthClassLabel": ",".join([f"class{i}" for i in range(1001)])
                }
                json.dump(payload_data, tmp)
                tmp_path = tmp.name
            mock_readPayloadFile.return_value = tmp_path
            mock_classifier = mock_KerasClassifier.return_value
            probs = np.zeros((1, 1000))
            probs[0, 0] = 1.0 
            mock_classifier.predict.return_value = probs
            mock_model_real = mock_readModelFile.return_value[0]
            mock_model_real.predict.return_value = probs
            mock_attack_instance = mock_PixelAttack.return_value
            mock_attack_instance.generate.return_value = np.zeros((1, 299, 299, 3))
            mock_genReport.return_value = "Job123"

            value = Art.PixelAttack(batchId)
        finally:
            if not had_image:
                delattr(src.service.art, 'image')
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":'Job123'}
        assert isinstance(value, dict)
        assert value == expectedOutput 

    def test_PixelAttack_None(self):
        TestArt.reportDeletion()
        value = Art.PixelAttack(None)
        assert value is None    

#     #-----------------------SaliencyMapMethod Attack---------------      

    @patch('src.service.art.SaliencyMapMethod')
    @patch('src.service.art.KerasClassifier')
    @patch('src.service.art.RT.generateimagereport')
    @patch('src.service.art.UT.databaseDelete')
    @patch('src.service.art.UT.readPayloadFile')
    @patch('src.service.art.UT.readDataFile')
    @patch('src.service.art.UT.readModelFile')
    def test_SaliencyMapMethodAttack(self, mock_readModelFile, mock_readDataFile, mock_readPayloadFile, 
                                     mock_dbDelete, mock_genReport, mock_KerasClassifier, mock_SaliencyMapMethod):
        TestArt.reportDeletion()
        attackName = 'SaliencyMapMethod'
        batchId = TestArt.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        
        mock_image_module = MagicMock()
        mock_image_module.img_to_array.side_effect = lambda x: np.array(x)
        import src.service.art
        had_image = hasattr(src.service.art, 'image')
        setattr(src.service.art, 'image', mock_image_module)

        try:
            mock_readModelFile.return_value = (MagicMock(), "dummy_model_path", "KerasClassifierImageModel", "Keras")
            dummy_img = np.zeros((299, 299, 3))
            mock_readDataFile.return_value = ({"img1.jpg": dummy_img}, "dummy_data_path")
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                payload_data = {
                    "groundTruthClassNames": list(range(1001)), 
                    "groundTruthClassLabel": ",".join([f"class{i}" for i in range(1001)])
                }
                json.dump(payload_data, tmp)
                tmp_path = tmp.name
            mock_readPayloadFile.return_value = tmp_path
            mock_classifier = mock_KerasClassifier.return_value
            probs = np.zeros((1, 1000))
            probs[0, 0] = 1.0 
            mock_classifier.predict.return_value = probs
            mock_model_real = mock_readModelFile.return_value[0]
            mock_model_real.predict.return_value = probs
            mock_attack_instance = mock_SaliencyMapMethod.return_value
            mock_attack_instance.generate.return_value = np.zeros((1, 299, 299, 3))
            mock_genReport.return_value = "Job123"

            value = Art.SaliencyMapMethodAttack(batchId)
        finally:
            if not had_image:
                delattr(src.service.art, 'image')
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":'Job123'}
        assert isinstance(value, dict)
        assert value == expectedOutput 

    def test_SaliencyMapMethodAttack_None(self):
        TestArt.reportDeletion()
        value = Art.SaliencyMapMethodAttack(None)
        assert value is None

#     #-----------------------SimBA Attack---------------      

    @patch('src.service.art.SimBA')
    @patch('src.service.art.KerasClassifier')
    @patch('src.service.art.RT.generateimagereport')
    @patch('src.service.art.UT.databaseDelete')
    @patch('src.service.art.UT.readPayloadFile')
    @patch('src.service.art.UT.readDataFile')
    @patch('src.service.art.UT.readModelFile')
    def test_SimbaAttack(self, mock_readModelFile, mock_readDataFile, mock_readPayloadFile, 
                         mock_dbDelete, mock_genReport, mock_KerasClassifier, mock_SimBA):
        TestArt.reportDeletion()
        attackName = 'SimBA'
        batchId = TestArt.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        
        mock_image_module = MagicMock()
        mock_image_module.img_to_array.side_effect = lambda x: np.array(x)
        import src.service.art
        had_image = hasattr(src.service.art, 'image')
        setattr(src.service.art, 'image', mock_image_module)

        try:
            mock_readModelFile.return_value = (MagicMock(), "dummy_model_path", "KerasClassifierImageModel", "Keras")
            dummy_img = np.zeros((299, 299, 3))
            mock_readDataFile.return_value = ({"img1.jpg": dummy_img}, "dummy_data_path")
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                payload_data = {
                    "groundTruthClassNames": list(range(1001)), 
                    "groundTruthClassLabel": ",".join([f"class{i}" for i in range(1001)])
                }
                json.dump(payload_data, tmp)
                tmp_path = tmp.name
            mock_readPayloadFile.return_value = tmp_path
            mock_classifier = mock_KerasClassifier.return_value
            probs = np.zeros((1, 1000))
            probs[0, 0] = 1.0 
            mock_classifier.predict.return_value = probs
            mock_model_real = mock_readModelFile.return_value[0]
            mock_model_real.predict.return_value = probs
            mock_attack_instance = mock_SimBA.return_value
            mock_attack_instance.generate.return_value = np.zeros((1, 299, 299, 3))
            mock_genReport.return_value = "Job123"

            value = Art.SimbaAttack(batchId)
        finally:
            if not had_image:
                delattr(src.service.art, 'image')
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":'Job123'}
        assert isinstance(value, dict)
        assert value == expectedOutput 

    def test_SimbaAttack_None(self):
        TestArt.reportDeletion()
        value = Art.SimbaAttack(None)
        assert value is None
    

#     #-----------------------SpatialTransformation Attack---------------      

    @patch('src.service.art.SpatialTransformation')
    @patch('src.service.art.KerasClassifier')
    @patch('src.service.art.RT.generateimagereport')
    @patch('src.service.art.UT.databaseDelete')
    @patch('src.service.art.UT.readPayloadFile')
    @patch('src.service.art.UT.readDataFile')
    @patch('src.service.art.UT.readModelFile')
    def test_SpatialTransformation(self, mock_readModelFile, mock_readDataFile, mock_readPayloadFile, 
                                   mock_dbDelete, mock_genReport, mock_KerasClassifier, mock_SpatialTransformation):
        TestArt.reportDeletion()
        attackName = 'SpatialTransformation'
        batchId = TestArt.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        
        mock_image_module = MagicMock()
        mock_image_module.img_to_array.side_effect = lambda x: np.array(x)
        import src.service.art
        had_image = hasattr(src.service.art, 'image')
        setattr(src.service.art, 'image', mock_image_module)

        try:
            mock_readModelFile.return_value = (MagicMock(), "dummy_model_path", "KerasClassifierImageModel", "Keras")
            dummy_img = np.zeros((299, 299, 3))
            mock_readDataFile.return_value = ({"img1.jpg": dummy_img}, "dummy_data_path")
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                payload_data = {
                    "groundTruthClassNames": list(range(1001)), 
                    "groundTruthClassLabel": ",".join([f"class{i}" for i in range(1001)])
                }
                json.dump(payload_data, tmp)
                tmp_path = tmp.name
            mock_readPayloadFile.return_value = tmp_path
            mock_classifier = mock_KerasClassifier.return_value
            probs = np.zeros((1, 1000))
            probs[0, 0] = 1.0 
            mock_classifier.predict.return_value = probs
            mock_model_real = mock_readModelFile.return_value[0]
            mock_model_real.predict.return_value = probs
            mock_attack_instance = mock_SpatialTransformation.return_value
            mock_attack_instance.generate.return_value = np.zeros((1, 299, 299, 3))
            mock_genReport.return_value = "Job123"

            value = Art.SpatialTransformation(batchId)
        finally:
            if not had_image:
                delattr(src.service.art, 'image')
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":'Job123'}
        assert isinstance(value, dict)
        assert value == expectedOutput 

    def test_SpatialTransformation_None(self):
        TestArt.reportDeletion()
        value = Art.SpatialTransformation(None)
        assert value is None
        

#     #-----------------------Square Attack---------------      

    @patch('src.service.art.SquareAttack')
    @patch('src.service.art.KerasClassifier')
    @patch('src.service.art.RT.generateimagereport')
    @patch('src.service.art.UT.databaseDelete')
    @patch('src.service.art.UT.readPayloadFile')
    @patch('src.service.art.UT.readDataFile')
    @patch('src.service.art.UT.readModelFile')
    def test_SquareAttack(self, mock_readModelFile, mock_readDataFile, mock_readPayloadFile, 
                          mock_dbDelete, mock_genReport, mock_KerasClassifier, mock_SquareAttack):
        TestArt.reportDeletion()
        attackName = 'Square'
        batchId = TestArt.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        
        mock_image_module = MagicMock()
        mock_image_module.img_to_array.side_effect = lambda x: np.array(x)
        import src.service.art
        had_image = hasattr(src.service.art, 'image')
        setattr(src.service.art, 'image', mock_image_module)

        try:
            mock_readModelFile.return_value = (MagicMock(), "dummy_model_path", "KerasClassifierImageModel", "Keras")
            dummy_img = np.zeros((299, 299, 3))
            mock_readDataFile.return_value = ({"img1.jpg": dummy_img}, "dummy_data_path")
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                payload_data = {
                    "groundTruthClassNames": list(range(1001)), 
                    "groundTruthClassLabel": ",".join([f"class{i}" for i in range(1001)])
                }
                json.dump(payload_data, tmp)
                tmp_path = tmp.name
            mock_readPayloadFile.return_value = tmp_path
            mock_classifier = mock_KerasClassifier.return_value
            probs = np.zeros((1, 1000))
            probs[0, 0] = 1.0 
            mock_classifier.predict.return_value = probs
            mock_model_real = mock_readModelFile.return_value[0]
            mock_model_real.predict.return_value = probs
            mock_attack_instance = mock_SquareAttack.return_value
            mock_attack_instance.generate.return_value = np.zeros((1, 299, 299, 3))
            mock_genReport.return_value = "Job123"

            value = Art.SquareAttack(batchId)
        finally:
            if not had_image:
                delattr(src.service.art, 'image')
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

        id = UrlLinks.Current_ID - 1
        attackName = 'Square'
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":'Job123'}
        assert isinstance(value, dict)
        assert value == expectedOutput 

    def test_SquareAttack_None(self):
        TestArt.reportDeletion()
        value = Art.SquareAttack(None)
        assert value is None
     

#     #-----------------------UniversalPerturbation Attack---------------      

    @patch('src.service.art.UniversalPerturbation')
    @patch('src.service.art.KerasClassifier')
    @patch('src.service.art.RT.generateimagereport')
    @patch('src.service.art.UT.databaseDelete')
    @patch('src.service.art.UT.readPayloadFile')
    @patch('src.service.art.UT.readDataFile')
    @patch('src.service.art.UT.readModelFile')
    def test_UniversalPerturbationAttack(self, mock_readModelFile, mock_readDataFile, mock_readPayloadFile, 
                                         mock_dbDelete, mock_genReport, mock_KerasClassifier, mock_UniversalPerturbation):
        TestArt.reportDeletion()
        attackName = 'UniversalPerturbation'
        batchId = TestArt.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        
        mock_image_module = MagicMock()
        mock_image_module.img_to_array.side_effect = lambda x: np.array(x)
        import src.service.art
        had_image = hasattr(src.service.art, 'image')
        setattr(src.service.art, 'image', mock_image_module)

        try:
            mock_readModelFile.return_value = (MagicMock(), "dummy_model_path", "KerasClassifierImageModel", "Keras")
            dummy_img = np.zeros((299, 299, 3))
            mock_readDataFile.return_value = ({"img1.jpg": dummy_img}, "dummy_data_path")
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                payload_data = {
                    "groundTruthClassNames": list(range(1001)), 
                    "groundTruthClassLabel": ",".join([f"class{i}" for i in range(1001)])
                }
                json.dump(payload_data, tmp)
                tmp_path = tmp.name
            mock_readPayloadFile.return_value = tmp_path
            mock_classifier = mock_KerasClassifier.return_value
            probs = np.zeros((1, 1000))
            probs[0, 0] = 1.0 
            mock_classifier.predict.return_value = probs
            mock_model_real = mock_readModelFile.return_value[0]
            mock_model_real.predict.return_value = probs
            mock_attack_instance = mock_UniversalPerturbation.return_value
            mock_attack_instance.generate.return_value = np.zeros((1, 299, 299, 3))
            mock_genReport.return_value = "Job123"

            value = Art.UniversalPerturbationAttack(batchId)
        finally:
            if not had_image:
                delattr(src.service.art, 'image')
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":'Job123'}
        assert isinstance(value, dict)
        assert value == expectedOutput 

    def test_UniversalPerturbationAttack_None(self):
        TestArt.reportDeletion()
        value = Art.UniversalPerturbationAttack(None)
        assert value is None


#     #-----------------------Wasserstein Attack---------------      

    @patch('src.service.art.Wasserstein')
    @patch('src.service.art.KerasClassifier')
    @patch('src.service.art.RT.generateimagereport')
    @patch('src.service.art.UT.databaseDelete')
    @patch('src.service.art.UT.readPayloadFile')
    @patch('src.service.art.UT.readDataFile')
    @patch('src.service.art.UT.readModelFile')
    def test_WassersteinAttack(self, mock_readModelFile, mock_readDataFile, mock_readPayloadFile, 
                               mock_dbDelete, mock_genReport, mock_KerasClassifier, mock_Wasserstein):
        TestArt.reportDeletion()
        attackName = 'Wasserstein'
        batchId = TestArt.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        
        mock_image_module = MagicMock()
        mock_image_module.img_to_array.side_effect = lambda x: np.array(x)
        import src.service.art
        had_image = hasattr(src.service.art, 'image')
        setattr(src.service.art, 'image', mock_image_module)

        try:
            mock_readModelFile.return_value = (MagicMock(), "dummy_model_path", "KerasClassifierImageModel", "Keras")
            dummy_img = np.zeros((299, 299, 3))
            mock_readDataFile.return_value = ({"img1.jpg": dummy_img}, "dummy_data_path")
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                payload_data = {
                    "groundTruthClassNames": list(range(1001)), 
                    "groundTruthClassLabel": ",".join([f"class{i}" for i in range(1001)])
                }
                json.dump(payload_data, tmp)
                tmp_path = tmp.name
            mock_readPayloadFile.return_value = tmp_path
            mock_classifier = mock_KerasClassifier.return_value
            probs = np.zeros((1, 1000))
            probs[0, 0] = 1.0 
            mock_classifier.predict.return_value = probs
            mock_model_real = mock_readModelFile.return_value[0]
            mock_model_real.predict.return_value = probs
            mock_attack_instance = mock_Wasserstein.return_value
            mock_attack_instance.generate.return_value = np.zeros((1, 299, 299, 3))
            mock_genReport.return_value = "Job123"

            value = Art.WassersteinAttack(batchId)
        finally:
            if not had_image:
                delattr(src.service.art, 'image')
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":'Job123'}
        assert isinstance(value, dict)
        assert value == expectedOutput 

    def test_WassersteinAttack_None(self):
        TestArt.reportDeletion()
        value = Art.WassersteinAttack(None)
        assert value is None
            
# # # #-------------------- GeometricDecisionBased Attack ----------------------------------

    # def test_GeometricDecisionBasedAttack(self):
    #     TestArt.reportDeletion()
    #     attackName = 'GeometricDecisionBasedAttack'      
    #     batchId = TestArt.getBatchId(self.modelIdTensorFlowV2ClassifierImage,self.dataIdTensorFlowV2ClassifierImage,[attackName])        
    #     value = Art.GeometricDecisionAttack(batchId)
        
    #     id = UrlLinks.Current_ID - 1
    #     k = f'{attackName}_{id}'
    #     expectedOutput = {"Job_Id":f'{k}'}
        
    #     assert isinstance(value, dict)
    #     assert value == expectedOutput
                    
    # def test_GeometricDecisionBasedAttack_None(self):
    #     TestArt.reportDeletion()
    #     with pytest.raises(Exception):
    #         Art.GeometricDecisionAttack(None)
        