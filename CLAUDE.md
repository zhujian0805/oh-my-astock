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
- 2026-01-25: Updated all feature specs with current implementation status
- 2026-01-25: Backend API (003): US1 complete, US2 critical blocker for MVP
- 2026-01-25: Frontend (002): Basic structure complete, awaiting backend API integration
- 2026-01-25: Core system (001): Fully implemented with expanded scope beyond original requirements
- 2026-01-25: Confirmed dual backend architecture - root src/ (CLI) and backend/ (FastAPI API) are separate implementations
- 2026-01-25: Backend/ directory contains active FastAPI service with dedicated requirements.txt and configuration
- 2026-01-25: manage.sh script correctly manages both frontend (port 4142) and backend (port 8000) services
- 003-backend-api: Added Python 3.10+ (matching existing codebase requirements) + FastAPI 0.109+, Uvicorn 0.27+, Pydantic 2.5+ (see research.md for rationale)
- 2026-01-20: Updated to Python 3.10+ requirement (match statement usage)
- 2026-01-20: Corrected project structure documentation

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
