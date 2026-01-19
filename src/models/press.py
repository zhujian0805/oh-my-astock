"""Company press/announcement data model."""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Press:
    """Company announcement/press release information."""

    symbol: str
    title: str
    date: Optional[datetime] = None
    type: Optional[str] = None           # e.g., "定期报告", "临时公告", "澄清公告"
    url: Optional[str] = None
    summary: Optional[str] = None

    def __post_init__(self):
        """Validate press data after initialization."""
        if not self.symbol or not isinstance(self.symbol, str):
            raise ValueError("Press symbol must be a non-empty string")
        if not self.title or not isinstance(self.title, str):
            raise ValueError("Press title must be a non-empty string")
        self.symbol = self.symbol.strip()
        self.title = self.title.strip()

    def to_dict(self) -> Dict[str, Any]:
        """Convert press to dictionary."""
        result = {
            "symbol": self.symbol,
            "title": self.title,
            "type": self.type,
            "url": self.url,
            "summary": self.summary
        }
        if self.date:
            result["date"] = self.date.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Press':
        """Create press from dictionary."""
        press_date = None
        if data.get("date"):
            if isinstance(data["date"], str):
                press_date = datetime.fromisoformat(data["date"])
            else:
                press_date = data["date"]

        return cls(
            symbol=data["symbol"],
            title=data["title"],
            date=press_date,
            type=data.get("type"),
            url=data.get("url"),
            summary=data.get("summary")
        )

    def __str__(self) -> str:
        """String representation."""
        date_str = self.date.strftime("%Y-%m-%d") if self.date else "N/A"
        title_preview = self.title[:50] + "..." if len(self.title) > 50 else self.title
        return f"Press(symbol='{self.symbol}', title='{title_preview}', date={date_str})"