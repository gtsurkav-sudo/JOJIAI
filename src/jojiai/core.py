"""Core JOJIAI functionality."""

import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


class JOJIAICore:
    """Core JOJIAI processing engine."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize JOJIAI core with optional configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.initialized = True
        self.version = "0.1.0"
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config.get('log_level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def process_data(self, data: Union[List[Any], str, int, float]) -> List[Any]:
        """Process input data and return transformed results.
        
        Args:
            data: Input data to process
            
        Returns:
            List of processed data items
            
        Raises:
            ValueError: If data is invalid
        """
        if data is None:
            raise ValueError("Data cannot be None")
            
        if isinstance(data, (list, tuple)):
            if not data:
                raise ValueError("Data cannot be empty")
            return [self._transform_item(item) for item in data]
        else:
            return [self._transform_item(data)]
    
    def _transform_item(self, item: Any) -> Any:
        """Transform a single data item.
        
        Args:
            item: Item to transform
            
        Returns:
            Transformed item
        """
        if isinstance(item, str):
            return item.upper()
        elif isinstance(item, (int, float)):
            return item * 2
        else:
            return str(item).upper()
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        if data is None:
            return False
        if isinstance(data, (list, tuple)) and len(data) == 0:
            return False
        if isinstance(data, str) and len(data.strip()) == 0:
            return False
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status.
        
        Returns:
            Dictionary containing system status information
        """
        return {
            "initialized": self.initialized,
            "version": self.version,
            "config_keys": len(self.config.keys()),
            "has_config": bool(self.config)
        }
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update system configuration.
        
        Args:
            new_config: New configuration to merge
        """
        if not isinstance(new_config, dict):
            raise ValueError("Configuration must be a dictionary")
        self.config.update(new_config)
        self._setup_logging()  # Refresh logging if config changed
    
    def reset(self) -> None:
        """Reset the system to initial state."""
        self.config = {}
        self.initialized = True
        self._setup_logging()