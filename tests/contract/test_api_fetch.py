"""Contract tests for stock API fetching."""

import pytest
from unittest.mock import patch, MagicMock
from services.api_service import ApiService
from models.stock import Stock


class TestStockApiFetchContract:
    """Contract tests for stock API fetch functionality."""

    def test_api_service_initialization(self):
        """Test that API service can be initialized."""
        service = ApiService()
        assert service is not None, "API service should be created"

    def test_api_response_structure(self):
        """Test that API response has expected structure when fetching real data."""
        service = ApiService()
        stocks = service.fetch_stock_info()

        # Should return a significant number of stocks from all regions
        assert len(stocks) >= 1000, f"Expected at least 1000 stocks, got {len(stocks)}"
        assert isinstance(stocks[0], Stock)
        assert stocks[0].code, "Stock code should not be empty"
        assert stocks[0].name, "Stock name should not be empty"

        # Check that we have stocks from different regions
        sh_codes = [s.code for s in stocks if s.code.startswith('6')]
        sz_codes = [s.code for s in stocks if s.code.startswith(('0', '3'))]
        bj_codes = [s.code for s in stocks if s.code.startswith('8')]

        assert len(sh_codes) > 0, "Should have Shanghai stocks (6xxxx)"
        assert len(sz_codes) > 0, "Should have Shenzhen stocks (0xxxx/3xxxx)"
        # Beijing stocks are fewer, so we don't require them

    def test_stock_data_validation(self):
        """Test that fetched stock data meets validation criteria."""
        service = ApiService()

        # Valid stocks
        valid_stocks = [
            Stock(code="000001", name="Test Stock 1"),
            Stock(code="000002", name="Test Stock 2"),
        ]
        assert service.validate_stock_data(valid_stocks) is True

        # Invalid stocks (empty list)
        assert service.validate_stock_data([]) is False

    def test_error_handling(self):
        """Test error handling for API failures."""
        service = ApiService()

        # Mock all the API methods to fail
        with patch.object(service, '_fetch_all_stocks_with_pagination', side_effect=Exception("Unified API Error")), \
             patch("akshare.stock_info_a_code_name", side_effect=Exception("Primary API Error")), \
             patch.object(service, '_fetch_stocks_with_code_name_pagination', side_effect=Exception("Pagination API Error")):

            # Should still return sample data when all APIs fail
            stocks = service.fetch_stock_info()
            assert len(stocks) == 10, "Should return 10 sample stocks when all APIs fail"
            assert all(isinstance(stock, Stock) for stock in stocks)
