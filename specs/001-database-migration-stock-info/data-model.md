# Data Model: Database Migration and Stock Information Table

**Date**: 2026-01-25
**Feature**: Database Migration and Stock Information Table

## Entities

### StockInfo Entity

**Purpose**: Represents comprehensive stock information merged from East Money and Xueqiu APIs

**Attributes**:

| Field | Type | Required | Description | Validation Rules | Source Mapping |
|-------|------|----------|-------------|------------------|----------------|
| stock_code | VARCHAR(10) | ✓ | Stock code (e.g., '000001') | Primary key, normalized format | EM: 股票代码, XQ: symbol |
| company_name | VARCHAR(100) | ✓ | Full company name | Not empty, trimmed | EM: 公司名称, XQ: name |
| industry | VARCHAR(50) |  | Industry classification |  | EM: 行业, XQ: industry |
| sector | VARCHAR(50) |  | Sector classification |  | EM: 板块, XQ: sector |
| market | VARCHAR(20) |  | Market (SH/SZ) | Enum: 'SH', 'SZ' | Derived from stock_code |
| listing_date | DATE |  | IPO date | Valid date format | EM: 上市日期, XQ: listing_date |
| total_shares | BIGINT |  | Total shares outstanding | > 0 | EM: 总股本, XQ: total_shares |
| circulating_shares | BIGINT |  | Circulating shares | > 0, <= total_shares | EM: 流通股本, XQ: circulating_shares |
| market_cap | DECIMAL(20,2) |  | Market capitalization (CNY) | >= 0 | EM: 总市值, XQ: market_cap |
| pe_ratio | DECIMAL(10,2) |  | Price-to-earnings ratio | >= 0 | EM: 市盈率, XQ: pe_ratio |
| pb_ratio | DECIMAL(10,2) |  | Price-to-book ratio | >= 0 | EM: 市净率, XQ: pb_ratio |
| dividend_yield | DECIMAL(5,2) |  | Dividend yield (%) | >= 0, <= 100 | EM: 股息率, XQ: dividend_yield |
| roe | DECIMAL(5,2) |  | Return on equity (%) | >= -100, <= 100 | EM: 净资产收益率, XQ: roe |
| roa | DECIMAL(5,2) |  | Return on assets (%) | >= -100, <= 100 | EM: 总资产报酬率, XQ: roa |
| net_profit | DECIMAL(20,2) |  | Latest net profit (CNY) |  | EM: 净利润, XQ: net_profit |
| total_assets | DECIMAL(20,2) |  | Total assets (CNY) | >= 0 | EM: 总资产, XQ: total_assets |
| total_liability | DECIMAL(20,2) |  | Total liability (CNY) | >= 0 | EM: 总负债, XQ: total_liability |
| created_at | TIMESTAMP | ✓ | Record creation timestamp | Auto-generated | System |
| updated_at | TIMESTAMP | ✓ | Last update timestamp | Auto-generated | System |

**Relationships**:
- None (standalone entity)

**Business Rules**:
- stock_code must be unique and follow Chinese stock code format
- market_cap = price × circulating_shares (when price available)
- pe_ratio and pb_ratio should be reasonable values (< 1000)
- dividend_yield should be percentage (0-100)
- All monetary values in CNY
- Dates in YYYY-MM-DD format

**Validation Rules**:
- Stock code format: 6 digits for A-shares
- Company name: 1-100 characters, no special characters
- Financial ratios: reasonable ranges to detect data errors
- Market cap: positive values only
- Share counts: positive integers

### Migration Entity

**Purpose**: Tracks database schema migration versions and execution history

**Attributes**:

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| version | INTEGER | ✓ | Migration version number | Primary key, sequential |
| name | VARCHAR(100) | ✓ | Migration description | Not empty |
| applied_at | TIMESTAMP | ✓ | When migration was applied | Not null |
| checksum | VARCHAR(64) | ✓ | SHA256 hash of migration file | Valid hex string |
| success | BOOLEAN | ✓ | Migration execution result | True/False |
| execution_time_ms | INTEGER |  | Time taken to execute (ms) | >= 0 |

**Relationships**:
- None (system table)

**Business Rules**:
- Versions must be applied sequentially (no gaps)
- Checksum prevents file tampering
- Failed migrations prevent further migrations
- Execution time tracked for performance monitoring

## Data Flow

### Stock Information Collection Flow

1. **API Fetch**: Retrieve data from East Money and Xueqiu APIs
2. **Data Normalization**: Convert API responses to standard format
3. **Field Mapping**: Map EM/XQ fields to unified schema
4. **Conflict Resolution**: Apply rules for conflicting data
5. **Validation**: Check data integrity and business rules
6. **Storage**: Insert/update stock_stock_info table
7. **Indexing**: Maintain performance indexes

### Migration Flow

1. **Discovery**: Scan migration directory for new files
2. **Ordering**: Sort by version number
3. **Validation**: Check checksums and dependencies
4. **Execution**: Apply migrations in order
5. **Recording**: Update migration table with results
6. **Rollback**: Support reversal for development

## Schema Evolution

### Version 1.0 (Initial)
- Basic stock information fields
- Essential financial metrics
- Primary indexing on stock_code

### Future Versions
- Additional API sources integration
- Historical data relationships
- Performance metrics expansion
- Audit trail enhancements

## Performance Considerations

### Indexes
- PRIMARY KEY on stock_code
- INDEX on industry for sector queries
- INDEX on market for market-specific queries
- INDEX on created_at for recent data queries

### Partitioning Strategy
- No partitioning initially (DuckDB limitations)
- Consider table splitting if data grows significantly

### Caching Strategy
- Application-level caching for frequently accessed stocks
- TTL: 24 hours for stock info, 1 hour for market data
- Cache invalidation on data updates

## Data Quality

### Completeness Checks
- Required fields must be present
- Financial data should have reasonable ranges
- Cross-field validation (e.g., circulating_shares <= total_shares)

### Consistency Rules
- Same stock should have consistent data across updates
- Financial ratios should be mathematically sound
- Market classification should match stock code format

### Error Handling
- Log data quality issues for manual review
- Graceful handling of missing API data
- Data correction workflow for identified errors