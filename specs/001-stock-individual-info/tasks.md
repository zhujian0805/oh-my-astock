# Tasks: Add Individual Stock Information Menu Item

**Input**: Design documents from `/specs/001-stock-individual-info/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks included per constitution test-first discipline requirement.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan
- [X] T002 Initialize Python/FastAPI backend with akshare dependencies
- [X] T003 Initialize React/TypeScript frontend with Tailwind CSS

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Update frontend navigation to add 个股信息 menu item under 股市数据 section in frontend/src/components/Navigation.tsx
- [X] T005 Configure rate limiting for akshare API calls in backend/src/lib/rate_limiter.py
- [X] T006 Setup caching infrastructure for API responses in backend/src/lib/cache.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Individual Stock Information (Priority: P1) 🎯 MVP

**Goal**: Allow users to select a stock from dropdown and view merged information from East Money and Xueqiu APIs

**Independent Test**: Navigate to 个股信息 page, select stock from dropdown, verify merged data displays correctly from both APIs

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [P] [US1] Contract test for stock info API endpoint in backend/tests/contract/test_stock_info_api.py
- [X] T008 [P] [US1] Integration test for stock data merging in backend/tests/integration/test_stock_data_merging.py

### Implementation for User Story 1

- [X] T009 [US1] Create StockInfoService for API integration in backend/src/services/stock_info_service.py
- [X] T010 [US1] Implement stock info router with merged data endpoint in backend/src/routers/stock_info_router.py
- [X] T011 [P] [US1] Create StockInfoApi service for frontend API calls in frontend/src/services/stockInfoApi.ts
- [X] T012 [P] [US1] Create StockInfoDropdown component in frontend/src/components/StockInfoDropdown.tsx
- [X] T013 [P] [US1] Create StockInfoDisplay component in frontend/src/components/StockInfoDisplay.tsx
- [X] T014 [US1] Create IndividualStockPage component integrating dropdown and display in frontend/src/pages/IndividualStockPage.tsx
- [X] T015 [US1] Add error handling for API failures in backend/src/services/stock_info_service.py
- [X] T016 [US1] Add structured logging for API operations in backend/src/services/stock_info_service.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T017 [P] Documentation updates in specs/001-stock-individual-info/
- [ ] T018 Code cleanup and refactoring across backend and frontend
- [ ] T019 Performance optimization for API response times
- [ ] T020 Security review of API endpoints and data handling
- [ ] T021 Run quickstart.md validation and update if needed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Service before router
- Backend before frontend
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Frontend components within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for stock info API endpoint in backend/tests/contract/test_stock_info_api.py"
Task: "Integration test for stock data merging in backend/tests/integration/test_stock_data_merging.py"

# Launch all frontend components for User Story 1 together:
Task: "Create StockInfoApi service for frontend API calls in frontend/src/services/stockInfoApi.ts"
Task: "Create StockInfoDropdown component in frontend/src/components/StockInfoDropdown.tsx"
Task: "Create StockInfoDisplay component in frontend/src/components/StockInfoDisplay.tsx"
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
3. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 backend
   - Developer B: User Story 1 frontend
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence</content>
<parameter name="file_path">specs/001-stock-individual-info/tasks.md