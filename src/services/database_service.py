"""Database service for initialization and management."""

import os
import json
from typing import Optional, List
from models.database import DatabaseConnection
from models.stock import Stock
from lib.config import Config
from lib.logging import get_logger
from lib.debug import timed_operation


logger = get_logger(__name__)


class DatabaseService:
    """Service for database initialization and management."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database service.

        Args:
            db_path: Path to database file, uses default if None
        """
        self.db_path = Config.get_database_path(db_path)
        self.db_connection = DatabaseConnection(self.db_path)

    @timed_operation("database_initialization")
    def initialize_database(self) -> bool:
        """Initialize the database and create basic schema.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Connect to database (keeps connection open)
            conn = self.db_connection.connect()

            # Create basic stock_name_code table if it doesn't exist
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stock_name_code (
                    code VARCHAR PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    metadata JSON
                )
            """)

            # Create historical data table if it doesn't exist
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stock_historical_data (
                    date DATE NOT NULL,
                    stock_code VARCHAR NOT NULL,
                    open_price DECIMAL(12,2),
                    close_price DECIMAL(12,2),
                    high_price DECIMAL(12,2),
                    low_price DECIMAL(12,2),
                    volume BIGINT,
                    turnover DECIMAL(18,2),
                    amplitude DECIMAL(8,2),
                    price_change_rate DECIMAL(8,2),
                    price_change DECIMAL(12,2),
                    turnover_rate DECIMAL(8,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (date, stock_code)
                )
            """)

            # Create indexes for better query performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_stock_historical_data_code ON stock_historical_data(stock_code)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_stock_historical_data_date ON stock_historical_data(date)")

            logger.info(f"Database initialized successfully at {self.db_path}")
            return True

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False

    @timed_operation("stock_insertion")
    def insert_stocks(self, stocks: List[Stock]) -> int:
        """Insert or update stocks in database.

        Args:
            stocks: List of Stock objects to insert

        Returns:
            Number of stocks successfully inserted
        """
        if not stocks:
            logger.warning("No stocks to insert")
            return 0

        conn = self.db_connection.connect()
        inserted = 0

        for stock in stocks:
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO stock_name_code (code, name, metadata) VALUES (?, ?, ?)",
                    (stock.code, stock.name, json.dumps(stock.metadata) if stock.metadata else None)
                )
                inserted += 1
            except Exception as e:
                logger.error(f"Failed to insert stock {stock.code}: {e}")

        logger.info(f"Successfully inserted {inserted} out of {len(stocks)} stocks")
        return inserted

    @timed_operation("stock_retrieval")
    def get_all_stocks(self) -> List[Stock]:
        """Retrieve all stocks from database.

        Returns:
            List of Stock objects
        """
        conn = self.db_connection.connect()
        result = conn.execute("SELECT code, name, metadata FROM stock_name_code ORDER BY code")

        stocks = []
        for row in result.fetchall():
            metadata = json.loads(row[2]) if row[2] else None
            stock = Stock(code=row[0], name=row[1], metadata=metadata)
            stocks.append(stock)

        logger.info(f"Retrieved {len(stocks)} stocks from database")
        return stocks

    def list_tables(self) -> List[str]:
        """List all tables in the database.

        Returns:
            List of table names
        """
        conn = self.db_connection.connect()
        result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")

        tables = [row[0] for row in result.fetchall()]
        logger.info(f"Found {len(tables)} tables in database")
        return tables

    def database_exists(self) -> bool:
        """Check if database file exists.

        Returns:
            True if database file exists, False otherwise
        """
        return os.path.exists(self.db_path)

    def get_connection(self) -> DatabaseConnection:
        """Get database connection instance.

        Returns:
            DatabaseConnection instance
        """
        return self.db_connection