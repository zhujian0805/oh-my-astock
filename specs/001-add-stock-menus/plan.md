# Implementation Plan: Add Stock Market Menu Items

**Branch**: `001-add-stock-menus` | **Date**: 2026-01-25 | **Spec**: /home/jzhu/oh-my-astock/specs/001-add-stock-menus/spec.md
**Input**: Feature specification from `/specs/001-add-stock-menus/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add 5 new CLI commands (sse-summary, szse-summary, szse-area-summary, szse-sector-summary, sse-daily-deals) to fetch and display various Chinese stock exchange market overviews using akshare APIs, following existing command patterns with JSON output and proper error handling.

## Technical Context

**Language/Version**: Python 3.10+ (match statements, modern f-strings required)
**Primary Dependencies**: akshare >= 1.10.0 (Chinese stock API), click >= 8.0.0 (CLI framework), DuckDB >= 0.8.0 (database), pandas (data processing)
**Storage**: DuckDB (single source of truth, no additional storage needed for this feature)
**Testing**: pytest >= 7.0.0 with contract and integration tests
**Target Platform**: Linux (CLI tool)
**Project Type**: Single CLI project
**Performance Goals**: Support 4000+ stocks with thread-safe parallel processing (20+ threads)
**Constraints**: Thread-safe operations, exponential backoff retry, rate limiting, multi-level caching, <30 second command execution
**Scale/Scope**: 5 CLI commands for stock market overviews, integrating with existing API service layer

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Modular Architecture First**: New CLI commands fit within existing layered structure - commands in CLI layer calling existing ApiService.

✅ **Test-First Discipline**: New CLI commands will have contract tests written first to validate interfaces.

✅ **Database-Centric Design**: No database changes required - feature only fetches and displays API data.

✅ **Performance & Scalability**: Follows existing patterns with rate limiting and retry logic in ApiService.

✅ **Observable & Debuggable**: Uses existing centralized logging and structured output (JSON).

**Gate Status**: PASS - No violations, no justifications needed.

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
src/
├── cli/commands.py      # Add 5 new CLI commands (sse-summary, szse-summary, szse-area-summary, szse-sector-summary, sse-daily-deals)
├── services/            # Extend ApiService if needed for new akshare functions
│   └── api_service.py
└── lib/                 # Use existing utilities (logging, config, rate limiting)

tests/
├── contract/            # Add contract tests for new CLI commands
└── integration/         # Add integration tests for API service extensions
```

**Structure Decision**: Single CLI project structure maintained. New commands added to existing commands.py file, leveraging existing ApiService for akshare integration.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
