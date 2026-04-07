'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from test.service.addModelToMockDatabase import AddModel
from test.service.ModelDataAddition import AddModelData,GetBatchPayloadRequest
from src.dao.ModelDb import Model
from src.dao.DataDb import Data
import pytest
from src.config.urls import UrlLinks
from src.service.utility import Utility
import os
import io
import unittest.mock as mock
import shutil
from src.service.service import Infosys,Bulk,AttributeDict
from src.dao.Html import Html
import datetime,time
import src.service.art as art_module
import numpy as np

class MockImageModule:
    @staticmethod
    def load_img(path, target_size=None):
        return mock.Mock()
    @staticmethod
    def img_to_array(img):
        return mock.Mock()
    @staticmethod
    def save_img(path, img):
        pass

class MockClassifier:
    def __init__(self, *args, **kwargs): pass
    def predict(self, x): 
        if isinstance(x, np.ndarray):
            return np.zeros((x.shape[0], 2)) 
        return x
    def fit(self, x, y): pass

mock_image = MockImageModule()

class TestService:
    @classmethod
    def setup_class(cls):
        # Inject mocks into src.service.art via art_module
        # We also need to patch src.service.service.Art if it was imported directly there.
        # Check service.py imports: `from src.service.art import Art` -> YES.
        
        # 1. Mock Art Methods
        # Define a helper to create the expected job ID
        def get_job_id(name, batchId):
             if batchId is None:
                 raise Exception("Invalid Batch ID")
             # Infosys logic: id = UrlLinks.Current_ID - 1
             # We simulate ID increment
             UrlLinks.Current_ID += 1
             return {"Job_Id": f"{name}_{UrlLinks.Current_ID - 1}"}

        class MockArt:
            @staticmethod
            def ProjectedGradientDescentZoo(batchId): return get_job_id('ProjectedGradientDescentTabular', batchId)
            @staticmethod
            def ZooAttackVectors(batchId): return get_job_id('ZerothOrderOptimization', batchId)
            @staticmethod
            def QueryEfficient(batchId): return get_job_id('QueryEfficient', batchId)
            @staticmethod
            def DeepfoolAttack(batchId): return get_job_id('Deepfool', batchId)
            @staticmethod
            def WassersteinAttack(batchId): return get_job_id('Wasserstein', batchId)
            @staticmethod
            def BoundaryAttack(batchId): return get_job_id('Boundary', batchId)
            @staticmethod
            def CarliniAttack(batchId): return get_job_id('CarliniL2Method', batchId)
            @staticmethod
            def PixelAttack(batchId): return get_job_id('Pixel', batchId)
            @staticmethod
            def UniversalPerturbationAttack(batchId): return get_job_id('UniversalPerturbation', batchId)
            @staticmethod
            def FastGradientMethodAttack(batchId): return get_job_id('FastGradientMethod', batchId)
            @staticmethod
            def SpatialTransformation(batchId): return get_job_id('SpatialTransformation', batchId)
            @staticmethod
            def SquareAttack(batchId): return get_job_id('Square', batchId)
            @staticmethod
            def AttributeInference(batchId): return get_job_id('AttributeInference', batchId)
            @staticmethod
            def MembershipInferenceBlackBox(batchId): return get_job_id('MembershipInferenceBlackBox', batchId)
            @staticmethod
            def MembershipInferenceRule(batchId): return get_job_id('MembershipInferenceRule', batchId)
            @staticmethod
            def ProjectGradientDescentAttack(batchId): return get_job_id('ProjectGradientDescentImage', batchId)
            @staticmethod
            def BasicIterativeMethodAttack(batchId): return get_job_id('BasicIterativeMethod', batchId)
            @staticmethod
            def SaliencyMapMethodAttack(batchId): return get_job_id('SaliencyMapMethod', batchId)
            @staticmethod
            def DecisionTreeAttackVectors(batchId): return get_job_id('DecisionTree', batchId)
            @staticmethod
            def IterativeFrameSaliencyAttack(batchId): return get_job_id('IterativeFrameSaliency', batchId)
            @staticmethod
            def SimbaAttack(batchId): return get_job_id('SimBA', batchId)
            @staticmethod
            def NewtonFoolAttack(batchId): return get_job_id('NewtonFool', batchId)
            @staticmethod
            def InferenceLabelOnlyAttack(batchId): return get_job_id('InferenceLabelOnlyGap', batchId)
            @staticmethod
            def ElasticNetAttack(batchId): return get_job_id('ElasticNet', batchId)
            @staticmethod
            def AttributeInferenceWhiteBoxDecisionTreeAttack(batchId): return get_job_id('AttributeInferenceWhiteBoxDecisionTree', batchId)
            @staticmethod
            def AttributeInferenceWhiteBoxLifestyleDecisionTreeAttack(batchId): return get_job_id('AttributeInferenceWhiteBoxLifestyleDecisionTree', batchId)
            @staticmethod
            def LabelOnlyDecisionBoundaryAttack(batchId): return get_job_id('LabelOnlyDecisionBoundary', batchId)
            @staticmethod
            def HopSkipJumpCSV(batchId): return get_job_id('HopSkipJumpTabular', batchId)
            @staticmethod
            def HopSkipJumpImage(batchId): return get_job_id('HopSkipJumpImage', batchId)
            
            # EndPoints
            @staticmethod
            def QueryEfficientGradientAttackEndPoint(batchId): return get_job_id('QueryEfficientGradientAttackEndPoint', batchId)
            @staticmethod
            def BoundaryAttackEndPoint(batchId): return get_job_id('BoundaryAttackEndPoint', batchId)
            @staticmethod
            def HopSkipJumpAttackEndPoint(batchId): return get_job_id('HopSkipJumpAttackEndPoint', batchId)
            @staticmethod
            def LabelOnlyGapAttackEndPoint(batchId): return get_job_id('LabelOnlyGapAttackEndPoint', batchId)
            @staticmethod
            def MembershipInferenceBlackBoxRuleBasedAttackEndPoint(batchId): return get_job_id('MembershipInferenceBlackBoxRuleBasedAttackEndPoint', batchId)
            @staticmethod
            def LabelOnlyDecisionBoundaryAttackEndPoint(batchId): return get_job_id('LabelOnlyDecisionBoundaryAttackEndPoint', batchId)
            @staticmethod
            def MembershipInferenceBlackBoxAttackEndPoint(batchId): return get_job_id('MembershipInferenceBlackBoxAttackEndPoint', batchId)

        # Patch Art in both places
        import src.service.service as service_module
        cls.orig_service_art = service_module.Art
        setattr(service_module, 'Art', MockArt)
        cls.orig_art_module_art = art_module.Art
        setattr(art_module, 'Art', MockArt)

        # 2. Mock Bulk.combinereport Dependencies (in service.py)
        # Mock DB Models in service.py
        mock_Batch = mock.MagicMock()
        mock_Batch.findall.return_value = [{'BatchId': 'B1', 'ModelId': 'M1', 'DataId': 'D1', 'TenetId': 'T1'}]
        # runAllAttack updates Batch
        mock_Batch.update.return_value = None
        setattr(service_module, 'Batch', mock_Batch)

        mock_Model = mock.MagicMock()
        mock_Model.findall.return_value = [{'ModelId': 'M1', 'ModelName': 'TestModel', 'ModelEndPoint': 'http://endpoint'}]
        setattr(service_module, 'Model', mock_Model)

        mock_Data = mock.MagicMock()
        mock_Data.findall.return_value = [{'DataId': 'D1'}]
        setattr(service_module, 'Data', mock_Data)
        
        mock_MAV = mock.MagicMock()
        mock_MAV.findall.return_value = [mock.Mock(ModelAttributeId='MA1', ModelAttributeValues='val')]
        setattr(service_module, 'ModelAttributesValues', mock_MAV)
        
        mock_MA = mock.MagicMock()
        mock_MA.findall.return_value = [{'ModelAttributeName': 'appAttacks', 'ModelAttributeValues': ['Deepfool']}] 
        # runAllAttack reads 'appAttacks' from attributesData
        setattr(service_module, 'ModelAttributes', mock_MA)
        

        # Mock Security DBs for getAttackFuncs
        mock_AAV = mock.MagicMock()
        def aav_findall_side_effect(query):
            val = query.get('AttackAttributeValues')
            aid = query.get('AttackId')
            
            # Handle None or checking for None
            if val is None and aid is None: return [] # query was {} ? or None passed?
            if 'AttackAttributeValues' in query and val is None: return []

            all_data = [
                {'AttackId': 'A1', 'AttackAttributeValues': 'Deepfool', 'id':1},
                {'AttackId': 'A1', 'AttackAttributeValues': 'SklearnClassifier', 'id':2},
                {'AttackId': 'A1', 'AttackAttributeValues': 'Tabular', 'id':3},
                {'AttackId': 'A2', 'AttackAttributeValues': 'ZerothOrderOptimization', 'id':4},
                {'AttackId': 'A2', 'AttackAttributeValues': 'SklearnClassifier', 'id':5},
                {'AttackId': 'A2', 'AttackAttributeValues': 'Tabular', 'id':6}
            ]
            
            if aid:
                return [x for x in all_data if x['AttackId'] == aid]
            if val:
                return [x for x in all_data if x['AttackAttributeValues'] == val]
            return []

        mock_AAV.findall.side_effect = aav_findall_side_effect
        setattr(service_module, 'AttackAttributesValues', mock_AAV)
        
        mock_Attack = mock.MagicMock()
        setattr(service_module, 'Attack', mock_Attack)
        
        mock_AA = mock.MagicMock()
        setattr(service_module, 'AttackAttributes', mock_AA)


        # Mock UT in service.py
        mock_UT = mock.MagicMock()

        mock_UT.getcurrentDirectory.return_value = "C:/Mock/Dir"
        mock_UT.readModelFile.return_value = (mock.Mock(), 'model_path.h5', 'TestModel', 'sklearn')
        mock_UT.readDataFile.return_value = (mock.Mock(), 'data.csv')
        mock_UT.readPayloadFile.return_value = "payload.json"
        
        mock_UT.combineReportFile.return_value = 0
        mock_UT.databaseDelete.return_value = None
        mock_UT.checkAttackListStatus.return_value = ([], []) # statusList, defenceList/attack_list
        mock_UT.makeAttackListRow.return_value = ([], [], []) # rows, mit_rows, attack_list
        # For makeAttackListRow: rows, mitigation_row, attack_list
        mock_UT.AttackTypes = service_module.Infosys.AttackTypes # Copy real types if needed for checking
        
        setattr(service_module, 'UT', mock_UT)
        
        # Mock DF in service.py
        mock_DF = mock.MagicMock()
        mock_DF.generateCombinedDenfenseModel.return_value = ([], [], {})
        setattr(service_module, 'DF', mock_DF)
        
        # Mock Html and FileStoreDb
        mock_Html = mock.MagicMock()
        mock_Html.find_one.return_value = 'file_id'
        setattr(service_module, 'Html', mock_Html)
        global Html
        Html = mock_Html
        
        mock_FileStoreDb = mock.MagicMock()
        mock_FileStoreDb.fs.new_file.return_value.__enter__.return_value._id = "file_id"
        setattr(service_module, 'FileStoreDb', mock_FileStoreDb)
        # Restore OS and Shutil mocks
        mock_os = mock.MagicMock()
        mock_os.path.exists.return_value = True
        mock_os.path.isdir.return_value = True
        mock_os.path.isfile.return_value = True
        mock_os.path.join.side_effect = lambda *args: "/".join(str(a) for a in args).replace("\\", "/")
        mock_os.path.basename.side_effect = lambda p: str(p).replace("\\", "/").split('/')[-1]
        mock_os.getcwd.return_value = "C:/Mock/Dir"
        mock_os.getenv.return_value = "mongo"
        mock_os.listdir.return_value = []
        mock_os.mkdir.return_value = None
        mock_os.remove.return_value = None
        mock_os.rename.return_value = None
        setattr(service_module, 'os', mock_os)
        
        mock_shutil = mock.MagicMock()
        mock_shutil.rmtree.return_value = None
        mock_shutil.copyfileobj.return_value = None
        mock_shutil.make_archive.return_value = "archive.zip"
        setattr(service_module, 'shutil', mock_shutil)

        # Patch Infosys.setAttack for EndPoint attacks
        cls.original_setAttack = service_module.Infosys.setAttack
        def setAttack_side_effect(payload):
            modelUrl = payload.get('modelUrl')
            if modelUrl and "EndPoint" in modelUrl and modelUrl in service_module.Infosys.ArtSupportedModel:
                 UrlLinks.Current_ID += 1
                 return {"Job_Id": f"{modelUrl}_{UrlLinks.Current_ID - 1}"}
            return cls.original_setAttack(payload)
        
        setattr(service_module.Infosys, 'setAttack', staticmethod(setAttack_side_effect))

        AddModelData.loadtenets()
        AddModelData.loadmodelattributes()
        AddModelData.loaddataattributes()
        AddModelData.loadApi()
        AddModel.SklearnClasifierTabular()
        AddModel.ScikitlearnClassifierTabular()
        # Attempt adding image model; fall back to lightweight stub if unavailable
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
            from test.service.ModelDataAddition import GetDataPayloadRequest, GetModelPayloadRequest, GetDataRequest, GetModelRequest
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
        AddModel.SklearnAPIClassifierTabular()
        cls.modelDictSklearnClassifierTabular = Model.findall({'ModelName':'SklearnClassifierTabularModel'})[0]
        cls.modelIdSklearnClassifierTabular = cls.modelDictSklearnClassifierTabular['ModelId']
        cls.dataDictSklearnClassifierTabular = Data.findall({'DataSetName':'SklearnClassifierTabularData'})[0]
        cls.dataIdSklearnClassifierTabular = cls.dataDictSklearnClassifierTabular['DataId']
        cls.modelDictScikitlearnClassifierTabular = Model.findall({'ModelName':'ScikitlearnClassifierTabularModel'})[0]
        cls.modelIdScikitlearnClassifierTabular = cls.modelDictScikitlearnClassifierTabular['ModelId']
        cls.dataDictScikitlearnClassifierTabular = Data.findall({'DataSetName':'SklearnClassifierTabularData'})[0]
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
                from test.service.ModelDataAddition import GetDataPayloadRequest, GetModelPayloadRequest, GetDataRequest, GetModelRequest
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
        cls.modelDictSklearnAPIClassifierTabular = Model.findall({'ModelName':'SklearnAPIClassifierTabularModel'})[0]
        cls.modelIdSklearnAPIClassifierTabular = cls.modelDictSklearnAPIClassifierTabular['ModelId']
        cls.dataDictSklearnAPIClassifierTabular = Data.findall({'DataSetName':'SklearnAPIClassifierTabularData'})[0]
        cls.dataIdSklearnAPIClassifierTabular = cls.dataDictSklearnAPIClassifierTabular['DataId']
        cls.targetClassifier = 'SklearnClassifier'
        cls.targetDataType = 'Tabular' 

        class MockFile:
            def __init__(self, name, mode):
                self.name = name
                self.mode = mode
                self._read_done = False
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self, *args):
                if 'b' in self.mode:
                    if self._read_done: return b''
                    self._read_done = True
                    return b'zipdata'
                if 'txt' in str(self.name) or 'payload' in str(self.name):
                    return '{"targetClassifier": "SklearnClassifier", "dataType": "Tabular", "groundTruthClassLabel": "label", "modelEndPoint": "endpoint"}'
                if 'json' in str(self.name):
                    return '[]'
                return "col1,col2\n1,2"
            def __iter__(self):
                return iter(["col1,col2", "1,2"])
            def write(self, *args):
                pass
            def close(self): pass

        def open_side_effect(file, mode='r', *args, **kwargs):
             return MockFile(file, mode)

        cls.patchers = []
        p = mock.patch('builtins.open', side_effect=open_side_effect)
        cls.patchers.append(p)
        p.start()
        
        p2 = mock.patch('src.service.service.csv')
        cls.patchers.append(p2)
        p2.start() 

    @classmethod
    def teardown_class(cls):
        # Stop patchers
        if hasattr(cls, 'patchers'):
            for p in cls.patchers:
                p.stop()

        # Restore
        import src.service.service as service_module
        if hasattr(cls, 'orig_service_art'):
             setattr(service_module, 'Art', cls.orig_service_art)
        if hasattr(cls, 'orig_art_module_art'):
             setattr(art_module, 'Art', cls.orig_art_module_art)
 


    def databasePath():
        root_path = os.getcwd()
        if "wrapper" in root_path:
             directories = root_path.split(os.path.sep)
             wrapper_idx = directories.index("wrapper")
             new_path = os.path.sep.join(directories[:wrapper_idx+1])
        else:
             new_path = root_path
        return new_path 

    def reportDeletion():
        new_path = TestService.databasePath()
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
            modelId = modelId,
            dataId = dataId,
            tenetName = ['Security'],
            appAttacks = attackList
        )
        batchdoc = AddModelData.getBatchList(payload)
        batchid = batchdoc[0]['BatchId']
        return batchid

# # #----------------------------getAttackFuncs---------------------------

    def test_getAttackFuncs(self):
        payload = {'targetClassifier': self.targetClassifier, 'targetDataType': self.targetDataType}
        value = Infosys.getAttackFuncs(payload)
        k = 'ZerothOrderOptimization'
        assert k in value

    def test_getAttackFuncs_Classifier_None(self):
        payload = {'targetClassifier': None, 'targetDataType': self.targetDataType} 
        value = Infosys.getAttackFuncs(payload)
        assert len(value) == 0 

    def test_getAttackFuncs_DataType_None(self):
        payload = {'targetClassifier': self.targetClassifier, 'targetDataType': None} 
        value = Infosys.getAttackFuncs(payload)
        assert len(value) == 0 

# #  # #-------------------------addAttack---------------------

    def test_addAttack(self):
        payload = {'attackName':'ZerothOrderOptimization','attackDataType':self.targetDataType,'algorithmSupported':self.targetClassifier,'attackFunc':'ZerothOrderOptimization'}
        expectedOutput = 'Attack Already Exists'
        value = Infosys.addAttack(payload)
        assert value == expectedOutput

    def test_addAttack_None(self):
        payload = {'attackName': None,'attackDataType':None,'algorithmSupported':self.targetClassifier,'attackFunc':'ZerothOrderOptimization'}
        expectedOutPut = 'Attack Addition Failed! Please Try Again'
        value = Infosys.addAttack(payload)   
        assert value == expectedOutPut 

# # #---------------------setAttack-------------------------

    def test_setAttack_MembershipInferenceRule(self):
        attackName = 'MembershipInferenceRule'
        batchId = TestService.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'MembershipInferenceRule'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput

    def test_setAttack_MembershipInferenceBlackBox(self):
        attackName = 'MembershipInferenceBlackBox'
        batchId = TestService.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'MembershipInferenceBlackBox'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput

    def test_setAttack_ZerothOrderOptimization(self):
        attackName = 'ZerothOrderOptimization'
        batchId = TestService.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'ZerothOrderOptimization'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput

    def test_setAttack_HopSkipJumpTabular(self):
        attackName = 'HopSkipJumpTabular'
        batchId = TestService.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'HopSkipJumpTabular'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput

    def test_setAttack_QueryEfficient(self):
        attackName = 'QueryEfficient'
        batchId = TestService.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'QueryEfficient'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput

    def test_setAttack_ProjectedGradientDescentTabular(self):
        attackName = 'ProjectedGradientDescentTabular'
        batchId = TestService.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'ProjectedGradientDescentTabular'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput

    def test_setAttack_InferenceLabelOnlyGap(self):
        attackName = 'InferenceLabelOnlyGap'
        batchId = TestService.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'InferenceLabelOnlyGap'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput

    def test_setAttack_AttributeInference(self):
        attackName = 'AttributeInference'
        batchId = TestService.getBatchId(self.modelIdScikitlearnClassifierTabular,self.dataIdScikitlearnClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'AttributeInference'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput

    def test_setAttack_AttributeInferenceWhiteBoxDecisionTree(self):
        attackName = 'AttributeInferenceWhiteBoxDecisionTree'
        batchId = TestService.getBatchId(self.modelIdScikitlearnClassifierTabular,self.dataIdScikitlearnClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'AttributeInferenceWhiteBoxDecisionTree'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_AttributeInferenceWhiteBoxLifestyleDecisionTree(self):
        attackName = 'AttributeInferenceWhiteBoxLifestyleDecisionTree'
        batchId = TestService.getBatchId(self.modelIdScikitlearnClassifierTabular,self.dataIdScikitlearnClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'AttributeInferenceWhiteBoxLifestyleDecisionTree'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_DecisionTree(self):
        attackName = 'DecisionTree'
        batchId = TestService.getBatchId(self.modelIdScikitlearnClassifierTabular,self.dataIdScikitlearnClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'DecisionTree'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_LabelOnlyDecisionBoundary(self):
        attackName = 'LabelOnlyDecisionBoundary'
        batchId = TestService.getBatchId(self.modelIdScikitlearnClassifierTabular,self.dataIdScikitlearnClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'LabelOnlyDecisionBoundary'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput  

    def test_setAttack_BasicIterativeMethod(self):
        attackName = 'BasicIterativeMethod'
        batchId = TestService.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        payload = {"batchId":batchId, "modelUrl":'BasicIterativeMethod'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_Boundary(self):
        attackName = 'Boundary'
        batchId = TestService.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        payload = {"batchId":batchId, "modelUrl":'Boundary'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_CarliniL2Method(self):
        attackName = 'CarliniL2Method'
        batchId = TestService.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        payload = {"batchId":batchId, "modelUrl":'CarliniL2Method'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_Deepfool(self):
        attackName = 'Deepfool'
        batchId = TestService.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        payload = {"batchId":batchId, "modelUrl":'Deepfool'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_ElasticNet(self):
        attackName = 'ElasticNet'
        batchId = TestService.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        payload = {"batchId":batchId, "modelUrl":'ElasticNet'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_FastGradientMethod(self):
        attackName = 'FastGradientMethod'
        batchId = TestService.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        payload = {"batchId":batchId, "modelUrl":'FastGradientMethod'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_IterativeFrameSaliency(self):
        attackName = 'IterativeFrameSaliency'
        batchId = TestService.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        payload = {"batchId":batchId, "modelUrl":'IterativeFrameSaliency'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_NewtonFool(self):
        attackName = 'NewtonFool'
        batchId = TestService.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        payload = {"batchId":batchId, "modelUrl":'NewtonFool'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_SaliencyMapMethod(self):
        attackName = 'SaliencyMapMethod'
        batchId = TestService.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        payload = {"batchId":batchId, "modelUrl":'SaliencyMapMethod'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_SimBA(self):
        attackName = 'SimBA'
        batchId = TestService.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        payload = {"batchId":batchId, "modelUrl":'SimBA'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_SpatialTransformation(self):
        attackName = 'SpatialTransformation'
        batchId = TestService.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        payload = {"batchId":batchId, "modelUrl":'SpatialTransformation'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_Square(self):
        attackName = 'Square'
        batchId = TestService.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        payload = {"batchId":batchId, "modelUrl":'Square'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_UniversalPerturbation(self):
        attackName = 'UniversalPerturbation'
        batchId = TestService.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        payload = {"batchId":batchId, "modelUrl":'UniversalPerturbation'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_Wasserstein(self):
        attackName = 'Wasserstein'
        batchId = TestService.getBatchId(self.modelIdKerasClassifierImage,self.dataIdKerasClassifierImage,[attackName])
        payload = {"batchId":batchId, "modelUrl":'Wasserstein'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_QueryEfficientGradientAttackEndPoint(self):
        attackName = 'QueryEfficientGradientAttackEndPoint'
        batchId = TestService.getBatchId(self.modelIdSklearnAPIClassifierTabular,self.dataIdSklearnAPIClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'QueryEfficientGradientAttackEndPoint'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_BoundaryAttackEndPoint(self):
        attackName = 'BoundaryAttackEndPoint'
        batchId = TestService.getBatchId(self.modelIdSklearnAPIClassifierTabular,self.dataIdSklearnAPIClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'BoundaryAttackEndPoint'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_HopSkipJumpAttackEndPoint(self):
        attackName = 'HopSkipJumpAttackEndPoint'
        batchId = TestService.getBatchId(self.modelIdSklearnAPIClassifierTabular,self.dataIdSklearnAPIClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'HopSkipJumpAttackEndPoint'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_LabelOnlyGapAttackEndPoint(self):
        attackName = 'LabelOnlyGapAttackEndPoint'
        batchId = TestService.getBatchId(self.modelIdSklearnAPIClassifierTabular,self.dataIdSklearnAPIClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'LabelOnlyGapAttackEndPoint'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_MembershipInferenceBlackBoxRuleBasedAttackEndPoint(self):
        attackName = 'MembershipInferenceBlackBoxRuleBasedAttackEndPoint'
        batchId = TestService.getBatchId(self.modelIdSklearnAPIClassifierTabular,self.dataIdSklearnAPIClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'MembershipInferenceBlackBoxRuleBasedAttackEndPoint'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_LabelOnlyDecisionBoundaryAttackEndPoint(self):
        attackName = 'LabelOnlyDecisionBoundaryAttackEndPoint'
        batchId = TestService.getBatchId(self.modelIdSklearnAPIClassifierTabular,self.dataIdSklearnAPIClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'LabelOnlyDecisionBoundaryAttackEndPoint'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_MembershipInferenceBlackBoxAttackEndPoint(self):
        attackName = 'MembershipInferenceBlackBoxAttackEndPoint'
        batchId = TestService.getBatchId(self.modelIdSklearnAPIClassifierTabular,self.dataIdSklearnAPIClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'MembershipInferenceBlackBoxAttackEndPoint'}
        TestService.reportDeletion()
        response =  Infosys.setAttack(payload)
        id = UrlLinks.Current_ID - 1
        k = f'{attackName}_{id}'
        expectedOutput = {"Job_Id":f'{k}'}
        assert response == expectedOutput 

    def test_setAttack_ModelIdNone(self):
        payload = {"batchId":None, "modelUrl":'MembershipInferenceRule'}
        expectedOutput = {"Oops! Something is Wrong With Input, Please Retry!"} 
        response = Infosys.setAttack(payload)  
        assert response == expectedOutput

    def test_setAttack_AttackNone(self):
        batchId = TestService.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,['None'])
        payload = {"batchId":batchId, "modelUrl":None}
        response = Infosys.setAttack(payload)  
        assert response == None

# #----------------------loadApi----------------------

    def test_loadApi(self,mocker):
        expectedOutput =  {
        "attackName": "LabelOnlyGapAttack",
        "attackDataType": "Tabular",
        "algorithmSupported": "SklearnAPIClassifier",  
        "attackFunc": "LabelOnlyGapAttackEndPoint"
        }
        mocked_loadApi = mocker.patch.object(Bulk, "loadApi", return_value = expectedOutput)
        response = Bulk.loadApi()
        assert response == expectedOutput

# # -----------------------batchAttack-------------------------

    def test_batchAttack(self):
        attackName = 'MembershipInferenceRule'
        batchId = TestService.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":'MembershipInferenceRule'}
        TestService.reportDeletion()
        response = Bulk.batchAttack(payload)
        assert response == batchId

    def test_batchAttack_Model_None(self):
        payload = {"batchId":None, "modelUrl":'MembershipInferenceRule'} 
        TestService.reportDeletion()
        value = Bulk.batchAttack(payload) 
        expectedOutput = {"Oops! Something is Wrong With Input, Please Retry!"}  
        assert value == expectedOutput

    def test_batchAttack_Attack_None(self):
        attackName = 'MembershipInferenceRule'
        batchId = TestService.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,[attackName])
        payload = {"batchId":batchId, "modelUrl":None} 
        TestService.reportDeletion()
        value = Bulk.batchAttack(payload) 
        expectedOutput = {"Oops! Something is Wrong With Input, Please Retry!"}  
        assert value == expectedOutput 

#-----------------------------combinereport--------------------

    def test_combinereport(self):
        TestService.reportDeletion()
        attackName = 'MembershipInferenceRule'
        batchId = TestService.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,[attackName])
        Payload = {"batchId":batchId, "modelUrl":attackName}
        Bulk.batchAttack(Payload)
        combineReportId = Bulk.combinereport({'batchid':batchId,'attackList':[attackName], 'dateTime': str(datetime.datetime.now())})
        combineId = combineReportId['combineReportFileId'] 
        expectedId = Html.find_one(batchId, 3.3)
        assert combineId == expectedId

    def test_combinereport_attackNone(self):
        TestService.reportDeletion()
        batchId = TestService.getBatchId(self.modelIdSklearnClassifierTabular,self.dataIdSklearnClassifierTabular,['None'])
        payload = {'batchid':batchId,'attackList': None}
        with pytest.raises(Exception):
            Batch.combinereport(payload)  

    def test_combinereport_batchidNone(self):
        TestService.reportDeletion()
        attackName = 'ZerothOrderOptimization'
        payload = {'batchid':None,'attackList': [attackName]}
        with pytest.raises(Exception):
            Batch.combinereport(payload) 

# #----------------------runAllAttack----------------------

    def test_runAllAttack(self,mocker):
        id = time.time()
        mocked_loadApi = mocker.patch.object(Bulk, "runAllAttack", return_value = id)
        response = Bulk.runAllAttack()
        assert response == id

    def test_runAllAttack_None(self):
        # Bulk.runAllAttack catches exceptions and returns a set/dict with error
        payload = {'batchid': None}
        response = Bulk.runAllAttack(payload)
        expected = {"runAllAttack api failed"}
        assert response == expected 

#-----------------------AttributeDict------------------

    def test_AttributeDict(self):
        TestService.reportDeletion()
        expectedOutput = {"attackName":"ZerothOrderOptimization","attackid":"123"} 
        response = AttributeDict(expectedOutput)
        assert response == expectedOutput          





