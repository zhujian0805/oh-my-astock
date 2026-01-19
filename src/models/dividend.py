"""Dividend data model."""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class Dividend:
    """Dividend and share distribution information like rains."""

    # Match rains Dividend struct exactly
    date: str
    shares_dividend: float = 0.0
    shares_into: float = 0.0
    money: float = 0.0
    date_dividend: str = ""
    date_record: str = ""

    def __post_init__(self):
        """Validate dividend data after initialization."""
        if not self.date or not isinstance(self.date, str):
            raise ValueError("Dividend date must be a non-empty string")
        self.date = self.date.strip()

    def to_dict(self) -> Dict[str, Any]:
        """Convert dividend to dictionary."""
        return {
            "date": self.date,
            "shares_dividend": self.shares_dividend,
            "shares_into": self.shares_into,
            "money": self.money,
            "date_dividend": self.date_dividend,
            "date_record": self.date_record
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Dividend':
        """Create dividend from dictionary."""
        return cls(
            date=data["date"],
            shares_dividend=data.get("shares_dividend", 0.0),
            shares_into=data.get("shares_into", 0.0),
            money=data.get("money", 0.0),
            date_dividend=data.get("date_dividend", ""),
            date_record=data.get("date_record", "")
        )

    def __str__(self) -> str:
        """String representation."""
        return f"Dividend(date='{self.date}', shares_dividend={self.shares_dividend}, shares_into={self.shares_into}, money={self.money})"