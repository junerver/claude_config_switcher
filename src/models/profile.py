"""
Profile data model for configuration management.
"""

import json
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

@dataclass
class Profile:
    """Configuration profile model."""

    id: Optional[int] = None
    name: str = ""
    config_json: str = "{}"
    content_hash: str = ""
    is_active: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Profile':
        """Create Profile from dictionary."""
        # Handle datetime conversion
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

        updated_at = data.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))

        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            config_json=data.get('config_json', '{}'),
            content_hash=data.get('content_hash', ''),
            is_active=bool(data.get('is_active', False)),
            created_at=created_at,
            updated_at=updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Profile to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'config_json': self.config_json,
            'content_hash': self.content_hash,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def create_new(cls, name: str, config_json: str) -> 'Profile':
        """
        Create a new profile with calculated hash and timestamps.

        Args:
            name: Profile name
            config_json: JSON configuration content

        Returns:
            New Profile instance
        """
        content_hash = cls.calculate_content_hash(config_json)
        now = datetime.now()

        return cls(
            name=name,
            config_json=config_json,
            content_hash=content_hash,
            created_at=now,
            updated_at=now
        )

    @staticmethod
    def calculate_content_hash(config_json: str) -> str:
        """
        Calculate SHA-256 hash of normalized JSON.

        Args:
            config_json: JSON content string

        Returns:
            SHA-256 hash string
        """
        try:
            # Parse and normalize JSON for consistent hashing
            parsed = json.loads(config_json)
            normalized = json.dumps(parsed, sort_keys=True, separators=(',', ':'))
            return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        except json.JSONDecodeError:
            # If JSON is invalid, hash the raw string
            return hashlib.sha256(config_json.encode('utf-8')).hexdigest()

    def get_config_dict(self) -> Dict[str, Any]:
        """
        Parse and return configuration as dictionary.

        Returns:
            Parsed configuration dictionary
        """
        try:
            return json.loads(self.config_json)
        except json.JSONDecodeError:
            return {}

    def update_config(self, config_json: str) -> None:
        """
        Update configuration and recalculate hash.

        Args:
            config_json: New JSON configuration content
        """
        self.config_json = config_json
        self.content_hash = self.calculate_content_hash(config_json)
        self.updated_at = datetime.now()

    def get_base_url(self) -> str:
        """
        Extract base URL from configuration.

        Returns:
            Base URL if found, empty string otherwise
        """
        config = self.get_config_dict()
        return config.get('env', {}).get('ANTHROPIC_BASE_URL', '')

    def get_auth_token_masked(self) -> str:
        """
        Get masked authentication token.

        Returns:
            Masked token (e.g., "sk-ant...9029") if found, empty string otherwise
        """
        config = self.get_config_dict()
        token = config.get('env', {}).get('ANTHROPIC_AUTH_TOKEN', '')
        if token and len(token) > 10:
            return f"{token[:8]}...{token[-4:]}"
        return token

    def get_model(self) -> str:
        """
        Extract model from configuration.

        Returns:
            Model name if found, empty string otherwise
        """
        config = self.get_config_dict()
        return config.get('model', '')

    def validate(self) -> List[str]:
        """
        Validate profile data.

        Returns:
            List of validation error messages
        """
        errors = []

        if not self.name or not self.name.strip():
            errors.append("Profile name is required")

        if len(self.name) > 100:
            errors.append("Profile name must be 100 characters or less")

        # Check for invalid characters in name
        invalid_chars = ['/', '\\', '..', '\0']
        if any(char in self.name for char in invalid_chars):
            errors.append("Profile name contains invalid characters")

        # Validate JSON
        try:
            json.loads(self.config_json)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON configuration: {e}")

        # Validate hash matches content
        expected_hash = self.calculate_content_hash(self.config_json)
        if self.content_hash != expected_hash:
            errors.append("Content hash does not match configuration")

        return errors

    def __str__(self) -> str:
        """String representation of profile."""
        return f"Profile(id={self.id}, name='{self.name}', active={self.is_active})"

    def __repr__(self) -> str:
        """Detailed string representation of profile."""
        return (f"Profile(id={self.id}, name='{self.name}', "
                f"hash='{self.content_hash[:8]}...', active={self.is_active}, "
                f"created={self.created_at}, updated={self.updated_at})")