# Quick Start: Individual Stock Information and Market Quotes

**Feature**: 001-stock-individual-info
**Date**: 2026-01-26

## Overview

The feature provides comprehensive stock market data through two menu items under "股市数据":

1. **个股信息** - Individual stock details merged from East Money and Xueqiu APIs
2. **行情报价** - Current market bid-ask quotes and trading data

Both features include robust error handling and performance optimizations.

## Prerequisites

- Python 3.10+
- akshare >= 1.10.0
- Running backend server on port 8000
- Running frontend development server

## API Usage

### Get Individual Stock Information

```bash
# Get information for stock code 000001 (平安银行)
curl http://localhost:8000/api/v1/stocks/000001/info

# Response includes merged data from both APIs
{
  "stock_code": "000001",
  "data": {
    "股票代码": "000001",
    "股票简称": "平安银行",
    "最新": "10.51",
    "总市值": "2000000000",
    "市盈率": "8.5"
  },
  "source_status": {
    "em_api": "success",
    "xq_api": "success"
  },
  "timestamp": "2026-01-26T10:30:00Z"
}
```

### Get Market Quotes

```bash
# Get quotes for specific stocks
curl "http://localhost:8000/api/v1/market-quotes?stocks=000001,600000"

# Get quotes for default popular stocks
curl http://localhost:8000/api/v1/market-quotes

# Response includes bid-ask data
{
  "quotes": [
    {
      "stock_code": "000001",
      "stock_name": "平安银行",
      "bid_price_1": 10.50,
      "bid_volume_1": 1000,
      "ask_price_1": 10.52,
      "ask_volume_1": 800,
      "latest_price": 10.51,
      "change_percent": 0.85,
      "volume": 5000000,
      "data_source": "east_money"
    }
  ],
  "metadata": {
    "total_quotes": 1,
    "last_updated": "2026-01-26T10:30:00Z"
  }
}
```

### Error Handling

**Stock Info - Partial Data** (when Xueqiu API fails):
```json
{
  "stock_code": "000001",
  "data": {
    "股票代码": "000001",
    "总市值": "2000000000",
    "市盈率": "8.5"
  },
  "source_status": {
    "em_api": "success",
    "xq_api": "failed"
  },
  "errors": ["Xueqiu API temporarily unavailable"]
}
```

**Market Quotes - Error Response**:
```json
{
  "error": "Internal server error",
  "message": "Failed to retrieve market quotes"
}
```

## Frontend Usage

### Individual Stock Information

1. Navigate to the application
2. Click on "股市数据" in the main menu
3. Select "个股信息" from the submenu
4. Choose a stock from the dropdown menu
5. View comprehensive stock information in the flexible grid layout

### Market Quotes

1. Navigate to the application
2. Click on "股市数据" in the main menu
3. Select "行情报价" from the submenu
4. View current bid-ask prices and market data in table format
5. Data refreshes automatically with current market conditions

## Testing

### Backend API Tests

```bash
# Run all backend tests
pytest backend/tests/ -v

# Run contract tests for stock info API
pytest backend/tests/contract/test_stock_info_api.py -v

# Run integration tests for data merging
pytest backend/tests/integration/test_stock_data_merging.py -v
```

### Frontend Tests

```bash
# Run frontend tests (after fixing existing test issues)
npm test --prefix frontend

# Run specific component tests
npm test --prefix frontend -- --testNamePattern="StockInfoDisplay"
```

## Development Workflow

### Individual Stock Information

1. **Backend**: StockInfoService handles API calls and data merging
2. **Frontend**: IndividualStockInfo page + StockInfoDisplay component
3. **API**: GET `/api/v1/stocks/{stock_code}/info`

### Market Quotes

1. **Backend**: MarketQuotesService calls stock_bid_ask_em API
2. **Frontend**: MarketQuotesPage + MarketQuotesTable component
3. **API**: GET `/api/v1/market-quotes`

## Performance Expectations

- **Individual Stock Info**: Loads within 3 seconds of selection
- **Market Quotes**: Loads within 2 seconds of page access
- Both features: 95% success rate for valid requests
- Graceful degradation with partial data when APIs fail

## Troubleshooting

### Common Issues

1. **API Timeouts**: Check network connectivity and akshare version
2. **Invalid Stock Codes**: Ensure 6-digit format, verify stock exists
3. **Partial Data Display**: Normal behavior when secondary API fails
4. **Menu Not Visible**: Check frontend build and routing configuration

### Debug Mode

**Backend**:
```bash
uvicorn backend.src.main:app --reload --log-level debug
```

**Frontend**:
```bash
npm run dev --prefix frontend
```

### API Endpoints

- **Stock Info**: `/api/v1/stocks/{stock_code}/info`
- **Market Quotes**: `/api/v1/market-quotes`
- **Health Check**: `/health`

## Architecture Notes

- **Backend Services**: Separate services for different data types (StockInfoService, MarketQuotesService)
- **API Integration**: Rate limiting and caching for external API calls
- **Frontend Components**: Reusable components with consistent error handling
- **Data Flow**: External APIs → Backend services → Frontend components
- **State Management**: Loading states and error boundaries throughout

## Success Criteria

- ✅ Individual stock info: 95% success rate, 3-second response time
- ✅ Market quotes: 95% success rate, 2-second response time
- ✅ Both menu items accessible and fully functional
- ✅ Error handling provides clear user feedback
- ✅ Responsive design works across different screen sizes
