# Implementation Plan: Claude Code Configuration Switcher

**Branch**: `001-config-switcher-gui` | **Date**: 2025-10-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-config-switcher-gui/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a desktop GUI application that enables users to quickly switch between different Claude Code configuration profiles. Users can manage multiple configuration profiles (create, edit, delete, duplicate) and apply them to Claude Code's settings with a double-click. The application displays the current active profile, validates JSON configurations, and provides visual feedback for all operations.

Technical approach: Single-window desktop application using CustomTkinter for modern GUI, SQLite for local profile storage, and file I/O for Claude Code settings.json manipulation. Supports PyInstaller packaging for standalone executable distribution.

## Technical Context

**Language/Version**: Python >=3.13 (per pyproject.toml)
**Primary Dependencies**: CustomTkinter (GUI framework), SQLite3 (built-in, profile storage)
**Storage**: SQLite database for profiles, JSON file I/O for Claude Code settings
**Testing**: pytest (unit/integration), pytest-qt or similar for GUI testing
**Target Platform**: Windows desktop (primary), cross-platform capable (Windows/macOS/Linux)
**Project Type**: Single desktop application
**Performance Goals**: <3s startup time with 50 profiles, <5s profile switching, <10s CRUD operations
**Constraints**: Must support PyInstaller packaging, must handle locked/read-only files gracefully
**Scale/Scope**: Single-user desktop app, 50+ profiles supported, <100MB memory footprint

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### UV-First Tooling (NON-NEGOTIABLE)
- ✅ **PASS**: All commands use `uv run` for execution
- ✅ **PASS**: Dependencies managed via `uv add`/`uv remove`
- ✅ **PASS**: No bare `python` or `pip` commands in workflow
- ✅ **PASS**: PyInstaller invoked via `uv run pyinstaller`

### CLI-First Interface
- ⚠️ **PARTIAL**: Primary interface is GUI (CustomTkinter), not CLI
- **JUSTIFICATION**: Feature explicitly requires GUI for user-friendly profile switching. However, we will provide a CLI fallback for automation/scripting use cases and testing.
- **MITIGATION**: Implement CLI module supporting profile operations via command-line arguments, ensuring text-based I/O for scripting and testing

### Test-First Development (NON-NEGOTIABLE)
- ✅ **PASS**: TDD workflow will be enforced
- ✅ **PASS**: Tests written before implementation
- ✅ **PASS**: Red-Green-Refactor cycle in tasks

### Integration Testing for Contracts
- ✅ **PASS**: File I/O contract tests required (settings.json read/write)
- ✅ **PASS**: Database contract tests required (SQLite operations)
- ✅ **PASS**: GUI interaction contract tests required (profile switching flow)

### Simplicity and Observability
- ✅ **PASS**: Simple architecture (GUI → Service → Storage)
- ✅ **PASS**: Structured logging for all file operations and errors
- ✅ **PASS**: No unnecessary abstractions (direct SQLite, file I/O)

**Gate Status**: ✅ PASS with justification

**Complexity Justification**: GUI requirement necessitates deviation from pure CLI-first principle, but is core to user value proposition. CLI fallback maintains testability and automation capabilities.

## Re-evaluation After Phase 1 Design

The constitution check status remains **PASS** with additional clarifications:

### CLI-First Interface - Updated Assessment
**Status**: ✅ PASS - Mitigated

**New Evidence**:
- CLI interface contract ([cli_interface.md](./contracts/cli_interface.md)) provides comprehensive automation capabilities
- CLI supports all GUI operations: profile CRUD, application, backup/restore, status checking
- CLI includes multiple output formats (table, JSON, YAML) for integration
- CLI exit codes standardized for scripting and automation
- CLI interface enables integration testing without GUI dependencies

**Final Assessment**: The application provides a robust CLI interface that fully satisfies the CLI-first principle while maintaining the GUI for user-friendly interaction. The CLI is not just a fallback but a first-class interface for automation, scripting, and testing.

### Updated Compliance Summary

- **UV-First Tooling**: ✅ PASS - All operations use uv
- **CLI-First Interface**: ✅ PASS - Comprehensive CLI with full feature parity
- **Test-First Development**: ✅ PASS - TDD workflow defined in contracts
- **Integration Testing**: ✅ PASS - Contract tests defined for all boundaries
- **Simplicity & Observability**: ✅ PASS - Direct SQLite, file I/O, structured logging

**Final Gate Status**: ✅ PASS - All constitutional requirements met with appropriate justifications documented.

## Project Structure

### Documentation (this feature)

```
specs/001-config-switcher-gui/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── profile_service.md
│   ├── config_service.md
│   └── cli_interface.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
src/
├── main.py              # Application entry point (GUI mode)
├── cli.py               # CLI entry point (text-based automation)
├── models/
│   ├── __init__.py
│   ├── profile.py       # Profile data model
│   └── config.py        # Configuration data model
├── services/
│   ├── __init__.py
│   ├── profile_service.py      # Profile CRUD operations
│   ├── config_service.py       # Claude Code settings file I/O
│   └── validation_service.py   # JSON validation logic
├── storage/
│   ├── __init__.py
│   └── database.py      # SQLite database operations
├── gui/
│   ├── __init__.py
│   ├── app.py           # Main application window
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── profile_list.py     # Profile list widget
│   │   ├── profile_editor.py   # Profile create/edit dialog
│   │   └── settings_dialog.py  # Settings/config dialog
│   └── assets/
│       └── icons/       # Gear icon and other UI assets
└── utils/
    ├── __init__.py
    ├── logger.py        # Structured logging setup
    └── paths.py         # Path detection (.claude directory)

scripts/
├── build.py             # PyInstaller build script
└── dev_setup.py         # Development environment setup

tests/
├── contract/
│   ├── test_profile_service_contract.py
│   ├── test_config_service_contract.py
│   └── test_cli_contract.py
├── integration/
│   ├── test_profile_switching_flow.py
│   ├── test_profile_crud_flow.py
│   └── test_gui_integration.py
└── unit/
    ├── test_profile_model.py
    ├── test_config_model.py
    ├── test_profile_service.py
    ├── test_config_service.py
    ├── test_validation_service.py
    └── test_database.py

data/
└── profiles.db          # SQLite database (created at runtime)
```

**Structure Decision**: Single desktop application structure selected. Source code organized by layer (models, services, storage, gui, utils) to support both GUI and CLI interfaces. Test structure follows contract/integration/unit separation per constitution requirements. Scripts directory contains build and development tooling. The `/src` directory contains all source code as specified by user requirements.

## Complexity Tracking

*No constitution violations requiring justification. CLI-First partial deviation is documented in Constitution Check section above.*

