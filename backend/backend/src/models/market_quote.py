"""
Market Quote Models
Pydantic models for market quote data validation and serialization
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MarketQuote(BaseModel):
    """Market quote model with bid-ask data"""

    # Basic identifiers
    stock_code: str
    stock_name: Optional[str] = None

    # Bid prices and volumes (5 levels each)
    bid_price_1: Optional[float] = None
    bid_volume_1: Optional[int] = None
    bid_price_2: Optional[float] = None
    bid_volume_2: Optional[int] = None
    bid_price_3: Optional[float] = None
    bid_volume_3: Optional[int] = None
    bid_price_4: Optional[float] = None
    bid_volume_4: Optional[int] = None
    bid_price_5: Optional[float] = None
    bid_volume_5: Optional[int] = None

    # Ask prices and volumes (5 levels each)
    ask_price_1: Optional[float] = None
    ask_volume_1: Optional[int] = None
    ask_price_2: Optional[float] = None
    ask_volume_2: Optional[int] = None
    ask_price_3: Optional[float] = None
    ask_volume_3: Optional[int] = None
    ask_price_4: Optional[float] = None
    ask_volume_4: Optional[int] = None
    ask_price_5: Optional[float] = None
    ask_volume_5: Optional[int] = None

    # Market data
    latest_price: Optional[float] = None
    change_amount: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    turnover: Optional[float] = None

    # Metadata
    last_updated: datetime = datetime.now()
    data_source: str = "east_money"
    error: Optional[str] = None

    def has_valid_data(self) -> bool:
        """Check if the quote has any meaningful market data"""
        return (
            self.latest_price is not None or
            self.bid_price_1 is not None or
            self.ask_price_1 is not None or
            self.volume is not None
        )

    def get_bid_ask_levels(self) -> list:
        """Get available bid/ask levels as list of tuples"""
        levels = []
        for i in range(1, 6):
            bid_price = getattr(self, f"bid_price_{i}")
            bid_volume = getattr(self, f"bid_volume_{i}")
            ask_price = getattr(self, f"ask_price_{i}")
            ask_volume = getattr(self, f"ask_volume_{i}")

            if bid_price is not None or ask_price is not None:
                levels.append({
                    'level': i,
                    'bid_price': bid_price,
                    'bid_volume': bid_volume,
                    'ask_price': ask_price,
                    'ask_volume': ask_volume
                })
        return levels


class MarketQuotesResponse(BaseModel):
    """API response model for market quotes"""

    quotes: list[MarketQuote]
    metadata: dict

    def get_total_quotes(self) -> int:
        """Get total number of quotes"""
        return len(self.quotes)

    def get_successful_quotes(self) -> int:
        """Get number of quotes with valid data"""
        return len([q for q in self.quotes if q.has_valid_data()])</content>
<parameter name="file_path">backend/src/models/market_quote.py