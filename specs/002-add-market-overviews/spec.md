# Feature Specification: Add Stock Market Overview Items to Frontend/Backend

**Feature Branch**: `002-add-market-overviews`
**Created**: 2026-01-25
**Status**: Draft
**Input**: User description: "add stock market overview items to frontend and backend: 上海证券交易所, 深圳证券交易所, 证券类别统计, 地区交易排序, 股票行业成交, 上海证券交易所-每日概况"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Shanghai Stock Exchange Overview (Priority: P1)

As a market analyst, I want to view Shanghai Stock Exchange overall market data so I can understand the current market status through the web interface.

**Why this priority**: Core Shanghai exchange overview, already exists as baseline functionality.

**Independent Test**: Navigate to 股票市场总貌 → 上海证券交易所 and verify market data displays in table format.

**Acceptance Scenarios**:

1. **Given** I navigate to the stock market overview page, **When** I select 上海证券交易所, **Then** I see overall market data in a table
2. **Given** the data loads successfully, **When** I view the table, **Then** it shows key metrics like total market value and PE ratios

---

### User Story 2 - View Shenzhen Stock Exchange Overview (Priority: P1)

As a market analyst, I want to view Shenzhen Stock Exchange security category statistics so I can analyze different security types' performance.

**Why this priority**: Primary Shenzhen exchange data, complements Shanghai overview.

**Independent Test**: Navigate to 股票市场总貌 → 深圳证券交易所 and verify security category data displays.

**Acceptance Scenarios**:

1. **Given** I navigate to the stock market overview page, **When** I select 深圳证券交易所, **Then** I see security category statistics in a table
2. **Given** the data loads successfully, **When** I view the data, **Then** it shows quantity, trading amount, and market value by security type

---

### User Story 3 - View Regional Trading Rankings (Priority: P2)

As a regional market analyst, I want to see trading rankings by region in the Shenzhen exchange so I can identify regional trading patterns.

**Why this priority**: Regional analysis provides geographic insights into trading activity.

**Independent Test**: Navigate to 股票市场总貌 → 地区交易排序 and verify regional ranking data displays.

**Acceptance Scenarios**:

1. **Given** I navigate to the stock market overview page, **When** I select 地区交易排序, **Then** I see regional trading rankings in a table
2. **Given** the data loads successfully, **When** I view the rankings, **Then** it shows regions with their trading amounts and market share

---

### User Story 4 - View Stock Industry Transaction Data (Priority: P2)

As an industry analyst, I want to view stock transaction data by industry sector so I can analyze sector performance.

**Why this priority**: Industry sector analysis is crucial for understanding market composition.

**Independent Test**: Navigate to 股票市场总貌 → 股票行业成交 and verify industry transaction data displays.

**Acceptance Scenarios**:

1. **Given** I navigate to the stock market overview page, **When** I select 股票行业成交, **Then** I see industry sector transaction data in a table
2. **Given** the data loads successfully, **When** I view the data, **Then** it shows trading amounts and volumes by industry sector

---

### User Story 5 - View Shanghai Daily Stock Overview (Priority: P2)

As a daily market watcher, I want to see daily stock transaction details for the Shanghai exchange so I can track daily market activity.

**Why this priority**: Daily overview provides current market activity insights.

**Independent Test**: Navigate to 股票市场总貌 → 上海证券交易所-每日概况 and verify daily transaction data displays.

**Acceptance Scenarios**:

1. **Given** I navigate to the stock market overview page, **When** I select 上海证券交易所-每日概况, **Then** I see daily stock transaction details in a table
2. **Given** the data loads successfully, **When** I view the data, **Then** it shows trading volumes and market capitalization metrics

---

### User Story 6 - View Security Category Statistics (Priority: P2)

As a market analyst, I want to view detailed security category statistics so I can understand market composition by security types.

**Why this priority**: Detailed security category breakdown provides comprehensive market analysis.

**Independent Test**: Navigate to 股票市场总貌 → 证券类别统计 and verify detailed security statistics display.

**Acceptance Scenarios**:

1. **Given** I navigate to the stock market overview page, **When** I select 证券类别统计, **Then** I see detailed security category statistics
2. **Given** the data loads successfully, **When** I view the statistics, **Then** it shows comprehensive breakdown of all security types

---

### Edge Cases

- What happens when API calls fail or return no data?
- How does the interface handle large datasets?
- What happens when network connectivity is poor?
- How does the interface handle data that doesn't fit in the table format?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Backend MUST provide API endpoints for all 6 market overview data types using akshare APIs
- **FR-002**: Frontend MUST display all 6 market overview options in the left sidebar of the stock market overview page
- **FR-003**: Each frontend component MUST fetch data from corresponding backend API endpoint
- **FR-004**: All data MUST be displayed in responsive table format with proper Chinese labels
- **FR-005**: Interface MUST handle loading states and error conditions gracefully
- **FR-006**: Navigation between different overview types MUST be smooth and preserve state
- **FR-007**: All components MUST support dark mode theming
- **FR-008**: Data MUST be refreshed on demand with refresh buttons

### Key Entities *(include if feature involves data)*

- **Market Summary Data**: Overall exchange statistics (SSE/SZSE summary)
- **Security Category Data**: Breakdown by security types with trading metrics
- **Regional Trading Data**: Geographic trading activity rankings
- **Industry Sector Data**: Transaction data grouped by industry
- **Daily Transaction Data**: Current day trading metrics

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can navigate to all 6 market overview sections and view data within 3 seconds of page load
- **SC-002**: All API endpoints return properly formatted JSON data for frontend consumption
- **SC-003**: Interface displays meaningful error messages when data cannot be loaded
- **SC-004**: Navigation between overview sections works smoothly without page reloads
- **SC-005**: All components properly support dark/light theme switching
- **SC-006**: Tables display data correctly with proper formatting for large numbers and Chinese text
