# Data Model: Add Calendar for Stock Industry Transactions

**Date**: 2026-01-25
**Feature**: 001-calendar-stock-industry

## Overview

This feature extends the existing industry transaction data display with month-based filtering. Users can select a specific month via a calendar interface, and the system filters the industry sector transaction data accordingly.

## Data Entities

### Month Selection Data (New)
**Source**: User calendar interaction
**Structure**: Object with year and month components
**Format**: { year: number, month: number }
**Validation**: Year between 2020-2030, month 1-12
**Display**: Calendar picker with month/year navigation

### Industry Transaction Data (Existing, Filtered)
**Source**: akshare.stock_szse_sector_summary(date="YYYYMM")
**Structure**: Array of industry sector objects with transaction metrics
**Filtering**: Applied by selected month parameter
**Display**: Filtered table data matching existing SzseSectorSummary component format

## API Request/Response Format

### Request (Updated)
```json
GET /api/market/szse-sector-summary?month=202501
```

**Parameters:**
- `month`: Optional string in "YYYYMM" format (e.g., "202501")

### Response (Existing Format)
```json
{
  "data": [
    {
      "行业名称": "行业A",
      "成交金额": 1234567890.12,
      "成交量": 987654,
      "涨跌幅": 2.34
    }
  ],
  "metadata": {
    "count": 10,
    "source": "Shenzhen Stock Exchange",
    "month": "202501"
  }
}
```

## Frontend Data Handling

### Calendar State
- `selectedMonth`: { year: number, month: number }
- `currentView`: Current calendar display month/year
- `availableRange`: Min/max months with data

### Data Flow
1. User selects month in calendar → Updates selectedMonth state
2. Component fetches data with month parameter → API call with ?month=YYYYMM
3. Backend filters data using akshare date parameter → Returns filtered results
4. Frontend displays filtered data in existing table format

## Error Handling

- **Invalid Month**: API returns 400 with error message
- **No Data for Month**: API returns empty data array with appropriate metadata
- **API Unavailable**: Frontend shows error state with retry option

## Performance Considerations

- **Caching**: Month-filtered results can be cached briefly
- **Lazy Loading**: Calendar loads only when component mounts
- **Minimal API Calls**: Single parameterized call vs multiple requests