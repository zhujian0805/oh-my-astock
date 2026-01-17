# Oh My Astock

A modular Python library for managing stock data using DuckDB and akshare API.

## Features

- **Database Management**: Initialize and manage DuckDB databases for stock data
- **Stock Data Fetching**: Retrieve stock information from akshare API
- **Data Models**: Well-defined Python models for stock data with validation
- **CLI Interface**: Command-line tools for database operations
- **Modular Design**: Clean separation of concerns with reusable components

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Initialize Database

```bash
# Initialize with default path
stocklib init-db --default

# Or specify custom path
stocklib init-db --db-path /path/to/stocks.db
```

### 2. Fetch Stock Data

```bash
# Fetch and store stocks in database
stocklib fetch-stocks --default-db

# Just validate data without storing
stocklib fetch-stocks --validate-only
```

### 3. Query Stocks

```bash
# List all stocks
stocklib list-stocks --default-db

# List first 10 stocks
stocklib list-stocks --default-db --limit 10
```

### 4. Inspect Database

```bash
# See all tables in the database
stocklib list-tables --default-db
```

### 5. Debug Mode

```bash
# Enable debug logging and performance metrics
stocklib --debug init-db --default

# Debug fetch operation with timing
stocklib --debug fetch-stocks --validate-only
```

## API Usage

```python
from stocklib.services import DatabaseService, ApiService
from stocklib.models import Stock

# Initialize database
db = DatabaseService()
db.initialize_database()

# Fetch stocks from API
api = ApiService()
stocks = api.fetch_stock_info()

# Store in database
db.insert_stocks(stocks)

# Query stocks
all_stocks = db.get_all_stocks()
```

## Development

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Project Structure

```
src/
├── models/          # Data models (Stock, StockList, DatabaseConnection)
├── services/        # Business logic (DatabaseService, ApiService)
├── cli/            # Command-line interface
└── lib/            # Utilities (config, logging, db_utils)

tests/
├── contract/       # Contract tests for individual components
├── integration/    # Integration tests for component interaction
└── unit/           # Unit tests (if needed)
```

## Requirements

- Python 3.8+
- DuckDB
- akshare library
- click (for CLI)
- pytest (for testing)

## Virtual Environment Setup

Before using the library, set up a virtual environment:

```bash
# Create virtual environment
python -m venv "D:\venvs\stock"

# Activate (Windows)
D:\venvs\stock\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

See `VIRTUAL_ENV_SETUP.md` for detailed setup instructions.

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
- **Example**: `stocklib --debug fetch-stocks --validate-only`

### Test Failures
- **Problem**: Tests fail due to existing database
- **Solution**: Remove existing database files or use different paths for testing
- **Check**: Run tests with `pytest --tb=short` for detailed error information

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
├── models/          # Data models (Stock, StockList, DatabaseConnection)
├── services/        # Business logic (DatabaseService, ApiService)
├── cli/            # Command-line interface
└── lib/            # Utilities (config, logging, debug, db_utils)

tests/
├── contract/       # Contract tests for individual components
├── integration/    # Integration tests for component interaction
└── unit/           # Unit tests for utilities
```

## License

MIT License# oh-my-astock
