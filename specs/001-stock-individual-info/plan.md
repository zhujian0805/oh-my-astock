# Implementation Plan: Add Individual Stock Information Menu Item

**Branch**: `001-stock-individual-info` | **Date**: 2026-01-25 | **Spec**: [specs/001-stock-individual-info/spec.md](specs/001-stock-individual-info/spec.md)
**Input**: Feature specification from `/specs/001-stock-individual-info/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add a menu item "个股信息" under "股市数据" section that allows users to select stocks from a dropdown and view merged information from stock_individual_info_em and stock_individual_basic_info_xq APIs. Backend will provide a new API endpoint that fetches and merges data from both sources.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: akshare >= 1.10.0, FastAPI/Pydantic, React/TypeScript/Tailwind CSS
**Storage**: DuckDB (existing database, no new tables needed)
**Testing**: pytest >= 7.0.0
**Target Platform**: Linux server, web application
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Handle 4000+ stocks, thread-safe parallel processing
**Constraints**: Rate limiting for API calls, caching, production workloads
**Scale/Scope**: Chinese stock market data, individual stock information display

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Modular Architecture First**: ✅ Feature fits within existing layered structure - backend services for API integration, frontend UI components
- **Test-First Discipline**: ✅ New functionality will have contract and integration tests written first
- **Database-Centric Design**: ✅ No new database schema changes required - leverages existing DuckDB storage if needed for caching
- **Performance & Scalability**: ✅ API calls will implement rate limiting, caching, and thread-safe operations per constitution requirements
- **Observable & Debuggable Systems**: ✅ Will include structured logging, error context, and debug mode support for API operations

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
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
backend/
├── src/
│   ├── models/
│   ├── services/          # NEW: stock_info_service.py (API integration)
│   ├── routers/           # NEW: stock_info_router.py (API endpoint)
│   └── lib/
└── tests/

frontend/
├── src/
│   ├── components/        # NEW: StockInfoDropdown.tsx, StockInfoDisplay.tsx
│   ├── pages/             # NEW: IndividualStockPage.tsx
│   └── services/          # NEW: stockInfoApi.ts
└── tests/
```

**Structure Decision**: Web application structure with separate backend (FastAPI) and frontend (React/TypeScript). New components added to existing directories following established patterns.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
