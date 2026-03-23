import os
import io
import json
import csv
import types
import pickle
import pandas as pd
import numpy as np
import builtins
from pathlib import Path

import pytest

from src.service import defence as defence_mod
from src.service.defence import Defence
from src.service.utility import Utility as UT


class DummyXGBClassifier:
    def fit(self, X, y):
        self.fitted_ = True
        return self

class DummyLogReg:
    def fit(self, X, y):
        self.fitted_ = True
        return self
    def predict(self, X):
        # Predict constant 0 for simplicity
        return np.zeros(len(X), dtype=int)


def _write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow(r)


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    # Point UT.getcurrentDirectory to tmp_path
    monkeypatch.setattr(UT, 'getcurrentDirectory', lambda: str(tmp_path))
    base = tmp_path / 'database'
    for d in ['data', 'model', 'payload', 'report', 'cacheMemory']:
        (base / d).mkdir(parents=True, exist_ok=True)
    return base


@pytest.fixture()
def fast_pickle_dump(monkeypatch):
    def _dump(obj, fh):
        try:
            fh.write(b'OK')
        except TypeError:
            # If opened text mode accidentally
            fh.write('OK')
    monkeypatch.setattr(pickle, 'dump', _dump)


def test_generateDenfenseModel_creates_model(tmp_db, monkeypatch, fast_pickle_dump):
    # Arrange minimal payload/data
    model_name = 'm1'
    folder = 'rep1'
    (tmp_db / 'report' / folder).mkdir(parents=True, exist_ok=True)

    # payload json
    payload_txt = tmp_db / 'payload' / f'{model_name}.txt'
    payload_txt.write_text(json.dumps({'groundTruthClassLabel': 'label'}))

    # original data
    data_csv = tmp_db / 'data' / 'orig.csv'
    rows = [
        ['f1','f2','label'],
        [1,2,0],
        [2,1,1],
        [3,0,0],
    ]
    _write_csv(str(data_csv), rows)

    # adversarial data: include two extra trailing columns to be dropped
    adv_csv = tmp_db / 'data' / 'adv.csv'
    rows_adv = [
        ['f1','f2','label','extra1','extra2'],
        [1,2,1,0.1, True],
        [2,1,1,0.2, True],
    ]
    _write_csv(str(adv_csv), rows_adv)

    # Speed: replace heavy XGBClassifier
    monkeypatch.setattr(defence_mod, 'XGBClassifier', DummyXGBClassifier)

    payload = {
        'modelName': model_name,
        'folderName': folder,
        'data_path': str(data_csv),
        'adversarial_path': str(adv_csv),
    }

    # Act
    Defence.generateDenfenseModel(payload)

    # Assert: model pickle written in report folder
    out = tmp_db / 'report' / folder / 'DefenseModel.pkl'
    assert out.exists()


def test_generateCombinedDenfenseModel2_end_to_end(tmp_db, monkeypatch, fast_pickle_dump):
    # Prepare report path with one original and two attack csvs
    report_path = tmp_db / 'report' / 'combined2'
    report_path.mkdir(parents=True, exist_ok=True)

    # original dataset named by dataFileName
    orig = [
        ['a','b','label'],
        [1,2,0],
        [3,4,1],
    ]
    _write_csv(str(report_path / 'orig.csv'), orig)

    # attack csvs: last column is boolean success; include two trailing columns to be dropped
    att1 = [
        ['a','b','label','pred','success','score'],
        [1,2,1,1, True, 0.9],
        [3,4,0,0, False, 0.1],
    ]
    _write_csv(str(report_path / 'attack1.csv'), att1)

    att2 = [
        ['a','b','label','pred','success','score'],
        [5,6,1,1, True, 0.8],
        [7,8,1,1, True, 0.7],
    ]
    _write_csv(str(report_path / 'attack2.csv'), att2)

    # Use fast classifier
    monkeypatch.setattr(defence_mod, 'XGBClassifier', DummyXGBClassifier)

    payload = {
        'payloadData': {'groundTruthClassLabel': 'label'},
        'report_path': str(report_path),
        'dataFileName': 'orig',
        'modelName': 'm1',
    }

    # Act
    Defence.generateCombinedDenfenseModel2(payload)

    # Assert
    assert (report_path / 'DefenseModel.pkl').exists()


def test_generateCombinedDenfenseModel_metrics(tmp_db, monkeypatch, fast_pickle_dump):
    # Prepare report path with original and one attack csv
    report_path = tmp_db / 'report' / 'combined'
    report_path.mkdir(parents=True, exist_ok=True)

    # original
    orig = [
        ['x','y','label'],
        [0,0,0],
        [1,0,1],
        [0,1,0],
    ]
    _write_csv(str(report_path / 'data.csv'), orig)

    # attack: last three are meta columns where -2 is target, -1 unused
    att = [
        ['x','y','c1','target','flag','score'],
        [0,0,0,0, True, 0.5],
        [1,0,0,1, True, 0.6],
        [0,1,0,0, False, 0.2],
    ]
    _write_csv(str(report_path / 'attack.csv'), att)

    # Speed: dummy LogisticRegression and simple metrics to avoid sklearn type edge-cases
    monkeypatch.setattr(defence_mod, 'LogisticRegression', DummyLogReg)
    monkeypatch.setattr(defence_mod, 'accuracy_score', lambda y_true, y_pred: 1.0)
    monkeypatch.setattr(defence_mod, 'confusion_matrix', lambda y_true, y_pred: np.array([[1,0],[0,1]]))
    monkeypatch.setattr(defence_mod, 'classification_report', lambda y_true, y_pred, output_dict=True: {'accuracy':1.0})

    payload = {
        'payloadData': {'groundTruthClassLabel': 'label'},
        'report_path': str(report_path),
        'dataFileName': 'data',
    }

    conf_mat, class_rep, attack_acc = Defence.generateCombinedDenfenseModel(payload)

    # Basic sanity assertions
    assert conf_mat.shape[0] == conf_mat.shape[1]
    assert isinstance(class_rep, dict)
    assert any(k in attack_acc for k in ['attack.csv'])
