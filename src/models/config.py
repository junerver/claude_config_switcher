"""
Application configuration model.
"""

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any

@dataclass
class AppConfig:
    """Application configuration settings."""

    claude_config_path: Optional[str] = None
    backup_retention_count: int = 10
    log_level: str = "INFO"
    theme: str = "system"  # light, dark, system
    window_width: int = 800
    window_height: int = 600
    auto_refresh: bool = True
    show_confirmations: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """Create AppConfig from dictionary."""
        return cls(**{
            k: v for k, v in data.items()
            if hasattr(cls, k)
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert AppConfig to dictionary."""
        return asdict(self)

    def save_to_file(self, file_path: Path) -> bool:
        """
        Save configuration to file.

        Args:
            file_path: Path to save configuration

        Returns:
            True if saved successfully
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    @classmethod
    def load_from_file(cls, file_path: Path) -> Optional['AppConfig']:
        """
        Load configuration from file.

        Args:
            file_path: Path to load configuration from

        Returns:
            AppConfig instance or None if failed
        """
        try:
            if not file_path.exists():
                return cls()

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception:
            return cls()

def get_default_config_path() -> Path:
    """Get default application configuration file path."""
    if os.name == 'nt':  # Windows
        config_dir = Path(os.environ.get('APPDATA', '')) / 'claude-config-switcher'
    else:  # macOS/Linux
        config_dir = Path.home() / '.config' / 'claude-config-switcher'

    return config_dir / 'config.json'