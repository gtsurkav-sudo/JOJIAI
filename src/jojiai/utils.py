"""Utility functions for JOJIAI project."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Union

logger = logging.getLogger(__name__)


def helper_function(value: Union[str, int, float]) -> str:
    """Helper function for common operations.
    
    Args:
        value: Input value to process.
        
    Returns:
        Processed string value.
    """
    if isinstance(value, str):
        return f"processed_{value}"
    elif isinstance(value, (int, float)):
        return f"number_{value}"
    else:
        return f"unknown_{str(value)}"


def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """Load configuration from JSON file.
    
    Args:
        config_path: Path to configuration file.
        
    Returns:
        Configuration dictionary.
        
    Raises:
        FileNotFoundError: If config file doesn't exist.
        json.JSONDecodeError: If config file is invalid JSON.
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        raise


def save_config(config: Dict[str, Any], config_path: Union[str, Path]) -> None:
    """Save configuration to JSON file.
    
    Args:
        config: Configuration dictionary to save.
        config_path: Path where to save configuration.
    """
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Configuration saved to {config_path}")


def format_output(data: Any, format_type: str = "json") -> str:
    """Format data for output.
    
    Args:
        data: Data to format.
        format_type: Output format type ("json" or "text").
        
    Returns:
        Formatted string.
        
    Raises:
        ValueError: If format_type is not supported.
    """
    if format_type == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)
    elif format_type == "text":
        return str(data)
    else:
        raise ValueError(f"Unsupported format type: {format_type}")