from src.service.utility import Utility


def test_htmlCssContent_tabular_and_image():
    css_tab = Utility.htmlCssContent({"model_metaData": {"dataType": "Tabular"}})
    assert isinstance(css_tab, str)
    assert "report-header" in css_tab or "attack-header" in css_tab

    css_img = Utility.htmlCssContent({"model_metaData": {"dataType": "Image"}})
    assert isinstance(css_img, str)
    assert "report-header" in css_img or "attack-header" in css_img


def test_htmlContent_tabular_and_image():
    base_payload = {
        "modelName": "m",
        "reportTime": "now",
        "success_skipped": [2, 1, 1],
        "rows": "<tr></tr>",
        "graph": "AAA",
    }

    tab_html = Utility.htmlContent({
        **base_payload,
        "model_metaData": {
            "dataType": "Tabular",
            "groundTruthClassLabel": "gt",
            "useModelApi": "Yes",
            "modelEndPoint": "http://ep",
            "groundTruthClassNames": ["A", "B"],
            "targetClassifier": "clf",
        },
    })
    assert isinstance(tab_html, str)
    assert "report-container" in tab_html

    img_html = Utility.htmlContent({
        **base_payload,
        "model_metaData": {
            "dataType": "Image",
            "targetDataType": "Image",
            "useModelApi": "Yes",
            "modelEndPoint": "http://ep",
            "targetClassifier": "clf",
        },
    })
    assert isinstance(img_html, str)
    assert "report-container" in img_html


def test_htmlMitigationContent_tabular():
    mit_html = Utility.htmlMitigationContent({
        "modelName": "m",
        "model_metaData": {"dataType": "Tabular"},
        "reportTime": "now",
        "success_skipped": [2, 1, 1],
        "rows": "<tr></tr>",
        "graph": "AAA",
        "confusion_matrix": [[1, 0], [0, 1]],
        "mitigation_row": "<tr></tr>",
    })
    assert isinstance(mit_html, str)
    assert ("classification report" in mit_html.lower()) or ("confusion matrix" in mit_html.lower())
