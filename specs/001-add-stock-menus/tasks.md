# Tasks: Add Stock Market Menu Items

**Input**: Design documents from `/specs/001-add-stock-menus/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan
- [x] T002 Initialize Python project with akshare dependencies
- [x] T003 [P] Configure linting and formatting tools

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [x] T004 [P] Add akshare methods to ApiService for market overviews in src/services/api_service.py
- [x] T005 Verify existing CLI command patterns and error handling in src/cli/commands.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Access Shanghai Stock Exchange Overview (Priority: P1) 🎯 MVP

**Goal**: Provide CLI command to fetch and display Shanghai Stock Exchange overall market data

**Independent Test**: Run `stocklib sse-summary` and verify it returns JSON with market metrics

### Implementation for User Story 1

- [x] T006 [US1] Add sse_summary method to ApiService in src/services/api_service.py
- [x] T007 [US1] Implement sse-summary CLI command in src/cli/commands.py
- [x] T008 [US1] Add command help text and examples for sse-summary

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Access Shenzhen Stock Exchange Security Statistics (Priority: P1)

**Goal**: Provide CLI command to fetch and display Shenzhen security category statistics

**Independent Test**: Run `stocklib szse-summary` and verify it returns JSON with security type data

### Implementation for User Story 2

- [x] T009 [US2] Add szse_summary method to ApiService in src/services/api_service.py
- [x] T010 [US2] Implement szse-summary CLI command in src/cli/commands.py
- [x] T011 [US2] Add command help text and examples for szse-summary

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - View Regional Trading Rankings (Priority: P2)

**Goal**: Provide CLI command to fetch and display regional trading rankings for Shenzhen

**Independent Test**: Run `stocklib szse-area-summary` and verify it returns JSON with regional trading data

### Implementation for User Story 3

- [x] T012 [US3] Add szse_area_summary method to ApiService in src/services/api_service.py
- [x] T013 [US3] Implement szse-area-summary CLI command in src/cli/commands.py
- [x] T014 [US3] Add command help text and examples for szse-area-summary

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Access Stock Industry Transaction Data (Priority: P2)

**Goal**: Provide CLI command to fetch and display stock industry transaction data

**Independent Test**: Run `stocklib szse-sector-summary` and verify it returns JSON with industry sector data

### Implementation for User Story 4

- [x] T015 [US4] Add szse_sector_summary method to ApiService in src/services/api_service.py
- [x] T016 [US4] Implement szse-sector-summary CLI command in src/cli/commands.py
- [x] T017 [US4] Add command help text and examples for szse-sector-summary

---

## Phase 7: User Story 5 - View Shanghai Daily Stock Overview (Priority: P2)

**Goal**: Provide CLI command to fetch and display Shanghai daily stock transaction details

**Independent Test**: Run `stocklib sse-daily-deals` and verify it returns JSON with daily transaction data

### Implementation for User Story 5

- [x] T018 [US5] Add sse_deal_daily method to ApiService in src/services/api_service.py
- [x] T019 [US5] Implement sse-daily-deals CLI command in src/cli/commands.py
- [x] T020 [US5] Add command help text and examples for sse-daily-deals

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T021 [P] Update CLI help documentation in src/cli/commands.py
- [x] T022 [P] Add command usage examples to quickstart.md
- [x] T023 [P] Run quickstart.md validation
- [x] T024 Test all commands with error scenarios
- [x] T025 [P] Code cleanup and linting across all new code

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- ApiService method before CLI command
- Core implementation before help text
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All user stories are independent and can be implemented in parallel

---

## Parallel Example: User Story 1

```bash
# Launch User Story 1 tasks together:
Task: "Add sse_summary method to ApiService in src/services/api_service.py"
Task: "Implement sse-summary CLI command in src/cli/commands.py"
Task: "Add command help text and examples for sse-summary"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Shanghai overview)
4. **STOP and VALIDATE**: Test `stocklib sse-summary` independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Stories 3-5 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Stories 1 & 3 (Shanghai-focused)
   - Developer B: User Stories 2 & 4 (Shenzhen-focused)
   - Developer C: User Story 5 (Daily overview)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- All tasks follow strict checklist format with IDs and file paths
- Stop at any checkpoint to validate story independently
- All 5 CLI commands are independent and can be implemented in any order after foundational work</content>
<parameter name="file_path">specs/001-add-stock-menus/tasks.md