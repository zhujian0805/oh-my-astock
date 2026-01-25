# Quick Start: Database Migration and Stock Information Table

**Feature**: Database Migration and Stock Information Table
**Date**: 2026-01-25

## Overview

This feature adds database migration capabilities and comprehensive stock information storage to the oh-my-astock platform. It enables fetching, merging, and displaying detailed stock data from multiple Chinese financial APIs.

## Prerequisites

- Python 3.10+
- DuckDB 0.8.0+
- akshare 1.10.0+
- FastAPI backend running
- React frontend development environment

## Quick Setup

### 1. Database Migration

```bash
# Initialize database with new schema
stocklib init-db --default-db

# Run migrations to create stock_info table
stocklib migrate
```

### 2. Fetch Stock Information

```bash
# Fetch info for a single stock
stocklib fetch-stock-info --stock-code 000001

# Fetch info for multiple stocks (batch)
stocklib fetch-stock-info --batch --file stock_list.txt
```

### 3. Verify Data

```bash
# Check migration status
stocklib migrate --status

# Query stock information
stocklib query-stock-info --stock-code 000001
```

## API Usage

### Get Stock Information

```bash
# Single stock
curl http://localhost:8000/api/v1/stocks/000001/info

# Batch request
curl -X POST http://localhost:8000/api/v1/stocks/info/batch \
  -H "Content-Type: application/json" \
  -d '{"stock_codes": ["000001", "600000"]}'
```

### Response Format

```json
{
  "stock_code": "000001",
  "company_name": "平安银行股份有限公司",
  "industry": "银行",
  "market": "SZ",
  "market_cap": 1234567890.12,
  "pe_ratio": 12.34,
  "created_at": "2024-01-25T10:00:00Z",
  "updated_at": "2024-01-25T10:00:00Z"
}
```

## Frontend Integration

### Component Usage

```tsx
import { StockInfoPanel } from '@/components/StockInfoPanel';

function HistoricalDataPage({ stockCode }: { stockCode: string }) {
  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="chart-container">
        {/* Existing chart component */}
      </div>
      <StockInfoPanel stockCode={stockCode} />
    </div>
  );
}
```

### Stock Info Panel Component

```tsx
interface StockInfoPanelProps {
  stockCode: string;
}

export function StockInfoPanel({ stockCode }: StockInfoPanelProps) {
  const { data, loading, error } = useStockInfo(stockCode);

  if (loading) return <div>Loading stock information...</div>;
  if (error) return <div>Error loading stock data</div>;

  return (
    <div className="stock-info-panel">
      <h3>{data.company_name}</h3>
      <dl>
        <dt>Industry</dt>
        <dd>{data.industry}</dd>
        <dt>Market Cap</dt>
        <dd>{formatCurrency(data.market_cap)}</dd>
        <dt>P/E Ratio</dt>
        <dd>{data.pe_ratio}</dd>
      </dl>
    </div>
  );
}
```

## Development Workflow

### 1. Test-First Development

```bash
# Run contract tests
pytest tests/contract/test_migrate_command.py -v

# Run integration tests
pytest tests/integration/test_stock_info_api.py -v

# Run with coverage
pytest --cov=src --cov-report=html
```

### 2. Code Quality

```bash
# Lint code
ruff check .

# Format code
ruff format .

# Type check (if applicable)
mypy src/
```

### 3. Database Operations

```bash
# Check current schema
stocklib db-schema

# Backup before migrations
stocklib db-backup

# Apply migrations
stocklib migrate
```

## Troubleshooting

### Common Issues

**Migration fails with "table already exists"**
```bash
# Check migration status
stocklib migrate --status

# Reset to clean state (development only)
stocklib db-reset
```

**API rate limiting errors**
```bash
# Check rate limit status
stocklib api-status

# Wait or reduce batch size
stocklib fetch-stock-info --batch-size 10
```

**Frontend shows empty stock info**
```bash
# Check API connectivity
curl http://localhost:8000/api/v1/stocks/000001/info

# Check database data
stocklib query-stock-info --stock-code 000001
```

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# CLI debug mode
stocklib --debug fetch-stock-info --stock-code 000001

# Backend debug mode
uvicorn backend.src.main:app --reload --log-level debug

# Frontend debug
npm run dev
```

## Performance Tips

- Use batch operations for multiple stocks
- Enable caching for frequently accessed data
- Monitor API rate limits
- Use pagination for large datasets

## Next Steps

1. Review the detailed specification in `spec.md`
2. Examine the implementation plan in `plan.md`
3. Check the data model in `data-model.md`
4. Review API contracts in `contracts/`
5. Begin implementation with `/speckit.tasks` command</content>
<parameter name="file_path">specs/001-database-migration-stock-info/quickstart.md