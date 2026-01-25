"""
Stock service
Business logic for stock data operations
"""

import logging
import re
from typing import List, Dict, Any, Optional
import pandas as pd
from ..database import db_service

logger = logging.getLogger(__name__)


class StockService:
    """Stock service for business logic operations"""

    async def get_all_stocks(self) -> List[Dict[str, Any]]:
        """Get all stocks from database"""
        try:
            logger.info("Fetching all stocks from database")

            sql = """
                SELECT code, name
                FROM stock_name_code
                ORDER BY code
            """

            stocks = await db_service.query(sql)

            logger.info(f"Retrieved {len(stocks)} stocks")
            return stocks

        except Exception as e:
            logger.error(f"Error fetching stocks: {e}")
            raise Exception("Failed to retrieve stocks from database")

    async def get_historical_data(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Get historical data for a specific stock"""
        try:
            logger.info(f"Fetching historical data for stock: {stock_code}")

            # First check if stock exists
            if not await self.stock_exists(stock_code):
                return None

            sql = """
                SELECT
                    date,
                    close_price,
                    open_price,
                    high_price,
                    low_price,
                    volume,
                    turnover,
                    amplitude,
                    price_change_rate,
                    price_change,
                    turnover_rate
                FROM stock_historical_data
                WHERE stock_code = ?
            """

            params = [stock_code]

            # Add date filtering if provided
            if start_date:
                sql += " AND date >= ?"
                params.append(start_date)

            if end_date:
                sql += " AND date <= ?"
                params.append(end_date)

            sql += " ORDER BY date DESC"

            data = await db_service.query(sql, params)

            logger.info(f"Retrieved {len(data)} historical records for {stock_code}")
            return data

        except Exception as e:
            logger.error(f"Error fetching historical data for {stock_code}: {e}")
            raise Exception("Failed to retrieve historical data")

    async def get_sse_summary(self) -> List[Dict[str, Any]]:
        """Get Shanghai Stock Exchange summary data"""
        try:
            logger.info("Fetching SSE summary data")
            import akshare as ak

            df = ak.stock_sse_summary()
            if df is None or df.empty:
                logger.warning("No SSE summary data available")
                return []

            # Convert DataFrame to dict and handle NaN values
            data = df.to_dict(orient="records")
            # Replace NaN values with None for JSON compatibility
            for record in data:
                for key, value in record.items():
                    if isinstance(value, float) and (pd.isna(value) or value != value):  # Check for NaN
                        record[key] = None
                    elif isinstance(value, float) and (value == float('inf') or value == float('-inf')):
                        record[key] = None

            logger.info(f"Retrieved {len(data)} SSE summary records")
            return data
        except Exception as e:
            logger.error(f"Error fetching SSE summary: {e}")
            raise Exception("Failed to retrieve SSE summary data")

    async def get_szse_summary(self) -> List[Dict[str, Any]]:
        """Get Shenzhen Stock Exchange security category statistics"""
        try:
            logger.info("Fetching SZSE security category statistics")
            import akshare as ak

            df = ak.stock_szse_summary()
            if df is None or df.empty:
                logger.warning("No SZSE summary data available")
                return []

            # Convert DataFrame to dict and handle NaN values
            data = df.to_dict(orient="records")
            # Replace NaN values with None for JSON compatibility
            for record in data:
                for key, value in record.items():
                    if isinstance(value, float) and (pd.isna(value) or value != value):  # Check for NaN
                        record[key] = None
                    elif isinstance(value, float) and (value == float('inf') or value == float('-inf')):
                        record[key] = None

            logger.info(f"Retrieved {len(data)} SZSE summary records")
            return data
        except Exception as e:
            logger.error(f"Error fetching SZSE summary: {e}")
            raise Exception("Failed to retrieve SZSE summary data")

    async def get_szse_area_summary(self) -> List[Dict[str, Any]]:
        """Get Shenzhen Stock Exchange regional trading rankings"""
        try:
            logger.info("Fetching SZSE regional trading rankings")
            import akshare as ak

            df = ak.stock_szse_area_summary()
            if df is None or df.empty:
                logger.warning("No SZSE area summary data available")
                return []

            # Convert DataFrame to dict and handle NaN values
            data = df.to_dict(orient="records")
            # Replace NaN values with None for JSON compatibility
            for record in data:
                for key, value in record.items():
                    if isinstance(value, float) and (pd.isna(value) or value != value):  # Check for NaN
                        record[key] = None
                    elif isinstance(value, float) and (value == float('inf') or value == float('-inf')):
                        record[key] = None

            logger.info(f"Retrieved {len(data)} SZSE area summary records")
            return data
        except Exception as e:
            logger.error(f"Error fetching SZSE area summary: {e}")
            raise Exception("Failed to retrieve SZSE area summary data")

    async def get_szse_sector_summary(self) -> List[Dict[str, Any]]:
        """Get Shenzhen Stock Exchange industry sector transaction data"""
        try:
            logger.info("Fetching SZSE industry sector transaction data")
            import akshare as ak

            df = ak.stock_szse_sector_summary()
            if df is None or df.empty:
                logger.warning("No SZSE sector summary data available")
                return []

            # Convert DataFrame to dict and handle NaN values
            data = df.to_dict(orient="records")
            # Replace NaN values with None for JSON compatibility
            for record in data:
                for key, value in record.items():
                    if isinstance(value, float) and (pd.isna(value) or value != value):  # Check for NaN
                        record[key] = None
                    elif isinstance(value, float) and (value == float('inf') or value == float('-inf')):
                        record[key] = None

            logger.info(f"Retrieved {len(data)} SZSE sector summary records")
            return data
        except Exception as e:
            logger.error(f"Error fetching SZSE sector summary: {e}")
            raise Exception("Failed to retrieve SZSE sector summary data")

    async def get_sse_daily_deals(self) -> List[Dict[str, Any]]:
        """Get Shanghai Stock Exchange daily stock transaction details"""
        try:
            logger.info("Fetching SSE daily stock transaction details")
            import akshare as ak

            df = ak.stock_sse_deal_daily()
            if df is None or df.empty:
                logger.warning("No SSE daily deals data available")
                return []

            # Convert DataFrame to dict and handle NaN values
            data = df.to_dict(orient="records")
            # Replace NaN values with None for JSON compatibility
            for record in data:
                for key, value in record.items():
                    if isinstance(value, float) and (pd.isna(value) or value != value):  # Check for NaN
                        record[key] = None
                    elif isinstance(value, float) and (value == float('inf') or value == float('-inf')):
                        record[key] = None

            logger.info(f"Retrieved {len(data)} SSE daily deals records")
            return data
        except Exception as e:
            logger.error(f"Error fetching SSE daily deals: {e}")
            raise Exception("Failed to retrieve SSE daily deals data")

    async def get_security_categories(self) -> List[Dict[str, Any]]:
        """Get comprehensive security category statistics"""
        try:
            logger.info("Fetching comprehensive security category statistics")
            import akshare as ak

            # Use the same SZSE summary API for comprehensive categories
            df = ak.stock_szse_summary()
            if df is None or df.empty:
                logger.warning("No security categories data available")
                return []

            # Convert DataFrame to dict and handle NaN values
            data = df.to_dict(orient="records")
            # Replace NaN values with None for JSON compatibility
            for record in data:
                for key, value in record.items():
                    if isinstance(value, float) and (pd.isna(value) or value != value):  # Check for NaN
                        record[key] = None
                    elif isinstance(value, float) and (value == float('inf') or value == float('-inf')):
                        record[key] = None

            logger.info(f"Retrieved {len(data)} security categories records")
            return data
        except Exception as e:
            logger.error(f"Error fetching security categories: {e}")
            raise Exception("Failed to retrieve security categories data")

    async def stock_exists(self, stock_code: str) -> bool:
        """Check if stock exists in database"""
        try:
            sql = """
                SELECT COUNT(*) as count
                FROM stock_name_code
                WHERE code = ?
            """

            result = await db_service.query(sql, [stock_code])
            return result[0]["count"] > 0

        except Exception as e:
            logger.error(f"Error checking stock existence for {stock_code}: {e}")
            raise e

    def is_valid_stock_code(self, code: str) -> bool:
        """Validate stock code format"""
        # Chinese stock codes are typically 6 digits
        return bool(re.match(r"^\d{6}$", code))


# Singleton instance
stock_service = StockService()
