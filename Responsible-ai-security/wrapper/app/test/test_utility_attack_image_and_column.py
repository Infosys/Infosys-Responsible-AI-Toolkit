import os
import shutil
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')

from src.service.utility import Utility


def _tmp(prefix):
    base = os.path.join(os.getcwd(), prefix)
    if not os.path.exists(base):
        os.makedirs(base)
    folder = os.path.join(base, str(time.time()).replace(".", "_"))
    os.makedirs(folder)
    return folder


def test_graphForAttack_image_branch_embeds_png():
    folder = _tmp("attack_image_branch")
    try:
        # Build minimal attackDataList structure expected by graphForAttack
        H, W = 10, 12
        orig = np.zeros((1, H, W, 3), dtype=np.uint8)
        adv = np.ones((1, H, W, 3), dtype=np.uint8)
        attackDataList = {
            'sample.png': [None, orig, adv, 'cat', 'dog']
        }
        payload = {
            'type': 'Image',
            'folder_path': folder,
            'top_keys': ['sample.png'],
            'attackDataList': attackDataList,
        }
        html = Utility.graphForAttack(payload)
        assert isinstance(html, str) and 'data:image/png;base64' in html
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def test_graphForAttackColumn_image_branch_noop():
    folder = _tmp("attack_column_image")
    try:
        out = Utility.graphForAttackColumn({'type': 'Image'})
        assert out is None
    finally:
        shutil.rmtree(folder, ignore_errors=True)
