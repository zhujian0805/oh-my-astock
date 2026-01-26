# Tasks: Add Individual Stock Information Menu Item

**Input**: Design documents from `/specs/001-stock-individual-info/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Following test-first discipline per constitution, tests are included and should be written before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/` per plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Ensure development environment and basic project structure are ready

- [ ] T001 Verify backend dependencies (FastAPI, Pydantic, akshare >= 1.10.0) in backend/requirements.txt
- [ ] T002 Verify frontend dependencies (React, TypeScript, Tailwind CSS) in frontend/package.json
- [ ] T003 [P] Ensure backend test framework (pytest >= 7.0.0) is configured in backend/
- [ ] T004 [P] Ensure frontend test framework is configured in frontend/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Verify existing backend FastAPI application structure in backend/src/
- [ ] T006 Verify existing frontend React/TypeScript application structure in frontend/src/
- [ ] T007 Confirm DuckDB database connection and basic functionality (no new schema needed)
- [ ] T008 Verify akshare API access and basic functionality for stock_individual_info_em and stock_individual_basic_info_xq

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - View Individual Stock Information (Priority: P1) 🎯 MVP

**Goal**: Users can access detailed information about a specific stock by selecting from a dropdown menu, with data merged from East Money and Xueqiu APIs

**Independent Test**: Navigate to 个股信息 menu item, select a stock from dropdown, verify merged information displays correctly from both APIs

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T009 [P] [US1] Contract test for stock info API endpoint in backend/tests/test_stock_info_api.py
- [ ] T010 [P] [US1] Integration test for stock data merging in backend/tests/test_stock_data_merging.py
- [ ] T011 [P] [US1] Frontend component test for StockInfoDisplay in frontend/src/components/StockInfoDisplay.test.tsx

### Implementation for User Story 1

- [ ] T012 [P] [US1] Create StockInfo model with merged API fields in backend/src/models/stock_info.py
- [ ] T013 [P] [US1] Implement stock_info_service.py for API calls and data merging in backend/src/services/stock_info_service.py
- [ ] T014 [US1] Create stock_info_router.py with GET /api/v1/stock-info/{stock_code} endpoint in backend/src/routers/stock_info_router.py
- [ ] T015 [P] [US1] Update menu.ts to add 个股信息 item under 股市数据 section in frontend/src/config/menu.ts
- [ ] T016 [P] [US1] Create IndividualStockInfo.tsx page component with stock dropdown in frontend/src/pages/IndividualStockInfo.tsx
- [ ] T017 [P] [US1] Create StockInfoDisplay.tsx component with flexible grid layout in frontend/src/components/StockInfoDisplay.tsx
- [ ] T018 [US1] Implement stock API service client in frontend for calling backend endpoint
- [ ] T019 [US1] Integrate dropdown selection with API calls and display updates in IndividualStockInfo.tsx
- [ ] T020 [US1] Add error handling for partial API failures with clear error indicators
- [ ] T021 [US1] Add loading states and performance optimizations for 3-second requirement

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: Edge Cases & Error Handling (Priority: P2)

**Goal**: Handle API failures, invalid stock codes, and backend unavailability gracefully

**Independent Test**: Test error scenarios including Xueqiu API failure, invalid codes, and backend offline

### Tests for Edge Cases ⚠️

- [ ] T022 [P] [US1] Contract test for error responses (404, 500) in backend/tests/test_stock_info_api.py
- [ ] T023 [P] [US1] Integration test for partial data scenarios in backend/tests/test_stock_data_merging.py

### Implementation for Edge Cases

- [ ] T024 [US1] Implement validation for 6-digit stock codes in stock_info_router.py
- [ ] T025 [US1] Add error handling for Xueqiu API failures (show partial East Money data)
- [ ] T026 [US1] Add error handling for East Money API failures (show partial Xueqiu data)
- [ ] T027 [US1] Add error handling for both APIs failing (show error message)
- [ ] T028 [US1] Update StockInfoDisplay.tsx to show error indicators for failed data sources
- [ ] T029 [US1] Add frontend error boundaries and fallback displays

**Checkpoint**: All error scenarios should be handled gracefully with appropriate user feedback

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect the entire feature

- [ ] T030 [P] Add comprehensive type hints to all backend code
- [ ] T031 [P] Add JSDoc comments to frontend components
- [ ] T032 Update quickstart.md with actual implementation details
- [ ] T033 [P] Run backend tests with coverage report
- [ ] T034 [P] Run frontend tests and validate component rendering
- [ ] T035 Performance testing to ensure 3-second requirement is met
- [ ] T036 Code review against constitution principles (modular architecture, test-first)
- [ ] T037 Update CLAUDE.md with any new patterns or technologies used

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-4)**: All depend on Foundational phase completion
  - User stories proceed in priority order (P1 → P2)
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **Edge Cases (P2)**: Depends on User Story 1 completion - builds on core functionality

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Tests for a user story marked [P] can run in parallel
- Models/components marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for stock info API endpoint in backend/tests/test_stock_info_api.py"
Task: "Integration test for stock data merging in backend/tests/test_stock_data_merging.py"
Task: "Frontend component test for StockInfoDisplay in frontend/src/components/StockInfoDisplay.test.tsx"

# Launch all models/components for User Story 1 together:
Task: "Create StockInfo model with merged API fields in backend/src/models/stock_info.py"
Task: "Create IndividualStockInfo.tsx page component with stock dropdown in frontend/src/pages/IndividualStockInfo.tsx"
Task: "Create StockInfoDisplay.tsx component with flexible grid layout in frontend/src/components/StockInfoDisplay.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently with merged API data
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add Edge Cases → Test error scenarios → Deploy/Demo
4. Add Polish → Final improvements

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: Backend API (service + router)
   - Developer B: Frontend components (page + display)
   - Developer C: Tests and integration
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
