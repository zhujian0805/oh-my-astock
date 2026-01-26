"""Test configuration and utilities for API testing."""

import pytest
import asyncio
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from main import app
except ImportError:
    # Try alternative import path
    try:
        from backend.main import app
    except ImportError:
        # Create a minimal FastAPI app for testing if import fails
        from fastapi import FastAPI
        app = FastAPI(title="Test App")


@pytest.fixture
async def test_client():
    """Create test client for backend API tests."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Test data constants
TEST_STOCK_CODES = ['000001', '600036', '300750']
TEST_INVALID_STOCK_CODES = ['invalid', '123', '1234567', '']


@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing."""
    return {
        'code': '000001',
        'name': '平安银行',
        'exchange': 'Shenzhen',
        'current_price': 10.5,
        'change_percent': 1.2,
        'market_cap': 5000000000,
        'volume': 1000000,
        'turnover': 10500000,
        'pe_ratio': 8.5,
        'pb_ratio': 1.2,
        'data_sources': {'east_money': True, 'xueqiu': False},
        'last_updated': '2024-01-01T00:00:00Z'
    }


@pytest.fixture
def sample_market_quotes():
    """Sample market quotes data for testing."""
    return {
        'quotes': [
            {
                'stock_code': '000001',
                'stock_name': '平安银行',
                'latest_price': 10.5,
                'change_amount': 0.2,
                'change_percent': 1.94,
                'volume': 1000000,
                'turnover': 10500000,
                'bid_price_1': 10.5,
                'bid_volume_1': 1000,
                'ask_price_1': 10.6,
                'ask_volume_1': 800,
                'last_updated': '2024-01-01T00:00:00Z',
                'data_source': 'east_money'
            }
        ],
        'metadata': {
            'total_quotes': 1,
            'last_updated': '2024-01-01T00:00:00Z',
            'data_source': 'east_money'
        }
    }


@pytest.fixture
def sample_historical_data():
    """Sample historical price data for testing."""
    return [
        {
            'date': '2024-01-01',
            'open_price': 10.0,
            'high_price': 10.5,
            'low_price': 9.8,
            'close_price': 10.2,
            'volume': 1000000,
            'turnover': 10200000,
            'amplitude': 7.14,
            'price_change_rate': 2.0,
            'price_change': 0.2,
            'turnover_rate': 1.5
        },
        {
            'date': '2024-01-02',
            'open_price': 10.2,
            'high_price': 10.8,
            'low_price': 10.1,
            'close_price': 10.6,
            'volume': 1200000,
            'turnover': 12720000,
            'amplitude': 6.86,
            'price_change_rate': 3.92,
            'price_change': 0.4,
            'turnover_rate': 1.8
        }
    ]