import pytest
import json
from fairness.dao.bias_model import TrainingDataset, PredictionDataset, Bias

class TestTrainingDataset:
    def test_all_fields(self):
        d = TrainingDataset(id=1, name='train', fileType='csv', label='y', extension='csv',
                           path={'storage': 'local', 'uri': '/data'})
        assert d.id == 1 and d.name == 'train'
    def test_empty(self):
        d = TrainingDataset()
        assert d.id is None
    def test_to_dict(self):
        d = TrainingDataset(id=1, name='test')
        assert d.model_dump()['id'] == 1

class TestPredictionDataset:
    def test_predlabel(self):
        d = PredictionDataset(id=2, predlabel='pred', label='actual')
        assert d.predlabel == 'pred'
    def test_empty(self):
        d = PredictionDataset()
        assert d.predlabel is None

class TestBias:
    def test_empty(self):
        b = Bias()
        assert b.method is None
        assert b.favourableOutcome == []
        assert b.labelmaps == {}
    def test_defaults(self):
        b = Bias()
        assert b.outputPath['storage'] == 'INFY_AICLD_NUTANIX'
    def test_with_datasets(self):
        tr = TrainingDataset(id=1, name='train.csv')
        pr = PredictionDataset(id=2, predlabel='pred')
        b = Bias(trainingDataset=tr, predictionDataset=pr)
        assert b.trainingDataset.id == 1
        assert b.predictionDataset.predlabel == 'pred'
    def test_complex_fields(self):
        b = Bias(favourableOutcome=[1,0], labelmaps={'0':'no','1':'yes'},
                facet=['age','gender'], ca_dict={'gender':['M','F']})
        assert len(b.facet) == 2
        assert b.labelmaps['0'] == 'no'
    def test_serialization(self):
        b = Bias(method='test', favourableOutcome=[1])
        d = b.model_dump()
        assert d['method'] == 'test'
        j = b.model_dump_json()
        assert 'test' in j
    def test_nested_serialization(self):
        tr = TrainingDataset(id=1, name='train')
        b = Bias(method='test', trainingDataset=tr)
        d = b.model_dump()
        assert d['trainingDataset']['name'] == 'train'

class TestEdgeCases:
    def test_empty_strings(self):
        d = TrainingDataset(name='', label='')
        assert d.name == ''
    def test_special_chars(self):
        d = TrainingDataset(name='file@#$.csv')
        assert '@#' in d.name
    def test_large_list(self):
        b = Bias(facet=[f'f{i}' for i in range(100)])
        assert len(b.facet) == 100
    def test_nested_dict(self):
        d = TrainingDataset(path={'storage':'s3','config':{'region':'us-east-1'}})
        assert d.path['config']['region'] == 'us-east-1'

class TestPerformance:
    def test_creation(self):
        import time
        s = time.perf_counter()
        m = [TrainingDataset(id=i) for i in range(1000)]
        assert time.perf_counter() - s < 0.5 and len(m) == 1000
    def test_serialization(self):
        import time
        b = Bias(facet=[f'f{i}' for i in range(50)])
        s = time.perf_counter()
        for _ in range(100): b.model_dump_json()
        assert time.perf_counter() - s < 0.5

class TestCodeQuality:
    def test_inheritance(self):
        from pydantic import BaseModel
        assert issubclass(TrainingDataset, BaseModel)
        assert issubclass(Bias, BaseModel)
    def test_fields(self):
        assert hasattr(TrainingDataset(), 'id')
        assert hasattr(PredictionDataset(), 'predlabel')
        assert hasattr(Bias(), 'method')
    def test_schema(self):
        s = Bias.model_json_schema()
        assert 'properties' in s

class TestRegression:
    def test_all_bias_fields(self):
        b = Bias()
        fields = ['method','biasType','taskType','trainingDataset','predictionDataset',
                 'features','categoricalAttributes','ca_dict','favourableOutcome',
                 'labelmaps','facet','outputPath']
        for f in fields: assert hasattr(b, f)
