"""
Stock service
Business logic for stock data operations
"""

import logging
import re
from typing import List, Dict, Any, Optional
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

            data = df.to_dict(orient="records")
            logger.info(f"Retrieved {len(data)} SSE summary records")
            return data
        except Exception as e:
            logger.error(f"Error fetching SSE summary: {e}")
            raise Exception("Failed to retrieve SSE summary data")

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
