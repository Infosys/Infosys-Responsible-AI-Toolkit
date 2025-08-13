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

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from explain.service.responsible_ai_explain import ResponsibleAIExplain
from sklearn.datasets import load_iris, fetch_california_housing
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
from sklearn.model_selection import train_test_split
import pytest
import joblib
import keras
import pandas as pd

class TestKernelShapLocalExplanation:

    @classmethod
    def setup_class(cls):
        cls.housing = fetch_california_housing(as_frame=True)
        cls.X = cls.housing.data
        cls.y = cls.housing.target
        cls.X_train, cls.X_test, cls.y_train, cls.y_test = train_test_split(cls.X, cls.y, test_size=0.2, random_state=42)
        cls.model = RandomForestRegressor(max_depth=2,random_state=42)
        cls.model.fit(cls.X_train, cls.y_train)

        cls.params = {
            'model': cls.model,
            'dataset': cls.housing.frame,
            'taskType': 'REGRESSION',
            'modelType': 'Scikit-learn',
            'targetClassLabel': cls.housing.target_names[0],
            'targetClassNames': None,
            'inputIndex': 0,
            'api_input_request': None,
            'api_output_response': None
        }

        cls.result = ResponsibleAIExplain.kernel_shap_local_explanation(cls.params)

    def test_assert_keys_not_none(self):
        assert all(self.result[0][key] is not None for key in ['predictedTarget', 'modelConfidence', 'importantFeatures', 'inputRow'])

    def test_assert_predicted_target(self):
        assert self.result[0]['predictedTarget'] != self.model.predict(self.X_test.to_numpy()[0].reshape(1, -1))[0]

    def test_assert_model_none(self):
        self.params['model'] = None
        with pytest.raises(AttributeError):
            ResponsibleAIExplain.kernel_shap_local_explanation(self.params)

    def test_assert_dataset_none(self):
        self.params['model'] = self.model
        self.params['dataset'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.kernel_shap_local_explanation(self.params)
        self.params['dataset'] = self.housing.frame

    def test_assert_target_class_label_none(self):
        self.params['targetClassLabel'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.kernel_shap_local_explanation(self.params)
        self.params['targetClassLabel'] = self.housing.target_names[0]

    def test_assert_task_type_none(self):
        self.params['taskType'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.kernel_shap_local_explanation(self.params)
        self.params['taskType'] = 'REGRESSION'

    def test_assert_input_index_invalid(self):
        self.params['inputIndex'] = -1
        with pytest.raises(ValueError):
            ResponsibleAIExplain.kernel_shap_local_explanation(self.params)

class TestAnchorTabularLocalExplanation:
    @classmethod
    def setup_class(cls):
        # Assuming ResponsibleAIExplain is available
        # Load data (replace with your data loading logic)
        cls.dataset_cls = load_iris(as_frame=True)
        cls.X1 = cls.dataset_cls.data
        cls.y1 = cls.dataset_cls.target
        cls.X_train1, cls.X_test1, cls.y_train1, cls.y_test1 = train_test_split(cls.X1, cls.y1, test_size=0.2, random_state=42)
        cls.model_cls = RandomForestClassifier(random_state=42)
        cls.model_cls.fit(cls.X_train1, cls.y_train1)
        
        # Prepare the parameters
        cls.params = {
            'model': cls.model_cls,
            'dataset': cls.dataset_cls.frame,
            'modelType': 'Scikit-learn',
            'targetClassLabel': 'target',
            'targetClassNames': cls.dataset_cls.target_names.tolist(),
            'inputIndex': 0,
            'api_input_request': None,
            'api_output_response': None
        }

        # Test with all required parameters
        cls.result = ResponsibleAIExplain.anchor_tabular_local_explanation(cls.params)

    def test_assert_keys_not_none(self):
        assert all(key in self.result[0] for key in ['predictedTarget', 'modelConfidence', 'anchor', 'inputRow'])

    def test_assert_predicted_target(self):
        predicted_target = self.dataset_cls.target_names[self.model_cls.predict(self.X_test1.to_numpy()[0].reshape(1, -1))[0]]
        assert self.result[0]['predictedTarget'] != str(predicted_target)

    def test_assert_input_index_invalid(self):
        self.params['inputIndex'] = -1
        with pytest.raises(ValueError):
            ResponsibleAIExplain.anchor_tabular_local_explanation(self.params)

    def test_assert_missing_parameter(self):
        del self.params['inputIndex']
        with pytest.raises(KeyError):
            ResponsibleAIExplain.anchor_tabular_local_explanation(self.params)

    def test_assert_model_type_invalid(self):
        self.params['inputIndex'] = 0
        self.params['modelType'] = 'invalid'
        with pytest.raises(Exception):
            ResponsibleAIExplain.anchor_tabular_local_explanation(self.params)

    def test_assert_model_none(self):
        self.params['inputIndex'] = 0
        self.params['model'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.anchor_tabular_local_explanation(self.params)

    def test_assert_dataset_none(self):
        self.params['model'] = self.model_cls
        self.params['dataset'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.anchor_tabular_local_explanation(self.params)

    def test_assert_target_class_label_none(self):
        self.params['dataset'] = self.dataset_cls.frame
        self.params['targetClassLabel'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.anchor_tabular_local_explanation(self.params)

    def test_assert_model_type_none(self):
        self.params['targetClassLabel'] = 'target'
        self.params['modelType'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.anchor_tabular_local_explanation(self.params)
    
class TestPartialDependenceVarianceGlobalExplanation:
    @classmethod
    def setup_class(cls):
        # Assuming ResponsibleAIExplain is available
        # Load data (replace with your data loading logic)
        cls.housing = fetch_california_housing(as_frame=True)
        cls.X = cls.housing.data
        cls.y = cls.housing.target
        X_train, X_test, y_train, y_test = train_test_split(cls.X, cls.y, test_size=0.2, random_state=42)
        cls.model = RandomForestRegressor(max_depth=2,random_state=42)
        cls.model.fit(X_train, y_train)

        # Prepare the parameters
        cls.params = {
            'model': cls.model,
            'dataset': cls.housing.frame,
            'taskType': 'REGRESSION',
            'modelType': 'Scikit-learn',
            'targetClassLabel': cls.housing.target_names[0],
            'targetClassNames': None,
            'api_input_request': None,
            'api_output_response': None
        }

        # Call the function with all required parameters
        cls.result = ResponsibleAIExplain.partial_dependence_variance_global_explanation(cls.params)

    def test_assert_keys_not_none(self):
        assert all(key in self.result[0] for key in ['modelConfidence', 'importantFeatures'])

    def test_assert_model_none(self):
        self.params['model'] = None
        with pytest.raises(AttributeError):
            ResponsibleAIExplain.partial_dependence_variance_global_explanation(self.params)

    def test_assert_dataset_none(self):
        self.params['model'] = self.model
        self.params['dataset'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.partial_dependence_variance_global_explanation(self.params)

    def test_assert_target_class_label_none(self):
        self.params['dataset'] = self.housing.frame
        self.params['targetClassLabel'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.partial_dependence_variance_global_explanation(self.params)

    def test_assert_task_type_none(self):
        self.params['targetClassLabel'] = self.housing.target_names[0]
        self.params['taskType'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.partial_dependence_variance_global_explanation(self.params)

class TestTreeShapLocalExplanationRegression:

    @classmethod
    def setup_class(cls):
        cls.housing = fetch_california_housing(as_frame=True)
        cls.X = cls.housing.data
        cls.y = cls.housing.target
        cls.X_train, cls.X_test, cls.y_train, cls.y_test = train_test_split(cls.X, cls.y, test_size=0.2, random_state=42)
        cls.model = RandomForestRegressor(max_depth=2,random_state=42)
        cls.model.fit(cls.X_train, cls.y_train)

        cls.params = {
            'model': cls.model,
            'dataset': cls.housing.frame,
            'taskType': 'REGRESSION',
            'modelType': 'Scikit-learn',
            'targetClassLabel': cls.housing.target_names[0],
            'targetClassNames': None,
            'inputIndex': 0,
            'api_input_request': None,
            'api_output_response': None
        }

        cls.result = ResponsibleAIExplain.tree_shap_local_explanation(cls.params)

    def test_assert_keys_not_none(self):
        assert all(self.result[0][key] is not None for key in ['predictedTarget', 'modelConfidence', 'importantFeatures', 'inputRow'])

    def test_assert_predicted_target(self):
        assert self.result[0]['predictedTarget'] != self.model.predict(self.X_test.to_numpy()[0].reshape(1, -1))[0]

    def test_assert_model_none(self):
        self.params['model'] = None
        with pytest.raises(AttributeError):
            ResponsibleAIExplain.tree_shap_local_explanation(self.params)

    def test_assert_dataset_none(self):
        self.params['model'] = self.model
        self.params['dataset'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.tree_shap_local_explanation(self.params)
        self.params['dataset'] = self.housing.frame

    def test_assert_target_class_label_none(self):
        self.params['targetClassLabel'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.tree_shap_local_explanation(self.params)
        self.params['targetClassLabel'] = self.housing.target_names[0]

    def test_assert_task_type_none(self):
        self.params['taskType'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.tree_shap_local_explanation(self.params)
        self.params['taskType'] = 'REGRESSION'

    def test_assert_input_index_invalid(self):
        self.params['inputIndex'] = -1
        with pytest.raises(ValueError):
            ResponsibleAIExplain.tree_shap_local_explanation(self.params)


class TestTreeShapLocalExplanationclassification:
    @classmethod
    def setup_class(cls):
        # Assuming ResponsibleAIExplain is available
        # Load data (replace with your data loading logic)
        cls.dataset_cls = load_iris(as_frame=True)
        cls.X1 = cls.dataset_cls.data
        cls.y1 = cls.dataset_cls.target
        cls.X_train1, cls.X_test1, cls.y_train1, cls.y_test1 = train_test_split(cls.X1, cls.y1, test_size=0.2, random_state=42)
        cls.model_cls = RandomForestClassifier(random_state=42)
        cls.model_cls.fit(cls.X_train1, cls.y_train1)
        
        # Prepare the parameters
        cls.params = {
            'model': cls.model_cls,
            'dataset': cls.dataset_cls.frame,
            'taskType': 'CLASSIFICATION',
            'modelType': 'Scikit-learn',
            'targetClassLabel': 'target',
            'targetClassNames': cls.dataset_cls.target_names.tolist(),
            'inputIndex': 0,
            'api_input_request': None,
            'api_output_response': None
        }

        # Test with all required parameters
        cls.result = ResponsibleAIExplain.tree_shap_local_explanation(cls.params)

    def test_assert_keys_not_none(self):
        assert all(key in self.result[0] for key in ['predictedTarget', 'modelConfidence', 'importantFeatures', 'inputRow'])

    def test_assert_predicted_target(self):
        predicted_target = self.dataset_cls.target_names[self.model_cls.predict(self.X_test1.to_numpy()[0].reshape(1, -1))[0]]
        assert self.result[0]['predictedTarget'] != str(predicted_target)

    def test_assert_input_index_invalid(self):
        self.params['inputIndex'] = -1
        with pytest.raises(ValueError):
            ResponsibleAIExplain.tree_shap_local_explanation(self.params)

    def test_assert_missing_parameter(self):
        del self.params['inputIndex']
        with pytest.raises(KeyError):
            ResponsibleAIExplain.tree_shap_local_explanation(self.params)

    def test_assert_model_none(self):
        self.params['inputIndex'] = 0
        self.params['model'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.tree_shap_local_explanation(self.params)

    def test_assert_dataset_none(self):
        self.params['model'] = self.model_cls
        self.params['dataset'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.tree_shap_local_explanation(self.params)

    def test_assert_target_class_label_none(self):
        self.params['dataset'] = self.dataset_cls.frame
        self.params['targetClassLabel'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.tree_shap_local_explanation(self.params)
                   
class TestTreeShapGlobalExplanationRegression:

    @classmethod
    def setup_class(cls):
        cls.housing = fetch_california_housing(as_frame=True)
        cls.X = cls.housing.data
        cls.y = cls.housing.target
        cls.X_train, cls.X_test, cls.y_train, cls.y_test = train_test_split(cls.X, cls.y, test_size=0.2, random_state=42)
        cls.model = RandomForestRegressor(max_depth=2,random_state=42)
        cls.model.fit(cls.X_train, cls.y_train)

        cls.params = {
            'model': cls.model,
            'dataset': cls.housing.frame,
            'taskType': 'REGRESSION',
            'modelType': 'Scikit-learn',
            'targetClassLabel': cls.housing.target_names[0],
            'targetClassNames': None,
        }

        cls.result = ResponsibleAIExplain.tree_shap_global_explanation(cls.params)

    def test_assert_keys_not_none(self):
        assert all(self.result[0][key] is not None for key in ['modelConfidence', 'importantFeatures'])

    def test_assert_model_none(self):
        self.params['model'] = None
        with pytest.raises(AttributeError):
            ResponsibleAIExplain.tree_shap_global_explanation(self.params)

    def test_assert_dataset_none(self):
        self.params['model'] = self.model
        self.params['dataset'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.tree_shap_global_explanation(self.params)
        self.params['dataset'] = self.housing.frame

    def test_assert_target_class_label_none(self):
        self.params['targetClassLabel'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.tree_shap_global_explanation(self.params)
        self.params['targetClassLabel'] = self.housing.target_names[0]

    def test_assert_task_type_none(self):
        self.params['taskType'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.tree_shap_global_explanation(self.params)
        self.params['taskType'] = 'REGRESSION'
        
        
class TestTreeShapGlobalExplanationclassification:
    @classmethod
    def setup_class(cls):
        # Assuming ResponsibleAIExplain is available
        # Load data (replace with your data loading logic)
        cls.dataset_cls = load_iris(as_frame=True)
        cls.X1 = cls.dataset_cls.data
        cls.y1 = cls.dataset_cls.target
        cls.X_train1, cls.X_test1, cls.y_train1, cls.y_test1 = train_test_split(cls.X1, cls.y1, test_size=0.2, random_state=42)
        cls.model_cls = RandomForestClassifier(random_state=42)
        cls.model_cls.fit(cls.X_train1, cls.y_train1)
        
        # Prepare the parameters
        cls.params = {
            'model': cls.model_cls,
            'dataset': cls.dataset_cls.frame,
            'taskType': 'CLASSIFICATION',
            'modelType': 'Scikit-learn',
            'targetClassLabel': 'target',
            'targetClassNames': cls.dataset_cls.target_names.tolist(),
        }

        # Test with all required parameters
        cls.result = ResponsibleAIExplain.tree_shap_global_explanation(cls.params)

    def test_assert_keys_not_none(self):
        assert all(key in self.result[0] for key in ['modelConfidence', 'importantFeatures'])



    def test_assert_model_none(self):
        self.params['model'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.tree_shap_global_explanation(self.params)

    def test_assert_dataset_none(self):
        self.params['model'] = self.model_cls
        self.params['dataset'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.tree_shap_global_explanation(self.params)

    def test_assert_target_class_label_none(self):
        self.params['dataset'] = self.dataset_cls.frame
        self.params['targetClassLabel'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.tree_shap_global_explanation(self.params)


class TestPermutationImportanceGlobalExplanation:

    @classmethod
    def setup_class(cls):
        cls.housing = fetch_california_housing(as_frame=True)
        cls.X = cls.housing.data
        cls.y = cls.housing.target
        cls.X_train, cls.X_test, cls.y_train, cls.y_test = train_test_split(cls.X, cls.y, test_size=0.2, random_state=42)
        cls.model = RandomForestRegressor(max_depth=2,random_state=42)
        cls.model.fit(cls.X_train, cls.y_train)

        cls.params = {
            'model': cls.model,
            'dataset': cls.housing.frame,
            'taskType': 'REGRESSION',
            'modelType': 'Scikit-learn',
            'targetClassLabel': cls.housing.target_names[0],
            'targetClassNames': None,
            'api_input_request': None,
            'api_output_response': None
        }

        cls.result = ResponsibleAIExplain.permutation_importance_global_explanation(cls.params)

    def test_assert_keys_not_none(self):
        assert all(self.result[0][key] is not None for key in ['modelConfidence', 'importantFeatures'])

    def test_assert_model_none(self):
        self.params['model'] = None
        with pytest.raises(AttributeError):
            ResponsibleAIExplain.permutation_importance_global_explanation(self.params)

    def test_assert_dataset_none(self):
        self.params['model'] = self.model
        self.params['dataset'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.permutation_importance_global_explanation(self.params)
        self.params['dataset'] = self.housing.frame

    def test_assert_target_class_label_none(self):
        self.params['targetClassLabel'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.permutation_importance_global_explanation(self.params)
        self.params['targetClassLabel'] = self.housing.target_names[0]

    def test_assert_task_type_none(self):
        self.params['taskType'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.permutation_importance_global_explanation(self.params)
        self.params['taskType'] = 'REGRESSION'
        
class TestLimeTabularLocalExplanation:
    @classmethod
    def setup_class(cls):
        # Assuming ResponsibleAIExplain is available
        # Load data (replace with your data loading logic)
        cls.dataset_cls = load_iris(as_frame=True)
        cls.X1 = cls.dataset_cls.data
        cls.y1 = cls.dataset_cls.target
        cls.X_train1, cls.X_test1, cls.y_train1, cls.y_test1 = train_test_split(cls.X1, cls.y1, test_size=0.2, random_state=42)
        cls.model_cls = RandomForestClassifier(random_state=42)
        cls.model_cls.fit(cls.X_train1, cls.y_train1)
        
        # Prepare the parameters
        cls.params = {
            'model': cls.model_cls,
            'dataset': cls.dataset_cls.frame,
            'taskType': 'CLASSIFICATION',
            'modelType': 'Scikit-learn',
            'targetClassLabel': 'target',
            'targetClassNames': cls.dataset_cls.target_names.tolist(),
            'inputIndex': 0,
        }

        # Test with all required parameters
        cls.result = ResponsibleAIExplain.lime_tabular_local_explanation(cls.params)

    def test_assert_keys_not_none(self):
        assert all(key in self.result[0] for key in ['predictedTarget', 'modelConfidence', 'importantFeatures', 'inputRow'])

    def test_assert_predicted_target(self):
        predicted_target = self.dataset_cls.target_names[self.model_cls.predict(self.X_test1.to_numpy()[0].reshape(1, -1))[0]]
        assert self.result[0]['predictedTarget'] != str(predicted_target)

    def test_assert_input_index_invalid(self):
        self.params['inputIndex'] = -1
        with pytest.raises(ValueError):
            ResponsibleAIExplain.lime_tabular_local_explanation(self.params)

    def test_assert_missing_parameter(self):
        del self.params['inputIndex']
        with pytest.raises(KeyError):
            ResponsibleAIExplain.lime_tabular_local_explanation(self.params)

    def test_assert_model_type_invalid(self):
        self.params['inputIndex'] = 0
        self.params['modelType'] = 'invalid'
        with pytest.raises(Exception):
            ResponsibleAIExplain.lime_tabular_local_explanation(self.params)

    def test_assert_model_none(self):
        self.params['inputIndex'] = 0
        self.params['model'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.lime_tabular_local_explanation(self.params)

    def test_assert_dataset_none(self):
        self.params['model'] = self.model_cls
        self.params['dataset'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.lime_tabular_local_explanation(self.params)

    def test_assert_target_class_label_none(self):
        self.params['dataset'] = self.dataset_cls.frame
        self.params['targetClassLabel'] = None
        
        with pytest.raises(Exception):
            ResponsibleAIExplain.lime_tabular_local_explanation(self.params)

    def test_assert_model_type_none(self):
        self.params['targetClassLabel'] = 'target'
        self.params['modelType'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.lime_tabular_local_explanation(self.params)

class TestAnchorTextLocalExplanation:
    @classmethod
    def setup_class(cls):
        cls.model = joblib.load(r'models\localtext_explain_model.pkl')
        cls.vectorizer = joblib.load(r'models\localtext_explain_vectorizer.pkl')
        cls.dataset = pd.read_csv(r'dataset\Test_Data.csv')
        
        # Prepare the parameters
        cls.params = {
            'model': cls.model,
            'preprocessor': cls.vectorizer,
            'dataset': cls.dataset,
            'targetClassNames': ['Negative', 'Positive']
        }

        # Test with all required parameters
        cls.result = ResponsibleAIExplain.anchor_text_local_explanation(cls.params)

    def test_assert_keys_not_none(self):
        assert all(key in self.result[0] for key in ['anchorText', 'description'])

    def test_assert_model_none(self):
        self.params['model'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.anchor_text_local_explanation(self.params)

    def test_assert_preprocessor_none(self):
        self.params['model'] = self.model
        self.params['preprocessor'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.anchor_text_local_explanation(self.params)
    
    def test_assert_dataset_none(self):
        self.params['model'] = self.model
        self.params['preprocessor'] = self.vectorizer
        self.params['dataset'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.anchor_text_local_explanation(self.params)
    
    def test_assert_target_class_names_none(self):
        self.params['dataset'] = self.dataset
        self.params['targetClassNames'] = None
        with pytest.raises(Exception):
            ResponsibleAIExplain.anchor_text_local_explanation(self.params)

    def test_assert_missing_parameter(self):
        self.params['targetClassNames'] = ['Negative', 'Positive']
        del self.params['model']
        with pytest.raises(KeyError):
            ResponsibleAIExplain.anchor_text_local_explanation(self.params)


    
                                                    