import os
import numpy as np

from src.service.utility import Utility


def test_graphForMitigation_tabular(tmp_path):
    folder = tmp_path / "mitigation"
    folder.mkdir(parents=True)

    classification_reports = {
        "0": {"precision": 0.8, "recall": 0.7, "f1-score": 0.75, "support": 10},
        "1": {"precision": 0.9, "recall": 0.85, "f1-score": 0.875, "support": 12},
        "accuracy": {"support": 22},
        "macro avg": {"precision": 0.85, "recall": 0.775, "f1-score": 0.8125, "support": 22},
        "weighted avg": {"precision": 0.86, "recall": 0.78, "f1-score": 0.82, "support": 22},
    }
    confusion_matrix = np.array([[8, 2], [1, 11]])

    payload = {
        "folder_path": str(folder),
        "modelName": "m",
        "model_metaData": {"dataType": "Tabular"},
        "classification_reports": classification_reports,
        "confusion_matrix": confusion_matrix,
    }

    # Exercise computation; expect enriched DataFrame returned
    df = Utility.graphForMitigation(payload)
    assert hasattr(df, 'loc')
    # Check added columns exist
    for col in ['specificity', 'balance accuracy', 'FPR']:
        assert col in df.columns
