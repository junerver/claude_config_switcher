# Profile Service Contract

**Service**: ProfileService
**Purpose**: Manage configuration profiles (CRUD operations, application, active detection)
**Type**: Core business logic service

## Interface Definition

### Methods

#### create_profile(name: str, config_json: str) -> Profile
**Purpose**: Create a new configuration profile

**Input Parameters**:
- `name`: Profile name (1-100 chars, unique, no path separators)
- `config_json`: Valid JSON configuration string

**Returns**:
- `Profile` object with generated ID and extracted metadata

**Raises**:
- `ValidationError`: Invalid name or JSON syntax
- `IntegrityError`: Profile name already exists
- `DatabaseError`: Database operation failed

**Contract**:
- Input JSON must be valid and parseable
- Name must be unique and non-empty
- Base URL and auth token extracted and stored for display
- Content hash calculated for active detection
- Timestamps automatically set

#### get_profile(id: int) -> Optional[Profile]
**Purpose**: Retrieve a profile by ID

**Input Parameters**:
- `id`: Profile identifier

**Returns**:
- `Profile` object if found, `None` if not found

**Raises**:
- `DatabaseError`: Database operation failed

**Contract**:
- Returns complete profile with all metadata
- Returns None for non-existent ID
- Includes display-ready base_url and masked auth_token

#### get_all_profiles() -> List[Profile]
**Purpose**: Retrieve all profiles for display

**Returns**:
- List of `Profile` objects sorted by name

**Raises**:
- `DatabaseError`: Database operation failed

**Contract**:
- Returns profiles in alphabetical order by name
- Each profile includes display metadata
- Includes is_active flag for currently active profile
- Never returns None (empty list if no profiles)

#### update_profile(id: int, name: str = None, config_json: str = None) -> Profile
**Purpose**: Update existing profile

**Input Parameters**:
- `id`: Profile identifier
- `name`: New profile name (optional)
- `config_json`: New configuration JSON (optional)

**Returns**:
- Updated `Profile` object

**Raises**:
- `ValidationError`: Invalid name or JSON syntax
- `IntegrityError`: New name already exists
- `NotFoundError`: Profile not found
- `DatabaseError`: Database operation failed

**Contract**:
- At least one parameter must be provided
- Name validation applies if name provided
- JSON validation applies if config_json provided
- Content hash recalculated if config_json changed
- Timestamp updated to current time
- Active status preserved

#### delete_profile(id: int) -> bool
**Purpose**: Delete a profile

**Input Parameters**:
- `id`: Profile identifier

**Returns**:
- `True` if deleted, `False` if not found

**Raises**:
- `DatabaseError`: Database operation failed

**Contract**:
- Cannot delete currently active profile
- Cascade deletes any related records
- Returns False for non-existent profile
- Returns True for successful deletion

#### apply_profile(id: int) -> bool
**Purpose**: Apply profile configuration to Claude Code settings

**Input Parameters**:
- `id`: Profile identifier

**Returns**:
- `True` if successfully applied, `False` on failure

**Raises**:
- `NotFoundError`: Profile not found
- `FileError`: Settings.json not found or unwritable
- `BackupError`: Failed to create backup
- `DatabaseError`: Database operation failed

**Contract**:
- Creates backup of current settings.json
- Writes profile config to settings.json
- Updates is_active flags in database
- Logs operation for audit trail
- Returns True only on complete success
- No partial state changes on failure

#### get_active_profile() -> Optional[Profile]
**Purpose**: Detect and return currently active profile

**Returns**:
- `Profile` object if active profile detected, `None` otherwise

**Raises**:
- `FileError`: Settings.json not found
- `DatabaseError`: Database operation failed

**Contract**:
- Reads current settings.json content
- Calculates hash of normalized content
- Compares with stored profile hashes
- Updates is_active flags based on comparison
- Returns matching profile or None

#### duplicate_profile(id: int, new_name: str) -> Profile
**Purpose**: Create a copy of existing profile

**Input Parameters**:
- `id`: Source profile identifier
- `new_name`: Name for duplicate profile

**Returns**:
- New `Profile` object with copied configuration

**Raises**:
- `ValidationError`: Invalid name
- `IntegrityError`: Name already exists
- `NotFoundError`: Source profile not found
- `DatabaseError`: Database operation failed

**Contract**:
- Copies all profile data except ID and timestamps
- New profile gets unique ID and current timestamps
- is_active flag starts as False
- Name validation applies to new_name

### Data Structures

#### Profile
```python
@dataclass
class Profile:
    id: int
    name: str
    config_json: str
    base_url: Optional[str]
    auth_token: Optional[str]  # Masked format
    content_hash: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
```

#### ValidationError
```python
@dataclass
class ValidationError:
    field: str
    message: str
    value: Any
```

### Error Handling

#### Standard Exceptions
- `ValidationError`: Input validation failures
- `NotFoundError`: Resource not found
- `IntegrityError`: Constraint violations
- `FileError`: File system errors
- `BackupError`: Backup operation failures
- `DatabaseError`: Database operation errors

#### Error Recovery
- Database operations use transactions
- File operations create backups before modification
- Validation failures don't modify data
- Partial operations rollback on error

### Performance Requirements

#### Response Times
- `create_profile`: < 100ms
- `get_profile`: < 50ms
- `get_all_profiles`: < 200ms for 50 profiles
- `update_profile`: < 100ms
- `delete_profile`: < 50ms
- `apply_profile`: < 500ms (including file I/O)
- `get_active_profile`: < 300ms (including file read)

#### Concurrency
- Multiple read operations supported
- Write operations use database transactions
- File operations are atomic (backup + write)
- Database connection pooling for multiple threads

### Testing Requirements

#### Unit Tests
- All methods with valid and invalid inputs
- Error conditions and edge cases
- Database constraint violations
- File system error simulation

#### Integration Tests
- Complete profile switching flow
- File I/O operations
- Active profile detection accuracy
- Backup and restore functionality

#### Contract Tests
- Method signatures and return types
- Error raising behavior
- Transaction rollback scenarios
- Data integrity preservation

### Logging Requirements

#### Operations to Log
- Profile creation: `profile.created id={id} name={name}`
- Profile updates: `profile.updated id={id} changes={changes}`
- Profile deletion: `profile.deleted id={id} name={name}`
- Profile application: `profile.applied id={id} backup={backup_path}`
- Validation failures: `validation.failed field={field} error={error}`
- File operations: `file.{operation} path={path} result={success/failure}`

#### Log Levels
- INFO: Successful operations
- DEBUG: Detailed operation data
- WARNING: Validation warnings
- ERROR: Operation failures
- CRITICAL: Database or file system errors

### Security Requirements

#### Input Validation
- Profile names: No path separators, length limits
- JSON content: Valid syntax, size limits
- File paths: Within expected directories

#### Data Protection
- Sensitive keys masked in display
- No full auth tokens in logs
- Input sanitization for injection prevention
- Parameterized database queries

### Dependencies

#### Required Dependencies
- `sqlite3`: Database operations
- `json`: JSON parsing and validation
- `pathlib`: Path manipulation
- `hashlib`: Content hashing
- `logging`: Structured logging

#### External Dependencies
- `config_service`: For settings.json operations
- `validation_service`: For JSON validation
- File system access for settings.json