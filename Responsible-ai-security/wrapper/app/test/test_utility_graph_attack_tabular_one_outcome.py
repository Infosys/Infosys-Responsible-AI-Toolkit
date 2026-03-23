import pandas as pd

from src.service.utility import Utility


def test_graphForAttack_tabular_single_outcome(tmp_path):
    # All predictions equal to target -> single outcome 'Unsuccessful'
    df = pd.DataFrame({
        'target': [0, 1, 0, 1],
        'prediction': [0, 1, 0, 1]
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
