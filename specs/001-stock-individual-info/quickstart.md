# Quick Start: Individual Stock Information

**Feature**: 001-stock-individual-info
**Date**: 2026-01-26

## Overview

The Individual Stock Information feature adds a new menu item "个股信息" under "股市数据" that displays comprehensive stock information merged from East Money and Xueqiu APIs.

## Prerequisites

- Python 3.10+
- akshare >= 1.10.0
- Running backend server on port 8000
- Running frontend development server

## API Usage

### Get Stock Information

```bash
# Get information for stock code 601127 (中国神华)
curl http://localhost:8000/api/v1/stock-info/601127

# Response includes merged data from both APIs
{
  "code": "601127",
  "name": "中国神华",
  "symbol": "SH601127",
  "current_price": 25.68,
  "change_percent": 2.34,
  "market_cap": 456789.12,
  "pe_ratio": 12.34,
  "data_sources": {
    "east_money": true,
    "xueqiu": true
  }
}
```

### Error Handling

When one API fails, partial data is still returned:

```json
{
  "code": "601127",
  "name": "中国神华",
  "market": "沪A",
  "industry": "煤炭开采",
  "data_sources": {
    "east_money": true,
    "xueqiu": false
  },
  "errors": ["Xueqiu API temporarily unavailable"]
}
```

## Frontend Usage

1. Navigate to the application
2. Click on "股市数据" in the main menu
3. Select "个股信息" from the submenu
4. Choose a stock from the dropdown menu
5. View comprehensive stock information in the flexible grid layout

## Testing

### Backend API Tests

```bash
# Run contract tests for the new API endpoint
pytest tests/contract/test_stock_info_api.py -v

# Run integration tests
pytest tests/integration/test_stock_data_merging.py -v
```

### Frontend Tests

```bash
# Run component tests
npm test -- --testPathPattern=StockInfoDisplay.test.tsx

# Run E2E tests
npm run test:e2e
```

## Development Workflow

1. **Backend**: Implement `stock_info_service.py` and `stock_info_router.py`
2. **Frontend**: Create `IndividualStockInfo.tsx` page and `StockInfoDisplay.tsx` component
3. **Menu**: Update `menu.ts` to include the new menu item
4. **Testing**: Write tests before implementation (test-first approach)

## Performance Expectations

- Stock information loads within 3 seconds of selection
- API handles 95% success rate for valid stock selections
- Graceful degradation when one data source fails

## Troubleshooting

### Common Issues

1. **Stock not found**: Verify the 6-digit stock code is valid
2. **API timeout**: Check network connectivity and API availability
3. **Partial data**: This is expected behavior when Xueqiu API fails
4. **Display issues**: Ensure flexible grid layout is working in different screen sizes

### Debug Mode

Enable debug logging to see detailed API call information:

```bash
# Backend with debug logging
uvicorn backend.src.main:app --reload --log-level debug

# Frontend development mode
npm run dev
```

## Architecture Notes

- **Backend**: Service layer merges API data, router handles HTTP endpoints
- **Frontend**: Page component manages state, display component renders data
- **Data Flow**: Frontend → API → Service → External APIs → Merged Response
- **Error Handling**: Partial data display with clear source status indicators
