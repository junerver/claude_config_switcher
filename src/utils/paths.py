"""
Path detection and manipulation utilities.
"""

import os
import platform
from pathlib import Path
from typing import Optional

def detect_claude_config_path() -> Optional[Path]:
    """
    Auto-detect Claude Code configuration file path.

    Returns:
        Path to settings.json if found, None otherwise
    """
    system = platform.system()

    if system == "Windows":
        # Windows: C:\Users\<username>\.claude\settings.json
        home = Path(os.environ.get('USERPROFILE', ''))
        config_path = home / '.claude' / 'settings.json'
    elif system == "Darwin":
        # macOS: ~/.claude/settings.json
        home = Path.home()
        config_path = home / '.claude' / 'settings.json'
    else:  # Linux and others
        # Linux: ~/.claude/settings.json
        home = Path.home()
        config_path = home / '.claude' / 'settings.json'

    # Check if file exists and is readable
    if config_path.exists() and config_path.is_file():
        try:
            # Test if we can read the file
            with open(config_path, 'r', encoding='utf-8') as f:
                f.read(1)  # Try to read first character
            return config_path
        except (OSError, UnicodeDecodeError):
            pass

    return None

def get_default_backup_directory(claude_config_path: Path) -> Path:
    """
    Get default backup directory path for the given Claude config.

    Args:
        claude_config_path: Path to Claude settings.json

    Returns:
        Path to backup directory
    """
    claude_dir = claude_config_path.parent
    backup_dir = claude_dir / 'backups'
    return backup_dir

def ensure_directory_exists(path: Path) -> bool:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure exists

    Returns:
        True if directory exists or was created successfully
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False

def is_safe_path(path: Path, base_path: Optional[Path] = None) -> bool:
    """
    Check if a path is safe (no path traversal attempts).

    Args:
        path: Path to check
        base_path: Base path to check against (defaults to user home)

    Returns:
        True if path is safe, False otherwise
    """
    if base_path is None:
        base_path = Path.home()

    try:
        path.resolve().relative_to(base_path.resolve())
        return True
    except (ValueError, OSError):
        return False