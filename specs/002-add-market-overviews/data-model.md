# Data Model: Add Stock Market Overview Items to Frontend/Backend

**Date**: 2026-01-25
**Feature**: 002-add-market-overviews

## Overview

This feature extends the existing stock market overview functionality by adding 5 additional data types to both backend APIs and frontend display components. All data flows from akshare APIs through backend services to frontend components for display.

## Data Entities

### SSE Summary Data (Existing)
**Source**: akshare.stock_sse_summary()
**Structure**: Array of objects with market metrics (total value, PE ratios, etc.)
**Display**: Table format with Chinese column headers

### SZSE Summary Data (New)
**Source**: akshare.stock_szse_summary()
**Structure**: Array of security category objects with quantity, trading amount, market value
**Display**: Table with security types and trading metrics

### SZSE Area Summary Data (New)
**Source**: akshare.stock_szse_area_summary()
**Structure**: Array of regional trading objects with amounts and market share
**Display**: Table ranked by region with trading activity metrics

### SZSE Sector Summary Data (New)
**Source**: akshare.stock_szse_sector_summary()
**Structure**: Array of industry sector objects with trading volumes and amounts
**Display**: Table grouped by industry sectors

### SSE Daily Deals Data (New)
**Source**: akshare.stock_sse_deal_daily()
**Structure**: Array of daily transaction objects with volume and market cap data
**Display**: Table with current day trading metrics

### Security Categories Data (New)
**Source**: akshare.stock_szse_summary() (same as SZSE Summary)
**Structure**: Detailed breakdown of security types
**Display**: Enhanced table with comprehensive security category statistics

## API Response Format

All backend endpoints return data in this standard format:

```json
{
  "data": [
    {"column1": "value1", "column2": "value2", ...}
  ],
  "metadata": {
    "count": 10,
    "source": "Exchange Name"
  }
}
```

## Frontend Data Handling

### Component Props
- `data`: Array of data objects from API
- `loading`: Boolean loading state
- `error`: String error message or null
- `onRefresh`: Function to reload data

### State Management
- Local component state for loading/error
- Data fetched on component mount
- Refresh capability with loading indicators

## Data Flow

1. **Frontend Component Mount**: Calls API endpoint
2. **Backend API**: Receives request, calls stock_service method
3. **Stock Service**: Fetches data from akshare API, formats response
4. **Frontend Display**: Receives JSON data, renders in responsive table
5. **User Interaction**: Refresh button triggers re-fetch

## Error Handling

- **Network Errors**: Display user-friendly error messages
- **API Failures**: Graceful fallback with retry options
- **Empty Data**: Show "no data available" states
- **Loading States**: Spinner indicators during data fetch

## Performance Considerations

- **Lazy Loading**: Components load data only when active
- **Caching**: No client-side caching (real-time market data)
- **Table Rendering**: Efficient rendering for large datasets
- **Responsive Design**: Tables adapt to screen sizes</content>
<parameter name="file_path">specs/002-add-market-overviews/data-model.md