# Claude Code Configuration Switcher - Claude Context

**Project**: claude-config-switcher
**Purpose**: Claude AI assistant context for this project

## Project Overview

This is a desktop GUI application for switching Claude Code configuration profiles. Users can create, edit, and switch between different Claude Code configurations without manually editing JSON files.

## Technology Stack

- **Language**: Python >=3.13
- **GUI Framework**: CustomTkinter (modern Tkinter-based UI)
- **Database**: SQLite3 (built-in)
- **Packaging**: PyInstaller for standalone executables
- **Testing**: pytest
- **Package Manager**: uv (UV-First principle)

## Project Structure

```
src/
├── main.py              # GUI entry point
├── cli.py               # CLI entry point (for automation/testing)
├── models/
│   ├── profile.py       # Profile data model
│   └── config.py        # Configuration data model
├── services/
│   ├── profile_service.py      # Profile CRUD operations
│   ├── config_service.py       # Claude Code settings file I/O
│   └── validation_service.py   # JSON validation logic
├── storage/
│   └── database.py      # SQLite database operations
├── gui/
│   ├── app.py           # Main application window
│   ├── widgets/
│   │   ├── profile_list.py     # Profile list widget
│   │   ├── profile_editor.py   # Profile create/edit dialog
│   │   └── settings_dialog.py  # Settings/config dialog
│   └── assets/
│       └── icons/       # UI assets
└── utils/
    ├── logger.py        # Structured logging setup
    └── paths.py         # Path detection (.claude directory)
```

## Key Components

### Configuration Profiles
- Store complete Claude Code JSON configurations
- Extract and display Base URL and Auth Token for UI
- Hash-based active profile detection
- Backup/restore functionality

### Claude Code Integration
- Auto-detects `~/.claude/settings.json` location
- Creates backups before configuration changes
- Applies profiles by writing to settings.json
- Handles file locking and permission errors

### Security Features
- API token masking in display (sk-ant...9029)
- Sensitive key detection patterns
- No logging of full authentication tokens
- Input validation for injection prevention

## Development Guidelines

### Constitution Compliance
- **UV-First**: All commands use `uv run`
- **Test-First**: TDD workflow enforced
- **CLI-First**: CLI fallback for automation/testing
- **Simplicity**: Direct SQLite and file I/O, no over-abstraction

### Code Style
- Follow Python PEP 8
- Use type hints consistently
- Document all public methods
- Implement proper error handling

### Testing Strategy
- Unit tests for all business logic
- Integration tests for file I/O and GUI flows
- Contract tests for service interfaces
- CLI tests for automation scenarios

## Common Commands

```bash
# Development
uv sync                    # Install dependencies
uv run python src/main.py # Run GUI
uv run python src/cli.py  # Run CLI

# Testing
uv run pytest            # Run all tests
uv run pytest --cov=src # Run with coverage

# Building
uv run python scripts/build.py  # Create executable
```

## JSON Configuration Format

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

## Important Patterns

### Error Handling
- Use structured logging with appropriate levels
- Handle file permission errors gracefully
- Provide user-friendly error messages
- Implement proper cleanup on failures

### File Operations
- Atomic writes (temp file + rename)
- Always create backups before modifications
- Handle cross-platform path differences
- Validate file permissions before operations

### Database Operations
- Use parameterized queries
- Implement proper transaction handling
- Create indexes for performance
- Handle connection errors gracefully

## Configuration Detection

The application searches for Claude Code configuration in:
- **Windows**: `C:\Users\<username>\.claude\settings.json`
- **macOS**: `~/.claude/settings.json`
- **Linux**: `~/.claude/settings.json`

Users can override this path in the settings dialog.

## CLI Interface Examples

```bash
# List profiles
uv run python src/cli.py profile list

# Create profile
uv run python src/cli.py profile create "Production" --file prod.json

# Apply profile
uv run python src/cli.py profile apply "Production"

# Show status
uv run python src/cli.py config status

# Create backup
uv run python src/cli.py config backup
```

## Future Enhancements (Not in MVP)

- Cloud sync integration
- Profile import/export
- Configuration templates
- Encryption for stored sensitive data
- Multi-profile merging
- Advanced search and filtering

This context provides Claude with the essential information needed to assist with development tasks, code generation, and problem-solving for this project.