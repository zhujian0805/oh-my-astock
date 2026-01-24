# Data Model: Backend API Data Access Layer

## Overview

This feature adds API response models for the RESTful backend. These models define the JSON structure returned by API endpoints. They are Pydantic models that provide automatic validation, serialization, and OpenAPI schema generation.

## API Response Entities

### StockResponse

Represents a stock entity in the stock list endpoint response.

**Fields**:
- `code` (str): Stock code, primary identifier, required (e.g., "000001")
- `name` (str): Stock name, required, human-readable label (e.g., "平安银行")
- `metadata` (dict, optional): Additional stock information, default None

**Validation Rules**:
- `code`: Non-empty string, alphanumeric
- `name`: Non-empty string
- `metadata`: Dictionary or None

**Usage**:
- Returned by GET /api/stocks endpoint
- Maps directly from `models.stock.Stock` dataclass

**Example JSON**:
```json
{
  "code": "000001",
  "name": "平安银行",
  "metadata": null
}
```

**Pydantic Model**:
```python
class StockResponse(BaseModel):
    code: str = Field(..., example="000001")
    name: str = Field(..., example="平安银行")
    metadata: Optional[dict] = None
```

### HistoricalDataPoint

Represents a single historical price record in the time-series data.

**Fields**:
- `date` (date): Trading date, required, ISO 8601 format (e.g., "2024-01-15")
- `close_price` (float): Closing price, required, decimal value
- `open_price` (float, optional): Opening price, decimal value
- `high_price` (float, optional): Highest price, decimal value
- `low_price` (float, optional): Lowest price, decimal value
- `volume` (int, optional): Trading volume, integer
- `turnover` (float, optional): Turnover amount, decimal value
- `amplitude` (float, optional): Price amplitude percentage, decimal
- `price_change_rate` (float, optional): Price change rate percentage, decimal
- `price_change` (float, optional): Absolute price change, decimal
- `turnover_rate` (float, optional): Turnover rate percentage, decimal

**Validation Rules**:
- `date`: Valid date object, serialized to ISO 8601 string
- `close_price`: Positive float
- All optional fields: Float or None

**Usage**:
- Returned as array elements in GET /api/stocks/{code}/historical endpoint
- Maps from `stock_historical_data` table columns

**Example JSON**:
```json
{
  "date": "2024-01-15",
  "close_price": 12.35,
  "open_price": 12.10,
  "high_price": 12.50,
  "low_price": 12.00,
  "volume": 15420000,
  "turnover": 189567000.00,
  "amplitude": 4.13,
  "price_change_rate": 2.06,
  "price_change": 0.25,
  "turnover_rate": 1.54
}
```

**Pydantic Model**:
```python
class HistoricalDataPoint(BaseModel):
    date: date
    close_price: float
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    volume: Optional[int] = None
    turnover: Optional[float] = None
    amplitude: Optional[float] = None
    price_change_rate: Optional[float] = None
    price_change: Optional[float] = None
    turnover_rate: Optional[float] = None

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }
```

### HistoricalDataResponse

Wrapper response containing stock code and historical data array.

**Fields**:
- `stock_code` (str): Stock code identifier, required
- `data` (List[HistoricalDataPoint]): Array of historical data points, required

**Validation Rules**:
- `stock_code`: Non-empty string
- `data`: List of HistoricalDataPoint objects (can be empty)

**Usage**:
- Returned by GET /api/stocks/{code}/historical endpoint
- Aggregates historical data points for a single stock

**Example JSON**:
```json
{
  "stock_code": "000001",
  "data": [
    {
      "date": "2024-01-15",
      "close_price": 12.35,
      "open_price": 12.10,
      "high_price": 12.50,
      "low_price": 12.00,
      "volume": 15420000
    },
    {
      "date": "2024-01-16",
      "close_price": 12.42,
      "open_price": 12.35,
      "high_price": 12.58,
      "low_price": 12.30,
      "volume": 16230000
    }
  ]
}
```

**Pydantic Model**:
```python
class HistoricalDataResponse(BaseModel):
    stock_code: str
    data: List[HistoricalDataPoint]
```

### HealthCheckResponse

Health check endpoint response indicating system status.

**Fields**:
- `status` (str): Status string, required, values: "ok", "degraded", "error"
- `timestamp` (str): ISO 8601 timestamp, required, UTC time
- `database_connected` (bool): Database connectivity flag, required
- `error` (str, optional): Error message if status is "error"

**Validation Rules**:
- `status`: One of ["ok", "degraded", "error"]
- `timestamp`: ISO 8601 formatted string
- `database_connected`: Boolean

**Usage**:
- Returned by GET /api/health endpoint
- Enables monitoring and operational visibility

**Example JSON (Healthy)**:
```json
{
  "status": "ok",
  "timestamp": "2024-01-24T12:34:56.789Z",
  "database_connected": true
}
```

**Example JSON (Degraded)**:
```json
{
  "status": "degraded",
  "timestamp": "2024-01-24T12:34:56.789Z",
  "database_connected": false,
  "error": "Database file not found"
}
```

**Pydantic Model**:
```python
class HealthCheckResponse(BaseModel):
    status: str = Field(..., pattern="^(ok|degraded|error)$")
    timestamp: str
    database_connected: bool
    error: Optional[str] = None
```

### ErrorResponse

Standard error response for API errors.

**Fields**:
- `detail` (str): Error message, required, human-readable description

**Validation Rules**:
- `detail`: Non-empty string

**Usage**:
- Automatically generated by FastAPI when HTTPException is raised
- Provides consistent error format across all endpoints

**Example JSON (404 Not Found)**:
```json
{
  "detail": "No historical data found for stock 999999"
}
```

**Example JSON (500 Internal Server Error)**:
```json
{
  "detail": "Failed to retrieve stocks"
}
```

**FastAPI Handling**:
```python
# FastAPI automatically formats HTTPException as ErrorResponse
raise HTTPException(
    status_code=404,
    detail="No historical data found for stock 999999"
)
```

## Data Mapping

### Database → API Response Mapping

| Database Table | Database Column | API Entity | API Field |
|----------------|-----------------|------------|-----------|
| stock_name_code | code | StockResponse | code |
| stock_name_code | name | StockResponse | name |
| stock_name_code | metadata | StockResponse | metadata |
| stock_historical_data | date | HistoricalDataPoint | date |
| stock_historical_data | close_price | HistoricalDataPoint | close_price |
| stock_historical_data | open_price | HistoricalDataPoint | open_price |
| stock_historical_data | high_price | HistoricalDataPoint | high_price |
| stock_historical_data | low_price | HistoricalDataPoint | low_price |
| stock_historical_data | volume | HistoricalDataPoint | volume |
| stock_historical_data | turnover | HistoricalDataPoint | turnover |
| stock_historical_data | amplitude | HistoricalDataPoint | amplitude |
| stock_historical_data | price_change_rate | HistoricalDataPoint | price_change_rate |
| stock_historical_data | price_change | HistoricalDataPoint | price_change |
| stock_historical_data | turnover_rate | HistoricalDataPoint | turnover_rate |

### Model → API Response Mapping

| Source Model | Source Type | API Entity | Transformation |
|--------------|-------------|------------|----------------|
| models.stock.Stock | Dataclass | StockResponse | Direct field mapping via Pydantic |
| pandas.DataFrame | DataFrame | List[HistoricalDataPoint] | Iterate rows, convert to Pydantic |
| DatabaseService | Service | N/A | Composes queries, returns models |

## State Transitions

No state transitions - all entities are immutable read-only responses.

## Validation Strategy

All validation is handled by Pydantic:
- **Type validation**: Automatic conversion and type checking (str, int, float, date)
- **Required fields**: Pydantic enforces required fields at instantiation
- **Optional fields**: Fields with `Optional[T] = None` default to None if missing
- **Date serialization**: Dates automatically serialized to ISO 8601 strings in JSON

Example validation:
```python
# Valid
point = HistoricalDataPoint(
    date=date(2024, 1, 15),
    close_price=12.35
)
# Output: {"date": "2024-01-15", "close_price": 12.35, ...}

# Invalid - raises ValidationError
point = HistoricalDataPoint(
    date="not-a-date",  # Error: invalid date format
    close_price="abc"   # Error: not a float
)
```

## API Contract Integration

These models define the OpenAPI schema automatically:
- FastAPI generates OpenAPI 3.0 specification from Pydantic models
- Swagger UI endpoint: `/api/docs`
- ReDoc endpoint: `/api/redoc`

Example OpenAPI schema excerpt:
```yaml
components:
  schemas:
    StockResponse:
      type: object
      required:
        - code
        - name
      properties:
        code:
          type: string
          example: "000001"
        name:
          type: string
          example: "平安银行"
        metadata:
          type: object
          nullable: true
```

## Testing Strategy

Response models are validated in contract tests:

```python
# tests/contract/test_api.py
def test_stock_response_schema():
    response = client.get("/api/stocks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for stock in data:
        assert "code" in stock
        assert "name" in stock
        assert isinstance(stock["code"], str)
        assert isinstance(stock["name"], str)

def test_historical_data_schema():
    response = client.get("/api/stocks/000001/historical")
    assert response.status_code == 200
    data = response.json()
    assert "stock_code" in data
    assert "data" in data
    assert isinstance(data["data"], list)
    for point in data["data"]:
        assert "date" in point
        assert "close_price" in point
        # Validate ISO 8601 date format
        datetime.fromisoformat(point["date"])
```

## Performance Considerations

- **Serialization**: Pydantic serialization adds ~1-2ms per 1000 records
- **Memory**: Each HistoricalDataPoint ~200 bytes in memory
- **Network**: JSON response size ~150 bytes per data point
- **Example**: 750 data points = ~150KB response, ~2ms serialization time

All well within performance goals (<200ms p95 latency).
