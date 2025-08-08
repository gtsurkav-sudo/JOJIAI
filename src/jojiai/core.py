"""Core functionality for JOJIAI project."""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class JOJIAICore:
    """Main class for JOJIAI functionality."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize JOJIAI core.
        
        Args:
            config: Optional configuration dictionary.
        """
        self.config = config or {}
        self.initialized = True
        logger.info("JOJIAI Core initialized successfully")

    def process_data(self, data: List[Any]) -> List[Any]:
        """Process input data.
        
        Args:
            data: List of data items to process.
            
        Returns:
            Processed data list.
            
        Raises:
            ValueError: If data is empty.
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        processed = []
        for item in data:
            if isinstance(item, str):
                processed.append(item.upper())
            elif isinstance(item, (int, float)):
                processed.append(item * 2)
            else:
                processed.append(str(item))
        
        logger.info(f"Processed {len(processed)} items")
        return processed

    def get_status(self) -> Dict[str, Any]:
        """Get current status.
        
        Returns:
            Status dictionary.
        """
        return {
            "initialized": self.initialized,
            "config_keys": list(self.config.keys()),
            "version": "0.1.0"
        }

    def validate_input(self, input_data: Any) -> bool:
        """Validate input data.
        
        Args:
            input_data: Data to validate.
            
        Returns:
            True if valid, False otherwise.
        """
        if input_data is None:
            return False
        
        if isinstance(input_data, (list, dict, str)) and len(input_data) == 0:
            return False
            
        return True