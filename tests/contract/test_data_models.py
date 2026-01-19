"""Contract tests for data model validation."""

import pytest
from models.stock import Stock
from models.stock_list import StockList


class TestDataModelContract:
    """Contract tests for data models."""

    def test_stock_creation(self):
        """Test Stock object creation."""
        stock = Stock(code="000001", name="Test Stock")
        assert stock.code == "000001"
        assert stock.name == "Test Stock"
        assert stock.metadata is None

    def test_stock_validation(self):
        """Test Stock validation."""
        # Valid stock
        stock = Stock(code="000001", name="Test")
        assert stock.code == "000001"

        # Invalid code
        with pytest.raises(ValueError):
            Stock(code="", name="Test")

        # Invalid name
        with pytest.raises(ValueError):
            Stock(code="000001", name="")

    def test_stock_serialization(self):
        """Test Stock to/from dict conversion."""
        stock = Stock(code="000001", name="Test Stock", metadata={"key": "value"})
        stock_dict = stock.to_dict()

        assert stock_dict["code"] == "000001"
        assert stock_dict["name"] == "Test Stock"
        assert stock_dict["metadata"] == {"key": "value"}

        # Round trip
        stock2 = Stock.from_dict(stock_dict)
        assert stock2.code == stock.code
        assert stock2.name == stock.name
        assert stock2.metadata == stock.metadata

    def test_stock_list_creation(self):
        """Test StockList creation."""
        stocks = [
            Stock(code="000001", name="Stock A"),
            Stock(code="000002", name="Stock B"),
        ]
        stock_list = StockList(stocks)

        assert len(stock_list) == 2
        assert stock_list.get_stock("000001").name == "Stock A"

    def test_stock_list_validation(self):
        """Test StockList validation."""
        # Duplicate codes should fail
        with pytest.raises(ValueError):
            StockList(
                [
                    Stock(code="000001", name="Stock A"),
                    Stock(code="000001", name="Stock B"),
                ]
            )

    def test_stock_list_operations(self):
        """Test StockList operations."""
        stock_list = StockList()

        # Add stock
        stock = Stock(code="000001", name="Test Stock")
        stock_list.add_stock(stock)
        assert len(stock_list) == 1

        # Get stock
        retrieved = stock_list.get_stock("000001")
        assert retrieved.name == "Test Stock"

        # Remove stock
        assert stock_list.remove_stock("000001") is True
        assert len(stock_list) == 0
        assert stock_list.remove_stock("nonexistent") is False
