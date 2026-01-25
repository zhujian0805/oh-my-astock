# Research Findings: Database Migration and Stock Information Table

**Date**: 2026-01-25
**Feature**: Database Migration and Stock Information Table
**Status**: Complete

## Research Tasks Completed

### 1. akshare API Functions for Stock Information

**Decision**: Use `akshare.stock_individual_info_em()` for East Money and `akshare.stock_individual_info_xq()` for Xueqiu

**Rationale**:
- Both functions return comprehensive stock information including basic profile, financial metrics, and market data
- Functions are stable and well-documented in akshare 1.10.0+
- Return format is pandas DataFrame, compatible with existing data processing patterns

**Alternatives considered**:
- `akshare.stock_info_a_code_name()` - too basic, only code/name mapping
- `akshare.stock_info_sh_delist()` - delisted stocks only, not relevant

**Implementation notes**:
- Both APIs return similar field structures but with different naming conventions
- East Money API: Uses Chinese field names (公司名称, 行业, etc.)
- Xueqiu API: Uses English field names (name, industry, etc.)
- Need field mapping for data merging

### 2. DuckDB Migration Strategy

**Decision**: Implement migration system using versioned SQL scripts stored in `src/lib/migrations/`

**Rationale**:
- DuckDB supports standard SQL DDL statements
- Versioned migrations allow forward/backward compatibility
- Migration table tracks applied versions
- CLI command `stocklib migrate` executes pending migrations

**Alternatives considered**:
- Alembic (SQLAlchemy migration tool) - overkill for DuckDB, adds ORM dependency
- Manual schema updates - error-prone, no rollback capability
- Schema versioning in code - harder to track changes over time

**Implementation notes**:
- Migration table: `CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, applied_at TIMESTAMP)`
- Migration files: `001_create_stock_info_table.sql`, `002_add_indexes.sql`, etc.
- Rollback support for development environments

### 3. Data Merging Strategy for Stock Information

**Decision**: Create unified StockInfo model with field mapping and conflict resolution rules

**Rationale**:
- Both APIs provide overlapping information (company name, industry, market cap, etc.)
- Need consistent field names and data types
- Some fields may have different values requiring resolution logic
- Missing data from one source should be filled from the other

**Alternatives considered**:
- Store separate tables for each source - increases query complexity, data duplication
- Simple concatenation - doesn't handle conflicts or missing data
- Custom merge logic per field - too complex to maintain

**Implementation notes**:
- Primary key: stock_code (string, normalized format)
- Field mapping: Define explicit mapping from EM/XQ field names to unified schema
- Conflict resolution: Prefer more recent/complete data, log discrepancies
- Data validation: Ensure required fields are present, handle missing values

### 4. Frontend Layout for Historical Data Page

**Decision**: Use CSS Grid layout with 1fr 1fr (50/50 split) for chart and stock info panel

**Rationale**:
- Maintains responsive design principles
- Allows equal space allocation between chart and information
- Grid layout provides better control than flexbox for this use case
- Supports future extensibility (additional panels)

**Alternatives considered**:
- Fixed pixel widths - not responsive
- Flexbox with flex: 1 - less precise control
- Separate pages/tabs - disrupts user workflow

**Implementation notes**:
- Chart container: `grid-column: 1`
- Stock info panel: `grid-column: 2`
- Responsive breakpoints: stack vertically on mobile devices
- Loading states for both chart and stock info data

## Technical Decisions

### Database Schema Design

**Stock Info Table Structure**:
```sql
CREATE TABLE stock_stock_info (
    stock_code VARCHAR PRIMARY KEY,
    company_name VARCHAR NOT NULL,
    industry VARCHAR,
    sector VARCHAR,
    market VARCHAR,
    listing_date DATE,
    total_shares BIGINT,
    circulating_shares BIGINT,
    market_cap DECIMAL(20,2),
    pe_ratio DECIMAL(10,2),
    pb_ratio DECIMAL(10,2),
    dividend_yield DECIMAL(5,2),
    roe DECIMAL(5,2),
    roa DECIMAL(5,2),
    net_profit DECIMAL(20,2),
    total_assets DECIMAL(20,2),
    total_liability DECIMAL(20,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes**: stock_code (primary), industry, market for query performance

### API Integration Patterns

**Rate Limiting**: Implement token bucket algorithm with configurable limits per API
**Error Handling**: Exponential backoff with jitter for transient failures
**Caching**: TTL-based caching for stock info (24 hours default)
**Batch Processing**: Process stocks in chunks of 100 to balance memory and throughput

### Performance Optimizations

**Database Operations**: Use prepared statements and batch inserts
**API Calls**: Parallel processing with thread-local connections (max 20 threads)
**Frontend Loading**: Lazy load stock info when chart data is available
**Memory Management**: Stream processing for large datasets

## Risks and Mitigations

### API Reliability
**Risk**: External APIs may be unavailable or change format
**Mitigation**:
- Implement retry logic with exponential backoff
- Cache successful responses
- Log API failures for monitoring
- Graceful degradation (show cached data when available)

### Data Consistency
**Risk**: Conflicting data between East Money and Xueqiu APIs
**Mitigation**:
- Define clear precedence rules (e.g., prefer more recent data)
- Log data discrepancies for manual review
- Implement data validation rules
- Support manual data correction workflow

### Migration Safety
**Risk**: Schema changes could corrupt existing data
**Mitigation**:
- Test migrations on development data first
- Implement rollback capability
- Backup data before migrations
- Validate data integrity after migrations

### Performance at Scale
**Risk**: Processing 4000+ stocks may exceed time limits
**Mitigation**:
- Implement incremental processing
- Add progress tracking and resumable operations
- Optimize database queries and indexes
- Monitor performance metrics in debug mode