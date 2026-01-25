"""
Stock Information Service
Handles retrieval and merging of individual stock data from multiple APIs
"""

import logging
from typing import Dict, List, Optional, Tuple
import akshare as ak
from ..lib.rate_limiter import rate_limiter
from ..lib.cache import api_cache

logger = logging.getLogger(__name__)


class StockInfoService:
    """Service for retrieving and merging individual stock information"""

    def _get_prefixed_symbol(self, stock_code: str) -> str:
        """
        Convert 6-digit stock code to prefixed format for akshare APIs

        Args:
            stock_code: 6-digit stock code (e.g., "601127", "000001")

        Returns:
            Prefixed symbol (e.g., "SH601127", "SZ000001")
        """
        if not stock_code or len(stock_code) != 6:
            raise ValueError(f"Invalid stock code format: {stock_code}")

        if stock_code.startswith('6'):
            return f"SH{stock_code}"
        elif stock_code.startswith(('0', '3')):
            return f"SZ{stock_code}"
        else:
            raise ValueError(f"Unknown stock exchange for code: {stock_code}")

    def get_stock_info(self, stock_code: str) -> Dict:
        """
        Get merged stock information from multiple APIs

        Args:
            stock_code: Stock code (6 digits)

        Returns:
            Dict with merged data and source status
        """
        # Check cache first
        cache_key = f"stock_info_{stock_code}"
        cached_result = api_cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for stock {stock_code}")
            return cached_result

        logger.info(f"Fetching stock info for {stock_code}")

        # Get prefixed symbol for Xueqiu API (only XQ API needs prefixing)
        prefixed_symbol = self._get_prefixed_symbol(stock_code)
        logger.debug(f"Using prefixed symbol for XQ API: {prefixed_symbol}")

        # Fetch from both APIs
        em_data, em_success = self._fetch_em_data(stock_code)  # EM API uses raw code
        xq_data, xq_success = self._fetch_xq_data(prefixed_symbol)  # XQ API needs prefix

        # Merge data
        merged_data = self._merge_api_data(em_data, xq_data)

        result = {
            "stock_code": stock_code,
            "data": merged_data,
            "source_status": {
                "em_api": "success" if em_success else "failed",
                "xq_api": "success" if xq_success else "failed"
            }
        }

        # Cache successful results
        if em_success or xq_success:
            api_cache.set(cache_key, result)

        return result

    def _fetch_em_data(self, stock_code: str) -> Tuple[List[Dict], bool]:
        """
        Fetch data from East Money API

        Args:
            stock_code: 6-digit stock code (e.g., "601127")

        Returns:
            Tuple of (data_list, success_flag)
        """
        try:
            # Wait for rate limit
            if not rate_limiter.wait_for_api('em_api', timeout=30.0):
                logger.warning("Rate limit timeout for EM API")
                return [], False

            logger.debug(f"Calling EM API for {stock_code}")
            df = ak.stock_individual_info_em(symbol=stock_code)

            if df.empty:
                logger.warning(f"EM API returned empty data for {stock_code}")
                return [], False

            # Convert DataFrame to list of dicts
            data = df.to_dict('records')
            logger.info(f"EM API success for {stock_code}: {len(data)} items")
            return data, True

        except Exception as e:
            logger.error(f"EM API error for {stock_code}: {str(e)}")
            return [], False

    def _fetch_xq_data(self, prefixed_symbol: str) -> Tuple[List[Dict], bool]:
        """
        Fetch data from Xueqiu API

        Args:
            prefixed_symbol: Prefixed stock symbol (e.g., "SH601127")

        Returns:
            Tuple of (data_list, success_flag)
        """
        try:
            # Wait for rate limit
            if not rate_limiter.wait_for_api('xq_api', timeout=30.0):
                logger.warning("Rate limit timeout for XQ API")
                return [], False

            logger.debug(f"Calling XQ API for {prefixed_symbol}")
            df = ak.stock_individual_basic_info_xq(symbol=prefixed_symbol)

            if df.empty:
                logger.warning(f"XQ API returned empty data for {prefixed_symbol}")
                return [], False

            # Convert DataFrame to list of dicts
            data = df.to_dict('records')
            logger.info(f"XQ API success for {prefixed_symbol}: {len(data)} items")
            return data, True

        except Exception as e:
            logger.error(f"XQ API error for {prefixed_symbol}: {str(e)}")
            return [], False

    def _merge_api_data(self, em_data: List[Dict], xq_data: List[Dict]) -> Dict[str, str]:
        """
        Merge data from both APIs, prioritizing EM over XQ for duplicates

        Args:
            em_data: List of EM API records
            xq_data: List of XQ API records

        Returns:
            Merged dictionary with item->value mapping
        """
        merged = {}

        # Add XQ data first (lower priority)
        for record in xq_data:
            if 'item' in record and 'value' in record:
                merged[record['item']] = str(record['value'])

        # Add/override with EM data (higher priority)
        for record in em_data:
            if 'item' in record and 'value' in record:
                merged[record['item']] = str(record['value'])

        logger.debug(f"Merged {len(merged)} unique items from APIs")
        return merged