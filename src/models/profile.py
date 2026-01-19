"""Company profile data model."""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import date


@dataclass
class Profile:
    """Company profile information."""

    symbol: str
    name: str
    english_name: Optional[str] = None
    listing_date: Optional[date] = None
    industry: Optional[str] = None
    business: Optional[str] = None
    market_cap: Optional[float] = None  # Market capitalization
    pe_ratio: Optional[float] = None    # Price-to-earnings ratio
    pb_ratio: Optional[float] = None    # Price-to-book ratio
    eps: Optional[float] = None         # Earnings per share
    bps: Optional[float] = None         # Book value per share
    total_shares: Optional[int] = None  # Total shares outstanding
    circulating_shares: Optional[int] = None  # Circulating shares
    website: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

    def __post_init__(self):
        """Validate profile data after initialization."""
        if not self.symbol or not isinstance(self.symbol, str):
            raise ValueError("Profile symbol must be a non-empty string")
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Profile name must be a non-empty string")
        self.symbol = self.symbol.strip()
        self.name = self.name.strip()

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        result = {
            "symbol": self.symbol,
            "name": self.name,
            "english_name": self.english_name,
            "industry": self.industry,
            "business": self.business,
            "market_cap": self.market_cap,
            "pe_ratio": self.pe_ratio,
            "pb_ratio": self.pb_ratio,
            "eps": self.eps,
            "bps": self.bps,
            "total_shares": self.total_shares,
            "circulating_shares": self.circulating_shares,
            "website": self.website,
            "address": self.address,
            "phone": self.phone
        }
        if self.listing_date:
            result["listing_date"] = self.listing_date.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Profile':
        """Create profile from dictionary."""
        listing_date = None
        if data.get("listing_date"):
            if isinstance(data["listing_date"], str):
                listing_date = date.fromisoformat(data["listing_date"])
            else:
                listing_date = data["listing_date"]

        return cls(
            symbol=data["symbol"],
            name=data["name"],
            english_name=data.get("english_name"),
            listing_date=listing_date,
            industry=data.get("industry"),
            business=data.get("business"),
            market_cap=data.get("market_cap"),
            pe_ratio=data.get("pe_ratio"),
            pb_ratio=data.get("pb_ratio"),
            eps=data.get("eps"),
            bps=data.get("bps"),
            total_shares=data.get("total_shares"),
            circulating_shares=data.get("circulating_shares"),
            website=data.get("website"),
            address=data.get("address"),
            phone=data.get("phone")
        )

    def __str__(self) -> str:
        """String representation."""
        market_cap_str = ".2f" if self.market_cap else "N/A"
        return f"Profile(symbol='{self.symbol}', name='{self.name}', market_cap={market_cap_str}, industry='{self.industry or 'N/A'}')"