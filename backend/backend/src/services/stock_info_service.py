"""
Stock Information Service
Handles retrieval and merging of individual stock data from multiple APIs
"""

from typing import Dict, List, Optional, Tuple
import logging
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

    def _fetch_east_money_data(self, stock_code: str) -> Tuple[Dict, bool]:
        """Fetch data from East Money API"""
        try:
            rate_limiter.wait_if_needed()

            # Use akshare to get stock individual info
            data = ak.stock_individual_info_em(symbol=stock_code)

            if data is not None and not data.empty:
                # Convert to dict format
                record = data.iloc[0].to_dict()
                return {
                    "exchange": record.get("市场名称"),
                    "industry": record.get("行业"),
                    "total_market_cap": record.get("总市值"),
                    "circulating_market_cap": record.get("流通市值"),
                    "pe_ratio": record.get("市盈率-动态"),
                    "pb_ratio": record.get("市净率"),
                    "roe": record.get("净利率"),
                    "gross_margin": record.get("毛利率"),
                    "net_margin": record.get("净利率")
                }, True
            else:
                return {}, False

        except Exception as e:
            logger.warning(f"East Money API failed for {stock_code}: {e}")
            return {}, False

    def _fetch_xueqiu_data(self, symbol: str) -> Tuple[Dict, bool]:
        """Fetch data from Xueqiu API"""
        try:
            rate_limiter.wait_if_needed()

            # Use akshare to get stock basic info
            data = ak.stock_individual_basic_info_xq(symbol=symbol)

            if data is not None and not data.empty:
                # Convert to dict format
                record = data.iloc[0].to_dict()
                return {
                    "current_price": record.get("当前"),
                    "change_percent": record.get("涨幅"),
                    "volume": record.get("成交量"),
                    "turnover": record.get("成交额"),
                    "high_52w": record.get("52周最高"),
                    "low_52w": record.get("52周最低"),
                    "eps": record.get("每股收益"),
                    "dividend_yield": record.get("股息率")
                }, True
            else:
                return {}, False

        except Exception as e:
            logger.warning(f"Xueqiu API failed for {symbol}: {e}")
            return {}, False

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
        if cached_result is not None:
            logger.debug(f"Cache hit for {cache_key}")
            return cached_result

        # Initialize result
        result = {
            "code": stock_code,
            "data_sources": {"east_money": False, "xueqiu": False},
            "errors": []
        }

        # Get symbol for Xueqiu API
        try:
            symbol = self._get_prefixed_symbol(stock_code)
            result["symbol"] = symbol
        except ValueError as e:
            result["errors"].append(str(e))
            return result

        # Fetch from East Money API
        em_data, em_success = self._fetch_east_money_data(stock_code)
        result["data_sources"]["east_money"] = em_success

        # Fetch from Xueqiu API
        xq_data, xq_success = self._fetch_xueqiu_data(symbol)
        result["data_sources"]["xueqiu"] = xq_success

        # Merge data with precedence rules
        merged_data = {}

        # Xueqiu takes precedence for these fields
        xueqiu_priority_fields = ["current_price", "change_percent", "volume", "turnover"]
        for field in xueqiu_priority_fields:
            if xq_success and field in xq_data and xq_data[field] is not None:
                merged_data[field] = xq_data[field]
            elif em_success and field in em_data and em_data[field] is not None:
                merged_data[field] = em_data[field]

        # East Money takes precedence for these fields
        east_money_priority_fields = ["pe_ratio", "pb_ratio"]
        for field in east_money_priority_fields:
            if em_success and field in em_data and em_data[field] is not None:
                merged_data[field] = em_data[field]
            elif xq_success and field in xq_data and xq_data[field] is not None:
                merged_data[field] = xq_data[field]

        # Add remaining fields from whichever source has them
        all_fields = set(em_data.keys()) | set(xq_data.keys())
        for field in all_fields:
            if field not in merged_data:
                if em_success and field in em_data and em_data[field] is not None:
                    merged_data[field] = em_data[field]
                elif xq_success and field in xq_data and xq_data[field] is not None:
                    merged_data[field] = xq_data[field]

        # Update result with merged data
        result.update(merged_data)

        # Add error messages
        if not em_success:
            result["errors"].append("Failed to fetch data from East Money API")
        if not xq_success:
            result["errors"].append("Failed to fetch data from Xueqiu API")

        # Cache the result for 5 minutes
        api_cache.set(cache_key, result, ttl_seconds=300)

        return result