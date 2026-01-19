"""Configuration utilities."""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration management for the application."""

    @staticmethod
    def get_database_path(db_path: Optional[str] = None) -> Path:
        """Get database path, using default if none provided.

        Args:
            db_path: Custom database path

        Returns:
            Path to database file
        """
        if db_path:
            return Path(db_path)

        # Default database path
        default_path = os.getenv("ASTOCK_DB_PATH", "d:\\duckdb\\stock.duckdb")
        return Path(default_path)

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
        return int(os.getenv("DUCKDB_THREADS", "4"))

    @staticmethod
    def get_memory_limit() -> str:
        """Get memory limit for DuckDB.

        Returns:
            Memory limit string
        """
        return os.getenv("DUCKDB_MEMORY_LIMIT", "2GB")