"""
Integration tests for stock data merging functionality
Tests service-level integration between API calls and data processing
"""

import pytest
from unittest.mock import patch, MagicMock
from src.services.stock_info_service import StockInfoService


class TestStockDataMerging:
    """Test suite for stock data merging logic"""

    @pytest.fixture
    def service(self):
        """Create service instance for testing"""
        return StockInfoService()

    def test_merge_successful_data(self, service):
        """Test merging when both APIs return data"""
        em_data = [
            {"item": "最新", "value": "10.5"},
            {"item": "股票代码", "value": "000001"},
            {"item": "成交量", "value": "1000000"}
        ]

        xq_data = [
            {"item": "org_name_cn", "value": "平安银行股份有限公司"},
            {"item": "org_id", "value": "T000071215"},
            {"item": "最新", "value": "10.5"}  # Duplicate field
        ]

        result = service._merge_api_data(em_data, xq_data)

        # Should prioritize EM data for duplicates
        assert result["最新"] == "10.5"  # From EM
        assert result["股票代码"] == "000001"  # From EM
        assert result["成交量"] == "1000000"  # From EM
        assert result["org_name_cn"] == "平安银行股份有限公司"  # From XQ
        assert result["org_id"] == "T000071215"  # From XQ

    def test_merge_partial_data_em_only(self, service):
        """Test merging when only EM API returns data"""
        em_data = [
            {"item": "最新", "value": "10.5"},
            {"item": "股票代码", "value": "000001"}
        ]

        result = service._merge_api_data(em_data, [])

        assert result["最新"] == "10.5"
        assert result["股票代码"] == "000001"
        assert len(result) == 2

    def test_merge_partial_data_xq_only(self, service):
        """Test merging when only XQ API returns data"""
        xq_data = [
            {"item": "org_name_cn", "value": "平安银行股份有限公司"},
            {"item": "org_id", "value": "T000071215"}
        ]

        result = service._merge_api_data([], xq_data)

        assert result["org_name_cn"] == "平安银行股份有限公司"
        assert result["org_id"] == "T000071215"
        assert len(result) == 2

    def test_merge_empty_data(self, service):
        """Test merging when both APIs return no data"""
        result = service._merge_api_data([], [])

        assert result == {}
        assert len(result) == 0

    def test_merge_handles_duplicates(self, service):
        """Test merging handles duplicate keys correctly"""
        em_data = [{"item": "price", "value": "10.5"}]
        xq_data = [{"item": "price", "value": "10.6"}]

        result = service._merge_api_data(em_data, xq_data)

        # EM should take precedence
        assert result["price"] == "10.5"
        assert len(result) == 1

    @patch('src.services.stock_info_service.rate_limiter')
    @patch('src.services.stock_info_service.api_cache')
    def test_get_stock_info_integration(self, mock_cache, mock_limiter, service):
        """Integration test for full stock info retrieval"""
        # Mock rate limiter to allow calls
        mock_limiter.wait_for_api.return_value = True

        # Mock cache to return None (cache miss)
        mock_cache.get.return_value = None

        # Mock API calls
        with patch('akshare.stock_individual_info_em') as mock_em, \
             patch('akshare.stock_individual_basic_info_xq') as mock_xq:

            # Create mock DataFrames
            import pandas as pd
            em_df = pd.DataFrame([
                {"item": "最新", "value": "10.5"},
                {"item": "股票代码", "value": "000001"}
            ])
            xq_df = pd.DataFrame([
                {"item": "org_name_cn", "value": "平安银行股份有限公司"}
            ])

            mock_em.return_value = em_df
            mock_xq.return_value = xq_df

            result = service.get_stock_info("000001")

            assert result["stock_code"] == "000001"
            assert result["data"]["最新"] == "10.5"
            assert result["data"]["org_name_cn"] == "平安银行股份有限公司"
            assert result["source_status"]["em_api"] == "success"
            assert result["source_status"]["xq_api"] == "success"

            # Verify API calls were made
            mock_em.assert_called_once_with(symbol="000001")
            mock_xq.assert_called_once_with(symbol="000001")

            # Verify cache was checked and set
            mock_cache.get.assert_called_once()
            mock_cache.set.assert_called_once()