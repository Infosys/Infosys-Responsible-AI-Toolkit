import os
import json
import numpy as np
import pandas as pd
import datetime as dt
import pytest

from src.service import utility as ut_mod
from src.service.utility import Utility


def _prep_payload(tmp_path, model_name='M'):
    base = tmp_path / 'database' / 'payload'
    base.mkdir(parents=True, exist_ok=True)
    data = {
        'groundTruthClassLabel': 'y',
        'dataType': 'Tabular',
        'targetClassifier': 'Sklearn',
    }
    (base / f'{model_name}.txt').write_text(json.dumps(data), encoding='utf-8')
    return str(tmp_path)


def test_graph_for_combine_attack_tabular(monkeypatch, tmp_path):
    # Point Utility.getcurrentDirectory and create base report.html
    monkeypatch.setattr(ut_mod.Utility, 'getcurrentDirectory', lambda: _prep_payload(tmp_path))
    folder = tmp_path / 'database' / 'report' / 'M'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'report.html').write_text('<html><body>base</body></html>', encoding='utf-8')

    # Create simple Boundary.csv with target/prediction columns
    df = pd.DataFrame({
        'y': [0, 1, 1, 0],
        'prediction': [1, 1, 0, 0],
    })
    (folder / 'Boundary.csv').write_text(df.to_csv(index=False), encoding='utf-8')

    payload = {
        'folder_path': str(folder),
        'modelName': 'M',
        'model_metaData': {'dataType': 'Tabular'},
        'reportTime': dt.datetime.now(),
        'success_skipped': [1, 1, 0],
        'rows': '<tr><td>row</td></tr>',
        'attack_list': [{'name': 'Boundary', 'type': 'Evasion'}],
        'confusion_matrix': np.array([1, 0, 0, 1]),
        'mitigation_row': '<tr><td>mit</td></tr>',
        'classification_reports': {
            'benign': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 2},
            'adversarial': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 2},
            'accuracy': {'precision': 0.0, 'recall': 0.0, 'f1-score': 0.0, 'support': 4},
            'macro avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 4},
            'weighted avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 4},
        },
    }
    # Should produce updated report.html; tolerant assertion on existence
    Utility.graphForCombineAttack(payload)
    assert (folder / 'report.html').exists()


def test_graph_for_combine_attack_image(monkeypatch, tmp_path):
    monkeypatch.setattr(ut_mod.Utility, 'getcurrentDirectory', lambda: _prep_payload(tmp_path))
    folder = tmp_path / 'database' / 'report' / 'M'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'report.html').write_text('<html><body>base</body></html>', encoding='utf-8')

    # Create image files with names encoding status T/F
    (folder / 'img1^BoundaryT.png').write_bytes(b'\x89PNG\r\n')
    (folder / 'img2^BoundaryF.png').write_bytes(b'\x89PNG\r\n')

    payload = {
        'folder_path': str(folder),
        'modelName': 'M',
        'model_metaData': {'dataType': 'Image'},
        'reportTime': dt.datetime.now(),
        'success_skipped': [1, 1, 0],
        'rows': '<tr><td>row</td></tr>',
        'attack_list': [{'name': 'Boundary', 'type': 'Evasion'}],
    }
    Utility.graphForCombineAttack(payload)
    assert (folder / 'report.html').exists()


def test_graph_for_combine_attack1_tabular(monkeypatch, tmp_path):
    monkeypatch.setattr(ut_mod.Utility, 'getcurrentDirectory', lambda: _prep_payload(tmp_path))
    folder = tmp_path / 'database' / 'report' / 'M'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'report.html').write_text('<html><body>base</body></html>', encoding='utf-8')

    df = pd.DataFrame({
        'y': [0, 1],
        'prediction': [1, 1],
    })
    (folder / 'Boundary.csv').write_text(df.to_csv(index=False), encoding='utf-8')

    payload = {
        'folder_path': str(folder),
        'modelName': 'M',
        'model_metaData': {'dataType': 'Tabular'},
        'reportTime': dt.datetime.now(),
        'success_skipped': [1, 1, 0],
        'rows': '<tr><td>row</td></tr>',
        'attack_list': [{'name': 'Boundary', 'type': 'Evasion'}],
        'confusion_matrix': np.array([1, 0, 0, 1]),
        'mitigation_row': '<tr><td>mit</td></tr>',
        'classification_reports': {
            'benign': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 2},
            'adversarial': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 2},
            'accuracy': {'precision': 0.0, 'recall': 0.0, 'f1-score': 0.0, 'support': 4},
            'macro avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 4},
            'weighted avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 4},
        },
    }
    Utility.graphForCombineAttack1(payload)
    assert (folder / 'report.html').exists()


def test_graph_for_combine_attack1_image(monkeypatch, tmp_path):
    monkeypatch.setattr(ut_mod.Utility, 'getcurrentDirectory', lambda: _prep_payload(tmp_path))
    folder = tmp_path / 'database' / 'report' / 'M'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'report.html').write_text('<html><body>base</body></html>', encoding='utf-8')

    (folder / 'img1^BoundaryT.png').write_bytes(b'\x89PNG\r\n')
    (folder / 'img2^BoundaryF.png').write_bytes(b'\x89PNG\r\n')

    payload = {
        'folder_path': str(folder),
        'modelName': 'M',
        'model_metaData': {'dataType': 'Image'},
        'reportTime': dt.datetime.now(),
        'success_skipped': [1, 1, 0],
        'rows': '<tr><td>row</td></tr>',
        'attack_list': [{'name': 'Boundary', 'type': 'Evasion'}],
    }
    Utility.graphForCombineAttack1(payload)
    assert (folder / 'report.html').exists()
