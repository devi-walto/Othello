# othello/tests/unit/test_log.py

import sys
import pytest

from othello.internal.log import (
    DebugLogger,
    dprint,
    LOGGER,
)

# ============================== DebugLogger.start / stop ==============================

def test_start_enables_logger_and_opens_file(tmp_path):
    """start() should enable logging and open the given file."""
    log = DebugLogger()
    log_file = tmp_path / "debug.txt"

    log.start(filename=str(log_file))

    assert log.enabled is True, "Logger should be enabled after start()"
    assert log.file is not None, "Logger should have an open file after start()"
    # Basic sanity: file should exist on disk
    assert log_file.exists(), "Log file should be created by start()"

    # Cleanup
    log.stop()


def test_stop_disables_logger_and_closes_file(tmp_path):
    """stop() should close the file and disable logging."""
    log = DebugLogger()
    log_file = tmp_path / "debug.txt"
    log.start(filename=str(log_file))

    # Keep a reference to the file object to verify it gets closed
    file_obj = log.file

    log.stop()

    assert log.enabled is False, "Logger should be disabled after stop()"
    assert log.file is None or log.enabled is False, "File handle should not be used after stop()"
    # file_obj should be closed (closed attribute is standard on file objects)
    assert file_obj.closed is True, "Underlying file object should be closed by stop()"


# ============================== DebugLogger.write (stdout behavior) ==============================

def test_write_always_prints_to_stdout(capsys, tmp_path):
    """
    write() should always send output to sys.stdout
    regardless of whether logging is enabled.
    """
    log = DebugLogger()
    log_file = tmp_path / "debug.txt"
    log.start(filename=str(log_file))

    log.write("hello world\n")

    captured = capsys.readouterr()
    assert "hello world\n" in captured.out, "write() should print to stdout"

    # Cleanup
    log.stop()


# ============================== DebugLogger.write (file behavior) ==============================

def test_write_writes_to_file_when_enabled(tmp_path):
    """If enabled and file is set, write() should append to the log file."""
    log = DebugLogger()
    log_file = tmp_path / "debug.txt"
    log.start(filename=str(log_file))

    log.write("line 1\n")
    log.write("line 2\n")

    # Make sure data actually hit disk
    log.file.flush()

    content = log_file.read_text(encoding="utf-8")
    assert "line 1\n" in content
    assert "line 2\n" in content

    # Cleanup
    log.stop()


def test_write_does_not_crash_when_disabled(tmp_path, capsys):
    """
    If the logger is disabled or file is None,
    write() should still print to stdout but not write to any file.
    """
    log = DebugLogger()
    log_file = tmp_path / "debug.txt"
    log.start(filename=str(log_file))

    # Manually disable and drop the file handle to simulate "off" state
    log.enabled = False
    log.file = None

    log.write("only to stdout\n")

    captured = capsys.readouterr()
    assert "only to stdout\n" in captured.out, "stdout should still receive output when disabled"

    # File should remain empty because we dropped the handle
    # (We created it via start, but with file=None nothing new should be written)
    if log_file.exists():
        content = log_file.read_text(encoding="utf-8")
        assert content == "" or "only to stdout\n" not in content

    # Cleanup (safe even if file is None)
    log.stop()


# ============================== dprint (integration with LOGGER) ==============================

def test_dprint_calls_logger_write(mocker):
    """
    dprint() should format the message and pass it into LOGGER.write().
    """
    # Patch LOGGER.write to inspect what dprint sends
    mock_write = mocker.patch.object(LOGGER, "write")

    dprint("hello", 123, "world", end="!!\n")

    # dprint joins args with spaces and adds the 'end' string
    mock_write.assert_called_once_with("hello 123 world!!\n")


def test_dprint_uses_newline_by_default(mocker):
    """
    Default end argument for dprint() should be a newline.
    """
    mock_write = mocker.patch.object(LOGGER, "write")

    dprint("line")

    mock_write.assert_called_once_with("line\n")


def test_dprint_integration_with_real_logger(tmp_path, capsys):
    """
    Small integration test:
    - start LOGGER with a real file
    - call dprint()
    - verify output goes to both stdout and the log file.
    """
    # Point LOGGER at a temporary debug file
    log_file = tmp_path / "debug.txt"
    LOGGER.start(filename=str(log_file))

    try:
        dprint("integrated", "message")

        # Check stdout
        captured = capsys.readouterr()
        assert "integrated message\n" in captured.out

        # Check file content
        content = log_file.read_text(encoding="utf-8")
        assert "integrated message\n" in content
    finally:
        # Make sure we always clean up the global logger
        LOGGER.stop()