# Implementation Plan: Add Stock Market Overview Items to Frontend/Backend

**Branch**: `002-add-market-overviews` | **Date**: 2026-01-25 | **Spec**: /home/jzhu/oh-my-astock/specs/002-add-market-overviews/spec.md
**Input**: Feature specification from `/specs/002-add-market-overviews/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add 6 stock market overview sections to the frontend sidebar (上海证券交易所, 深圳证券交易所, 证券类别统计, 地区交易排序, 股票行业成交, 上海证券交易所-每日概况) with corresponding backend API endpoints fetching data from akshare APIs, all displayed in responsive table format with dark mode support.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.10+ (backend), TypeScript/React (frontend)
**Primary Dependencies**: FastAPI/Pydantic (backend), React/TypeScript/Tailwind CSS (frontend), akshare >= 1.10.0
**Storage**: DuckDB (existing database, no new storage needed)
**Testing**: pytest (backend), no specific frontend testing framework mentioned
**Target Platform**: Web application (Linux server backend, browser frontend)
**Project Type**: Full-stack web application (backend + frontend)
**Performance Goals**: Data loading within 3 seconds, smooth navigation between sections
**Constraints**: Responsive table display, dark mode support, proper Chinese text rendering
**Scale/Scope**: 6 new market overview components, extending existing stock market overview page

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Modular Architecture First**: Backend follows layered structure (routers → services → models), frontend components are self-contained.

✅ **Test-First Discipline**: Backend endpoints can have contract tests, frontend components follow existing patterns.

✅ **Database-Centric Design**: Uses existing DuckDB infrastructure, no new database changes required.

✅ **Performance & Scalability**: API calls include proper async handling, frontend components are lightweight.

✅ **Observable & Debuggable**: Backend uses structured logging, frontend follows existing error handling patterns.

**Gate Status**: PASS - No violations, design aligns with existing architecture.

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
backend/
├── src/
│   ├── routers/stocks.py      # Add 5 new endpoints: /market/szse-summary, /market/szse-area-summary, /market/szse-sector-summary, /market/sse-daily-deals, /market/security-categories
│   └── services/stock_service.py # Add 5 new methods for market data fetching

frontend/
├── src/
│   ├── pages/StockMarketOverviewPage.tsx # Update to include all 6 menu items
│   ├── pages/                                # Add 5 new overview components
│   │   ├── SzseSummary.tsx                  # Shenzhen exchange summary
│   │   ├── SzseAreaSummary.tsx             # Regional trading rankings
│   │   ├── SzseSectorSummary.tsx           # Industry sector data
│   │   ├── SseDailyDeals.tsx               # Shanghai daily deals
│   │   └── SecurityCategories.tsx          # Security category statistics
│   └── services/api.ts                     # Ensure API client supports new endpoints
```

**Structure Decision**: Full-stack web application extending existing market overview page with additional sidebar navigation items.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
