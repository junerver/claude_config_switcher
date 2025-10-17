# Quickstart Guide: Claude Code Configuration Switcher

**Feature**: 001-config-switcher-gui
**Purpose**: Get developers up and running quickly with the configuration switcher

## Overview

The Claude Code Configuration Switcher is a desktop application that enables users to quickly switch between different Claude Code configuration profiles. It provides both a graphical interface (CustomTkinter) and a command-line interface for automation and scripting.

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11 (primary), macOS 10.14+, Linux
- **Python**: >=3.13 (automatically managed by uv)
- **Memory**: 100MB minimum
- **Disk Space**: 50MB for application, 10MB+ for profiles data
- **Permissions**: Read/write access to user directory and Claude Code settings

### Claude Code Installation
- Claude Code must be installed with standard configuration
- Default configuration location: `~/.claude/settings.json`
- User must have write permissions to this file

## Installation

### Option 1: Development Installation (Recommended)

```bash
# Clone repository
git clone https://github.com/your-org/claude-config-switcher.git
cd claude-config-switcher

# Set up development environment
uv sync

# Run application
uv run python src/main.py
```

### Option 2: Standalone Executable

1. Download the latest release from GitHub Releases
2. Extract the ZIP file
3. Run `claude-config-switcher.exe` (Windows) or `claude-config-switcher` (macOS/Linux)

## First Run

### Auto-Detection
On first launch, the application will:
1. Auto-detect Claude Code configuration directory
2. Create SQLite database for profile storage
3. Check for existing settings.json file
4. Create initial application settings

### Configuration Directory Detection
The application searches in these locations:
- **Windows**: `C:\Users\<username>\.claude\settings.json`
- **macOS**: `~/.claude/settings.json`
- **Linux**: `~/.claude/settings.json`

If auto-detection fails, the settings dialog will open for manual configuration.

## Basic Usage

### Creating Your First Profile

1. **Launch the application**:
   ```bash
   uv run python src/main.py
   ```

2. **Create a new profile**:
   - Click the "+" button or "Create Profile"
   - Enter profile name (e.g., "Development")
   - Paste your JSON configuration:
     ```json
     {
         "env": {
             "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
             "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-your-token-here"
         },
         "model": "claude-3-opus-20240229"
     }
     ```
   - Click "Save"

3. **Switch profiles**:
   - Double-click the profile in the list
   - Confirm the switch
   - Your Claude Code configuration is updated!

### Profile List Interface

The main window shows:
- **Header**: Claude Code directory path + settings button (gear icon)
- **Profile List**: Name, Base URL, masked Auth Token
- **Active Indicator**: ✓ for currently active profile
- **Action Buttons**: Create, Edit, Delete, Duplicate

### Managing Profiles

#### Edit Profile
- Select profile from list
- Click "Edit" button
- Modify name or configuration
- Save changes

#### Delete Profile
- Select profile from list
- Click "Delete" button
- Confirm deletion
- **Note**: Cannot delete currently active profile

#### Duplicate Profile
- Select profile from list
- Click "Duplicate" button
- Enter new profile name
- Create copy with same configuration

## Command Line Interface

For automation and scripting, use the CLI:

```bash
# List all profiles
uv run python src/cli.py profile list

# Create profile from file
uv run python src/cli.py profile create Production --file prod-config.json

# Apply profile
uv run python src/cli.py profile apply Development

# Show current status
uv run python src/cli.py config status

# Create backup
uv run python src/cli.py config backup
```

### CLI Output Formats

```bash
# Table format (default)
uv run python src/cli.py profile list

# JSON format for scripting
uv run python src/cli.py profile list --format json

# YAML format for configuration files
uv run python src/cli.py profile show Production --format yaml
```

## Configuration Examples

### Development Profile
```json
{
    "env": {
        "ANTHROPIC_BASE_URL": "https://api.dev.anthropic.com",
        "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-dev-token"
    },
    "model": "claude-3-haiku-20240307",
    "max_tokens": 4096,
    "temperature": 0.7
}
```

### Production Profile
```json
{
    "env": {
        "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
        "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-prod-token"
    },
    "model": "claude-3-opus-20240229",
    "max_tokens": 8192,
    "temperature": 0.1
}
```

### Testing Profile
```json
{
    "env": {
        "ANTHROPIC_BASE_URL": "https://api.test.anthropic.com",
        "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-test-token"
    },
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 2048,
    "temperature": 0.5
}
```

## Advanced Features

### Backup and Restore

#### Automatic Backups
The application automatically creates backups before switching profiles:
- Backup location: `~/.claude/backups/`
- Filename: `settings.json.backup.YYYYMMDD_HHMMSS`
- Default retention: 10 most recent backups

#### Manual Backup
```bash
# Create backup
uv run python src/cli.py config backup

# List available backups
uv run python src/cli.py config backup --list

# Restore from backup
uv run python src/cli.py config backup --restore settings.json.backup.20251017_143052
```

### Settings Configuration

Access settings via the gear icon in the main window:

#### Basic Settings
- **Claude Code Directory**: Path to Claude Code configuration
- **Backup Retention**: Number of backups to keep (1-50)
- **Theme**: Light, Dark, or System
- **Log Level**: DEBUG, INFO, WARNING, ERROR

#### Advanced Settings
- **Window Size**: Remember last window dimensions
- **Auto-refresh**: Update profile list automatically
- **Confirmation dialogs**: Show confirmations for destructive operations

### Security Considerations

#### API Token Handling
- Tokens are masked in the interface (e.g., `sk-ant...9029`)
- Full tokens shown only in edit mode with visibility toggle
- Tokens never logged to files
- Consider encryption for stored tokens (future enhancement)

#### File Permissions
- Application requires write access to Claude Code settings
- Backup files created with restrictive permissions
- Database file protected by user directory permissions

## Troubleshooting

### Common Issues

#### "Claude Code configuration not found"
**Solution**:
1. Check Claude Code installation
2. Verify settings.json exists in `~/.claude/`
3. Use settings dialog to specify custom path

#### "Permission denied" errors
**Solution**:
1. Ensure write permissions to `~/.claude/settings.json`
2. Run application with appropriate user permissions
3. Check if Claude Code has the file locked

#### "Invalid JSON configuration"
**Solution**:
1. Validate JSON syntax using online validator
2. Check for missing commas, brackets, or quotes
3. Use "Validate JSON" button in profile editor

#### Profile switching not working
**Solution**:
1. Check Claude Code is not running (it may lock settings file)
2. Restart Claude Code after switching profiles
3. Check application logs for error details

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# GUI with debug logging
uv run python src/main.py --log-level DEBUG

# CLI with debug logging
uv run python src/cli.py --log-level DEBUG config status
```

Log files are stored in:
- **Windows**: `%APPDATA%/claude-config-switcher/logs/`
- **macOS**: `~/Library/Logs/claude-config-switcher/`
- **Linux**: `~/.local/share/claude-config-switcher/logs/`

### Reset Application

To reset all application data:

```bash
# WARNING: This deletes all profiles and settings
rm -rf ~/.claude-config-switcher/
rm -rf data/profiles.db
```

## Development

### Project Structure
```
src/
├── main.py              # GUI entry point
├── cli.py               # CLI entry point
├── models/              # Data models
├── services/            # Business logic
├── storage/             # Database operations
├── gui/                 # GUI components
└── utils/               # Utilities

tests/                   # Test suite
scripts/                 # Build scripts
data/                    # Runtime data
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/unit/test_profile_service.py
```

### Building Executable
```bash
# Build standalone executable
uv run python scripts/build.py

# Output: dist/claude-config-switcher.exe (Windows)
```

### Adding Dependencies
```bash
# Add new dependency
uv add new-package

# Add development dependency
uv add --dev pytest-mock
```

## Support

### Documentation
- **Feature Specification**: [spec.md](./spec.md)
- **Implementation Plan**: [plan.md](./plan.md)
- **Data Model**: [data-model.md](./data-model.md)
- **API Contracts**: [contracts/](./contracts/)

### Getting Help
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share experiences
- **Documentation**: Check the docs/ folder for detailed guides

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request
5. Follow the constitution requirements in development

## Next Steps

1. **Create your first profile** with your Claude Code configuration
2. **Set up backup strategy** for important configurations
3. **Explore CLI interface** for automation opportunities
4. **Configure settings** to match your workflow
5. **Share profiles** with your team (export/import feature coming soon)

Enjoy switching between Claude Code configurations effortlessly!