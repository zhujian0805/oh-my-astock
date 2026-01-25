# Feature Specification: Backend API Data Access Layer

**Feature Branch**: `003-backend-api`
**Created**: 2026-01-24
**Status**: Implementation In Progress - US1 Complete, US2/US3/US4 Pending
**Input**: User description: "now i have frontend, add a backend to serve as database access layer so frontend can get dsta from it"

## Implementation Status (Updated 2026-01-25)

**Current State**: MVP foundation complete with US1 fully functional. US2 (historical data API) is the critical blocker for MVP completion.

**Completed**:
- ✅ US1: GET /api/stocks endpoint fully implemented and tested
- ✅ FastAPI application infrastructure (app.py, routes.py, schemas.py, middleware.py)
- ✅ CORS configuration and request logging
- ✅ Database integration with existing DuckDB schema
- ✅ 23 of 65 total tasks completed (foundation + US1)

**Pending**:
- ❌ US2: GET /api/stocks/{code}/historical endpoint (14 tasks, P1 priority, MVP blocker)
- ❌ US3: GET /api/health + API documentation (10 tasks, P2 priority)
- ❌ US4: CORS testing and validation (8 tasks, P2 priority)

**Architecture Notes**:
- Backend implemented in `backend/` directory (not `src/api/` as originally planned)
- Uses separate requirements.txt and configuration from main CLI
- Actual implementation exceeds original spec scope with additional middleware and error handling

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fetch Available Stocks for Dropdown Menu (Priority: P1)

When the frontend application loads, it needs to populate the stock selection dropdown with all available stocks from the database. The backend API must provide an endpoint that returns a list of stocks with their codes and names to enable the frontend to display selectable options.

**Why this priority**: This is the foundational capability required for the frontend to function. Without the ability to retrieve the stock list, users cannot select stocks, making the entire application non-functional. This is the absolute minimum viable API.

**Independent Test**: Can be fully tested by sending an HTTP GET request to the stocks list endpoint and verifying that it returns a JSON array of stock objects containing code and name fields. Delivers immediate value by unblocking the frontend dropdown functionality.

**Acceptance Scenarios**:

1. **Given** the database contains at least 1,000 stocks in the `stock_name_code` table, **When** the frontend requests GET /api/stocks, **Then** the API returns a JSON array with all stock records, each containing `code` and `name` fields
2. **Given** the stocks list endpoint is called, **When** the database contains no stocks, **Then** the API returns an empty JSON array `[]` with HTTP 200 status
3. **Given** the stocks list endpoint is called, **When** the database connection fails, **Then** the API returns HTTP 500 status with a descriptive error message

---

### User Story 2 - Fetch Historical Price Data for Chart Visualization (Priority: P1)

When a user selects a stock from the dropdown, the frontend must display a historical price chart. The backend API must provide an endpoint that accepts a stock code parameter and returns all historical price data for that stock, enabling the frontend to render a time-series chart.

**Why this priority**: This is the second half of the core user value proposition. After selecting a stock (P1 Story 1), users must be able to view the historical price chart. Together, these two stories form the complete MVP experience.

**Independent Test**: Can be fully tested by sending an HTTP GET request to the historical data endpoint with a valid stock code (e.g., `GET /api/stocks/000001/historical`) and verifying that it returns a JSON array of price records with date and close_price fields. Delivers the core chart visualization capability.

**Acceptance Scenarios**:

1. **Given** the database contains historical data for stock code "000001" spanning 1+ years, **When** the frontend requests GET /api/stocks/000001/historical, **Then** the API returns a JSON array of historical price records, each containing `date`, `close_price`, and other OHLCV fields
2. **Given** a stock code exists in `stock_name_code` but has no historical data in `stock_historical_data`, **When** the frontend requests historical data for that code, **Then** the API returns an empty JSON array `[]` with HTTP 200 status
3. **Given** a stock code does not exist in the database, **When** the frontend requests historical data for that code, **Then** the API returns HTTP 404 status with a message indicating the stock was not found
4. **Given** the historical data endpoint is called, **When** the database query returns more than 1,000 records, **Then** the API returns all available records without pagination (pagination is a future enhancement)

---

### User Story 3 - API Health Check and Documentation (Priority: P2)

Developers and operations teams need to verify that the backend API is running and accessible, and developers integrating the frontend need to understand the available endpoints and their expected request/response formats.

**Why this priority**: While not critical for core functionality, health checks enable monitoring and troubleshooting, and API documentation accelerates frontend development. This improves developer experience and operational reliability but can be added after core endpoints are functional.

**Independent Test**: Can be tested by sending GET /api/health and verifying it returns HTTP 200 with a status message, and by accessing /api/docs to view API documentation. Delivers operational visibility and developer productivity improvements.

**Acceptance Scenarios**:

1. **Given** the backend API server is running, **When** a request is sent to GET /api/health, **Then** the API returns HTTP 200 with a JSON response containing `{"status": "ok", "timestamp": "<ISO 8601 timestamp>"}`
2. **Given** the API documentation is enabled, **When** a developer accesses GET /api/docs, **Then** the API returns interactive API documentation listing all endpoints with request/response examples
3. **Given** the backend API server is not running or the database is unreachable, **When** the health check endpoint is called, **Then** the API returns HTTP 503 (Service Unavailable) with details about the failure

---

### User Story 4 - CORS Configuration for Frontend Integration (Priority: P2)

The frontend application is served from a different origin than the backend API (e.g., frontend on `localhost:5173`, backend on `localhost:8000`). The backend must enable Cross-Origin Resource Sharing (CORS) to allow the frontend to make API requests without browser security errors.

**Why this priority**: Required for frontend-backend integration in development and production environments where they are served from different origins. However, it's a configuration task that can be added after endpoints are implemented, so it's P2 rather than P1.

**Independent Test**: Can be tested by making a cross-origin request from the frontend application to the backend API and verifying that the response includes appropriate CORS headers (`Access-Control-Allow-Origin`, etc.). Delivers seamless frontend-backend integration.

**Acceptance Scenarios**:

1. **Given** the frontend application makes a GET request from origin `http://localhost:5173`, **When** the request reaches the backend API, **Then** the response includes `Access-Control-Allow-Origin: *` header (or specific allowed origins)
2. **Given** the frontend makes a preflight OPTIONS request, **When** the backend receives the OPTIONS request, **Then** the API responds with HTTP 204 and appropriate `Access-Control-Allow-Methods` and `Access-Control-Allow-Headers` headers
3. **Given** CORS is configured with allowed origins list, **When** a request comes from an unauthorized origin, **Then** the API rejects the request with appropriate CORS error

---

### Edge Cases

- What happens when the database file is corrupted or unreadable? → API returns HTTP 503 (Service Unavailable) with error details, and logs the error for debugging
- How does the system handle concurrent requests from multiple frontend users? → Backend should support concurrent connections (target: 100+ concurrent users) without performance degradation or data corruption
- What happens when a stock code contains special characters or invalid characters? → API validates stock code format and returns HTTP 400 (Bad Request) for invalid codes
- How does the API handle large historical datasets (5+ years, 1,000+ records per stock)? → Return all data without pagination initially; implement pagination in future iterations if performance issues arise
- What happens when the database query times out? → API returns HTTP 504 (Gateway Timeout) after a configurable timeout period (default 30 seconds)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a RESTful HTTP API server that accepts GET requests and returns JSON responses
- **FR-002**: System MUST provide a GET /api/stocks endpoint that returns a list of all available stocks from the `stock_name_code` table
- **FR-003**: System MUST provide a GET /api/stocks/{code}/historical endpoint that accepts a stock code parameter and returns historical price data from the `stock_historical_data` table
- **FR-004**: System MUST validate stock code parameters and return HTTP 400 for invalid stock codes
- **FR-005**: System MUST return HTTP 404 when a requested stock code does not exist in the `stock_name_code` table
- **FR-006**: System MUST handle database connection errors gracefully and return HTTP 500 or 503 with descriptive error messages
- **FR-007**: System MUST enable CORS headers to allow cross-origin requests from the frontend application
- **FR-008**: System MUST provide a GET /api/health endpoint that returns API status and timestamp
- **FR-009**: System MUST log all API requests with timestamp, endpoint, HTTP method, and response status code
- **FR-010**: System MUST reuse the existing DatabaseConnection and database models from the `src/models/` directory
- **FR-011**: System MUST return stock list data with fields: `code` (string), `name` (string)
- **FR-012**: System MUST return historical price data with fields: `date` (ISO 8601 string), `close_price` (number), `open_price` (number), `high_price` (number), `low_price` (number), `volume` (integer), and other available OHLCV fields
- **FR-013**: System MUST maintain backward compatibility with the existing DuckDB database schema defined in feature 001-duckdb-stock-setup

### Key Entities *(include if feature involves data)*

- **StockResponse**: API response entity representing a stock in the list endpoint. Attributes: `code` (stock identifier), `name` (stock name)
- **HistoricalDataResponse**: API response entity representing a single historical price record. Attributes: `date` (trading date), `close_price`, `open_price`, `high_price`, `low_price`, `volume`, `turnover`, `amplitude`, `price_change_rate`, `price_change`, `turnover_rate`
- **HealthCheckResponse**: API response entity for health check endpoint. Attributes: `status` (string: "ok" or "error"), `timestamp` (ISO 8601 string), optional `error` (string)
- **ErrorResponse**: API response entity for error cases. Attributes: `error` (error message string), `status_code` (HTTP status code), optional `details` (additional context)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Frontend can retrieve the complete list of stocks (1,000+ records) from the API in under 2 seconds on a typical network connection
- **SC-002**: Frontend can retrieve 1+ years of historical price data (250-750 records) for a single stock in under 2 seconds
- **SC-003**: API handles at least 100 concurrent requests without response time degradation beyond 20%
- **SC-004**: API achieves 99.9% uptime during normal operation (excluding intentional shutdowns or database failures)
- **SC-005**: All API responses include appropriate HTTP status codes (200 for success, 400 for bad requests, 404 for not found, 500/503 for server errors)
- **SC-006**: API documentation is accessible and provides working examples for all endpoints, reducing frontend integration time to under 2 hours
- **SC-007**: API error messages are descriptive enough for frontend developers to diagnose issues without accessing backend logs

## Assumptions

- **Database Schema**: The `stock_name_code` and `stock_historical_data` tables are already created and populated via feature 001-duckdb-stock-setup
- **Data Volume**: Database contains at least 1,000 stocks and 1+ years of historical data for the majority of stocks
- **Network Environment**: Backend API and frontend application may run on different ports during development (e.g., backend on port 8000, frontend on port 5173)
- **Authentication**: No authentication or authorization required for initial version; all endpoints are publicly accessible
- **Data Updates**: Historical data is relatively static (updated daily or less frequently); no real-time data streaming required in this iteration
- **Frontend Requirements**: Frontend expects JSON responses with specific field names matching the database schema (e.g., `close_price`, not `closePrice`)
- **Error Handling**: Frontend can gracefully handle API errors by displaying user-friendly messages based on HTTP status codes and error response bodies

## Out of Scope

- User authentication and authorization (JWT, OAuth, API keys)
- Real-time data streaming or WebSocket connections
- Data pagination or filtering (e.g., date range filters, limit/offset pagination)
- Rate limiting or throttling
- API versioning (e.g., /api/v1/, /api/v2/)
- Caching layer (Redis, in-memory cache)
- Data write operations (POST, PUT, DELETE endpoints)
- Advanced analytics endpoints (e.g., stock comparison, technical indicators)
- GraphQL API (REST only)
- Database migrations or schema versioning tools
- Containerization (Docker) or deployment configuration
- Load balancing or horizontal scaling
- API key management or usage analytics
