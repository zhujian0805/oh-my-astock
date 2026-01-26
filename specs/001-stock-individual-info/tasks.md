# Tasks: Add Individual Stock Information and Market Quotes

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

- [X] T001 Verify backend dependencies (FastAPI, Pydantic, akshare >= 1.10.0) in backend/requirements.txt
- [X] T002 Verify frontend dependencies (React, TypeScript, Tailwind CSS) in frontend/package.json
- [X] T003 [P] Ensure backend test framework (pytest >= 7.0.0) is configured in backend/
- [X] T004 [P] Ensure frontend test framework (Vitest) is configured in frontend/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Verify existing backend FastAPI application structure in backend/src/
- [X] T006 Verify existing frontend React/TypeScript application structure in frontend/src/
- [X] T007 Confirm DuckDB database connection and basic functionality (no new schema needed)
- [X] T008 Verify akshare API access and basic functionality for stock_individual_info_em and stock_individual_basic_info_xq
- [X] T009 Verify akshare API access for stock_bid_ask_em (market quotes)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - View Individual Stock Information (Priority: P1) 🎯 MVP

**Goal**: Users can access detailed information about a specific stock by selecting from a dropdown menu, with data merged from East Money and Xueqiu APIs

**Independent Test**: Navigate to 个股信息 menu item, select a stock from dropdown, verify merged information displays correctly from both APIs

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Contract test for stock info API endpoint in backend/tests/contract/test_stock_info_api.py
- [ ] T011 [P] [US1] Integration test for stock data merging in backend/tests/integration/test_stock_data_merging.py
- [ ] T012 [P] [US1] Frontend component test for StockInfoDisplay in frontend/tests/StockInfoDisplay.test.tsx

### Implementation for User Story 1

- [ ] T013 [P] [US1] Create StockInfo model with merged API fields in backend/src/models/stock_info.py
- [ ] T014 [P] [US1] Implement stock_info_service.py for API calls and data merging in backend/src/services/stock_info_service.py
- [X] T015 [US1] Create stock_info_router.py with GET /api/v1/stocks/{stock_code}/info endpoint in backend/src/routers/stock_info_router.py
- [ ] T016 [P] [US1] Update menu.ts to add 个股信息 item under 股市数据 section in frontend/src/config/menu.ts
- [ ] T017 [P] [US1] Create IndividualStockInfo.tsx page component with stock dropdown in frontend/src/pages/IndividualStockInfo.tsx
- [ ] T018 [P] [US1] Create StockInfoDisplay.tsx component with flexible grid layout in frontend/src/components/StockInfoDisplay.tsx
- [X] T019 [US1] Implement stock API service client in frontend/src/services/stockInfoApi.ts
- [X] T020 [US1] Integrate dropdown selection with API calls and display updates in IndividualStockInfo.tsx
- [X] T021 [US1] Add error handling for partial API failures with clear error indicators
- [X] T022 [US1] Add loading states and performance optimizations for 3-second requirement

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - View Market Quotes/Bid-Ask Data (Priority: P2)

**Goal**: Users can view current market quotes and bid-ask prices for stocks to understand market liquidity and price levels

**Independent Test**: Navigate to 行情报价 menu item and verify that current bid-ask data displays correctly for stocks

### Tests for User Story 2 ⚠️

- [X] T023 [P] [US2] Contract test for market quotes API endpoint in backend/tests/contract/test_market_quotes_api.py
- [ ] T024 [P] [US2] Integration test for market quotes data retrieval in backend/tests/integration/test_market_quotes.py
- [ ] T025 [P] [US2] Frontend component test for MarketQuotesTable in frontend/tests/MarketQuotesTable.test.tsx

### Implementation for User Story 2

- [X] T026 [P] [US2] Create MarketQuote model with bid-ask fields in backend/src/models/market_quote.py
- [X] T027 [P] [US2] Implement market_quotes_service.py for API calls in backend/src/services/market_quotes_service.py
- [X] T028 [US2] Create market_quotes_router.py with GET /api/v1/market-quotes endpoint in backend/src/routers/market_quotes_router.py
- [X] T029 [P] [US2] Update menu.ts to add 行情报价 item under 股市数据 section in frontend/src/config/menu.ts
- [X] T030 [P] [US2] Create MarketQuotesPage.tsx page component in frontend/src/pages/MarketQuotesPage.tsx
- [X] T031 [P] [US2] Create MarketQuotesTable.tsx component with table layout in frontend/src/components/MarketQuotesTable.tsx
- [X] T032 [US2] Implement market quotes API service client in frontend/src/services/marketQuotesApi.ts
- [X] T033 [US2] Integrate API data loading and table display in MarketQuotesPage.tsx
- [X] T034 [US2] Add error handling for market quotes API failures
- [X] T035 [US2] Add loading states and performance optimizations for 2-second requirement

**Checkpoint**: At this point, User Story 2 should be fully functional and testable independently

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect both user stories

- [ ] T036 [P] Add comprehensive type hints to all new backend code
- [ ] T037 [P] Add JSDoc comments to all new frontend components
- [ ] T038 Update quickstart.md with actual implementation details for both features
- [ ] T039 [P] Run backend tests with coverage report for both features
- [ ] T040 [P] Run frontend tests and validate component rendering
- [ ] T041 Performance testing to ensure 2-3 second requirements are met
- [ ] T042 Code review against constitution principles for both features
- [ ] T043 Update CLAUDE.md with any new patterns or technologies used
- [ ] T044 End-to-end testing of both menu items and navigation flow
- [ ] T045 Documentation updates for API endpoints and usage

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-4)**: All depend on Foundational phase completion
  - User Story 1 (P1) can start immediately after Foundational
  - User Story 2 (P2) can start immediately after Foundational (independent of US1)
- **Polish (Phase 5)**: Depends on both user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - can start after Foundational (Phase 2)
- **User Story 2 (P2)**: Independent - can start after Foundational (Phase 2)

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before error handling
- Story complete before moving to polish phase

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational is done:
  - User Story 1 and User Story 2 can be developed in parallel by different team members
  - Tests for each story marked [P] can run in parallel
  - Models/components marked [P] can run in parallel within each story
- Cross-cutting concerns marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for stock info API endpoint in backend/tests/contract/test_stock_info_api.py"
Task: "Integration test for stock data merging in backend/tests/integration/test_stock_data_merging.py"
Task: "Frontend component test for StockInfoDisplay in frontend/tests/StockInfoDisplay.test.tsx"

# Launch all models/components for User Story 1 together:
Task: "Create StockInfo model with merged API fields in backend/src/models/stock_info.py"
Task: "Create IndividualStockInfo.tsx page component with stock dropdown in frontend/src/pages/IndividualStockInfo.tsx"
Task: "Create StockInfoDisplay.tsx component with flexible grid layout in frontend/src/components/StockInfoDisplay.tsx"
```

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
Task: "Contract test for market quotes API endpoint in backend/tests/contract/test_market_quotes_api.py"
Task: "Integration test for market quotes data retrieval in backend/tests/integration/test_market_quotes.py"
Task: "Frontend component test for MarketQuotesTable in frontend/tests/MarketQuotesTable.test.tsx"

# Launch all models/components for User Story 2 together:
Task: "Create MarketQuote model with bid-ask fields in backend/src/models/market_quote.py"
Task: "Create MarketQuotesPage.tsx page component in frontend/src/pages/MarketQuotesPage.tsx"
Task: "Create MarketQuotesTable.tsx component with table layout in frontend/src/components/MarketQuotesTable.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Individual Stock Information)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Full Feature Delivery

1. Complete Setup + Foundational → Foundation ready
2. **PARALLEL DEVELOPMENT**: Start both User Stories simultaneously
   - Team A: User Story 1 (Individual Stock Info)
   - Team B: User Story 2 (Market Quotes)
3. Both stories complete and independently testable
4. Add Polish → Final improvements and cross-cutting concerns
5. End-to-end testing and documentation

### Team Parallelization

With multiple developers:

1. All team members complete Setup + Foundational together
2. Once Foundational is done:
   - Developer A: StockInfoService + StockInfoRouter (backend US1)
   - Developer B: MarketQuotesService + MarketQuotesRouter (backend US2)
   - Developer C: StockInfoDisplay + IndividualStockInfo (frontend US1)
   - Developer D: MarketQuotesTable + MarketQuotesPage (frontend US2)
   - Developer E: Tests for both features
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
