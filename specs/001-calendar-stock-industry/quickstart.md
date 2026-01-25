# Quick Start: Add Calendar for Stock Industry Transactions

**Feature**: 001-calendar-stock-industry
**Date**: 2026-01-25

## Overview

This feature adds a month selection calendar to the 股票行业成交 (Stock Industry Transactions) page, allowing users to filter and view industry sector transaction data by specific months.

## New Calendar Feature

### Location
- Navigate to: 股市数据 → 股票市场总貌 → 股票行业成交

### Calendar Usage

1. **Month Selection**: Click the calendar icon or month display area
2. **Navigate Months**: Use arrow buttons to browse different months
3. **Select Month**: Click on any month to filter data
4. **Current Month**: View latest available data (default when no month selected)

### Visual Indicators

- **Selected Month**: Highlighted in calendar picker
- **Current Month**: Marked with "(当前)" indicator
- **Data Status**: Loading spinner during data fetch
- **No Data**: Clear message when no data available for selected month

## API Usage

### Frontend Integration

```typescript
// Calendar state management
const [selectedMonth, setSelectedMonth] = useState<{year: number, month: number} | null>(null);

// API call with month parameter
const response = await apiClient.get('/market/szse-sector-summary', {
  params: selectedMonth ? { month: `${selectedMonth.year}${selectedMonth.month.toString().padStart(2, '0')}` } : {}
});
```

### Backend API

```bash
# Get current data (default)
curl http://localhost:8000/api/market/szse-sector-summary

# Get data for specific month
curl "http://localhost:8000/api/market/szse-sector-summary?month=202501"
```

## Navigation

1. Start the backend server:
```bash
cd backend && python -m uvicorn src.main:app --reload
```

2. Start the frontend:
```bash
cd frontend && npm run dev
```

3. Navigate to the application and go to:
   - 股市数据 → 股票市场总貌 → 股票行业成交

4. Use the new calendar to select different months and observe data changes

## Features

- **Month Picker**: Intuitive calendar interface for month selection
- **Data Filtering**: Real-time filtering of industry transaction data
- **Loading States**: Visual feedback during data loading
- **Error Handling**: Graceful handling of API errors and missing data
- **Dark Mode**: Full dark/light theme support for calendar
- **Responsive**: Works on different screen sizes

## Development Notes

- Calendar component follows existing React/TypeScript patterns
- API maintains backward compatibility (month parameter is optional)
- Error boundaries prevent calendar failures from breaking the page
- Month selection is persisted during navigation within the page</content>
<parameter name="file_path">specs/001-calendar-stock-industry/quickstart.md