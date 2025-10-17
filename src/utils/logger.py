"""
Structured logging setup for the configuration switcher application.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Set up structured logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path. If None, uses default location.
        console_output: Whether to output to console

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("claude_config_switcher")
    logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler with rotation
    if log_file is None:
        # Default log directory based on platform
        if os.name == 'nt':  # Windows
            log_dir = Path(os.environ.get('APPDATA', '')) / 'claude-config-switcher' / 'logs'
        else:  # macOS/Linux
            log_dir = Path.home() / '.local' / 'share' / 'claude-config-switcher' / 'logs'

        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'app.log'

    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(f"claude_config_switcher.{name}")