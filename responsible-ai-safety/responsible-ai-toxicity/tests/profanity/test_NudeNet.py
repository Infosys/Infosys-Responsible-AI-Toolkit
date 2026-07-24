import builtins
import sys
import io
import tempfile
import os
import base64
import importlib
from types import SimpleNamespace

import pytest


def make_fake_file(data: bytes):
    f = io.BytesIO(data)
    f.name = "fake"
    f.file = f
    return f


class DummyDetector:
    def __init__(self, *args, **kwargs):
        pass

    def detect(self, path):
        # Return a detection in the centre of a 100x100 image
        return [
            {"class": "FEMALE_BREAST_EXPOSED", "score": 0.9, "box": [10, 10, 20, 20]}
        ]


class DummyCap:
    def __init__(self, frames):
        self._frames = frames
        self._index = 0

    def isOpened(self):
        return self._index < len(self._frames)

    def read(self):
        if self._index >= len(self._frames):
            return False, None
        frame = self._frames[self._index]
        self._index += 1
        return True, frame

    def get(self, prop):
        # width, height, fps
        if prop == 3:  # CAP_PROP_FRAME_WIDTH
            return 100
        if prop == 4:  # CAP_PROP_FRAME_HEIGHT
            return 100
        if prop == 5:  # CAP_PROP_FPS
            return 24
        return 0

    def release(self):
        pass


class DummyWriter:
    def __init__(self, *args, **kwargs):
        self.frames = []

    def write(self, frame):
        self.frames.append(frame)

    def release(self):
        pass


def test_image_to_byte_and_nude_net_images(monkeypatch, tmp_path):
    # Prepare a fake image bytes (a small RGB PNG)
    from PIL import Image

    img = Image.new("RGB", (50, 50), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    data = buf.getvalue()

    fake_file = make_fake_file(data)

    # Insert DummyDetector into module before import
    mod_name = "profanity.util.NudeNet.NudeNet"
    # Ensure parent package is importable
    import importlib.util

    # Monkeypatch cv2 functions used by NudeNet
    class FakeCV2:
        IMREAD_COLOR = 1

        @staticmethod
        def imdecode(arr, flag):
            # Return a numpy-like array (PIL -> ndarray conversion not needed for our code path)
            from numpy import ones

            return ones((50, 50, 3), dtype="uint8") * 255

        @staticmethod
        def imwrite(path, img):
            # write a simple file to represent output
            with open(path, "wb") as f:
                f.write(b"jpeg")
            return True

        @staticmethod
        def GaussianBlur(roi, ksize, sigma):
            return roi

        COLOR_BGR2RGB = 0
        COLOR_RGB2BGR = 0

        @staticmethod
        def cvtColor(img, flag):
            return img

    # Ensure the real cv2 is replaced before importing the module
    monkeypatch.setitem(sys.modules, "cv2", FakeCV2)

    # Patch the external nudenet module with a NudeDetector attr
    monkeypatch.setitem(sys.modules, "nudenet", SimpleNamespace(NudeDetector=DummyDetector))

    # Import the module under test (fresh) and reload to ensure it uses our sys.modules stubs
    mod = importlib.reload(importlib.import_module("profanity.util.NudeNet.NudeNet"))

    # Monkeypatch the module's nude_detector instance to our dummy (redundant but explicit)
    mod.nude_detector = DummyDetector()

    # Call nudeNetImages (module implements camelCase names)
    resp = mod.nudeNetImages({"image": fake_file})
    assert "blurredImage" in resp and "originalImage" in resp and "nudanalyze" in resp
    assert isinstance(resp["blurredImage"], str)
    assert isinstance(resp["originalImage"], str)
    assert resp["nudanalyze"].get("FEMALE_BREAST_EXPOSED") == 0.9


def test_nude_net_video(monkeypatch, tmp_path):
    # Create three fake frames (numpy arrays)
    import numpy as np

    frames = [np.ones((100, 100, 3), dtype="uint8") * 255 for _ in range(3)]

    # Monkeypatch VideoCapture and VideoWriter
    def fake_VideoCapture(path):
        return DummyCap(frames)

    # Replace global cv2 module with a namespace providing required symbols
    monkeypatch.setitem(sys.modules, "cv2", SimpleNamespace(
        VideoCapture=fake_VideoCapture,
        VideoWriter=lambda *a, **k: DummyWriter(),
        imwrite=lambda p, img: True,
        cvtColor=lambda img, flag: img,
        GaussianBlur=lambda roi, k, s: roi,
        COLOR_BGR2RGB=0,
        COLOR_RGB2BGR=0,
        CAP_PROP_FRAME_WIDTH=3,
        CAP_PROP_FRAME_HEIGHT=4,
        CAP_PROP_FPS=5,
        VideoWriter_fourcc=lambda *args: 0,
    ))

    # Patch nudenet module
    monkeypatch.setitem(sys.modules, "nudenet", SimpleNamespace(NudeDetector=DummyDetector))

    # Import fresh module and reload to pick up the cv2/nudenet stubs
    import importlib
    mod = importlib.reload(importlib.import_module("profanity.util.NudeNet.NudeNet"))
    mod.nude_detector = DummyDetector()
    # Avoid opening the actual output file by stubbing videoToByte (module uses camelCase)
    mod.videoToByte = lambda path: base64.b64encode(b"fakevideo").decode("utf-8")

    # Create a fake video file-like object
    fake_video = make_fake_file(b"fakevideo")

    # Ensure the expected output file exists so the function can read and remove it
    open("output1.mp4", "wb").write(b"stub")

    resp = mod.nudeNetVideo({"video": fake_video})
    assert "nudanalyze" in resp and "BLURRED" in resp
    assert isinstance(resp["BLURRED"], str)
