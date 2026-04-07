import os
import numpy as np
from PIL import Image

from src.service.utility import Utility


def test_generateImage_creates_png(tmp_path):
    base = np.zeros((1, 6, 6, 3), dtype=float)
    adv = np.ones((1, 6, 6, 3), dtype=float)
    payload = {
        'base_sample': base,
        'adversial_sample': adv,
        'report_path': str(tmp_path),
        'attackName': 'genimg',
    }
    Utility.generateImage(payload)
    out = tmp_path / 'genimg.png'
    assert out.exists() and out.stat().st_size > 0


def _write_png(path, size=(8, 8), color=(100, 100, 200)):
    img = Image.new('RGB', size, color)
    img.save(path, format='PNG')


def test_createAttackFolder_augly_branch(tmp_path):
    # Prepare images that match Augly naming convention
    _write_png(tmp_path / 'img1^Augly.png')
    _write_png(tmp_path / 'img2^Augly.png')
    payload = {
        'report_path': str(tmp_path),
        'attack_list': [{'type': 'Augmentation', 'name': 'Augly'}],
    }
    Utility.createAttackFolder(payload)
    # Ensure Augly/Augmentation base dir created and originals removed
    base_dir = tmp_path / 'Augly' / 'Augmentation'
    assert base_dir.exists()