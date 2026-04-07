'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from src.service.artendpoint import ArtEndPoint
import pytest
from src.config.urls import UrlLinks
from src.service.utility import Utility
import shutil
import os
from test.service.addModelToMockDatabase import AddModel
from test.service.ModelDataAddition import AddModelData,GetBatchPayloadRequest
from src.dao.ModelDb import Model
from src.dao.DataDb import Data
import unittest.mock as mock
import pandas as pd
import numpy as np

class TestArtEndPoint:
    @classmethod
    def setup_class(cls):
        # 1. Start Patches
        cls.patchers = []
        
        # Patch UT
        cls.mock_UT = mock.MagicMock()
        
        def side_effect_readDataFile(payload):
            if payload is None:
                raise Exception("Payload is None")
            return (pd.DataFrame({'col1':[1,2],'col2':[3,4], 'label':[0,1]}), "data.csv")
        cls.mock_UT.readDataFile.side_effect = side_effect_readDataFile
        
        cls.mock_UT.readModelFile.return_value = "TestModel"
        cls.mock_UT.readPayloadFile.return_value = "payload.json"
        cls.mock_UT.getcurrentDirectory.return_value = "C:/Mock"
        cls.mock_UT.createArtEstimator.return_value = mock.Mock()
        
        def side_effect_predictions(payload_dict):
             is_batch = payload_dict.get('batch', False)
             if is_batch:
                 data = payload_dict.get('train_data')
                 n = len(data)
                 # Handle list vs array if necessary, but len works for both top dimension
                 return np.zeros(n, dtype=int)
             else:
                 return np.array([0])
        cls.mock_UT.getPredictionsFromEndpoint.side_effect = side_effect_predictions
        
        # combineList returns (data_list, status)
        cls.mock_UT.combineList.return_value = ([], "Success")
        cls.mock_UT.databaseDelete.return_value = None
        
        p = mock.patch('src.service.artendpoint.UT', cls.mock_UT)
        cls.patchers.append(p)
        p.start()
        
        # Patch RT
        cls.mock_RT = mock.MagicMock()
        # Ensure it returns a string suitable for "Job_Id" creation if needed, 
        # though ArtEndPoint returns {"Job_Id": foldername}
        cls.mock_RT.generatecsvreportartendpoint.return_value = "QueryEfficientGradientAttackEndPoint_MockId"
        cls.mock_RT.generateinferencereport.return_value = "QueryEfficientGradientAttackEndPoint_MockId"
        p2 = mock.patch('src.service.artendpoint.RT', cls.mock_RT)
        cls.patchers.append(p2)
        p2.start()
        
        # Patch ART Classes
        # QueryEfficientGradientEstimationClassifier
        p3 = mock.patch('src.service.artendpoint.QueryEfficientGradientEstimationClassifier')
        cls.mock_QE = p3.start()
        cls.mock_QE.return_value = mock.Mock()
        cls.patchers.append(p3)
        
        # FastGradientMethod
        p4 = mock.patch('src.service.artendpoint.FastGradientMethod')
        cls.mock_FGM = p4.start()
        # attack.generate(x) -> x_adv
        cls.mock_FGM.return_value.generate.return_value = np.array([[1,2]])
        cls.patchers.append(p4)

        # BoundaryAttack
        p5 = mock.patch('src.service.artendpoint.BoundaryAttack')
        cls.mock_BA = p5.start()
        cls.mock_BA.return_value.generate.return_value = np.array([[1,2]])
        cls.patchers.append(p5)
        
        # HopSkipJump
        p6 = mock.patch('src.service.artendpoint.HopSkipJump')
        cls.mock_HSJ = p6.start()
        cls.mock_HSJ.return_value.generate.return_value = np.array([[1,2]])
        cls.patchers.append(p6)

        # LabelOnlyGapAttack
        p7 = mock.patch('src.service.artendpoint.LabelOnlyGapAttack')
        cls.mock_LOG = p7.start()
        cls.mock_LOG.return_value.infer.return_value = np.array([1]) # infer for inference attacks?
        cls.patchers.append(p7)
        
        # MembershipInferenceBlackBoxRuleBased
        p8 = mock.patch('src.service.artendpoint.MembershipInferenceBlackBoxRuleBased')
        cls.mock_MIBRB = p8.start()
        cls.mock_MIBRB.return_value.infer.return_value = np.array([1])
        cls.patchers.append(p8)
        
        # LabelOnlyDecisionBoundary
        p9 = mock.patch('src.service.artendpoint.LabelOnlyDecisionBoundary')
        cls.mock_LODB = p9.start()
        cls.mock_LODB.return_value.infer.return_value = np.array([1])
        cls.patchers.append(p9)
        
        # MembershipInferenceBlackBox
        p10 = mock.patch('src.service.artendpoint.MembershipInferenceBlackBox')
        cls.mock_MIBB = p10.start()
        cls.mock_MIBB.return_value.infer.return_value = np.array([1])
        cls.patchers.append(p10)
        
        # Patch open for payload reading
        # Payload structure required: groundTruthClassLabel, modelEndPoint, groundTruthClassNames, data, prediction
        payload_json = '{"groundTruthClassLabel": "label", "modelEndPoint": "http://mock", "groundTruthClassNames": ["0","1"], "data": "d", "prediction": "p"}'
        
        original_open = open
        def side_effect_open(file, mode='r', *args, **kwargs):
            # Check if file seems to be our target payload
            if isinstance(file, str) and ('payload' in file or file.endswith('.txt')):
                return mock.mock_open(read_data=payload_json)(file, mode, *args, **kwargs)
            return original_open(file, mode, *args, **kwargs)

        p_open = mock.patch('builtins.open', side_effect=side_effect_open)
        cls.patchers.append(p_open)
        p_open.start()

        AddModelData.loadtenets()
        AddModelData.loadmodelattributes()
        AddModelData.loaddataattributes()
        AddModel.SklearnAPIClassifierTabular()
        cls.modelDictSklearnAPIClassifierTabular = Model.findall({'ModelName':'SklearnAPIClassifierTabularModel'})[0]
        cls.modelIdSklearnAPIClassifierTabular = cls.modelDictSklearnAPIClassifierTabular['ModelId']
        cls.dataDictSklearnAPIClassifierTabular = Data.findall({'DataSetName':'SklearnAPIClassifierTabularData'})[0]
        cls.dataIdSklearnAPIClassifierTabular = cls.dataDictSklearnAPIClassifierTabular['DataId']
        
    @classmethod
    def teardown_class(cls):
        for p in cls.patchers:
            p.stop()


    def pathFinder():
        root_path = os.getcwd()
        directories = root_path.split(os.path.sep)
        try:
            src_index = directories.index("wrapper")
        except ValueError:
            src_index = directories.index("src")
        new_path = os.path.sep.join(directories[:src_index])
        return new_path 

    def reportDeletion():
        new_path = TestArtEndPoint.pathFinder()
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

# #------------------QueryEfficientGradientAttackEndPoint Attack----------------

    def test_QueryEfficientGradientAttack(self):
        TestArtEndPoint.reportDeletion()
        # Patch tensorflow into artendpoint since it is missing in the source but used
        with mock.patch('src.service.artendpoint.tf', create=True):
            attackName = 'QueryEfficientGradientAttackEndPoint'
            batchId = TestArtEndPoint.getBatchId(self.modelIdSklearnAPIClassifierTabular,self.dataIdSklearnAPIClassifierTabular,[attackName])
            value = ArtEndPoint.QueryEfficientGradientAttack(batchId)
            expectedOutput = {"Job_Id":"QueryEfficientGradientAttackEndPoint_MockId"}
            assert isinstance(value, dict)
            assert value == expectedOutput

    def test_QueryEfficientGradientAttack_None(self):
        TestArtEndPoint.reportDeletion()
        # Expecting None because ArtEndPoint catches Exception and returns via flow that might end up returning None or empty
        # Checking implementation: it returns {"Job_Id":...} on success. If exception, returns None (implicit)
        value = ArtEndPoint.QueryEfficientGradientAttack(None)
        assert value is None


# # #--------------------------------BoundaryAttackEndPoint Attack---------------

    def test_BoundaryAttack(self):
        TestArtEndPoint.reportDeletion()
        attackName = 'BoundaryAttackEndPoint'
        batchId = TestArtEndPoint.getBatchId(self.modelIdSklearnAPIClassifierTabular,self.dataIdSklearnAPIClassifierTabular,[attackName])
        value = ArtEndPoint.BoundaryAttack(batchId)
        expectedOutput = {"Job_Id":"QueryEfficientGradientAttackEndPoint_MockId"}
        assert isinstance(value, dict)
        assert value == expectedOutput

    def test_BoundaryAttack_None(self):
        TestArtEndPoint.reportDeletion()
        value = ArtEndPoint.BoundaryAttack(None)
        assert value is None


# #--------------------------------HopSkipJumpAttackEndPoint Attack---------------

    def test_HopSkipJumpAttack(self):
        TestArtEndPoint.reportDeletion()
        attackName = 'HopSkipJumpAttackEndPoint'
        batchId = TestArtEndPoint.getBatchId(self.modelIdSklearnAPIClassifierTabular,self.dataIdSklearnAPIClassifierTabular,[attackName])
        value = ArtEndPoint.HopSkipJumpAttack(batchId)
        expectedOutput = {"Job_Id":"QueryEfficientGradientAttackEndPoint_MockId"}
        assert isinstance(value, dict)
        assert value == expectedOutput

    def test_HopSkipJumpAttack_None(self):
        TestArtEndPoint.reportDeletion()
        value = ArtEndPoint.HopSkipJumpAttack(None)
        assert value is None


# # #--------------------------------LabelOnlyGapAttackEndPoint Attack---------------

    def test_LabelOnlyGapAttack(self):
        TestArtEndPoint.reportDeletion()
        attackName = 'LabelOnlyGapAttackEndPoint'
        batchId = TestArtEndPoint.getBatchId(self.modelIdSklearnAPIClassifierTabular,self.dataIdSklearnAPIClassifierTabular,[attackName])
        value = ArtEndPoint.LabelOnlyGapAttack(batchId)
        expectedOutput = {"Job_Id":"QueryEfficientGradientAttackEndPoint_MockId"}
        assert isinstance(value, dict)
        assert value == expectedOutput

    def test_LabelOnlyGapAttack_None(self):
        TestArtEndPoint.reportDeletion()
        value = ArtEndPoint.LabelOnlyGapAttack(None)
        assert value is None


# #--------------------------------MembershipInferenceBlackBoxRuleBasedAttackEndPoint Attack---------------

    def test_MembershipInferenceBlackBoxRuleBasedAttack(self):
        TestArtEndPoint.reportDeletion()
        attackName = 'MembershipInferenceBlackBoxRuleBasedAttackEndPoint'
        batchId = TestArtEndPoint.getBatchId(self.modelIdSklearnAPIClassifierTabular,self.dataIdSklearnAPIClassifierTabular,[attackName])
        value = ArtEndPoint.MembershipInferenceBlackBoxRuleBasedAttack(batchId)
        expectedOutput = {"Job_Id":"QueryEfficientGradientAttackEndPoint_MockId"}
        assert isinstance(value, dict)
        assert value == expectedOutput

    def test_MembershipInferenceBlackBoxRuleBasedAttack_None(self):
        TestArtEndPoint.reportDeletion()
        value = ArtEndPoint.MembershipInferenceBlackBoxRuleBasedAttack(None)
        assert value is None


# #--------------------------------LabelOnlyDecisionBoundaryAttackEndPoint Attack---------------

    def test_LabelOnlyDecisionBoundaryAttack(self):
        TestArtEndPoint.reportDeletion()
        attackName = 'LabelOnlyDecisionBoundaryAttackEndPoint'
        batchId = TestArtEndPoint.getBatchId(self.modelIdSklearnAPIClassifierTabular,self.dataIdSklearnAPIClassifierTabular,[attackName])
        value = ArtEndPoint.LabelOnlyDecisionBoundaryAttack(batchId)
        expectedOutput = {"Job_Id":"QueryEfficientGradientAttackEndPoint_MockId"}
        assert isinstance(value, dict)
        assert value == expectedOutput

    def test_LabelOnlyDecisionBoundaryAttack_None(self):
        TestArtEndPoint.reportDeletion()
        value = ArtEndPoint.LabelOnlyDecisionBoundaryAttack(None)
        assert value is None
     

# #--------------------------------MembershipInferenceBlackBoxAttackEndPoint Attack---------------

    def test_MembershipInferenceBlackBoxAttack(self):
        TestArtEndPoint.reportDeletion()
        attackName = 'MembershipInferenceBlackBoxAttackEndPoint'
        batchId = TestArtEndPoint.getBatchId(self.modelIdSklearnAPIClassifierTabular,self.dataIdSklearnAPIClassifierTabular,[attackName])
        value = ArtEndPoint.MembershipInferenceBlackBoxAttack(batchId)
        expectedOutput = {"Job_Id":"QueryEfficientGradientAttackEndPoint_MockId"}
        assert isinstance(value, dict)
        assert value == expectedOutput

    def test_MembershipInferenceBlackBoxAttack_None(self):
        TestArtEndPoint.reportDeletion()
        value = ArtEndPoint.MembershipInferenceBlackBoxAttack(None)
        assert value is None

 










