# oh-my-astock Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-20

## Active Technologies
- **Python 3.10+** (uses match statements and modern f-strings)
- **DuckDB >= 0.8.0** (file-based SQL database)
- **akshare >= 1.10.0** (Chinese stock market data API)
- **click >= 8.0.0** (CLI framework)
- **pandas** (data processing)
- **pytest >= 7.0.0** (testing framework)
- **ruff** (linting and formatting)

## Project Structure

```text
oh-my-astock/
├── src/                    # Main source code
│   ├── cli/               # Command-line interface
│   ├── models/            # Data models (Stock, Quote, Profile, etc.)
│   ├── services/          # Business logic (API, Database, Historical Data)
│   └── lib/               # Utilities (config, logging, debug)
├── tests/                 # Test suite
│   ├── contract/          # CLI and API contract tests
│   └── integration/       # Integration tests
├── specs/                 # Feature specifications and documentation
└── pyproject.toml         # Project configuration
```

## Commands

**Testing (run from project root):**
```bash
pytest                              # Run all tests
pytest -v                          # Verbose output
pytest --cov=src --cov-report=html # With coverage report
pytest tests/contract/             # Contract tests only
```

**Code Quality:**
```bash
ruff check .                       # Check for issues
ruff check . --fix                # Auto-fix issues
ruff format .                      # Format code
```

**CLI Usage:**
```bash
stocklib --help                    # Show all commands
stocklib init-db --default-db      # Initialize database
stocklib fetch-stocks --default-db # Fetch stock data
```

## Code Style

- **Python:** Follow PEP 8 conventions
- **Linting:** Use ruff for code quality checks
- **Type Hints:** Strongly encouraged throughout codebase
- **Docstrings:** Use for all public functions and classes
- **Testing:** Write contract tests for all new features

## Recent Changes
- 2026-01-20: Updated to Python 3.10+ requirement (match statement usage)
- 2026-01-20: Corrected project structure documentation
- 2026-01-20: Fixed command examples (pytest runs from root, not src/)
- 001-duckdb-stock-setup: Initial setup with DuckDB + akshare integration

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
