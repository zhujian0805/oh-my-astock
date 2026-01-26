# Implementation Plan: Add Individual Stock Information Menu Item

**Branch**: `001-stock-individual-info` | **Date**: 2026-01-26 | **Spec**: /home/jzhu/oh-my-astock/specs/001-stock-individual-info/spec.md
**Input**: Feature specification from `/specs/001-stock-individual-info/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement menu items for "个股信息" (individual stock information) and "行情报价" (market quotes/bid-ask data) under "股市数据". Backend will merge data from stock_individual_info_em and stock_individual_basic_info_xq APIs using field-level precedence rules, with automatic retry logic for rate limiting. Frontend provides dropdown selection for stocks and table display for quotes. Comprehensive contract and end-to-end testing ensures API reliability and frontend-backend integration.

## Technical Context

**Language/Version**: Python 3.10+ (match statements, modern f-strings required)
**Primary Dependencies**: FastAPI/Pydantic (backend), React/TypeScript/Tailwind CSS (frontend), akshare >= 1.10.0 (Chinese stock APIs), DuckDB >= 0.8.0 (database)
**Storage**: DuckDB >= 0.8.0 (file-based SQL database)
**Testing**: pytest >= 7.0.0 (testing framework), contract tests for API interfaces, end-to-end tests for user flows
**Target Platform**: Linux server (backend), web browser (frontend)
**Project Type**: web application (frontend + backend)
**Performance Goals**: Stock info display within 3 seconds, market quotes within 2 seconds
**Constraints**: 95% success rate for data retrieval, handle API failures gracefully with partial data
**Scale/Scope**: 4,000+ stocks, thread-safe parallel processing, curated market quotes selection

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **PASS**: Feature adheres to all constitution principles:
- Modular Architecture: Backend services layer for API integration, frontend components for UI
- Test-First Discipline: Contract tests for APIs, end-to-end tests for user flows
- Database-Centric: DuckDB as single source of truth for stock data
- Performance Built-In: 3s/2s response times, rate limiting with retry logic
- Observable Systems: Error handling with user messages, debug logging

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
│   ├── routers/
│   │   └── stock_info.py          # New: Stock and market quotes API endpoints
│   ├── services/
│   │   └── stock_service.py       # New: API integration and data merging
│   ├── models/
│   │   ├── stock.py               # New: Stock data models
│   │   └── market_quote.py        # New: Market quote models
│   └── lib/
│       └── api_client.py          # Updated: Rate limiting and retry logic
├── tests/
│   ├── contract/
│   │   └── test_stock_api.py      # New: API contract tests
│   └── integration/
│       └── test_stock_workflow.py # New: Data merging integration tests
└── requirements.txt                # Updated: akshare >= 1.10.0

frontend/
├── src/
│   ├── pages/
│   │   ├── StockInfo.tsx          # New: Individual stock page
│   │   └── MarketQuotes.tsx       # New: Market quotes page
│   ├── components/
│   │   ├── StockDisplay.tsx       # New: Stock data display
│   │   └── MarketQuotesTable.tsx  # New: Quotes table component
│   └── services/
│       └── stockApi.ts            # New: Frontend API client
├── tests/
│   └── e2e/
│       └── stock-workflow.spec.ts # New: E2E tests
└── package.json                   # Updated: React/TypeScript dependencies

src/ (CLI)
├── models/
│   ├── stock.py                   # New: CLI stock models
│   └── market_quote.py            # New: CLI market quote models
├── services/
│   └── stock_cli_service.py       # New: CLI stock operations
└── cli/
    └── commands/
        └── stock_info.py          # New: CLI commands for stock data
```

**Structure Decision**: Web application with separate backend and frontend deployments, following the project's established pattern. New feature adds stock-related models and services while maintaining modular architecture.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
