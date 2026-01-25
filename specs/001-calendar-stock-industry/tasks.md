# Tasks: Add Calendar for Stock Industry Transactions

**Input**: Design documents from `/specs/001-calendar-stock-industry/`
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

**Purpose**: Verify development environment and dependencies

- [x] T001 Verify backend and frontend development environments are ready
- [x] T002 [P] Confirm akshare dependency is available in backend

---

## Phase 2: Foundational (Backend API Extensions)

**Purpose**: Add month filtering support to backend API

**⚠️ CRITICAL**: Frontend work cannot begin until this phase is complete

- [x] T003 Add month parameter validation to get_szse_sector_summary method in backend/src/services/stock_service.py
- [x] T004 Update /market/szse-sector-summary endpoint to accept month query parameter in backend/src/routers/stocks.py
- [x] T005 Test updated API endpoint with month parameter

**Checkpoint**: Backend API ready for month filtering - frontend development can now begin

---

## Phase 3: User Story 1 - View Industry Transactions by Month (Priority: P1) 🎯 MVP

**Goal**: Add month selection calendar to industry transactions page

**Independent Test**: Navigate to 股票市场总貌 → 股票行业成交, select a month using the calendar, and verify that the table displays data for the selected month.

- [x] T006 Create MonthPicker component in frontend/src/components/MonthPicker.tsx
- [x] T007 Integrate MonthPicker into SzseSectorSummary component in frontend/src/pages/SzseSectorSummary.tsx
- [x] T008 Add month selection state management to SzseSectorSummary component in frontend/src/pages/SzseSectorSummary.tsx
- [x] T009 Update API client calls to include month parameter in frontend/src/services/api.ts
- [x] T010 Add loading states and error handling for month selection in frontend/src/pages/SzseSectorSummary.tsx
- [x] T011 Test month selection and data filtering functionality

---

## Phase 4: User Story 2 - Navigate Between Months (Priority: P2)

**Goal**: Enhance calendar with better navigation and visual feedback

**Independent Test**: Use the calendar to switch between different months and verify data updates correctly for each selection.

- [x] T012 Add month navigation controls (previous/next) to MonthPicker component in frontend/src/components/MonthPicker.tsx
- [x] T013 Implement month highlighting for selected month in MonthPicker component in frontend/src/components/MonthPicker.tsx
- [x] T014 Add month range validation and available months logic in frontend/src/components/MonthPicker.tsx
- [x] T015 Improve calendar UI styling and responsive design in frontend/src/components/MonthPicker.tsx
- [x] T016 Test month navigation and highlighting functionality

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [x] T017 Add month display indicator in SzseSectorSummary header in frontend/src/pages/SzseSectorSummary.tsx
- [x] T018 Implement graceful error handling for months with no data in frontend/src/pages/SzseSectorSummary.tsx
- [x] T019 Add dark mode support to MonthPicker component in frontend/src/components/MonthPicker.tsx
- [x] T020 Optimize calendar performance and loading times
- [x] T021 Update quickstart.md with calendar usage examples
- [x] T022 Run final integration testing across all months and edge cases

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-4)**: All depend on Foundational phase completion
  - US1 (P1) can be developed independently
  - US2 (P2) depends on US1 completion for calendar foundation
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: No dependencies - core calendar functionality
- **US2 (P2)**: Depends on US1 - builds upon basic calendar

### Within Each User Story

- Component creation before integration
- API integration before state management
- Basic functionality before enhanced features

### Parallel Opportunities

- All setup tasks marked [P] can run in parallel
- Frontend component creation can happen in parallel with backend API work
- Month picker styling can be developed in parallel with navigation logic

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1: Setup
2. Complete Phase 2: Backend API (critical foundation)
3. Implement US1: Basic calendar with month selection and data filtering
4. **STOP and VALIDATE**: Ensure core functionality works before enhancements

### Incremental Delivery

1. Complete Setup + Backend API → API foundation ready
2. Add US1 → Basic month filtering works
3. Add US2 → Enhanced navigation and UX
4. Polish → Final optimizations and error handling

### Team Strategy

With multiple developers:

1. One developer: Complete backend API (Phase 2)
2. Developer A: Create MonthPicker component and basic integration (US1)
3. Developer B: Add navigation and styling enhancements (US2)
4. Final integration: All components work together seamlessly

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently testable
- Backend API must be complete before frontend work begins
- Calendar component should follow existing UI patterns
- Focus on month-level granularity as supported by akshare API</content>
<parameter name="file_path">specs/001-calendar-stock-industry/tasks.md