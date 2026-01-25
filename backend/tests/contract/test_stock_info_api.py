"""
Contract tests for stock info API endpoint
Validates API contract compliance with OpenAPI specification
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app  # Import from src directory

client = TestClient(app)


class TestStockInfoAPI:
    """Test suite for individual stock information API"""

    def test_get_stock_info_success(self):
        """Test successful retrieval of stock information"""
        # This test will fail until the endpoint is implemented
        response = client.get("/api/v1/stocks/000001/info")

        # Should return 200 on success
        assert response.status_code == 200

        data = response.json()

        # Validate response structure per contract
        assert "stock_code" in data
        assert data["stock_code"] == "000001"

        assert "data" in data
        assert isinstance(data["data"], dict)
        assert len(data["data"]) > 0  # Should have merged data

        assert "source_status" in data
        assert "em_api" in data["source_status"]
        assert "xq_api" in data["source_status"]
        assert data["source_status"]["em_api"] in ["success", "failed"]
        assert data["source_status"]["xq_api"] in ["success", "failed"]

    def test_get_stock_info_invalid_code(self):
        """Test response for invalid stock code"""
        response = client.get("/api/v1/stocks/invalid/info")

        # Should return 400 for invalid format
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data  # FastAPI uses 'detail' for error messages
        assert "Invalid stock code format" in data["detail"]

    def test_get_stock_info_not_found(self):
        """Test response for non-existent stock"""
        response = client.get("/api/v1/stocks/999999/info")

        # Should return 404 for not found
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data  # FastAPI uses 'detail' for error messages
        assert "Stock data not available" in data["detail"]

    @pytest.mark.parametrize("stock_code", ["000001", "600000", "300001"])
    def test_get_stock_info_various_codes(self, stock_code):
        """Test endpoint works with various valid stock codes"""
        response = client.get(f"/api/v1/stocks/{stock_code}/info")

        # May succeed or fail depending on data availability
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert data["stock_code"] == stock_code
            assert "data" in data
            assert "source_status" in data