# Tasks: Database Migration and Stock Information Table

**Input**: Design documents from `/specs/001-database-migration-stock-info/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Contract and integration tests are required per constitution (test-first discipline)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **CLI tool**: `src/` at repository root
- **Backend API**: `backend/src/`
- **Frontend**: `frontend/src/`
- **Tests**: `tests/` at repository root

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create migration utilities directory structure in src/lib/migrations/
- [x] T002 Create stock information models directory structure in src/models/stock_info.py
- [x] T003 Create stock information services directory structure in src/services/stock_info_service.py
- [x] T004 Create backend API directory structure in backend/src/routers/stock_info.py
- [x] T005 Create frontend components directory structure in frontend/src/components/StockInfoPanel.tsx
- [x] T006 Update pyproject.toml with new dependencies (if needed)
- [x] T007 Update backend requirements.txt with new dependencies (if needed)
- [x] T008 Update frontend package.json with new dependencies (if needed)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Create database migration framework in src/lib/migrations/migration_manager.py
- [x] T010 Create schema_migrations table definition in src/lib/migrations/001_create_schema_migrations.sql
- [x] T011 Create stock_stock_info table definition in src/lib/migrations/002_create_stock_info_table.sql
- [x] T012 Create base StockInfo dataclass in src/models/stock_info.py
- [x] T013 Create base Migration dataclass in src/models/migration.py
- [x] T014 Create database service extensions for migration support in src/services/database_service.py
- [x] T015 Create stock info backend service base in backend/src/services/stock_info_service.py
- [x] T016 Create frontend API client base in frontend/src/services/stockInfoApi.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Database Schema Migration (Priority: P1) 🎯 MVP

**Goal**: Enable system administrators to run database migrations via CLI to update schema safely

**Independent Test**: Run migration commands and verify schema changes without affecting other features

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T017 [P] [US1] Contract test for migrate command in tests/contract/test_migrate_command.py
- [ ] T018 [P] [US1] Integration test for migration execution in tests/integration/test_migration_execution.py

### Implementation for User Story 1

- [ ] T019 [US1] Implement MigrationManager class in src/lib/migrations/migration_manager.py
- [ ] T020 [US1] Implement migrate CLI command in src/cli/migrate.py
- [ ] T021 [US1] Add migration command to main CLI entry point in src/cli/__init__.py
- [ ] T022 [US1] Add migration logging and error handling in src/services/migration_service.py
- [ ] T023 [US1] Create migration status command in src/cli/migrate_status.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Stock Information Data Collection (Priority: P1)

**Goal**: Collect comprehensive stock information from multiple sources and store merged data

**Independent Test**: Fetch data from APIs and verify merged information is stored correctly

### Tests for User Story 2 ⚠️

- [ ] T024 [P] [US2] Contract test for stock-info-fetch command in tests/contract/test_stock_info_fetch.py
- [ ] T025 [P] [US2] Integration test for API data merging in tests/integration/test_stock_info_merging.py

### Implementation for User Story 2

- [ ] T026 [US2] Implement East Money API client in src/services/eastmoney_client.py
- [ ] T027 [US2] Implement Xueqiu API client in src/services/xueqiu_client.py
- [ ] T028 [US2] Implement data merging logic in src/services/stock_info_merger.py
- [ ] T029 [US2] Add stock info storage methods in src/services/stock_info_service.py
- [ ] T030 [US2] Implement fetch-stock-info CLI command in src/cli/fetch_stock_info.py
- [ ] T031 [US2] Add rate limiting and retry logic in src/lib/rate_limiter.py
- [ ] T032 [US2] Add caching support for stock info in src/lib/stock_info_cache.py
- [ ] T033 [US2] Implement batch processing for multiple stocks in src/services/batch_stock_processor.py
- [ ] T034 [US2] Add backend API endpoints in backend/src/routers/stock_info.py
- [ ] T035 [US2] Implement backend stock info service in backend/src/services/stock_info_service.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Stock Information Display (Priority: P2)

**Goal**: Display detailed stock information alongside historical price charts

**Independent Test**: View the updated page layout with stock information panel

### Tests for User Story 3 ⚠️

- [ ] T036 [P] [US3] Contract test for stock info API endpoint in tests/contract/test_stock_info_api.py
- [ ] T037 [P] [US3] Integration test for frontend stock info display in tests/integration/test_stock_info_display.py

### Implementation for User Story 3

- [ ] T038 [US3] Create StockInfoPanel React component in frontend/src/components/StockInfoPanel.tsx
- [ ] T039 [US3] Update historical data page layout in frontend/src/pages/HistoricalDataPage.tsx
- [ ] T040 [US3] Implement frontend API client in frontend/src/services/stockInfoApi.ts
- [ ] T041 [US3] Add CSS Grid layout for 50/50 chart/info split in frontend/src/styles/historical-data.css
- [ ] T042 [US3] Add loading states and error handling in StockInfoPanel component
- [ ] T043 [US3] Implement responsive design for mobile devices in StockInfoPanel
- [ ] T044 [US3] Add data formatting utilities in frontend/src/utils/stockFormatters.ts

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T045 [P] Update documentation in docs/ for new CLI commands
- [ ] T046 [P] Add comprehensive type hints throughout codebase
- [ ] T047 Code cleanup and refactoring across all modules
- [ ] T048 Performance optimization for stock data processing
- [ ] T049 Add debug logging and timing metrics
- [ ] T050 Run quickstart.md validation and update if needed
- [ ] T051 Security review of API endpoints and data handling
- [ ] T052 Add comprehensive error messages and user guidance

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - May use US1/US2 data but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before CLI/API endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
Task: "Contract test for stock-info-fetch command in tests/contract/test_stock_info_fetch.py"
Task: "Integration test for API data merging in tests/integration/test_stock_info_merging.py"

# Launch API clients in parallel:
Task: "Implement East Money API client in src/services/eastmoney_client.py"
Task: "Implement Xueqiu API client in src/services/xueqiu_client.py"
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
   - Developer A: User Story 1 (Database Migration)
   - Developer B: User Story 2 (Stock Data Collection)
   - Developer C: User Story 3 (Stock Info Display)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence