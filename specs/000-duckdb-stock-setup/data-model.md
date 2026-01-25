# Data Model: DuckDB Stock Setup

## Overview
This feature implements data models for stock information retrieved from the akshare API. All models are Python classes with type hints and validation.

## Entities

### Stock
Represents a single stock with basic identification information.

**Fields**:
- `code` (str): Stock code, primary key, required, unique identifier
- `name` (str): Stock name, required, human-readable label
- `metadata` (dict, optional): Additional stock information, default empty dict

**Validation Rules**:
- `code`: Non-empty string, alphanumeric with possible special characters
- `name`: Non-empty string
- `metadata`: Dictionary or None

**Relationships**:
- Belongs to StockList (many-to-one)

### StockList
Collection of Stock entities with bulk operations.

**Fields**:
- `stocks` (List[Stock]): List of Stock instances
- `count` (int): Computed property returning len(stocks)

**Validation Rules**:
- `stocks`: List of valid Stock objects
- No duplicate codes allowed

**Methods**:
- `add_stock(stock: Stock)`: Add single stock with duplicate check
- `get_by_code(code: str) -> Stock`: Retrieve stock by code
- `to_dict() -> List[dict]`: Serialize to list of dictionaries
- `from_dataframe(df: pd.DataFrame) -> StockList`: Create from pandas DataFrame

### DatabaseConnection
Manages DuckDB database connection and operations.

**Fields**:
- `path` (str): Database file path
- `connection` (duckdb.DuckDBPyConnection): Active database connection

**Validation Rules**:
- `path`: Valid file path string
- `connection`: Valid DuckDB connection object

**Methods**:
- `connect()`: Establish database connection
- `disconnect()`: Close database connection
- `execute_query(query: str, params: dict = None) -> pd.DataFrame`: Execute SELECT query
- `execute_command(command: str, params: dict = None)`: Execute INSERT/UPDATE/DELETE
- `create_table()`: Initialize stocks table if not exists
- `insert_stocks(stock_list: StockList)`: Bulk insert stock data

## Database Schema

### stock_name_code Table
```sql
CREATE TABLE stock_name_code (
    code VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    metadata JSON
);
```

**Indexes**:
- Primary key on `code`
- Optional index on `name` for search performance

## State Transitions
- Database: Uninitialized → Connected → Operational → Disconnected
- StockList: Empty → Populated → Validated (no duplicates)

## Data Flow
1. akshare API returns pandas DataFrame
2. DataFrame converted to StockList via `from_dataframe()`
3. StockList validated for duplicates and data integrity
4. DatabaseConnection inserts validated data into DuckDB table