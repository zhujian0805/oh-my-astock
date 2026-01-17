"""Integration tests for API data validation."""

import pytest
from unittest.mock import patch, MagicMock
from src.services.api_service import ApiService
from src.models.stock import Stock


class TestApiDataValidationIntegration:
    """Integration tests for API data validation."""

    @patch('akshare.stock_info_a_code_name')
    def test_full_api_fetch_workflow(self, mock_api):
        """Test complete API fetch and validation workflow."""
        # Mock API response with realistic data
        mock_df = MagicMock()
        mock_df.iterrows.return_value = [
            (0, {'code': '000001', 'name': '平安银行'}),
            (1, {'code': '000002', 'name': '万科A'}),
            (2, {'code': '000003', 'name': '国农科技'})
        ]
        mock_api.return_value = mock_df

        service = ApiService()
        stocks = service.fetch_stock_info()

        # Validate results
        assert len(stocks) == 3
        assert service.validate_stock_data(stocks) is True

        # Check specific stocks
        codes = [stock.code for stock in stocks]
        names = [stock.name for stock in stocks]

        assert '000001' in codes
        assert '平安银行' in names

    @patch('akshare.stock_info_a_code_name')
    def test_api_response_with_invalid_data(self, mock_api):
        """Test API response handling with some invalid data."""
        # Mock response with some invalid data
        mock_df = MagicMock()
        mock_df.iterrows.return_value = [
            (0, {'code': '000001', 'name': 'Valid Stock'}),
            (1, {'code': '', 'name': 'Invalid Code'}),  # Invalid: empty code
            (2, {'code': '000003', 'name': ''})  # Invalid: empty name
        ]
        mock_api.return_value = mock_df

        service = ApiService()
        stocks = service.fetch_stock_info()

        # Should only get valid stocks
        assert len(stocks) == 1
        assert stocks[0].code == '000001'
        assert stocks[0].name == 'Valid Stock'

    def test_validation_edge_cases(self):
        """Test validation with edge cases."""
        service = ApiService()

        # Test with duplicate codes
        duplicate_stocks = [
            Stock(code="000001", name="Stock A"),
            Stock(code="000001", name="Stock B")  # Duplicate code
        ]
        assert service.validate_stock_data(duplicate_stocks) is False