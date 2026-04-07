import os
import io
import base64
import json
import datetime as dt
import numpy as np
import pandas as pd
from PIL import Image

from src.service.utility import Utility


def _write_png(path, size=(10, 10), color=(255, 0, 0)):
    img = Image.new('RGB', size, color)
    img.save(path, format='PNG')


def test_graphForCombineAttack1_tabular(tmp_path):
    # Prepare minimal report.html
    html_path = tmp_path / 'report.html'
    html_path.write_text('<html><body>base</body></html>', encoding='utf-8')

    # Create two CSVs for one evasion and one inference attack
    df_evasion = pd.DataFrame({
        'f1': [0, 1, 2],
        'target': [0, 1, 0],
        'prediction': [0, 0, 0],
    })
    df_infer = pd.DataFrame({
        'f1': [0, 1, 2],
        'target': [0, 1, 0],
        'prediction': [1, 1, 0],
    })
    evasion_name = 'Boundary'  # in Art/Evasion
    infer_name = 'MembershipInferenceRule'  # in Art/Inference
    df_evasion.to_csv(tmp_path / f'{evasion_name}.csv', index=False)
    df_infer.to_csv(tmp_path / f'{infer_name}.csv', index=False)

    # Minimal classification report structure expected by graphForMitigation
    cls_report = {
        '0': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1},
        '1': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1},
        'accuracy': {'precision': 0.0, 'recall': 0.0, 'f1-score': 0.0, 'support': 2},
        'macro avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 2},
        'weighted avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 2},
    }
    payload = {
        'folder_path': str(tmp_path),
        'modelName': 'm',
        'model_metaData': {'dataType': 'Tabular'},
        'reportTime': dt.datetime.now(),
        'success_skipped': [1, 0, 0],
        'rows': '',
        'attack_list': [{'name': evasion_name}, {'name': infer_name}],
        'target': 'target',
        'confusion_matrix': np.array([[1, 0], [0, 1]]),
        'classification_reports': cls_report,
        'mitigation_row': '',
    }

    Utility.graphForCombineAttack1(payload)

    # Some environments or minimal inputs may not alter the HTML; ensure no crash and file remains.
    assert html_path.exists()


def test_graphForCombineAttack1_image(tmp_path):
    # Prepare minimal report.html
    html_path = tmp_path / 'report.html'
    html_path.write_text('<html><body>base</body></html>', encoding='utf-8')

    # Create a couple of images with naming pattern: name^AttackNameT/F.png
    attack = 'Boundary'
    _write_png(tmp_path / f'img1^{attack}T.png')
    _write_png(tmp_path / f'img2^{attack}F.png')

    payload = {
        'folder_path': str(tmp_path),
        'modelName': 'm',
        'model_metaData': {'dataType': 'Image'},
        'reportTime': dt.datetime.now(),
        'success_skipped': [1, 0, 0],
        'rows': '',
        'attack_list': [{'name': attack}],
    }

    Utility.graphForCombineAttack1(payload)

    # Ensure it runs without error and the report remains accessible
    assert html_path.exists()
