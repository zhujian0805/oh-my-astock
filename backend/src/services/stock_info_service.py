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

        # Fetch from both APIs
        em_data, em_success = self._fetch_em_data(stock_code)
        xq_data, xq_success = self._fetch_xq_data(stock_code)

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

    def _fetch_xq_data(self, stock_code: str) -> Tuple[List[Dict], bool]:
        """
        Fetch data from Xueqiu API

        Returns:
            Tuple of (data_list, success_flag)
        """
        try:
            # Wait for rate limit
            if not rate_limiter.wait_for_api('xq_api', timeout=30.0):
                logger.warning("Rate limit timeout for XQ API")
                return [], False

            logger.debug(f"Calling XQ API for {stock_code}")
            df = ak.stock_individual_basic_info_xq(symbol=stock_code)

            if df.empty:
                logger.warning(f"XQ API returned empty data for {stock_code}")
                return [], False

            # Convert DataFrame to list of dicts
            data = df.to_dict('records')
            logger.info(f"XQ API success for {stock_code}: {len(data)} items")
            return data, True

        except Exception as e:
            logger.error(f"XQ API error for {stock_code}: {str(e)}")
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