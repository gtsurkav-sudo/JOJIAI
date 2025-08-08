"""Utility functions for JOJIAI."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def helper_function(data: Union[str, List[Any]], multiplier: int = 1) -> Union[str, List[Any]]:
    """Helper function for data processing.
    
    Args:
        data: Input data (string or list)
        multiplier: Multiplier for numeric operations
        
    Returns:
        Processed data
        
    Raises:
        ValueError: If data is invalid
    """
    if data is None:
        raise ValueError("Data cannot be None")
    
    if isinstance(data, str):
        if not data.strip():
            raise ValueError("String data cannot be empty")
        return data.upper() * multiplier
    
    elif isinstance(data, list):
        if not data:
            raise ValueError("List data cannot be empty")
        return [item * multiplier if isinstance(item, (int, float)) else str(item).upper() 
                for item in data]
    
    else:
        raise ValueError(f"Unsupported data type: {type(data)}")


def format_output(data: Any, format_type: str = "json") -> str:
    """Format output data in specified format.
    
    Args:
        data: Data to format
        format_type: Output format ("json", "text", "csv")
        
    Returns:
        Formatted string
        
    Raises:
        ValueError: If format_type is unsupported
    """
    if format_type == "json":
        return json.dumps(data, indent=2, default=str)
    
    elif format_type == "text":
        if isinstance(data, (list, tuple)):
            return "\n".join(str(item) for item in data)
        else:
            return str(data)
    
    elif format_type == "csv":
        if isinstance(data, (list, tuple)):
            return ",".join(str(item) for item in data)
        else:
            return str(data)
    
    else:
        raise ValueError(f"Unsupported format type: {format_type}")


def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """Load configuration from JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in config file: {e}", e.doc, e.pos)


def save_config(config: Dict[str, Any], config_path: Union[str, Path]) -> None:
    """Save configuration to JSON file.
    
    Args:
        config: Configuration dictionary to save
        config_path: Path where to save configuration
        
    Raises:
        ValueError: If config is not a dictionary
        OSError: If file cannot be written
    """
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a dictionary")
    
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, default=str)
    except OSError as e:
        raise OSError(f"Cannot write config file: {e}")


def validate_data_structure(data: Any, expected_keys: Optional[List[str]] = None) -> bool:
    """Validate data structure against expected format.
    
    Args:
        data: Data to validate
        expected_keys: Expected keys for dictionary validation
        
    Returns:
        True if data structure is valid
    """
    if data is None:
        return False
    
    if expected_keys and isinstance(data, dict):
        return all(key in data for key in expected_keys)
    
    if isinstance(data, (list, tuple)):
        return len(data) > 0
    
    if isinstance(data, str):
        return len(data.strip()) > 0
    
    return True


def create_directory_structure(base_path: Union[str, Path], 
                             directories: List[str]) -> List[Path]:
    """Create directory structure.
    
    Args:
        base_path: Base directory path
        directories: List of directory names to create
        
    Returns:
        List of created directory paths
        
    Raises:
        OSError: If directories cannot be created
    """
    base_path = Path(base_path)
    created_dirs = []
    
    for directory in directories:
        dir_path = base_path / directory
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(dir_path)
        except OSError as e:
            raise OSError(f"Cannot create directory {dir_path}: {e}")
    
    return created_dirs


def setup_logging(log_level: str = "INFO", 
                 log_file: Optional[Union[str, Path]] = None) -> logging.Logger:
    """Setup logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup handlers
    handlers = [logging.StreamHandler()]
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        handlers=handlers,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return logging.getLogger(__name__)