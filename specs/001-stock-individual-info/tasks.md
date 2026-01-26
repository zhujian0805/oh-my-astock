# Tasks: Add Individual Stock Information Menu Item

**Input**: Design documents from `/specs/001-stock-individual-info/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Contract tests for API interfaces and end-to-end tests for user flows are explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/` per plan.md structure
- **CLI**: `src/` at repository root
- Paths follow the structure documented in plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan
- [X] T002 Initialize backend Python project with FastAPI/Pydantic dependencies in backend/requirements.txt
- [X] T003 Initialize frontend React/TypeScript project with Vite/Tailwind dependencies
- [X] T004 [P] Configure ruff linting and formatting for backend code
- [X] T005 [P] Configure TypeScript linting and formatting for frontend code

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Setup DuckDB database schema with stock_list, stocks, and market_quotes tables per data-model.md
- [X] T007 [P] Create base Pydantic models for StockList, Stock, and MarketQuote entities in backend/src/models/
- [X] T008 [P] Create base TypeScript interfaces for stock data in frontend/src/types/
- [X] T009 Implement API client with rate limiting and retry logic in backend/src/lib/api_client.py
- [X] T010 [P] Setup FastAPI application structure with routers and middleware in backend/src/
- [X] T011 [P] Setup React application structure with routing and API client in frontend/src/
- [X] T012 Populate initial stock list with 20-30 popular stocks in database

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Individual Stock Information (Priority: P1) 🎯 MVP

**Goal**: Enable users to select a stock from dropdown and view comprehensive merged information from East Money and Xueqiu APIs

**Independent Test**: Can be fully tested by navigating to the 个股信息 menu item, selecting a stock from the dropdown, and verifying that merged information from both data sources displays correctly.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T013 [P] [US1] Contract test for GET /stocks endpoint in backend/tests/contract/test_stock_api.py
- [X] T014 [P] [US1] Contract test for GET /stocks/{code} endpoint in backend/tests/contract/test_stock_api.py
- [X] T015 [P] [US1] End-to-end test for individual stock selection workflow in frontend/tests/e2e/stock-workflow.spec.ts

### Implementation for User Story 1

- [X] T016 [US1] Implement StockService for API integration and data merging in backend/src/services/stock_service.py
- [X] T017 [US1] Implement GET /stocks endpoint returning stock list for dropdown in backend/src/routers/stock_info.py
- [X] T018 [US1] Implement GET /stocks/{code} endpoint returning merged stock data in backend/src/routers/stock_info.py
- [X] T019 [US1] Create StockInfo React page with dropdown selection in frontend/src/pages/StockInfo.tsx
- [X] T020 [US1] Create StockDisplay component for flexible grid layout in frontend/src/components/StockInfoDisplay.tsx
- [X] T021 [US1] Implement frontend API client for stock endpoints in frontend/src/services/stockInfoApi.ts
- [X] T022 [US1] Add error handling for partial data scenarios in both backend and frontend

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - View Market Quotes/Bid-Ask Data (Priority: P2)

**Goal**: Enable users to view current market quotes and bid-ask prices for curated popular stocks in a table format

**Independent Test**: Can be fully tested by navigating to the 行情报价 menu item and verifying that current bid-ask data for stocks is displayed correctly.

### Tests for User Story 2 ⚠️

- [ ] T023 [P] [US2] Contract test for GET /market-quotes endpoint in backend/tests/contract/test_stock_api.py
- [ ] T024 [P] [US2] End-to-end test for market quotes display workflow in frontend/tests/e2e/stock-workflow.spec.ts

### Implementation for User Story 2

- [ ] T025 [US2] Extend StockService with market quotes functionality in backend/src/services/stock_service.py
- [ ] T026 [US2] Implement GET /market-quotes endpoint in backend/src/routers/stock_info.py
- [ ] T027 [US2] Create MarketQuotes React page in frontend/src/pages/MarketQuotes.tsx
- [ ] T028 [US2] Create MarketQuotesTable component for bid-ask data display in frontend/src/components/MarketQuotesTable.tsx
- [ ] T029 [US2] Extend frontend API client with market quotes endpoint in frontend/src/services/stockApi.ts
- [ ] T030 [US2] Add menu navigation between 个股信息 and 行情报价 pages

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T031 [P] Update CLI commands for stock data operations in src/cli/commands/stock_info.py
- [ ] T032 [P] Update frontend menu to include 个股信息 and 行情报价 under 股市数据
- [ ] T033 Code cleanup and refactoring across backend and frontend
- [ ] T034 Performance optimization for 3s/2s response time targets
- [ ] T035 Comprehensive error handling and user messaging for API failures
- [ ] T036 Run quickstart.md validation and update documentation
- [ ] T037 Execute manage.sh to restart applications and verify functionality

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
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

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for GET /stocks endpoint in backend/tests/contract/test_stock_api.py"
Task: "Contract test for GET /stocks/{code} endpoint in backend/tests/contract/test_stock_api.py"
Task: "End-to-end test for individual stock selection workflow in frontend/tests/e2e/stock-workflow.spec.ts"

# Launch implementation tasks for User Story 1:
Task: "Implement StockService for API integration and data merging in backend/src/services/stock_service.py"
Task: "Create StockInfo React page with dropdown selection in frontend/src/pages/StockInfo.tsx"
Task: "Create StockDisplay component for flexible grid layout in frontend/src/components/StockDisplay.tsx"
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
4. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
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
