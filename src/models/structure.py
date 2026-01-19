"""Shareholder structure data model."""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class Shareholder:
    """Individual shareholder information like rains."""

    name: str
    shares: float
    percent: float
    shares_type: str = ""

    def __post_init__(self):
        """Validate shareholder data after initialization."""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Shareholder name must be a non-empty string")
        self.name = self.name.strip()

    def to_dict(self) -> Dict[str, Any]:
        """Convert shareholder to dictionary."""
        return {
            "name": self.name,
            "shares": self.shares,
            "percent": self.percent,
            "shares_type": self.shares_type
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Shareholder':
        """Create shareholder from dictionary."""
        return cls(
            name=data["name"],
            shares=data["shares"],
            percent=data["percent"],
            shares_type=data.get("shares_type", "")
        )


@dataclass
class Structure:
    """Shareholder structure information like rains."""

    # Match rains Structure struct exactly
    date: str
    holders_num: Optional[float] = None
    shares_avg: Optional[float] = None
    holders_ten: Optional[List[Shareholder]] = None

    def __post_init__(self):
        """Validate structure data after initialization."""
        if not self.date or not isinstance(self.date, str):
            raise ValueError("Structure date must be a non-empty string")
        self.date = self.date.strip()
        if self.holders_ten is None:
            self.holders_ten = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert structure to dictionary."""
        return {
            "date": self.date,
            "holders_num": self.holders_num,
            "shares_avg": self.shares_avg,
            "holders_ten": [sh.to_dict() for sh in self.holders_ten]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Structure':
        """Create structure from dictionary."""
        shareholders = []
        if data.get("holders_ten"):
            shareholders = [Shareholder.from_dict(sh) for sh in data["holders_ten"]]

        return cls(
            date=data["date"],
            holders_num=data.get("holders_num"),
            shares_avg=data.get("shares_avg"),
            holders_ten=shareholders
        )

    def __str__(self) -> str:
        """String representation."""
        return f"Structure(date='{self.date}', holders_num={self.holders_num}, holders_ten_count={len(self.holders_ten)})"