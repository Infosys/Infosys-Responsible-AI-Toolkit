import os
import shutil
import time
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


def test_graphForAttack_tabular_evasion_pie_html():
    folder = _dir("attack_tab_evasion")
    try:
        # Rows where gt != prediction should be counted as Successful for Evasion
        pd.DataFrame({'gt': [0, 1, 1], 'prediction': [1, 1, 0]}).to_csv(os.path.join(folder, 'Attack_Samples.csv'), index=False)
        payload = {
            'type': 'Tabular',
            'folder_path': folder,
            'attackName': 'FastGradientMethod',
            'target': 'gt',
        }
        html = Utility.graphForAttack(payload)
        assert isinstance(html, str) and 'graph-image-csv' in html
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def test_graphForAttack_tabular_inference_pie_html():
    folder = _dir("attack_tab_inference")
    try:
        # Rows where gt == prediction counted as Successful for Inference
        pd.DataFrame({'gt': [0, 1, 1], 'prediction': [0, 0, 1]}).to_csv(os.path.join(folder, 'Attack_Samples.csv'), index=False)
        payload = {
            'type': 'Tabular',
            'folder_path': folder,
            'attackName': 'AttributeInference',
            'target': 'gt',
        }
        html = Utility.graphForAttack(payload)
        assert isinstance(html, str) and 'graph-image-csv' in html
    finally:
        shutil.rmtree(folder, ignore_errors=True)
