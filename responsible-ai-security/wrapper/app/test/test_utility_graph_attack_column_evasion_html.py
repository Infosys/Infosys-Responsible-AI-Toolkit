import os
import time
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')

from src.service.utility import Utility


def _dir(prefix):
    base = os.path.join(os.getcwd(), prefix)
    if not os.path.exists(base):
        os.makedirs(base)
    folder = os.path.join(base, str(time.time()).replace(".", "_"))
    os.makedirs(folder)
    return folder


def test_graphForAttackColumn_tabular_evasion_returns_html():
    folder = _dir("attack_column_evasion")
    try:
        # Original with 8 feature columns + target label at end
        orig_cols = [f'c{i}' for i in range(1, 8)] + ['target']
        orig_data = np.arange(1, 9)
        pd.DataFrame([orig_data, orig_data + 1], columns=orig_cols).to_csv(
            os.path.join(folder, 'original.csv'), index=False
        )

        # Adversarial with same 7 feature columns shifted + 3 extra cols to be trimmed
        adv_cols = [f'c{i}' for i in range(1, 8)] + ['x', 'y', 'z']
        adv_data = np.arange(2, 12)
        pd.DataFrame([adv_data, adv_data + 2], columns=adv_cols).to_csv(
            os.path.join(folder, 'adversarial.csv'), index=False
        )

        payload = {
            'type': 'Tabular',
            'report_path': folder,
            'adversarial_data_path': os.path.join(folder, 'adversarial.csv'),
            'original_data_path': os.path.join(folder, 'original.csv'),
            'attackName': 'FastGradientMethod',  # Evasion branch
        }

        html = Utility.graphForAttackColumn(payload)
        assert isinstance(html, str) and 'graph-container' in html and 'img src' in html
    finally:
        # Cleanup
        for fn in os.listdir(folder):
            try:
                os.remove(os.path.join(folder, fn))
            except Exception:
                pass
        try:
            os.rmdir(folder)
        except Exception:
            pass
