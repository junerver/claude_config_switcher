# Data Model: Claude Code Configuration Switcher

**Feature**: 001-config-switcher-gui
**Date**: 2025-10-17
**Purpose**: Define data entities, relationships, and validation rules

## Entity Definitions

### 1. Configuration Profile

**Purpose**: Stores a complete Claude Code configuration profile that can be applied.

**Table**: `profiles`

```sql
CREATE TABLE profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    config_json TEXT NOT NULL,
    base_url TEXT,
    auth_token TEXT,
    content_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE
);
```

**Fields**:
- **id**: Unique identifier (auto-incrementing integer)
- **name**: User-defined profile name (unique, required)
- **config_json**: Complete JSON configuration string (required)
- **base_url**: Extracted ANTHROPIC_BASE_URL value (for display)
- **auth_token**: Masked ANTHROPIC_AUTH_TOKEN value (for display)
- **content_hash**: SHA-256 hash of config_json (for active profile detection)
- **created_at**: Profile creation timestamp
- **updated_at**: Last modification timestamp
- **is_active**: Flag indicating if this is currently active profile

**Validation Rules**:
- `name` must be unique, non-empty, max 100 characters
- `name` cannot contain path separators (`/`, `\`, `..`)
- `config_json` must be valid JSON
- `config_json` must parse successfully and be serializable
- `content_hash` must be SHA-256 of normalized config_json
- `base_url` and `auth_token` extracted from config_json if present
- `auth_token` stored in masked format (first4...last4)

### 2. Application Settings

**Purpose**: Stores application-wide settings and configuration.

**Table**: `settings`

```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Fields**:
- **key**: Setting key (primary key)
- **value**: Setting value
- **updated_at**: Last modification timestamp

**Default Settings**:
- `claude_config_path`: Auto-detected Claude Code settings.json path
- `backup_retention_count`: Number of backups to keep (default: 10)
- `theme`: Application theme (light/dark, default: system)
- `log_level`: Logging level (DEBUG/INFO/WARNING/ERROR, default: INFO)
- `window_width`: Last window width (default: 800)
- `window_height`: Last window height (default: 600)

### 3. Backup Log

**Purpose**: Tracks configuration file backups for recovery.

**Table**: `backup_log`

```sql
CREATE TABLE backup_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backup_path TEXT NOT NULL,
    original_hash TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    profile_id INTEGER,
    FOREIGN KEY (profile_id) REFERENCES profiles (id)
);
```

**Fields**:
- **id**: Unique identifier
- **backup_path**: Full path to backup file
- **original_hash**: Hash of original settings.json content
- **timestamp**: Backup creation time
- **profile_id**: Profile applied after backup (nullable)

## JSON Configuration Schema

### Expected Configuration Structure

```json
{
    "env": {
        "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
        "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-xxxxx"
    },
    "other_setting": "value"
}
```

**Validation Rules**:
- Root object may contain any properties
- If `env` object exists, it must be a valid object
- Key names in `env` should follow environment variable conventions (UPPER_CASE)
- Values can be strings, numbers, booleans, or arrays
- Required fields for display: `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`

### Key Detection Patterns

**Sensitive Key Patterns** (for masking):
- `*_API_KEY`
- `*_AUTH_TOKEN`
- `*_SECRET`
- `*_TOKEN`
- `PASSWORD`
- `ANTHROPIC_AUTH_TOKEN`

**Display Key Patterns** (for profile list):
- `ANTHROPIC_BASE_URL` → Display as "Base URL"
- `ANTHROPIC_AUTH_TOKEN` → Display as "Auth Token" (masked)
- `ANTHROPIC_MODEL` → Display as "Model"

## Data Access Patterns

### Profile Operations

**Create Profile**:
```python
def create_profile(name: str, config_json: str) -> Profile:
    # Validate JSON syntax
    # Extract base_url and auth_token
    # Calculate content hash
    # Insert into database
    # Return Profile object
```

**Update Profile**:
```python
def update_profile(id: int, name: str = None, config_json: str = None) -> Profile:
    # Validate inputs
    # Update database
    # Update timestamp
    # Return updated Profile
```

**Delete Profile**:
```python
def delete_profile(id: int) -> bool:
    # Check if profile is active
    # Delete from database
    # Return success status
```

**Get Active Profile**:
```python
def get_active_profile() -> Optional[Profile]:
    # Compare current settings.json hash with stored hashes
    # Return matching Profile or None
```

**Apply Profile**:
```python
def apply_profile(id: int) -> bool:
    # Create backup of current settings
    # Write profile config to settings.json
    # Update active flag in database
    # Return success status
```

### Settings Operations

**Get Setting**:
```python
def get_setting(key: str) -> Optional[str]:
    # Query settings table
    # Return value or None
```

**Set Setting**:
```python
def set_setting(key: str, value: str) -> bool:
    # Insert or update setting
    # Return success status
```

### Validation Operations

**Validate JSON**:
```python
def validate_json(config_json: str) -> Validation:
    # Parse JSON
    # Check for required structure
    # Extract displayable keys
    # Return validation result
```

**Normalize JSON**:
```python
def normalize_json(config_json: str) -> str:
    # Parse JSON
    # Sort keys consistently
    # Pretty-print with 2-space indentation
    # Return normalized string
```

## Error Handling

### Database Errors
- `sqlite3.IntegrityError`: Constraint violations (duplicate names)
- `sqlite3.OperationalError`: Database connection issues
- `sqlite3.DatabaseError`: General database errors

### Validation Errors
- `json.JSONDecodeError`: Invalid JSON syntax
- `ValidationError`: Missing required fields, invalid structure
- `ValueError`: Invalid input values (empty names, etc.)

### File System Errors
- `FileNotFoundError`: Claude Code settings.json not found
- `PermissionError`: No write permissions
- `OSError`: General file system errors

### Logging Strategy

```python
import logging

logger = logging.getLogger(__name__)

# Database operations
logger.info(f"Created profile: {profile.name}")
logger.debug(f"Profile ID: {profile.id}, Hash: {profile.content_hash}")

# Validation
logger.warning(f"JSON validation failed: {error_message}")
logger.error(f"Invalid configuration in profile {profile_id}")

# File operations
logger.info(f"Backup created: {backup_path}")
logger.info(f"Profile {profile.name} applied to settings.json")
logger.error(f"Failed to write settings.json: {error}")
```

## Performance Considerations

### Indexes
```sql
CREATE INDEX idx_profiles_name ON profiles(name);
CREATE INDEX idx_profiles_hash ON profiles(content_hash);
CREATE INDEX idx_backup_log_timestamp ON backup_log(timestamp);
```

### Query Optimization
- Use prepared statements for repeated queries
- Cache active profile hash to avoid repeated file reads
- Use LIMIT for large result sets
- Implement pagination for profile list if >100 profiles

### Memory Management
- Use generators for large result sets
- Close database connections promptly
- Don't load all profiles into memory simultaneously

## Security Considerations

### Data Protection
- Mask sensitive keys in display
- Never log full auth tokens
- Validate input to prevent injection attacks
- Use parameterized queries

### File Permissions
- Validate file paths are within expected directories
- Check write permissions before operations
- Handle permission denied errors gracefully

## Migration Strategy

### Versioning
```sql
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_version (version) VALUES (1);
```

### Future Migration Support
- Store schema version in database
- Provide migration scripts for schema changes
- Backward compatibility for existing data
- Migration logging and rollback capability

## Testing Strategy

### Unit Tests
- Profile CRUD operations
- JSON validation and normalization
- Settings management
- Database constraints

### Integration Tests
- Complete profile switching flow
- File I/O operations
- Active profile detection
- Backup and restore

### Data Integrity Tests
- Duplicate name prevention
- JSON validation accuracy
- Hash consistency
- Transaction rollback

## Data Flow

### Profile Switching Flow
```
1. User double-clicks profile in GUI
2. GUI calls profile_service.apply_profile(profile_id)
3. Service creates backup of current settings.json
4. Service reads profile from database
5. Service writes profile.config_json to settings.json
6. Service updates is_active flags in database
7. GUI updates display to show new active profile
8. Service logs operation for audit trail
```

### Profile Creation Flow
```
1. User enters profile name and JSON config in GUI
2. GUI calls validation_service.validate_json(config_json)
3. GUI calls profile_service.create_profile(name, config_json)
4. Service validates inputs and extracts display data
5. Service calculates content hash
6. Service inserts into database
7. GUI updates profile list
8. Service logs creation
```

This data model provides a solid foundation for the configuration switcher while ensuring data integrity, performance, and maintainability.