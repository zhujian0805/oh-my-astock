# API Testing Suite

This directory contains comprehensive tests for both backend APIs and frontend API calls.

## Test Structure

### Backend API Tests (`tests/integration/test_backend_apis.py`)
Tests all FastAPI endpoints:
- Health check endpoint
- Stock list endpoints (v1 and legacy)
- Individual stock info endpoint
- Market quotes endpoint
- Historical data endpoint
- SSE summary endpoint
- API documentation endpoint
- Error handling for invalid requests

### Frontend API Tests (`tests/integration/test_frontend_apis.test.js`)
Tests frontend API service calls:
- StockInfoApiService (stock list and individual stock info)
- MarketQuotesApiService (market quotes)
- Error handling and validation

### Stock Service API Tests (`tests/integration/test_stock_service_apis.test.js`)
Tests the legacy stock service API calls used by hooks.

### React Hooks API Tests (`tests/integration/test_react_hooks_apis.test.js`)
Tests React hooks that make API calls:
- useStocks hook
- useHistoricalData hook

### Backend Services Tests (`tests/integration/test_backend_services.py`)
Tests backend service layer functionality.

## Running Tests

### All Tests
```bash
pytest
```

### Backend API Tests Only
```bash
pytest tests/integration/test_backend_apis.py -v
```

### Frontend API Tests Only
```bash
npm test tests/integration/test_frontend_apis.test.js
npm test tests/integration/test_stock_service_apis.test.js
npm test tests/integration/test_react_hooks_apis.test.js
```

### With Coverage
```bash
pytest --cov=src --cov=backend --cov-report=html
```

### Specific Test Categories
```bash
pytest -m "api and backend"  # Backend API tests
pytest -m "api and frontend" # Frontend API tests
pytest -m integration        # All integration tests
```

## Test Configuration

- **pytest.ini**: Pytest configuration with coverage settings
- **conftest.py**: Shared test fixtures and utilities
- **Test markers**: Use `@pytest.mark.api`, `@pytest.mark.backend`, etc.

## Test Data

Test fixtures provide realistic sample data:
- Sample stock information with Chinese field names
- Market quotes with bid/ask data
- Historical price data
- Error response scenarios

## Mocking Strategy

- **Backend tests**: Use httpx AsyncClient for real HTTP testing
- **Frontend tests**: Mock axios calls to test service layer
- **Service tests**: Mock external APIs (akshare) for consistent testing

## Coverage Requirements

- Minimum 80% code coverage required
- Coverage reports generated in HTML format
- Excludes test files, migrations, and cache directories</content>
<parameter name="file_path">tests/README.md