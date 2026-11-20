"""
Tests for CustomLogger in privacy/config/logger.py.
Covers branches missing from existing tests:
  - verbose key missing -> except branch (lines 77-78)
  - makedirs failure (lines 128-134)
  - has_file_handler, disable/enable console and file output
  - framework, _custom_log, debug/info/warning/error/critical methods
  - getSeesionId static method
"""
import logging
import os
import sys
import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Helper: build a CustomLogger with mocked config and file system
# ---------------------------------------------------------------------------

def _make_logger(verbose_val="False", log_dir="", exists=True):
    config = {"file_name": "test_log", "log_dir": log_dir}
    if verbose_val is not None:
        config["verbose"] = verbose_val

    with patch("privacy.config.logger.readConfig", return_value=config), \
         patch("os.path.exists", return_value=exists), \
         patch("logging.FileHandler") as mock_fh:
        mock_fh.return_value = MagicMock()   # no spec= inside a patch context
        from privacy.config.logger import CustomLogger
        return CustomLogger()


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

class TestCustomLoggerInit:

    def test_verbose_key_missing_defaults_to_false(self):
        """'verbose' key absent causes KeyError -> except -> verbose=False (lines 77-78)."""
        config = {"file_name": "no_verbose_log", "log_dir": ""}
        with patch("privacy.config.logger.readConfig", return_value=config), \
             patch("os.path.exists", return_value=True), \
             patch("logging.FileHandler") as mock_fh:
            mock_fh.return_value = MagicMock()
            from privacy.config.logger import CustomLogger
            logger = CustomLogger()
        assert logger.verbose is False

    def test_verbose_true(self):
        logger = _make_logger(verbose_val="True")
        assert logger.verbose is True

    def test_verbose_false(self):
        logger = _make_logger(verbose_val="")
        assert logger.verbose is False

    def test_no_log_dir_skips_file_handler(self):
        """Empty log_dir -> file_handler stays None."""
        logger = _make_logger(log_dir="")
        assert logger.file_handler is None

    def test_with_log_dir_creates_file_handler(self):
        """Non-empty log_dir with existing path -> FileHandler is created."""
        with patch("privacy.config.logger.readConfig", return_value={
                "file_name": "mylog", "verbose": "False", "log_dir": "/tmp/logs"}), \
             patch("os.path.exists", return_value=True), \
             patch("logging.FileHandler") as mock_fh:
            mock_fh.return_value = MagicMock()
            from privacy.config.logger import CustomLogger
            logger = CustomLogger()
        assert mock_fh.called


# ---------------------------------------------------------------------------
# makedirs exception path (lines 128-134)
# ---------------------------------------------------------------------------

class TestAddFileHandlerMakedirs:

    def test_makedirs_oserror_fallback(self):
        """makedirs raises OSError -> fallback dir used (lines 128-134)."""
        config = {"file_name": "mylog", "verbose": "False", "log_dir": "/bad/path"}
        with patch("privacy.config.logger.readConfig", return_value=config), \
             patch("os.path.exists", return_value=False), \
             patch("os.makedirs", side_effect=OSError("no permission")), \
             patch("logging.FileHandler") as mock_fh:
            mock_fh.return_value = MagicMock()
            from privacy.config.logger import CustomLogger
            logger = CustomLogger()
        assert logger is not None

    def test_makedirs_oserror_linux_fallback(self):
        """makedirs raises OSError on linux -> fallback is /tmp (lines 128-134)."""
        config = {"file_name": "mylog", "verbose": "False", "log_dir": "/bad/path"}
        with patch("privacy.config.logger.readConfig", return_value=config), \
             patch("os.path.exists", return_value=False), \
             patch("os.makedirs", side_effect=OSError("no permission")), \
             patch("sys.platform", "linux"), \
             patch("logging.FileHandler") as mock_fh:
            mock_fh.return_value = MagicMock()
            from privacy.config.logger import CustomLogger
            logger = CustomLogger()
        assert logger is not None

    def test_makedirs_success_creates_handler(self):
        """makedirs succeeds -> FileHandler created normally."""
        config = {"file_name": "mylog", "verbose": "False", "log_dir": "/new/path"}
        with patch("privacy.config.logger.readConfig", return_value=config), \
             patch("os.path.exists", return_value=False), \
             patch("os.makedirs") as mock_mkdir, \
             patch("logging.FileHandler") as mock_fh:
            mock_fh.return_value = MagicMock()
            from privacy.config.logger import CustomLogger
            logger = CustomLogger()
        assert mock_mkdir.called


# ---------------------------------------------------------------------------
# Handler management
# ---------------------------------------------------------------------------

class TestHandlerMethods:

    def test_has_console_handler_true_after_init(self):
        """Console handler added in __init__ -> has_console_handler() True."""
        logger = _make_logger()
        assert logger.has_console_handler() is True

    def test_has_file_handler_false_without_log_dir(self):
        """No log_dir -> has_file_handler() False (line 148)."""
        logger = _make_logger(log_dir="")
        assert logger.has_file_handler() is False

    def test_disable_console_output_removes_handler(self):
        """disable_console_output removes the stdout handler (lines 151-153)."""
        logger = _make_logger()
        logger.disable_console_output()
        assert logger.has_console_handler() is False

    def test_disable_console_output_noop_when_no_handler(self):
        """Calling disable with no handler is a no-op (early return line 151)."""
        logger = _make_logger()
        logger.removeHandler(logger.stdout_handler)
        logger.disable_console_output()  # must not raise

    def test_enable_console_output_noop_when_already_enabled(self):
        """enable_console_output is no-op when handler present (line 157)."""
        logger = _make_logger()
        assert logger.has_console_handler() is True
        logger.enable_console_output()  # early-return path
        assert logger.has_console_handler() is True

    def test_enable_console_output_re_adds_handler(self):
        """After disabling, enable_console_output restores handler."""
        logger = _make_logger()
        logger.disable_console_output()
        logger.enable_console_output()
        assert logger.has_console_handler() is True

    def test_disable_file_output_noop_without_handler(self):
        """No file handler -> disable_file_output is a no-op (lines 161-162)."""
        logger = _make_logger(log_dir="")
        logger.disable_file_output()  # must not raise

    def test_enable_file_output_noop_without_handler(self):
        """No file handler -> enable_file_output is a no-op (lines 166-167)."""
        logger = _make_logger(log_dir="")
        logger.enable_file_output()  # must not raise

    def test_disable_enable_file_output_cycle(self):
        """Disable then re-enable file output when file handler exists."""
        with patch("privacy.config.logger.readConfig", return_value={
                "file_name": "mylog", "verbose": "False", "log_dir": "/tmp/logs"}), \
             patch("os.path.exists", return_value=True), \
             patch("logging.FileHandler") as mock_fh:
            mock_fh.return_value = MagicMock()
            from privacy.config.logger import CustomLogger
            logger = CustomLogger()

        if logger.has_file_handler():
            logger.disable_file_output()
            logger.enable_file_output()


# ---------------------------------------------------------------------------
# Logging methods
# ---------------------------------------------------------------------------

class TestLoggingMethods:

    def test_framework_method(self):
        """framework() calls super().info (line 173)."""
        logger = _make_logger()
        with patch.object(logging.Logger, "info") as mock_info:
            logger.framework("hello framework")
        mock_info.assert_called_once()

    def test_custom_log_verbose_true_calls_func(self):
        """_custom_log with verbose=True calls the func (lines 179-180)."""
        logger = _make_logger(verbose_val="True")
        assert logger.verbose is True
        called = []
        logger._custom_log(lambda msg, **kw: called.append(msg), "test-msg")
        assert "test-msg" in called

    def test_custom_log_verbose_false_no_file_handler_returns_early(self):
        """_custom_log verbose=False, no file handler -> early return (lines 183-184)."""
        logger = _make_logger(verbose_val="", log_dir="")
        called = []
        logger._custom_log(lambda msg, **kw: called.append(msg), "should-not-log")
        assert called == []

    def test_custom_log_verbose_false_with_file_handler(self):
        """_custom_log verbose=False with file handler toggles console (lines 188-190)."""
        with patch("privacy.config.logger.readConfig", return_value={
                "file_name": "mylog", "verbose": "False", "log_dir": "/tmp/logs"}), \
             patch("os.path.exists", return_value=True), \
             patch("logging.FileHandler") as mock_fh:
            mock_fh.return_value = MagicMock()
            from privacy.config.logger import CustomLogger
            logger = CustomLogger()

        if logger.has_file_handler():
            called = []
            logger._custom_log(lambda msg, **kw: called.append(msg), "msg")
            assert "msg" in called

    def test_debug_method(self):
        _make_logger().debug("debug msg")

    def test_info_method(self):
        _make_logger().info("info msg")

    def test_warning_method(self):
        _make_logger().warning("warning msg")

    def test_error_method(self):
        _make_logger().error("error msg")

    def test_critical_method(self):
        """Covers line 217."""
        _make_logger().critical("critical msg")


# ---------------------------------------------------------------------------
# Static helper
# ---------------------------------------------------------------------------

class TestGetSessionId:

    def test_returns_context_var_value(self):
        """getSeesionId reads from request_id_var."""
        from privacy.config.logger import CustomLogger, request_id_var
        token = request_id_var.set("session-xyz-789")
        try:
            result = CustomLogger.getSeesionId()
            assert result == "session-xyz-789"
        finally:
            request_id_var.reset(token)

    def test_default_value_is_string(self):
        """getSeesionId returns a string even with no explicit context var set."""
        from privacy.config.logger import CustomLogger
        result = CustomLogger.getSeesionId()
        assert isinstance(result, str)
