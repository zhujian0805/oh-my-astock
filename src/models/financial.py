"""Financial data model."""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class Financial:
    """Quarterly financial metrics like rains."""

    # Match rains Financial struct exactly
    date: str
    total_revenue: Optional[float] = None
    net_profit: Optional[float] = None
    ps_net_assets: Optional[float] = None
    ps_capital_reserve: Optional[float] = None
    total_revenue_rate: float = 0.0
    net_profit_rate: float = 0.0

    def __post_init__(self):
        """Validate financial data after initialization."""
        if not self.date or not isinstance(self.date, str):
            raise ValueError("Financial date must be a non-empty string")
        self.date = self.date.strip()

    def to_dict(self) -> Dict[str, Any]:
        """Convert financial to dictionary."""
        return {
            "date": self.date,
            "total_revenue": self.total_revenue,
            "net_profit": self.net_profit,
            "ps_net_assets": self.ps_net_assets,
            "ps_capital_reserve": self.ps_capital_reserve,
            "total_revenue_rate": self.total_revenue_rate,
            "net_profit_rate": self.net_profit_rate
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Financial':
        """Create financial from dictionary."""
        return cls(
            date=data["date"],
            total_revenue=data.get("total_revenue"),
            net_profit=data.get("net_profit"),
            ps_net_assets=data.get("ps_net_assets"),
            ps_capital_reserve=data.get("ps_capital_reserve"),
            total_revenue_rate=data.get("total_revenue_rate", 0.0),
            net_profit_rate=data.get("net_profit_rate", 0.0)
        )

    def __str__(self) -> str:
        """String representation."""
        revenue_str = ".2f" if self.total_revenue else "N/A"
        profit_str = ".2f" if self.net_profit else "N/A"
        return f"Financial(date='{self.date}', total_revenue={revenue_str}, net_profit={profit_str})"