# Configuration Service Contract

**Service**: ConfigService
**Purpose**: Manage Claude Code settings.json file operations (read, write, backup, restore)
**Type**: File system operations service

## Interface Definition

### Methods

#### read_settings(claude_config_path: str) -> Optional[str]
**Purpose**: Read Claude Code settings.json content

**Input Parameters**:
- `claude_config_path`: Full path to settings.json file

**Returns**:
- JSON content string if file exists and readable, `None` otherwise

**Raises**:
- `FileNotFoundError`: Settings file not found
- `PermissionError`: No read permissions
- `OSError`: File system error
- `ValidationError`: Invalid JSON content

**Contract**:
- Returns raw file content as string
- Validates JSON syntax before returning
- Returns None if file doesn't exist
- Logs file read operation
- Handles encoding errors gracefully

#### write_settings(claude_config_path: str, config_json: str) -> bool
**Purpose**: Write configuration to Claude Code settings.json

**Input Parameters**:
- `claude_config_path`: Full path to settings.json file
- `config_json`: Valid JSON content string

**Returns**:
- `True` if write successful, `False` on failure

**Raises**:
- `ValidationError`: Invalid JSON syntax
- `PermissionError`: No write permissions
- `OSError`: File system error
- `FileNotFoundError`: Directory doesn't exist

**Contract**:
- Validates JSON syntax before writing
- Creates directory if it doesn't exist
- Writes atomically (write to temp file, then rename)
- Ensures proper permissions on created file
- Logs write operation with file size
- Returns True only on complete success

#### create_backup(claude_config_path: str, backup_dir: str) -> str
**Purpose**: Create backup of current settings.json

**Input Parameters**:
- `claude_config_path`: Full path to settings.json file
- `backup_dir`: Directory for backup files

**Returns**:
- Full path to created backup file

**Raises**:
- `FileNotFoundError`: Settings file not found
- `PermissionError`: No read/write permissions
- `OSError`: File system error

**Contract**:
- Creates timestamped backup: `settings.json.backup.YYYYMMDD_HHMMSS`
- Ensures backup directory exists
- Copies original file content exactly
- Returns full path to backup file
- Logs backup creation with file size
- Throws descriptive errors on failure

#### list_backups(backup_dir: str) -> List[str]
**Purpose**: List available backup files

**Input Parameters**:
- `backup_dir`: Directory containing backup files

**Returns**:
- List of backup file paths sorted by creation time (newest first)

**Raises**:
- `PermissionError`: No read permissions
- `OSError`: File system error

**Contract**:
- Returns only valid backup files (matching pattern)
- Sorts by timestamp (newest first)
- Returns empty list if no backups found
- Includes full paths, not just filenames
- Filters out non-backup files

#### restore_backup(backup_path: str, claude_config_path: str) -> bool
**Purpose**: Restore settings.json from backup

**Input Parameters**:
- `backup_path`: Full path to backup file
- `claude_config_path`: Target settings.json path

**Returns**:
- `True` if restore successful, `False` on failure

**Raises**:
- `FileNotFoundError`: Backup file not found
- `ValidationError`: Invalid JSON in backup
- `PermissionError`: No write permissions
- `OSError`: File system error

**Contract**:
- Validates backup file exists and readable
- Validates JSON content in backup
- Creates backup of current settings before restore
- Writes atomically (temp file then rename)
- Logs restore operation with source/destination
- Returns True only on complete success

#### cleanup_old_backups(backup_dir: str, keep_count: int) -> int
**Purpose**: Remove old backup files, keeping most recent ones

**Input Parameters**:
- `backup_dir`: Directory containing backup files
- `keep_count`: Number of most recent backups to keep

**Returns**:
- Number of backup files removed

**Raises**:
- `PermissionError`: No write permissions
- `OSError`: File system error

**Contract**:
- Sorts backups by creation time (newest first)
- Keeps most recent `keep_count` files
- Removes older files if count exceeded
- Returns count of files removed
- Skips files that cannot be removed (permission errors)
- Logs cleanup operation

#### calculate_content_hash(config_json: str) -> str
**Purpose**: Calculate SHA-256 hash of normalized JSON

**Input Parameters**:
- `config_json`: JSON content string

**Returns**:
- SHA-256 hash string

**Raises**:
- `ValidationError`: Invalid JSON syntax

**Contract**:
- Parses JSON to validate syntax
- Normalizes JSON (sorted keys, consistent formatting)
- Calculates SHA-256 hash of normalized content
- Returns hex-encoded hash string
- Hash is deterministic for equivalent JSON

#### detect_claude_config_path() -> Optional[str]
**Purpose**: Auto-detect Claude Code configuration file path

**Returns**:
- Full path to settings.json if found, `None` otherwise

**Contract**:
- Checks standard locations by platform:
  - Windows: `C:\Users\<username>\.claude\settings.json`
  - macOS: `~/.claude/settings.json`
  - Linux: `~/.claude/settings.json`
- Returns first existing and readable path found
- Returns None if no standard location found
- Uses platform-agnostic path detection

### Data Structures

#### BackupInfo
```python
@dataclass
class BackupInfo:
    path: str
    timestamp: datetime
    size: int
    content_hash: str
```

#### ConfigResult
```python
@dataclass
class ConfigResult:
    success: bool
    content: Optional[str]
    error: Optional[str]
    path: str
```

### Error Handling

#### Standard Exceptions
- `FileNotFoundError`: File not found
- `PermissionError`: Access denied
- `OSError`: General file system error
- `ValidationError`: Invalid JSON content
- `BackupError`: Backup operation failure

#### Error Recovery
- Atomic write operations (temp file then rename)
- Backup creation before modifications
- Rollback on write failures
- Graceful handling of permission errors

### Performance Requirements

#### Response Times
- `read_settings`: < 100ms for typical config file
- `write_settings`: < 200ms including validation
- `create_backup`: < 50ms for typical config file
- `list_backups`: < 100ms for 50 backup files
- `restore_backup`: < 300ms including backup creation
- `cleanup_old_backups`: < 200ms for 100 backup files
- `calculate_content_hash`: < 50ms for typical config file

#### File Operations
- Use atomic writes (temp file + rename)
- Buffer I/O for large files
- Proper file handle management
- Encoding handling (UTF-8)

### Testing Requirements

#### Unit Tests
- All methods with valid and invalid inputs
- File system error simulation
- JSON validation scenarios
- Backup file naming and sorting

#### Integration Tests
- Complete backup/restore flow
- File locking scenarios
- Permission error handling
- Cross-platform path detection

#### Contract Tests
- Method signatures and return types
- Error raising behavior
- Atomic operation verification
- File content preservation

### Logging Requirements

#### Operations to Log
- File reads: `config.read path={path} size={size} success={true/false}`
- File writes: `config.write path={path} size={size} success={true/false}`
- Backup creation: `config.backup.create source={source} backup={backup} size={size}`
- Backup restore: `config.backup.restore backup={backup} target={target} success={true/false}`
- Cleanup operations: `config.backup.cleanup removed={count} kept={count}`
- Hash calculation: `config.hash calculated={hash} size={size}`
- Error conditions: `config.error operation={operation} error={error}`

#### Log Levels
- INFO: Successful operations
- DEBUG: Detailed file operation data
- WARNING: Non-critical issues (missing files)
- ERROR: Operation failures
- CRITICAL: File system corruption issues

### Security Requirements

#### File Access
- Validate paths are within expected directories
- Check file permissions before operations
- Handle symlinks and junction points carefully
- Prevent path traversal attacks

#### Data Protection
- Validate JSON content for security issues
- No logging of sensitive configuration content
- Secure file permissions on created files
- Temporary file cleanup on errors

### Dependencies

#### Required Dependencies
- `json`: JSON parsing and validation
- `pathlib`: Path manipulation
- `hashlib`: Content hashing
- `shutil`: File copying operations
- `tempfile`: Temporary file handling
- `os`: File system operations
- `logging`: Structured logging

#### External Dependencies
- File system access for settings.json
- User home directory detection
- Platform-specific path handling

### Atomic Operations

#### Write Strategy
```python
def atomic_write(target_path: str, content: str) -> bool:
    # 1. Write to temporary file in same directory
    temp_path = target_path.with_suffix('.tmp')

    # 2. Write content to temp file
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(content)
        f.flush()  # Ensure written to disk

    # 3. Atomic rename to target
    os.replace(temp_path, target_path)

    return True
```

#### Backup Strategy
- Create backup before any modification
- Verify backup file was created successfully
- Keep backup creation and target write in same transaction
- Rollback on write failure using backup

### Cross-Platform Considerations

#### Path Handling
- Use `pathlib.Path` for cross-platform paths
- Handle Windows vs. Unix path separators
- Respect platform-specific home directories
- Support different filename lengths and restrictions

#### File Permissions
- Handle Windows file permissions
- Respect Unix file modes
- Default to restrictive permissions for new files
- Honor existing file permissions when possible

### Configuration Schema

#### Expected JSON Structure
```json
{
    "env": {
        "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
        "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-xxxxx"
    },
    "model": "claude-3-opus-20240229",
    "max_tokens": 4096,
    "temperature": 0.7
}
```

#### Validation Rules
- Must be valid JSON object
- Root object can contain any properties
- `env` object should contain environment variables
- Values can be strings, numbers, booleans, arrays, or objects
- No size restrictions (within reasonable limits)