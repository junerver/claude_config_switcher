"""
Configuration service for Claude Code settings.json file operations.
"""

import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from ..utils.logger import get_logger
from ..utils.paths import detect_claude_config_path, get_default_backup_directory
from ..utils.exceptions import (
    ConfigServiceError, ConfigNotFoundError, PermissionError,
    BackupError, ValidationError, InvalidJSONError
)

logger = get_logger(__name__)

class ConfigService:
    """Service for managing Claude Code configuration files."""

    def __init__(self, claude_config_path: Optional[Path] = None):
        """
        Initialize configuration service.

        Args:
            claude_config_path: Path to Claude settings.json. If None, attempts auto-detection.
        """
        self.claude_config_path = claude_config_path or detect_claude_config_path()
        if not self.claude_config_path:
            raise ConfigNotFoundError(str(self.claude_config_path or "auto-detection"))

        self.backup_dir = get_default_backup_directory(self.claude_config_path)

    def read_settings(self) -> Optional[str]:
        """
        Read Claude Code settings.json content.

        Returns:
            JSON content string if file exists and readable, None otherwise
        """
        try:
            if not self.claude_config_path.exists():
                logger.warning(f"Settings file not found: {self.claude_config_path}")
                return None

            with open(self.claude_config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Validate JSON syntax
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                raise InvalidJSONError(str(e))

            logger.debug(f"Read settings file: {self.claude_config_path} ({len(content)} bytes)")
            return content

        except (OSError, UnicodeDecodeError) as e:
            logger.error(f"Failed to read settings file: {e}")
            raise ConfigServiceError("read_settings", str(self.claude_config_path), str(e))

    def write_settings(self, config_json: str) -> bool:
        """
        Write configuration to Claude Code settings.json.

        Args:
            config_json: Valid JSON content string

        Returns:
            True if write successful, False on failure
        """
        try:
            # Validate JSON syntax
            try:
                json.loads(config_json)
            except json.JSONDecodeError as e:
                raise InvalidJSONError(str(e))

            # Ensure directory exists
            self.claude_config_path.parent.mkdir(parents=True, exist_ok=True)

            # Atomic write using temporary file
            return self._atomic_write(self.claude_config_path, config_json)

        except Exception as e:
            logger.error(f"Failed to write settings file: {e}")
            raise

    def _atomic_write(self, target_path: Path, content: str) -> bool:
        """
        Perform atomic write operation.

        Args:
            target_path: Target file path
            content: Content to write

        Returns:
            True if successful
        """
        temp_path = target_path.with_suffix('.tmp')

        try:
            # Write to temporary file
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(content)
                f.flush()  # Ensure written to disk
                os.fsync(f.fileno())  # Force write to disk

            # Atomic rename
            os.replace(temp_path, target_path)

            logger.info(f"Successfully wrote settings file: {target_path} ({len(content)} bytes)")
            return True

        except OSError as e:
            # Clean up temporary file on error
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass
            raise ConfigServiceError("atomic_write", str(target_path), str(e))

    def create_backup(self, backup_path: Optional[str] = None) -> str:
        """
        Create backup of current settings.json.

        Args:
            backup_path: Optional custom backup path

        Returns:
            Full path to created backup file
        """
        try:
            if not self.claude_config_path.exists():
                raise ConfigNotFoundError(str(self.claude_config_path))

            # Generate backup filename if not provided
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"settings.json.backup.{timestamp}"
                backup_path = self.backup_dir / backup_filename
            else:
                backup_path = Path(backup_path)

            # Ensure backup directory exists
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(self.claude_config_path, backup_path)

            file_size = backup_path.stat().st_size
            logger.info(f"Created backup: {backup_path} ({file_size} bytes)")

            return str(backup_path)

        except OSError as e:
            raise BackupError("create", str(e))

    def list_backups(self) -> List[str]:
        """
        List available backup files.

        Returns:
            List of backup file paths sorted by creation time (newest first)
        """
        try:
            if not self.backup_dir.exists():
                return []

            # Find backup files matching pattern
            backup_pattern = "settings.json.backup.*"
            backup_files = list(self.backup_dir.glob(backup_pattern))

            # Sort by modification time (newest first)
            backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            return [str(f) for f in backup_files]

        except OSError as e:
            logger.error(f"Failed to list backups: {e}")
            return []

    def restore_backup(self, backup_path: str) -> bool:
        """
        Restore settings.json from backup.

        Args:
            backup_path: Path to backup file

        Returns:
            True if restore successful
        """
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise ConfigNotFoundError(backup_path)

            # Validate backup file content
            with open(backup_file, 'r', encoding='utf-8') as f:
                content = f.read()
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                raise InvalidJSONError(f"Invalid JSON in backup: {e}")

            # Create backup of current settings before restore
            if self.claude_config_path.exists():
                self.create_backup()

            # Restore from backup
            return self._atomic_write(self.claude_config_path, content)

        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            raise BackupError("restore", str(e))

    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Remove old backup files, keeping most recent ones.

        Args:
            keep_count: Number of most recent backups to keep

        Returns:
            Number of backup files removed
        """
        try:
            backup_files = self.list_backups()
            if len(backup_files) <= keep_count:
                return 0

            # Files to remove (older ones)
            files_to_remove = backup_files[keep_count:]
            removed_count = 0

            for backup_file in files_to_remove:
                try:
                    Path(backup_file).unlink()
                    removed_count += 1
                    logger.debug(f"Removed old backup: {backup_file}")
                except OSError as e:
                    logger.warning(f"Failed to remove backup {backup_file}: {e}")

            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old backup files")

            return removed_count

        except Exception as e:
            logger.error(f"Failed to cleanup backups: {e}")
            return 0

    def calculate_content_hash(self, config_json: str) -> str:
        """
        Calculate SHA-256 hash of normalized JSON.

        Args:
            config_json: JSON content string

        Returns:
            SHA-256 hash string
        """
        import hashlib

        try:
            # Parse and normalize JSON for consistent hashing
            parsed = json.loads(config_json)
            normalized = json.dumps(parsed, sort_keys=True, separators=(',', ':'))
            return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        except json.JSONDecodeError:
            # If JSON is invalid, hash the raw string
            return hashlib.sha256(config_json.encode('utf-8')).hexdigest()

    def get_current_hash(self) -> Optional[str]:
        """
        Calculate hash of current settings file.

        Returns:
            Current content hash or None if file doesn't exist
        """
        content = self.read_settings()
        return self.calculate_content_hash(content) if content else None

    def compare_with_current(self, config_json: str) -> bool:
        """
        Compare configuration with current settings.

        Args:
            config_json: Configuration to compare

        Returns:
            True if different from current, False if same
        """
        current_hash = self.get_current_hash()
        new_hash = self.calculate_content_hash(config_json)
        return current_hash != new_hash

    def validate_config(self, config_json: str) -> List[str]:
        """
        Validate configuration JSON.

        Args:
            config_json: JSON content to validate

        Returns:
            List of validation error messages
        """
        errors = []

        # Check JSON syntax
        try:
            parsed = json.loads(config_json)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON syntax: {e}")
            return errors

        # Basic structure validation
        if not isinstance(parsed, dict):
            errors.append("Configuration must be a JSON object")
            return errors

        # Check for common Claude Code configuration structure
        if 'env' in parsed:
            env = parsed['env']
            if not isinstance(env, dict):
                errors.append("'env' must be an object")
            else:
                # Check for common environment variables
                if 'ANTHROPIC_BASE_URL' in env:
                    base_url = env['ANTHROPIC_BASE_URL']
                    if not isinstance(base_url, str) or not base_url.strip():
                        errors.append("ANTHROPIC_BASE_URL must be a non-empty string")

                if 'ANTHROPIC_AUTH_TOKEN' in env:
                    token = env['ANTHROPIC_AUTH_TOKEN']
                    if not isinstance(token, str) or not token.strip():
                        errors.append("ANTHROPIC_AUTH_TOKEN must be a non-empty string")

        return errors

    def get_settings_info(self) -> Dict[str, Any]:
        """
        Get information about current settings file.

        Returns:
            Dictionary with settings file information
        """
        info = {
            'path': str(self.claude_config_path),
            'exists': self.claude_config_path.exists(),
            'readable': False,
            'writable': False,
            'size': 0,
            'modified': None,
            'hash': None,
            'backup_count': len(self.list_backups()),
            'backup_dir': str(self.backup_dir)
        }

        if info['exists']:
            try:
                stat = self.claude_config_path.stat()
                info['size'] = stat.st_size
                info['modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()

                # Test readability
                with open(self.claude_config_path, 'r', encoding='utf-8') as f:
                    f.read(1)
                info['readable'] = True

                # Test writability
                with open(self.claude_config_path, 'a', encoding='utf-8'):
                    pass
                info['writable'] = True

                # Calculate hash
                content = self.read_settings()
                if content:
                    info['hash'] = self.calculate_content_hash(content)

            except Exception as e:
                logger.debug(f"Failed to get settings info: {e}")

        return info