import numpy as np
import pandas as pd
import datetime as dt

from src.service.utility import Utility


def test_date_time_format_none_and_value():
    s1 = Utility.dateTimeFormat(None)
    assert isinstance(s1, str) and 'UTC' in s1
    now = dt.datetime.now()
    s2 = Utility.dateTimeFormat(now)
    assert isinstance(s2, str) and any(m in s2 for m in ['AM', 'PM'])


def test_combine_list_evasion_and_inference():
    attack = np.array([[0, 0], [1, 1]])
    target = np.array([[1, 0], [0, 1]])
    pred = np.array([0, 1])

    e_evasion, f_evasion = Utility.combineList({
        'attack_data': attack,
        'target_data': target,
        'prediction_data': pred,
        'type': 'Evasion',
    })
    assert isinstance(e_evasion, list) and isinstance(f_evasion, list)
    assert e_evasion[0][-1] in ['True', 'False']

    e_infer, f_infer = Utility.combineList({
        'attack_data': attack,
        'target_data': target,
        'prediction_data': pred,
        'type': 'Inference',
    })
    assert isinstance(e_infer, list) and isinstance(f_infer, list)


def test_check_list_with_dummy_model():
    class DummyModel:
        def predict(self, arr):
            # arr shape (1, n); return two-class logits
            s = int(np.sum(arr[0]))
            return np.array([[1, 0]]) if (s % 2 == 0) else np.array([[0, 1]])

    model = DummyModel()
    x = np.array([[0, 0], [1, 0], [2, 0]])
    adv = np.array([[0, 1], [1, 1], [2, 1]])

    out = Utility.checkList({'model': model, 'original_data': x, 'adversial_data': adv})
    assert isinstance(out, list) and len(out) >= 1
