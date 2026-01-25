# Quick Start: Individual Stock Information

**Feature**: 001-stock-individual-info

## Overview

The 个股信息 feature allows users to view detailed information about individual stocks by selecting from a dropdown menu. Data is merged from East Money and Xueqiu APIs for comprehensive stock insights.

## Prerequisites

- Backend server running with new `/api/v1/stocks/{stock_code}/info` endpoint
- Frontend updated with 个股信息 menu item
- Valid stock codes (6-digit format)

## Usage

### Backend API

```bash
# Get information for stock code 000001
curl http://localhost:8000/api/v1/stocks/000001/info
```

**Response**:
```json
{
  "stock_code": "000001",
  "data": {
    "最新": "7.05",
    "股票代码": "000001",
    "org_name_cn": "平安银行股份有限公司"
  },
  "source_status": {
    "em_api": "success",
    "xq_api": "success"
  }
}
```

### Frontend

1. Navigate to the application
2. Click on "股市数据" menu
3. Select "个股信息"
4. Choose a stock from the dropdown
5. View the merged stock information

## Error Handling

- **Invalid stock code**: Returns 400 with error message
- **Data unavailable**: Returns partial data if possible, or 404
- **Rate limited**: Returns 429 with retry guidance
- **API failures**: Partial data returned with source status indicating failures

## Development

### Testing
```bash
# Run contract tests
pytest tests/contract/test_stock_info_api.py

# Run integration tests
pytest tests/integration/test_stock_data_merging.py
```

### Debugging
Enable debug mode for detailed API call logs:
```bash
python -m backend --debug
```