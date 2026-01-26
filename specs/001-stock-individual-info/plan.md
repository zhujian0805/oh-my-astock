# Implementation Plan: Add Individual Stock Information and Market Quotes

**Branch**: `001-stock-individual-info` | **Date**: 2026-01-26 | **Spec**: /home/jzhu/oh-my-astock/specs/001-stock-individual-info/spec.md
**Input**: Feature specification from `/specs/001-stock-individual-info/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add comprehensive stock market data functionality with two menu items under "股市数据": 个股信息 (individual stock details merged from East Money and Xueqiu APIs) and 行情报价 (market quotes/bid-ask data from East Money API). The feature includes backend API endpoints, frontend pages with flexible layouts, and comprehensive error handling for API failures.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.10+ (match statements, modern f-strings required)
**Primary Dependencies**: FastAPI/Pydantic (backend), React/TypeScript/Tailwind CSS (frontend), akshare >= 1.10.0 (Chinese stock APIs)
**Storage**: DuckDB >= 0.8.0 (existing database, no new tables needed)
**Testing**: pytest >= 7.0.0 (backend), Vitest (frontend)
**Target Platform**: Web application (Linux server)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Individual stock info within 3 seconds, market quotes within 2 seconds
**Constraints**: Show partial data with error indication when Xueqiu API fails for stock info
**Scale/Scope**: Two menu items displaying stock market data for selected stocks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **PASS** - Expanded feature design adheres to all core principles:

**I. Modular Architecture First**: Extended design maintains clear separation with dedicated services (StockInfoService, MarketQuotesService) and routers for different data types, following established layered structure.

**II. Test-First Discipline**: Design includes comprehensive contract and integration tests for both API endpoints, maintaining the established testing patterns in the codebase.

**III. Database-Centric Design**: No database changes required for either feature; existing DuckDB infrastructure sufficient for external API data serving.

**IV. Performance & Scalability**: Both features designed with 2-3 second response times, proper caching, rate limiting, and error handling as established in existing services.

**V. Observable & Debuggable Systems**: Both backend services include proper logging for API calls with context (stock codes, API endpoints); frontend components include loading states and error display with clear user feedback.

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
│   ├── services/          # NEW: stock_info_service.py, market_quotes_service.py (API calls and data processing)
│   ├── routers/           # NEW: stock_info_router.py, market_quotes_router.py (API endpoints)
│   └── lib/
└── tests/

frontend/
├── src/
│   ├── components/        # NEW: StockInfoDisplay.tsx, MarketQuotesTable.tsx (data visualization)
│   ├── pages/             # NEW: IndividualStockInfo.tsx, MarketQuotesPage.tsx (page components)
│   ├── services/          # Update: stock API service client
│   └── config/            # Update: menu.ts (add 行情报价 item)
└── tests/
```

**Structure Decision**: Web application structure selected as feature requires both backend API development (two new services/endpoints) and frontend UI components (two new pages with table/grid displays) for comprehensive stock market data functionality.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
