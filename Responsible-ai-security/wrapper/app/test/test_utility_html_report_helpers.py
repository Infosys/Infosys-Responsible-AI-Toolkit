import os
import io
import json
import numpy as np
import pandas as pd
import datetime as dt
import pytest

from src.service import utility as ut_mod
from src.service.utility import Utility


def test_graph_for_mitigation_dataframe():
    # classification report dict similar to typical sklearn output
    cls_rep = {
        'benign': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 2},
        'adversarial': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 2},
        'accuracy': {'precision': 0.0, 'recall': 0.0, 'f1-score': 0.0, 'support': 4},
        'macro avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 4},
        'weighted avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 4},
    }
    cm = np.array([1, 1, 1, 1])  # tn, fp, fn, tp
    df = Utility.graphForMitigation({'model_metaData': {'dataType': 'Tabular'}, 'confusion_matrix': cm, 'classification_reports': cls_rep})
    assert hasattr(df, 'loc') and set(df.columns) >= {'precision','recall','f1-score','specificity','balance accuracy','FPR','support'}


def test_html_css_content_and_report_tabular():
    css = Utility.htmlCssContent({'model_metaData': {'dataType': 'Tabular'}})
    assert isinstance(css, str) and '<style>' in css

    # Minimal payload content for htmlContentReport Tabular
    html = Utility.htmlContentReport({
        'type': 'Tabular',
        'attackName': 'Boundary',
        'graph_html': '<div>graph</div>',
        'attack_status_row': '<tr><td>1</td></tr>',
        'column_graph_data': '<div>columns</div>',
    })
    assert isinstance(html, str) and 'Boundary_Attack' in html and 'Attack Status' in html


def test_html_content_report_image_variants():
    html1 = Utility.htmlContentReport({
        'type': 'Image',
        'attackName': 'Boundary',
        'graph_html': '<img />',
        'attack_ipop_row': '<tr><td>img</td></tr>',
    })
    assert isinstance(html1, str) and 'Attack Analysis' in html1

    html2 = Utility.htmlContentReport({
        'type': 'Image',
        'attackName': 'Boundary',
        'graph_html': '',
        'attack_ipop_row': '<tr><td>img</td></tr>',
    })
    assert isinstance(html2, str) and 'Attack Analysis' in html2


def test_html_to_pdf_with_watermark_monkeypatched(tmp_path, monkeypatch):
    # Prepare folder and a simple html file
    folder = tmp_path
    (folder / 'report.html').write_text('<html><body>ok</body></html>', encoding='utf-8')

    # Stub pdfkit.from_file to write a simple PDF-like file
    class _StubPdfKit:
        @staticmethod
        def from_file(html_path, output_path, options=None):
            with open(output_path, 'wb') as f:
                f.write(b'%PDF-1.4\n%stub')
            return True
    monkeypatch.setattr(ut_mod, 'pdfkit', _StubPdfKit)

    # Stub reportlab.canvas.Canvas to create a watermark file
    class _StubCanvas:
        def __init__(self, path, pagesize=None):
            self._path = path
        def setFont(self, *args, **kwargs):
            pass
        def setFillColorRGB(self, *args, **kwargs):
            pass
        def setFillAlpha(self, *args, **kwargs):
            pass
        def rotate(self, *args, **kwargs):
            pass
        def drawString(self, *args, **kwargs):
            pass
        def save(self):
            with open(self._path, 'wb') as f:
                f.write(b'%PDF-1.4\n%watermark')
    # Patch the symbol in module scope
    monkeypatch.setattr(ut_mod, 'canvas', type('C', (), {'Canvas': _StubCanvas}))

    # Stub PyPDF2 reader/writer
    class _StubPage:
        def merge_page(self, other):
            pass
    class _StubReader:
        def __init__(self, f):
            self.pages = [_StubPage()]
    class _StubWriter:
        def __init__(self):
            self._pages = []
        def add_page(self, page):
            self._pages.append(page)
        def write(self, f):
            f.write(b'%PDF-1.4\n%merged')
    monkeypatch.setattr(ut_mod, 'PdfReader', _StubReader)
    monkeypatch.setattr(ut_mod, 'PdfWriter', _StubWriter)

    Utility.htmlToPdfWithWatermark({'folder_path': str(folder)})
    # report.pdf should be present and watermark removed
    assert (folder / 'report.pdf').exists()
    assert not (folder / 'watermark.pdf').exists()
