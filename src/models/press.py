"""Company press/announcement data model."""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class Press:
    """Company announcement/press release information like rains."""

    # Match rains Press struct exactly
    date: str
    title: str
    url: str

    def __post_init__(self):
        """Validate press data after initialization."""
        if not self.date or not isinstance(self.date, str):
            raise ValueError("Press date must be a non-empty string")
        if not self.title or not isinstance(self.title, str):
            raise ValueError("Press title must be a non-empty string")
        self.date = self.date.strip()
        self.title = self.title.strip()
        self.url = self.url.strip()

    def to_dict(self) -> Dict[str, Any]:
        """Convert press to dictionary."""
        return {
            "date": self.date,
            "title": self.title,
            "url": self.url
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Press':
        """Create press from dictionary."""
        return cls(
            date=data["date"],
            title=data["title"],
            url=data["url"]
        )

    def __str__(self) -> str:
        """String representation."""
        title_preview = self.title[:50] + "..." if len(self.title) > 50 else self.title
        return f"Press(date='{self.date}', title='{title_preview}')"