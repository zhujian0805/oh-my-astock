# Historical Data Fetching Refinements

## Overview

The historical data fetching has been refined to optimize performance and efficiency. The new workflow implements intelligent prioritization, batch processing, and smart data freshness checking.

## Key Improvements

### 1. **Batch Insert Accumulation** (100 stocks per batch)
- **New Method**: `accumulate_and_bulk_insert()` in `HistoricalDataService`
- Accumulates fetched data from up to 100 stocks before performing a bulk insert
- Reduces database I/O operations significantly
- Returns remaining data that hasn't reached batch threshold

**Benefits**:
- Fewer individual INSERT operations
- Better database performance
- Reduced network/disk I/O

### 2. **Stock Metadata Refresh**
- **New Method**: `refresh_stock_name_code()` in `HistoricalDataService`
- Refreshes the `stock_name_code` table with latest stock codes
- Ensures the database has a complete list of available stocks to process

**Implementation**:
```python
def refresh_stock_name_code(self, stock_codes: List[str]) -> int:
    """Refresh stock_name_code table with provided stock codes."""
```

### 3. **Missing Stocks Detection**
- **New Method**: `get_missing_stocks()` in `HistoricalDataService`
- Identifies stocks that exist in `stock_name_code` but not in `stock_historical_data`
- Returns prioritized list for initial data population

**Implementation**:
```python
def get_missing_stocks(self, all_stock_codes: List[str]) -> List[str]:
    """Find stocks in stock_name_code that are missing from stock_historical_data."""
```

### 4. **Smart Stock Prioritization**
- **Priority Order**:
  1. **Missing stocks** (no data in `stock_historical_data`) - HIGH PRIORITY
  2. **Existing stocks** (has some data) - LOW PRIORITY

- Ensures new stocks get populated first before updating existing ones

**Rationale**:
- Maximizes data coverage
- Prioritizes stocks with zero data
- More efficient for initial population phase

### 5. **Today's Data Freshness Check**
- **New Method**: `get_stocks_missing_today_data()` in `HistoricalDataService`
- Checks if stocks have data for today (or last business day if weekend)
- Only fetches additional data if today's data is missing
- Skips unnecessary API calls for already-current stocks

**Implementation**:
```python
def get_stocks_missing_today_data(self, stock_codes: List[str]) -> List[str]:
    """Find stocks that don't have today's historical data."""
```

**Logic**:
- Accounts for weekends (adjusts to Friday for weekend checks)
- Checks if current date has data in database
- Returns only stocks missing today's OHLC data

## Updated Workflow

The `sync-historical` command now follows this refined 5-step process:

### Step 1: Refresh Stock Metadata
```
→ Fetch all stock codes from stock_name_code table
→ Ensures we have the complete inventory
```

### Step 2: Identify Missing Stocks
```
→ Compare stock_name_code with stock_historical_data
→ Find stocks with zero historical records
→ Mark as HIGH PRIORITY for fetching
```

### Step 3: Parallel Fetch with Batch Accumulation
```
→ Fetch data for all stocks in parallel (using thread pool)
→ Accumulate fetched data from 100 stocks
→ Perform BULK INSERT when 100 stocks accumulated
→ Continue until all stocks processed
```

### Step 4: Final Batch Insert
```
→ After all parallel fetching completes
→ Insert any remaining accumulated data (< 100 stocks)
→ Ensures no data is left unflushed to database
```

### Step 5: Today's Data Validation
```
→ Check remaining stocks for missing today's data
→ Identify stocks needing additional fetch if it's a trading day
→ Report for potential next-run optimization
```

## New CLI Options

### `--batch-size`
```
Default: 100
Range: Any positive integer
Usage: --batch-size 50  # Flush every 50 stocks
```

Controls how many stocks to accumulate before performing bulk insert.

**Tuning Guide**:
- Smaller values (50): More frequent inserts, less memory usage
- Larger values (200): Fewer inserts, better performance, more memory
- Default (100): Balanced for most systems

## Usage Examples

### Basic Sync with Batch Optimization
```bash
stocklib sync-historical --all-stocks --default-db
# Uses default batch size of 100
```

### Custom Batch Size
```bash
stocklib sync-historical --all-stocks --default-db --batch-size 50
# Flushes every 50 stocks instead of 100
```

### Specific Stocks with Batch Optimization
```bash
stocklib sync-historical --stock-codes 000001,600000,600036 --batch-size 3
# Accumulates and flushes at 3 stocks (useful for small sets)
```

### High Performance (Larger Batch)
```bash
stocklib sync-historical --all-stocks --default-db --batch-size 200 --max-threads 20
# 200 stocks per batch, 20 parallel threads
# Best for systems with ample memory
```

## Performance Improvements

### Before Refinement
- Individual INSERT per stock
- Sequential processing with minimal batching
- No prioritization of missing data
- Redundant API calls for already-current stocks

### After Refinement
- Bulk INSERT every 100 stocks (~90% fewer database writes)
- Parallel fetching of up to 20 stocks simultaneously
- Missing stocks prioritized for faster initial population
- Skips today's freshness check for non-prioritized stocks
- Smart weekend detection for data freshness

**Expected Improvements**:
- **Database I/O**: 80-90% reduction in INSERT operations
- **Throughput**: 5-10x faster for missing stocks (no skip logic)
- **Memory**: Bounded to ~100 stock DataFrames at a time
- **Network**: More efficient batching of requests

## Implementation Details

### Core Methods Added/Modified

#### `HistoricalDataService`
1. **`refresh_stock_name_code(stock_codes: List[str]) -> int`**
   - Ensures stock_name_code table is up-to-date
   - Returns number of stocks refreshed

2. **`get_missing_stocks(all_stock_codes: List[str]) -> List[str]`**
   - Finds stocks with no historical data
   - Returns prioritized list

3. **`get_stocks_missing_today_data(stock_codes: List[str]) -> List[str]`**
   - Checks for today's data freshness
   - Returns stocks needing update
   - Handles weekends automatically

4. **`accumulate_and_bulk_insert(batch_data, batch_size=100) -> Tuple`**
   - Manages batch accumulation
   - Flushes when batch_size reached
   - Returns (results, remaining_data)

#### `sync_historical` Command
- Added `--batch-size` option
- Implemented 5-step workflow
- Real-time batch insert feedback in UI
- Improved progress reporting

## Database Impact

### Tables
- **stock_name_code**: Read/refresh in Step 1
- **stock_historical_data**: Queried in Step 2, written in Step 3-4, checked in Step 5

### Indexes
- Existing indexes leverage:
  - `idx_stock_historical_data_code`: For Step 2 & 5 lookups
  - `idx_stock_historical_data_date`: For freshness check

## Backward Compatibility

✅ **Fully backward compatible**
- All existing methods unchanged
- New methods are additive only
- Existing commands still work
- Default behavior enhanced but not breaking

## Testing Recommendations

### Unit Tests
```python
def test_batch_accumulation():
    """Test batch accumulation with different batch sizes"""

def test_missing_stocks_detection():
    """Test detection of stocks missing from historical data"""

def test_today_data_freshness():
    """Test freshness check with weekends"""

def test_stock_prioritization():
    """Test missing stocks are prioritized first"""
```

### Integration Tests
```bash
# Test full workflow with small dataset
stocklib sync-historical --all-stocks --default-db --batch-size 10 --limit 50

# Test batch accumulation with exact threshold
stocklib sync-historical --all-stocks --default-db --batch-size 20 --limit 100

# Test weekend date handling
# Run on Saturday/Sunday to verify Friday date is used
```

## Configuration Notes

### Recommended Settings by Scenario

**Development/Testing**:
- `--batch-size 10` (quick flushes for testing)
- `--max-threads 2` (minimal resource usage)

**Production - Small Dataset (< 2000 stocks)**:
- `--batch-size 100` (default)
- `--max-threads 10`

**Production - Large Dataset (5000+ stocks)**:
- `--batch-size 200` (better throughput)
- `--max-threads 20` (if system supports)

**Production - Memory Constrained**:
- `--batch-size 50` (smaller memory footprint)
- `--max-threads 5` (reduce concurrent operations)

## Future Enhancements

Potential improvements for future iterations:

1. **Adaptive Batch Sizing**: Dynamically adjust batch_size based on memory/performance
2. **Resume Capability**: Checkpoint progress for large sync operations
3. **Parallel Batch Insert**: Multiple threads inserting different batches simultaneously
4. **Data Validation**: Bulk validation before insert to catch issues early
5. **Metrics Collection**: Track insert rates, data quality, API response times
6. **Smart Retry**: Retry failed stocks from batch automatically

## Troubleshooting

### High Memory Usage
- Reduce `--batch-size` (e.g., `50` instead of `100`)
- Reduce `--max-threads` (parallel threads consume memory)

### Slow Database Inserts
- Increase `--batch-size` (e.g., `200` instead of `100`)
- May need to optimize DuckDB settings

### Missing Some Stocks in Initial Sync
- Check `stock_name_code` table is populated via `fetch-stocks` first
- Run with `--limit 10` to debug a small subset

### Weekend Data Handling
- The freshness check automatically adjusts to Friday
- No manual intervention needed
- Weekend runs will correctly identify missing Friday data
