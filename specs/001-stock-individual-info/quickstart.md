# Quick Start: Individual Stock Information

**Feature**: 001-stock-individual-info
**Date**: 2026-01-26

## Overview

The feature provides comprehensive stock market data through two menu items under "股市数据":

1. **个股信息** - Individual stock details merged from East Money and Xueqiu APIs
2. **行情报价** - Current market bid-ask quotes for curated popular stocks

Both features include robust error handling, performance optimizations, and comprehensive testing.

## Prerequisites

- Python 3.10+
- akshare >= 1.10.0
- FastAPI/Pydantic backend
- React/TypeScript frontend
- DuckDB database

## Database Setup

1. Initialize new tables:
```sql
-- See data-model.md for complete schema
CREATE TABLE stock_list (...);
CREATE TABLE stocks (...);
CREATE TABLE market_quotes (...);
```

2. Populate initial stock list with 20-30 popular stocks.

## Backend Implementation

### API Endpoints

- `GET /api/v1/stocks` - Returns list of available stocks for dropdown
- `GET /api/v1/stocks/{code}` - Returns merged individual stock data
- `GET /api/v1/market-quotes` - Returns current market quotes for curated stocks

### Key Components

1. **StockService**: Handles API calls, data merging with field precedence rules
2. **Rate Limiting**: Exponential backoff retry logic for external APIs
3. **Database Layer**: Persists merged data in DuckDB

## Frontend Implementation

### Pages

1. **StockInfo Page**: Dropdown selection + flexible grid display
2. **MarketQuotes Page**: Table display of bid-ask data

### Components

- Stock selector dropdown
- Data display components with loading/error states
- Responsive table for market quotes

## Testing Strategy

### Contract Tests
- API endpoint validation
- Response schema verification
- Error handling scenarios

### End-to-End Tests
- Complete user workflows
- Frontend-backend integration
- Performance validation

### Test Commands
```bash
# Backend tests
pytest tests/contract/ -v
pytest tests/integration/ -v

# Frontend tests
npm test
```

## Performance Targets

- Stock info: < 3 seconds load time
- Market quotes: < 2 seconds load time
- 95% success rate for valid requests
- Graceful degradation on API failures

## Development Workflow

1. Write failing contract tests first
2. Implement backend services
3. Add frontend components
4. Run comprehensive test suite
5. Validate performance targets

## Success Criteria

- ✅ All backend APIs tested and functional
- ✅ Frontend can access backend APIs reliably
- ✅ Comprehensive automated testing implemented
- ✅ Performance targets met
- ✅ Error handling provides clear user feedback</content>
<parameter name="file_path">/home/jzhu/oh-my-astock/specs/001-stock-individual-info/quickstart.md