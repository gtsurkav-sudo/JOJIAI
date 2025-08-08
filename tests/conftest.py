"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
from typing import Dict, Any

from jojiai.core import JOJIAICore


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Sample configuration for testing."""
    return {
        "debug": True,
        "max_items": 100,
        "timeout": 30,
        "features": ["feature1", "feature2"]
    }


@pytest.fixture
def jojiai_core(sample_config: Dict[str, Any]) -> JOJIAICore:
    """JOJIAI core instance for testing."""
    return JOJIAICore(config=sample_config)


@pytest.fixture
def sample_data() -> list:
    """Sample data for testing."""
    return ["test", 42, 3.14, "hello", 100]


@pytest.fixture
def temp_config_file(tmp_path: Path, sample_config: Dict[str, Any]) -> Path:
    """Temporary config file for testing."""
    config_file = tmp_path / "test_config.json"
    import json
    with open(config_file, 'w') as f:
        json.dump(sample_config, f)
    return config_file


@pytest.fixture
def empty_data() -> list:
    """Empty data for testing edge cases."""
    return []


@pytest.fixture
def mixed_data() -> list:
    """Mixed data types for testing."""
    return [1, "string", 3.14, None, [], {}]