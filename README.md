# Oh My Astock

A comprehensive Python library for managing Chinese stock data using DuckDB and akshare API. Provides efficient data fetching, storage, and querying capabilities with a focus on historical stock price data and smart synchronization.

## Overview

Oh My Astock is a professional-grade stock data management system designed specifically for Chinese A-share markets. It combines DuckDB's high-performance columnar storage with akshare's extensive market data APIs to deliver a complete solution for stock market analysis and research.

**Key Statistics:**
- 3,500+ lines of source code
- 11 comprehensive test suites
- 4 main service components
- 9 data models with validation
- 15+ CLI commands
- Thread-safe parallel processing

## Recent Updates (January 2026)

- **Optimized Historical Data Sync**: Batch processing with configurable chunk sizes and smarter stock prioritization (missing data first)
- **Thread-Safe Database Operations**: Thread-local connections eliminate segmentation faults in multi-threaded operations (safe up to 20+ concurrent threads)
- **Enhanced CLI Commands**: 15+ commands with improved help documentation and structured logging
- **Centralized HTTP/SSL Configuration**: Unified SSL, tqdm suppression, and library patching in a single http_config module
- **Database Improvements**: Dedicated table creation methods, automatic schema validation, and indexed queries
- **A-Share Stock Filtering**: Automatically filters for A-share stocks (codes: 0xxxx, 3xxxx, 6xxxx, 8xxxx)
- **Performance Enhancements**: Multi-level caching, rate limiting, and exponential backoff retry mechanisms

## FastAPI Backend

Oh My Astock includes a FastAPI-based REST API server for frontend integration and programmatic access to stock data.

### Quick Start with Backend

```bash
# Start the backend API server
./manage.sh start backend

# The API will be available at http://localhost:8000
# Interactive API documentation at http://localhost:8000/docs

# Start both frontend and backend
./manage.sh start all
```

### API Endpoints

- `GET /api/health` - Health check and database connectivity status
- `GET /api/stocks` - List all available stocks with pagination
- `GET /api/stocks/{code}/historical` - Get historical price data for a specific stock

### Example API Usage

```python
import requests

# Health check
response = requests.get("http://localhost:8000/api/health")
print(response.json())

# Get all stocks
response = requests.get("http://localhost:8000/api/stocks?limit=10")
stocks = response.json()

# Get historical data for a stock
response = requests.get("http://localhost:8000/api/stocks/000001/historical")
data = response.json()
```

## Features

### Core Capabilities

- **Stock Data Fetching**: Retrieve 4,000+ stocks from Shanghai (6xxxx), Shenzhen (0xxxx/3xxxx), and Beijing (8xxxx) exchanges via akshare API with automatic A-share filtering
- **Historical Data Synchronization**: Smart incremental sync with three strategies:
  - **full_sync**: Complete historical data refresh
  - **today_only**: Fetch only today's data
  - **smart_check**: Intelligent detection and filling of data gaps
- **Real-Time Market Data**: Live quotes, financials, dividends, shareholder structures, and press releases via Sina Finance API
- **Comprehensive Company Information**: Profile, financial metrics, shareholder structure, dividend history, and news aggregation

### Technical Features

- **Database Management**: DuckDB-based columnar storage with automatic schema initialization and indexed queries
- **Thread-Safe Operations**: Parallel processing with thread-local connections (safe up to 20+ concurrent threads)
- **Data Models**: 9 validated dataclasses (Stock, Quote, Profile, Financial, Dividend, Structure, Press, etc.)
- **CLI Interface**: 15+ commands for database, data, and query operations
- **FastAPI Backend**: RESTful API server with automatic OpenAPI documentation and CORS support
- **Modular Architecture**: Clean separation of concerns across CLI, services, models, routers, and utilities layers
- **Performance Optimization**:
  - Batch processing with configurable chunk sizes (default: 1000 records)
  - Multi-level caching with TTL-based expiration
  - Rate limiting with token bucket algorithm
  - Exponential backoff retry with circuit breakers
- **Debug & Observability**: Performance metrics, structured logging, and detailed error reporting
- **SSL Handling**: Centralized HTTP/SSL configuration with automatic certificate management

## Installation

It is highly recommended to use a virtual environment.

### 1. Set up Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Package

```bash
# Install dependencies
pip install -r requirements.txt

# Install the package in editable mode
pip install -e .
```

## Quick Start

Get started with oh-my-astock with this essential workflow:

### 🚀 Essential 3-Step Workflow

```bash
# Step 1: Create your database
stocklib init-db --default
# Creates stock.duckdb in your current working directory

# Step 2: Fetch all available stocks (~4000+ stocks from CN exchanges)
stocklib fetch-stocks --default-db

# Step 3: Sync historical data (smart incremental sync with parallel processing)
stocklib sync-historical --default-db --all-stocks --max-threads 20
```

That's it! You now have a complete Chinese stock database with historical data.

### 📊 Query Your Data

```bash
# View all stocks in your database
stocklib list-stocks --default-db --limit 10

# Get historical data for specific stock (e.g., Ping An Bank - 000001)
stocklib get-historical 000001 --default-db --start-date "2024-01-01"

# Get real-time quote
stocklib quote 000001,600036

# Search stocks by name or code
stocklib search "银行"
```

### 🎯 Advanced Usage

#### Initialize Custom Database Location
```bash
# Absolute paths
stocklib init-db --db-path /path/to/stocks.db
stocklib init-db --db-path ~/data/stocks.db

# Relative paths (from current directory)
stocklib init-db --db-path ./data/stocks.db
stocklib init-db --db-path data/stocks.db
```

#### Selective Stock Sync
```bash
# Sync only specific stocks
stocklib sync-historical --default-db --stock-codes "000001,600036,000858"

# Force full re-sync (overwrite existing data)
stocklib sync-historical --default-db --stock-codes "000001" --force-full-sync

# Limit number of stocks to process (useful for testing)
stocklib sync-historical --default-db --all-stocks --limit 100
```

#### Get Detailed Stock Information
```bash
# Fetch company profile and financial data
stocklib info 000001 --financials

# Get dividend history
stocklib info 000001 --dividends

# View shareholder structure
stocklib info 000001 --structure
```

#### Database Inspection
```bash
# View all tables in your database
stocklib list-tables --default-db

# Check stock data coverage
stocklib list-stocks --default-db
```

#### Debug & Performance Monitoring
```bash
# Enable debug mode with detailed logging and timing metrics
stocklib --debug init-db --default
stocklib --debug fetch-stocks --validate-only
stocklib --debug sync-historical --default-db --stock-codes "000001"
```

### 💡 Pro Tips

- **Default DB Path**: Use `--default-db` flag to automatically use `stock.duckdb` in your current working directory
- **Custom Location**: Set `ASTOCK_DB_PATH` environment variable to use a different default location
- **Validate First**: Use `--validate-only` flag with `fetch-stocks` to test API connectivity without storing data
- **Parallel Processing**: Adjust `--max-threads` (default: 10) based on your system capabilities and network
- **Smart Sync**: The historical sync automatically detects gaps and only fetches missing data - no duplicates!

## Architecture

The library follows a layered, modular architecture with clear separation of concerns and comprehensive utilities:

```
src/
├── cli/                     # Command-line interface layer
│   └── commands.py          # 15+ Click-based commands (963 LOC)
│
├── models/                  # Data models layer (9 models, 638 LOC)
│   ├── stock.py             # Stock entity (code, name, metadata)
│   ├── quote.py             # Real-time quotes (price, volume, change %)
│   ├── profile.py           # Company profiles (industry, market cap, ratios)
│   ├── financial.py         # Quarterly financials (revenue, profit, per-share)
│   ├── dividend.py          # Dividend history (shares, cash, dates)
│   ├── structure.py         # Shareholder composition (top 10 holders)
│   ├── press.py             # Press releases and news
│   ├── stock_list.py        # Stock list aggregation
│   └── database.py          # DatabaseConnection with connection pooling
│
├── services/                # Business logic layer (4 services, 2,843 LOC)
│   ├── api_service.py       # Akshare API integration (531 LOC)
│   │   ├── fetch_stock_info()
│   │   ├── validate_stock_data()
│   │   └── A-share filtering logic
│   │
│   ├── database_service.py  # DuckDB operations (185 LOC)
│   │   ├── initialize_database()
│   │   ├── insert_stocks()
│   │   └── get_all_stocks()
│   │
│   ├── historical_data_service.py # Historical sync engine (984 LOC)
│   │   ├── fetch_historical_data() with 3 strategies
│   │   ├── compute_fetching_list() with prioritization
│   │   ├── bulk_store_historical_data() with batch processing
│   │   ├── check_data_freshness()
│   │   └── Thread-safe parallel operations
│   │
│   └── sina_finance_service.py # Sina Finance API (1,143 LOC)
│       ├── get_quote() / get_quotes()
│       ├── get_profile()
│       ├── get_financials()
│       ├── get_shareholder_structure()
│       ├── get_dividends()
│       ├── get_press_releases()
│       └── search_stocks()
│
└── lib/                     # Utilities layer (371+ LOC)
    ├── config.py            # Configuration management (env vars, defaults)
    ├── logging.py           # Structured logging setup
    ├── debug.py             # Performance metrics and timing (80 LOC)
    ├── http_config.py       # Centralized HTTP/SSL/tqdm config (213 LOC)
    ├── db_utils.py          # Database helpers and pooling
    ├── cache.py             # Multi-level caching with TTL
    ├── rate_limiter.py      # Token bucket rate limiting
    └── retry.py             # Exponential backoff with jitter
```

### Component Responsibilities

| Component | Role | Key Features |
|-----------|------|--------------|
| **ApiService** | Fetch 4,000+ stocks from Chinese exchanges | Pagination, validation, A-share filtering |
| **DatabaseService** | DuckDB schema initialization and management | Batch insert, connection pooling, indexes |
| **HistoricalDataService** | Smart incremental sync with parallel processing | 3 strategies, missing data detection, batch processing |
| **SinaFinanceService** | Real-time quotes and company data aggregation | Quote, profile, financials, dividends, news, search |
| **CLI Commands** | User-friendly command-line interface | 15+ commands, structured help, global options |
| **Data Models** | Validated dataclasses for all data types | Type validation, serialization, from_dict/to_dict |
| **Utilities** | Cross-cutting concerns | Config, logging, caching, rate limiting, retry |

## API Usage

### Basic Usage

```python
from oh_my_astock.services.database_service import DatabaseService
from oh_my_astock.services.api_service import ApiService
from oh_my_astock.services.historical_data_service import HistoricalDataService

# Initialize database
db = DatabaseService()
db.initialize_database()

# Fetch stocks from API
api = ApiService()
stocks = api.fetch_stock_info()

# Store in database
db.insert_stocks(stocks)

# Initialize historical data service
hist_service = HistoricalDataService()

# Fetch and store historical data for a stock
hist_service.fetch_and_store_historical_data("000001")

# Query historical data
import pandas as pd
df = hist_service.get_historical_data("000001", "2023-01-01", "2023-12-31")
```

### Advanced Features

```python
from oh_my_astock.lib.cache import Cache
from oh_my_astock.lib.rate_limiter import RateLimiter
from oh_my_astock.lib.retry import retry_with_backoff
from oh_my_astock.lib.http_config import configure_ssl

# Configure SSL for reliable API access
configure_ssl()

# Use caching for API responses
cache = Cache(ttl=3600)  # 1-hour cache
data = cache.get_or_set("key", lambda: expensive_api_call())

# Rate limiting for API calls
limiter = RateLimiter(calls_per_second=5)
with limiter:
    api_call()

# Retry with exponential backoff
@retry_with_backoff(max_retries=3)
def fetch_data():
    return api.fetch_stock_info()
```

## Smart Sync Features

The historical data synchronization engine incorporates intelligent features for efficient and reliable data management:

### Sync Strategies

1. **full_sync**: Complete historical refresh (resets all data for selected stocks)
2. **today_only**: Fetch only today's OHLCV data (quick daily updates)
3. **smart_check**: Intelligent gap detection and filling (default, recommended)

### Optimization Features

- **Missing Data Detection**: Automatically identifies data gaps in existing records
- **Incremental Updates**: Only fetches missing data, not already stored (no duplicates)
- **Smart Prioritization**: Stocks without any historical data are fetched first
- **Parallel Processing**: Thread-safe concurrent processing with configurable threads (safe up to 20+)
- **Batch Optimization**: Accumulates records and bulk inserts in configurable chunks (default: 1000)
- **Freshness Validation**: Tracks last sync dates and detects stale data
- **Error Handling**: Graceful API failure handling with retry mechanisms
- **Duplicate Prevention**: Composite keys prevent duplicate entries (date + stock_code)
- **Rate Limiting**: Built-in API throttling to prevent service throttling
- **Intelligent Caching**: Response caching reduces redundant API requests

### Performance Metrics

For a complete sync of 4,000+ stocks:
- **Initial sync**: ~2-4 hours (depending on network and thread count)
- **Incremental sync**: ~5-15 minutes for daily updates
- **Parallel efficiency**: Near-linear scaling up to 20 threads
- **Storage**: ~5-15GB for 10+ years of historical data

## Requirements

- **Python 3.10+** (code uses `match` statement and modern f-string syntax)
- DuckDB >= 0.8.0
- akshare >= 1.10.0
- click >= 8.0.0
- pandas
- requests
- **FastAPI Backend Requirements:**
  - fastapi >= 0.109.0
  - uvicorn[standard] >= 0.27.0
  - pydantic >= 2.5.0
  - pydantic-settings >= 2.0.0
- pytest >= 7.0.0 (for testing)
- pytest-cov >= 4.0.0 (for coverage)
- ruff (for linting and formatting)

## Virtual Environment Setup

Set up a virtual environment before using the library:

### Windows

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Linux/macOS

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Development

### Testing

Run tests from the **project root directory**:

```bash
# Run all tests (from project root)
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test types
pytest tests/contract/           # Contract tests only
pytest tests/integration/        # Integration tests only

# Run a specific test file
pytest tests/contract/test_lib_utils.py -v

# Run with verbose output
pytest -v
```

### Code Quality

Check code quality with ruff:

```bash
# Check all code for issues
ruff check .

# Check and auto-fix issues
ruff check . --fix

# Check specific directory
ruff check src/

# Format code
ruff format .
```

**Note:** Current code uses Python 3.10+ features (`match` statement) which may cause syntax errors if targeting Python 3.8.

### Project Structure

```
src/
├── cli/                 # Command-line interface
│   ├── commands.py      # Click-based CLI commands
│   └── __init__.py
├── models/              # Data models
│   ├── database.py      # DatabaseConnection class
│   ├── stock.py         # Stock entity model
│   ├── quote.py         # Real-time quote model
│   ├── profile.py       # Company profile model
│   ├── dividend.py      # Dividend data model
│   ├── financial.py     # Financial data model
│   └── __init__.py
├── routers/             # FastAPI route handlers
│   ├── stocks.py        # Stock API endpoints
│   └── __init__.py
├── services/            # Business logic
│   ├── api_service.py   # Akshare API integration
│   ├── database_service.py # Database operations
│   ├── historical_data_service.py # Historical data management with batch processing
│   ├── sina_finance_service.py # Sina Finance API integration
│   ├── stock_service.py # Stock business logic for FastAPI
│   └── __init__.py
├── lib/                 # Utilities
│   ├── config.py        # Configuration management
│   ├── logging.py       # Structured logging setup
│   ├── debug.py         # Debug utilities and metrics
│   ├── db_utils.py      # Database utilities
│   ├── http_config.py   # Centralized HTTP/SSL configuration
│   ├── cache.py         # Caching mechanisms
│   ├── rate_limiter.py  # Rate limiting
│   ├── retry.py         # Retry logic with exponential backoff
│   └── __init__.py
├── main.py              # FastAPI application entry point
├── config.py            # FastAPI configuration
└── database.py          # FastAPI database service

backend/                 # Legacy Node.js backend (deprecated)
├── package.json         # Removed - migrated to Python
├── src/                 # Removed - migrated to Python
└── .env.example         # Updated for FastAPI

frontend/                # React/Vite frontend application
├── src/
├── package.json
├── vite.config.ts
└── ...

tests/
├── contract/           # Contract tests for CLI interfaces
├── integration/        # Integration tests for component interaction
└── __pycache__/        # Python cache files
```

## Data Schema

### Stock Information Table (`stock_name_code`)

Core stock registry with automatic A-share filtering:

| Column | Type | Description |
|--------|------|-------------|
| `code` | VARCHAR (PK) | Stock code (000001, 600000, etc.) |
| `name` | VARCHAR | Company name (Chinese) |
| `metadata` | JSON | Additional metadata (exchange, sector, etc.) |

**Indexes:** PRIMARY KEY on `code`

### Historical Data Table (`stock_historical_data`)

Complete OHLCV data with technical indicators:

| Column | Type | Description |
|--------|------|-------------|
| `date` | DATE | Trading date (composite PK with stock_code) |
| `stock_code` | VARCHAR | Stock code (composite PK with date) |
| `open_price` | DECIMAL | Opening price |
| `close_price` | DECIMAL | Closing price |
| `high_price` | DECIMAL | Daily high price |
| `low_price` | DECIMAL | Daily low price |
| `volume` | BIGINT | Trading volume (shares) |
| `turnover` | DECIMAL | Trading amount (RMB) |
| `amplitude` | DECIMAL | Price amplitude (%) |
| `price_change_rate` | DECIMAL | Price change rate (%) |
| `price_change` | DECIMAL | Absolute price change |
| `turnover_rate` | DECIMAL | Turnover rate (%) |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last update time |

**Indexes:**
- Composite PRIMARY KEY: (date, stock_code)
- `idx_stock_historical_data_code`: Optimizes stock lookups
- `idx_stock_historical_data_date`: Optimizes date range queries

### Exchange Code Reference

| Exchange | Code Range | Example |
|----------|-----------|---------|
| Shanghai | 6xxxx | 600000 (China Merchants Bank) |
| Shenzhen Main | 0xxxx | 000001 (Ping An Bank) |
| Shenzhen SME | 3xxxx | 300750 (Artisan Valley) |
| Beijing | 8xxxx | 880001 |

## Troubleshooting

### Database Connection Issues

**Problem:** Database file cannot be created or accessed
- **Solution:** Ensure write permissions to the target directory
- **Workaround:** Try using a simpler path like `/tmp/stock.db` or `./data/stock.db`
- **Command:** `stocklib init-db --db-path /tmp/test.db --debug`

### API Fetching Problems

**Problem:** Stock data fetch fails with SSL/Connection errors
- **Solution:** The library automatically handles SSL issues and has fallback mechanisms
- **Verify:** Use `--validate-only` flag to test connectivity without storing data
- **Command:** `stocklib fetch-stocks --default-db --validate-only --debug`

**Problem:** Rate limit errors from akshare API
- **Solution:** Reduce `--max-threads` or increase wait time between requests
- **Recommendation:** Start with `--max-threads 5` and increase gradually
- **Command:** `stocklib sync-historical --default-db --all-stocks --max-threads 5 --debug`

### Historical Data Sync Issues

**Problem:** Sync fails or experiences timeouts for specific stocks
- **Solution:** Use thread-local connections (enabled by default) and check thread count
- **Workaround:** Sync individual stocks to identify problematic ones
- **Command:** `stocklib sync-historical --default-db --stock-codes "000001" --debug`

**Problem:** Segmentation faults or memory issues
- **Solution:** Reduce `--max-threads` (thread-local connections eliminate most issues)
- **Recommendation:** Use 5-10 threads for stability, 10-15 for performance
- **Environment:** Set `DUCKDB_MEMORY_LIMIT=2GB` for constrained systems

### Import and Module Errors

**Problem:** `ModuleNotFoundError` or `ImportError` when running commands
- **Solution:** Ensure virtual environment is activated and package installed
- **Check:** Verify with `which python` and `pip list | grep oh-my-astock`
- **Fix:** Reinstall with `pip install -e .` from project root

**Problem:** Symbol or function not found in models/services
- **Solution:** Verify installation completed successfully
- **Check:** Run `python -c "from oh_my_astock.services import ApiService"`
- **Debug:** Check Python version with `python --version` (requires 3.10+)

### Configuration Issues

**Problem:** `--default-db` flag doesn't work as expected
- **Solution:** File path resolution order: CLI args → env var `ASTOCK_DB_PATH` → `./stock.duckdb`
- **Verify:** Check with `echo $ASTOCK_DB_PATH`
- **Fix:** Set explicitly with `stocklib init-db --db-path /path/to/stock.db`

### Performance Issues

**Problem:** Operations are slow or consuming excessive memory
- **Solution:** Enable debug mode to identify bottlenecks
- **Command:** `stocklib --debug sync-historical --default-db --stock-codes "000001"`
- **Analysis:** Check logs for API latency vs. database insertion time

**Problem:** Batch insert is slow
- **Workaround:** Adjust bulk insert chunk size
- **Command:** `BULK_INSERT_CHUNK_SIZE=500 stocklib sync-historical --default-db --all-stocks`
- **Default:** 1000 records per batch (optimal for most systems)

### Test Failures

**Problem:** Tests fail due to existing database files
- **Solution:** Remove test database files before running tests
- **Command:** `rm -f stock.duckdb && pytest tests/`
- **Check:** Use `pytest --tb=short` for detailed error information

## CLI Commands Reference

Complete list of available commands for database and data management:

### Database Management

| Command | Purpose | Key Options |
|---------|---------|------------|
| `init-db` | Initialize database with schema | `--db-path`, `--default-db` |
| `list-tables` | Show all database tables | `--db-path`, `--default-db` |
| `list-stocks` | Display stored stocks | `--limit`, `--db-path` |

### Stock Data Operations

| Command | Purpose | Key Options |
|---------|---------|------------|
| `fetch-stocks` | Fetch all stocks from exchanges | `--db-path`, `--validate-only`, `--default-db` |
| `sync-historical` | Sync historical price data | `--stock-codes`, `--all-stocks`, `--max-threads`, `--sync-strategy` |
| `get-historical` | Query historical data | `--start-date`, `--end-date`, `--db-path` |

### Real-Time Data & Search

| Command | Purpose | Key Options |
|---------|---------|------------|
| `quote` | Get real-time quotes | Single or multiple stock codes |
| `info` | Company comprehensive info | `--financials`, `--dividends`, `--structure`, `--all` |
| `search` | Search stocks by code/name | Query string (code, name, or pinyin) |

### Global Options

Available with all commands:
- `--log-level`: DEBUG, INFO, WARNING, ERROR (default: INFO)
- `--log-file`: Custom log file path
- `--debug` / `-d`: Enable verbose debug mode with timing metrics

### Examples

```bash
# Initialize and populate database
stocklib init-db --default-db
stocklib fetch-stocks --default-db
stocklib sync-historical --default-db --all-stocks --max-threads 15

# Query data
stocklib list-stocks --default-db --limit 20
stocklib get-historical 000001 --db-path ./stock.db --start-date 2024-01-01
stocklib quote 000001,600000

# Get company info
stocklib info 000001 --all
stocklib search "银行" --limit 10

# Debug operations
stocklib --debug sync-historical --default-db --stock-codes "000001"
stocklib --log-level DEBUG fetch-stocks --default-db --validate-only
```

## Configuration

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `ASTOCK_DB_PATH` | Default database path | `/data/stocks.db` |
| `DUCKDB_THREADS` | Thread count for queries | `4` (default: 2) |
| `DUCKDB_MEMORY_LIMIT` | Memory limit | `4GB` (default) |
| `BULK_INSERT_CHUNK_SIZE` | Records per batch insert | `1000` (default) |
| `TQDM_DISABLE` | Disable progress bars | `1` |

### Configuration Hierarchy

1. **CLI Parameters** (highest priority)
   - `--db-path`, `--max-threads`, `--log-level`

2. **Environment Variables**
   - `ASTOCK_DB_PATH`, `DUCKDB_THREADS`, `BULK_INSERT_CHUNK_SIZE`

3. **Compiled Defaults** (lowest priority)
   - DuckDB: 2 threads, 4GB memory
   - Sync: 1000-record chunks
   - DB: `./stock.duckdb`

## License

MIT License
