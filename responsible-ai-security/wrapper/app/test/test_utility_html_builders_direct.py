import datetime as dt
from src.service.utility import Utility


def test_htmlCssContent_tabular_and_image_have_style_and_classes():
    tab_css = Utility.htmlCssContent({'model_metaData': {'dataType': 'Tabular'}})
    img_css = Utility.htmlCssContent({'model_metaData': {'dataType': 'Image'}})
    assert isinstance(tab_css, str) and '<style>' in tab_css and 'attack-summary' in tab_css
    assert isinstance(img_css, str) and '<style>' in img_css and 'attack-summary' in img_css


def test_htmlContent_tabular_basic_sections_and_optional_graph():
    payload = {
        'modelName': 'ModelX',
        'model_metaData': {
            'dataType': 'Tabular',
            'useModelApi': False,
            'modelEndPoint': '-',
            'groundTruthClassNames': ['Benign', 'Adversarial'],
            'targetClassifier': 'LogisticRegression',
            'groundTruthClassLabel': ['0', '1'],
        },
        'reportTime': dt.datetime.now(),
        'rows': '<tr><td>Evasion</td><td>FastGradientMethod</td><td>T</td><td>90%</td></tr>',
    }
    html = Utility.htmlContent(payload)
    assert 'MODEL ROBUSTNESS ASSESSMENT REPORT' in html and 'ATTACK SUMMARY' in html

    # With graph embedded
    payload['graph'] = 'ZmFrZV9iYXNlNjQ='
    html_with_graph = Utility.htmlContent(payload)
    assert 'graph-image' in html_with_graph


def test_htmlContent_image_basic_sections():
    payload = {
        'modelName': 'ModelY',
        'model_metaData': {
            'dataType': 'Image',
            'targetDataType': 'Image',
            'useModelApi': False,
            'modelEndPoint': '-',
            'targetClassifier': 'ResNet',
        },
        'reportTime': dt.datetime.now(),
        'rows': '<tr><td>Evasion</td><td>FastGradientMethod</td><td>T</td><td>90%</td></tr>',
    }
    html = Utility.htmlContent(payload)
    assert 'MODEL ROBUSTNESS ASSESSMENT REPORT' in html and 'ATTACK SUMMARY' in html


def test_htmlMitigationContent_tabular_contains_heading_and_table():
    payload = {
        'model_metaData': {'dataType': 'Tabular'},
        'mitigation_row': '<tr><td>Evasion</td><td>Boundary</td><td>0.88</td></tr>',
    }
    html = Utility.htmlMitigationContent(payload)
    assert 'MITIGATION SUMMARY' in html and '<table>' in html


def test_htmlAppendixContent_tabular_and_image_have_appendix_and_classifier():
    tab_html = Utility.htmlAppendixContent({'model_metaData': {'dataType': 'Tabular'}})
    img_html = Utility.htmlAppendixContent({'model_metaData': {'dataType': 'Image'}})
    assert 'APPENDIX' in tab_html and 'Classifier' in tab_html
    assert 'APPENDIX' in img_html and 'Classifier' in img_html
