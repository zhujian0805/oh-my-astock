"""Backend API integration tests for all endpoints."""

import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from backend.main import app
import asyncio


class TestBackendAPIs:
    """Integration tests for all backend API endpoints."""

    @pytest.fixture
    async def client(self):
        """Create test client."""
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            yield client

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database_connected" in data
        assert data["database_connected"] is True

    @pytest.mark.asyncio
    async def test_get_stock_list_pagination(self, client):
        """Test stock list endpoint with pagination."""
        # Test basic request
        response = await client.get("/api/stocks")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)
        assert isinstance(data["pagination"], dict)

        # Test with custom pagination
        response = await client.get("/api/stocks?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) <= 10
        assert data["pagination"]["limit"] == 10
        assert data["pagination"]["offset"] == 0

    @pytest.mark.asyncio
    async def test_get_stock_list_v1(self, client):
        """Test v1 stock list endpoint."""
        response = await client.get("/api/v1/stocks")
        assert response.status_code == 200
        data = response.json()
        assert "stocks" in data
        assert isinstance(data["stocks"], list)

        # Verify stock structure
        if data["stocks"]:
            stock = data["stocks"][0]
            assert "code" in stock
            assert "name" in stock
            assert "exchange" in stock
            assert len(stock["code"]) == 6
            assert stock["code"].isdigit()

    @pytest.mark.asyncio
    async def test_get_individual_stock_info(self, client):
        """Test individual stock info endpoint."""
        # Test with valid stock code
        response = await client.get("/api/v1/stocks/000001")
        assert response.status_code == 200
        data = response.json()

        # Should have core fields
        assert "code" in data
        assert "data_sources" in data
        assert "last_updated" in data
        assert data["code"] == "000001"

        # Should have data source info
        assert isinstance(data["data_sources"], dict)
        assert "east_money" in data["data_sources"] or "xueqiu" in data["data_sources"]

    @pytest.mark.asyncio
    async def test_get_individual_stock_info_invalid_code(self, client):
        """Test individual stock info with invalid code."""
        # Test with invalid stock code
        response = await client.get("/api/v1/stocks/invalid")
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_market_quotes(self, client):
        """Test market quotes endpoint."""
        response = await client.get("/api/v1/market-quotes")
        assert response.status_code == 200
        data = response.json()

        assert "quotes" in data
        assert "metadata" in data
        assert isinstance(data["quotes"], list)
        assert isinstance(data["metadata"], dict)

    @pytest.mark.asyncio
    async def test_get_market_quotes_with_stocks(self, client):
        """Test market quotes endpoint with specific stocks."""
        response = await client.get("/api/v1/market-quotes?stocks=000001,600036")
        assert response.status_code == 200
        data = response.json()

        assert "quotes" in data
        assert "metadata" in data
        # Should return quotes for requested stocks
        assert isinstance(data["quotes"], list)

    @pytest.mark.asyncio
    async def test_get_historical_data(self, client):
        """Test historical data endpoint."""
        response = await client.get("/api/stocks/000001/historical")
        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert isinstance(data["data"], list)

        # If data exists, verify structure
        if data["data"]:
            record = data["data"][0]
            assert "date" in record
            assert "open_price" in record
            assert "close_price" in record
            assert "volume" in record

    @pytest.mark.asyncio
    async def test_get_historical_data_with_dates(self, client):
        """Test historical data endpoint with date filters."""
        response = await client.get("/api/stocks/000001/historical?start_date=2024-01-01&end_date=2024-01-31")
        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_get_sse_summary(self, client):
        """Test SSE summary endpoint."""
        response = await client.get("/api/market/sse-summary")
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        if data:
            record = data[0]
            assert "trading_date" in record or "date" in record

    @pytest.mark.asyncio
    async def test_api_docs_endpoint(self, client):
        """Test API documentation endpoint."""
        response = await client.get("/api/docs")
        assert response.status_code == 200
        data = response.json()

        assert "title" in data
        assert "version" in data
        assert "endpoints" in data

    @pytest.mark.asyncio
    async def test_error_handling(self, client):
        """Test error handling for invalid requests."""
        # Test non-existent endpoint
        response = await client.get("/api/non-existent")
        assert response.status_code == 404

        # Test invalid stock code format
        response = await client.get("/api/v1/stocks/123")
        assert response.status_code == 422  # Validation error