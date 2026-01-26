"""
Contract tests for market quotes API endpoint
Validates API contract compliance with OpenAPI specification
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app  # Import from src directory

client = TestClient(app)


class TestMarketQuotesAPI:
    """Test suite for market quotes API"""

    def test_get_market_quotes_success_default(self):
        """Test successful retrieval of market quotes with default stocks"""
        response = client.get("/api/v1/market-quotes")

        # Should return 200 on success
        assert response.status_code == 200

        data = response.json()

        # Validate response structure per contract
        assert "quotes" in data
        assert isinstance(data["quotes"], list)
        assert "metadata" in data

        # Validate metadata structure
        metadata = data["metadata"]
        assert "total_quotes" in metadata
        assert "last_updated" in metadata
        assert "data_source" in metadata
        assert metadata["data_source"] == "east_money"