"""Dividend data model."""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import date


@dataclass
class Dividend:
    """Dividend and share distribution information."""

    symbol: str
    record_date: Optional[date] = None      # Dividend record date
    ex_dividend_date: Optional[date] = None # Ex-dividend date
    dividend_per_share: Optional[float] = None  # Cash dividend per share
    share_dividend: Optional[float] = None      # Share dividend (bonus shares)
    total_dividend: Optional[float] = None      # Total dividend amount
    dividend_yield: Optional[float] = None      # Dividend yield percentage
    period: Optional[str] = None                # e.g., "2023年报", "2023年中报"

    def __post_init__(self):
        """Validate dividend data after initialization."""
        if not self.symbol or not isinstance(self.symbol, str):
            raise ValueError("Dividend symbol must be a non-empty string")
        self.symbol = self.symbol.strip()

    def to_dict(self) -> Dict[str, Any]:
        """Convert dividend to dictionary."""
        result = {
            "symbol": self.symbol,
            "dividend_per_share": self.dividend_per_share,
            "share_dividend": self.share_dividend,
            "total_dividend": self.total_dividend,
            "dividend_yield": self.dividend_yield,
            "period": self.period
        }
        if self.record_date:
            result["record_date"] = self.record_date.isoformat()
        if self.ex_dividend_date:
            result["ex_dividend_date"] = self.ex_dividend_date.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Dividend':
        """Create dividend from dictionary."""
        record_date = None
        ex_dividend_date = None

        if data.get("record_date"):
            if isinstance(data["record_date"], str):
                record_date = date.fromisoformat(data["record_date"])
            else:
                record_date = data["record_date"]

        if data.get("ex_dividend_date"):
            if isinstance(data["ex_dividend_date"], str):
                ex_dividend_date = date.fromisoformat(data["ex_dividend_date"])
            else:
                ex_dividend_date = data["ex_dividend_date"]

        return cls(
            symbol=data["symbol"],
            record_date=record_date,
            ex_dividend_date=ex_dividend_date,
            dividend_per_share=data.get("dividend_per_share"),
            share_dividend=data.get("share_dividend"),
            total_dividend=data.get("total_dividend"),
            dividend_yield=data.get("dividend_yield"),
            period=data.get("period")
        )

    def __str__(self) -> str:
        """String representation."""
        dividend_str = ".2f" if self.dividend_per_share else "N/A"
        return f"Dividend(symbol='{self.symbol}', period='{self.period or 'N/A'}', dividend_per_share={dividend_str})"