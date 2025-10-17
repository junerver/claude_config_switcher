"""
SQLite database operations for profile storage.
"""

import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from ..utils.logger import get_logger

logger = get_logger(__name__)

class Database:
    """SQLite database manager for profile storage."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to database file. If None, uses default location.
        """
        if db_path is None:
            db_path = Path("data") / "profiles.db"

        self.db_path = db_path
        self._local = threading.local()
        self._ensure_database_exists()

    def _ensure_database_exists(self) -> None:
        """Create database and tables if they don't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    config_json TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS backup_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER,
                    backup_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (profile_id) REFERENCES profiles (id) ON DELETE SET NULL
                );

                CREATE INDEX IF NOT EXISTS idx_profiles_name ON profiles(name);
                CREATE INDEX IF NOT EXISTS idx_profiles_active ON profiles(is_active);
                CREATE INDEX IF NOT EXISTS idx_backup_log_profile ON backup_log(profile_id);
            """)
            conn.commit()

        logger.info(f"Database initialized at {self.db_path}")

    @contextmanager
    def get_connection(self):
        """Get a thread-local database connection."""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self._local.connection.row_factory = sqlite3.Row

        try:
            yield self._local.connection
        except Exception:
            self._local.connection.rollback()
            raise

    def close_connection(self) -> None:
        """Close the thread-local connection."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None

    # Profile operations
    def create_profile(
        self,
        name: str,
        config_json: str,
        content_hash: str
    ) -> int:
        """
        Create a new profile.

        Args:
            name: Profile name
            config_json: JSON configuration content
            content_hash: SHA-256 hash of config content

        Returns:
            ID of created profile
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO profiles (name, config_json, content_hash, updated_at)
                VALUES (?, ?, ?, ?)
            """, (name, config_json, content_hash, datetime.now()))
            profile_id = cursor.lastrowid
            conn.commit()

        logger.info(f"Created profile '{name}' with ID {profile_id}")
        return profile_id

    def get_profile(self, profile_id: int) -> Optional[Dict[str, Any]]:
        """
        Get profile by ID.

        Args:
            profile_id: Profile ID

        Returns:
            Profile data or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM profiles WHERE id = ?
            """, (profile_id,))
            row = cursor.fetchone()

        return dict(row) if row else None

    def get_profile_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get profile by name.

        Args:
            name: Profile name

        Returns:
            Profile data or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM profiles WHERE name = ?
            """, (name,))
            row = cursor.fetchone()

        return dict(row) if row else None

    def get_all_profiles(self) -> List[Dict[str, Any]]:
        """
        Get all profiles.

        Returns:
            List of all profiles
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM profiles ORDER BY name
            """)
            rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def get_active_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get currently active profile.

        Returns:
            Active profile data or None if no active profile
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM profiles WHERE is_active = TRUE
            """)
            row = cursor.fetchone()

        return dict(row) if row else None

    def update_profile(
        self,
        profile_id: int,
        name: Optional[str] = None,
        config_json: Optional[str] = None,
        content_hash: Optional[str] = None
    ) -> bool:
        """
        Update profile.

        Args:
            profile_id: Profile ID
            name: New name (optional)
            config_json: New config JSON (optional)
            content_hash: New content hash (optional)

        Returns:
            True if updated successfully
        """
        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)

        if config_json is not None:
            updates.append("config_json = ?")
            params.append(config_json)

        if content_hash is not None:
            updates.append("content_hash = ?")
            params.append(content_hash)

        if not updates:
            return False

        updates.append("updated_at = ?")
        params.append(datetime.now())
        params.append(profile_id)

        with self.get_connection() as conn:
            conn.execute(f"""
                UPDATE profiles
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            conn.commit()

        logger.info(f"Updated profile {profile_id}")
        return True

    def delete_profile(self, profile_id: int) -> bool:
        """
        Delete profile.

        Args:
            profile_id: Profile ID

        Returns:
            True if deleted successfully
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM profiles WHERE id = ?
            """, (profile_id,))
            conn.commit()

        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(f"Deleted profile {profile_id}")

        return deleted

    def set_active_profile(self, profile_id: int) -> bool:
        """
        Set profile as active.

        Args:
            profile_id: Profile ID

        Returns:
            True if set successfully
        """
        with self.get_connection() as conn:
            # First, deactivate all profiles
            conn.execute("""
                UPDATE profiles SET is_active = FALSE
            """)

            # Then activate the specified profile
            cursor = conn.execute("""
                UPDATE profiles SET is_active = TRUE, updated_at = ?
                WHERE id = ?
            """, (datetime.now(), profile_id))
            conn.commit()

        updated = cursor.rowcount > 0
        if updated:
            logger.info(f"Set profile {profile_id} as active")

        return updated

    def clear_active_profile(self) -> None:
        """Clear all active profiles."""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE profiles SET is_active = FALSE
            """)
            conn.commit()

        logger.info("Cleared active profile")

    # Settings operations
    def get_setting(self, key: str) -> Optional[str]:
        """
        Get setting value.

        Args:
            key: Setting key

        Returns:
            Setting value or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT value FROM settings WHERE key = ?
            """, (key,))
            row = cursor.fetchone()

        return row['value'] if row else None

    def set_setting(self, key: str, value: str) -> None:
        """
        Set setting value.

        Args:
            key: Setting key
            value: Setting value
        """
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, value, datetime.now()))
            conn.commit()

        logger.debug(f"Set setting '{key}'")

    # Backup log operations
    def log_backup(self, profile_id: Optional[int], backup_path: str) -> int:
        """
        Log backup creation.

        Args:
            profile_id: Profile ID (optional)
            backup_path: Path to backup file

        Returns:
            Backup log ID
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO backup_log (profile_id, backup_path, created_at)
                VALUES (?, ?, ?)
            """, (profile_id, backup_path, datetime.now()))
            backup_id = cursor.lastrowid
            conn.commit()

        logger.debug(f"Logged backup creation: {backup_path}")
        return backup_id

    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Clean up old backup logs, keeping most recent ones.

        Args:
            keep_count: Number of recent backups to keep

        Returns:
            Number of backup logs removed
        """
        with self.get_connection() as conn:
            # Get IDs to keep
            cursor = conn.execute("""
                SELECT id FROM backup_log
                ORDER BY created_at DESC
                LIMIT ?
            """, (keep_count,))
            keep_ids = [row['id'] for row in cursor.fetchall()]

            if keep_ids:
                # Delete older ones
                cursor = conn.execute("""
                    DELETE FROM backup_log
                    WHERE id NOT IN ({})
                """.format(','.join('?' * len(keep_ids))), keep_ids)
            else:
                # Delete all if none to keep
                cursor = conn.execute("DELETE FROM backup_log")

            deleted_count = cursor.rowcount
            conn.commit()

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old backup log entries")

        return deleted_count