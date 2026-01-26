# Feature Specification: Add Individual Stock Information Menu Item

**Feature Branch**: `001-stock-individual-info`
**Created**: 2026-01-25
**Status**: Draft
**Input**: User description: "add a menu item under 股市数据，named 个股信息

1. update backend to call stock_individual_info_em and stock_individual_basic_info_xq
2. add a backend api for individual stock, which merge the response of stock_individual_info_em and stock_individual_basic_info_xq
3. on frontend, on 个股信息, you shouw the merged information, you can choose stock on a dropdown menu to show the individual info"

**Updated**: Add "行情报价" (market quotes/bid-ask data) under "股票数据" menu using stock_bid_ask_em API

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Individual Stock Information (Priority: P1)

As a user, I want to access detailed information about a specific stock so that I can make informed investment decisions.

**Why this priority**: This is the core functionality requested, providing the primary value of viewing comprehensive stock data.

**Independent Test**: Can be fully tested by navigating to the 个股信息 menu item, selecting a stock from the dropdown, and verifying that merged information from both data sources displays correctly.

**Acceptance Scenarios**:

1. **Given** I am on the 个股信息 page, **When** I select a stock from the dropdown menu, **Then** I see comprehensive stock information displayed
2. **Given** a valid stock is selected, **When** the data loads successfully, **Then** I see merged information from both stock_individual_info_em and stock_individual_basic_info_xq APIs

---

### User Story 2 - View Market Quotes/Bid-Ask Data (Priority: P2)

As a user, I want to view current market quotes and bid-ask prices for stocks so that I can understand market liquidity and price levels.

**Why this priority**: Provides essential trading information complementing the detailed stock information, important for investment analysis.

**Independent Test**: Can be fully tested by navigating to the 行情报价 menu item and verifying that current bid-ask data for stocks is displayed correctly.

**Acceptance Scenarios**:

1. **Given** I am on the 行情报价 page, **When** I view the page, **Then** I see a table of current bid-ask prices for multiple stocks
2. **Given** the market data loads successfully, **When** the page displays, **Then** I see bid prices, ask prices, and volume data from the stock_bid_ask_em API

---

### Edge Cases

- What happens when selected stock data is not available from one or both APIs?
- How does the system handle invalid or non-existent stock codes?
- What occurs when the backend API is temporarily unavailable?

When the Xueqiu API fails, the system MUST show partial data from the East Money API and clearly indicate that the Xueqiu API failed to load data.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a menu item named "个股信息" under the "股市数据" section
- **FR-002**: Backend MUST call the stock_individual_info_em API to retrieve detailed stock information using 6-digit stock codes (e.g., "601127")
- **FR-003**: Backend MUST call the stock_individual_basic_info_xq API to retrieve basic stock information using prefixed symbols (e.g., "SH601127" for Shanghai stocks starting with '6', "SZ000001" for Shenzhen stocks starting with '0' or '3')
- **FR-004**: Backend MUST merge responses from stock_individual_info_em and stock_individual_basic_info_xq into a single data structure
- **FR-005**: Backend MUST provide an API endpoint that returns the merged individual stock data
- **FR-006**: Frontend MUST display a dropdown menu allowing users to select stocks
- **FR-007**: Backend MUST call the stock_bid_ask_em API to retrieve current market quotes and bid-ask data
- **FR-008**: Frontend MUST use a flexible grid system layout that stretches content based on available screen space for optimal display of stock information
- **FR-009**: System MUST provide a menu item named "行情报价" under the "股市数据" section
- **FR-010**: Backend MUST provide an API endpoint that returns current market quotes data
- **FR-011**: Frontend MUST display market quotes in a table format showing bid-ask prices and volumes

### Key Entities *(include if feature involves data)*

- **Stock**: Represents an individual stock with a unique code, containing merged basic and detailed information attributes without implementation details
- **MarketQuote**: Represents current market bid-ask data for stocks, including buy/sell prices and volumes

## Clarifications

### Session 2026-01-26
- Q: API Symbol Format for stock_individual_basic_info_xq → A: API requires prefixed symbols like "SH601127", "SZ000001" - matches akshare documentation and examples
- Q: How should the stock information page layout be structured to be more stretched? → A: Flexible grid system
- Q: What should happen when the Xueqiu API fails? → A: Show partial data with error indication
- Q: How should the '行情报价' (market quotes/bid-ask data) feature be implemented? → A: Add market quotes table for multiple stocks
- Q: How should the system handle invalid or non-existent stock codes when a user selects them from the dropdown? → A: Empty state
- Q: Always add a step to restart applications using manage.sh → A: Use manage.sh to restart the applications, including frontend and backend, to make sure it's runnable

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view detailed information for any selected stock within 3 seconds of selection
- **SC-002**: Stock information displays correctly merged from both data sources for 95% of valid stock selections
- **SC-003**: The 个股信息 menu item is accessible and functional for all users
- **SC-004**: Users can view current market quotes and bid-ask data within 2 seconds of page load
- **SC-005**: Market quotes display correctly from the stock_bid_ask_em API for 95% of requests
- **SC-006**: The 行情报价 menu item is accessible and functional for all users
