import os
import joblib
import numpy as np

from src.service.utility import Utility


def test_find_duplicates_basic():
    x = np.array([
        [1, 2],
        [3, 4],
        [1, 2],  # duplicate of first row
        [5, 6],
    ])
    dup = Utility.find_duplicates(x)
    # Expect third element marked as duplicate
    assert dup.tolist() == [0.0, 0.0, 1.0, 0.0]


def test_calc_precision_recall_edge_and_normal():
    # Edge case: no positives in predicted/actual -> precision/recall default to 1
    predicted = [0, 0, 0]
    actual = [0, 0, 0]
    p, r = Utility.calc_precision_recall(predicted, actual, positive_value=1)
    assert p == 1 and r == 1

    # Normal case with some positives and correct predictions
    predicted = [1, 0, 1, 1]
    actual = [1, 0, 0, 1]
    p, r = Utility.calc_precision_recall(predicted, actual, positive_value=1)
    # score = correct positives at indices 0 and 3 => 2
    # num_positive_predicted = 3 => precision 2/3
    # num_positive_actual = 2 => recall 2/2
    assert abs(p - (2/3)) < 1e-6
    assert r == 1


def test_safe_load_from_file(tmp_path):
    # Dump a simple object and load via safe_load_from_file
    obj = {"a": 1, "b": [1, 2, 3]}
    fp = tmp_path / "obj.pkl"
    joblib.dump(obj, fp)
    loaded = Utility.safe_load_from_file(str(fp))
    assert loaded == obj


def test_databaseDelete_file_and_dir(tmp_path):
    # File deletion
    f = tmp_path / "to_delete.txt"
    f.write_text("hello")
    Utility.databaseDelete(str(f))
    assert not f.exists()

    # Directory deletion
    d = tmp_path / "to_delete_dir"
    d.mkdir()
    Utility.databaseDelete(str(d))
    assert not d.exists()
