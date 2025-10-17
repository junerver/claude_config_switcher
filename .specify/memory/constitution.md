<!--
Sync Impact Report:
Version: 0.0.0 → 1.0.0
Reason: Initial constitution ratification (MAJOR bump for first version)

Modified Principles:
- All principles defined for the first time

Added Sections:
- Core Principles (5 principles established)
- Package Management Requirements
- Development Workflow
- Governance

Templates Status:
- ✅ plan-template.md: Constitution Check section compatible
- ✅ spec-template.md: Requirements and testing sections align
- ✅ tasks-template.md: Phase structure and testing guidance align
- ⚠ Command files: Should reference this constitution when discussing project-specific rules

Follow-up TODOs:
- None (all placeholders filled)
-->

# claude-config-switcher Constitution

## Core Principles

### I. UV-First Tooling (NON-NEGOTIABLE)

**uv** is the exclusive tool for all Python package management, script execution, and project operations.

Rules:
- MUST use `uv run` to execute Python scripts and entry points
- MUST use `uv add` / `uv remove` for dependency management
- MUST use `uv sync` to synchronize project dependencies
- MUST use `uv pip` if direct pip operations are required
- MUST NOT use bare `python`, `pip`, or `python -m` commands

Rationale: Ensures consistent dependency resolution, reproducible builds, and unified tooling across all development environments. Eliminates version conflicts and "works on my machine" issues.

### II. CLI-First Interface

Every feature MUST expose functionality via command-line interface with text-based input/output protocol.

Rules:
- Standard input/arguments → standard output for data
- Errors and diagnostics → standard error
- Support both JSON and human-readable output formats where applicable
- Exit codes MUST follow POSIX conventions (0 = success, non-zero = error)

Rationale: CLI-first design enables automation, scripting, integration testing, and composability with other tools. Text protocols ensure debuggability and transparency.

### III. Test-First Development (NON-NEGOTIABLE)

Test-Driven Development (TDD) is mandatory for all feature implementation.

Rules:
- Tests MUST be written before implementation code
- Tests MUST fail initially (Red phase)
- Implementation proceeds only after test approval
- Implementation MUST make tests pass (Green phase)
- Refactoring follows only after tests pass (Refactor phase)
- Red-Green-Refactor cycle strictly enforced

Rationale: TDD ensures requirements are testable, code is designed for testability, and regressions are caught immediately. Executable specifications serve as living documentation.

### IV. Integration Testing for Contracts

Integration tests are REQUIRED for interface boundaries and cross-component interactions.

Focus areas requiring integration tests:
- New library contract tests (CLI interface, API endpoints)
- Contract changes to existing interfaces
- Inter-service or inter-module communication
- Shared data schemas and protocols

Rationale: Unit tests verify isolated behavior; integration tests verify components work together correctly. Contracts define boundaries that must remain stable.

### V. Simplicity and Observability

Start simple, maintain debuggability, and follow YAGNI (You Aren't Gonna Need It) principles.

Rules:
- Prefer simple solutions over complex architectures
- Text-based I/O ensures debuggability by default
- Structured logging REQUIRED for all significant operations
- Avoid premature optimization and unnecessary abstraction
- Complexity MUST be justified in implementation plans

Rationale: Simple systems are easier to understand, debug, and maintain. Observability through logging and text protocols enables effective troubleshooting in production.

## Package Management Requirements

### UV Workflow Standards

All Python operations MUST use uv. Common patterns:

```bash
# Running scripts
uv run python main.py        # Run main module
uv run pytest                # Run tests
uv run mypy src/             # Run type checker

# Dependency management
uv add requests              # Add dependency
uv add --dev pytest          # Add dev dependency
uv remove requests           # Remove dependency
uv sync                      # Sync lockfile to environment

# Direct pip operations (only when necessary)
uv pip install <package>     # Install package
uv pip list                  # List installed packages
```

### Prohibited Commands

The following commands MUST NOT be used:
- `python <script>.py` → use `uv run python <script>.py`
- `pip install` → use `uv add` or `uv pip install`
- `pip freeze` → use `uv pip list` or inspect `uv.lock`
- `python -m <module>` → use `uv run python -m <module>`

## Development Workflow

### Feature Development Process

1. **Specification**: Define requirements in spec.md with user stories and acceptance criteria
2. **Planning**: Create implementation plan with technical context and structure
3. **Task Generation**: Break down into actionable, testable tasks
4. **Test-First Implementation**: Write tests → verify failure → implement → verify success
5. **Integration**: Ensure contracts and interfaces work correctly
6. **Validation**: Run full test suite and verify against acceptance criteria

### Code Review Requirements

All pull requests MUST verify:
- Constitution compliance (especially UV-first and test-first principles)
- Tests present and passing
- Integration tests for contract changes
- Logging and observability for significant operations
- Simplicity justification if complexity introduced

### Quality Gates

Before merging:
- All tests MUST pass (`uv run pytest`)
- Type checking MUST pass if configured (`uv run mypy`)
- Code coverage targets MUST be met if defined
- Integration tests MUST pass for contract changes
- Documentation MUST be updated for user-facing changes

## Governance

### Amendment Process

Constitution amendments require:
1. Documented rationale for the change
2. Impact analysis on existing code and workflows
3. Migration plan if backward incompatible
4. Approval from project maintainers
5. Version bump according to semantic versioning

### Versioning Policy

Constitution version follows MAJOR.MINOR.PATCH:
- **MAJOR**: Backward incompatible governance changes, principle removals/redefinitions
- **MINOR**: New principles added, material expansions to guidance
- **PATCH**: Clarifications, wording improvements, typo fixes

### Compliance Review

All PRs, code reviews, and design documents MUST verify compliance with this constitution.

Complexity MUST be justified:
- Document why simpler alternatives are insufficient
- Explain specific problems requiring the complexity
- Include in implementation plan's "Complexity Tracking" section

### Runtime Development Guidance

For day-to-day development practices, tooling setup, and operational procedures, refer to project documentation (README.md, docs/, quickstart guides). This constitution defines non-negotiable principles; runtime guidance provides implementation details.

**Version**: 1.0.0 | **Ratified**: 2025-10-17 | **Last Amended**: 2025-10-17
