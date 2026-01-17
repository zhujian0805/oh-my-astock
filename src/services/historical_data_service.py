"""Historical data service for fetching and managing stock historical data."""

import akshare as ak
import pandas as pd
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from models.database import DatabaseConnection
from lib.config import Config
from lib.logging import get_logger
from lib.debug import debug_metrics, timed_operation, log_data_validation


logger = get_logger(__name__)


class HistoricalDataService:
    """Service for managing stock historical data."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize historical data service.

        Args:
            db_path: Path to database file, uses default if None
        """
        self.db_path = Config.get_database_path(db_path)
        self.db_connection = DatabaseConnection(self.db_path)
        self._configure_ssl()

    def _configure_ssl(self):
        """Configure SSL settings to handle certificate issues."""
        import urllib3
        import warnings
        import ssl
        import os
        import requests

        # Disable SSL warnings globally
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')

        # Set environment variables to disable SSL verification
        ssl_env_vars = ['REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE', 'SSL_CERT_FILE']
        for var in ssl_env_vars:
            os.environ[var] = ''

        # Try to set unverified SSL context
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
        except Exception as e:
            logger.debug(f"Could not set unverified SSL context: {e}")

        # Monkey patch libraries to disable SSL verification
        self._patch_urllib3()
        self._patch_requests()

    def _patch_urllib3(self):
        """Monkey patch urllib3 to disable SSL verification."""
        try:
            import urllib3
            original_init = urllib3.PoolManager.__init__

            def patched_init(self, *args, **kwargs):
                kwargs['cert_reqs'] = 'CERT_NONE'
                kwargs.pop('assert_hostname', None)
                return original_init(self, *args, **kwargs)

            urllib3.PoolManager.__init__ = patched_init
            logger.debug("Successfully patched urllib3 PoolManager")
        except Exception as e:
            logger.debug(f"Could not patch urllib3: {e}")

    def _patch_requests(self):
        """Monkey patch requests to disable SSL verification."""
        try:
            import requests
            original_request = requests.Session.request

            def patched_request(self, method, url, **kwargs):
                kwargs['verify'] = False
                return original_request(self, method, url, **kwargs)

            requests.Session.request = patched_request
            logger.debug("Successfully patched requests library")
        except Exception as e:
            logger.debug(f"Could not patch requests: {e}")

    @timed_operation("historical_data_table_creation")
    def create_historical_data_table(self) -> bool:
        """Create the stock_historical_data table if it doesn't exist.

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.db_connection.connect()

            # Create historical data table
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

            logger.info("Successfully created stock_historical_data table and indexes")
            return True

        except Exception as e:
            logger.error(f"Failed to create historical data table: {e}")
            return False

    @timed_operation("historical_data_fetch")
    def fetch_historical_data(self, stock_code: str, start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """Fetch historical data for a specific stock.

        Args:
            stock_code: Stock code to fetch data for
            start_date: Start date in YYYYMMDD format (optional)
            end_date: End date in YYYYMMDD format (optional)

        Returns:
            DataFrame with historical data or None if failed
        """
        try:
            logger.info(f"Fetching historical data for {stock_code} from {start_date} to {end_date}")

            # Use akshare to fetch historical data
            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period="daily",
                start_date=start_date or "19700101",
                end_date=end_date or "21000101",
                adjust=""
            )

            if df is not None and not df.empty:
                # Rename columns to match our schema
                column_mapping = {
                    '日期': 'date',
                    '开盘': 'open_price',
                    '收盘': 'close_price',
                    '最高': 'high_price',
                    '最低': 'low_price',
                    '成交量': 'volume',
                    '成交额': 'turnover',
                    '振幅': 'amplitude',
                    '涨跌幅': 'price_change_rate',
                    '涨跌额': 'price_change',
                    '换手率': 'turnover_rate'
                }

                df = df.rename(columns=column_mapping)

                # Ensure date column is datetime
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])

                logger.info(f"Successfully fetched {len(df)} records for {stock_code}")
                return df
            else:
                logger.warning(f"No historical data found for {stock_code}")
                return None

        except Exception as e:
            logger.error(f"Failed to fetch historical data for {stock_code}: {e}")
            return None

    def _convert_row_to_values(self, stock_code: str, row) -> tuple:
        """Convert a DataFrame row to database values tuple.

        Args:
            stock_code: Stock code for the row
            row: DataFrame row to convert

        Returns:
            Tuple of values for database insertion
        """
        def safe_float(value, default=0.0):
            return float(value) if pd.notna(value) else default

        def safe_int(value, default=0):
            return int(value) if pd.notna(value) else default

        return (
            row['date'].date() if hasattr(row['date'], 'date') else row['date'],
            stock_code,
            safe_float(row.get('open_price')),
            safe_float(row.get('close_price')),
            safe_float(row.get('high_price')),
            safe_float(row.get('low_price')),
            safe_int(row.get('volume')),
            safe_float(row.get('turnover')),
            safe_float(row.get('amplitude')),
            safe_float(row.get('price_change_rate')),
            safe_float(row.get('price_change')),
            safe_float(row.get('turnover_rate')),
            datetime.now(),
            datetime.now()
        )

    @timed_operation("historical_data_storage")
    def store_historical_data(self, stock_code: str, data: pd.DataFrame) -> int:
        """Store historical data in the database.

        Args:
            stock_code: Stock code
            data: DataFrame with historical data

        Returns:
            Number of records stored
        """
        if data is None or data.empty:
            logger.warning(f"No data to store for {stock_code}")
            return 0

        try:
            conn = self.db_connection.connect()
            stored_count = 0

            for _, row in data.iterrows():
                try:
                    values = self._convert_row_to_values(stock_code, row)

                    # Insert or update data
                    conn.execute("""
                        INSERT OR REPLACE INTO stock_historical_data
                        (date, stock_code, open_price, close_price, high_price, low_price,
                         volume, turnover, amplitude, price_change_rate, price_change, turnover_rate,
                         created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, values)

                    stored_count += 1

                except Exception as e:
                    logger.error(f"Failed to store row for {stock_code}: {e}")
                    continue

            logger.info(f"Successfully stored {stored_count} historical records for {stock_code}")
            return stored_count

        except Exception as e:
            logger.error(f"Failed to store historical data for {stock_code}: {e}")
            return 0

    @timed_operation("historical_data_fetch_and_store")
    def fetch_and_store_historical_data(self, stock_code: str, start_date: Optional[str] = None,
                                       end_date: Optional[str] = None) -> int:
        """Fetch and store historical data for a stock.

        Args:
            stock_code: Stock code to process
            start_date: Start date in YYYYMMDD format (optional)
            end_date: End date in YYYYMMDD format (optional)

        Returns:
            Number of records stored
        """
        logger.info(f"Fetching and storing historical data for {stock_code}")

        # Fetch the data
        data = self.fetch_historical_data(stock_code, start_date, end_date)
        if data is None:
            return 0

        # Store the data
        return self.store_historical_data(stock_code, data)

    @timed_operation("historical_data_retrieval")
    def get_historical_data(self, stock_code: str, start_date: Optional[str] = None,
                          end_date: Optional[str] = None, limit: Optional[int] = None) -> Optional[pd.DataFrame]:
        """Retrieve historical data from database.

        Args:
            stock_code: Stock code to retrieve data for
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            limit: Maximum number of records to return (optional)

        Returns:
            DataFrame with historical data or None if no data found
        """
        try:
            conn = self.db_connection.connect()

            # Build query
            query = "SELECT * FROM stock_historical_data WHERE stock_code = ?"
            params = [stock_code]

            if start_date:
                query += " AND date >= ?"
                params.append(start_date)

            if end_date:
                query += " AND date <= ?"
                params.append(end_date)

            query += " ORDER BY date DESC"

            if limit:
                query += f" LIMIT {limit}"

            result = conn.execute(query, params)
            rows = result.fetchall()

            if not rows:
                logger.info(f"No historical data found for {stock_code}")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=[desc[0] for desc in result.description])

            logger.info(f"Retrieved {len(df)} historical records for {stock_code}")
            return df

        except Exception as e:
            logger.error(f"Failed to retrieve historical data for {stock_code}: {e}")
            return None

    @timed_operation("historical_data_bulk_fetch_store")
    def fetch_and_store_multiple_stocks(self, stock_codes: List[str],
                                       start_date: Optional[str] = None,
                                       end_date: Optional[str] = None) -> Dict[str, int]:
        """Fetch and store historical data for multiple stocks.

        Args:
            stock_codes: List of stock codes to process
            start_date: Start date in YYYYMMDD format (optional)
            end_date: End date in YYYYMMDD format (optional)

        Returns:
            Dictionary mapping stock codes to number of records stored
        """
        results = {}

        for stock_code in stock_codes:
            try:
                logger.info(f"Processing historical data for {stock_code}")
                count = self.fetch_and_store_historical_data(stock_code, start_date, end_date)
                results[stock_code] = count
            except Exception as e:
                logger.error(f"Failed to process {stock_code}: {e}")
                results[stock_code] = 0

        successful = sum(1 for count in results.values() if count > 0)
        total_records = sum(results.values())

        logger.info(f"Processed {len(stock_codes)} stocks, {successful} successful, {total_records} total records stored")
        return results

    def get_latest_date_for_stock(self, stock_code: str) -> Optional[str]:
        """Get the latest date for which we have data for a stock.

        Args:
            stock_code: Stock code

        Returns:
            Latest date as string in YYYY-MM-DD format, or None if no data
        """
        try:
            conn = self.db_connection.connect()
            result = conn.execute(
                "SELECT MAX(date) FROM stock_historical_data WHERE stock_code = ?",
                [stock_code]
            )
            row = result.fetchone()

            if row and row[0]:
                return row[0].strftime('%Y-%m-%d')
            return None

        except Exception as e:
            logger.error(f"Failed to get latest date for {stock_code}: {e}")
            return None

    def check_data_freshness(self, stock_code: str) -> Tuple[bool, Optional[str]]:
        """Check if historical data for a stock is up-to-date.

        Args:
            stock_code: Stock code

        Returns:
            Tuple of (is_fresh, missing_start_date)
        """
        latest_date = self.get_latest_date_for_stock(stock_code)

        if not latest_date:
            # No data at all
            return False, (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')

        # Check if we have data for the last business day
        today = datetime.now().date()
        last_business_day = today

        # Adjust for weekends (simple logic)
        if today.weekday() >= 5:  # Saturday = 5, Sunday = 6
            days_to_subtract = today.weekday() - 4  # Go back to Friday
            last_business_day = today - timedelta(days=days_to_subtract)

        latest_date_obj = datetime.strptime(latest_date, '%Y-%m-%d').date()

        if latest_date_obj >= last_business_day:
            return True, None
        else:
            # Need to fetch from day after latest date
            next_date = latest_date_obj + timedelta(days=1)
            return False, next_date.strftime('%Y-%m-%d')

    @timed_operation("historical_data_update")
    def update_historical_data(self, stock_code: str) -> int:
        """Update historical data for a stock if it's not fresh.

        Args:
            stock_code: Stock code to update

        Returns:
            Number of new records added
        """
        is_fresh, start_date = self.check_data_freshness(stock_code)

        if is_fresh:
            logger.info(f"Historical data for {stock_code} is already up-to-date")
            return 0

        logger.info(f"Updating historical data for {stock_code} from {start_date}")
        return self.fetch_and_store_historical_data(stock_code, start_date)

    def get_connection(self) -> DatabaseConnection:
        """Get database connection instance.

        Returns:
            DatabaseConnection instance
        """
        return self.db_connection