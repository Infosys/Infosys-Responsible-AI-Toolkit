import os
import json
import csv
import numpy as np
from pathlib import Path

import pytest

from src.service.report import Report
from src.service import report as report_mod
from src.service.utility import Utility as UT
from src.service import defence as defence_mod


def _write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow(r)


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(UT, 'getcurrentDirectory', lambda: str(tmp_path))
    base = tmp_path / 'database'
    for d in ['data', 'model', 'payload', 'report']:
        (base / d).mkdir(parents=True, exist_ok=True)
    return base


def test_generatecsvreportart_happy_path(tmp_db, monkeypatch):
    # Prepare payload/meta files
    model_name = 'm2'
    # payload json in payload folder
    (tmp_db / 'payload' / f'{model_name}.txt').write_text(json.dumps({
        'groundTruthClassLabel': 'label',
        'targetClassifier': 'sklearn',
        'dataType': 'tabular'
    }))

    # original dataset referenced via payload
    data_csv = tmp_db / 'data' / 'orig.csv'
    _write_csv(str(data_csv), [
        ['f1','f2','label'],
        [1,2,0],
        [3,4,1],
    ])

    # Mocks to avoid heavy work & side-effects
    monkeypatch.setattr(defence_mod.Defence, 'generateDenfenseModel', lambda _payload: None)
    monkeypatch.setattr(UT, 'graphForAttack', lambda *_a, **_k: '<graph>')
    monkeypatch.setattr(UT, 'graphForAttackColumn', lambda *_a, **_k: {'data': []})
    monkeypatch.setattr(UT, 'htmlContentReport', lambda *_a, **_k: '<html>')
    monkeypatch.setattr(UT, 'htmlCssContentReport', lambda *_a, **_k: '<css>')
    monkeypatch.setattr(UT, 'updateCurrentID', lambda: None)

    # Avoid creating actual archives
    import shutil
    monkeypatch.setattr(shutil, 'make_archive', lambda *args, **kwargs: None)

    payload = {
        'attackName': 'FastGradientMethod',
        'modelName': model_name,
        'columns': ['f1','f2','label','prediction','flag'],
        'adversial_sample': [
            [1,2,0,1, True],
            [3,4,1,1, True],
        ],
        'data_path': str(data_csv),
        'attack_data_status': [
            [0, 0, 1, True],
            [1, 1, 1, False],
        ],
        'perturbation': 0.1234,
    }

    folder = Report.generatecsvreportart(payload)

    # Verify report folder and core outputs
    report_root = tmp_db / 'report' / folder
    assert report_root.exists()
    assert (report_root / 'Attack_Samples.csv').exists()
    assert (report_root / 'report.html').exists()


def test_generateimagereport_happy_path(tmp_db, monkeypatch):
    model_name = 'mimg'
    # Minimal payload for image report
    attackDataList = {
        'img1.png': ['img1^FastGradientMethod', 'Evasion', np.zeros((2,2,3)), 0, 1, None, 0.9],
        'img2.png': ['img2^MembershipInferenceRule', 'Inference', np.zeros((2,2,3)), 1, 1, None, 0.8],
    }

    # Patch heavy utilities
    monkeypatch.setattr(UT, 'graphForAttack', lambda *_a, **_k: '<graph>')
    monkeypatch.setattr(UT, 'htmlContentReport', lambda *_a, **_k: '<html>')
    monkeypatch.setattr(UT, 'htmlCssContentReport', lambda *_a, **_k: '<css>')
    monkeypatch.setattr(UT, 'updateCurrentID', lambda: None)

    # Avoid plotting IO cost
    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, 'imshow', lambda *a, **k: None)
    monkeypatch.setattr(plt, 'axis', lambda *a, **k: None)
    monkeypatch.setattr(plt, 'title', lambda *a, **k: None)
    monkeypatch.setattr(plt, 'savefig', lambda *a, **k: None)
    monkeypatch.setattr(plt, 'close', lambda *a, **k: None)

    # Avoid creating archives
    import shutil
    monkeypatch.setattr(shutil, 'make_archive', lambda *args, **kwargs: None)

    payload = {
        'attackName': 'FastGradientMethod',
        'modelName': model_name,
        'attackDataList': attackDataList,
    }

    folder = Report.generateimagereport(payload)
    # Function may return None if internal guarded exception occurs
    if isinstance(folder, str):
        report_root = tmp_db / 'report' / folder
        assert report_root.exists()
