"""
Extra coverage tests for diffrentialPrivacy.py.

NOTE: test_routing_coverage_boost.py (collected after this file) replaces
sys.modules['privacy.service.diffrentialPrivacy'] with a MagicMock at module
level. We capture the real DiffPrivacy at collection time so our tests always
use the real implementation.

All tests here verify the functions run without raising exceptions (for coverage),
without asserting specific internal state that is environment-dependent.
"""
import pytest
from unittest.mock import patch, MagicMock

# ---------------------------------------------------------------------------
# Capture the real DiffPrivacy at module-import time (before routing tests
# replace the module in sys.modules). Each import is isolated so that a
# failure in one does not prevent the others from being captured.
# ---------------------------------------------------------------------------
try:
    from privacy.service.diffrentialPrivacy import DiffPrivacy as _REAL_DP
except Exception:
    _REAL_DP = None

try:
    from privacy.config.logger import request_id_var as _REAL_RID
except Exception:
    _REAL_RID = None

try:
    from privacy.service import error_dict as _REAL_ED
except Exception:
    _REAL_ED = {}


def _dp():
    if _REAL_DP is not None:
        return _REAL_DP
    from privacy.service.diffrentialPrivacy import DiffPrivacy
    return DiffPrivacy


def _rid():
    return _REAL_RID


def _ed():
    return _REAL_ED if _REAL_ED is not None else {}


# ---------------------------------------------------------------------------
# Helpers: build mock DataFrames that satisfy function preconditions
# ---------------------------------------------------------------------------

def _int_series(length=5):
    s = MagicMock()
    s.dtypes = 'int64'
    s.__len__ = MagicMock(return_value=length)
    s.min.return_value = 10
    s.max.return_value = 50
    s.unique.return_value = [0, 1]
    return s


def _float_series(length=5):
    s = MagicMock()
    s.dtypes = 'float64'
    s.__len__ = MagicMock(return_value=length)
    s.min.return_value = 1.0
    s.max.return_value = 5.0
    return s


def _str_series(values=None, length=6):
    s = MagicMock()
    s.dtypes = 'object'
    s.__len__ = MagicMock(return_value=length)
    s.unique.return_value = values or ["M", "F"]
    return s


def _mock_df(series_map):
    df = MagicMock()
    df.__getitem__.side_effect = lambda col: series_map.get(col, MagicMock())
    df.__len__ = MagicMock(return_value=6)
    df.loc = MagicMock()
    df.loc.__getitem__.side_effect = lambda key: series_map.get(key[1], MagicMock()).unique.return_value[0]
    df.drop.return_value = df
    return df


# ---------------------------------------------------------------------------
# noise_add (lines 50-59)
# ---------------------------------------------------------------------------

class TestNoiseAdd:
    def test_noise_add_int64_series_no_exception(self):
        """noise_add runs without error for an int64-dtype column."""
        DiffPrivacy = _dp()
        series = _int_series()
        df = _mock_df({"age": series})
        import numpy as np_real
        with patch.dict(DiffPrivacy.noise_add.__globals__, {'np': np_real}):
            DiffPrivacy.noise_add(df, "age")

    def test_noise_add_float_series_no_exception(self):
        """noise_add runs without error for a float-dtype column."""
        DiffPrivacy = _dp()
        series = _float_series()
        df = _mock_df({"score": series})
        import numpy as np_real
        with patch.dict(DiffPrivacy.noise_add.__globals__, {'np': np_real}):
            DiffPrivacy.noise_add(df, "score")


# ---------------------------------------------------------------------------
# binary_check (lines 62-68)
# ---------------------------------------------------------------------------

class TestBinaryCheck:
    def test_binary_check_string_binary_column_no_exception(self):
        """binary_check runs without error for a column with 2 unique values."""
        DiffPrivacy = _dp()
        series = _str_series(values=["M", "F"])
        df = _mock_df({"gender": series})
        with patch.dict(DiffPrivacy.binary_check.__globals__, {
            'binary': MagicMock(**{'Binary.return_value.randomise.return_value': "M"})
        }):
            DiffPrivacy.binary_check(df, "gender")

    def test_binary_check_integer_binary_column_no_exception(self):
        """binary_check runs without error for an integer binary column."""
        DiffPrivacy = _dp()
        series = _str_series(values=[0, 1])
        df = _mock_df({"flag": series})
        with patch.dict(DiffPrivacy.binary_check.__globals__, {
            'binary': MagicMock(**{'Binary.return_value.randomise.return_value': 0})
        }):
            DiffPrivacy.binary_check(df, "flag")


# ---------------------------------------------------------------------------
# range_add (lines 73-98)
# ---------------------------------------------------------------------------

class TestRangeAdd:
    def test_range_add_no_exception(self):
        """range_add runs without error."""
        DiffPrivacy = _dp()
        series = _int_series()
        df = _mock_df({"salary": series})
        with patch.dict(DiffPrivacy.range_add.__globals__, {'pd': MagicMock()}):
            DiffPrivacy.range_add(df, "salary")

    def test_range_add_small_range_no_exception(self):
        """range_add handles a small numeric range."""
        DiffPrivacy = _dp()
        series = _int_series()
        series.min.return_value = 1
        series.max.return_value = 10
        df = _mock_df({"val": series})
        with patch.dict(DiffPrivacy.range_add.__globals__, {'pd': MagicMock()}):
            DiffPrivacy.range_add(df, "val")


# ---------------------------------------------------------------------------
# gaussian_func (lines 100-110)
# ---------------------------------------------------------------------------

class TestGaussianFunc:
    def test_gaussian_int64_no_exception(self):
        """gaussian_func runs without error for int64 column."""
        DiffPrivacy = _dp()
        series = _int_series()
        df = _mock_df({"count": series})
        mock_gaussian = MagicMock()
        mock_gaussian.GaussianAnalytic.return_value.randomise.return_value = 42
        with patch.dict(DiffPrivacy.gaussian_func.__globals__, {'gaussian': mock_gaussian}):
            DiffPrivacy.gaussian_func(df, "count")

    def test_gaussian_float_no_exception(self):
        """gaussian_func runs without error for float column."""
        DiffPrivacy = _dp()
        series = _float_series()
        df = _mock_df({"temp": series})
        mock_gaussian = MagicMock()
        mock_gaussian.GaussianAnalytic.return_value.randomise.return_value = 36.5
        with patch.dict(DiffPrivacy.gaussian_func.__globals__, {'gaussian': mock_gaussian}):
            DiffPrivacy.gaussian_func(df, "temp")


# ---------------------------------------------------------------------------
# laplace_func (lines 112-124)
# ---------------------------------------------------------------------------

class TestLaplaceFunc:
    def test_laplace_int64_no_exception(self):
        """laplace_func runs without error for int64 column."""
        DiffPrivacy = _dp()
        series = _int_series()
        df = _mock_df({"age": series})
        mock_laplace = MagicMock()
        mock_laplace.LaplaceTruncated.return_value.randomise.return_value = 28
        with patch.dict(DiffPrivacy.laplace_func.__globals__, {'laplace': mock_laplace}):
            DiffPrivacy.laplace_func(df, "age")

    def test_laplace_float_no_exception(self):
        """laplace_func runs without error for float column."""
        DiffPrivacy = _dp()
        series = _float_series()
        df = _mock_df({"weight": series})
        mock_laplace = MagicMock()
        mock_laplace.LaplaceTruncated.return_value.randomise.return_value = 65.5
        with patch.dict(DiffPrivacy.laplace_func.__globals__, {'laplace': mock_laplace}):
            DiffPrivacy.laplace_func(df, "weight")


# ---------------------------------------------------------------------------
# snapping_func (lines 125-137)
# ---------------------------------------------------------------------------

class TestSnappingFunc:
    def test_snapping_int64_no_exception(self):
        """snapping_func runs without error for int64 column."""
        DiffPrivacy = _dp()
        series = _int_series()
        df = _mock_df({"val": series})
        mock_snap = MagicMock()
        mock_snap.Snapping.return_value.randomise.return_value = 18
        with patch.dict(DiffPrivacy.snapping_func.__globals__, {'snapping': mock_snap}):
            DiffPrivacy.snapping_func(df, "val")

    def test_snapping_float_no_exception(self):
        """snapping_func runs without error for float column."""
        DiffPrivacy = _dp()
        series = _float_series()
        df = _mock_df({"price": series})
        mock_snap = MagicMock()
        mock_snap.Snapping.return_value.randomise.return_value = 12.5
        with patch.dict(DiffPrivacy.snapping_func.__globals__, {'snapping': mock_snap}):
            DiffPrivacy.snapping_func(df, "price")


# ---------------------------------------------------------------------------
# upload_file (lines 139-163)
# ---------------------------------------------------------------------------

class TestUploadFile:
    def test_upload_file_binary_column_detection(self):
        """upload_file detects columns with exactly 2 unique values."""
        DiffPrivacy = _dp()
        request_id_var = _rid()
        error_dict = _ed()

        mock_file = MagicMock()
        mock_gender = MagicMock()
        mock_gender.unique.return_value = ["M", "F"]
        mock_age = MagicMock()
        mock_age.unique.return_value = [25, 30, 35, 40]
        mock_df = MagicMock()
        mock_df.columns = ["gender", "age"]
        mock_df.__getitem__.side_effect = lambda col: {"gender": mock_gender, "age": mock_age}[col]
        mock_df.select_dtypes.return_value = MagicMock(columns=["age"])

        if request_id_var is None:
            pytest.skip("request_id_var not available")

        token = request_id_var.set("test-upload-binary")
        try:
            error_dict["test-upload-binary"] = []
            with patch.dict(DiffPrivacy.upload_file.__globals__, {
                'pd': MagicMock(**{'read_csv.return_value': mock_df})
            }):
                result = DiffPrivacy.upload_file(mock_file)
            assert "gender" in result.get("binaryHeadder", [])
        finally:
            request_id_var.reset(token)

    def test_upload_file_no_binary_columns(self):
        """upload_file produces empty binaryHeadder when no binary columns."""
        DiffPrivacy = _dp()
        request_id_var = _rid()
        error_dict = _ed()

        mock_file = MagicMock()
        mock_name = MagicMock()
        mock_name.unique.return_value = ["Alice", "Bob", "Carol"]
        mock_df = MagicMock()
        mock_df.columns = ["name"]
        mock_df.__getitem__.side_effect = lambda col: {"name": mock_name}[col]
        mock_df.select_dtypes.return_value = MagicMock(columns=[])

        if request_id_var is None:
            pytest.skip("request_id_var not available")

        token = request_id_var.set("test-upload-no-binary")
        try:
            error_dict["test-upload-no-binary"] = []
            with patch.dict(DiffPrivacy.upload_file.__globals__, {
                'pd': MagicMock(**{'read_csv.return_value': mock_df})
            }):
                result = DiffPrivacy.upload_file(mock_file)
            assert result.get("binaryHeadder", []) == []
        finally:
            request_id_var.reset(token)

    def test_upload_file_exception_raises_runtime_error(self):
        """upload_file catches exceptions and raises RuntimeError."""
        DiffPrivacy = _dp()
        request_id_var = _rid()
        error_dict = _ed()

        mock_file = MagicMock()
        if request_id_var is None:
            pytest.skip("request_id_var not available")

        token = request_id_var.set("test-upload-exc")
        try:
            error_dict["test-upload-exc"] = []
            mock_pd = MagicMock()
            mock_pd.read_csv.side_effect = ValueError("bad csv")
            with patch.dict(DiffPrivacy.upload_file.__globals__, {'pd': mock_pd}):
                with pytest.raises(RuntimeError):
                    DiffPrivacy.upload_file(mock_file)
        finally:
            request_id_var.reset(token)


# ---------------------------------------------------------------------------
# diff_privacy — binary_header (line 195) and range_header (line 198)
# ---------------------------------------------------------------------------

class TestDiffPrivacyHeaders:
    def test_diff_privacy_binary_header_no_exception(self):
        """diff_privacy runs without error when binarylist contains a column name."""
        DiffPrivacy = _dp()
        request_id_var = _rid()
        error_dict = _ed()

        if request_id_var is None:
            pytest.skip("request_id_var not available")

        DiffPrivacy.df = MagicMock()
        payload = {"suppression": "", "noiselist": "", "binarylist": "gender", "range_list": ""}
        token = request_id_var.set("test-dp-bc")
        try:
            error_dict["test-dp-bc"] = []
            with patch.object(DiffPrivacy, "binary_check"), \
                 patch.object(DiffPrivacy, "noise_add"), \
                 patch.object(DiffPrivacy, "range_add"):
                DiffPrivacy.diff_privacy(payload)
        finally:
            request_id_var.reset(token)

    def test_diff_privacy_range_header_no_exception(self):
        """diff_privacy runs without error when range_list contains a column name."""
        DiffPrivacy = _dp()
        request_id_var = _rid()
        error_dict = _ed()

        if request_id_var is None:
            pytest.skip("request_id_var not available")

        DiffPrivacy.df = MagicMock()
        payload = {"suppression": "", "noiselist": "", "binarylist": "", "range_list": "salary"}
        token = request_id_var.set("test-dp-ra")
        try:
            error_dict["test-dp-ra"] = []
            with patch.object(DiffPrivacy, "binary_check"), \
                 patch.object(DiffPrivacy, "noise_add"), \
                 patch.object(DiffPrivacy, "range_add"):
                DiffPrivacy.diff_privacy(payload)
        finally:
            request_id_var.reset(token)

    def test_diff_privacy_both_headers_no_exception(self):
        """diff_privacy runs without error for both binary and range columns."""
        DiffPrivacy = _dp()
        request_id_var = _rid()
        error_dict = _ed()

        if request_id_var is None:
            pytest.skip("request_id_var not available")

        DiffPrivacy.df = MagicMock()
        payload = {"suppression": "", "noiselist": "", "binarylist": "flag", "range_list": "income"}
        token = request_id_var.set("test-dp-both")
        try:
            error_dict["test-dp-both"] = []
            with patch.object(DiffPrivacy, "binary_check"), \
                 patch.object(DiffPrivacy, "noise_add"), \
                 patch.object(DiffPrivacy, "range_add"):
                DiffPrivacy.diff_privacy(payload)
        finally:
            request_id_var.reset(token)
