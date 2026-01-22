"""Historical data service for fetching and managing stock historical data."""

# Configure HTTP/SSL/tqdm BEFORE importing akshare
from lib.http_config import configure_all

configure_all()

# NOW import akshare after configuration
import akshare as ak
import pandas as pd
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
from models.database import DatabaseConnection
from lib.config import Config
from lib.logging import get_logger
from lib.debug import timed_operation


logger = get_logger(__name__)


class HistoricalDataService:
    """Service for managing stock historical data."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize historical data service.

        Args:
            db_path: Path to database file, uses default if None
        """
        self.db_path = str(Config.get_database_path(db_path))
        self.db_connection = DatabaseConnection(self.db_path)

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
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_stock_historical_data_code ON stock_historical_data(stock_code)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_stock_historical_data_date ON stock_historical_data(date)"
            )

            logger.info("Successfully created stock_historical_data table and indexes")
            return True

        except Exception as e:
            logger.error(f"Failed to create historical data table: {e}")
            return False

    @timed_operation("historical_data_fetch")
    def fetch_historical_data(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_retries: int = 5,
    ) -> Optional[pd.DataFrame]:
        """Fetch historical data for a specific stock.

        Args:
            stock_code: Stock code to fetch data for
            start_date: Start date in YYYYMMDD format (optional)
            end_date: End date in YYYYMMDD format (optional)
            max_retries: Maximum number of retry attempts for network/API failures

        Returns:
            DataFrame with historical data or None if failed
        """
        import time
        import ssl
        import requests
        from urllib3.exceptions import HTTPError

        # Define the APIs to try in order
        apis_to_try = [
            ("stock_zh_a_hist", ak.stock_zh_a_hist),
            # ('stock_zh_a_daily', ak.stock_zh_a_daily),  # This API seems broken in current akshare version
            ("stock_zh_a_hist_tx", ak.stock_zh_a_hist_tx),
        ]

        for attempt in range(max_retries + 1):
            df = None  # Initialize df for this attempt
            for api_name, api_function in apis_to_try:
                try:
                    logger.info(
                        f"Fetching historical data for {stock_code} using {api_name} from {start_date} to {end_date} (attempt {attempt + 1}/{max_retries + 1})"
                    )

                    # Call the API function
                    if api_name == "stock_zh_a_hist":
                        df = api_function(
                            symbol=stock_code,
                            period="daily",
                            start_date=start_date or "19700101",
                            end_date=end_date or "21000101",
                            adjust="",
                        )
                    elif api_name == "stock_zh_a_daily":
                        # stock_zh_a_daily takes symbol, start_date, end_date, adjust
                        df = api_function(
                            symbol=stock_code,
                            start_date=start_date or "19700101",
                            end_date=end_date or "21000101",
                            adjust="",
                        )
                    elif api_name == "stock_zh_a_hist_tx":
                        # stock_zh_a_hist_tx needs market prefix (sz/sh) and takes symbol, start_date, end_date, adjust
                        # Add market prefix if not present
                        if not stock_code.startswith(("sh", "sz", "SH", "SZ")):
                            # Determine market based on stock code
                            if stock_code.startswith("6") or stock_code.startswith("9"):
                                prefixed_symbol = f"sh{stock_code}"
                            else:
                                prefixed_symbol = f"sz{stock_code}"
                        else:
                            prefixed_symbol = stock_code.lower()

                        df = api_function(
                            symbol=prefixed_symbol,
                            start_date=start_date or "19700101",
                            end_date=end_date or "21000101",
                            adjust="",
                        )

                    if df is not None and not df.empty:
                        # Validate that we have some data to work with
                        logger.debug(f"Raw API response columns: {list(df.columns)}")
                        logger.debug(f"Raw API response shape: {df.shape}")
                        logger.debug(
                            f"First row sample: {df.iloc[0].to_dict() if len(df) > 0 else 'No rows'}"
                        )

                        # Rename columns to match our schema
                        if api_name == "stock_zh_a_hist_tx":
                            # stock_zh_a_hist_tx returns English column names
                            column_mapping = {
                                "date": "date",
                                "open": "open_price",
                                "close": "close_price",
                                "high": "high_price",
                                "low": "low_price",
                                "amount": "volume",  # Note: amount in stock_zh_a_hist_tx is actually volume
                                # turnover is not available in stock_zh_a_hist_tx
                            }
                        else:
                            # Default Chinese column names for other APIs
                            column_mapping = {
                                "日期": "date",
                                "开盘": "open_price",
                                "收盘": "close_price",
                                "最高": "high_price",
                                "最低": "low_price",
                                "成交量": "volume",
                                "成交额": "turnover",
                                "振幅": "amplitude",
                                "涨跌幅": "price_change_rate",
                                "涨跌额": "price_change",
                                "换手率": "turnover_rate",
                            }

                        # Only rename columns that exist in the DataFrame
                        existing_columns = [
                            col for col in column_mapping.keys() if col in df.columns
                        ]
                        if existing_columns:
                            df = df.rename(
                                columns={
                                    col: column_mapping[col] for col in existing_columns
                                }
                            )
                            logger.debug(f"Renamed columns: {existing_columns}")
                        else:
                            logger.warning(
                                f"No expected columns found in API response for {api_name}. Available columns: {list(df.columns)}"
                            )
                            continue

                        # Ensure date column is datetime if it exists
                        if "date" in df.columns:
                            try:
                                df["date"] = pd.to_datetime(df["date"])
                                logger.debug(
                                    f"Converted date column to datetime, {len(df)} rows"
                                )
                            except Exception as e:
                                logger.warning(
                                    f"Failed to convert date column to datetime: {e}"
                                )
                                # Try to drop rows with invalid dates
                                df = df.dropna(subset=["date"])
                                if df.empty:
                                    logger.warning(
                                        "No valid dates found after cleaning"
                                    )
                                    continue
                        else:
                            logger.warning(
                                f"No date column found after renaming for {api_name}"
                            )
                            continue

                        logger.info(
                            f"Successfully fetched {len(df)} records for {stock_code} using {api_name}"
                        )
                        return df
                    else:
                        logger.warning(
                            f"No historical data found for {stock_code} using {api_name}"
                        )
                        continue  # Try next API

                except (
                    ssl.SSLError,
                    requests.exceptions.SSLError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                    requests.exceptions.RequestException,
                    HTTPError,
                    ConnectionError,
                    TimeoutError,
                    OSError,
                ) as e:
                    if attempt < max_retries:
                        # Exponential backoff with jitter to avoid overwhelming the API
                        base_wait = 2.0
                        wait_time = base_wait * (2**attempt) + (
                            time.time() % 5
                        )  # Add jitter

                        logger.warning(
                            f"Network/API error for {stock_code} using {api_name} (attempt {attempt + 1}): {e}. Retrying in {wait_time:.1f}s..."
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(
                            f"Network/API error for {stock_code} using {api_name} after {max_retries + 1} attempts: {e}"
                        )
                        break  # Break to try next API

                except Exception as e:
                    # Add rate limiting detection
                    error_str = str(e).lower()
                    if any(
                        keyword in error_str
                        for keyword in [
                            "rate limit",
                            "too many requests",
                            "429",
                            "throttle",
                        ]
                    ):
                        if attempt < max_retries:
                            # Longer wait for rate limiting
                            wait_time = 60.0 * (attempt + 1)  # 60s, 120s, etc.
                            logger.warning(
                                f"Rate limit detected for {stock_code} using {api_name}. Waiting {wait_time:.1f}s before retry..."
                            )
                            time.sleep(wait_time)
                            continue
                        else:
                            logger.error(
                                f"Rate limit exceeded for {stock_code} using {api_name} after {max_retries + 1} attempts"
                            )
                            return None

                    logger.warning(
                        f"Failed to fetch historical data for {stock_code} using {api_name}: {e}"
                    )
                    # Continue to next API instead of failing completely
                    continue

            # If all APIs failed for this attempt, don't retry - just return None
            # No point retrying if the stock has no data available
            logger.warning(f"All APIs returned no data for {stock_code}")
            return None

        return None

    def _convert_row_to_values(self, stock_code: str, row: dict) -> tuple:
        """Convert a DataFrame row to database values tuple.

        Args:
            stock_code: Stock code for the row
            row: DataFrame row to convert

        Returns:
            Tuple of values for database insertion
        """

        def safe_float(value, default=0.0):
            """Safely convert value to float, handling various edge cases."""
            if pd.isna(value) or value is None:
                return default
            try:
                # Handle string values that might be special markers
                if isinstance(value, str):
                    value = value.strip()
                    if value == "" or value.lower() in [
                        "n/a",
                        "null",
                        "none",
                        "nan",
                        "i",
                    ]:
                        return default
                return float(value)
            except (ValueError, TypeError):
                logger.debug(
                    f"Could not convert '{value}' to float, using default {default}"
                )
                return default

        def safe_int(value, default=0):
            """Safely convert value to int, handling various edge cases."""
            if pd.isna(value) or value is None:
                return default
            try:
                # Handle string values that might be special markers
                if isinstance(value, str):
                    value = value.strip()
                    if value == "" or value.lower() in [
                        "n/a",
                        "null",
                        "none",
                        "nan",
                        "i",
                    ]:
                        return default
                return int(
                    float(value)
                )  # Convert through float first to handle '1.0' strings
            except (ValueError, TypeError):
                logger.debug(
                    f"Could not convert '{value}' to int, using default {default}"
                )
                return default

        # Handle date from dict (pandas timestamp or date object)
        date_val = row["date"]
        if hasattr(date_val, "date"):
            date_val = date_val.date()

        return (
            date_val,
            stock_code,
            safe_float(row.get("open_price")),
            safe_float(row.get("close_price")),
            safe_float(row.get("high_price")),
            safe_float(row.get("low_price")),
            safe_int(row.get("volume")),
            safe_float(row.get("turnover")),
            safe_float(row.get("amplitude")),
            safe_float(row.get("price_change_rate")),
            safe_float(row.get("price_change")),
            safe_float(row.get("turnover_rate")),
            datetime.now(),
            datetime.now(),
        )

    @timed_operation("historical_data_storage")
    def store_historical_data(self, stock_code: str, data: pd.DataFrame) -> int:
        """Store historical data in the database using batch insertion.

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

            # Convert DataFrame to dict records (10-100x faster than iterrows)
            logger.debug(f"Converting DataFrame with {len(data)} rows to dict records for {stock_code}")
            records = data.to_dict('records')
            logger.debug(f"Successfully converted {len(records)} records for {stock_code}")

            # Prepare all values for batch insertion
            logger.debug(f"Preparing batch values for {len(records)} records for {stock_code}")
            all_values = []
            for row in records:
                try:
                    values = self._convert_row_to_values(stock_code, row)
                    all_values.append(values)
                except Exception as e:
                    logger.error(f"Failed to prepare row for {stock_code}: {e}")
                    continue

            if not all_values:
                logger.warning(f"No valid data prepared for {stock_code}")
                return 0

            logger.debug(f"Prepared {len(all_values)} valid rows for batch insertion for {stock_code}")

            # Use transaction + executemany for efficient batch insertion
            query = """
                INSERT OR REPLACE INTO stock_historical_data
                (date, stock_code, open_price, close_price, high_price, low_price,
                 volume, turnover, amplitude, price_change_rate, price_change, turnover_rate,
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            logger.debug(f"Starting transaction for batch insertion of {len(all_values)} records for {stock_code}")
            conn.execute("BEGIN TRANSACTION")
            conn.executemany(query, all_values)
            conn.execute("COMMIT")
            logger.debug(f"Successfully committed transaction for {stock_code}")

            stored_count = len(all_values)

            logger.info(
                f"Successfully batch stored {stored_count} historical records for {stock_code}"
            )
            return stored_count

        except Exception as e:
            # Rollback transaction if connection exists
            try:
                conn.execute("ROLLBACK")
            except (NameError, AttributeError):
                pass  # Connection doesn't exist or isn't valid
            except Exception:
                pass  # Ignore other rollback errors
            logger.error(f"Failed to store historical data for {stock_code}: {e}")
            return 0

    @timed_operation("historical_data_fetch_and_store")
    def fetch_and_store_historical_data(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> int:
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
    def get_historical_data(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Optional[pd.DataFrame]:
        """Retrieve historical data from the single stock_historical_data table.

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

            # Query the single stock_historical_data table
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
            columns = [desc[0] for desc in result.description]
            df = pd.DataFrame(rows, columns=columns)

            logger.info(f"Retrieved {len(df)} historical records for {stock_code}")
            return df

        except Exception as e:
            logger.error(f"Failed to retrieve historical data for {stock_code}: {e}")
            return None

    @timed_operation("historical_data_bulk_fetch_store")
    def fetch_and_store_multiple_stocks(
        self,
        stock_codes: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, int]:
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
                count = self.fetch_and_store_historical_data(
                    stock_code, start_date, end_date
                )
                results[stock_code] = count
            except Exception as e:
                logger.error(f"Failed to process {stock_code}: {e}")
                results[stock_code] = 0

        successful = sum(1 for count in results.values() if count > 0)
        total_records = sum(results.values())

        logger.info(
            f"Processed {len(stock_codes)} stocks, {successful} successful, {total_records} total records stored"
        )
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
                [stock_code],
            )
            row = result.fetchone()

            if row and row[0]:
                return row[0].strftime("%Y-%m-%d")
            return None

        except Exception as e:
            logger.error(f"Failed to get latest date for {stock_code}: {e}")
            return None

    def get_stocks_with_historical_data(self) -> List[str]:
        """Get all stock codes that have historical data.

        Returns:
            List of stock codes that exist in the historical data table
        """
        try:
            conn = self.db_connection.connect()
            result = conn.execute(
                "SELECT DISTINCT stock_code FROM stock_historical_data ORDER BY stock_code"
            )
            rows = result.fetchall()

            stock_codes = [row[0] for row in rows]
            logger.info(f"Found {len(stock_codes)} stocks with historical data")
            return stock_codes

        except Exception as e:
            logger.error(f"Failed to get stocks with historical data: {e}")
            return []

    def refresh_stock_name_code(self, stock_codes: List[str]) -> int:
        """Refresh stock_name_code table with provided stock codes.

        Args:
            stock_codes: List of stock codes to update/insert

        Returns:
            Number of stocks updated/inserted
        """
        if not stock_codes:
            logger.warning("No stock codes provided to refresh")
            return 0

        try:
            conn = self.db_connection.connect()
            updated = 0

            for code in stock_codes:
                try:
                    # Insert or replace to refresh the entry
                    conn.execute(
                        "INSERT OR IGNORE INTO stock_name_code (code, name, metadata) VALUES (?, ?, ?)",
                        (
                            code,
                            "",
                            None,
                        ),  # Empty name and metadata for now - will be populated elsewhere
                    )
                    updated += 1
                except Exception as e:
                    logger.debug(f"Failed to update stock code {code}: {e}")
                    continue

            logger.info(
                f"Successfully refreshed {updated} stock codes in stock_name_code table"
            )
            return updated

        except Exception as e:
            logger.error(f"Failed to refresh stock_name_code table: {e}")
            return 0

    def get_missing_stocks(self, all_stock_codes: List[str]) -> List[str]:
        """Find stocks in stock_name_code that are missing from stock_historical_data.

        Args:
            all_stock_codes: List of all available stock codes from stock_name_code

        Returns:
            List of stock codes without historical data
        """
        try:
            existing_codes = set(self.get_stocks_with_historical_data())
            missing_codes = [
                code for code in all_stock_codes if code not in existing_codes
            ]
            logger.info(
                f"Found {len(missing_codes)} stocks missing from historical data"
            )
            return missing_codes

        except Exception as e:
            logger.error(f"Failed to get missing stocks: {e}")
            return []

    def get_stocks_missing_today_data(self, stock_codes: List[str]) -> List[str]:
        """Find stocks that don't have today's historical data.

        Args:
            stock_codes: List of stock codes to check

        Returns:
            List of stock codes missing today's data
        """
        try:
            conn = self.db_connection.connect()
            today = datetime.now().date()

            # Adjust for weekends (simple logic)
            if today.weekday() >= 5:  # Saturday = 5, Sunday = 6
                days_to_subtract = today.weekday() - 4  # Go back to Friday
                today = today - timedelta(days=days_to_subtract)

            stocks_missing_today = []

            for code in stock_codes:
                try:
                    result = conn.execute(
                        "SELECT COUNT(*) FROM stock_historical_data WHERE stock_code = ? AND date = ?",
                        [code, today],
                    )
                    row = result.fetchone()
                    count = row[0] if row else 0

                    if count == 0:
                        stocks_missing_today.append(code)
                except Exception as e:
                    logger.debug(f"Failed to check today's data for {code}: {e}")
                    stocks_missing_today.append(code)

            logger.info(
                f"Found {len(stocks_missing_today)} stocks missing today's data"
            )
            return stocks_missing_today

        except Exception as e:
            logger.error(f"Failed to get stocks missing today's data: {e}")
            return []

    def compute_fetching_list(self, all_stock_codes: List[str]) -> Dict[str, List[str]]:
        """Compute optimized fetching lists for different sync strategies.

        Args:
            all_stock_codes: List of all available stock codes from stock_name_code

        Returns:
            Dictionary with different categories of stocks to fetch:
            - 'missing_all': Stocks with no historical data (need full sync)
            - 'missing_today': Stocks with historical data but missing today's data (need today's data only)
            - 'skip': Stocks that are already up-to-date
        """
        try:
            # Get stocks that are completely missing from historical data
            missing_all = self.get_missing_stocks(all_stock_codes)

            # Get stocks that have some historical data
            existing_codes = [code for code in all_stock_codes if code not in missing_all]

            # Among existing stocks, find those missing today's data
            missing_today = self.get_stocks_missing_today_data(existing_codes)

            # Stocks that are already up-to-date
            skip_codes = [code for code in existing_codes if code not in missing_today]

            result = {
                'missing_all': missing_all,
                'missing_today': missing_today,
                'skip': skip_codes
            }

            logger.info(
                f"Fetching list computed: {len(missing_all)} need full sync, "
                f"{len(missing_today)} need today's data, {len(skip_codes)} already up-to-date"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to compute fetching list: {e}")
            return {'missing_all': [], 'missing_today': [], 'skip': []}

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
            return False, (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")

        # Check if we have data for the last business day
        today = datetime.now().date()
        last_business_day = today

        # Adjust for weekends (simple logic)
        if today.weekday() >= 5:  # Saturday = 5, Sunday = 6
            days_to_subtract = today.weekday() - 4  # Go back to Friday
            last_business_day = today - timedelta(days=days_to_subtract)

        latest_date_obj = datetime.strptime(latest_date, "%Y-%m-%d").date()

        if latest_date_obj >= last_business_day:
            return True, None
        else:
            # Need to fetch from day after latest date
            next_date = latest_date_obj + timedelta(days=1)
            return False, next_date.strftime("%Y-%m-%d")

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

    @timed_operation("historical_data_bulk_store")
    def bulk_store_historical_data(
        self, stock_data_dict: Dict[str, pd.DataFrame], chunk_size: Optional[int] = None
    ) -> Dict[str, int]:
        """Bulk store historical data for multiple stocks in the single stock_historical_data table.

        Args:
            stock_data_dict: Dictionary mapping stock codes to their DataFrames
            chunk_size: Not used in this implementation (kept for compatibility)

        Returns:
            Dictionary mapping stock codes to number of records stored
        """
        if not stock_data_dict:
            logger.warning("No stock data to bulk store")
            return {}

        try:
            conn = self.db_connection.connect()
            results = {}

            for stock_code, data in stock_data_dict.items():
                if data is None or data.empty:
                    logger.warning(f"No data to store for {stock_code}")
                    results[stock_code] = 0
                    continue

                try:
                    # Prepare DataFrame for storage
                    logger.debug(f"Preparing DataFrame for {stock_code}: {len(data)} rows")
                    df_to_store = data.copy()

                    # Add stock_code column if not present
                    if 'stock_code' not in df_to_store.columns:
                        df_to_store['stock_code'] = stock_code
                        logger.debug(f"Added stock_code column to DataFrame for {stock_code}")

                    # Ensure date column is datetime for proper storage
                    if 'date' in df_to_store.columns:
                        df_to_store['date'] = pd.to_datetime(df_to_store['date'])
                        logger.debug(f"Converted date column to datetime for {stock_code}")

                    # Add timestamps
                    current_time = datetime.now()
                    df_to_store['created_at'] = current_time
                    df_to_store['updated_at'] = current_time
                    logger.debug(f"Added timestamps to DataFrame for {stock_code}")

                    # Ensure all required columns exist in the DataFrame with default values
                    # and reorder them to match the table schema
                    table_columns = [
                        'date', 'stock_code', 'open_price', 'close_price', 'high_price', 'low_price',
                        'volume', 'turnover', 'amplitude', 'price_change_rate', 'price_change', 'turnover_rate',
                        'created_at', 'updated_at'
                    ]

                    for col in table_columns:
                        if col not in df_to_store.columns:
                            if col in ['volume']:
                                df_to_store[col] = 0
                            elif col in ['created_at', 'updated_at']:
                                df_to_store[col] = current_time
                            else:
                                df_to_store[col] = 0.0
                            logger.debug(f"Added default value for missing column '{col}' in DataFrame for {stock_code}")

                    # Reorder columns to match table schema
                    df_to_store = df_to_store[table_columns]
                    logger.debug(f"Reordered columns to match table schema for {stock_code}")

                    # Register DataFrame in DuckDB connection AFTER processing
                    logger.debug(f"Registering DataFrame as temporary table 'df_{stock_code}'")
                    conn.register(f"df_{stock_code}", df_to_store)

                    # Insert data into the single stock_historical_data table
                    # Use a simpler approach - let DuckDB handle type conversion
                    insert_query = f"""
                        INSERT OR REPLACE INTO stock_historical_data
                        SELECT * FROM df_{stock_code}
                    """

                    logger.debug(f"Executing insert query for {stock_code}: {insert_query.strip()}")
                    conn.execute(insert_query)
                    logger.debug(f"Successfully executed insert query for {stock_code}")

                    stored_count = len(df_to_store)
                    results[stock_code] = stored_count

                    logger.info(f"Successfully inserted {stored_count} records for {stock_code} into stock_historical_data table")

                except Exception as e:
                    logger.error(f"Failed to store historical data for {stock_code}: {e}")
                    results[stock_code] = 0
                    continue

            total_records = sum(results.values())
            successful_stocks = sum(1 for count in results.values() if count > 0)

            logger.info(
                f"Successfully stored {total_records} historical records across {successful_stocks} stocks in single table"
            )
            return results

        except Exception as e:
            logger.error(f"Failed to bulk store historical data: {e}")
            return {stock_code: 0 for stock_code in stock_data_dict.keys()}

    def accumulate_and_bulk_insert(
        self, batch_data: Dict[str, pd.DataFrame], batch_size: int = 100
    ) -> Tuple[Dict[str, int], Dict[str, pd.DataFrame]]:
        """Accumulate historical data in batches and perform bulk inserts when batch_size is reached.

        Args:
            batch_data: Dictionary of accumulated stock code -> DataFrame
            batch_size: Number of stocks to accumulate before bulk insert (default: 100)

        Returns:
            Tuple of (results_dict, remaining_data_dict) where results_dict contains
            stored counts for completed batches and remaining_data_dict contains
            data not yet inserted (incomplete batch)
        """
        results = {}

        if not batch_data:
            return results, {}

        # If we have batch_size or more stocks, perform bulk insert
        if len(batch_data) >= batch_size:
            # Split into full batches and remainder
            batch_items = list(batch_data.items())
            full_batch_items = batch_items[:batch_size]
            remaining_items = batch_items[batch_size:]

            full_batch_dict = dict(full_batch_items)
            remaining_dict = dict(remaining_items)

            # Insert the full batch
            batch_results = self.bulk_store_historical_data(full_batch_dict)
            results.update(batch_results)

            logger.info(
                f"Completed bulk insert of {len(full_batch_dict)} stocks, {len(remaining_dict)} stocks remaining in accumulator"
            )
            return results, remaining_dict
        else:
            # Not enough data yet, return empty results and keep all data for next accumulation
            logger.debug(
                f"Accumulated {len(batch_data)} stocks in batch, waiting for {batch_size - len(batch_data)} more stocks"
            )
            return results, batch_data
