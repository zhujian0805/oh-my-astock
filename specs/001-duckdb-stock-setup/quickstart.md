# Quick Start: DuckDB Stock Setup

## Overview

This guide helps you get started with the DuckDB Stock Setup library for fetching and storing Chinese stock information.

## Prerequisites

- Python 3.11+
- Virtual environment at `D:\venvs\stock` (create manually)
- pip for package installation

## Installation

```bash
# Activate virtual environment
D:\venvs\stock\Scripts\activate

# Install the package
pip install -e .
```

## Basic Usage

### 1. Initialize Database

```bash
# Initialize with default path (d:\duckdb\stock.duckdb)
stocklib init-db --default

# Initialize with custom path
stocklib init-db --db-path "C:\mydata\stocks.db"
```

### 2. Fetch Stock Data

```bash
# Fetch all A-share stock information and store in database
stocklib fetch-stocks --default-db

# Fetch and validate without storing
stocklib fetch-stocks --default-db --validate-only
```

### 3. Query Stock Data

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

## Python API Usage

```python
from src.services.database_service import DatabaseService
from src.services.api_service import ApiService

# Initialize database
db_service = DatabaseService()
db_service.initialize_database()

# Fetch stocks
api_service = ApiService()
stocks = api_service.fetch_stock_info()

# Store stocks
db_service.insert_stocks(stocks)

# Query stocks
all_stocks = db_service.get_all_stocks()
```

## Configuration

### Default Database Path
- Default: `d:\duckdb\stock.duckdb`
- Can be overridden with `--db-path` parameter

### Virtual Environment
- Required: `D:\venvs\stock`
- Manual setup and activation needed

### Debug Features
- Enable with `--log-level DEBUG`
- Supports ERROR, WARNING, INFO, DEBUG levels

## Troubleshooting

### Database Connection Issues
- Ensure write permissions to database directory
- Check path validity

### API Failures
- SSL certificate issues are handled automatically
- Falls back to sample data if API unavailable
- Check network connectivity

### Virtual Environment Issues
- Ensure virtual environment is activated
- Install dependencies within activated environment

### Import Errors
- Confirm Python 3.11+ installation
- Install all dependencies in virtual environment

## Sample Output

### Database Initialization
```
Database initialized successfully at d:\duckdb\stock.duckdb
```

### Stock Listing (JSON)
```json
[
  {
    "code": "000001",
    "name": "平安银行",
    "metadata": {}
  }
]
```

## Next Steps

- Review data models in `data-model.md`
- Check CLI contracts in `contracts/`
- Run comprehensive tests
- Extend with additional stock analysis features</content>
<parameter name="file_path">specs/001-duckdb-stock-setup/quickstart.md