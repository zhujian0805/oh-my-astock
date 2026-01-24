<!-- SYNC IMPACT REPORT
Version: 1.0.0 (initial ratification)
Changed Principles: None (first edition)
Added Sections: Core Principles (5), Governance
Removed Sections: None
Templates Updated:
  - plan-template.md: ✅ already compliant (Constitution Check section)
  - spec-template.md: ✅ already compliant (requirements framework)
  - tasks-template.md: ✅ already compliant (test-first enforcement)
Follow-up: None - all principles now explicitly documented
-->

# oh-my-astock Constitution

## Core Principles

### I. Modular Architecture First

The codebase is organized into clear, self-contained layers: CLI, models, services, and utilities. Each layer has distinct responsibilities and can be tested independently. New features MUST fit within the existing layered structure—do not create cross-cutting monoliths.

**Non-negotiable Rules**:
- CLI layer handles user interaction only (Click commands, argument parsing)
- Models layer defines validated dataclasses with type hints and serialization
- Services layer contains business logic (API integration, database operations, data transformation)
- Utilities layer provides cross-cutting concerns (config, logging, caching, retries)
- No circular dependencies between layers; data flows downward (CLI → Services → Models → Lib)

### II. Test-First Discipline (MANDATORY)

Tests are written BEFORE implementation. Contract tests validate CLI interfaces and system boundaries; integration tests validate inter-component communication. Tests must fail before code is written; this enforces clear specifications.

**Non-negotiable Rules**:
- Write failing contract/integration tests first (Red phase)
- Implement feature to make tests pass (Green phase)
- Refactor only after tests pass (Refactor phase)
- New services or CLI commands MUST have contract tests
- Test organization mirrors source structure: `tests/contract/` and `tests/integration/`

### III. Database-Centric Design

DuckDB is the single source of truth. All data flow—fetch, transform, validate, store—must be modeled with the database schema as the contract. Schema changes require careful design of both table structure and migration strategy.

**Non-negotiable Rules**:
- Database schema defined in dedicated initialization methods (e.g., `_create_stock_name_code_table()`)
- All tables have primary keys and strategic indexes (query performance, data integrity)
- Batch operations use configurable chunk sizes (default: 1000 records) to balance memory and throughput
- Composite keys used where necessary (e.g., date + stock_code for historical data)
- No schema-breaking changes without migration planning

### IV. Performance & Scalability Built-In

The system is designed for production workloads: 4,000+ stocks, thread-safe parallel processing (20+ threads), smart caching, rate limiting, and retry logic. Performance is not an afterthought—it is embedded in initial design.

**Non-negotiable Rules**:
- Thread-safe operations via thread-local connections (no segmentation faults in multi-threaded contexts)
- Exponential backoff retry with jitter for API failures
- Token bucket rate limiting to respect external API quotas
- Multi-level caching with TTL-based expiration
- Batch processing in configurable chunks; incremental syncs prioritize missing data first
- Debug mode provides performance metrics and structured logging for profiling bottlenecks

### V. Observable & Debuggable Systems

Code must be debuggable and observable in production. Centralized HTTP/SSL configuration, structured logging, and performance metrics are non-negotiable. Text-based output (stderr, stdout) and JSON formats support both human debugging and machine automation.

**Non-negotiable Rules**:
- Centralized HTTP/SSL configuration in a single module (e.g., `http_config.py`)
- All services log significant operations (start, fetch count, errors, completion)
- Debug mode (--debug flag) enables timing metrics and detailed logs
- CLI outputs support both human-readable text and JSON for automation
- Error messages include context (stock code, API endpoint, retry count) not just generic messages

## Project Requirements

### Technology Stack
- **Python 3.10+** (match statements, modern f-strings required)
- **DuckDB >= 0.8.0** (primary data store)
- **akshare >= 1.10.0** (Chinese stock API)
- **click >= 8.0.0** (CLI framework)
- **pandas** (data manipulation)
- **pytest >= 7.0.0** + **pytest-cov >= 4.0.0** (testing)
- **ruff** (linting/formatting)

### Code Quality Gates
- All code must pass `ruff check .` linting
- Code must be formatted with `ruff format .`
- Test coverage SHOULD be tracked (pytest --cov); no hard floor mandated but monitoring required
- Type hints strongly encouraged (not enforced, but expected)
- Docstrings for all public functions and classes

### Testing Strategy
- **Contract tests**: Validate CLI command interfaces, argument parsing, and output formats
- **Integration tests**: Validate service interactions, database operations, and API contract changes
- **Unit tests**: Optional for utilities and helpers (not enforced)
- Run tests from project root: `pytest` or `pytest --cov=src --cov-report=html`

## Development Workflow

### Feature Development
1. Plan the feature with attention to layer boundaries
2. Write failing contract/integration tests first
3. Implement services/models to satisfy tests
4. Add CLI commands to expose functionality
5. Validate tests pass and add documentation

### Database Changes
1. Design new table structure or schema migration
2. Implement table creation in dedicated method (e.g., `_create_X_table()`)
3. Update DatabaseService initialization
4. Write contract tests for data persistence
5. Test with sample data (fetch 100 stocks, verify schema)

### Performance Work
1. Run code in debug mode to identify bottlenecks
2. Profile with timing metrics enabled
3. Modify caching, batch sizes, or parallelism only when metrics justify it
4. Re-run full test suite and benchmarks after optimization
5. Document performance assumptions in code comments

## Governance

### Constitution Supersedes All Practices
This constitution is the source of truth for development practices. If a prior decision conflicts with these principles, the constitution wins. Any violations must be explicitly justified in code comments or PR descriptions.

### Amendment Procedure
1. Open a discussion issue describing the proposed principle change
2. Provide rationale and alternatives considered
3. Update this document with new/modified principles
4. Bump version per semantic versioning (see Version Control below)
5. Run speckit consistency checks (plan, spec, tasks templates) to validate propagation
6. Merge as a single commit with message: `docs: amend constitution to vX.Y.Z (principle changes)`

### Version Control
- **MAJOR**: Backward-incompatible principle removal or redefinition (rare)
- **MINOR**: New principle added or significant guidance expansion
- **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements
- Format: `MAJOR.MINOR.PATCH` (e.g., 1.2.3)

### Compliance Review
- All PR descriptions should reference relevant principles when changes touch multiple layers or affect testing/performance
- Architecture review focuses on adherence to modular design and test-first discipline
- Database changes require schema review against design guidelines

---

**Version**: 1.0.0 | **Ratified**: 2026-01-23 | **Last Amended**: 2026-01-23
