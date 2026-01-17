# CLI Contracts: DuckDB Stock Setup

## Command: init-db

**Purpose**: Initialize a new DuckDB database at specified path

**Usage**: `stocklib init-db [--db-path <path>] [--default]`

**Parameters**:
- `--db-path`: File system path for database (optional)
- `--default`: Use default path 'd:\duckdb\stock.duckdb'

**Output**: Success message with database path

**Errors**: Path invalid, permissions error, database already exists

## Command: fetch-stocks

**Purpose**: Fetch stock data from akshare API and store in database

**Usage**: `stocklib fetch-stocks [--db-path <path>] [--default-db] [--validate-only]`

**Parameters**:
- `--db-path`: Database path (optional)
- `--default-db`: Use default database path
- `--validate-only`: Fetch and validate without storing

**Output**: Success message with count, or JSON array if validate-only

**Errors**: Network error, API failure, database connection error, SSL issues

## Command: list-stocks

**Purpose**: Query and display stocks from database

**Usage**: `stocklib list-stocks [--db-path <path>] [--default-db] [--limit <n>]`

**Parameters**:
- `--db-path`: Database path (optional)
- `--default-db`: Use default database path
- `--limit`: Maximum number of stocks to return (optional)

**Output**: JSON array of stock objects

**Errors**: Database connection error, query failure

## Command: list-tables

**Purpose**: Display all tables in the DuckDB database

**Usage**: `stocklib list-tables [--db-path <path>] [--default-db]`

**Parameters**:
- `--db-path`: Database path (optional)
- `--default-db`: Use default database path

**Output**: JSON array of table names

**Errors**: Database connection error, query failure