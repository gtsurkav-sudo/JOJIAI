"""Unit tests for core functionality."""

import pytest
from unittest.mock import patch, MagicMock

from jojiai.core import JOJIAICore


class TestJOJIAICore:
    """Test cases for JOJIAICore class."""

    def test_init_with_config(self, sample_config):
        """Test initialization with configuration."""
        core = JOJIAICore(config=sample_config)
        assert core.config == sample_config
        assert core.initialized is True

    def test_init_without_config(self):
        """Test initialization without configuration."""
        core = JOJIAICore()
        assert core.config == {}
        assert core.initialized is True

    def test_process_data_success(self, jojiai_core, sample_data):
        """Test successful data processing."""
        result = jojiai_core.process_data(sample_data)
        expected = ["TEST", 84, 6.28, "HELLO", 200]
        assert result == expected

    def test_process_data_empty_list(self, jojiai_core):
        """Test processing empty data list."""
        with pytest.raises(ValueError, match="Data cannot be empty"):
            jojiai_core.process_data([])

    def test_process_data_string_items(self, jojiai_core):
        """Test processing string items."""
        data = ["hello", "world", "test"]
        result = jojiai_core.process_data(data)
        assert result == ["HELLO", "WORLD", "TEST"]

    def test_process_data_numeric_items(self, jojiai_core):
        """Test processing numeric items."""
        data = [1, 2.5, 10, 3.14]
        result = jojiai_core.process_data(data)
        assert result == [2, 5.0, 20, 6.28]

    def test_process_data_mixed_types(self, jojiai_core):
        """Test processing mixed data types."""
        data = [None, [], {}, object()]
        result = jojiai_core.process_data(data)
        assert len(result) == 4
        for item in result:
            assert isinstance(item, str)

    @patch('jojiai.core.logger')
    def test_process_data_logging(self, mock_logger, jojiai_core, sample_data):
        """Test that processing logs correctly."""
        jojiai_core.process_data(sample_data)
        mock_logger.info.assert_called_with(f"Processed {len(sample_data)} items")

    def test_get_status(self, jojiai_core, sample_config):
        """Test status retrieval."""
        status = jojiai_core.get_status()
        assert status["initialized"] is True
        assert status["config_keys"] == list(sample_config.keys())
        assert status["version"] == "0.1.0"

    def test_validate_input_valid_data(self, jojiai_core):
        """Test input validation with valid data."""
        assert jojiai_core.validate_input("test") is True
        assert jojiai_core.validate_input([1, 2, 3]) is True
        assert jojiai_core.validate_input({"key": "value"}) is True
        assert jojiai_core.validate_input(42) is True

    def test_validate_input_invalid_data(self, jojiai_core):
        """Test input validation with invalid data."""
        assert jojiai_core.validate_input(None) is False
        assert jojiai_core.validate_input([]) is False
        assert jojiai_core.validate_input({}) is False
        assert jojiai_core.validate_input("") is False

    @patch('jojiai.core.logger')
    def test_init_logging(self, mock_logger, sample_config):
        """Test that initialization logs correctly."""
        JOJIAICore(config=sample_config)
        mock_logger.info.assert_called_with("JOJIAI Core initialized successfully")