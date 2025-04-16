import os
from vinery.cli import cli


def test_cli_log_level(runner, monkeypatch):
    """Test the CLI command with provided log_level and path_to_library"""
    monkeypatch.delenv("VINE_LOG_LEVEL", raising=False)
    
    result = runner.invoke(cli.cli, ['version'])
    assert result.exit_code == 0
    # Assert that log-level is not shown if it is the default
    assert '--log-level: INFO' not in result.output
    assert 'INFO' == os.getenv("VINE_LOG_LEVEL")


def test_cli_with_default_path_to_library(runner, monkeypatch):
    # Assert that the path_to_library is the default
    monkeypatch.delenv("VINE_LOG_LEVEL")
    monkeypatch.setenv("VINE_LOG_LEVEL", "DEBUG")

    result = runner.invoke(cli.cli, ['version'])
    assert '--path-to-library: ./library' in result.output


def test_cli_with_log_level_and_path(runner, tmp_path, monkeypatch):
    # Assert log_level and path_to_library are set correctly
    monkeypatch.delenv("VINE_LOG_LEVEL")

    result = runner.invoke(cli.cli, ['-l', 'DEBUG', '-p', tmp_path, 'version'])
    assert result.exit_code == 0
    assert '--log-level: DEBUG' in result.output
    assert f'--path-to-library: {tmp_path}' in result.output
