import os
import pandas as pd

from src.service.utility import Utility


def test_graphForAttack_tabular_success_and_unsuccessful(tmp_path):
    # Create Attack_Samples.csv with target/prediction causing both branches
    df = pd.DataFrame({
        'target': [0, 1, 0, 1],
        'prediction': [1, 1, 0, 0]  # two successes (target != prediction) and two unsuccessful
    })
    folder = tmp_path
    csv_path = folder / 'Attack_Samples.csv'
    df.to_csv(csv_path, index=False)

    payload = {
        'type': 'Tabular',
        'folder_path': str(folder),
        'attackName': 'FastGradientMethod',
        'target': 'target'
    }

    html = Utility.graphForAttack(payload)
    assert html is not None and '<img' in html
