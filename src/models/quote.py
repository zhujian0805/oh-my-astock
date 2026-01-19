"""Stock quote data model."""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Quote:
    """Real-time stock quote data."""

    symbol: str
    name: str
    price: Optional[float] = None
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None
    volume: Optional[int] = None
    turnover: Optional[float] = None
    price_change: Optional[float] = None
    price_change_rate: Optional[float] = None
    timestamp: Optional[datetime] = None
    market_status: Optional[str] = None  # e.g., "trading", "closed", "pre-market"

    def __post_init__(self):
        """Validate quote data after initialization."""
        if not self.symbol or not isinstance(self.symbol, str):
            raise ValueError("Quote symbol must be a non-empty string")
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Quote name must be a non-empty string")
        self.symbol = self.symbol.strip()
        self.name = self.name.strip()

    def to_dict(self) -> Dict[str, Any]:
        """Convert quote to dictionary."""
        result = {
            "symbol": self.symbol,
            "name": self.name,
            "price": self.price,
            "open_price": self.open_price,
            "high_price": self.high_price,
            "low_price": self.low_price,
            "close_price": self.close_price,
            "volume": self.volume,
            "turnover": self.turnover,
            "price_change": self.price_change,
            "price_change_rate": self.price_change_rate,
            "market_status": self.market_status
        }
        if self.timestamp:
            result["timestamp"] = self.timestamp.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Quote':
        """Create quote from dictionary."""
        timestamp = None
        if data.get("timestamp"):
            if isinstance(data["timestamp"], str):
                timestamp = datetime.fromisoformat(data["timestamp"])
            else:
                timestamp = data["timestamp"]

        return cls(
            symbol=data["symbol"],
            name=data["name"],
            price=data.get("price"),
            open_price=data.get("open_price"),
            high_price=data.get("high_price"),
            low_price=data.get("low_price"),
            close_price=data.get("close_price"),
            volume=data.get("volume"),
            turnover=data.get("turnover"),
            price_change=data.get("price_change"),
            price_change_rate=data.get("price_change_rate"),
            timestamp=timestamp,
            market_status=data.get("market_status")
        )

    def __str__(self) -> str:
        """String representation."""
        price_str = ".2f" if self.price else "N/A"
        change_str = ".2f" if self.price_change is not None else "N/A"
        return f"Quote(symbol='{self.symbol}', name='{self.name}', price={price_str}, change={change_str})"