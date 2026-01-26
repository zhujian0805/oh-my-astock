# Implementation Plan: Add Individual Stock Information Menu Item

**Branch**: `001-stock-individual-info` | **Date**: 2026-01-26 | **Spec**: /home/jzhu/oh-my-astock/specs/001-stock-individual-info/spec.md
**Input**: Feature specification from `/specs/001-stock-individual-info/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add a menu item "个股信息" under "股市数据" that displays comprehensive individual stock information by merging data from two APIs (East Money and Xueqiu). The feature includes a backend API that fetches and merges stock data, and a frontend dropdown interface for stock selection with flexible grid layout.

## Technical Context

**Language/Version**: Python 3.10+ (match statements, modern f-strings required)
**Primary Dependencies**: FastAPI/Pydantic (backend), React/TypeScript/Tailwind CSS (frontend), akshare >= 1.10.0 (Chinese stock APIs)
**Storage**: DuckDB >= 0.8.0 (existing database, no new tables needed)
**Testing**: pytest >= 7.0.0 (testing framework)
**Target Platform**: Web application (Linux server)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Stock information loads within 3 seconds of selection
**Constraints**: Show partial data with error indication when Xueqiu API fails
**Scale/Scope**: Individual stock information display for selected stocks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **PASS** - Feature adheres to all core principles post-design:

**I. Modular Architecture First**: Design maintains clear separation with backend service layer for API integration and frontend component layer for UI display.

**II. Test-First Discipline**: Design includes contract tests for API endpoints and integration tests for data merging functionality.

**III. Database-Centric Design**: No database changes required; existing DuckDB infrastructure sufficient for this feature.

**IV. Performance & Scalability**: 3-second response time requirement aligns with performance guidelines; parallel API calls and error handling designed for reliability.

**V. Observable & Debuggable Systems**: API contract includes error responses and source status indicators; design supports debug logging and structured error messages.

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
│   ├── services/          # NEW: stock_info_service.py (merge API data)
│   ├── routers/           # NEW: stock_info_router.py (API endpoint)
│   └── lib/
└── tests/

frontend/
├── src/
│   ├── components/        # NEW: StockInfoDisplay.tsx (info display)
│   ├── pages/             # NEW: IndividualStockInfo.tsx (page component)
│   ├── services/          # Update: stock API service
│   └── config/            # Update: menu.ts (add 个股信息 item)
└── tests/
```

**Structure Decision**: Web application structure (Option 2) selected as feature requires both backend API development and frontend UI components for the individual stock information display.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
