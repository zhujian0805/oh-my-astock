# Oh My Astock

A comprehensive Python library for managing Chinese stock data using DuckDB and akshare API. Provides efficient data fetching, storage, and querying capabilities with a focus on historical stock price data and smart synchronization.

## Features

- **Database Management**: Initialize and manage DuckDB databases for stock data storage
- **Stock Data Fetching**: Retrieve comprehensive stock information from Chinese exchanges (Shanghai, Shenzhen, Beijing) via akshare API
- **Historical Data Sync**: Smart synchronization of historical stock price data with automatic missing data detection and incremental updates
- **Data Models**: Well-defined Python models for stock data with validation
- **CLI Interface**: Command-line tools for all database and data operations
- **Modular Design**: Clean separation of concerns with reusable components
- **Debug Capabilities**: Built-in performance metrics, logging, and troubleshooting tools
- **SSL Handling**: Automatic SSL certificate management for reliable API access

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install the package directly
pip install -e .
```

## Quick Start

### 1. Initialize Database

```bash
# Initialize with default path (d:\duckdb\stock.duckdb)
stocklib init-db --default

# Or specify custom path
stocklib init-db --db-path /path/to/stocks.db
```

### 2. Fetch Stock Information

```bash
# Fetch and store all stocks from Chinese exchanges
stocklib fetch-stocks --default-db

# Just validate data without storing
stocklib fetch-stocks --validate-only
```

### 3. Sync Historical Data

```bash
# Smart sync historical data for all stocks (recommended)
stocklib sync-historical --default-db --all-stocks

# Sync specific stocks
stocklib sync-historical --default-db --stock-codes "000001,600036,000858"

# Force full sync for specific stocks (overwrite existing data)
stocklib sync-historical --default-db --stock-codes "000001" --force-full-sync

# Sync with parallel processing (default 10 threads)
stocklib sync-historical --default-db --all-stocks --max-threads 20

# Limit number of stocks to process
stocklib sync-historical --default-db --all-stocks --limit 100
```

### 4. Query Data

```bash
# List all stocks
stocklib list-stocks --default-db

# List first 10 stocks
stocklib list-stocks --default-db --limit 10

# Get historical data for a specific stock
stocklib get-historical --default-db --stock-code "000001"

# Get historical data with date filters
stocklib get-historical --default-db --stock-code "000001" --start-date "2023-01-01" --end-date "2023-12-31"

# Get recent data with limit
stocklib get-historical --default-db --stock-code "000001" --limit 30
```

### 5. Inspect Database

```bash
# See all tables in the database
stocklib list-tables --default-db
```

### 6. Debug Mode

```bash
# Enable debug logging and performance metrics
stocklib --debug init-db --default

# Debug fetch operation with timing information
stocklib --debug fetch-stocks --validate-only

# Debug historical data sync
stocklib --debug sync-historical --default-db --stock-codes "000001"
```

## Architecture

The library follows a modular architecture:

```
src/
├── cli/              # Command-line interface using Click
├── models/           # Data models (Stock, DatabaseConnection)
├── services/         # Business logic (API, Database, HistoricalData services)
└── lib/              # Utilities (config, logging, debug, db_utils)
```

## API Usage

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

## Smart Sync Features

The historical data synchronization includes intelligent features:

- **Missing Data Detection**: Automatically identifies gaps in historical data
- **Incremental Updates**: Only fetches data that's missing, not already stored
- **Freshness Checks**: Validates data currency and updates as needed
- **Parallel Processing**: Concurrent processing of multiple stocks for performance
- **Error Handling**: Graceful handling of API failures with detailed logging
- **Duplicate Prevention**: Ensures no duplicate data entries

## Requirements

- Python 3.8+
- DuckDB >= 0.8.0
- akshare >= 1.10.0
- click >= 8.0.0
- pandas
- requests

## Virtual Environment Setup

Set up a virtual environment before using the library:

```bash
# Create virtual environment (Windows)
python -m venv "D:\venvs\stock"

# Activate (Windows)
D:\venvs\stock\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

See `VIRTUAL_ENV_SETUP.md` for detailed setup instructions.

## Development

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test types
pytest tests/contract/    # Contract tests
pytest tests/integration/ # Integration tests
```

### Project Structure

```
src/
├── cli/                 # Command-line interface
│   ├── commands.py      # Click-based CLI commands
│   └── __init__.py
├── models/              # Data models
│   ├── database.py      # DatabaseConnection class
│   ├── stock.py         # Stock entity model
│   └── __init__.py
├── services/            # Business logic
│   ├── api_service.py   # Akshare API integration
│   ├── database_service.py # Database operations
│   ├── historical_data_service.py # Historical data management
│   └── __init__.py
└── lib/                 # Utilities
    ├── config.py        # Configuration management
    ├── logging.py       # Structured logging setup
    ├── debug.py         # Debug utilities and metrics
    ├── db_utils.py      # Database utilities
    └── __init__.py

tests/
├── contract/           # Contract tests for CLI interfaces
├── integration/        # Integration tests for component interaction
└── __pycache__/        # Python cache files
```

## Data Schema

### Stock Information Table (`stock_name_code`)
- `code` (VARCHAR, PRIMARY KEY): Stock code (e.g., "000001")
- `name` (VARCHAR): Stock name (e.g., "平安银行")
- `metadata` (JSON): Additional metadata

### Historical Data Table (`stock_historical_data`)
- `date` (DATE): Trading date
- `stock_code` (VARCHAR): Stock code
- `open_price` (DECIMAL): Opening price
- `close_price` (DECIMAL): Closing price
- `high_price` (DECIMAL): Highest price
- `low_price` (DECIMAL): Lowest price
- `volume` (BIGINT): Trading volume
- `turnover` (DECIMAL): Trading amount
- `amplitude` (DECIMAL): Price amplitude (%)
- `price_change_rate` (DECIMAL): Price change rate (%)
- `price_change` (DECIMAL): Price change amount
- `turnover_rate` (DECIMAL): Turnover rate (%)

## Troubleshooting

### Database Connection Issues
- **Problem**: Database file cannot be created
- **Solution**: Ensure write permissions to the target directory
- **Check**: Run `stocklib init-db --db-path /path/to/test.db` with a simple path first

### API Fetching Problems
- **Problem**: Stock data fetch fails with SSL errors
- **Solution**: The library handles SSL issues automatically and falls back to sample data
- **Check**: Use `--validate-only` flag to test API connectivity without database storage

### Import Errors
- **Problem**: `ModuleNotFoundError` when running commands
- **Solution**: Ensure virtual environment is activated and package is installed
- **Check**: Run `pip install -e .` to reinstall the package

### Virtual Environment Issues
- **Problem**: Virtual environment not working
- **Solution**: Recreate with `python -m venv "D:\venvs\stock"` (use absolute path)
- **Check**: Verify Python version with `python --version` (requires 3.8+)

### Performance Issues
- **Problem**: Operations are slow
- **Solution**: Use `--debug` flag to see performance metrics and identify bottlenecks
- **Example**: `stocklib --debug sync-historical --default-db --stock-codes "000001"`

### Historical Data Sync Issues
- **Problem**: Sync fails for specific stocks
- **Solution**: Check debug logs for API errors, try individual stock sync
- **Check**: `stocklib --debug sync-historical --default-db --stock-codes "STOCK_CODE"`

### Test Failures
- **Problem**: Tests fail due to existing database
- **Solution**: Remove existing database files or use different paths for testing
- **Check**: Run tests with `pytest --tb=short` for detailed error information

## License

MIT License
