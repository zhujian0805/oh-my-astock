"""
Stock Models
Pydantic models for stock data validation and serialization
"""

from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel


class StockList(BaseModel):
    """Stock list item model"""

    id: Optional[int] = None
    code: str
    name: str
    exchange: str
    is_active: bool = True
    priority: int = 0
    created_at: Optional[datetime] = None


class Stock(BaseModel):
    """Stock model with merged data from multiple APIs"""

    # Primary key
    code: str

    # Basic info (precedence: Xueqiu > East Money)
    name: Optional[str] = None
    symbol: Optional[str] = None
    exchange: Optional[str] = None

    # East Money API fields
    industry: Optional[str] = None
    total_market_cap: Optional[float] = None
    circulating_market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None  # East Money preferred
    pb_ratio: Optional[float] = None  # East Money preferred
    roe: Optional[float] = None
    gross_margin: Optional[float] = None
    net_margin: Optional[float] = None

    # Xueqiu API fields
    current_price: Optional[float] = None  # Xueqiu preferred
    change_percent: Optional[float] = None  # Xueqiu preferred
    volume: Optional[int] = None  # Xueqiu preferred
    turnover: Optional[float] = None  # Xueqiu preferred
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    eps: Optional[float] = None
    dividend_yield: Optional[float] = None

    # Metadata
    last_updated: datetime = datetime.now()
    data_sources: Dict[str, bool] = {"east_money": False, "xueqiu": False}
    errors: list = []