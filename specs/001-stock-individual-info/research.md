# Research Findings: Add Individual Stock Information Menu Item

**Feature**: 001-stock-individual-info
**Date**: 2026-01-25

## API Integration Research

### stock_individual_info_em (East Money API)

**Decision**: Use akshare.stock_individual_info_em() for detailed stock metrics
**Rationale**: Provides comprehensive stock information including latest price, trading data, and key financial indicators
**Parameters**:
- symbol: str (stock code like "000001")
- timeout: float (optional)
**Return Format**: pandas DataFrame with columns:
- item: str (metric name)
- value: str/object (metric value)
**Examples**: Returns items like "最新" (latest price), "股票代码" (stock code), etc.

**Alternatives considered**: Direct HTTP calls to East Money API - rejected due to complexity and maintenance burden

### stock_individual_basic_info_xq (Xueqiu API)

**Decision**: Use akshare.stock_individual_basic_info_xq() for basic company information
**Rationale**: Complements EM data with fundamental company details and organizational information
**Parameters**:
- symbol: str (stock code like "SH601127")
- token: str (optional API token)
- timeout: float (optional)
**Return Format**: pandas DataFrame with columns:
- item: str (information field)
- value: str/object (field value)
**Examples**: Returns items like "org_id", "org_name_cn" (company name), etc.

**Alternatives considered**: Manual Xueqiu API integration - rejected for consistency with existing akshare usage

## Data Merging Strategy

**Decision**: Concatenate DataFrames and handle duplicates by prioritizing EM data over XQ data
**Rationale**: Both APIs return similar item/value structure, allowing simple concatenation. EM prioritized for trading data accuracy.
**Implementation**:
- Convert both DataFrames to dictionaries
- Merge with EM values taking precedence for duplicate keys
- Return unified dictionary structure

**Alternatives considered**:
- Separate data structures - rejected for UI complexity
- Weighted merging - rejected as over-engineering for current requirements

## Error Handling & Edge Cases

**Decision**: Implement graceful degradation with partial data display
**Rationale**: Ensures user experience continues even when individual APIs fail, following observable systems principle

### Unavailable Stock Data
**Decision**: Return partial data from successful API calls
**Rationale**: Better UX than complete failure; user still gets valuable information
**Implementation**: Try/catch blocks around each API call, collect successful results

### Invalid Stock Codes
**Decision**: Validate format client-side, handle API exceptions server-side
**Rationale**: Prevents unnecessary API calls while providing clear error messages
**Implementation**: Basic regex validation for stock code format (6 digits)

### Backend API Unavailable
**Decision**: Frontend shows connection error with retry option
**Rationale**: Clear user feedback and recovery path
**Implementation**: HTTP error status codes with descriptive messages

**Alternatives considered**:
- Complete failure on any API error - rejected for poor UX
- Client-side caching only - rejected as insufficient for real-time data

## Performance Considerations

**Decision**: Implement caching with TTL and rate limiting
**Rationale**: Meets constitution requirements for production workloads and API quota management
**Implementation**:
- Cache successful responses for 5 minutes
- Exponential backoff retry for rate limits
- Thread-safe operations for concurrent requests

**Alternatives considered**: No caching - rejected due to API limits and performance goals

## Frontend Integration

**Decision**: Add menu item under "股市数据" section with dropdown selection
**Rationale**: Follows existing UI patterns and provides intuitive stock selection
**Implementation**:
- New route/page for 个股信息
- Dropdown populated with available stocks (potentially from database)
- Display component for merged data

**Alternatives considered**: Search interface - rejected as dropdown is simpler for known stocks</content>
<parameter name="file_path">specs/001-stock-individual-info/research.md