import os
import shutil
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.service.utility import Utility


def _make_temp_dir(prefix="tmp_attack_folder"):
    base = os.path.join(os.getcwd(), prefix)
    if not os.path.exists(base):
        os.makedirs(base)
    folder = os.path.join(base, str(time.time()).replace(".", "_"))
    os.makedirs(folder)
    return folder


def test_createAttackFolder_image_and_csv_segmentation(monkeypatch):
    folder = _make_temp_dir("attack_folder")
    try:
        # Allow special characters expected by folder logic (like '^')
        monkeypatch.setattr(Utility, 'sanitize_filenameorfoldername', lambda x: x)

        # Create base image files for Evasion, Inference, Augly
        for name in ["FastGradientMethod", "AttributeInference", "Augly"]:
            img = np.zeros((10, 10, 3), dtype=np.uint8)
            plt.imshow(img)
            plt.axis('off')
            plt.savefig(os.path.join(folder, f"orig^{name}.png"))
            plt.close()

        # Create CSVs for Evasion/Inference
        with open(os.path.join(folder, "FastGradientMethod.csv"), "w") as f:
            f.write("gt,prediction\n0,1\n1,1\n")
        with open(os.path.join(folder, "AttributeInference.csv"), "w") as f:
            f.write("gt,prediction\n0,0\n1,1\n")

        # Attack types to create target folders
        attack_list = [
            {"type": "Evasion"},
            {"type": "Inference"},
            {"type": "Augmentation"},
        ]

        Utility.createAttackFolder({"report_path": folder, "attack_list": attack_list})

        # Assert image files moved into proper folders
        evasion_file = os.path.join(folder, "Art", "Evasion", "FastGradientMethod", "orig.png")
        inference_file = os.path.join(folder, "Art", "Inference", "AttributeInference", "orig.png")
        augly_file = os.path.join(folder, "Augly", "Augmentation", "Augly", "orig.png")
        assert os.path.exists(evasion_file)
        assert os.path.exists(inference_file)
        assert os.path.exists(augly_file)

        # Assert CSVs copied into folders
        csv_evasion = os.path.join(folder, "Art", "Evasion", "FastGradientMethod", "FastGradientMethod.csv")
        csv_inference = os.path.join(folder, "Art", "Inference", "AttributeInference", "AttributeInference.csv")
        assert os.path.exists(csv_evasion)
        assert os.path.exists(csv_inference)
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def test_createAttackFolder_multiple_images_folder_resets(monkeypatch):
    folder = _make_temp_dir("attack_folder_multi")
    try:
        monkeypatch.setattr(Utility, 'sanitize_filenameorfoldername', lambda x: x)

        # Create multiple images for the same attack to exercise path resets
        attacks = ["FastGradientMethod", "AttributeInference", "Augly"]
        for attack in attacks:
            for _ in range(2):  # create two images per attack without T/F suffix
                img = np.zeros((5, 5, 3), dtype=np.uint8)
                plt.imshow(img)
                plt.axis('off')
                plt.savefig(os.path.join(folder, f"orig^{attack}.png"))
                plt.close()

        attack_list = [
            {"type": "Evasion"},
            {"type": "Inference"},
            {"type": "Augmentation"},
        ]

        Utility.createAttackFolder({"report_path": folder, "attack_list": attack_list})

        # All images should be moved into their respective single-level folders, not nested repeatedly
        evasion_dir = os.path.join(folder, "Art", "Evasion", "FastGradientMethod")
        infer_dir = os.path.join(folder, "Art", "Inference", "AttributeInference")
        augly_dir = os.path.join(folder, "Augly", "Augmentation", "Augly")
        assert os.path.isdir(evasion_dir)
        assert os.path.isdir(infer_dir)
        assert os.path.isdir(augly_dir)
        # Expect images moved and renamed to orig.png; final file exists
        assert os.path.exists(os.path.join(evasion_dir, "orig.png"))
        assert os.path.exists(os.path.join(infer_dir, "orig.png"))
        assert os.path.exists(os.path.join(augly_dir, "orig.png"))
    finally:
        shutil.rmtree(folder, ignore_errors=True)
