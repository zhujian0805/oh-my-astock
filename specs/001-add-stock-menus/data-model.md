# Data Model: Add Stock Market Menu Items

**Date**: 2026-01-25
**Feature**: 001-add-stock-menus

## Overview

This feature adds 5 CLI commands that fetch and display Chinese stock market overview data from akshare APIs. No new database models are required as the data is fetched and displayed directly without persistence. The data structures represent the API response formats.

## Data Entities

### Stock Market Summary
Represents overall market data for Shanghai Stock Exchange.

**Attributes**:
- `total_market_value`: Total market capitalization (float)
- `average_pe_ratio`: Average price-to-earnings ratio (float)
- `trading_volume`: Total trading volume (integer)
- `market_metrics`: Additional market indicators (dict)

**Validation Rules**:
- All numeric values must be non-negative
- PE ratio should be reasonable range (0-1000)

### Security Category Statistics
Represents breakdown of securities by type in Shenzhen Exchange.

**Attributes**:
- `security_type`: Type of security (string: "股票", "债券", etc.)
- `quantity`: Number of securities (integer)
- `trading_amount`: Total trading amount (float)
- `market_value`: Total market value (float)

**Validation Rules**:
- Quantity must be non-negative integer
- Amounts and values must be non-negative floats

### Regional Trading Data
Represents trading activity by geographic region.

**Attributes**:
- `region`: Geographic region name (string)
- `trading_amount`: Total trading amount for region (float)
- `market_share`: Percentage of total market (float, 0-100)

**Validation Rules**:
- Market share must be between 0 and 100
- Trading amount must be non-negative

### Industry Sector Data
Represents transaction data grouped by industry sectors.

**Attributes**:
- `industry_sector`: Industry/sector name (string)
- `trading_days`: Number of trading days (integer)
- `trading_amount`: Total amount traded (float)
- `trading_volume`: Total volume traded (integer)

**Validation Rules**:
- Trading days must be positive integer
- Amounts and volumes must be non-negative

### Daily Transaction Details
Represents daily stock trading metrics for Shanghai Exchange.

**Attributes**:
- `date`: Trading date (string, YYYY-MM-DD format)
- `trading_volume`: Daily trading volume (integer)
- `market_capitalization`: Market capitalization (float)
- `price_metrics`: Additional price-related metrics (dict)

**Validation Rules**:
- Date must be valid YYYY-MM-DD format
- Volume and capitalization must be non-negative

## Data Flow

1. CLI command invoked with optional parameters
2. ApiService calls appropriate akshare function
3. Raw API data received as pandas DataFrame or dict
4. Data validated and formatted as JSON
5. JSON output displayed to user

## No Database Persistence

This feature does not require database storage - all data is fetched on-demand and displayed directly. This aligns with the feature's read-only nature for market overview information.