'''
License textMIT Licensehttps://mit-license.org/Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

import pytest

from privacy.util.model_integrity import (
    assert_model_files_are_real,
    find_lfs_pointer_weight_files,
    is_lfs_pointer_file,
)


LFS_POINTER_CONTENT = (
    "version https://git-lfs.github.com/spec/v1\n"
    "oid sha256:4d7a214614ab2935c943f9e0ff69d22eadbb17e6c4f4b1d4d3b9ee6a30d8a6a\n"
    "size 123456789\n"
)


class TestIsLfsPointerFile:
    def test_detects_lfs_pointer_file(self, tmp_path):
        pointer_file = tmp_path / "pytorch_model.bin"
        pointer_file.write_text(LFS_POINTER_CONTENT)

        assert is_lfs_pointer_file(str(pointer_file)) is True

    def test_ignores_real_binary_file(self, tmp_path):
        real_file = tmp_path / "pytorch_model.bin"
        real_file.write_bytes(bytes(range(256)) * 100)

        assert is_lfs_pointer_file(str(real_file)) is False

    def test_missing_file_is_not_a_pointer(self, tmp_path):
        missing_file = tmp_path / "does_not_exist.bin"

        assert is_lfs_pointer_file(str(missing_file)) is False


class TestFindLfsPointerWeightFiles:
    def test_finds_pointer_weight_files_only(self, tmp_path):
        (tmp_path / "pytorch_model.bin").write_text(LFS_POINTER_CONTENT)
        (tmp_path / "config.json").write_text('{"model_type": "bert"}')
        (tmp_path / "model.safetensors").write_bytes(b"\x00\x01\x02\x03" * 50)

        assert find_lfs_pointer_weight_files(str(tmp_path)) == ["pytorch_model.bin"]

    def test_returns_empty_list_for_missing_directory(self, tmp_path):
        missing_dir = tmp_path / "does_not_exist"

        assert find_lfs_pointer_weight_files(str(missing_dir)) == []

    def test_returns_empty_list_when_all_weights_are_real(self, tmp_path):
        (tmp_path / "pytorch_model.bin").write_bytes(b"\x00\x01\x02\x03" * 50)

        assert find_lfs_pointer_weight_files(str(tmp_path)) == []


class TestAssertModelFilesAreReal:
    def test_raises_actionable_error_for_lfs_pointer(self, tmp_path):
        (tmp_path / "pytorch_model.bin").write_text(LFS_POINTER_CONTENT)

        with pytest.raises(RuntimeError, match="Git LFS pointer"):
            assert_model_files_are_real(str(tmp_path))

    def test_does_not_raise_for_missing_directory(self, tmp_path):
        missing_dir = tmp_path / "does_not_exist"

        assert_model_files_are_real(str(missing_dir))

    def test_does_not_raise_for_real_model_files(self, tmp_path):
        (tmp_path / "pytorch_model.bin").write_bytes(b"\x00\x01\x02\x03" * 50)

        assert_model_files_are_real(str(tmp_path))
