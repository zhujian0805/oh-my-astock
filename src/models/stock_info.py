"""
Stock Information Models

This module contains dataclasses for stock information entities.
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


@dataclass
class StockInfo:
    """
    Comprehensive stock information merged from multiple sources.

    Represents all available stock data including basic profile, financial metrics,
    and market data from East Money and Xueqiu APIs.
    """
    stock_code: str
    company_name: str
    industry: Optional[str] = None
    sector: Optional[str] = None
    market: str = "SZ"  # SH or SZ
    listing_date: Optional[date] = None
    total_shares: Optional[int] = None
    circulating_shares: Optional[int] = None
    market_cap: Optional[Decimal] = None
    pe_ratio: Optional[Decimal] = None
    pb_ratio: Optional[Decimal] = None
    dividend_yield: Optional[Decimal] = None
    roe: Optional[Decimal] = None
    roa: Optional[Decimal] = None
    net_profit: Optional[Decimal] = None
    total_assets: Optional[Decimal] = None
    total_liability: Optional[Decimal] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        """Set default timestamps if not provided."""
        now = datetime.now()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now

    @property
    def market_cap_billion(self) -> Optional[Decimal]:
        """Market cap in billions (CNY)."""
        if self.market_cap is None:
            return None
        return self.market_cap / Decimal('1000000000')

    @property
    def circulating_cap(self) -> Optional[Decimal]:
        """Circulating market cap (CNY)."""
        if self.circulating_shares is None or self.market_cap is None or self.total_shares is None or self.total_shares == 0:
            return None
        return self.market_cap * Decimal(self.circulating_shares) / Decimal(self.total_shares)


@dataclass
class Migration:
    """
    Database migration tracking entity.

    Tracks applied database schema migrations with version control.
    """
    version: int
    name: str
    applied_at: datetime
    checksum: str
    success: bool = True
    execution_time_ms: Optional[int] = None

    @property
    def version_string(self) -> str:
        """Formatted version string (e.g., '001', '042')."""
        return f"{self.version:03d}"