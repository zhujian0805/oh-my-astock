# Quick Start: Add Stock Market Overview Items to Frontend/Backend

**Feature**: 002-add-market-overviews
**Date**: 2026-01-25

## Overview

This feature adds 5 additional stock market overview sections to the existing frontend sidebar navigation, each with corresponding backend API endpoints.

## New Menu Items

### 1. 上海证券交易所 (Shanghai Stock Exchange)
- **API**: `GET /api/market/sse-summary`
- **Component**: `StockMarketOverview` (existing, enhanced)
- **Data**: Overall market metrics, PE ratios, trading volumes

### 2. 深圳证券交易所 (Shenzhen Stock Exchange)
- **API**: `GET /api/market/szse-summary`
- **Component**: `SzseSummary`
- **Data**: Security category statistics

### 3. 地区交易排序 (Regional Trading Rankings)
- **API**: `GET /api/market/szse-area-summary`
- **Component**: `SzseAreaSummary`
- **Data**: Trading activity by geographic region

### 4. 股票行业成交 (Stock Industry Transactions)
- **API**: `GET /api/market/szse-sector-summary`
- **Component**: `SzseSectorSummary`
- **Data**: Transaction data by industry sector

### 5. 上海证券交易所-每日概况 (SSE Daily Overview)
- **API**: `GET /api/market/sse-daily-deals`
- **Component**: `SseDailyDeals`
- **Data**: Daily stock trading metrics

### 6. 证券类别统计 (Security Category Statistics)
- **API**: `GET /api/market/security-categories`
- **Component**: `SecurityCategories`
- **Data**: Comprehensive security type breakdown

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
   - 股市数据 → 股票市场总貌

4. Use the left sidebar to switch between different market overview sections

## API Testing

Test the new endpoints directly:

```bash
# Shenzhen summary
curl http://localhost:8000/api/market/szse-summary

# Regional rankings
curl http://localhost:8000/api/market/szse-area-summary

# Industry sectors
curl http://localhost:8000/api/market/szse-sector-summary

# Daily deals
curl http://localhost:8000/api/market/sse-daily-deals

# Security categories
curl http://localhost:8000/api/market/security-categories
```

## Features

- **Responsive Tables**: All data displayed in responsive table format
- **Dark Mode**: Full dark/light theme support
- **Loading States**: Spinner indicators during data fetch
- **Error Handling**: User-friendly error messages with retry options
- **Chinese Text**: Proper rendering of Chinese characters and labels
- **Refresh Capability**: Manual refresh buttons for real-time data

## Development Notes

- All components follow existing patterns from `StockMarketOverview.tsx`
- API responses follow the standard format with `data` and `metadata` fields
- Components are lazy-loaded when selected in the sidebar
- Error boundaries prevent crashes from individual component failures</content>
<parameter name="file_path">specs/002-add-market-overviews/quickstart.md