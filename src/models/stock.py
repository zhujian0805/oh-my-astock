"""Stock data model."""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class Stock:
    """Stock entity with code, name, and optional metadata."""

    code: str
    name: str
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate stock data after initialization."""
        if not self.code or not isinstance(self.code, str):
            raise ValueError("Stock code must be a non-empty string")
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Stock name must be a non-empty string")
        self.code = self.code.strip()
        self.name = self.name.strip()

    def to_dict(self) -> Dict[str, Any]:
        """Convert stock to dictionary."""
        result = {
            "code": self.code,
            "name": self.name
        }
        if self.metadata:
            result["metadata"] = self.metadata
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Stock':
        """Create stock from dictionary."""
        return cls(
            code=data["code"],
            name=data["name"],
            metadata=data.get("metadata")
        )

    def __str__(self) -> str:
        """String representation."""
        return f"Stock(code='{self.code}', name='{self.name}')"