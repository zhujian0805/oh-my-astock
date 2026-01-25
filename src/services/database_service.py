"""Database service for initialization and management."""

import os
import json
from typing import Optional, List, Dict, Any
from pathlib import Path
from models.database import DatabaseConnection
from models.stock import Stock
from models.stock_info import StockInfo
from lib.config import Config
from lib.logging import get_logger
from lib.debug import timed_operation
from lib.migrations.migration_manager import MigrationManager


logger = get_logger(__name__)


class DatabaseService:
    """Service for database initialization and management."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database service.

        Args:
            db_path: Path to database file, uses default if None
        """
        path_obj = Config.get_database_path(db_path)
        self.db_path = path_obj
        self.db_connection = DatabaseConnection(str(path_obj))
        self.migration_manager = MigrationManager(str(path_obj), "src/lib/migrations")

    @timed_operation("stock_name_code_table_creation")
    def create_stock_name_code_table(self) -> bool:
        """Create the stock_name_code table if it doesn't exist.

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.db_connection.connect()

            # Create stock_name_code table if it doesn't exist
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stock_name_code (
                    code VARCHAR PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    metadata JSON
                )
            """)

            logger.info("Successfully created stock_name_code table")
            return True

        except Exception as e:
            logger.error(f"Failed to create stock_name_code table: {e}")
            return False

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
            if not self.create_stock_name_code_table():
                return False

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

    def run_migrations(self, dry_run: bool = False, target_version: Optional[int] = None) -> bool:
        """Run database migrations.

        Args:
            dry_run: If True, show what would be executed without running
            target_version: Target version to migrate to (None = latest)

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.migration_manager as mm:
                return mm.migrate(target_version=target_version, dry_run=dry_run)
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False

    def get_migration_status(self) -> Dict[str, Any]:
        """Get migration status information.

        Returns:
            Dictionary with migration status details
        """
        try:
            with self.migration_manager as mm:
                return mm.get_migration_status()
        except Exception as e:
            logger.error(f"Failed to get migration status: {e}")
            return {
                'applied_count': 0,
                'pending_count': 0,
                'error': str(e)
            }

    def save_stock_info(self, stock_info: StockInfo) -> bool:
        """Save or update stock information in database.

        Args:
            stock_info: StockInfo object to save

        Returns:
            True if successful, False otherwise
        """
        conn = self.db_connection.connect()

        try:
            # Convert StockInfo to database format
            data = {
                'stock_code': stock_info.stock_code,
                'company_name': stock_info.company_name,
                'industry': stock_info.industry,
                'sector': stock_info.sector,
                'market': stock_info.market,
                'listing_date': stock_info.listing_date.isoformat() if stock_info.listing_date else None,
                'total_shares': stock_info.total_shares,
                'circulating_shares': stock_info.circulating_shares,
                'market_cap': float(stock_info.market_cap) if stock_info.market_cap else None,
                'pe_ratio': float(stock_info.pe_ratio) if stock_info.pe_ratio else None,
                'pb_ratio': float(stock_info.pb_ratio) if stock_info.pb_ratio else None,
                'dividend_yield': float(stock_info.dividend_yield) if stock_info.dividend_yield else None,
                'roe': float(stock_info.roe) if stock_info.roe else None,
                'roa': float(stock_info.roa) if stock_info.roa else None,
                'net_profit': float(stock_info.net_profit) if stock_info.net_profit else None,
                'total_assets': float(stock_info.total_assets) if stock_info.total_assets else None,
                'total_liability': float(stock_info.total_liability) if stock_info.total_liability else None,
            }

            # Insert or replace stock info
            conn.execute("""
                INSERT OR REPLACE INTO stock_stock_info (
                    stock_code, company_name, industry, sector, market, listing_date,
                    total_shares, circulating_shares, market_cap, pe_ratio, pb_ratio,
                    dividend_yield, roe, roa, net_profit, total_assets, total_liability,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, list(data.values()))

            logger.info(f"Successfully saved stock info for {stock_info.stock_code}")
            return True

        except Exception as e:
            logger.error(f"Failed to save stock info for {stock_info.stock_code}: {e}")
            return False

    def get_stock_info(self, stock_code: str) -> Optional[StockInfo]:
        """Get stock information by stock code.

        Args:
            stock_code: Stock code to retrieve

        Returns:
            StockInfo object or None if not found
        """
        conn = self.db_connection.connect()

        try:
            result = conn.execute("""
                SELECT stock_code, company_name, industry, sector, market, listing_date,
                       total_shares, circulating_shares, market_cap, pe_ratio, pb_ratio,
                       dividend_yield, roe, roa, net_profit, total_assets, total_liability,
                       created_at, updated_at
                FROM stock_stock_info
                WHERE stock_code = ?
            """, [stock_code])

            row = result.fetchone()
            if not row:
                return None

            # Convert row to StockInfo
            from datetime import date
            return StockInfo(
                stock_code=row[0],
                company_name=row[1],
                industry=row[2],
                sector=row[3],
                market=row[4],
                listing_date=date.fromisoformat(row[5]) if row[5] else None,
                total_shares=row[6],
                circulating_shares=row[7],
                market_cap=row[8],
                pe_ratio=row[9],
                pb_ratio=row[10],
                dividend_yield=row[11],
                roe=row[12],
                roa=row[13],
                net_profit=row[14],
                total_assets=row[15],
                total_liability=row[16],
                created_at=row[17],
                updated_at=row[18]
            )

        except Exception as e:
            logger.error(f"Failed to get stock info for {stock_code}: {e}")
            return None

    def insert_stocks(self, stocks: List[Stock]) -> int:
        """Insert or update stocks in database using batch operation.

        Args:
            stocks: List of Stock objects to insert

        Returns:
            Number of stocks successfully inserted
        """
        if not stocks:
            logger.warning("No stocks to insert")
            return 0

        conn = self.db_connection.connect()

        try:
            # Prepare all values for batch insertion
            values = [
                (stock.code, stock.name, json.dumps(stock.metadata) if stock.metadata else None)
                for stock in stocks
            ]

            # Use transaction + executemany for efficiency
            conn.execute("BEGIN TRANSACTION")
            conn.executemany(
                "INSERT OR REPLACE INTO stock_name_code (code, name, metadata) VALUES (?, ?, ?)",
                values
            )
            conn.execute("COMMIT")

            logger.info(f"Successfully batch inserted {len(values)} stocks")
            return len(values)

        except Exception as e:
            conn.execute("ROLLBACK")
            logger.error(f"Failed to batch insert stocks: {e}")
            return 0

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

    def get_stock_by_code(self, code: str) -> Optional[Stock]:
        """Get a single stock by code.

        Args:
            code: Stock code to search for

        Returns:
            Stock object if found, None otherwise
        """
        conn = self.db_connection.connect()
        result = conn.execute("SELECT code, name, metadata FROM stock_name_code WHERE code = ?", [code])
        row = result.fetchone()

        if row:
            metadata = json.loads(row[2]) if row[2] else None
            return Stock(code=row[0], name=row[1], metadata=metadata)
        return None

    def get_historical_data(self, code: str) -> List[dict]:
        """Get historical data for a stock.

        Args:
            code: Stock code to get historical data for

        Returns:
            List of historical data records as dictionaries
        """
        conn = self.db_connection.connect()
        result = conn.execute("""
            SELECT date, open_price, close_price, high_price, low_price, volume,
                   turnover, amplitude, price_change_rate, price_change, turnover_rate
            FROM stock_historical_data
            WHERE stock_code = ?
            ORDER BY date ASC
        """, [code])

        records = []
        for row in result.fetchall():
            record = {
                'date': row[0],
                'open_price': row[1],
                'close_price': row[2],
                'high_price': row[3],
                'low_price': row[4],
                'volume': row[5],
                'turnover': row[6],
                'amplitude': row[7],
                'price_change_rate': row[8],
                'price_change': row[9],
                'turnover_rate': row[10]
            }
            records.append(record)

        logger.info(f"Retrieved {len(records)} historical records for {code}")
        return records

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