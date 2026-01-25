# Quick Start: Add Stock Market Menu Items

**Feature**: 001-add-stock-menus
**Date**: 2026-01-25

## Overview

This feature adds 5 new CLI commands to access Chinese stock market overview data from Shanghai and Shenzhen exchanges.

## Prerequisites

- Python 3.10+
- akshare >= 1.10.0 installed
- CLI tool built: `pip install -e .`

## New Commands

### Shanghai Stock Exchange Summary
```bash
stocklib sse-summary
```
Displays overall market data including total market value and average PE ratio.

### Shenzhen Security Category Statistics
```bash
stocklib szse-summary
```
Shows security breakdown by type with quantity, trading amount, and market value.

### Shenzhen Regional Trading Rankings
```bash
stocklib szse-area-summary
```
Displays trading activity rankings by geographic region.

### Shenzhen Industry Sector Transactions
```bash
stocklib szse-sector-summary
```
Shows transaction data grouped by industry sectors.

### Shanghai Daily Stock Transactions
```bash
stocklib sse-daily-deals
```
Displays daily stock transaction details including volume and market cap.

## Usage Examples

```bash
# Get Shanghai exchange overview
stocklib sse-summary > shanghai_summary.json

# View Shenzhen security types
stocklib szse-summary | jq '.[] | select(.security_type == "股票")'

# Check regional trading
stocklib szse-area-summary | jq 'sort_by(.trading_amount) | reverse | .[0:5]'

# Industry sector analysis
stocklib szse-sector-summary > industry_data.json

# Daily market activity
stocklib sse-daily-deals
```

## Output Format

All commands output JSON data for easy parsing and integration with other tools. Use `jq` for JSON processing or redirect to files for analysis.

## Error Handling

Commands return appropriate exit codes:
- `0`: Success
- `1`: API error or network failure

Error messages are displayed to stderr with context about the failure.</content>
<parameter name="file_path">specs/001-add-stock-menus/quickstart.md