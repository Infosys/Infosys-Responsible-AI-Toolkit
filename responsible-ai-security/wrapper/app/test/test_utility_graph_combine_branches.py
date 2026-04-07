import os
import shutil
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.service.utility import Utility


def _make_dir(prefix="combine_graph"):
    base = os.path.join(os.getcwd(), prefix)
    if not os.path.exists(base):
        os.makedirs(base)
    folder = os.path.join(base, str(time.time()).replace(".", "_"))
    os.makedirs(folder)
    # seed report.html for combine paths
    with open(os.path.join(folder, "report.html"), "w", encoding="utf-8") as f:
        f.write("<html><body>combined</body></html>")
    return folder


def _write_png(path, name_with_flag):
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    plt.imshow(img)
    plt.axis('off')
    plt.savefig(os.path.join(path, f"orig^{name_with_flag}.png"))
    plt.close()


def test_graphForCombineAttack_image_simple_and_multi_subplot(monkeypatch):
    folder = _make_dir("combine_image")
    try:
        # Stub HTML helpers to ensure deterministic augmentation
        monkeypatch.setattr(Utility, 'htmlContent', lambda payload: '<GRAPH>')
        monkeypatch.setattr(Utility, 'htmlAppendixContent', lambda payload: '<APPENDIX>')
        monkeypatch.setattr(Utility, 'htmlCssContent', lambda payload: '<CSS>')
        # Prepare attacks (>8 triggers multi-subplot in graphForCombineAttack1)
        attacks = [
            {"name": f"Attack{i}"} for i in range(1, 10)
        ]
        # Write one image per attack with T/F flags to exercise equal/unequal logic
        for i in range(1, 10):
            flag = "T" if i % 2 == 0 else "F"
            _write_png(folder, f"Attack{i}{flag}")

        payload_base = {
            "folder_path": folder,
            "attack_list": attacks,
            "modelName": "m",
            "model_metaData": {"dataType": "Image"},
            "reportTime": "now",
            "success_skipped": [],
            "rows": [],
        }

        # graphForCombineAttack (Image)
        Utility.graphForCombineAttack(payload_base)
        # graphForCombineAttack1 (Image) with multi-subplots
        Utility.graphForCombineAttack1(payload_base)

        # Ensure report.html was augmented (content length grows)
        rp = os.path.join(folder, "report.html")
        with open(rp, "r", encoding="utf-8") as f:
            content = f.read()
        # Content should be augmented beyond the base seed
        assert '<GRAPH>' in content and '<APPENDIX>' in content and '<CSS>' in content
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def test_graphForCombineAttack_tabular_both_categories(monkeypatch):
    folder = _make_dir("combine_tabular")
    try:
        # Stub HTML helpers
        monkeypatch.setattr(Utility, 'htmlContent', lambda payload: '<GRAPHHTML>')
        monkeypatch.setattr(Utility, 'htmlMitigationContent', lambda payload: '<MITIGATION>')
        monkeypatch.setattr(Utility, 'htmlAppendixContent', lambda payload: '<APPENDIX>')
        monkeypatch.setattr(Utility, 'htmlCssContent', lambda payload: '<CSS>')
        # Create two CSVs: one Evasion, one Inference
        evasion = os.path.join(folder, "FastGradientMethod.csv")
        inference = os.path.join(folder, "AttributeInference.csv")
        pd.DataFrame({"gt": [0, 1, 1], "prediction": [0, 0, 1]}).to_csv(evasion, index=False)
        pd.DataFrame({"gt": [0, 1, 1], "prediction": [1, 1, 1]}).to_csv(inference, index=False)

        payload = {
            "folder_path": folder,
            "attack_list": [{"name": "FastGradientMethod"}, {"name": "AttributeInference"}],
            "modelName": "m",
            "model_metaData": {"dataType": "Tabular"},
            "reportTime": "now",
            "success_skipped": [],
            "rows": [],
            "target": "gt",
            "confusion_matrix": np.array([[2, 1], [1, 2]]),
            "classification_reports": {
                "0": {"precision": 1.0, "recall": 0.5, "f1-score": 0.67, "support": 2},
                "1": {"precision": 0.67, "recall": 1.0, "f1-score": 0.8, "support": 3},
                "accuracy": {"precision": 0.0, "recall": 0.0, "f1-score": 0.0, "support": 5},
                "macro avg": {"precision": 0.84, "recall": 0.75, "f1-score": 0.74, "support": 5},
                "weighted avg": {"precision": 0.8, "recall": 0.8, "f1-score": 0.78, "support": 5},
            },
            "mitigation_row": [],
        }

        # Run both combine functions in Tabular mode
        Utility.graphForCombineAttack(payload)
        Utility.graphForCombineAttack1(payload)

        # Check report.html augmented
        rp = os.path.join(folder, "report.html")
        with open(rp, "r", encoding="utf-8") as f:
            content = f.read()
        # Combined report should include additional HTML beyond base seed
        assert '<GRAPHHTML>' in content and '<MITIGATION>' in content and '<APPENDIX>' in content and '<CSS>' in content
    finally:
        shutil.rmtree(folder, ignore_errors=True)
