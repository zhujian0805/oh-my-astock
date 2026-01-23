"""Configuration utilities."""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration management for the application."""

    @staticmethod
    def get_database_path(db_path: Optional[str] = None) -> Path:
        """Get database path, using default if none provided.

        Priority order:
        1. Custom path provided via db_path parameter
        2. Environment variable ASTOCK_DB_PATH
        3. Default: ~/data/stock.duckdb

        Args:
            db_path: Custom database path

        Returns:
            Path to database file
        """
        if db_path:
            return Path(db_path)

        # Check environment variable first
        env_path = os.getenv("ASTOCK_DB_PATH")
        if env_path:
            return Path(env_path)

        # Default path to ~/data/stock.duckdb (all platforms)
        return Path.home() / "data" / "stock.duckdb"

    @staticmethod
    def ensure_path_exists(db_path: str) -> None:
        """Ensure the directory for the database path exists.

        Args:
            db_path: Database file path
        """
        path = Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_threads() -> int:
        """Get number of threads for DuckDB.

        Returns:
            Number of threads
        """
        return int(os.getenv("DUCKDB_THREADS", "2"))

    @staticmethod
    def get_memory_limit() -> str:
        """Get memory limit for DuckDB.

        Returns:
            Memory limit string
        """
        return os.getenv("DUCKDB_MEMORY_LIMIT", "4GB")

    @staticmethod
    def get_bulk_insert_chunk_size() -> int:
        """Get chunk size for bulk inserts.

        Returns:
            Number of records per chunk
        """
        return int(os.getenv("BULK_INSERT_CHUNK_SIZE", "1000"))
