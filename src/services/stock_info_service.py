"""
Stock Information Service

This module provides business logic for fetching, processing, and storing stock information
from multiple Chinese financial data sources.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
import asyncio

from ..models.stock_info import StockInfo

logger = logging.getLogger(__name__)


class StockInfoService:
    """
    Service for managing stock information operations.

    Provides methods for fetching stock data from APIs, merging information
    from multiple sources, and storing results in the database.
    """

    def __init__(self, database_service, cache_service=None, rate_limiter=None):
        """
        Initialize the stock info service.

        Args:
            database_service: Database service for persistence
            cache_service: Optional caching service
            rate_limiter: Optional rate limiting service
        """
        self.database_service = database_service
        self.cache_service = cache_service
        self.rate_limiter = rate_limiter

    async def get_stock_info(self, stock_code: str, force_refresh: bool = False) -> Optional[StockInfo]:
        """
        Get stock information for a single stock code.

        Args:
            stock_code: Stock code (e.g., '000001')
            force_refresh: Force refresh from APIs instead of using cache

        Returns:
            StockInfo object or None if not found
        """
        # Check cache first (unless force refresh)
        if not force_refresh and self.cache_service:
            cached_data = await self.cache_service.get(f"stock_info:{stock_code}")
            if cached_data:
                logger.debug(f"Cache hit for stock {stock_code}")
                return self._dict_to_stock_info(cached_data)

        # Fetch from database first
        db_data = await self.database_service.get_stock_info(stock_code)
        if db_data and not force_refresh:
            # Cache the database result
            if self.cache_service:
                await self.cache_service.set(
                    f"stock_info:{stock_code}",
                    self._stock_info_to_dict(db_data),
                    ttl=86400  # 24 hours
                )
            return db_data

        # Fetch from APIs and merge
        merged_data = await self._fetch_and_merge_stock_info(stock_code)
        if merged_data:
            # Store in database
            await self.database_service.save_stock_info(merged_data)

            # Cache the result
            if self.cache_service:
                await self.cache_service.set(
                    f"stock_info:{stock_code}",
                    self._stock_info_to_dict(merged_data),
                    ttl=86400  # 24 hours
                )

            return merged_data

        return None

    async def get_stock_info_batch(self, stock_codes: List[str], force_refresh: bool = False) -> Dict[str, Optional[StockInfo]]:
        """
        Get stock information for multiple stock codes in batch.

        Args:
            stock_codes: List of stock codes
            force_refresh: Force refresh from APIs

        Returns:
            Dictionary mapping stock codes to StockInfo objects
        """
        results = {}

        # Process in batches to avoid overwhelming APIs
        batch_size = 10
        for i in range(0, len(stock_codes), batch_size):
            batch_codes = stock_codes[i:i + batch_size]

            # Create tasks for parallel processing
            tasks = [
                self.get_stock_info(code, force_refresh)
                for code in batch_codes
            ]

            # Execute batch
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for code, result in zip(batch_codes, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Error fetching stock {code}: {result}")
                    results[code] = None
                else:
                    results[code] = result

            # Small delay between batches to be respectful to APIs
            if i + batch_size < len(stock_codes):
                await asyncio.sleep(0.1)

        return results

    async def _fetch_and_merge_stock_info(self, stock_code: str) -> Optional[StockInfo]:
        """
        Fetch stock information from multiple APIs and merge the results.

        Args:
            stock_code: Stock code to fetch

        Returns:
            Merged StockInfo object or None if all sources fail
        """
        # This will be implemented by subclasses
        raise NotImplementedError("Subclasses must implement _fetch_and_merge_stock_info")

    def _dict_to_stock_info(self, data: Dict[str, Any]) -> StockInfo:
        """Convert dictionary to StockInfo object."""
        # Convert string dates back to date objects
        listing_date = None
        if data.get('listing_date'):
            listing_date = datetime.fromisoformat(data['listing_date']).date()

        return StockInfo(
            stock_code=data['stock_code'],
            company_name=data['company_name'],
            industry=data.get('industry'),
            sector=data.get('sector'),
            market=data.get('market', 'SZ'),
            listing_date=listing_date,
            total_shares=data.get('total_shares'),
            circulating_shares=data.get('circulating_shares'),
            market_cap=Decimal(str(data['market_cap'])) if data.get('market_cap') else None,
            pe_ratio=Decimal(str(data['pe_ratio'])) if data.get('pe_ratio') else None,
            pb_ratio=Decimal(str(data['pb_ratio'])) if data.get('pb_ratio') else None,
            dividend_yield=Decimal(str(data['dividend_yield'])) if data.get('dividend_yield') else None,
            roe=Decimal(str(data['roe'])) if data.get('roe') else None,
            roa=Decimal(str(data['roa'])) if data.get('roa') else None,
            net_profit=Decimal(str(data['net_profit'])) if data.get('net_profit') else None,
            total_assets=Decimal(str(data['total_assets'])) if data.get('total_assets') else None,
            total_liability=Decimal(str(data['total_liability'])) if data.get('total_liability') else None,
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))
        )

    def _stock_info_to_dict(self, stock_info: StockInfo) -> Dict[str, Any]:
        """Convert StockInfo object to dictionary for caching."""
        return {
            'stock_code': stock_info.stock_code,
            'company_name': stock_info.company_name,
            'industry': stock_info.industry,
            'sector': stock_info.sector,
            'market': stock_info.market,
            'listing_date': stock_info.listing_date.isoformat() if stock_info.listing_date else None,
            'total_shares': stock_info.total_shares,
            'circulating_shares': stock_info.circulating_shares,
            'market_cap': str(stock_info.market_cap) if stock_info.market_cap else None,
            'pe_ratio': str(stock_info.pe_ratio) if stock_info.pe_ratio else None,
            'pb_ratio': str(stock_info.pb_ratio) if stock_info.pb_ratio else None,
            'dividend_yield': str(stock_info.dividend_yield) if stock_info.dividend_yield else None,
            'roe': str(stock_info.roe) if stock_info.roe else None,
            'roa': str(stock_info.roa) if stock_info.roa else None,
            'net_profit': str(stock_info.net_profit) if stock_info.net_profit else None,
            'total_assets': str(stock_info.total_assets) if stock_info.total_assets else None,
            'total_liability': str(stock_info.total_liability) if stock_info.total_liability else None,
            'created_at': stock_info.created_at.isoformat(),
            'updated_at': stock_info.updated_at.isoformat()
        }