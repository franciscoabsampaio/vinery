from click.testing import CliRunner
import pytest


@pytest.fixture
def runner():
    """Fixture to provide a CliRunner instance for testing"""
    
    # Replace the actual setup function with the mock
    
    return CliRunner()
