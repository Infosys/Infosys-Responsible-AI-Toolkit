import os

from src.service.utility import Utility


def test_graphForAttack_tabular(tmp_path):
    folder = tmp_path / "attack_graph"
    folder.mkdir(parents=True)

    # Create Attack_Samples.csv with target and prediction columns
    csv_path = folder / "Attack_Samples.csv"
    csv_path.write_text("gt_label,prediction\n0,1\n1,1\n")

    html = Utility.graphForAttack({
        "type": "Tabular",
        "folder_path": str(folder),
        "attackName": "FastGradientMethod",
        "target": "gt_label",
    })

    assert isinstance(html, str)
    assert "data:image/png;base64" in html
