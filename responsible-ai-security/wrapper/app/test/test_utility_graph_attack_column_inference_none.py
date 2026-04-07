import pandas as pd

from src.service.utility import Utility


def test_graphForAttackColumn_inference_returns_none(tmp_path):
    # Minimal CSVs; function should early-return None for Inference attack
    orig = pd.DataFrame({'Feature1': [1, 2], 'Target': [0, 1]})
    adv = pd.DataFrame({'Feature1': [1.1, 1.9], 'c2': [0, 0], 'c3': [0, 0], 'c4': [0, 0]})
    orig_path = tmp_path / 'original.csv'
    adv_path = tmp_path / 'adversarial.csv'
    orig.to_csv(orig_path, index=False)
    adv.to_csv(adv_path, index=False)

    payload = {
        'type': 'Tabular',
        'report_path': str(tmp_path),
        'adversarial_data_path': str(adv_path),
        'original_data_path': str(orig_path),
        'attackName': 'MembershipInferenceRule'
    }
    html = Utility.graphForAttackColumn(payload)
    assert html is None
