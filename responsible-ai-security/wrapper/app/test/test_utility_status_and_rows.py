import os
import shutil
import json
import time
import numpy as np
import pandas as pd

from src.service.utility import Utility


def _make_temp_dir(prefix="tmp_status"):
    base = os.path.join(os.getcwd(), prefix)
    if not os.path.exists(base):
        os.makedirs(base)
    folder = os.path.join(base, str(time.time()).replace(".", "_"))
    os.makedirs(folder)
    return folder


def test_checkAttackListStatus_and_makeAttackListRow_tabular():
    folder = _make_temp_dir("ut_status_rows")
    try:
        # Create CSVs for two attacks with boolean last column
        attacks = ["FastGradientMethod", "AttributeInference"]
        acc_map = {}
        for name in attacks:
            df = pd.DataFrame({
                "gt": [0, 1, 0, 1],
                "prediction": [0, 1, 1, 1],
                "flag": [True, False, True, True],
            })
            csv_path = os.path.join(folder, f"{name}.csv")
            df.to_csv(csv_path, index=False)
            acc_map[f"{name}.csv"] = 0.8  # detection accuracy placeholder

        statusList, defenceList = Utility.checkAttackListStatus({
            "meta_data": {"dataType": "Tabular"},
            "folder_path": folder,
            "attack_accuracy_dict": acc_map,
        })
        assert isinstance(statusList, list) and isinstance(defenceList, list)
        assert len(statusList) == 2 and len(defenceList) == 2

        # Compose makeAttackListRow payload
        all_attacks = attacks
        rows, mitigation_row, attack_list = Utility.makeAttackListRow({
            "meta_data": {"dataType": "Tabular"},
            "total_attacks": all_attacks,
            "attackList": all_attacks,
            "statusList": statusList,
            "defenceList": defenceList,
        })
        assert "Attack Type" not in rows  # it's table body rows
        assert "detection-accuracy" in mitigation_row
        assert isinstance(attack_list, list) and len(attack_list) == 2
    finally:
        shutil.rmtree(folder, ignore_errors=True)
