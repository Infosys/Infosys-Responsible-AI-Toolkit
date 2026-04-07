import os
import numpy as np
import pandas as pd

from src.service.utility import Utility


def test_checkAttackListStatus_and_makeAttackListRow_tabular(tmp_path):
    folder = tmp_path / "tabular_attacks"
    folder.mkdir()

    # Create CSVs: last column is a boolean flag indicating successful rows
    df_evasion = pd.DataFrame({
        "target": [0, 1, 1, 0],
        "prediction": [0, 0, 1, 1],
        "flag": [True, True, False, False],
    })
    df_evasion.to_csv(folder / "FastGradientMethod.csv", index=False)

    df_inference = pd.DataFrame({
        "target": [0, 0, 1, 1],
        "prediction": [1, 0, 1, 0],
        "flag": [True, False, True, False],
    })
    df_inference.to_csv(folder / "AttributeInference.csv", index=False)

    attack_accuracy_dict = {
        "FastGradientMethod.csv": 0.85,
        "AttributeInference.csv": 0.55,
    }

    statusList, defenceList = Utility.checkAttackListStatus({
        "folder_path": str(folder),
        "modelName": "m",
        "attackList": ["FastGradientMethod", "AttributeInference"],
        "meta_data": {"dataType": "Tabular"},
        "attack_accuracy_dict": attack_accuracy_dict,
    })

    # Expect keys for both attacks and numeric values
    keys = {list(d.keys())[0] for d in statusList}
    assert {"FastGradientMethod", "AttributeInference"}.issubset(keys)
    assert all(isinstance(list(d.values())[0], (int, float)) for d in statusList)

    rows, mitigation_row, attack_list = Utility.makeAttackListRow({
        "total_attacks": ["FastGradientMethod", "AttributeInference"],
        "attackList": ["FastGradientMethod", "AttributeInference"],
        "statusList": statusList,
        "defenceList": defenceList,
        "meta_data": {"dataType": "Tabular"},
    })

    # Generated HTML snippets should include bars for accuracy/detection
    assert "attack-accuracy-bar-fill" in rows
    assert "detection-accuracy-bar-fill" in mitigation_row
    # Attack list contains name/type pairs
    assert any(a.get("name") == "FastGradientMethod" and a.get("type") == "Evasion" for a in attack_list)
    assert any(a.get("name") == "AttributeInference" and a.get("type") == "Inference" for a in attack_list)


def test_checkAttackListStatus_and_makeAttackListRow_image(tmp_path):
    folder = tmp_path / "image_attacks"
    folder.mkdir()

    # Create image filenames encoding attack name and success flag (T/F)
    # format used: <prefix>^<AttackName><T/F>.jpg
    (folder / "img^FastGradientMethodT.jpg").write_bytes(b"")
    (folder / "img^FastGradientMethodF.jpg").write_bytes(b"")
    (folder / "img^AttributeInferenceT.png").write_bytes(b"")
    (folder / "img^AttributeInferenceF.png").write_bytes(b"")

    statusList = Utility.checkAttackListStatus({
        "folder_path": str(folder),
        "modelName": "m",
        "attackList": ["FastGradientMethod", "AttributeInference"],
        "meta_data": {"dataType": "Image"},
    })

    # Status for each attack should be computed as percentage
    keys = {list(d.keys())[0] for d in statusList}
    assert {"FastGradientMethod", "AttributeInference"}.issubset(keys)

    rows, attack_list = Utility.makeAttackListRow({
        "total_attacks": ["FastGradientMethod", "AttributeInference"],
        "attackList": ["FastGradientMethod", "AttributeInference"],
        "statusList": statusList,
        "meta_data": {"dataType": "Image"},
    })

    # HTML includes selection marker and attack_list contains typed entries
    assert "selected-attack" in rows
    assert any(a.get("name") == "FastGradientMethod" and a.get("type") == "Evasion" for a in attack_list)
    assert any(a.get("name") == "AttributeInference" and a.get("type") == "Inference" for a in attack_list)
