import os
from pathlib import Path
import pytest
from vinery import io


@pytest.fixture
def directories_mock():
    return {"tmp": "tmp_test_dir"}


@pytest.fixture
def setup_tmp_dir(tmp_path):
    tmp_dir = tmp_path / "tmp_test_dir"
    tmp_dir.mkdir()
    return tmp_dir


def test_setup_directories(tmp_path):
    # Define mock directories with temporary paths
    mock_directories = {
        "config": tmp_path / "config",
        "logs": tmp_path / "logs",
        "data": tmp_path / "data"
    }
    
    io.setup_directories(directories=mock_directories)
    
    # Assert that all directories are created
    for dir_path in mock_directories.values():
        assert dir_path.exists() and dir_path.is_dir()


def test_set_log_level(monkeypatch):
    monkeypatch.delenv("VINE_LOG_LEVEL", raising=False)
    io.set_log_level("DEBUG")
    assert os.getenv("VINE_LOG_LEVEL") == "DEBUG"

    pytest.raises(ValueError, io.set_log_level, "INVALID_LOG_LEVEL")


def test_read_file_not_found(directories_mock, monkeypatch):
    monkeypatch.setenv("VINE_LOG_LEVEL", "WARNING")
    monkeypatch.setattr("vinery.io.DIRECTORIES", directories_mock)
    result = io.read_file("nonexistent.txt")
    assert result == set()  # Should return an empty set when file is missing


def test_read_file_success(setup_tmp_dir, directories_mock, monkeypatch):
    monkeypatch.setattr("vinery.io.DIRECTORIES", directories_mock)
    filename = setup_tmp_dir / "test.txt"
    filename.write_text("\n\nline1\nline2\n")

    result = io.read_file(filename)
    assert result == {"line1", "line2"}


def test_update_file(setup_tmp_dir, directories_mock, monkeypatch):
    monkeypatch.setattr("vinery.io.DIRECTORIES", directories_mock)
    filename = setup_tmp_dir / "test.txt"
    io.update_file(filename, ["new_line1\n", "new_line2\n"])
    
    # Verify file contents
    result = io.read_file(filename)
    assert result == {"new_line1", "new_line2"}
    
    # Append more lines and check
    io.update_file(filename, ["extra_line\n"])
    result = io.read_file(filename)
    assert result == {"new_line1", "new_line2", "extra_line"}


def test_echo_suppressed(capsys, monkeypatch):
    monkeypatch.setenv("VINE_LOG_LEVEL", "ERROR")  # Suppress non-error messages
    io.echo("This should not be printed", "INFO")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_echo_invalid_level(capsys):
    with pytest.raises(ValueError):
        io.echo("Invalid level test", "INVALID")
