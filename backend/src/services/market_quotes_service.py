"""
Market Quotes Service
Handles retrieval of market bid-ask data from akshare APIs
"""

import logging
import akshare as ak
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.market_quote import MarketQuote
from ..lib.rate_limiter import rate_limiter
from ..lib.cache import api_cache

logger = logging.getLogger(__name__)


class MarketQuotesService:
    """Service for retrieving market quotes data"""

    def get_market_quotes(self, stock_codes: Optional[List[str]] = None) -> List[MarketQuote]:
        """
        Get market quotes for specified stocks or default popular stocks

        Args:
            stock_codes: List of 6-digit stock codes. If None, returns default stocks.

        Returns:
            List of MarketQuote objects
        """
        if stock_codes is None:
            # Default popular stocks
            stock_codes = ["000001", "600000", "000002", "600036", "000858"]

        quotes = []
        for stock_code in stock_codes:
            try:
                quote = self._get_single_quote(stock_code)
                quotes.append(quote)
            except Exception as e:
                logger.error(f"Failed to get quote for {stock_code}: {e}")
                # Return quote with error
                quotes.append(MarketQuote(
                    stock_code=stock_code,
                    error=str(e)
                ))

        return quotes

    def _get_single_quote(self, stock_code: str) -> MarketQuote:
        """
        Get market quote for a single stock

        Args:
            stock_code: 6-digit stock code

        Returns:
            MarketQuote object
        """
        # Check cache first
        cache_key = f"market_quote_{stock_code}"
        cached_result = api_cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for market quote {stock_code}")
            return cached_result

        logger.info(f"Fetching market quote for {stock_code}")

        try:
            # Wait for rate limit
            if not rate_limiter.wait_for_api('quotes_api', timeout=30.0):
                logger.warning("Rate limit timeout for quotes API")
                raise Exception("Rate limit exceeded")

            # Call akshare API
            df = ak.stock_bid_ask_em(symbol=stock_code)

            if df.empty:
                logger.warning(f"Quotes API returned empty data for {stock_code}")
                raise Exception("No quote data available")

            # Convert DataFrame to MarketQuote
            quote = self._parse_quote_data(stock_code, df)

            # Cache successful results
            api_cache.set(cache_key, quote)

            return quote

        except Exception as e:
            logger.error(f"Error fetching quote for {stock_code}: {str(e)}")
            raise

    def _parse_quote_data(self, stock_code: str, df) -> MarketQuote:
        """
        Parse akshare DataFrame into MarketQuote model

        Args:
            stock_code: The stock code
            df: akshare DataFrame with quote data

        Returns:
            MarketQuote object
        """
        # Convert DataFrame to dict for easier processing
        data = {}
        for _, row in df.iterrows():
            key = str(row['item']).strip()
            value = row['value']

            # Handle different data types
            if isinstance(value, str):
                # Try to convert numeric strings
                try:
                    # Check if it's a number
                    if '.' in value or value.isdigit():
                        if '.' in value:
                            data[key] = float(value)
                        else:
                            data[key] = int(value)
                    else:
                        data[key] = value
                except ValueError:
                    data[key] = value
            else:
                data[key] = value

        # Extract bid/ask data
        bid_ask_data = self._extract_bid_ask_levels(data)

        # Create MarketQuote object
        quote = MarketQuote(
            stock_code=stock_code,
            stock_name=data.get('股票简称') or data.get('股票名称'),
            # Bid/Ask levels
            **bid_ask_data,
            # Market data - map to correct akshare field names
            latest_price=data.get('最新'),
            average_price=data.get('均价'),
            change_amount=data.get('涨跌'),
            change_percent=data.get('涨幅'),
            volume=data.get('总手'),
            turnover=data.get('金额'),
            turnover_rate=data.get('换手'),
            volume_ratio=data.get('量比'),
            high=data.get('最高'),
            low=data.get('最低'),
            open=data.get('今开'),
            previous_close=data.get('昨收'),
            limit_up=data.get('涨停'),
            limit_down=data.get('跌停'),
            external_volume=data.get('外盘'),
            internal_volume=data.get('内盘'),
            # Metadata
            last_updated=datetime.now(),
            data_source="east_money"
        )

        return quote

    def _extract_bid_ask_levels(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract bid and ask levels from the parsed data dict

        Args:
            data: Dict containing all parsed akshare data

        Returns:
            Dict with bid/ask level data
        """
        levels_data = {}

        # Extract bid (buy) levels
        for level in range(1, 6):
            bid_price_key = f'buy_{level}'
            bid_volume_key = f'buy_{level}_vol'

            if bid_price_key in data:
                levels_data[f'bid_price_{level}'] = data[bid_price_key]
            if bid_volume_key in data:
                levels_data[f'bid_volume_{level}'] = data[bid_volume_key]

        # Extract ask (sell) levels
        for level in range(1, 6):
            ask_price_key = f'sell_{level}'
            ask_volume_key = f'sell_{level}_vol'

            if ask_price_key in data:
                levels_data[f'ask_price_{level}'] = data[ask_price_key]
            if ask_volume_key in data:
                levels_data[f'ask_volume_{level}'] = data[ask_volume_key]

        return levels_data

    def _extract_level_number(self, item: str) -> Optional[int]:
        """Extract level number from item string"""
        # Look for numbers in the item name
        import re
        match = re.search(r'(\d+)', item)
        if match:
            return int(match.group(1))
        return None

    def _parse_numeric(self, value, target_type=float):
        """Parse value to numeric type, return None if invalid"""
        if value is None or value == '' or str(value).lower() in ['none', 'null', 'nan']:
            return None

        try:
            if target_type == int:
                return int(float(value))
            else:
                return target_type(value)
        except (ValueError, TypeError):
            return None


# Singleton instance
market_quotes_service = MarketQuotesService()