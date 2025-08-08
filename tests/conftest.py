"""Pytest configuration and shared fixtures."""

import pytest
import tempfile
import json
from pathlib import Path
from jojiai.core import JOJIAICore
from jojiai.utils import save_config


@pytest.fixture
def sample_data():
    """Sample data for testing."""
    return ["test", "data", 123, 45.6]


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "debug": True,
        "max_items": 1000,
        "timeout": 30,
        "log_level": "INFO"
    }


@pytest.fixture
def jojiai_core(sample_config):
    """JOJIAI core instance with sample configuration."""
    return JOJIAICore(config=sample_config)


@pytest.fixture
def temp_config_file(sample_config):
    """Temporary configuration file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_config, f)
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_directory():
    """Temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_api_responses():
    """Mock API responses for testing."""
    return {
        "health": {"status": "healthy", "version": "0.1.0"},
        "process": {"result": "processed", "count": 4},
        "config": {"debug": True, "max_items": 1000},
        "status": {"initialized": True, "version": "0.1.0"}
    }


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration after each test."""
    import logging
    yield
    # Clear all handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.root.setLevel(logging.WARNING)