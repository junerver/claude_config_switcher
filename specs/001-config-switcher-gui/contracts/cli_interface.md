# CLI Interface Contract

**Interface**: Command Line Interface
**Purpose**: Provide text-based interface for automation, scripting, and testing
**Type**: CLI-first interface per constitution requirement

## Interface Definition

### Command Structure

```
claude-config-switcher [OPTIONS] COMMAND [ARGS]
```

#### Global Options
- `--config-path PATH`: Override Claude Code settings.json path
- `--log-level LEVEL`: Set logging level (DEBUG|INFO|WARNING|ERROR)
- `--format FORMAT`: Output format (text|json, default: text)
- `--no-color`: Disable colored output
- `--help`: Show help message
- `--version`: Show version information

#### Exit Codes
- `0`: Success
- `1`: General error
- `2`: Invalid arguments
- `3`: File not found
- `4`: Permission denied
- `5`: Invalid configuration
- `6`: Database error

### Commands

#### profile list
**Purpose**: List all configuration profiles

**Usage**: `claude-config-switcher profile list`

**Options**:
- `--active-only`: Show only currently active profile
- `--format FORMAT`: Output format (table|json|csv, default: table)

**Output (table format)**:
```
ID  NAME              BASE_URL                  ACTIVE  UPDATED
1   Production        https://api.anthropic.com  ✓       2025-10-17 14:30
2   Development       https://api.dev.anthropic.com  ✗    2025-10-17 13:15
3   Testing           https://api.test.anthropic.com  ✗    2025-10-16 09:45
```

**Output (json format)**:
```json
{
  "profiles": [
    {
      "id": 1,
      "name": "Production",
      "base_url": "https://api.anthropic.com",
      "auth_token": "sk-ant...9029",
      "is_active": true,
      "updated_at": "2025-10-17T14:30:00Z"
    }
  ],
  "total": 3
}
```

**Contract**:
- Returns all profiles sorted by name
- Shows masked auth tokens
- Includes active status indicator
- Returns empty list if no profiles exist
- Supports multiple output formats

#### profile show
**Purpose**: Show details of a specific profile

**Usage**: `claude-config-switcher profile show PROFILE_ID_OR_NAME`

**Arguments**:
- `PROFILE_ID_OR_NAME`: Profile ID or name

**Options**:
- `--show-secrets`: Show full auth tokens (use with caution)
- `--format FORMAT`: Output format (yaml|json, default: yaml)

**Output**:
```yaml
id: 1
name: Production
base_url: https://api.anthropic.com
auth_token: sk-ant-api03-9471eac03e6b1611038a7681eac1ce3d782bcb135fe1c2bcd0c9d4fa74709029
config_json: |
  {
    "env": {
      "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
      "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-9471eac03e6b1611038a7681eac1ce3d782bcb135fe1c2bcd0c9d4fa74709029"
    },
    "model": "claude-3-opus-20240229"
  }
created_at: 2025-10-17T10:00:00Z
updated_at: 2025-10-17T14:30:00Z
is_active: true
```

**Contract**:
- Accepts either profile ID or name
- Returns complete profile details
- Masks sensitive data unless `--show-secrets` used
- Returns error if profile not found
- Supports YAML and JSON output formats

#### profile create
**Purpose**: Create a new configuration profile

**Usage**: `claude-config-switcher profile create NAME [OPTIONS]`

**Arguments**:
- `NAME`: Profile name (unique, 1-100 chars)

**Options**:
- `--file PATH`: Read JSON configuration from file
- `--json JSON`: JSON configuration string
- `--interactive`: Interactive mode with prompts

**Interactive Mode**:
```
Enter profile name: Production
Enter JSON configuration (press Ctrl+D when done):
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
    "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-xxxxx"
  }
}

Profile created successfully!
ID: 1
Name: Production
Base URL: https://api.anthropic.com
Auth Token: sk-ant...9029
```

**Contract**:
- Name must be unique and valid
- JSON configuration must be valid
- Supports multiple input methods
- Returns created profile details
- Validates input before creation
- Returns descriptive errors on validation failure

#### profile update
**Purpose**: Update an existing profile

**Usage**: `claude-config-switcher profile update PROFILE_ID_OR_NAME [OPTIONS]`

**Arguments**:
- `PROFILE_ID_OR_NAME`: Profile ID or name

**Options**:
- `--name NEW_NAME`: New profile name
- `--file PATH`: Read JSON configuration from file
- `--json JSON`: JSON configuration string
- `--interactive`: Interactive mode

**Contract**:
- Profile must exist
- At least one option must be provided
- Validates all inputs
- Returns updated profile details
- Preserves unchanged fields
- Returns descriptive errors on validation failure

#### profile delete
**Purpose**: Delete a configuration profile

**Usage**: `claude-config-switcher profile delete PROFILE_ID_OR_NAME [OPTIONS]`

**Arguments**:
- `PROFILE_ID_OR_NAME`: Profile ID or name

**Options**:
- `--force`: Skip confirmation prompt
- `--dry-run`: Show what would be deleted without deleting

**Interactive Confirmation**:
```
Delete profile 'Production'? [y/N]: y
Profile 'Production' deleted successfully.
```

**Contract**:
- Profile must exist
- Cannot delete currently active profile
- Prompts for confirmation unless `--force` used
- Returns success confirmation
- Returns error for non-existent profile
- Returns error for active profile deletion attempt

#### profile apply
**Purpose**: Apply a profile to Claude Code configuration

**Usage**: `claude-config-switcher profile apply PROFILE_ID_OR_NAME [OPTIONS]`

**Arguments**:
- `PROFILE_ID_OR_NAME`: Profile ID or name

**Options**:
- `--no-backup`: Skip creating backup
- `--dry-run`: Show what would be applied without applying

**Output**:
```
Applying profile 'Production'...
✓ Created backup: C:\Users\user\.claude\settings.json.backup.20251017_143052
✓ Updated settings.json
✓ Profile applied successfully!

Active profile: Production
Base URL: https://api.anthropic.com
Auth Token: sk-ant...9029
```

**Contract**:
- Creates backup of current settings unless `--no-backup`
- Writes profile configuration to settings.json
- Updates active status in database
- Returns success confirmation
- Returns error on any failure
- No partial state changes on failure

#### profile duplicate
**Purpose**: Create a copy of existing profile

**Usage**: `claude-config-switcher profile duplicate SOURCE_ID_OR_NAME NEW_NAME`

**Arguments**:
- `SOURCE_ID_OR_NAME`: Source profile ID or name
- `NEW_NAME`: Name for duplicated profile

**Contract**:
- Source profile must exist
- New name must be unique and valid
- Copies all profile data except ID and timestamps
- Returns new profile details
- Returns error if source not found
- Returns error if name already exists

#### config status
**Purpose**: Show current configuration status

**Usage**: `claude-config-switcher config status`

**Output**:
```
Claude Code Configuration Status
================================

Config Path: C:\Users\user\.claude\settings.json
Active Profile: Production (ID: 1)
Config Modified: 2025-10-17 14:30:00
Backup Count: 3
Total Profiles: 3

Active Profile Details:
  Name: Production
  Base URL: https://api.anthropic.com
  Auth Token: sk-ant...9029
  Updated: 2025-10-17 14:30:00
```

**Contract**:
- Detects current active profile
- Shows configuration file path
- Shows backup file count
- Shows total profile count
- Returns error if config file not found

#### config backup
**Purpose**: Create backup of current configuration

**Usage**: `claude-config-switcher config backup [OPTIONS]`

**Options**:
- `--list`: List available backups
- `--restore BACKUP_PATH`: Restore from backup
- `--cleanup COUNT`: Keep only N most recent backups

**List Output**:
```
Available Backups (C:\Users\user\.claude\backups\)
=================================================
1. settings.json.backup.20251017_143052 (2025-10-17 14:30:52) - 523 bytes
2. settings.json.backup.20251017_132015 (2025-10-17 13:20:15) - 498 bytes
3. settings.json.backup.20251016_094530 (2025-10-16 09:45:30) - 501 bytes
```

**Contract**:
- Creates timestamped backup of current settings
- Lists available backups with timestamps
- Restores from specific backup file
- Cleans up old backups keeping N most recent
- Returns error if backup creation fails

### Error Handling

#### Standard Error Format
```
Error: [ERROR_CODE] [ERROR_MESSAGE]

Usage: claude-config-switcher profile list [OPTIONS]

For help, use: claude-config-switcher --help
```

#### Error Messages
- `ProfileNotFound`: "Profile 'nonexistent' not found"
- `ProfileAlreadyExists`: "Profile name 'duplicate' already exists"
- `InvalidJSON`: "Invalid JSON configuration: [details]"
- `ConfigNotFound`: "Claude Code configuration file not found at [path]"
- `PermissionDenied`: "Permission denied accessing [path]"
- `ActiveProfileProtected`: "Cannot delete currently active profile 'Production'"

### Input Validation

#### Profile Names
- Must be 1-100 characters
- Cannot be empty or whitespace only
- Cannot contain path separators: `/`, `\`, `..`
- Must be unique across all profiles
- Case-sensitive for uniqueness

#### JSON Configuration
- Must be valid JSON syntax
- Must be parseable and serializable
- Should follow Claude Code configuration structure
- No size limits (within reasonable memory constraints)

#### File Paths
- Must be absolute or relative to current directory
- Must exist for read operations
- Parent directory must exist for write operations
- Must have appropriate permissions

### Output Formats

#### Table Format
- Human-readable columns
- Colored output (unless disabled)
- Aligned columns with spacing
- Status indicators (✓, ✗, !)

#### JSON Format
- Machine-readable JSON
- Consistent field names
- ISO 8601 timestamps
- No trailing commas

#### YAML Format
- Human-readable YAML
- Nested structure preservation
- Comment support for additional context

### Performance Requirements

#### Response Times
- `profile list`: < 100ms for 50 profiles
- `profile show`: < 50ms
- `profile create`: < 200ms including validation
- `profile apply`: < 500ms including file I/O
- `config status`: < 200ms including file read

#### Memory Usage
- Stream large JSON files
- Don't load all profiles into memory simultaneously
- Efficient string handling for large configurations

### Testing Requirements

#### Unit Tests
- All command parsing and validation
- Error condition handling
- Output format generation
- Input validation scenarios

#### Integration Tests
- Complete profile management flows
- File system integration
- Database interaction
- Error recovery scenarios

#### Contract Tests
- CLI interface specifications
- Exit code consistency
- Output format compliance
- Error message standards

### Security Requirements

#### Input Sanitization
- Validate profile names for path traversal
- Sanitize JSON input for injection attacks
- Validate file paths are within expected directories
- Handle special characters in names and paths

#### Sensitive Data Protection
- Mask auth tokens in output by default
- Log full tokens only at DEBUG level with explicit flag
- Clear sensitive data from memory after operations
- Never log full configuration content

### Dependencies

#### Required Dependencies
- `argparse`: Command-line argument parsing
- `json`: JSON parsing and generation
- `yaml`: YAML output support (optional)
- `pathlib`: Path manipulation
- `logging`: Structured logging
- `sys`: Exit codes and system interaction

#### External Dependencies
- `profile_service`: Profile management operations
- `config_service`: Configuration file operations
- File system access for settings.json and backups

### Scripting Integration

#### Example Scripts
```bash
#!/bin/bash
# Switch to development profile
claude-config-switcher profile apply Development

# List all profiles in JSON format
claude-config-switcher profile list --format json

# Create profile from file
claude-config-switcher profile create Production --file prod-config.json

# Backup current configuration
claude-config-switcher config backup

# Check status
claude-config-switcher config status
```

#### Automation Support
- Consistent exit codes for error handling
- JSON output for machine processing
- Non-interactive mode for scripting
- Batch operations support

### Cross-Platform Compatibility

#### Path Handling
- Platform-agnostic path detection
- Handle Windows vs. Unix path separators
- Support different home directory locations
- Respect path length limitations

#### Command Line Differences
- Handle Windows command line quoting
- Support Unix shell escaping
- Different help message formatting
- Color support detection

This CLI interface ensures the application meets the constitution's CLI-first requirement while providing a robust automation interface for the GUI application.