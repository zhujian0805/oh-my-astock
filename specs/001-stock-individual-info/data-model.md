# Data Model: Add Individual Stock Information Menu Item

**Feature**: 001-stock-individual-info
**Date**: 2026-01-25

## Key Entities

### Stock

**Purpose**: Represents an individual stock with merged information from multiple data sources for display in the frontend.

**Attributes** (merged from APIs)**:
- `stock_code`: str - Unique stock identifier (e.g., "000001")
- `latest_price`: float - Current stock price from EM API
- `org_name_cn`: str - Company name in Chinese from XQ API
- `org_id`: str - Organization ID from XQ API
- `additional_metrics`: dict - Other item/value pairs from both APIs (merged)

**Validation Rules**:
- `stock_code`: Required, 6-digit string, matches regex pattern `^[0-9]{6}$`
- `latest_price`: Optional float, must be positive if present
- `org_name_cn`: Optional string, non-empty if present
- `org_id`: Optional string

**Relationships**:
- None (standalone entity for this feature)

**State Transitions**:
- None (static data display, no state changes)

**Notes**:
- Data is fetched on-demand, not persisted
- Merging logic: EM API data takes precedence over XQ for duplicate fields
- Partial data allowed (if one API fails)