# Data Model: Individual Stock Information

**Feature**: 001-stock-individual-info
**Date**: 2026-01-26

## Overview

The feature introduces a single Stock entity that represents comprehensive individual stock information merged from two data sources: East Money (detailed info) and Xueqiu (basic info).

## Entities

### Stock Entity

Represents an individual stock with merged information from both APIs.

**Fields**:
- `code`: str - 6-digit stock code (e.g., "601127")
- `name`: str - Stock name in Chinese
- `symbol`: str - Prefixed symbol for Xueqiu API (e.g., "SH601127", "SZ000001")

**East Money API Fields** (`stock_individual_info_em`):
- `market`: str - Market identifier
- `industry`: str - Industry classification
- `total_market_cap`: float - Total market capitalization
- `circulating_market_cap`: float - Circulating market capitalization
- `pe_ratio`: float - Price-to-earnings ratio
- `pb_ratio`: float - Price-to-book ratio
- `roe`: float - Return on equity
- `gross_margin`: float - Gross profit margin
- `net_margin`: float - Net profit margin

**Xueqiu API Fields** (`stock_individual_basic_info_xq`):
- `current_price`: float - Current stock price
- `change_percent`: float - Daily price change percentage
- `volume`: int - Trading volume
- `turnover`: float - Turnover amount
- `high_52w`: float - 52-week high price
- `low_52w`: float - 52-week low price
- `market_cap`: float - Market capitalization
- `eps`: float - Earnings per share
- `dividend_yield`: float - Dividend yield percentage

**Metadata Fields**:
- `last_updated`: datetime - Timestamp of last data fetch
- `data_sources`: dict - Status of each API source
  - `east_money`: bool - Whether East Money data was successfully retrieved
  - `xueqiu`: bool - Whether Xueqiu data was successfully retrieved
- `errors`: list[str] - List of error messages for failed API calls

## Relationships

- **Self-contained**: Stock entity has no relationships to other entities
- **API Dependencies**: Data is sourced from external APIs, not stored in database

## Validation Rules

- `code`: Must be exactly 6 digits, numeric only
- `symbol`: Must match pattern `SH[0-9]{6}` or `SZ[0-9]{6}`
- `current_price`: Must be positive float
- `market_cap`: Must be positive float
- At least one data source must be successfully retrieved (partial data allowed)

## State Transitions

1. **Initial State**: Empty stock object with code/symbol
2. **Loading State**: API calls in progress
3. **Partial State**: One API succeeded, one failed (display with error indication)
4. **Complete State**: Both APIs succeeded, full data available
5. **Error State**: Both APIs failed (display error message)

## Data Flow

1. User selects stock code
2. Frontend calls backend API with stock code
3. Backend calls both APIs in parallel
4. Backend merges responses into Stock entity
5. Backend returns Stock data with source status
6. Frontend displays data with error indicators for failed sources
