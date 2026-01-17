"""StockList collection model."""

from typing import List, Optional
from models.stock import Stock


class StockList:
    """Collection of Stock entities with bulk operations."""

    def __init__(self, stocks: Optional[List[Stock]] = None):
        """Initialize stock list.

        Args:
            stocks: Initial list of stocks
        """
        self.stocks = stocks or []
        self._validate_stocks()

    def _validate_stocks(self):
        """Validate that all stocks have unique codes."""
        if not self.stocks:
            return

        codes = [stock.code for stock in self.stocks]
        if len(codes) != len(set(codes)):
            raise ValueError("Stock codes must be unique")

    def add_stock(self, stock: Stock):
        """Add a stock to the collection.

        Args:
            stock: Stock to add

        Raises:
            ValueError: If stock code already exists
        """
        if any(s.code == stock.code for s in self.stocks):
            raise ValueError(f"Stock with code {stock.code} already exists")
        self.stocks.append(stock)

    def get_stock(self, code: str) -> Optional[Stock]:
        """Get stock by code.

        Args:
            code: Stock code to find

        Returns:
            Stock object or None if not found
        """
        return next((stock for stock in self.stocks if stock.code == code), None)

    def remove_stock(self, code: str) -> bool:
        """Remove stock by code.

        Args:
            code: Stock code to remove

        Returns:
            True if removed, False if not found
        """
        original_length = len(self.stocks)
        self.stocks = [stock for stock in self.stocks if stock.code != code]
        return len(self.stocks) < original_length

    def to_dict_list(self) -> List[dict]:
        """Convert all stocks to list of dictionaries.

        Returns:
            List of stock dictionaries
        """
        return [stock.to_dict() for stock in self.stocks]

    @classmethod
    def from_dict_list(cls, data: List[dict]) -> 'StockList':
        """Create StockList from list of dictionaries.

        Args:
            data: List of stock dictionaries

        Returns:
            StockList instance
        """
        stocks = [Stock.from_dict(item) for item in data]
        return cls(stocks)

    def __len__(self) -> int:
        """Get number of stocks."""
        return len(self.stocks)

    def __iter__(self):
        """Iterate over stocks."""
        return iter(self.stocks)

    def __str__(self) -> str:
        """String representation."""
        return f"StockList({len(self.stocks)} stocks)"