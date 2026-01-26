# Data Model: Individual Stock Information and Market Quotes

**Feature**: 001-stock-individual-info
**Date**: 2026-01-26

## Overview

The feature introduces two entities: Stock (for individual stock information merged from two APIs) and MarketQuote (for current market bid-ask data). Both entities represent external API data without database persistence.

## Entities

### Stock Entity

Represents an individual stock with merged information from East Money and Xueqiu APIs.

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

### MarketQuote Entity

Represents current market bid-ask data for stocks from East Money API.

**Fields**:
- `stock_code`: str - 6-digit stock code (e.g., "000001")
- `stock_name`: str - Stock name in Chinese

**Bid-Ask Price Fields**:
- `bid_price_1`: float - Best bid price level 1
- `bid_volume_1`: int - Bid volume at level 1
- `bid_price_2`: float - Bid price level 2
- `bid_volume_2`: int - Bid volume at level 2
- `bid_price_3`: float - Bid price level 3
- `bid_volume_3`: int - Bid volume at level 3
- `bid_price_4`: float - Bid price level 4
- `bid_volume_4`: int - Bid volume at level 4
- `bid_price_5`: float - Bid price level 5
- `bid_volume_5`: int - Bid volume at level 5

**Ask Price Fields**:
- `ask_price_1`: float - Best ask price level 1
- `ask_volume_1`: int - Ask volume at level 1
- `ask_price_2`: float - Ask price level 2
- `ask_volume_2`: int - Ask volume at level 2
- `ask_price_3`: float - Ask price level 3
- `ask_volume_3`: int - Ask volume at level 3
- `ask_price_4`: float - Ask price level 4
- `ask_volume_4`: int - Ask volume at level 4
- `ask_price_5`: float - Ask price level 5
- `ask_volume_5`: int - Ask volume at level 5

**Market Data Fields**:
- `latest_price`: float - Latest transaction price
- `change_amount`: float - Price change from previous close
- `change_percent`: float - Percentage change from previous close
- `volume`: int - Total trading volume
- `turnover`: float - Total turnover amount

**Metadata Fields**:
- `last_updated`: datetime - Timestamp of last data fetch
- `data_source`: str - API source identifier ("east_money")
- `error`: str - Error message if data retrieval failed (null if successful)

## Relationships

- **Stock**: Self-contained entity with no relationships
- **MarketQuote**: Self-contained entity with no relationships
- **API Dependencies**: Both entities are sourced from external APIs, not stored in database

## Validation Rules

**Stock Entity**:
- `code`: Must be exactly 6 digits, numeric only
- `symbol`: Must match pattern `SH[0-9]{6}` or `SZ[0-9]{6}`
- `current_price`: Must be positive float
- `market_cap`: Must be positive float
- At least one data source must be successfully retrieved (partial data allowed)

**MarketQuote Entity**:
- `stock_code`: Must be exactly 6 digits, numeric only
- `latest_price`: Must be positive float
- Bid/ask prices: Must be positive floats when present
- Bid/ask volumes: Must be non-negative integers when present

## State Transitions

**Stock Entity**:
1. **Initial State**: Empty stock object with code/symbol
2. **Loading State**: API calls in progress
3. **Partial State**: One API succeeded, one failed (display with error indication)
4. **Complete State**: Both APIs succeeded, full data available
5. **Error State**: Both APIs failed (display error message)

**MarketQuote Entity**:
1. **Initial State**: Empty quote object with stock code
2. **Loading State**: API call in progress
3. **Success State**: Complete bid-ask data retrieved
4. **Error State**: API call failed (display error message)

## Data Flow

**Stock Information**:
1. User selects stock code
2. Frontend calls backend API with stock code
3. Backend calls both APIs in parallel (East Money + Xueqiu)
4. Backend merges responses into Stock entity
5. Backend returns Stock data with source status
6. Frontend displays data with error indicators for failed sources

**Market Quotes**:
1. User navigates to market quotes page
2. Frontend calls backend API for current quotes
3. Backend calls East Money API for bid-ask data
4. Backend returns MarketQuote data array
5. Frontend displays quotes in table format
6. Frontend handles loading and error states
