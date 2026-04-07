import os
import shutil
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')

from src.service.utility import Utility


def _tmp_folder(prefix):
    base = os.path.join(os.getcwd(), prefix)
    if not os.path.exists(base):
        os.makedirs(base)
    folder = os.path.join(base, str(time.time()).replace(".", "_"))
    os.makedirs(folder)
    return folder


def test_graphForCombineAttack_image_branch(monkeypatch):
    folder = _tmp_folder("combine_attack_img")
    try:
        # Stub HTML builders to predictable markers
        monkeypatch.setattr(Utility, 'htmlContent', lambda payload: "<GRAPH>" + (payload.get('graph')[:10] if payload.get('graph') else ""))
        monkeypatch.setattr(Utility, 'htmlAppendixContent', lambda payload: "<APPENDIX>")
        monkeypatch.setattr(Utility, 'htmlCssContent', lambda payload: "<CSS>")

        # Seed image files with T/F suffixes for two attacks
        names = ["FastGradientMethod", "AttributeInference"]
        for attack in names:
            for s in ["T", "F"]:
                path = os.path.join(folder, f"orig^{attack}{s}.png")
                # Write a tiny PNG
                import matplotlib.pyplot as plt
                img = np.zeros((4, 4, 3), dtype=np.uint8)
                plt.imshow(img)
                plt.axis('off')
                plt.savefig(path)
                plt.close()

        # Create base report.html that will be prepended
        with open(os.path.join(folder, 'report.html'), 'w', encoding='utf-8') as f:
            f.write("BASE")

        payload = {
            'folder_path': folder,
            'model_metaData': {'dataType': 'Image'},
            'attack_list': [{'name': n} for n in names],
            'modelName': 'm',
            'reportTime': 'now',
            'success_skipped': '0',
            'rows': [],
        }

        Utility.graphForCombineAttack(payload)

        # Assert graph inserted and css appended
        with open(os.path.join(folder, 'report.html'), 'r', encoding='utf-8') as f:
            content = f.read()
        assert '<GRAPH>' in content and '<APPENDIX>' in content and '<CSS>' in content
        # graph.png should be deleted after embedding
        assert not os.path.exists(os.path.join(folder, 'graph.png'))
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def test_graphForCombineAttack_tabular_branch(monkeypatch):
    folder = _tmp_folder("combine_attack_tab")
    try:
        monkeypatch.setattr(Utility, 'htmlContent', lambda payload: "<GRAPHHTML>")
        monkeypatch.setattr(Utility, 'htmlMitigationContent', lambda payload: "<MITIGATION>")
        monkeypatch.setattr(Utility, 'htmlAppendixContent', lambda payload: "<APPENDIX>")
        monkeypatch.setattr(Utility, 'htmlCssContent', lambda payload: "<CSS>")

        # Create CSVs for Evasion and Inference attacks
        evasion_csv = os.path.join(folder, 'FastGradientMethod.csv')
        infer_csv = os.path.join(folder, 'AttributeInference.csv')
        pd.DataFrame({'gt': [0, 1, 1], 'prediction': [0, 0, 1]}).to_csv(evasion_csv, index=False)
        pd.DataFrame({'gt': [0, 1, 0], 'prediction': [1, 1, 0]}).to_csv(infer_csv, index=False)

        # Minimal confusion matrix and classification report
        confusion = np.array([[1, 1], [1, 1]])
        class_report = {
            '0': {'precision': 1.0, 'recall': 0.5, 'f1-score': 0.67, 'support': 2},
            '1': {'precision': 0.5, 'recall': 1.0, 'f1-score': 0.67, 'support': 2},
            'accuracy': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 4},
            'macro avg': {'precision': 0.75, 'recall': 0.75, 'f1-score': 0.67, 'support': 4},
            'weighted avg': {'precision': 0.75, 'recall': 0.75, 'f1-score': 0.67, 'support': 4},
        }

        with open(os.path.join(folder, 'report.html'), 'w', encoding='utf-8') as f:
            f.write("BASE")

        payload = {
            'folder_path': folder,
            'model_metaData': {'dataType': 'Tabular'},
            'attack_list': [{'name': 'FastGradientMethod'}, {'name': 'AttributeInference'}],
            'modelName': 'm',
            'reportTime': 'now',
            'success_skipped': '0',
            'rows': [],
            'target': 'gt',
            'confusion_matrix': confusion,
            'classification_reports': class_report,
            'mitigation_row': '<ROW>'
        }

        Utility.graphForCombineAttack(payload)

        with open(os.path.join(folder, 'report.html'), 'r', encoding='utf-8') as f:
            content = f.read()
        assert '<GRAPHHTML>' in content and '<MITIGATION>' in content and '<APPENDIX>' in content and '<CSS>' in content
        assert not os.path.exists(os.path.join(folder, 'graph.png'))
    finally:
        shutil.rmtree(folder, ignore_errors=True)
