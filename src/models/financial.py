"""Financial data model."""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import date


@dataclass
class Financial:
    """Quarterly financial metrics."""

    symbol: str
    period: str  # e.g., "2023Q4", "2024Q1"
    report_date: Optional[date] = None
    revenue: Optional[float] = None          # Operating revenue
    net_profit: Optional[float] = None       # Net profit
    eps: Optional[float] = None              # Earnings per share
    roe: Optional[float] = None              # Return on equity
    roa: Optional[float] = None              # Return on assets
    gross_margin: Optional[float] = None     # Gross profit margin
    net_margin: Optional[float] = None       # Net profit margin
    total_assets: Optional[float] = None     # Total assets
    total_liabilities: Optional[float] = None # Total liabilities
    shareholder_equity: Optional[float] = None # Shareholder equity

    # Year-over-year growth rates
    revenue_yoy: Optional[float] = None      # Revenue YoY growth
    net_profit_yoy: Optional[float] = None   # Net profit YoY growth
    eps_yoy: Optional[float] = None          # EPS YoY growth

    def __post_init__(self):
        """Validate financial data after initialization."""
        if not self.symbol or not isinstance(self.symbol, str):
            raise ValueError("Financial symbol must be a non-empty string")
        if not self.period or not isinstance(self.period, str):
            raise ValueError("Financial period must be a non-empty string")
        self.symbol = self.symbol.strip()
        self.period = self.period.strip()

    def to_dict(self) -> Dict[str, Any]:
        """Convert financial to dictionary."""
        result = {
            "symbol": self.symbol,
            "period": self.period,
            "revenue": self.revenue,
            "net_profit": self.net_profit,
            "eps": self.eps,
            "roe": self.roe,
            "roa": self.roa,
            "gross_margin": self.gross_margin,
            "net_margin": self.net_margin,
            "total_assets": self.total_assets,
            "total_liabilities": self.total_liabilities,
            "shareholder_equity": self.shareholder_equity,
            "revenue_yoy": self.revenue_yoy,
            "net_profit_yoy": self.net_profit_yoy,
            "eps_yoy": self.eps_yoy
        }
        if self.report_date:
            result["report_date"] = self.report_date.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Financial':
        """Create financial from dictionary."""
        report_date = None
        if data.get("report_date"):
            if isinstance(data["report_date"], str):
                report_date = date.fromisoformat(data["report_date"])
            else:
                report_date = data["report_date"]

        return cls(
            symbol=data["symbol"],
            period=data["period"],
            report_date=report_date,
            revenue=data.get("revenue"),
            net_profit=data.get("net_profit"),
            eps=data.get("eps"),
            roe=data.get("roe"),
            roa=data.get("roa"),
            gross_margin=data.get("gross_margin"),
            net_margin=data.get("net_margin"),
            total_assets=data.get("total_assets"),
            total_liabilities=data.get("total_liabilities"),
            shareholder_equity=data.get("shareholder_equity"),
            revenue_yoy=data.get("revenue_yoy"),
            net_profit_yoy=data.get("net_profit_yoy"),
            eps_yoy=data.get("eps_yoy")
        )

    def __str__(self) -> str:
        """String representation."""
        revenue_str = ".2f" if self.revenue else "N/A"
        profit_str = ".2f" if self.net_profit else "N/A"
        return f"Financial(symbol='{self.symbol}', period='{self.period}', revenue={revenue_str}, net_profit={profit_str})"