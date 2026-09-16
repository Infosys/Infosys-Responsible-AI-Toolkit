'''
License textMIT Licensehttps://mit-license.org/Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

import os

LFS_POINTER_SIGNATURE = "version https://git-lfs.github.com/spec"
_WEIGHT_FILE_EXTENSIONS = (".bin", ".safetensors", ".h5", ".ckpt", ".pt")


def is_lfs_pointer_file(file_path):
    """Return True if file_path is an unresolved Git LFS pointer stub rather than real binary content."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            head = f.read(200)
    except OSError:
        return False
    return head.lstrip().startswith(LFS_POINTER_SIGNATURE)


def find_lfs_pointer_weight_files(model_dir):
    """Return the names of weight files under model_dir that are unresolved Git LFS pointers."""
    if not os.path.isdir(model_dir):
        return []
    pointer_files = []
    for entry in sorted(os.listdir(model_dir)):
        if entry.lower().endswith(_WEIGHT_FILE_EXTENSIONS):
            full_path = os.path.join(model_dir, entry)
            if os.path.isfile(full_path) and is_lfs_pointer_file(full_path):
                pointer_files.append(entry)
    return pointer_files


def assert_model_files_are_real(model_dir):
    """Raise a clear, actionable error if model_dir contains unresolved Git LFS pointer files.

    Passing pointer stubs to transformers/torch fails deep inside torch.load with a
    confusing pickle error. When the model is loaded at module import time, that
    crashes the whole process (e.g. a Kubernetes pod CrashLoopBackOff) with no clear
    indication of the real cause. Failing fast here with an actionable message turns
    that into a diagnosable startup error.
    """
    pointer_files = find_lfs_pointer_weight_files(model_dir)
    if pointer_files:
        raise RuntimeError(
            f"Model files in '{model_dir}' are Git LFS pointer stubs, not the actual "
            f"model weights: {', '.join(pointer_files)}. This happens when the model "
            "was downloaded with 'git clone' without Git LFS installed. Fix it by "
            "installing Git LFS and running 'git lfs pull' inside the model "
            "directory, or by re-downloading the files directly, e.g. "
            f"'huggingface-cli download <repo_id> --local-dir {model_dir}'."
        )
