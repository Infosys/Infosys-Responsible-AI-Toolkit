import os
import time
import numpy as np
import pandas as pd
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


def _make_csv(path, eq_rows=True):
    # Create simple CSV with target/prediction matching or not
    if eq_rows:
        df = pd.DataFrame({'gt': [0, 1, 1, 0], 'prediction': [0, 1, 1, 0], 'f1': [0.1, 0.2, 0.3, 0.4]})
    else:
        df = pd.DataFrame({'gt': [0, 1, 1, 0], 'prediction': [1, 0, 0, 1], 'f1': [0.1, 0.2, 0.3, 0.4]})
    df.to_csv(path, index=False)


def test_graphForCombineAttack1_tabular_multi_subplot():
    folder = _dir("combine1_tab_multi")
    try:
        # Base report file
        with open(os.path.join(folder, 'report.html'), 'w', encoding='utf-8') as f:
            f.write('<html><body>base</body></html>')

        # >8 attacks to force multiple subplots
        evasion = [
            'FastGradientMethod', 'Deepfool', 'Boundary', 'HopSkipJumpTabular',
            'Square', 'Wasserstein', 'ZerothOrderOptimization', 'ProjectGradientDescentImage'
        ]
        inference = ['AttributeInference', 'MembershipInferenceBlackBox']
        attack_names = evasion + inference  # 10 attacks

        # Write CSVs for each attack with alternating equality
        for i, name in enumerate(attack_names):
            _make_csv(os.path.join(folder, f'{name}.csv'), eq_rows=(i % 2 == 0))

        payload = {
            'folder_path': folder,
            'modelName': 'm',
            'model_metaData': {'dataType': 'Tabular'},
            'reportTime': 'now',
            'success_skipped': [0, 0, 0],
            'rows': '',
            'attack_list': [{'name': n} for n in attack_names],
            'target': 'gt',
            'confusion_matrix': np.array([[2, 0], [0, 2]]),
            'classification_reports': {
                '0': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 2},
                '1': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 2},
                'accuracy': {'precision': 0.0, 'recall': 0.0, 'f1-score': 0.0, 'support': 4},
                'macro avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 4},
                'weighted avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 4},
            },
            'mitigation_row': '<tr><td>Evasion</td><td>FastGradientMethod</td><td>0.95</td></tr>',
        }

        Utility.graphForCombineAttack1(payload)

        # Validate report file remains accessible post-run
        html_path = os.path.join(folder, 'report.html')
        assert os.path.exists(html_path)
    finally:
        # Cleanup folder
        for fn in os.listdir(folder):
            try:
                os.remove(os.path.join(folder, fn))
            except Exception:
                pass
        try:
            os.rmdir(folder)
        except Exception:
            pass
