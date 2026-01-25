# Implementation Plan: Add Calendar for Stock Industry Transactions

**Branch**: `001-calendar-stock-industry` | **Date**: 2026-01-25 | **Spec**: /home/jzhu/oh-my-astock/specs/001-calendar-stock-industry/spec.md
**Input**: Feature specification from `/specs/001-calendar-stock-industry/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add a month selection calendar to the 股票行业成交 (Stock Industry Transactions) page, allowing users to filter and view industry sector transaction data by specific months. The calendar will integrate with the existing SzseSectorSummary component and may require backend API modifications to support month-based data filtering using akshare APIs.

## Technical Context

**Language/Version**: Python 3.10+ (backend), TypeScript/React (frontend)
**Primary Dependencies**: FastAPI/Pydantic (backend), React/TypeScript/Tailwind CSS (frontend), akshare >= 1.10.0
**Storage**: DuckDB (existing database, no new storage needed)
**Testing**: pytest (backend), no specific frontend testing framework mentioned
**Target Platform**: Web application (Linux server backend, browser frontend)
**Project Type**: Full-stack web application extending existing market overview page
**Performance Goals**: Calendar loads within 1 second, data updates within 3 seconds of month selection
**Constraints**: Responsive calendar UI, dark mode support, proper Chinese text rendering, graceful handling of months with no data
**Scale/Scope**: Single month picker component extending existing industry transactions page

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Modular Architecture First**: Frontend calendar component integrates cleanly with existing React component structure, following established patterns from other market overview components.

✅ **Test-First Discipline**: Any new functionality will follow test-first approach, though this feature primarily extends existing tested components.

✅ **Database-Centric Design**: No new database changes required - feature filters existing industry transaction data.

✅ **Performance & Scalability**: Calendar component is lightweight UI addition with minimal performance impact, data filtering happens on existing APIs.

✅ **Observable & Debuggable**: Uses existing error handling and logging patterns, no new observability requirements.

**Gate Status**: PASS - No violations, design aligns with existing architecture.

## Project Structure

### Documentation (this feature)

```text
specs/001-calendar-stock-industry/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── pages/SzseSectorSummary.tsx    # Add month picker calendar and state management
│   └── services/api.ts                # Ensure API client supports month parameters

backend/ (if needed)
├── src/
│   ├── routers/stocks.py              # Potentially add month parameter to /market/szse-sector-summary
│   └── services/stock_service.py      # Potentially add month filtering to get_szse_sector_summary
```

**Structure Decision**: Frontend-only enhancement extending existing market overview page with calendar component.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]
