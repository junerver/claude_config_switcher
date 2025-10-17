"""
Environment and configuration management utilities.
"""

import os
import platform
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .exceptions import ConfigNotFoundError
from .logger import get_logger

logger = get_logger(__name__)

@dataclass
class EnvironmentInfo:
    """Environment information for the application."""

    system: str
    version: str
    python_version: str
    user_home: Path
    app_data_dir: Path
    config_dir: Path
    log_dir: Path
    temp_dir: Path

def get_environment_info() -> EnvironmentInfo:
    """
    Get comprehensive environment information.

    Returns:
        EnvironmentInfo instance with current environment details
    """
    system = platform.system()
    version = platform.version()
    python_version = platform.python_version()
    user_home = Path.home()

    if system == "Windows":
        app_data = Path(os.environ.get('APPDATA', user_home / 'AppData' / 'Roaming'))
        config_dir = app_data / 'claude-config-switcher'
        log_dir = app_data / 'claude-config-switcher' / 'logs'
        temp_dir = Path(os.environ.get('TEMP', user_home / 'temp'))
    elif system == "Darwin":  # macOS
        app_data = user_home / 'Library' / 'Application Support'
        config_dir = user_home / '.config' / 'claude-config-switcher'
        log_dir = user_home / 'Library' / 'Logs' / 'claude-config-switcher'
        temp_dir = Path('/tmp')
    else:  # Linux and others
        app_data = user_home / '.local' / 'share'
        config_dir = user_home / '.config' / 'claude-config-switcher'
        log_dir = user_home / '.local' / 'share' / 'claude-config-switcher' / 'logs'
        temp_dir = Path('/tmp')

    return EnvironmentInfo(
        system=system,
        version=version,
        python_version=python_version,
        user_home=user_home,
        app_data_dir=app_data,
        config_dir=config_dir,
        log_dir=log_dir,
        temp_dir=temp_dir
    )

def ensure_directories() -> Dict[str, Path]:
    """
    Ensure all necessary directories exist.

    Returns:
        Dictionary mapping directory names to their paths
    """
    env_info = get_environment_info()
    directories = {
        'config': env_info.config_dir,
        'logs': env_info.log_dir,
        'temp': env_info.temp_dir,
        'data': Path.cwd() / 'data'
    }

    created = []
    for name, path in directories.items():
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ensured: {path}")
        except OSError as e:
            logger.warning(f"Failed to create {name} directory at {path}: {e}")
        else:
            created.append(name)

    logger.info(f"Created/verified directories: {', '.join(created)}")
    return directories

def get_default_claude_paths() -> Dict[str, Path]:
    """
    Get default Claude Code configuration paths for the current platform.

    Returns:
        Dictionary mapping path types to their default locations
    """
    env_info = get_environment_info()
    user_home = env_info.user_home

    # Standard Claude Code configuration locations
    claude_dir = user_home / '.claude'
    settings_file = claude_dir / 'settings.json'
    backup_dir = claude_dir / 'backups'

    return {
        'claude_dir': claude_dir,
        'settings_file': settings_file,
        'backup_dir': backup_dir
    }

def validate_claude_installation() -> Dict[str, Any]:
    """
    Validate Claude Code installation and configuration.

    Returns:
        Dictionary with validation results
    """
    paths = get_default_claude_paths()
    results = {
        'claude_dir_exists': paths['claude_dir'].exists(),
        'settings_file_exists': paths['settings_file'].exists(),
        'settings_readable': False,
        'settings_writable': False,
        'backup_dir_accessible': False,
        'installation_path': str(paths['claude_dir']),
        'settings_path': str(paths['settings_file'])
    }

    # Check settings file accessibility
    if results['settings_file_exists']:
        try:
            with open(paths['settings_file'], 'r', encoding='utf-8') as f:
                f.read(1)  # Test read access
            results['settings_readable'] = True
        except OSError as e:
            logger.debug(f"Settings file not readable: {e}")

        try:
            # Test write access by opening in append mode (won't modify content)
            with open(paths['settings_file'], 'a', encoding='utf-8'):
                pass
            results['settings_writable'] = True
        except OSError as e:
            logger.debug(f"Settings file not writable: {e}")

    # Check backup directory accessibility
    try:
        paths['backup_dir'].mkdir(parents=True, exist_ok=True)
        # Test write access
        test_file = paths['backup_dir'] / '.access_test'
        test_file.touch()
        test_file.unlink()
        results['backup_dir_accessible'] = True
    except OSError as e:
        logger.debug(f"Backup directory not accessible: {e}")

    return results

def detect_claude_executable() -> Optional[Path]:
    """
    Attempt to detect Claude Code executable path.

    Returns:
        Path to Claude executable if found, None otherwise
    """
    system = platform.system()

    if system == "Windows":
        # Check common Windows locations
        search_paths = [
            Path(os.environ.get('ProgramFiles', 'C:\\Program Files')) / 'Claude',
            Path(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')) / 'Claude',
            Path.home() / 'AppData' / 'Local' / 'Claude',
        ]
        executable_name = 'claude.exe'
    elif system == "Darwin":
        # Check macOS locations
        search_paths = [
            Path('/Applications/Claude.app/Contents/MacOS'),
            Path.home() / 'Applications/Claude.app/Contents/MacOS',
        ]
        executable_name = 'Claude'
    else:
        # Check Linux locations
        search_paths = [
            Path('/usr/local/bin'),
            Path('/usr/bin'),
            Path.home() / '.local' / 'bin',
        ]
        executable_name = 'claude'

    # Search in PATH and specific locations
    all_paths = search_paths + [Path(p) for p in os.environ.get('PATH', '').split(os.pathsep)]

    for path in all_paths:
        if path:
            exe_path = path / executable_name
            if exe_path.exists() and exe_path.is_file():
                try:
                    # Test if executable
                    if system == "Windows":
                        if exe_path.suffix.lower() == '.exe':
                            return exe_path
                    else:
                        if os.access(exe_path, os.X_OK):
                            return exe_path
                except OSError:
                    continue

    return None

def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information for debugging.

    Returns:
        Dictionary with system information
    """
    import sys

    env_info = get_environment_info()
    claude_validation = validate_claude_installation()
    claude_executable = detect_claude_executable()

    return {
        'platform': {
            'system': env_info.system,
            'version': env_info.version,
            'python_version': env_info.python_version,
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
        },
        'paths': {
            'current_working_directory': str(Path.cwd()),
            'user_home': str(env_info.user_home),
            'app_config_dir': str(env_info.config_dir),
            'log_dir': str(env_info.log_dir),
        },
        'claude': {
            **claude_validation,
            'executable_path': str(claude_executable) if claude_executable else None,
        },
        'python': {
            'executable': sys.executable,
            'version': sys.version,
            'platform': sys.platform,
        }
    }

def setup_environment() -> bool:
    """
    Set up the application environment.

    Returns:
        True if setup successful, False otherwise
    """
    try:
        logger.info("Setting up application environment")

        # Create necessary directories
        directories = ensure_directories()

        # Validate Claude Code installation
        validation = validate_claude_installation()
        if not validation['settings_file_exists']:
            logger.warning("Claude Code settings file not found")

        if not validation['settings_writable']:
            logger.warning("Claude Code settings file not writable")

        # Log environment info for debugging
        env_info = get_environment_info()
        logger.info(f"Environment: {env_info.system} {env_info.python_version}")
        logger.info(f"Config directory: {env_info.config_dir}")
        logger.info(f"Log directory: {env_info.log_dir}")

        return True

    except Exception as e:
        logger.error(f"Environment setup failed: {e}")
        return False