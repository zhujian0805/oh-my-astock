"""Shareholder structure data model."""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import date


@dataclass
class Shareholder:
    """Individual shareholder information."""

    name: str
    shares: int
    percentage: float
    share_type: Optional[str] = None  # e.g., "A股", "B股", "H股"

    def __post_init__(self):
        """Validate shareholder data after initialization."""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Shareholder name must be a non-empty string")
        if self.shares < 0:
            raise ValueError("Shares cannot be negative")
        if not 0 <= self.percentage <= 100:
            raise ValueError("Percentage must be between 0 and 100")

    def to_dict(self) -> Dict[str, Any]:
        """Convert shareholder to dictionary."""
        return {
            "name": self.name,
            "shares": self.shares,
            "percentage": self.percentage,
            "share_type": self.share_type
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Shareholder':
        """Create shareholder from dictionary."""
        return cls(
            name=data["name"],
            shares=data["shares"],
            percentage=data["percentage"],
            share_type=data.get("share_type")
        )


@dataclass
class Structure:
    """Shareholder structure information."""

    symbol: str
    report_date: Optional[date] = None
    total_shareholders: Optional[int] = None
    top_10_shareholders: Optional[List[Shareholder]] = None

    def __post_init__(self):
        """Validate structure data after initialization."""
        if not self.symbol or not isinstance(self.symbol, str):
            raise ValueError("Structure symbol must be a non-empty string")
        self.symbol = self.symbol.strip()
        if self.top_10_shareholders is None:
            self.top_10_shareholders = []

    def add_shareholder(self, shareholder: Shareholder):
        """Add a shareholder to the top 10 list."""
        self.top_10_shareholders.append(shareholder)

    def to_dict(self) -> Dict[str, Any]:
        """Convert structure to dictionary."""
        result = {
            "symbol": self.symbol,
            "total_shareholders": self.total_shareholders,
            "top_10_shareholders": [sh.to_dict() for sh in self.top_10_shareholders]
        }
        if self.report_date:
            result["report_date"] = self.report_date.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Structure':
        """Create structure from dictionary."""
        report_date = None
        if data.get("report_date"):
            if isinstance(data["report_date"], str):
                report_date = date.fromisoformat(data["report_date"])
            else:
                report_date = data["report_date"]

        shareholders = []
        if data.get("top_10_shareholders"):
            shareholders = [Shareholder.from_dict(sh) for sh in data["top_10_shareholders"]]

        return cls(
            symbol=data["symbol"],
            report_date=report_date,
            total_shareholders=data.get("total_shareholders"),
            top_10_shareholders=shareholders
        )

    def __str__(self) -> str:
        """String representation."""
        return f"Structure(symbol='{self.symbol}', total_shareholders={self.total_shareholders}, top_10_count={len(self.top_10_shareholders)})"