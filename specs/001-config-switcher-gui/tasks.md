---
description: "Task list for feature implementation"
---

# Tasks: Claude Code Configuration Switcher

**Input**: Design documents from `/specs/001-config-switcher-gui/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Tests are optional - only generate if explicitly requested

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description with file path`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

<!--
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.

  The /speckit.tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/

  Tasks MUST be organized by user story so each story can be:
  - Developed independently
  - Tested independently
  - Delivered as an MVP increment

  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan
- [X] T002 Initialize Python project with CustomTkinter dependencies
- [X] T003 [P] Configure logging and error handling setup

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [X] T004 Setup SQLite database schema and migrations framework
- [X] T005 [P] Implement authentication/authorization framework
- [X] T006 [P] Setup API routing and middleware structure
- [X] T007 Create base models/entities that all stories depend on
- [X] T008 Configure error handling and logging infrastructure
- [X] T009 Setup environment configuration management

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Switch Configuration Profiles (Priority: P1) 🎯 MVP

**Goal**: Enable users to quickly switch between different Claude Code configuration profiles by double-clicking

**Independent Test**: Can be fully tested by creating a profile, double-clicking it, and verifying the Claude Code configuration file reflects the selected profile content

### Implementation for User Story 1

- [X] T010 [P] [US1] Create Profile data model in src/models/profile.py
- [X] T011 [P] [US1] Implement ConfigService for settings.json operations in src/services/config_service.py
- [X] T012 [P] [US1] Create ProfileService for profile CRUD operations in src/services/profile_service.py
- [X] T013 [P] [US1] Implement database operations in src/storage/database.py
- [X] T014 [P] [US1] Create main application window in src/gui/app.py
- [X] T015 [P] [US1] Implement profile list widget in src/gui/widgets/profile_list.py
- [X] T016 [US1] Create GUI entry point in src/main.py
- [X] T017 [US1] Create CLI entry point in src/cli.py
- [X] T018 [US1] Implement profile switching logic (double-click handler)
- [X] T019 [US1] Add active profile detection and visual indicators
- [X] T020 [US1] Implement backup creation before profile application

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Manage Configuration Profiles (Priority: P2)

**Goal**: Enable users to create, edit, rename, duplicate, and delete configuration profiles

**Independent Test**: Can be tested by performing all CRUD operations (create, read, update, delete) on profiles and verifying each profile stores the correct key-value configuration data

### Implementation for User Story 2

- [X] T021 [P] [US2] Create profile editor dialog in src/gui/widgets/profile_editor.py
- [X] T022 [P] [US2] Implement profile creation workflow with validation
- [X] T023 [P] [US2] Implement profile editing workflow with validation
- [X] T024 [P] [US2] Add profile deletion with confirmation dialog
- [X] T025 [P] [US2] Implement profile duplication functionality
- [X] T026 [US2] Add profile rename capability
- [X] T027 [US2] Create settings configuration dialog in src/gui/widgets/settings_dialog.py
- [X] T028 [P] [US2] Implement Claude Code path configuration
- [X] T029 [P] [US2] Add backup retention settings
- [X] T030 [P] [US2] Create application preferences management

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - View and Validate Profiles (Priority: P3)

**Goal**: Enable users to preview profile configurations and receive validation warnings

**Independent Test**: Can be tested by selecting a profile and viewing its full JSON content in the GUI, and by attempting to create or edit profiles with invalid JSON to verify validation warnings appear

### Implementation for User Story 3

- [X] T031 [P] [US3] Create JSON validation service in src/services/validation_service.py
- [X] T032 [P] [US3] Implement JSON syntax validation and error reporting
- [X] T033 [P] [US3] Add key detection and masking for sensitive data
- [X] T034 [P] [US3] Create profile preview dialog with formatted JSON display
- [X] T035 [P] [US3] Implement real-time JSON validation in profile editor
- [X] T036 [P] [US3] Add visual feedback for validation errors
- [X] T037 [P] [US3] Implement profile summary display in list view
- [X] T038 [P] [US3] Add warnings for potentially problematic configurations

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T039 [P] Documentation updates in docs/
- [X] T040 [P] Code cleanup and refactoring
- [X] T041 [P] Performance optimization across all stories
- [X] T042 [P] Error handling improvements
- [X] T043 [P] Cross-platform compatibility testing
- [X] T044 [P] Add PyInstaller build script in scripts/build.py
- [X] T045 [P] Create development setup script in scripts/dev_setup.py
- [X] T046 [P] Add comprehensive logging with structured format
- [X] T047 [P] Implement application settings persistence
- [X] T048 [P] Add keyboard shortcuts and accessibility features

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1, extends functionality
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Enhances US1 and US2 with validation

### Within Each User Story

- Models can be created in parallel (different files)
- Services can be developed in parallel once models are ready
- GUI components can be developed once services are defined
- Integration connects all components

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- GUI components can be developed in parallel once services are defined
- Utility modules can be developed in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all models and core services together:
Task: "Create Profile data model in src/models/profile.py"
Task: "Implement ConfigService for settings.json operations in src/services/config_service.py"
Task: "Implement ProfileService for profile CRUD operations in src/services/profile_service.py"
Task: "Implement database operations in src/storage/database.py"

# Launch GUI components together:
Task: "Create main application window in src/gui/app.py"
Task: "Implement profile list widget in src/gui/widgets/profile_list.py"

# Launch entry points together:
Task: "Create GUI entry point in src/main.py"
Task: "Create CLI entry point in src/cli.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (core switching)
   - Developer B: User Story 2 (profile management)
   - Developer C: User Story 3 (validation and preview)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- UV-First principle: All commands use `uv run` prefix
- CLI-First principle: CLI interface provides full feature parity
- Test-First principle: Tests written before implementation (if testing requested)
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
