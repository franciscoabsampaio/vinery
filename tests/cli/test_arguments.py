import pytest
import click
from click.testing import CliRunner
from vinery.cli.arguments import argument_plan


# Test function decorated with argument_plan
@click.command()
@argument_plan
def dummy_command(plan):
    return plan


@pytest.fixture
def runner():
    """Provide a Click testing runner."""
    return CliRunner()


def test_argument_plan_valid_input(runner, monkeypatch):
    # Test valid input (single and multiple plans)
    monkeypatch.setenv("VINE_LOG_LEVEL", "DEBUG")
    dummy_plans = ['plan1', 'plan2']
    result = runner.invoke(dummy_command, dummy_plans)

    # Assert no errors, and check if the output is correct
    assert result.exit_code == 0
    for plan in dummy_plans:
        assert plan in result.output


def test_argument_plan_empty_input(runner):
    # Test case where no plans are provided
    result = runner.invoke(dummy_command, [])

    # Assert that no error message is shown
    assert result.exit_code == 0


def test_argument_plan_invalid_input(runner):
    # Test invalid input (if any specific error conditions are triggered by the callback logic)
    result = runner.invoke(dummy_command, ['/'])

    assert result.exit_code == 1
    assert "Invalid plan provided. Plans must not be '/'." in result.output
