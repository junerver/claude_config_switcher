# Research: Claude Code Configuration Switcher

**Feature**: 001-config-switcher-gui
**Date**: 2025-10-17
**Purpose**: Research technical decisions, best practices, and implementation patterns

## Technology Decisions

### 1. GUI Framework: CustomTkinter

**Decision**: Use CustomTkinter for the desktop GUI

**Rationale**:
- Modern, customizable Tkinter-based framework with native look and feel
- Cross-platform support (Windows, macOS, Linux)
- Lightweight with no heavy dependencies
- Good PyInstaller compatibility for executable packaging
- Active community and documentation
- Supports theming (dark/light modes)
- Easy integration with standard Python libraries

**Alternatives Considered**:
- **PyQt5/PySide6**: More powerful but heavier dependencies, licensing complexity (GPL/LGPL), larger executable size (~150MB)
- **wxPython**: Good cross-platform support but less modern UI appearance, steeper learning curve
- **Kivy**: Designed for mobile/touch, overkill for desktop-only app, non-native UI feel
- **Dear PyGui**: Fast but less mature ecosystem, fewer widgets for traditional desktop apps

**Best Practices**:
- Separate GUI logic from business logic (use MVC/MVVM pattern)
- Use CTk widgets (CTkButton, CTkEntry, CTkListbox) for consistency
- Implement async operations for file I/O to prevent UI freezing
- Use CTkScrollableFrame for profile list to handle 50+ profiles
- Validate inputs before passing to services layer

### 2. Database: SQLite3

**Decision**: Use SQLite3 (Python built-in) for profile storage

**Rationale**:
- Zero-configuration, serverless database
- Built into Python standard library (no external dependencies)
- File-based storage (single .db file, easy backup/migration)
- ACID-compliant transactions
- Excellent performance for single-user desktop apps
- PyInstaller-friendly (no runtime dependencies)

**Alternatives Considered**:
- **JSON file**: Simpler but no ACID guarantees, harder to query, corruption risk
- **PostgreSQL/MySQL**: Overkill for single-user app, requires server setup
- **TinyDB**: Pure Python but slower, less mature than SQLite

**Best Practices**:
- Use parameterized queries to prevent SQL injection
- Implement connection pooling or context managers
- Create indexes on frequently queried fields (profile name)
- Use transactions for multi-step operations
- Implement proper error handling and rollback
- Store schema version for future migrations

### 3. Packaging: PyInstaller

**Decision**: Use PyInstaller for creating standalone executables

**Rationale**:
- Mature and widely-used Python packaging tool
- Supports CustomTkinter and SQLite out-of-box
- Creates single executable or folder distribution
- Cross-platform build support
- Good documentation and community

**Alternatives Considered**:
- **py2exe**: Windows-only, less active development
- **cx_Freeze**: More complex configuration, larger output size
- **Nuitka**: Compiled Python (faster) but longer build times, more complex setup

**Best Practices**:
- Use `--onefile` for single executable distribution
- Include data files (icons, assets) via `--add-data` flag
- Test packaged executable on clean VM (no Python installed)
- Use `--windowed` to hide console window on Windows
- Create spec file for reproducible builds
- Handle resource paths correctly (use `sys._MEIPASS` for bundled resources)

### 4. Claude Code Configuration Location

**Decision**: Auto-detect `~/.claude/settings.json` with user override option

**Rationale**:
- Standard Claude Code configuration location on Windows: `C:\Users\<username>\.claude\settings.json`
- Cross-platform: `~/.claude/settings.json` (macOS/Linux)
- User may have custom installation path
- Need fallback mechanism if path doesn't exist

**Best Practices**:
- Use `pathlib.Path.home()` for cross-platform home directory detection
- Check multiple common locations (Windows, macOS, Linux)
- Allow user to configure custom path via settings dialog
- Validate path exists and is writable before operations
- Store user-configured path in application settings
- Provide clear error messages if path invalid

### 5. JSON Validation

**Decision**: Use Python's built-in `json` module with custom validation rules

**Rationale**:
- Built-in module (no dependencies)
- Fast and reliable
- Sufficient for configuration validation needs
- Can add custom validation logic on top

**Best Practices**:
- Validate JSON syntax before saving profiles
- Check for required fields (`env` object structure)
- Detect sensitive fields (API keys, tokens) for masking in UI
- Provide user-friendly error messages (line/column of JSON errors)
- Allow optional validation bypass for advanced users
- Log validation failures for debugging

### 6. Error Handling & Logging

**Decision**: Use Python's `logging` module with structured logging

**Rationale**:
- Standard library solution (no dependencies)
- Configurable log levels and handlers
- Easy integration with file/console output
- Supports structured logging formats

**Best Practices**:
- Log all file I/O operations (read/write settings.json)
- Log all database operations (CRUD on profiles)
- Log validation failures with context
- Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Write logs to file in user directory (`~/.claude-config-switcher/logs/`)
- Rotate log files to prevent unbounded growth
- Include timestamps, log levels, and contextual information

### 7. Key Detection & Masking

**Decision**: Pattern-based key detection with configurable sensitivity

**Rationale**:
- Common API key patterns: `*_API_KEY`, `*_TOKEN`, `*_SECRET`, `ANTHROPIC_AUTH_TOKEN`
- Need to display masked values in list view for security
- Full values stored in database (encrypted or plaintext based on user preference)

**Best Practices**:
- Use regex patterns to detect sensitive field names
- Mask middle characters (show first/last 4 chars): `88_9471...9029`
- Display full keys only in edit mode with visibility toggle
- Never log full key values
- Consider optional encryption for stored keys (future enhancement)

### 8. Active Profile Detection

**Decision**: Hash-based comparison of current settings.json with stored profiles

**Rationale**:
- Can't rely on metadata (user may edit settings.json externally)
- Need accurate detection of which profile is active
- Hash comparison is fast and reliable

**Best Practices**:
- Normalize JSON before hashing (consistent formatting, key ordering)
- Use SHA-256 for content hashing
- Cache hash values to avoid repeated file reads
- Re-check on profile list refresh
- Visual indicator (highlight, checkmark, different color) for active profile

### 9. File Backup & Recovery

**Decision**: Automatic backup before applying any configuration change

**Rationale**:
- Protect against configuration corruption
- Allow user to rollback changes
- Meet FR-012 requirement (preserve original)

**Best Practices**:
- Create timestamped backup: `settings.json.backup.20251017_143052`
- Keep last N backups (configurable, default 10)
- Provide "Restore Backup" option in settings
- Clean up old backups automatically
- Log backup operations
- Verify backup written successfully before applying new config

### 10. Concurrent Access Handling

**Decision**: File locking with retry mechanism and user feedback

**Rationale**:
- Claude Code may have settings.json open
- Multiple app instances possible (discouraged but handle gracefully)
- Need to handle read-only files

**Best Practices**:
- Use `fcntl.flock` (Unix) or `msvcrt.locking` (Windows) for file locking
- Retry mechanism with exponential backoff (3 attempts)
- Display clear error message if file locked/read-only
- Detect file changes by other processes (watch modification time)
- Offer "force overwrite" option with warning

## GUI Design Patterns

### Main Window Layout

**Pattern**: Single-window application with sidebar navigation

**Components**:
1. **Header**: Claude Code directory path display + settings button (gear icon)
2. **Profile List**: Scrollable list with multi-column display (Name, Base URL, Token preview)
3. **Action Buttons**: Create, Edit, Delete, Duplicate (context-sensitive enablement)

**Best Practices**:
- Use CTkScrollableFrame for profile list (handles overflow)
- Highlight active profile with distinct color/icon
- Show profile count and active status in header
- Implement double-click to apply profile
- Context menu (right-click) for quick actions

### Profile Editor Dialog

**Pattern**: Modal dialog with tabbed interface

**Components**:
1. **General Tab**: Profile name (required, unique)
2. **Configuration Tab**: JSON editor with syntax highlighting
3. **Preview Tab**: Formatted JSON display with key detection

**Best Practices**:
- Real-time JSON syntax validation
- Highlight detected keys (BASE_URL, AUTH_TOKEN)
- Mask sensitive values by default with toggle visibility
- Save/Cancel buttons with confirmation on unsaved changes
- Auto-format JSON on save (pretty-print)

### Settings Dialog

**Pattern**: Modal dialog with configuration options

**Components**:
1. Claude Code directory path (editable with file browser)
2. Backup retention count (spinner, 1-50)
3. Theme selection (light/dark mode)
4. Log level selection (DEBUG, INFO, WARNING, ERROR)

**Best Practices**:
- Validate path on change (directory exists, writable)
- Show current settings.json content preview
- Apply button with immediate effect
- Reset to defaults option

## Testing Strategy

### Unit Tests
- Profile model: CRUD operations, validation
- Config service: File I/O, JSON parsing, backup/restore
- Validation service: JSON syntax, key detection
- Database: SQLite operations, transactions

### Integration Tests
- Profile switching flow: GUI → Service → File
- CRUD flow: Create → Edit → Duplicate → Delete
- Active profile detection: Hash comparison accuracy

### Contract Tests
- Profile service contract: Method signatures, return types
- Config service contract: File operations, error handling
- CLI interface contract: Command-line arguments, exit codes

### GUI Testing
- Use pytest-qt or similar for GUI component testing
- Test widget interactions (button clicks, list selection)
- Mock file I/O and database for isolated GUI tests
- Verify visual feedback (success/error messages)

## Security Considerations

### API Key Handling
- Never log full API keys
- Mask in UI by default
- Consider encryption at rest (future enhancement)
- Clear clipboard after copy operations (future enhancement)

### File Permissions
- Validate write permissions before operations
- Handle permission denied errors gracefully
- Warn user if settings.json is world-readable

### Input Validation
- Sanitize profile names (prevent path traversal: `../`, null bytes)
- Validate JSON structure matches expected schema
- Limit profile name length (prevent database issues)
- Limit JSON size (prevent memory exhaustion)

## Performance Optimizations

### Startup Performance
- Lazy-load profile list (load on-demand if >100 profiles)
- Cache hash values in memory
- Use indexes on database queries

### UI Responsiveness
- Async file I/O operations (threading or asyncio)
- Progress indicators for long operations
- Debounce JSON validation (don't validate on every keystroke)

### Memory Management
- Don't load all profiles into memory simultaneously
- Use generators for large result sets
- Close database connections promptly

## Cross-Platform Considerations

### Path Handling
- Use `pathlib.Path` for all path operations
- Handle Windows vs. Unix path separators
- Respect platform-specific home directory locations

### File Locking
- Implement platform-specific locking (fcntl vs. msvcrt)
- Fallback to polling if locking unavailable

### Icon Assets
- Support multiple DPI/resolutions
- Use platform-appropriate icon formats (.ico for Windows, .icns for macOS)

## Future Enhancements

### Potential Features (not in MVP)
- Cloud sync (Google Drive, Dropbox)
- Profile import/export (share configurations)
- Configuration templates (starter profiles)
- Multi-profile activation (merge configurations)
- Command palette (keyboard shortcuts)
- Profile groups/categories
- Search/filter profiles
- Encryption at rest for sensitive keys
- Auto-update checker

### Technical Debt to Monitor
- Consider migrating to async/await for file I/O
- Evaluate JSON schema validation library (jsonschema)
- Consider configuration file versioning/migration strategy
- Monitor CustomTkinter updates for breaking changes

## Conclusion

All technology decisions support the core requirements: fast profile switching, reliable persistence, user-friendly GUI, and cross-platform compatibility. The stack (CustomTkinter + SQLite + PyInstaller) minimizes dependencies while maximizing reliability and ease of distribution.

Next steps: Proceed to Phase 1 (data model, contracts, quickstart).
