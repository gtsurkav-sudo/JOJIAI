"""Unit tests for utility functions."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from jojiai.utils import (
    helper_function,
    load_config,
    save_config,
    format_output
)


class TestHelperFunction:
    """Test cases for helper_function."""

    def test_helper_function_string(self):
        """Test helper function with string input."""
        result = helper_function("test")
        assert result == "processed_test"

    def test_helper_function_integer(self):
        """Test helper function with integer input."""
        result = helper_function(42)
        assert result == "number_42"

    def test_helper_function_float(self):
        """Test helper function with float input."""
        result = helper_function(3.14)
        assert result == "number_3.14"

    def test_helper_function_other_types(self):
        """Test helper function with other types."""
        result = helper_function(None)
        assert result == "unknown_None"
        
        result = helper_function([1, 2, 3])
        assert result == "unknown_[1, 2, 3]"


class TestLoadConfig:
    """Test cases for load_config function."""

    def test_load_config_success(self, temp_config_file, sample_config):
        """Test successful config loading."""
        result = load_config(temp_config_file)
        assert result == sample_config

    def test_load_config_file_not_found(self):
        """Test config loading with non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_config("non_existent_file.json")

    def test_load_config_invalid_json(self, tmp_path):
        """Test config loading with invalid JSON."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("invalid json content")
        
        with pytest.raises(json.JSONDecodeError):
            load_config(invalid_file)

    @patch('jojiai.utils.logger')
    def test_load_config_logging(self, mock_logger, temp_config_file, sample_config):
        """Test that config loading logs correctly."""
        load_config(temp_config_file)
        mock_logger.info.assert_called_with(f"Configuration loaded from {temp_config_file}")

    @patch('jojiai.utils.logger')
    def test_load_config_error_logging(self, mock_logger, tmp_path):
        """Test that config loading errors are logged."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("invalid json")
        
        with pytest.raises(json.JSONDecodeError):
            load_config(invalid_file)
        
        mock_logger.error.assert_called_once()


class TestSaveConfig:
    """Test cases for save_config function."""

    def test_save_config_success(self, tmp_path, sample_config):
        """Test successful config saving."""
        config_file = tmp_path / "saved_config.json"
        save_config(sample_config, config_file)
        
        assert config_file.exists()
        with open(config_file, 'r') as f:
            saved_config = json.load(f)
        assert saved_config == sample_config

    def test_save_config_creates_directory(self, tmp_path, sample_config):
        """Test that save_config creates parent directories."""
        config_file = tmp_path / "subdir" / "config.json"
        save_config(sample_config, config_file)
        
        assert config_file.exists()
        assert config_file.parent.exists()

    @patch('jojiai.utils.logger')
    def test_save_config_logging(self, mock_logger, tmp_path, sample_config):
        """Test that config saving logs correctly."""
        config_file = tmp_path / "config.json"
        save_config(sample_config, config_file)
        mock_logger.info.assert_called_with(f"Configuration saved to {config_file}")


class TestFormatOutput:
    """Test cases for format_output function."""

    def test_format_output_json(self, sample_config):
        """Test JSON formatting."""
        result = format_output(sample_config, "json")
        expected = json.dumps(sample_config, indent=2, ensure_ascii=False)
        assert result == expected

    def test_format_output_text(self, sample_config):
        """Test text formatting."""
        result = format_output(sample_config, "text")
        assert result == str(sample_config)

    def test_format_output_invalid_format(self, sample_config):
        """Test formatting with invalid format type."""
        with pytest.raises(ValueError, match="Unsupported format type: invalid"):
            format_output(sample_config, "invalid")

    def test_format_output_default_json(self, sample_config):
        """Test default JSON formatting."""
        result = format_output(sample_config)
        expected = json.dumps(sample_config, indent=2, ensure_ascii=False)
        assert result == expected