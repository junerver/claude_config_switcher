# Claude Code Configuration Switcher

A desktop GUI application that enables users to quickly switch between different Claude Code configuration profiles. Users can manage multiple configuration profiles (create, edit, delete, duplicate) and apply them to Claude Code's settings with a double-click.

## Features

- **Profile Management**: Create, edit, delete, and duplicate configuration profiles
- **Quick Switching**: Double-click profiles to apply them to Claude Code
- **Visual Indicators**: See which profile is currently active
- **JSON Validation**: Real-time validation of configuration JSON
- **Backup Support**: Automatic backups before profile changes
- **GUI and CLI**: Both graphical and command-line interfaces
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.13+
- uv package manager
- Claude Code installed and configured

## Quick Start

### Development Setup

1. Clone the repository
2. Set up the development environment:
   ```bash
   uv run python scripts/dev_setup.py
   ```

### Running the Application

#### GUI Mode
```bash
uv run python src/main.py
```

#### CLI Mode
```bash
# List all profiles
uv run python src/cli.py profile list

# Create a new profile
uv run python src/cli.py profile create Production --file prod-config.json

# Apply a profile
uv run python src/cli.py profile apply Development

# Show status
uv run python src/cli.py config status
```

### Building Executable

```bash
# Build standalone executable
uv run python scripts/build.py

# Create portable package
uv run python scripts/build.py --portable

# Clean build artifacts
uv run python scripts/build.py --clean
```

## Configuration

The application stores configuration in:
- **Windows**: `%APPDATA%/claude-config-switcher/config.json`
- **macOS**: `~/.config/claude-config-switcher/config.json`
- **Linux**: `~/.config/claude-config-switcher/config.json`

Profiles are stored in a SQLite database at `data/profiles.db`.

## Usage

### Getting Started

1. **Launch the application**:
   ```bash
   uv run python src/main.py
   ```

2. **Create your first profile**:
   - Click **"Create Profile"** button
   - Enter a name (e.g., "My Production Config")
   - Paste your Claude Code JSON configuration
   - Click **"Save"**

3. **Switch between profiles**:
   - **Double-click** any profile to activate it
   - The app automatically backs up your current settings
   - A success message confirms the switch

### Creating Profiles

1. Click the **"Create Profile"** button at the bottom of the window
2. Enter a descriptive profile name (e.g., "Production", "Development", "Testing")
3. Paste your JSON configuration in the text editor
4. (Optional) Click the **"Show/Hide Tokens"** checkbox to reveal or mask API tokens
5. Click **"Save"** to create the profile

Example configuration:
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
    "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-your-token-here"
  },
  "model": "claude-3-opus-20240229",
  "max_tokens": 4096,
  "temperature": 0.1
}
```

### Managing Profiles

#### Viewing Profiles
- All profiles are displayed in a scrollable list
- **Active profile**: Marked with ✓ checkmark and green border
- **Selected profile**: Highlighted with blue border
- **Inactive profiles**: Gray border

#### Profile Actions
- **Single-click**: Select a profile (blue highlight)
- **Double-click**: Activate the profile (apply to Claude Code)
- **Right-click**: Open context menu with options:
  - **Preview Profile**: View full JSON configuration
  - **Activate Profile**: Apply this profile to Claude Code
  - **Edit Profile**: Modify name or configuration
  - **Duplicate Profile**: Create a copy with a new name
  - **Delete Profile**: Remove profile (with confirmation)

#### Scrolling
- Use **mouse wheel** to scroll through many profiles
- Works on both Windows and Linux

### Editing Profiles

1. **Right-click** a profile and select **"Edit Profile"**
2. Modify the profile name or JSON configuration
3. Use **"Validate JSON"** button to check for syntax errors
4. Click **"Save"** to update the profile

### Switching Profiles

**GUI Method:**
1. **Double-click** the profile you want to activate
2. Confirm the activation dialog
3. The app will:
   - Create a backup of your current Claude Code settings
   - Apply the selected profile's configuration
   - Mark the profile as active with ✓ and green border

**CLI Method:**
```bash
# Apply a profile by name
uv run python src/cli.py profile apply "Production"

# List all profiles to see available names
uv run python src/cli.py profile list
```

### Configuration Templates

You can use these templates as starting points:

**Production API (Anthropic Direct)**
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
    "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-xxxxx"
  },
  "model": "claude-3-opus-20240229",
  "max_tokens": 4096,
  "temperature": 0.1
}
```

**Development (Higher Temperature)**
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
    "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-xxxxx"
  },
  "model": "claude-3-sonnet-20240229",
  "max_tokens": 2048,
  "temperature": 0.7
}
```

**Custom Proxy**
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://your-proxy.example.com/v1",
    "ANTHROPIC_AUTH_TOKEN": "your-proxy-token"
  },
  "model": "claude-3-haiku-20240307",
  "max_tokens": 4096,
  "temperature": 0.5
}
```

### Settings

Click the gear icon to configure:
- **Claude Code Location**: Override auto-detected settings.json path
- **Backup Settings**: Configure backup retention and location
- **Theme**: Choose light or dark mode
- **Logging**: Set log level and output location

### Keyboard Shortcuts

The application supports the following keyboard shortcuts for faster workflow:

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | Create new profile |
| `Ctrl+E` | Edit selected profile |
| `Del` | Delete selected profile |
| `Ctrl+D` | Duplicate selected profile |
| `F5` or `Ctrl+R` | Refresh profile list |
| `Ctrl+,` | Open settings dialog |
| `Ctrl+Q` | Quit application |

**Note**: All shortcuts are also displayed in the button labels for easy reference.

## Development

### Project Structure

```
src/
   main.py              # GUI entry point
   cli.py               # CLI entry point
   models/              # Data models
   services/            # Business logic
   storage/             # Database operations
   gui/                 # GUI components
   utils/               # Utilities

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
uv run pytest tests/unit/test_profile_model.py
```

### Adding Dependencies

```bash
# Add new dependency
uv add new-package

# Add development dependency
uv add --dev pytest-mock
```

## Architecture

The application follows a clean architecture with:

- **Models**: Data structures for profiles and configuration
- **Services**: Business logic for profile management, validation, and file operations
- **Storage**: SQLite database operations
- **GUI**: CustomTkinter-based user interface
- **CLI**: Command-line interface for automation

## Troubleshooting

### Common Issues

**Profile list not displaying**
- Check that the database file exists in `data/profiles.db`
- Verify the application has write permissions to the data directory

**Cannot find Claude Code settings**
- The app auto-detects `~/.claude/settings.json`
- Use the Settings dialog (gear icon) to manually specify the path

**Profile not activating**
- Ensure Claude Code is not running when switching profiles
- Check that you have write permissions to the Claude Code settings file
- Review the backup directory for recent backups

**Mouse wheel scrolling not working**
- This feature was recently added and should work on Windows and Linux
- If issues persist, use the scrollbar on the right side of the profile list

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run the test suite
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and support, please create an issue in the GitHub repository.
