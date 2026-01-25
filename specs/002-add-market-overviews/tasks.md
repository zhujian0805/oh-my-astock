# Tasks: Add Stock Market Overview Items to Frontend/Backend

**Input**: Design documents from `/specs/002-add-market-overviews/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are optional - only include if explicitly requested. This feature focuses on extending existing functionality.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/` - FastAPI application
- **Frontend**: `frontend/src/` - React/TypeScript application
- **Full-stack**: Both backend and frontend changes

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Verify backend and frontend development environments are ready
- [x] T002 [P] Confirm akshare dependency is available in backend
- [x] T003 Test existing API endpoints and frontend components

---

## Phase 2: Foundational (Backend API Extensions)

**Purpose**: Add new backend API endpoints that all frontend components depend on

**⚠️ CRITICAL**: Frontend work cannot begin until this phase is complete

- [x] T004 Add get_szse_summary method to StockService in backend/src/services/stock_service.py
- [x] T005 Add get_szse_area_summary method to StockService in backend/src/services/stock_service.py
- [x] T006 Add get_szse_sector_summary method to StockService in backend/src/services/stock_service.py
- [x] T007 Add get_sse_daily_deals method to StockService in backend/src/services/stock_service.py
- [x] T008 Add get_security_categories method to StockService in backend/src/services/stock_service.py
- [x] T009 Add /market/szse-summary endpoint to backend/src/routers/stocks.py
- [x] T010 Add /market/szse-area-summary endpoint to backend/src/routers/stocks.py
- [x] T011 Add /market/szse-sector-summary endpoint to backend/src/routers/stocks.py
- [x] T012 Add /market/sse-daily-deals endpoint to backend/src/routers/stocks.py
- [x] T013 Add /market/security-categories endpoint to backend/src/routers/stocks.py

**Checkpoint**: All 5 new backend endpoints ready - frontend development can now begin

---

## Phase 3: User Story 1 - View Shanghai Stock Exchange Overview (Priority: P1) 🎯 MVP

**Goal**: Existing functionality - ensure baseline Shanghai overview works

**Independent Test**: Navigate to 股票市场总貌 → 上海证券交易所 and verify data displays

- [x] T014 Test existing sse-summary endpoint and frontend component
- [x] T015 Verify StockMarketOverview component renders correctly

**Checkpoint**: Shanghai overview baseline confirmed

---

## Phase 4: User Story 2 - View Shenzhen Stock Exchange Overview (Priority: P1)

**Goal**: Add Shenzhen exchange security statistics to frontend

**Independent Test**: Navigate to 股票市场总貌 → 深圳证券交易所 and verify data displays

- [x] T016 Create SzseSummary.tsx component in frontend/src/pages/
- [x] T017 Update StockMarketOverviewPage.tsx to include Shenzhen menu item
- [x] T018 Test SzseSummary component fetches and displays data correctly

---

## Phase 5: User Story 3 - View Regional Trading Rankings (Priority: P2)

**Goal**: Add regional trading rankings display

**Independent Test**: Navigate to 股票市场总貌 → 地区交易排序 and verify rankings display

- [x] T019 Create SzseAreaSummary.tsx component in frontend/src/pages/
- [x] T020 Update StockMarketOverviewPage.tsx to include regional rankings menu item
- [x] T021 Test SzseAreaSummary component with regional data

---

## Phase 6: User Story 4 - View Stock Industry Transaction Data (Priority: P2)

**Goal**: Add industry sector transaction data display

**Independent Test**: Navigate to 股票市场总貌 → 股票行业成交 and verify sector data displays

- [x] T022 Create SzseSectorSummary.tsx component in frontend/src/pages/
- [x] T023 Update StockMarketOverviewPage.tsx to include industry sector menu item
- [x] T024 Test SzseSectorSummary component with industry data

---

## Phase 7: User Story 5 - View Shanghai Daily Stock Overview (Priority: P2)

**Goal**: Add Shanghai daily transaction details

**Independent Test**: Navigate to 股票市场总貌 → 上海证券交易所-每日概况 and verify daily data displays

- [x] T025 Create SseDailyDeals.tsx component in frontend/src/pages/
- [x] T026 Update StockMarketOverviewPage.tsx to include daily deals menu item
- [x] T027 Test SseDailyDeals component with daily transaction data

---

## Phase 8: User Story 6 - View Security Category Statistics (Priority: P2)

**Goal**: Add comprehensive security category statistics

**Independent Test**: Navigate to 股票市场总貌 → 证券类别统计 and verify detailed categories display

- [x] T028 Create SecurityCategories.tsx component in frontend/src/pages/
- [x] T029 Update StockMarketOverviewPage.tsx to include security categories menu item
- [x] T030 Test SecurityCategories component with detailed category data

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [x] T031 Test all 6 menu items navigation and data loading
- [x] T032 Verify dark mode support across all new components
- [x] T033 Test responsive table layouts on different screen sizes
- [x] T034 Validate Chinese text rendering in all components
- [x] T035 Update API documentation to include new endpoints
- [x] T036 Run quickstart.md validation with actual application

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all frontend stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can proceed in parallel after backend APIs are ready
  - US1 (existing) can be tested immediately
  - US2-6 can be developed in any order after foundational work
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Existing functionality, no new dependencies
- **US2-6 (P2)**: All depend on Phase 2 backend APIs, independent of each other

### Within Each User Story

- Backend API must be ready before frontend component
- Component creation before menu integration
- Menu integration before testing

### Parallel Opportunities

- All setup tasks marked [P] can run in parallel
- All backend API additions can be developed in parallel
- All frontend components (US2-6) can be developed in parallel once APIs are ready
- Testing of different user stories can happen in parallel

---

## Parallel Example: User Stories 2-6

```bash
# Multiple developers can work on different frontend components simultaneously:
Developer A: Create SzseSummary.tsx and update menu
Developer B: Create SzseAreaSummary.tsx and update menu
Developer C: Create SzseSectorSummary.tsx and SseDailyDeals.tsx
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1: Setup
2. Complete Phase 2: Backend APIs (critical for all stories)
3. Test US1: Confirm existing Shanghai overview works
4. **STOP and VALIDATE**: Ensure baseline functionality intact

### Incremental Delivery

1. Complete Setup + Backend APIs → API foundation ready
2. Add one user story at a time → Test independently → Deploy/Demo
3. Each new menu item adds value without breaking existing ones

### Parallel Team Strategy

With multiple developers:

1. One developer: Complete backend APIs (Phase 2)
2. Multiple developers: Work on different frontend components simultaneously
3. Each developer: Component creation → Menu integration → Testing
4. Final integration: All components work together in unified navigation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently testable
- Backend APIs must be complete before frontend work begins
- All components should follow existing patterns (StockMarketOverview.tsx)
- Test navigation between all 6 menu items before completion</content>
<parameter name="file_path">specs/002-add-market-overviews/tasks.md