"""JOJIAI - AI-powered project with comprehensive CI/CD pipeline."""

__version__ = "0.1.0"
__author__ = "JOJIAI Team"
__email__ = "team@jojiai.com"

from .core import JOJIAICore
from .utils import helper_function

__all__ = ["JOJIAICore", "helper_function", "__version__"]