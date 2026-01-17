"""Contract tests for stock API fetching."""

import pytest
from unittest.mock import patch, MagicMock
from src.services.api_service import ApiService
from src.models.stock import Stock


class TestStockApiFetchContract:
    """Contract tests for stock API fetch functionality."""

    def test_api_service_initialization(self):
        """Test that API service can be initialized."""
        service = ApiService()
        assert service is not None, "API service should be created"

    @patch('akshare.stock_info_a_code_name')
    def test_api_response_structure(self, mock_api):
        """Test that API response has expected structure."""
        # Mock API response
        mock_data = {
            'code': ['000001', '000002'],
            'name': ['Stock A', 'Stock B']
        }
        mock_df = MagicMock()
        mock_df.iterrows.return_value = [
            (0, {'code': '000001', 'name': 'Stock A'}),
            (1, {'code': '000002', 'name': 'Stock B'})
        ]
        mock_api.return_value = mock_df

        service = ApiService()
        stocks = service.fetch_stock_info()

        assert len(stocks) == 2
        assert isinstance(stocks[0], Stock)
        assert stocks[0].code == '000001'
        assert stocks[0].name == 'Stock A'

    def test_stock_data_validation(self):
        """Test that fetched stock data meets validation criteria."""
        service = ApiService()

        # Valid stocks
        valid_stocks = [
            Stock(code="000001", name="Test Stock 1"),
            Stock(code="000002", name="Test Stock 2")
        ]
        assert service.validate_stock_data(valid_stocks) is True

        # Invalid stocks (empty list)
        assert service.validate_stock_data([]) is False

    def test_error_handling(self):
        """Test error handling for API failures."""
        service = ApiService()

        with patch('akshare.stock_info_a_code_name', side_effect=Exception("API Error")):
            with pytest.raises(Exception):
                service.fetch_stock_info()