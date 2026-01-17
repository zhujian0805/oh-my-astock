"""Database connection model."""

import duckdb
from typing import Optional
from lib.config import Config
from lib.logging import get_logger


logger = get_logger(__name__)


class DatabaseConnection:
    """Model for managing DuckDB database connections."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection.

        Args:
            db_path: Path to database file, uses default if None
        """
        self.db_path = Config.get_database_path(db_path)
        self._connection: Optional[duckdb.DuckDBPyConnection] = None
        logger.debug(f"DatabaseConnection initialized for path: {self.db_path}")

    def connect(self) -> duckdb.DuckDBPyConnection:
        """Establish database connection.

        Returns:
            DuckDB connection object
        """
        if self._connection is None:
            Config.ensure_path_exists(self.db_path)
            self._connection = duckdb.connect(str(self.db_path))

            # Configure performance settings
            logger.debug("Configuring DuckDB performance settings")
            threads = Config.get_threads()
            memory_limit = Config.get_memory_limit()

            self._connection.execute(f"SET threads = {threads}")
            self._connection.execute(f"SET memory_limit = '{memory_limit}'")

            # Additional performance settings
            self._connection.execute("SET enable_progress_bar = false")  # Reduce output noise
            self._connection.execute("SET enable_object_cache = true")   # Cache frequently used objects
            self._connection.execute("SET preserve_insertion_order = false")  # Better performance for bulk inserts

            logger.debug(f"DuckDB performance settings configured: threads={threads}, memory_limit={memory_limit}, progress_bar=disabled, object_cache=enabled")

            logger.info(f"Connected to database at {self.db_path}")
        return self._connection

    def disconnect(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    def is_connected(self) -> bool:
        """Check if connection is active.

        Returns:
            True if connected, False otherwise
        """
        return self._connection is not None

    def __enter__(self):
        """Context manager entry."""
        return self.connect()

    def execute(self, query: str, params: tuple = ()) -> duckdb.DuckDBPyRelation:
        """Execute a SQL query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Query result relation
        """
        if not self._connection:
            raise RuntimeError("Database connection not established")
        return self._connection.execute(query, params)