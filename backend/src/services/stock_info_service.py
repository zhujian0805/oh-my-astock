"""
Backend Stock Information Service

FastAPI service layer for stock information operations.
"""

import logging
from typing import Dict, List, Optional

from ...models.stock_info import StockInfo

logger = logging.getLogger(__name__)


class BackendStockInfoService:
    """
    Backend service for stock information operations.

    This service coordinates between the core stock info service
    and the FastAPI application layer.
    """

    def __init__(self, core_stock_service):
        """
        Initialize the backend stock info service.

        Args:
            core_stock_service: Core stock information service from src/
        """
        self.core_stock_service = core_stock_service

    async def get_stock_info(self, stock_code: str, force_refresh: bool = False) -> Optional[StockInfo]:
        """
        Get stock information for a single stock code.

        Args:
            stock_code: Stock code (e.g., '000001')
            force_refresh: Force refresh from APIs

        Returns:
            StockInfo object or None if not found
        """
        try:
            return await self.core_stock_service.get_stock_info(stock_code, force_refresh)
        except Exception as e:
            logger.error(f"Error getting stock info for {stock_code}: {e}")
            raise

    async def get_stock_info_batch(
        self,
        stock_codes: List[str],
        force_refresh: bool = False
    ) -> Dict[str, Optional[StockInfo]]:
        """
        Get stock information for multiple stock codes.

        Args:
            stock_codes: List of stock codes
            force_refresh: Force refresh from APIs

        Returns:
            Dictionary mapping stock codes to StockInfo objects
        """
        try:
            return await self.core_stock_service.get_stock_info_batch(stock_codes, force_refresh)
        except Exception as e:
            logger.error(f"Error in batch stock info request: {e}")
            raise