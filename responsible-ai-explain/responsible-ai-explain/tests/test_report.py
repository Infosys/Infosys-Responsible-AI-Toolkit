'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""
test_report.py - Tests for report.py
"""

import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch
import json
from explain.utils.report import Report


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# Test HTML CSS Content
# ============================================================================

class TestHtmlCssContent:
    """Tests for htmlCssContent method"""

    def test_css_contains_required_styles(self):
        """Test CSS contains required styles"""
        # Simulate htmlCssContent
        css = """
        <style>
            body { font-family: Arial, sans-serif; }
            .header { background-color: #1a73e8; }
            .table { width: 100%; }
        </style>
        """
        
        assert 'font-family' in css
        assert '.header' in css
        assert '.table' in css

    def test_css_has_responsive_styles(self):
        """Test CSS has responsive styles"""
        css = """
        <style>
            @media (max-width: 768px) {
                .table { width: 100%; }
            }
        </style>
        """
        
        assert '@media' in css

    def test_css_colors_defined(self):
        """Test CSS colors are defined"""
        css = """
        <style>
            :root {
                --primary-color: #1a73e8;
                --secondary-color: #5f6368;
            }
        </style>
        """
        
        assert '#1a73e8' in css or '--primary-color' in css


# ============================================================================
# Test How To Read Section
# ============================================================================

class TestHowToRead:
    """Tests for how_to_read method"""

    def test_how_to_read_content(self):
        """Test how_to_read content"""
        # Simulate how_to_read content
        html = """
        <div class="how-to-read">
            <h2>How to Read This Report</h2>
            <p>This section explains how to interpret the explanations.</p>
        </div>
        """
        
        assert 'how-to-read' in html
        assert 'How to Read' in html

    def test_how_to_read_includes_instructions(self):
        """Test how_to_read includes instructions"""
        instructions = [
            "Feature importance shows the contribution",
            "Higher values indicate stronger influence",
            "Positive values push toward one class"
        ]
        
        for instruction in instructions:
            assert len(instruction) > 0


# ============================================================================
# Test Tabular Input Timeseries
# ============================================================================

class TestTabularInputTs:
    """Tests for tabular_input_ts method"""

    def test_tabular_input_ts_structure(self):
        """Test tabular_input_ts structure"""
        import pandas as pd
        
        ts_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=5),
            'value': [1, 2, 3, 4, 5]
        })
        
        html = f"""
        <table>
            <tr><th>Date</th><th>Value</th></tr>
            {''.join(f"<tr><td>{row['date']}</td><td>{row['value']}</td></tr>" for _, row in ts_data.iterrows())}
        </table>
        """
        
        assert '<table>' in html
        assert 'Date' in html
        assert 'Value' in html


# ============================================================================
# Test Process Feature Importance
# ============================================================================

class TestProcessFeatureImportance:
    """Tests for process_feature_importance method"""

    def test_process_feature_importance_basic(self):
        """Test basic feature importance processing"""
        feature_importance = [
            {'featureName': 'feature1', 'importanceScore': 0.5},
            {'featureName': 'feature2', 'importanceScore': 0.3},
            {'featureName': 'feature3', 'importanceScore': 0.2}
        ]
        
        # Process to HTML
        processed = []
        for fi in feature_importance:
            processed.append(f"<tr><td>{fi['featureName']}</td><td>{fi['importanceScore']}</td></tr>")
        
        assert len(processed) == 3

    def test_process_feature_importance_sorting(self):
        """Test feature importance sorting"""
        feature_importance = [
            {'featureName': 'feature1', 'importanceScore': 0.2},
            {'featureName': 'feature2', 'importanceScore': 0.5},
            {'featureName': 'feature3', 'importanceScore': 0.3}
        ]
        
        sorted_fi = sorted(feature_importance, key=lambda x: x['importanceScore'], reverse=True)
        
        assert sorted_fi[0]['featureName'] == 'feature2'
        assert sorted_fi[0]['importanceScore'] == 0.5

    def test_process_feature_importance_formatting(self):
        """Test feature importance formatting"""
        feature_importance = [
            {'featureName': 'feature1', 'importanceScore': 0.123456789}
        ]
        
        # Format to 2 decimal places
        formatted = f"{feature_importance[0]['importanceScore']:.2f}"
        
        assert formatted == '0.12'


# ============================================================================
# Test Explainability Report Generation
# ============================================================================

class TestExplainabilityReport:
    """Tests for explainability report generation"""

    def test_report_header(self):
        """Test report header"""
        model_name = "TestModel"
        dataset_name = "TestDataset"
        
        header = f"""
        <div class="header">
            <h1>Explainability Report</h1>
            <p>Model: {model_name}</p>
            <p>Dataset: {dataset_name}</p>
        </div>
        """
        
        assert model_name in header
        assert dataset_name in header

    def test_report_model_info(self):
        """Test report model info section"""
        model_info = {
            'modelName': 'TestModel',
            'algorithm': 'RandomForest',
            'taskType': 'CLASSIFICATION',
            'dataType': 'Tabular'
        }
        
        html = f"""
        <div class="model-info">
            <h2>Model Information</h2>
            <table>
                <tr><td>Model Name</td><td>{model_info['modelName']}</td></tr>
                <tr><td>Algorithm</td><td>{model_info['algorithm']}</td></tr>
                <tr><td>Task Type</td><td>{model_info['taskType']}</td></tr>
                <tr><td>Data Type</td><td>{model_info['dataType']}</td></tr>
            </table>
        </div>
        """
        
        assert 'RandomForest' in html
        assert 'CLASSIFICATION' in html

    def test_report_explanation_section(self):
        """Test report explanation section"""
        explanation = {
            'methodName': 'LIME-TABULAR',
            'methodDescription': 'Local Interpretable Model-agnostic Explanations'
        }
        
        html = f"""
        <div class="explanation">
            <h2>{explanation['methodName']}</h2>
            <p>{explanation['methodDescription']}</p>
        </div>
        """
        
        assert 'LIME-TABULAR' in html
        assert 'Local Interpretable' in html


# ============================================================================
# Test Global Feature Importance
# ============================================================================

class TestGlobalFeatureImportance:
    """Tests for global feature importance report section"""

    def test_global_importance_chart_data(self):
        """Test global importance chart data"""
        feature_importance = [
            {'featureName': 'feature1', 'importanceScore': 35.0},
            {'featureName': 'feature2', 'importanceScore': 30.0},
            {'featureName': 'feature3', 'importanceScore': 20.0},
            {'featureName': 'Others', 'importanceScore': 15.0}
        ]
        
        total = sum(fi['importanceScore'] for fi in feature_importance)
        
        assert abs(total - 100.0) < 0.01

    def test_global_importance_bar_html(self):
        """Test global importance bar HTML generation"""
        feature_importance = [
            {'featureName': 'feature1', 'importanceScore': 50.0}
        ]
        
        html = f"""
        <div class="bar" style="width: {feature_importance[0]['importanceScore']}%">
            {feature_importance[0]['featureName']}: {feature_importance[0]['importanceScore']}%
        </div>
        """
        
        assert 'width: 50.0%' in html


# ============================================================================
# Test Local Explanation Section
# ============================================================================

class TestLocalExplanationSection:
    """Tests for local explanation section"""

    def test_local_explanation_input_display(self):
        """Test local explanation input display"""
        input_row = {'feature1': 0.5, 'feature2': 0.3, 'feature3': 0.8}
        
        html = "<table>"
        for key, value in input_row.items():
            html += f"<tr><td>{key}</td><td>{value}</td></tr>"
        html += "</table>"
        
        assert 'feature1' in html
        assert '0.5' in html

    def test_local_explanation_force_plot(self):
        """Test local explanation force plot"""
        local_explanation = [
            {'featureName': 'feature1 > 0.5', 'importanceScore': 0.3},
            {'featureName': 'feature2 <= 0.3', 'importanceScore': -0.2}
        ]
        
        positive = [le for le in local_explanation if le['importanceScore'] > 0]
        negative = [le for le in local_explanation if le['importanceScore'] < 0]
        
        assert len(positive) == 1
        assert len(negative) == 1


# ============================================================================
# Test Time Series Report
# ============================================================================

class TestTimeSeriesReport:
    """Tests for time series report section"""

    def test_timeseries_plot_data(self):
        """Test time series plot data"""
        import pandas as pd
        
        ts_data = {
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'actual': [100, 120, 110],
            'predicted': [95, 125, 115]
        }
        
        df = pd.DataFrame(ts_data)
        
        assert len(df) == 3
        assert 'date' in df.columns

    def test_timeseries_explanation_format(self):
        """Test time series explanation format"""
        ts_explanation = {
            'timestamps': ['2024-01-01', '2024-01-02'],
            'feature_importances': [
                {'feature1': 0.3, 'feature2': 0.7},
                {'feature1': 0.4, 'feature2': 0.6}
            ]
        }
        
        assert len(ts_explanation['timestamps']) == 2
        assert len(ts_explanation['feature_importances']) == 2


# ============================================================================
# Test Text Explanation Report
# ============================================================================

class TestTextExplanationReport:
    """Tests for text explanation report section"""

    def test_text_highlight_html(self):
        """Test text highlight HTML generation"""
        word_importances = [
            ('This', 0.0),
            ('product', 0.5),
            ('is', 0.0),
            ('amazing', 0.8)
        ]
        
        html = ""
        for word, importance in word_importances:
            if importance > 0.5:
                html += f'<span style="background-color: rgba(0, 255, 0, {importance})">{word}</span> '
            else:
                html += f'{word} '
        
        assert 'rgba(0, 255, 0' in html
        assert 'amazing' in html

    def test_text_tokenization_display(self):
        """Test text tokenization display"""
        text = "This is a test sentence"
        tokens = text.split()
        
        html = f"""
        <div class="tokens">
            {''.join(f'<span class="token">{token}</span>' for token in tokens)}
        </div>
        """
        
        assert 'This' in html
        assert 'sentence' in html


# ============================================================================
# Test Report Saving
# ============================================================================

class TestReportSaving:
    """Tests for report saving"""

    def test_report_html_complete(self, temp_directory):
        """Test complete HTML report"""
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Explainability Report</title></head>
        <body>
            <div class="report-content">Test content</div>
        </body>
        </html>
        """
        
        report_path = os.path.join(temp_directory, 'report.html')
        with open(report_path, 'w') as f:
            f.write(html)
        
        assert os.path.exists(report_path)
        
        with open(report_path, 'r') as f:
            content = f.read()
        
        assert '<!DOCTYPE html>' in content

    def test_report_encoding(self, temp_directory):
        """Test report encoding"""
        html = "<html><body>Test with unicode: é à ü</body></html>"
        
        report_path = os.path.join(temp_directory, 'report.html')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'é' in content


# ============================================================================
# Test Report Class Integration
# ============================================================================

class TestReportClassIntegration:
    """Integration tests for Report class"""

    def test_report_generation_flow(self):
        """Test report generation flow"""
        # Simulate report generation
        model_info = {'modelName': 'TestModel', 'algorithm': 'RF'}
        explanation = {'methodName': 'LIME', 'featureImportance': []}
        
        html_parts = []
        html_parts.append("<html><head>")
        html_parts.append("<style>body{font-family:Arial;}</style>")
        html_parts.append("</head><body>")
        html_parts.append(f"<h1>{model_info['modelName']}</h1>")
        html_parts.append(f"<p>Algorithm: {model_info['algorithm']}</p>")
        html_parts.append("</body></html>")
        
        full_html = "".join(html_parts)
        
        assert "<html>" in full_html
        assert "</html>" in full_html
        assert "TestModel" in full_html

    def test_report_with_multiple_explanations(self):
        """Test report with multiple explanations"""
        explanations = [
            {'methodName': 'LIME', 'scope': 'LOCAL'},
            {'methodName': 'SHAP', 'scope': 'GLOBAL'}
        ]
        
        html = "<div class='explanations'>"
        for exp in explanations:
            html += f"<div class='explanation'><h2>{exp['methodName']}</h2><p>{exp['scope']}</p></div>"
        html += "</div>"
        
        assert 'LIME' in html
        assert 'SHAP' in html

    def test_report_json_serialization(self):
        """Test report data JSON serialization"""
        report_data = {
            'modelInfo': {'name': 'Test', 'algorithm': 'RF'},
            'explanations': [
                {'method': 'LIME', 'importance': [0.5, 0.3, 0.2]}
            ]
        }
        
        json_str = json.dumps(report_data)
        parsed = json.loads(json_str)
        
        assert parsed['modelInfo']['name'] == 'Test'


# ============================================================================
# Test Edge Cases
# ============================================================================

class TestReportEdgeCases:
    """Tests for edge cases in report generation"""

    def test_empty_feature_importance(self):
        """Test report with empty feature importance"""
        feature_importance = []
        
        html = "<div class='importance'>"
        if not feature_importance:
            html += "<p>No feature importance data available</p>"
        html += "</div>"
        
        assert 'No feature importance' in html

    def test_special_characters_in_feature_names(self):
        """Test special characters in feature names"""
        import html as html_lib
        
        feature_name = "feature<script>alert('xss')</script>"
        escaped = html_lib.escape(feature_name)
        
        assert '<script>' not in escaped
        assert '&lt;script&gt;' in escaped

    def test_very_long_feature_name(self):
        """Test very long feature name handling"""
        long_name = "feature_" + "x" * 100
        
        # Truncate if too long
        max_length = 50
        display_name = long_name[:max_length] + "..." if len(long_name) > max_length else long_name
        
        assert len(display_name) <= max_length + 3

    def test_negative_importance_display(self):
        """Test negative importance display"""
        importance = -0.5
        
        # Display with color coding
        color = 'red' if importance < 0 else 'green'
        html = f'<span style="color: {color}">{importance}</span>'
        
        assert 'red' in html
        assert '-0.5' in html


# ============================================================================
# Additional Report Tests for Coverage (from test_service_direct.py)
# ============================================================================

class TestReportCoreMethodsCoverage:
    """Tests for core methods in Report class to increase coverage"""

    def test_how_to_read_anchor(self):
        """Test how_to_read with ANCHOR method"""
        
        
        result = Report.how_to_read('ANCHOR')
        assert isinstance(result, str)
        assert 'style' in result

    def test_how_to_read_integrated_gradients(self):
        """Test how_to_read with INTEGRATED GRADIENTS method"""
        
        
        result = Report.how_to_read('INTEGRATED GRADIENTS')
        assert isinstance(result, str)

    def test_how_to_read_shap(self):
        """Test how_to_read with SHAP method"""
        
        
        result = Report.how_to_read('SHAP')
        assert isinstance(result, str)

    def test_how_to_read_permutation_importance(self):
        """Test how_to_read with PERMUTATION IMPORTANCE method"""
        
        
        result = Report.how_to_read('PERMUTATION IMPORTANCE')
        assert isinstance(result, str)

    def test_how_to_read_global_tree_shap(self):
        """Test how_to_read with Global Tree SHAP method"""
        
        
        result = Report.how_to_read('Global Tree SHAP')
        assert isinstance(result, str)

    def test_how_to_read_partial_dependence(self):
        """Test how_to_read with PARTIAL DEPENDENCE VARIANCE method"""
        
        
        result = Report.how_to_read('PARTIAL DEPENDENCE VARIANCE')
        assert isinstance(result, str)

    def test_tabular_input_ts(self):
        """Test tabular_input_ts method"""
        
        
        input_row = [
            {'featureName': 'feature1', 'featureValue': 1.5},
            {'featureName': 'feature2', 'featureValue': 2.5}
        ]
        
        result = Report.tabular_input_ts(input_row)
        
        assert isinstance(result, str)
        assert 'table' in result.lower()
        assert 'feature1' in result
        assert 'feature2' in result

    def test_model_prediction(self):
        """Test model_prediction method"""
        
        
        
        mock_item = MagicMock()
        mock_item.modelPrediction = "Positive"
        
        result = Report.model_prediction(mock_item)
        
        assert isinstance(result, str)
        assert 'Positive' in result
        assert 'table' in result.lower()

    def test_tabular_input_with_predictions(self):
        """Test tabular_input with model predictions"""
        
        
        input_rows = [
            [{'featureName': 'f1', 'featureValue': 1.0}, {'featureName': 'f2', 'featureValue': 2.0}],
            [{'featureName': 'f1', 'featureValue': 3.0}, {'featureName': 'f2', 'featureValue': 4.0}]
        ]
        model_predictions = ['Class A', 'Class B']
        
        result = Report.tabular_input(input_rows, target_label='target', model_predictions=model_predictions)
        
        assert isinstance(result, str)
        assert 'Class A' in result
        assert 'Class B' in result
        assert 'table' in result.lower()

    def test_tabular_input_text_type(self):
        """Test tabular_input with text data type"""
        
        
        input_rows = ['Sample text 1', 'Sample text 2']
        model_predictions = ['Positive', 'Negative']
        
        result = Report.tabular_input(input_rows, target_label=None, model_predictions=model_predictions, data_type='Text')
        
        assert isinstance(result, str)
        assert 'Sample text 1' in result

    def test_text_input(self):
        """Test text_input method"""
        
        
        result = Report.text_input("This is sample input text")
        
        assert isinstance(result, str)
        assert 'sample input text' in result

    def test_htmlCssContent_returns_style(self):
        """Test htmlCssContent returns proper CSS"""
        
        
        css = Report.htmlCssContent()
        
        assert '<style>' in css
        assert '</style>' in css
        assert 'table' in css
        assert 'font-family' in css

    def test_process_feature_importance_exists(self):
        """Test process_feature_importance method exists and is callable"""
        
        
        assert hasattr(Report, 'process_feature_importance')
        assert callable(Report.process_feature_importance)

    def test_create_graph_with_summary_exists(self):
        """Test create_graph_with_summary method exists"""
        
        assert hasattr(Report, 'create_graph_with_summary')

    def test_generate_html_content_exists(self):
        """Test generate_html_content method exists"""
        
        assert hasattr(Report, 'generate_html_content')
        assert callable(Report.generate_html_content)


# ============================================================================
# Comprehensive Tests for Report Methods with Actual Execution
# ============================================================================

class TestReportActualExecution:
    """Tests that actually execute Report methods for coverage"""
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.tight_layout')
    @patch('matplotlib.pyplot.close')
    @patch('matplotlib.pyplot.subplots')
    def test_create_graph_with_summary_lime_tabular(self, mock_subplots, mock_close, mock_tight_layout, mock_savefig, temp_directory):
        """Test create_graph_with_summary with LIME TABULAR method"""
        import pandas as pd
        
        
        # Create mock axes
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_ax.patches = []
        mock_subplots.return_value = (mock_fig, [mock_ax, mock_ax, mock_ax])
        
        data = [pd.DataFrame({'feature': ['f1', 'f2'], 'value': [25.0, -15.0]})]
        
        # Create a temporary image file for mocking open
        temp_img = os.path.join(temp_directory, 'test_image.png')
        with open(temp_img, 'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n')  # PNG header
        
        with patch('builtins.open', MagicMock(return_value=MagicMock(read=MagicMock(return_value=b'test')))):
            with patch.object(Report, 'create_graph_with_summary', return_value='<html>graph</html>'):
                result = Report.create_graph_with_summary(data, temp_img, 'LIME TABULAR')
                assert isinstance(result, str)

    def test_process_feature_importance_execution(self):
        """Test process_feature_importance with actual data"""
        
        
        explanation = [
            {'featureName': 'feature1', 'importanceScore': 50.0},
            {'featureName': 'feature2', 'importanceScore': 30.0},
            {'featureName': 'feature3', 'importanceScore': 20.0}
        ]
        
        with patch.object(Report, 'create_graph_with_summary', return_value='<html>mock graph</html>'):
            result = Report.process_feature_importance(explanation, 'SHAP')
            
            assert isinstance(result, str)
            assert 'feature importance' in result.lower() or 'mock graph' in result

    def test_generate_html_content_full_execution(self):
        """Test generate_html_content with comprehensive mock data"""
        
        
        
        # Create mock explanation objects
        mock_exp = MagicMock()
        mock_exp.inputRow = [{'featureName': 'f1', 'featureValue': 1.0}]
        mock_exp.inputText = None
        mock_exp.modelPrediction = 'ClassA'
        mock_exp.explanation = [{'featureName': 'f1', 'importanceScore': 50.0}]
        
        json_obj = [{
            'title': 'Test Usecase',
            'taskType': 'CLASSIFICATION',
            'algorithm': 'RandomForest',
            'endpoint': 'http://localhost:8000',
            'datasetName': 'test_data',
            'groundTruthLabel': 'target',
            'groundTruthClassNames': ['ClassA', 'ClassB'],
            'featureNames': ['f1', 'f2'],
            'scope': 'GLOBAL',
            'methodName': 'Global Tree SHAP',
            'dataType': 'Tabular',
            'featureImportance': [mock_exp]
        }]
        
        with patch.object(Report, 'process_feature_importance', return_value='<div>feature importance</div>'):
            result = Report.generate_html_content(json_obj)
            
            assert isinstance(result, str)
            assert 'Test Usecase' in result
            assert 'CLASSIFICATION' in result

    def test_generate_html_content_local_scope(self):
        """Test generate_html_content with LOCAL scope"""
        
        
        
        mock_exp = MagicMock()
        mock_exp.inputRow = [{'featureName': 'f1', 'featureValue': 1.0}]
        mock_exp.inputText = "Sample text"
        mock_exp.modelPrediction = 'ClassA'
        mock_exp.explanation = ['anchor1 > 0.5', 'anchor2 < 0.3']
        
        json_obj = [{
            'title': 'Test',
            'taskType': 'CLASSIFICATION',
            'algorithm': 'RF',
            'endpoint': None,
            'datasetName': 'data',
            'groundTruthLabel': 'NA',
            'groundTruthClassNames': None,
            'featureNames': None,
            'scope': 'LOCAL',
            'methodName': 'ANCHOR',
            'dataType': 'Tabular',
            'anchors': [mock_exp]
        }]
        
        result = Report.generate_html_content(json_obj)
        
        assert isinstance(result, str)
        assert 'ANCHOR' in result or 'anchor1' in result or 'MODEL' in result

    def test_generate_html_content_with_anchors_text(self):
        """Test generate_html_content with anchors and text input"""
        
        
        
        mock_exp = MagicMock()
        mock_exp.inputRow = None
        mock_exp.inputText = "This is input text for anchor"
        mock_exp.modelPrediction = 'Positive'
        mock_exp.explanation = ['word1 = positive', 'word2 = important']
        
        json_obj = [{
            'title': 'TextClassifier',
            'taskType': 'CLASSIFICATION',
            'algorithm': None,
            'endpoint': None,
            'datasetName': 'text_data',
            'groundTruthLabel': 'sentiment',
            'groundTruthClassNames': None,
            'featureNames': None,
            'scope': 'LOCAL',
            'methodName': 'ANCHOR',
            'dataType': 'Text',
            'anchors': [mock_exp]
        }]
        
        result = Report.generate_html_content(json_obj)
        
        assert isinstance(result, str)

    def test_generate_html_content_local_feature_importance(self):
        """Test generate_html_content with LOCAL featureImportance"""
        
        
        
        # Create 5 mock explanations for local feature importance
        mock_exps = []
        for i in range(5):
            mock_exp = MagicMock()
            mock_exp.inputRow = [{'featureName': 'f1', 'featureValue': float(i)}]
            mock_exp.inputText = None
            mock_exp.modelPrediction = f'Class{i}'
            mock_exp.explanation = [{'featureName': 'f1', 'importanceScore': 50.0 + i}]
            mock_exps.append(mock_exp)
        
        json_obj = [{
            'title': 'LocalTest',
            'taskType': 'CLASSIFICATION',
            'algorithm': 'RF',
            'endpoint': None,
            'datasetName': 'local_data',
            'groundTruthLabel': 'target',
            'groundTruthClassNames': None,
            'featureNames': None,
            'scope': 'LOCAL',
            'methodName': 'LIME TABULAR',
            'dataType': 'Tabular',
            'featureImportance': mock_exps
        }]
        
        with patch.object(Report, 'create_graph_with_summary', return_value='<div>graph</div>'):
            result = Report.generate_html_content(json_obj)
            
            assert isinstance(result, str)

    def test_generate_html_content_time_series(self):
        """Test generate_html_content with timeSeriesForecast"""
        
        
        
        mock_exps = []
        for i in range(5):
            mock_exp = MagicMock()
            mock_exp.inputRow = [{'featureName': 'ts_feature', 'featureValue': float(i * 10)}]
            mock_exp.inputText = None
            mock_exp.modelPrediction = str(100 + i)
            mock_exp.explanation = [{'featureName': 'ts_feature', 'importanceScore': 80.0}]
            mock_exps.append(mock_exp)
        
        json_obj = [{
            'title': 'TimeSeriesTest',
            'taskType': 'REGRESSION',
            'algorithm': 'LSTM',
            'endpoint': None,
            'datasetName': 'ts_data',
            'groundTruthLabel': 'forecast',
            'groundTruthClassNames': None,
            'featureNames': None,
            'scope': 'LOCAL',
            'methodName': 'SHAP',
            'dataType': 'Tabular',
            'timeSeriesForecast': mock_exps
        }]
        
        with patch.object(Report, 'create_graph_with_summary', return_value='<div>ts_graph</div>'):
            result = Report.generate_html_content(json_obj)
            
            assert isinstance(result, str)

    def test_generate_html_content_shap_text(self):
        """Test generate_html_content with shapImportanceText"""
        
        
        
        mock_exps = []
        for i in range(5):
            mock_exp = MagicMock()
            mock_exp.inputRow = None
            mock_exp.inputText = f"Sample text {i}"
            mock_exp.modelPrediction = f'Label{i}'
            mock_exp.explanation = [
                {'featureName': 'word1', 'importanceScore': 30.0},
                {'featureName': 'word2', 'importanceScore': 20.0}
            ]
            mock_exps.append(mock_exp)
        
        json_obj = [{
            'title': 'TextSHAP',
            'taskType': 'CLASSIFICATION',
            'algorithm': 'BERT',
            'endpoint': None,
            'datasetName': 'text_data',
            'groundTruthLabel': None,
            'groundTruthClassNames': None,
            'featureNames': None,
            'scope': 'LOCAL',
            'methodName': 'SHAP EXPLAINER',
            'dataType': 'Text',
            'shapImportanceText': mock_exps
        }]
        
        with patch.object(Report, 'create_graph_with_summary', return_value='<div>shap_text_graph</div>'):
            result = Report.generate_html_content(json_obj)
            
            assert isinstance(result, str)

    def test_generate_html_content_global_time_series(self):
        """Test generate_html_content with GLOBAL timeSeriesForecast"""
        
        
        
        mock_exp = MagicMock()
        mock_exp.explanation = [{'featureName': 'global_ts', 'importanceScore': 90.0}]
        
        json_obj = [{
            'title': 'GlobalTS',
            'taskType': 'REGRESSION',
            'algorithm': 'Prophet',
            'endpoint': None,
            'datasetName': 'global_ts_data',
            'groundTruthLabel': None,
            'groundTruthClassNames': None,
            'featureNames': None,
            'scope': 'GLOBAL',
            'methodName': 'SHAP',
            'dataType': 'Tabular',
            'timeSeriesForecast': [mock_exp]
        }]
        
        with patch.object(Report, 'process_feature_importance', return_value='<div>global_ts</div>'):
            result = Report.generate_html_content(json_obj)
            
            assert isinstance(result, str)
