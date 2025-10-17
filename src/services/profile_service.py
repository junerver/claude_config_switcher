"""
Profile service for profile CRUD operations.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..models.profile import Profile
from ..storage.database import Database
from ..utils.logger import get_logger
from ..utils.exceptions import (
    ProfileError, ProfileNotFoundError, ProfileAlreadyExistsError,
    ActiveProfileProtectedError, ValidationError, DatabaseError
)

logger = get_logger(__name__)

class ProfileService:
    """Service for managing configuration profiles."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize profile service.

        Args:
            db_path: Path to database file. If None, uses default location.
        """
        self.database = Database(db_path)

    def create_profile(self, name: str, config_json: str) -> int:
        """
        Create a new configuration profile.

        Args:
            name: Profile name (must be unique)
            config_json: JSON configuration content

        Returns:
            ID of created profile

        Raises:
            ProfileAlreadyExistsError: If profile name already exists
            ValidationError: If configuration is invalid
        """
        # Validate inputs
        validation_errors = self._validate_profile_data(name, config_json)
        if validation_errors:
            raise ValidationError("; ".join(validation_errors))

        # Check if name already exists
        if self.database.get_profile_by_name(name):
            raise ProfileAlreadyExistsError(name)

        # Create profile model
        profile = Profile.create_new(name, config_json)

        try:
            profile_id = self.database.create_profile(
                name=profile.name,
                config_json=profile.config_json,
                content_hash=profile.content_hash
            )

            logger.info(f"Created profile '{name}' with ID {profile_id}")
            return profile_id

        except Exception as e:
            logger.error(f"Failed to create profile '{name}': {e}")
            raise DatabaseError("ProfileService", "create_profile", str(e))

    def get_profile(self, profile_id: int) -> Optional[Profile]:
        """
        Get profile by ID.

        Args:
            profile_id: Profile ID

        Returns:
            Profile instance or None if not found
        """
        try:
            profile_data = self.database.get_profile(profile_id)
            return Profile.from_dict(profile_data) if profile_data else None

        except Exception as e:
            logger.error(f"Failed to get profile {profile_id}: {e}")
            raise DatabaseError("ProfileService", "get_profile", str(e))

    def get_profile_by_name(self, name: str) -> Optional[Profile]:
        """
        Get profile by name.

        Args:
            name: Profile name

        Returns:
            Profile instance or None if not found
        """
        try:
            profile_data = self.database.get_profile_by_name(name)
            return Profile.from_dict(profile_data) if profile_data else None

        except Exception as e:
            logger.error(f"Failed to get profile '{name}': {e}")
            raise DatabaseError("ProfileService", "get_profile_by_name", str(e))

    def get_profile_by_name_or_id(self, profile_id_or_name: str) -> Optional[Profile]:
        """
        Get profile by ID or name.

        Args:
            profile_id_or_name: Profile ID (as string) or name

        Returns:
            Profile instance or None if not found
        """
        # Try to parse as integer ID first
        try:
            profile_id = int(profile_id_or_name)
            return self.get_profile(profile_id)
        except ValueError:
            # Not an integer, treat as name
            return self.get_profile_by_name(profile_id_or_name)

    def get_all_profiles(self) -> List[Profile]:
        """
        Get all profiles.

        Returns:
            List of all profiles sorted by name
        """
        try:
            profiles_data = self.database.get_all_profiles()
            return [Profile.from_dict(data) for data in profiles_data]

        except Exception as e:
            logger.error(f"Failed to get all profiles: {e}")
            raise DatabaseError("ProfileService", "get_all_profiles", str(e))

    def get_active_profile(self) -> Optional[Profile]:
        """
        Get currently active profile.

        Returns:
            Active profile instance or None if no active profile
        """
        try:
            profile_data = self.database.get_active_profile()
            return Profile.from_dict(profile_data) if profile_data else None

        except Exception as e:
            logger.error(f"Failed to get active profile: {e}")
            raise DatabaseError("ProfileService", "get_active_profile", str(e))

    def update_profile(
        self,
        profile_id: int,
        name: Optional[str] = None,
        config_json: Optional[str] = None
    ) -> bool:
        """
        Update an existing profile.

        Args:
            profile_id: Profile ID
            name: New profile name (optional)
            config_json: New configuration JSON (optional)

        Returns:
            True if updated successfully

        Raises:
            ProfileNotFoundError: If profile doesn't exist
            ProfileAlreadyExistsError: If new name already exists
            ValidationError: If new configuration is invalid
        """
        # Get existing profile
        profile = self.get_profile(profile_id)
        if not profile:
            raise ProfileNotFoundError(str(profile_id))

        # Validate new name if provided
        if name and name != profile.name:
            if self.database.get_profile_by_name(name):
                raise ProfileAlreadyExistsError(name)

            validation_errors = self._validate_profile_name(name)
            if validation_errors:
                raise ValidationError("; ".join(validation_errors))

        # Validate new configuration if provided
        if config_json:
            validation_errors = self._validate_config_json(config_json)
            if validation_errors:
                raise ValidationError("; ".join(validation_errors))

        # Calculate new hash if configuration changed
        content_hash = None
        if config_json:
            content_hash = Profile.calculate_content_hash(config_json)

        try:
            success = self.database.update_profile(
                profile_id=profile_id,
                name=name,
                config_json=config_json,
                content_hash=content_hash
            )

            if success:
                logger.info(f"Updated profile {profile_id}")
            return success

        except Exception as e:
            logger.error(f"Failed to update profile {profile_id}: {e}")
            raise DatabaseError("ProfileService", "update_profile", str(e))

    def delete_profile(self, profile_id: int) -> bool:
        """
        Delete a profile.

        Args:
            profile_id: Profile ID

        Returns:
            True if deleted successfully

        Raises:
            ProfileNotFoundError: If profile doesn't exist
            ActiveProfileProtectedError: If trying to delete active profile
        """
        # Get profile to check if it's active
        profile = self.get_profile(profile_id)
        if not profile:
            raise ProfileNotFoundError(str(profile_id))

        if profile.is_active:
            raise ActiveProfileProtectedError(profile.name)

        try:
            success = self.database.delete_profile(profile_id)
            if success:
                logger.info(f"Deleted profile '{profile.name}' (ID: {profile_id})")
            return success

        except Exception as e:
            logger.error(f"Failed to delete profile {profile_id}: {e}")
            raise DatabaseError("ProfileService", "delete_profile", str(e))

    def set_active_profile(self, profile_id: int) -> bool:
        """
        Set a profile as active.

        Args:
            profile_id: Profile ID

        Returns:
            True if set successfully

        Raises:
            ProfileNotFoundError: If profile doesn't exist
        """
        # Verify profile exists
        profile = self.get_profile(profile_id)
        if not profile:
            raise ProfileNotFoundError(str(profile_id))

        try:
            success = self.database.set_active_profile(profile_id)
            if success:
                logger.info(f"Set profile '{profile.name}' (ID: {profile_id}) as active")
            return success

        except Exception as e:
            logger.error(f"Failed to set active profile {profile_id}: {e}")
            raise DatabaseError("ProfileService", "set_active_profile", str(e))

    def clear_active_profile(self) -> None:
        """Clear all active profiles."""
        try:
            self.database.clear_active_profile()
            logger.info("Cleared active profile")

        except Exception as e:
            logger.error(f"Failed to clear active profile: {e}")
            raise DatabaseError("ProfileService", "clear_active_profile", str(e))

    def duplicate_profile(self, source_profile_id: int, new_name: str) -> int:
        """
        Create a duplicate of an existing profile.

        Args:
            source_profile_id: Source profile ID
            new_name: Name for the duplicated profile

        Returns:
            ID of the new profile

        Raises:
            ProfileNotFoundError: If source profile doesn't exist
            ProfileAlreadyExistsError: If new name already exists
            ValidationError: If new name is invalid
        """
        # Get source profile
        source_profile = self.get_profile(source_profile_id)
        if not source_profile:
            raise ProfileNotFoundError(str(source_profile_id))

        # Validate new name
        validation_errors = self._validate_profile_name(new_name)
        if validation_errors:
            raise ValidationError("; ".join(validation_errors))

        # Check if new name already exists
        if self.database.get_profile_by_name(new_name):
            raise ProfileAlreadyExistsError(new_name)

        # Create duplicate
        try:
            new_profile_id = self.database.create_profile(
                name=new_name,
                config_json=source_profile.config_json,
                content_hash=source_profile.content_hash
            )

            logger.info(f"Duplicated profile '{source_profile.name}' to '{new_name}' (ID: {new_profile_id})")
            return new_profile_id

        except Exception as e:
            logger.error(f"Failed to duplicate profile {source_profile_id}: {e}")
            raise DatabaseError("ProfileService", "duplicate_profile", str(e))

    def search_profiles(self, query: str) -> List[Profile]:
        """
        Search profiles by name or configuration content.

        Args:
            query: Search query

        Returns:
            List of matching profiles
        """
        try:
            all_profiles = self.get_all_profiles()
            query_lower = query.lower()

            matching_profiles = []
            for profile in all_profiles:
                # Search in name
                if query_lower in profile.name.lower():
                    matching_profiles.append(profile)
                    continue

                # Search in configuration content
                config_dict = profile.get_config_dict()
                if self._search_in_dict(config_dict, query_lower):
                    matching_profiles.append(profile)

            return matching_profiles

        except Exception as e:
            logger.error(f"Failed to search profiles: {e}")
            raise DatabaseError("ProfileService", "search_profiles", str(e))

    def get_profile_count(self) -> int:
        """
        Get total number of profiles.

        Returns:
            Number of profiles
        """
        try:
            return len(self.database.get_all_profiles())

        except Exception as e:
            logger.error(f"Failed to get profile count: {e}")
            return 0

    def _validate_profile_data(self, name: str, config_json: str) -> List[str]:
        """Validate profile data."""
        errors = []

        # Validate name
        errors.extend(self._validate_profile_name(name))

        # Validate configuration
        errors.extend(self._validate_config_json(config_json))

        return errors

    def _validate_profile_name(self, name: str) -> List[str]:
        """Validate profile name."""
        errors = []

        if not name or not name.strip():
            errors.append("Profile name is required")

        if len(name) > 100:
            errors.append("Profile name must be 100 characters or less")

        # Check for invalid characters
        invalid_chars = ['/', '\\', '..', '\0']
        if any(char in name for char in invalid_chars):
            errors.append("Profile name contains invalid characters")

        return errors

    def _validate_config_json(self, config_json: str) -> List[str]:
        """Validate JSON configuration."""
        errors = []

        try:
            import json
            json.loads(config_json)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON configuration: {e}")

        return errors

    def _search_in_dict(self, data: Dict[str, Any], query: str) -> bool:
        """Recursively search for query string in dictionary values."""
        if not isinstance(data, dict):
            return str(data).lower() if data else False

        for key, value in data.items():
            if query in key.lower():
                return True

            if isinstance(value, dict):
                if self._search_in_dict(value, query):
                    return True
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and self._search_in_dict(item, query):
                        return True
                    elif query in str(item).lower():
                        return True
            elif query in str(value).lower():
                return True

        return False