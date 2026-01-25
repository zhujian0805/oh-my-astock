# oh-my-astock Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-25

## Active Technologies
- **Python 3.10+** (uses match statements and modern f-strings)
- **DuckDB >= 0.8.0** (file-based SQL database)
- **akshare >= 1.10.0** (Chinese stock market data API)
- **click >= 8.0.0** (CLI framework)
- **pandas** (data processing)
- **pytest >= 7.0.0** (testing framework)
- **ruff** (linting and formatting)
- **FastAPI 0.109+** (REST API framework)
- **Uvicorn 0.27+** (ASGI server)
- **Pydantic 2.5+** (data validation)
- **React/Vite** (frontend framework)
- **Tailwind CSS** (styling)
- **aiohttp >= 3.8.0** (async HTTP client)
- **websockets >= 10.0** (WebSocket support)
- Python 3.10+ (match statements, modern f-strings required) + akshare >= 1.10.0 (Chinese stock API), click >= 8.0.0 (CLI framework), DuckDB >= 0.8.0 (database), pandas (data processing) (001-add-stock-menus)
- DuckDB (single source of truth, no additional storage needed for this feature) (001-add-stock-menus)
- Python 3.10+ (backend), TypeScript/React (frontend) + FastAPI/Pydantic (backend), React/TypeScript/Tailwind CSS (frontend), akshare >= 1.10.0 (002-add-market-overviews)
- DuckDB (existing database, no new storage needed) (002-add-market-overviews)
- Python 3.10+ (match statements, modern f-strings required) + akshare >= 1.10.0 (Chinese stock API), click >= 8.0.0 (CLI framework), DuckDB >= 0.8.0 (database), pandas (data processing), FastAPI/Pydantic (backend), React/TypeScript/Tailwind CSS (frontend) (001-database-migration-stock-info)
- DuckDB >= 0.8.0 (single source of truth, no additional storage needed) (001-database-migration-stock-info)
- Python 3.10+ + akshare >= 1.10.0, FastAPI/Pydantic, React/TypeScript/Tailwind CSS (001-stock-individual-info)
- DuckDB (existing database, no new tables needed) (001-stock-individual-info)

## Project Structure

```text
oh-my-astock/
├── src/                    # Main CLI source code (15+ commands)
│   ├── cli/               # Command-line interface (15+ commands)
│   ├── models/            # 9 validated dataclasses (Stock, Quote, Profile, etc.)
│   ├── services/          # 4 main business logic services (ApiService, DatabaseService, etc.)
│   ├── routers/           # FastAPI route handlers
│   └── lib/               # 8 utility modules (config, logging, caching, rate limiting)
├── backend/               # Active FastAPI backend service (separate deployment)
│   ├── src/               # FastAPI application code
│   ├── requirements.txt   # Backend-specific dependencies
│   └── .env.example       # Backend configuration template
├── frontend/              # React/Vite web application
├── tests/                 # Test suite (11 test suites)
│   ├── contract/          # CLI and API contract tests
│   └── integration/       # Integration tests
├── specs/                 # Feature specifications and documentation
└── pyproject.toml         # Project configuration (CLI package)
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
- 001-stock-individual-info: Added Python 3.10+ + akshare >= 1.10.0, FastAPI/Pydantic, React/TypeScript/Tailwind CSS
- 001-database-migration-stock-info: Added Python 3.10+ (match statements, modern f-strings required) + akshare >= 1.10.0 (Chinese stock API), click >= 8.0.0 (CLI framework), DuckDB >= 0.8.0 (database), pandas (data processing), FastAPI/Pydantic (backend), React/TypeScript/Tailwind CSS (frontend)
- 001-calendar-stock-industry: Added Python 3.10+ (backend), TypeScript/React (frontend) + FastAPI/Pydantic (backend), React/TypeScript/Tailwind CSS (frontend), akshare >= 1.10.0

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
