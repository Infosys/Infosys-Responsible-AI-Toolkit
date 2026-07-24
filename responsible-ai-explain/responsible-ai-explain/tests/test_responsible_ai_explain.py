'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""
test_responsible_ai_explain.py - Tests for ResponsibleAIExplain class
"""

import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch
import pandas as pd
import numpy as np
from explain.service.responsible_ai_explain import ResponsibleAIExplain
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



# ============================================================================
#  ResponsibleAIExplain Tests for Coverage 
# ============================================================================

class TestResponsibleAIExplainGetExplanationDispatcher:
    """Tests for get_explanation dispatcher method"""

    @patch('explain.service.responsible_ai_explain.ResponsibleAIExplain.lime_tabular_local_explanation')
    def test_get_explanation_lime_local(self, mock_lime):
        """Test get_explanation dispatches to lime_tabular_local_explanation"""
        
        
        mock_lime.return_value = [{'explanation': 'test'}]
        
        result = ResponsibleAIExplain.get_explanation(
            model=MagicMock(),
            taskType='CLASSIFICATION',
            modelType='Scikit-learn',
            dataset=pd.DataFrame({'a': [1, 2], 'b': [3, 4]}),
            method='LIME-TABULAR',
            scope='LOCAL'
        )
        
        mock_lime.assert_called_once()
        assert result == [{'explanation': 'test'}]

    @patch('explain.service.responsible_ai_explain.ResponsibleAIExplain.kernel_explainer_global_explanation')
    def test_get_explanation_kernel_global(self, mock_kernel):
        """Test get_explanation dispatches to kernel_explainer_global_explanation"""
        
        
        mock_kernel.return_value = [{'importantFeatures': []}]
        
        result = ResponsibleAIExplain.get_explanation(
            model=MagicMock(),
            taskType='CLASSIFICATION',
            modelType='Scikit-learn',
            dataset=pd.DataFrame({'a': [1, 2], 'b': [3, 4]}),
            method='KERNEL-EXPLAINER',
            scope='GLOBAL'
        )
        
        mock_kernel.assert_called_once()

    @patch('explain.service.responsible_ai_explain.ResponsibleAIExplain.timeSeries_local_explanation_lime')
    def test_get_explanation_ts_lime(self, mock_ts_lime):
        """Test get_explanation dispatches to timeSeries_local_explanation_lime"""
        
        
        mock_ts_lime.return_value = [{'timeSeries': []}]
        
        result = ResponsibleAIExplain.get_explanation(
            model=MagicMock(),
            taskType='TIMESERIESFORECAST',
            modelType='Statsmodels',
            dataset=pd.DataFrame({'a': [1, 2], 'b': [3, 4]}),
            method='TS-LIME-TABULAR',
            scope='LOCAL'
        )
        
        mock_ts_lime.assert_called_once()

    @patch('explain.service.responsible_ai_explain.ResponsibleAIExplain.timeSeries_global_explanation')
    def test_get_explanation_ts_kernel(self, mock_ts_kernel):
        """Test get_explanation dispatches to timeSeries_global_explanation"""
        
        
        mock_ts_kernel.return_value = [{'timeSeries': []}]
        
        result = ResponsibleAIExplain.get_explanation(
            model=MagicMock(),
            taskType='TIMESERIESFORECAST',
            modelType='Statsmodels',
            dataset=pd.DataFrame({'a': [1, 2], 'b': [3, 4]}),
            method='TS-KERNEL-EXPLAINER',
            scope='GLOBAL'
        )
        
        mock_ts_kernel.assert_called_once()

    @patch('explain.service.responsible_ai_explain.ResponsibleAIExplain.text_shap_local_explanation')
    def test_get_explanation_text_shap(self, mock_text_shap):
        """Test get_explanation dispatches to text_shap_local_explanation"""
        
        
        mock_text_shap.return_value = [{'shapImportanceText': []}]
        
        result = ResponsibleAIExplain.get_explanation(
            model=MagicMock(),
            taskType='CLASSIFICATION',
            modelType='Scikit-learn',
            dataset=pd.DataFrame({'a': [1, 2], 'b': [3, 4]}),
            method='TEXT-SHAP-EXPLAINER',
            scope='LOCAL'
        )
        
        mock_text_shap.assert_called_once()

    def test_get_explanation_invalid_scope(self):
        """Test get_explanation with invalid scope raises KeyError"""
        
        
        with pytest.raises(KeyError):
            ResponsibleAIExplain.get_explanation(
                model=MagicMock(),
                method='LIME-TABULAR',
                scope='INVALID'
            )

    def test_get_explanation_invalid_method(self):
        """Test get_explanation with invalid method raises KeyError"""
        
        
        with pytest.raises(KeyError):
            ResponsibleAIExplain.get_explanation(
                model=MagicMock(),
                method='INVALID-METHOD',
                scope='LOCAL'
            )


class TestResponsibleAIExplainCoreMethodsCoverage:
    """Tests for core methods in ResponsibleAIExplain to increase coverage"""

    def test_split_set_basic(self):
        """Test split_set with basic data"""
        
        
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12], [13, 14], [15, 16], [17, 18], [19, 20]])
        y = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
        
        X_split, y_split = ResponsibleAIExplain.split_set(X, y, fraction=0.3)
        
        assert len(X_split) == 3  # 30% of 10
        assert len(y_split) == 3

    def test_prepare_data_with_target(self):
        """Test prepare_data with target column"""
        
        
        dataset = pd.DataFrame({
            'feature1': [1, 2, 3, 4],
            'feature2': [5, 6, 7, 8],
            'target': [0, 1, 0, 1]
        })
        
        data, target, featureNames, targetClassNames = ResponsibleAIExplain.prepare_data(
            dataset, 'target', ['class0', 'class1']
        )
        
        assert data.shape == (4, 2)
        assert len(target) == 4
        assert featureNames == ['feature1', 'feature2']
        assert targetClassNames == ['class0', 'class1']

    def test_prepare_data_without_target_column(self):
        """Test prepare_data when target column not in dataset"""
        
        
        dataset = pd.DataFrame({
            'feature1': [1, 2, 3],
            'feature2': [4, 5, 6]
        })
        
        data, target, featureNames, targetClassNames = ResponsibleAIExplain.prepare_data(
            dataset, 'nonexistent', None
        )
        
        assert data.shape == (3, 2)
        assert target is None

    def test_prepare_data_infer_class_names(self):
        """Test prepare_data infers class names from target"""
        
        
        dataset = pd.DataFrame({
            'feature1': [1, 2, 3, 4],
            'target': ['A', 'B', 'A', 'B']
        })
        
        data, target, featureNames, targetClassNames = ResponsibleAIExplain.prepare_data(
            dataset, 'target', None
        )
        
        assert set(targetClassNames) == {'A', 'B'}

    def test_find_date_column_with_datetime(self):
        """Test find_date_column with datetime data"""
        
        
        dataset = pd.DataFrame({
            'date_col': pd.date_range('2020-01-01', periods=5),
            'value': [1, 2, 3, 4, 5]
        })
        
        result = ResponsibleAIExplain.find_date_column(dataset)
        assert result == 'date_col'

    def test_find_date_column_no_datetime(self):
        """Test find_date_column raises ValueError when no date column found"""
        
        
        # Use string data that cannot be converted to datetime
        # and make sure more than 50% values fail conversion
        dataset = pd.DataFrame({
            'a': ['not a date x', 'also not y', 'neither z'],
            'b': ['abc', 'def', 'ghi']
        })
        
        with pytest.raises(ValueError):
            ResponsibleAIExplain.find_date_column(dataset)

    @patch('explain.service.responsible_ai_explain.shap.KernelExplainer')
    def test_kernel_explainer_global_classification(self, mock_explainer_class):
        """Test kernel_explainer_global_explanation for classification"""
        
        
        # Setup mock
        mock_explainer = MagicMock()
        mock_explainer_class.return_value = mock_explainer
        mock_explainer.shap_values.return_value = np.random.rand(10, 5)
        
        mock_model = MagicMock()
        mock_model.predict_proba = MagicMock(return_value=np.array([[0.5, 0.5]]))
        
        params = {
            'model': mock_model,
            'taskType': 'CLASSIFICATION',
            'modelType': 'Scikit-learn',
            'dataset': pd.DataFrame({f'feature{i}': range(10) for i in range(5)} | {'target': [0]*5 + [1]*5}),
            'targetClassLabel': 'target',
            'targetClassNames': ['class0', 'class1'],
            'api_input_request': None,
            'api_output_response': None
        }
        
        result = ResponsibleAIExplain.kernel_explainer_global_explanation(params)
        
        assert 'importantFeatures' in result[0]
        assert 'featureNames' in result[0]
        assert 'description' in result[0]

    @patch('explain.service.responsible_ai_explain.shap.KernelExplainer')
    def test_kernel_explainer_global_regression(self, mock_explainer_class):
        """Test kernel_explainer_global_explanation for regression"""
        
        
        mock_explainer = MagicMock()
        mock_explainer_class.return_value = mock_explainer
        mock_explainer.shap_values.return_value = np.random.rand(10, 5)
        
        mock_model = MagicMock()
        mock_model.predict = MagicMock(return_value=np.array([1.0, 2.0]))
        
        params = {
            'model': mock_model,
            'taskType': 'REGRESSION',
            'modelType': 'Scikit-learn',
            'dataset': pd.DataFrame({f'feature{i}': range(10) for i in range(5)} | {'target': range(10)}),
            'targetClassLabel': 'target',
            'targetClassNames': None,
            'api_input_request': None,
            'api_output_response': None
        }
        
        result = ResponsibleAIExplain.kernel_explainer_global_explanation(params)
        
        assert 'importantFeatures' in result[0]

    def test_kernel_explainer_global_small_dataset(self):
        """Test kernel_explainer_global_explanation with too small dataset"""
        
        
        mock_model = MagicMock()
        
        params = {
            'model': mock_model,
            'taskType': 'CLASSIFICATION',
            'modelType': 'Scikit-learn',
            'dataset': pd.DataFrame({'a': [1], 'target': [0]}),  # Only 1 sample
            'targetClassLabel': 'target',
            'targetClassNames': ['class0'],
            'api_input_request': None,
            'api_output_response': None
        }
        
        with pytest.raises(ValueError, match="too small"):
            ResponsibleAIExplain.kernel_explainer_global_explanation(params)

    @patch('explain.service.responsible_ai_explain.LimeTabularExplainer')
    def test_lime_tabular_local_explanation_regression(self, mock_lime_class):
        """Test lime_tabular_local_explanation for regression"""
        
        
        mock_explainer = MagicMock()
        mock_lime_class.return_value = mock_explainer
        
        mock_explanation = MagicMock()
        mock_explanation.as_list.return_value = [('feature1', 0.5), ('feature2', -0.3)]
        mock_explanation.predicted_value = 1.5
        mock_explainer.explain_instance.return_value = mock_explanation
        
        mock_model = MagicMock()
        mock_model.predict = MagicMock(return_value=np.array([1.5]))
        
        dataset = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'feature2': [5, 4, 3, 2, 1],
            'target': [1.0, 2.0, 3.0, 4.0, 5.0]
        })
        
        params = {
            'model': mock_model,
            'taskType': 'REGRESSION',
            'modelType': 'Scikit-learn',
            'dataset': dataset,
            'targetClassLabel': 'target',
            'targetClassNames': None,
            'lineDataset': None,
            'inputIndex': 0
        }
        
        result = ResponsibleAIExplain.lime_tabular_local_explanation(params)
        
        assert 'importantFeatures' in result[0]
        assert 'featureNames' in result[0]

    def test_lime_tabular_local_explanation_invalid_index(self):
        """Test lime_tabular_local_explanation with invalid input index"""
        
        
        mock_model = MagicMock()
        
        dataset = pd.DataFrame({
            'feature1': [1, 2, 3],
            'target': [0, 1, 0]
        })
        
        params = {
            'model': mock_model,
            'taskType': 'CLASSIFICATION',
            'modelType': 'Scikit-learn',
            'dataset': dataset,
            'targetClassLabel': 'target',
            'targetClassNames': ['class0', 'class1'],
            'lineDataset': None,
            'inputIndex': -1  # Invalid index
        }
        
        with pytest.raises(ValueError):
            ResponsibleAIExplain.lime_tabular_local_explanation(params)


# ============================================================================
# Additional Comprehensive Tests for ResponsibleAIExplain Coverage
# ============================================================================

class TestResponsibleAIExplainMethods:
    """Additional tests for ResponsibleAIExplain methods"""

    def test_split_set_actual(self):
        """Test split_set actual method"""
        
        
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]])
        y = np.array([0, 1, 0, 1, 0])
        
        X_split, y_split = ResponsibleAIExplain.split_set(X, y, 0.4)
        
        assert X_split.shape[0] == 2  # 40% of 5 samples
        assert len(y_split) == 2

    def test_prepare_data_actual(self):
        """Test prepare_data actual method"""
        
        
        dataset = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'feature2': [5, 4, 3, 2, 1],
            'target': [0, 1, 0, 1, 0]
        })
        
        data, target, featureNames, targetClassNames = ResponsibleAIExplain.prepare_data(
            dataset, 'target', ['class0', 'class1']
        )
        
        assert data.shape == (5, 2)
        assert len(target) == 5
        assert 'feature1' in featureNames
        assert 'feature2' in featureNames
        assert 'class0' in targetClassNames

    def test_prepare_data_without_target_column(self):
        """Test prepare_data when target column not in dataset"""
        
        
        dataset = pd.DataFrame({
            'feature1': [1, 2, 3],
            'feature2': [4, 5, 6]
        })
        
        data, target, featureNames, targetClassNames = ResponsibleAIExplain.prepare_data(
            dataset, 'nonexistent_column', None
        )
        
        assert data.shape == (3, 2)
        assert target is None
        assert len(featureNames) == 2

    def test_prepare_data_infer_target_class_names(self):
        """Test prepare_data inferring target class names"""
        
        
        dataset = pd.DataFrame({
            'feature1': [1, 2, 3, 4],
            'target': ['A', 'B', 'A', 'C']
        })
        
        data, target, featureNames, targetClassNames = ResponsibleAIExplain.prepare_data(
            dataset, 'target', None  # Don't provide target class names
        )
        
        assert len(targetClassNames) == 3  # A, B, C

    def test_find_date_column_success(self):
        """Test find_date_column with valid date column"""
        
        
        dataset = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'value': [1, 2, 3]
        })
        
        date_col = ResponsibleAIExplain.find_date_column(dataset)
        
        assert date_col == 'date'

    def test_find_date_column_no_date(self):
        """Test find_date_column with no date column - uses invalid date strings"""
        
        
        # Create data where values cannot be converted to datetime
        # The function raises ValueError when no valid date column is found
        dataset = pd.DataFrame({
            'feature1': ['not_a_date', 'invalid_date', 'random_text'],
            'feature2': ['abc123', 'xyz789', 'foo_bar']
        })
        
        with pytest.raises(ValueError):
            ResponsibleAIExplain.find_date_column(dataset)

    @patch('shap.KernelExplainer')
    def test_kernel_explainer_global_regression(self, mock_kernel_class):
        """Test kernel_explainer_global_explanation for regression"""
        
        
        mock_explainer = MagicMock()
        mock_kernel_class.return_value = mock_explainer
        
        # Mock SHAP values
        mock_shap_values = np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]])
        mock_explainer.shap_values.return_value = mock_shap_values
        
        mock_model = MagicMock()
        mock_model.predict = MagicMock(return_value=np.array([1.0, 2.0, 3.0]))
        
        dataset = pd.DataFrame({
            'feature1': [1, 2, 3],
            'feature2': [4, 5, 6],
            'target': [1.0, 2.0, 3.0]
        })
        
        params = {
            'model': mock_model,
            'taskType': 'REGRESSION',
            'modelType': 'Scikit-learn',
            'dataset': dataset,
            'targetClassLabel': 'target',
            'targetClassNames': None,
            'api_input_request': None,
            'api_output_response': None
        }
        
        result = ResponsibleAIExplain.kernel_explainer_global_explanation(params)
        
        assert 'importantFeatures' in result[0]
        assert 'featureNames' in result[0]

    @patch('shap.KernelExplainer')
    def test_kernel_explainer_global_large_dataset(self, mock_kernel_class):
        """Test kernel_explainer_global_explanation with large dataset (>100 samples)"""
        
        
        mock_explainer = MagicMock()
        mock_kernel_class.return_value = mock_explainer
        
        mock_shap_values = np.random.rand(100, 3)
        mock_explainer.shap_values.return_value = mock_shap_values
        
        mock_model = MagicMock()
        mock_model.predict_proba = MagicMock(return_value=np.random.rand(100, 2))
        
        # Create large dataset
        dataset = pd.DataFrame({
            'feature1': np.random.rand(150),
            'feature2': np.random.rand(150),
            'feature3': np.random.rand(150),
            'target': np.random.randint(0, 2, 150)
        })
        
        params = {
            'model': mock_model,
            'taskType': 'CLASSIFICATION',
            'modelType': 'Scikit-learn',
            'dataset': dataset,
            'targetClassLabel': 'target',
            'targetClassNames': ['class0', 'class1'],
            'api_input_request': None,
            'api_output_response': None
        }
        
        result = ResponsibleAIExplain.kernel_explainer_global_explanation(params)
        
        assert 'importantFeatures' in result[0]

    @patch('shap.KernelExplainer')
    def test_timeSeries_global_explanation(self, mock_kernel_class):
        """Test timeSeries_global_explanation method"""
        
        
        mock_explainer = MagicMock()
        mock_kernel_class.return_value = mock_explainer
        
        mock_shap_values = np.random.rand(50, 3)
        mock_explainer.shap_values.return_value = mock_shap_values
        
        mock_model = MagicMock()
        mock_model.predict = MagicMock(return_value=np.random.rand(50))
        
        dataset = pd.DataFrame({
            'feature1': np.random.rand(100),
            'feature2': np.random.rand(100),
            'feature3': np.random.rand(100),
            'target': np.random.rand(100)
        })
        
        params = {
            'model': mock_model,
            'taskType': 'REGRESSION',
            'modelType': 'Scikit-learn',
            'dataset': dataset,
            'targetClassLabel': 'target',
            'targetClassNames': None
        }
        
        result = ResponsibleAIExplain.timeSeries_global_explanation(params)
        
        assert 'timeSeries' in result[0]
        assert 'featureNames' in result[0]

    @patch('explain.service.responsible_ai_explain.LimeTabularExplainer')
    def test_lime_tabular_with_pipeline(self, mock_lime_class):
        """Test lime_tabular_local_explanation with pipeline model"""
        
        
        mock_explainer = MagicMock()
        mock_lime_class.return_value = mock_explainer
        
        mock_explanation = MagicMock()
        mock_explanation.as_list.return_value = [('f1', 0.3), ('f2', 0.2)]
        mock_explanation.predicted_value = 0.5
        mock_explainer.explain_instance.return_value = mock_explanation
        
        # Create mock pipeline
        mock_pipeline = MagicMock()
        mock_pipeline.steps = [('preprocessor', MagicMock()), ('model', MagicMock())]
        type(mock_pipeline).__name__ = 'Pipeline'
        
        # Mock the pipeline processing
        with patch.object(ResponsibleAIExplain, 'pipeline_processing') as mock_pp:
            mock_model = MagicMock()
            mock_model.predict = MagicMock(return_value=np.array([0.5]))
            
            dataset = pd.DataFrame({
                'feature1': [1, 2, 3, 4, 5],
                'feature2': [5, 4, 3, 2, 1],
                'target': [1.0, 2.0, 3.0, 4.0, 5.0]
            })
            
            mock_pp.return_value = (mock_model, dataset, 'target', None)
            
            params = {
                'model': mock_pipeline,
                'taskType': 'REGRESSION',
                'modelType': 'Scikit-learn',
                'dataset': dataset,
                'targetClassLabel': 'target',
                'targetClassNames': None,
                'lineDataset': None,
                'inputIndex': 0
            }
            
            result = ResponsibleAIExplain.lime_tabular_local_explanation(params)
            
            assert 'importantFeatures' in result[0]

    @patch('explain.service.responsible_ai_explain.LimeTabularExplainer')
    def test_lime_tabular_classification_keras(self, mock_lime_class):
        """Test lime_tabular_local_explanation for Keras classification"""
        
        
        mock_explainer = MagicMock()
        mock_lime_class.return_value = mock_explainer
        
        mock_explanation = MagicMock()
        mock_explanation.as_list.return_value = [('f1', 0.4), ('f2', -0.3)]
        mock_explainer.explain_instance.return_value = mock_explanation
        
        mock_model = MagicMock()
        mock_model.predict = MagicMock(return_value=np.array([[0.3, 0.7]]))
        
        dataset = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'feature2': [5, 4, 3, 2, 1],
            'target': [0, 1, 0, 1, 0]
        })
        
        params = {
            'model': mock_model,
            'taskType': 'CLASSIFICATION',
            'modelType': 'Keras',
            'dataset': dataset,
            'targetClassLabel': 'target',
            'targetClassNames': ['class0', 'class1'],
            'lineDataset': None,
            'inputIndex': 0
        }
        
        result = ResponsibleAIExplain.lime_tabular_local_explanation(params)
        
        assert 'importantFeatures' in result[0]

    @patch('shap.Explainer')
    def test_text_shap_local_explanation(self, mock_explainer_class):
        """Test text_shap_local_explanation method"""
        
        
        mock_explainer = MagicMock()
        mock_explainer_class.return_value = mock_explainer
        
        mock_shap_values = np.random.rand(1, 10)
        mock_explainer.shap_values.return_value = mock_shap_values
        
        mock_model = MagicMock()
        mock_model.predict = MagicMock(return_value=np.array([1]))
        
        mock_preprocessor = MagicMock()
        mock_preprocessor.transform = MagicMock(return_value=MagicMock(toarray=MagicMock(return_value=np.ones((1, 10)))))
        mock_preprocessor.get_feature_names_out = MagicMock(return_value=np.array(['word1', 'word2', 'word3', 'word4', 'word5', 'word6', 'word7', 'word8', 'word9', 'word10']))
        
        dataset = pd.DataFrame({'text': ['sample text', 'another text']})
        
        params = {
            'model': mock_model,
            'dataset': dataset,
            'preprocessor': mock_preprocessor,
            'targetClassNames': ['negative', 'positive'],
            'lineDataset': None
        }
        
        result = ResponsibleAIExplain.text_shap_local_explanation(params)
        
        assert 'shapImportanceText' in result[0]

    def test_pipeline_processing_method(self):
        """Test pipeline_processing method"""
        
        
        # Create mock pipeline
        mock_preprocessor = MagicMock()
        mock_preprocessor.n_features_in_ = 2
        mock_preprocessor.transform = MagicMock(return_value=np.array([[1, 2], [3, 4]]))
        mock_preprocessor.get_feature_names_out = MagicMock(return_value=np.array(['feature1', 'feature2']))
        
        mock_model = MagicMock()
        
        mock_pipeline = MagicMock()
        mock_pipeline.steps = [('preprocessor', mock_preprocessor), ('model', mock_model)]
        mock_pipeline.__getitem__ = MagicMock(return_value=mock_preprocessor)
        
        dataset = pd.DataFrame({
            'feature1': [1, 2],
            'feature2': [3, 4],
            'target': [0, 1]
        })
        
        model, processed_data, label, input_data = ResponsibleAIExplain.pipeline_processing(
            mock_pipeline, dataset, 'target', None
        )
        
        assert model == mock_model

