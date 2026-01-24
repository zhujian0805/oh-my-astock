"""
DuckDB database service
Direct in-process database access for maximum performance
"""

import duckdb
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from .config import settings

logger = logging.getLogger(__name__)


class DatabaseService:
    """DuckDB database service"""

    def __init__(self):
        self.db_path = Path(__file__).parent.parent / settings.database_path
        self.connection: Optional[duckdb.DuckDBPyConnection] = None
        self.is_connected = False

    async def connect(self) -> None:
        """Initialize database connection"""
        if self.is_connected:
            return

        try:
            logger.info(f"Connecting to DuckDB at: {self.db_path}")

            # Connect to DuckDB
            self.connection = duckdb.connect(str(self.db_path))

            # Test connection
            result = self.connection.execute("SELECT 1 as test").fetchall()
            if not result:
                raise Exception("Connection test failed")

            self.is_connected = True
            logger.info("DuckDB connection established successfully")

        except Exception as e:
            logger.error(f"Failed to connect to DuckDB: {e}")
            raise Exception(f"Database connection failed: {e}")

    async def query(self, sql: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results"""
        try:
            if not self.is_connected:
                await self.connect()

            logger.debug(f"Executing query: {sql}", extra={"params": params})

            if params:
                result = self.connection.execute(sql, params).fetchall()
            else:
                result = self.connection.execute(sql).fetchall()

            # Convert to list of dicts
            if result:
                # Get column names
                columns = [desc[0] for desc in self.connection.description]
                rows = [dict(zip(columns, row)) for row in result]
            else:
                rows = []

            logger.debug(f"Query returned {len(rows)} rows")
            return rows

        except Exception as e:
            logger.error(f"Query execution failed: {sql}", extra={"error": str(e), "params": params})
            raise e

    async def is_healthy(self) -> bool:
        """Check if database is accessible"""
        try:
            if not self.is_connected:
                await self.connect()

            result = self.connection.execute("SELECT 1 as health_check").fetchall()
            return len(result) > 0
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    async def close(self) -> None:
        """Close database connection"""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None

            self.is_connected = False
            logger.info("DuckDB connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection info for debugging"""
        return {
            "is_connected": self.is_connected,
            "db_path": str(self.db_path),
            "has_connection": self.connection is not None
        }


# Singleton instance
db_service = DatabaseService()