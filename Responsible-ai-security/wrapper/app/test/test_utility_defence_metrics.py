import os
import json
import numpy as np
import pandas as pd
import pytest

from src.service import utility as ut_mod
from src.service.utility import Utility


class _DummyModel:
    def predict(self, X):
        # Return ones for any shape
        return np.ones((len(X),), dtype=int)


def _write_payload(tmp_path, model_name='M'):
    base = tmp_path / 'database' / 'payload'
    base.mkdir(parents=True, exist_ok=True)
    data = {
        'groundTruthClassLabel': 'y',
        'dataType': 'Tabular',
        'targetClassifier': 'Sklearn',
    }
    (base / f'{model_name}.txt').write_text(json.dumps(data), encoding='utf-8')
    return str(tmp_path)


def test_generate_defence_accuracy(monkeypatch, tmp_path):
    # Point Utility.getcurrentDirectory to tmp workspace and stub model loader
    monkeypatch.setattr(ut_mod.Utility, 'getcurrentDirectory', lambda: _write_payload(tmp_path))
    monkeypatch.setattr(ut_mod.Utility, 'safe_load_from_file', lambda f: _DummyModel())

    # Prepare folder with a dummy model and CSV
    folder = tmp_path / 'database' / 'report'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'M.pkl').write_bytes(b'model')

    # CSV columns: y, f1, f2, metaA, metaB, success (last col True ensures filtering)
    df = pd.DataFrame({
        'y': [0, 1, 1],
        'f1': [1, 2, 3],
        'f2': [0, 1, 1],
        'metaA': [9, 9, 9],
        'metaB': [8, 8, 8],
        'success': [True, True, True],
    })
    csv_path = folder / 'Boundary.csv'
    df.to_csv(csv_path, index=False)

    acc = Utility.generateDefenceAccuracy({'folder_path': str(folder), 'csv_path': str(csv_path), 'modelName': 'M'})
    assert isinstance(acc, float) and acc >= 0.0


def test_confusion_matrix(monkeypatch, tmp_path):
    # Point Utility.getcurrentDirectory to tmp workspace and stub model loader
    monkeypatch.setattr(ut_mod.Utility, 'getcurrentDirectory', lambda: _write_payload(tmp_path))
    monkeypatch.setattr(ut_mod.Utility, 'safe_load_from_file', lambda f: _DummyModel())

    folder = tmp_path / 'database' / 'report'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'M.pkl').write_bytes(b'model')

    # Two CSVs with y as ground truth and extra trailing columns to be dropped
    df1 = pd.DataFrame({
        'y': [0, 1],
        'f1': [0, 1],
        'f2': [0, 1],
        'metaA': [5, 5],
        'metaB': [6, 6],
        'flag': [True, True],
    })
    df2 = pd.DataFrame({
        'y': [1, 0],
        'f1': [2, 3],
        'f2': [1, 0],
        'metaA': [7, 7],
        'metaB': [8, 8],
        'flag': [True, True],
    })
    (folder / 'Boundary.csv').write_text(df1.to_csv(index=False), encoding='utf-8')
    (folder / 'Deepfool.csv').write_text(df2.to_csv(index=False), encoding='utf-8')

    cm = Utility.confusionMatrix({'folder_path': str(folder), 'modelName': 'M'})
    assert isinstance(cm, list) and len(cm) == 4
