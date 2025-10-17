"""
Custom exceptions for the configuration switcher application.
"""

class ConfigSwitcherError(Exception):
    """Base exception for all configuration switcher errors."""
    pass

class ProfileError(ConfigSwitcherError):
    """Profile-related errors."""
    pass

class ProfileNotFoundError(ProfileError):
    """Profile not found error."""
    def __init__(self, profile_id_or_name: str):
        self.profile_id_or_name = profile_id_or_name
        super().__init__(f"Profile '{profile_id_or_name}' not found")

class ProfileAlreadyExistsError(ProfileError):
    """Profile already exists error."""
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Profile name '{name}' already exists")

class ActiveProfileProtectedError(ProfileError):
    """Attempt to modify active profile error."""
    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        super().__init__(f"Cannot delete currently active profile '{profile_name}'")

class ValidationError(ConfigSwitcherError):
    """Validation-related errors."""
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message)

class InvalidJSONError(ValidationError):
    """Invalid JSON configuration error."""
    def __init__(self, json_error: str):
        self.json_error = json_error
        super().__init__(f"Invalid JSON configuration: {json_error}")

class ConfigServiceError(ConfigSwitcherError):
    """Configuration service errors."""
    pass

class ConfigNotFoundError(ConfigServiceError):
    """Configuration file not found error."""
    def __init__(self, path: str):
        self.path = path
        super().__init__(f"Claude Code configuration file not found at {path}")

class PermissionError(ConfigServiceError):
    """File permission error."""
    def __init__(self, path: str, operation: str):
        self.path = path
        self.operation = operation
        super().__init__(f"Permission denied accessing {path} for {operation}")

class BackupError(ConfigServiceError):
    """Backup operation error."""
    def __init__(self, operation: str, reason: str):
        self.operation = operation
        self.reason = reason
        super().__init__(f"Backup {operation} failed: {reason}")

class DatabaseError(ConfigSwitcherError):
    """Database operation errors."""
    pass

class DatabaseConnectionError(DatabaseError):
    """Database connection error."""
    def __init__(self, path: str, reason: str):
        self.path = path
        self.reason = reason
        super().__init__(f"Database connection failed at {path}: {reason}")

class DatabaseIntegrityError(DatabaseError):
    """Database integrity constraint error."""
    def __init__(self, constraint: str, details: str):
        self.constraint = constraint
        self.details = details
        super().__init__(f"Database integrity error ({constraint}): {details}")

class ServiceError(ConfigSwitcherError):
    """Service layer errors."""
    def __init__(self, service: str, operation: str, reason: str):
        self.service = service
        self.operation = operation
        self.reason = reason
        super().__init__(f"{service} {operation} failed: {reason}")

class GUIError(ConfigSwitcherError):
    """GUI-related errors."""
    pass

class WidgetError(GUIError):
    """Widget operation error."""
    def __init__(self, widget: str, operation: str, reason: str):
        self.widget = widget
        self.operation = operation
        self.reason = reason
        super().__init__(f"{widget} {operation} failed: {reason}")

class FileOperationError(ConfigSwitcherError):
    """File operation errors."""
    def __init__(self, operation: str, path: str, reason: str):
        self.operation = operation
        self.path = path
        self.reason = reason
        super().__init__(f"File {operation} failed for {path}: {reason}")

# Error codes for CLI exit codes
class ExitCode:
    """Standard exit codes for CLI operations."""
    SUCCESS = 0
    GENERAL_ERROR = 1
    INVALID_ARGUMENTS = 2
    FILE_NOT_FOUND = 3
    PERMISSION_DENIED = 4
    INVALID_CONFIGURATION = 5
    DATABASE_ERROR = 6