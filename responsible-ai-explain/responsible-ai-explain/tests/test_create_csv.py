'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""
test_create_csv.py - Tests for create_csv.py
"""

import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch
import pandas as pd
import json
from explain.utils.create_csv import CreateCSV
from unittest.mock import MagicMock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))
class TestCreateCSVActualCoverage:
    """Tests for actual CreateCSV.json_to_csv method to increase coverage"""

    def test_json_to_csv_with_anchors(self, temp_directory):
        """Test json_to_csv with anchors data"""
        
        
        
        # Create mock explanation object
        mock_exp = MagicMock()
        mock_exp.inputRow = [{'featureName': 'f1', 'featureValue': 1.0}]
        mock_exp.inputText = None
        mock_exp.modelPrediction = 'ClassA'
        mock_exp.explanation = ['anchor1 > 0.5', 'anchor2 < 0.3']  # String explanations
        
        json_response = [{
            'scope': 'LOCAL',
            'anchors': [mock_exp]
        }]
        
        with patch('pandas.DataFrame.to_csv') as mock_to_csv:
            CreateCSV.json_to_csv(json_response)
            mock_to_csv.assert_called_once()

    def test_json_to_csv_with_feature_importance_dicts(self, temp_directory):
        """Test json_to_csv with featureImportance dict data"""
        
        
        
        mock_exp = MagicMock()
        mock_exp.inputRow = [{'featureName': 'f1', 'featureValue': 2.0}]
        mock_exp.inputText = None
        mock_exp.modelPrediction = 'ClassB'
        mock_exp.explanation = [{'featureName': 'f1', 'importanceScore': 0.5}]  # Dict explanations
        
        json_response = [{
            'scope': 'LOCAL',
            'featureImportance': [mock_exp]
        }]
        
        with patch('pandas.DataFrame.to_csv') as mock_to_csv:
            CreateCSV.json_to_csv(json_response)
            mock_to_csv.assert_called_once()

    def test_json_to_csv_with_time_series(self, temp_directory):
        """Test json_to_csv with timeSeriesForecast data"""
        
        
        
        mock_exp = MagicMock()
        mock_exp.inputRow = [{'featureName': 'ts_feature', 'featureValue': 100.0}]
        mock_exp.inputText = None
        mock_exp.modelPrediction = '150.0'
        mock_exp.explanation = [{'featureName': 'ts_feature', 'importanceScore': 0.8}]
        
        json_response = [{
            'scope': 'LOCAL',
            'timeSeriesForecast': [mock_exp]
        }]
        
        with patch('pandas.DataFrame.to_csv') as mock_to_csv:
            CreateCSV.json_to_csv(json_response)
            mock_to_csv.assert_called_once()

    def test_json_to_csv_with_shap_text(self, temp_directory):
        """Test json_to_csv with shapImportanceText data"""
        
        
        
        mock_exp = MagicMock()
        mock_exp.inputRow = None  # No inputRow for text
        mock_exp.inputText = "This is sample text"
        mock_exp.modelPrediction = 'Positive'
        mock_exp.explanation = [{'featureName': 'word1', 'importanceScore': 0.7}]
        
        json_response = [{
            'scope': 'LOCAL',
            'shapImportanceText': [mock_exp]
        }]
        
        with patch('pandas.DataFrame.to_csv') as mock_to_csv:
            CreateCSV.json_to_csv(json_response)
            mock_to_csv.assert_called_once()

    def test_json_to_csv_skips_global_scope(self):
        """Test json_to_csv skips GLOBAL scope items"""
        
        
        json_response = [{
            'scope': 'GLOBAL',
            'featureImportance': []
        }]
        
        # Should not raise and should not call to_csv
        with patch('pandas.DataFrame.to_csv') as mock_to_csv:
            CreateCSV.json_to_csv(json_response)
            mock_to_csv.assert_not_called()

    def test_json_to_csv_empty_list(self):
        """Test json_to_csv with empty list"""
        
        
        result = CreateCSV.json_to_csv([])
        assert result is None

    def test_json_to_csv_no_explanations(self):
        """Test json_to_csv with LOCAL scope but no explanations"""
        
        
        json_response = [{
            'scope': 'LOCAL'
            # No anchors, featureImportance, etc.
        }]
        
        with patch('pandas.DataFrame.to_csv') as mock_to_csv:
            CreateCSV.json_to_csv(json_response)
            mock_to_csv.assert_not_called()


class TestCreateCSVComprehensive:
    """Comprehensive tests for CreateCSV"""

    def test_json_to_csv_method_exists(self):
        """Test json_to_csv method exists"""
        
        assert hasattr(CreateCSV, 'json_to_csv')
        assert callable(CreateCSV.json_to_csv)

    def test_json_to_csv_empty_response(self):
        """Test json_to_csv with empty response"""
        
        result = CreateCSV.json_to_csv([])
        assert result is None

    def test_json_to_csv_global_scope(self):
        """Test json_to_csv with GLOBAL scope item"""
        
        json_response = [{'scope': 'GLOBAL'}]
        result = CreateCSV.json_to_csv(json_response)
        assert result is None

    def test_json_to_csv_local_no_explanations(self):
        """Test json_to_csv with LOCAL scope but no explanations"""
        
        json_response = [{'scope': 'LOCAL'}]
        result = CreateCSV.json_to_csv(json_response)
        assert result is None
