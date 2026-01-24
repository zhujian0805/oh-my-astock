# Tasks: Backend API Data Access Layer

**Input**: Design documents from `/home/jzhu/oh-my-astock/specs/003-backend-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Included per constitution principle II (Test-First Discipline - MANDATORY)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Source structure: `src/api/` for new API layer

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Install FastAPI dependencies: fastapi>=0.109.0, uvicorn[standard]>=0.27.0, pydantic>=2.5.0 in pyproject.toml
- [X] T002 Install testing dependencies: httpx>=0.26.0 in pyproject.toml [dev]
- [X] T003 [P] Create src/api/ directory structure (app.py, routes.py, schemas.py, middleware.py, __init__.py)
- [X] T004 [P] Create tests/contract/test_api.py file (empty, to be filled per story)
- [X] T005 [P] Create tests/integration/test_api_database.py file (empty, to be filled per story)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core API infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create FastAPI application initialization in src/api/app.py (app instance, basic config, no routes yet)
- [X] T007 [P] Configure CORS middleware in src/api/app.py (allow localhost:5173, GET methods)
- [X] T008 [P] Configure request logging middleware in src/api/app.py (timestamp, method, endpoint, status code)
- [X] T009 [P] Setup error handling with HTTPException patterns in src/api/app.py
- [X] T010 Create base Pydantic schemas in src/api/schemas.py (empty file, to be populated per story)
- [X] T011 Create API routes module in src/api/routes.py (APIRouter instance, no endpoints yet)
- [X] T012 Include router in FastAPI app in src/api/app.py (app.include_router with /api prefix)
- [X] T013 Verify FastAPI app starts with uvicorn api.main:app --reload (smoke test)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Fetch Available Stocks for Dropdown Menu (Priority: P1) 🎯 MVP

**Goal**: Provide GET /api/stocks endpoint that returns all available stocks from database for frontend dropdown population

**Independent Test**: Send HTTP GET to /api/stocks and verify JSON array response with code and name fields

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T014 [P] [US1] Contract test for GET /api/stocks endpoint in tests/contract/test_api.py (test_get_stocks_returns_200, test_get_stocks_returns_array, test_get_stocks_schema)
- [X] T015 [P] [US1] Contract test for GET /api/stocks with empty database in tests/contract/test_api.py (test_get_stocks_empty_database_returns_empty_array)
- [X] T016 [P] [US1] Contract test for GET /api/stocks with database error in tests/contract/test_api.py (test_get_stocks_database_error_returns_500)
- [X] T017 [P] [US1] Integration test for stock list database query in tests/integration/test_api_database.py (test_get_stocks_queries_stock_name_code_table)

### Implementation for User Story 1

- [X] T018 [US1] Create StockResponse Pydantic model in src/api/schemas.py (code, name, metadata fields)
- [X] T019 [US1] Create helper function to convert Stock dataclass to StockResponse in src/api/schemas.py
- [X] T020 [US1] Implement GET /api/stocks endpoint in src/api/routes.py (queries DatabaseService, returns List[StockResponse])
- [X] T021 [US1] Add error handling for database connection failures in GET /api/stocks endpoint
- [X] T022 [US1] Add logging for GET /api/stocks requests (info level: request received, stocks count returned)
- [X] T023 [US1] Verify all User Story 1 tests pass (pytest tests/contract/test_api.py::test_get_stocks* tests/integration/test_api_database.py::test_get_stocks*)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Frontend can now fetch stock list for dropdown.

---

## Phase 4: User Story 2 - Fetch Historical Price Data for Chart Visualization (Priority: P1)

**Goal**: Provide GET /api/stocks/{code}/historical endpoint that returns historical price data for a stock to enable frontend chart rendering

**Independent Test**: Send HTTP GET to /api/stocks/000001/historical and verify JSON response with stock_code and data array containing OHLCV fields

### Tests for User Story 2

- [ ] T024 [P] [US2] Contract test for GET /api/stocks/{code}/historical endpoint in tests/contract/test_api.py (test_get_historical_returns_200, test_get_historical_schema)
- [ ] T025 [P] [US2] Contract test for GET /api/stocks/{code}/historical with no data in tests/contract/test_api.py (test_get_historical_no_data_returns_empty_array)
- [ ] T026 [P] [US2] Contract test for GET /api/stocks/{code}/historical with invalid stock code in tests/contract/test_api.py (test_get_historical_invalid_code_returns_404)
- [ ] T027 [P] [US2] Contract test for GET /api/stocks/{code}/historical with malformed code in tests/contract/test_api.py (test_get_historical_malformed_code_returns_400)
- [ ] T028 [P] [US2] Integration test for historical data database query in tests/integration/test_api_database.py (test_get_historical_queries_stock_historical_data_table)

### Implementation for User Story 2

- [ ] T029 [P] [US2] Create HistoricalDataPoint Pydantic model in src/api/schemas.py (date, close_price, open_price, high_price, low_price, volume, turnover, amplitude, price_change_rate, price_change, turnover_rate)
- [ ] T030 [P] [US2] Create HistoricalDataResponse Pydantic model in src/api/schemas.py (stock_code, data: List[HistoricalDataPoint])
- [ ] T031 [US2] Create helper function to convert DataFrame to List[HistoricalDataPoint] in src/api/schemas.py
- [ ] T032 [US2] Implement GET /api/stocks/{code}/historical endpoint in src/api/routes.py (queries HistoricalDataService or DatabaseService, returns HistoricalDataResponse)
- [ ] T033 [US2] Add stock code validation in GET /api/stocks/{code}/historical endpoint (return 400 for invalid format)
- [ ] T034 [US2] Add stock existence check in GET /api/stocks/{code}/historical endpoint (return 404 if stock not found)
- [ ] T035 [US2] Add error handling for database query failures in GET /api/stocks/{code}/historical endpoint (return 500 with descriptive message)
- [ ] T036 [US2] Add logging for GET /api/stocks/{code}/historical requests (info level: request received with stock code, records count returned)
- [ ] T037 [US2] Verify all User Story 2 tests pass (pytest tests/contract/test_api.py::test_get_historical* tests/integration/test_api_database.py::test_get_historical*)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Frontend can now fetch stocks and display historical price charts. MVP COMPLETE!

---

## Phase 5: User Story 3 - API Health Check and Documentation (Priority: P2)

**Goal**: Provide GET /api/health endpoint for monitoring and auto-generated API documentation for developers

**Independent Test**: Send HTTP GET to /api/health and verify 200 response with status and timestamp, access /api/docs and verify interactive documentation displays

### Tests for User Story 3

- [ ] T038 [P] [US3] Contract test for GET /api/health endpoint in tests/contract/test_api.py (test_health_check_returns_200, test_health_check_schema)
- [ ] T039 [P] [US3] Contract test for GET /api/health with database unavailable in tests/contract/test_api.py (test_health_check_database_down_returns_degraded_or_503)
- [ ] T040 [P] [US3] Integration test for health check database connectivity in tests/integration/test_api_database.py (test_health_check_verifies_database_connection)

### Implementation for User Story 3

- [ ] T041 [US3] Create HealthCheckResponse Pydantic model in src/api/schemas.py (status, timestamp, database_connected, error optional)
- [ ] T042 [US3] Implement GET /api/health endpoint in src/api/routes.py (checks DatabaseService.database_exists, returns HealthCheckResponse)
- [ ] T043 [US3] Add database connectivity check logic in GET /api/health endpoint (try connection, set status ok/degraded/error)
- [ ] T044 [US3] Add timestamp generation in GET /api/health endpoint (ISO 8601 UTC format)
- [ ] T045 [US3] Add error handling for health check failures in GET /api/health endpoint (return 503 if critical failure)
- [ ] T046 [US3] Verify FastAPI auto-documentation at /api/docs (Swagger UI) and /api/redoc (ReDoc) displays all endpoints
- [ ] T047 [US3] Verify all User Story 3 tests pass (pytest tests/contract/test_api.py::test_health* tests/integration/test_api_database.py::test_health*)

**Checkpoint**: All core endpoints functional. Health monitoring enabled, API documentation available for frontend developers.

---

## Phase 6: User Story 4 - CORS Configuration for Frontend Integration (Priority: P2)

**Goal**: Enable CORS headers to allow frontend (localhost:5173) to make cross-origin requests to backend API (localhost:8000)

**Independent Test**: Make cross-origin GET request from frontend to backend and verify Access-Control-Allow-Origin header is present

### Tests for User Story 4

- [ ] T048 [P] [US4] Contract test for CORS headers in GET /api/stocks response in tests/contract/test_api.py (test_cors_headers_present_in_response)
- [ ] T049 [P] [US4] Contract test for OPTIONS preflight request in tests/contract/test_api.py (test_cors_preflight_options_request)
- [ ] T050 [P] [US4] Integration test for CORS with allowed origin in tests/integration/test_api_database.py (test_cors_allows_localhost_5173)

### Implementation for User Story 4

- [ ] T051 [US4] Verify CORSMiddleware configuration in src/api/app.py (allow_origins includes http://localhost:5173)
- [ ] T052 [US4] Verify CORSMiddleware allow_methods includes GET in src/api/app.py
- [ ] T053 [US4] Verify CORSMiddleware allow_headers set to * in src/api/app.py
- [ ] T054 [US4] Test CORS headers in actual response using TestClient with origin header
- [ ] T055 [US4] Verify all User Story 4 tests pass (pytest tests/contract/test_api.py::test_cors* tests/integration/test_api_database.py::test_cors*)

**Checkpoint**: All user stories complete. Frontend can now successfully integrate with backend API across different origins.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T056 [P] Add API request/response examples to OpenAPI schema in src/api/schemas.py (Field examples for all models)
- [ ] T057 [P] Add comprehensive docstrings to all endpoints in src/api/routes.py
- [ ] T058 [P] Verify logging coverage for all endpoints (info level for success, error level for failures)
- [ ] T059 Run complete test suite and verify 100% pass rate (pytest tests/contract/test_api.py tests/integration/test_api_database.py -v)
- [ ] T060 [P] Code cleanup and refactoring (remove unused imports, standardize error messages)
- [ ] T061 Validate quickstart.md instructions (install deps, start server, verify endpoints)
- [ ] T062 [P] Performance test: Verify GET /api/stocks returns 1000+ stocks in <2s
- [ ] T063 [P] Performance test: Verify GET /api/stocks/{code}/historical returns 750 records in <2s
- [ ] T064 [P] Run ruff check and ruff format on src/api/ directory
- [ ] T065 Update CLAUDE.md Recent Changes section with feature 003 completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Phase 2 - No dependencies on other stories
  - User Story 2 (P1): Can start after Phase 2 - No dependencies on other stories
  - User Story 3 (P2): Can start after Phase 2 - No dependencies on other stories (documentation/health check)
  - User Story 4 (P2): Can start after Phase 2 - Technically configured in Phase 2 (T007), but tests verify functionality
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Independently testable
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Independently testable (CORS already configured in T007)

**Note**: User Stories 1 and 2 are both P1 priority and together form the MVP. They can be implemented in parallel or sequentially. User Story 1 enables stock selection, User Story 2 enables chart visualization.

### Within Each User Story

- Tests MUST be written and FAIL before implementation (Red phase)
- Pydantic schemas before endpoint implementation
- Endpoint implementation before error handling
- Error handling and logging before test verification
- All tests pass before moving to next user story

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003, T004, T005 can run in parallel

**Phase 2 (Foundational)**:
- T007, T008, T009, T010 can run in parallel after T006 completes

**Phase 3 (User Story 1)**:
- Tests: T014, T015, T016, T017 can run in parallel
- No parallel implementation tasks (sequential dependency on T018 → T019 → T020)

**Phase 4 (User Story 2)**:
- Tests: T024, T025, T026, T027, T028 can run in parallel
- Schemas: T029, T030 can run in parallel
- T031 depends on T029, T030

**Phase 5 (User Story 3)**:
- Tests: T038, T039, T040 can run in parallel

**Phase 6 (User Story 4)**:
- Tests: T048, T049, T050 can run in parallel
- Implementation: T051, T052, T053 can run in parallel (all verify existing config)

**Phase 7 (Polish)**:
- T056, T057, T058, T060, T062, T063, T064 can run in parallel

**Across User Stories** (after Foundational phase complete):
- User Story 1, 2, 3, 4 can ALL be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for GET /api/stocks endpoint in tests/contract/test_api.py"
Task: "Contract test for GET /api/stocks with empty database in tests/contract/test_api.py"
Task: "Contract test for GET /api/stocks with database error in tests/contract/test_api.py"
Task: "Integration test for stock list database query in tests/integration/test_api_database.py"
```

## Parallel Example: After Foundational Phase

```bash
# Different team members can work on different user stories simultaneously:
Developer A: User Story 1 (GET /api/stocks)
Developer B: User Story 2 (GET /api/stocks/{code}/historical)
Developer C: User Story 3 (GET /api/health + docs)
Developer D: User Story 4 (CORS testing)
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T013) - **CRITICAL BLOCKER**
3. Complete Phase 3: User Story 1 (T014-T023)
4. Complete Phase 4: User Story 2 (T024-T037)
5. **STOP and VALIDATE**: Test User Stories 1 and 2 independently
6. Frontend can now:
   - Fetch stock list for dropdown (User Story 1)
   - Display historical price charts (User Story 2)
7. Deploy/demo MVP

**MVP Scope**: 37 tasks (T001-T037) delivers complete P1 functionality

### Incremental Delivery

1. Complete Setup + Foundational (T001-T013) → Foundation ready
2. Add User Story 1 (T014-T023) → Test independently → Stock list API available
3. Add User Story 2 (T024-T037) → Test independently → Historical data API available → **MVP DEPLOYED**
4. Add User Story 3 (T038-T047) → Test independently → Health check + docs available
5. Add User Story 4 (T048-T055) → Test independently → CORS fully tested
6. Add Polish (T056-T065) → Production ready

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With 2 developers (recommended for P1 MVP):

1. Both complete Setup + Foundational together (T001-T013)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T014-T023)
   - **Developer B**: User Story 2 (T024-T037)
3. Both stories complete independently, integrate seamlessly
4. MVP delivered in parallel

With 4 developers (full feature):

1. All complete Setup + Foundational together (T001-T013)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T014-T023)
   - **Developer B**: User Story 2 (T024-T037)
   - **Developer C**: User Story 3 (T038-T047)
   - **Developer D**: User Story 4 (T048-T055)
3. All stories complete and integrate independently
4. Complete feature delivered in parallel

---

## Task Summary

**Total Tasks**: 65

**Tasks per User Story**:
- Setup (Phase 1): 5 tasks
- Foundational (Phase 2): 8 tasks (BLOCKS all stories)
- User Story 1 (P1): 10 tasks (4 tests + 6 implementation)
- User Story 2 (P1): 14 tasks (5 tests + 9 implementation)
- User Story 3 (P2): 10 tasks (3 tests + 7 implementation)
- User Story 4 (P2): 8 tasks (3 tests + 5 implementation)
- Polish (Phase 7): 10 tasks

**MVP Scope**: 37 tasks (Phase 1 + 2 + User Stories 1 & 2)

**Parallel Opportunities Identified**:
- Setup phase: 3 parallel tasks
- Foundational phase: 4 parallel tasks (after app.py created)
- User Story 1 tests: 4 parallel tasks
- User Story 2 tests: 5 parallel tasks
- User Story 3 tests: 3 parallel tasks
- User Story 4 tests: 3 parallel tasks
- Polish phase: 7 parallel tasks
- **Cross-story parallelism**: All 4 user stories can be worked on simultaneously after Foundational phase

**Independent Test Criteria per Story**:
- **US1**: `curl http://localhost:8000/api/stocks` returns JSON array with stock objects
- **US2**: `curl http://localhost:8000/api/stocks/000001/historical` returns JSON with historical data
- **US3**: `curl http://localhost:8000/api/health` returns 200 with status, access http://localhost:8000/api/docs shows Swagger UI
- **US4**: Cross-origin request from localhost:5173 succeeds with CORS headers

**Suggested MVP Scope**: Phase 1 + Phase 2 + User Story 1 + User Story 2 (37 tasks, delivers core P1 functionality)

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability (US1, US2, US3, US4)
- Each user story is independently completable and testable
- Test-first discipline enforced per constitution: Write tests FIRST, ensure they FAIL, then implement
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Format Validation**: All tasks follow `- [ ] [TaskID] [P?] [Story?] Description with file path` format
