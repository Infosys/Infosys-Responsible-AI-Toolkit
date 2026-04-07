import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')

from src.service.utility import Utility


def test_graphForAttack_image_branch(tmp_path):
    # Prepare minimal image-like arrays wrapped as expected
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    adv = np.zeros((10, 10, 3), dtype=np.uint8)
    key = 'img.png'
    payload = {
        'type': 'Image',
        'folder_path': str(tmp_path),
        'top_keys': [key],
        'attackDataList': {
            key: [None, np.array([img]), np.array([adv]), 'labelA', 'labelB']
        }
    }
    html = Utility.graphForAttack(payload)
    assert html is not None and len(html) > 0


def test_graphForAttackColumn_nonzero_mae_tabular(tmp_path):
    # Create original and adversarial CSVs with non-zero MAE in first column
    orig = pd.DataFrame({'Feature1': [1.0, 2.0, 3.0, 4.0], 'Target': [0, 1, 0, 1]})
    adv = pd.DataFrame({'Feature1': [1.2, 2.1, 2.7, 3.9], 'c2': [0, 0, 0, 0], 'c3': [0, 0, 0, 0], 'c4': [0, 0, 0, 0]})
    orig_path = tmp_path / 'original.csv'
    adv_path = tmp_path / 'adversarial.csv'
    orig.to_csv(orig_path, index=False)
    adv.to_csv(adv_path, index=False)

    payload = {
        'type': 'Tabular',
        'report_path': str(tmp_path),
        'adversarial_data_path': str(adv_path),
        'original_data_path': str(orig_path),
        'attackName': 'FastGradientMethod'
    }
    html = Utility.graphForAttackColumn(payload)
    assert html is not None
