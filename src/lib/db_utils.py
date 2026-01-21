"""Database utilities for efficient batch operations and transaction management.

Provides helpers for batch inserts, transaction context managers, and
optimized queries for DuckDB.
"""

from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Generator
import duckdb


class DatabaseTransactionManager:
    """Context manager for database transactions."""

    def __init__(self, connection: duckdb.DuckDBPyConnection):
        """Initialize transaction manager.

        Args:
            connection: DuckDB connection
        """
        self.connection = connection
        self.in_transaction = False

    def __enter__(self):
        """Start transaction."""
        self.connection.execute("BEGIN TRANSACTION")
        self.in_transaction = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Commit or rollback transaction."""
        if self.in_transaction:
            if exc_type is not None:
                self.connection.execute("ROLLBACK")
            else:
                self.connection.execute("COMMIT")
            self.in_transaction = False

        return False


@contextmanager
def transaction(connection: duckdb.DuckDBPyConnection) -> Generator:
    """Context manager for database transactions.

    Usage:
        with transaction(conn):
            conn.execute("INSERT INTO table VALUES ...")
            conn.execute("UPDATE table SET ...")
    """
    manager = DatabaseTransactionManager(connection)
    try:
        with manager:
            yield manager
    except Exception:
        raise


class BatchInsertBuilder:
    """Helper for building and executing batch inserts efficiently."""

    def __init__(self, connection: duckdb.DuckDBPyConnection, table: str):
        """Initialize batch insert builder.

        Args:
            connection: DuckDB connection
            table: Table name
        """
        self.connection = connection
        self.table = table
        self.rows: List[Dict[str, Any]] = []

    def add_row(self, **kwargs) -> 'BatchInsertBuilder':
        """Add a row to the batch.

        Args:
            **kwargs: Column-value pairs

        Returns:
            Self for method chaining
        """
        self.rows.append(kwargs)
        return self

    def add_rows(self, rows: List[Dict[str, Any]]) -> 'BatchInsertBuilder':
        """Add multiple rows to the batch.

        Args:
            rows: List of dictionaries with column-value pairs

        Returns:
            Self for method chaining
        """
        self.rows.extend(rows)
        return self

    def execute(self) -> int:
        """Execute the batch insert.

        Returns:
            Number of rows inserted
        """
        if not self.rows:
            return 0

        # Build INSERT statement with VALUES
        columns = self.rows[0].keys()
        columns_str = ', '.join(f'"{col}"' for col in columns)

        # Build VALUES clause
        values_parts = []
        for row in self.rows:
            values = []
            for col in columns:
                val = row.get(col)
                if val is None:
                    values.append('NULL')
                elif isinstance(val, str):
                    # Escape single quotes
                    escaped = val.replace("'", "''")
                    values.append(f"'{escaped}'")
                elif isinstance(val, bool):
                    values.append('TRUE' if val else 'FALSE')
                else:
                    values.append(str(val))
            values_parts.append(f"({', '.join(values)})")

        values_str = ', '.join(values_parts)

        # Execute batch insert
        query = f"INSERT INTO {self.table} ({columns_str}) VALUES {values_str}"
        self.connection.execute(query)

        return len(self.rows)

    def execute_or_replace(self) -> int:
        """Execute batch insert with OR REPLACE (conflict handling).

        Returns:
            Number of rows inserted/updated
        """
        if not self.rows:
            return 0

        # Build INSERT OR REPLACE statement
        columns = self.rows[0].keys()
        columns_str = ', '.join(f'"{col}"' for col in columns)

        # Build VALUES clause
        values_parts = []
        for row in self.rows:
            values = []
            for col in columns:
                val = row.get(col)
                if val is None:
                    values.append('NULL')
                elif isinstance(val, str):
                    escaped = val.replace("'", "''")
                    values.append(f"'{escaped}'")
                elif isinstance(val, bool):
                    values.append('TRUE' if val else 'FALSE')
                else:
                    values.append(str(val))
            values_parts.append(f"({', '.join(values)})")

        values_str = ', '.join(values_parts)

        # Execute batch insert or replace
        query = f"INSERT OR REPLACE INTO {self.table} ({columns_str}) VALUES {values_str}"
        self.connection.execute(query)

        return len(self.rows)

    def clear(self):
        """Clear accumulated rows."""
        self.rows.clear()
        return self


def batch_insert(
    connection: duckdb.DuckDBPyConnection,
    table: str,
    rows: List[Dict[str, Any]],
    batch_size: int = 1000,
) -> int:
    """Execute batch insert with automatic chunking for large datasets.

    Args:
        connection: DuckDB connection
        table: Table name
        rows: List of dictionaries with column-value pairs
        batch_size: Number of rows per batch

    Returns:
        Total number of rows inserted
    """
    total_inserted = 0

    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        builder = BatchInsertBuilder(connection, table)
        builder.add_rows(batch)
        total_inserted += builder.execute()

    return total_inserted


def batch_insert_or_replace(
    connection: duckdb.DuckDBPyConnection,
    table: str,
    rows: List[Dict[str, Any]],
    batch_size: int = 1000,
) -> int:
    """Execute batch insert or replace with automatic chunking.

    Args:
        connection: DuckDB connection
        table: Table name
        rows: List of dictionaries with column-value pairs
        batch_size: Number of rows per batch

    Returns:
        Total number of rows inserted/updated
    """
    total_inserted = 0

    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        builder = BatchInsertBuilder(connection, table)
        builder.add_rows(batch)
        total_inserted += builder.execute_or_replace()

    return total_inserted


def upsert_historical_data(
    connection: duckdb.DuckDBPyConnection,
    table: str,
    rows: List[Dict[str, Any]],
) -> int:
    """Efficient upsert for historical data (update or insert).

    DuckDB doesn't support UPSERT directly, so we:
    1. Delete existing records
    2. Insert all records (faster than one-by-one updates)

    Args:
        connection: DuckDB connection
        table: Table name
        rows: List of dictionaries with column-value pairs

    Returns:
        Number of rows inserted
    """
    if not rows:
        return 0

    # Extract unique (date, stock_code) pairs for deletion
    delete_conditions = set()
    for row in rows:
        if 'date' in row and 'stock_code' in row:
            delete_conditions.add((row['date'], row['stock_code']))

    # Delete existing records
    for date, stock_code in delete_conditions:
        query = (
            f"DELETE FROM {table} "
            f"WHERE date = '{date}' AND stock_code = '{stock_code}'"
        )
        connection.execute(query)

    # Insert all records
    return batch_insert(connection, table, rows)


def get_partition_stats(
    connection: duckdb.DuckDBPyConnection,
    table: str,
) -> Dict[str, Any]:
    """Get statistics about table partitions and size.

    Args:
        connection: DuckDB connection
        table: Table name

    Returns:
        Dictionary with table stats
    """
    result = connection.execute(
        f"SELECT COUNT(*) as row_count FROM {table}"
    ).fetchall()

    row_count = result[0][0] if result else 0

    return {
        'row_count': row_count,
        'table': table,
    }
