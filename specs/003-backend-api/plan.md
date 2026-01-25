# Implementation Plan: Backend API Data Access Layer

**Branch**: `003-backend-api` | **Date**: 2026-01-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/home/jzhu/oh-my-astock/specs/003-backend-api/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature adds a RESTful HTTP API backend that serves as a data access layer between the frontend React application and the existing DuckDB database. The API provides two core endpoints: GET /api/stocks (returns all available stocks for dropdown population) and GET /api/stocks/{code}/historical (returns historical price data for chart visualization). Additional endpoints include health checks and API documentation. The backend enables CORS for cross-origin requests and maintains backward compatibility with the existing database schema from feature 001-duckdb-stock-setup.

## Technical Context

**Language/Version**: Python 3.10+ (matching existing codebase requirements)
**Primary Dependencies**: FastAPI 0.109+, Uvicorn 0.27+, Pydantic 2.5+ (see research.md for rationale)
**Storage**: DuckDB >= 0.8.0 (existing database, read-only access for this feature)
**Testing**: pytest >= 7.0.0 (contract tests for API endpoints, integration tests for database queries), httpx 0.26+ (FastAPI TestClient)
**Target Platform**: Linux server (development), cross-platform deployment
**Project Type**: Web application (backend API + existing frontend)
**Performance Goals**: 100+ concurrent requests, <2s response time for stock list (1000+ records), <2s response time for historical data (250-750 records per stock), <200ms p95 latency
**Constraints**: <200ms p95 latency for API endpoints, database read-only (no schema changes), backward compatibility with existing database schema
**Scale/Scope**: 1,000+ stocks, 100+ concurrent users, 3 core API endpoints (stocks list, historical data, health check)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Modular Architecture First ✅ PASS

**Assessment**: The backend API fits cleanly into the existing layered architecture:
- **API layer** (new): Handles HTTP requests/responses, request validation, CORS
- **Services layer** (existing): Reuses DatabaseService for database queries
- **Models layer** (existing): Reuses Stock and database models for data representation
- **Utilities layer** (existing): Reuses Config and logging utilities

**Compliance**:
- No circular dependencies introduced
- Data flow follows downward pattern: API → Services → Models → Lib
- API layer is a new top-level interface that composes existing services
- Clear separation of concerns: API layer handles HTTP, Services handle business logic

### II. Test-First Discipline (MANDATORY) ✅ PASS

**Assessment**: Feature design follows test-first principles:
- Contract tests will validate API endpoints before implementation (Red phase)
- Integration tests will validate database queries and response serialization
- Test organization will follow `tests/contract/test_api.py` and `tests/integration/test_api_database.py`

**Compliance**:
- Plan includes contract test generation in Phase 1
- Tests will be written before API implementation
- API endpoints have clear acceptance criteria from spec (testable contracts)
- Test structure mirrors source structure

### III. Database-Centric Design ✅ PASS

**Assessment**: Backend API is read-only and respects existing database schema:
- No schema changes required (uses existing `stock_name_code` and `stock_historical_data` tables)
- Reuses existing DatabaseService and DatabaseConnection
- All queries target well-indexed tables with existing primary keys
- No batch operations needed (read-only queries)

**Compliance**:
- Maintains backward compatibility with feature 001 database schema
- No migration planning required (read-only access)
- Leverages existing indexes for query performance

### IV. Performance & Scalability Built-In ✅ PASS

**Assessment**: Feature requirements include explicit performance targets:
- 100+ concurrent requests without >20% degradation
- <2s response time for stock list and historical data
- Uses existing thread-safe DatabaseConnection (thread-local connections)
- API framework will provide built-in concurrency handling

**Compliance**:
- Performance goals defined in spec (SC-001, SC-002, SC-003)
- Reuses thread-safe database connection patterns from existing codebase
- No rate limiting needed (internal API, not external)
- Caching is out of scope but foundation supports future addition

### V. Observable & Debuggable Systems ✅ PASS

**Assessment**: Feature includes observability requirements:
- Request logging with timestamp, endpoint, method, status code (FR-009)
- Health check endpoint for monitoring (FR-008)
- API documentation for debugging (User Story 3)
- Error responses include descriptive messages (SC-007)

**Compliance**:
- Reuses existing centralized logging from lib/logging.py
- Structured error responses with context
- Health check enables production monitoring
- API documentation reduces debugging time

### Summary: All Gates PASS ✅

No violations detected. Feature aligns with all constitution principles:
- Fits modular architecture without cross-cutting concerns
- Follows test-first discipline with contract/integration tests
- Respects database-centric design (read-only, no schema changes)
- Includes performance requirements and reuses scalable patterns
- Provides observability through logging, health checks, and documentation

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Existing structure (from features 001-002)
src/
├── models/          # Data models (Stock, DatabaseConnection - REUSE)
├── services/        # Business logic (DatabaseService - REUSE)
├── cli/             # CLI commands (existing, not modified)
├── lib/             # Utilities (config, logging - REUSE)
└── routers/         # FastAPI route handlers (existing, not modified)

# NEW: Separate backend service (implemented architecture)
backend/
├── src/             # FastAPI application (ACTUAL IMPLEMENTATION)
│   ├── main.py      # FastAPI app with CORS, logging, error handling
│   ├── config.py    # Backend-specific configuration
│   ├── database.py  # Database service for API
│   ├── routers/     # API endpoints
│   │   ├── stocks.py # GET /api/stocks endpoints
│   │   └── __init__.py
│   └── services/    # API-specific services
│       ├── stock_service.py # Business logic for stock operations
│       └── __init__.py
├── requirements.txt # Backend dependencies (FastAPI, Uvicorn, Pydantic)
├── .env.example     # Configuration template
└── .env             # Runtime configuration

tests/
├── contract/
│   └── test_api.py  # NEW: API endpoint contract tests
└── integration/
    └── test_api_database.py  # NEW: API-database integration tests

frontend/            # Existing React frontend (from feature 002)
├── src/
│   ├── components/
│   ├── pages/
│   └── services/    # Will consume new API endpoints
```

**Structure Decision (UPDATED)**: Initial plan specified `src/api/` directory for API layer, but implementation created separate `backend/` service for better deployment isolation. This provides cleaner separation between CLI tools (in `src/`) and web API (in `backend/`). The backend reuses existing models and services from `src/` but maintains its own dependency management and configuration.

## Complexity Tracking

No violations detected - this section is not applicable.

## Phase 0 Completion: Research ✅

**Status**: COMPLETED

**Artifacts Generated**:
- ✅ `research.md`: Technical decision documentation
  - Web framework selection: FastAPI (rationale provided)
  - DuckDB integration pattern: Synchronous queries in thread pool
  - CORS configuration: CORSMiddleware with configurable origins
  - Testing strategy: pytest + FastAPI TestClient
  - Error handling: HTTPException with descriptive messages
  - Performance analysis: Expected 10-20k req/s, <50ms p95 latency

**Key Decisions**:
1. **Framework**: FastAPI 0.109+ (native async, auto-documentation, minimal boilerplate)
2. **Dependencies**: Uvicorn 0.27+ (ASGI server), Pydantic 2.5+ (validation)
3. **Integration Pattern**: Synchronous DB queries in thread pool (DuckDB not async-native)
4. **Testing**: httpx 0.26+ for TestClient

**All NEEDS CLARIFICATION items resolved** ✅

## Phase 1 Completion: Design & Contracts ✅

**Status**: COMPLETED

**Artifacts Generated**:
- ✅ `data-model.md`: API response entity definitions
  - StockResponse (code, name, metadata)
  - HistoricalDataPoint (date, OHLCV fields)
  - HistoricalDataResponse (stock_code, data array)
  - HealthCheckResponse (status, timestamp, database_connected)
  - ErrorResponse (detail message)
  
- ✅ `contracts/openapi.yaml`: OpenAPI 3.0 specification
  - GET /api/health (health check)
  - GET /api/stocks (list all stocks)
  - GET /api/stocks/{code}/historical (get historical data)
  - Complete request/response schemas
  - Error responses (400, 404, 500, 503)
  
- ✅ `quickstart.md`: Setup and running instructions
  - Installation steps
  - Development and production server commands
  - API verification examples
  - Frontend integration guide
  - Troubleshooting section

- ✅ `CLAUDE.md`: Updated with FastAPI, Uvicorn, Pydantic dependencies

**Design Validation**: All entities map cleanly to database schema and spec requirements.

## Post-Phase 1 Constitution Re-Check ✅

Re-evaluating design artifacts against constitution principles:

### I. Modular Architecture First ✅ PASS (Re-confirmed)

**Design Artifacts Review**:
- `data-model.md` defines API-specific Pydantic models separate from domain models
- Models compose existing database models (Stock, DatabaseConnection)
- Clean separation: Pydantic models (API layer) vs dataclasses (domain layer)
- No circular dependencies in design

**Compliance**: Design maintains layered architecture with clear boundaries.

### II. Test-First Discipline (MANDATORY) ✅ PASS (Re-confirmed)

**Design Artifacts Review**:
- `contracts/openapi.yaml` provides testable API contract specifications
- Each endpoint has defined request/response schemas
- `data-model.md` includes testing strategy section
- `quickstart.md` documents test execution commands

**Compliance**: Design enables contract-first testing approach. Tests can be written from OpenAPI spec before implementation.

### III. Database-Centric Design ✅ PASS (Re-confirmed)

**Design Artifacts Review**:
- `data-model.md` includes explicit database-to-API mapping table
- All response fields map 1:1 to existing database columns
- No schema changes required
- Read-only access pattern documented

**Compliance**: Design respects existing database schema and leverages indexes.

### IV. Performance & Scalability Built-In ✅ PASS (Re-confirmed)

**Design Artifacts Review**:
- `research.md` documents expected performance: 10-20k req/s, <50ms p95 latency
- `data-model.md` includes performance analysis (serialization: 1-2ms per 1000 records)
- Thread pool pattern for synchronous DB queries documented
- Response size estimates provided (150KB for 750 data points)

**Compliance**: Design exceeds performance requirements by 4x margin (50ms vs 200ms target).

### V. Observable & Debuggable Systems ✅ PASS (Re-confirmed)

**Design Artifacts Review**:
- `contracts/openapi.yaml` provides auto-generated API documentation
- Health check endpoint designed for monitoring
- Error responses include descriptive detail messages
- `quickstart.md` includes troubleshooting guide

**Compliance**: Design provides comprehensive observability through auto-docs, health checks, and structured errors.

### Post-Phase 1 Summary: All Gates PASS ✅

Design artifacts confirm alignment with all constitution principles. No violations introduced during Phase 0-1.

**Ready for Phase 2**: Proceed to task breakdown with `/speckit.tasks` command.

## Planning Summary

**Feature**: Backend API Data Access Layer
**Branch**: 003-backend-api
**Status**: Planning Complete (Phases 0-1) ✅

**What Was Delivered**:

1. **Phase 0: Research**
   - Technical framework decision (FastAPI + Uvicorn + Pydantic)
   - Integration patterns (DuckDB, CORS, testing)
   - Performance analysis and validation

2. **Phase 1: Design & Contracts**
   - Data model definitions (5 API response entities)
   - OpenAPI 3.0 API contract (3 endpoints fully specified)
   - Quickstart guide for developers
   - Agent context updates (CLAUDE.md)

**Artifacts Location**:
- Planning docs: `/home/jzhu/oh-my-astock/specs/003-backend-api/`
- Source code structure: `src/api/` (to be created during implementation)
- Test structure: `tests/contract/test_api.py`, `tests/integration/test_api_database.py`

**Constitution Compliance**: ✅ All principles validated (pre-research and post-design)

**Next Step**: Run `/speckit.tasks` to generate implementation task breakdown.
