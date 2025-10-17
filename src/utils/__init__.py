"""
Utility modules for the configuration switcher application.
"""

from .logger import setup_logging
from .paths import detect_claude_config_path

__all__ = ["setup_logging", "detect_claude_config_path"]